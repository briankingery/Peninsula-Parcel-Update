"""
Name:     MonthlyParcelUpdate.py
Author:   Brian Kingery
Created:  8/18/2016
Purpose:  Automate the monthly Parcel update process
Folder:   R:\Divisions\InfoTech\Shared\GIS\Parcels

############################################################################################

Data Sources

Williamsburg
    Website = https://www.williamsburgva.gov/Index.aspx?page=793
    Parcels.zip = http://www.williamsburgva.gov/Modules/ShowDocument.aspx?documentid=3604
York County
    -- Confidential --
Poquoson
    WorldView Solutions maintains Poquoson parcel data and set up a profile to request data
    Updates quarterly
    Website = https://worldviewsolutions.atlassian.net/servicedesk/customer/portals
Newport News
    -- Confidential --
James City County
    Website = http://www.jamescitycountyva.gov/397/Mapping-Layers
    jcc_parcels.zip = ftp://property.jamescitycountyva.gov/GIS/layers/jcc_parcels.zip
Hampton
    -- Confidential --
New Kent County
    -- Confidential --
Zipcodes
    ftp://ftp2.census.gov/geo/tiger/TIGER2015/ZCTA5/
County Data
    ftp://ftp2.census.gov/geo/tiger/TIGER2015/COUNTY/
    
############################################################################################

Order of Operations

1 Start()
    - A folder of TodaysDate will be created at R:\Divisions\InfoTech\Shared\GIS\Parcels containing a file geodatabase
2 Manually import each zipfile to correct CityData folder
    - York County parcels from rest service directly to main geodatabase
    - Download CountyGIS.gdb.zip for NKC to the correct CityData folder
        - Right click zip file --> Extract All... to NKC folder
        - Run NKCParcels() --> Open Arcmap --> Add .lyr and export to GDB as NKC    
3 ProcessData()
4 FieldCalc()
    - AddTempFields()
        - If any error messages occur, investigate and run specific function for select municipality that errored
    - SendEmail()
5 Finish()
    - MergeParcels()
    - ZipCodeJoin()
    - CityJoin()
    - AlterFields()
    - SendEmail()

Final Product

Feature Class named RealPropertyParcel properly formatted ready to be copied to sde

"""

import arcpy, datetime, os, zipfile
from arcpy import env

env.workspace = r'R:\Divisions\InfoTech\Shared\GIS\Parcels'
env.overwriteoutput = True

TodaysDate = datetime.datetime.today().strftime('%Y%m%d') # today's date in yyyymmdd format

## Temporary fields are used so no duplicates cause errors when added to each feature class
TempFields   = ['_Parcel_ID_','_Name_Owner_','_HouseNumber_','_Street_','_City_Loc_','_State_','_Zip_Code_',
                '_Square_Feet_','_Acres_US_','_Sub_Name_','_Legal_Desc_','_Info_Source_','_EditDate_','_EditBy_']

FinalFields = ['Parcel_ID', 'Name_Owner', 'HouseNumber', 'Street', 'City_Loc', 'State','Zip_Code',
                'Square_Feet', 'Acres_US', 'Sub_Name', 'Legal_Desc', 'Info_Source', 'EditDate', 'EditBy']

WB  = env.workspace + os.sep + 'UpdateFolder' + os.sep + TodaysDate + os.sep + 'Parcels_' + TodaysDate + '.gdb' + os.sep + 'WB'
YC  = env.workspace + os.sep + 'UpdateFolder' + os.sep + TodaysDate + os.sep + 'Parcels_' + TodaysDate + '.gdb' + os.sep + 'YC'
POQ = env.workspace + os.sep + 'UpdateFolder' + os.sep + TodaysDate + os.sep + 'Parcels_' + TodaysDate + '.gdb' + os.sep + 'POQ'
NN  = env.workspace + os.sep + 'UpdateFolder' + os.sep + TodaysDate + os.sep + 'Parcels_' + TodaysDate + '.gdb' + os.sep + 'NN'
JCC = env.workspace + os.sep + 'UpdateFolder' + os.sep + TodaysDate + os.sep + 'Parcels_' + TodaysDate + '.gdb' + os.sep + 'JCC'
HAM = env.workspace + os.sep + 'UpdateFolder' + os.sep + TodaysDate + os.sep + 'Parcels_' + TodaysDate + '.gdb' + os.sep + 'HAM'
NKC = env.workspace + os.sep + 'UpdateFolder' + os.sep + TodaysDate + os.sep + 'Parcels_' + TodaysDate + '.gdb' + os.sep + 'NKC'

