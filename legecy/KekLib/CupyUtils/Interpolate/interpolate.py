"""
    CupyUtils.Interpolate.interpolate.py

    
"""
import cupy as np
from cupy import (array, asarray)
from CupyUtils.NumpyWrapper import searchsorted

from scipy._lib.six import xrange, integer_types, string_types
from .polyint import _Interpolator1D
from ._bsplines import make_interp_spline, BSpline

def _check_broadcast_up_to(arr_from, shape_to, name):
    """Helper to check that arr_from broadcasts up to shape_to"""
    shape_from = arr_from.shape
    if len(shape_to) >= len(shape_from):
        for t, f in zip(shape_to[::-1], shape_from[::-1]):
            if f != 1 and f != t:
                break
        else:  # all checks pass, do the upcasting that we need later
            if arr_from.size != 1 and arr_from.shape != shape_to:
                arr_from = np.ones(shape_to, arr_from.dtype) * arr_from
            return arr_from.ravel()
    # at least one check failed
    raise ValueError('%s argument must be able to broadcast up '
                     'to shape %s but had shape %s'
                     % (name, shape_to, shape_from))


def _do_extrapolate(fill_value):
    """Helper to check if fill_value == "extrapolate" without warnings"""
    return (isinstance(fill_value, string_types) and
            fill_value == 'extrapolate')


