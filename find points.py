import arcpy

def find_nearest(poly, points):
    arcpy.Near_analysis(points, poly[SHAPE],"","LOCATION","","")

def get_total_rating(poly, point):
    poly[TOTAL] = int(poly[STATIC] + point[NEAR_DIST]*-500/300000+10) #FIXME



SHAPE = 0
LENGTH = 1
NEAR_DIST = 2
NEAR_X = 3
NEAR_Y = 4
BEST_X = 5
BEST_Y = 6
BEST_RATING = 7
STATIC = 1
TOTAL = 2

# tool inputs and outputs
points = arcpy.GetParameterAsText(0)
polys = arcpy.GetParameterAsText(1)
out_polys = arcpy.GetParameterAsText(2)

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
    search_point = arcpy.da.UpdateCursor(points, ("SHAPE@", "Shape_Leng", "NEAR_DIST", "NEAR_X", "NEAR_Y", "BEST_X", "BEST_Y", "BEST_SCORE"))
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
arcpy.CopyFeatures_management(good_points, out_polys)

