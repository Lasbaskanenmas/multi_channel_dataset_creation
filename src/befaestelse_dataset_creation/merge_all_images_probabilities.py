import os
import pathlib
import numpy as np
from osgeo import gdal
import argparse
import time
import rasterio
from PIL import Image



def get_patches_per_large_image(input_folder):
    """
    :param input_folder:
    :return: {"large_image_name_1.tif":{"pattern":"path/to/match/*.tif","patches":["patch_1.tif","patch_2.tif",,,]},}
    """
    input_files = os.listdir(input_folder)
    #find all different image names (the name of the image before it was splitted up)
    images ={}
    for input_file in input_files:

        image_name =  pathlib.Path("_".join(input_file.split("_")[:-2]) + ".tif")



        patch_path = input_folder+"\\"+input_file

        if image_name in images:
            images[image_name]["patches"].append(patch_path)
        else:
            images[image_name]={"patches":[patch_path],"pattern":str(input_folder/image_name.with_suffix(''))+"*.tif"}

    return images

def merge_channels(images,output_file_path,gdal_path= "None"):
    """
    combine all channels into a single multi-channel image
    """
    gdal_merge_path = '"'+gdal_path +'gdal_merge.py"'  # gdal_merge_path = r'"C:/Program Files/QGIS 3.22.4/apps/Python39/Scripts/gdal_merge.py"'

    pathlib.Path(output_file_path).parent.mkdir(parents=True, exist_ok=True)
    merge_argument = " ".join(images)

    gdal_merge_process = "python "+gdal_merge_path +' -separate -o '+'"'+output_file_path +'"'+" "+merge_argument
    print(gdal_merge_process)
    print("merging :"+str(len(images))+ " chanel-images to "+output_file_path)
    # Call process.
    os.system(gdal_merge_process)
    print("done")


def combine_patches(pattern,output_file_path = r"C:\Users\B152325\Desktop\befæstelse_status_2023\\",gdal_path = "None",use_gdalbuildvrt = True):
    """
    create a mosaik by combining all pathces to a single image
    process is faster with
    use_gdalbuildvrt = True

    batches are depricated and should be removed! TODO!
    """
    start_time = time.time()
    pathlib.Path(output_file_path).parent.mkdir(parents=True, exist_ok=True)

    #we use a vrt file as a temporary step before turning it into a geotiff
    output_file_path_buldvrt =str(pathlib.Path(output_file_path).parent /"tmp.vrt")
    #if it allready exists, remove it
    pathlib.Path(output_file_path_buldvrt).unlink(missing_ok=True)


    gdalbuildvrt = "gdalbuildvrt "
    gdal_merge_path = '"'+gdal_path +'gdal_merge.py"'  #r'"C:/Program Files/QGIS 3.22.4/apps/Python39/Scripts/gdal_merge.py"'








    gdalbuildvrt_process = gdalbuildvrt + output_file_path_buldvrt + " " + pattern

    if use_gdalbuildvrt:
        print(gdalbuildvrt_process)
        os.system(gdalbuildvrt_process)


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



    #clean up
    pathlib.Path(output_file_path_buldvrt).unlink(missing_ok=True)







def create_channel_images(large_images,channel_images,bands,gdal_path = "None"):
    """
    Crate one image for each segmentation class
    This operation use gdal_calc and can take some time...

    :param large_images:
    :param channel_images:
    :param bands:
    :param gdal_path:
    :return:
    """
    print(str(pathlib.Path(channel_images[0]).parent))
    pathlib.Path(channel_images[0]).parent.mkdir(parents=True, exist_ok=True)
    print("created folder?")
    print("#######################################################")
    print("creating channel-images")
    print("#######################################################")
    create_channels_start = time.time()
    for i_band in range(len(bands)):
        create_channel_start = time.time()
        band= bands[i_band]

        print("CREATING BAND: "+str(band) + " out of : "+str(len(bands)))


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
        print("gdal_calc running on "+str(len(input_files))+" overlapping images...")
        # Call process.
        os.system(gdal_calc_process)
        print("gdal_calc done")
        print("created: "+str(output_file_path))
        create_channel_end = time.time()
        print("creating channel took :"+str(create_channel_end-create_channel_start))
    create_channels_end = time.time()
    print("creating channels took :"+str(create_channels_end-create_channels_start))


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

