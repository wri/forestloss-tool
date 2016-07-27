import numpy as np


class BiomassConversion(object):

    def __init__(self):
        self.name = "Biomass conversion"
        self.description = ("This function converts biomass from  "
                            "biomass/ha to biomass/px.")

    def getParameterInfo(self):
        return [
            {
                'name': 'biomass',
                'dataType': 'raster',
                'value': None,
                'required': True,
                'displayName': "Biomass raster",
                'description': "A single-band raster where pixel values represent biomass/ha."
            },
            {
                'name': 'area',
                'dataType': 'raster',
                'value': None,
                'required': True,
                'displayName': "Area Raster",
                'description': "A single-band raster where pixel values represent pixel area in m2."
            },
        ]

    def getConfiguration(self, **scalars):
        return {
          'inheritProperties': 4 | 8,               # inherit all but the pixel type and NoData from the input raster
          'invalidateProperties': 2 | 4 | 8,        # invalidate statistics & histogram on the parent dataset because we modify pixel values.
          'inputMask': False                        # Don't need input raster mask in .updatePixels(). Simply use the inherited NoData.
        }

    def updateRasterInfo(self, **kwargs):
        kwargs['output_info']['bandCount'] = 1      # output is a single band raster
        kwargs['output_info']['statistics'] = ()    # we know nothing about the stats of the outgoing raster.
        kwargs['output_info']['histogram'] = ()     # we know nothing about the histogram of the outgoing raster.
        kwargs['output_info']['pixelType'] = 'f4'
        return kwargs

    def updatePixels(self, tlc, size, props, **pixelBlocks):

        # Get raster layers
        biomass = np.array(pixelBlocks['biomass_pixels'], dtype='f4', copy=False)
        area = np.array(pixelBlocks['area_pixels'], dtype='f4', copy=False)

        # Convert biomass/ha to biomass/px
        outBlock = biomass * area/10000

        pixelBlocks['output_pixels'] = outBlock.astype(props['pixelType'], copy=False)
        return pixelBlocks

    def updateKeyMetadata(self, names, bandIndex, **keyMetadata):
        return keyMetadata