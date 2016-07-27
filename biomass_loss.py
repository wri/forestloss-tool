import os
import arcpy
import analysis
import util


class BioMassLoss(object):
    '''
    Tree cover loss tool
    '''

    def __init__(self):
        self.label       = "Biomass Loss"
        self.description = "Calculate biomass loss for a given feature class " + \
                           "Define custom threshold for tree cover density"
        self.canRunInBackground = False

    def getParameterInfo(self):
        '''
        Define parameter definitions
        :return:
        '''

        # Input Features parameter
        in_features = arcpy.Parameter(
            displayName="Input Features",
            name="in_features",
            datatype="GPFeatureLayer",
            parameterType="Required",
            direction="Input")

        # Tree cover density threshold. Input value must be an integer between 10 and 100
        tcd_threshold = arcpy.Parameter(
            displayName="Tree cover density (10 - 100)",
            name="tcd_threshold",
            datatype="GPLong",
            parameterType="Required",
            direction="Input")

        tcd_threshold.value = "30"
        tcd_threshold.filter.type = "Range"
        tcd_threshold.filter.list = [10, 100]

        # Workspace containing mosaic datasets
        mosaic_workspace = arcpy.Parameter(
            displayName="Mosaic Workspace",
            name="mosaic_workspace",
            datatype="DEWorkspace",
            parameterType="Required",
            direction="Input")

        mosaic_workspace.filter.list = ['Local Database']



        # Derived Output Features parameter
        out_table = arcpy.Parameter(
            displayName="Output table",
            name="out_table",
            datatype="DETable",
            parameterType="Required",
            direction="Output")

        parameters = [in_features, tcd_threshold, mosaic_workspace, out_table]

        return parameters

    def isLicensed(self):
        '''
        Allow the tool to execute, only if the ArcGIS Spatial Analyst extension
        is available.
        :return:
        '''

        try:
            if arcpy.CheckExtension("Spatial") != "Available":
                raise Exception("Spatial Analyst extension not available")
        except Exception("Spatial Analyst extension not available"):
             return False  # tool cannot be executed

        return True  # tool can be executed

    def updateParameters(self, parameters): #optional
       return

    def updateMessages(self, parameters):
        '''
        Check if workspace is geodatabase and
        if loss, area and tcd mosaic datasets are in GDB
        :param parameters:
        :return:
        '''

        if parameters[2].altered and parameters[2].valueAsText:
            mosaic_workspace = parameters[2].valueAsText
            if arcpy.Exists(mosaic_workspace):
                if not util.is_file_gdb(mosaic_workspace):
                    parameters[2].setErrorMessage("Workspace must be a geodatabase")
                    return
            else:
                parameters[2].setErrorMessage("Workspace does not exist")
                return

            if not util.mosaic_datasets_exist([os.path.join(mosaic_workspace, "lossyear"),
                                               os.path.join(mosaic_workspace, "tcd"),
                                               os.path.join(mosaic_workspace, "biomass"),
                                               os.path.join(mosaic_workspace, "area")]):
                parameters[2].setErrorMessage("Geodatabase must contain loss, biomass and tcd mosaic datasets")

        return

    def execute(self, parameters, messages):
        '''
        Run tree cover loss analysis
        :param parameters:
        :param messages:
        :return:
        '''

        # Check out the Spatial Analyst extension
        arcpy.CheckOutExtension("Spatial")

        # Always overwrite output
        arcpy.env.overwriteOutput = True

        in_features = parameters[0].valueAsText
        tcd_threshold = int(parameters[1].valueAsText)
        mosaic_workspace = parameters[2].valueAsText
        out_table = parameters[3].valueAsText

        analysis.biomass_loss(in_features, tcd_threshold, mosaic_workspace, out_table, messages)
