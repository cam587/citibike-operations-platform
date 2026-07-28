SELECT
  COUNT(*) AS total_active_stations,

  COUNTIF(num_bikes_available = 0) AS stations_with_zero_bikes,

  COUNTIF(num_docks_available = 0) AS stations_with_zero_docks,

  SAFE_DIVIDE(
    COUNTIF(num_bikes_available = 0),
    COUNT(*)
  ) AS zero_bike_station_rate,

  SAFE_DIVIDE(
    COUNTIF(num_docks_available = 0),
    COUNT(*)
  ) AS zero_dock_station_rate

FROM `citibike-operations-colin-2026.citibike_operations.station_status`

WHERE is_renting = 1
  AND is_returning = 1;