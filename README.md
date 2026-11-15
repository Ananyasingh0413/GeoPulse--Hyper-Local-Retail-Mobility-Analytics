<<<<<<< HEAD
\# GeoPulse: Hyper-Local Retail Mobility Analytics



\## 1. Project Overview



GeoPulse is a Retail Mobility Analytics project that uses GPS location data to understand movement patterns and identify retail store catchment areas.



The project aims to convert location-based data into useful insights that can support retail store planning and business decisions.



\## 2. Project Objectives



\- Generate synthetic GPS mobility data.

\- Analyze device locations around retail stores.

\- Identify devices within a 500-meter store radius.

\- Prepare location data for geospatial analysis.

\- Build a foundation for hourly unique visitor analysis.



\## 3. Technology Stack



\*\*Currently Used:\*\*

\- Python

\- Pandas

\- NumPy

\- Geopy

\- Jupyter Notebook

\- Git and GitHub



\*\*Planned Technologies:\*\*

\- Snowflake

\- PySpark

\- Apache Sedona

\- dbt

\- SQL



\## 4. Week 1: GPS Data Generation and Analysis



During Week 1, a synthetic GPS dataset was created using Python.



The dataset contains:

\- DeviceID

\- Lat

\- Long

\- Timestamp



\### Dataset Details



\- Total GPS Records: 100

\- Total Sample Stores: 5

\- Missing Values: 0

\- Duplicate Records: 0



\### Data Quality Validation



The dataset was checked for missing values, duplicate records, and valid latitude and longitude ranges.



All 100 records passed the initial data quality checks.



\## 5. Store Catchment Analysis



Five sample retail store locations were created.



Using the Geopy library, the geographical distance between GPS devices and stores was calculated.



A 500-meter radius was used to identify devices located within each store's catchment area.



\### Catchment Analysis Results



| Store | Devices Within 500m |

|---|---:|

| Store A | 1 |

| Store B | 0 |

| Store C | 1 |

| Store D | 1 |

| Store E | 1 |



\### Key Observation



Store B had no GPS devices within its 500-meter radius, while the other four sample stores had one device each.



These results are based on synthetic GPS data and are intended for project demonstration.



\## 6. Project Files



| File Name | Description |

|---|---|

| GeoPulse\_Week1\_GPS\_Analysis.ipynb | GPS data generation and analysis |

| geopulse\_gps\_data.csv | Synthetic GPS dataset |

| geopulse\_store\_locations.csv | Sample retail store locations |

| geopulse\_catchment\_analysis.csv | 500-meter catchment results |

| .gitignore | Excludes temporary and environment files |



\## 7. Upcoming Work



\- Load GPS data into Snowflake GEOGRAPHY tables.

\- Perform spatial analysis using PySpark and Apache Sedona.

\- Develop 500-meter spatial joins.

\- Build hourly unique visitor models using dbt.

\- Validate and document analytical results.



\## 8. Project Goal



The main goal of GeoPulse is to transform GPS mobility data into meaningful retail insights that help understand store locations, customer movement patterns, and potential retail opportunities.
=======
# GeoPulse: Hyper-Local Retail Mobility Analytics

## 1. Project Overview

GeoPulse is a Retail Mobility Analytics project that uses GPS location data to understand movement patterns and identify retail store catchment areas.

The project aims to convert location-based data into useful insights that can support retail store planning and business decisions.

## 2. Project Objectives

- Generate synthetic GPS mobility data.
- Analyze device locations around retail stores.
- Identify devices within a 500-meter store radius.
- Prepare location data for geospatial analysis.
- Build a foundation for hourly unique visitor analysis.

## 3. Technology Stack

**Currently Used:**
- Python
- Pandas
- NumPy
- Geopy
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

## 5. Store Catchment Analysis

Five sample retail store locations were created.

Using the Geopy library, the geographical distance between GPS devices and stores was calculated.

A 500-meter radius was used to identify devices located within each store's catchment area.

### Catchment Analysis Results

| Store | Devices Within 500m |
|---|---:|
| Store A | 1 |
| Store B | 0 |
| Store C | 1 |
| Store D | 1 |
| Store E | 1 |

### Key Observation

Store B had no GPS devices within its 500-meter radius, while the other four sample stores had one device each.

These results are based on synthetic GPS data and are intended for project demonstration.

## 6. Project Files

| File Name | Description |
|---|---|
| GeoPulse_Week1_GPS_Analysis.ipynb | GPS data generation and analysis |
| geopulse_gps_data.csv | Synthetic GPS dataset |
| geopulse_store_locations.csv | Sample retail store locations |
| geopulse_catchment_analysis.csv | 500-meter catchment results |
| .gitignore | Excludes temporary and environment files |

## 7. Upcoming Work

- Load GPS data into Snowflake GEOGRAPHY tables.
- Perform spatial analysis using PySpark and Apache Sedona.
- Develop 500-meter spatial joins.
- Build hourly unique visitor models using dbt.
- Validate and document analytical results.

The main goal of GeoPulse is to transform GPS mobility data into meaningful retail insights that help understand store locations, customer movement patterns, and potential retail opportunities.

## 8. Project Goal

The main goal of GeoPulse is to transform GPS mobility data into meaningful retail insights that help understand store locations, customer movement patterns, and potential retail opportunities.