class interp1d(_Interpolator1D):
    """
    Interpolate a 1-D function.

    `x` and `y` are arrays of values used to approximate some function f:
    ``y = f(x)``.  This class returns a function whose call method uses
    interpolation to find the value of new points.

    Note that calling `interp1d` with NaNs present in input values results in
    undefined behaviour.

    Parameters
    ----------
    x : (N,) array_like
        A 1-D array of real values.
    y : (...,N,...) array_like
        A N-D array of real values. The length of `y` along the interpolation
        axis must be equal to the length of `x`.
    kind : str or int, optional
        Specifies the kind of interpolation as a string
        ('linear', 'nearest', 'zero', 'slinear', 'quadratic', 'cubic',
        'previous', 'next', where 'zero', 'slinear', 'quadratic' and 'cubic'
        refer to a spline interpolation of zeroth, first, second or third
        order; 'previous' and 'next' simply return the previous or next value
        of the point) or as an integer specifying the order of the spline
        interpolator to use.
        Default is 'linear'.
    axis : int, optional
        Specifies the axis of `y` along which to interpolate.
        Interpolation defaults to the last axis of `y`.
    copy : bool, optional
        If True, the class makes internal copies of x and y.
        If False, references to `x` and `y` are used. The default is to copy.
    bounds_error : bool, optional
        If True, a ValueError is raised any time interpolation is attempted on
        a value outside of the range of x (where extrapolation is
        necessary). If False, out of bounds values are assigned `fill_value`.
        By default, an error is raised unless ``fill_value="extrapolate"``.
    fill_value : array-like or (array-like, array_like) or "extrapolate", optional
        - if a ndarray (or float), this value will be used to fill in for
          requested points outside of the data range. If not provided, then
          the default is NaN. The array-like must broadcast properly to the
          dimensions of the non-interpolation axes.
        - If a two-element tuple, then the first element is used as a
          fill value for ``x_new < x[0]`` and the second element is used for
          ``x_new > x[-1]``. Anything that is not a 2-element tuple (e.g.,
          list or ndarray, regardless of shape) is taken to be a single
          array-like argument meant to be used for both bounds as
          ``below, above = fill_value, fill_value``.

          .. versionadded:: 0.17.0
        - If "extrapolate", then points outside the data range will be
          extrapolated.

          .. versionadded:: 0.17.0
    assume_sorted : bool, optional
        If False, values of `x` can be in any order and they are sorted first.
        If True, `x` has to be an array of monotonically increasing values.

    Attributes
    ----------
    fill_value

    Methods
    -------
    __call__

    See Also
    --------
    splrep, splev
        Spline interpolation/smoothing based on FITPACK.
    UnivariateSpline : An object-oriented wrapper of the FITPACK routines.
    interp2d : 2-D interpolation

    Examples
    --------
    >>> import matplotlib.pyplot as plt
    >>> from scipy import interpolate
    >>> x = np.arange(0, 10)
    >>> y = np.exp(-x/3.0)
    >>> f = interpolate.interp1d(x, y)

    >>> xnew = np.arange(0, 9, 0.1)
    >>> ynew = f(xnew)   # use interpolation function returned by `interp1d`
    >>> plt.plot(x, y, 'o', xnew, ynew, '-')
    >>> plt.show()
    """

    def __init__(self, x, y, kind='linear', axis=-1,
                 copy=True, bounds_error=None, fill_value=np.nan,
                 assume_sorted=False):
        """ Initialize a 1D linear interpolation class."""
        _Interpolator1D.__init__(self, x, y, axis=axis)

        self.bounds_error = bounds_error  # used by fill_value setter
        self.copy = copy

        if kind in ['zero', 'slinear', 'quadratic', 'cubic']:
            order = {'zero': 0, 'slinear': 1,
                     'quadratic': 2, 'cubic': 3}[kind]
            kind = 'spline'
        elif isinstance(kind, int):
            order = kind
            kind = 'spline'
        elif kind not in ('linear', 'nearest', 'previous', 'next'):
            raise NotImplementedError("%s is unsupported: Use fitpack "
                                      "routines for other types." % kind)
        x = array(x, copy=self.copy)
        y = array(y, copy=self.copy)

        if not assume_sorted:
            ind = np.argsort(x)
            x = x[ind]
            y = np.take(y, ind, axis=axis)

        if x.ndim != 1:
            raise ValueError("the x array must have exactly one dimension.")
        if y.ndim == 0:
            raise ValueError("the y array must have at least one dimension.")

        # Force-cast y to a floating-point type, if it's not yet one
        if not issubclass(y.dtype.type, np.inexact):
            y = y.astype(np.float_)

        # Backward compatibility
        self.axis = axis % y.ndim

        # Interpolation goes internally along the first axis
        self.y = y
        self._y = self._reshape_yi(self.y)
        self.x = x
        del y, x  # clean up namespace to prevent misuse; use attributes
        self._kind = kind
        self.fill_value = fill_value  # calls the setter, can modify bounds_err

        # Adjust to interpolation kind; store reference to *unbound*
        # interpolation methods, in order to avoid circular references to self
        # stored in the bound instance methods, and therefore delayed garbage
        # collection.  See: https://docs.python.org/reference/datamodel.html
        if kind in ('linear', 'nearest', 'previous', 'next'):
            # Make a "view" of the y array that is rotated to the interpolation
            # axis.
            minval = 2
            if kind == 'nearest':
                # Do division before addition to prevent possible integer
                # overflow
                self.x_bds = self.x / 2.0
                self.x_bds = self.x_bds[1:] + self.x_bds[:-1]

                self._call = self.__class__._call_nearest
            elif kind == 'previous':
                # Side for np.searchsorted and index for clipping
                self._side = 'left'
                self._ind = 0
                # Move x by one floating point value to the left
                self._x_shift = np.nextafter(self.x, -np.inf)
                self._call = self.__class__._call_previousnext
            elif kind == 'next':
                self._side = 'right'
                self._ind = 1
                # Move x by one floating point value to the right
                self._x_shift = np.nextafter(self.x, np.inf)
                self._call = self.__class__._call_previousnext
            else:
                # Check if we can delegate to numpy.interp (2x-10x faster).
                cond = self.x.dtype == np.float_ and self.y.dtype == np.float_
                cond = cond and self.y.ndim == 1
                cond = cond and not _do_extrapolate(fill_value)

                if cond:
                    self._call = self.__class__._call_linear_np
                else:
                    self._call = self.__class__._call_linear
        else:
            minval = order + 1

            rewrite_nan = False
            xx, yy = self.x, self._y
            if order > 1:
                # Quadratic or cubic spline. If input contains even a single
                # nan, then the output is all nans. We cannot just feed data
                # with nans to make_interp_spline because it calls LAPACK.
                # So, we make up a bogus x and y with no nans and use it
                # to get the correct shape of the output, which we then fill
                # with nans.
                # For slinear or zero order spline, we just pass nans through.
                if np.isnan(self.x).any():
                    xx = np.linspace(min(self.x), max(self.x), len(self.x))
                    rewrite_nan = True
                if np.isnan(self._y).any():
                    yy = np.ones_like(self._y)
                    rewrite_nan = True

            self._spline = make_interp_spline(xx, yy, k=order,
                                              check_finite=False)
            if rewrite_nan:
                self._call = self.__class__._call_nan_spline
            else:
                self._call = self.__class__._call_spline

        if len(self.x) < minval:
            raise ValueError("x and y arrays must have at "
                             "least %d entries" % minval)

    @property
    def fill_value(self):
        """The fill value."""
        # backwards compat: mimic a public attribute
        return self._fill_value_orig

    @fill_value.setter
    def fill_value(self, fill_value):
        # extrapolation only works for nearest neighbor and linear methods
        if _do_extrapolate(fill_value):
            if self.bounds_error:
                raise ValueError("Cannot extrapolate and raise "
                                 "at the same time.")
            self.bounds_error = False
            self._extrapolate = True
        else:
            broadcast_shape = (self.y.shape[:self.axis] +
                               self.y.shape[self.axis + 1:])
            if len(broadcast_shape) == 0:
                broadcast_shape = (1,)
            # it's either a pair (_below_range, _above_range) or a single value
            # for both above and below range
            if isinstance(fill_value, tuple) and len(fill_value) == 2:
                below_above = [np.asarray(fill_value[0]),
                               np.asarray(fill_value[1])]
                names = ('fill_value (below)', 'fill_value (above)')
                for ii in range(2):
                    below_above[ii] = _check_broadcast_up_to(
                        below_above[ii], broadcast_shape, names[ii])
            else:
                fill_value = np.asarray(fill_value)
                below_above = [_check_broadcast_up_to(
                    fill_value, broadcast_shape, 'fill_value')] * 2
            self._fill_value_below, self._fill_value_above = below_above
            self._extrapolate = False
            if self.bounds_error is None:
                self.bounds_error = True
        # backwards compat: fill_value was a public attr; make it writeable
        self._fill_value_orig = fill_value

    def _call_linear_np(self, x_new):
        # Note that out-of-bounds values are taken care of in self._evaluate
        return np.interp(x_new, self.x, self.y)

    def _call_linear(self, x_new):
        # 2. Find where in the original data, the values to interpolate
        #    would be inserted.
        #    Note: If x_new[n] == x[m], then m is returned by searchsorted.
        x_new_indices = searchsorted(self.x, x_new)

        # 3. Clip x_new_indices so that they are within the range of
        #    self.x indices and at least 1.  Removes mis-interpolation
        #    of x_new[n] = x[0]
        x_new_indices = x_new_indices.clip(1, len(self.x)-1).astype(int)

        # 4. Calculate the slope of regions that each x_new value falls in.
        lo = x_new_indices - 1
        hi = x_new_indices

        x_lo = self.x[lo]
        x_hi = self.x[hi]
        y_lo = self._y[lo]
        y_hi = self._y[hi]

        # Note that the following two expressions rely on the specifics of the
        # broadcasting semantics.
        slope = (y_hi - y_lo) / (x_hi - x_lo)[:, None]

        # 5. Calculate the actual value for each entry in x_new.
        y_new = slope*(x_new - x_lo)[:, None] + y_lo

        return y_new

    def _call_nearest(self, x_new):
        """ Find nearest neighbour interpolated y_new = f(x_new)."""

        # 2. Find where in the averaged data the values to interpolate
        #    would be inserted.
        #    Note: use side='left' (right) to searchsorted() to define the
        #    halfway point to be nearest to the left (right) neighbour
        x_new_indices = searchsorted(self.x_bds, x_new, side='left')

        # 3. Clip x_new_indices so that they are within the range of x indices.
        x_new_indices = x_new_indices.clip(0, len(self.x)-1).astype(intp)

        # 4. Calculate the actual value for each entry in x_new.
        y_new = self._y[x_new_indices]

        return y_new

    def _call_previousnext(self, x_new):
        """Use previous/next neighbour of x_new, y_new = f(x_new)."""

        # 1. Get index of left/right value
        x_new_indices = searchsorted(self._x_shift, x_new, side=self._side)

        # 2. Clip x_new_indices so that they are within the range of x indices.
        x_new_indices = x_new_indices.clip(1-self._ind,
                                           len(self.x)-self._ind).astype(intp)

        # 3. Calculate the actual value for each entry in x_new.
        y_new = self._y[x_new_indices+self._ind-1]

        return y_new

    def _call_spline(self, x_new):
        return self._spline(x_new)

    def _call_nan_spline(self, x_new):
        out = self._spline(x_new)
        out[...] = np.nan
        return out

    def _evaluate(self, x_new):
        # 1. Handle values in x_new that are outside of x.  Throw error,
        #    or return a list of mask array indicating the outofbounds values.
        #    The behavior is set by the bounds_error variable.
        x_new = asarray(x_new)
        y_new = self._call(self, x_new)
        if not self._extrapolate:
            below_bounds, above_bounds = self._check_bounds(x_new)
            if len(y_new) > 0:
                # Note fill_value must be broadcast up to the proper size
                # and flattened to work here
                y_new[below_bounds] = self._fill_value_below
                y_new[above_bounds] = self._fill_value_above
        return y_new

    def _check_bounds(self, x_new):
        """Check the inputs for being in the bounds of the interpolated data.

        Parameters
        ----------
        x_new : array

        Returns
        -------
        out_of_bounds : bool array
            The mask on x_new of values that are out of the bounds.
        """

        # If self.bounds_error is True, we raise an error if any x_new values
        # fall outside the range of x.  Otherwise, we return an array indicating
        # which values are outside the boundary region.
        below_bounds = x_new < self.x[0]
        above_bounds = x_new > self.x[-1]

        # !! Could provide more information about which values are out of bounds
        if self.bounds_error and below_bounds.any():
            raise ValueError("A value in x_new is below the interpolation "
                             "range.")
        if self.bounds_error and above_bounds.any():
            raise ValueError("A value in x_new is above the interpolation "
                             "range.")

        # !! Should we emit a warning if some values are out of bounds?
        # !! matlab does not.
        return below_bounds, above_bounds
