import os
import arcpy
from lxml import objectify



def mask_mosaic(tcd_mosaic):
    '''
    Create a raster function template to mask forest loss mosaic with tree cover density threshold
    This function uses the template_tcd_mask raster function template and writes results to tcd_mask
    :param tcd_mosaic:
    :return:
    '''

    abspath = os.path.abspath(__file__)
    dir_name = os.path.dirname(abspath)
    template = os.path.join(dir_name, r"templates\mask_mosaic_template.rft.xml")

    tcd_gdb = os.path.dirname(tcd_mosaic)
    tcd_gdb_name = os.path.dirname(tcd_gdb)
    tcd_name = os.path.basename(tcd_mosaic)

    with open(template) as f:
        tree = objectify.parse(f)

    root = tree.getroot()
    values = root.Arguments.Values.getchildren()
    for value in values:
        if value.Name == "Raster2":
            value.Value.WorkspaceName.PathName = tcd_gdb
            objectify.deannotate(value.Value.WorkspaceName.PathName, cleanup_namespaces=True)

            value.Value.WorkspaceName.BrowseName = tcd_gdb_name
            objectify.deannotate(value.Value.WorkspaceName.BrowseName, cleanup_namespaces=True)

            value.Value.WorkspaceName.ConnectionProperties.PropertyArray.PropertySetProperty.Value = tcd_gdb
            objectify.deannotate(value.Value.WorkspaceName.ConnectionProperties.PropertyArray.PropertySetProperty.Value, cleanup_namespaces=True)

            value.Value.Name = tcd_name
            objectify.deannotate(value.Value.Name, cleanup_namespaces=True)
            objectify.xsiannotate(value.Value.Name)

    mask_path = os.path.join(dir_name,r"templates\mask_mosaic.rft.xml")
    tree.write(mask_path)
    return mask_path

def update_tcd_mask(tcd_threshold):
    '''
    Create a raster function template to mask forest loss mosaic with tree cover density threshold
    This function uses the template_tcd_mask raster function template and writes results to tcd_mask
    :param tcd_threshold:
    :param loss_mosaic:
    :param tcd_mosaic:
    :return:
    '''

    abspath = os.path.abspath(__file__)
    dir_name = os.path.dirname(abspath)
    template = os.path.join(dir_name, r"templates\tcd_mask_template.rft.xml")

    with open(template) as f:
        tree = objectify.parse(f)

    root = tree.getroot()
    values = root.Arguments.Values.getchildren()
    for value in values:
        if value.Name == "InputRanges":
            objectify.SubElement(value.Value, "Double")
            objectify.SubElement(value.Value, "Double")
            objectify.SubElement(value.Value, "Double")
            objectify.SubElement(value.Value, "Double")

            value.Value.Double[0] = 0
            value.Value.Double[1] = tcd_threshold
            value.Value.Double[2] = tcd_threshold
            value.Value.Double[3] = 101

            #xsi_nil=True,
            objectify.deannotate(value.Value.Double[0], cleanup_namespaces=True)
            objectify.deannotate(value.Value.Double[1], cleanup_namespaces=True)
            objectify.deannotate(value.Value.Double[2], cleanup_namespaces=True)
            objectify.deannotate(value.Value.Double[3], cleanup_namespaces=True)

        elif value.Name == "OutputValues":
            objectify.SubElement(value.Value, "Double")
            objectify.SubElement(value.Value, "Double")

            value.Value.Double[0] = 0
            value.Value.Double[1] = 1

            objectify.deannotate(value.Value.Double[0], cleanup_namespaces=True)
            objectify.deannotate(value.Value.Double[1], cleanup_namespaces=True)

    mask_path = os.path.join(dir_name, r"templates\tcd_mask.rft.xml")
    tree.write(mask_path)
    return mask_path

def replace_raster_function(mosaic, raster_function):
    '''
    Remove all raster functions from a raster function chain in a mosaic dataset
    Add new raster function to mosaic dataset
    :param mosaic:
    :param raster_function:
    :return:
    '''

    arcpy.EditRasterFunction_management(mosaic, "EDIT_MOSAIC_DATASET", "REMOVE", raster_function)
    arcpy.EditRasterFunction_management(mosaic, "EDIT_MOSAIC_DATASET", "INSERT", raster_function)

    return
