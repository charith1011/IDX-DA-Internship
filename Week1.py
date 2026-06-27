import pandas as pd
from pathlib import Path

# ---------------------------------------------------------
# Week 1 – Monthly Dataset Aggregation
# This script combines all monthly MLS Listing and Sold files
# from March 2024 through April 2026 into two datasets,
# filters both to Residential properties only, and saves them.
# ---------------------------------------------------------

csv_folder = Path('/Users/charithreddydasari/Documents/IDX Exchange Internship/csv')

# Generate list of months from 202403 to 202604
months = pd.period_range(start="2024-03", end="2026-04", freq="M").strftime("%Y%m").tolist()

# ---------------------------------------------------------
# Step 1 – Collect Listing files
# Skips any months where the file is missing
# ---------------------------------------------------------

listing_files = []
for month in months:
    f = csv_folder / f"CRMLSListing{month}.csv"
    if not f.exists():
        print(f"Warning: skipping missing Listing file {f.name}")
        continue
    listing_files.append(f)

print(f"Listing files found: {len(listing_files)}")

# ---------------------------------------------------------
# Step 2 – Collect Sold files
# For months with both a regular and _filled version,
# the regular file is used. The _filled version is only
# used if no regular file exists for that month.
# ---------------------------------------------------------

sold_files = []
for month in months:
    regular = csv_folder / f"CRMLSSold{month}.csv"
    filled = csv_folder / f"CRMLSSold{month}_filled.csv"
    if regular.exists():
        sold_files.append(regular)
    elif filled.exists():
        sold_files.append(filled)
    else:
        print(f"Warning: skipping missing Sold file for {month}")

print(f"Sold files found: {len(sold_files)}")

# ---------------------------------------------------------
# Step 3 – Load and concatenate Listing files
# ---------------------------------------------------------

listing_frames = []
for f in listing_files:
    df = pd.read_csv(f, low_memory=False)
    listing_frames.append(df)

listings = pd.concat(listing_frames, ignore_index=True)
print(f"\nListing rows after concatenation: {len(listings):,}")

# ---------------------------------------------------------
# Step 4 – Load and concatenate Sold files
# ---------------------------------------------------------

sold_frames = []
for f in sold_files:
    df = pd.read_csv(f, low_memory=False)
    sold_frames.append(df)

sold = pd.concat(sold_frames, ignore_index=True)
print(f"Sold rows after concatenation: {len(sold):,}")

# ---------------------------------------------------------
# Step 5 – Filter both datasets to Residential only
# ---------------------------------------------------------

listings_residential = listings[listings["PropertyType"] == "Residential"].copy()
sold_residential = sold[sold["PropertyType"] == "Residential"].copy()

print(f"\nListing rows after Residential filter: {len(listings_residential):,}")
print(f"Sold rows after Residential filter: {len(sold_residential):,}")

# ---------------------------------------------------------
# Step 6 – Save the combined datasets
# ---------------------------------------------------------

listings_residential.to_csv(csv_folder / "CRMLSListing_combined_residential.csv", index=False)
sold_residential.to_csv(csv_folder / "CRMLSSold_combined_residential.csv", index=False)

print("\nBoth files saved. Done!")

