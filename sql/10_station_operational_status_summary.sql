SELECT
  is_renting,
  is_returning,
  COUNT(*) AS station_count
FROM `citibike-operations-colin-2026.citibike_operations.station_status`
GROUP BY is_renting, is_returning
ORDER BY is_renting DESC, is_returning DESC;