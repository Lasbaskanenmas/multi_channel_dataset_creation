# Creating a dataset for semantic segmentation into different kind of impervious surfaces

Prerequsites are:
	1. An arcgis project with the different areas marked up as polygons in a feature class.
	2. Orthografik images georefferenced orthografi

copy orto-versioner af alle lod billeder til local disk
for each iamge:
    get label for area
    get forors-orto-foto for area
    get lidar for area
	







work from https://sdfidk.github.io/SDFIPython/package.html and reate a package for befaestelse dataset creation

instead of devel .yml etc: instruct to install arcgis pro 
copy conda environment (typical in this folder) to this folder
activate environment
read this to change from requiremnts.txt to .yml and install directly from github (multichanel albumetations) https://stackoverflow.com/questions/19042389/conda-installing-upgrading-directly-from-github
install mamba install --file requirements.txt --channel fastchan --channel conda-forge --channel pytorch -y


after activating the mamba environment
python -m pip install -e .







I should also see if I can get mcdocs to work : see https://sdfidk.github.io/grf-programmel-overblik/
