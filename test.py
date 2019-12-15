import arcpy
import math
import numpy as np
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt

input = arcpy.GetParameterAsText(0)
def get_distance(point1, point2):
    x_dist = abs(point1.firstPoint.X-point2.firstPoint.X)
    y_dist = abs(point1.firstPoint.Y-point2.firstPoint.Y)
    distance = math.sqrt(x_dist**2 + y_dist**2)
    arcpy.AddMessage("distance " + str(distance))
    return distance

def get_final_distances(points):
    dists = []
    for i in range(0, len(points)-1):
        dists.append(get_distance(points[i], points[i+1]))
    return dists
points = []
for i in arcpy.da.SearchCursor(input, ("SHAPE@", )):
    points.append(i[0])
final_distance_data = get_final_distances(points)
num_bins = 5
n, bins, patches = plt.hist(final_distance_data, num_bins, facecolor='blue', alpha=0.5)
plt.show()