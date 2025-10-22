# Creating a dataset for semantic segmentation based on multi-channel images
Combining images and lidar data from different sources into a single multi-channel image dataset.
Also handle conversion of labels stored as geopackage files plygon featureclass into geotiff label-images. 
The finnished dataset is meant to be used for training and inference with  https://github.com/SDFIdk/ML_sdfi_fastai2 
 

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
          rgb:
            image-X.tif
          cir:
            image-X.tif          
          OrtoRGB:
            image-X.tif          
          OrtoCIR:
            image-X.tif         
          DSM:
            image-X.tif
          DTM:
            image-X.tif            
          
Images in original_data will be renamed and moved to the rgb, cir, OrtoRGB, OrtoCIR, DSM and DTM folders.

If no images exists in original_data folder, images in  rgb, cir, OrtoRGB, OrtoCIR, DSM and DTM folders will be used instead.

Labels
- A geopackage with different areas marked up with polygons



## Installation 
git clone https://github.com/rasmuspjohansson/multi_channel_dataset_creation.git

cd multi_channel_dataset_creation

conda env create -f environment.yml

conda activate multi-channel-env

Install the library in 'editable' mode. Editable mode makes sure that a change in the code also updates the installed version of the code  
pip install -e .



## Usage
A small example dataset is included withy this repo. The following comand works on the provided example dataset

python src/multi_channel_dataset_creation/create_dataset.py --dataset_config configs/create_dataset_example_dataset.ini

For more help on the usage type
python src/multi_channel_dataset_creation/create_dataset.py -h

An example on how to create label images from a geopackage is:
python src/multi_channel_dataset_creation/geopackage_to_label_v2.py --geopackage example_dataset/labels/example_dataset.gpkg --input_folder example_dataset/data/rgb/




