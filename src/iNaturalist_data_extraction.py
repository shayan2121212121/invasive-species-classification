import os
import requests
import pandas as pd
from tqdm import tqdm

def download_inaturalist_images(species_name: str, max_records: int = 1000):
    """
    Downloads iNaturalist images and appends matching metadata to metadata.csv,
    avoiding duplicates and only writing metadata after successful download.
    """

    # Prepare paths
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    image_dir = os.path.join(project_root, "data", "raw", species_name.replace(" ", "_").lower())
    metadata_path = os.path.join(project_root, "data", "metadata", "metadata.csv")
    os.makedirs(image_dir, exist_ok=True)
    os.makedirs(os.path.dirname(metadata_path), exist_ok=True)

    # Load existing metadata if exists
    if os.path.exists(metadata_path):
        existing_metadata = pd.read_csv(metadata_path)
        existing_ids = set(existing_metadata["occurrenceID"].astype(str))
    else:
        existing_metadata = pd.DataFrame()
        existing_ids = set()

    downloaded_count = 0
    metadata_to_append = []

    print(f"Searching iNaturalist for: {species_name}")
    url = "https://api.inaturalist.org/v1/observations"
    params = {
        "q": species_name,
        "place_id": "6744",  # Australia
        "per_page": 200,
        "photos": True,
        "verifiable": True,
        "page": 1
    }

    while downloaded_count < max_records:
        try:
            response = requests.get(url, params=params, timeout=15)
            response.raise_for_status()
            results = response.json().get("results", [])
        except Exception as e:
            print(f"Failed to fetch data: {e}")
            break

        if not results:
            break

        for obs in results:
            obs_id = str(obs["id"])
            if obs_id in existing_ids:
                continue  # skip duplicate

            if not obs.get("photos"):
                continue

            # Prepare image URL and filename
            image_url = obs["photos"][0]["url"].replace("square", "original")
            filename = os.path.join(image_dir, f"{obs_id}.jpg")
            relative_image_path = os.path.relpath(filename, start=project_root)

            if os.path.exists(filename):
                continue  # already downloaded image

            # Try downloading image
            try:
                img_data = requests.get(image_url, timeout=10).content
                with open(filename, "wb") as f:
                    f.write(img_data)
            except Exception as e:
                print(f"Image download failed for {image_url}: {e}")
                continue  # skip if download failed

            # Prepare metadata (only after successful download)
            coords = obs.get("geojson", {}).get("coordinates", [None, None])
            metadata_to_append.append({
                "occurrenceID": obs_id,
                "scientificName": species_name,
                "imageURL": image_url,
                "decimalLatitude": coords[1],
                "decimalLongitude": coords[0],
                "eventDate": obs.get("observed_on"),
                "dataResourceName": "iNaturalist",
                "imageFile": relative_image_path
            })

            downloaded_count += 1
            if downloaded_count >= max_records:
                break

        params["page"] += 1

    # Append metadata to CSV
    if metadata_to_append:
        df_new = pd.DataFrame(metadata_to_append)
        if not existing_metadata.empty:
            df_combined = pd.concat([existing_metadata, df_new], ignore_index=True)
        else:
            df_combined = df_new

        df_combined.to_csv(metadata_path, index=False)
        print(f"Added {len(df_new)} new records to metadata.csv")
    else:
        print("No new images were added.")



if __name__ == "__main__":
    download_inaturalist_images("Acridotheres tristis", max_records=5000)
