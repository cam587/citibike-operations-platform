SELECT
  station_id,
  num_bikes_available,
  num_bikes_disabled,
  num_docks_available,
  num_docks_disabled,
  is_renting,
  is_returning
FROM `citibike-operations-colin-2026.citibike_operations.station_status`
WHERE is_renting = 1
  AND is_returning = 1
ORDER BY num_bikes_disabled DESC
LIMIT 20;