import streamlit as st
import pandas as pd
import re

# Set page configuration
st.set_page_config(
    page_title="Product Search Engine",
    layout="wide"
)

# Function to load data
@st.cache_data
def load_data(file_path="C:\\Users\\vishn\\\Downloads\\updated_price_tracking_data3.csv"):
    # Load CSV file
    df = pd.read_csv(file_path)
    
    # Clean discount_price and actual_price columns if they are strings
    if df['discount_price'].dtype == object:
        df['discount_price'] = df['discount_price'].str.replace('₹', '').str.replace(',', '').astype(float)
    if df['actual_price'].dtype == object:
        df['actual_price'] = df['actual_price'].str.replace('₹', '').str.replace(',', '').astype(float)
    
    return df

# Upload CSV file
uploaded_file = st.sidebar.file_uploader("Upload your CSV file", type=['csv'])

if uploaded_file is not None:
    # Load data from uploaded file
    df = load_data(uploaded_file)
else:
    # Use default file path
    try:
        df = load_data()
        st.sidebar.success("Using default CSV file: amazon_products.csv")
    except FileNotFoundError:
        st.sidebar.error("Default CSV file not found. Please upload a file.")
        # Create empty DataFrame
        df = pd.DataFrame()

# Define function to search products
def search_products(df, search_query):
    if not search_query or df.empty:
        return df
    
    # Convert search query to lowercase for case-insensitive search
    search_query = search_query.lower()
    
    # Create a mask for filtering products
    mask = df['name'].str.lower().str.contains(search_query)
    
    # Return filtered dataframe
    return df[mask]

# App title and description
st.title("Amazon Product Search")
st.write("Search for products based on keywords. Example: try searching for 'filter', 'camera', etc.")

if not df.empty:
    # Search input
    search_query = st.text_input("Search for products", "")

    # Filter products based on search query
    filtered_df = search_products(df, search_query)

    # Display number of results
    st.write(f"Found {len(filtered_df)} results")

    # Display product cards
    if not filtered_df.empty:
        # Create columns for product display
        num_cols = 3
        
        for i in range(0, len(filtered_df), num_cols):
            cols = st.columns(num_cols)
            
            for j in range(num_cols):
                if i + j < len(filtered_df):
                    product = filtered_df.iloc[i + j]
                    
                    with cols[j]:
                        # Display image if image URL is available
                        if 'image' in product and pd.notna(product['image']):
                            st.image(product['image'], width=150)
                        
                        # Display product name
                        name_display = product['name']
                        if len(name_display) > 50:
                            name_display = name_display[:50] + "..."
                        st.write(f"**{name_display}**")
                        
                        # Display ratings if available
                        if 'ratings' in product and pd.notna(product['ratings']):
                            st.write(f"Rating: ⭐ {product['ratings']} ({product['no_of_ratings']} reviews)")
                        
                        # Calculate discount percentage
                        discount = round(((product['actual_price'] - product['discount_price']) / product['actual_price']) * 100)
                        
                        st.write(f"**₹{int(product['discount_price']):,}**  ~~₹{int(product['actual_price']):,}~~  ({discount}% off)")
                        
                        # Display link if available
                        if 'link' in product and pd.notna(product['link']):
                            st.markdown(f"[View on Amazon]({product['link']})")
                        
                        st.markdown("---")
    else:
        st.warning("No products found matching your search query.")

    # Add filters in sidebar
    st.sidebar.header("Filters")

    # Main category filter (if you have multiple categories)
    if 'main_category' in df.columns and len(df['main_category'].unique()) > 1:
        selected_categories = st.sidebar.multiselect(
            "Select Main Categories",
            options=sorted(df['main_category'].unique()),
            default=[]
        )

    # Price range filter
    min_price = int(df['discount_price'].min())
    max_price = int(df['discount_price'].max())

    price_range = st.sidebar.slider(
        "Price Range (₹)",
        min_value=min_price,
        max_value=max_price,
        value=(min_price, max_price)
    )

    # Rating filter
    if 'ratings' in df.columns:
        rating_options = sorted(df['ratings'].unique(), reverse=True)
        selected_ratings = st.sidebar.multiselect(
            "Minimum Rating",
            options=rating_options,
            default=[]
        )
else:
    st.warning("Please upload a CSV file or make sure the default CSV file is available.")

# Add about section in sidebar
st.sidebar.markdown("---")
st.sidebar.header("About")
st.sidebar.info(
    "This is a simple product search engine built with Streamlit. "
    "It allows you to search for products based on keywords and apply filters."
)