MasterParcels       = env.workspace + os.sep + 'UpdateFolder' + os.sep + TodaysDate + os.sep + 'Parcels_' + TodaysDate + '.gdb' + os.sep + 'Master_Parcels_' + TodaysDate
MasterZipCodeJoinFC = env.workspace + os.sep + 'UpdateFolder' + os.sep + TodaysDate + os.sep + 'Parcels_' + TodaysDate + '.gdb' + os.sep + 'Master_Join_1_ZipCode'
MasterCityJoinFC    = env.workspace + os.sep + 'UpdateFolder' + os.sep + TodaysDate + os.sep + 'Parcels_' + TodaysDate + '.gdb' + os.sep + 'Master_Join_2_City'
FinalFCname = 'RealPropertyParcel'
CleanedParcels      = env.workspace + os.sep + 'UpdateFolder' + os.sep + TodaysDate + os.sep + 'Parcels_' + TodaysDate + '.gdb' + os.sep + FinalFCname

ZipCodeFC   = env.workspace + os.sep + 'Data' + os.sep + 'Data.gdb' + os.sep + 'ZipCode'
CityFC      = env.workspace + os.sep + 'Data' + os.sep + 'Data.gdb' + os.sep + 'City'

codeblock_Date = """def Date():
    import datetime
    return datetime.datetime.today().strftime('%Y%m%d')"""

codeblock_Street = """def Street(FIELD):
    x = FIELD.split(" ")
    x.remove(x[0])
    y = " ".join(x)
    return y"""

## Do not want to include HouseNo that start with 0. If this was not an issue, could do the following...
##def FixStreet(HouseNo, Street):
##    try:
##        if isinstance(HouseNo[0],int):
##            return Street
##        else:
##            return HouseNo + " " + Street
##    except:
##        return Street

codeblock_FixStreet = """def FixStreet(HouseNo, Street):
    integerList = ['1','2','3','4','5','6','7','8','9']
    try:
        if HouseNo[0] in integerList:
            return Street
        else:
            return HouseNo + " " + Street
    except:
        return Street """

codeblock_FixHouseNo = """def FixHouseNo(HouseNo):
    integerList = ['1','2','3','4','5','6','7','8','9']
    try:
        if HouseNo[0] in integerList:
            return HouseNo
        else:
            return "--"
    except:
        return "--" """

############################################################################################

def Start():
    CreateFolder()
    CreateFileGeodatabase()

def CreateFolder():
    global folder
    folder = env.workspace + os.sep + 'UpdateFolder' + os.sep + TodaysDate
    if arcpy.Exists(folder):
        arcpy.Delete_management(folder)
    os.makedirs(folder)
    CityData  = folder + os.sep + 'CityData'
    WBfolder  = CityData + os.sep + 'Williamsburg'
    POQfolder = CityData + os.sep + 'Poquoson'
    NNfolder  = CityData + os.sep + 'NewportNews'
    JCCfolder = CityData + os.sep + 'JamesCityCounty'
    HAMfolder = CityData + os.sep + 'Hampton'
    NKCfolder = CityData + os.sep + 'NewKentCounty'
    os.makedirs(CityData)
    os.makedirs(WBfolder)
    os.makedirs(POQfolder)
    os.makedirs(NNfolder)
    os.makedirs(JCCfolder)
    os.makedirs(HAMfolder)
    os.makedirs(NKCfolder)
    print 'Project Folder = ' + folder
        
def CreateFileGeodatabase():
    global gdb
    gdb = 'Parcels_' + TodaysDate + '.gdb'
    if arcpy.Exists(folder + os.sep + gdb):
        arcpy.Delete_management(folder + os.sep + gdb)
    arcpy.CreateFileGDB_management(folder, gdb)
    print 'GDB = ' + gdb

############################################################################################
    
def ProcessData():
    WBParcels()
    ## York County parcels from rest service directly to main geodatabase
    POQParcels()
    NNParcels()
    JCCParcels()
    HAMParcels()
    NKCParcels()

