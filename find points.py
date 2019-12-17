import arcpy
import math
import numpy as np
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt

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

def get_total_rating(poly, point, spacing):
        poly[TOTAL] = int(poly[STATIC] + distance_scale_factor*((point[NEAR_DIST]*-10/spacing)+10))
# gets a new set of points where the ideal points are halfway between the ith and ith +2 points also returns the total
# distance difference
def get_new_initial_points(last_best):
    prev_list = []
    new_list = []
    prev_points = arcpy.da.SearchCursor(last_best, ("SHAPE@",))
    for point in prev_points:
        prev_list.append(point[0])

    # makes the new list of initial points from the midpoints of the previous best points
    # it is important that a left right or right left order is maintained otherwise the midpoints will be incorrectly
    # calculated on the next iteration
    new_list.append(prev_list[0])
    for i in range(0, len(prev_list)-2):
        new_list.append(get_midpoint(prev_list[i], prev_list[i+2]))
    new_list.append(prev_list[len(prev_list)-1])
    new_best = arcpy.CopyFeatures_management(new_list, temp + str(fnum.i()))

    return new_best

# gets sum of the distances of two iterations of points
def get_total_distance(pnts1, pnts2):
    dist = 0
    for i in range(0, len(pnts1)):
        dist += get_distance(pnts1[i], pnts2[i])
    return dist

# returns a list of how much each point has changed between iterations
def get_distance_change(pnts1, pnts2):
    dist = []
    for i in range(0, len(pnts1)):
        dist.append(get_distance(pnts1[i], pnts2[i]))
    return dist

# returns the total change in change in distance over iterations. This should give an indication of whether the points
# are now oscillating over the iterations
def get_distance_change_difference(dist1, dist2):
    change = 0
    for i in range(0, len(dist1)):
            change += abs(dist1[i]-dist2[i])
    return change

#returns a list of distances between points
def get_point_seperations(points):
    dists = []
    for i in range(0, len(points)-1):
        dists.append(get_distance(points[i], points[i+1]))
    return dists

# returns distance between two points
def get_distance(point1, point2):
    x_dist = abs(point1.firstPoint.X-point2.firstPoint.X)
    y_dist = abs(point1.firstPoint.Y-point2.firstPoint.Y)
    distance = math.sqrt(x_dist**2 + y_dist**2)
    return distance


def tuple_to_point(tuple):
    p = arcpy.Point(tuple.X, tuple[1])
    return arcpy.PointGeometry(p)

def get_midpoint(point1, point2):
    x = (point1.firstPoint.X + point2.firstPoint.X)/2
    y = (point1.firstPoint.Y + point2.firstPoint.Y)/2
    p = arcpy.Point(x,y)
    return arcpy.PointGeometry(p)



