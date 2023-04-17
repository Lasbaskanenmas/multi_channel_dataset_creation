#going from folder/a_name_DSM.tif , folder/a_name_OrtoCIR.tif ... to  DSM/a_name.tif , OrtoCIR/a_name.tif ..
#images not containing any of the strings ["DSM","DTM","OrtoCIR","OrtoRGB","cir"] arte left in the original folder (typically this will be the lod images)

import rename_files
import pathlib
import os
import configparser
import json
def main(config):
    ini_parser = configparser.ConfigParser()
    ini_parser.read(config)
    section = "SETTINGS"

    for datatype in json.loads(ini_parser[section]["datatypes"]):
        input("datatype:"+str(datatype))
        #set the variables that rename_files.main() need

        inputfolder = pathlib.Path(ini_parser[section]["folder_containing_all_image_types"])
        outputfolder = inputfolder.parent / (datatype)
        replacestring = "_"+datatype+ ".tif"
        newstring = ".tif"
        only_consider_files_with_matching_names = True
        move_instead_of_copy = True

        os.makedirs(outputfolder, exist_ok = True)

        print("moving data of type :"+str(datatype) +" from : "+str(inputfolder)+ " to "+str(outputfolder))
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