def WBParcels():
    try:
        WBfolder = env.workspace + os.sep + 'UpdateFolder' + os.sep + TodaysDate + os.sep + 'CityData' + os.sep + 'Williamsburg'
        WBZip = WBfolder + os.sep + 'Parcels.zip'
        with zipfile.ZipFile(WBZip, "r") as z:
            z.extractall(WBfolder)
        SHP = WBfolder + os.sep + 'Parcels.shp'
        arcpy.CopyFeatures_management(SHP, WB)
        print 'WB parcels copied to main database'
    except:
        print 'Make sure Parcels.zip is saved to WB folder.'

def POQParcels():
    try:
        POQfolder = env.workspace + os.sep + 'UpdateFolder' + os.sep + TodaysDate + os.sep + 'CityData' + os.sep + 'Poquoson'
        POQZip = POQfolder + os.sep + 'Waterworks.zip'
        with zipfile.ZipFile(POQZip, "r") as z:
            z.extractall(POQfolder)
        FC = POQfolder + '\Waterworks\Waterworks.gdb\Tax_Parcels'
        arcpy.CopyFeatures_management(FC, POQ)
        print 'POQ parcels copied to main database'
    except:
        print 'Make sure Waterworks.zip is saved to POQ folder.'

def NNParcels():
    try:
        NNfolder = env.workspace + os.sep + 'UpdateFolder' + os.sep + TodaysDate + os.sep + 'CityData' + os.sep + 'NewportNews'
        NNZip = NNfolder + os.sep + 'NNParcels.zip'
        with zipfile.ZipFile(NNZip, "r") as z:
            z.extractall(NNfolder)
        SHP = NNfolder + os.sep + 'NNParcels.shp'
        arcpy.CopyFeatures_management(SHP, NN)
        print 'NN parcels copied to main database'
    except:
        print 'Make sure NNParcels.zip is saved to NN folder.'    

def JCCParcels():
    try:
        JCCfolder = env.workspace + os.sep + 'UpdateFolder' + os.sep + TodaysDate + os.sep + 'CityData' + os.sep + 'JamesCityCounty'
        JCCZip = JCCfolder + os.sep + 'jcc_parcels.zip'
        with zipfile.ZipFile(JCCZip, "r") as z:
            z.extractall(JCCfolder)
        SHP = JCCfolder + os.sep + 'parcel_public.shp'
        arcpy.CopyFeatures_management(SHP, JCC)
        print 'JCC parcels copied to main database'
    except:
        print 'Make sure jcc_parcels.zip is saved to JCC folder.' 

def HAMParcels():
    try:
        HAMfolder = env.workspace + os.sep + 'UpdateFolder' + os.sep + TodaysDate + os.sep + 'CityData' + os.sep + 'Hampton'
        HAMZip = HAMfolder + os.sep + 'Parcel.zip'
        with zipfile.ZipFile(HAMZip, "r") as z:
            z.extractall(HAMfolder)
        SHP = HAMfolder + os.sep + 'Parcel' + os.sep + 'PropertyPolygons.shp'
        arcpy.CopyFeatures_management(SHP, HAM)
        print 'HAM parcels copied to main database'
    except:
        print 'Make sure Parcel.zip is saved to HAM folder.'
        
def NKCParcels():
    try:
        NKCfolder = env.workspace + os.sep + 'UpdateFolder' + os.sep + TodaysDate + os.sep + 'CityData' + os.sep + 'NewKentCounty'
        CountyGISParcels = NKCfolder + os.sep + 'CountyGIS.gdb\Cadastral\Parcels'
        ParcelLayer = arcpy.MakeFeatureLayer_management(CountyGISParcels, 'NKCParcels')
        LayerFile = NKCfolder + os.sep + 'NKCParcels.lyr'
        arcpy.SaveToLayerFile_management(ParcelLayer, LayerFile)
        Table = NKCfolder + os.sep + 'CountyGIS.gdb\VISION_CURRENT'
        arcpy.AddJoin_management(LayerFile, "AV_PID", Table, "REM_PID", "KEEP_ALL")        
        print 'NKCParcels.lyr created and joined with VISION_CURRENT'
        print 'Open Arcmap --> Add NKCParcels.lyr --> Export data to GDB as NKC'       
    except:
        print 'Make sure CountyGIS.gdb is saved to NKC folder.'

