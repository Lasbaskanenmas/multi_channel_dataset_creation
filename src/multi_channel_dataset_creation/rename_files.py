import os
import argparse
import pathlib
import shutil

def main(inputfolder,outputfolder,replacestring,newstring,only_consider_files_with_matching_names,move_instead_of_copy):
    files = os.listdir(inputfolder)
    total_files = len(files)
    for (index,file) in enumerate(files):
        #print("working on file :"+str(index) + " out of :"+str(len(files)))
        completion_percentage = (index / total_files) * 100
        print(f'\rProcessing file {str(index)}/{total_files} - {completion_percentage:.2f}%', end='', flush=True)
        input_path = pathlib.Path(inputfolder)/pathlib.Path(file)
        output_path = pathlib.Path(outputfolder)/pathlib.Path(file.replace(replacestring,newstring))
        if only_consider_files_with_matching_names and replacestring not in file:
            pass
        else:
            if move_instead_of_copy:
                shutil.move(input_path,output_path)
            else:
                shutil.copy2(input_path,output_path)
        print("done")


if __name__ == "__main__":
    """
    copy files from a folder to another 
    gives the files new names by replacing part of its name with a new string
    
    if your code assumes that all data sources and labels have the same name for the same area this script is handy to use for changing the names to the correct format
    """



    usage_example="example usage: \n "+r"python rename_files.py --inputfolder path\to\folder --outputfolder path\to\folder --replacestring originalstring --newstring newstring"
    # Initialize parser
    parser = argparse.ArgumentParser(
        epilog=usage_example,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("-i", "--inputfolder", help="path\to\folder",required=True)
    parser.add_argument("-o", "--outputfolder", help="path\to\folder",required=True)
    parser.add_argument("-r", "--replacestring", help="e.g original_image",required=True)
    parser.add_argument("-n", "--newstring", help="e.g new_image_copy",required=True)
    parser.add_argument('-m','--move_instead_of_copy',
                        help='should we move the file isntead of copying it? -m-> True , no -m -> False: ',action = 'store_true',default=False)
    parser.add_argument('--Only_consider_files_with_matching_names',
                        help='Only_consider_files_with_matching_names?',action = 'store_true',default=False)


    args = parser.parse_args()

    main(args.inputfolder,args.outputfolder,args.replacestring,args.newstring,args.only_consider_files_with_matching_names,args.move_instead_of_copy)
