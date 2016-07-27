##Name:         MonthlyParcelUpdate.py
##Author:       Brian Kingery
##Created:      7/27/2016
##
##Purpose:      Automate the monthly Parcel update process
##
##Folder:       R:\Divisions\InfoTech\Shared\GIS\Parcels
##
##Order of Operations:
## 1 Start()
## 2 Manually add each municipality's parcel fc to GDB created in Start()
## 3 AddTempFields()
## 4 FieldCleanup()
## 5 MergeParcels()

import arcpy, datetime, os
from arcpy import env

env.workspace = r'R:\Divisions\InfoTech\Shared\GIS\Parcels'
env.overwriteoutput = True
TodaysDate = datetime.datetime.today().strftime('%Y%m%d') # today's date in yyyymmdd format

TempFields   = ['_Parcel_ID_','_Name_Owner_','_HouseNumber_','_Street_','_City_Loc_','_State_','_Zip_Code_',
                '_Square_Feet_','_Acres_US_','_Sub_Name_','_Legal_Desc_','_Info_Source_','_EditDate_','_EditBy_']

MasterFields = ['Parcel_ID', 'Name_Owner', 'HouseNumber', 'Street', 'City_Loc', 'State','Zip_Code',
                'Square_Feet', 'Acres_US', 'Sub_Name', 'Legal_Desc', 'Info_Source', 'EditDate', 'EditBy']

MasterParcels = env.workspace + os.sep + TodaysDate + os.sep + 'Parcels_' + TodaysDate + '.gdb' + os.sep + 'MasterParcels_' + TodaysDate
WB  = env.workspace + os.sep + TodaysDate + os.sep + 'Parcels_' + TodaysDate + '.gdb' + os.sep + 'WB'
YC  = env.workspace + os.sep + TodaysDate + os.sep + 'Parcels_' + TodaysDate + '.gdb' + os.sep + 'YC'
POQ = env.workspace + os.sep + TodaysDate + os.sep + 'Parcels_' + TodaysDate + '.gdb' + os.sep + 'POQ'
NN  = env.workspace + os.sep + TodaysDate + os.sep + 'Parcels_' + TodaysDate + '.gdb' + os.sep + 'NN'
JCC = env.workspace + os.sep + TodaysDate + os.sep + 'Parcels_' + TodaysDate + '.gdb' + os.sep + 'JCC'
HAM = env.workspace + os.sep + TodaysDate + os.sep + 'Parcels_' + TodaysDate + '.gdb' + os.sep + 'HAM'
NKC = env.workspace + os.sep + TodaysDate + os.sep + 'Parcels_' + TodaysDate + '.gdb' + os.sep + 'NKC'

############################################################################################

def Start():
    CreateFolder()
    CreateFileGeodatabase()
    CreateMasterParcelsFC()
    
def CreateFolder():
    global folder
    folder = env.workspace + os.sep + TodaysDate
    if arcpy.Exists(folder):
        arcpy.Delete_management(folder)    
    os.makedirs(folder)
    print 'Folder = ' + folder
        
def CreateFileGeodatabase():
    global gdb
    gdb = 'Parcels_' + TodaysDate + '.gdb'
    if arcpy.Exists(folder + os.sep + gdb):
        arcpy.Delete_management(folder + os.sep + gdb)
    arcpy.CreateFileGDB_management(folder, gdb)
    print 'GDB = ' + gdb

def CreateMasterParcelsFC():
    path = folder + os.sep + gdb
    name = 'MasterParcels_' + TodaysDate
    geometry_type = 'POLYGON'
    # http://resources.arcgis.com/en/help/arcgis-rest-api/index.html#/Projected_coordinate_systems/02r3000000vt000000/
    sr = arcpy.SpatialReference(2284)
    arcpy.CreateFeatureclass_management(path, name, geometry_type, '', '', '', sr)
    print 'Master FC = ' + env.workspace + os.sep + TodaysDate + os.sep + gdb + os.sep + name

############################################################################################

def AddTempFields():
    env.workspace = env.workspace + os.sep + TodaysDate + os.sep + 'Parcels_' + TodaysDate + '.gdb'

    fieldName1  = "_Parcel_ID_"
    fieldName2  = "_Name_Owner_"
    fieldName3  = "_HouseNumber_"
    fieldName4  = "_Street_"
    fieldName5  = "_City_Loc_"
    fieldName6  = "_State_"
    fieldName7  = "_Zip_Code_"
    fieldName8  = "_Square_Feet_"
    fieldName9  = "_Acres_US_"
    fieldName10 = "_Sub_Name_"
    fieldName11 = "_Legal_Desc_"
    fieldName12 = "_Info_Source_"
    fieldName13 = "_EditDate_"
    fieldName14 = "_EditBy_"
    
    fieldType1  = "TEXT"
    fieldType2  = "DOUBLE"

    for fc in arcpy.ListFeatureClasses():
        print 'Adding fields to ' + fc
        arcpy.AddField_management(fc, fieldName1,  fieldType1, "", "", 50)
        arcpy.AddField_management(fc, fieldName2,  fieldType1, "", "", 150)
        arcpy.AddField_management(fc, fieldName3,  fieldType1, "", "", 10)
        arcpy.AddField_management(fc, fieldName4,  fieldType1, "", "", 50)
        arcpy.AddField_management(fc, fieldName5,  fieldType1, "", "", 50)
        arcpy.AddField_management(fc, fieldName6,  fieldType1, "", "", 5)
        arcpy.AddField_management(fc, fieldName7,  fieldType1, "", "", 10)
        arcpy.AddField_management(fc, fieldName8,  fieldType2, "", "", 20)
        arcpy.AddField_management(fc, fieldName9,  fieldType2, "", "", 20)
        arcpy.AddField_management(fc, fieldName10, fieldType1, "", "", 50)
        arcpy.AddField_management(fc, fieldName11, fieldType1, "", "", 150)
        arcpy.AddField_management(fc, fieldName12, fieldType1, "", "", 50)
        arcpy.AddField_management(fc, fieldName13, fieldType1, "", "", 10)
        arcpy.AddField_management(fc, fieldName14, fieldType1, "", "", 50)

