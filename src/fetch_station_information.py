"""Fetch and save Citi Bike station-information data."""

from datetime import datetime, timezone
from pathlib import Path
import json

import requests
from google.cloud import storage


STATION_INFORMATION_URL = (
    "https://gbfs.citibikenyc.com/gbfs/en/station_information.json"
)

BUCKET_NAME = "citibike-operations-colin-2026-data"


def fetch_station_information() -> dict:
    """Request the latest Citi Bike station-information data."""

    response = requests.get(STATION_INFORMATION_URL, timeout=30)
    response.raise_for_status()

    return response.json()


def validate_station_information(data: dict) -> int:
    """Validate the response and return the number of stations."""

    if "data" not in data:
        raise ValueError("Response is missing the 'data' field.")

    if "stations" not in data["data"]:
        raise ValueError("Response is missing the 'stations' field.")

    stations = data["data"]["stations"]

    if not isinstance(stations, list):
        raise TypeError("'stations' must be a list.")

    if len(stations) == 0:
        raise ValueError("The station list is empty.")

    required_fields = {"station_id", "name", "lat", "lon"}

    for station in stations:
        missing_fields = required_fields - station.keys()

        if missing_fields:
            raise ValueError(
                f"Station is missing required fields: {missing_fields}"
            )

    return len(stations)


def add_collection_metadata(data: dict) -> dict:
    """Add pipeline collection metadata."""

    data["pipeline_metadata"] = {
        "collected_at_utc": datetime.now(timezone.utc).isoformat(),
        "source": STATION_INFORMATION_URL,
    }

    return data


def build_output_file() -> Path:
    """Create the local station-information file path."""

    return Path("data/raw/station_information.json")


def save_json(data: dict, output_file: Path) -> None:
    """Save station-information JSON locally."""

    output_file.parent.mkdir(parents=True, exist_ok=True)

    with output_file.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=2)


def upload_to_cloud_storage(local_file: Path) -> str:
    """Upload station information to Cloud Storage."""

    client = storage.Client()
    bucket = client.bucket(BUCKET_NAME)

    blob_name = f"reference/{local_file.name}"
    blob = bucket.blob(blob_name)
    blob.upload_from_filename(local_file)

    return f"gs://{BUCKET_NAME}/{blob_name}"


def main() -> None:
    """Fetch, validate, save, and upload station information."""

    station_data = fetch_station_information()
    station_count = validate_station_information(station_data)
    station_data = add_collection_metadata(station_data)

    output_file = build_output_file()
    save_json(station_data, output_file)

    cloud_path = upload_to_cloud_storage(output_file)

    print("Station-information fetch completed successfully.")
    print(f"Station count: {station_count:,}")
    print(f"Local file: {output_file}")
    print(f"Cloud Storage path: {cloud_path}")


if __name__ == "__main__":
    main()