import math
import os
import arcpy
import raster_function


def zonal_stats(mask_mosaic, value_mosaic, in_features, messages):
    """
    Calulate zonal stats for a mask mosaic and a value mosaic using a vector feature as mask
    :param mask_mosaic:
    :param value_mosaic:
    :param in_features:
    :param messages:
    :return:
    """

    # Make lossyear mosaic spatial reference the default output coordinate system
    desc = arcpy.Describe(mask_mosaic)
    arcpy.env.outputCoordinateSystem = desc.spatialReference

    # Snap to lossyear mosaic
    arcpy.env.snapRaster = mask_mosaic

    # Make feature layer from input features
    in_layer = arcpy.MakeFeatureLayer_management(in_features, "in_layer")

    # Create list to register temp output tables
    temp_tables = list()

    # Create lists to count if all features were processed
    processed = list()


    # Calculate lossyear for input features
    # Loop as long over features until all were processed
    done = False
    while not done:
        # Create list to count all features
        id = list()

        # Count number of rows in input layer
        row_count = int(arcpy.GetCount_management(in_layer).getOutput(0))

        with arcpy.da.SearchCursor(in_layer, ['OID@', 'Shape@']) as cursor:
            for row in cursor:
                id.append(row[0])
                # If feature was not yet processed copy feature to temporary feature class
                # Assign temporary feature class as mask in environment settings
                # Must be feature class, Geometries are not accepted
                if row[0] not in processed:
                    mask_layer = "in_memory/mask"
                    arcpy.CopyFeatures_management(row[1], mask_layer)
                    arcpy.env.mask = mask_layer
                    desc = arcpy.Describe(mask_layer)
                    arcpy.env.extent = desc.extent
                    # Somehow every second features does not get properly copies. Don't know why
                    # If mask is empty feature get skipped and will be processed in the next loop
                    if not math.isnan(arcpy.env.extent.XMin):
                        # Sum area values for every year in mask lossyear layer
                        # Save results in temporary table and add feature ID as extra column
                        messages.AddMessage("Process feature {} out of {}".format(len(processed) + 1, row_count))
                        temp_table = "in_memory/feature_{}".format(row[0])
                        temp_tables.append(temp_table)

                        arcpy.gp.ZonalStatisticsAsTable_sa(mask_mosaic, "VALUE", value_mosaic, temp_table, "DATA", "SUM")

                        arcpy.AddField_management(temp_table, "FID", "LONG")
                        arcpy.CalculateField_management (temp_table, "FID", row[0])

                        # Make feature as processed
                        processed.append(row[0])

        # Once all features are processed quite while loop
        if id == sorted(processed):
            done = True

    if len(temp_tables) > 0:
        # Merge all results into one tab;e
        messages.AddMessage("Merge results")
        temp_merge = "in_memory/merge_table"

        arcpy.CreateTable_management(os.path.dirname(temp_merge), os.path.basename(temp_merge), temp_table)
        arcpy.Append_management(temp_tables, temp_merge)

        return temp_merge

    else:
        raise Exception("No features found in input Layer")

def mask_mosaic(mosaic, tcd_mosaic, tcd_threshold, messages):
    '''
    Mask loss year with TCD threshold
    :param lossyear_mosaic:
    :param tcd_mosaic:
    :param tcd_threshold:
    :return:
    '''

    messages.AddMessage("Load Raster functions")

    # Create raster function template file
    remap_tcd = raster_function.update_tcd_mask(tcd_threshold)
    mask = raster_function.mask_mosaic(tcd_mosaic)

    # Load raster functions
    raster_function.replace_raster_function(tcd_mosaic, remap_tcd)
    raster_function.replace_raster_function(mosaic, mask)


def clean_up(messages):
    """
    Delete all in_memort datasets
    :return:
    """

    messages.AddMessage("Clean up")

    arcpy.env.workspace = "in_memory"
    datasets = arcpy.ListDatasets()

    for dataset in datasets:
        arcpy.Delete_management(dataset)


