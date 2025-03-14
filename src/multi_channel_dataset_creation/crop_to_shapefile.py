import os
import pathlib
import rasterio
from rasterio.windows import Window
from osgeo import ogr
import sys
import time

def main(inputfolder, outputfolder,shapefile_path,extra_boarder=50, replacestring="", newstring="", only_consider_files_with_matching_names=False):
    if pathlib.Path(inputfolder).exists():
        files = os.listdir(inputfolder)
        files.sort()
    else:
        files =[]
    for (index, file) in enumerate(files):
        print("working on file :" + str(index) + " out of :" + str(len(files)))
        input_path = pathlib.Path(inputfolder) / pathlib.Path(file)
        output_path = pathlib.Path(outputfolder) / pathlib.Path(file.replace(replacestring, newstring))
        if only_consider_files_with_matching_names and replacestring not in file:
            pass
        else:
            if True:#try:
                main_crop_geotiff(geotiff_path=input_path, shapefile_path=shapefile_path, output_path=output_path,extra_boarder=extra_boarder)
            else:#except:
                print("##############################################failed to crop iamge:"+str(input_path))


import rasterio
from rasterio.windows import from_bounds



def crop_geotiff(input_path, output_path, bounding_box):
    print("croping image:"+str(input_path)+ " to "+str(output_path))
    with rasterio.open(input_path) as src:
        # Create a window based on the bounding box
        window = from_bounds(bounding_box[0], bounding_box[2], bounding_box[1], bounding_box[3], src.transform)

        if (window.col_off < 0 or window.row_off < 0 or
            window.col_off + window.width > src.width or
            window.row_off + window.height > src.height):
            input("Window is out of bounds for the input raster., now making sure that the outut file is deletet (if input and outputfile is the same we need to delete it , otherwise we could keep the original)")
            pathlib.Path(output_path).unlink(missing_ok=True)

        try:
            # Read the data within the window
            data = src.read(window=window)
        except:
            print("failed to crop :"+str(input_path))
            print("making sure the output file is deleted in case input and output is the same")
            pathlib.Path(output_path).unlink(missing_ok=True)
            return
        # Update the transform for the new window
        window_transform = src.window_transform(window)

        # Update the metadata
        meta = src.meta
        meta.update({
            'driver': 'GTiff',
            'height': window.height,
            'width': window.width,
            'transform': window_transform
        })

    # Write the cropped GeoTIFF to a tmp file before moving it to the destination (this fixes an issie with rasterio if input path and output path are identical)
    # Create a new path by adding 'tmp_' to the file name
    tmp_path = pathlib.Path(input_path).with_name('tmp_' + pathlib.Path(input_path).name)
    with rasterio.open(tmp_path, 'w', **meta) as dst:
        dst.write(data)
    # Move the file to the new location
    pathlib.Path(tmp_path).rename(output_path)

"""

def crop_geotiff(input_path, output_path, bounding_box):
    with rasterio.open(input_path) as src:
        # Get the window based on the bounding box
        window = src.window(bounding_box[0], bounding_box[2], bounding_box[1], bounding_box[3])

        # Read the data within the window
        data = src.read(window=window)

        # Update the transform for the new window
        window_transform = src.window_transform(window)

        # Update the metadata
        meta = src.meta
        meta.update({
            'driver': 'GTiff',
            'height': window.height,
            'width': window.width,
            'transform': window_transform
        })

        # Write the cropped GeoTIFF
        with rasterio.open(output_path, 'w', **meta) as dst:
            dst.write(data)
"""
def main_crop_geotiff(geotiff_path, shapefile_path, output_path,extra_boarder):
    # Open the shapefile to get the bounding box
    shape_ds = ogr.Open(shapefile_path)
    layer = shape_ds.GetLayer()
    extent = layer.GetExtent()
    with rasterio.open(geotiff_path) as openedfile:
        original_bounds = openedfile.bounds
        # get the bounds of the shapefile
        xmin, xmax, ymin, ymax = extent

        # Add a 50-pixel border to bounds (good to have a little information on whats around the pixel, and we also remove the 20 outmost pr$

        xmin -= extra_boarder
        ymin -= extra_boarder
        xmax += extra_boarder
        ymax += extra_boarder

        # adjust the bounds to not be utside of the original image


        xmin = max(xmin, original_bounds.left)
        ymin = max(ymin, original_bounds.bottom)
        xmax = min(xmax, original_bounds.right)
        ymax = min(ymax, original_bounds.top)

        print("shapefile:" + str(extent))
        print("original image :" + str(original_bounds))
        print("rasterio version: " + str([xmin, xmax, ymin, ymax]))

        # Calculate the pixel coordinates of the bounding box
    with rasterio.open(geotiff_path) as src:


        xmin_pixel, ymin_pixel = map(int, ~src.transform * (xmin, ymin))
        xmax_pixel, ymax_pixel = map(int, ~src.transform * (xmax, ymax))


        # Get the geographic coordinates of the adjusted bounding box
        xmin_adj, ymin_adj = src.transform * (xmin_pixel, ymin_pixel)
        xmax_adj, ymax_adj = src.transform * (xmax_pixel, ymax_pixel)

    print("Adjusted bounding box in pixels: ", [xmin_pixel, xmax_pixel, ymin_pixel, ymax_pixel])
    print("Adjusted bounding box in geographic coordinates: ", [xmin_adj, xmax_adj, ymin_adj, ymax_adj])
    print("min([xmax_pixel-xmin_pixel,ymax_pixel-ymin_pixel]):"+str(min([xmax_pixel-xmin_pixel,ymax_pixel-ymin_pixel])))
    print("[xmin_pixel, xmax_pixel, ymin_pixel, ymax_pixel]:"+str([xmin_pixel, xmax_pixel, ymin_pixel, ymax_pixel]))
    print("min([xmax_pixel-xmin_pixel, ymin_pixel- ymax_pixel]):"+str(min([xmax_pixel-xmin_pixel, ymin_pixel- ymax_pixel])))

    if min([xmin_pixel, xmax_pixel, ymin_pixel, ymax_pixel])<0:
        print("output image would have become negative size")
        pathlib.Path(output_path).unlink(missing_ok=True)
        
    elif min([xmax_pixel-xmin_pixel, ymin_pixel- ymax_pixel]) <1010:
        print("images smaller than 1010 are skipped, a better solution would be to enlarge them to be 1010")
        pathlib.Path(output_path).unlink(missing_ok=True)
    else:
        # Crop the GeoTIFF using the adjusted bounding box
        crop_geotiff(geotiff_path, output_path, [xmin_adj, xmax_adj, ymin_adj, ymax_adj])

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Crop GeoTIFF using a shapefile with a 10-pixel border.")
    parser.add_argument("--input", required=True, help="Path to the folder or GeoTIFF file.")
    parser.add_argument("--shapefile", required=True, help="Path to the shapefile.")
    parser.add_argument("--output", required=True, help="Path to output folder or the new GeoTIFF file")
    parser.add_argument("--extra_boarder",default = 50,type=int)

    args = parser.parse_args()

    if pathlib.Path(args.input).is_dir() and  pathlib.Path(args.output).is_dir():
        main(inputfolder=args.input, outputfolder=args.output, replacestring="", newstring="", only_consider_files_with_matching_names=False, shapefile_path=args.shapefile,extra_boarder = args.extra_boarder)
    elif pathlib.Path(args.input).is_file() and  pathlib.Path(args.output).is_file(): 
        main_crop_geotiff(args.input, args.shapefile, args.output,args.extra_boarder)
    else:
        sys.exit("input and output paths shoudl point to two folders OR two files")

