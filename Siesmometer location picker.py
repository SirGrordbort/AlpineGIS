import time
import arcpy
import copy


# a class for holding all the information that the program needs to store
class Info:
    def __init__(self):

        # a collection of soft rock names
        self.soft_rocks = ["breccia", "conglomerate", "gravel", "mud", "mudstone", "sand"]

        # a collection of hard rock names
        self.hard_rocks = ["andesite", "basalt", "dacite", "diorite", "gabbro", "gneiss", "granite", "hornfels",
                           "ignimbrite", "limestone", "marble", "peridotite", "quartzite", "rhyolite", "sandstone",
                           "schist", "serpentinite", "tuff"]

        # attributes used by the program that have also been altered by the program i.e. intermediate values
        self.buffered_fault = None
        self.buffered_side = None
        self.buffered_road = None
        self.clipped_doc = None
        self.clipped_dissolved_doc = None
        self.unioned_layers = None
        self.clipped_geo = None
        self.clipped_dissolved_geo = None

    # gets relevant tool inputs and outputs and stores them in a way that can be used by the program
    def get_info(self):
        param_num = IncrementingNumber(-1)

        # information needed to build the specified buffers and the ratings associated with them
        self.fault_buffer = self.get_fault_buffer(param_num)
        self.fault_buffer_rating = arcpy.GetParameterAsText(param_num.i())
        self.side_buffer = self.get_side_buffer(param_num)
        self.side_buffer_rating = arcpy.GetParameterAsText(param_num.i())
        self.road_buffer = self.get_road_buffer(param_num)
        self.road_buffer_rating = arcpy.GetParameterAsText(param_num.i())

        self.doc_land = self.get_in_out(param_num)
        self.doc_rating = arcpy.GetParameterAsText(param_num.i())
        self.geo_map = self.get_in_out(param_num)
        self.hard_rock_rating = arcpy.GetParameterAsText(param_num.i())
        self.soft_rock_rating = arcpy.GetParameterAsText(param_num.i())
        # main program output location
        self.union_output = arcpy.GetParameterAsText(param_num.i())

        # another output needed by the location picker tool
        self.clipped_roads_out = arcpy.GetParameterAsText(param_num.i())

    # gets a list containing an input parameter and an output parameter
    def get_in_out(self, param_num):
        return [arcpy.GetParameterAsText(param_num.i()), arcpy.GetParameterAsText(param_num.i())]

    # gets the required values for running the buffer tool on the fault. default values are saved as empty strings
    def get_fault_buffer(self, param_num):
        buffer_params = self.get_params(param_num, 3)
        self.add_empty_strings(buffer_params, 3, 7)
        buffer_params[METHOD] = ALL  # ensures the buffer is merged into one feature
        return buffer_params

    # same as get_fault_buffer except the input is copied from the fault buffer input and the buffer side is hard coded
    # to left (which is actually right looking north on the map)
    def get_side_buffer(self, param_num):
        buffer_params = []
        self.add_empty_strings(buffer_params, 0, 7)
        buffer_params[INPUT] = arcpy.CopyFeatures_management(self.fault_buffer[INPUT], temp + str(fnum.i()))
        buffer_params[OUTPUT] = arcpy.GetParameterAsText(param_num.i())
        buffer_params[DISTANCE] = arcpy.GetParameterAsText(param_num.i())
        buffer_params[SIDE] = LEFT
        buffer_params[METHOD] = ALL
        return buffer_params

    def get_road_buffer(self, param_num):
        buffer_params = self.get_params(param_num, 3)
        self.add_empty_strings(buffer_params, 3, 5)
        # merge type currently an input parameter but should be hard coded to all
        buffer_params.append(arcpy.GetParameterAsText(param_num.i()))
        self.add_empty_strings(buffer_params, 6, 7)

        return buffer_params

    # @param num_of_params is the quantity of parameters to get from the tool input
    # @return params is the list of parameters from the tool input
    def get_params(self, param_num, num_of_params):
        params = []
        for num in range(num_of_params):
            params.append(arcpy.GetParameterAsText(param_num.i()))
        return params

    # adds empty strings in the place of default parameters
    def add_empty_strings(self, list, start, end):
        for num in range(start, end):
            list.append("")


