from datetime import datetime, timezone
from pathlib import Path
import glob
import json


RAW_PATTERN = "data/raw/station_status_*.json"
PROCESSED_DIR = Path("data/processed")


def find_latest_raw_file() -> Path:
    """Find the newest timestamped raw station-status file."""

    files = glob.glob(RAW_PATTERN)

    if not files:
        raise FileNotFoundError("No timestamped raw station-status files found.")

    return Path(max(files))


def load_json(file_path: Path) -> dict:
    """Load a JSON file into Python."""

    with file_path.open("r", encoding="utf-8") as file:
        return json.load(file)


def unix_to_iso(timestamp: int) -> str:
    """Convert a Unix timestamp into an ISO UTC timestamp."""

    return datetime.fromtimestamp(
        timestamp,
        tz=timezone.utc,
    ).isoformat()


def transform_station_records(data: dict, source_file: Path) -> list[dict]:
    """Flatten station records into BigQuery-ready rows."""

    collected_at = data["pipeline_metadata"]["collected_at_utc"]
    stations = data["data"]["stations"]

    transformed_rows = []

    for station in stations:
        row = {
            "station_id": station["station_id"],
            "num_bikes_available": station["num_bikes_available"],
            "num_bikes_disabled": station["num_bikes_disabled"],
            "num_docks_available": station["num_docks_available"],
            "num_docks_disabled": station["num_docks_disabled"],
            "is_installed": station["is_installed"],
            "is_renting": station["is_renting"],
            "is_returning": station["is_returning"],
            "last_reported": unix_to_iso(station["last_reported"]),
            "legacy_id": station["legacy_id"],
            "num_ebikes_available": station["num_ebikes_available"],
            "num_scooters_available": station.get(
                "num_scooters_available", 0
            ),
            "num_scooters_unavailable": station.get(
                "num_scooters_unavailable", 0
            ),
            "eightd_has_available_keys": station[
                "eightd_has_available_keys"
            ],
            "collected_at_utc": collected_at,
            "source_file": source_file.name,
        }

        transformed_rows.append(row)

    return transformed_rows


def save_ndjson(rows: list[dict], output_file: Path) -> None:
    """Save rows as newline-delimited JSON."""

    output_file.parent.mkdir(parents=True, exist_ok=True)

    with output_file.open("w", encoding="utf-8") as file:
        for row in rows:
            file.write(json.dumps(row) + "\n")


def main() -> None:
    raw_file = find_latest_raw_file()
    raw_data = load_json(raw_file)

    rows = transform_station_records(raw_data, raw_file)

    output_file = (
        PROCESSED_DIR / raw_file.name.replace(".json", ".ndjson")
    )

    save_ndjson(rows, output_file)

    print(f"Transformed {len(rows):,} rows")
    print(f"Saved processed data to {output_file}")


if __name__ == "__main__":
    main()