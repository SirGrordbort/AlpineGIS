import arcpy
import math
import matplotlib.pyplot as plt


# a number that can be easily incremented (in place of the ++num java code)
class IncrementingNumber:
    def __init__(self, num):
        self.num = num

    # increments the number this class holds by 1
    def i(self):
        self.num += 1
        return self.num

    # returns the number held by this class
    def get(self):
        return self.num


# @param poly is an update cursor row representing a polygon from the rated map
# @param points is a feature class of the ideal points along the fault
# adds the coordinates of the nearest point on the polygon to the point feature class
def find_nearest(poly, points):
    arcpy.Near_analysis(points, poly[PolyEnum.SHAPE], "", "LOCATION", "", "")


# @param poly is an update cursor row representing a polygon from the rated map
# @param point is an update cursor row representing a point from the theoretical set of points along the fault
# @param spacing is the average spacing between the theoretical points along the fault
# calculates the total rating for each point relative to the given polygon and adds that rating to the polygon
def get_total_rating(poly, point, spacing):
    poly[PolyEnum.TOTAL] = int(
        poly[PolyEnum.STATIC] + distance_scale_factor * ((point[PointEnum.NEAR_DIST] * -10 / spacing) + 10))


# @param last_best a feature class containing the previous iterations highest rated points
# @return a new set of points where these are halfway between the ith and ith +2 last best points
def get_new_initial_points(last_best):
    prev_list = []
    new_list = []
    # turns the prev points feature class into a list which is easier to work with
    prev_points = arcpy.da.SearchCursor(last_best, ("SHAPE@",))
    for point in prev_points:
        prev_list.append(point[0])

    # end points stay in their location from the first iteration to avoid the point distribution from becoming too tight
    new_list.append(prev_list[0])
    for i in range(0, len(prev_list) - 2):
        new_list.append(
            get_midpoint(prev_list[i], prev_list[i + 2]))
    new_list.append(prev_list[len(prev_list) - 1])
    # turns the list of new theoretical points into a feature class
    new_best = arcpy.CopyFeatures_management(new_list, temp + str(fnum.i()))
    return new_best


# @param pnts1 and pnts2 are both lists of pointGeometries
# @return dist is the sum of the distances between each two corresponding points in the lists
def get_total_distance(pnts1, pnts2):
    dist = 0
    for i in range(0, len(pnts1)):
        dist += get_distance(pnts1[i], pnts2[i])
    return dist


# @param pnts1 and pnts2 are both lists of pointGeometries
# @return dist is a list of floats describing how much each point has changed between iterations
def get_distance_change(pnts1, pnts2):
    dist = []
    for i in range(0, len(pnts1)):
        dist.append(get_distance(pnts1[i], pnts2[i]))
    return dist


# @param dist1 and dist2 are lists of the change in distance for each point from iteration i to i+1 and from i+1 to i+2
# @return change is the sum of the difference between each
def get_distance_change_difference(dist1, dist2):
    change = 0
    for i in range(0, len(dist1)):
        change += abs(dist1[i] - dist2[i])
    return change


# @param points is a list of pointGeometries
# @return dists is a list of distances between points
def get_point_seperations(points):
    dists = []
    for i in range(0, len(points) - 1):
        dists.append(get_distance(points[i], points[i + 1]))
    return dists


# @param point1 and point2 are pointGeometry objects
# @return distance is the between two points
def get_distance(point1, point2):
    x_dist = abs(point1.firstPoint.X - point2.firstPoint.X)
    y_dist = abs(point1.firstPoint.Y - point2.firstPoint.Y)
    distance = math.sqrt(x_dist ** 2 + y_dist ** 2)
    return distance


# @param point1 and point2 are pointGeometry objects
# @return pointGeometry with coordinates at the midpoint between point1 and point2
def get_midpoint(point1, point2):
    x = (point1.firstPoint.X + point2.firstPoint.X) / 2
    y = (point1.firstPoint.Y + point2.firstPoint.Y) / 2
    p = arcpy.Point(x, y)
    return arcpy.PointGeometry(p)


# @param point is an update cursor row representing a point from the theoretical points feature class
# @param poly is an update cursor row representing a polygon from the rated map
# assigns each point row information from the polygon row
def info_to_point(point, poly):
    point[PointEnum.BEST_X] = point[PointEnum.NEAR_X]
    point[PointEnum.BEST_Y] = point[PointEnum.NEAR_Y]
    point[PointEnum.BEST_RATING] = poly[PolyEnum.TOTAL]
    point[PointEnum.STATIC] = poly[PolyEnum.STATIC]
    point[PointEnum.FAULT_SIDE] = poly[PolyEnum.FAULT_SIDE]
    point[PointEnum.DOC_LAND] = poly[PolyEnum.DOC_LAND]
    point[PointEnum.ROCK_TYPE] = poly[PolyEnum.ROCK_TYPE]
    search_point.updateRow(point)


