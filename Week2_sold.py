import pandas as pd
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# Week 2 - Dataset Structuring and Validation (Sold)
# Inspects the sold dataset, analyzes missing values,
# reviews numeric distributions, answers EDA questions,
# and saves the validated dataset.

csv_folder = Path('/Users/charithreddydasari/Documents/IDX Exchange Internship/csv')
output_folder = Path('/Users/charithreddydasari/Documents/IDX Exchange Internship/Week2-3_results')

sold = pd.read_csv(csv_folder / 'sold.csv', low_memory=False)

# Step 1 - Dataset Understanding
print(f"Rows: {len(sold):,}")
print(f"Columns: {len(sold.columns)}")

print("\nColumn data types:")
print(sold.dtypes.to_string())

print("\nFirst 5 rows:")
print(sold.head())

print("\nUnique PropertyType values (filter applied upstream in Week 1):")
print(sold['PropertyType'].unique())

# Step 2 - Missing Value Analysis
missing = pd.DataFrame({
    'missing_count': sold.isnull().sum(),
    'missing_pct': (sold.isnull().sum() / len(sold) * 100).round(2)
}).sort_values('missing_pct', ascending=False)

print("\nMissing Value Report:")
print(missing.to_string())

high_missing = missing[missing['missing_pct'] > 90]
print(f"\nColumns with >90% missing values: {len(high_missing)}")
print(high_missing)

missing.to_csv(output_folder / 'sold_missing_value_report.csv')
print("Missing value report saved.")

# Step 3 - Numeric Distribution Review
# Full summary table (all 9 key fields) -- numbers only, no charts.
key_numeric_fields = ['ClosePrice', 'ListPrice', 'OriginalListPrice',
                       'LivingArea', 'LotSizeAcres', 'BedroomsTotal',
                       'BathroomsTotalInteger', 'DaysOnMarket', 'YearBuilt']
key_numeric_fields = [f for f in key_numeric_fields if f in sold.columns]

dist_summary = sold[key_numeric_fields].describe(
    percentiles=[.01, .10, .25, .50, .75, .90, .99])
dist_summary.to_csv(output_folder / 'sold_distribution_summary.csv')
print("\nFull distribution summary (9 fields) saved to sold_distribution_summary.csv")

# Focused summary printed to console for the 3 fields the deliverable specifically asks about.
required_fields = ['ClosePrice', 'LivingArea', 'DaysOnMarket']
print("\nFocused Distribution Summary (ClosePrice, LivingArea, DaysOnMarket):")
print(sold[required_fields].describe(percentiles=[.10, .25, .50, .75, .90]).to_string())

# Charts: only for the 3 required fields, and clipped to the 1st-99th
# percentile for the *display* only. Underlying data/stats above are
# untouched -- outliers still show up in the real min/max/mean.
for col in required_fields:
    data = sold[col].dropna()
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
    plt.savefig(output_folder / f'{col}_distribution.png')
    plt.close()
    print(f'Saved chart for {col}')

# Step 4 - EDA Questions
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

# sold_above_list was only needed to compute the stat above, not part of
# the saved schema -- drop it so sold_validated.csv stays a clean version
# of the original columns, same as listings_validated.csv.
sold = sold.drop(columns=['sold_above_list'])

# Step 4b - Drop duplicate columns and high-missing columns
# The raw Trestle export has some columns appearing twice (pandas appends
# '.1' when a header repeats in the source CSV). Confirm each pair is
# actually identical before dropping, then keep only the original.
dup_base_cols = [c[:-2] for c in sold.columns if c.endswith('.1')]
for base in dup_base_cols:
    dup_col = f"{base}.1"
    if base in sold.columns and dup_col in sold.columns:
        if sold[base].equals(sold[dup_col]):
            sold = sold.drop(columns=[dup_col])
            print(f"Dropped duplicate column: {dup_col}")
        else:
            print(f"WARNING: {base} and {dup_col} are NOT identical -- kept both")

# Drop columns flagged above as >90% missing (decision per handbook:
# keep core fields even if partially missing, drop the rest)
cols_to_drop = [c for c in high_missing.index.tolist() if c in sold.columns]
sold = sold.drop(columns=cols_to_drop)
print(f"\nDropped {len(cols_to_drop)} columns with >90% missing values.")
print(f"Remaining columns: {len(sold.columns)}")

# Step 5 - Save validated dataset
sold.to_csv(csv_folder / 'sold_validated.csv', index=False)
print("\nsold_validated.csv saved. Done!")