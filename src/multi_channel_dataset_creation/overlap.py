#when splitting a trainingset into train and validation partitions it is important to be able to verify that the images in the two sets dont overlap
#this module provide this functionality

from osgeo import gdal
import argparse

def geotiff_overlap(file1_path, file2_path):
    try:
        # Open the first GeoTIFF file
        dataset1 = gdal.Open(file1_path, gdal.GA_ReadOnly)

        # Open the second GeoTIFF file
        dataset2 = gdal.Open(file2_path, gdal.GA_ReadOnly)

        # Get the extent (bounding box) for the first dataset
        geo_transform1 = dataset1.GetGeoTransform()
        min_x1 = geo_transform1[0]
        max_x1 = min_x1 + geo_transform1[1] * dataset1.RasterXSize
        min_y1 = geo_transform1[3] + geo_transform1[5] * dataset1.RasterYSize
        max_y1 = geo_transform1[3]

        # Get the extent (bounding box) for the second dataset
        geo_transform2 = dataset2.GetGeoTransform()
        min_x2 = geo_transform2[0]
        max_x2 = min_x2 + geo_transform2[1] * dataset2.RasterXSize
        min_y2 = geo_transform2[3] + geo_transform2[5] * dataset2.RasterYSize
        max_y2 = geo_transform2[3]

        # Check if the extents overlap
        overlap = not (max_x1 < min_x2 or max_x2 < min_x1 or max_y1 < min_y2 or max_y2 < min_y1)

        return overlap

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return False


if __name__ == "__main__":
    usage_example= "python overlap.py --image_1 images/a_geotif.image.tif --image_2 images/another_geotif.image.tif"
    # Initialize parser
    parser = argparse.ArgumentParser(
        epilog=usage_example,
        formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("--image_1",help ="path to a geotif image ",required=True)
    parser.add_argument("--image_2",help ="path to a geotif image ",required=True)
    args = parser.parse_args()


    #### RUN ####
    if geotiff_overlap(file1_path=args.image_1, file2_path=args.image_2):
        print("The two GeoTIFF files overlap.")
    else:
        print("The two GeoTIFF files do not overlap.")