SELECT
  COUNTIF(num_bikes_available = 0) AS stations_with_zero_bikes,
  COUNTIF(num_docks_available = 0) AS stations_with_zero_docks,
  COUNTIF(
    num_bikes_available = 0
    AND num_docks_available = 0
  ) AS stations_with_both_zero
FROM `citibike-operations-colin-2026.citibike_operations.station_status`
WHERE is_renting = 1
  AND is_returning = 1;