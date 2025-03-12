"""
    CupyUtils.CupyWrapper.ndimage.measurements.py
    
"""
import numpy as np
from scipy import ndimage
import cupy as cp
from CupyUtils.NumpyWrapper import searchsorted

def _safely_castable_to_int(dt):
    """Test whether the numpy data type `dt` can be safely cast to an int."""
    int_size = cp.dtype(int).itemsize
    safe = ((cp.issubdtype(dt, cp.signedinteger) and dt.itemsize <= int_size) or
            (cp.issubdtype(dt, cp.unsignedinteger) and dt.itemsize < int_size))
    return safe

def _stats(input, labels=None, index=None, centered=False):
    """Count, sum, and optionally compute (sum - centre)^2 of input by label

    Parameters
    ----------
    input : array_like, n-dimensional
        The input data to be analyzed.
    labels : array_like (n-dimensional), optional
        The labels of the data in `input`.  This array must be broadcast
        compatible with `input`; typically it is the same shape as `input`.
        If `labels` is None, all nonzero values in `input` are treated as
        the single labeled group.
    index : label or sequence of labels, optional
        These are the labels of the groups for which the stats are computed.
        If `index` is None, the stats are computed for the single group where
        `labels` is greater than 0.
    centered : bool, optional
        If True, the centered sum of squares for each labeled group is
        also returned.  Default is False.

    Returns
    -------
    counts : int or ndarray of ints
        The number of elements in each labeled group.
    sums : scalar or ndarray of scalars
        The sums of the values in each labeled group.
    sums_c : scalar or ndarray of scalars, optional
        The sums of mean-centered squares of the values in each labeled group.
        This is only returned if `centered` is True.

    """
    def single_group(vals):
        if centered:
            vals_c = vals - vals.mean()
            return vals.size, vals.sum(), (vals_c * vals_c.conjugate()).sum()
        else:
            return vals.size, vals.sum()

    if labels is None:
        return single_group(input)

    # ensure input and labels match sizes
    input, labels = cp.broadcast_arrays(input, labels)

    if index is None:
        return single_group(input[labels > 0])

    if cp.isscalar(index):
        return single_group(input[labels == index])

    def _sum_centered(labels):
        # `labels` is expected to be an ndarray with the same shape as `input`.
        # It must contain the label indices (which are not necessarily the labels
        # themselves).
        means = sums / counts
        centered_input = input - means[labels]
        # bincount expects 1d inputs, so we ravel the arguments.
        bc = numpy.bincount(labels.ravel(),
                              weights=(centered_input *
                                       centered_input.conjugate()).ravel())
        return bc

    # Remap labels to unique integers if necessary, or if the largest
    # label is larger than the number of values.

    if (not _safely_castable_to_int(labels.dtype) or
            labels.min() < 0 or labels.max() > labels.size):
        # Use numpy.unique to generate the label indices.  `new_labels` will
        # be 1-d, but it should be interpreted as the flattened n-d array of
        # label indices.
        unique_labels, new_labels = cp.unique(labels, return_inverse=True)
        counts = cp.bincount(new_labels)
        sums = cp.bincount(new_labels, weights=input.ravel())
        if centered:
            # Compute the sum of the mean-centered squares.
            # We must reshape new_labels to the n-d shape of `input` before
            # passing it _sum_centered.
            sums_c = _sum_centered(new_labels.reshape(labels.shape))
        idxs = searchsorted(unique_labels, index)
        # make all of idxs valid
        idxs[idxs >= unique_labels.size] = 0
        found = (unique_labels[idxs] == index)
    else:
        # labels are an integer type allowed by bincount, and there aren't too
        # many, so call bincount directly.
        counts = cp.bincount(labels.ravel())
        sums = cp.bincount(labels.ravel(), weights=input.ravel())
        if centered:
            sums_c = _sum_centered(labels)
        # make sure all index values are valid
        idxs = cp.asanyarray(index, np.int).copy()
        found = (idxs >= 0) & (idxs < counts.size)
        idxs[~found] = 0

    counts = counts[idxs]
    counts[~found] = 0
    sums = sums[idxs]
    sums[~found] = 0

    if not centered:
        return (counts, sums)
    else:
        sums_c = sums_c[idxs]
        sums_c[~found] = 0
        return (counts, sums, sums_c)

