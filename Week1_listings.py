import pandas as pd
from pathlib import Path

# Week 1 – Listings Dataset Aggregation
# Combines monthly MLS Listing files from March 2024 through April 2026,
# filters to Residential only, and saves as listings.csv

csv_folder = Path('/Users/charithreddydasari/Documents/IDX Exchange Internship/csv')

months = pd.period_range(start="2024-03", end="2026-04", freq="M").strftime("%Y%m").tolist()

# Collect listing files, skip any missing months
listing_files = []
for month in months:
    f = csv_folder / f"CRMLSListing{month}.csv"
    if not f.exists():
        print(f"Warning: skipping {f.name}")
        continue
    listing_files.append(f)

print(f"Listing files found: {len(listing_files)}")

# Load and concatenate
listing_frames = [pd.read_csv(f, low_memory=False) for f in listing_files]
listings = pd.concat(listing_frames, ignore_index=True)
print(f"Rows after concatenation: {len(listings):,}")

# Filter to Residential only
listings_residential = listings[listings["PropertyType"] == "Residential"].copy()
print(f"Rows after Residential filter: {len(listings_residential):,}")

# Save
listings_residential.to_csv(csv_folder / "listings.csv", index=False)
print("listings.csv saved. Done!")