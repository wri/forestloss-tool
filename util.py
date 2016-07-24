import arcpy
import os

class messages(object):
    '''
    Helper class to create arcpy messages
    '''
    def __init__(self):
        pass

    def AddMessage(self, message):
        """
        arcpy Message
        :param message: String
        :return:
        """
        arcpy.AddMessage(message)

def is_file_gdb(workspace):
    '''
    Check if workspace is a file GDB
    :param workspace: string
    :return: boolean
    '''
    # TODO: make sure to check for fileGDB not just GDB
    desc = arcpy.Describe(workspace)
    if desc.dataType == "FileSystem":
        return False
    return True

def mosaic_datasets_exist(mosaics):
    """
    Check if all mosaic datasets exist
    :param mosaics:
    :return:
    """

    for mosaic in mosaics:
        if arcpy.Exists(mosaic):
            desc = arcpy.Describe(mosaic)
            if not desc.dataType == "MosaicDataset":
                return False
        else:
            return False

    return True

def create_mosaic_dataset(workspace, name, datasets, datatype, messages):
    """
    Create mosaic dataset and add rasters
    :param workspace:
    :param name:
    :param datasets:
    :param datatype:
    :param messages:
    :return:
    """
    messages.AddMessage("Create {} mosaic".format(name))
    arcpy.CreateMosaicDataset_management(workspace,
                                         name,
                                         arcpy.SpatialReference("WGS 1984"),
                                         1,
                                         datatype)

    messages.AddMessage("Add rasters")
    arcpy.AddRastersToMosaicDataset_management(os.path.join(workspace,name),
                                               "Raster Dataset",
                                               datasets,
                                               duplicate_items_action="OVERWRITE_DUPLICATES")