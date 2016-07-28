##Name:     MonthlyParcelUpdate.py
##Author:   Brian Kingery
##Created:  7/27/2016
##
##Purpose:  Automate the monthly Parcel update process
##
##Folder:   R:\Divisions\InfoTech\Shared\GIS\Parcels
##
## 1 Start()
## 2 Manually add each municipality's parcel fc to GDB created in Start()
##      - Write a script that will join table to NKC Parcels
## 3 AddTempFields()
## 4 FieldCalculations()
## 5 MergeParcels()
## 6 Need to find a zipcode file and do a spatial join
## 7 Need to find a city file to do a spatial join
## 8 Alter field names
## 9 Copy fc to master name


##Data Sources
##
##WB  = Website = https://www.williamsburgva.gov/Index.aspx?page=793
##      Parcels.zip = http://www.williamsburgva.gov/Modules/ShowDocument.aspx?documentid=3604
##YC  = ?
##POQ = ?
##NN  = http://gis.nngov.com/resources/NNParcels.zip
##JCC = ?
##HAM = ?   Expired Drop Box = https://hampton.box.com/s/glghtvifu33lqhn0grd0glluvi3a6zp0
##NKC = Website = https://www.dropbox.com/sh/ynce0em649y5aas/AACjCT4zCthTqNWAIL7qL7Aka?dl=0
##      CountyGIS.gdb = https://www.dropbox.com/sh/ynce0em649y5aas/AAAN5xE8tjXoeOco3jOQn-Fga/CountyGIS.gdb?dl=0%3Flst




import arcpy, datetime, os
from arcpy import env

env.workspace = r'R:\Divisions\InfoTech\Shared\GIS\Parcels'
env.overwriteoutput = True

TodaysDate = datetime.datetime.today().strftime('%Y%m%d') # today's date in yyyymmdd format

## Temporary fields are used so no duplicates cause errors when added to each feature class
TempFields   = ['_Parcel_ID_','_Name_Owner_','_HouseNumber_','_Street_','_City_Loc_','_State_','_Zip_Code_',
                '_Square_Feet_','_Acres_US_','_Sub_Name_','_Legal_Desc_','_Info_Source_','_EditDate_','_EditBy_']

FinalFields = ['Parcel_ID', 'Name_Owner', 'HouseNumber', 'Street', 'City_Loc', 'State','Zip_Code',
                'Square_Feet', 'Acres_US', 'Sub_Name', 'Legal_Desc', 'Info_Source', 'EditDate', 'EditBy']

MasterParcels = env.workspace + os.sep + TodaysDate + os.sep + 'Parcels_' + TodaysDate + '.gdb' + os.sep + 'MasterParcels_' + TodaysDate
WB  = env.workspace + os.sep + TodaysDate + os.sep + 'Parcels_' + TodaysDate + '.gdb' + os.sep + 'WB'
YC  = env.workspace + os.sep + TodaysDate + os.sep + 'Parcels_' + TodaysDate + '.gdb' + os.sep + 'YC'
POQ = env.workspace + os.sep + TodaysDate + os.sep + 'Parcels_' + TodaysDate + '.gdb' + os.sep + 'POQ'
NN  = env.workspace + os.sep + TodaysDate + os.sep + 'Parcels_' + TodaysDate + '.gdb' + os.sep + 'NN'
JCC = env.workspace + os.sep + TodaysDate + os.sep + 'Parcels_' + TodaysDate + '.gdb' + os.sep + 'JCC'
HAM = env.workspace + os.sep + TodaysDate + os.sep + 'Parcels_' + TodaysDate + '.gdb' + os.sep + 'HAM'
NKC = env.workspace + os.sep + TodaysDate + os.sep + 'Parcels_' + TodaysDate + '.gdb' + os.sep + 'NKC'

codeblock_Date = """def Date():
    import datetime
    return datetime.datetime.today().strftime('%Y%m%d')"""

codeblock_Street = """def Street(FIELD):
    x = FIELD.split(" ")
    x.remove(x[0])
    y = " ".join(x)
    return y"""

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
  
def FieldCalculations():
    try:
        Williamsburg()
    except:
        print 'Error Williamsburg()'
    try:
        YorkCounty()
    except:
        print 'Error YorkCounty()'
    try:
        Poquoson()
    except:
        print 'Error Poquoson()'
    try:
        NewportNews()
    except:
        print 'Error NewportNews()'
    try:
        JamesCityCounty()
    except:
        print 'Error JamesCityCounty()'
    try:
        Hampton()
    except:
        print 'Error Hampton()'
    try:
        NewKentCounty()
    except:
        print 'Error NewKentCounty()'

