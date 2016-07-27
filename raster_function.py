import os
import arcpy
from lxml import objectify


def mask_lossyear_mosaic(tcd_mosaic, tcd_threshold, messages):
    """
    Create a raster function template to mask forest loss mosaic with tree cover density threshold
    This function uses the template_tcd_mask raster function template and writes results to tcd_mask.
    Value within TCD threshold will stay as it. All values outside TCD threshold will be set to -1
    :param tcd_mosaic: String
    :param tcd_threshold: Integer
    :return: String
    """

    # Define path to template XML file
    abspath = os.path.abspath(__file__)
    dir_name = os.path.dirname(abspath)
    template = os.path.join(dir_name, r"templates\lossyear_mask_template.rft.xml")

    # Define path and name of GDB and mosaic
    tcd_gdb = os.path.dirname(tcd_mosaic)
    tcd_gdb_name = os.path.dirname(tcd_gdb)
    tcd_name = os.path.basename(tcd_mosaic)

    # Read XML template into object tree
    with open(template) as f:
        tree = objectify.parse(f)

    root = tree.getroot()
    values = root.Arguments.Values.getchildren()
    for value in values:
        try:
            if value.Name == "tcd_threshold":
                value.Value = tcd_threshold

            elif value.Name == "Raster2":

                value.Value.WorkspaceName.PathName = tcd_gdb
                objectify.deannotate(value.Value.WorkspaceName.PathName, cleanup_namespaces=True)

                value.Value.WorkspaceName.BrowseName = tcd_gdb_name
                objectify.deannotate(value.Value.WorkspaceName.BrowseName, cleanup_namespaces=True)

                value.Value.WorkspaceName.ConnectionProperties.PropertyArray.PropertySetProperty.Value = tcd_gdb
                objectify.deannotate(value.Value.WorkspaceName.ConnectionProperties.PropertyArray.PropertySetProperty.Value, cleanup_namespaces=True)

                value.Value.Name = tcd_name
                objectify.deannotate(value.Value.Name, cleanup_namespaces=True)
                objectify.xsiannotate(value.Value.Name)

        except AttributeError:
            pass

    # Write update values to a new XML file (keep template untouched)
    mask_path = os.path.join(dir_name, r"templates\lossyear_mask.rft.xml")
    tree.write(mask_path)
    return mask_path


def convert_biomass_mosaic(area_mosaic, messages):
    """
    Create a raster function template to convert biomass data from biomass per hectare to biomass per pixel.
    Multiplies biomass layer with area values devided by 10000
    :param area_mosaic: string
    :return: string
    """
    # Define path to template XML file
    abspath = os.path.abspath(__file__)
    dir_name = os.path.dirname(abspath)
    template = os.path.join(dir_name, r"templates\biomass_conversion_template.rft.xml")

    # Define path and name of GDB and mosaic
    area_gdb = os.path.dirname(area_mosaic)
    area_gdb_name = os.path.dirname(area_gdb)
    area_name = os.path.basename(area_mosaic)

    # Read XML template into object tree
    with open(template) as f:
        tree = objectify.parse(f)

    root = tree.getroot()
    values = root.Arguments.Values.getchildren()
    for value in values:
        try:
            if value.Name == "Raster2":
                value.Value.WorkspaceName.PathName = area_gdb
                objectify.deannotate(value.Value.WorkspaceName.PathName, cleanup_namespaces=True)

                value.Value.WorkspaceName.BrowseName = area_gdb_name
                objectify.deannotate(value.Value.WorkspaceName.BrowseName, cleanup_namespaces=True)

                value.Value.WorkspaceName.ConnectionProperties.PropertyArray.PropertySetProperty.Value = area_gdb
                objectify.deannotate(value.Value.WorkspaceName.ConnectionProperties.PropertyArray.PropertySetProperty.Value, cleanup_namespaces=True)

                value.Value.Name = area_name
                objectify.deannotate(value.Value.Name, cleanup_namespaces=True)
                objectify.xsiannotate(value.Value.Name)

        except AttributeError:
            pass

    # Write update values to a new XML file (keep template untouched)
    mask_path = os.path.join(dir_name, r"templates\biomass_conversion.rft.xml")
    tree.write(mask_path)
    return mask_path



def replace_raster_function(mosaic, raster_function, messages):
    '''
    Remove all raster functions from a raster function chain in a mosaic dataset
    Add new raster function to mosaic dataset
    :param mosaic:
    :param raster_function:
    :return:
    '''

    arcpy.EditRasterFunction_management(mosaic, "EDIT_MOSAIC_DATASET", "REMOVE")
    arcpy.EditRasterFunction_management(mosaic, "EDIT_MOSAIC_DATASET", "INSERT", raster_function)

    return
