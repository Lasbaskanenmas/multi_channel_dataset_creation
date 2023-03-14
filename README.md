# Creating a dataset for impervious surfaces - semantic segmentation
Combining images from different sources with lidar data into a single dataset with multi-channel images.
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


#Quickstart

update the config files in the config folder to point to your own data


python
from befaestelse_dataset_creation import create_label_images,create_orthofoto_images,create_lidar_images,split,create_text_files
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









work from https://sdfidk.github.io/SDFIPython/package.html and reate a package for befaestelse dataset creation

instead of devel .yml etc: instruct to install arcgis pro 
copy conda environment (typical in this folder) to this folder
activate environment
read this to change from requiremnts.txt to .yml and install directly from github (multichanel albumetations) https://stackoverflow.com/questions/19042389/conda-installing-upgrading-directly-from-github
install mamba install --file requirements.txt --channel fastchan --channel conda-forge --channel pytorch -y


after activating the mamba environment
python -m pip install -e .







I should also see if I can get mcdocs to work : see https://sdfidk.github.io/grf-programmel-overblik/
