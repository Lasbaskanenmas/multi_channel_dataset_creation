import os
import pathlib
import numpy as np
from osgeo import gdal
import argparse
import time



def get_patches_per_large_image(input_folder):
    """
    :param input_folder:
    :return: {"large_image_name_1.tif":["patch_1.tif","patch_2.tif",,,],}
    """
    input_files = os.listdir(input_folder)
    #find all different image names (the name of the image before it was splitted up)
    images ={}
    for input_file in input_files:
        #input(input_file)
        image_name =  "_".join(input_file.split("_")[:-2]) + ".tif"



        patch_path = input_folder+"\\"+input_file
        #input(image_name)
        if image_name in images:
            images[image_name].append(patch_path)
        else:
            images[image_name] = [patch_path]
    return images

def merge_channels(images,output_file_path,gdal_path= "None"):
    gdal_merge_path = '"'+gdal_path +'gdal_merge.py"'  # gdal_merge_path = r'"C:/Program Files/QGIS 3.22.4/apps/Python39/Scripts/gdal_merge.py"'
    #input(output_file_path)
    pathlib.Path(output_file_path).parent.mkdir(parents=True, exist_ok=True)
    merge_argument = " ".join(images)

    gdal_merge_process = "python "+gdal_merge_path +' -separate -o '+'"'+output_file_path +'"'+" "+merge_argument
    print(gdal_merge_process)
    print("merging :"+str(len(images))+ " nr of chanel-images to "+output_file_path)
    # Call process.
    os.system(gdal_merge_process)
    print("done")


def combine_patches(patches,output_file_path = r"C:\Users\B152325\Desktop\befæstelse_status_2023\\",gdal_path = "None",use_gdalbuildvrt = True):
    start_time = time.time()

    output_file_path_buldvrt = "tmp2.vrt"

    gdalbuildvrt = "gdalbuildvrt "







    gdal_merge_path = '"'+gdal_path +'gdal_merge.py"'  #r'"C:/Program Files/QGIS 3.22.4/apps/Python39/Scripts/gdal_merge.py"'





    #gdal_merge_path = '"'+gdal_path +'gdal_merge.py"'  #r'"C:/Program Files/QGIS 3.22.4/apps/Python39/Scripts/gdal_merge.py"'


    pathlib.Path(output_file_path).parent.mkdir(parents=True, exist_ok=True)
    #input("crated folder?")


    #output_file_path= str(pathlib.Path(output_file_path)/ (  large_image_name + ".tif"))



    #divide the patches up unto batches (gdal_merge can not handle to many images)
    number_of_batches = max(1,int(len(patches)/80))
    batches = [list(batch) for batch in np.array_split(patches,number_of_batches)]
    #merge each batch
    print("dividing the patches into :"+str(number_of_batches)+ " nr of batches")

    for id_batch, batch in enumerate(batches):
        batch_start= time.time()

        if id_batch!=0:
            #if we allready have merged some of the files we merge the rest of the files with the output of that operation
            if use_gdalbuildvrt:
                pass #batch.append(output_file_path_buldvrt)
            else:
                batch.append(output_file_path_buldvrtoutput_file_path)


        merge_argument = " ".join(batch)

        gdal_merge_process = "python "+gdal_merge_path +' -o '+'"'+output_file_path +'"'+" "+' -init 0 -ot float32 ' +merge_argument
        gdalbuildvrt_process = gdalbuildvrt + output_file_path_buldvrt+" "+merge_argument

        if use_gdalbuildvrt:
            print("merging :"+str(len(batch))+ " nr of patches to "+output_file_path_buldvrt)
        # Call process.

        print("##running the following command ###")

        if use_gdalbuildvrt:
            print(gdalbuildvrt_process)
            os.system(gdalbuildvrt_process)
        else:
            os.system(gdal_merge_process)

        print("##Done ###")
        batch_end = time.time()

        print("merging batch took:"+str(batch_end-batch_start))
    end_time = time.time()
    print("end_time-start_time:"+str(end_time-start_time))
    print("done combining patches")

    if use_gdalbuildvrt:
        print("turn the VRT file into a geotif")
        print("##running the following command ###")
        vrt_to_geotif = "gdal_translate -of GTiff "+output_file_path_buldvrt + " "+output_file_path
        print(vrt_to_geotif)
        vrt_to_tif_start_time = time.time()
        os.system(vrt_to_geotif)
        vrt_to_tif_end_time = time.time()
        print("##Done ###")
        print("vrt_to_tif took:"+str(vrt_to_tif_end_time-vrt_to_tif_start_time))