def save_preds(path_to_probs,path_to_preds=None):
    if not path_to_preds:
        path_to_preds = pathlib.Path(path_to_probs).with_name(pathlib.Path(path_to_probs).name.replace(".tif","_pred.tif"))
    #Image.fromarray(np.array(rasterio.open(path_to_probs).read().argmax(axis=0),dtype=np.uint8)).save(path_to_preds)

    with rasterio.open(path_to_probs) as src:
        # make a copy of the geotiff metadata so we can save the prediction/probabilities as the same kind of geotif as the input image
        #load teh probs and do argmax in order to get predictions
        new_meta = src.meta.copy()
        new_xform = src.transform
        predictions = src.read().argmax(axis=0)

    new_meta["count"] = 1
    new_meta["dtype"] = np.uint8


    with rasterio.open(path_to_preds, "w", **new_meta) as dest:
        dest.write(np.expand_dims(predictions, axis=0))



def crop_to_same_shape(image_folder=r"C:\Users\b199819\Desktop\process_block_output\mosaik_1km1_1",shape_file_path= r"T:\trainingdata\befastelse\1km2\6175_724.shp",output_folder = r"C:\Users\b199819\Desktop\process_block_output\croped_1km2_mosaiks_3"):
    crop_start= time.time()
    image_paths = [pathlib.Path(image_folder)/im_name for im_name in os.listdir(image_folder)]


    #output_folder = r"T:\trainingdata\befastelse\1km2\croped_mosaiks"


    pathlib.Path(output_folder).mkdir(parents=True, exist_ok=True)
    for im in image_paths:
        #crop to shapefile
        output_path = str(pathlib.Path(output_folder)/im.name)
        # Call process.
        call= "gdalwarp -cutline "+shape_file_path+" -crop_to_cutline "+str(im)+" "+output_path
        os.system(call)
        #gdalwarp -cutline C:\Users\B152325\Desktop\croping_window\output.shp -crop_to_cutline "C:\Users\B152325\Desktop\1km2\PROBS_O2021_84_40_1_0045_00093316_0_5760.tif" C:\Users\B152325\Desktop\croping_window\output.tif

    #arr= np.array(images)
    #save to disk as geotif with rasterio
    #arr= np.sum(arr,axis=0)
    #predictions = np.argmax(arr,axis=0)
    #save to disk as geotif with rasterio
    crop_end= time.time()

    print("cropping took :"+str(crop_end-crop_start))