# @param feature is a feature class
# @param point is a feature class containing a single pointGeometry object
# @return near_dist.next()[0] is the shortest distance between the feature and the point
def get_dist_2_feature(feature, point):
    arcpy.Near_analysis(feature, point)
    near_dist = arcpy.da.SearchCursor(feature, ("NEAR_DIST",))
    return near_dist.next()[0]


try:
    # enum classes simply to make code more readable
    class PolyEnum:
        def __init__(self):
            self.SHAPE = 0
            self.STATIC = 1
            self.TOTAL = 2
            self.FAULT_SIDE = 3
            self.DOC_LAND = 4
            self.ROCK_TYPE = 5


    class PointEnum:
        def __init__(self):
            self.SHAPE = 0
            self.NEAR_DIST = 1
            self.NEAR_X = 2
            self.NEAR_Y = 3
            self.BEST_X = 4
            self.BEST_Y = 5
            self.BEST_RATING = 6
            self.STATIC = 7
            self.ROCK_TYPE = 8
            self.FAULT_SIDE = 9
            self.DOC_LAND = 10
            self.DIST_2_RD = 11
            self.DIST_2_FLT = 12


    # initialise helper classes
    PointEnum = PointEnum()
    PolyEnum = PolyEnum()
    fnum = IncrementingNumber(-1)
    param_num = IncrementingNumber(-1)
    temp = "in_memory/temp"

    # tool inputs
    num_points = arcpy.GetParameter(param_num.i())
    fault = arcpy.GetParameterAsText(param_num.i())
    roads = arcpy.GetParameterAsText(param_num.i())
    polys = arcpy.GetParameterAsText(param_num.i())
    distance_scale_factor = arcpy.GetParameter(param_num.i())
    iteration = arcpy.GetParameter(param_num.i())
    iteration_end_value = arcpy.GetParameter(param_num.i())
    bin_num = arcpy.GetParameter(param_num.i())

    # tool output
    final_points = arcpy.GetParameterAsText(param_num.i())

    # gets the spacing for the theoretical points along the fault
    search_4_len = arcpy.da.SearchCursor(fault, ("Shape_Length",))
    fault_length = None
    for length in search_4_len:
        fault_length = length[0]
        break
    spacing = fault_length / (num_points - 1)

    # makes the initial theoretical points along the fault
    points = None
    points = arcpy.GeneratePointsAlongLines_management(fault, points, 'DISTANCE', spacing, "", 'END_POINTS')

    # removes the last point from the theoretical points
    # necessary because the last point sits on top of the second to last point
    last_point = str(num_points + 1)
    expression = "OBJECTID = " + last_point
    to_delete = arcpy.SelectLayerByAttribute_management(points, "NEW_SELECTION", expression)
    arcpy.DeleteRows_management(to_delete)

    # spatial reference used for making new points
    spatial_ref = arcpy.Describe(points).spatialReference
    arcpy.AddMessage("Average point spacing: " + str(spacing))

    current_best_points = None  # holds a feature class containing the current highest rated points
    dist = 1  # holds sum of the distance between the points in the ith and i +1 iterations

    # holds the sum of the difference in distance between the i to i+1 and i+1 to i+2 iterations. Initialised to one
    # more than the end value to ensure at least one iteration is run
    dist_dif = iteration_end_value + 1

    # holds a list of change in change in distances for determining whether the points are oscillating
    old_dists = None
    i = 1  # number of iterations
    old_best = None  # a list of point geometries that holds the highest rated points for the previous iteration

    while dist_dif > iteration_end_value:
        # adds necessary fields to the input polygons and points
        # deleting the field ensures the field is empty before the program begins
        arcpy.DeleteField_management(polys, "tot_score")
        arcpy.AddField_management(polys, "tot_score", "LONG")
        arcpy.DeleteField_management(points, "BEST_X")
        arcpy.AddField_management(points, "BEST_X", "DOUBLE")
        arcpy.DeleteField_management(points, "BEST_Y")
        arcpy.AddField_management(points, "BEST_Y", "DOUBLE")
        arcpy.DeleteField_management(points, "BEST_SCORE")
        arcpy.AddField_management(points, "BEST_SCORE", "DOUBLE")
        arcpy.DeleteField_management(points, "stat_rate")
        arcpy.AddField_management(points, "stat_rate", "DOUBLE")
        arcpy.DeleteField_management(points, "rock_type")
        arcpy.AddField_management(points, "rock_type", "TEXT")
        arcpy.DeleteField_management(points, "fault_side")
        arcpy.AddField_management(points, "fault_side", "TEXT")
        arcpy.DeleteField_management(points, "doc_land")
        arcpy.AddField_management(points, "doc_land", "TEXT")
        arcpy.DeleteField_management(points, "dist_to_rd")
        arcpy.AddField_management(points, "dist_2_rd", "DOUBLE")
        arcpy.DeleteField_management(points, "dist_2_flt")
        arcpy.AddField_management(points, "dist_2_flt", "DOUBLE")
        good_points = []  # a list of the best points for this iteration
        search_poly = arcpy.da.UpdateCursor(polys,
                                            (
                                                "SHAPE@", "stat_rate", "tot_score", "fault_side", "doc_land",
                                                "rock_group"))
        for poly in search_poly:
            find_nearest(poly, points)
            search_point = arcpy.da.UpdateCursor(points, (
                "SHAPE@", "NEAR_DIST", "NEAR_X", "NEAR_Y", "BEST_X", "BEST_Y", "BEST_SCORE", "stat_rate", "rock_type",
                "fault_side", "doc_land", "dist_2_rd", "dist_2_flt"))
            for point in search_point:
                get_total_rating(poly, point, spacing)
                search_poly.updateRow(poly)
                if point[PointEnum.BEST_X] is None:
                    info_to_point(point, poly)  # transfers the required information from each polygon to each point
                elif poly[PolyEnum.TOTAL] > point[PointEnum.BEST_RATING]:
                    info_to_point(point, poly)

        best_points = arcpy.da.UpdateCursor(points,
                                            ("BEST_X", "BEST_Y", "stat_rate", "dist_2_rd", "dist_2_flt", "SHAPE@"))
        rating = 0  # the total static rating summed over each point
        for best_point in best_points:
            # calculates total static rating
            rating += best_point[2]

            # makes a list of the best points for this iteration
            pnt = arcpy.Point(best_point[0], best_point[1])
            good_point = arcpy.PointGeometry(pnt, spatial_ref)
            good_points.append(good_point)

            # changes the best point coordinates to the actual best coordinates
            best_point[5] = good_point
            best_points.updateRow(best_point)

        # Iteration end checker
        new_dists = None
        if old_best is not None:  # ensures old_best is initialised so it can be compared to the current set of points
            dist = get_total_distance(old_best, good_points)  # calculates the dist
            new_dists = get_distance_change(old_best, good_points)
        # ensures an old dists is initialised so that the get_distance_change_difference method has an initial and
        # current set of points to compare
        if old_dists is not None:
            dist_dif = get_distance_change_difference(old_dists, new_dists)
        # updates the variables that store the previous iteration values with this iterations values in preparation for
        # the next iteration
        old_dists = new_dists
        old_best = good_points

        # determines if the program with run in iteration mode or not
        if not iteration:
            dist_dif = -1

        # checks if this is the last iteration
        if dist_dif <= iteration_end_value:
            # fills the dist_2_rd and dist_2_fault
            update_attr_table = arcpy.da.UpdateCursor(points, ("SHAPE@", "dist_2_rd", "dist_2_flt"))
            for point in update_attr_table:
                feature_point = arcpy.CopyFeatures_management(point[0], temp + str(fnum.i()))
                point[1] = get_dist_2_feature(roads, point[0])
                point[2] = get_dist_2_feature(fault, point[0])
                update_attr_table.updateRow(point)
            # deletes irrelevant information from the attribute table
            arcpy.DeleteField_management(points, "ORIG_FID")
            arcpy.DeleteField_management(points, "NEAR_FID")
            arcpy.DeleteField_management(points, "NEAR_DIST")
            arcpy.DeleteField_management(points, "NEAR_X")
            arcpy.DeleteField_management(points, "NEAR_Y")

            # makes a feature class from the best current points
            current_best_points = arcpy.CopyFeatures_management(points, final_points)
        else:
            # sets up the new theoretical points for the next iteration
            current_best_points = arcpy.CopyFeatures_management(good_points, temp + str(fnum.i()))
            new_ideal_points = get_new_initial_points(current_best_points)
            points = new_ideal_points

        arcpy.AddMessage("output stats for iteration " + str(i))
        arcpy.AddMessage("--------------------------------")
        arcpy.AddMessage("rating: " + str(rating))
        arcpy.AddMessage("sum of distance change: " + str(dist))
        arcpy.AddMessage("sum of change in change in distance: " + str(dist_dif))

        i += 1
    # ensures the histogra has data to output
    if old_best is not None:
        # creats and outputs hisstogram based on point seperation
        final_distance_data = get_point_seperations(old_best)
        num_bins = bin_num
        n, bins, patches = plt.hist(final_distance_data, num_bins, facecolor='blue', alpha=0.5)
        plt.xlabel('point separation (m)')
        plt.ylabel('count')
        plt.show()
finally:
    # ensures the ram used is returned to the system
    arcpy.Delete_management("in_memory")
