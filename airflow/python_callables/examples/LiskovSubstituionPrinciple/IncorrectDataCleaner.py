import pandas as pd

csv_data = pd.DataFrame({
    "Name": ["Eric", None, "Bob"],
    "Date": ["2022-01-01", "2022-02-01", None]
})

api_data = pd.DataFrame({
    "Name": ["Eric", None, "Bob"],
    "Date": ["2022-03-01", None, "2022-04-01"]
})

# Base class
class DataCleaner:
    def clean_missing_values(self, data):
        # Default: Replace missing values with 0
        return data.fillna(0)

    def format_dates(self, data, column):
        # Convert column to datetime format
        data[column] = pd.to_datetime(data[column], errors='coerce')
        return data
    
# Subclass that violates LSP
class ApiCleaner(DataCleaner):
    def clean_missing_values(self, data):
        # Different behavior: Drop rows with missing values instead
        return data.dropna()

# Subclass that follows the base class behavior
class CsvCleaner(DataCleaner):
    pass  # Uses default behavior of the base class

def clean_data(data_cleaner, data):
    data = data_cleaner.clean_missing_values(data)
    data = data_cleaner.format_dates(data, "Date")
    return data

csv_cleaner = CsvCleaner()
api_cleaner = ApiCleaner()

cleaned_csv = clean_data(csv_cleaner, csv_data)
cleaned_api = clean_data(api_cleaner, api_data)

print("CSV Data:\n", cleaned_csv)
print("\nAPI Data:\n", cleaned_api)