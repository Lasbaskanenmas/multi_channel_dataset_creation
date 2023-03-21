# Creating a dataset for impervious surfaces - semantic segmentation
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

pip install .


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



TODO:
conversion to mask-DINO format
I should also see if I can get mcdocs to work : see https://sdfidk.github.io/grf-programmel-overblik/
