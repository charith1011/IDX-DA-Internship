import pandas as pd
import geopandas as gpd
from pathlib import Path

# Week 6 - School District Spatial Join (Sold + Listings)
# Attaches a Unified School District name to each property using a
# spatial join against CA's school district boundary GeoJSON, based on
# each property's Latitude/Longitude.

csv_folder = Path('/Users/charithreddydasari/Documents/IDX Exchange Internship/csv')
output_folder = Path('/Users/charithreddydasari/Documents/IDX Exchange Internship/Week6_results')

# Step 1 - Load and prep the school district boundaries
districts = gpd.read_file(csv_folder / 'ca_school_districts.geojson')

# Reproject to match the plain lat/long format of the MLS data (the raw
# file comes in as EPSG:3857, MLS coordinates are EPSG:4326)
districts = districts.to_crs(epsg=4326)

# Filter to Unified districts only -- Elementary and High School districts
# often overlap the same land, which would cause a property to match two
# districts at once instead of one
districts = districts[districts['DistrictType'] == 'Unified']
print(f"Unified school districts loaded: {len(districts)}")

# Keep only what we actually need for the join -- no reason to carry the
# enrollment/demographic columns from the source file into our MLS data
districts = districts[['DistrictName', 'geometry']]

#this function takes a dataframe and a label (either 'Sold' or 'Listings') and 
#adds a school district name to each property based on its latitude and longitude. 
def add_school_district(df, label):
    rows_before = len(df)

    # Build a point geometry per row. points_from_xy expects (x, y),
    # i.e. (Longitude, Latitude) -- reversed order is a silent bug, not
    # an error, so this order matters.
    df_geo = gpd.GeoDataFrame(
        df.copy(),
        geometry=gpd.points_from_xy(df['Longitude'], df['Latitude']),
        crs='EPSG:4326'
    )

    # Spatial join: for each property point, find which district polygon
    # (if any) contains it
    joined = gpd.sjoin(df_geo, districts, how='left', predicate='within')

    # A point sitting exactly on a shared boundary line could theoretically
    # match more than one polygon and duplicate the row -- drop any extra
    # matches, keeping the first, so row count never grows from the join
    joined = joined[~joined.index.duplicated(keep='first')]

    matched = joined['DistrictName'].notnull().sum()
    unmatched = joined['DistrictName'].isnull().sum()
    print(f"\n{label}: {matched:,} properties matched to a district, {unmatched:,} unmatched")
    print(f"{label} row count before join: {rows_before:,} | after join: {len(joined):,}")

    match_summary = pd.DataFrame({
        'status': ['matched', 'unmatched'],
        'count': [matched, unmatched]
    })
    match_summary.to_csv(output_folder / f'{label.lower()}_district_match_summary.csv', index=False)

    # Drop the join's own helper columns and geometry -- we only wanted
    # DistrictName out of this, not to keep a geometry column in the
    # final analysis CSV
    joined = joined.drop(columns=['geometry', 'index_right'], errors='ignore')

    return joined


# Step 2 - Load the Week 4-5 cleaned datasets and join each to districts
sold = pd.read_csv(csv_folder / 'sold_cleaned.csv', low_memory=False)
listings = pd.read_csv(csv_folder / 'listings_cleaned.csv', low_memory=False)

sold = add_school_district(sold, 'Sold')
listings = add_school_district(listings, 'Listings')

# Step 3 - Re-convert date columns to real datetime
# CSV format doesn't preserve dtypes -- the datetime conversion from
# Week 4-5 was lost the moment sold_cleaned.csv/listings_cleaned.csv were
# saved, so these columns came back in as plain text on reload above.
date_cols = ['CloseDate', 'PurchaseContractDate', 'ListingContractDate', 'ContractStatusChangeDate']
for col in date_cols:
    if col in sold.columns:
        sold[col] = pd.to_datetime(sold[col], errors='coerce')
    if col in listings.columns:
        listings[col] = pd.to_datetime(listings[col], errors='coerce')

# Step 4 - Feature engineering

def add_engineered_metrics(df, date_key_col):
    df['price_ratio'] = df['ClosePrice'] / df['OriginalListPrice']
    df['price_per_sqft'] = df['ClosePrice'] / df['LivingArea']

    # Year / Month / YrMo, derived from the relevant date key
    # (CloseDate for sold, ListingContractDate for listings)
    df['year'] = df[date_key_col].dt.year
    df['month'] = df[date_key_col].dt.month
    df['yr_mo'] = df[date_key_col].dt.to_period('M').astype(str)

    # Listing to Contract Days -- time from listing to accepted offer
    df['listing_to_contract_days'] = (df['PurchaseContractDate'] - df['ListingContractDate']).dt.days

    # Contract to Close Days -- escrow/closing duration
    df['contract_to_close_days'] = (df['CloseDate'] - df['PurchaseContractDate']).dt.days

    # A negative day count is logically impossible, not just an outlier --
    # mask it to NaN wherever the Week 4-5 date-order flags already caught
    # that violation. The flag itself and the raw dates are untouched, so
    # nothing is hidden; this only protects the engineered metric from
    # producing a nonsense number if someone aggregates it without
    # checking the flag first.
    if 'negative_timeline_flag' in df.columns:
        df.loc[df['negative_timeline_flag'], 'listing_to_contract_days'] = pd.NA
    if 'purchase_after_close_flag' in df.columns:
        df.loc[df['purchase_after_close_flag'], 'contract_to_close_days'] = pd.NA

    return df


# Note: price_ratio and price_per_sqft use ClosePrice, so they will be
# null for the ~75% of listings that haven't closed yet -- expected,
# same reasoning as the ListPrice-vs-ClosePrice note from Week 2.
sold = add_engineered_metrics(sold, date_key_col='CloseDate')
listings = add_engineered_metrics(listings, date_key_col='ListingContractDate')

print("\nSample engineered metrics (Sold):")
print(sold[['price_ratio', 'price_per_sqft', 'yr_mo',
             'listing_to_contract_days', 'contract_to_close_days']].head())

print("\nSample engineered metrics (Listings):")
print(listings[['price_ratio', 'price_per_sqft', 'yr_mo',
                  'listing_to_contract_days', 'contract_to_close_days']].head())

# Step 5 - Save enriched datasets
sold.to_csv(csv_folder / 'sold_engineered.csv', index=False)
listings.to_csv(csv_folder / 'listings_engineered.csv', index=False)

print("\nBoth files saved. Done!")