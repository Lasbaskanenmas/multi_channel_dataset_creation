#use this script to turn geopackages into label images
# for instructions, do:
# python geopackage_to_label_im.py -h

import argparse
import os
import json
import geopandas as gpd
import rasterio
from rasterio.features import geometry_mask
import numpy as np
from osgeo import gdal
import fiona



def create_mapping(gdf):
    """
    Find the classes that exist in the geopackage
    Also including the ignore_index == 0 wichmeans that we dont cate how the ML model classifies the pixel, and the background class == 1 wich means that the pixel NOT is a building
    """
    unique_values = list(gdf['AI tagklasse (Beregnet)'].unique())
    unique_values = [value for value in unique_values if value != None]

    print("unique_values:"+str(unique_values))
    unique_values.sort()
    unique_values= ["ignore_index","background"]+unique_values
    return {val: idx + 0 for idx, val in enumerate(unique_values)}  # Start indexing from 0 (ignore_index ==0, background == 1 )

def save_mapping(mapping, path):
    with open(path, 'w') as f:
        json.dump(mapping, f)

def load_mapping(path):
    with open(path, 'r') as f:
        return json.load(f)

def process_geotiff(geopackage_path, geotiff_path, output_geotiff_path, value_map,unknown_boarder_size ):
    print(f"#### Working on creating: {output_geotiff_path} ####")
    print(f"Area defined by: {geotiff_path}")

    try:
        ###################################################################################
        #DEBUGGING#
        debug = False
        if debug:
            # List all layers in the GeoPackage
            layers = fiona.listlayers(geopackage_path)
            print(f"Layers in GeoPackage: {layers}")

            # Iterate over each layer to list fields
            for layer in layers:
                print(f"\nFields in layer '{layer}':")
                with fiona.open(geopackage_path, layer=layer) as src:
                    fields = src.schema['properties']
                    for field, field_type in fields.items():
                        print(f" - {field} ({field_type})")
        ###################################################################################

        # Load the geopackage
        print("reading geopackage..")
        gdf = gpd.read_file(geopackage_path,layer="GeoDanmark/BBR Bygning")
        print("done")



        # Read the input GeoTIFF
        with rasterio.open(geotiff_path) as src:
            profile = src.profile
            transform = src.transform
            out_shape = src.shape

            # Ensure the profile for the output is for a single-band image
            profile.update(
                dtype=rasterio.uint8,
                count=1,
                compress='lzw',  # optional, for compression
                photometric='Grayscale',
                nodata=0
            )

            #1.  Create an initial array filled with 1 (value for areas not covered by any polygon)
            output_array = np.ones(out_shape, dtype=rasterio.uint8)

            #2. create the labels
            #fill building polygons with value coresponding to roof material
            #also make a boarder filled with 0 == ignore_label so that the model dont have to classify the boarderpixels
            # Set all values covered by a polygon plus a buffer of size 1 to zero
            if not gdf.empty:
                value_mask = geometry_mask([geom.buffer(unknown_boarder_size/2) for geom in gdf.geometry], transform=transform, invert=True, out_shape=out_shape)
                output_array[value_mask] = 0
            # Assign values to the output array based on the attribute values
            # this should overwrite the 0 values except at the boarder areas
            for value, int_value in value_map.items():
                value_gdf = gdf[gdf['AI tagklasse (Beregnet)'] == value]

                if not value_gdf.empty:
                    value_mask = geometry_mask([geom.buffer(-unknown_boarder_size/2) for geom in value_gdf.geometry], transform=transform, invert=True, out_shape=out_shape)
                    output_array[value_mask] = int_value

            #3.handle invalid labels
            #handle invalid labels by setting them to 0 == ingore_label
            # Set all areas with "Dårlig label" == True to unknown
            unknown_gdf = gdf[gdf['Dårlig label']]
            print(unknown_gdf)
            unknown_gdf = gdf[gdf['Dårlig label']==True]
            print(unknown_gdf)
            if not unknown_gdf.empty:
                unknown_mask = geometry_mask([geom.buffer(unknown_boarder_size/2) for geom in unknown_gdf.geometry], transform=transform, invert=True, out_shape=out_shape)
                output_array[unknown_mask] = 0
            else:
                print("no polygons with value 'Dårlig label'")

            #set all values with label 'Ukendt' til unkown==0
            value_gdf = gdf[gdf['AI tagklasse (Beregnet)'] == "Ukendt"]
            if not value_gdf.empty:
                value_mask = geometry_mask([geom for geom in value_gdf.geometry], transform=transform, invert=True, out_shape=out_shape)
                output_array[value_mask] = 0








        #4. Write the output GeoTIFF
        with rasterio.open(output_geotiff_path, 'w', **profile) as dst:
            dst.write(output_array, 1)
        print("range of data in output_array is : " + str(output_array.flatten().min()) + " - " + str(output_array.flatten().max()))

        print(f"Output GeoTIFF saved to {output_geotiff_path}")
        return True

    except Exception as e:
        print(f"Failed to process {geotiff_path}: {e}")
        return False


