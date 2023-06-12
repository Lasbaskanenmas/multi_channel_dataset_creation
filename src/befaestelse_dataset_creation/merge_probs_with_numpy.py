import os
import pathlib
import numpy as np
import argparse
import time
import rasterio
from PIL import Image
from osgeo import ogr
from rasterio.crs import CRS

def save_tiff(numpy_array,path,shape_file,meter_per_pixel = 0.1):
    """
    Save an array as GEotif based on a shapefile for the area covered
    :param numpy_array:
    :param path:
    :param shape_file: e.g C:/Users/b199819/Desktop/imageshape.shp
    :return:
    """



    #extract the coordinates form the shapefile that defines the area we have made a map over
    #when creating a geotif we want the coordinates for the upper left corner.
    # the shapefile lists 5 points [(x1,y1),(x2,y2),(x3,y3),(x4,y4),(x1,y1)] coresponding to lower left ,upper left ,upper right ,lower right and lower left
    #in order to get the coordinate for teh upper left we extract x2 and y2

    shapefile = ogr.Open(shape_file)
    layer = shapefile.GetLayer()
    #print("coordinates in shapefile :"+str([f.GetGeometryRef().ExportToWkt() for f in layer][0].replace("(","").replace(","," ").split()))

    #after splitting we get this format
    # ['POLYGON', '724000', '6175000', '724000', '6176000', '725000', '6176000', '725000', '6175000', '724000', '6175000))']
    #in order to get (x2,y2) we need to extract the item at position 3 and 4
    coord_1=int([f.GetGeometryRef().ExportToWkt() for f in layer][0].replace("(","").replace(","," ").split()[3])
    coord_2=int([f.GetGeometryRef().ExportToWkt() for f in layer][0].replace("(","").replace(","," ").split()[4])


    if len(numpy_array.shape)==2:
        #ad an extra dimension of there only are 2
        #rasterios write operation demans a 3dim array
        numpy_array= np.expand_dims(numpy_array,axis=0)

    number_of_bands, height, width = numpy_array.shape
    #print("input array shape:"+str(numpy_array.shape))
    #print("input array max:"+str(numpy_array.max()))
    #print("input array min:"+str(numpy_array.min()))




    #print("input array max:"+str(numpy_array.max()))


    kwargs = {'driver': 'GTiff', 'dtype': numpy_array.dtype, 'nodata': None, 'width': width, 'height': height, 'count': number_of_bands, 'crs': CRS.from_epsg(25832), 'transform': rasterio.Affine(meter_per_pixel, 0.0, coord_1, 0.0, -meter_per_pixel, coord_2)}

    with rasterio.open(path, 'w', **kwargs) as dst:
        dst.write(numpy_array)


    print("saved file: "+str(path))




def merge_with_numpy(shape_file,image_folder=r"C:\Users\b199819\Desktop\process_block_output\croped_1km2_mosaiks_3",output_folder = r"C:\Users\b199819\Desktop\process_block_output\numpy_merged_3"):

    merge_with_numpy_start = time.time()
    summed = np.zeros([11,10000,10000])
    pathlib.Path(output_folder).mkdir(parents=True, exist_ok=True)
    image_paths = [pathlib.Path(image_folder)/im_name for im_name in os.listdir(image_folder)]
    print("merging "+str(len(image_paths))+ " files with numpy")

    for im in image_paths:
        print("opening image : "+str(im))
        #append the numpy array version of the data
        try:
            summed = summed +rasterio.open(im).read()
        except:
            print("failed to read :"+str(im))



    merge_with_numpy_done_opening = time.time()



    pred = summed.argmax(axis=0).astype(np.uint8)
    print("pred.shape:"+str(pred.shape))

    save_tiff(summed.argmax(axis=0).astype(np.uint8),(pathlib.Path(output_folder)/ ("preds"+ pathlib.Path(shape_file).name)).with_suffix(".tif") ,shape_file=shape_file)
    #save_tiff(summed,(pathlib.Path(output_folder)/ ("probs"+ pathlib.Path(shape_file).name)).with_suffix(".tif") ,shape_file=shape_file)

    '''


    rgb = np.transpose(summed[0:3],(1,2,0))

    max=rgb.max()
    min=rgb.min()


    as_numpy = np.array(((rgb-min)/(max-min))*255,dtype=np.uint8)
    print(as_numpy.shape)
    print(as_numpy)

    Image.fromarray(as_numpy).save(output_folder+"\\RGBsummed6.tif")
    print("wrote summed data to: "+str(output_folder+"\\RGBsummed6.tif"))
    Image.fromarray(summed.argmax(axis=0).astype(np.uint8)).save(output_folder+"\\predictions6.tif")
    print("wrote predictions  data to: "+str(output_folder+"\\predictions6.tif"))
    '''

    merge_with_numpy_end = time.time()

    print("loading all images took :"+str(merge_with_numpy_done_opening - merge_with_numpy_start))

    print("merge_with_numpy took "+str(merge_with_numpy_end - merge_with_numpy_start))




def main(args):


    merge_with_numpy(shape_file=args.Shapefile,image_folder=args.Croped_mosaicked_preds_folder,output_folder = args.Output_merged_preds_folder)



if __name__ == "__main__":
    example_usage= r"python merge_probs_with_numpy.py -m T:\trainingdata\befastelse\1km2\croped_mosaiks -o T:\trainingdata\befastelse\1km2\merged_with_numpy"
    print("########################EXAMPLE USAGE########################")
    print(example_usage)
    print("#############################################################")

    # Initialize parser
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--Croped_mosaicked_preds_folder", help="path/to/folder/to/save/croped/mosaicked/probs/in (the mosaik are croped to fit the 1km2 tile)",required=True)
    parser.add_argument("-o", "--Output_merged_preds_folder", help="path/to/folder/to/save/merged/probs/in",required=True)
    parser.add_argument("-s", "--Shapefile", help="path/to/shapefile.sh",required=True)



    args = parser.parse_args()
    main(args)

