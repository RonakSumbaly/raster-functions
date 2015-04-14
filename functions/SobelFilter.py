import numpy as np
from scipy import ndimage as ndi
import math

class SobelFilter():

    def __init__(self):
        self.name = "Sobel Filter"
        self.description = "Reduces degradation and noise in an image using Wiener Filter."

    def getParameterInfo(self):
        return [
            {
                'name': 'raster',
                'dataType': 'raster',
                'value': None,
                'required': True,
                'displayName': "Input Raster",
                'description': "A single-band input raster for applying the Gabor Filter."
            },
        ]

    def getConfiguration(self, **scalars):
        return {
          'inheritProperties':  1 | 2 | 4 | 8,      # inherit everything but the pixel type (1) and NoData (2)
          'invalidateProperties': 2 | 4 | 8,        # invalidate these aspects because we are modifying pixel values and updating key properties.
          'padding': 0,                             # no padding of the input pixel block
          'inputMask': False                        # we don't need the input mask in .updatePixels()
        }

    def updateRasterInfo(self, **kwargs):

        kwargs['output_info']['bandCount'] = kwargs['raster_info']['bandCount']
        kwargs['output_info']['pixelType'] = kwargs['raster_info']['pixelType']
        kwargs['output_info']['statistics'] = ()
        kwargs['output_info']['histogram'] = ()
        kwargs['output_info']['colormap'] = ()

        return kwargs


    def updatePixels(self, tlc, shape, props, **pixelBlocks):
        raster = np.array(pixelBlocks['raster_pixels'], dtype ='f4', copy=False)
        dx = ndi.sobel(raster, 1)  # horizontal derivative
        dy = ndi.sobel(raster, 0)  # vertical derivative
        mag = np.hypot(dx, dy)  # magnitude
        pixelBlocks['output_pixels'] = mag.astype(props['pixelType'], copy=False)
        return pixelBlocks


    def updateKeyMetadata(self, names, bandIndex, **keyMetadata):
        if bandIndex == -1:                             # dataset-level properties
            keyMetadata['datatype'] = 'Processed'       # outgoing dataset is now 'Processed'
        elif bandIndex == 0:                            # properties for the first band
            keyMetadata['wavelengthmin'] = None         # reset inapplicable band-specific key metadata
            keyMetadata['wavelengthmax'] = None
            keyMetadata['bandname'] = 'SobelFilter'
        return keyMetadata

# ----- ## ----- ## ----- ## ----- ## ----- ## ----- ## ----- ## ----- ##

"""
References:
    [1]. Wikipedia: Sobel Operator.
    http://en.wikipedia.org/wiki/Sobel_operator
"""
