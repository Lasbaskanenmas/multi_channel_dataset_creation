# Multi-Channel Dataset Creation for Semantic Segmentation

Use this repository to create semantic segmentation datasets by combining imagery and LiDAR data from multiple geospatial sources into unified multi-channel image datasets.  
Data and labels are cut into patches and dataset is divided into train and test/valid subsets while taking geographical overlap into consideration.
Code supports conversion of labeled polygons stored in GeoPackage files into GeoTIFF label images.  

The resulting datasets can be used for training and inference with [ML_sdfi_fastai2](https://github.com/SDFIdk/ML_sdfi_fastai2).

---

## Data Sources

The dataset combines the following georeferenced layers:

- **Orthophoto:** [GeoDanmark Orthophoto](https://datafordeler.dk/dataoversigt/geodanmark-ortofoto/)  
- **Oblique Camera (Ortho Version):** [LOD Images](https://dataforsyningen.dk/data/1036)  
- **Digital Terrain Model (DTM):** [Danmarks Højdemodel – DHM Raster Download](https://datafordeler.dk/dataoversigt/danmarks-hoejdemodel-dhm/dhm-fildownload-raster/)  
- **Digital Surface Model (DSM):** [Danmarks Højdemodel – DHM Raster Download](https://datafordeler.dk/dataoversigt/danmarks-hoejdemodel-dhm/dhm-fildownload-raster/)  

---

## Example Folder Structure

```
training_dataset/
  labels/
    large_labels/
      image-x.tif
  data/
    original_data/
      image-X_rgb.tif
      image-X_cir.tif
      image-X_OrtoRGB.tif
      image-X_OrtoCIR.tif
      image-X_DSM.tif
      image-X_DTM.tif
    rgb/
      image-X.tif
    cir/
      image-X.tif
    OrtoRGB/
      image-X.tif
    OrtoCIR/
      image-X.tif
    DSM/
      image-X.tif
    DTM/
      image-X.tif
```

Images located in the `original_data` folder will be renamed and distributed into the appropriate subfolders (`rgb`, `cir`, `OrtoRGB`, `OrtoCIR`, `DSM`, `DTM`).  
If `original_data` is empty, the tool will use existing images from these subfolders.

---

## Labels

Labels should be provided as **GeoPackages** containing polygon features marking different semantic areas.  
These will be rasterized into GeoTIFF label images during dataset creation.

---

## Installation

```bash
git clone https://github.com/rasmuspjohansson/multi_channel_dataset_creation.git
cd multi_channel_dataset_creation

conda env create -f environment.yml
conda activate multi-channel-env

# Install in editable mode so changes in the source code are reflected immediately
pip install -e .
```

---

## Usage

A small example dataset is included with this repository.  
You can generate a dataset using the example configuration:

```bash
python src/multi_channel_dataset_creation/create_dataset.py   --dataset_config configs/create_dataset_example_dataset.ini
```

To see all available options:

```bash
python src/multi_channel_dataset_creation/create_dataset.py -h
```

Creating label Images from a GeoPackage without further processing can be done with

```bash
python src/multi_channel_dataset_creation/geopackage_to_label_v2.py   --geopackage example_dataset/labels/example_dataset.gpkg   --input_folder example_dataset/data/rgb/   --output_folder example_dataset/labels/large_labels/   --atribute ML_CATEGORY
```

---

## 📘 Notes

- The tool is designed for geospatial datasets with consistent coordinate systems.  
- Each channel (RGB, CIR, OrthoRGB, OrthoCIR, DSM, DTM) should be aligned and georeferenced properly before processing.

---

