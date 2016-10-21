#################################################################################################################
##  CCBH Geocoding Service can be used to geocode any dbf file with address, city, state, and zip field.       ##
##    It requires a computer with an ArcGIS software license available for use.  The first geocode attempt     ##
##    is made with the ArcGIS software which requires an "Address Locator" file as input.  The Address locator ##
##    file is made within the ArcGIS software. 
##    Google maps API is utilized also, therefore internet is also a requirement. A max of 15,000 geocoding
##      request may be made per 24 hours.
##                                                                                                             ##
##   Created July 2012 by Carl Preusser                                                                        ##
#################################################################################################################

# Import system modules required for this program
import sys, string, os, arcpy
from arcpy import env
import time
import geopy
import pyproj
from geopy import geocoders
#Set arcpy to Overwrite any existing data...if this is set to False the program would require unique names...maybe set with a datetime timestamp
arcpy.env.overwriteOutput = True
 
layerString = "T:\\transfer\\GIS DATA\\Preusser\\Cuyahoga\\Septic_Storm_Project\\service_areas.shp"  #arcpy.GetParameterAsText(0)
desc = arcpy.Describe(layerString)
shapefieldname = desc.ShapeFieldName

cursor = arcpy.UpdateCursor(layerString)


#Test Loop to determine if we can loop through each polygon record in a shapefile to gather the points in each
for row in cursor:
    polygon = row.getValue(shapefieldname)
    for points in polygon:
        for point in points:
            print point.X, point.Y

# CHANGE LOCATION A .......................................................................................................
Local address file we are looking to geocode...
incidents = "C:\\Program Files\\ArcGIS\\Python\\Euclid_SRTS.csv"
 
# CHANGE LOCATION B .......................................................................................................
# ArcGIS created address locator.  
addressLocator = "C:\\Program Files\\ArcGIS\\Cuyahoga\\Address Locators\\AddressLocator"

# CHANGE LOCATION C.......................................................................................................
# Output file...1st attempt to match all addresses.
incidentGeocodeOutput = "C:\\Program Files\\ArcGIS\\Python\\SRTS_GeocodeOutput.shp"

# CHANGE LOCATION D .......................................................................................................
# Run ArcGIS Geocode tool: Geocode Addresses...
# Note the syntax of the field names referenced is: "identifier" "actual field name" VISIBLE NONE,
arcpy.GeocodeAddresses_geocoding(incidents, addressLocator, "Street Address VISIBLE NONE; City City VISIBLE NONE",incidentGeocodeOutput, "STATIC")

desc = arcpy.Describe(incidentGeocodeOutput)
shapefieldname = desc.ShapeFieldName

#Set local variables for the addition of fields in the newly created file
fieldName1 = "GeoLat"
fieldName2 = "GeoLon"
fieldName3 = "GeoMethod"
fieldName4 = "GeoErr"
fieldName5 = "GeoStatus"
fieldName6 = "GeoExplain"
fieldPrecision = 16
fieldScale = 6
 
#Add Fields: GeoLat, GeoLon
arcpy.AddField_management(incidentGeocodeOutput, fieldName1, "DOUBLE", fieldPrecision, fieldScale, "", "", "NULLABLE")
arcpy.AddField_management(incidentGeocodeOutput, fieldName2, "DOUBLE", fieldPrecision, fieldScale, "", "", "NULLABLE")
#Add Field: GeoMethod.  This is to explain what method was used to attain the latitude and longitude
arcpy.AddField_management(incidentGeocodeOutput, fieldName3, "TEXT", "", "")
#Add Field: GeoErr.  This reports the google error from the google geocode attempt.
arcpy.AddField_management(incidentGeocodeOutput, fieldName4, "TEXT", "", "")
#Add Fields: GeoStatus, GeoStatusExp. GeoStatus field reports "Could not Geocode", GeoStatusExp reports a reason, i.e. PO Box
arcpy.AddField_management(incidentGeocodeOutput, fieldName5, "TEXT", "", "")
arcpy.AddField_management(incidentGeocodeOutput, fieldName6, "TEXT", "", "")


#Change Projection to World/Lat Long Projection
coordinateSystem = "GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]]"
arcpy.DefineProjection_management(incidentGeocodeOutput, coordinateSystem)

#Create update cursor for feature class 
rows = arcpy.UpdateCursor(incidentGeocodeOutput)

