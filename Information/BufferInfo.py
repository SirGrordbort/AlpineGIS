# holds information for creating a buffer around the fault
import arcpy


class BufferInfo:
    def __init__(self, parameterNumber):
        self.fault = arcpy.GetParameterAsText(parameterNumber.i())
        self.bufferedFault = arcpy.GetParameterAsText(parameterNumber.i())
        self.bufferDist = arcpy.GetParameterAsText(parameterNumber.i())
        self.sideType = arcpy.GetParameterAsText(parameterNumber.i())
        self.endType = arcpy.GetParameterAsText(parameterNumber.i())
        self.method = arcpy.GetParameterAsText(parameterNumber.i())
        self.merge = arcpy.GetParameterAsText(parameterNumber.i())