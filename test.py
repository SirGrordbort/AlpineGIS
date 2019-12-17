import arcpy
fault =arcpy.GetParameterAsText(0)
num_pnts = arcpy.GetParameter(1)
points = arcpy.GetParameterAsText(2)
search_4_len = arcpy.da.SearchCursor(fault, ("Shape_Length",))
fault_length = None
for length in search_4_len:
    fault_length = length[0]
    break
spacing = fault_length / (num_pnts - 1)
percentage = 100/(num_pnts)
points = arcpy.GeneratePointsAlongLines_management(fault, points, 'DISTANCE', spacing, "", 'END_POINTS')
last_point = str(num_pnts +1)
expression = "OBJECTID = " + last_point
arcpy.AddMessage(expression)
to_delete = arcpy.SelectLayerByAttribute_management(points, "NEW_SELECTION", expression)
arcpy.DeleteRows_management(to_delete)