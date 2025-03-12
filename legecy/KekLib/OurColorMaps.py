"""

    CmapAlbulaLike.py

    

        COLORMAP
            http://colormap.org/

        custom_cmap.py
            http://matplotlib.org/examples/pylab_examples/custom_cmap.html

"""
from matplotlib.colors import LinearSegmentedColormap

class CmapAlbulaLikeDynamic( LinearSegmentedColormap ):
    def __init__( self, mean = 0.5 ):
        self.mean = mean
        cmap_param = self.compute_cmap_param( mean )
        LinearSegmentedColormap.__init__( self, 'ALBULA_like', cmap_param )

    def compute_cmap_param( self, mean ):

        # TODO: better mappin when when < 0.5
        mean = max( 0.42, mean )
        mean = min( 0.73, mean )
        tp1 = mean - 0.25
        tp2 = mean - 0.10
        tp3 = mean - 0.00
        tp4 = mean + 0.00
        tp5 = mean + 0.10
        tp6 = mean + 0.25
        # print( 'mean=%g, tp=(%g, %g, %g, %g, %g, %g)' % ( mean, tp1, tp2, tp3, tp4, tp5, tp6 ) )
        tp1_touple = ( tp1,  0.9, 0.9 )
        tp2_touple = ( tp2,  0.7, 0.7 )
        tp3_touple = ( tp3,  0.0, 0.0 )
        tp4_touple = ( tp4,  0.0, 0.0 )
        tp5_touple = ( tp5,  0.1, 0.1 )

        cmap_param = {
            'red':      ((0.0,  1.0, 1.0),
                         (0.15, 1.0, 1.0),
                         tp1_touple,
                         tp2_touple,
                         tp3_touple,
                         tp4_touple,
                         tp5_touple,
                         (tp6,  1.0, 1.0),
                         (1.0,  1.0, 1.0)),
            'green':    ((0.0,  1.0, 1.0),
                         (0.15, 1.0, 1.0),
                         tp1_touple,
                         tp2_touple,
                         tp3_touple,
                         tp4_touple,
                         tp5_touple,
                         (tp6,  0.0, 0.0),
                         (1.0,  1.0, 1.0)),
            'blue':     ((0.0,  1.0, 1.0),
                         (0.15, 1.0, 1.0),
                         tp1_touple,
                         tp2_touple,
                         tp4_touple,
                         (1.0,  0.0, 0.0)),
            }
        return cmap_param

    def adjusted_cmap( self, delta ):
        return CmapAlbulaLikeDynamic( self.mean + delta )

