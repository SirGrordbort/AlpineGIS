import arcpy

try:
    for shape in arcpy.da.SearchCursor('fishnet_label_Clip', "Shape"):
        point = arcpy.Point(shape[0][0], shape[0][1])
        point_geo = arcpy.PointGeometry(point)
        point_class = arcpy.CopyFeatures_management(point_geo, "in_memory/temp1")
        intersect = [point_class, "BufferedSide"]
        intersection = arcpy.Intersect_analysis(intersect, "in_memory/temp2")
        print(arcpy.management.GetCount(intersection))
finally:
    arcpy.Delete_management("in_memory")