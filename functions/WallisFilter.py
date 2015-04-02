import numpy as np
import math
from scipy import ndimage as ndi

class WallisFilter():

    def __init__(self):
        self.name = "Wallis Normalization Function"
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
                'name': 'dsmean',
                'dataType': 'numeric',
                'value': 128.0,
                'required': True,
                'displayName': "Desired Mean",
                'description': ("Enter desired mean for the output image.")
            },
            {
                'name': 'dsstd',
                'dataType': 'numeric',
                'value': 76.8,
                'required': True,
                'displayName': "Desired Standard Deviation",
                'description': ("Enter desired standard deviation for the output image.")
            },
            {
                'name': 'win',
                'dataType': 'numeric',
                'value': 3,
                'required': True,
                'displayName': "Moving Window Size",
                'description': ("Enter size of square data window for computation of local mean and deviation. Must be an odd number. If you enter an even number, function automatically adds one (+1) to make the number odd.")
            },
            {
                'name': 'gain',
                'dataType': 'numeric',
                'value': 6.0,
                'required': True,
                'displayName': "Contrast Expansion (Gain)",
                'description': ("Enter maximum contrast expansion (Gain).")
            },
            {
                'name': 'alpha',
                'dataType': 'numeric',
                'value': 0.8,
                'required': True,
                'displayName': "Brightness Forcing Constant",
                'description': ("Enter factor to govern mean value shifting.")
            },
        ]

    def getConfiguration(self, **scalars):
        return {
          'inheritProperties': 4 | 8,           # inherit everything but the pixel type (1) and NoData (2)
          'invalidateProperties': 2 | 4 | 8,    # invalidate these aspects because we are modifying pixel values and updating key properties.
          'padding': 0,                         # no padding of the input pixel block
          'inputMask': False                    # we don't need the input mask in .updatePixels()
        }


    def updateRasterInfo(self, **kwargs):
        kwargs['output_info']['bandCount'] = 1
        kwargs['output_info']['pixelType'] = 'f4'
        kwargs['output_info']['statistics'] = ()
        kwargs['output_info']['histogram'] = ()
        kwargs['output_info']['colormap'] = ()

        if kwargs['raster_info']['bandCount'] > 1:
            raise Exception("Input raster has more than one band. Only single-band raster datasets are supported.")

        # desired mean
        self.dsMean = kwargs.get('dsmean',128.0)
        if self.dsMean>255.0 or self.dsMean<0.0:
            raise Exception("Desired mean out of range.")

        # desired deviation
        self.dsStd = kwargs.get('dsstd',76.8)
        if self.dsStd>255.0 or self.dsStd<1.0:
            raise Exception("Desired standard deviation out of range.")

        # moving window size
        self.windowSize = int(kwargs.get('win', 3))
        self.windowSize = self.windowSize if (self.windowSize%2 != 0) else self.windowSize+1

        # maximum gain
        self.maxGain = kwargs.get('gain',6.0)
        if self.maxGain > 255.0 or self.maxGain < 0.0:
            raise Exception("Maximum gain out of range.")

        # alpha
        self.alpha = kwargs.get('alpha',0.8)
        if self.alpha < 0.0:
            raise Exception("Alpha out of range.")

        return kwargs

    def updatePixels(self, tlc, shape, props, **pixelBlocks):
        r = np.array(pixelBlocks['raster_pixels'], dtype='f4', copy=False)

        kernel = np.ones((self.windowSize, self.windowSize),np.int16)
        windowPixels = (self.windowSize * self.windowSize)

        ### Calculate local statistics ###
        localmean = ndi.convolve(r, kernel) / windowPixels
        localstddev = ndi.generic_filter(r, np.std,self.windowSize)

        ### Apply Wallis Filter Formula ###
        r = self.alpha * self.dsMean + (1 - self.alpha) * localmean + (r - localmean) * self.dsStd/(self.dsStd/self.maxGain + localstddev)

        pixelBlocks['output_pixels'] = r.astype(props['pixelType'], copy=False)
        return pixelBlocks

    def updateKeyMetadata(self, names, bandIndex, **keyMetadata):
        if bandIndex == -1:                             # dataset-level properties
            keyMetadata[    'datatype'] = 'Processed'       # outgoing dataset is now 'Processed'
        elif bandIndex == 0:                            # properties for the first band
            keyMetadata['wavelengthmin'] = None         # reset inapplicable band-specific key metadata
            keyMetadata['wavelengthmax'] = None
            keyMetadata['bandname'] = 'WallisFilter'
        return keyMetadata
