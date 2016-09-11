import os

import arcpy

import analysis
import util


class TreeCoverLoss(object):
    '''
    Tree cover loss tool
    '''

    def __init__(self):
        self.label       = "Tree Cover Loss"
        self.description = "Calculate tree cover loss for a given feature class " + \
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
            displayName="Tree cover density threshold (exclude values <=)",
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

        # Make output table a pivot table
        pivot = arcpy.Parameter(
            displayName="Make output a pivot table",
            name="pivot",
            datatype="GPBoolean",
            parameterType="Required",
            direction="Output")

        pivot.value = True


        # Location of temporary merge table
        temp_merge = arcpy.Parameter(
            displayName="Temporay output table",
            name="temp_merge",
            datatype="DETable",
            parameterType="Required",
            direction="Output",
            category="Advanced")

        temp_merge.value = "in_memory/merge_table"

        # Maximum number of temporary features
        max_temp = arcpy.Parameter(
            displayName="Maximum number of temporary features",
            name="max_temp",
            datatype="GPLong",
            parameterType="Required",
            direction="Input",
            category="Advanced")

        max_temp.value = "100"

        parameters = [in_features, tcd_threshold, mosaic_workspace, out_table, pivot, temp_merge, max_temp]

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

        if parameters[2].altered and parameters[2].valueAsText and not parameters[2].hasBeenValidated:
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
                                               os.path.join(mosaic_workspace, "area")]):
                parameters[2].setErrorMessage("Geodatabase must contain loss, area and tcd mosaic datasets")
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
        pivot = bool(parameters[4].value)
        temp_merge = parameters[5].valueAsText
        max_temp = int(parameters[6].valueAsText)

        analysis.tc_loss(in_features, tcd_threshold, mosaic_workspace, out_table, pivot, max_temp, max_temp, messages)