class Diverging( LinearSegmentedColormap ):
    def __init__( self ):
        cmap_param = {

            'red' : (
                ( 0,0.231373,0.231373 ),
                ( 0.03125,0.266667,0.266667 ),
                ( 0.0625,0.305882,0.305882 ),
                ( 0.09375,0.345098,0.345098 ),
                ( 0.125,0.384314,0.384314 ),
                ( 0.15625,0.423529,0.423529 ),
                ( 0.1875,0.466667,0.466667 ),
                ( 0.21875,0.509804,0.509804 ),
                ( 0.25,0.552941,0.552941 ),
                ( 0.28125,0.596078,0.596078 ),
                ( 0.3125,0.639216,0.639216 ),
                ( 0.34375,0.682353,0.682353 ),
                ( 0.375,0.721569,0.721569 ),
                ( 0.40625,0.760784,0.760784 ),
                ( 0.4375,0.8,0.8 ),
                ( 0.46875,0.835294,0.835294 ),
                ( 0.5,0.866667,0.866667 ),
                ( 0.53125,0.898039,0.898039 ),
                ( 0.5625,0.92549,0.92549 ),
                ( 0.59375,0.945098,0.945098 ),
                ( 0.625,0.960784,0.960784 ),
                ( 0.65625,0.968627,0.968627 ),
                ( 0.6875,0.968627,0.968627 ),
                ( 0.71875,0.968627,0.968627 ),
                ( 0.75,0.956863,0.956863 ),
                ( 0.78125,0.945098,0.945098 ),
                ( 0.8125,0.92549,0.92549 ),
                ( 0.84375,0.898039,0.898039 ),
                ( 0.875,0.870588,0.870588 ),
                ( 0.90625,0.835294,0.835294 ),
                ( 0.9375,0.796078,0.796078 ),
                ( 0.96875,0.752941,0.752941 ),
                ( 1,0.705882,0.705882 )
            ),

            'green' : (
                ( 0,0.298039,0.298039 ),
                ( 0.03125,0.352941,0.352941 ),
                ( 0.0625,0.407843,0.407843 ),
                ( 0.09375,0.458824,0.458824 ),
                ( 0.125,0.509804,0.509804 ),
                ( 0.15625,0.556863,0.556863 ),
                ( 0.1875,0.603922,0.603922 ),
                ( 0.21875,0.647059,0.647059 ),
                ( 0.25,0.690196,0.690196 ),
                ( 0.28125,0.72549,0.72549 ),
                ( 0.3125,0.760784,0.760784 ),
                ( 0.34375,0.788235,0.788235 ),
                ( 0.375,0.815686,0.815686 ),
                ( 0.40625,0.835294,0.835294 ),
                ( 0.4375,0.85098,0.85098 ),
                ( 0.46875,0.858824,0.858824 ),
                ( 0.5,0.866667,0.866667 ),
                ( 0.53125,0.847059,0.847059 ),
                ( 0.5625,0.827451,0.827451 ),
                ( 0.59375,0.8,0.8 ),
                ( 0.625,0.768627,0.768627 ),
                ( 0.65625,0.733333,0.733333 ),
                ( 0.6875,0.694118,0.694118 ),
                ( 0.71875,0.65098,0.65098 ),
                ( 0.75,0.603922,0.603922 ),
                ( 0.78125,0.552941,0.552941 ),
                ( 0.8125,0.498039,0.498039 ),
                ( 0.84375,0.439216,0.439216 ),
                ( 0.875,0.380392,0.380392 ),
                ( 0.90625,0.313725,0.313725 ),
                ( 0.9375,0.243137,0.243137 ),
                ( 0.96875,0.156863,0.156863 ),
                ( 1,0.0156863,0.0156863 )
            ),

            'blue' : (
                ( 0,0.752941,0.752941 ),
                ( 0.03125,0.8,0.8 ),
                ( 0.0625,0.843137,0.843137 ),
                ( 0.09375,0.882353,0.882353 ),
                ( 0.125,0.917647,0.917647 ),
                ( 0.15625,0.945098,0.945098 ),
                ( 0.1875,0.968627,0.968627 ),
                ( 0.21875,0.984314,0.984314 ),
                ( 0.25,0.996078,0.996078 ),
                ( 0.28125,1,1 ),
                ( 0.3125,1,1 ),
                ( 0.34375,0.992157,0.992157 ),
                ( 0.375,0.976471,0.976471 ),
                ( 0.40625,0.956863,0.956863 ),
                ( 0.4375,0.933333,0.933333 ),
                ( 0.46875,0.901961,0.901961 ),
                ( 0.5,0.866667,0.866667 ),
                ( 0.53125,0.819608,0.819608 ),
                ( 0.5625,0.776471,0.776471 ),
                ( 0.59375,0.72549,0.72549 ),
                ( 0.625,0.678431,0.678431 ),
                ( 0.65625,0.627451,0.627451 ),
                ( 0.6875,0.580392,0.580392 ),
                ( 0.71875,0.529412,0.529412 ),
                ( 0.75,0.482353,0.482353 ),
                ( 0.78125,0.435294,0.435294 ),
                ( 0.8125,0.388235,0.388235 ),
                ( 0.84375,0.341176,0.341176 ),
                ( 0.875,0.298039,0.298039 ),
                ( 0.90625,0.258824,0.258824 ),
                ( 0.9375,0.219608,0.219608 ),
                ( 0.96875,0.184314,0.184314 ),
                ( 1,0.14902,0.14902 )
            )
        }

        LinearSegmentedColormap.__init__( self, 'Diverging', cmap_param )

    def adjusted_cmap( self, delta ):
        # no adjustment
        return Diverging()
