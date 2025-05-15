# LABIC-Image-Extractor

## About

This repository contains a script developed in Labic (Laboratório de Internet e Ciência de Dados) with non-commercial goals.

The script processes images and the corresponding JSON file exported from Label Studio. It organizes the images into folders based on the ID of the person who labeled them, with subdirectories for each assigned label.

## Installation

First, you need to clone the repository:
```bash
git clone https://github.com/joaoloss/LABIC-Image-Extractor.git
```
Enter the project's root directory:
```bash
cd LABIC-Image-Extractor
```
Then, create a virtual conda enviroment and activate it:
```bash
conda create -n labic-image-extractor python
conda activate labic-image-extractor
```
Lastly, install all requirements:
```bash
pip install -r requirements.txt
```

## Usage

To use the script you will need the `DatasetCrisis` directory and the `output_crisis.json` file in the root directory.

Then, you run the script with the command:
```bash
python ls_image_extractor.py -v <verbose_value>
```

- `-v` or `--verbose`: Sets the verbosity level: 0 (silent), 1 (normal), 2 (debug). 

All results will be stored in the `output` directory.