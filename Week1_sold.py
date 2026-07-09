import pandas as pd
from pathlib import Path

# Week 1 – Sold Dataset Aggregation
# Combines monthly MLS Sold files from March 2024 through April 2026,
# filters to Residential only, and saves as sold.csv.
# Regular file preferred over _filled version where both exist.
# _filled files have 2 extra columns at the end which are dropped.

csv_folder = Path('/Users/charithreddydasari/Documents/IDX Exchange Internship/csv')

months = pd.period_range(start="2024-03", end="2026-04", freq="M").strftime("%Y%m").tolist()

# Collect sold files, prefer regular over _filled
sold_files = []
for month in months:
    regular = csv_folder / f"CRMLSSold{month}.csv"
    filled = csv_folder / f"CRMLSSold{month}_filled.csv"
    if regular.exists():
        sold_files.append((regular, False))
    elif filled.exists():
        sold_files.append((filled, True))
    else:
        print(f"Warning: skipping missing Sold file for {month}")

print(f"Sold files found: {len(sold_files)}")

# Load and concatenate
sold_frames = []
for f, is_filled in sold_files:
    df = pd.read_csv(f, low_memory=False)
    if is_filled:
        df = df.iloc[:, :-2]  # drop the last 2 columns
    sold_frames.append(df)

sold = pd.concat(sold_frames, ignore_index=True)
print(f"Rows after concatenation: {len(sold):,}")

# Filter to Residential only
sold_residential = sold[sold["PropertyType"] == "Residential"].copy()
print(f"Rows after Residential filter: {len(sold_residential):,}")

# Save
sold_residential.to_csv(csv_folder / "sold.csv", index=False)
print("sold.csv saved. Done!")