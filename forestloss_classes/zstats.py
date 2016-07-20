import arcpy
arcpy.CheckOutExtension("Spatial")
import os

def zonal_stats_mask(snapraster,fc_geo,scratch_gdb,maindir,shapefile,column_name2,outdir):
    arcpy.env.snapRaster = snapraster
    arcpy.env.scratchWorkspace = scratch_gdb

    extent = fc_geo.extent
    envextent = arcpy.Extent(extent.XMin, extent.YMin, extent.XMax, extent.YMax)
    arcpy.env.extent = envextent
    layer = os.path.join(maindir, "shapefile")
    arcpy.MakeFeatureLayer_management(shapefile, layer)
    exp = """"FC_NAME" = '{}'""".format(column_name2)
    arcpy.AddMessage("selecting by attribute")
    arcpy.SelectLayerByAttribute_management(layer, "NEW_SELECTION", exp)
    arcpy.AddMessage("converting layer to feature class")
    arcpy.FeatureClassToFeatureClass_conversion(layer, outdir, column_name2)
    mask = os.path.join(outdir, column_name2 + ".shp")
    return mask, envextent

def zonal_stats(zone_raster, value_raster, filename, calculation, snapraster,mask,scratch_gdb,outdir,column_name2,orig_fcname, envextent):
    arcpy.AddMessage(           "zonal stats")
    arcpy.env.scratchWorkspace = scratch_gdb
    arcpy.env.snapRaster = snapraster
    arcpy.env.mask = mask
    arcpy.env.extent = envextent

    if calculation == "biomass_max" or calculation == "forest_loss" or calculation == "area_only":
        arcpy.env.cellSize = "MAXOF"
    if calculation == "biomass_min":
        arcpy.env.cellSize = "MINOF"
    if calculation == "area_30m" or calculation == "biomass_30m":
        arcpy.env.cellSize = "MAXOF"
    z_stats_tbl = os.path.join(outdir, column_name2 + "_" + filename + "_" + calculation)
    arcpy.gp.ZonalStatisticsAsTable_sa(zone_raster, "VALUE", value_raster, z_stats_tbl, "DATA", "SUM")
    # add a field to identify the table onces it is merged with the other zonal stats tables
    arcpy.AddField_management(z_stats_tbl, "ID", "TEXT")
    arcpy.CalculateField_management(z_stats_tbl, "ID", "'" + str(orig_fcname) + "'", "PYTHON_9.3")
    arcpy.AddField_management(z_stats_tbl, "uID", "TEXT")
    arcpy.CalculateField_management(z_stats_tbl, "uID", """!ID!+"_"+str( !Value!)""", "PYTHON_9.3", "")
    # arcpy.AddMessage("     " + str(datetime.datetime.now() - zstatstime))

def zonal_stats_nomask(zone_raster, value_raster, filename, calculation, snapraster,scratch_gdb,outdir,column_name2,orig_fcname):
    # zstatstime = datetime.datetime.now()
    arcpy.AddMessage(           "zonal stats")
    arcpy.env.scratchWorkspace = scratch_gdb
    arcpy.env.snapRaster = snapraster
    if calculation == "biomass_max" or calculation == "forest_loss"or calculation == "area_only":
        arcpy.env.cellSize = "MAXOF"
    if calculation == "biomass_min":
        arcpy.env.cellSize = "MINOF"
    if calculation == "area_30m" or calculation == "biomass_30m":
        arcpy.env.cellSize = "MAXOF"
    z_stats_tbl = os.path.join(outdir, column_name2 + "_" + filename + "_" + calculation)
    arcpy.gp.ZonalStatisticsAsTable_sa(zone_raster, "VALUE", value_raster, z_stats_tbl, "DATA", "SUM")
    # add a field to identify the table onces it is merged with the other zonal stats tables
    arcpy.AddField_management(z_stats_tbl, "ID", "TEXT")
    arcpy.CalculateField_management(z_stats_tbl, "ID", "'" + orig_fcname + "'", "PYTHON_9.3")
    arcpy.AddField_management(z_stats_tbl, "uID", "TEXT")
    arcpy.CalculateField_management(z_stats_tbl, "uID", """!ID!+"_"+str( !Value!)""", "PYTHON_9.3", "")
    # arcpy.AddMessage("     " + str(datetime.datetime.now() - zstatstime))
