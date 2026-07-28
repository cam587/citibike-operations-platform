SELECT
  station_id,
  num_bikes_available,
  num_bikes_disabled,
  num_bikes_available + num_bikes_disabled AS total_bikes,
  SAFE_DIVIDE(
    num_bikes_disabled,
    num_bikes_available + num_bikes_disabled
  ) AS disabled_bike_rate
FROM `citibike-operations-colin-2026.citibike_operations.station_status`
WHERE is_renting = 1
  AND is_returning = 1
  AND num_bikes_available + num_bikes_disabled >= 10
ORDER BY disabled_bike_rate DESC
LIMIT 20;