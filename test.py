import arcpy
geo_map = arcpy.GetParameterAsText(0)
out = arcpy.GetParameterAsText(1)
arcpy.Dissolve_management(geo_map, out, "rating")



