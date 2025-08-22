#!/usr/bin/env python3
"""
Extract data from VRT files for each tile in a shapefile and save as GeoTIFF files.
"""

import argparse
import os
import sys
from pathlib import Path
import geopandas as gpd
import rasterio
from rasterio.warp import calculate_default_transform, reproject, Resampling
from rasterio.windows import from_bounds
from rasterio.mask import mask
import numpy as np
from tqdm import tqdm


def extract_tile_data(vrt_path, tile_geometry, tile_name, output_folder, resolution):
    """
    Extract data from VRT for a single tile and save as GeoTIFF.
    
    Args:
        vrt_path (str): Path to the VRT file
        tile_geometry: Shapely geometry of the tile
        tile_name (str): Name for the output file (without extension)
        output_folder (str): Output directory path
        resolution (float): Target resolution in meters per pixel
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        with rasterio.open(vrt_path) as src:
            # Get tile bounds
            minx, miny, maxx, maxy = tile_geometry.bounds
            
            # Calculate output dimensions based on resolution
            width = int((maxx - minx) / resolution)
            height = int((maxy - miny) / resolution)
            
            # Create output transform
            transform = rasterio.transform.from_bounds(minx, miny, maxx, maxy, width, height)
            
            # Create output profile
            profile = src.profile.copy()
            profile.update({
                'height': height,
                'width': width,
                'transform': transform,
                'crs': src.crs
            })
            
            # Output file path
            output_path = os.path.join(output_folder, f"{tile_name}.tiff")
            
            # Read and resample data
            with rasterio.open(output_path, 'w', **profile) as dst:
                for band_idx in range(1, src.count + 1):
                    # Read data from source
                    reproject(
                        source=rasterio.band(src, band_idx),
                        destination=rasterio.band(dst, band_idx),
                        src_transform=src.transform,
                        src_crs=src.crs,
                        dst_transform=transform,
                        dst_crs=src.crs,
                        resampling=Resampling.bilinear
                    )
        
        return True
    
    except Exception as e:
        print(f"\nError processing tile {tile_name}: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Extract data from VRT files for each tile in a shapefile"
    )
    parser.add_argument("--shape", required=True, help="Path to shapefile with tiles")
    parser.add_argument("--vrt", required=True, help="Path to VRT file with data")
    parser.add_argument("--output_folder", required=True, help="Output folder for GeoTIFF files")
    parser.add_argument("--resolution", type=float, default=0.1, 
                       help="Resolution in meters per pixel (default: 0.1)")
    
    args = parser.parse_args()
    
    # Validate inputs
    if not os.path.exists(args.shape):
        print(f"Error: Shapefile {args.shape} does not exist")
        sys.exit(1)
    
    if not os.path.exists(args.vrt):
        print(f"Error: VRT file {args.vrt} does not exist")
        sys.exit(1)
    
    # Create output folder if it doesn't exist
    Path(args.output_folder).mkdir(parents=True, exist_ok=True)
    
    print(f"Loading shapefile: {args.shape}")
    try:
        # Read shapefile
        gdf = gpd.read_file(args.shape)
        print(f"Found {len(gdf)} tiles in shapefile")
    except Exception as e:
        print(f"Error reading shapefile: {e}")
        sys.exit(1)
    
    # Check if VRT is readable
    try:
        with rasterio.open(args.vrt) as src:
            print(f"VRT file has {src.count} bands, CRS: {src.crs}")
    except Exception as e:
        print(f"Error reading VRT file: {e}")
        sys.exit(1)
    
    print(f"Processing tiles with resolution: {args.resolution} m/pixel")
    print(f"Output folder: {args.output_folder}")
    
    # Process each tile
    successful = 0
    total_tiles = len(gdf)
    
    for idx, row in gdf.iterrows():
        # Get tile name - try common column names
        tile_name = None
        for col in ['location', 'name', 'id', 'tile_name', 'filename']:
            if col in gdf.columns:
                tile_name = str(row[col])
                # Remove file extension if present
                tile_name = os.path.splitext(tile_name)[0]
                break
        
        if tile_name is None:
            tile_name = f"tile_{idx:06d}"
        
        # Extract data for this tile
        if extract_tile_data(args.vrt, row.geometry, tile_name, args.output_folder, args.resolution):
            successful += 1
        
        # Print progress on same line
        progress = (idx + 1) / total_tiles * 100
        print(f"\rProgress: {progress:.1f}% ({idx + 1}/{total_tiles}) - {successful} successful", end="", flush=True)
    
    print(f"\n\nCompleted! Successfully processed {successful}/{total_tiles} tiles")
    
    if successful < total_tiles:
        print(f"Failed to process {total_tiles - successful} tiles")


if __name__ == "__main__":
    main()
