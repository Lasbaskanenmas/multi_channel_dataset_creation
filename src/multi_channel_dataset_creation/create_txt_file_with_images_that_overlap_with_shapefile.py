from osgeo import gdal
import argparse
import sys
import os
import overlap
import pathlib


def create_txt_file_with_files_overlapping_with_shp_file(shape_file,folder,output_txt,images_must_be_crops_of_these_images_path):
    print("Listing all .tif files...")
    tiff_files = [str(pathlib.Path(folder)/f) for f in os.listdir(folder) if f.endswith('.tif')]
    if images_must_be_crops_of_these_images_path:
        print("filtering away files that not are crops of the files listed in 'images_must_be_crops_of_these_images_path'")
        with open(images_must_be_crops_of_these_images_path, 'r') as file:
            # Read all lines into a list, stripping any trailing newline characters
            large_tiff_files = [line.strip() for line in file]
            #remove the .tif in order to get the part of the filename that also occurs in the crop
            large_tiff_files =[large_tiff_file.strip(".tif").split("/")[-1] for large_tiff_file in large_tiff_files]

            tiff_files_that_are_crops_of_set_of_larger_tiff_files = []
            for tiff_file in tiff_files:
                #e.g: remove the "_7000_2880.tif" part of "O2021_82_24_1_0020_00004289_7000_2880.tif"
                search_string = "_".join(tiff_file.split("_")[0:-2]).split("/")[-1]
                #input("search_string:"+str(search_string))
                #input("large_tiff_files[0]:"+str(large_tiff_files[0]))
                if search_string in large_tiff_files:
                    tiff_files_that_are_crops_of_set_of_larger_tiff_files.append(tiff_file)
        tiff_files = tiff_files_that_are_crops_of_set_of_larger_tiff_files




    print("filtering away geotiff files that dont overlap with .shp file...")
    nr_of_files = len(tiff_files)
    overlapping_tif_files = []
    checked_files=0
    for filepath in tiff_files:
        if overlap.shp_geotif_overlap(shp_path=shape_file,tiff_path=filepath):
             overlapping_tif_files.append(filepath.split("/")[-1])
        checked_files+=1
        print(f"\rPercent ready: {100*(checked_files/nr_of_files)}%", end="")
    print("saving the filenames of all overlapping geotiffs to : "+str(output_txt)+ " ...")
    pathlib.Path(pathlib.Path(output_txt).parent).mkdir(parents=True, exist_ok=True)
    with open(output_txt, 'w') as f:
        f.write('\n'.join(overlapping_tif_files))
    print("printed the filenames to the file : " + output_txt)








if __name__ == "__main__":
    usage_example= "python create_txt_file_with_images_that_overlap_with_shapefile.py --shapefile path/to/file.shp --folder path/to/images/ --output_txt path/to/filenames.txt"
    # Initialize parser
    parser = argparse.ArgumentParser(
        epilog=usage_example,
        formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("--shapefile", required=True, help="Path to the shapefile.")
    parser.add_argument('--folder', help='Path to the root folder of the TIFF files.')
    parser.add_argument('--output_txt', help='Path to the txt were we should save all filenames')
    parser.add_argument('--images_must_be_crops_of_these_images_path',default = None, help='Path to a .txt file listing all unsplitted images that overlap with the .shp file. only images that are crops of these images can overlap with the .shp file')
    args = parser.parse_args()


    #### RUN ####
    create_txt_file_with_files_overlapping_with_shp_file(shape_file=args.shapefile,folder=args.folder,output_txt=args.output_txt,images_must_be_crops_of_these_images_path=args.images_must_be_crops_of_these_images_path)
