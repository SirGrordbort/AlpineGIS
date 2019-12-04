# a program to build the layers required to determine where to put siesmometers on a fault based on:
# The fault location (feature class)
# The prefered side of the fault(Boolean)
# The Land ownership (feature class)
# The Geology of the area (feature class)
# The spacing requirements for the siesmometers (double?)
# The accessability of the site
# CMCA feature class Common Marine and Coastal Area
# CLB feature class Cross Lease Building
# CI customary entitlement
# easment
# FST Fee Simple Title
# FDU future development unit
# Hydro
# Lease
# git testing
import time
import arcpy
import copy


# try:


# stores information necessary for the program to run
class Info:
    def __init__(self):
        self.buffered_fault = None
        self.buffered_side = None
        self.buffered_road = None
        self.clipped_doc = None
        self.clipped_dissolved_doc = None
        self.unioned_layers = None

    # gets relevant info from the tool inputs in arcpro
    def get_info(self):
        param_num = IncrementingNumber(-1)
        self.fault_buffer = self.get_fault_buffer(param_num)
        self.side_buffer = self.get_side_buffer(param_num)
        self.road_buffer = self.get_road_buffer(param_num)
        # self.ownership_info = OwnershipInfo(param_num)
        self.doc_land = self.get_doc_land(param_num)
        # self.analysis_zone = self.get_zone_buffer(param_num)
        self.union_output = arcpy.GetParameterAsText(param_num.i())
        self.theoretical_points = arcpy.GetParameterAsText(param_num.i())

        # TODO self.geology = arcpy.GetParameterAsText(2)
        # TODO self.idealSpacing = arcpy.GetParameterAsText(3)

    def get_doc_land(self, param_num):
        return [arcpy.GetParameterAsText(param_num.i()), arcpy.GetParameterAsText(param_num.i())]

    def get_fault_buffer(self, param_num):
        buffer_params = self.get_params(param_num, 7)
        buffer_params[METHOD] = "ALL"
        # prep_tools = PrepTools()
        # buffer_params[INPUT] = prep_tools.prep_alpine_fault(buffer_params[INPUT])
        return buffer_params

    def get_side_buffer(self, param_num):
        buffer_params = []
        self.add_empty_strings(buffer_params, 0, 7)
        buffer_params[INPUT] = arcpy.CopyFeatures_management(self.fault_buffer[INPUT], temp + str(fnum.i()))
        buffer_params[OUTPUT] = arcpy.GetParameterAsText(param_num.i())
        buffer_params[DISTANCE] = arcpy.GetParameterAsText(param_num.i())
        buffer_params[SIDE] = "LEFT"
        buffer_params[METHOD] = "ALL"
        return buffer_params

    # TODO ensure the appropriate parameters are added to the tool
    def get_road_buffer(self, param_num):
        buffer_params = self.get_params(param_num, 3)
        self.add_empty_strings(buffer_params, 3, 5)
        # merge type
        buffer_params.append(arcpy.GetParameterAsText(param_num.i()))
        self.add_empty_strings(buffer_params, 6, 7)

        return buffer_params

    # gets info relating to the area of interest around the fault
    def get_zone_buffer(self, param_num):
        buffer_params = [self.fault_buffer[INPUT]]
        buffer_params.append(temp + str(fnum.i()))
        # size of zone
        buffer_params.append(arcpy.GetParameterAsText(param_num.i()))
        self.add_empty_strings(buffer_params, 3, 7)
        return buffer_params

    # gets a list of parameters from the arcpro tool UI
    def get_params(self, param_num, num_of_params):
        params = []
        for num in range(num_of_params):
            params.append(arcpy.GetParameterAsText(param_num.i()))
        return params

    # adds empty strings in the place of unused parameters
    def add_empty_strings(self, list, start, end):
        for num in range(start, end):
            list.append("")


class OwnershipInfo:
    def __init__(self, parameterNumber):
        assert parameterNumber.get() >= 0, "parameterNumber is negative"
        self.parcel_intent = {}
        self.ownership = arcpy.GetParameterAsText(parameterNumber.i())
        self.parcel_intent["'Fee Simple Title'"] = arcpy.GetParameterAsText(parameterNumber.i())
        self.parcel_intent["'DCDB'"] = arcpy.GetParameterAsText(parameterNumber.i())
        self.is_not_split = True

    # method that uses the ownership metadata to split the ownership into layers based on the land parcel intent field
    def split(self):
        self.is_not_split = False
        for parcel_str in self.parcel_intent.keys():
            selected = arcpy.SelectLayerByAttribute_management(self.ownership, "NEW_SELECTION",
                                                               "PARCEL_INT = " + parcel_str)
            copy_destination = self.parcel_intent.get(parcel_str, -1)
            # Error checking
            if copy_destination == -1:
                raise ValueError("missing key for" + parcel_str)
            arcpy.CopyFeatures_management(selected, copy_destination)

    def get_DCDB(self):
        return self.parcel_intent.get("'DCDB'")

    def get_FST(self):
        return self.parcel_intent.get("'Fee Simple Title'")


