import pandas as pd
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# Week 2 – Dataset Structuring and Validation (Listings)
# Inspects the listings dataset, analyzes missing values,
# reviews numeric distributions, answers EDA questions,
# and saves the validated dataset.

csv_folder = Path('/Users/charithreddydasari/Documents/IDX Exchange Internship/csv')
output_folder = Path('/Users/charithreddydasari/Documents/IDX Exchange Internship')

# Load listings dataset
listings = pd.read_csv(csv_folder / 'listings.csv', low_memory=False)

# Step 1 – Dataset Understanding
print(f"Rows: {len(listings):,}")
print(f"Columns: {len(listings.columns)}")

print("\nFirst 5 rows:")
print(listings.head())

print("\nUnique PropertyType values:")
print(listings['PropertyType'].unique())

# Step 2 – Missing Value Analysis
missing = pd.DataFrame({
    'missing_count': listings.isnull().sum(),
    'missing_pct': (listings.isnull().sum() / len(listings) * 100).round(2)
}).sort_values('missing_pct', ascending=False)

print("\nMissing Value Report:")
print(missing.to_string())

high_missing = missing[missing['missing_pct'] > 90]
print(f"\nColumns with >90% missing values: {len(high_missing)}")
print(high_missing)

# Save missing value report
missing.to_csv(output_folder / 'listings_missing_value_report.csv')
print("Missing value report saved.")

# Step 3 – Numeric Distribution Review
key_numeric_fields = ['ListPrice', 'OriginalListPrice', 'LivingArea',
                      'LotSizeAcres', 'BedroomsTotal', 'BathroomsTotalInteger',
                      'DaysOnMarket', 'YearBuilt']

key_numeric_fields = [f for f in key_numeric_fields if f in listings.columns]

print("\nFocused Distribution Summary (ListPrice, LivingArea, DaysOnMarket):")
print(listings[['ListPrice', 'LivingArea', 'DaysOnMarket']].describe(
    percentiles=[.10, .25, .50, .75, .90]).to_string())

# Save distribution summary
dist_summary = listings[key_numeric_fields].describe(percentiles=[.10, .25, .50, .75, .90])
dist_summary.to_csv(output_folder / 'listings_distribution_summary.csv')
print("Distribution summary saved.")

# Generate histograms and boxplots
for col in key_numeric_fields:
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
    data = listings[col].dropna()

    ax1.hist(data, bins=50, color='steelblue', edgecolor='white')
    ax1.set_title(f'{col} - Histogram')
    ax1.set_xlabel(col)
    ax1.set_ylabel('Count')

    ax2.boxplot(data, vert=True)
    ax2.set_title(f'{col} - Boxplot')
    ax2.set_ylabel(col)

    plt.tight_layout()
    plt.savefig(output_folder / f'listings_{col}_distribution.png')
    plt.close()
    print(f'Saved chart for {col}')

# Step 4 – EDA Questions
print("\n--- EDA QUESTIONS ---")

print(f"\nMedian ListPrice: ${listings['ListPrice'].median():,.0f}")
print(f"Average ListPrice: ${listings['ListPrice'].mean():,.0f}")

print(f"\nDaysOnMarket:")
print(f"  Min: {listings['DaysOnMarket'].min()}")
print(f"  Median: {listings['DaysOnMarket'].median()}")
print(f"  Mean: {listings['DaysOnMarket'].mean():.1f}")
print(f"  Max: {listings['DaysOnMarket'].max()}")

print("\nTop 10 Counties by Median ListPrice:")
county_prices = listings.groupby('CountyOrParish')['ListPrice'].median().sort_values(ascending=False).head(10)
print(county_prices.to_string())

# Step 5 – Save validated dataset
listings.to_csv(csv_folder / 'listings_validated.csv', index=False)
print("\nlistings_validated.csv saved. Done!")