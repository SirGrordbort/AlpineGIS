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

    # gets relevant info from the tool inputs in arcpro
    def get_info(self):
        param_num = IncrementingNumber(-1)
        self.fault_buffer = self.get_fault_buffer(param_num)
        self.side_buffer = self.get_side_buffer(param_num)
        self.road_buffer = self.get_road_buffer(param_num)
        self.ownership_info = OwnershipInfo(param_num)
        self.doc_land = self.get_doc_land(param_num)
        self.analysis_zone = self.get_zone_buffer(param_num)
        self.intersection_output = arcpy.GetParameterAsText(param_num.i())



        # TODO self.geology = arcpy.GetParameterAsText(2)
        # TODO self.idealSpacing = arcpy.GetParameterAsText(3)
    def get_doc_land(self, param_num):
        return [arcpy.GetParameterAsText(param_num.i())]



    def get_fault_buffer(self, param_num):
        buffer_params = self.get_params(param_num, 7)
        prep_tools = PrepTools()
        buffer_params[INPUT] = prep_tools.prep_alpine_fault(buffer_params[INPUT])
        return buffer_params

    def get_side_buffer(self, param_num):
        buffer_params = []
        self.add_empty_strings(buffer_params, 0, 7)
        buffer_params[INPUT] = arcpy.CopyFeatures_management(self.fault_buffer[INPUT], temp + str(fnum.i()))
        buffer_params[OUTPUT] = arcpy.GetParameterAsText(param_num.i())
        buffer_params[DISTANCE] = arcpy.GetParameterAsText(param_num.i())
        buffer_params[SIDE] = "RIGHT"
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

    def list_for_intersect(self, info):

        # precondition checks
        if info.buffered_fault is None:
            raise TypeError("buffered_fault has not been initialised")
        if info.buffered_side is None:
            raise TypeError("buffered_side has not been initialised")
        if info.buffered_road is None:
            raise TypeError("buffered_road has not been initialised")
        if info.ownership_info.is_not_split:
            raise TypeError("ownership has not been split")

        input_features = [info.buffered_fault, info.buffered_side, info.buffered_road, info.ownership_info.get_FST(),
                          info.ownership_info.get_DCDB()] # union relevant ownership layers first
        return input_features


# For running arcpy tools
class Tool:

    # constructor that gets the required buffer information
    def __init__(self):
        pass

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
    start = time.time()
    zone = tool.make_buffer(info.analysis_zone)
    print_time_dif("making zone buffer took ", start, time.time())

    # make road related buffers
    start = time.time()
    roads_in = tool.clip(info.road_buffer[INPUT], zone, temp + str(fnum.i()), LOWEST_TOLERANCE)
    print_time_dif("clipping roads took ", start, time.time())
    start = time.time()
    road_buffer_copy = copy.deepcopy(info.road_buffer)
    road_buffer_copy[INPUT] = roads_in
    info.buffered_road = tool.make_buffer(road_buffer_copy)
    print_time_dif("buffering roads took ", start, time.time())

    # split land ownership
    start = time.time()
    clipped_ownership = tool.clip(info.ownership_info.ownership, zone, temp + str(fnum.i()), LOWEST_TOLERANCE)
    print_time_dif("clipping ownership took ", start, time.time())
    start = time.time()
    info.ownership_info.ownership = clipped_ownership
    info.ownership_info.split()
    print_time_dif("splitting ownership took ", start, time.time())

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