# for preparing data to be input into the tools
class PrepTools:

    def prep_alpine_fault(self, fault):
        selected = arcpy.SelectLayerByAttribute_management(fault, "NEW_SELECTION",
                                                           "NAME = 'Alpine Fault'")
        return arcpy.CopyFeatures_management(selected, temp + str(fnum.i()))

    def get_rating_fields(self, fc):
        rating_fields = []
        for field in arcpy.ListFields(fc):
            fname = field.name
            if fname.startswith("rating"):
                rating_fields.append(fname)
        return rating_fields

    def list_for_tool(self, info):

        # precondition checks
        if info.buffered_fault is None:
            raise TypeError("buffered_fault has not been initialised")
        if info.buffered_side is None:
            raise TypeError("buffered_side has not been initialised")
        if info.buffered_road is None:
            raise TypeError("buffered_road has not been initialised")
        if info.clipped_dissolved_doc is None:
            raise TypeError("doc land has not been dissolved")

        input_features = [info.buffered_fault, info.buffered_side, info.buffered_road, info.clipped_dissolved_doc]
        return input_features


# For running arcpy tools
class Tool:

    # constructor that gets the required buffer information
    def __init__(self):
        pass

    # adds a field to a list of feature classes
    def add_field(self, f_c_list, f_name, f_type):
        for f_class in f_c_list:
            arcpy.AddField_management(f_class, f_name, f_type)

        # post condition check

    # fills a field with a specific value
    def fill_field(self, f_class, f_name, value):
        cursor = arcpy.da.UpdateCursor(f_class, (f_name,))
        for row in cursor:
            row[0] = value
            cursor.updateRow(row)

    # fills a field with the sum of values from other fields within the given feature
    def fill_field_from_sum(self, f_class, to_update, f_names):
        # precondition check
        fnames = []
        for field in arcpy.ListFields(f_class):
            fnames.append(field.name)
        for name in f_names:
            assert fnames.__contains__(name)
        assert fnames.__contains__(to_update)

        search = arcpy.da.SearchCursor(f_class, f_names)
        update = arcpy.da.UpdateCursor(f_class, (to_update,))
        ratings = []
        for row in search:
            rating = 0
            for col in row:
                rating = rating + col
            ratings.append(rating)
        i = 0
        for row2 in update:
            row2[0] = ratings[i]
            update.updateRow(row2)
            i += 1

    # implements the buffer tool
    def make_buffer(self, buffer_info):
        buffered_data = arcpy.Buffer_analysis(buffer_info[INPUT], buffer_info[OUTPUT],
                                              buffer_info[DISTANCE],
                                              buffer_info[SIDE], buffer_info[END], buffer_info[METHOD],
                                              buffer_info[MERGE])
        return buffered_data

    # implements the clip tool
    def clip(self, clippee, clipper, clipped, tolerance):
        clipped_data = arcpy.Clip_analysis(clippee, clipper, clipped, tolerance)
        return clipped_data

    # intersect tool that takes the features to be intersected, the location of the output featue likely temp and the
    # attributes for the output feature that are preserved from the input features
    def make_intersect(self, in_features, out_feature, out_attr):
        return arcpy.Intersect_analysis(in_features, out_feature, out_attr)

    def union(self, in_features, out_feature, join_attr):
        return arcpy.Union_analysis(in_features, out_feature, join_attr)

    def dissolve(self, in_features, out_feature):
        return arcpy.Dissolve_management(in_features, out_feature)




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


# a function for printing a message in arcpro that has the time difference between to parts of code
def print_time_dif(message, start, end):
    arcpy.AddMessage(message + str(end - start) + " Seconds")


# for buffering
INPUT = 0
OUTPUT = 1
DISTANCE = 2
SIDE = 3
END = 4
METHOD = 5
MERGE = 6

# for clipping
CLIPPEE = 0
CLIPPER = 1
CLIPPED = 2
HIGH_TOLERANCE = "1 Kilometer"
LOWEST_TOLERANCE = "0"

