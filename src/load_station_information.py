"""Load transformed station-information data into BigQuery."""

from pathlib import Path

from google.cloud import bigquery, storage


BUCKET_NAME = "citibike-operations-colin-2026-data"

BIGQUERY_DESTINATION_TABLE = (
    "citibike-operations-colin-2026."
    "citibike_operations.station_information"
)


def upload_processed_file(local_file: Path) -> str:
    """Upload processed station information to Cloud Storage."""

    client = storage.Client()
    bucket = client.bucket(BUCKET_NAME)

    blob_name = f"reference/{local_file.name}"
    blob = bucket.blob(blob_name)
    blob.upload_from_filename(local_file)

    return f"gs://{BUCKET_NAME}/{blob_name}"


def load_to_bigquery(cloud_path: str) -> tuple[int, str]:
    """Replace the BigQuery station-information table."""

    client = bigquery.Client()

    schema = [
        bigquery.SchemaField("station_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("station_name", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("latitude", "FLOAT", mode="REQUIRED"),
        bigquery.SchemaField("longitude", "FLOAT", mode="REQUIRED"),
        bigquery.SchemaField("capacity", "INTEGER"),
        bigquery.SchemaField("region_id", "STRING"),
        bigquery.SchemaField("physical_configuration", "STRING"),
    ]

    job_config = bigquery.LoadJobConfig(
        schema=schema,
        source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
    )

    load_job = client.load_table_from_uri(
        cloud_path,
        BIGQUERY_DESTINATION_TABLE,
        job_config=job_config,
    )

    load_job.result()

    return load_job.output_rows, load_job.job_id


def main() -> None:
    """Upload and load the transformed station-information file."""

    processed_file = Path("data/processed/station_information.ndjson")

    if not processed_file.exists():
        raise FileNotFoundError(
            "Processed station-information file was not found. "
            "Run transform_station_information.py first."
        )

    cloud_path = upload_processed_file(processed_file)
    rows_loaded, job_id = load_to_bigquery(cloud_path)

    print("Station-information load completed successfully.")
    print(f"Cloud Storage path: {cloud_path}")
    print(f"BigQuery table: {BIGQUERY_DESTINATION_TABLE}")
    print(f"Rows loaded: {rows_loaded:,}")
    print(f"BigQuery job ID: {job_id}")


if __name__ == "__main__":
    main()