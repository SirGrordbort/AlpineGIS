# For creating a buffer
import arcpy


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