def Williamsburg():
    print 'Williamsburg'
    print '\tField calculating'
    arcpy.CalculateField_management(WB, "_Parcel_ID_", '!PID!', "PYTHON_9.3")
    arcpy.CalculateField_management(WB, "_State_", '"VA"', "PYTHON_9.3")
    arcpy.CalculateField_management(WB, "_Square_Feet_", 'round(!shape.area@SQUAREFEET!, 2)', "PYTHON_9.3")
    arcpy.CalculateField_management(WB, "_Acres_US_", 'round(!shape.area@ACRES!, 2)', "PYTHON_9.3")
    arcpy.CalculateField_management(WB, "_Legal_Desc_", '!LUCat!', "PYTHON_9.3")
    arcpy.CalculateField_management(WB, "_Info_Source_", '"Williamsburg GIS Website"', "PYTHON_9.3")
    arcpy.CalculateField_management(WB, "_EditDate_", 'Date()', "PYTHON_9.3", codeblock_Date)
    arcpy.CalculateField_management(WB, "_EditBy_", '"bkingery"', "PYTHON_9.3")
    print '\tDeleting unnecessary fields'
    for field in arcpy.ListFields(WB):
        if not field.required and field.name not in TempFields:
            arcpy.DeleteField_management(WB, field.name)
            print '\t\tDeleted ' + field.name

def YorkCounty():
    print 'York County'
    print '\tField calculating'
    arcpy.CalculateField_management(YC, "_Parcel_ID_", '!GPIN!', "PYTHON_9.3")
    arcpy.CalculateField_management(YC, "_Name_Owner_", '!OWNERSNAME!', "PYTHON_9.3")
    arcpy.CalculateField_management(YC, "_HouseNumber_", '!LOCADDR!.split(" ")[0]', "PYTHON_9.3")
    arcpy.CalculateField_management(YC, "_Street_", '!STRTNAME!', "PYTHON_9.3")
    arcpy.CalculateField_management(YC, "_State_", '"VA"', "PYTHON_9.3")
    arcpy.CalculateField_management(YC, "_Square_Feet_", 'round(!shape.area@SQUAREFEET!, 2)', "PYTHON_9.3")
    arcpy.CalculateField_management(YC, "_Acres_US_", 'round(!shape.area@ACRES!, 2)', "PYTHON_9.3")
    arcpy.CalculateField_management(YC, "_Sub_Name_", '!SUBDIVISION!', "PYTHON_9.3")
    arcpy.CalculateField_management(YC, "_Legal_Desc_", '[LEGLDESC]', "VB")
    arcpy.CalculateField_management(YC, "_Info_Source_", '"York County GIS Manager"', "PYTHON_9.3")
    arcpy.CalculateField_management(YC, "_EditDate_", 'Date()', "PYTHON_9.3", codeblock_Date)
    arcpy.CalculateField_management(YC, "_EditBy_", '"bkingery"', "PYTHON_9.3")
    print '\tDeleting unnecessary fields'
    for field in arcpy.ListFields(YC):
        if not field.required and field.name not in TempFields:
            arcpy.DeleteField_management(YC, field.name)
            print '\t\tDeleted ' + field.name
            