def process_all_geotiffs(geopackage_path, input_folder, output_folder, value_map,unknown_boarder_size):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    failed_files = []

    for file_name in os.listdir(input_folder):
        if file_name.endswith('.tiff') or file_name.endswith('.tif'):
            input_path = os.path.join(input_folder, file_name)
            output_path = os.path.join(output_folder, file_name)
            if not process_geotiff(geopackage_path, input_path, output_path, value_map,unknown_boarder_size):
                failed_files.append(file_name)

    # Save the failed files to a text file
    with open('failed_files.txt', 'w') as f:
        for file in failed_files:
            f.write(f"{file}\n")

    # Print the failed files
    if failed_files:
        print("Failed files:")
        for file in failed_files:
            print(file)

def main():
    example_usage = 'python geopackage_to_label_im.py --geopackage "F:\SDFI\DATA\MachineLearning\bygningsudpegning\labels\GeoDanmark -AI projekt\GeoDanmark -AI projekt\AI_bygning_labels.gpkg" --input_folder \\prod.sitad.dk\dfs\CU2314\F-DREV\SDFI\DATA\MachineLearning\bygningsudpegning\data\machine_learning_ready_data\rgb --create_new_mapping --path_to_mapping \\prod.sitad.dk\dfs\CU2314\F-DREV\SDFI\DATA\MachineLearning\bygningsudpegning\data\machine_learning_ready_data\mapping2.txt --unknown_boarder_size 0.1 --output_folder \\prod.sitad.dk\dfs\CU2314\F-DREV\SDFI\DATA\MachineLearning\bygningsudpegning\labels\large_labels'
    print("example usage: "+str(example_usage))
    parser = argparse.ArgumentParser(description='Process GeoTIFF files based on GeoPackage data.')
    parser.add_argument('--geopackage', type=str, required=True, help='Path to the GeoPackage file')
    parser.add_argument('--input_folder', type=str, required=True, help='Path to the folder containing input GeoTIFF files')
    parser.add_argument('--output_folder', type=str, required=True, help='Path to the folder to save output GeoTIFF files')
    parser.add_argument('--create_new_mapping', action='store_true', help='Whether to create a new mapping from the GeoPackage')
    parser.add_argument('--path_to_mapping', type=str, required=True, help='Path to save or load the mapping file')
    parser.add_argument('--unknown_boarder_size', type=float, default=0.1, help='how large baorder of "unkown"==0 values should there be around the areas defined by polygons? set to 0 to not have any boarder at all. 0.1 is interpreted as 0.1 meter of boarder ')


    args = parser.parse_args()

    if args.create_new_mapping:
        gdf = gpd.read_file(args.geopackage,layer="GeoDanmark/BBR Bygning")
        value_map = create_mapping(gdf)
        save_mapping(value_map, args.path_to_mapping)
    else:
        value_map = load_mapping(args.path_to_mapping)

    process_all_geotiffs(args.geopackage, args.input_folder, args.output_folder, value_map,args.unknown_boarder_size)

if __name__ == '__main__':
    main()
