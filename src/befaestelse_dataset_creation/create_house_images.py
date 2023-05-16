#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
from arcpy import env
from arcpy.sa import *
from PIL import Image
import configparser
import argparse
import arcpy
import pathlib
_all__ = ["createmasks"]


# PARAMETER-BESKRIVELSE
# source_path - Mappen der indeholder ortofotos, der skal danne ramme for maskefilerne
# destination_path - Mappen hvor maskefilerne skal placeres.
# feature_workspace - ArcGIS workspacet, hvor polygon-laget der skal laves masker af, ligger
# mask_featureclass - Navnet på laget
# category_field - Feltet der angiver pixelværdien for maskerne
# includeEmptyFiles - Flag der angiver om der skal laves en maskefil,
#   hvis der ikke er nogle polygoner (så bliver det bare en sort maskefil).
# outputCellSize - Sørg for at cellSize matcher ortofotos cellsize. Default er sat til 0.10

class CreateMasks:
    def __init__(self):
        pass
    """
    def __init__(self, source_path, destination_path, feature_workspace, mask_featureclass,
                 category_field, priority_field, includeEmptyFiles, outputCellSize):
        self.source_path = source_path
        self.destination_path = destination_path
#        self.extent = extent
        self.feature_workspace = feature_workspace
        self.mask_featureclass = mask_featureclass
        self.category_field = category_field
        self.priority_field = priority_field
        self.includeEmptyFiles = includeEmptyFiles
        self.outputCellSize = outputCellSize
    """



    def CreateMaskFile(self, source_path, raw_mask_folder,mask_folder, feature_workspace, mask_featureclass,
                 category_field, priority_field, includeEmptyFiles, outputCellSize,load_extnet_from_PIL=False,unknown_value2=9):
        """
        :param source_path: folder with images
        :param raw_mask_folder: folder were the raw masks should be stored masks
        :param mask_folder : folder where the final masks should be stored
        :param feature_workspace:
        :param mask_featureclass:
        :param category_field: ML_CAt
        :param priority_field: the name of the field/fælt in the featureclasse that tell us what priority the object has:  should be ''
        :param includeEmptyFiles: this should normally always be true
        :param outputCellSize:
        :param unknown_value2: the value given to the areas that are manualy labeled as unkown in arcgis (these should be reclassed to 0 to be mergd with the areaas that dont have any labels)
        :return: maskfile: path to label
        """
        maskfile = ""
        arcpy.env.overwriteOutput = False

        arcpy.CheckOutExtension("Spatial") # TAGER EN LICENS FRA ARCGIS - I starten af main !!!
        i=0
        #num_files = len(fnmatch.filter(os.listdir(source_path),'*.tif')) # Tæl antallet af billeder, der skal behandles
        emptyImages = []
        #print("Antal billedfiler der skal behandles: " + str(num_files))
        mask_count = 0

        os.makedirs(raw_mask_folder,exist_ok=True)

        os.makedirs(mask_folder,exist_ok=True)

        file = source_path # Loop igennem alle filer i folderen med ortofotos.
        basename = os.path.basename(file)
        if basename.upper().endswith('.PNG') or basename.upper().endswith('.TIF') or basename.upper().endswith('.JPG'):
            i=i+1
            #Since teh label allready is moved into pixel koordinates, we want to use the image shape as extent
            Image.MAX_IMAGE_PIXELS = 933120000 #to alow pil to open large immages
            (width,heigh) = Image.open(file).size
            rasterImg = arcpy.Raster(file)  # Åben foto
            rasterExtent = rasterImg.extent
            #If image still is georefferenced we need to calculate a non-georefferenced extent


            if load_extnet_from_PIL:
                """
                Some images are georefferenced even after the removal of the .tfw file. Their extent are therfore in utm coordinates and can not be used to refference labels in pixel coordinates
                We therfore create a new extent based on the number of rows and collumns in the image instead
                """
                print("original rasterExtent:"+str(rasterExtent))
                half_pixel_offset= 0.5
                extend_from_PIL = [-half_pixel_offset,-(heigh-half_pixel_offset),(width-half_pixel_offset),half_pixel_offset]
                print("extend_from_PIL"+str(extend_from_PIL))
                #rasterExtent.YMin=-(heigh-half_pixel_offset)
                #rasterExtent.XMax=(width-half_pixel_offset)
                #rasterExtent.XMin = -half_pixel_offset
                #rasterExtent.YMax = half_pixel_offset
                rasterExtent = arcpy.Extent(-half_pixel_offset,-(heigh-half_pixel_offset),(width-half_pixel_offset),half_pixel_offset)
                print("rasterExtent with extent loaded from PIL:"+str(rasterExtent))

            extentString = str(rasterExtent).replace(' NaN NaN NaN NaN','')
            print("extentString: " + extentString)
            x = basename.upper().replace('.PNG','.tif').replace('.JPG','.tif').replace('.TIF','.tif')
            with arcpy.EnvManager(extent=rasterExtent):     # Sæt ortofotoets extent som default-extent i ArcGIS geoprocesserings-miljø.
                outputFile = raw_mask_folder + "\\" + x
                reclassFile = mask_folder + "\\" + x
                # bit_reclassFile = destination_path + "\\reclass\\bit_" + x
                print("Outputdestfile = " + outputFile)
                env.workspace = feature_workspace
                #env.cellSize = rasterImg;
                #env.cellSizeProjectionMethod = "PRESERVE_RESOLUTION";

                # Tæl antallet af objekter i fotoets extent (som er sat i geoprocesseringsmiljøet)
                object_count = int(str(arcpy.GetCount_management(mask_featureclass)))



                if object_count > 0:   # Hvis der er objekter, skal der beregnes masker.
                    arcpy.PolygonToRaster_conversion(mask_featureclass, category_field, outputFile, "CELL_CENTER", priority_field, outputCellSize)
                    rawMaskRaster = arcpy.Raster(outputFile)
                    emptyRaster = IsNull(rawMaskRaster)
                    reclassMaskRaster = Con(emptyRaster, 0, rawMaskRaster, "VALUE > 0")#make null values 0
                    #cone(if condition,then, else)

                    reclassMaskRaster = Con(reclassMaskRaster == unknown_value2, 0,reclassMaskRaster)  # all areas that are manually labeled as 'unnown' should get value 0
                    reclassMaskRaster.save(reclassFile)#save to new raster file
                    # arcpy.management.CopyRaster(reclassFile, bit_reclassFile, pixel_type = "1_BIT")
                    mask_count = mask_count+1
                elif includeEmptyFiles == 'TRUE':  # Hvis der ikke er objekter i extent, skal man alligevel danne masker, hvis includeEmptyFiles er sat
                    arcpy.PolygonToRaster_conversion(mask_featureclass, category_field, outputFile, "CELL_CENTER", priority_field, outputCellSize)   # Her kaldes geoprocesserings-toolet,
                    # der danner rasterbillede fra polygonlaget - i ortofotoets extent
                    rawMaskRaster = arcpy.Raster(outputFile)    # Resultatet af konverteringen åbnes
                    emptyRaster = IsNull(rawMaskRaster)         # Udvælg tomme pixels
                    reclassMaskRaster = Con(emptyRaster, 0, rawMaskRaster, "VALUE > 0") # Omkoder tomme pixels til værdien 0 (nul)

                    reclassMaskRaster = Con(reclassMaskRaster == unknown_value2, 0, reclassMaskRaster)  # all areas that are manually labeled as 'unnown' should get value 0
                    reclassMaskRaster.save(reclassFile)                                 # Gem filen med omkodningen i undermappe "/reclass"
                    mask_count = mask_count+1
                    emptyImages.append(basename)
                else:
                    emptyImages.append(basename)
                maskfile = reclassFile

        print("Færdig. Antal maskefiler dannet: " + str(mask_count) + " (der bliver ikke lavet maskefiler for billeder uden bygninger).")
        self.HandleEmptyImages(emptyImages)
        return maskfile

    # METODE DER HÅNDTERER HVAD DER SKAL SKE MED TOMME MASKEFILER (HVOR DER IKKE ER BYGNINGER I)
    # PARAMETER-BESKRIVELSE
    # emptyImages - liste over de bileder, der ikke indeholder bygninger.
    def HandleEmptyImages(self, emptyImages):
        if (len(emptyImages) == 0):
            print("Alle billedfiler indeholdt bygninger: ")
        else:
            print("Følgende billedfiler indeholdt ikke bygninger: ")    # Udskriver til skærm
            with open('EmptyImages.txt', 'w') as f:                     # Dan textfil der skal indeholde filnavnene
                for item in emptyImages:                                # loop gennem listen af navne
                    print(item)                                         # print filnavn til output
                    f.write("%s\n" % item)                              # skriv filnavn i textfil.



    """
    # HÅNDTERING AF INPUT-PARAMETRE
    if len(sys.argv) > 1:
        print ("Bruger input-parametre")
        InputWorkImgFolder = sys.argv[1]
        OutputWorkspace = sys.argv[2]
        inputworkspace = sys.argv[3]
        inputbygninger = sys.argv[4]
        categoryField = sys.argv[5]
        priorityField = sys.argv[6]
        includeemptyString = sys.argv[7]
        if includeemptyString.upper() == "TRUE":
            print("MEDTAGER BILLEDER UDEN BYGNINGER!!!")
            includeEmptyFiles = True
        else:
            includeEmptyFiles = False

        cellSizeString = sys.argv[8]
        if cellSizeString == "":
            inputCellSize = 0.16
        else:
            inputCellSize = float(cellSizeString)
    """


