import numpy as np
import math
from scipy.cluster.vq import kmeans2, whiten

class KMeans():

    def __init__(self):
        self.name = "K-Means Cluster Analysis Function"
        self.description = "This function performs K-Means Cluster Analysis"

    def getParameterInfo(self):
        return [
            {
                'name': 'raster',
                'dataType': 'raster',
                'value': None,
                'required': True,
                'displayName': "Input Raster",
                'description': "A single-band raster where to be used for K-Means Cluster Analysis."
            },
            {
                'name': 'cluster',
                'dataType': 'numeric',
                'value': 14,
                'required': True,
                'displayName': "Number of Clusters",
                'description': "Number of Clusters."
            },
            {
                'name': 'iter',
                'dataType': 'numeric',
                'value': 30,
                'required': True,
                'displayName': "Number of Iterations",
                'description': "Number of Iterations."
            },

        ]

    def getConfiguration(self, **scalars):
        return {
          'inheritProperties':  2 | 4 | 8,      # inherit everything but the pixel type (1)
          'invalidateProperties': 2 | 4 | 8,    # invalidate these aspects because we are modifying pixel values and updating key properties.
          'padding': 0,                         # no extra padding of the input pixel block
          'inputMask': False                    # we don't need the input mask in .updatePixels()
        }

    def updateRasterInfo(self, **kwargs):
        self.cluster = kwargs.get('cluster', 14)
        self.iter    = kwargs.get('iter', 30)

        kwargs['output_info']['bandCount'] = 1
        kwargs['output_info']['pixelType'] = 'f4'
        kwargs['output_info']['statistics'] = ({'minimum': 0 , 'maximum': (self.cluster-1)})
        kwargs['output_info']['histogram'] = ()
        kwargs['output_info']['colormap'] = ()
        return kwargs


    def updatePixels(self, tlc, shape, props, **pixelBlocks):
        k = np.array(pixelBlocks['raster_pixels'], dtype ='f4', copy=False)
        output = kmeans2(whiten(k.ravel()),int(self.cluster),int(self.iter),minit = 'points')[1].reshape(k.shape)
        pixelBlocks['output_pixels'] = output.astype(props['pixelType'], copy=False)
        return pixelBlocks

    def updateKeyMetadata(self, names, bandIndex, **keyMetadata):
        if bandIndex == -1:                             # dataset-level properties
            keyMetadata['datatype'] = 'Processed'       # outgoing dataset is now 'Processed'
        elif bandIndex == 0:                            # properties for the first band
            keyMetadata['wavelengthmin'] = None         # reset inapplicable band-specific key metadata
            keyMetadata['wavelengthmax'] = None
            keyMetadata['bandname'] = 'KMeans'
        return keyMetadata

# ----- ## ----- ## ----- ## ----- ## ----- ## ----- ## ----- ## ----- ##

"""
References:
    [1]. Wikipedia : K-means Clustering.
    http://en.wikipedia.org/wiki/K-means_clustering
"""
