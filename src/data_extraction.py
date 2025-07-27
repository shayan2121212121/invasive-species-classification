import os
import requests
from tqdm import tqdm
import pandas as pd
import time


def get_species_guid(species_name):
    """
    Fetch the LSID (GUID) for a species name from ALA's BIE API.
    """
    search_url = f"https://bie.ala.org.au/ws/search.json?q={species_name}"
    try:
        response = requests.get(search_url)
        response.raise_for_status()
        results = response.json().get("searchResults", {}).get("results", [])
        if results:
            return results[0].get("guid")
        else:
            print(f"No GUID found for species: {species_name}")
            return None
    except Exception as e:
        print(f"Failed to retrieve GUID: {e}")
        return None


def clean_filename(s):
    """
    Cleans strings to be safe filenames.
    """
    return "".join(c if c.isalnum() else "_" for c in s)


def sanitize_species_name(name):
    return name.lower().replace(" ", "_")


def download_species_images(species_name, max_records=5000):
    species_safe = sanitize_species_name(species_name)
    image_dir = f"data/raw/{species_safe}"
    metadata_dir = f"data/metadata/{species_safe}"
    metadata_file = os.path.join(metadata_dir, "metadata.csv")

    # Check or create folders
    if os.path.exists(image_dir):
        print(f"Image folder already exists: {image_dir}")
    else:
        os.makedirs(image_dir)
        print(f"Created image folder: {image_dir}")

    if os.path.exists(metadata_dir):
        print(f"Metadata folder already exists: {metadata_dir}")
    else:
        os.makedirs(metadata_dir)
        print(f"Created metadata folder: {metadata_dir}")

    # Load existing metadata if available
    if os.path.exists(metadata_file):
        existing_df = pd.read_csv(metadata_file)
        existing_ids = set(existing_df["occurrenceID"].astype(str).tolist())
        print(f"Found {len(existing_ids)} previously downloaded records.")
    else:
        existing_df = pd.DataFrame()
        existing_ids = set()

    # Step 1: Get species GUID
    guid = get_species_guid(species_name)
    if not guid:
        return

    print(f"🔎 GUID for '{species_name}': {guid}")

    # Step 2: Paginated fetch
    downloaded = 0
    start = 0
    step = 1000
    new_metadata = []

    while downloaded < max_records:
        url = (
            f"https://biocache.ala.org.au/ws/occurrences/search"
            f"?q=lsid:{guid}&mediaType=Image&pageSize={step}&start={start}"
        )
        try:
            response = requests.get(url)
            response.raise_for_status()
            occurrences = response.json().get("occurrences", [])
            if not occurrences:
                break

            for occ in occurrences:
                if downloaded >= max_records:
                    break

                occ_id = str(occ.get("occurrenceID"))
                if not occ_id or occ_id in existing_ids:
                    continue  # Skip already downloaded

                image_urls = occ.get("imageUrls", [])
                if not image_urls:
                    continue

                for j, image_url in enumerate(image_urls):
                    try:
                        filename = f"{clean_filename(occ_id)}.jpg"
                        filepath = os.path.join(image_dir, filename)

                        if os.path.exists(filepath):
                            print(f"📷 Image already exists: {filename}")
                            break

                        img_data = requests.get(image_url, timeout=10)
                        img_data.raise_for_status()

                        with open(filepath, "wb") as f:
                            f.write(img_data.content)

                        new_metadata.append({
                            "occurrenceID": occ_id,
                            "scientificName": occ.get("scientificName"),
                            "imageURL": image_url,
                            "decimalLatitude": occ.get("decimalLatitude"),
                            "decimalLongitude": occ.get("decimalLongitude"),
                            "eventDate": occ.get("eventDate"),
                            "dataResourceName": occ.get("dataResourceName"),
                            "imageFile": filename
                        })

                        existing_ids.add(occ_id)
                        downloaded += 1
                        break  # Only first image per record

                    except Exception as e:
                        print(f"⚠️ Image download failed: {image_url} - {e}")
                        continue

            print(f"[Batch] Fetched {len(occurrences)} records, Total new: {downloaded}")
            start += step
            time.sleep(1)

        except Exception as e:
            print(f"API request failed at start={start}: {e}")
            break

    # Save or append metadata
    if new_metadata:
        new_df = pd.DataFrame(new_metadata)
        combined_df = pd.concat([existing_df, new_df], ignore_index=True)
        combined_df.to_csv(metadata_file, index=False)
        print(f"\n Appended {len(new_df)} new records to: {metadata_file}")
    else:
        print("No new valid image records found.")


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python3 src/data_extraction.py <species_name> [max_records]")
        sys.exit(1)

    species_name = sys.argv[1]
    max_records = int(sys.argv[2]) if len(sys.argv) > 2 else 1000

    print(f"\nDownloading images and metadata for: {species_name}")
    download_species_images(species_name, max_records=max_records)
