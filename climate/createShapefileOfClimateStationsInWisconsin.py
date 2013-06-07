import arcpy, urllib, time, os
import numpy as np
from arcpy import env
env.overwriteOutput = True
user = 'ruesca'

# Input
climateDir = 'T:/Projects/Wisconsin_River/GIS_Datasets/Climatological/stationData'
wrbFile = "T:/Projects/Wisconsin_River/GIS_Datasets/Watersheds/WRB_Basin.shp"
stationLink = "ftp://ftp.ncdc.noaa.gov/pub/data/inventories/ISH-HISTORY.TXT"
wgs84file = "C:/Program Files (x86)/ArcGIS/Desktop10.0/Coordinate Systems/Geographic Coordinate Systems/World/WGS 1984.prj"
# Intermediate Files
stationFile = 'C:/Users/' + user + '/Downloads/stationInfo.txt'
cleanedFile = 'C:/Users/' + user + '/Downloads/stationInfo_cleaned.txt'
globalStations = 'C:/TEMP/globalStations.shp'
buffer50Mile = 'C:/TEMP/buffer50Mile.shp'
# Output Files
wisconsinStations = climateDir + '/locations/stationLocations.shp'
urllib.urlretrieve (stationLink, stationFile)
fixedWidths = [7, 6, 30, 6, 3, 5, 7, 8, 10, 9, 9]
dtypes = np.dtype([('USAF', 'S7')\
          , ('WBAN', 'S6')\
          , ('STATION NAME', 'S30')\
          , ('CTRY', 'S6')\
          , ('ST', 'S3')\
          , ('CALL', 'S5')\
          , ('LAT', float)\
          , ('LON', float)\
          , ('ELEV', float)\
          , ('BEGIN', 'S9')\
          , ('END', 'S9')])
# Use skiprows if version earlier than 1.3, otherwise skip_header
if float(np.version.version[0:3]) >= 1.7:
	stationData = np.genfromtxt (stationFile, dtype = dtypes, skip_header = 22\
		, delimiter = fixedWidths)
else:
	stationData = np.genfromtxt (stationFile, dtype = dtypes, skiprows = 22\
		, delimiter = fixedWidths)
recovery = np.empty_like(stationData)
recovery[:] = stationData
# ------------------------------------------

stationData = np.empty_like(recovery)
stationData[:] = recovery
stationData = stationData[stationData['LAT'] != -99999.0]
stationData = stationData[stationData['LAT'] != 0.0]
stationData = stationData[np.invert(np.isnan(stationData['LAT']))]
stationData = stationData[stationData['LON'] != -99999.0]
stationData = stationData[stationData['LON'] != 0.0]
stationData = stationData[np.invert(np.isnan(stationData['LON']))]
stationData['LAT'] = stationData['LAT'] / 1000.
stationData['LON'] = stationData['LON'] / 1000.
stationData = stationData[['USAF', 'WBAN', 'LAT', 'LON', 'BEGIN', 'END']]
# Strip leading and trailing characters
for col in ['USAF', 'WBAN', 'BEGIN', 'END']:
	stationData[col] = np.char.rstrip(stationData[col], ' ')
	stationData[col] = np.char.lstrip(stationData[col], ' ')

f = open(cleanedFile, 'w')
f.write(','.join(stationData.dtype.names) + '\n')
np.savetxt(f, stationData, fmt = '%s,%s,%f,%f,%s,%s')
f.close()
##arcpy.MakeTableView_management(cleanedFile, "stationTable")
arcpy.MakeXYEventLayer_management(cleanedFile, "LON", "LAT", "latLongPoints", wgs84file)
arcpy.CopyFeatures_management("latLongPoints", globalStations)
arcpy.Buffer_analysis(wrbFile, buffer50Mile, "50 miles")
env.outputCoordinateSystem = wrbFile
arcpy.Clip_analysis(globalStations, buffer50Mile, wisconsinStations)

# Create metadata
wisconsinStations = os.path.basename(wisconsinStations)
timeNow = time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime())
scriptFile = r'"\code\climate\mergeWwiWithNass2011_wholeState.py"'

mergedMetadataOut = mergedFile + " was created/changed by " + user + " on " + timeNow\
	+ ' using ' + scriptFile + '\n\n'
f = open(mergedMetadataFile, 'a+')
f.write(mergedMetadataOut)
f.close()





