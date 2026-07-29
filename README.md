# Citi Bike Operations Platform

An automated cloud data pipeline and operations dashboard designed to monitor Citi Bike station availability, identify service issues, and prioritize stations requiring operational attention.

The platform collects live Citi Bike station data every hour, validates and transforms it with Python, stores historical snapshots in Google Cloud, analyzes station performance in BigQuery, and presents actionable metrics through a Looker Studio dashboard.

## Business Problem

Citi Bike operators need to know where bikes and open docks are unavailable so they can make better rebalancing and maintenance decisions.

A station with no available bikes prevents customers from beginning a trip. A station with no available docks prevents customers from ending one. Repeated availability problems can reduce customer satisfaction and indicate where operational resources should be prioritized.

This project answers the following questions:

* What is the current availability of bikes and docks across the system?
* Which stations currently have no bikes or no open docks?
* How does system availability change throughout the day?
* Which stations experience repeated service issues?
* Which stations should be prioritized for rebalancing or maintenance?

## Stakeholders

The dashboard is designed for:

* Operations managers monitoring system performance
* Rebalancing teams moving bikes between stations
* Maintenance teams investigating disabled bikes and docks
* Business leaders evaluating service reliability

## Project Architecture

```text
Cloud Scheduler
      |
      v
Cloud Run Job
      |
      v
Python Data Pipeline
      |
      |-- Fetch Citi Bike GBFS API data
      |-- Validate required fields
      |-- Save raw JSON
      |-- Transform data into NDJSON
      |-- Load station status snapshots
      |-- Refresh station reference information
      |
      v
Google Cloud Storage
      |
      |-- Raw station-status JSON
      |-- Processed station-status NDJSON
      |-- Station-information reference files
      |
      v
BigQuery
      |
      |-- Historical station-status table
      |-- Station-information table
      |-- Analytical SQL views
      |
      v
Looker Studio Dashboard
```

## Technology Stack

* **Python:** API extraction, validation, transformation, and loading
* **Google Cloud Storage:** Raw and processed data storage
* **BigQuery:** Historical storage, SQL analysis, KPI calculations, and reporting views
* **Cloud Run Jobs:** Containerized pipeline execution
* **Cloud Scheduler:** Hourly pipeline scheduling
* **Cloud Build:** Docker image creation and deployment
* **Artifact Registry:** Docker image storage
* **Looker Studio:** Interactive operations dashboard
* **Git and GitHub:** Version control and project documentation

## Data Sources

The project uses Citi Bike’s public General Bikeshare Feed Specification feeds.

### Station Status

Provides frequently updated operational data, including:

* Available bikes
* Available docks
* Disabled bikes
* Disabled docks
* Station activity status
* Station rental and return status
* Last reported timestamp

### Station Information

Provides station reference data, including:

* Station name
* Latitude and longitude
* Station capacity
* Region
* Physical station configuration

Approximately **2,462 stations** are processed during each pipeline run, although the total may change as the Citi Bike network changes.

## Automated Pipeline

The Cloud Scheduler triggers the Cloud Run Job every hour.

During each execution, the pipeline:

1. Requests the current station-status feed.
2. Checks that the API response contains the required structure and fields.
3. Adds pipeline timestamps to preserve when each snapshot was collected.
4. Saves the original response as raw JSON.
5. Uploads the raw file to Google Cloud Storage.
6. Transforms each station into a newline-delimited JSON record.
7. Uploads the processed file to Google Cloud Storage.
8. Appends the station snapshot to the historical BigQuery table.
9. Refreshes the station-information reference data.
10. Replaces the BigQuery station-information table with the latest reference records.

This design preserves historical station performance while keeping station names, locations, and capacity information current.

## Data Storage

### Cloud Storage Structure

```text
raw/
  station_status_YYYY-MM-DD_HH-MM-SS.json

processed/
  station_status_YYYY-MM-DD_HH-MM-SS.ndjson

reference/
  station_information.json
  station_information.ndjson
```

### BigQuery Tables

#### `station_status`

An append-only historical table containing one row per station for every hourly pipeline execution.

Important fields include:

* `station_id`
* `num_bikes_available`
* `num_docks_available`
* `num_bikes_disabled`
* `num_docks_disabled`
* `is_installed`
* `is_renting`
* `is_returning`
* `last_reported`
* `pipeline_timestamp`

#### `station_information`

A refreshed reference table containing:

* `station_id`
* `station_name`
* `latitude`
* `longitude`
* `capacity`
* `region_id`
* `physical_configuration`

## Analytical Views

The project uses BigQuery views to separate raw data storage from reporting logic.

### `station_status_clean`

Cleans the historical station-status data and creates standardized operational fields.

### `station_status_latest`

Returns the most recent record available for each station.

### `current_system_kpis`

Calculates system-wide metrics from the latest station snapshot.

### `current_station_issues`

Identifies stations currently experiencing operational problems.

### `hourly_system_trends`

Aggregates bike availability, dock availability, and service issues over time.

### `station_reliability_summary`

Measures historical issue frequency for each station.

### `station_priority_ranking`

Ranks stations using their historical operational risk.

### `station_operations_detail`

Joins station reliability results with station names, locations, capacity, and other reference information for dashboard reporting.

## Key Performance Indicators

### Total Stations

Number of stations included in the latest available snapshot.

### Active Stations

Number of stations currently installed, renting bikes, and accepting bike returns.

### Available Bikes

Total number of bikes currently available across active stations.

### Available Docks

Total number of open docks currently available across active stations.

### Bike Availability Rate

```text
available bikes /
(available bikes + available docks)
```

This measures the share of usable station capacity currently occupied by available bikes.

### Stations With No Bikes

Number of active stations where customers cannot currently begin a trip.

### Stations With No Open Docks