def Poquoson():
    print 'Poquoson'
    print '\tField calculating'
    arcpy.CalculateField_management(POQ, "_Parcel_ID_", '!MAP_PIN!', "PYTHON_9.3")
    arcpy.CalculateField_management(POQ, "_Name_Owner_", '!OWNRNAME!', "PYTHON_9.3")
    arcpy.CalculateField_management(POQ, "_HouseNumber_", '!STRTNUMB!', "PYTHON_9.3") # Long - so recalc below to add to text
    arcpy.CalculateField_management(POQ, "_HouseNumber_", '!_HouseNumber_! + !NUMBSUFX!', "PYTHON_9.3") # To add Apt number
    arcpy.CalculateField_management(POQ, "_Street_", '!STRTNAME!', "PYTHON_9.3")
    arcpy.CalculateField_management(POQ, "_State_", '"VA"', "PYTHON_9.3")
    arcpy.CalculateField_management(POQ, "_Square_Feet_", 'round(!shape.area@SQUAREFEET!, 2)', "PYTHON_9.3")
    arcpy.CalculateField_management(POQ, "_Acres_US_", 'round(!shape.area@ACRES!, 2)', "PYTHON_9.3")
    arcpy.CalculateField_management(POQ, "_Sub_Name_", '!PROPDESC!', "PYTHON_9.3")
    arcpy.CalculateField_management(POQ, "_Legal_Desc_", '!LEGLDESC!', "PYTHON_9.3")
    arcpy.CalculateField_management(POQ, "_Info_Source_", '"Poquoson Assessor Office"', "PYTHON_9.3")
    arcpy.CalculateField_management(POQ, "_EditDate_", 'Date()', "PYTHON_9.3", codeblock_Date)
    arcpy.CalculateField_management(POQ, "_EditBy_", '"bkingery"', "PYTHON_9.3")
    print '\tDeleting unnecessary fields'
    for field in arcpy.ListFields(POQ):
        if not field.required and field.name not in TempFields:
            arcpy.DeleteField_management(POQ, field.name)
            print '\t\tDeleted ' + field.name
            
def NewportNews():
    print 'Newport News'
    print '\tField calculating'
    arcpy.CalculateField_management(NN, "_Parcel_ID_", '!REISID!', "PYTHON_9.3")
    arcpy.CalculateField_management(NN, "_HouseNumber_", '!HouseNo!', "PYTHON_9.3") # Double - so recalc below to add to text
    arcpy.CalculateField_management(NN, "_HouseNumber_", '!_HouseNumber_! + !Apt!', "PYTHON_9.3") # To add Apt number
    arcpy.CalculateField_management(NN, "_Street_", '!Street!', "PYTHON_9.3")
    arcpy.CalculateField_management(NN, "_State_", '"VA"', "PYTHON_9.3")
    arcpy.CalculateField_management(NN, "_Square_Feet_", 'round(!shape.area@SQUAREFEET!, 2)', "PYTHON_9.3")
    arcpy.CalculateField_management(NN, "_Acres_US_", 'round(!shape.area@ACRES!, 2)', "PYTHON_9.3")
    arcpy.CalculateField_management(NN, "_Sub_Name_", '!SubdivName!', "PYTHON_9.3")
    arcpy.CalculateField_management(NN, "_Legal_Desc_", '!LeglDesc!', "PYTHON_9.3")
    arcpy.CalculateField_management(NN, "_Info_Source_", '"NN Dept of Engineering"', "PYTHON_9.3")
    arcpy.CalculateField_management(NN, "_EditDate_", 'Date()', "PYTHON_9.3", codeblock_Date)
    arcpy.CalculateField_management(NN, "_EditBy_", '"bkingery"', "PYTHON_9.3")
    print '\tDeleting unnecessary fields'
    for field in arcpy.ListFields(NN):
        if not field.required and field.name not in TempFields:
            arcpy.DeleteField_management(NN, field.name)
            print '\t\tDeleted ' + field.name

def JamesCityCounty():
    print 'James City County'
    print '\tField calculating'
    arcpy.CalculateField_management(JCC, "_Parcel_ID_", '!PIN!', "PYTHON_9.3")
    arcpy.CalculateField_management(JCC, "_HouseNumber_", '!LOCADDR!.split(" ")[0]', "PYTHON_9.3")
    arcpy.CalculateField_management(JCC, "_Street_", 'Street(!LOCADDR!)', "PYTHON_9.3", codeblock_Street)
    arcpy.CalculateField_management(JCC, "_State_", '"VA"', "PYTHON_9.3")
    arcpy.CalculateField_management(JCC, "_Square_Feet_", 'round(!shape.area@SQUAREFEET!, 2)', "PYTHON_9.3")
    arcpy.CalculateField_management(JCC, "_Acres_US_", 'round(!shape.area@ACRES!, 2)', "PYTHON_9.3")
    arcpy.CalculateField_management(JCC, "_Sub_Name_", '!PL_Subname!', "PYTHON_9.3")
    arcpy.CalculateField_management(JCC, "_Legal_Desc_", '!Legal1!', "PYTHON_9.3")
    arcpy.CalculateField_management(JCC, "_Info_Source_", '"James City County GIS Website"', "PYTHON_9.3")
    arcpy.CalculateField_management(JCC, "_EditDate_", 'Date()', "PYTHON_9.3", codeblock_Date)
    arcpy.CalculateField_management(JCC, "_EditBy_", '"bkingery"', "PYTHON_9.3")
    print '\tDeleting unnecessary fields'
    for field in arcpy.ListFields(JCC):
        if not field.required and field.name not in TempFields:
            arcpy.DeleteField_management(JCC, field.name)
            print '\t\tDeleted ' + field.name