def tc_loss(in_features, tcd_threshold, mosaic_workspace, out_table, messages):
    '''
    Calculate tree cover loss for input features
    :param in_features:
    :param tcd_threshold:
    :param mosaic_workspace:
    :param out_table:
    :param messages:
    :return:
    '''

    # Define mosaic layers
    lossyear_mosaic = os.path.join(mosaic_workspace, "lossyear")
    area_mosaic = os.path.join(mosaic_workspace, "area")
    tcd_mosaic = os.path.join(mosaic_workspace, "tcd")

    # Mask loss year using the TCD threshold
    mask_mosaic(lossyear_mosaic, tcd_mosaic, tcd_threshold, messages)

    # Calculating annual loss for every input feature
    zonal_stats_table = zonal_stats(lossyear_mosaic, area_mosaic, in_features, messages)

    # Create final output table and define fields
    arcpy.CreateTable_management (os.path.dirname(out_table), os.path.basename(out_table))
    arcpy.AddField_management(out_table, "FID", "LONG")
    arcpy.AddField_management(out_table, "YEAR", "TEXT")
    arcpy.AddField_management(out_table, "TCD", "LONG")
    arcpy.AddField_management(out_table, "LOSS_M2", "DOUBLE")

    # Select relevant fields from merged table
    cursor = arcpy.da.SearchCursor(zonal_stats_table, ["FID", "VALUE", "SUM"])

    # Create Insert cursor for output table
    newrows = arcpy.InsertCursor(out_table)

    # Loop over all rows in merge table and write results into output table
    for row in cursor:
        newrow = newrows.newRow()
        newrow.setValue("FID", row[0])
        if row[1] == 0:
            newrow.setValue("YEAR", "no loss")
        else:
            newrow.setValue("YEAR", 2000 + row[1])
        newrow.setValue("TCD", tcd_threshold)
        newrow.setValue("LOSS_M2", row[2])
        newrows.insertRow(newrow)

    # Delete all in_memory datasets
    clean_up(messages)


def biomass_loss(in_features, tcd_threshold, mosaic_workspace, out_table, messages):
    '''
    Calculate tree cover loss for input features
    :param in_features:
    :param tcd_threshold:
    :param mosaic_workspace:
    :param out_table:
    :param messages:
    :return:
    '''

    # Define mosaic layers
    lossyear_mosaic = os.path.join(mosaic_workspace, "lossyear")
    biomass_mosaic = os.path.join(mosaic_workspace, "biomass")
    tcd_mosaic = os.path.join(mosaic_workspace, "tcd")

    # Mask loss year using the TCD threshold
    mask_mosaic(lossyear_mosaic, tcd_mosaic, tcd_threshold, messages)

     # Mask biomass using the TCD threshold
    mask_mosaic(biomass_mosaic, tcd_mosaic, tcd_threshold, messages)

    # Calculating annual loss for every input feature
    zonal_stats_table = zonal_stats(lossyear_mosaic, biomass_mosaic, in_features, messages)

    # Create final output table and define fields
    arcpy.CreateTable_management (os.path.dirname(out_table), os.path.basename(out_table))
    arcpy.AddField_management(out_table, "FID", "LONG")
    arcpy.AddField_management(out_table, "YEAR", "TEXT")
    arcpy.AddField_management(out_table, "TCD", "LONG")
    arcpy.AddField_management(out_table, "BIOMASS_LOSS_MG", "DOUBLE")
    arcpy.AddField_management(out_table, "EMISSIONS_MT_CO2", "DOUBLE")

    # Select relevant fields from merged table
    cursor = arcpy.da.SearchCursor(zonal_stats_table, ["FID", "VALUE", "SUM"])

    # Create Insert cursor for output table
    newrows = arcpy.InsertCursor(out_table)

    # Loop over all rows in merge table and write results into output table
    for row in cursor:
        newrow = newrows.newRow()
        newrow.setValue("FID", row[0])
        if row[1] == 0:
            newrow.setValue("YEAR", "remaining biomass")
        else:
            newrow.setValue("YEAR", 2000 + row[1])
        newrow.setValue("TCD", tcd_threshold)
        newrow.setValue("BIOMASS_LOSS_MG", row[2])
        # TODO: Check actual carbon emissions formula
        newrow.setValue("EMISSIONS_MT_CO2", row[2]*.5*3.67/1000000)
        newrows.insertRow(newrow)

    # Delete all in_memory datasets
    clean_up(messages)
