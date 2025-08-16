# Multiclass Image Classification on Species Data

This project builds a **multiclass image classification pipeline** using species image data from the **Atlas of Living Australia (ALA)** and **iNaturalist** databases. It covers the full workflow from **data extraction** to **model training and evaluation**.

---

## Requirements

The project requires the following Python packages:

- pandas, numpy, matplotlib, seaborn  
- os, requests, tqdm  
- scikit-learn, copy  
- torch, torchvision  
- geopandas, opencv-python (cv2)  
- Pillow (PIL), imagehash  
- collections  

Install dependencies via:

```bash
pip install -r requirements.txt

# Folder structure
├── data/
│   ├── raw/                    # Unprocessed images & CSVs from ALA/iNaturalist
│   ├── processed/              # Cleaned, resized, augmented images
│   └── metadata/               # CSVs with metadata, species lists
├── notebooks/
│   ├── 01-eda.ipynb            # Exploratory Data Analysis
│   └── modeling.ipynb          # Model training & evaluation
├── src/
│   ├── data_extraction.py
│   ├── iNaturalist_data_extraction.py
│   ├── data_cleaning.py
│   ├── preprocessing.py
│   ├── data_split.py
│   └── label_generation.py
└── README.md
# Create the below folder for storing data
├── data/
│   ├── raw/                    # Unprocessed images & CSVs from ALA/iNaturalist
│   ├── processed/              # Cleaned, resized, augmented images
│   └── metadata/               # CSVs with metadata, species lists

# Run below Bash Script for data download
python src/data_extraction.py
python src/iNaturalist_data_extraction.py

# Run below Bash Script for data cleaning
python scripts/data_cleaning.py

# Run below Bash Script for Preprocessing & Augmentation
python scripts/preprocessing.py

# Run below Bash Script to Split dataset into train, test, and validation sets:
python scripts/data_split.py

# Run below Bash script to Generate class labels for training:
python scripts/label_generation.py

# For data visualisation and analysis run below notebook
notebooks/01-eda.ipynb

# For modeling and classification evaluation run below notebook
notebooks/modeling.ipynb
