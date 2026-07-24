from datetime import datetime, timezone
from pathlib import Path
import json

import requests


STATION_STATUS_URL = (
    "https://gbfs.citibikenyc.com/gbfs/en/station_status.json"
)


def build_output_file() -> Path:
    """Create a timestamped raw-data file path."""

    collected_at = datetime.now(timezone.utc)

    timestamp = collected_at.strftime("%Y-%m-%d_%H-%M-%S")

    return Path(f"data/raw/station_status_{timestamp}.json")

def fetch_station_status() -> dict:
    """Request the latest Citi Bike station-status data."""

    response = requests.get(STATION_STATUS_URL, timeout=30)

    response.raise_for_status()

    return response.json()

def validate_station_status(data: dict) -> int:
    """Validate the station-status response and return the station count."""

    if "data" not in data:
        raise ValueError("Response is missing the 'data' field.")

    if "stations" not in data["data"]:
        raise ValueError("Response is missing the 'stations' field.")

    stations = data["data"]["stations"]

    if not isinstance(stations, list):
        raise TypeError("'stations' must be a list.")

    if len(stations) == 0:
        raise ValueError("The station list is empty.")

    return len(stations)

def add_collection_metadata(data: dict) -> dict:
    """Add pipeline metadata without changing the station records."""

    data["pipeline_metadata"] = {
        "collected_at_utc": datetime.now(timezone.utc).isoformat(),
        "source": STATION_STATUS_URL,
    }

    return data

def save_json(data: dict, output_file: Path) -> None:
    """Save JSON data to a local file."""

    output_file.parent.mkdir(parents=True, exist_ok=True)

    with output_file.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=2)


def main() -> None:
    station_data = fetch_station_status()
    station_count = validate_station_status(station_data)

    station_data = add_collection_metadata(station_data)

    output_file = build_output_file()
    save_json(station_data, output_file)

    print(f"Saved {station_count:,} station records to {output_file}")


if __name__ == "__main__":
    main()