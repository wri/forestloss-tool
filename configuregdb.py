import os
import arcpy
import util


class ConfigureGDB(object):
    '''
    Tree cover loss tool
    '''

    def __init__(self):
        self.label       = "Configure GDB"
        self.description = "Configure GDB for analysis " + \
                           "Install required mosaics and add rasters"
        self.category = "Installation"
        self.canRunInBackground = False

    def getParameterInfo(self):
        '''
        Define parameter definitions
        :return:
        '''

        # Workspace containing mosaic datasets
        mosaic_workspace = arcpy.Parameter(
            displayName="Mosaic Workspace",
            name="mosaic_workspace",
            datatype="DEWorkspace",
            parameterType="Required",
            direction="Input")

        loss_rasters = arcpy.Parameter(
            displayName="Loss rasters",
            name="loss_rasters",
            category="Loss year",
            datatype="DERasterDataset",
            parameterType="Optional",
            direction="Input",
            multiValue=True)

        gain_rasters = arcpy.Parameter(
            displayName="Gain rasters",
            name="gain_rasters",
            category="Gain",
            datatype="DERasterDataset",
            parameterType="Optional",
            direction="Input",
            multiValue=True)

        area_rasters = arcpy.Parameter(
            displayName="Area rasters",
            name="area_rasters",
            category="Area",
            datatype="DERasterDataset",
            parameterType="Optional",
            direction="Input",
            multiValue=True)

        tcd_rasters = arcpy.Parameter(
            displayName="TCD rasters",
            name="tcd_rasters",
            category="TCD",
            datatype="DERasterDataset",
            parameterType="Optional",
            direction="Input",
            multiValue=True)

        biomass_rasters = arcpy.Parameter(
            displayName="Biomass rasters",
            name="biomass_rasters",
            category="Biomass",
            datatype="DERasterDataset",
            parameterType="Optional",
            direction="Input",
            multiValue=True)

        parameters = [mosaic_workspace, loss_rasters, gain_rasters, area_rasters, tcd_rasters, biomass_rasters]

        return parameters

    def isLicensed(self):
        '''
        This tool doesn't require any special licenses
        :return:
        '''

        return True  # tool can be executed

    def updateParameters(self, parameters):
        '''
        No update parameters
        :param parameters:
        :return:
        '''
        return

    def updateMessages(self, parameters):
        '''
        Select if selected fileGDB already has corresponding mosaics
        :param parameters:
        :return:
        '''
        if parameters[0].altered:
            mosaic_workspace = parameters[0].valueAsText
            if parameters[1].values and arcpy.Exists(os.path.join(mosaic_workspace, "lossyear")):
                parameters[1].setErrorMessage("Selected GDB already has a lossyear mosaic dataset")
            if parameters[2].values and arcpy.Exists(os.path.join(mosaic_workspace, "gain")):
                parameters[2].setErrorMessage("Selected GDB already has a gain mosaic dataset")
            if parameters[3].values and arcpy.Exists(os.path.join(mosaic_workspace, "area")):
                parameters[3].setErrorMessage("Selected GDB already has a area mosaic dataset")
            if parameters[4].values and arcpy.Exists(os.path.join(mosaic_workspace, "tcd")):
                parameters[4].setErrorMessage("Selected GDB already has a tcd mosaic dataset")
            if parameters[5].values and arcpy.Exists(os.path.join(mosaic_workspace, "biomass")):
                parameters[5].setErrorMessage("Selected GDB already has a biomass mosaic dataset")

        return

    def execute(self, parameters, messages):
        '''
        Create mosaic datasets for lossyear, gain, area, tcd and biomass
        Add selected rasters to new mosaic datasets
        :param parameters:
        :param messages:
        :return:
        '''

        mosaic_workspace = parameters[0].valueAsText

        if parameters[1].values:
            lossyear_rasters = [v.value for v in parameters[1].values]
            util.create_mosaic_dataset(mosaic_workspace, "lossyear", lossyear_rasters, "8_BIT_UNSIGNED", messages)
        if parameters[2].values:
            gain_rasters = [v.value for v in parameters[2].values]
            util.create_mosaic_dataset(mosaic_workspace, "gain", gain_rasters, "8_BIT_UNSIGNED", messages)
        if parameters[3].values:
            area_rasters = [v.value for v in parameters[3].values]
            util.create_mosaic_dataset(mosaic_workspace, "area", area_rasters, "32_BIT_FLOAT", messages)
        if parameters[4].values:
            tcd_rasters = [v.value for v in parameters[4].values]
            util.create_mosaic_dataset(mosaic_workspace, "tcd", tcd_rasters, "8_BIT_UNSIGNED", messages)
        if parameters[5].values:
            biomass_rasters = [v.value for v in parameters[5].values]
            util.create_mosaic_dataset(mosaic_workspace, "biomass", biomass_rasters, "32_BIT_FLOAT", messages)




