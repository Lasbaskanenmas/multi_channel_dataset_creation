import os

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

def combine_patches(patches,large_image_name,output_file_path = r"C:\Users\B152325\Desktop\befæstelse_status_2023\\"):
    gdal_merge_path = r'"C:/Program Files/QGIS 3.22.4/apps/Python39/Scripts/gdal_merge.py"'

    output_file_path= output_file_path+   large_image_name + ".tif"
    merge_argument = " ".join(patches)

    gdal_merge_process = "python "+gdal_merge_path +' -o '+'"'+output_file_path +'"'+" "+' -init 0 ' +merge_argument
    print(gdal_merge_process)
    print("merging :"+str(len(patches))+ " nr of images to "+output_file_path)
    # Call process.
    os.system(gdal_merge_process)
    print("done")

    return output_file_path

def add_probabilities(large_images,output_folder=r"C:\Users\B152325\Desktop\befæstelse_status_2023\\"):
    gdal_calc_path = r'"C:/Program Files/QGIS 3.22.4/apps/Python39/Scripts/gdal_calc.py"'

    input_args =[]

    A = 65
    Z = 90
    a = 97
    z= 122
    numbers = list(range(A,Z+1))+list(range(a,z+1))

    #limitinh number of images to process to number of images or gdal_calcs limit
    max_args= min(len(numbers),len(large_images))

    numbers = numbers[0:max_args]
    input_files=large_images[0:max_args]

    #numbers = [0:max_args]

    processed_nr=A-1
    for i in range(max_args):
        character = chr(numbers[i])
        input_args.append("-"+character+ " "+input_files[i])

    input(input_args)
    input_args = " ".join(input_args)
    input(input_args)

    calc_argument = "--calc " +'"' + "+".join([chr(i) for i in numbers])+ '"'
    input(calc_argument)

    #input_args = [input_file for input_file in input_files]

    # Arguements.

    #output_file_path = r"C:\Users\B152325\Desktop\befæstelse_status_2023\\"

    output_file_path=output_folder+   "calc_merged_probs" + ".tif"
    calc_expr = '"A + B"'
    typeof = '"Float32"'


    # Generate string of process.
    gdal_calc_str = 'python {0} -A {1} -B {2} --outfile={3} --calc={4} --type={5} --hideNoData'



    

    gdal_calc_process = "python "+gdal_calc_path +" "+input_args+' --outfile '+'"'+output_file_path +'"'+" "+calc_argument+' --type="Float32" --hideNoData --overwrite --extent=union'

    print(gdal_calc_process)
    print("gdal_calc running...")
    # Call process.
    os.system(gdal_calc_process)
    print("gdal_calc done")
    print("created: "+str(output_file_path))





def main(args):
    debug = True


    if debug:
        add_probabilities([r"C:\Users\B152325\Desktop\befæstelse_status_2023\PROBS_O2021_82_20_1_0023_00004975.tif",r"C:\Users\B152325\Desktop\befæstelse_status_2023\PROBS_O2021_82_20_1_0023_00004976.tif",r"C:\Users\B152325\Desktop\befæstelse_status_2023\PROBS_O2021_82_22_1_0032_00000909.tif"])
        input("the probabilities have now been added!")

    #lots of 1000x1000 croped probabilities-images are located in a folder
    #input_folder =r"T:\logs_and_models\befastelse\orthoimages_iteration_31\models\befaestelse_dataset_creation_test_2"

    #create a dictionary with the original image as key and a list of patches as value
    small_images_for_each_large_image = get_pathes_per_large_image(args.Input_preds)
    large_images=[]
    for large_image in small_images_for_each_large_image:
        output_path = combine_patches(patches= small_images_for_each_large_image[large_image],large_image_name = large_image,output_file_path=args.Mosaicked_preds_folder)
        input("done merging images to :"+output_path)
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

"""
gdal_calc_path = r'"C:/Program Files/QGIS 3.22.4/apps/Python39/Scripts/gdal_calc.py"'

#gdal_calc_path = os.path.join(gdal_path, 'gdal_calc.py')


input_folder =r"T:\logs_and_models\befastelse\orthoimages_iteration_31\models\befaestelse_dataset_creation_test_2"
input_files = os.listdir(input_folder)

#find all different image names
images ={}
for input_file in input_files:
    #input(input_file)
    image_name =  "_".join(input_file.split("_")[:-2])
    #input(image_name)
    if image_name in images:
        images[image_name].append(input_folder+"\\"+input_file)
    else:
        images[image_name] = [input_folder+"\\"+input_file]

for name in images:
    print(name+" have this many images:"+str(len(images[name])))
input("check out dictionary")
input(images)

input_files = images[large_file_name] #images["PROBS_O2021_84_40_1_0045_00093328"]




input(input_files)
input_args =[]



A = 65
Z = 90
a = 97
z= 122
numbers = list(range(A,Z+1))+list(range(a,z+1))

#limitinh number of images to process to number of images or gdal_calcs limit
max_args= min(len(numbers),len(input_files))

numbers = numbers[0:max_args]
input_files=input_files[0:max_args]

#numbers = [0:max_args]

processed_nr=A-1
for i in range(max_args):
    character = chr(numbers[i])
    input_args.append("-"+character+ " "+input_folder+"\\"+ input_files[i])

input(input_args)
input_args = " ".join(input_args)
input(input_args)

calc_argument = "--calc " +'"' + "+".join([chr(i) for i in numbers])+ '"'
input(calc_argument)

#input_args = [input_file for input_file in input_files]

# Arguements.
input_file_path = r"T:\logs_and_models\befastelse\orthoimages_iteration_31\models\befaestelse_dataset_creation_test_2\PROBS_O2021_82_19_1_0023_00005473_3000_4000.tif"
input_file_path2 = r"T:\logs_and_models\befastelse\orthoimages_iteration_31\models\befaestelse_dataset_creation_test_2\PROBS_O2021_82_19_1_0024_00005008_3000_5000.tif"

output_file_path = r"C:\Users\B152325\Desktop\befæstelse_status_2023\\"

output_file_path=output_file_path+   large_file_name + ".tif"
calc_expr = '"A + B"'
typeof = '"Float32"'


# Generate string of process.
gdal_calc_str = 'python {0} -A {1} -B {2} --outfile={3} --calc={4} --type={5} --hideNoData'



gdal_calc_process = gdal_calc_str.format(gdal_calc_path, input_file_path, input_file_path2,
                                         output_file_path, calc_expr, typeof)

gdal_calc_process = "python "+gdal_calc_path +" "+input_args+' --outfile '+'"'+output_file_path +'"'+" "+calc_argument+' --type="Float32" --hideNoData --overwrite --extent=union'

print(gdal_calc_process)
# Call process.
os.system(gdal_calc_process)
print("created: "+st(output_file_path))

"""