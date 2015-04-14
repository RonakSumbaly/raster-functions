import numpy as np
from scipy import ndimage as ndi
import math

class EstimatorFilter():

    def __init__(self):
        self.name = "Estimator Filter"
        self.description = "Function applies an order statistic noise-reduction filter to a single - band raster."

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
                'name': 'mode',
                'dataType': 'string',
                'value': 'Median',
                'required': True,
                'domain': ('Median','Mid Point'),
                'displayName': "Mode",
                'description': "Select Mode for Estimator Filter."
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
        self.mode = kwargs.get("mode","Median")
        kwargs['output_info']['bandCount'] = 1
        kwargs['output_info']['pixelType'] = kwargs['raster_info']['pixelType']
        kwargs['output_info']['statistics'] = ()
        kwargs['output_info']['histogram'] = ()
        kwargs['output_info']['colormap'] = ()

        return kwargs


    def updatePixels(self, tlc, shape, props, **pixelBlocks):
        raster = np.array(pixelBlocks['raster_pixels'], dtype ='f4', copy=False)
        if self.mode == "Median":
            raster = ndi.generic_filter(raster,np.median,size=3)
        else:
            rastermin = ndi.generic_filter(raster,np.min,size=3)
            rastermax = ndi.generic_filter(raster,np.max,size=3)
            raster = (rastermin+rastermax)/2


        pixelBlocks['output_pixels'] = raster.astype(props['pixelType'], copy=False)
        return pixelBlocks


    def updateKeyMetadata(self, names, bandIndex, **keyMetadata):
        if bandIndex == -1:                             # dataset-level properties
            keyMetadata['datatype'] = 'Processed'       # outgoing dataset is now 'Processed'
        elif bandIndex == 0:                            # properties for the first band
            keyMetadata['wavelengthmin'] = None         # reset inapplicable band-specific key metadata
            keyMetadata['wavelengthmax'] = None
            keyMetadata['bandname'] = 'EstimatorFilter'
        return keyMetadata

# ----- ## ----- ## ----- ## ----- ## ----- ## ----- ## ----- ## ----- ##

"""
References:
    [1]. Exelis : Estimator_Filter.
    http://www.exelisvis.com/docs/ESTIMATOR_FILTER.html
"""
