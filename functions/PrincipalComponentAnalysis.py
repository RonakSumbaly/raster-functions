## incomplete

import numpy as np
import math
import utils


class PrincipalComponentAnalysis():

    def __init__(self):
        self.name = "Principal Component Analysis Function"
        self.description = "Performs Principal Component Analysis (PCA) on a set of raster bands and generates a single multiband raster as output."
        self.trace = utils.Trace()

    def getParameterInfo(self):
        return [
            {
                'name': 'raster',
                'dataType': 'raster',
                'value': None,
                'required': True,
                'displayName': "Input Raster Bands",
                'description': "Multi-band raster to apply Principal Component Analysis (PCA)"
            },
            {
                'name': 'comp',
                'dataType': 'numeric',
                'value': 3.0,
                'required': True,
                'displayName': "Number of Components",
                'description': "Number of components as PCA output."
            },
        ]

    def getConfiguration(self, **scalars):
        return {
          'inheritProperties': 1 | 2 | 4 | 8,           # inherit everything but the pixel type (1) and noData (2)
          'invalidateProperties': 2 | 4 ,               # invalidate these aspects because we are modifying pixel values and updating key properties.
          'padding': 1,                                 #  padding of the input pixel block
          'inputMask': True                             # we don't need the input mask in .updatePixels()
        }

    def updateRasterInfo(self, **kwargs):
        self.comp = int(kwargs.get('comp',3.0))

        if self.comp > kwargs['raster_info']['bandCount']:
            raise Exception ("Number of components greater that number of bands.")

        kwargs['output_info']['bandCount'] =  self.comp
        kwargs['output_info']['resampling'] = False
        kwargs['output_info']['statistics'] = ()
        kwargs['output_info']['histogram'] = ()
        kwargs['output_info']['colormap'] = ()
        return kwargs


    def updatePixels(self, tlc, shape, props, **pixelBlocks):
        r = np.array(pixelBlocks['raster_pixels'],dtype=props['pixelType'],copy=False)
        m = np.array(pixelBlocks['raster_mask'], dtype='u1', copy=False)

        ## create empty output & output mask raster without padding
        output =  np.ones([self.comp,r[0].shape[0]-2,r[0].shape[1]-2])
        outputmask = np.copy(output)

        ## raster stack for computation
        rasters = np.vstack([np.array(raster.ravel(),copy=False) for raster, i in zip(r,xrange(self.comp))])

        ## mask out the noData value for Covariance computation
        rasters = np.ma.array(rasters, mask= rasters == props['noData'][0])         ## method 2
        #maskrasters = rasters.mask.any(axis=0)                                     ## method 1
        #rasters = np.ma.array(rasters, mask=np.vstack((maskrasters, maskrasters)))

        ## covariance & correlation mask calculation
        cov_mat = np.ma.cov(rasters, bias=True)
        cor_mat = np.ma.corrcoef(rasters, bias=True)
        
        ## method 1 computation with bias = False - Number of observations = (N-1) 
        #cov_mat = np.ma.cov(rasters)
        #cor_mat = np.ma.corrcoef(rasters)

        self.trace.log("Trace|updatePixels.1|Covariance Matrix: {0} \n| Correlation Matrix: {1}\n".format(cov_mat,cor_mat))
        
        ## eigen - value and eigen vector computation
        eig_val_cov, eig_vec_cov = np.linalg.eig(cov_mat)

        ## pair and sort eigen values and vectors
        eig_pairs = [(np.abs(eig_val_cov[i]), eig_vec_cov[:,i]) for i in range(len(eig_val_cov))]
        eig_pairs.sort()
        eig_pairs.reverse()

        matrix_w = np.hstack((eig_pairs[i][1].reshape(self.comp,1) for i in xrange(len(eig_pairs)))) * (-1) ## fix phase convention - change sign
        
        self.trace.log("Trace|updatePixels.2|Eigen Pairs: {0} \n| Matrix: {1}\n".format(eig_pairs,matrix_w))

        ## multiply eigen-vector matrix transpose to the original raster
        transformed = np.ma.dot(np.transpose(matrix_w), rasters)

        ## reshape all transformed stack rasters
        for i in xrange(len(transformed)):
            output[i] = transformed[i].reshape((r[0].shape[0],r[0].shape[1]))[1:-1, 1:-1]
            outputmask[i]      = m[i][1:-1, 1:-1]

        pixelBlocks['output_pixels'] = output.astype(props['pixelType'], copy=False)
        pixelBlocks['output_mask']   = outputmask.astype('u1',copy = False)
        return pixelBlocks


    def updateKeyMetadata(self, names, bandIndex, **keyMetadata):
        if bandIndex == -1:                             # dataset-level properties
            keyMetadata['datatype'] = 'Processed'       # outgoing dataset is now 'Processed'
        elif bandIndex == 0:                            # properties for the first band
            keyMetadata['wavelengthmin'] = None         # reset inapplicable band-specific key metadata
            keyMetadata['wavelengthmax'] = None
            keyMetadata['bandname'] = 'PrincipalComponent'
        return keyMetadata

# ----- ## ----- ## ----- ## ----- ## ----- ## ----- ## ----- ## ----- ##

"""
References:
    [1]. Esri (2013): ArcGIS Resources. How Principal Components works.
    http://resources.arcgis.com/en/help/main/10.2/index.html#/How_Principal_Components_works/009z000000qm000000/
    [2]. Wikipedia : Principal Component Analysis.
    http://en.wikipedia.org/wiki/Principal_component_analysis
"""
