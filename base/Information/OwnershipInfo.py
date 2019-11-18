# currently simply holds the land ownership data
import arcpy


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