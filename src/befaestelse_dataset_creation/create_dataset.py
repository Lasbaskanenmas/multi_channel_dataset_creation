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
    print("NO ARCPY INSTALLED! , This is OK if you dont want to create rasters from polyogns (e.g labels or houses)")


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



def main(args):
    if not "move_data_to_separate_folders" in args.skip:
        print("move_data_to_separate_folders")
        #going from folder/a_name_DSM.tif , folder/a_name_OrtoCIR.tif ... to  DSM/a_name.tif , OrtoCIR/a_name.tif ..
        move_data_to_separate_folders.main(config=args.config)
    if not "update_arcgis_feature_class" in args.skip:
        print("update the 'merged_labels' feature class to include the newest data")
        update_arcgis_feature_class.main(config=args.config)

    if not "create_labels" in args.skip:
        print("create_labels")
        #convert the GIS database to label images of same shape as the 'lod-images'
        #if there are no label data for the area covered by the image, we don create any label
        create_label_images.main(config=args.config)

    if not "create_houses" in args.skip:
        print("create_houses")
        #convert the GIS database to images of same shape as the 'lod-images'
        #if there are no house polygons for the area covered by the image, we still create black images
        create_house_images.main(config=args.config)


    if not "create_patches" in args.skip:
        print("create_patches")
        #split the data and label-images up into smaler pathces e.g 1000x1000
        create_patches.main(config=args.config)
    if not "remove_empty_label_images" in args.skip:
        print("remove_empty_label_images")
        #remove all images without valid labels (label image must exist AND ,must contain pixels with labels !=0)
        delete_images_with_only_zeroes.main(config=args.config)
    if not "create_text_files" in args.skip:
        print("create_text_files")
        #divide the dataset into trainingset and validationset and save the split as all.txt, train.txt and valid.txt
        create_txt_files.main(config=args.config)
 


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