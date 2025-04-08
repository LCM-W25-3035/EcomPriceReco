
# llm- chatgpt 
# prompt: I gave the codes untitled1.ipynb and feature_engineering.ipynb and asked to combine into .py file 
# (made it into .py because we can further integrate to mongodb)

# price_tracking_preprocessing.py

import pandas as pd
import numpy as np

# Load initial data
df = pd.read_csv('updated_price_tracking_data (3).csv')

# Display basic info (optional debug)
print(df.info())
print(df.describe())
print(df.head(10))
print("Missing values before cleaning:\n", df.isna().sum())

# Function to clean numeric columns
def clean_numeric(column):
    return pd.to_numeric(df[column].astype(str).str.replace("₹", "").str.replace(",", ""), errors='coerce')

# Clean numeric columns
df["ratings"] = clean_numeric("ratings")
df["no_of_ratings"] = clean_numeric("no_of_ratings")
df["discount_price"] = clean_numeric("discount_price")
df["actual_price"] = clean_numeric("actual_price")

# Fill missing values with mean or corresponding values
df["ratings"].fillna(df["ratings"].mean(), inplace=True)
df["no_of_ratings"].fillna(df["no_of_ratings"].mean(), inplace=True)
df["discount_price"].fillna(df["actual_price"], inplace=True)
df["actual_price"].fillna(df["discount_price"], inplace=True)

# Drop unnecessary columns
df.drop(columns=["Unnamed: 0", "image", "link"], inplace=True)

# Discount Percentage
df["discount_percentage"] = ((df["actual_price"] - df["discount_price"]) / df["actual_price"]) * 100

# Price Ratio
df["price_ratio"] = df["discount_price"] / df["actual_price"]

# Popularity Score
df["popularity_score"] = df["ratings"] * np.log1p(df["no_of_ratings"])

# Price Difference
df["price_difference"] = df["actual_price"] - df["discount_price"]

# Log transformation of ratings and number of ratings
df["log_no_of_ratings"] = np.log1p(df["no_of_ratings"])

# Category Encoding
df["main_category_encoded"] = df["main_category"].astype('category').cat.codes
df["sub_category_encoded"] = df["sub_category"].astype('category').cat.codes

# Save final feature-engineered data
final_file_path = "Feature_engineered_price_tracking_data2.csv"
df.to_csv(final_file_path, index=False)

print("Feature engineering complete. File saved at:", final_file_path)
