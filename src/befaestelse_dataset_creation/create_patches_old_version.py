import split
from pathlib import Path
import configparser
import argparse
def main(config):
    ini_parser = configparser.ConfigParser()
    ini_parser.read(config)
    section = "SETTINGS"


    mask_folder = ini_parser[section]["mask_folder"]
    image_folder = ini_parser[section]["image_folder"]
    cir_image_folder = ini_parser[section]["cir_image_folder"]

    splitted_image_folder = ini_parser[section]["splitted_image_folder"]
    splitted_mask_folder = ini_parser[section]["splitted_mask_folder"]
    splitted_cir_image_folder = ini_parser[section]["splitted_cir_image_folder"]

    tile_size_y = ini_parser[section]["tile_size_y"]
    tile_size_x = ini_parser[section]["tile_size_x"]

    ignore_id = int(ini_parser[section]["ignore_id"])


    folders_with_large_images= [mask_folder,image_folder,cir_image_folder]
    folders_with_patches= [splitted_mask_folder,splitted_image_folder,splitted_cir_image_folder]

    #when cutting images into pathces we want to fill in with the pixels that are "outside of the image"  with different values
    #for labels we want to fill them in with ignore_id ,for other kinds of data it might be different
    cutdatatypes=["mask_NaN","photo","photo"]


    for n_folder in range(len(folders_with_large_images)):
        orig_folder =folders_with_large_images[n_folder]
        splitted_folder =folders_with_patches[n_folder]
        print("splitting images in folder:"+str(orig_folder) + ", saving patches in folder :"+str(splitted_folder))
        cutdatatype = cutdatatypes[n_folder]
        Path(splitted_folder).mkdir(parents=True, exist_ok=True)
        splitf = split.Split()
        splitf.splitdst(in_path=orig_folder, out_path=splitted_folder, tile_size_x=int(tile_size_x), tile_size_y=int(tile_size_y),kun_ok_pic=False,ignore_id=ignore_id,cutdatatype=cutdatatype)






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



