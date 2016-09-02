

import arcpy, datetime, os, zipfile, urllib
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
OldParcels          = env.workspace + os.sep + 'UpdateFolder' + os.sep + TodaysDate + os.sep + 'Parcels_' + TodaysDate + '.gdb' + os.sep + 'OLD_RealPropertyParcel_' + TodaysDate



############################################################################################

def UpdateData():
    # Add a Database connection to sdeVector using SQL Server on Conway using Operating System Authentication
        # Rename to OS_DQSQL_sdeVector.sde
    # Create version (using ArcMap Version Manager) - bkingery
    # Right Click on connection --> Geodatabase Connection Properties --> Choose appropriate Version

##    # Test
##    masterParcels = r'Database Connections\OS_DQSQL_sdeVector.sde\sdeVector.SDEDATAOWNER.Cadastral\sdeVector.SDEDATAOWNER.RealPropertyParcel'

    # Real
    masterParcels = r'Database Connections\OS_Conway_sdeVector.sde\sdeVector.SDEDATAOWNER.Cadastral\sdevector.SDEDATAOWNER.RealPropertyParcel'


##    # Copy outdated parcels to project gdb as a backup
##    arcpy.CopyFeatures_management(masterParcels, OldParcels)
##    print 'Old version of Parcels copied to Parcels_' + TodaysDate + '.gdb'


    # Delete rows in versioned feature class
    arcpy.DeleteFeatures_management(masterParcels)
    print 'Parcels deleted'


    # Append new values to versioned feature class

##    # Test
##    try:
##        arcpy.Append_management(OldParcels, masterParcels, "TEST", "", "")
##    except:
##        print 'Error - check results'

    # Real
    try:
        arcpy.Append_management(CleanedParcels, masterParcels, "TEST", "", "")
    except:
        print 'Error - check results'

    print 'New version of Parcels uploaded'


