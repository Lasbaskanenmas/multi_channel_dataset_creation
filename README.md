# Creating a dataset for semantic segmentation of impervious surfaces
Combining images from different sources with lidar data into a single multi-channel image dataset
## Prerequsites are:
Software
- Conda-environment from ArcGIS pro installation

Data
- Georeferenced Orthophoto (https://datafordeler.dk/dataoversigt/geodanmark-ortofoto/)
- Georeferenced ortho-version of the downward facing camera("lod-billede") from oblique images(https://dataforsyningen.dk/data/1036)
- Georeferenced Ortho-TIN-image of lidar "extra-bytes" of type deviation

Labels
- An ArcGIS project with the different areas marked up as polygons in a feature class



## Installation 
git clone https://github.com/rasmuspjohansson/befaestelse_dataset_creation.git

cd befaestelse_dataset_creation

conda activate *your_arcgis_pro_environment*

#####install the library in 'editable' mode. Editable mode makes sure that a change in the code also updates the installed version of the code  
pip install -e .


## Quickstart

*update the config files in the config folder to point to your own data*

python src\befaestelse_dataset_creation\create_dataset.py

## Importing the library and calling it from another program
>from befaestelse_dataset_creation import create_dataset, create_label_images,create_orthofoto_images,create_lidar_images,split,create_text_files
##
create_dataset.main()
##you can also do the different steps one by one like this

## Create large labels for each "lod image"
create_label_images.main("configs/template_create_labels.ini")
## Create one orthofoto image for each "lod image"
create_orthofoto_images.main("configs/template_create_orthofoto_images.ini")
## Create lidar-deviation image for each "lod image"
create_lidar_images.main("configs/template_create_lidar_images.ini")
## Split up all images and labels into smaller patches
split.main("configs/template_split.ini")
## Create text files that defines train and validations splits
create_text_files.main("configs/template_split.ini")

NOTES creating the folder structure:
if all your input data is in the same folder and have differetn names depending on the channel, you can move the files to separate folders and rename the files to have the same name like this
src\befaestelse_dataset_creation>python rename_files.py -i T:\trainingdata\befastelse\befaestelse_dataset_creation_test\data\large_lod_rgb-nir_images -o T:\trainingdata\befastelse\befaestelse_dataset_creation_test\data\large_lod_cir_images -r _cir.tif -n .tif -m --Only_consider_files_with_matching_names
The example above asumes that we have images that contain rgb information e.g image1.tif and iamges that contain nir information e.g image1_cir.tif in the same folder.

TODO:
conversion to mask-DINO format
I should also see if I can get mcdocs to work : see https://sdfidk.github.io/grf-programmel-overblik/
