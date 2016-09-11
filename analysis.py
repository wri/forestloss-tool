import math
import os
import arcpy
import raster_function
import util


def get_geometry(fc):
    cursor = arcpy.da.SearchCursor(fc, ["Shape@"])
    for row in cursor:
        return row[0]


def merge_results(temp_tables, temp_merge, messages):
    if len(temp_tables) > 0:
        # Merge all results into one tab;e
        messages.AddMessage("Merge results")
        if not arcpy.Exists(temp_merge):
            arcpy.CreateTable_management(os.path.dirname(temp_merge), os.path.basename(temp_merge), temp_tables[0])
        arcpy.Append_management(temp_tables, temp_merge)
        for temp_table in temp_tables:
            arcpy.Delete_management(temp_table)
        return temp_merge

    else:
        raise Exception("No features found in input Layer")


def zonal_stats(mask_mosaic, value_mosaic, in_features, temp_merge, max_temp, messages):
    """
    Calulate zonal stats for a mask mosaic and a value mosaic using a vector feature as mask
    :param mask_mosaic: string
    :param value_mosaic: string
    :param in_features: string
    :param temp_merge: string
    :param max_temp: long
    :param messages: object
    :return:
    """

    # Make lossyear mosaic spatial reference the default output coordinate system
    desc = arcpy.Describe(mask_mosaic)
    arcpy.env.outputCoordinateSystem = desc.spatialReference

    mask_mosaic_layer = arcpy.MakeMosaicLayer_management(mask_mosaic, "mask_mosaic_layer")
    value_mosaic_layer = arcpy.MakeMosaicLayer_management(value_mosaic, "value_mosaic_layer")

    mask_mosaic_boundary = get_geometry("mask_mosaic_layer/Boundary")
    value_mosaic_boundary = get_geometry("value_mosaic_layer/Boundary")

    # Snap to lossyear mosaic
    arcpy.env.snapRaster = mask_mosaic

    # Make feature layer from input features
    in_layer = arcpy.MakeFeatureLayer_management(in_features, "in_layer")

    # Create list to register temp output tables
    temp_tables = list()

    # Check if temporary output table exist. If yes, delete to make sure that new table with correct schema will be created
    if arcpy.Exists(temp_merge):
        arcpy.Delete_management(temp_merge)

    # Create lists to count if all features were processed
    processed = list()

    # Count number of rows in input layer
    row_count = int(arcpy.GetCount_management(in_layer).getOutput(0))

    # Calculate lossyear for input features
    # Loop as long over features until all were processed
    done = False
    while not done:
        # Create list to count all features
        id = list()

        with arcpy.da.SearchCursor(in_layer, ['OID@', 'Shape@']) as cursor:
            for row in cursor:
                id.append(row[0])
                # If feature was not yet processed copy feature to temporary feature class
                # Assign temporary feature class as mask in environment settings
                # Must be feature class, Geometries are not accepted
                if row[0] not in processed:
                    # Check if geometry actually exists
                    if row[1]:
                        # check if geometry of input feature is within bounds of mosaic datasets
                        geometry = row[1].projectAs("WGS 1984")
                        if geometry.within(mask_mosaic_boundary) and geometry.within(value_mosaic_boundary):

                            # Copy geometry to in memory feature class
                            mask_layer = "in_memory/mask"
                            arcpy.CopyFeatures_management(geometry, mask_layer)
                            arcpy.env.mask = mask_layer
                            desc = arcpy.Describe(mask_layer)
                            arcpy.env.extent = desc.extent

                            # Somehow every second features does not get properly copies. Don't know why
                            # If mask is empty feature get skipped and will be processed in the next loop
                            if not math.isnan(arcpy.env.extent.XMin):
                                # Sum area values for every year in mask lossyear layers
                                # Save results in temporary table and add feature ID as extra column
                                messages.AddMessage("Process feature {} out of {} (ID {})".format(len(processed) + 1,
                                                                                                  row_count, row[0]))
                                temp_table = "in_memory/feature_{}".format(row[0])
                                temp_tables.append(temp_table)

                                arcpy.gp.ZonalStatisticsAsTable_sa(mask_mosaic, "VALUE", value_mosaic, temp_table, "DATA", "SUM")

                                arcpy.AddField_management(temp_table, "FID", "LONG")
                                arcpy.CalculateField_management (temp_table, "FID", row[0])

                                # Make feature as processed
                                processed.append(row[0])
                        else:
                            messages.AddMessage("Feature out of bounds - Skip (ID {})".format(row[0]))
                            processed.append(row[0])
                    else:
                        messages.AddMessage("Feature has no valid geometry - Skip (ID {})".format(row[0]))
                        processed.append(row[0])

        # once given threshold is reached, write all temporary results into one single table to prevent script from crashing
        # might be internal memory related issue? Normally, max number of feature classes is 2Bil

        if len(processed) == max_temp:
            merge_results(temp_tables, temp_merge, messages)
            temp_tables = list()

        # Once all features are processed quite while loop
        if id == sorted(processed):
            done = True

    if len(temp_tables) > 0:
        merge_results(temp_tables, temp_merge, messages)

    if arcpy.Exists(temp_merge):
        return temp_merge
    else:
        raise Exception("No features found in input Layer")


