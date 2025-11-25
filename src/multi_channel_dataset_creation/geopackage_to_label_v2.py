import os
import time
import glob
import logging
from pathlib import Path
import geopandas as gpd
import rasterio
from rasterio.features import rasterize
import numpy as np
import pandas as pd
from scipy.ndimage import distance_transform_edt
from shapely.geometry import box
from typing import Tuple, Optional

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def process_single_raster_labels(
    gdf: gpd.GeoDataFrame,
    bounds: Tuple[float, float, float, float],  # (left, bottom, right, top)
    output_shape: Tuple[int, int],  # (height, width)
    out_transform: rasterio.transform.Affine,
    unknown_border_size: float,
    background_value: int,
    ignore_value: int,
    attr_column: Optional[str] = None,
    value_used_for_all_polygons: Optional[int] = None,
) -> np.ndarray:
    """
    Core logic for generating a label array for a single raster file.
    
    Args:
        gdf: GeoDataFrame containing polygons. If using value_used_for_all_polygons,
             no attribute column is needed. If using attr_column, that column must exist.
        bounds: Raster bounds (left, bottom, right, top)
        output_shape: Output array shape (height, width)
        out_transform: Affine transform for the raster
        unknown_border_size: Width of the border in ground units (e.g., meters)
        background_value: Value for areas not covered by polygons
        ignore_value: Value for border/unknown regions
        attr_column: Name of the attribute column to use for polygon values (optional)
        value_used_for_all_polygons: If provided, all polygons get this value (optional)
    
    Returns:
        np.ndarray: The generated label array.
    """
    # Validate inputs
    if value_used_for_all_polygons is not None and attr_column is not None:
        raise ValueError(
            "Cannot specify both 'value_used_for_all_polygons' and 'attr_column'. "
            "Use one or the other."
        )
    
    if value_used_for_all_polygons is None and attr_column is None:
        raise ValueError(
            "Must specify either 'value_used_for_all_polygons' or 'attr_column'."
        )
    
    if attr_column is not None and not isinstance(attr_column, str):
        raise TypeError(
            f"attr_column must be a string, got {type(attr_column).__name__}: {attr_column}"
        )
    
    out_shape = output_shape
    
    # Calculate mean_res from the transform
    x_res = abs(out_transform.a)
    y_res = abs(out_transform.e)
    mean_res = (x_res + y_res) / 2
    
    pixel_border_width = unknown_border_size / mean_res

    bbox = box(*bounds)
    gdf_subset = gdf[gdf.geometry.intersects(bbox)].copy()

    fill_value = background_value if background_value is not None else ignore_value

    if gdf_subset.empty:
        logging.info(f"No valid polygons intersect the raster extent. Creating an all-background label array.")
        label_array = np.full(out_shape, fill_value, dtype=np.uint8)
    else:
        # Sort by area descending to ensure smaller polygons are drawn over larger ones
        if "area" not in gdf_subset.columns:
            gdf_subset["area"] = gdf_subset.geometry.area
        gdf_subset = gdf_subset.sort_values(by="area", ascending=False)
        
        # Create shapes list based on mode
        if value_used_for_all_polygons is not None:
            # All polygons get the same value
            shapes = [(geom, value_used_for_all_polygons) for geom in gdf_subset.geometry]
        else:
            # Use attribute column for values
            if attr_column not in gdf_subset.columns:
                raise ValueError(
                    f"Attribute column '{attr_column}' not found in GeoDataFrame. "
                    f"Available columns: {list(gdf_subset.columns)}"
                )
            shapes = [(geom, value) for geom, value in zip(gdf_subset.geometry, gdf_subset[attr_column])]

        label_array = rasterize(
            shapes=shapes,
            out_shape=out_shape,
            transform=out_transform,
            fill=fill_value,
            dtype=np.uint8,
            all_touched=False,
        )

        # Apply boundary mask
        padded_labels = np.pad(label_array, 1, mode="edge")
        diff_n = padded_labels[1:-1, 1:-1] != padded_labels[:-2, 1:-1]
        diff_s = padded_labels[1:-1, 1:-1] != padded_labels[2:, 1:-1]
        diff_w = padded_labels[1:-1, 1:-1] != padded_labels[1:-1, :-2]
        diff_e = padded_labels[1:-1, 1:-1] != padded_labels[1:-1, 2:]

        boundary_mask = diff_n | diff_s | diff_w | diff_e
        dt_map = distance_transform_edt(np.invert(boundary_mask))
        # Divide by 2 because the distance transform is from the *center* of the pixel
        # to the boundary, and we want a border of width `pixel_border_width`.
        border_mask = dt_map < (pixel_border_width/2)
        label_array[border_mask] = ignore_value
    
    return label_array

