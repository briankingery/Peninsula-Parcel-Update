import arcpy, datetime, os, zipfile, urllib
from arcpy import env

env.workspace = r'R:\Divisions\InfoTech\Shared\GIS\Parcels'
env.overwriteoutput = True

TodaysDate = datetime.datetime.today().strftime('%Y%m%d') # today's date in yyyymmdd format

WB  = env.workspace + os.sep + 'UpdateFolder' + os.sep + TodaysDate + os.sep + 'Parcels_' + TodaysDate + '.gdb' + os.sep + 'WB'
YC  = env.workspace + os.sep + 'UpdateFolder' + os.sep + TodaysDate + os.sep + 'Parcels_' + TodaysDate + '.gdb' + os.sep + 'YC'
POQ = env.workspace + os.sep + 'UpdateFolder' + os.sep + TodaysDate + os.sep + 'Parcels_' + TodaysDate + '.gdb' + os.sep + 'POQ'
NN  = env.workspace + os.sep + 'UpdateFolder' + os.sep + TodaysDate + os.sep + 'Parcels_' + TodaysDate + '.gdb' + os.sep + 'NN'
JCC = env.workspace + os.sep + 'UpdateFolder' + os.sep + TodaysDate + os.sep + 'Parcels_' + TodaysDate + '.gdb' + os.sep + 'JCC'
HAM = env.workspace + os.sep + 'UpdateFolder' + os.sep + TodaysDate + os.sep + 'Parcels_' + TodaysDate + '.gdb' + os.sep + 'HAM'
NKC = env.workspace + os.sep + 'UpdateFolder' + os.sep + TodaysDate + os.sep + 'Parcels_' + TodaysDate + '.gdb' + os.sep + 'NKC'

def WBParcels():
    try:
        WBfolder = env.workspace + os.sep + 'UpdateFolder' + os.sep + TodaysDate + os.sep + 'CityData' + os.sep + 'Williamsburg'
        url = 'http://www.williamsburgva.gov/Modules/ShowDocument.aspx?documentid=3604'
        WBParcels = urllib.URLopener()
        WBZip = WBfolder + os.sep + 'Parcels.zip'
        WBParcels.retrieve(url,WBZip)
        with zipfile.ZipFile(WBZip, "r") as z:
            z.extractall(WBfolder)
        SHP = WBfolder + os.sep + 'Parcels.shp'
        arcpy.CopyFeatures_management(SHP, WB)
        print 'WB parcels copied to main database'
    except:
        print 'Check URL'

def JCCParcels():
    try:
        JCCfolder = env.workspace + os.sep + 'UpdateFolder' + os.sep + TodaysDate + os.sep + 'CityData' + os.sep + 'JamesCityCounty'
        url = "ftp://property.jamescitycountyva.gov/GIS/layers/jcc_parcels.zip"
        JCCParcels = urllib.URLopener()
        JCCZip = JCCfolder + os.sep + 'jcc_parcels.zip'
        JCCParcels.retrieve(url,JCCZip)
        with zipfile.ZipFile(JCCZip, "r") as z:
            z.extractall(JCCfolder)
        SHP = JCCfolder + os.sep + 'parcel_public.shp'
        arcpy.CopyFeatures_management(SHP, JCC)
        print 'JCC parcels copied to main database'
    except:
        print 'Check URL'