def Hampton():
    print 'Hampton'
    print '\tField calculating'
    arcpy.CalculateField_management(HAM, "_Parcel_ID_", '!LRSNTXT!', "PYTHON_9.3")
    arcpy.CalculateField_management(HAM, "_HouseNumber_", '!SITUS!.split(" ")[0]', "PYTHON_9.3")
    arcpy.CalculateField_management(HAM, "_Street_", 'Street(!SITUS!)', "PYTHON_9.3", codeblock_Street)
    arcpy.CalculateField_management(HAM, "_State_", '"VA"', "PYTHON_9.3")
    arcpy.CalculateField_management(HAM, "_Square_Feet_", 'round(!shape.area@SQUAREFEET!, 2)', "PYTHON_9.3")
    arcpy.CalculateField_management(HAM, "_Acres_US_", 'round(!shape.area@ACRES!, 2)', "PYTHON_9.3")
    arcpy.CalculateField_management(HAM, "_Sub_Name_", '!Sub_Div!', "PYTHON_9.3")
    arcpy.CalculateField_management(HAM, "_Info_Source_", '"Hampton IT GIS"', "PYTHON_9.3")
    arcpy.CalculateField_management(HAM, "_EditDate_", 'Date()', "PYTHON_9.3", codeblock_Date)
    arcpy.CalculateField_management(HAM, "_EditBy_", '"bkingery"', "PYTHON_9.3")
    print '\tDeleting unnecessary fields'
    for field in arcpy.ListFields(HAM):
        if not field.required and field.name not in TempFields:
            arcpy.DeleteField_management(HAM, field.name)
            print '\t\tDeleted ' + field.name

def NewKentCounty():
    print 'New Kent County'
    print '\tField calculating'
    arcpy.CalculateField_management(NKC, "_Parcel_ID_", '!GPIN!', "PYTHON_9.3")
    arcpy.CalculateField_management(NKC, "_Name_Owner_", '!REM_OWN_NA!', "PYTHON_9.3")
    arcpy.CalculateField_management(NKC, "_HouseNumber_", '!REM_PRCL_L!.split(" ")[0]', "PYTHON_9.3")
    arcpy.CalculateField_management(NKC, "_Street_", 'Street(!REM_PRCL_L!)', "PYTHON_9.3", codeblock_Street)
    arcpy.CalculateField_management(NKC, "_State_", '"VA"', "PYTHON_9.3")
    arcpy.CalculateField_management(NKC, "_Square_Feet_", 'round(!shape.area@SQUAREFEET!, 2)', "PYTHON_9.3")
    arcpy.CalculateField_management(NKC, "_Acres_US_", 'round(!shape.area@ACRES!, 2)', "PYTHON_9.3")
    arcpy.CalculateField_management(NKC, "_Sub_Name_", '!SUBDIVISIO!', "PYTHON_9.3")
    arcpy.CalculateField_management(NKC, "_Legal_Desc_", '!VNS_STYLE_!', "PYTHON_9.3")
    arcpy.CalculateField_management(NKC, "_Info_Source_", '"New Kent County GIS"', "PYTHON_9.3")
    arcpy.CalculateField_management(NKC, "_EditDate_", 'Date()', "PYTHON_9.3", codeblock_Date)
    arcpy.CalculateField_management(NKC, "_EditBy_", '"bkingery"', "PYTHON_9.3")
    print '\tDeleting unnecessary fields'
    for field in arcpy.ListFields(NKC):
        if not field.required and field.name not in TempFields:
            arcpy.DeleteField_management(NKC, field.name)
            print '\t\tDeleted ' + field.name

############################################################################################

def MergeParcels():
    # http://resources.arcgis.com/en/help/main/10.2/index.html#/Merge/001700000055000000/
    arcpy.Merge_management([YC, POQ, NN, JCC, HAM, NKC], MasterParcels)
                           
############################################################################################

def Zipcodes():
    pass

############################################################################################

def City():
    pass
