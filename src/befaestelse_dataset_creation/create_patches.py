import split
from pathlib import Path
import configparser
import argparse
import shutil
import json
def main(config):
    ini_parser = configparser.ConfigParser()
    ini_parser.read(config)
    section = "SETTINGS"





    tile_size_y = ini_parser[section]["tile_size_y"]
    tile_size_x = ini_parser[section]["tile_size_x"]
    overlap= ini_parser[section]["overlap"]

    ignore_id = int(ini_parser[section]["ignore_id"])


    #handle label masks
    if "mask_folder" in ini_parser[section]:
        print("dataset includes label masks that should be splitted")
        large_masks_folder = ini_parser[section]["mask_folder"]
        splitted_mask_folder = ini_parser[section]["splitted_mask_folder"]
        print("splitting the labels in "+str(large_masks_folder)+"and string them in folder :"+str(splitted_mask_folder))


        #remove the destination folder and create it anew
        if Path(splitted_mask_folder).exists() and Path(splitted_mask_folder).is_dir():
            shutil.rmtree(Path(splitted_mask_folder))
        
        Path(splitted_mask_folder).mkdir(parents=True, exist_ok=True)

        splitf = split.Split()
        splitf.splitdst(in_path=large_masks_folder, out_path=splitted_mask_folder, tile_size_x=int(ini_parser[section]["tile_size_x"]),tile_size_y=int(ini_parser[section]["tile_size_y"]),kun_ok_pic=False,ignore_id=ignore_id,cutdatatype="mask_NaN",overlap=int(overlap))

    else:
        print("dataset does NOT include any label masks")

    # handle house masks
    if "mask_folder_houses" in ini_parser[section]:
        print("dataset includes house masks that should be splitted")
        large_masks_folder_houses = ini_parser[section]["mask_folder_houses"]
        splitted_mask_folder_houses = ini_parser[section]["splitted_mask_folder_houses"]
        print("splitting the houses in "+str(large_masks_folder_houses)+"and string them in folder :"+str(splitted_mask_folder_houses))


        #remove the destination folder and create it anew
        if Path(splitted_mask_folder_houses).exists() and Path(splitted_mask_folder_houses).is_dir():
            shutil.rmtree(Path(splitted_mask_folder_houses))
        Path(splitted_mask_folder_houses).mkdir(parents=True, exist_ok=True)


        splitf = split.Split()
        splitf.splitdst(in_path=large_masks_folder_houses, out_path=splitted_mask_folder_houses, tile_size_x=int(ini_parser[section]["tile_size_x"]), tile_size_y=int(ini_parser[section]["tile_size_y"]),kun_ok_pic=False,ignore_id=ignore_id,cutdatatype="mask_NaN",overlap=int(overlap))
    else:
        print("dataset does not include any house masks")

    # handle input data
    datatypes =json.loads(ini_parser[section]["datatypes"])
    data_folders_parent_directory =Path(ini_parser[section]["data_folder"])
    data_folders = [data_folders_parent_directory / datatype for datatype in datatypes]
    splitted_data_folders_parent_directory = Path(ini_parser[section]["splitted_data_parent_folder"])
    for data_folder in data_folders:
        splitted_folder = splitted_data_folders_parent_directory/data_folder.name

        print("splitting the data in "+str(data_folder)+", and storing them in folder :"+str(splitted_folder))


        #remove the destination folder and create it anew
        if Path(splitted_folder).exists():
            shutil.rmtree(Path(splitted_folder))
        Path(splitted_folder).mkdir(parents=True, exist_ok=True)


        splitf = split.Split()
        failed_files = splitf.splitdst(in_path=data_folder, out_path=splitted_folder, tile_size_x=int(tile_size_x), tile_size_y=int(tile_size_y),kun_ok_pic=False,ignore_id=ignore_id,cutdatatype="photo",stop_on_error=False,overlap=int(overlap))
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



