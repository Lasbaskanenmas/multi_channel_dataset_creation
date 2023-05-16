import os
from PIL import Image
import numpy
import pandas as pd
import argparse
import pathlib




def _OBSELETE_create_all_txt_with_images_with_least_background(folder_path,datatype,all_filename,allowed_blocks,max_nr_of_images,label_folder_name = "labels/masks",images_folder_name= "images"):
    """
    :param folder_path: path to dataset folder
    :param datatype: e.g '.tif'
    :param all_filename: e.g 'esbjerg++'
        ('.xml' will be added to filename later to form 'esbjerg++.xml')
        (.txt will be added to create a file with all them images in the blocks)
        ("limited_all.txt" will be added to create a all.txt file that only includes the images with least background pixels)
    :param allowed_blocks: .eg ['83_25','83_26'] #only images in these blocks will beconsidered
    :param Max_nr_of_images: when creating a limited dataset we need to say max number of images to include ,images with much background will be omitted in the resulting datasetnamelimited_all.txt
    :return: None
    """

    labels =[0,1] #ad more labels if nececeary. e.g if we want to consider forst and lakes
    bins=labels+[labels[-1]] #ad last label +1 as uper bound for lastbin

    all_txt_filename =  all_filename + ".txt"
    all_xcel_filename = all_filename + ".xlsx"
    
    # 1. create a all.txt file that includes the paths to all images in the decired block-folders
    create_all_txt(folder_path, datatype, all_txt_filename, allowed_blocks)
    # 2. iterate over the images and save numberof pixels for each label in pandas dataframe
    pandas_dataframe = pd.DataFrame(columns=["path"]+labels)
    with open(all_txt_filename, 'r') as f:
        all_list = f.readlines()
    for i in range(len(all_list)):
        print("i:"+str(i),end="\r",flush=True)
        path= folder_path+ "/"+all_list[i].rstrip()
        im= Image.open(path)
        #im.show()
        label_path = path.replace(images_folder_name,label_folder_name)
        label= Image.open(label_path)
        numpy_label = numpy.array(label)
        label_im = Image.fromarray(numpy.clip( (numpy_label*100),0,255))
        #label_im.show()
        histogram= numpy.histogram(numpy_label,bins=bins)
        #print("histogram:"+str(histogram))
        #column_names=[]
        #column_values=[]
        row = {"path": path }
        for n_label_name in range(len(histogram)):
            label_name = histogram[1][n_label_name]
            #column_names.append(label_name)
            number_of_pixles = histogram[0][n_label_name]
            #column_values.append(number_of_pixles)
            row[label_name]=number_of_pixles


            # if there is no column for the label in the dataframe ,make one
            if not label_name in pandas_dataframe.columns:
                pandas_dataframe[label_name] = 0 #all old rows sould have 0 as value



        pandas_dataframe = pandas_dataframe.append(row, ignore_index=True)



    pandas_dataframe = pandas_dataframe.sort_values(by=[1])#image with least background/most labeled pixels e.g houses, first 
    #Image.open(pandas_dataframe.iloc[-1]["path"]).show()#show image with most buildings
    #print(pandas_dataframe.head) #show the paths to the images with least background
    try:
        pandas_dataframe.to_excel(all_xcel_filename)#save so we can do more things with this list if needed
    except:
        print("failed to save as excell")
    
    #pandas_dataframe=pd.read_excel(all_xcel_filename, index_col=0)  #if we want to load the saved excell sheet
    #only keep the label folder, remove the rest of the folders from the paths
    pandas_dataframe["path"]=pandas_dataframe["path"].apply(lambda x:"/".join(x.split("/")[-2:]))

    #remove al except the images with least background
    #save in csv/all.txt format (a csv file without headers and only one column is the same format as the all.txt files use)
    pandas_dataframe.iloc[-int(max_nr_of_images):]["path"].to_csv(all_txt_filename.replace(".txt","limited_all.txt"),header=False,index=False, sep='\t')
    



def verify_all_files_exists(file_name,folder_path,other_data_folders =[]):
    all_files_exists = True

<<<<<<< HEAD
    for data_folder in  other_data_folders:
        if not (pathlib.Path(data_folder)/file_name).is_file():
            print("missing file :"+str(pathlib.Path(data_folder)/file_name))
=======
    for other_data_folder in  other_data_folders:
        if not (other_data_folder/file_name).is_file():
            #(pathlib.Path(folder_path).parent/pathlib.Path(data_folder)/file_name).is_file():
>>>>>>> 1537e95b5b056ff10ea0720f2580f93513c3f4cb
            all_files_exists = False
            print("this file does not exist:"+str((other_data_folder/file_name)))
    #if no other data folders are used its enough that the initial file exists
    if not (pathlib.Path(folder_path)/file_name).is_file():
        all_files_exists = False
    #print("all_files_exists:"+str(all_files_exists))

    return all_files_exists






