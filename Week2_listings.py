import pandas as pd
from pathlib import Path
import matplotlib
matplotlib.use("Agg") #save images directly to files instead of trying to open a window.
import matplotlib.pyplot as plt

# Week 2 - Dataset Structuring and Validation (Listings)
# Inspects the listings dataset, analyzes missing values,
# reviews numeric distributions, answers EDA questions,
# and saves the validated dataset.

csv_folder = Path('/Users/charithreddydasari/Documents/IDX Exchange Internship/csv')
output_folder = Path('/Users/charithreddydasari/Documents/IDX Exchange Internship/Week2-3_results')

#Week 1 concatendtaded listings
listings = pd.read_csv(csv_folder / 'listings.csv', low_memory=False)

# Step 1 - Dataset Understanding
print(f"Rows: {len(listings):,}")
print(f"Columns: {len(listings.columns)}")

print("\nColumn data types:")
print(listings.dtypes.to_string())

# print("\nFirst 5 rows:")
# print(listings.head())

# The Residential filter was already applied during Week 1 aggregation, before listings.csv was ever saved. This should only ever show one value.
print("\nUnique PropertyType values (filter applied upstream in Week 1):")
print(listings['PropertyType'].unique())

# Step 2 - Missing Value Analysis

# Produces something like
# Column	Missing Count	Missing %
# PoolFeatures	1,800,000	95%
missing = pd.DataFrame({
    'missing_count': listings.isnull().sum(),
    'missing_pct': (listings.isnull().sum() / len(listings) * 100).round(2)
}).sort_values('missing_pct', ascending=False)

print("\nMissing Value Report:")
print(missing.to_string())

high_missing = missing[missing['missing_pct'] > 90]
print(f"\nColumns with >90% missing values: {len(high_missing)}")
print(high_missing)

missing.to_csv(output_folder / 'listings_missing_value_report.csv')
print("Missing value report saved.")

# Step 3 - Numeric Distribution Review
# Full summary table (all key fields) -- numbers only, no charts.
key_numeric_fields = ['ListPrice', 'OriginalListPrice', 'LivingArea',
                       'LotSizeAcres', 'BedroomsTotal', 'BathroomsTotalInteger',
                       'DaysOnMarket', 'YearBuilt']
key_numeric_fields = [f for f in key_numeric_fields if f in listings.columns]

dist_summary = listings[key_numeric_fields].describe(
    percentiles=[.01, .10, .25, .50, .75, .90, .99])
dist_summary.to_csv(output_folder / 'listings_distribution_summary.csv')
print("\nFull distribution summary saved to listings_distribution_summary.csv")

# Focused summary printed to console for the fields that matter most here.
# (Listings has no ClosePrice, so we use ListPrice as the price field.)
required_fields = ['ListPrice', 'LivingArea', 'DaysOnMarket']
print("\nFocused Distribution Summary (ListPrice, LivingArea, DaysOnMarket):")
print(listings[required_fields].describe(percentiles=[.10, .25, .50, .75, .90]).to_string())

# Charts: only for the 3 focused fields, clipped to the 1st-99th percentile
# for the *display* only. Underlying data/stats above are untouched.
for col in required_fields:
    data = listings[col].dropna()
    lower = data.quantile(0.01)
    upper = data.quantile(0.99)
    clipped = data[(data >= lower) & (data <= upper)]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))

    ax1.hist(clipped, bins=50, color='steelblue', edgecolor='white')
    ax1.set_title(f'{col} - Histogram (1st-99th percentile view)')
    ax1.set_xlabel(col)
    ax1.set_ylabel('Count')

    ax2.boxplot(data, vert=True, showfliers=False)
    ax2.set_title(f'{col} - Boxplot (outlier points hidden)')
    ax2.set_ylabel(col)

    plt.tight_layout()
    plt.savefig(output_folder / f'listings_{col}_distribution.png')
    plt.close()
    print(f'Saved chart for {col}')

# Step 4 - EDA Questions
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

# Step 4b - Drop duplicate columns and high-missing columns
# The raw Trestle export has some columns appearing twice (pandas appends
# '.1' when a header repeats in the source CSV). Confirm each pair is
# actually identical before dropping, then keep only the original.
dup_base_cols = [c[:-2] for c in listings.columns if c.endswith('.1')]
for base in dup_base_cols:
    dup_col = f"{base}.1"
    if base in listings.columns and dup_col in listings.columns:
        if listings[base].equals(listings[dup_col]):
            listings = listings.drop(columns=[dup_col])
            print(f"Dropped duplicate column: {dup_col}")
        else:
            print(f"WARNING: {base} and {dup_col} are NOT identical -- kept both")

# Drop columns flagged above as >90% missing (decision per handbook:
# keep core fields even if partially missing, drop the rest)
cols_to_drop = [c for c in high_missing.index.tolist() if c in listings.columns]
listings = listings.drop(columns=cols_to_drop)
print(f"\nDropped {len(cols_to_drop)} columns with >90% missing values.")
print(f"Remaining columns: {len(listings.columns)}")

# Step 5 - Save validated dataset
listings.to_csv(csv_folder / 'listings_validated.csv', index=False)
print("\nlistings_validated.csv saved. Done!")