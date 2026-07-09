import pandas as pd
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# Week 2 – Dataset Structuring and Validation (Sold)
# Inspects the sold dataset, analyzes missing values,
# reviews numeric distributions, answers EDA questions,
# and saves the validated dataset.

csv_folder = Path('/Users/charithreddydasari/Documents/IDX Exchange Internship/csv')
output_folder = Path('/Users/charithreddydasari/Documents/IDX Exchange Internship')

# Load sold dataset
sold = pd.read_csv(csv_folder / 'sold.csv', low_memory=False)

# Step 1 – Dataset Understanding
print(f"Rows: {len(sold):,}")
print(f"Columns: {len(sold.columns)}")

print("\nFirst 5 rows:")
print(sold.head())

# print("\nAll columns and data types:")
# for col in sold.columns:
#     print(f"  {col}: {sold[col].dtype}")

print("\nUnique PropertyType values:")
print(sold['PropertyType'].unique())

# Step 2 – Missing Value Analysis
missing = pd.DataFrame({
    'missing_count': sold.isnull().sum(),
    'missing_pct': (sold.isnull().sum() / len(sold) * 100).round(2)
}).sort_values('missing_pct', ascending=False)

print("\nMissing Value Report:")
print(missing.to_string())

high_missing = missing[missing['missing_pct'] > 90]
print(f"\nColumns with >90% missing values: {len(high_missing)}")
print(high_missing)

# Save missing value report
missing.to_csv(output_folder / 'sold_missing_value_report.csv')
print("Missing value report saved.")

# Step 3 – Numeric Distribution Review
key_numeric_fields = ['ClosePrice', 'ListPrice', 'OriginalListPrice',
                      'LivingArea', 'LotSizeAcres', 'BedroomsTotal',
                      'BathroomsTotalInteger', 'DaysOnMarket', 'YearBuilt']

key_numeric_fields = [f for f in key_numeric_fields if f in sold.columns]

# print("\nNumeric Distribution Summary:")
# print(sold[key_numeric_fields].describe(percentiles=[.10, .25, .50, .75, .90]).to_string())

print("\nFocused Distribution Summary (ClosePrice, LivingArea, DaysOnMarket):")
print(sold[['ClosePrice', 'LivingArea', 'DaysOnMarket']].describe(
    percentiles=[.10, .25, .50, .75, .90]).to_string())

# Save distribution summary
dist_summary = sold[key_numeric_fields].describe(percentiles=[.10, .25, .50, .75, .90])
dist_summary.to_csv(output_folder / 'sold_distribution_summary.csv')
print("Distribution summary saved.")

# Generate histograms and boxplots
for col in key_numeric_fields:
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
    data = sold[col].dropna()

    ax1.hist(data, bins=50, color='steelblue', edgecolor='white')
    ax1.set_title(f'{col} - Histogram')
    ax1.set_xlabel(col)
    ax1.set_ylabel('Count')

    ax2.boxplot(data, vert=True)
    ax2.set_title(f'{col} - Boxplot')
    ax2.set_ylabel(col)

    plt.tight_layout()
    plt.savefig(output_folder / f'{col}_distribution.png')
    plt.close()
    print(f'Saved chart for {col}')

# Step 4 – EDA Questions
print("\n--- EDA QUESTIONS ---")

print(f"\nMedian ClosePrice: ${sold['ClosePrice'].median():,.0f}")
print(f"Average ClosePrice: ${sold['ClosePrice'].mean():,.0f}")

sold['sold_above_list'] = sold['ClosePrice'] > sold['ListPrice']
above = sold['sold_above_list'].sum()
below = (~sold['sold_above_list']).sum()
total = len(sold)
print(f"\nHomes sold above list price: {above:,} ({above/total*100:.1f}%)")
print(f"Homes sold below list price: {below:,} ({below/total*100:.1f}%)")

print(f"\nDaysOnMarket:")
print(f"  Min: {sold['DaysOnMarket'].min()}")
print(f"  Median: {sold['DaysOnMarket'].median()}")
print(f"  Mean: {sold['DaysOnMarket'].mean():.1f}")
print(f"  Max: {sold['DaysOnMarket'].max()}")

listing_dt = pd.to_datetime(sold['ListingContractDate'], errors='coerce')
close_dt = pd.to_datetime(sold['CloseDate'], errors='coerce')
date_issues = (close_dt < listing_dt).sum()
print(f"\nRecords where CloseDate is before ListingContractDate: {date_issues:,}")

print("\nTop 10 Counties by Median ClosePrice:")
county_prices = sold.groupby('CountyOrParish')['ClosePrice'].median().sort_values(ascending=False).head(10)
print(county_prices.to_string())

# Step 5 – Save validated dataset
sold.to_csv(csv_folder / 'sold_validated.csv', index=False)
print("\nsold_validated.csv saved. Done!")