def create_all_txt(folder_path,datatype,all_txt_filename,other_data_folders=[]):
    """
    Create all.txt file with all image files included in the folder_path

    """

    input("verify")
    input(other_data_folders)
 
    #folder_path=folder_path.replace("//","/")
    folder_path = pathlib.Path(folder_path)

    print(folder_path)
    files_in_folder =os.listdir(folder_path)
    print(files_in_folder)


    
    files= [x for x in files_in_folder if datatype in x and ".xml" not in x and verify_all_files_exists(x,folder_path,other_data_folders)]

    

    print("number of image files in all: " + str(len(files)))
    print("first image: "+str(files[0]))

    
    with open(all_txt_filename, 'w') as f:
        f.write('\n'.join(files))
    print("printed the filenames to the file : " + all_txt_filename)

def create_valid_txt(all_txt_filename,valid_txt_filename,pick_every):
    with open(all_txt_filename, 'r') as f:
        all_list = f.readlines()
        valid_list=[]
        for i in range(0,len(all_list),pick_every):
            valid_list.append(all_list[i].split("/")[-1])
        with open(valid_txt_filename, 'w') as f:
            f.write(''.join(valid_list))
            print("number of files in valid: " + str(len(valid_list)) + "  == "+str(100*len(valid_list)/len(all_list)) +" % of images in all_txt_file")

            print("first elements in valid_list : " + str(valid_list[0]))
            print("printed the valid filenames to the file : " + valid_txt_filename)


def create_all_and_valid(all_txt_filename,valid_txt_filename,path_to_training_images,datatype,nr_of_images_between_validation_samples,other_data_folders=[]):

    create_all_txt(folder_path=path_to_training_images,datatype=datatype,all_txt_filename=all_txt_filename,other_data_folders=other_data_folders)
    create_valid_txt(all_txt_filename=all_txt_filename,valid_txt_filename=valid_txt_filename,pick_every=nr_of_images_between_validation_samples)
if __name__ == "__main__":
    usage_example="example usage: \n "+r"python create_all_and_valid_txt.py -f /mnt/trainingdata-disk/trainingdata/RoofTopOrto/images/ -a /mnt/trainingdata-disk/trainingdata//RoofTopOrto/esbjergplusplus/all.txt  -v  /mnt/trainingdata-disk/trainingdata//RoofTopOrto/esbjergplusplus/valid.txt -p 17 -d .tif --other_data_folders splitted_cir splitted_DSM splitted_DTM splitted_OrtoCIR splitted_OrtoRGB splitted_rgb"
    # Initialize parser
    parser = argparse.ArgumentParser(
                                    epilog=usage_example,
                                    formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("-f", "--Folder_path", help="path to dataset folder",required=True)
    parser.add_argument("-a", "--All_filename", help="all.txt filename .eg 'esbjerg++_all.txt'  -> esbjer++_all.txt and 'esbjerg++_all.xlsx'",required=True)
    parser.add_argument("-v", "--Valid_filename", help=".eg -v valid.txt",required=True)
    parser.add_argument("-d", "--Datatype", help=".eg -d .tif",required=True)
    parser.add_argument("-p", "--nr_of_images_between_validation_samples",type = int,default = 17, help=".eg pick every 17 when creating a validation set: -p 17",required=False)
    parser.add_argument("--other_data_folders", help="e.g [splitted_cir splitted_DSM splitted_DTM splitted_OrtoCIR splitted_OrtoRGB splitted_rgb] ", nargs='+', default=[],required=False)




    
    
    args = parser.parse_args()

    create_all_and_valid(all_txt_filename =args.All_filename,valid_txt_filename=args.Valid_filename,path_to_training_images=args.Folder_path,datatype=args.Datatype,nr_of_images_between_validation_samples=args.nr_of_images_between_validation_samples,other_data_folders=args.other_data_folders)


    #create_all_txt(folder_path=args.Folder_path,datatype=args.Datatype,all_txt_filename=args.All_filename,allowed_blocks=args.Allowed_blocks)
    





    #create_all_txt_with_images_with_least_background(folder_path=args.Folder_path,datatype=args.Datatype,all_filename=args.All_filename,allowed_blocks=args.Allowed_blocks,max_nr_of_images=args.Max_nr_of_images,label_folder_name=args.Labelsfoldername)
    #if args.Create_valid_txt:
    #    create_valid_txt(all_txt_filename=args.All_filename + 'limited_all.txt', valid_txt_filename=args.All_filename+"_valid.txt", pick_every=pick_every)


    """
    path_to_training_images = r'C:\mnt\trainingdata\rooftop_500p\images\\'
    all_txt_filename = "./all.txt"
    valid_txt_filename = "./valid.txt"
    allowed_blocks= ["83_25","83_26"]
    
    """
