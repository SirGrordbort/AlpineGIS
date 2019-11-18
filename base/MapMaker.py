# a program to build the layers required to determine where to put siesmometers on a fault based on:
from base.Information.Info import *
from base.BufferFault import BufferFault


def main():
    info = Info()
    info.getInfo()
    buffer = BufferFault()
    buffer.makeBuffer(info.bufferInfo)
    info.ownershipInfo.split()
    # TODO sideBuffer = buffer.makeBuffer(info.sideBufferInfo)

# except:
# arcpy.AddError("program failed")
# arcpy.AddMessage(arcpy.GetMessages())
# debugging
# arcpy.AddMessage("FAIL")
