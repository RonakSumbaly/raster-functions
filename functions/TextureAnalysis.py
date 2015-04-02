from scipy import ndimage as ndi
from scipy.stats import kurtosis , skew
import numpy as np
import math

class TextureAnalysis():

    def __init__(self):
        self.name = "Texture Analysis Function"
        self.description = ""

    def getParameterInfo(self):
        return [
            {
                'name': 'raster',
                'dataType': 'raster',
                'value': None,
                'required': True,
                'displayName': "Input Raster",
                'description': "Raster for texture analysis.",
            },
            {
                'name': 'op',
                'dataType': 'string',
                'value': 'Variance',
                'required': True,
                'domain': ('Variance', 'Skewness', 'Kurtosis'),
                'displayName': "Operator",
                'description': "Select the mathematical formula to use for texture analysis."
            },
            {
                'name': 'win',
                'dataType': 'numeric',
                'value': 3,
                'required': True,
                'displayName': "Moving Window Size",
                'description': ("Enter the moving window size. Must be an odd number. If you enter an even number, function automatically adds one (+1) to make the number odd.")
            },
        ]

    def getConfiguration(self, **scalars):
        return {
          'inheritProperties': 4 | 8,           # inherit everything but the pixel type (1) and NoData (2)
          'invalidateProperties': 2 | 4 | 8,    # invalidate these aspects because we are modifying pixel values and updating key properties.
          'padding': 0,                         # no padding to the input pixel block.
          'inputMask': False                    # input mask in .updatePixels() not required.
         }


    def updateRasterInfo(self, **kwargs):
        kwargs['output_info']['bandCount'] = kwargs['raster_info']['bandCount']
        kwargs['output_info']['pixelType'] = 'f4'
        kwargs['output_info']['statistics'] = ()
        kwargs['output_info']['histogram'] = ()
        kwargs['output_info']['colormap'] = ()

        self.windowSize = kwargs.get('win', 3)          # moving window size.
        self.windowSize = self.windowSize if (self.windowSize%2 != 0) else self.windowSize+1    # ensure odd window size.

        self.op = kwargs.get('op',"Variance").lower()   # test statistics

        if self.op == "variance"    : self.op = ndi.variance
        elif self.op == "skewness"  : self.op = skew
        else                        : self.op = kurtosis

        return kwargs

    def updatePixels(self, tlc, shape, props, **pixelBlocks):
        r = np.array(pixelBlocks['raster_pixels'], dtype='f4', copy=False)
        if len(r.shape) < 3:
            r  = ndi.generic_filter(r, self.op, self.windowSize)
        else:
            for x in xrange(int(r.shape[0])):
                r[x]  = ndi.generic_filter(r[x], self.op, self.windowSize)
        pixelBlocks['output_pixels'] = r.astype(props['pixelType'], copy=False)
        return pixelBlocks

    def updateKeyMetadata(self, names, bandIndex, **keyMetadata):
        if bandIndex == -1:                             # dataset-level properties
            keyMetadata['datatype'] = 'Processed'       # outgoing dataset is now 'Processed'
        elif bandIndex == 0:                            # properties for the first band
            keyMetadata['wavelengthmin'] = None         # reset inapplicable band-specific key metadata
            keyMetadata['wavelengthmax'] = None
            keyMetadata['bandname'] = 'TextureAnalysis'
        return keyMetadata



