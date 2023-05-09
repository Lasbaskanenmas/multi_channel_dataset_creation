import os
import pathlib
from osgeo import gdal
large_file_name = "PROBS_O2021_84_40_1_0037_00084319"



def get_pathes_per_large_image(input_folder):
    input_files = os.listdir(input_folder)
    #find all different image names (the name of the image before it was splitted up)
    images ={}
    for input_file in input_files:
        #input(input_file)
        image_name =  "_".join(input_file.split("_")[:-2])
        patch_path = input_folder+"\\"+input_file
        #input(image_name)
        if image_name in images:
            images[image_name].append(patch_path)
        else:
            images[image_name] = [patch_path]
    return images

def merge_channels(images,output_file_path):
    gdal_merge_path = r'"C:/Program Files/QGIS 3.22.4/apps/Python39/Scripts/gdal_merge.py"'
    #input(output_file_path)
    pathlib.Path(output_file_path).parent.mkdir(parents=True, exist_ok=True)
    merge_argument = " ".join(images)

    gdal_merge_process = "python "+gdal_merge_path +' -separate -o '+'"'+output_file_path +'"'+" "+merge_argument
    print(gdal_merge_process)
    print("merging :"+str(len(images))+ " nr of chanel-images to "+output_file_path)
    # Call process.
    os.system(gdal_merge_process)
    print("done")


def combine_patches(patches,large_image_name,output_file_path = r"C:\Users\B152325\Desktop\befæstelse_status_2023\\"):
    gdal_merge_path = r'"C:/Program Files/QGIS 3.22.4/apps/Python39/Scripts/gdal_merge.py"'
    #input(output_file_path)
    pathlib.Path(output_file_path).mkdir(parents=True, exist_ok=True)
    #input("crated folder?")

    output_file_path= str(pathlib.Path(output_file_path)/ (  large_image_name + ".tif"))
    #input(output_file_path)
    merge_argument = " ".join(patches)

    gdal_merge_process = "python "+gdal_merge_path +' -o '+'"'+output_file_path +'"'+" "+' -init 0 -ot float32 ' +merge_argument
    print(gdal_merge_process)
    print("merging :"+str(len(patches))+ " nr of patches to "+output_file_path)
    # Call process.
    os.system(gdal_merge_process)
    print("done")

    return output_file_path

