# Phase 3 BigQuery Findings

## Data Quality Results

- 2,461 total rows
- 2,461 unique stations
- 0 missing station IDs
- 0 missing source timestamps
- 0 missing collection timestamps

## Operational Metrics

- 36,698 bikes available
- 16,754 e-bikes available
- 29,748 docks available
- 4,271 disabled bikes
- 75 disabled docks
- 98 stations not renting
- 98 stations not accepting returns

## Operational Rates

- Disabled-bike rate: 10.42%
- E-bike share of available bikes: 45.65%
- Station rental outage rate: 3.98%
- Station return outage rate: 3.98%

## Business Interpretation

- Roughly 1 in 10 bikes in the current inventory is disabled, which may indicate a meaningful maintenance or fleet-availability issue.
- E-bikes represent nearly 46% of currently available bikes, showing that they are a major part of rider-accessible supply.
- About 4% of stations are unable to rent bikes or accept returns.
- Because the rental and return outage counts are identical, the same stations may be fully unavailable.

## Station-Level Maintenance Findings

- The highest number of disabled bikes at an active station was 23.
- Some stations had high disabled-bike counts but still had substantial available inventory.
- Station `66dc4bd9-0aca-11e7-82f6-3863bb44ef7c` had only 1 available bike and 11 disabled bikes, indicating a more urgent operational issue.
- Maintenance priority should consider both the number of disabled bikes and the share of total bikes that are disabled.

## Maintenance Priority Findings

- One active station had 10 total bikes and all 10 were disabled.
- Another active station had 11 of 12 bikes disabled, producing a 91.67% disabled-bike rate.
- A third active station had 9 of 11 bikes disabled, producing an 81.82% disabled-bike rate.
- Filtering to stations with at least 10 bikes created a more useful priority list by balancing outage severity with operational scale.