"""Run the Citi Bike raw-data fetch and transformation pipeline."""

from pathlib import Path

import requests
from google.cloud import bigquery, storage

from fetch_station_status import (
    BUCKET_NAME,
    add_collection_metadata,
    build_output_file,
    fetch_station_status,
    save_json,
    upload_to_cloud_storage,
    validate_station_status,
    verify_cloud_upload,
)
from transform_station_status import (
    PROCESSED_DIR,
    load_json,
    save_ndjson,
    transform_station_records,
)

BIGQUERY_DESTINATION_TABLE = (
    "citibike-operations-colin-2026."
    "citibike_operations.station_status"
)


def build_processed_output_file(raw_file: Path) -> Path:
    """Build an NDJSON path from the current run's raw filename."""

    return PROCESSED_DIR / raw_file.with_suffix(".ndjson").name


def upload_processed_to_cloud_storage(local_file: Path) -> str:
    """Upload a processed NDJSON file to the Cloud Storage processed zone."""

    client = storage.Client()
    bucket = client.bucket(BUCKET_NAME)

    blob_name = f"processed/{local_file.name}"
    blob = bucket.blob(blob_name)
    blob.upload_from_filename(local_file)

    return f"gs://{BUCKET_NAME}/{blob_name}"


def load_processed_to_bigquery(cloud_path: str) -> tuple[int, str]:
    """Append processed NDJSON from Cloud Storage to BigQuery."""

    client = bigquery.Client()
    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
        write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
    )

    load_job = client.load_table_from_uri(
        cloud_path,
        BIGQUERY_DESTINATION_TABLE,
        job_config=job_config,
    )
    load_job.result()

    return load_job.output_rows, load_job.job_id


def main() -> None:
    """Fetch, store, verify, and transform one station-status snapshot."""

    try:
        station_data = fetch_station_status()
        station_count = validate_station_status(station_data)
        station_data = add_collection_metadata(station_data)

        raw_file = build_output_file()
        save_json(station_data, raw_file)

        cloud_path = upload_to_cloud_storage(raw_file)
        verify_cloud_upload(raw_file, cloud_path)

        raw_data = load_json(raw_file)
        transformed_rows = transform_station_records(raw_data, raw_file)

        processed_file = build_processed_output_file(raw_file)
        save_ndjson(transformed_rows, processed_file)

        processed_cloud_path = upload_processed_to_cloud_storage(
            processed_file
        )
        verify_cloud_upload(processed_file, processed_cloud_path)

        rows_loaded, bigquery_job_id = load_processed_to_bigquery(
            processed_cloud_path
        )

    except requests.RequestException as error:
        print(f"API request failed: {error}")
        raise
    except OSError as error:
        print(f"Local file operation failed: {error}")
        raise
    except (KeyError, TypeError, ValueError) as error:
        print(f"Data validation or transformation failed: {error}")
        raise
    except Exception as error:
        print(f"Pipeline failed: {error}")
        raise

    print("Citi Bike pipeline completed successfully.")
    print(f"Station count: {station_count:,}")
    print(f"Raw local path: {raw_file}")
    print(f"Raw Cloud Storage path: {cloud_path}")
    print(f"Processed local path: {processed_file}")
    print(f"Processed Cloud Storage path: {processed_cloud_path}")
    print(f"BigQuery destination table: {BIGQUERY_DESTINATION_TABLE}")
    print(f"Number of rows loaded: {rows_loaded:,}")
    print(f"BigQuery job ID: {bigquery_job_id}")


if __name__ == "__main__":
    main()