def add_probabilities(large_images,output_folder=r"C:\Users\B152325\Desktop\befæstelse_status_2023\\",output_name= "a_name"):
    nr_of_bands =gdal.Open((large_images[0])).ReadAsArray().shape[0]

    #for band 1,2,3,4,,,n
    #gdall_calc only processes a single band at a time, so we need to merge all images for each band and save them to separate images before merging them to a multichannel image
    band_images=[]
    for band in range(1,nr_of_bands+1):
        band = str(band)
        print("CREATING BAND: "+str(band) + " out of : "+str(nr_of_bands))

        print(output_folder)
        pathlib.Path(output_folder).mkdir(parents=True, exist_ok=True)
        print("crated folder?")
        gdal_calc_path = r'"C:/Program Files/QGIS 3.22.4/apps/Python39/Scripts/gdal_calc.py"'

        input_args =[]

        A = 65
        Z = 90
        a = 97
        z= 122
        numbers = list(range(A,Z+1))+list(range(a,z+1))

        #limitinh number of images to process to number of images or gdal_calcs limit
        max_args= min(len(numbers),len(large_images))
        if max_args < len(large_images):
            input("only merging :"+str(max_args) + " out of : "+str(len(large_images)) + " images, is this OK?")

        numbers = numbers[0:max_args]
        input_files=large_images[0:max_args]

        #numbers = [0:max_args]

        processed_nr=A-1
        for i in range(max_args):
            character = chr(numbers[i])
            input_args.append("-"+character+ " "+input_files[i])
            #gdall_calc only processes a single band at a time, so we need to merge all images for each band and save them to separate images before merging them to a multichannel image
            input_args.append("--"+character+ "_band="+band)


        input_args = " ".join(input_args)


        calc_argument = "--calc " +'"' + "+".join([chr(i) for i in numbers])+ '"'
        print(calc_argument)

        #input_args = [input_file for input_file in input_files]

        # Arguements.

        #output_file_path = r"C:\Users\B152325\Desktop\befæstelse_status_2023\\"

        output_file_path= str(pathlib.Path(output_folder)/ (output_name+"band_"+band+ "_calc_merged_probs" + ".tif"))

        #output_file_path=output_folder+   "calc_merged_probs" + ".tif"
        calc_expr = '"A + B"'
        typeof = '"Float32"'


        # Generate string of process.
        gdal_calc_str = 'python {0} -A {1} -B {2} --outfile={3} --calc={4} --type={5} --hideNoData'





        gdal_calc_process = "python "+gdal_calc_path +" "+input_args+' --outfile '+'"'+output_file_path +'"'+" "+calc_argument+' --type="Float32" --hideNoData --overwrite --extent=union'

        print(gdal_calc_process)
        print("gdal_calc running on "+str()+" nr of overlapping images...")
        # Call process.
        os.system(gdal_calc_process)
        print("gdal_calc done")
        print("created: "+str(output_file_path))
        band_images.append(output_file_path)
    print("now we can merge the images with")
    print("gdal_merge -separate -o outputfilename inputfiename1 inputfilename2 inputfilename3 ..")
    merge_channels([str(path) for path in band_images],output_file_path= str(pathlib.Path(output_folder)/ (output_name+"_allbands_" "_calc_merged_probs" + ".tif")))
    print("merged channels are stored in : "+str(pathlib.Path(output_folder)/ (output_name+"_allbands_" "_calc_merged_probs" + ".tif")))



def main(args):
    debug = False


    if debug:
        print("merging the proibabiliteis of a few small handselected images")
        add_probabilities([r"T:\logs_and_models\befastelse\orthoimages_iteration_31_linux\models\1km2\PROBS_O2021_84_40_1_0045_00093310_7000_0.tif",r"T:\logs_and_models\befastelse\orthoimages_iteration_31_linux\models\1km2\PROBS_O2021_84_40_1_0045_00093310_7000_2000.tif"],output_name= "c_name")
        input("the probabilities have now been added!")

    #lots of 1000x1000 croped probabilities-images are located in a folder
    #input_folder =r"T:\logs_and_models\befastelse\orthoimages_iteration_31\models\befaestelse_dataset_creation_test_2"

    #create a dictionary with the original image as key and a list of patches as value
    small_images_for_each_large_image = get_pathes_per_large_image(args.Input_preds)
    large_images=[]
    for large_image in small_images_for_each_large_image:
        output_path = combine_patches(patches= small_images_for_each_large_image[large_image],large_image_name = large_image,output_file_path=args.Mosaicked_preds_folder)
        print("done merging images to :"+output_path)
        large_images.append(output_path)



    #merge the resulting overlapping images to a single tiff file
    add_probabilities(large_images,output_folder = args.Output_merged_preds_folder)

if __name__ == "__main__":
    example_usage= r"python merge_all_images_probabilities.py -i path\to\folder\with\probs -o folder\to\save\merged\probs\in"
    print("########################EXAMPLE USAGE########################")
    print(example_usage)
    print("#############################################################")
    import argparse

    # Initialize parser
    parser = argparse.ArgumentParser()

    parser.add_argument("-i", "--Input_preds", help="path/to/folder/with/probs  ",required=True)
    parser.add_argument("-m", "--Mosaicked_preds_folder", help="path/to/folder/to/save/mosaicked/probs/in (crops from same images are recomined to a large image)",required=True)
    parser.add_argument("-o", "--Output_merged_preds_folder", help="path/to/folder/to/save/merged/probs/in",required=True)

    args = parser.parse_args()
    main(args)

