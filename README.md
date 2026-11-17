# GeoPulse: Hyper-Local Retail Mobility Analytics

## 1. Project Overview

GeoPulse is a Retail Mobility Analytics project that uses GPS location data to understand movement patterns and identify retail store catchment areas.

The project aims to convert location-based data into useful insights that can support retail store planning and business decisions.

## 2. Project Objectives

- Generate synthetic GPS mobility data.
- Analyze device locations around retail stores.
- Identify devices within a 500-meter store radius.
- Perform geospatial distance calculations.
- Prepare data for hourly unique visitor analysis.

## 3. Technology Stack

**Currently Used:**
- Python
- Pandas
- NumPy
- Matplotlib
- Jupyter Notebook
- Git and GitHub

**Planned Technologies:**
- Snowflake
- PySpark
- Apache Sedona
- dbt
- SQL

## 4. Week 1: GPS Data Generation and Analysis

During Week 1, a synthetic GPS dataset was created using Python.

The dataset contains:
- DeviceID
- Lat
- Long
- Timestamp

### Dataset Details

- Total GPS Records: 100
- Total Sample Stores: 5
- Missing Values: 0
- Duplicate Records: 0

### Data Quality Validation

The dataset was checked for missing values, duplicate records, and valid latitude and longitude ranges.

All 100 records passed the initial data quality checks.

## 5. Week 2: Spatial Catchment Analysis

During Week 2, spatial analysis was performed to identify GPS devices located within a 500-meter radius of retail stores.

The Haversine formula was implemented in Python to calculate geographical distances between GPS coordinates.

### Analysis Details

- GPS Records Analyzed: 100
- Retail Stores Analyzed: 5
- Total Device-Store Comparisons: 500
- Catchment Radius: 500 meters
- Devices Within 500m: 4
- Missing Values in Spatial Results: 0

### Store-wise Catchment Summary

| Store | Unique Devices Within 500m | GPS Visits |
|---|---:|---:|
| Store A | 1 | 1 |
| Store B | 0 | 0 |
| Store C | 1 | 1 |
| Store D | 1 | 1 |
| Store E | 1 | 1 |

### Key Findings

- Four GPS observations were found within the 500-meter catchment areas.
- Store B had no nearby GPS observations.
- All five stores were included in the analysis.
- All 500 device-store distance comparisons were completed successfully.
- No missing values were found in the spatial analysis output.

These findings are based on synthetic GPS observations and do not represent verified customer visits.

## 6. Project Files

| File Name | Description |
|---|---|
| GeoPulse_Week1_GPS_Analysis.ipynb | Week 1 GPS data generation and analysis |
| 03_spatial_catchment_analysis.ipynb | Week 2 spatial catchment analysis |
| geopulse_gps_data.csv | Synthetic GPS dataset |
| geopulse_store_locations.csv | Sample retail store locations |
| geopulse_catchment_analysis.csv | Initial catchment results |
| geopulse_spatial_analysis.csv | Detailed device-store distance analysis |
| geopulse_spatial_summary.csv | Store-wise spatial summary |

## 7. Upcoming Work

- Load GPS data into Snowflake GEOGRAPHY tables.
- Perform spatial analysis using PySpark and Apache Sedona.
- Develop 500-meter spatial joins.
- Build hourly unique visitor models using dbt.
- Validate and document analytical results.

## 8. Project Goal

The main goal of GeoPulse is to transform GPS mobility data into meaningful retail insights that help understand store locations, movement patterns, and potential retail opportunities.