def _sum(input, labels=None, index=None):
    """
    Calculate the sum of the values of the array.

    Parameters
    ----------
    input : array_like
        Values of `input` inside the regions defined by `labels`
        are summed together.
    labels : array_like of ints, optional
        Assign labels to the values of the array. Has to have the same shape as
        `input`.
    index : array_like, optional
        A single label number or a sequence of label numbers of
        the objects to be measured.

    Returns
    -------
    sum : ndarray or scalar
        An array of the sums of values of `input` inside the regions defined
        by `labels` with the same shape as `index`. If 'index' is None or scalar,
        a scalar is returned.

    See also
    --------
    mean, median

    Examples
    --------
    >>> from scipy import ndimage
    >>> input =  [0,1,2,3]
    >>> labels = [1,1,2,2]
    >>> ndimage.sum(input, labels, index=[1,2])
    [1.0, 5.0]
    >>> ndimage.sum(input, labels, index=1)
    1
    >>> ndimage.sum(input, labels)
    6


    """
    count, sum = _stats(input, labels, index)
    return sum

def mean(input, labels=None, index=None):
    """
    Calculate the mean of the values of an array at labels.

    Parameters
    ----------
    input : array_like
        Array on which to compute the mean of elements over distinct
        regions.
    labels : array_like, optional
        Array of labels of same shape, or broadcastable to the same shape as
        `input`. All elements sharing the same label form one region over
        which the mean of the elements is computed.
    index : int or sequence of ints, optional
        Labels of the objects over which the mean is to be computed.
        Default is None, in which case the mean for all values where label is
        greater than 0 is calculated.

    Returns
    -------
    out : list
        Sequence of same length as `index`, with the mean of the different
        regions labeled by the labels in `index`.

    See also
    --------
    variance, standard_deviation, minimum, maximum, sum, label

    Examples
    --------
    >>> from scipy import ndimage
    >>> a = np.arange(25).reshape((5,5))
    >>> labels = np.zeros_like(a)
    >>> labels[3:5,3:5] = 1
    >>> index = np.unique(labels)
    >>> labels
    array([[0, 0, 0, 0, 0],
           [0, 0, 0, 0, 0],
           [0, 0, 0, 0, 0],
           [0, 0, 0, 1, 1],
           [0, 0, 0, 1, 1]])
    >>> index
    array([0, 1])
    >>> ndimage.mean(a, labels=labels, index=index)
    [10.285714285714286, 21.0]

    """

    count, sum = _stats(cp.asarray(input), cp.asarray(labels), cp.asarray(index))
    return cp.asnumpy(sum / cp.asanyarray(count).astype(cp.float))

def center_of_mass(input, labels=None, index=None):
    """
    Calculate the center of mass of the values of an array at labels.

    Parameters
    ----------
    input : ndarray
        Data from which to calculate center-of-mass. The masses can either
        be positive or negative.
    labels : ndarray, optional
        Labels for objects in `input`, as generated by `ndimage.label`.
        Only used with `index`.  Dimensions must be the same as `input`.
    index : int or sequence of ints, optional
        Labels for which to calculate centers-of-mass. If not specified,
        all labels greater than zero are used.  Only used with `labels`.

    Returns
    -------
    center_of_mass : tuple, or list of tuples
        Coordinates of centers-of-mass.

    Examples
    --------
    >>> a = np.array(([0,0,0,0],
    ...               [0,1,1,0],
    ...               [0,1,1,0],
    ...               [0,1,1,0]))
    >>> from scipy import ndimage
    >>> ndimage.measurements.center_of_mass(a)
    (2.0, 1.5)

    Calculation of multiple objects in an image

    >>> b = np.array(([0,1,1,0],
    ...               [0,1,0,0],
    ...               [0,0,0,0],
    ...               [0,0,1,1],
    ...               [0,0,1,1]))
    >>> lbl = ndimage.label(b)[0]
    >>> ndimage.measurements.center_of_mass(b, lbl, [1,2])
    [(0.33333333333333331, 1.3333333333333333), (3.5, 2.5)]

    Negative masses are also accepted, which can occur for example when
    bias is removed from measured data due to random noise.

    >>> c = np.array(([-1,0,0,0],
    ...               [0,-1,-1,0],
    ...               [0,1,-1,0],
    ...               [0,1,1,0]))
    >>> ndimage.measurements.center_of_mass(c)
    (-4.0, 1.0)

    If there are division by zero issues, the function does not raise an
    error but rather issues a RuntimeWarning before returning inf and/or NaN.

    >>> d = np.array([-1, 1])
    >>> ndimage.measurements.center_of_mass(d)
    (inf,)
    """
    labels_ = None if labels is None else cp.asarray(labels)
    index_ = None if index is None else cp.asarray(index)
    return _center_of_mass(cp.asarray(input), labels_, index_)

def _center_of_mass(input, labels=None, index=None):
    normalizer = _sum(input, labels, index)
    grids = cp.ogrid[[slice(0, i) for i in input.shape]]

    results_ = [cp.asnumpy(_sum(input * grids[dir].astype(float), labels, index) / normalizer)
               for dir in range(input.ndim)]

    results = np.array(results_)

    if np.isscalar(results[0]):
        return tuple(results)

    return [tuple(v) for v in results.T]
