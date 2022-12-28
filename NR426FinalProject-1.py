# Alex Hey
# December 10th, 2022
# Programming for GIS 

#this code takes fire station and parcel data from Longmont, Colorado. It clips out the desired fire station, followed by the homeowners within 3000 feet of that fire station.
# It then uses the Near tool to generate a distance for each homeowner from the fire station. Once all the data is clipped and gathered, the code generates a well-formulated message to homeowners and individual txt files that can be sent to homeowners of Longmont so they are aware of the event.


# Import modules

import arcpy, sys,os

print("imported arcpy")

# Set environments and variables
arcpy.env.workspace = "LongmontProjectData.gdb"
qry = "Address = '1070 Terry Street'"

#make sure data exists

if not arcpy.Exists(arcpy.env.workspace):
    print ("Workspace doesn't exist.")
else:
    print( "\n Workspace is in: {0})".format(arcpy.env.workspace))

# Enable data to overwrite
arcpy.env.overwriteOutput = True  # overwrites output so you can run it again


# arcpy.management.MakeFeatureLayer(in_features, out_layer, {where_clause}, {workspace}, {field_info})
# arcpy.management.SelectLayerByAttribute(in_layer_or_view, {selection_type}, {where_clause}, {invert_where_clause})
# arcpy.management.SelectLayerByLocation(in_layer, {overlap_type}, {select_features}, {search_distance}, {selection_type}, {invert_spatial_relationship})


# Must clip desired fire station out of Layer
# arcpy.management.SelectLayerByAttribute(in_layer_or_view, {selection_type}, {where_clause}, {invert_where_clause})
print("\n Extracting Desired Fire station...")

slct = arcpy.MakeFeatureLayer_management("LongmontFireStations", "TargetFireStation")
slct2 = arcpy.SelectLayerByAttribute_management(slct, "New_Selection", qry)
arcpy.CopyFeatures_management(slct2, "TargetFireStation")
print("Extraction complete.")

# How many points are not within 3000 feet of fire station?
print("\n Selecting within audible yodeling threshold...")
# arcpy.management.SelectLayerByLocation(in_layer, {overlap_type}, {select_features}, {search_distance}, {selection_type}, {invert_spatial_relationship})
slct3 = arcpy.MakeFeatureLayer_management("BoulderCoParcelsforLongmont", "HomesToNotify")
slct4 = arcpy.MakeFeatureLayer_management("TargetFireStation", "FS_Layer")

arcpy.SelectLayerByLocation_management(slct3, "WITHIN_A_DISTANCE", slct4, "3000 FEET")
# #Save as feature class

arcpy.CopyFeatures_management(slct3, "HomesNearYodel")
print("Feature Class Saved. Can be found in: " + r"N:\Classes\workspace\AlHey\Final Project Data\LongmontProjectData.gdb")

#getting count for error checking
cnt4 = arcpy.GetCount_management(slct3)
print("The number of homeowners to contact is:  " + str(cnt4))

#make address 2 equal address 1 if adress 2 isn't null
#UpdateCursor (in_table, field_names, {where_clause}, {spatial_reference}, {explode_to_points}, {sql_clause}, {datum_transformation})
HNY = "HomesNearYodel"
fields = ['MAIL_ADDR1', 'MAIL_ADDR2']
print("\n Combining alternate addresses in parcel data...")
with arcpy.da.UpdateCursor(HNY, fields) as cur:
    for row in cur:
        #if address 2 has an address, make it equal to address 1
        if row[1] != None:
            row[0] = row[1]

        cur.updateRow(row)
print("Mailing addresses updated.")

#Generate distance in feet to Fire Station
#arcpy.analysis.Near(in_features, near_features, {search_radius}, {location}, {angle}, {method}, {field_names})
print("\n Calculating distance of each homeowner to YodelFest..")
arcpy.analysis.Near("HomesNearYodel","TargetFireStation","","","","GEODESIC")
print("New Field with Distance added in HomesNearYodel Layer.")

#Setting cursors for text template,
# SearchCursor (in_table, field_names, {where_clause}, {spatial_reference}, {explode_to_points}, {sql_clause}, {datum_transformation})


txtfields = ['MAIL_ADDR1','NEAR_DIST']
print("Generating text files for mailing...")
#use search cursor to view values of attribute table
with arcpy.da.SearchCursor(HNY, txtfields) as cur:
    for row in cur:
        #take out null rows
        if row[0] != None:
            #generate txt file
            with open("output.txt","a") as f:
                print("To Homeowner at " + row[0] + ":" + "\n You are located " + str(row[1]) + " feet of Fire Station #1 at 1070 Terry Street. We are having our annual yodeling concert this weekend. Please disregard all yodeling during this time.", file=f)
print("Master text file generation complete.")

print("\n Generating letters for every 2 lines of master file...")

# open the original file for reading
original_file = open('output.txt', 'r')

# initialize the line counter to 0
counter = 0
filecounter = 0

# loop through the lines in the file
for line in original_file:
    # if the line counter is 0
    if counter == 0:
        # create a new file
        new_file = open('letter'+ str(filecounter) + '.txt', 'w')
        filecounter += 1
    # write the line to the new file
    new_file.write(line)
    # increment the line counter
    counter += 1
    # if the line counter is 2
    if counter == 2:
        # close the new file
        new_file.close()
        # reset the counter
        counter = 0
# close the original file
original_file.close()

print("\n Letters have been generated." )