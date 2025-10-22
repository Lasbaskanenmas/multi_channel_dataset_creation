import argparse
import os
import glob
import logging
from pathlib import Path

import geopandas as gpd
import rasterio
from rasterio.features import rasterize
import numpy as np
import pandas as pd # Used for efficient NaN handling
from scipy.ndimage import distance_transform_edt
from shapely.geometry import box

# --- Configuration and Setup ---

# Set up basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def process_label_generation():
    """
    Main function to parse arguments and orchestrate the label generation process.
    """
    parser = argparse.ArgumentParser(
        description="Converts polygons from a GeoPackage into GeoTIFF label images for semantic segmentation.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("--geopackage", type=str, required=True, help="Path to the input GeoPackage file.")
    parser.add_argument("--input_folder", type=str, required=True, help="Path to the folder containing input GeoTIFF images (RGB).")
    parser.add_argument("--output_folder", type=str, required=True, help="Path to the folder where output label GeoTIFFs will be saved.")
    parser.add_argument("--unknown_boarder_size", type=float, default=0.1, help="Width of the 'unknown' border (value 0) between different class areas, in map units (e.g., meters). Default is 0.1.")
    parser.add_argument("--atribute", type=str, required=True, help="The polygon attribute field (column name) used for the class value (e.g., ML_CATEGORY). Must contain integers 0-255.")

    args = parser.parse_args()

    # Create output directory if it doesn't exist
    output_path = Path(args.output_folder)
    output_path.mkdir(parents=True, exist_ok=True)
    
    logging.info(f"Starting label generation. Output folder: {output_path}")

    # --- Load and Prepare Vector Data (Will fail hard on GeoPackage errors) ---
    logging.info(f"Loading GeoPackage: {args.geopackage}")
    gdf = gpd.read_file(args.geopackage)

    # Check for attribute existence
    if args.atribute not in gdf.columns:
        raise ValueError(f"Attribute column '{args.atribute}' not found in the GeoPackage.")

    # 1. Handle NaN/missing values in the attribute column
    original_count = len(gdf)
    
    # Drop rows where the class attribute is missing (NaN)
    missing_mask = pd.isna(gdf[args.atribute])
    gdf = gdf[~missing_mask]
    
    dropped_count = original_count - len(gdf)
    if dropped_count > 0:
        logging.info(f"Removed {dropped_count} polygons because the attribute '{args.atribute}' was missing (NaN).")

    # 2. Ensure attribute column is numeric (and suitable for uint8, 0-255)
    # This will raise a ValueError if values are outside the 0-255 range or are non-numeric strings
    gdf[args.atribute] = gdf[args.atribute].astype(np.uint8)

    # Calculate area for priority sorting
    gdf['area'] = gdf.geometry.area
    
    # --- Process Rasters ---
    raster_files = glob.glob(os.path.join(args.input_folder, '**', '*.tif'), recursive=True)
    raster_files.extend(glob.glob(os.path.join(args.input_folder, '**', '*.tiff'), recursive=True))

    if not raster_files:
        logging.info(f"No GeoTIFF files found in the input folder: {args.input_folder}")
        return

    for input_raster_path in raster_files:
        input_raster_path = Path(input_raster_path)
        output_label_path = output_path / input_raster_path.name
        logging.info(f"Processing image: {input_raster_path.name}")

        # Opening the raster file (will raise RasterioIOError on failure)
        with rasterio.open(input_raster_path) as src:
            # Read raster metadata
            out_shape = (src.height, src.width)
            out_transform = src.transform
            out_crs = src.crs
            
            # Calculate pixel resolution (assuming square pixels for simplicity)
            x_res = abs(src.transform.a)
            y_res = abs(src.transform.e)
            mean_res = (x_res + y_res) / 2
            
            # Convert border size from map units to pixels
            pixel_border_width = args.unknown_boarder_size / mean_res
            
            # Get the raster bounds in the raster's CRS
            bbox = box(*src.bounds)
            
            # Filter polygons to only those intersecting the current raster extent
            gdf_subset = gdf[gdf.geometry.intersects(bbox)].copy()

            if gdf_subset.empty:
                logging.info(f"No valid polygons intersect {input_raster_path.name}. Creating an all-zero label file.")
                label_array = np.zeros(out_shape, dtype=np.uint8)
            else:
                # 1. Overlap Priority: Sort by area ascending. Smallest polygons processed last overwrite larger ones.
                gdf_subset = gdf_subset.sort_values(by='area', ascending=True)

                # Prepare shapes/value tuples for rasterization
                shapes = [
                    (geom, value) 
                    for geom, value in zip(gdf_subset.geometry, gdf_subset[args.atribute])
                ]

                # 2. Initial Rasterization: Creates the base label image (background=0, priority handled)
                label_array = rasterize(
                    shapes=shapes,
                    out_shape=out_shape,
                    transform=out_transform,
                    fill=0,
                    dtype=np.uint8,
                    all_touched=False # Full pixel coverage required
                )

                # 3. Create Unknown Border (Value 0)

                # 3a. Identify Boundaries (where a pixel differs from any neighbor)
                padded_labels = np.pad(label_array, 1, mode='edge')
                
                diff_n = padded_labels[1:-1, 1:-1] != padded_labels[:-2, 1:-1]
                diff_s = padded_labels[1:-1, 1:-1] != padded_labels[2:, 1:-1]
                diff_w = padded_labels[1:-1, 1:-1] != padded_labels[1:-1, :-2]
                diff_e = padded_labels[1:-1, 1:-1] != padded_labels[1:-1, 2:]

                # The boundary mask is True wherever a pixel differs from any neighbor
                boundary_mask = diff_n | diff_s | diff_w | diff_e
                
                # 3b. Distance Transform: Calculate the distance from the nearest boundary pixel.
                # dt_map[i, j] = distance (in pixels) to the nearest TRUE (boundary) pixel
                dt_map = distance_transform_edt(np.invert(boundary_mask))
                
                # 3c. Apply Border Mask: If the distance is less than the required pixel width, set to 0.
                border_mask = dt_map < pixel_border_width 

                # Apply the border mask to the label array
                label_array[border_mask] = 0

            # 4. Write Output GeoTIFF
            profile = src.profile
            profile.update(
                dtype=rasterio.uint8,
                count=1,
                nodata=0 # Use 0 as the nodata value (also the unknown/background class)
            )
            #sanity check what labels are presetn and how many pixels of each
            # Get unique values and their counts
            unique, counts = np.unique(label_array, return_counts=True)

            # Create dictionary
            result = dict(zip(unique, counts))
            print("ids presetn in the label image together with their counts")
            print(result)  # {1: 1, 2: 2, 3: 3, 4: 4}


            with rasterio.open(output_label_path, 'w', **profile) as dst:
                dst.write(label_array, 1)

            logging.info(f"Successfully created label file: {output_label_path.name}")

if __name__ == "__main__":
    process_label_generation()
