import csv
from pathlib import Path

import requests

DATA_DIR = Path(__file__).resolve().parent / "data"
DATA_DIR.mkdir(exist_ok=True)

# old: https://data.gov.sg/dataset/resale-flat-prices
# new: https://beta.data.gov.sg/collections/189/view
URI = "https://data.gov.sg/dataset/7a339d20-3c57-4b11-a695-9348adfd7614/download"

ZIP_PATH = DATA_DIR / "resale-flat-prices.zip"

# https://beta.data.gov.sg/datasets/d_2d5ff9ea31397b66239f245f57751537/view
CSV1 = DATA_DIR / "ResaleFlatPricesBasedonRegistrationDateFromMar2012toDec2014.csv"
# https://beta.data.gov.sg/datasets/d_ea9ed51da2787afaf8e51f827c304208/view
CSV2 = DATA_DIR / "ResaleFlatPricesBasedonRegistrationDateFromJan2015toDec2016.csv"
# https://beta.data.gov.sg/datasets/d_8b84c4ee58e3cfc0ece0d773c8ca6abc/view
CSV3 = DATA_DIR / "ResaleflatpricesbasedonregistrationdatefromJan2017onwards.csv"


def remove_download():
    # remove data if it exists
    print("Removing existing data...")
    if ZIP_PATH.exists():
        ZIP_PATH.unlink()
    if CSV1.exists():
        CSV1.unlink()
    if CSV2.exists():
        CSV2.unlink()
    if CSV3.exists():
        CSV3.unlink()
    print("Done! Previous download removed.")


def download_data():
    """
    Download data if it doesn't exist
    """
    if not CSV1.exists() or not CSV2.exists() or not CSV3.exists():
        print("Missing data files!")
        print(
            f"Please manually download the data from the link below and place it in {DATA_DIR}"
        )
        print("https://beta.data.gov.sg/collections/189/view")
    else:
        print("OK! Data files exist.")
    return
    if not ZIP_PATH.exists():
        try:
            response = requests.get(URI)
            with ZIP_PATH.open("wb") as f:
                f.write(response.content)
            print(f"OK! Downloaded data to {ZIP_PATH}")
        except Exception as e:
            print(f"Error: {e}")
    else:
        print(f"OK! Data already exists at {ZIP_PATH}")

    # unzip data if it doesn't exist
    if not CSV1.exists() or not CSV2.exists() or not CSV3.exists():
        try:
            import zipfile

            with zipfile.ZipFile(ZIP_PATH, "r") as zip_ref:
                zip_ref.extractall(DATA_DIR)
            print(f"OK! Data unzipped to {DATA_DIR}")
        except Exception as e:
            print(f"Error: {e}")
    else:
        print(f"OK! Data already unzipped at {DATA_DIR}")


def get_data(force_update=False):
    if force_update:
        # remove_download()
        ...
    # download data if it doesn't exist
    download_data()

    # merge three csv files into one
    with CSV1.open() as f1, CSV2.open() as f2, CSV3.open() as f3:
        reader1 = csv.DictReader(f1)
        reader2 = csv.DictReader(f2)
        reader3 = csv.DictReader(f3)
        # print(reader1.fieldnames)
        # print(reader2.fieldnames)
        # print(reader3.fieldnames)
        data = list(reader1) + list(reader2) + list(reader3)

    return data


if __name__ == "__main__":
    get_data(force_update=False)
