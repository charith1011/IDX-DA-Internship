import pandas as pd
from pathlib import Path

# Week 4-5 - Data Cleaning and Preparation (Listings)
# Converts date fields to real datetime, validates numeric fields,
# flags invalid values and date-order violations, and checks
# geographic data quality. Nothing is deleted -- rows are flagged,
# not dropped, per the handbook's flag-don't-delete approach.

csv_folder = Path('/Users/charithreddydasari/Documents/IDX Exchange Internship/csv')
output_folder = Path('/Users/charithreddydasari/Documents/IDX Exchange Internship/Week4-5_results')

# Load the Week 2-3 enriched dataset (already deduplicated, high-missing
# columns dropped, and carrying the mortgage rate columns)
listings = pd.read_csv(csv_folder / 'listings_with_rates.csv', low_memory=False)

rows_before = len(listings)
cols_before = len(listings.columns)
print(f"Rows before cleaning: {rows_before:,}")
print(f"Columns before cleaning: {cols_before}")

# Step 1 - Convert date fields to real datetime objects
# (they're currently just text strings that happen to look like dates)
# Note: CloseDate and PurchaseContractDate are mostly missing here since most listings haven't closed yet
date_cols = ['CloseDate', 'PurchaseContractDate', 'ListingContractDate', 'ContractStatusChangeDate']
date_cols = [c for c in date_cols if c in listings.columns]
for col in date_cols:
    listings[col] = pd.to_datetime(listings[col], errors='coerce')#errors="coerce" means invalid dates become NaT ("Not a Time")

print("\nDate column types after conversion:")
print(listings[date_cols].dtypes.to_string())

# Step 2 - Confirm numeric fields are properly typed
numeric_cols = ['ClosePrice', 'ListPrice', 'OriginalListPrice', 'LivingArea',
                 'LotSizeAcres', 'BedroomsTotal', 'BathroomsTotalInteger',
                 'DaysOnMarket', 'YearBuilt', 'Latitude', 'Longitude']
numeric_cols = [c for c in numeric_cols if c in listings.columns]
print("\nNumeric column types:")
print(listings[numeric_cols].dtypes.to_string())

# Step 2b - Drop unnecessary/redundant columns
cols_to_drop_judgment = [
    # Redundant with a field already kept
    'ListAgentFirstName', 'ListAgentLastName',   # ListAgentFullName covers this
    'ListingKeyNumeric', 'ListingId',            # ListingKey is enough as an ID
    # Buyer-side / co-list agent detail -- competitive analysis wants. listing agents/offices, not these
    'BuyerAgentMlsId', 'BuyerAgentFirstName', 'BuyerAgentLastName',
    'CoListAgentFirstName', 'CoListAgentLastName', 'CoListOfficeName',
    # Board/association codes and commission fields -- not used by any dashboard, filter, or Week 6 metric
    'ListAgentAOR', 'BuyerAgentAOR', 'BuyerOfficeAOR',
    'AssociationFee', 'AssociationFeeFrequency',
    'BuyerAgencyCompensationType', 'BuyerAgencyCompensation',
    # Internal pipeline metadata, not market data
    'OriginatingSystemName', 'OriginatingSystemSubName',
    # Property amenity/feature fields not in any required metric or filter
    'Flooring', 'ViewYN', 'PoolPrivateYN', 'AttachedGarageYN',
    'ParkingTotal', 'GarageSpaces', 'Levels', 'NewConstructionYN',
    'MainLevelBedrooms', 'LotSizeArea', 'LotSizeSquareFeet',
    # School name fields -- Week 6 adds school districts via a separate lat/long join, not from these MLS text fields
    'ElementarySchool', 'MiddleOrJuniorSchool', 'HighSchool', 'HighSchoolDistrict',
    # No analytical value in a CA-only dataset
    'StateOrProvince',
    # Address components already covered by City/CountyOrParish/PostalCode
    'UnparsedAddress', 'StreetNumberNumeric', 'SubdivisionName',
]
cols_to_drop_judgment = [c for c in cols_to_drop_judgment if c in listings.columns]
listings = listings.drop(columns=cols_to_drop_judgment)
print(f"\nDropped {len(cols_to_drop_judgment)} unnecessary/redundant columns (judgment call, not >90% missing).")
print(f"Columns remaining: {len(listings.columns)}")
cols_after_drop = len(listings.columns)  # baseline for counting flag columns added later