def crate_predictions(large_images,output_folder=r"C:\Users\B152325\Desktop\befæstelse_status_2023\\",output_name= "a_name",gdal_path = "None"):
    print("#######################################################")
    print("creating prediction image")
    print("#######################################################")




    pathlib.Path(output_folder).mkdir(parents=True, exist_ok=True)
    print("crated folder?")
    gdal_calc_path = '"'+gdal_path +'gdal_calc.py"' # r'"C:/Program Files/QGIS 3.22.4/apps/Python39/Scripts/gdal_calc.py"'

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



    input_args = " ".join(input_args)


    calc_argument = "--calc " +'"' + "numpy.argmax((" +','.join([chr(i) for i in numbers])+ '),axis=0)"'
    print(calc_argument)

    #input_args = [input_file for input_file in input_files]

    # Arguements.

    #output_file_path = r"C:\Users\B152325\Desktop\befæstelse_status_2023\\"

    output_file_path= str(pathlib.Path(output_folder)/ (output_name+"_calc_merged_preds" + ".tif"))

    #output_file_path=output_folder+   "calc_merged_probs" + ".tif"
    calc_expr = '"A + B"'
    typeof = '"Float32"'


    # Generate string of process.
    gdal_calc_str = 'python {0} -A {1} -B {2} --outfile={3} --calc={4} --type={5} --hideNoData'





    gdal_calc_process = "python "+gdal_calc_path +" "+input_args+' --outfile '+'"'+output_file_path +'"'+" "+calc_argument+' --type="Float32" --hideNoData --overwrite'

    print(gdal_calc_process)
    print("gdal_calc running on "+str(len(input_files))+" nr of overlapping images...")
    # Call process.
    os.system(gdal_calc_process)
    print("gdal_calc done")
    print("created: "+str(output_file_path))



    #THIS WORKED gdal_calc -A T:\logs_and_models\befastelse\orthoimages_iteration_31_linux\models\1km2\PROBS_O2021_84_40_1_0045_00093310_7000_0.tif -B T:\logs_and_models\befastelse\orthoimages_iteration_31_linux\models\1km2\PROBS_O2021_84_40_1_0045_00093310_7000_2000.tif --outfile \\TRUENAS\mlnas\mnt\logs_and_models\befastelse\orthoimages_iteration_31_linux\models\1km2_merged_old\a_name_allbands__calc_merged_pred_6.tif --type=UInt16 --calc=""numpy.argmax((A,B),axis=0)"

def create_channel_images(large_images,channel_images,bands,gdal_path = "None"):
    """
    Crate one image for each segmentation class

    :param large_images:
    :param channel_images:
    :param bands:
    :param gdal_path:
    :return:
    """
    print("#######################################################")
    print("creating channel-images")
    print("#######################################################")
    for i_band in range(len(bands)):
        band= bands[i_band]

        print("CREATING BAND: "+str(band) + " out of : "+str(nr_of_bands))

        print(str(pathlib.Path(channel_images).parent))
        pathlib.Path(channel_images).parent.mkdir(parents=True, exist_ok=True)
        print("crated folder?")
        gdal_calc_path = '"'+gdal_path +'gdal_calc.py"' # r'"C:/Program Files/QGIS 3.22.4/apps/Python39/Scripts/gdal_calc.py"'

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

        for i in range(max_args):
            character = chr(numbers[i])
            input_args.append("-"+character+ " "+input_files[i])
            #gdall_calc only processes a single band at a time, so we need to merge all images for each band and save them to separate images before merging them to a multichannel image
            input_args.append("--"+character+ "_band="+band)

        input_args = " ".join(input_args)
        calc_argument = "--calc " +'"' + "+".join([chr(i) for i in numbers])+ '"'
        print(calc_argument)

        output_file_path=  channel_images[i_band] #str(pathlib.Path(output_folder)/ (output_name+"band_"+band+ "_calc_merged_probs" + ".tif"))
        gdal_calc_process = "python "+gdal_calc_path +" "+input_args+' --outfile '+'"'+output_file_path +'"'+" "+calc_argument+' --type="Float32" --hideNoData --overwrite --extent=union'

        print(gdal_calc_process)
        print("gdal_calc running on "+str()+" nr of overlapping images...")
        # Call process.
        os.system(gdal_calc_process)
        print("gdal_calc done")
        print("created: "+str(output_file_path))


