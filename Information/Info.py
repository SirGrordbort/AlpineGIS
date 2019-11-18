from Information.BufferInfo import BufferInfo
from Information.IncrementableNum import IncrementingNumber
from Information.OwnershipInfo import OwnershipInfo
from base.MapMaker import *

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