############################################################################################

def FieldCalc():
    
    AddTempFields()
    
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

    SendEmail()

def AddTempFields():
    env.workspace = env.workspace + os.sep + 'UpdateFolder' + os.sep + TodaysDate + os.sep + 'Parcels_' + TodaysDate + '.gdb'

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
        arcpy.AddField_management(fc, fieldName3,  fieldType1, "", "", 50)
        arcpy.AddField_management(fc, fieldName4,  fieldType1, "", "", 50)
        arcpy.AddField_management(fc, fieldName5,  fieldType1, "", "", 50)
        arcpy.AddField_management(fc, fieldName6,  fieldType1, "", "", 20)
        arcpy.AddField_management(fc, fieldName7,  fieldType1, "", "", 10)
        arcpy.AddField_management(fc, fieldName8,  fieldType2, "", "", 20)
        arcpy.AddField_management(fc, fieldName9,  fieldType2, "", "", 20)
        arcpy.AddField_management(fc, fieldName10, fieldType1, "", "", 150)
        arcpy.AddField_management(fc, fieldName11, fieldType1, "", "", 150)
        arcpy.AddField_management(fc, fieldName12, fieldType1, "", "", 50)
        arcpy.AddField_management(fc, fieldName13, fieldType1, "", "", 10)
        arcpy.AddField_management(fc, fieldName14, fieldType1, "", "", 50)

def Williamsburg():
    print 'Williamsburg'
    print '\tField calculating'
    arcpy.CalculateField_management(WB, "_Parcel_ID_", '!PID!', "PYTHON_9.3")
    arcpy.CalculateField_management(WB, "_Legal_Desc_", '!LUCat!', "PYTHON_9.3")
    arcpy.CalculateField_management(WB, "_Info_Source_", '"Williamsburg GIS Website"', "PYTHON_9.3")
    print '\tDeleting unnecessary fields'
    for field in arcpy.ListFields(WB):
        if not field.required and field.name not in TempFields:
            arcpy.DeleteField_management(WB, field.name)

def YorkCounty():
    print 'York County'
    print '\tField calculating'
    arcpy.CalculateField_management(YC, "_Parcel_ID_", '!GPIN!', "PYTHON_9.3")
    arcpy.CalculateField_management(YC, "_Name_Owner_", '!OWNERSNAME!', "PYTHON_9.3")
    arcpy.CalculateField_management(YC, "_HouseNumber_", '!LOCADDR!.split(" ")[0]', "PYTHON_9.3")
    arcpy.CalculateField_management(YC, "_Street_", 'Street(!LOCADDR!)', "PYTHON_9.3", codeblock_Street)#"_Street_", '!STRTNAME!', "PYTHON_9.3")
    arcpy.CalculateField_management(YC, "_Sub_Name_", '!SUBDIVISION!', "PYTHON_9.3")
    arcpy.CalculateField_management(YC, "_Legal_Desc_", '!TABLDIST_DESC!', "PYTHON_9.3")#'[LEGLDESC]', "VB")
    arcpy.CalculateField_management(YC, "_Info_Source_", '"York County GIS Manager"', "PYTHON_9.3")
    print '\tDeleting unnecessary fields'
    for field in arcpy.ListFields(YC):
        if not field.required and field.name not in TempFields:
            arcpy.DeleteField_management(YC, field.name)
            
def Poquoson():
    print 'Poquoson'
    print '\tField calculating'
    arcpy.CalculateField_management(POQ, "_Parcel_ID_", '!MAP_PIN!', "PYTHON_9.3")
    arcpy.CalculateField_management(POQ, "_Name_Owner_", '!OWNRNAME!', "PYTHON_9.3")
    arcpy.CalculateField_management(POQ, "_HouseNumber_", '!STRTNUMB!', "PYTHON_9.3") # Long - so recalc below to add to text
    arcpy.CalculateField_management(POQ, "_HouseNumber_", '!_HouseNumber_! + !NUMBSUFX!', "PYTHON_9.3") # To add Apt number
    arcpy.CalculateField_management(POQ, "_Street_", '!STRTNAME!', "PYTHON_9.3")
    arcpy.CalculateField_management(POQ, "_Sub_Name_", '!PROPDESC!', "PYTHON_9.3")
    arcpy.CalculateField_management(POQ, "_Legal_Desc_", '[LEGLDESC]', "VB")#'!LEGLDESC!', "PYTHON_9.3")
    arcpy.CalculateField_management(POQ, "_Info_Source_", '"Poquoson Assessor Office"', "PYTHON_9.3")
    print '\tDeleting unnecessary fields'
    for field in arcpy.ListFields(POQ):
        if not field.required and field.name not in TempFields:
            arcpy.DeleteField_management(POQ, field.name)
            
