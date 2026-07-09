import pandas as pd
from pathlib import Path

# Week 2-3 – Mortgage Rate Enrichment
# Fetches 30-year fixed mortgage rate from FRED,
# resamples to monthly averages, and merges onto
# both sold and listings datasets.

csv_folder = Path('/Users/charithreddydasari/Documents/IDX Exchange Internship/csv')

# Step 1 – Fetch mortgage rate data from FRED
url = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=MORTGAGE30US"
mortgage = pd.read_csv(url, parse_dates=['observation_date'])
mortgage.columns = ['date', 'rate_30yr_fixed']

print(f"Mortgage rate data loaded: {len(mortgage)} rows")
print(mortgage.head())

# Step 2 – Resample weekly rates to monthly averages
mortgage['year_month'] = mortgage['date'].dt.to_period('M')
mortgage_monthly = (
    mortgage.groupby('year_month')['rate_30yr_fixed']
    .mean()
    .reset_index()
)

print(f"\nMonthly mortgage rates: {len(mortgage_monthly)} rows")
print(mortgage_monthly.tail())

# Step 3 – Load sold and listings datasets
sold = pd.read_csv(csv_folder / 'sold.csv', low_memory=False)
listings = pd.read_csv(csv_folder / 'listings.csv', low_memory=False)

# Step 4 – Create year_month key on MLS datasets
sold['year_month'] = pd.to_datetime(sold['CloseDate'], errors='coerce').dt.to_period('M')
listings['year_month'] = pd.to_datetime(listings['ListingContractDate'], errors='coerce').dt.to_period('M')

# Step 5 – Merge mortgage rates onto both datasets
sold_with_rates = sold.merge(mortgage_monthly, on='year_month', how='left')
listings_with_rates = listings.merge(mortgage_monthly, on='year_month', how='left')

# Step 6 – Validate merge
sold_nulls = sold_with_rates['rate_30yr_fixed'].isnull().sum()
listings_nulls = listings_with_rates['rate_30yr_fixed'].isnull().sum()

print(f"\nNull rates after merge (sold): {sold_nulls}")
print(f"Null rates after merge (listings): {listings_nulls}")

if sold_nulls > 0:
    missing_months = sold_with_rates.loc[sold_with_rates['rate_30yr_fixed'].isnull(), 'year_month'].unique()
    print(f"Sold - months with no matching rate: {missing_months}")

if listings_nulls > 0:
    missing_months = listings_with_rates.loc[listings_with_rates['rate_30yr_fixed'].isnull(), 'year_month'].unique()
    print(f"Listings - months with no matching rate: {missing_months}")

print("\nSold preview:")
print(sold_with_rates[['CloseDate', 'year_month', 'ClosePrice', 'rate_30yr_fixed']].head())

print("\nListings preview:")
print(listings_with_rates[['ListingContractDate', 'year_month', 'ListPrice', 'rate_30yr_fixed']].head())

# Step 7 – Save enriched datasets
sold_with_rates.to_csv(csv_folder / 'sold_with_rates.csv', index=False)
listings_with_rates.to_csv(csv_folder / 'listings_with_rates.csv', index=False)

print("\nBoth files saved. Done!")