# for preparing data to be input into the tools
class PrepTools:

    # returns all fields starting with "rating" from the input feature class
    def get_rating_fields(self, fc):
        rating_fields = []
        for field in arcpy.ListFields(fc):
            fname = field.name
            if fname.startswith("rating"):
                rating_fields.append(fname)
        return rating_fields

    # returns a list of parameters to have the rating field added to them
    def list_for_add_field(self, info):

        # precondition checks
        if info.buffered_fault is None:
            raise TypeError("buffered_fault has not been initialised")
        if info.buffered_side is None:
            raise TypeError("buffered_side has not been initialised")
        if info.buffered_road is None:
            raise TypeError("buffered_road has not been initialised")
        if info.clipped_dissolved_doc is None:
            raise TypeError("doc land has not been dissolved")
        if info.clipped_geo is None:
            raise TypeError("geo map has not been clipped")

        input_features = [info.buffered_fault, info.buffered_side, info.buffered_road, info.clipped_dissolved_doc,
                          info.clipped_geo]
        return input_features

    # returns a list of input parameters for the union tool
    def list_for_union(self, info):
        # precondition checks
        if info.buffered_fault is None:
            raise TypeError("buffered_fault has not been initialised")
        if info.buffered_side is None:
            raise TypeError("buffered_side has not been initialised")
        if info.buffered_road is None:
            raise TypeError("buffered_road has not been initialised")
        if info.clipped_dissolved_doc is None:
            raise TypeError("doc land has not been dissolved")
        if info.clipped_dissolved_geo is None:
            raise TypeError("geo map has not been clipped or dissolved")

        input_features = [info.buffered_fault, info.buffered_side, info.buffered_road, info.clipped_dissolved_doc,
                          info.clipped_dissolved_geo]
        return input_features


# For running arcpy tools
class Tool:

    # constructor that gets the required buffer information
    def __init__(self):
        pass

    # adds a field to a list of feature classes
    def add_field(self, feature_class_list, field_name, field_type):
        for f_class in feature_class_list:
            arcpy.AddField_management(f_class, field_name, field_type)

    # fills each entry in an existing field from a given feature class with a specific value
    def fill_ratings(self, feature_class, field_name, value):
        cursor = arcpy.da.UpdateCursor(feature_class, (field_name,))
        for row in cursor:
            row[0] = value
            cursor.updateRow(row)

    # fills the rating field of the geo class with ratings based each rock group
    def fill_geo_ratings(self, geo_f_class, info):
        rock = 0
        rating = 1
        no_rock = 0
        u_cursor = arcpy.da.UpdateCursor(geo_f_class, ("rock_group", "rating"))
        for row in u_cursor:
            # apparently rows with no rock type exist, not sure why
            if row[rock] == " ":
                row[rating] = no_rock

            elif row[rock] in info.soft_rocks:
                row[rating] = info.soft_rock_rating
            elif row[rock] in info.hard_rocks:
                row[rating] = info.hard_rock_rating
            else:
                raise RuntimeError(
                    "input rock " + row[rock] + " was not in either hard or soft rock list" + str(type(row[rock])))
            u_cursor.updateRow(row)

    # @param feature_class is a feature class
    # @param to_update is the field in the given feature class whos values you want to fill with the sum of other fields
    # @ param field_names are the names of the fields who's values are to be summed
    # fills a field with the sum of values from other fields within the given feature
    def fill_field_from_sum(self, feature_class, to_update, field_names):
        # precondition check ensuring all the required fields exist within the feature class
        fnames = []
        for field in arcpy.ListFields(feature_class):
            fnames.append(field.name)
        for name in field_names:
            assert fnames.__contains__(name)
        assert fnames.__contains__(to_update)

        search = arcpy.da.SearchCursor(feature_class, field_names)
        update = arcpy.da.UpdateCursor(feature_class, (to_update,))
        ratings = []  # a list of the sum of the field name values for each row of fields in the feature class
        for row in search:
            rating = 0
            for col in row:
                rating = rating + col
            ratings.append(rating)
        i = 0
        # fills the to_update field with the sum of the other fields
        for row2 in update:
            row2[0] = ratings[i]
            update.updateRow(row2)
            i += 1

    # @param buffer_info is a list of input parameters for the buffer tool
    # implements the buffer tool
    # return buffered_data is a feature class containing the buffer made by the buffer tool
    def make_buffer(self, buffer_info):
        buffered_data = arcpy.Buffer_analysis(buffer_info[INPUT], buffer_info[OUTPUT],
                                              buffer_info[DISTANCE],
                                              buffer_info[SIDE], buffer_info[END], buffer_info[METHOD],
                                              buffer_info[MERGE])
        return buffered_data
    # @param clipee is the feature class to be clipped
    # @param clipper is the feature class clipee will be clipped by
    # @ param clipped is the output feature class
    # @param tolerance is how accurate you want the clipping to be
    # implements the clip tool
    def clip(self, clippee, clipper, clipped, tolerance):
        clipped_data = arcpy.Clip_analysis(clippee, clipper, clipped, tolerance)
        return clipped_data

    # @param in_features is a list of features to be unioned
    # @param join_attr determines which attributes will be joined from the input features. default is all
    def union(self, in_features, out_feature, join_attr):
        return arcpy.Union_analysis(in_features, out_feature, join_attr)

    # @param field are the fields to be dissolved, default is SHAPE
    def dissolve(self, in_features, out_feature, field=""):
        return arcpy.Dissolve_management(in_features, out_feature, field)