def NewportNews():
    print 'Newport News'
    print '\tField calculating'
    arcpy.CalculateField_management(NN, "_Parcel_ID_", '!REISID!', "PYTHON_9.3")
    arcpy.CalculateField_management(NN, "_HouseNumber_", '!HouseNo!', "PYTHON_9.3") # Double - so recalc below to add to text
    arcpy.CalculateField_management(NN, "_HouseNumber_", '!_HouseNumber_! + !Apt!', "PYTHON_9.3") # To add Apt number
    arcpy.CalculateField_management(NN, "_Street_", '!Street!', "PYTHON_9.3")
    arcpy.CalculateField_management(NN, "_Sub_Name_", '!SubdivName!', "PYTHON_9.3")
    arcpy.CalculateField_management(NN, "_Legal_Desc_", '!LeglDesc!', "PYTHON_9.3")
    arcpy.CalculateField_management(NN, "_Info_Source_", '"NN Dept of Engineering"', "PYTHON_9.3")
    print '\tDeleting unnecessary fields'
    for field in arcpy.ListFields(NN):
        if not field.required and field.name not in TempFields:
            arcpy.DeleteField_management(NN, field.name)

def JamesCityCounty():
    print 'James City County'
    print '\tField calculating'
    arcpy.CalculateField_management(JCC, "_Parcel_ID_", '!PIN!', "PYTHON_9.3")
    arcpy.CalculateField_management(JCC, "_HouseNumber_", '!LOCADDR!.split(" ")[0]', "PYTHON_9.3")
    arcpy.CalculateField_management(JCC, "_Street_", 'Street(!LOCADDR!)', "PYTHON_9.3", codeblock_Street)
    arcpy.CalculateField_management(JCC, "_Legal_Desc_", '!Legal1!', "PYTHON_9.3")
    arcpy.CalculateField_management(JCC, "_Info_Source_", '"James City County GIS Website"', "PYTHON_9.3")
    print '\tDeleting unnecessary fields'
    for field in arcpy.ListFields(JCC):
        if not field.required and field.name not in TempFields:
            arcpy.DeleteField_management(JCC, field.name)

def Hampton():
    print 'Hampton'
    print '\tField calculating'
    arcpy.CalculateField_management(HAM, "_Parcel_ID_", '!LRSNTXT!', "PYTHON_9.3")
    arcpy.CalculateField_management(HAM, "_HouseNumber_", '!SITUS!.split(" ")[0]', "PYTHON_9.3")
    arcpy.CalculateField_management(HAM, "_Street_", 'Street(!SITUS!)', "PYTHON_9.3", codeblock_Street) # or !FRONT_ST!
    arcpy.CalculateField_management(HAM, "_Sub_Name_", '[Sub_Div]', "VB")
    arcpy.CalculateField_management(HAM, "_Info_Source_", '"Hampton IT GIS"', "PYTHON_9.3")
    print '\tDeleting unnecessary fields'
    for field in arcpy.ListFields(HAM):
        if not field.required and field.name not in TempFields:
            arcpy.DeleteField_management(HAM, field.name)