# Step 3 - Flag invalid numeric values (business rules, not missingness)
# NaN values naturally evaluate to False in these comparisons, so missing
# data is NOT counted as invalid -- only impossible values are flagged.
listings['close_price_invalid_flag'] = listings['ClosePrice'] <= 0
listings['living_area_invalid_flag'] = listings['LivingArea'] <= 0
listings['dom_invalid_flag'] = listings['DaysOnMarket'] < 0
listings['bedrooms_invalid_flag'] = listings['BedroomsTotal'] < 0
listings['bathrooms_invalid_flag'] = listings['BathroomsTotalInteger'] < 0

print("\nInvalid numeric value counts:")
print(f"  ClosePrice <= 0: {listings['close_price_invalid_flag'].sum():,}")
print(f"  LivingArea <= 0: {listings['living_area_invalid_flag'].sum():,}")
print(f"  DaysOnMarket < 0: {listings['dom_invalid_flag'].sum():,}")
print(f"  Negative BedroomsTotal: {listings['bedrooms_invalid_flag'].sum():,}")
print(f"  Negative BathroomsTotalInteger: {listings['bathrooms_invalid_flag'].sum():,}")

# Step 4 - Date consistency flags
# violations of the Listing -> Purchase -> Close order are caught.
# Most listings won't have a CloseDate/PurchaseContractDate yet, so these
# counts will naturally be much smaller than in the sold dataset.
listings['listing_after_close_flag'] = listings['ListingContractDate'] > listings['CloseDate']
listings['purchase_after_close_flag'] = listings['PurchaseContractDate'] > listings['CloseDate']
listings['negative_timeline_flag'] = listings['ListingContractDate'] > listings['PurchaseContractDate']

print("\nDate consistency flag counts:")
print(f"  listing_after_close_flag: {listings['listing_after_close_flag'].sum():,}")
print(f"  purchase_after_close_flag: {listings['purchase_after_close_flag'].sum():,}")
print(f"  negative_timeline_flag: {listings['negative_timeline_flag'].sum():,}")

# Step 5 - Geographic data quality checks
# California's approximate bounding box, used only to catch coordinates
# that fall clearly outside the state -- not a precise state boundary.
CA_LAT_RANGE = (32.5, 42.0)
CA_LON_RANGE = (-124.5, -114.0)

listings['missing_coords_flag'] = listings['Latitude'].isnull() | listings['Longitude'].isnull()
listings['zero_coords_flag'] = (listings['Latitude'] == 0) | (listings['Longitude'] == 0)
listings['positive_longitude_flag'] = listings['Longitude'] > 0
listings['implausible_coords_flag'] = (
    listings['Latitude'].notnull() & listings['Longitude'].notnull() &
    (~listings['Latitude'].between(*CA_LAT_RANGE) | ~listings['Longitude'].between(*CA_LON_RANGE))
)

geo_summary = pd.DataFrame({
    'flag': ['missing_coords_flag', 'zero_coords_flag', 'positive_longitude_flag', 'implausible_coords_flag'],
    'count': [
        listings['missing_coords_flag'].sum(),
        listings['zero_coords_flag'].sum(),
        listings['positive_longitude_flag'].sum(),
        listings['implausible_coords_flag'].sum(),
    ]
})
print("\nGeographic data quality summary:")
print(geo_summary.to_string(index=False))
geo_summary.to_csv(output_folder / 'listings_geo_quality_summary.csv', index=False)
print("Geographic data quality summary saved.")

# Step 6 - Save cleaned, analysis-ready dataset
# No rows removed -- every check above is a flag column, not a filter.
listings.to_csv(csv_folder / 'listings_cleaned.csv', index=False)

rows_after = len(listings)
cols_after = len(listings.columns)
print(f"\nRows after cleaning: {rows_after:,} (unchanged -- no rows dropped)")
print(f"Columns after cleaning: {cols_after} (added {cols_after - cols_after_drop} flag columns, after dropping {len(cols_to_drop_judgment)} unnecessary columns from the original {cols_before})")
print("\nlistings_cleaned.csv saved. Done!")