#usage .    first create a .txt file containing all file_names of the files you want to copy. e.g with create_txt_file_with_images_that_overlap_with_shapefile.py
#           then use this script to copy all files with those names from a folder to another
#           .eg 1. create txt_file copy from rgb folder to another rgb folder , copy from one cir folder to anotehr , copy from one label folder to another
#           the fileformat can optioally be changed (if we for instance need to change from .tif to .jpg)
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
        #in order to make sure we only have the name of the file and not a complete filepath ,we do: pathlib.Path(line.rstrip()).name 
        files = [origin_folder/pathlib.Path(line.rstrip()).name for line in lines if os.path.isfile(origin_folder/line.rstrip())]
    print("copying the images noted in " +str(text_file)+ " from :"+str(origin_folder) +" to "+str(destination_folder) +"...")
    for file in files:
        if new_image_format:
            im = Image.open(file)
            im.save(destination_folder/file.with_suffix(new_image_format).name)
        else:
            # Copy the file
            shutil.copyfile(file, destination_folder/file.name)

    print("done copying the images noted in " +str(text_file)+ " from :"+str(origin_folder) +" to "+str(destination_folder) )



if __name__ == "__main__":
    example_usage= r"python copy_files_listed_in_txt_file.py --text_file --folder --new_folder"
    print("########################EXAMPLE USAGE########################")
    print(example_usage)
    print("#############################################################")
    import argparse

    # Initialize parser
    parser = argparse.ArgumentParser()

    parser.add_argument("-t", "--text_file", help="path/to/text_file.txt ",required=True, type=pathlib.Path)

    parser.add_argument("-f", "--folder", help="path/to/folder  e.g path/to/images",required=True,type=pathlib.Path)
    parser.add_argument("-n", "--new_folder", help="path/to/folder  e.g path/to/new_folder",required=True,type=pathlib.Path)

    parser.add_argument("--New_Image_format", help="e.g .jpg",default=None,required=False)


    args = parser.parse_args()

    print("copying images")
    copy_files_to_folder(text_file=args.text_file,origin_folder=args.folder,destination_folder= args.new_folder,new_image_format =args.New_Image_format )