############################################################################################
  
def FieldCleanup():
    #Williamsburg()
    YorkCounty()
    Poquoson()
    NewportNews()
    JamesCityCounty()
    Hampton()
    NewKentCounty()

codeblock_Date = """def Date():
    import datetime
    return datetime.datetime.today().strftime('%Y%m%d')"""

def Williamsburg():
    print 'Williamsburg'

    OriginalFields = ['PID','LUCat']

    print '\tDeleting fields'
    for field in arcpy.ListFields(WB):
        if not field.required and field.name not in TempFields and field.name not in OriginalFields:
            arcpy.DeleteField_management(WB, field.name)

    print '\tField calculating'
    arcpy.CalculateField_management(WB, "_Parcel_ID_",      '!PID!',                                "PYTHON_9.3")
    arcpy.CalculateField_management(WB, "_City_Loc_",       '"Williamsburg"',                       "PYTHON_9.3")
    arcpy.CalculateField_management(WB, "_State_",          '"VA"',                                 "PYTHON_9.3")
    arcpy.CalculateField_management(WB, "_Square_Feet_",    'round(!shape.area@SQUAREFEET!, 2)',    "PYTHON_9.3")
    arcpy.CalculateField_management(WB, "_Acres_US_",       'round(!shape.area@ACRES!, 2)',         "PYTHON_9.3")
    arcpy.CalculateField_management(WB, "_Legal_Desc_",     '!LUCat!',                              "PYTHON_9.3")
    arcpy.CalculateField_management(WB, "_Info_Source_",    '"Williamsburg GIS Website"',           "PYTHON_9.3")
    arcpy.CalculateField_management(WB, "_EditDate_",       'Date()',                               "PYTHON_9.3", codeblock_Date)
    arcpy.CalculateField_management(WB, "_EditBy_",         '"bkingery"',                           "PYTHON_9.3")

    print '\tFinalizing fields'
    for field in arcpy.ListFields(WB):
        if not field.required and field.name not in TempFields:
            arcpy.DeleteField_management(WB, field.name)

def YorkCounty():
    print 'York County'

    OriginalFields = ['GPIN','OWNERSNAME','LOCADDR','STRTNAME','OWNRZIPC','SUBDIVISION','LEGLDESC']

    print '\tDeleting fields'
    for field in arcpy.ListFields(YC):
        if not field.required and field.name not in TempFields and field.name not in OriginalFields:
            arcpy.DeleteField_management(YC, field.name)

    print '\tField calculating'
    arcpy.CalculateField_management(YC, "_Parcel_ID_",      '!GPIN!',                               "PYTHON_9.3")
    arcpy.CalculateField_management(YC, "_Name_Owner_",     '!OWNERSNAME!',                         "PYTHON_9.3")
    arcpy.CalculateField_management(YC, "_HouseNumber_",    '!LOCADDR!.split(" ")[0]',              "PYTHON_9.3")
    arcpy.CalculateField_management(YC, "_Street_",         '!STRTNAME!',                           "PYTHON_9.3")
    arcpy.CalculateField_management(YC, "_City_Loc_",       '"York County"',                        "PYTHON_9.3")
    arcpy.CalculateField_management(YC, "_State_",          '"VA"',                                 "PYTHON_9.3")
    arcpy.CalculateField_management(YC, "_Zip_Code_",       '!OWNRZIPC!',                           "PYTHON_9.3")
    arcpy.CalculateField_management(YC, "_Square_Feet_",    'round(!shape.area@SQUAREFEET!, 2)',    "PYTHON_9.3")
    arcpy.CalculateField_management(YC, "_Acres_US_",       'round(!shape.area@ACRES!, 2)',         "PYTHON_9.3")
    arcpy.CalculateField_management(YC, "_Sub_Name_",       '!SUBDIVISION!',                        "PYTHON_9.3")
    arcpy.CalculateField_management(YC, "_Legal_Desc_",     '!LEGLDESC!',                           "PYTHON_9.3")
    arcpy.CalculateField_management(YC, "_Info_Source_",    '"York County GIS Manager"',            "PYTHON_9.3")
    arcpy.CalculateField_management(YC, "_EditDate_",       'Date()',                               "PYTHON_9.3", codeblock_Date)
    arcpy.CalculateField_management(YC, "_EditBy_",         '"bkingery"',                           "PYTHON_9.3")

    print '\tFinalizing fields'
    for field in arcpy.ListFields(YC):
        if not field.required and field.name not in TempFields:
            arcpy.DeleteField_management(YC, field.name)
            
def Poquoson():
    pass
def NewportNews():
    pass
def JamesCityCounty():
    pass
def Hampton():
    pass
def NewKentCounty():
    pass
        
############################################################################################

def MergeParcels():
    # http://resources.arcgis.com/en/help/main/10.2/index.html#/Merge/001700000055000000/
    env.workspace = 'R:\Divisions\InfoTech\Shared\GIS\Parcels'    
    arcpy.Merge_management([YC, POQ, NN, JCC, HAM, NKC], MasterParcels)
                           
############################################################################################




