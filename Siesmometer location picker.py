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
import arcpy
import copy


# try:

# gets and holds the iformation from the user that is necesary for the program to run
class Info:
    def __init__(self):
        pass

    def get_info(self):
        param_num = IncrementingNumber(-1)
        self.fault_buffer = self.get_fault_buffer(param_num)
        self.side_buffer = self.get_side_buffer(param_num)
        self.road_buffer = self.get_road_buffer(param_num)
        self.ownership = OwnershipInfo(param_num)
        # TODO ensure the appropriate parameters are added to the tool
        self.analysis_zone = self.get_zone_buffer(param_num)


        # TODO self.geology = arcpy.GetParameterAsText(2)
        # TODO self.idealSpacing = arcpy.GetParameterAsText(3)

    def get_fault_buffer(self, param_num):
        buffer_params = self.get_params(param_num, 7)
        return buffer_params

    def get_side_buffer(self, param_num):
        buffer_params = copy.deepcopy(self.fault_buffer)
        buffer_params[OUTPUT] = arcpy.GetParameterAsText(param_num.i())
        buffer_params[DISTANCE] = arcpy.GetParameterAsText(param_num.i())
        buffer_params[SIDE] = "LEFT"
        return buffer_params

    # TODO ensure the appropriate parameters are added to the tool
    def get_road_buffer(self, param_num):
        buffer_params = self.get_params(param_num, 3)
        self.add_empty_strings(buffer_params, 3, 7)
        return buffer_params

    def get_zone_buffer(self, param_num):
        buffer_params = [self.fault_buffer[INPUT]]
        buffer_params.append("Temp")
        buffer_params.append(arcpy.GetParameterAsText(param_num.i()))
        self.add_empty_strings(buffer_params, 3, 7)
        return buffer_params


    def get_params(self, param_num, num_of_params):
        params = []
        for num in range(num_of_params):
            params.append(arcpy.GetParameterAsText(param_num.i()))
        return params

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

    def split(self):
        for parcel_str in self.parcel_intent.keys():
            selected = arcpy.SelectLayerByAttribute_management(self.ownership, "NEW_SELECTION",
                                                               "PARCEL_INT = " + parcel_str)
            copy_destination = self.parcel_intent.get(parcel_str, -1)
            # Error checking
            if copy_destination == -1:
                raise ValueError("missing key for" + parcel_str)
            arcpy.CopyFeatures_management(selected, copy_destination)

        # with arcpy.da.SearchCursor(self.ownerShip, ("parcel_intent",)) as cursor:
        # for row in cursor:
        # if row[0] == "Fee Simple Title":


# For creating a buffer
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

    def clip(self, clippee, clipper, clipped):
        clipped_data = arcpy.Clip_analysis(clippee, clipper, clipped)
        return clipped_data


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

# function that tell which part of the program to execute and when.
def coordinateProgram():
    # gets all information from user
    info = Info()
    info.get_info()

    # processes information
    tool = Tool()
    tool.make_buffer(info.fault_buffer)
    tool.make_buffer(info.side_buffer)
    zone = tool.make_buffer(info.analysis_zone)
    tool.clip(info.road_buffer[INPUT], zone, info.analysis_zone[OUTPUT]) # todo find road data

    info.ownership.split()


arcpy.AddMessage("COORDINATE PROGRAM CALLED")
coordinateProgram()

# except:
# arcpy.AddError("program failed")
# arcpy.AddMessage(arcpy.GetMessages())
# debugging
# arcpy.AddMessage("FAIL")
