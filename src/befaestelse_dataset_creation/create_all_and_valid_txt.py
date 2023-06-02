import os
from PIL import Image
import numpy
import pandas as pd
import argparse
import pathlib






def verify_all_files_exists(file_name,folder_path,other_data_folders =[]):
    all_files_exists = True


    for other_data_folder in  other_data_folders:
        if not (other_data_folder/file_name).is_file():
            all_files_exists = False
            #print("this file does not exist:"+str((other_data_folder/file_name)))
    #if no other data folders are used its enough that the initial file exists
    if not (pathlib.Path(folder_path)/file_name).is_file():
        all_files_exists = False
    #print("all_files_exists:"+str(all_files_exists))

    return all_files_exists






def create_all_txt(folder_path,datatype,all_txt_filename,other_data_folders=[]):
    """
    Create all.txt file with all image files included in the folder_path

    """
    #make sure the folder we want to save the txt file in exists
    pathlib.Path(all_txt_filename).parent.mkdir(parents=True, exist_ok=True)



 
    #folder_path=folder_path.replace("//","/")
    folder_path = pathlib.Path(folder_path)





    files_in_folder =os.listdir(folder_path)

    print("files in folder :"+str(len(files_in_folder)))

    files= [x for x in files_in_folder if datatype in x and ".xml" not in x and verify_all_files_exists(x,folder_path,other_data_folders)]
    print("files in folder that also exists in "+str(other_data_folders)+" :" + str(len(files)))


    

    print("number of image files in all: " + str(len(files)))
    print("first image: "+str(files[0]))

    
    with open(all_txt_filename, 'w') as f:
        f.write('\n'.join(files))
    print("printed the filenames to the file : " + all_txt_filename)

def create_valid_txt(all_txt_filename,valid_txt_filename,pick_every):
    with open(all_txt_filename, 'r') as f:
        all_list = f.readlines()
        valid_list=[]
        for i in range(0,len(all_list),pick_every):
            valid_list.append(all_list[i].split("/")[-1])
        with open(valid_txt_filename, 'w') as f:
            f.write(''.join(valid_list))
            print("number of files in valid: " + str(len(valid_list)) + "  == "+str(100*len(valid_list)/len(all_list)) +" % of images in all_txt_file")

            print("first elements in valid_list : " + str(valid_list[0]))
            print("printed the valid filenames to the file : " + valid_txt_filename)


def create_all_and_valid(all_txt_filename,valid_txt_filename,path_to_training_images,datatype,nr_of_images_between_validation_samples,other_data_folders=[]):

    create_all_txt(folder_path=path_to_training_images,datatype=datatype,all_txt_filename=all_txt_filename,other_data_folders=other_data_folders)
    create_valid_txt(all_txt_filename=all_txt_filename,valid_txt_filename=valid_txt_filename,pick_every=nr_of_images_between_validation_samples)
if __name__ == "__main__":
    usage_example="example usage: \n "+r"python create_all_and_valid_txt.py -f /mnt/trainingdata-disk/trainingdata/RoofTopOrto/path/to/splitted/rgb -a /mnt/trainingdata-disk/trainingdata//RoofTopOrto/esbjergplusplus/all.txt  -v  /mnt/trainingdata-disk/trainingdata//RoofTopOrto/esbjergplusplus/valid.txt -p 17 -d .tif --other_data_folders path/to/splitted/cir path/to/splitted/DSM path/to/splitted/DTM path/to/splitted/OrtoCIR path/to/splitted/OrtoRGB"
    # Initialize parser
    parser = argparse.ArgumentParser(
                                    epilog=usage_example,
                                    formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("-f", "--Folder_path", help="path to dataset folder",required=True)
    parser.add_argument("-a", "--All_filename", help="all.txt filename .eg 'esbjerg++_all.txt'  -> esbjer++_all.txt and 'esbjerg++_all.xlsx'",required=True)
    parser.add_argument("-v", "--Valid_filename", help=".eg -v valid.txt",required=True)
    parser.add_argument("-d", "--Datatype", help=".eg -d .tif",required=True)
    parser.add_argument("-p", "--nr_of_images_between_validation_samples",type = int,default = 17, help=".eg pick every 17 when creating a validation set: -p 17",required=False)
    parser.add_argument("--other_data_folders", help="e.g [T:\trainingdata\befastelse\ten_channels_1\data\splitted\cir T:\trainingdata\befastelse\ten_channels_1\data\splitted\DSM T:\trainingdata\befastelse\ten_channels_1\data\splitted\DTM T:\trainingdata\befastelse\ten_channels_1\data\splitted\OrtoCIR T:\trainingdata\befastelse\ten_channels_1\data\splitted\OrtoRGB]", nargs='+', default=[],required=False)




    
    
    args = parser.parse_args()

    create_all_and_valid(all_txt_filename =args.All_filename,valid_txt_filename=args.Valid_filename,path_to_training_images=args.Folder_path,datatype=args.Datatype,nr_of_images_between_validation_samples=args.nr_of_images_between_validation_samples,other_data_folders=[pathlib.Path(folder_path) for folder_path in args.other_data_folders])


    #create_all_txt(folder_path=args.Folder_path,datatype=args.Datatype,all_txt_filename=args.All_filename,allowed_blocks=args.Allowed_blocks)
    





    #create_all_txt_with_images_with_least_background(folder_path=args.Folder_path,datatype=args.Datatype,all_filename=args.All_filename,allowed_blocks=args.Allowed_blocks,max_nr_of_images=args.Max_nr_of_images,label_folder_name=args.Labelsfoldername)
    #if args.Create_valid_txt:
    #    create_valid_txt(all_txt_filename=args.All_filename + 'limited_all.txt', valid_txt_filename=args.All_filename+"_valid.txt", pick_every=pick_every)


    """
    path_to_training_images = r'C:\mnt\trainingdata\rooftop_500p\images\\'
    all_txt_filename = "./all.txt"
    valid_txt_filename = "./valid.txt"
    allowed_blocks= ["83_25","83_26"]
    
    """
