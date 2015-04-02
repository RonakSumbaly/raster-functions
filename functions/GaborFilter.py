import numpy as np
from scipy import ndimage as ndi
import math

class GaborFilter():

    def __init__(self):
        self.name = "Gabor Filter"
        self.description = "Extract texture features using the Gabor Filter."

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
                'name': 'theta',
                'dataType': 'numeric',
                'value': 0.0,
                'required': True,
                'displayName': "Theta Value",
                'description': "Orientation of the normal to the parallel stripes of a Gabor function."
            },
            {
                'name': 'psi',
                'dataType': 'numeric',
                'value': 1.0,
                'required': True,
                'displayName': "Psi Value",
                'description': "Phase offset."
            },
            {
                'name': 'lambda',
                'dataType': 'numeric',
                'value': 4.0,
                'required': True,
                'displayName': "Lambda Value",
                'description': "The wavelength of the sinusoidal factor."
            },
            {
                'name': 'sigma',
                'dataType': 'numeric',
                'value': 2.0,
                'required': True,
                'displayName': "Sigma Value",
                'description': "The sigma/standard deviation of the Gaussian envelope."
            },
            {
                'name': 'gamma',
                'dataType': 'numeric',
                'value': 0.3,
                'required': True,
                'displayName': "Gamma Value",
                'description': "Spatial aspect ratio. Specifies the ellipticity of the support of the Gabor function."
            },
        ]

    def getConfiguration(self, **scalars):
        return {
          'inheritProperties':  1 | 2 | 4 | 8,      # inherit everything but the pixel type (1) and NoData (2)
          'invalidateProperties': 2 | 4 | 8,    # invalidate these aspects because we are modifying pixel values and updating key properties.
          'padding': 0,                         # no padding of the input pixel block
          'inputMask': False                    # we don't need the input mask in .updatePixels()
        }

    def updateRasterInfo(self, **kwargs):
        theta = kwargs.get('theta', 0.0)
        lamba = kwargs.get('lambda', 4.0)
        psi   = kwargs.get('psi', 1.0)
        sigma = kwargs.get('sigma', 2.0)
        gamma = kwargs.get('gamma', 0.3)
        nstds = 3       ## standard bounding box

        self.kernel = (self.createGaborKernel(nstds, lamba, theta, psi, sigma, gamma))

        kwargs['output_info']['bandCount'] = 1
        kwargs['output_info']['pixelType'] = kwargs['raster_info']['pixelType']
        kwargs['output_info']['statistics'] = ()
        kwargs['output_info']['histogram'] = ()
        kwargs['output_info']['colormap'] = ()

        return kwargs

    def updatePixels(self, tlc, shape, props, **pixelBlocks):
        raster = np.array(pixelBlocks['raster_pixels'], dtype ='f4', copy=False)
        raster = ndi.convolve(raster, self.kernel)
        pixelBlocks['output_pixels'] = raster.astype(props['pixelType'], copy=False)
        return pixelBlocks

    def updateKeyMetadata(self, names, bandIndex, **keyMetadata):
        if bandIndex == -1:                             # dataset-level properties
            keyMetadata['datatype'] = 'Processed'       # outgoing dataset is now 'Processed'
        elif bandIndex == 0:                            # properties for the first band
            keyMetadata['wavelengthmin'] = None         # reset inapplicable band-specific key metadata
            keyMetadata['wavelengthmax'] = None
            keyMetadata['bandname'] = 'GaborFilter'
        return keyMetadata

    def createGaborKernel(self, nstds, lamba, theta, psi, sigma, gamma):
        sigma_x = sigma
        sigma_y = sigma / gamma

        ## bounding box
        xCord = int(np.ceil(max(np.abs(nstds * sigma_x * np.cos(theta)),
                     np.abs(nstds * sigma_y * np.sin(theta)), 1)))
        yCord = int(np.ceil(max(np.abs(nstds * sigma_y * np.cos(theta)),
                     np.abs(nstds * sigma_x * np.sin(theta)), 1)))

        y, x = np.mgrid[-yCord:yCord + 1, -xCord:xCord + 1]

        xTemp = x * np.cos(theta) + y * np.sin(theta)
        yTemp = -x * np.sin(theta) + y * np.cos(theta)

        ## create gabor filter
        g = np.zeros(x.shape, dtype=np.double)

        g[:] = np.exp(-1 * ((xTemp ** 2 + gamma ** 2 * yTemp ** 2)) / (2 * sigma ** 2)) * np.cos(2 * np.pi  * xTemp / lamba + psi)
        g[:] = g / np.sum(g)

        return g

# ----- ## ----- ## ----- ## ----- ## ----- ## ----- ## ----- ## ----- ##

"""
References:
    [1]. Wikipedia: Gabor filter .
    http://en.wikipedia.org/wiki/Gabor_filter
"""
