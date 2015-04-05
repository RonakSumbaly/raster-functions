import numpy as np
import math

class ChangeDetection():

    def __init__(self):
        self.name = "Change Detection Function"
        self.description = ("The operator performs change detection by computing the ratio of log ratio of given image pair. \
                             It is assumed that the input product is a stack of two co-registered images.")

    def getParameterInfo(self):
        return [
            {
                'name': 'raster',
                'dataType': 'raster',
                'value': None,
                'required': True,
                'displayName': "Input Raster",
                'description': "A multi-band raster as input to Change Detection function."
            },
            {
                'name': 'band1',
                'dataType': 'numeric',
                'value': 1,
                'required': True,
                'displayName': "Input Band Number A",
                'description': "First band number of the raster to take as input for Change Detection."
            },
            {
                'name': 'band2',
                'dataType': 'numeric',
                'value': 2,
                'required': True,
                'displayName': "Input Band Number B",
                'description': "Second band number of the raster to take as input for Change Detection."
            },
            {
                'name': 'log',
                'dataType': 'string',
                'value': 'True',
                'required': True,
                'domain': ('True', 'False'),
                'displayName': "Output log ratio",
                'description': "Apply logarithmic ratio in the Change Detection function."
            },


        ]


    def getConfiguration(self, **scalars):
        return {
          'inheritProperties':    4 | 8,        # inherit everything but the pixel type (1) and NoData (2)
          'invalidateProperties': 2 | 4 | 8,    # invalidate these aspects because we are modifying pixel values and updating key properties.
          'padding': 0,                         # no padding on each of the input pixel block
          'inputMask': False                    # we don't need the input mask in .updatePixels()
        }

    def updateRasterInfo(self, **kwargs):
        self.band1 = kwargs.get('band1',1) - 1
        self.band2 = kwargs.get('band2',2) - 1
        self.log   = np.log if kwargs.get('log','True') == "True" else np.double

        if self.band1 > kwargs['raster_info']['bandCount'] or self.band2 > kwargs['raster_info']['bandCount']:
            raise Exception ("Input band number doesn't exist.")

        kwargs['output_info']['bandCount'] = 1
        kwargs['output_info']['pixelType'] = 'f4'
        kwargs['output_info']['noData'] = np.array([0])
        kwargs['output_info']['statistics'] = ()
        kwargs['output_info']['histogram'] = ()
        kwargs['output_info']['colormap'] = ()
        return kwargs

    def updatePixels(self, tlc, shape, props, **pixelBlocks):
        raster1 = np.array(pixelBlocks['raster_pixels'][self.band1], dtype ='f4', copy=False)
        raster2 = np.array(pixelBlocks['raster_pixels'][self.band2], dtype ='f4', copy=False)

        ratio = np.divide(raster1,raster2)         # ratio of input raster bands

        output  = np.where(np.logical_or(np.logical_or(raster1<=0,raster2<=0),\
        np.logical_or(raster1==props['noData'],raster2==props['noData'])),0.0,self.log(np.max(ratio,1.e-15)))       # calculation for change detection

        pixelBlocks['output_pixels'] = output.astype(props['pixelType'], copy=False)

        return pixelBlocks

    def updateKeyMetadata(self, names, bandIndex, **keyMetadata):
        if bandIndex == -1:                             # dataset-level properties
            keyMetadata['datatype'] = 'Processed'       # outgoing dataset is now 'Processed'
        elif bandIndex == 0:                            # properties for the first band
            keyMetadata['wavelengthmin'] = None         # reset inapplicable band-specific key metadata
            keyMetadata['wavelengthmax'] = None
            keyMetadata['bandname'] = 'ChangeDetection'
        return keyMetadata


