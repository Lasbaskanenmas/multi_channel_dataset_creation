import os
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

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def process_label_generation(
    geopackage: str,
    input_folder: str,
    output_folder: str,
    unknown_border_size: float = 0.1,
    attribute: str = None,
    background_value: int = 1,
    value_used_for_all_polygons: int = 2,
    ignore_value: int = 0,
):
    if background_value == value_used_for_all_polygons:
        raise ValueError(
            f"Invalid configuration: background_value ({background_value}) "
            f"cannot be equal to value_used_for_all_polygons ({value_used_for_all_polygons})."
        )

    use_constant_class = attribute is None
    class_attribute_name = attribute

    output_path = Path(output_folder)
    output_path.mkdir(parents=True, exist_ok=True)

    logging.info(f"Starting label generation. Output folder: {output_path}")
    logging.info(f"Loading GeoPackage: {geopackage}")
    gdf = gpd.read_file(geopackage)

    if use_constant_class:
        logging.info(f"No attribute provided. All polygons will be treated as class {value_used_for_all_polygons}.")
        attr_column = "label_class_constant"
        gdf[attr_column] = np.uint8(value_used_for_all_polygons)
    else:
        attr_column = class_attribute_name
        if attr_column not in gdf.columns:
            print("Available columns:", list(gdf.columns))
            raise ValueError(f"Attribute column '{attr_column}' not found in the GeoPackage.")

        original_count = len(gdf)
        gdf = gdf.dropna(subset=[attr_column])
        dropped_count = original_count - len(gdf)
        if dropped_count > 0:
            logging.info(f"Removed {dropped_count} polygons missing '{attr_column}' values.")

        try:
            gdf[attr_column] = gdf[attr_column].astype(np.uint8)
        except ValueError as e:
            logging.error(f"Error converting '{attr_column}' to uint8. Ensure values are 0–255 integers.")
            raise e

    gdf["area"] = gdf.geometry.area

    raster_files = glob.glob(os.path.join(input_folder, "**", "*.tif"), recursive=True)
    raster_files.extend(glob.glob(os.path.join(input_folder, "**", "*.tiff"), recursive=True))

    if not raster_files:
        logging.info(f"No GeoTIFF files found in the input folder: {input_folder}")
        return

    for input_raster_path in raster_files:
        input_raster_path = Path(input_raster_path)
        output_label_path = output_path / input_raster_path.name
        logging.info(f"Processing image: {input_raster_path.name}")

        with rasterio.open(input_raster_path) as src:
            out_shape = (src.height, src.width)
            out_transform = src.transform
            out_crs = src.crs

            x_res = abs(src.transform.a)
            y_res = abs(src.transform.e)
            mean_res = (x_res + y_res) / 2
            pixel_border_width = unknown_border_size / mean_res

            bbox = box(*src.bounds)
            gdf_subset = gdf[gdf.geometry.intersects(bbox)].copy()

            fill_value = background_value if background_value is not None else ignore_value

            if gdf_subset.empty:
                logging.info(f"No valid polygons intersect {input_raster_path.name}. Creating an all-background label file.")
                label_array = np.full(out_shape, fill_value, dtype=np.uint8)
            else:
                gdf_subset = gdf_subset.sort_values(by="area", ascending=False)
                shapes = [(geom, value) for geom, value in zip(gdf_subset.geometry, gdf_subset[attr_column])]

                label_array = rasterize(
                    shapes=shapes,
                    out_shape=out_shape,
                    transform=out_transform,
                    fill=fill_value,
                    dtype=np.uint8,
                    all_touched=False,
                )

                padded_labels = np.pad(label_array, 1, mode="edge")
                diff_n = padded_labels[1:-1, 1:-1] != padded_labels[:-2, 1:-1]
                diff_s = padded_labels[1:-1, 1:-1] != padded_labels[2:, 1:-1]
                diff_w = padded_labels[1:-1, 1:-1] != padded_labels[1:-1, :-2]
                diff_e = padded_labels[1:-1, 1:-1] != padded_labels[1:-1, 2:]

                boundary_mask = diff_n | diff_s | diff_w | diff_e
                dt_map = distance_transform_edt(np.invert(boundary_mask))
                border_mask = dt_map < (pixel_border_width/2)
                label_array[border_mask] = ignore_value

            profile = src.profile
            profile.update(dtype=rasterio.uint8, count=1, nodata=ignore_value)

            unique, counts = np.unique(label_array, return_counts=True)
            result = dict(zip(unique, counts))
            print("IDs present in label image and their counts:")
            print(result)

            with rasterio.open(output_label_path, "w", **profile) as dst:
                dst.write(label_array, 1)

            logging.info(f"Successfully created label file: {output_label_path.name}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description=(
            "Converts polygons from a GeoPackage into GeoTIFF label images for semantic segmentation.\n"
            "If no --attribute VALUE is given, all polygons get the same value."
        ),
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument("--geopackage", type=str, required=True, help="Path to the input GeoPackage file.")
    parser.add_argument("--input_folder", type=str, required=True, help="Path to the folder containing input GeoTIFF images (RGB).")
    parser.add_argument("--output_folder", type=str, required=True, help="Path to the folder where output label GeoTIFFs will be saved.")
    parser.add_argument("--unknown_border_size", type=float, default=0.1, help="Width of the unknown border (value 0). Default: 0.1.")
    parser.add_argument("--attribute", type=str, help="Polygon attribute column name (e.g., ML_CATEGORY).")
    parser.add_argument("--background_value", type=int, default=1, help="Background raster value before filling polygons. Default: 1.")
    parser.add_argument("--ignore_value", type=int, default=0, help="Value for the border/unknown region. Default: 0.")
    parser.add_argument("--value_used_for_all_polygons", type=int, default=2, help="Value for all polygons if no attribute is provided. Default: 2.")

    args = parser.parse_args()

    process_label_generation(
        geopackage=args.geopackage,
        input_folder=args.input_folder,
        output_folder=args.output_folder,
        unknown_border_size=args.unknown_border_size,
        attribute=args.attribute,
        background_value=args.background_value,
        ignore_value=args.ignore_value,
        value_used_for_all_polygons=args.value_used_for_all_polygons,
    )
