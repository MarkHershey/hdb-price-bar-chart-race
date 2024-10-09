import csv
import shutil
from pathlib import Path
from typing import *
from rich import print

from data_utils import get_data
from singapore import get_category_by_name

ROOT_DIR = Path(__file__).resolve().parent.parent
PUBLIC_DIR = ROOT_DIR / "bar-chart-race" / "public"
PUBLIC_DIR.mkdir(exist_ok=True)
DATA_DIR = Path(__file__).resolve().parent / "data"
DATA_DIR.mkdir(exist_ok=True)
CLEAN_CSV = DATA_DIR / "cleaned_data.csv"
RACE_CSV = DATA_DIR / "race_data.csv"


def get_clean_data(force_update=False):
    data: List[dict] = get_data(force_update=force_update)
    # we only keep month, town, floor_area_sqm, resale_price
    # and compute resale_price_per_sqm
    cleaned_data: List[dict] = []
    for row in data:
        cleaned_data.append(
            dict(
                month=row.get("month"),
                town=row.get("town"),
                floor_area_sqm=row.get("floor_area_sqm"),
                resale_price=row.get("resale_price"),
                resale_price_per_sqm=int(
                    float(row.get("resale_price")) / float(row.get("floor_area_sqm"))
                ),
            )
        )
    # sort by month
    cleaned_data.sort(key=lambda x: x["month"])
    # write to csv
    with CLEAN_CSV.open("w") as f:
        writer = csv.DictWriter(f, fieldnames=cleaned_data[0].keys())
        writer.writeheader()
        writer.writerows(cleaned_data)
        print(f"OK! Cleaned data written to {CLEAN_CSV}")
    del data

    return cleaned_data


def main(force_update=False):
    # ask user if they want to force update
    # if not force_update:
    #     force_update = (
    #         input("Force fetching the latest data from data.gov.sg? (y/n): ").lower()
    #         == "y"
    #     )

    # data = get_clean_data(force_update=force_update)
    data = get_clean_data(force_update=force_update)
    print(
        f"STATS: {len(data)} records dated from {data[0]['month']} to {data[-1]['month']}"
    )

    # get headers
    headers = set(data[0].keys())
    # print(f"Headers ({len(headers)}): {set(headers)}")
    assert "town" in headers
    assert "floor_area_sqm" in headers
    assert "month" in headers
    assert "resale_price" in headers
    assert "resale_price_per_sqm" in headers

    unique_towns = set([row["town"] for row in data])
    num_towns = len(unique_towns)
    # print(f"Unique towns ({num_towns}): {unique_towns}")
    assert num_towns == 26, "There should be 26 unique towns"

    target_headers = [
        "date",  # str: YYYY-MM-DD
        "name",  # str: town
        "value",  # int: resale_price_per_sqm
        "category",  # str: get_category_by_name(town)
    ]

    tmp_data_dict: Dict[str, Dict[str, List[int]]] = (
        {}
    )  # key: town, value: dict ( key: month, value: list of resale_price_per_sqm)
    race_data_rows: List[Dict[str, Union[str, int]]] = []

    # Compute resale price per sqm for each row
    for row in data:
        name = row["town"]
        date = f"{row['month']}-01"  # YYYY-MM to YYYY-MM-DD
        value = int(row["resale_price_per_sqm"])
        category = get_category_by_name(name)

        if category == "Unknown":
            print("Unknown category for", name)

        if name not in tmp_data_dict:
            tmp_data_dict[name] = {}
        if date not in tmp_data_dict[name]:
            tmp_data_dict[name][date] = []

        tmp_data_dict[name][date].append(value)

    # Compute average resale price per sqm for each month
    for name, date_dict in tmp_data_dict.items():
        for date in date_dict:
            avg_resale_price_per_sqm = sum(date_dict[date]) / len(date_dict[date])
            # overwrite value with avg_resale_price_per_sqm
            date_dict[date] = int(avg_resale_price_per_sqm)

    # unpack data in tmp_data_dict to race_data_rows
    for name, date_dict in tmp_data_dict.items():
        for date, value in date_dict.items():
            row = {
                "name": name,
                "date": date,
                "value": value,
                "category": get_category_by_name(name),
            }
            race_data_rows.append(row)

    num_data_rows = len(race_data_rows)
    print(f"Number of race data rows: {num_data_rows}")

    # write to new csv
    with RACE_CSV.open("w") as f:
        writer = csv.DictWriter(f, fieldnames=target_headers)
        writer.writeheader()
        writer.writerows(race_data_rows)
        print(f"OK! RACE DATA GENERATED/UPDATED AT: '{RACE_CSV}'")

    # copy to public folder
    print(f"Copying RACE DATA to public folder...")
    shutil.copy2(RACE_CSV, PUBLIC_DIR / "data.csv")
    print(f"OK! RACE DATA COPIED TO: '{PUBLIC_DIR / 'data.csv'}'")


if __name__ == "__main__":
    main(force_update=False)
