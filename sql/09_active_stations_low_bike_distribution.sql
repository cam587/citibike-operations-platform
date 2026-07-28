SELECT
  num_bikes_available,
  COUNT(*) AS active_station_count
FROM `citibike-operations-colin-2026.citibike_operations.station_status`
WHERE is_renting = 1
  AND is_returning = 1
  AND num_bikes_available BETWEEN 1 AND 5
GROUP BY num_bikes_available
ORDER BY num_bikes_available;