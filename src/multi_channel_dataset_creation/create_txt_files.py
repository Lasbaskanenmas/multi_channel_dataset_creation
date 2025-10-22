import create_all_and_valid_txt
import create_train_txt
import configparser
import argparse
import time
import pathlib
import json


def main(config):
    ini_parser = configparser.ConfigParser()
    ini_parser.read(config)
    section = "SETTINGS"
    all_txt_filename =ini_parser[section]["all_txt_filename"]
    valid_txt_filename =ini_parser[section]["valid_txt_filename"]

    #this can safely be set to False since it only is a speed optimization
    images_must_be_crops_of_these_images_path = ini_parser[section].get("images_must_be_crops_of_these_images_path")

    data_path = ini_parser[section]["data_folder"]
    splitted_data_parent_folder =pathlib.Path(ini_parser[section]["splitted_data_parent_folder"])


    #we base the list of filenames on the filenames in the splitted version of one of the datasources
    path_to_images = (splitted_data_parent_folder / json.loads(ini_parser[section]["datatypes"])[0] )

    datatype =ini_parser[section]["datatype"]


    other_data_folders = [(splitted_data_parent_folder / data_folder) for data_folder in json.loads(ini_parser[section]["datatypes"])]
    print(other_data_folders)



    nr_of_images_between_validation_samples =int(ini_parser[section]["nr_of_images_between_validation_samples"])
    print("creating all.txt and valid.txt based on the files in this folder:")
    print(path_to_images)


    create_all_and_valid_txt.create_all_and_valid(all_txt_filename =all_txt_filename,valid_txt_filename=valid_txt_filename,path_to_training_images=path_to_images,datatype=datatype,nr_of_images_between_validation_samples=nr_of_images_between_validation_samples,other_data_folders=other_data_folders,label_folder = pathlib.Path(ini_parser[section]["splitted_mask_folder"]),remove_overlap =(ini_parser[section]["remove_images_from_all_that_overlap_with_validationset"] in ["True","true"]) ,remove_images_without_label =(ini_parser[section]["remove_images_without_label"] in ["True","true"]),use_fixed_validation_set =(ini_parser[section]["use_fixed_validation_set"] in ["True","true"]),images_must_be_crops_of_these_images_path=images_must_be_crops_of_these_images_path,text_file_listing_images_to_consider=None)
    print("creating train.txt by removing all images in valid.txt from all.txt")

    create_train_txt.create_train_txt(path_to_all_txt=all_txt_filename,path_to_valid_txt=valid_txt_filename,path_to_all_images=path_to_images,path_to_valid_images=path_to_images,name_prefix="")
    



if __name__ == "__main__":
    """
    Creates patches of a given size for input data(e.g images) and labels-images
    """

    usage_example="example usage: \n "+r"python create_txt_files.py --config path\to\file.ini"
    # Initialize parser
    parser = argparse.ArgumentParser(
        epilog=usage_example,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("-c", "--config", help="one or more paths to config file",nargs ='+',required=True)
    args = parser.parse_args()
    main(args.config)



