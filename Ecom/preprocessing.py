import pandas as pd
import re
from app import get_database, get_collection
import streamlit as st
import pandas as pd
from PIL import Image
import requests
from io import BytesIO

def fetch_data_from_collection(collection_name):
    """Fetch all documents from the specified collection."""
    try:
        print("Fetching Data from Mongodb.")
        # Get the database connection
        db = get_database()

        # Get the collection
        collection = get_collection(db, collection_name)

        # Fetch all documents
        documents = collection.find()
        return documents
        # print("Documents fetched successfully:")
        # for doc in documents:
        #     print(doc)
    except Exception as e:
        print("Error fetching data:", e)

def preprocessing(collection_name):
    data= fetch_data_from_collection(collection_name)
    data = pd.DataFrame(data)

    # Droping the MongoDB "_id" column
    if "_id" in data.columns:
        data.drop(columns=["_id"], inplace=True)
    
    # file_path = "C://Users//jesel sequeira//Downloads//output_data2.csv"
    # data = pd.(file_path)

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

    output_file_path = 'pre-processed_data0302.csv'
    data.to_csv(output_file_path, index=False)

    output_file_path

# Function to fetch unique categories from MongoDB
def fetch_categories(collection_name):
    db = get_database()
    collection = get_collection(db, collection_name)
    categories = collection.distinct('main_category') 
    return categories

# Function to fetch unique sub-categories based on the main category
def fetch_sub_categories(collection_name, main_category):
    db = get_database()
    collection = get_collection(db, collection_name)
    sub_categories = collection.distinct('sub_category', {'main_category': main_category})  
    return sub_categories

# Function to fetch product data from MongoDB based on main and sub category
def fetch_products(collection_name, main_category=None, sub_category=None, limit=20, skip=0):
    db = get_database()
    collection = db[collection_name] 
    query = {}
    if main_category:
        query['main_category'] = main_category
    if sub_category:
        query['sub_category'] = sub_category
    
    # Fetch only 'limit' number of products, starting from 'skip' offset for pagination
    products = collection.find(query).skip(skip).limit(limit)
    return pd.DataFrame(list(products))

# Function to fetch random products
def fetch_random_products(collection_name, limit=10):
    db = get_database()
    collection = db[collection_name]  
    products = collection.aggregate([{"$sample": {"size": limit}}]) 
    return pd.DataFrame(list(products))

def fetch_products_by_name(collection_name, product_name, limit=20, skip=0):
    db = get_database()
    collection = db[collection_name] 
    # Query MongoDB to find products matching the product name (case-insensitive)
    query = {"name": {"$regex": product_name, "$options": "i"}}  # MongoDB regex search for case-insensitive match
    
    # Fetch products using the query, skip, and limit# Fetch products using the query, skip, and limit
    products_cursor = collection.find(query).skip(skip).limit(limit)
    products_list = list(products_cursor)
    
    # Convert the MongoDB query result into a pandas DataFrame
    if products_list:
        return pd.DataFrame(products_list)
    else:
        return pd.DataFrame()  # Return an empty DataFrame if no products are found

# Function to safely load an image from a URL
def load_image_from_url(image_url, size=(300, 300)):
    try:
        response = requests.get(image_url)
        if response.status_code == 200:
            img = Image.open(BytesIO(response.content))
            img = img.resize(size)
            return img
        else:
            st.warning(f"Failed to load image from URL: {image_url}. HTTP Status Code: {response.status_code}")
            return None
    except Exception as e:
        st.warning(f"Error loading image from URL {image_url}: {e}")
        return None

# Integrate the product fetching and display logic in the main Streamlit function
def integrate(collection_name):
    st.set_page_config(page_title="PriceReco - Pricing Optimization", page_icon="💰", layout="centered")

    # Title and description
    st.title("PriceReco")
    st.subheader("Analyze, Adjust & Optimize your pricing")
    st.write("Unlock the full potential of your pricing strategy with our insights.")
    st.write("Browse through the recommended products based on your selection!")

    # Display category and sub-category dropdowns side by side
    col1, col2 = st.columns(2)

    with col1:
        # Initial blank selection for main category
        main_category = st.selectbox("Select the main product category:", [""] + fetch_categories(collection_name))

    with col2:
        sub_category = None
        # Show sub-category dropdown only if a main category is selected
        if main_category:
            sub_categories = fetch_sub_categories(collection_name, main_category)
            if sub_categories:
                sub_category = st.selectbox("Select the sub-category:", sub_categories)
            else:
                st.warning("No sub-categories available for the selected category!")

    # Input box for searching by product name directly
    search_query = st.text_input("Or, search by product name directly:")

    # Initially, display top trending products (before user selection)
    st.subheader("Top Trending Products:")
    trending_products = fetch_random_products(collection_name, limit=5)
    if not trending_products.empty:
        for index, product in trending_products.iterrows():
            st.write(f"**Name**: {product['name']}")
            st.write(f"**Category**: {product['main_category']} - {product['sub_category']}")
            st.write(f"**Ratings**: {product['ratings']} ({product['no_of_ratings']} reviews)")
            st.write(f"**Discounted Price**: ₹{product['discount_price']}")
            st.write(f"**Original Price**: ₹{product['actual_price']}")
            st.write(f"[View Product on Amazon]({product['link']})")
    else:
        st.write("No trending products found.")

    # Only show products after user selection or search
    if search_query:  # Search by product name directly
        filtered_products = fetch_products_by_name(collection_name, search_query)
        if not filtered_products.empty:
            st.subheader(f"Search Results for '{search_query}':")
            for index, product in filtered_products.iterrows():
                st.write(f"**Name**: {product['name']}")
                st.write(f"**Category**: {product['main_category']} - {product['sub_category']}")
                st.write(f"**Ratings**: {product['ratings']} ({product['no_of_ratings']} reviews)")
                st.write(f"**Discounted Price**: ₹{product['discount_price']}")
                st.write(f"**Original Price**: ₹{product['actual_price']}")
                st.write(f"[View Product on Amazon]({product['link']})")
        else:
            st.write(f"No products found for '{search_query}'.")

    elif (main_category and sub_category):  # Show products based on category selection
        filtered_products = fetch_products(collection_name, main_category, sub_category)
        if not filtered_products.empty:
            st.subheader(f"Products in {main_category} - {sub_category}:")
            for index, product in filtered_products.iterrows():
                st.write(f"**Name**: {product['name']}")
                st.write(f"**Category**: {product['main_category']} - {product['sub_category']}")
                st.write(f"**Ratings**: {product['ratings']} ({product['no_of_ratings']} reviews)")
                st.write(f"**Discounted Price**: ₹{product['discount_price']}")
                st.write(f"**Original Price**: ₹{product['actual_price']}")
                st.write(f"[View Product on Amazon]({product['link']})")
        else:
            st.write("No products found for the selected category and sub-category.")

    else:
        st.write("Please select a category and sub-category or enter a product name to search.")