"""
source_path = r'C:\\Users\B028851\Documents\VTI\data\source\2020_84_40_10_0664.tif'
destination_path = r'F:\TEMP\PEMAC\Vector2Image\dest'
feature_workspace = r'C:\\Users\B028851\Documents\ArcGIS\Projects\VITrans\dagi_ma_bygning.gdb'
mask_featureclass = 'dagi_px_bygninger_i_ramme'
category_field = 'ML_CAT'
priority_field = 'ML_PRIORITY'
includeEmptyFiles = 'TRUE'
outputCellSize = 0.10
cm = CreateMasks(source_path, destination_path, feature_workspace, mask_featureclass, category_field, priority_field, includeEmptyFiles, outputCellSize)
cm.CreateMaskFile()
"""
def main(config):
    ini_parser = configparser.ConfigParser()
    ini_parser.read(config)
    section = "SETTINGS"

    mask_featureclass = ini_parser[section]["house_featureclass"]

    raw_mask_folder = ini_parser[section]["raw_mask_folder_houses"]
    mask_folder = ini_parser[section]["mask_folder_houses"]

    image_folder = ini_parser[section]["images_that_define_areas_to_create_labels_for"]

    arcpy_workspace = ini_parser[section]['arcpy_workspace_buldings']
    category_field= ini_parser[section]['category_field']
    priority_field= ini_parser[section]['category_field'] #it does not matter what polygon that is prioritized so we just need a number
    includeEmptyFiles= ini_parser[section]['includeEmptyFiles']
    outputCellSize= float(ini_parser[section]['outputCellSize'])
    unknown_value2 = int(ini_parser[section]['unknown_value2'])
    create_masks_obj= CreateMasks()




    images = os.listdir(image_folder)
    nr_of_images = len(images)
    for (index,im) in enumerate(images):
        print("workign on image:"+str(im) + " index :"+str(index) + " out of a totall of:"+str(nr_of_images) + " images")


        im_path = str(pathlib.Path(image_folder)/pathlib.Path(im))
        print("im_path:"+str(im_path))

        #mask_path = str(pathlib.Path(raw_mask_folder))
        create_masks_obj.CreateMaskFile(source_path=im_path, raw_mask_folder= raw_mask_folder,mask_folder=mask_folder, feature_workspace=arcpy_workspace, mask_featureclass=mask_featureclass,
                                        category_field=category_field, priority_field=priority_field, includeEmptyFiles=includeEmptyFiles, outputCellSize=outputCellSize,load_extnet_from_PIL=False,unknown_value2=unknown_value2)



if __name__ == "__main__":
    """
    
    Creates masks given .ini file with : paths to images ,gdb-file, mask_featureclass, and folder for masks.
    
    
    """

    usage_example="example usage: \n "+r"python createmasks.py --config path\to\file.ini"
    # Initialize parser
    parser = argparse.ArgumentParser(
        epilog=usage_example,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("-c", "--config", help="one or more paths to config file",nargs ='+',required=True)
    args = parser.parse_args()
    main(args.config)



    #TO DO!!!
