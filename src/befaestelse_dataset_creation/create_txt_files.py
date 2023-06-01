import create_all_and_valid_txt
import create_train_txt
import configparser
import argparse

import pathlib
import json


def main(config):
    ini_parser = configparser.ConfigParser()
    ini_parser.read(config)
    section = "SETTINGS"
    all_txt_filename =ini_parser[section]["all_txt_filename"]
    valid_txt_filename =ini_parser[section]["valid_txt_filename"]
    data_path = ini_parser[section]["data_folder"]
    if "splitted_mask_folder" in ini_parser[section]:
        #if the dataset have labels we only want to list the files that exists in the label folder
        path_to_images =ini_parser[section]["splitted_mask_folder"]
    else:
        #if ther is no labels we base the list of filenames on the filenames in the splitted version of one of the datasources
        path_to_images = ((pathlib.Path(data_path)/ "splitted") / json.loads(ini_parser[section]["datatypes"])[0] )

    datatype =ini_parser[section]["datatype"]


    other_data_folders = [((pathlib.Path(data_path)/ "splitted") / data_folder) for data_folder in json.loads(ini_parser[section]["datatypes"])]
    print(other_data_folders)


    nr_of_images_between_validation_samples =int(ini_parser[section]["nr_of_images_between_validation_samples"])
    print("creating all.txt and valid.txt based on the files in this folder:")
    print(path_to_images)


    create_all_and_valid_txt.create_all_and_valid(all_txt_filename =all_txt_filename,valid_txt_filename=valid_txt_filename,path_to_training_images=path_to_images,datatype=datatype,nr_of_images_between_validation_samples=nr_of_images_between_validation_samples,other_data_folders=other_data_folders)
    print("creating train.txt")
    create_train_txt.create_train_txt(path_to_all_txt=all_txt_filename,path_to_valid_txt=valid_txt_filename,name_prefix="")



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