def process_label_generation_main(
    geopackage: str,
    input_folder: str,
    output_folder: str,
    unknown_border_size: float = 0.1,
    attribute: str = None,
    background_value: int = 1,
    value_used_for_all_polygons: int = None,
    ignore_value: int = 0,
):
    """
    Handles I/O: loads GeoPackage, finds rasters, calls the core processing function,
    and writes the resulting label images to disk.
    
    Args:
        geopackage: Path to GeoPackage file or pre-loaded GeoDataFrame
        input_folder: Path to folder with input rasters or single raster file
        output_folder: Path to output folder or single output file
        unknown_border_size: Width of border in ground units (default 0.1)
        attribute: Attribute column name for polygon values (optional)
        background_value: Value for background areas (default 1)
        value_used_for_all_polygons: If provided, all polygons get this value (optional)
        ignore_value: Value for border regions (default 0)
    """
    # Validate configuration
    if value_used_for_all_polygons is not None and attribute is not None:
        raise ValueError(
            "Cannot specify both 'value_used_for_all_polygons' and 'attribute'. "
            "Use one or the other."
        )
    
    if value_used_for_all_polygons is None and attribute is None:
        raise ValueError(
            "Must specify either 'value_used_for_all_polygons' or 'attribute'."
        )
    
    if value_used_for_all_polygons is not None and background_value == value_used_for_all_polygons:
        raise ValueError(
            f"Invalid configuration: background_value ({background_value}) "
            f"cannot be equal to value_used_for_all_polygons ({value_used_for_all_polygons})."
        )

    logging.info(f"Starting label generation. Output folder: {output_folder}")

    # --- GeoPackage Loading ---
    if isinstance(geopackage, str):
        print("Loading geopackage...")
        reading_geopkg_start = time.time()
        gdf = gpd.read_file(geopackage)
        print(f"Reading geopackage took: {(time.time()-reading_geopkg_start)/60:.2f} minutes")
    else:
        print("Using preloaded geopackage")
        gdf = geopackage

    # --- Preprocessing based on mode ---
    attr_column = None
    
    if value_used_for_all_polygons is not None:
        # Simple mode: all polygons get the same value
        logging.info(f"All polygons will be assigned value {value_used_for_all_polygons}.")
        # No attribute column processing needed
        
    else:
        # Attribute mode: use specified column
        attr_column = attribute
        
        if attr_column not in gdf.columns:
            print("Available columns:", list(gdf.columns))
            raise ValueError(f"Attribute column '{attr_column}' not found in the GeoPackage.")

        original_count = len(gdf)
        gdf = gdf.dropna(subset=[attr_column])
        dropped_count = original_count - len(gdf)
        if dropped_count > 0:
            logging.info(f"Removed {dropped_count} polygons missing '{attr_column}' values.")

        try:
            # Ensure the attribute is a uint8 type for rasterize
            gdf[attr_column] = gdf[attr_column].astype(np.uint8)
        except ValueError as e:
            logging.error(f"Error converting '{attr_column}' to uint8. Ensure values are 0–255 integers.")
            raise e

    # Pre-calculate area for sorting (done once)
    if "area" not in gdf.columns:
        gdf["area"] = gdf.geometry.area
    
    # --- Raster File Discovery ---
    if Path(input_folder).suffix and Path(output_folder).suffix:
        # Single image file processing
        raster_files = [input_folder]
        output_path_base = None  # Signal that output_folder is a full file path
    else:
        # Batch processing
        output_path_base = Path(output_folder)
        output_path_base.mkdir(parents=True, exist_ok=True)

        raster_files = glob.glob(os.path.join(input_folder, "**", "*.tif"), recursive=True)
        raster_files.extend(glob.glob(os.path.join(input_folder, "**", "*.tiff"), recursive=True))

    if not raster_files:
        logging.info(f"No GeoTIFF files found in the input folder: {input_folder}")
        return gdf

    # --- Processing Loop ---
    for input_raster_path_str in raster_files:
        input_raster_path = Path(input_raster_path_str)
        
        if output_path_base is None:
            # Single file case
            output_label_path = output_folder
        else:
            # Batch case
            output_label_path = output_path_base / input_raster_path.name
            
        logging.info(f"Processing image: {input_raster_path.name}")

        with rasterio.open(input_raster_path) as src:
            
            # Extract necessary metadata from src
            bounds = src.bounds
            output_shape = (src.height, src.width)
            out_transform = src.transform
            
            # --- Call the I/O-free core function ---
            label_array = process_single_raster_labels(
                gdf=gdf,
                bounds=bounds,
                output_shape=output_shape,
                out_transform=out_transform,
                unknown_border_size=unknown_border_size,
                background_value=background_value,
                ignore_value=ignore_value,
                attr_column=attr_column,
                value_used_for_all_polygons=value_used_for_all_polygons,
            )
            
            # --- Write Output ---
            profile = src.profile

            # --- Remove conflicting metadata for single-band output ---
            # Remove keys that are invalid for single-band label images (like YCBCR, JPEG compression)
            for key in ['compress', 'photometric', 'interleave']:
                if key in profile:
                    del profile[key]

            # Update profile for the label file
            profile.update(dtype=rasterio.uint8, count=1, nodata=ignore_value)

            unique, counts = np.unique(label_array, return_counts=True)
            result = dict(zip(unique, counts))
            print("IDs present in label image and their counts:")
            print(result)

            with rasterio.open(output_label_path, "w", **profile) as dst:
                dst.write(label_array, 1)

            logging.info(f"Successfully created label file: {output_label_path}")
            
    # Return the loaded geopackage to avoid reloading
    return gdf 

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description=(
            "Converts polygons from a GeoPackage into GeoTIFF label images for semantic segmentation.\n"
            "Either specify --attribute to use polygon attributes, or --value_used_for_all_polygons "
            "to assign the same value to all polygons."
        ),
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument("--geopackage", type=str, required=True, help="Path to the input GeoPackage file.")
    parser.add_argument("--input_folder", type=str, required=True, help="Path to the folder containing input GeoTIFF images (RGB).")
    parser.add_argument("--output_folder", type=str, required=True, help="Path to the folder where output label GeoTIFFs will be saved.")
    parser.add_argument("--unknown_border_size", type=float, default=0.1, help="Width of the unknown border (value 0). Default: 0.1.")
    parser.add_argument("--attribute", type=str, help="Polygon attribute column name (e.g., ML_CATEGORY). Mutually exclusive with --value_used_for_all_polygons.")
    parser.add_argument("--background_value", type=int, default=1, help="Background raster value before filling polygons. Default: 1.")
    parser.add_argument("--ignore_value", type=int, default=0, help="Value for the border/unknown region. Default: 0.")
    parser.add_argument("--value_used_for_all_polygons", type=int, help="Value for all polygons (ignores attribute column). Mutually exclusive with --attribute.")

    args = parser.parse_args()

    process_label_generation_main(
        geopackage=args.geopackage,
        input_folder=args.input_folder,
        output_folder=args.output_folder,
        unknown_border_size=args.unknown_border_size,
        attribute=args.attribute,
        background_value=args.background_value,
        ignore_value=args.ignore_value,
        value_used_for_all_polygons=args.value_used_for_all_polygons,
    )
