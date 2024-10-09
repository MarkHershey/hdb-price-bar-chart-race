import csv
import json
from pathlib import Path
from typing import List

import requests
from rich import print

DATA_DIR = Path(__file__).resolve().parent / "data"
DATA_DIR.mkdir(exist_ok=True)


def update_collection(collectionId: int = 189) -> None:
    """
    Update the collection if it is not up-to-date.
    """
    collection_metadata_path = DATA_DIR / f"meta_collection_{collectionId}.json"
    if collection_metadata_path.exists():
        with collection_metadata_path.open() as f:
            collection_metadata = json.load(f)
            previous_last_updated = collection_metadata.get("lastUpdatedAt", "")
    else:
        previous_last_updated = ""

    url = f"https://api-production.data.gov.sg/v2/public/api/collections/{collectionId}/metadata"
    response = requests.get(url)
    response.raise_for_status()
    collection_metadata = response.json().get("data", {}).get("collectionMetadata")
    if not collection_metadata:
        raise ValueError("Collection Metadata Not Found!")

    last_updated = collection_metadata.get("lastUpdatedAt", "")
    if previous_last_updated != last_updated:
        print(f"Updating collection: {collectionId}")
        print(f"    Previous Last Updated: {previous_last_updated}")
        print(f"    Current Last Updated : {last_updated}")
        # save metadata
        with collection_metadata_path.open("w") as f:
            json.dump(collection_metadata, f, indent=4)
    else:
        print(f"Collection {collectionId} is up-to-date.")
        return

    child_dataset_ids: List[str] = collection_metadata.get("childDatasets", [])

    known_child = {
        "d_ebc5ab87086db484f88045b47411ebc5": 0,  # Resale Flat Prices (Based on Approval Date), 1990 - 1999
        "d_43f493c6c50d54243cc1eab0df142d6a": 1,  # Resale Flat Prices (Based on Approval Date), 2000 - Feb 2012
        "d_2d5ff9ea31397b66239f245f57751537": 2,  # Resale Flat Prices (Based on Registration Date), From Mar 2012 to Dec 2014
        "d_ea9ed51da2787afaf8e51f827c304208": 3,  # Resale Flat Prices (Based on Registration Date), From Jan 2015 to Dec 2016
        "d_8b84c4ee58e3cfc0ece0d773c8ca6abc": 4,  # Resale flat prices based on registration date from Jan-2017 onwards
    }

    for child in child_dataset_ids:
        if child in known_child:
            update_dataset(child)
        else:
            print(f"[WARNING] Unknown child dataset: {child}")


def update_dataset(datasetId: str) -> None:
    """
    Update the dataset if it is not up-to-date.
    """
    metadata_cache_path = DATA_DIR / f"meta_{datasetId}.json"
    data_filepath = DATA_DIR / f"{datasetId}.csv"
    if metadata_cache_path.exists() and data_filepath.exists():
        with metadata_cache_path.open() as f:
            metadata_cache = json.load(f)
            previous_last_updated = metadata_cache.get("lastUpdatedAt", "")
    else:
        previous_last_updated = ""
    # Get metadata
    url = f"https://api-production.data.gov.sg/v2/public/api/datasets/{datasetId}/metadata"
    response = requests.get(url, headers={})
    response.raise_for_status()
    data = response.json().get("data", {})
    lastUpdatedAt = data.get("lastUpdatedAt", "")
    if not lastUpdatedAt:
        raise ValueError("Unexpected Error: lastUpdatedAt not found!")

    if previous_last_updated != lastUpdatedAt:
        print(f"Updating dataset: {datasetId}")
        print(f"    Previous Last Updated: {previous_last_updated}")
        print(f"    Current Last Updated : {lastUpdatedAt}")
        # save metadata
        with metadata_cache_path.open("w") as f:
            json.dump(data, f)
    else:
        print(f"Dataset {datasetId} is up-to-date.")
        return

    # Download the dataset
    url = (
        f"https://api-open.data.gov.sg/v1/public/api/datasets/{datasetId}/poll-download"
    )
    response = requests.get(url, headers={"Content-Type": "application/json"}, json={})
    response.raise_for_status()
    data = response.json().get("data", {})

    # a status of "DOWNLOAD_SUCCESS" indicates that the file is ready for download
    _status = data.get("status", "")
    # a URL to download the file should be returned
    _url = data.get("url", "").strip()

    if _status == "DOWNLOAD_SUCCESS" and _url:
        print(f"Dowloading dataset: {datasetId}")
        # download file
        response = requests.get(_url)
        with data_filepath.open("wb") as f:
            f.write(response.content)
        print(f"Downloaded: {data_filepath}")
        return
    else:
        print(f"Failed to download dataset: {datasetId}")
        print(f"    Status: {_status}")
        print(f"    URL: {_url}")
        return


def get_data(force_update=False):
    if force_update:
        update_collection()

    known_child = {
        # "d_ebc5ab87086db484f88045b47411ebc5": 0,  # Resale Flat Prices (Based on Approval Date), 1990 - 1999
        # "d_43f493c6c50d54243cc1eab0df142d6a": 1,  # Resale Flat Prices (Based on Approval Date), 2000 - Feb 2012
        "d_2d5ff9ea31397b66239f245f57751537": 2,  # Resale Flat Prices (Based on Registration Date), From Mar 2012 to Dec 2014
        "d_ea9ed51da2787afaf8e51f827c304208": 3,  # Resale Flat Prices (Based on Registration Date), From Jan 2015 to Dec 2016
        "d_8b84c4ee58e3cfc0ece0d773c8ca6abc": 4,  # Resale flat prices based on registration date from Jan-2017 onwards
    }

    file_paths = [DATA_DIR / f"{datasetId}.csv" for datasetId in known_child.keys()]
    if not all([file_path.exists() for file_path in file_paths]):
        raise FileNotFoundError("Missing dataset files!")

    data = []
    for file_path in file_paths:
        with file_path.open() as f:
            reader = csv.DictReader(f)
            data.extend(list(reader))

    return data


if __name__ == "__main__":
    get_data(force_update=False)
