import numpy as np


class LossYearMask(object):

    def __init__(self):
        self.name = "Lossyear mask"
        self.description = ("This function mask lossyear based on  "
                            "tree cover density threshold.")
        self.tcd_threshold = 30

    def getParameterInfo(self):
        return [
            {
                'name': 'lossyear',
                'dataType': 'raster',
                'value': None,
                'required': True,
                'displayName': "Lossyear raster",
                'description': "A single-band raster where pixel values represent loss year."
            },
            {
                'name': 'tcd',
                'dataType': 'raster',
                'value': None,
                'required': True,
                'displayName': "TCD Raster",
                'description': "A single-band raster where pixel values represent TCD in percent."
            },
            {
                'name': 'tcd_threshold',
                'dataType': 'numeric',
                'value': self.tcd_threshold,
                'required': True,
                'displayName': "TCD Threshold",
                'description': "An integer representing the TCD threshold."
            },
        ]

    def getConfiguration(self, **scalars):
        return {
          'inheritProperties': 4 | 8,               # inherit all but the pixel type and NoData from the input raster
          'invalidateProperties': 2 | 4 | 8,        # invalidate statistics & histogram on the parent dataset because we modify pixel values.
          'inputMask': False                        # Don't need input raster mask in .updatePixels(). Simply use the inherited NoData.
        }

    def updateRasterInfo(self, **kwargs):

        self.tcd_threshold = int(kwargs.get('tcd_threshold', None))

        kwargs['output_info']['bandCount'] = 1      # output is a single band raster
        kwargs['output_info']['statistics'] = ()    # we know nothing about the stats of the outgoing raster.
        kwargs['output_info']['histogram'] = ()     # we know nothing about the histogram of the outgoing raster.
        kwargs['output_info']['pixelType'] = 'i2'
        return kwargs

    def updatePixels(self, tlc, size, props, **pixelBlocks):

        #Get raster layers
        lossyear = np.array(pixelBlocks['lossyear_pixels'], dtype='i1', copy=False)
        tcd = np.array(pixelBlocks['tcd_pixels'], dtype='i1', copy=False)

        #Convert all values of lossyear outside threshold to -1
        np.place(lossyear, tcd<=self.tcd_threshold, [-1])

        outBlock = lossyear
        pixelBlocks['output_pixels'] = outBlock.astype(props['pixelType'], copy=False)
        return pixelBlocks

    def updateKeyMetadata(self, names, bandIndex, **keyMetadata):
        return keyMetadata