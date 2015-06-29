import math
import numpy as np
from utils import Trace
from scipy import ndimage as ndi


class TerrainRuggednessIndex():

    def __init__(self):
        self.name = "Terrain Ruggedness Index"
        self.description = "This function calculates the TRI that provides an objective quantitative measure of topographic heterogeneity."
        self.trace = Trace()

    def getParameterInfo(self):
        return [
            {
                'name': 'raster',
                'dataType': 'raster',
                'value': None,
                'required': True,
                'displayName': "Input Raster",
                'description': "The primary input raster where pixel values represent elevation."
            },
        ]

    def getConfiguration(self, **scalars):
        return {
          'extractBands': (0,),                 # we only need the first band.  Comma after zero ensures it's a tuple.
          'inheritProperties':  4 | 8,          # inherit everything but the pixel type (1) and NoData (2)
          'invalidateProperties': 2 | 4 | 8,    # invalidate these aspects because we are modifying pixel values and updating key properties.
          'padding': 1,                         # one extra on each each of the input pixel block
          'inputMask': True                     # we need the input mask in .updatePixels()
        }

    def updateRasterInfo(self, **kwargs):
        r = kwargs['raster_info']
        if r['bandCount'] > 1:
            raise Exception("Input raster has more than one band. Only single-band raster datasets are supported")

        kwargs['output_info']['bandCount'] = 1
        kwargs['output_info']['pixelType'] = 'u2'
        kwargs['output_info']['histogram'] = ()
        kwargs['output_info']['resampling'] = False
        kwargs['output_info']['colormap'] = ()

        return kwargs

    def updatePixels(self, tlc, shape, props, **pixelBlocks):
        r = np.array(pixelBlocks['raster_pixels'], dtype='f4', copy=False)
        m = np.array(pixelBlocks['raster_mask'], dtype='u1', copy=False)

        # terrain ruggedness index computation
        s = ndi.uniform_filter(r, size=3) * 9
        t = ndi.uniform_filter(r * r, size=3) * 9
        outBlock = np.sqrt(t + (9 * r * r) - (2 * r * s))

        pixelBlocks['output_pixels'] = outBlock[1:-1, 1:-1].astype(props['pixelType'], copy=False)
        pixelBlocks['output_mask'] = \
            m[:-2, :-2]  & m[1:-1, :-2]  & m[2:, :-2]  \
          & m[:-2, 1:-1] & m[1:-1, 1:-1] & m[2:, 1:-1] \
          & m[:-2, 2:]   & m[1:-1, 2:]   & m[2:, 2:]

        return pixelBlocks

    def updateKeyMetadata(self, names, bandIndex, **keyMetadata):
        if bandIndex == -1:                             # dataset-level properties
            keyMetadata['datatype'] = 'Processed'       # outgoing dataset is now 'Processed'
        elif bandIndex == 0:                            # properties for the first band
            keyMetadata['wavelengthmin'] = None         # reset inapplicable band-specific key metadata
            keyMetadata['wavelengthmax'] = None
            keyMetadata['bandname'] = 'RuggednessIndex'
        return keyMetadata

# ----- ## ----- ## ----- ## ----- ## ----- ## ----- ## ----- ## ----- ##

"""
References:
    [1]. Riley, S. J., S. D. DeGloria and R. Elliot (1999).
    A terrain ruggedness index that quantifies topographic heterogeneity, Intermountain Journal of Sciences, vol. 5, No. 1-4,1999.
    [2]. Blaszczynski, Jacek S., 1997.
    Landform characterization with Geographic Information Systems, Photogrammetric Enginnering and Remote Sensing, vol. 63, no. 2, February 1997, pp. 183-191.
"""