def mask_lossyear(mosaic, tcd_mosaic, tcd_threshold, messages):
    """
    Apply TCD mask to lossyear mosaic
    :param mosaic: string
    :param tcd_mosaic: string
    :param tcd_threshold: integer
    :param messages: object
    :return:
    """

    messages.AddMessage("Apply TCD mask to lossyear mosaic")

    # Create raster function template file
    mask_function = raster_function.mask_lossyear_mosaic(tcd_mosaic, tcd_threshold, messages)

    # Load raster functions
    raster_function.replace_raster_function(mosaic, mask_function, messages)

    return


def convert_biomass(mosaic, area_mosaic, messages):
    """
    Apply biomass raster function to biomass mosaic
    :param mosaic: string
    :param area_mosaic: string
    :param messages: object
    :return:
    """

    messages.AddMessage("Apply biomass raster function to biomass mosaic")

    # Create raster function template file
    rf = raster_function.convert_biomass_mosaic(area_mosaic, messages)

    # Load raster functions
    raster_function.replace_raster_function(mosaic, rf, messages)

    return


def clean_up(mosaics, messages):
    """
    Delete all in_memort datasets and remove raster functions from listed mosaics
    :param mosaics: list
    :return:
    """

    messages.AddMessage("Clean up")

    # get all datasets in "in_memory" workspace
    arcpy.env.workspace = "in_memory"
    datasets = arcpy.ListDatasets()

    # remove all datasets in in_memory workspace
    for dataset in datasets:
        arcpy.Delete_management(dataset)

    # remove all datasets from listed mosaics
    for mosaic in mosaics:
        arcpy.EditRasterFunction_management(mosaic, "EDIT_MOSAIC_DATASET", "REMOVE")
    return


def tc_loss(in_features, tcd_threshold, mosaic_workspace, out_table, pivot, merge_table, max_temp, messages):
    '''
    Calculate tree cover loss for input features
    :param in_features: string
    :param tcd_threshold: integer
    :param mosaic_workspace: string
    :param out_table: string
    :param pivot: boolean
    :param merge_table: string
    :param max_temp: integer
    :param messages: object
    :return:
    '''

    # Define mosaic layers
    lossyear_mosaic = os.path.join(mosaic_workspace, "lossyear")
    area_mosaic = os.path.join(mosaic_workspace, "area")
    tcd_mosaic = os.path.join(mosaic_workspace, "tcd")

    # Mask loss year using the TCD threshold
    mask_lossyear(lossyear_mosaic, tcd_mosaic, tcd_threshold, messages)

    # Calculating annual loss for every input feature
    zonal_stats_table = zonal_stats(lossyear_mosaic, area_mosaic, in_features, merge_table, max_temp, messages)

    # If final output is a pivot table write format table into a temp file,
    # IF not create directly output table
    if pivot:
        format_table = "in_memory/format_table"
    else:
        format_table = out_table

    # Create final output table and define fields
    arcpy.CreateTable_management (os.path.dirname(format_table), os.path.basename(format_table))
    arcpy.AddField_management(format_table, "FID", "LONG")
    arcpy.AddField_management(format_table, "YEAR", "TEXT")
    arcpy.AddField_management(format_table, "TCD", "LONG")
    arcpy.AddField_management(format_table, "LOSS_HA", "DOUBLE")

    # Select relevant fields from merged table
    cursor = arcpy.da.SearchCursor(zonal_stats_table, ["FID", "VALUE", "SUM"], sql_clause=(None, "ORDER BY FID DESC"))

    # Create Insert cursor for output table
    newrows = arcpy.InsertCursor(format_table)

    # Loop over all rows in merge table and write results into output table
    for row in cursor:
        newrow = newrows.newRow()
        newrow.setValue("FID", row[0])
        if row[1] == -1:
            newrow.setValue("YEAR", "area outside threshold")
        elif row[1] == 0:
            newrow.setValue("YEAR", "no loss")
        else:
            newrow.setValue("YEAR", "Year {}".format(2000 + row[1]))
        newrow.setValue("TCD", tcd_threshold)
        newrow.setValue("LOSS_HA", row[2]/10000)
        newrows.insertRow(newrow)

    if pivot:
        # Flatten table.
        # One line per feature, with seperate columns for each year
        messages.AddMessage("Flatten table".format(out_table))
        arcpy.PivotTable_management(format_table, "FID;TCD", "YEAR", "LOSS_HA", out_table)

    # Delete all in_memory datasets
    clean_up([lossyear_mosaic], messages)

    return


