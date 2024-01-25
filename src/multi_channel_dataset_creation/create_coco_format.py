"""
Script developed in order to create the coco .json file needed by IBM in order to train a object segmentation model on SDFIs solarcell dataset.
The .json used for object segmentation should be possible to use also for pure image segmentation models but have only been tested for object segmentation in the IBM project


In order to visualize the coco-format lables you can use  https://github.com/rasmuspjohansson/coco-viewer.git
"""

# https://www.immersivelimit.com/create-coco-annotations-from-scratch
from pathlib import Path
from PIL import Image
import argparse
import json
import os
import numpy as np  # (pip install numpy)
from skimage import measure  # (pip install scikit-image)
from shapely.geometry import Polygon, MultiPolygon  # (pip install Shapely)


def main(args):
    # images_folder =  # "/mnt/T/mnt/trainingdata/befastelse/1km2/data/splitted/rgb"
    # labels_folder =  # "/mnt/T/mnt/trainingdata/befastelse/1km2/labels/splitted_labels"

    dictionary = {}
    add_info_section(dictionary)
    add_licence_section(dictionary)
    add_images_and_annotations_section(images_folder=args.images, labels_folder=args.labels, dictionary=dictionary,
                                       textfile=args.images_text)
    add_categories(dictionary)

    out_file = open(args.outputfile, "w")

    json.dump(dictionary, out_file, indent=6)


def add_categories(dict):
    dict["categories"] = [{"supercategory": "solar_energy", "id": 1, "name": "photovoltic_solarcell"},
                          {"supercategory": "solar_energy", "id": 2, "name": "solar_heat_collector"}]


def add_info_section(dict):
    dict["info"] = {"description": "SDFI solarcell dataset 2024", "url": "http://cocodataset.org", "version": "0.1",
                    "year": 2024, "contributor": "SDFI", "date_created": "2024/01/11"}


def add_licence_section(dict):
    # No licence for the public images
    dict["licenses"] = ["no licence"]


def add_images_and_annotations_section(images_folder, labels_folder, dictionary, textfile):
    # Get a list of all image files in the images_folder that are listed in a text dokument e.g. all.txt
    if textfile:
        with open(textfile, 'r') as file:
            # Read lines from the file and remove leading/trailing whitespaces
            file_list = [line.strip() for line in file.readlines()]
    else:
        file_list = [afile for afile in os.listdir(images_folder) if Path(afile).suffix in [".tif", ".jpg", ".png"]]

    image_files = [Path(images_folder) / file_name for file_name in file_list]

    image_list = []
    annotations = []
    annotation_id = 0
    is_crowd = 0

    for index, image_path in enumerate(image_files):
        # Open the image to get its properties
        with Image.open(image_path) as img:
            image_id = index
            image_name = image_path.name
            image_height, image_width = img.size

        # Add information about the image to the image_list
        image_info = {
            "license": 0,
            "file_name": image_name,
            "height": image_height,
            "width": image_width,
            "date_captured": "2023",
            "id": image_id
        }
        image_list.append(image_info)

        # get the mask image (only one per image)
        mask_image = Path(labels_folder) / image_name

        # get the submasks (one mask per class in each image)
        sub_masks = create_sub_masks(Image.open(mask_image))
        # for each submask ,find the countours of the objects of that class and ad the anotation to the dictionary
        for color, sub_mask in sub_masks.items():
            category_id = int(color)
            (new_annotations, updated_annotation_id) = create_sub_mask_annotations(sub_mask, image_id, category_id,
                                                                                   annotation_id, is_crowd)
            annotations = annotations + new_annotations
            annotation_id = updated_annotation_id

    dictionary["images"] = image_list
    dictionary["annotations"] = annotations


def create_sub_masks(mask_image):
    width, height = mask_image.size

    # Initialize a dictionary of sub-masks indexed by RGB colors
    sub_masks = {}
    for x in range(width):
        for y in range(height):
            # Get the RGB values of the pixel
            pixel = mask_image.getpixel((x, y))

            # If the pixel is not black...
            if pixel != 0:
                # print("found pixel value:"+str(pixel))
                # Check to see if we've created a sub-mask...
                pixel_str = str(pixel)
                sub_mask = sub_masks.get(pixel_str)
                if sub_mask is None:
                    # Create a sub-mask (one bit per pixel) and add to the dictionary
                    # Note: we add 1 pixel of padding in each direction
                    # because the contours module doesn't handle cases
                    # where pixels bleed to the edge of the image
                    sub_masks[pixel_str] = Image.new('1', (width + 2, height + 2))

                # Set the pixel value to 1 (default is 0), accounting for padding
                sub_masks[pixel_str].putpixel((x + 1, y + 1), 1)

    return sub_masks


def create_sub_mask_annotations(sub_mask, image_id, category_id, annotation_id, is_crowd):
    # Find contours (boundary lines) around each sub-mask
    # Note: there could be multiple contours if the object
    # is partially occluded. (E.g. an elephant behind a tree)
    contours = measure.find_contours(np.array(sub_mask), 0.5, positive_orientation='low')

    # segmentations = []
    annotations = []
    # polygons = []
    for contour in contours:
        # Flip from (row, col) representation to (x, y)
        # and subtract the padding pixel
        for i in range(len(contour)):
            row, col = contour[i]
            contour[i] = (col - 1, row - 1)

        # Make a polygon and simplify it
        poly = Polygon(contour)
        poly = poly.simplify(1.0, preserve_topology=False)
        # polygons.append(poly)
        segmentation = np.array(poly.exterior.coords).ravel().tolist()
        # segmentations.append(segmentation)

        # Combine the polygons to calculate the bounding box and area

        if str(poly) == "POLYGON EMPTY":
            print(poly)
            pass
        else:
            print(poly)
            multi_poly = MultiPolygon([poly])
            x, y, max_x, max_y = multi_poly.bounds
            width = max_x - x
            height = max_y - y
            bbox = (x, y, width, height)
            area = multi_poly.area

            annotation = {
                'segmentation': [segmentation],
                'iscrowd': is_crowd,
                'image_id': image_id,
                'category_id': category_id,
                'id': annotation_id,
                'bbox': bbox,
                'area': area
            }
            annotations.append(annotation)
            annotation_id += 1

    return (annotations, annotation_id)



if __name__ == "__main__":
    """

    convert data to coco (instance segmetnation) format, by creating a .json file
    """

    usage_example = "example usage: \n " + r"python create_coco_format.py -i T:\IBM\IBM_orto_images\random_subset\yes_solar_cell_random_subset\labels\large_label\reclass -l T:\IBM\IBM_orto_images\random_subset\yes_solar_cell_random_subset\labels\large_label\reclass -o random_subset_yes_20230125.json"
    # Initialize parser
    parser = argparse.ArgumentParser(
        epilog=usage_example,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("-i", "--images", help="path to images", required=True)
    parser.add_argument("-t", "--images_text",
                        help="path to textfile that lists all images, without this argument all image files in image directory are used",
                        required=False)
    parser.add_argument("-l", "--labels", help="path to labels", required=True)
    parser.add_argument("-o", "--outputfile", help="path to outputfile_coco_instance_segmentation_format.json", required=True)
    args = parser.parse_args()
    main(args)
