import arcpy
# a number that can be easily incremented (in place of the ++num java code)
class IncrementingNumber:
    def __init__(self, num):
        self.num = num

    # increments the number this class holds by 1
    def i(self):
        self.num += 1
        return self.num

    def get(self):
        return self.num

def find_nearest(poly, points):
    arcpy.Near_analysis(points, poly[SHAPE],"","LOCATION","","")

def get_total_rating(poly, point):
    poly[TOTAL] = int(poly[STATIC] + (point[NEAR_DIST]*-500/300000+10)) #FIXME

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
    new_best = arcpy.CopyFeatures_management(new_list, temp + str(fnum.i()))

    return new_best

def tuple_to_point(tuple):
    p = arcpy.Point(tuple.X, tuple[1])
    return arcpy.PointGeometry(p)

def get_midpoint(point1, point2):
    x = (point1.firstPoint.X + point2.firstPoint.X)/2
    y = (point1.firstPoint.Y + point2.firstPoint.Y)/2
    p = arcpy.Point(x,y)
    return arcpy.PointGeometry(p)

SHAPE = 0
NEAR_DIST = 1
NEAR_X = 2
NEAR_Y = 3
BEST_X = 4
BEST_Y = 5
BEST_RATING = 6
STATIC = 1
TOTAL = 2
temp = "temp"
# tool inputs and outputs
points = arcpy.GetParameterAsText(0)
polys = arcpy.GetParameterAsText(1)
final_points = arcpy.GetParameterAsText(2)
fnum = IncrementingNumber(-1)
current_best_points = None
for x in range(0,3):
    # add a total rating field to be filled later
    arcpy.AddField_management(polys, "tot_score", "SHORT")
    # for storing the current best value in each point
    arcpy.AddField_management(points, "BEST_X", "DOUBLE")
    arcpy.AddField_management(points, "BEST_Y", "DOUBLE")
    arcpy.AddField_management(points, "BEST_SCORE", "DOUBLE")
    good_points = []
    search_poly = arcpy.da.UpdateCursor(polys, ("SHAPE@", "static_rating", "tot_score"))
    for poly in search_poly:
        find_nearest(poly, points)
        search_point = arcpy.da.UpdateCursor(points, ("SHAPE@", "NEAR_DIST", "NEAR_X", "NEAR_Y", "BEST_X", "BEST_Y", "BEST_SCORE"))
        for point in search_point:
            get_total_rating(poly, point)
            search_poly.updateRow(poly)
            if point[BEST_X] is None:
                point[BEST_X] = point[NEAR_X]
                point[BEST_Y] = point[NEAR_Y]
                point[BEST_RATING] = poly[TOTAL]
                search_point.updateRow(point)
                best_rating = poly[TOTAL]
            elif poly[TOTAL] > point[BEST_RATING]:
                point[BEST_X] = point[NEAR_X]
                point[BEST_Y] = point[NEAR_Y]
                point[BEST_RATING] = poly[TOTAL]
                search_point.updateRow(point)

    best_points = arcpy.da.SearchCursor(points, ("BEST_X", "BEST_Y"))
    for best_point in best_points:
        pnt = arcpy.Point(best_point[0], best_point[1])
        good_points.append(arcpy.PointGeometry(pnt))


    current_best_points = arcpy.CopyFeatures_management(good_points, temp + str(fnum.i()))
    points = get_new_initial_points(current_best_points)

final_points = current_best_points
arcpy.Delete_management("in_memory")