def create_multichannel_image(channel_images=None,output_folder=r"C:\Users\B152325\Desktop\befæstelse_status_2023\\",output_name= "a_name",gdal_path = "None"):
    """
    Merge all channel images into a single multi-channel image
    :param large_images:
    :param channel_images:
    :param bands:
    :param output_folder:
    :param output_name:
    :param gdal_path:
    :return:
    """
    print("#######################################################")
    print("creating multichannel image")
    print("#######################################################")


    #gdall_calc only processes a single band at a time, so we need to merge all images for each band and save them to separate images before merging them to a multichannel image

    print("now we can merge the images with")
    print("gdal_merge -separate -o outputfilename inputfiename1 inputfilename2 inputfilename3 ..")
    merge_channels([str(path) for path in channel_images],output_file_path= str(pathlib.Path(output_folder)/ (output_name+"_allbands_" "_calc_merged_probs" + ".tif")),gdal_path=gdal_path)
    print("merged channels are stored in : "+str(pathlib.Path(output_folder)/ (output_name+"_allbands_" "_calc_merged_probs" + ".tif")))



def main(args):



    if args.Debug:
        print("merging the proibabiliteis of a few small handselected images")
        add_probabilities([r"T:\logs_and_models\befastelse\orthoimages_iteration_31_linux\models\1km2\PROBS_O2021_84_40_1_0045_00093310_7000_0.tif",r"T:\logs_and_models\befastelse\orthoimages_iteration_31_linux\models\1km2\PROBS_O2021_84_40_1_0045_00093310_7000_2000.tif"],output_name= "c_name",gdal_path = args.Gdal_path,output_folder = args.Output_merged_preds_folder)
        input("the probabilities have now been added!")

    #lots of 1000x1000 croped probabilities-images are located in a folder
    #input_folder =r"T:\logs_and_models\befastelse\orthoimages_iteration_31\models\befaestelse_dataset_creation_test_2"

    #create a dictionary with the original image as key and a list of patches as value
    #e.g {"large_image_name_1.tif":["patch_1.tif","patch_2.tif",,,],}
    small_images_for_each_large_image = get_patches_per_large_image(args.Input_preds)
    large_images=[]
    for large_image in small_images_for_each_large_image:


        output_file_path= str(pathlib.Path(args.Mosaicked_preds_folder)/  large_image )
        if not args.Skip_combine_patches_to_mosaik:
            combine_patches(patches= small_images_for_each_large_image[large_image],output_file_path=output_file_path,gdal_path = args.Gdal_path)
            print("done merging patches to :"+output_file_path)
        large_images.append(output_file_path)


    #create a list with names for the images that store the separate channels
    nr_of_bands =gdal.Open((large_images[0])).ReadAsArray().shape[0]
    channel_images =[]
    bands = [str(band) for band in range(1,nr_of_bands+1)]
    output_name= "a_name"
    for band in bands:
        channel_images.append(str(pathlib.Path(args.Output_merged_preds_folder)/ (output_name+"band_"+band+ "_calc_merged_probs" + ".tif")))

    #create the images for holding the probabilities for each class
    if not args.Skip_add_overlapping_probs_to_single_image:
        #merge the resulting overlapping images to a single tiff file

        #first create separate images for each channel
        create_channel_images(large_images=large_images,channel_images=channel_images,bands=bands,gdal_path = args.Gdal_path)

        #then merge the channel images to a single multichannel image
        create_multichannel_image(channel_images=channel_images,output_folder=args.Output_merged_preds_folder,output_name= output_name,gdal_path = args.Gdal_path)

    if not args.Skip_create_pred_image:
        #also crate a prediction image for the area
        crate_predictions(channel_images,output_folder = args.Output_merged_preds_folder,gdal_path = args.Gdal_path)

if __name__ == "__main__":
    example_usage= r"python merge_all_images_probabilities.py -i path\to\folder\with\probs -o folder\to\save\merged\probs\in"
    print("########################EXAMPLE USAGE########################")
    print(example_usage)
    print("#############################################################")


    # Initialize parser
    parser = argparse.ArgumentParser()

    parser.add_argument("-i", "--Input_preds", help="path/to/folder/with/probs  ",required=True)
    parser.add_argument("-m", "--Mosaicked_preds_folder", help="path/to/folder/to/save/mosaicked/probs/in (crops from same images are recomined to a large image)",required=True)
    parser.add_argument("-o", "--Output_merged_preds_folder", help="path/to/folder/to/save/merged/probs/in",required=True)
    parser.add_argument("-g", "--Gdal_path", help="e.g C:/Program Files/QGIS 3.16.8>/apps/Python39/Scripts/",required=False,default =r"C:/Program Files/QGIS 3.16.8/apps/Python39/Scripts/" )

    parser.add_argument("--Skip_combine_patches_to_mosaik",required=False, action='store_true',default =False )
    parser.add_argument("--Skip_add_overlapping_probs_to_single_image",required=False, action='store_true',default =False)
    parser.add_argument("--Skip_create_pred_image",required=False, action='store_true',default =False)
    parser.add_argument("--Debug",required=False, action='store_true',default =False)




    args = parser.parse_args()
    main(args)