# a number that can be easily incremented (in place of the ++num java code)
class IncrementingNumber:
    def __init__(self, num):
        self.num = num

    # increments then returns  the number this class holds by 1
    def i(self):
        self.num += 1
        return self.num
    # returns the number held by this object
    def get(self):
        return self.num


# a function for printing a message that has the time difference between to parts of code
def print_time_dif(message, start, end):
    arcpy.AddMessage(message + str(end - start) + " Seconds")

# constants to make code more readable
# for buffering
INPUT = 0
OUTPUT = 1
DISTANCE = 2
SIDE = 3
END = 4
METHOD = 5
MERGE = 6
ALL = "ALL"
LEFT = "LEFT"

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
STATIC_RATING = "stat_rate"


# function that tell which part of the program to execute and when.
def coordinate_program():
    try:
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
        # temp + str(fnum.i()) specifies a location in ram e.g. in_memory/temp1
        roads_in = tool.clip(info.road_buffer[INPUT], info.buffered_fault, temp + str(fnum.i()), LOWEST_TOLERANCE)
        print_time_dif("clipping roads took ", start, time.time())
        start = time.time()
        # makes a copy f the clipped roads
        clipped_roads = arcpy.CopyFeatures_management(roads_in, temp + str(fnum.i()))
        # dissolves the copy
        dissolved_roads = arcpy.Dissolve_management(clipped_roads, temp + str(fnum.i()))
        # converts the copy to NZGD 2000 New Zealand Transverse Mercator coordinate system and adds it to the output
        arcpy.Project_management(dissolved_roads, info.clipped_roads_out,
                                 arcpy.Describe(info.fault_buffer[INPUT]).spatialReference)
        print_time_dif("making clipped road output took ", start, time.time())

        # make road related buffers
        start = time.time()
        road_buffer_copy = copy.deepcopy(info.road_buffer)   # defensive copy of the road input
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

        # clip geo map to area around the fault
        start = time.time()
        info.clipped_geo = tool.clip(info.geo_map[INPUT], info.buffered_fault, temp + str(fnum.i()), LOWEST_TOLERANCE)
        print_time_dif("clipping geo map took ", start, time.time())

        # add rating field to output layers
        start = time.time()
        add_rating = prep_tools.list_for_add_field(info)
        tool.add_field(add_rating, RATING, "SHORT")
        for f_class in add_rating:
            if f_class is info.buffered_fault:
                tool.fill_ratings(f_class, RATING, info.fault_buffer_rating)
            elif f_class is info.buffered_side:
                tool.fill_ratings(f_class, RATING, info.side_buffer_rating)
            elif f_class is info.buffered_road:
                tool.fill_ratings(f_class, RATING, info.road_buffer_rating)
            elif f_class is info.clipped_dissolved_doc:
                tool.fill_ratings(f_class, RATING, info.doc_rating)
            elif f_class is info.clipped_geo:
                # needs its own method because not every row has the same rating value
                tool.fill_geo_ratings(info.clipped_geo, info)
            else:
                raise RuntimeError("one of the classes has not had its value field updated")

        print_time_dif("adding rating fields took ", start, time.time())

        # dissolve lithostratigraphy based on hard and soft rock as well as the rock group
        start = time.time()
        info.clipped_dissolved_geo = tool.dissolve(info.clipped_geo, info.geo_map[OUTPUT], ["rock_group", "rating"])
        print_time_dif("dissolving lithostratigraphy took ", start, time.time())

        # join all relevant layers with union
        start = time.time()
        union_input = prep_tools.list_for_union(info)
        info.unioned_layers = tool.union(union_input, info.union_output, "")
        print_time_dif("union of all layers took ", start, time.time())

        # add total static rating to union layer
        u_layers = [info.union_output]
        tool.add_field(u_layers, STATIC_RATING, "LONG")
        ratings = prep_tools.get_rating_fields(info.union_output)
        tool.fill_field_from_sum(info.union_output, STATIC_RATING, ratings)

        # make the unioned layers fields useful by adding a yes or a no as to whether the polygon is on doc land and/or
        # the correct side of the fault
        arcpy.AddField_management(info.union_output, "fault_side", "TEXT")
        arcpy.AddField_management(info.union_output, "doc_land", "TEXT")
        polys = arcpy.da.UpdateCursor(info.union_output, ("FID_" + str(arcpy.Describe(info.buffered_side).Name),
                                                          "FID_" + str(arcpy.Describe(info.clipped_dissolved_doc).Name),
                                                          "fault_side", "doc_land"))

        for poly in polys:
            if poly[0] == -1:
                poly[2] = "NO"
            else:
                poly[2] = "YES"
            if poly[1] == -1:
                poly[3] = "NO"
            else:
                poly[3] = "YES"
            polys.updateRow(poly)
    finally:
        # ensures ram is returned to the system
        arcpy.Delete_management("in_memory")


arcpy.AddMessage("COORDINATE PROGRAM CALLED")
coordinate_program()
