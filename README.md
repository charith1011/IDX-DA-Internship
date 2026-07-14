# IDX Exchange Data Analyst Internship

## Project Overview
Analyzing real MLS transaction data from the California Regional MLS (CRMLS) 
to build housing market insights and Tableau dashboards.

## Tools Used
- Python (Pandas)
- Tableau Desktop Public Edition

## Week 0 – MLS Data Pipeline Orientation
Reviewed the Real Estate Data Analyst Primer and Trestle Property Metadata 
reference to understand MLS data structure, the real estate transaction 
lifecycle (Listing → Pending → Closed), and key fields (ListPrice, ClosePrice, 
StandardStatus, DaysOnMarket, PropertyType). Downloaded all available monthly 
CRMLSListing and CRMLSSold CSV files via FTP using FileZilla.

## Week 1 – Monthly Dataset Aggregation
Combined monthly MLS Listing and Sold CSV files from January 2024 through 
June 2026 into two unified datasets, filtered to Residential properties only.

**Results:** After adding May and June data
- Listings: 933,278 rows after concatenation → 594,521 after Residential filter
- Sold: 665,619 rows after concatenation → 448,093 after Residential filter

**Scripts:**
- `Week1_listings.py` – produces listings.csv
- `Week1_sold.py` – produces sold.csv

Note: Some Sold months are only available as `_filled` versions (2 extra 
trailing columns dropped per team guidance); regular version is preferred 
where both exist.

## Week 2 – Dataset Structuring and Validation
Inspected both datasets for structure, missing values, and numeric distributions.
Answered key EDA questions about pricing, days on market, and county-level trends.
Note: the Residential vs. other property type share (~64% listings, ~67% sold)
was already established in Week 1 and can't be recomputed here, since both
datasets are Residential-only by this point.

**Key findings (Sold):**
- 448,093 rows, 82 columns (raw)
- 15 columns with >90% missing values, dropped
- No duplicate (.1-suffix) columns found in the Sold dataset
- 67 columns remain after cleaning → saved as `sold_validated.csv`
- Median close price: $825,000 | Average: $1,192,658
- 40.0% of homes sold above list price, 60.0% below
- Days on market: median 18, mean 37.3, min -288, max 12,430 (~34 years) —
  both values are data errors
- ClosePrice minimum of $0 found — invalid
- 68 records where CloseDate is before ListingContractDate
- A `sold_above_list` boolean column was created to compute the above/below
  stat, then dropped before saving — not part of the final saved schema

**Key findings (Listings):**
- 594,521 rows, 84 columns (raw)
- 13 columns with >90% missing values, dropped
- 10 duplicate (.1-suffix) columns found from the raw Trestle export; 8 were
  confirmed identical and dropped. `BuyerOfficeName`/`BuyerOfficeName.1` and
  `UnparsedAddress`/`UnparsedAddress.1` were NOT identical and were both kept
  as-is, cause not yet investigated
- 62 columns remain after cleaning → saved as `listings_validated.csv`
- ClosePrice is 75% missing in listings.csv (most listings haven't closed
  yet), so **ListPrice was used as the price field** for the listings
  distribution summary and charts instead of ClosePrice
- Median list price: $849,000 | Average: $1,316,547
- Days on market: median 11, mean 18.7, min -58 (invalid, same date-logic
  issue as Sold), max 1,063
- Other outliers found: LivingArea max ~17M sqft, LotSizeAcres max ~4.2M
  acres, BedroomsTotal max 108, YearBuilt max 2028

**Scripts:**
- `Week2_sold.py` – validates sold dataset, saves sold_validated.csv
- `Week2_listings.py` – validates listings dataset, saves listings_validated.csv

## Week 2-3 – Mortgage Rate Enrichment
Fetched the 30-year fixed mortgage rate (MORTGAGE30US) directly from the St.
Louis Federal Reserve (FRED) — 2,885 weekly readings going back to 1971.
Resampled from weekly to monthly averages (664 monthly values), then merged
onto both the Week 2 validated datasets (`sold_validated.csv` and
`listings_validated.csv`, not the raw Week 1 files) using a year_month key —
`CloseDate` for sold, `ListingContractDate` for listings. Enriching the
validated files instead of raw ones was a deliberate choice so the Week 2
column cleanup carries forward rather than being undone.

**Results:**
- 0 non-numeric/missing weekly rate values from FRED
- 0 null rates after merge on both datasets — every row matched a month
- Output columns added: `year_month`, `rate_30yr_fixed`

**Scripts:**
- `Week2-3_mortgage.py` – produces sold_with_rates.csv and listings_with_rates.csv

## How to Run
1. Place all monthly CSV files in the csv/ folder
2. Run Week1_listings.py to generate listings.csv
3. Run Week1_sold.py to generate sold.csv
4. Run Week2_sold.py to validate and analyze the sold dataset
5. Run Week2_listings.py to validate and analyze the listings dataset
6. Run Week2-3_mortgage.py to enrich both datasets with mortgage rates