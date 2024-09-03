import os
import pathlib
import rasterio
from rasterio.windows import Window
from osgeo import ogr



def main(inputfolder, outputfolder, replacestring, newstring, only_consider_files_with_matching_names, shapefile_path):
    if pathlib.Path.exists(inputfolder):
        files = os.listdir(inputfolder)
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
                main_crop_geotiff(geotiff_path=input_path, shapefile_path=shapefile_path, output_path=output_path)
            else:#except:
                print("##############################################failed to crop iamge:"+str(input_path))


import rasterio
from rasterio.windows import from_bounds

def crop_geotiff(input_path, output_path, bounding_box):
    print("croping image:"+str(input_path)+ " to "+str(output_path))
    with rasterio.open(input_path) as src:
        # Create a window based on the bounding box
        window = from_bounds(bounding_box[0], bounding_box[2], bounding_box[1], bounding_box[3], src.transform)

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

# Rest of your code remains unchanged
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
def main_crop_geotiff(geotiff_path, shapefile_path, output_path):
    # Open the shapefile to get the bounding box
    shape_ds = ogr.Open(shapefile_path)
    layer = shape_ds.GetLayer()
    extent = layer.GetExtent()

    original_bounds = rasterio.open(geotiff_path).bounds

    # get the bounds of the shapefile
    xmin, xmax, ymin, ymax = extent

    # Add a 50-pixel border to bounds (good to have a little information on whats around the pixel, and we also remove the 20 outmost pr$

    xmin -= 50
    ymin -= 50
    xmax += 50
    ymax += 50

    # adjust the bounds to not be utside of the original image


    xmin = max(xmin, original_bounds.left)
    ymin = max(ymin, original_bounds.bottom)
    xmax = min(xmax, original_bounds.right)
    ymax = min(ymax, original_bounds.top)

    print("shapefile:" + str(extent))
    print("original image :" + str(original_bounds))
    print("rasterio version: " + str([xmin, xmax, ymin, ymax]))

    # Calculate the pixel coordinates of the bounding box
    src = rasterio.open(geotiff_path)


    xmin_pixel, ymin_pixel = map(int, ~src.transform * (xmin, ymin))
    xmax_pixel, ymax_pixel = map(int, ~src.transform * (xmax, ymax))

    # Adjust the bounding box to be within the original image boundaries
    #xmin, xmax, ymin, ymax = extent
    #xmin = max(xmin, original_bounds.left)
    #ymin = max(ymin, original_bounds.bottom)
    #xmax = min(xmax, original_bounds.right)
    #ymax = min(ymax, original_bounds.top)

    # Add a 50-pixel border to the adjusted bounding box (good to have a little information on whats around the pixel, and we also remove the 20 outmost predictionpixels)

    #xmin -= 50
    #ymin -= 50
    #xmax += 50
    #ymax += 50

    # Ensure the adjusted bounding box is within the original image extent
    #xmin = max(xmin, original_bounds.left)
    #ymin = max(ymin, original_bounds.bottom)
    #xmax = min(xmax, original_bounds.right)
    #ymax = min(ymax, original_bounds.top)


    # Get the geographic coordinates of the adjusted bounding box
    xmin_adj, ymin_adj = src.transform * (xmin_pixel, ymin_pixel)
    xmax_adj, ymax_adj = src.transform * (xmax_pixel, ymax_pixel)

    print("Adjusted bounding box in pixels: ", [xmin_pixel, xmax_pixel, ymin_pixel, ymax_pixel])
    print("Adjusted bounding box in geographic coordinates: ", [xmin_adj, xmax_adj, ymin_adj, ymax_adj])
    print("min([xmax_pixel-xmin_pixel,ymax_pixel-ymin_pixel]):"+str(min([xmax_pixel-xmin_pixel,ymax_pixel-ymin_pixel])))
    print("[xmin_pixel, xmax_pixel, ymin_pixel, ymax_pixel]:"+str([xmin_pixel, xmax_pixel, ymin_pixel, ymax_pixel]))
    print("min([xmax_pixel-xmin_pixel, ymin_pixel- ymax_pixel]):"+str(min([xmax_pixel-xmin_pixel, ymin_pixel- ymax_pixel])))

    if min([xmin_pixel, xmax_pixel, ymin_pixel, ymax_pixel])<0:
        pass
    elif min([xmax_pixel-xmin_pixel, ymin_pixel- ymax_pixel]) <1010:
        print("images smaller than 1010 are skipped, a better solution would be to enlarge them to be 1010")
        pass
    else:
        # Crop the GeoTIFF using the adjusted bounding box
        crop_geotiff(geotiff_path, output_path, [xmin_adj, xmax_adj, ymin_adj, ymax_adj])

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Crop GeoTIFF using a shapefile with a 10-pixel border.")
    parser.add_argument("--geotif", required=True, help="Path to the GeoTIFF file.")
    parser.add_argument("--shapefile", required=True, help="Path to the shapefile.")
    parser.add_argument("--output_geotif", required=True, help="Path to new the GeoTIFF file")

    args = parser.parse_args()


    main_crop_geotiff(args.geotif, args.shapefile, args.output_geotif)

