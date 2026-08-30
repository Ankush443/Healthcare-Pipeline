import json
from pathlib import Path

import pandas as pd
import requests


API_URL = "https://api.fda.gov/drug/event.json"

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "app" / "data"

CSV_PATH = DATA_DIR / "records.csv"
JSON_PATH = DATA_DIR / "records.json"

LIMIT = 100


def fetch_data():
    """Fetch adverse drug event records from the openFDA API."""

    params = {
        "limit": LIMIT
    }

    response = requests.get(API_URL, params=params, timeout=30)
    response.raise_for_status()

    return response.json().get("results", [])


def transform_data(records):
    """Clean and transform raw API records."""

    cleaned_records = []

    for index, record in enumerate(records, start=1):
        patient = record.get("patient", {})

        drugs = patient.get("drug", [])
        reactions = patient.get("reaction", [])

        drug_names = [
            drug.get("medicinalproduct")
            for drug in drugs
            if drug.get("medicinalproduct")
        ]

        reaction_names = [
            reaction.get("reactionmeddrapt")
            for reaction in reactions
            if reaction.get("reactionmeddrapt")
        ]

        cleaned_records.append(
            {
                "id": index,
                "received_date": record.get("receivedate"),
                "patient_age": patient.get("patientonsetage"),
                "patient_sex": patient.get("patientsex"),
                "drugs": ", ".join(drug_names) if drug_names else "Unknown",
                "reactions": ", ".join(reaction_names)
                if reaction_names
                else "Unknown",
                "serious": int(record.get("serious", 0)),
                "country": record.get("occurcountry", "Unknown"),
            }
        )

    return cleaned_records


def save_data(records):
    """Save processed records as CSV and JSON."""

    DATA_DIR.mkdir(parents=True, exist_ok=True)

    dataframe = pd.DataFrame(records)

    dataframe.to_csv(CSV_PATH, index=False)

    with open(JSON_PATH, "w", encoding="utf-8") as file:
        json.dump(records, file, indent=2)

    print(f"Saved {len(records)} records.")
    print(f"CSV:  {CSV_PATH}")
    print(f"JSON: {JSON_PATH}")


def main():
    print("Fetching healthcare data...")

    raw_records = fetch_data()

    print(f"Fetched {len(raw_records)} records.")

    processed_records = transform_data(raw_records)

    save_data(processed_records)


if __name__ == "__main__":
    main()