Number of active stations where customers cannot currently end a trip.

### Disabled Bike Rate

```text
disabled bikes /
(available bikes + disabled bikes)
```

This estimates the share of reported bikes that are unavailable because they are disabled.

## Station Reliability Metrics

### No Bikes Rate

Percentage of a station’s historical snapshots in which it had zero available bikes.

### No Docks Rate

Percentage of a station’s historical snapshots in which it had zero available docks.

### Average Disabled Bike Rate

Average share of disabled bikes recorded at a station across its historical snapshots.

### Priority Score

```text
priority score =
no bikes rate
+ no docks rate
+ average disabled bike rate
```

A higher score represents a station with more frequent availability or maintenance problems.

Stations with fewer than 10 active historical snapshots are labeled as having insufficient data to avoid ranking them using an unreliable sample.

## Dashboard

The Looker Studio report contains two pages.

### Page 1: Executive Overview

Provides a system-wide view of current performance and recent operational trends.

The page includes:

* Total stations
* Active stations
* Available bikes
* Available docks
* Bike availability rate
* Inactive stations
* Stations with no bikes
* Stations with no open docks
* Disabled bikes and docks
* Current system disabled-bike rate
* Hourly bike and dock availability
* Current station issues
* Hourly service-issue trends

### Page 2: Station Operations

Provides station-level information for operational investigation and prioritization.

The page includes:

* Station search control
* Geographic station operations map
* Selected-station details
* Station priority table
* Station capacity
* Priority score
* No bikes rate
* No docks rate
* Average disabled-bike rate
* Station reliability risk scatter plot

The scatter plot compares each station’s no-bikes rate and no-docks rate, with disabled-bike performance included as an additional risk measure.

## Data Quality and Validation

The pipeline includes checks to reduce the risk of incomplete or misleading analysis.

Validation steps include:

* Confirming successful API responses
* Checking for the required JSON structure
* Verifying that the station list is present
* Checking required station fields
* Recording the pipeline collection timestamp
* Comparing fetched, transformed, and loaded row counts
* Preserving raw source files for auditing
* Using append-only storage for historical station-status data
* Using replacement loading for current station-reference data
* Excluding incomplete location records from the dashboard detail view
* Requiring a minimum number of observations for station-priority classifications

A successful pipeline run currently processes approximately:

```text
2,462 station-status records
2,462 station-information records
```

## Repository Structure

```text
citibike-operations-platform/
|
|-- src/
|   |-- fetch_station_status.py
|   |-- transform_station_status.py
|   |-- load_station_status.py
|   |-- fetch_station_information.py
|   |-- transform_station_information.py
|   |-- load_station_information.py
|   |-- run_pipeline.py
|
|-- sql/
|   |-- BigQuery table and view queries
|
|-- data/
|   |-- raw/
|   |-- processed/
|
|-- Dockerfile
|-- requirements.txt
|-- README.md
```

Local data files are excluded from version control where appropriate to prevent generated files from unnecessarily increasing the repository size.

## Running the Pipeline Locally

### 1. Create and activate a virtual environment

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 2. Install dependencies

```powershell
pip install -r requirements.txt
```

### 3. Authenticate with Google Cloud

```powershell
gcloud auth application-default login
```

### 4. Run the complete pipeline

```powershell
python src/run_pipeline.py
```

A successful execution will load a new station-status snapshot and refresh the station-information table.

## Cloud Deployment

The project is packaged as a Docker container and deployed as a Cloud Run Job.

The current container image is stored in Artifact Registry and is built using Cloud Build.

Example deployment commands:

```powershell
gcloud builds submit `
  --tag us-east1-docker.pkg.dev/PROJECT_ID/citibike-pipeline/citibike-pipeline:v2
```

```powershell
gcloud run jobs update citibike-pipeline `
  --image us-east1-docker.pkg.dev/PROJECT_ID/citibike-pipeline/citibike-pipeline:v2 `
  --region us-east1
```

```powershell
gcloud run jobs execute citibike-pipeline `
  --region us-east1 `
  --wait
```

## Business Recommendations

The platform can support several operational actions:

1. Prioritize rebalancing at stations with consistently high no-bikes or no-docks rates.
2. Investigate maintenance needs at stations with elevated disabled-bike rates.
3. Adjust staffing and bike-moving schedules around recurring hourly demand patterns.
4. Compare priority scores with station capacity so high-volume locations receive appropriate attention.
5. Use station-level historical performance rather than relying only on current conditions.
6. Track whether operational interventions improve station reliability over time.

## Current Limitations

* The priority score is a transparent rule-based metric rather than a predictive model.
* Weather, events, ridership demand, and neighborhood characteristics are not currently included.
* Hourly snapshots may not capture short service interruptions between pipeline runs.
* Stations removed from the current station-information feed are not included in the location-based detail view.
* The dashboard identifies operational risk but does not optimize truck routes or bike-rebalancing quantities.

## Future Improvements

Possible future additions include:

* Weather data integration
* Daily and weekly demand patterns
* Station-level trip data
* Event and holiday indicators
* Borough and neighborhood analysis
* Automated pipeline failure alerts
* Rebalancing demand forecasts
* Anomaly detection
* Recommended bike-transfer quantities
* Route optimization for rebalancing teams

## Project Outcome

This project demonstrates an end-to-end data engineering and business intelligence workflow:

```text
Business problem definition
→ API data collection
→ data validation
→ cloud storage
→ transformation
→ BigQuery modeling
→ KPI development
→ dashboard reporting
→ operational recommendations
```

Rather than only displaying Citi Bike data, the platform converts live operational information into a repeatable decision-support system for monitoring service reliability and identifying stations requiring attention.

## Author

**Colin Mendoza**

Cornell University
Information Science
