import arcpy

def get_new_initial_points(last_best):
    prev_list = []
    new_list = []
    prev_points = arcpy.da.SearchCursor(last_best, ("SHAPE@",))
    for point in prev_points:
        prev_list.append(point[0])

    # makes the new list of initial points from the midpoints of the previous best points
    # it is important that a left right or right left order is maintained otherwise the midpoints will be incorrectly
    # calculated on the next iteration
    new_list.append(prev_list[0])  # FIXME shape might have one more step before it is a tuple
    for i in range(0, len(prev_list)-2):
        new_list.append(get_midpoint(prev_list[i], prev_list[i+2]))
    new_list.append(prev_list[len(prev_list)-1])
    new_best = arcpy.CopyFeatures_management(new_list, out)
    return new_best

def tuple_to_point(tuple):
    p = arcpy.Point(tuple.X, tuple[1])
    return arcpy.PointGeometry(p)

def get_midpoint(point1, point2):
    x = (point1.firstPoint.X + point2.firstPoint.X)/2
    y = (point1.firstPoint.Y + point2.firstPoint.Y)/2
    p = arcpy.Point(x,y)
    return arcpy.PointGeometry(p)


in_points = arcpy.GetParameterAsText(0)
out = arcpy.GetParameterAsText(1)
get_new_initial_points(in_points)