try:
    SHAPE = 0
    NEAR_DIST = 1
    NEAR_X = 2
    NEAR_Y = 3
    BEST_X = 4
    BEST_Y = 5
    BEST_RATING = 6
    STATIC_PNT_RATING = 7
    STATIC = 1
    TOTAL = 2
    temp = "in_memory/temp"
    PERCENTAGE = "PERCENTAGE"
    END_POINTS = "END_POINTS"
    # tool inputs and outputs
    fnum = IncrementingNumber(-1)
    param_num = IncrementingNumber(-1)
    num_points = arcpy.GetParameter(param_num.i())
    fault = arcpy.GetParameterAsText(param_num.i())
    polys = arcpy.GetParameterAsText(param_num.i())
    distance_scale_factor = arcpy.GetParameter(param_num.i())
    iteration = arcpy.GetParameter(param_num.i())
    iteration_end_value = arcpy.GetParameter(param_num.i())
    bin_num = arcpy.GetParameter(param_num.i())
    final_points = arcpy.GetParameterAsText(param_num.i())

    search_4_len = arcpy.da.SearchCursor(fault, ("Shape_Length",))
    fault_length = None
    for length in search_4_len:
        fault_length = length[0]
        break
    spacing = fault_length / (num_points - 2)
    points = arcpy.GeneratePointsAlongLines_management(fault, temp + str(fnum.i()), 'DISTANCE', spacing, "", 'END_POINTS')
    last_point = str(num_points + 1)
    expression = "OBJECTID = " + last_point
    arcpy.AddMessage(expression)
    to_delete = arcpy.SelectLayerByAttribute_management(points, "NEW_SELECTION", expression)
    arcpy.DeleteRows_management(to_delete) #FIXME test me

    arcpy.AddMessage("Average point spacing: " + str(spacing))
    current_best_points = None
    dist = 1


    dist_dif = iteration_end_value +1

    # holds a list of change in change in distances for determining whether the points are oscillating
    old_dists = None
    rating = 0
    i = 1
    old_best = None
    while dist_dif > iteration_end_value:
        # add a total rating field to be filled later
        # deleting the field ensures the field is empty before the program begins
        arcpy.DeleteField_management(polys, "tot_score")
        arcpy.AddField_management(polys, "tot_score", "SHORT")
        # for storing the current best value in each point
        arcpy.DeleteField_management(points, "BEST_X")
        arcpy.AddField_management(points, "BEST_X", "DOUBLE")
        arcpy.DeleteField_management(points, "BEST_Y")
        arcpy.AddField_management(points, "BEST_Y", "DOUBLE")
        arcpy.DeleteField_management(points, "BEST_SCORE")
        arcpy.AddField_management(points, "BEST_SCORE", "DOUBLE")
        arcpy.DeleteField_management(points, "stat_rate")
        arcpy.AddField_management(points, "stat_rate", "DOUBLE")
        good_points = []
        search_poly = arcpy.da.UpdateCursor(polys, ("SHAPE@", "stat_rate", "tot_score"))
        for poly in search_poly:
            find_nearest(poly, points)
            search_point = arcpy.da.UpdateCursor(points, ("SHAPE@", "NEAR_DIST", "NEAR_X", "NEAR_Y", "BEST_X", "BEST_Y", "BEST_SCORE", "stat_rate"))
            for point in search_point:
                get_total_rating(poly, point,spacing)
                search_poly.updateRow(poly)
                if point[BEST_X] is None:
                    point[BEST_X] = point[NEAR_X]
                    point[BEST_Y] = point[NEAR_Y]
                    point[BEST_Y] = point[NEAR_Y]
                    point[BEST_RATING] = poly[TOTAL]
                    point[STATIC_PNT_RATING] = poly[STATIC]
                    search_point.updateRow(point)
                    best_rating = poly[TOTAL]
                elif poly[TOTAL] > point[BEST_RATING]:
                    point[BEST_X] = point[NEAR_X]
                    point[BEST_Y] = point[NEAR_Y]
                    point[BEST_RATING] = poly[TOTAL]
                    point[STATIC_PNT_RATING] = poly[STATIC]
                    search_point.updateRow(point)
        best_points = arcpy.da.SearchCursor(points, ("BEST_X", "BEST_Y", "stat_rate"))
        rating = 0
        for best_point in best_points:

            # calculates total static rating
            rating += best_point[2]

            # makes a list of the best points for this iteration
            pnt = arcpy.Point(best_point[0], best_point[1])
            good_points.append(arcpy.PointGeometry(pnt))



        # alternative iteration end checker
        new_dists = None
        if old_best is not None:
            dist = get_total_distance(old_best, good_points)
            new_dists = get_distance_change(old_best, good_points)
        if old_dists is not None:
            dist_dif = get_distance_change_difference(old_dists, new_dists)
        old_dists = new_dists
        old_best = good_points

        # determines if the program with run in iteration mode or not
        if not iteration:
            dist_dif = 0

        # makes a feature class from the best current points
        if dist_dif < iteration_end_value:
            current_best_points = arcpy.CopyFeatures_management(good_points, final_points)
        else:
            current_best_points = arcpy.CopyFeatures_management(good_points, temp + str(fnum.i()))
            new_ideal_points = get_new_initial_points(current_best_points)
            points = new_ideal_points

        arcpy.AddMessage("output stats for iteration " + str(i))
        arcpy.AddMessage("--------------------------------")
        arcpy.AddMessage("rating: " + str(rating))
        arcpy.AddMessage("sum of distance change: " + str(dist))
        arcpy.AddMessage("sum of change in change in distance: " + str(dist_dif))

        i += 1


    if old_best is not None:
        final_distance_data = get_point_seperations(old_best)
        num_bins = bin_num
        n, bins, patches = plt.hist(final_distance_data, num_bins, facecolor='blue', alpha=0.5)
        plt.xlabel('point separation (m)')
        plt.ylabel('count')
        plt.show()
finally:
    arcpy.Delete_management("in_memory")

