


import os
import numpy as np
from PIL import Image
import argparse
import pathlib
import configparser
def main(config):
    ini_parser = configparser.ConfigParser()
    ini_parser.read(config)
    section = "SETTINGS"


    splitted_mask_folder = pathlib.Path(ini_parser[section]["splitted_mask_folder"])
    images_that_define_areas_to_create_labels_for = ini_parser[section]["images_that_define_areas_to_create_labels_for"]
    images_that_define_areas_to_create_labels_for= pathlib.Path(images_that_define_areas_to_create_labels_for)
    splitted_image_folder= (pathlib.Path(ini_parser[section]["data_folder"])/"splitted")/ images_that_define_areas_to_create_labels_for.name

    datatype= ini_parser[section]["datatype"]

    delete_files_with_only_zeros_in_label(image_folder=splitted_image_folder,label_folder=splitted_mask_folder,datatype=datatype)

def delete_files_with_only_zeros_in_label(image_folder,label_folder,datatype):
    """
    Some images have labels consisting only of zeros (unknown)
    This seems to mess up the cost function so we delete these
    """

    image_folder= pathlib.Path(image_folder)
    label_folder = pathlib.Path(label_folder)
    deleted_images_because_of_only_zeros_in_label = []
    deleted_labels_because_of_only_zeros_in_label = []
    deleted_images_because_of_missing_label_file = []


    images = [image_folder/file for file in os.listdir(image_folder) if pathlib.Path(file).suffix == datatype]
    labels = [label_folder/(file_path.name) for file_path in images]
    print("verifying that all images have valid labels: .." )
    for i in range(len(images)):

        #if there is no label to open we throw an exception and delete the image
        try:

            if np.array(Image.open(labels[i])).sum() ==0:
                #if there are only zeros in the label we delete the iamge and the label
                os.remove(images[i])
                deleted_images_because_of_only_zeros_in_label.append(images[i])
                os.remove(labels[i])
                deleted_labels_because_of_only_zeros_in_label.append(labels[i])
        except:
            os.remove(images[i])
            deleted_images_because_of_missing_label_file.append(images[i])

    print("deleted_images_because_of_only_zeros_in_label")
    print(deleted_images_because_of_only_zeros_in_label)
    print("nr of files :"+str(len(deleted_images_because_of_only_zeros_in_label)))
    print("deleted_labels_because_of_only_zeros_in_label")
    print(deleted_labels_because_of_only_zeros_in_label)
    print("nr of files :"+str(len(deleted_labels_because_of_only_zeros_in_label)))

    print("deleted_images_because_of_missing_label_file")
    print(deleted_images_because_of_missing_label_file)
    print("nr of files :"+str(len(deleted_images_because_of_missing_label_file)))





if __name__ == "__main__":

    # Initialize parser
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", help="one or more paths to config file",nargs ='+',required=True)
    args = parser.parse_args()
    main(args.config)
    args = parser.parse_args()