for row in rows:
    status = row.Status
    if status == "M":  
        address = row.GetValue(inAddressField)
        #Create the geometry object 'feat'

        feat = row.getValue(shapefieldname)
        pnt = feat.getPart() 
        partnum = 0

        #Count the number of points in the current multipart feature
        partcount = feat.partCount

        #Enter while loop for each point in the multipoint feature 
        while partnum < partcount:
            #Get the point based on the current part number
            pnt = feat.getPart(partnum)
            Print x,y coordinates of current point
            row.GeoLat = pnt.X
            row.GeoLon = pnt.Y
            row.GeoMethod = "ArcGIS"
            print str(row.GeoLat) + ", " + str(row.GeoLon) + ", " + row.GeoMethod
            rows.updateRow(row) 
            partnum += 1
    elif status == "U":
         g = geocoders.Google()
         time.sleep(1)
        #This is the variable made up of the actual address file field/column names for Street Number/Name, City, State
        #  The syntax is necessary for google's geocoding service
        address = row.ST + " in " + row.CITY + ", Ohio"  
        try:
            place, (lat, lng) = g.geocode(address) 
            row.GeoMethod = "Google"
            feat = row.getValue(shapefieldname)
            pnt = feat.getPart()
            p1 = pyproj.Proj(init='epsg:3734')
            # 1 foot = 0.3048 meters
            conv = 0.3048
            x, y = p1(lng,lat)
            y1 = x/conv
            x1 = y/conv
            partnum = 0
            #Count the number of points in the current multipart feature
            partcount = feat.partCount
            Enter while loop for each point in the multipoint feature
            while partnum < partcount:
            #Get the point based on the current part number
                pnt = feat.getPart(partnum)
                pnt.X = y1
                pnt.Y = x1
                row.GeoLat = pnt.X
                row.GeoLon = pnt.Y
                print str(y1) + ", " + str(x1) + ", " + row.GeoMethod
                rows.updateRow(row)
                partnum += 1
        except ValueError:
            continue

#Delete cursor and row objects to remove locks on the data 
del row 
del rows

print "Geocode Complete..."
inTable = "C:\\Program Files\\ArcGIS\\Python\\incidentPythonGeocodeOutput.shp"
outTable = "C:\\Program Files\\ArcGIS\\Python\\tableGeocode.dbf"
arcpy.CopyRows_management(inTable, outTable)

#Set the local variables
x_coords = "GeoLat"
y_coords = "GeoLon"
out_Layer = "C:\\Program Files\\ArcGIS\\Python\\incidents_layer"
saved_Layer = "C:\\Program Files\\ArcGIS\\Python\\GeocodedIncidents.lyr"
 
# Set the spatial reference
spRef = r"Coordinate Systems\Projected Coordinate Systems\State Plane\NAD 1983 (US Feet)\NAD 1983 StatePlane Ohio North FIPS 3401 (US Feet).prj"
 
# Make the XY event layer...
arcpy.MakeXYEventLayer_management(outTable, x_coords, y_coords, out_Layer, spRef)
 
# Print the total rows
print arcpy.GetCount_management(out_Layer)
 
# Save to a layer file
arcpy.SaveToLayerFile_management(out_Layer, saved_Layer)

# This section was an attempt to then pass the resultant geocoded data table into various ESRI tools like hot spot analysis...

# Aggregate data to available census block group...
spatialJoin = "C:\\Program Files\\ArcGIS\\Python\\tl_2010_39035_bg10\\tl_2010_39035_bg10.shp"
spatialJoinOut = "C:\\Program Files\\ArcGIS\\Python\\spatialJoinOutput.shp"
arcpy.SpatialJoin_analysis(spatialJoin,incidentGeocodeOutput, spatialJoinOut, "JOIN_ONE_TO_ONE", "KEEP_ALL","#", "CONTAINS")

print "Spatial Join Complete..."

# generage a spatial weight matrix for our polygon layer
swmFC = "C:\\Program Files\\ArcGIS\\Python\\euclidean6Neighs.swm"
swm = arcpy.GenerateSpatialWeightsMatrix_stats(spatialJoinOut, "TARGET_FID",
                       swmFC,
                       "K_NEAREST_NEIGHBORS",
                       "#", "#", "#", 6,
                       "NO_STANDARDIZATION") 

# Hot Spot Analysis of Incidents
# Process: Hot Spot Analysis (Getis-Ord Gi*)
incidentHotSpotOutput = "C:\\Program Files\\ArcGIS\\Python\\incidentHotSpotOutput.shp"
arcpy.HotSpots_stats(spatialJoinOut, "Join_Count", incidentHotSpotOutput, 
                "GET_SPATIAL_WEIGHTS_FROM_FILE",
                "EUCLIDEAN_DISTANCE", "NONE",
                "#", "#", swmFC)

 
