import numpy as np
from scipy import ndimage as ndi
from scipy import signal
import math

class WienerFilter():

    def __init__(self):
        self.name = "Wiener Filter"
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
            {
                'name': 'win',
                'dataType': 'numeric',
                'value': 3.0,
                'required': True,
                'displayName': "Window Size",
                'description': "Enter size of square data window for computation of Wiener Filter."
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
        self.win = int(kwargs.get("win",3.0))

        kwargs['output_info']['bandCount'] = kwargs['raster_info']['bandCount']
        kwargs['output_info']['pixelType'] = kwargs['raster_info']['pixelType']
        kwargs['output_info']['statistics'] = ()
        kwargs['output_info']['histogram'] = ()
        kwargs['output_info']['colormap'] = ()

        return kwargs


    def updatePixels(self, tlc, shape, props, **pixelBlocks):
        raster = np.array(pixelBlocks['raster_pixels'], dtype ='f4', copy=False)
        raster = signal.wiener(raster,self.win)
        pixelBlocks['output_pixels'] = raster.astype(props['pixelType'], copy=False)
        return pixelBlocks


    def updateKeyMetadata(self, names, bandIndex, **keyMetadata):
        if bandIndex == -1:                             # dataset-level properties
            keyMetadata['datatype'] = 'Processed'       # outgoing dataset is now 'Processed'
        elif bandIndex == 0:                            # properties for the first band
            keyMetadata['wavelengthmin'] = None         # reset inapplicable band-specific key metadata
            keyMetadata['wavelengthmax'] = None
            keyMetadata['bandname'] = 'WienerFilter'
        return keyMetadata

# ----- ## ----- ## ----- ## ----- ## ----- ## ----- ## ----- ## ----- ##

"""
References:
    [1]. Wikipedia: Wiener Deconvolution .
    http://en.wikipedia.org/wiki/Wiener_deconvolution
"""
