import pandas as pd
import re

# Load the dataset
file_path = "C://Users//jesel sequeira//Downloads//output_data2.csv"
data = pd.read_csv(file_path)

# Display the first few rows to understand the data
print("Original Data:")
print(data.head())

print("\nNull Values in Each Column:")
print(data.isnull().sum())

# Preprocessing steps

# 1. Handle missing values
data = data.fillna({
    'name': 'Unknown',
    'main_category': 'Unknown',
    'sub_category': 'Unknown',
    'image': 'No Image',
    'link': 'No Link'
})

# 2. Convert numerical columns to appropriate data types
data['ratings'] = pd.to_numeric(data['ratings'], errors='coerce').where(pd.to_numeric(data['ratings'], errors='coerce').notnull(), None)
data['no_of_ratings'] = pd.to_numeric(data['no_of_ratings'], errors='coerce').where(pd.to_numeric(data['no_of_ratings'], errors='coerce').notnull(), None)

# Fill NaN in 'ratings' column with median of respective 'sub_category' for missing values only
data['ratings'] = data['ratings'].fillna(data.groupby('sub_category')['ratings'].transform('median'))

# Fill NaN in 'no_of_ratings' column with median of respective 'sub_category' for missing values only
data['no_of_ratings'] = data['no_of_ratings'].fillna(data.groupby('sub_category')['no_of_ratings'].transform('median'))

print("\nNull Values in Each Column:")
print(data.isnull().sum())

def clean_price_column(column):
    # Remove special characters and non-numeric characters except for decimal points
    column = column.replace(r'[^\d.]', '', regex=True)
    
    # Convert to numeric values, errors='coerce' will turn invalid parsing into NaN (null)
    return pd.to_numeric(column, errors='coerce')

data['discount_price'] = clean_price_column(data['discount_price'])
data['actual_price'] = clean_price_column(data['actual_price'])
data['Price'] = clean_price_column(data['Price'])

# Function to fill 'discount_price' for each row
def fill_discount_price(row):
    if pd.isna(row['discount_price']):
        # If discount_price is NaN, fill based on priority order
        if not pd.isna(row['actual_price']):
            return row['actual_price']
        elif not pd.isna(row['Price']):
            return row['Price']
        else:
            # Group by 'sub_category' and get median of 'discount_price' in that category
            return data[data['sub_category'] == row['sub_category']]['discount_price'].median() 
    return row['discount_price']  # Keep existing value

# Function to fill 'actual_price' for each row
def fill_actual_price(row):
    if pd.isna(row['actual_price']):
        # If actual_price is NaN, fill based on priority order
        if not pd.isna(row['discount_price']):
            return row['discount_price']
        elif not pd.isna(row['Price']):
            return row['Price']
        else:
            # Group by 'sub_category' and get median of 'actual_price' in that category
            return data[data['sub_category'] == row['sub_category']]['actual_price'].median() 
    return row['actual_price']  # Keep existing value

# Apply row-wise logic
data['actual_price'] = data.apply(fill_actual_price, axis=1)
data['discount_price'] = data.apply(fill_discount_price, axis=1)

data=data.drop(columns=["Price"])

output_file_path = 'pre-processed_data0302.csv'
data.to_csv(output_file_path, index=False)

output_file_path