def main(args):
    main_start_time = time.time()



    #if args.Debug:
    #    #print("merging the proibabiliteis of a few small handselected images")
    #    #add_probabilities([r"T:\logs_and_models\befastelse\orthoimages_iteration_31_linux\models\1km2\PROBS_O2021_84_40_1_0045_00093310_7000_0.tif",r"T:\logs_and_models\befastelse\orthoimages_iteration_31_linux\models\1km2\PROBS_O2021_84_40_1_0045_00093310_7000_2000.tif"],output_name= "c_name",gdal_path = args.Gdal_path,output_folder = args.Output_merged_preds_folder)
    #    #input("the probabilities have now been added!")

    #lots of 1000x1000 croped probabilities-images are located in a folder
    #input_folder =r"T:\logs_and_models\befastelse\orthoimages_iteration_31\models\befaestelse_dataset_creation_test_2"

    #create a dictionary with the original image as key and a list of patches as value
    #e.g {"large_image_name_1.tif":["patch_1.tif","patch_2.tif",,,],}
    patches_and_patterns_dict = get_patches_per_large_image(args.Input_preds)



    large_images=[]
    print("##################################################")
    print("This script does the following operations:")
    print("1. combines the ML output for all patches related to a certain image into an inference image of the same shape as the original large-image")
    print("2. crops the resulting images to the area defined by a shape file (areas outside of the image is filled with zeros)")
    print("##################################################")

    print("nr of large images to produce:"+str(len(patches_and_patterns_dict)))
    print("####")
    for i, large_image  in enumerate(patches_and_patterns_dict):
        print("working on image :"+str(i)+ " out of :"+str(len(patches_and_patterns_dict)))
        patches=patches_and_patterns_dict[large_image]["patches"]
        pattern=patches_and_patterns_dict[large_image]["pattern"]
        print("nr of patches to combine :"+str(len(patches)))

        print("pattern that match the patches we want to process:"+str(pattern))

        output_file_path= str(pathlib.Path(args.Mosaicked_preds_folder)/  large_image )
        if not args.Skip_combine_patches_to_mosaik:
            combine_patches(pattern=pattern,output_file_path=output_file_path,gdal_path = args.Gdal_path)
            print("done merging patches to :"+output_file_path)
            if args.create_pred_image:
                save_preds(output_file_path)

        large_images.append(output_file_path)


    #crop the probability-images to fit the 1km2 tile
    crop_to_same_shape(image_folder=args.Mosaicked_preds_folder,shape_file_path=args.Shape_file,output_folder =args.Croped_mosaicked_preds_folder)

    main_finnished_mosaik_time = time.time()


    """



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
    main_finnished_multichannel_image_time = time.time()

    if not args.Skip_create_pred_image:
        #also create a prediction image for the area
        crate_predictions(channel_images,output_folder = args.Output_merged_preds_folder,gdal_path = args.Gdal_path)
        
        
    """
    main_finnished_prediction_image_time = time.time()
    print("########################DONE##################################################################################################")
    print("times:")
    print("totall : "+str(main_finnished_prediction_image_time-main_start_time))
    print("creating mosaik: "+str(main_finnished_mosaik_time-main_start_time))

    print("##############################################################################################################################")


if __name__ == "__main__":



    example_usage= r"python merge_all_images_probabilities.py -i path\to\folder\with\probs -o folder\to\save\merged\probs\in"
    print("########################EXAMPLE USAGE########################")
    print(example_usage)
    print("#############################################################")


    # Initialize parser
    parser = argparse.ArgumentParser()

    parser.add_argument("-i", "--Input_preds", help="path/to/folder/with/probs  ",required=True)
    parser.add_argument("-m", "--Mosaicked_preds_folder", help="path/to/folder/to/save/mosaicked/probs/in (crops from same images are recomined to a large image)",required=True)
    parser.add_argument("-c", "--Croped_mosaicked_preds_folder", help="path/to/folder/to/save/croped/mosaicked/probs/in (the mosaik are croped to fit the 1km2 tile)",required=True)

    # parser.add_argument("-o", "--Output_merged_preds_folder", help="path/to/folder/to/save/merged/probs/in",required=True)
    parser.add_argument("-g", "--Gdal_path", help="e.g C:/Program Files/QGIS 3.16.8>/apps/Python39/Scripts/",required=False,default =r"C:/Program Files/QGIS 3.16.8/apps/Python39/Scripts/" )

    parser.add_argument("--Skip_combine_patches_to_mosaik",required=False, action='store_true',default =False )
    #parser.add_argument("--Skip_add_overlapping_probs_to_single_image",required=False, action='store_true',default =False)
    parser.add_argument("--create_pred_image",required=False, action='store_true',default =False)
    parser.add_argument("--Debug",required=False, action='store_true',default =False)

    parser.add_argument("--Shape_file", help="path/to/file.shp",required=False,default =r"T:\trainingdata\befastelse\1km2\6175_724.shp" )






    args = parser.parse_args()
    main(args)

