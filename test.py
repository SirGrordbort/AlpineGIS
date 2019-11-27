import arcpy
import time

class IncrementingNumber:
    def __init__(self, num):
        self.num = num

    # increments the number this class holds by 1
    def i(self):
        self.num += 1
        return self.num

    def get(self):
        return self.num

def print_time_dif(message, start, end):
    arcpy.AddMessage(message + str(end-start) + " Seconds")


class OwnershipInfo:
    def __init__(self, parameterNumber):
        self.parcel_intent = {}
        self.ownership = arcpy.GetParameterAsText(parameterNumber.i())
        self.parcel_intent["'Fee Simple Title'"] = arcpy.GetParameterAsText(parameterNumber.i())
        self.parcel_intent["'DCDB'"] = arcpy.GetParameterAsText(parameterNumber.i())

    def split(self):
        index = arcpy.AddIndex_management(self.ownership,"PARCEL_INT", "MyIndex")
        for parcel_str in self.parcel_intent.keys():
            selected = arcpy.SelectLayerByAttribute_management(index, "NEW_SELECTION",
                                                               "PARCEL_INT = " + parcel_str)
            copy_destination = self.parcel_intent.get(parcel_str, -1)
            # Error checking
            if copy_destination == -1:
                raise ValueError("missing key for" + parcel_str)
            arcpy.CopyFeatures_management(selected, copy_destination)


fnum = IncrementingNumber(-1)
start = time.time()
ownership = OwnershipInfo(fnum)
print_time_dif("initializing ownership took ", start, time.time())
start = time.time()
ownership.split()
print_time_dif("splitting ownership took ", start, time.time())