def NewKentCounty():
    print 'New Kent County'
    print '\tField calculating'
    arcpy.CalculateField_management(NKC, "_Parcel_ID_", '!GPIN!', "PYTHON_9.3")
    arcpy.CalculateField_management(NKC, "_Name_Owner_", '!REM_OWN_NAME!', "PYTHON_9.3")
    arcpy.CalculateField_management(NKC, "_HouseNumber_", '!REM_PRCL_LOCN!.split(" ")[0]', "PYTHON_9.3")
    arcpy.CalculateField_management(NKC, "_Street_", 'Street(!REM_PRCL_LOCN!)', "PYTHON_9.3", codeblock_Street)
    arcpy.CalculateField_management(NKC, "_Sub_Name_", '!SUBDIVISION!', "PYTHON_9.3")
    arcpy.CalculateField_management(NKC, "_Legal_Desc_", '!VNS_STYLE_DESC!', "PYTHON_9.3")
    arcpy.CalculateField_management(NKC, "_Info_Source_", '"New Kent County GIS"', "PYTHON_9.3")
    print '\tDeleting unnecessary fields'
    for field in arcpy.ListFields(NKC):
        if not field.required and field.name not in TempFields:
            arcpy.DeleteField_management(NKC, field.name)

############################################################################################

def Finish():
    MergeParcels()
    ZipCodeJoin()
    CityJoin()
    AlterFields()
    SendEmail()
    
def MergeParcels():
    print 'Merging all parcels to Master'
    # http://resources.arcgis.com/en/help/main/10.2/index.html#/Merge/001700000055000000/
    arcpy.Merge_management([WB, YC, POQ, NN, JCC, HAM, NKC], MasterParcels)
                              
def ZipCodeJoin():
    print 'Joining to ZipCode FC'
    arcpy.SpatialJoin_analysis(MasterParcels, ZipCodeFC, MasterZipCodeJoinFC, "JOIN_ONE_TO_ONE", "KEEP_ALL", "", "HAVE_THEIR_CENTER_IN")#"COMPLETELY_WITHIN")
    print '\tField calculating'
    arcpy.CalculateField_management(MasterZipCodeJoinFC, "_Zip_Code_", '!ZCTA5CE10!', "PYTHON_9.3")
    print '\tDeleting unnecessary fields'
    for field in arcpy.ListFields(MasterZipCodeJoinFC):
        if not field.required and field.name not in TempFields:
            arcpy.DeleteField_management(MasterZipCodeJoinFC, field.name)
            
def CityJoin():
    print 'Joining to City FC'
    arcpy.SpatialJoin_analysis(MasterZipCodeJoinFC, CityFC, MasterCityJoinFC, "JOIN_ONE_TO_ONE", "KEEP_ALL", "", "HAVE_THEIR_CENTER_IN")#"COMPLETELY_WITHIN")
    print '\tField calculating'
    arcpy.CalculateField_management(MasterCityJoinFC, "_City_Loc_", '!NAMELSAD!', "PYTHON_9.3")
    print '\tDeleting unnecessary fields'
    for field in arcpy.ListFields(MasterCityJoinFC):
        if not field.required and field.name not in TempFields:
            arcpy.DeleteField_management(MasterCityJoinFC, field.name)
    out_path = env.workspace + os.sep + 'UpdateFolder' + os.sep + TodaysDate + os.sep + 'Parcels_' + TodaysDate + '.gdb'
    out_name = FinalFCname
    arcpy.FeatureClassToFeatureClass_conversion(MasterCityJoinFC, out_path, out_name)

