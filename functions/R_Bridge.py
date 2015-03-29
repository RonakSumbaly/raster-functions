import rpy2.robjects as robjects
import rpy2.robjects.numpy2ri
import numpy as np


class R_Bridge():
    def __init__(self):
        self.name = "R Bridge Function"
        self.description = "This function exists a R Bridge between Python Raster Function and R Script"
        rpy2.robjects.numpy2ri.activate()       # enable conversion of numpy to R matrix


    def getParameterInfo(self):
        return [
            {
                'name': 'raster',
                'dataType': 'raster',
                'value': None,
                'required': True,
                'displayName': "Input Raster",
                'description': "Input raster for manipulation."
            },
            {
                'name': 'addr',
                'dataType': 'string',
                'value': 'Temperature Conversion',
                'required': True,
                'domain': ('Temperature Conversion','Elevation Limit'),
                'displayName': "R Script",
                'description': "Location of the R Script"
            },
            {
                'name': 'par1',
                'dataType': 'numeric',
                'value': 1.0,
                'required': True,
                'displayName': "Parameter",
                'description': "Temperature Conversion : {0 - Celsius to Fahrenheit , 1 - Fahrenheit to Celsius} , Elevation Limit : {elevation limit}."
            },
        ]

    def getConfiguration(self, **scalars):
        return {
          'inheritProperties': 2 | 4 | 8,       # inherit everything but the pixel type (1)
          'invalidateProperties': 2 | 4 | 8,    # invalidate these aspects because we are modifying pixel values and updating key properties.
          'padding': 0,                         # no padding of the input pixel block
          'inputMask': False                    # we don't need the input mask in .updatePixels()
        }

    def updateRasterInfo(self, **kwargs):
        kwargs['output_info']['bandCount'] = 1
        kwargs['output_info']['statistics'] = ()
        kwargs['output_info']['histogram'] = ()
        kwargs['output_info']['pixelType'] = 'f4'

        self.noData = kwargs['raster_info']['noData'][0]
        self.addr = kwargs.get('addr')
        self.value = kwargs.get('par1',1.0)
        r_source = robjects.r['source']
        if (self.addr == "Temperature Conversion"):
            r_source('TemperatureConversion.r')
            self.getname = robjects.globalenv['temperatureConversion']
        else:
            r_source('ElevationLimit.r')
            self.getname = robjects.globalenv['elevationLimit']
        return kwargs

    def updatePixels(self, tlc, shape, props, **pixelBlocks):
        r = np.array(pixelBlocks['raster_pixels'], dtype ='f4')
        r1 = self.getname(r,self.value,self.noData)
        r1 = np.array(r1,dtype = 'f4').reshape(r.shape)

        pixelBlocks['output_pixels'] = r1.astype(props['pixelType'])
        return pixelBlocks
