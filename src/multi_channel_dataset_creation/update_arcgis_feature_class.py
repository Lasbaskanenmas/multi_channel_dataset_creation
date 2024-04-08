import arcpy
import configparser



def create_field_with_inverse_polygon_area(input_fc ,field_name="Inverse_area",field_type = "DOUBLE"):
    arcpy.AddField_management(input_fc, field_name, field_type)
    # Calculate the inverse of the area for each polygon
    with arcpy.da.UpdateCursor(input_fc, ["SHAPE@", field_name]) as cursor:
        for row in cursor:
            polygon = row[0]
            #some polygons might be None, check for this before trying to create the 'Inverse_area' field
            if polygon is not None:


                area = polygon.area
                if area != 0:  # To avoid division by zero
                    inverse_area = 1 / area
                    row[1] = inverse_area
                else:
                    row[1] = None  # Handle cases where the area is zero
                cursor.updateRow(row)


def main(config):
    ini_parser = configparser.ConfigParser()
    ini_parser.read(config)
    section = "SETTINGS"
    gdb_file =ini_parser[section]["gdb_file"]
    merged_labels = ini_parser[section]["mask_featureclass"]


    merged_labels_feature_class = gdb_file+ "\\" + merged_labels  # r"F:\SDFI\DATA\MachineLearning\befaestelse\arcgislabels\arcgis_labels\arcgis_labels.gdb\merged_labels"

    unmerged_feature_classes= ini_parser[section]["unmerged_feature_classes"]
    print("clearing the feature_class..")
    arcpy.management.DeleteFeatures(merged_labels_feature_class)
    
    #remove the field that doesnt exists in original arcgis feaure classes(we create it later in the merged_features featureclass)
    arcpy.management.DeleteField(merged_labels_feature_class, "Inverse_area")
    #fill the featureclass with all label data in all the differetn featureclasses the people working with making the labels have done
    print("filling the feature class with all labels stored in all the different feature classes that people have saved labels to...")
    arcpy.management.Append(unmerged_feature_classes,merged_labels_feature_class , "TEST", None, '', "OBJECTID IS NOT NULL")
    #When crating labels, it sometimes happens that people first create a large polygon , and then crates a small polygon "ontop of the large". In order to prioritize the small polygons we create afield holding the inverse area , wich later can be used as priority when creating mask-images
    create_field_with_inverse_polygon_area(input_fc=merged_labels_feature_class)

    print(merged_labels + " : Done")







