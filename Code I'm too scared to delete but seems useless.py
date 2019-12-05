

# class OwnershipInfo:
#     def __init__(self, parameterNumber):
#         assert parameterNumber.get() >= 0, "parameterNumber is negative"
#         self.parcel_intent = {}
#         self.ownership = arcpy.GetParameterAsText(parameterNumber.i())
#         self.parcel_intent["'Fee Simple Title'"] = arcpy.GetParameterAsText(parameterNumber.i())
#         self.parcel_intent["'DCDB'"] = arcpy.GetParameterAsText(parameterNumber.i())
#         self.is_not_split = True
#
#     # method that uses the ownership metadata to split the ownership into layers based on the land parcel intent field
#     def split(self):
#         self.is_not_split = False
#         for parcel_str in self.parcel_intent.keys():
#             selected = arcpy.SelectLayerByAttribute_management(self.ownership, "NEW_SELECTION",
#                                                                "PARCEL_INT = " + parcel_str)
#             copy_destination = self.parcel_intent.get(parcel_str, -1)
#             # Error checking
#             if copy_destination == -1:
#                 raise ValueError("missing key for" + parcel_str)
#             arcpy.CopyFeatures_management(selected, copy_destination)
#
#     def get_DCDB(self):
#         return self.parcel_intent.get("'DCDB'")
#
#     def get_FST(self):
#         return self.parcel_intent.get("'Fee Simple Title'")

# self.ownership_info = OwnershipInfo(param_num)

# self.analysis_zone = self.get_zone_buffer(param_num)
# self.theoretical_points = arcpy.GetParameterAsText(param_num.i())

# prep_tools = PrepTools()
        # buffer_params[INPUT] = prep_tools.prep_alpine_fault(buffer_params[INPUT])

# start = time.time()
    # zone = tool.make_buffer(info.analysis_zone)
    # print_time_dif("making zone buffer took ", start, time.time())

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


# except:
# arcpy.AddError("program failed")
# arcpy.AddMessage(arcpy.GetMessages())
# debugging
# arcpy.AddMessage("FAIL")