def biomass_loss(in_features, tcd_threshold, mosaic_workspace, out_table, pivot, unit, merge_table, max_temp, messages):
    '''
    Calculate biomass loss for input features
    :param in_features: string
    :param tcd_threshold: integer
    :param mosaic_workspace: string
    :param out_table: string
    :param pivot: boolean
    :param unit: string
    :param merge_table: string
    :param max_temp: integer
    :param messages: object
    :return:
    '''

    # Define mosaic layers
    lossyear_mosaic = os.path.join(mosaic_workspace, "lossyear")
    biomass_mosaic = os.path.join(mosaic_workspace, "biomass")
    tcd_mosaic = os.path.join(mosaic_workspace, "tcd")
    area_mosaic = os.path.join(mosaic_workspace, "area")

    # TODO: Add biomass conversion function here
    # Somehow I cannot remove existing raster functions from the biomass layer. Not sure why!? It works for the lossyear
    # As a result would add the biomass function multiple times which cases wrong results.
    # As a work around I add the biomass conversion function directly on mosaic creation and won't touch it anymore. FOREVER.

    # Convert biomass per hectare to biomass per pixel
    # convert_biomass(biomass_mosaic, area_mosaic, messages)

    # Mask loss year using the TCD threshold. set all values outside threshold to -1
    mask_lossyear(lossyear_mosaic, tcd_mosaic, tcd_threshold, messages)

    # Calculating annual loss for every input feature
    zonal_stats_table = zonal_stats(lossyear_mosaic, biomass_mosaic, in_features, merge_table, max_temp, messages)

    # If final output is a pivot table write format table into a temp file,
    # IF not create directly output table
    if pivot:
        format_table = "in_memory/format_table"
    else:
        format_table = out_table
    # Create final output table and define fields
    arcpy.CreateTable_management (os.path.dirname(format_table), os.path.basename(format_table))
    arcpy.AddField_management(format_table, "FID", "LONG")
    arcpy.AddField_management(format_table, "YEAR", "TEXT")
    arcpy.AddField_management(format_table, "TCD", "LONG")
    arcpy.AddField_management(format_table, "BIOMASS_LOSS_MG", "DOUBLE")
    arcpy.AddField_management(format_table, "EMISSIONS_MT_CO2", "DOUBLE")

    # Select relevant fields from merged table
    cursor = arcpy.da.SearchCursor(zonal_stats_table, ["FID", "VALUE", "SUM"], sql_clause=(None, "ORDER BY FID DESC"))

    # Create Insert cursor for output table
    newrows = arcpy.InsertCursor(format_table)

    # Loop over all rows in merge table and write results into output table
    for row in cursor:
        newrow = newrows.newRow()
        newrow.setValue("FID", row[0])
        if row[1] == -1:
            newrow.setValue("YEAR", "biomass outside threshold")
        elif row[1] == 0:
            newrow.setValue("YEAR", "no biomass loss")
        else:
            newrow.setValue("YEAR", "Year {}".format(2000 + row[1]))
        newrow.setValue("TCD", tcd_threshold)
        newrow.setValue("BIOMASS_LOSS_MG", row[2])
        newrow.setValue("EMISSIONS_MT_CO2", row[2]*.5*3.67/1000000)
        newrows.insertRow(newrow)

    if pivot:
        # Flatten table.
        # One line per feature, with seperate columns for each year
        messages.AddMessage("Flatten table".format(out_table))
        if unit == "Mg biomass":
            value_column = "BIOMASS_LOSS_MG"
        else:
            value_column = "EMISSIONS_MT_CO2"
        arcpy.PivotTable_management(format_table, "FID;TCD", "YEAR", value_column, out_table)

    # Delete all in_memory datasets
    # Remove all raster functions

    # TODO: Remove raster function from biomass layer
    # I wasn't able to remove the biomass raster functions using this approach. Not sure why?! It works for the lossyear.
    # Since biomass conversion doesn't require any additional user input or can't be altered in the tool
    # I add it directly during the creation of the mosaic dataset and keep it there.
    # This has the disadvantage that it always shows up. If the user replaces it or results form this tool will be wrong.

    clean_up([lossyear_mosaic], messages)

    return

if __name__ == "__main__":
    arcpy.CheckOutExtension("Spatial")
    arcpy.env.overwriteOutput = True
    m = util.messages()

    biomass_loss(r"C:\Users\Thomas.Maschler\Documents\Atlas\CMR\atlas_forestier.mdb\unites_administratives\departements",
                 30,
                 r"C:\Users\Thomas.Maschler\Desktop\gabon\analysis.gdb",
                 "rC:\Users\Thomas.Maschler\Desktop\gabon\analysis.gdb\dep",
                 True, m)
