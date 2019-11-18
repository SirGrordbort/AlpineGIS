# a program to build the layers required to determine where to put siesmometers on a fault based on:
# The fault location (feature class)
# The prefered side of the fault(Boolean)
# The Land ownership (feature class)
# The Geology of the area (feature class)
# The spacing requirements for the siesmometers (double?)
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


# try:

# gets and holds the iformation from the user that is necesary for the program to run
class Info:
    def __init__(self):
        pass

    def getInfo(self):
        parameterNumber = IncrementingNumber(-1)
        self.bufferInfo = BufferInfo(parameterNumber)
        # TODO self.sideBufferInfo = BufferInfo(parameterNumber)
        self.ownershipInfo = OwnershipInfo(parameterNumber)
        # TODO self.geology = arcpy.GetParameterAsText(2)
        # TODO self.idealSpacing = arcpy.GetParameterAsText(3)


# holds information for creating a buffer around the fault
class BufferInfo:
    def __init__(self, parameterNumber):
        self.fault = arcpy.GetParameterAsText(parameterNumber.i())
        self.bufferedFault = arcpy.GetParameterAsText(parameterNumber.i())
        self.bufferDist = arcpy.GetParameterAsText(parameterNumber.i())
        self.sideType = arcpy.GetParameterAsText(parameterNumber.i())
        self.endType = arcpy.GetParameterAsText(parameterNumber.i())
        self.method = arcpy.GetParameterAsText(parameterNumber.i())
        self.merge = arcpy.GetParameterAsText(parameterNumber.i())


# currently simply holds the land ownership data
class OwnershipInfo:
    def __init__(self, parameterNumber):
        # featureClass
        self.ownership = arcpy.GetParameterAsText(parameterNumber.i())
        self.FST = arcpy.GetParameterAsText(parameterNumber.i())

    def split(self):
        selectedFST = arcpy.SelectLayerByAttribute_management(self.ownership, "NEW_SELECTION",
                                                              "PARCEL_INT = 'Fee Simple Title'")
        self.FST = arcpy.CopyFeatures_management(selectedFST, self.FST)

        # with arcpy.da.SearchCursor(self.ownerShip, ("parcel_intent",)) as cursor:
    # for row in cursor:
    # if row[0] == "Fee Simple Title":


# For creating a buffer
class BufferFault:

    # constructor that gets the required buffer information
    def __init__(self):
        pass

    # implements the buffer tool
    def makeBuffer(self, bufferInfo):
        bufferedData = arcpy.Buffer_analysis(bufferInfo.fault, bufferInfo.bufferedFault, bufferInfo.bufferDist,
                                             bufferInfo.sideType, bufferInfo.endType, bufferInfo.method,
                                             bufferInfo.merge)
        return bufferedData


# a number that can be easily incremented (in place of the ++num java code)
class IncrementingNumber:
    def __init__(self, num):
        self.num = num

    # increments the number this class holds by 1
    def i(self):
        self.num += 1
        return self.num


# function that tell which part of the program to execute and when.
def coordinateProgram():
    info = Info()
    info.getInfo()
    buffer = BufferFault()
    buffer.makeBuffer(info.bufferInfo)
    info.ownershipInfo.split()
    # TODO sideBuffer = buffer.makeBuffer(info.sideBufferInfo)


arcpy.AddMessage("COORDINATE PROGRAM CALLED")
coordinateProgram()

# except:
# arcpy.AddError("program failed")
# arcpy.AddMessage(arcpy.GetMessages())
# debugging
# arcpy.AddMessage("FAIL")
