SELECT
  SAFE_DIVIDE(
    SUM(num_bikes_disabled),
    SUM(num_bikes_available) + SUM(num_bikes_disabled)
  ) AS disabled_bike_rate,

  SAFE_DIVIDE(
    SUM(num_ebikes_available),
    SUM(num_bikes_available)
  ) AS ebike_share_of_available_bikes,

  SAFE_DIVIDE(
    COUNTIF(is_renting = 0),
    COUNT(*)
  ) AS station_rental_outage_rate,

  SAFE_DIVIDE(
    COUNTIF(is_returning = 0),
    COUNT(*)
  ) AS station_return_outage_rate
FROM `citibike-operations-colin-2026.citibike_operations.station_status`;