def AlterFields():
    print FinalFCname
    # Run this to match field names to current schema and delete temporary fields
    fieldName1  = "Parcel_ID"
    fieldName2  = "Name_Owner"
    fieldName3  = "HouseNumber"
    fieldName4  = "Street"
    fieldName5  = "City_Loc"
    fieldName6  = "State"
    fieldName7  = "Zip_Code"
    fieldName8  = "Square_Feet"
    fieldName9  = "Acres_US"
    fieldName10 = "Sub_Name"
    fieldName11 = "Legal_Desc"
    fieldName12 = "Info_Source"
    fieldName13 = "EditDate"
    fieldName14 = "EditBy"
    
    fieldType1  = "TEXT"
    fieldType2  = "DOUBLE"

    print '\tAdding fields to ' + FinalFCname
    arcpy.AddField_management(CleanedParcels, fieldName1,  fieldType1, "", "", 50)
    arcpy.AddField_management(CleanedParcels, fieldName2,  fieldType1, "", "", 150)
    arcpy.AddField_management(CleanedParcels, fieldName3,  fieldType1, "", "", 50)
    arcpy.AddField_management(CleanedParcels, fieldName4,  fieldType1, "", "", 50)
    arcpy.AddField_management(CleanedParcels, fieldName5,  fieldType1, "", "", 50)
    arcpy.AddField_management(CleanedParcels, fieldName6,  fieldType1, "", "", 20)
    arcpy.AddField_management(CleanedParcels, fieldName7,  fieldType1, "", "", 10)
    arcpy.AddField_management(CleanedParcels, fieldName8,  fieldType2, "", "", 20)
    arcpy.AddField_management(CleanedParcels, fieldName9,  fieldType2, "", "", 20)
    arcpy.AddField_management(CleanedParcels, fieldName10, fieldType1, "", "", 150)
    arcpy.AddField_management(CleanedParcels, fieldName11, fieldType1, "", "", 150)
    arcpy.AddField_management(CleanedParcels, fieldName12, fieldType1, "", "", 50)
    arcpy.AddField_management(CleanedParcels, fieldName13, fieldType1, "", "", 10)
    arcpy.AddField_management(CleanedParcels, fieldName14, fieldType1, "", "", 50)

    print '\tField calculating'
    arcpy.CalculateField_management(CleanedParcels, "Parcel_ID",     '!_Parcel_ID_!',   "PYTHON_9.3")
    arcpy.CalculateField_management(CleanedParcels, "Name_Owner",    '!_Name_Owner_!',  "PYTHON_9.3")
    # Fix Streets first and then clean the House Numbers
    arcpy.CalculateField_management(CleanedParcels, "Street",        'FixStreet(!_HouseNumber_!,!_Street_!)',   "PYTHON_9.3", codeblock_FixStreet)
    arcpy.CalculateField_management(CleanedParcels, "HouseNumber",   'FixHouseNo(!_HouseNumber_!)',             "PYTHON_9.3", codeblock_FixHouseNo)
    arcpy.CalculateField_management(CleanedParcels, "City_Loc",      '!_City_Loc_!',    "PYTHON_9.3")
    arcpy.CalculateField_management(CleanedParcels, "State",         '"VA"',            "PYTHON_9.3")
    arcpy.CalculateField_management(CleanedParcels, "Zip_Code",      '!_Zip_Code_!',    "PYTHON_9.3")   
    arcpy.CalculateField_management(CleanedParcels, "Square_Feet",   'round(!shape.area@SQUAREFEET!, 2)',       "PYTHON_9.3")
    arcpy.CalculateField_management(CleanedParcels, "Acres_US",      'round(!shape.area@ACRES!, 2)',            "PYTHON_9.3")
    arcpy.CalculateField_management(CleanedParcels, "Sub_Name",      '!_Sub_Name_!',    "PYTHON_9.3")
    arcpy.CalculateField_management(CleanedParcels, "Legal_Desc",    '[_Legal_Desc_]',  "VB")
    arcpy.CalculateField_management(CleanedParcels, "Info_Source",   '!_Info_Source_!', "PYTHON_9.3")
    arcpy.CalculateField_management(CleanedParcels, "EditDate",      'Date()',          "PYTHON_9.3", codeblock_Date)
    arcpy.CalculateField_management(CleanedParcels, "EditBy",        '"bkingery"',      "PYTHON_9.3")

    print '\tDeleting unnecessary fields'
    for field in arcpy.ListFields(CleanedParcels):
        if not field.required and field.name not in FinalFields:
            arcpy.DeleteField_management(CleanedParcels, field.name)

def SendEmail():
    try:
        import smtplib
        #mailServer      = 'birch.nnww.local'
        mailServer      = 'nnww-smtp.nnww.nnva.gov'
        mailRecipients  = ['Brian Kingery <bkingery@nnva.gov>']
        mailSender = '%s <%s@nnva.gov>' % (os.environ['USERNAME'], os.environ['USERNAME'])

        subject = 'Parcel Update'
        
        body  = '\nParcel update operation successful\r\n'
        
        message  = ''
        message += 'From: %s\r\n' % mailSender
        message += 'To: %s\r\n' % ', '.join(mailRecipients)
        message += 'Subject: %s\r\n\r\n' % subject
        message += '%s\r\n' % body
        server = smtplib.SMTP(mailServer)
        server.sendmail(mailSender, mailRecipients, message)
        server.quit()
        print 'Email sent'
    except:
        print 'Email not sent'

############################################################################################
