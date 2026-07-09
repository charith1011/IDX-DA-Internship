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
Inspected both datasets for structure, missing values, and numeric distributions.
Answered key EDA questions about pricing, days on market, and county-level trends.

**Key findings (Sold):**
- 389,797 rows, 82 columns
- 17 columns with >90% missing values
- Median close price: $825,000 | Average: $1,202,759
- 40.1% of homes sold above list price
- Median days on market: 18 days
- Data quality flags: negative DaysOnMarket values, ClosePrice of $0, 58 records where CloseDate is before ListingContractDate

**Key findings (Listings):**
- 512,665 rows, 84 columns
- 15 columns with >90% missing values
- Median list price: $849,000 | Average: $1,318,395
- Duplicate columns detected (.1 suffix) — to be fixed in cleaning phase

**Scripts:**
- `Week2_sold.py` – validates sold dataset, saves sold_validated.csv
- `Week2_listings.py` – validates listings dataset, saves listings_validated.csv

## How to Run
1. Place all monthly CSV files in the csv/ folder
2. Run Week1_listings.py to generate listings.csv
3. Run Week1_sold.py to generate sold.csv
4. Run Week2_sold.py to validate and analyze the sold dataset
5. Run Week2_listings.py to validate and analyze the listings dataset