SELECT
  SUM(num_bikes_available) AS total_bikes_available,
  SUM(num_ebikes_available) AS total_ebikes_available,
  SUM(num_docks_available) AS total_docks_available,
  SUM(num_bikes_disabled) AS total_bikes_disabled,
  SUM(num_docks_disabled) AS total_docks_disabled,
  COUNTIF(is_renting = 0) AS stations_not_renting,
  COUNTIF(is_returning = 0) AS stations_not_accepting_returns
FROM `citibike-operations-colin-2026.citibike_operations.station_status`;