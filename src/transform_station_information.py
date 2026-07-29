"""Transform Citi Bike station-information data for BigQuery."""

from pathlib import Path
import json


PROCESSED_DIR = Path("data/processed")


def load_json(input_file: Path) -> dict:
    """Load a JSON file."""

    with input_file.open("r", encoding="utf-8") as file:
        return json.load(file)


def transform_station_records(data: dict) -> list[dict]:
    """Select and standardize station-information fields."""

    stations = data["data"]["stations"]
    transformed_rows = []

    for station in stations:
        transformed_rows.append(
            {
                "station_id": station["station_id"],
                "station_name": station["name"],
                "latitude": station["lat"],
                "longitude": station["lon"],
                "capacity": station.get("capacity"),
                "region_id": station.get("region_id"),
                "physical_configuration": station.get(
                    "physical_configuration"
                ),
            }
        )

    return transformed_rows


def save_ndjson(rows: list[dict], output_file: Path) -> None:
    """Save records as newline-delimited JSON."""

    output_file.parent.mkdir(parents=True, exist_ok=True)

    with output_file.open("w", encoding="utf-8") as file:
        for row in rows:
            file.write(json.dumps(row))
            file.write("\n")


def main() -> None:
    """Transform the current station-information file."""

    input_file = Path("data/raw/station_information.json")
    output_file = PROCESSED_DIR / "station_information.ndjson"

    raw_data = load_json(input_file)
    transformed_rows = transform_station_records(raw_data)

    save_ndjson(transformed_rows, output_file)

    print("Station-information transformation completed successfully.")
    print(f"Rows transformed: {len(transformed_rows):,}")
    print(f"Processed file: {output_file}")


if __name__ == "__main__":
    main()