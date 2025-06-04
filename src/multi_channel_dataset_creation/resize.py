import argparse
import os
import glob
import rasterio
from rasterio.enums import Resampling
from rasterio.transform import Affine

def resample_geotiff(input_path, output_path, resolution):
    with rasterio.open(input_path) as src:
        original_res = src.res  # (xres, yres)
        original_size = (src.width, src.height)

        print(f"Original resolution: {original_res[0]:.4f} x {original_res[1]:.4f} meters/pixel")
        print(f"Original size: {original_size[0]} x {original_size[1]} pixels")

        scale_x = original_res[0] / resolution
        scale_y = original_res[1] / resolution

        #if scale_x != 1.0:input(scale_x)

        new_width = int(src.width * scale_x)
        new_height = int(src.height * scale_y)

        new_transform = Affine(
            resolution, 0.0, src.bounds.left,
            0.0, -resolution, src.bounds.top
        )

        kwargs = src.meta.copy()
        kwargs.update({
            'height': new_height,
            'width': new_width,
            'transform': new_transform
        })

        with rasterio.open(output_path, 'w', **kwargs) as dst:
            for i in range(1, src.count + 1):
                data = src.read(i, out_shape=(new_height, new_width), resampling=Resampling.bilinear)
                dst.write(data, i)

        print(f"Resampled resolution: {resolution:.4f} x {resolution:.4f} meters/pixel")
        print(f"Resampled size: {new_width} x {new_height} pixels\n")

def main():
    parser = argparse.ArgumentParser(description="Resample GeoTIFFs to a specified resolution.")
    parser.add_argument('--folder', required=True, help='Folder containing input GeoTIFFs')
    parser.add_argument('--output_folder', required=True, help='Folder to save resampled GeoTIFFs')
    parser.add_argument('--resolution', type=float, default=0.16, help='Target resolution in meters per pixel (default: 0.16)')

    args = parser.parse_args()

    os.makedirs(args.output_folder, exist_ok=True)

    tiffs = glob.glob(os.path.join(args.folder, '*.tif')) + glob.glob(os.path.join(args.folder, '*.tiff'))
    if not tiffs:
        print("No GeoTIFFs found in the input folder.")
        return

    for tif in tiffs:
        filename = os.path.basename(tif)
        output_path = os.path.join(args.output_folder, filename)
        print(f"Processing: {filename}")
        resample_geotiff(tif, output_path, args.resolution)

if __name__ == '__main__':
    main()
