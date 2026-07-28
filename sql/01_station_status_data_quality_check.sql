SELECT
  COUNT(*) AS total_rows,
  COUNT(DISTINCT station_id) AS unique_stations,
  COUNTIF(station_id IS NULL) AS missing_station_ids,
  COUNTIF(last_reported IS NULL) AS missing_last_reported,
  COUNTIF(collected_at_utc IS NULL) AS missing_collection_times
FROM `citibike-operations-colin-2026.citibike_operations.station_status`;