# Creating a dataset for semantic segmentation based on multi-channel images
Combining images and lidar data from different sources into a single multi-channel image dataset.
Also handels conversion of labels stored as Arcgis plygon featureclass into label-images. 
The finnished dataset is meant to be used for training and inference with http://sdfe-git/ITU/ML/fastai2 or https://github.com/rasmuspjohansson/lightning
## Prerequsites are:
Software
- Conda-environment from ArcGIS pro installation (at the time of writing this only works on windows OS)
- You can alternatively create a fresh conda environment but the software will then not be able to create labels. It can howeverstill preprocess the data so they are ready for ML-inference. 

Data
- Georeferenced Orthophoto (https://datafordeler.dk/dataoversigt/geodanmark-ortofoto/)
- Georeferenced ortho-version of the downward facing camera("lod-billede") from oblique images(https://dataforsyningen.dk/data/1036)
- Georeferenced DTM
- Georeferenced DSM

## Example of folder structure:
    training_dataset:
      labels:
        large_labels:
          image-x.tif 
        data:
          original_data:		
            image-X_rgb.tif
            image-X_cir.tif
            image-X_OrtoRGB.tif
            image-X_OrtoCir.tif
            image-X_DSM.tif
            image-X_DTM.tif

Labels
- An ArcGIS project with the different areas marked up as polygons in a feature class



## Installation 
git clone https://github.com/rasmuspjohansson/multi_channel_dataset_creation.git

cd multi_channel_dataset_creation

conda activate *your_arcgis_pro_environment*
*alternatively create a fresh environment and activate it with * 
conda create -n multichannel python=3.8
conda activate multichannel

Install the library in 'editable' mode. Editable mode makes sure that a change in the code also updates the installed version of the code  
pip install -e .


## Usage example

python src/multi_channel_dataset_creation/create_dataset.py --config configs/create_dataset_example_dataset.ini
For more help on the usage type
python src/multi_channel_dataset_creation/create_dataset.py -h




