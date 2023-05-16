import split
from pathlib import Path
import configparser
import argparse
import json
def main(config):
    ini_parser = configparser.ConfigParser()
    ini_parser.read(config)
    section = "SETTINGS"






    tile_size_y = ini_parser[section]["tile_size_y"]
    tile_size_x = ini_parser[section]["tile_size_x"]

    ignore_id = int(ini_parser[section]["ignore_id"])


    if "mask_folder" in ini_parser[section]:
        print("dataset includes masks that should be splitted")
        large_masks_folder = ini_parser[section]["mask_folder"]
        splitted_mask_folder = ini_parser[section]["splitted_mask_folder"]
        print("splitting the labels in "+str(large_masks_folder)+"and string them in folder :"+str(splitted_mask_folder))
        Path(splitted_mask_folder).mkdir(parents=True, exist_ok=True)
        splitf = split.Split()
        splitf.splitdst(in_path=large_masks_folder, out_path=splitted_mask_folder, tile_size_x=int(ini_parser[section]["tile_size_x"]), tile_size_y=int(ini_parser[section]["tile_size_y"]),kun_ok_pic=False,ignore_id=ignore_id,cutdatatype="mask_NaN")
    else:
        print("dataset does NOT include any masks")


    datatypes =json.loads(ini_parser[section]["datatypes"])
    data_folders_parent_directory =Path(ini_parser[section]["folder_containing_all_image_types"]).parent
    data_folders = [data_folders_parent_directory / datatype for datatype in datatypes]
    for data_folder in data_folders:
        splitted_folder = data_folder.with_name("splitted_"+data_folder.name)
        Path(splitted_folder).mkdir(parents=True, exist_ok=True)
        print("splitting the data in "+str(data_folder)+", and storing them in folder :"+str(splitted_folder))
        splitf = split.Split()
        failed_files = splitf.splitdst(in_path=data_folder, out_path=splitted_folder, tile_size_x=int(tile_size_x), tile_size_y=int(tile_size_y),kun_ok_pic=False,ignore_id=ignore_id,cutdatatype="photo",stop_on_error=False)
        print("failed to split the following files: "+str(failed_files))




if __name__ == "__main__":
    """
    
    Creates masks given .ini file with : paths to images ,gdb-file, mask_featureclass, and folder for masks.
    
    
    """

    usage_example="example usage: \n "+r"python create_patches.py --config path\to\file.ini"
    # Initialize parser
    parser = argparse.ArgumentParser(
        epilog=usage_example,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("-c", "--config", help="one or more paths to config file",required=True)
    args = parser.parse_args()
    main(args.config)