# for naming intermediate files
fnum = IncrementingNumber(-1)
temp = "in_memory/temp"

# for layer rating
RATING = "rating"
STATIC_RATING = "static_rating"
BEGINS_RATING = "rating%"
FAULT_BUFFER = 10
SIDE_BUFFER = 5
ROAD_BUFFER = 100
DOC_LAND = 3


# function that tell which part of the program to execute and when.
def coordinateProgram():
    # gets all information from user
    start = time.time()
    info = Info()
    info.get_info()
    print_time_dif("Getting info took ", start, time.time())

    # make fault related buffers
    start = time.time()
    tool = Tool()
    prep_tools = PrepTools()
    info.buffered_fault = tool.make_buffer(info.fault_buffer)
    info.buffered_side = tool.make_buffer(info.side_buffer)
    print_time_dif("making basic buffers took ", start, time.time())
    # start = time.time()
    # zone = tool.make_buffer(info.analysis_zone)
    # print_time_dif("making zone buffer took ", start, time.time())

    # make road related buffers
    start = time.time()
    roads_in = tool.clip(info.road_buffer[INPUT], info.buffered_fault, temp + str(fnum.i()), LOWEST_TOLERANCE)
    print_time_dif("clipping roads took ", start, time.time())
    start = time.time()
    road_buffer_copy = copy.deepcopy(info.road_buffer)
    road_buffer_copy[INPUT] = roads_in
    info.buffered_road = tool.make_buffer(road_buffer_copy)
    print_time_dif("buffering roads took ", start, time.time())

    # clip doc land to fault buffer
    start = time.time()
    info.clipped_doc = tool.clip(info.doc_land[INPUT], info.buffered_fault, temp + str(fnum.i()), LOWEST_TOLERANCE)
    print_time_dif("clipping doc land took ", start, time.time())

    # dissolve doc land into a single feature
    start = time.time()
    info.clipped_dissolved_doc = tool.dissolve(info.clipped_doc, info.doc_land[OUTPUT], )
    print_time_dif("dissolving doc land took ", start, time.time())

    # add rating field to output layers
    add_rating = prep_tools.list_for_tool(info)
    tool.add_field(add_rating, RATING, "SHORT")
    for f_class in add_rating:
        if f_class is info.buffered_fault:
            tool.fill_field(f_class, RATING, FAULT_BUFFER)
        elif f_class is info.buffered_side:
            tool.fill_field(f_class, RATING, SIDE_BUFFER)
        elif f_class is info.buffered_road:
            tool.fill_field(f_class, RATING, ROAD_BUFFER)
        elif f_class is info.clipped_dissolved_doc:
            tool.fill_field(f_class, RATING, DOC_LAND)
        else:
            raise RuntimeError("one of the classes has not had its value field updated")

    # join all relevant layers with union
    start = time.time()
    union_input = prep_tools.list_for_tool(info)
    info.unioned_layers = tool.union(union_input, info.union_output, "")
    print_time_dif("union of all layers took ", start, time.time())

    # add total static rating to union layer
    u_layers = [info.unioned_layers]
    tool.add_field(u_layers, STATIC_RATING, "SHORT")
    ratings = prep_tools.get_rating_fields(info.unioned_layers)
    tool.fill_field_from_sum(info.unioned_layers, STATIC_RATING, ratings)



    # split land ownership
    # start = time.time()
    # clipped_ownership = tool.clip(info.ownership_info.ownership, info.buffered_fault, temp + str(fnum.i()), LOWEST_TOLERANCE)
    # print_time_dif("clipping ownership took ", start, time.time())
    # start = time.time()
    # info.ownership_info.ownership = clipped_ownership
    # info.ownership_info.split()
    # print_time_dif("splitting ownership took ", start, time.time())

    # intersect all layers
    # start = time.time()
    # input_features = prep_tools.list_for_intersect(info)
    # print_time_dif("prepping intersect data took ", start, time.time())
    # start = time.time()
    # tool.make_intersect(input_features, info.intersection_output, "ONLY_FID")
    # print_time_dif("intersecting layers took ", start, time.time())

    start = time.time()
    arcpy.Delete_management("in_memory")
    print_time_dif("clearing memory took ", start, time.time())


arcpy.AddMessage("COORDINATE PROGRAM CALLED")
coordinateProgram()

# except:
# arcpy.AddError("program failed")
# arcpy.AddMessage(arcpy.GetMessages())
# debugging
# arcpy.AddMessage("FAIL")
