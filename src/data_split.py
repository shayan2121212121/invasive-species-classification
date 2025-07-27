import pandas as pd
from sklearn.model_selection import train_test_split
import os

# Load labeled metadata
df = pd.read_csv("/Users/mdshayan/Desktop/invasive-species-classifier/data/metadata_labels/image_labels.csv")

# Stratified split by species_id
train_val, test = train_test_split(df, test_size=0.15, stratify=df['species_id'], random_state=42)
train, val = train_test_split(train_val, test_size=0.1765, stratify=train_val['species_id'], random_state=42)  # 0.1765 * 0.85 ≈ 15%

# Save splits
os.makedirs("/Users/mdshayan/Desktop/invasive-species-classifier/data/splits", exist_ok=True)
train.to_csv("/Users/mdshayan/Desktop/invasive-species-classifier/data/splits/train.csv", index=False)
val.to_csv("/Users/mdshayan/Desktop/invasive-species-classifier/data/splits/val.csv", index=False)
test.to_csv("/Users/mdshayan/Desktop/invasive-species-classifier/data/splits/test.csv", index=False)

print("Dataset split complete")