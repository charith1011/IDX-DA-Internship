# IDX Exchange Data Analyst Internship

## Project Overview
Analyzing real MLS transaction data from the California Regional MLS (CRMLS) 
to build housing market insights and Tableau dashboards.

## Tools Used
- Python (Pandas)
- Tableau Desktop Public Edition

## Week 1 – Monthly Dataset Aggregation
Combined monthly MLS Listing and Sold CSV files from March 2024 through 
April 2026 into two unified datasets, filtered to Residential properties only.

**Scripts:**
- `Week1_listings.py` – produces listings.csv
- `Week1_sold.py` – produces sold.csv

## Week 2 – Dataset Structuring and Validation
Inspected the sold dataset for structure, missing values, and numeric distributions.
Answered key EDA questions about pricing, days on market, and county-level trends.

**Scripts:**
- `Week2_sold.py` – missing value report, numeric distributions, EDA questions, saves sold_validated.csv

## How to Run
1. Place all monthly CSV files in the csv/ folder
2. Run Week1_listings.py to generate listings.csv
3. Run Week1_sold.py to generate sold.csv
4. Run Week2_sold.py to validate and analyze the sold dataset