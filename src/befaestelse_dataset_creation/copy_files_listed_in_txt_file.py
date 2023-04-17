#Some ML projects for semantic segmetnation e.g mask-dino assumes that the training data and validation data are in training and validation folders
#This script use train.txt and valid.txt files for copying all iamges to this format.

import os
import pathlib
import shutil
from PIL import Image
def copy_files_to_folder(text_file,origin_folder,destination_folder,new_image_format):
    """
    :param text_file:
    :param origin_folder:
    :param destination_folder:
    :return:
    """
    origin_folder = pathlib.Path(origin_folder)
    destination_folder = pathlib.Path(destination_folder)
    os.makedirs(destination_folder, exist_ok = True)
    with open(text_file) as f:
        lines= f.readlines()

        files = [origin_folder/line.rstrip() for line in lines if os.path.isfile(origin_folder/line.rstrip())]
    print("copying the images noted in " +str(text_file)+ " from :"+str(origin_folder) +" to "+str(destination_folder) +"...")
    for file in files:
        im = Image.open(file)
        im.save(destination_folder/file.with_suffix(new_image_format).name)

    print("done copying the images noted in " +str(text_file)+ " from :"+str(origin_folder) +" to "+str(destination_folder) )



def copy_to_train_and_valid_folders(origin_folder,train_folder,valid_folder,train_txt,valid_txt):
    copy_files_to_folder(train_txt,origin_folder,train_folder)
    copy_files_to_folder(valid_txt,origin_folder,valid_folder)

if __name__ == "__main__":
    example_usage= r"python copy_files_listed_in_txt_file.py "
    print("########################EXAMPLE USAGE########################")
    print(example_usage)
    print("#############################################################")
    import argparse

    # Initialize parser
    parser = argparse.ArgumentParser()

    parser.add_argument("-t", "--Train_text_file", help="path/to/train.txt ",required=True, type=pathlib.Path)
    parser.add_argument("-v", "--Valid_text_file", help="path/to/valid.txt ",required=True,type=pathlib.Path)
    parser.add_argument("-l", "--LabelFolder", help="path/to/folder  e.g path/to/masks",required=True,type=pathlib.Path)
    parser.add_argument("-i", "--ImageFolder", help="path/to/folder  e.g path/to/images",required=True,type=pathlib.Path)

    parser.add_argument("--New_Image_format", help="e.g .jpg",default = ".jpg",required=False)
    parser.add_argument("--New_Label_format", help="e.g .png",default = ".png",required=False)

    #images are copied to images/validation and images/training
    parser.add_argument("--Valid_folder_name", help="folder name e.g validation",default = "validation", required=False)
    parser.add_argument("--Training_folder_name", help="folder name e.g training",default = "training", required=False)

    #labels are copied to annotations/training and annotations/validation
    parser.add_argument("--New_label_folder", help="folder name e.g annotations",default = "annotations", required=False)
    parser.add_argument("--New_image_folder", help="folder name e.g images",default = "images", required=False)



    args = parser.parse_args()

    print("copying images")
    copy_files_to_folder(text_file=args.Valid_text_file,origin_folder=args.ImageFolder,destination_folder= args.ImageFolder.parent/args.New_image_folder/args.Valid_folder_name,new_image_format =args.New_Image_format )
    copy_files_to_folder(text_file=args.Train_text_file,origin_folder=args.ImageFolder,destination_folder= args.ImageFolder.parent/args.New_image_folder/args.Training_folder_name,new_image_format =args.New_Image_format)

    print("copying labels")
    copy_files_to_folder(text_file=args.Valid_text_file,origin_folder=args.LabelFolder,destination_folder= args.ImageFolder.parent/args.New_label_folder/args.Valid_folder_name,new_image_format =args.New_Label_format)
    copy_files_to_folder(text_file=args.Train_text_file,origin_folder=args.LabelFolder,destination_folder= args.ImageFolder.parent/args.New_label_folder/args.Training_folder_name,new_image_format =args.New_Label_format)
