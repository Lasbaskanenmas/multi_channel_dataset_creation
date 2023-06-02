import os
import sys
import inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

sys.path.insert(0, currentdir)

arcpy_installed= False
try:
    import arcpy
    arcpy_installed = True
except:
    print("#########################################################################################################")
    print("NO arcpy INSTALLED! , This is OK if you dont want to create rasters from polyogns (e.g label or house masks/rasters), otherwise you should use a conda environment that is based on the one you get with a windows arcpy installation")
    print("labels must be created on a windows machine")
    print("#########################################################################################################")


if arcpy_installed:
    import create_label_images
    import create_house_images
    import update_arcgis_feature_class
else:
    print("with no arcpy installed the program can not crate raster data (e.g labels or houses) from polygons")

import create_patches
import create_txt_files
import delete_images_with_only_zeroes
import move_data_to_separate_folders
import argparse
import time



def main(args):
    create_dataset_start_time = time.time()
    if not "move_data_to_separate_folders" in args.skip:
        print("#######################################")
        print("move_data_to_separate_folders")
        print("#######################################")
        #going from folder/a_name_DSM.tif , folder/a_name_OrtoCIR.tif ... to  DSM/a_name.tif , OrtoCIR/a_name.tif ..
        move_data_to_separate_folders.main(config=args.config)
    if not "update_arcgis_feature_class" in args.skip:
        print("#######################################")
        print("update the 'merged_labels' feature class to include the newest data")
        print("#######################################")
        update_arcgis_feature_class.main(config=args.config)

    if not "create_labels" in args.skip:
        print("#######################################")
        print("create_labels")
        print("#######################################")
        #convert the GIS database to label images of same shape as the 'lod-images'
        #if there are no label data for the area covered by the image, we don create any label
        create_label_images.main(config=args.config)

    if not "create_houses" in args.skip:
        print("#######################################")
        print("create_houses")
        print("#######################################")
        #convert the GIS database to images of same shape as the 'lod-images'
        #if there are no house polygons for the area covered by the image, we still create black images
        create_house_images.main(config=args.config)


    if not "create_patches" in args.skip:
        print("#######################################")
        print("create_patches")
        print("#######################################")
        #split the data and label-images up into smaler pathces e.g 1000x1000
        create_patches.main(config=args.config)
    if not "remove_empty_label_images" in args.skip:
        print("#######################################")
        print("remove_empty_label_images")
        print("#######################################")
        #remove all images without valid labels (label image must exist AND ,must contain pixels with labels !=0)
        delete_images_with_only_zeroes.main(config=args.config)
    if not "create_text_files" in args.skip:
        print("#######################################")
        print("create_text_files")
        print("#######################################")
        #divide the dataset into trainingset and validationset and save the split as all.txt, train.txt and valid.txt
        create_txt_files.main(config=args.config)

    create_dataset_end_time = time.time()
    print("################################################################################")
    print("create_dataset took: "+str(create_dataset_end_time-create_dataset_start_time ))
    print("################################################################################")
    print()
    print()

 


if __name__ == "__main__":
    usage_example= "python create_dataset.py --config --skip move_data_to_separate_folders update_arcgis_feature_class create_labels create_houses create_patches remove_empty_label_images create_text_files"
    # Initialize parser
    parser = argparse.ArgumentParser(
        epilog=usage_example,
        formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("--config",help ="path to config.ini file e.g ..\..\configs\template_create_dataset.ini",required=True)

    parser.add_argument("--skip",help ="path to folder containing images to be splitted",nargs ='+',default =[],required=False)

    args = parser.parse_args()

    main(args)