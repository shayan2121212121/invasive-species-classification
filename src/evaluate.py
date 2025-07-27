import os
import requests
import pandas as pd
from tqdm import tqdm

def rebuild_metadata_from_existing_images(species_name: str):
    # Setup paths
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    image_dir = os.path.join('/Users/mdshayan/Desktop/invasive-species-classifier', "data", "raw", species_name.replace(" ", "_").lower())
    metadata_path = os.path.join('/Users/mdshayan/Desktop/invasive-species-classifier', "data", "metadata", species_name.replace(" ", "_").lower(), "metadata.csv")
    os.makedirs(os.path.dirname(metadata_path), exist_ok=True)

    # List all image files
    image_files = [f for f in os.listdir(image_dir) if f.lower().endswith(".jpg")]
    occurrence_ids = [os.path.splitext(f)[0] for f in image_files]

    if not occurrence_ids:
        print("❌ No images found to rebuild metadata.")
        return

    print(f"🧠 Rebuilding metadata for {len(occurrence_ids)} existing images...")

    metadata = []
    batch_size = 200
    for i in tqdm(range(0, len(occurrence_ids), batch_size), desc="Fetching metadata"):
        batch_ids = occurrence_ids[i:i + batch_size]
        ids_param = ",".join(batch_ids)
        
        try:
            url = f"https://api.inaturalist.org/v1/observations"
            params = {
                "id": ids_param,
                "per_page": batch_size
            }
            response = requests.get(url, params=params, timeout=20)
            response.raise_for_status()
            observations = response.json().get("results", [])
        except Exception as e:
            print(f"⚠️ Failed to fetch metadata batch: {e}")
            continue

        for obs in observations:
            obs_id = str(obs["id"])
            filename = f"{obs_id}.jpg"
            file_path = os.path.join(image_dir, filename)
            if not os.path.exists(file_path):
                continue

            coords = obs.get("geojson", {}).get("coordinates", [None, None])
            image_url = obs["photos"][0]["url"].replace("square", "original") if obs.get("photos") else None

            metadata.append({
                "occurrenceID": obs_id,
                "scientificName": species_name,
                "imageURL": image_url,
                "decimalLatitude": coords[1],
                "decimalLongitude": coords[0],
                "eventDate": obs.get("observed_on"),
                "dataResourceName": "iNaturalist",
                "imageFile": os.path.relpath(file_path, start=project_root)
            })

    # Save metadata to CSV
    if metadata:
        df = pd.DataFrame(metadata)
        df.to_csv(metadata_path, index=False)
        print(f"✅ Rebuilt metadata with {len(df)} records: {metadata_path}")
    else:
        print("⚠️ No valid metadata could be reconstructed.")

# Example use
if __name__ == "__main__":
    rebuild_metadata_from_existing_images("Vulpes vulpes")  # Replace with your species
