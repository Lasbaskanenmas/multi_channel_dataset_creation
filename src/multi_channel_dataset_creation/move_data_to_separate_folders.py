#going from folder/a_name_DSM.tif , folder/a_name_OrtoCIR.tif ... to  DSM/a_name.tif , OrtoCIR/a_name.tif ..
#images not containing any of the strings ["DSM","DTM","OrtoCIR","OrtoRGB","cir","rgb"] are left in the original folder 
import crop_to_shapefile
import rename_files
import pathlib
import os
import configparser
import json

def get_shapefile(args):
    """
    get the shapefile that defines the area we are interested in)

    :param args:
    :return:
    """
    ini_parser = configparser.ConfigParser()
    ini_parser.read(args.merge_inference_images_config)
    section = "SETTINGS"
    return ini_parser[section]["Shape_file"]


def main(args):
    config=args.dataset_config
    ini_parser = configparser.ConfigParser()
    ini_parser.read(config)
    section = "SETTINGS"

    for datatype in json.loads(ini_parser[section]["datatypes"]):
        print("datatype:"+str(datatype))
        #set the variables that rename_files.main() need

        inputfolder = pathlib.Path(ini_parser[section]["folder_containing_all_image_types"])
        data_folder = pathlib.Path(ini_parser[section]["data_folder"])
        outputfolder = data_folder / (datatype)
        replacestring = "_"+datatype+   ini_parser[section]["datatype"]
        newstring = ini_parser[section]["datatype"]
        only_consider_files_with_matching_names = True
        move_instead_of_copy = True
        try:
            #if the dataset is created for ML inference in production, there will be a merge_ini file that defines , among other things a shapefile that defins what areas we are interested in. 
            #if get_shapefile(args) suceed such a shapefile exists, and we should crop away all unnececeary data 
            get_shapefile(args)
            crop_to_shapefile_plus_buffer = True
        except:
            crop_to_shapefile_plus_buffer = False


        os.makedirs(outputfolder, exist_ok = True)

        print("moving data of type :"+str(datatype) +" from : "+str(inputfolder)+ " to "+str(outputfolder))
        if crop_to_shapefile_plus_buffer:
            crop_to_shapefile.main(inputfolder ,outputfolder,replacestring,newstring,only_consider_files_with_matching_names,shapefile_path=get_shapefile(args) )
        else:        
            rename_files.main(inputfolder ,outputfolder,replacestring,newstring,only_consider_files_with_matching_names,move_instead_of_copy)



if __name__ == "__main__":
    example_usage= r"python move_files_to_separate_folders.py "
    print("########################EXAMPLE USAGE########################")
    print(example_usage)
    print("#############################################################")
    import argparse

    # Initialize parser
    parser = argparse.ArgumentParser()

    parser.add_argument("-f", "--inputfolder", help="path/to/original_folder",required=True, type=pathlib.Path)

    args = parser.parse_args()

    main(args)
