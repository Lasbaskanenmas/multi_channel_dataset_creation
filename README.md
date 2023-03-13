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

## Folder structure
Place you ortho versions of the "lod images" here
*your_dataset*/large_images/name1.tif
## Create large labels for each "lod image"
python create_labels.py path/to/config.ini
## Create one orthofoto image for each "lod image"
python create_orthofoto_images.py
## Create lidar-deviation image for each "lod image"
python create_lidar_images.py

## Split up all images and labels into smaller patches
python split.py width 1000 height 1000
	







work from https://sdfidk.github.io/SDFIPython/package.html and reate a package for befaestelse dataset creation

instead of devel .yml etc: instruct to install arcgis pro 
copy conda environment (typical in this folder) to this folder
activate environment
read this to change from requiremnts.txt to .yml and install directly from github (multichanel albumetations) https://stackoverflow.com/questions/19042389/conda-installing-upgrading-directly-from-github
install mamba install --file requirements.txt --channel fastchan --channel conda-forge --channel pytorch -y


after activating the mamba environment
python -m pip install -e .







I should also see if I can get mcdocs to work : see https://sdfidk.github.io/grf-programmel-overblik/
