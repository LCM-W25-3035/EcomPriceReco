import streamlit as st
import pandas as pd
import pickle
import matplotlib.pyplot as plt
import numpy as np
import os
from datetime import datetime, timedelta

# Set page configuration
st.set_page_config(
    page_title="Product Search & Price Prediction",
    layout="wide"
)

# Create session state for managing pages
if 'page' not in st.session_state:
    st.session_state.page = 'search'
if 'selected_product' not in st.session_state:
    st.session_state.selected_product = None

# Function to load data
@st.cache_data
def load_data(file_path='amazon_products.csv'):
    # Load CSV file
    df = pd.read_csv(file_path)
    
    # Clean discount_price and actual_price columns if they are strings
    if df['discount_price'].dtype == object:
        df['discount_price'] = df['discount_price'].str.replace('₹', '').str.replace(',', '').astype(float)
    if df['actual_price'].dtype == object:
        df['actual_price'] = df['actual_price'].str.replace('₹', '').str.replace(',', '').astype(float)
    
    return df

# Function to load the price prediction model and encoders
@st.cache_resource
def load_model_and_encoders():
    model = None
    encoders = None
    
    # Load Random Forest Model
    try:
        with open('random_forest_model.pkl', 'rb') as file:
            model = pickle.load(file)
        st.sidebar.success("Random Forest model loaded successfully!")
    except FileNotFoundError:
        st.sidebar.warning("Model file 'random_forest_model.pkl' not found.")
    
    # Load Label Encoders
    try:
        with open('label_encoders.pkl', 'rb') as file:
            encoders = pickle.load(file)
        st.sidebar.success("Label encoders loaded successfully!")
    except FileNotFoundError:
        st.sidebar.warning("Encoders file 'label_encoders.pkl' not found.")
    
    return model, encoders

def predict_price(model, encoders, product):
    if model is None or encoders is None:
        return None
    
    try:
        # List of all features in the exact order expected by the model
        expected_features = [
            'name', 'main_category', 'sub_category', 'ratings', 'no_of_ratings',
            'discount_price', 'actual_price', 'discounted_price_1', 'discounted_price_2',
            'discounted_price_3', 'discounted_price_4', 'discounted_price_5',
            'discounted_price_6', 'discounted_price_7', 'discount_percentage',
            'price_ratio', 'popularity_score', 'price_difference', 'log_no_of_ratings',
            'main_category_encoded', 'sub_category_encoded'
        ]
        
        # Initialize feature vector with appropriate values
        feature_values = []
        
        for feature in expected_features:
            if feature == 'name':
                # For 'name', we just use a placeholder as it's likely not used in prediction
                feature_values.append(0)
            elif feature == 'main_category':
                # Skip this categorical feature - we'll use the encoded version
                # But still need a numeric placeholder for the model
                feature_values.append(0)
            elif feature == 'sub_category':
                # Skip this categorical feature - we'll use the encoded version
                # But still need a numeric placeholder for the model
                feature_values.append(0)
            elif feature == 'main_category_encoded':
                # Handle the encoded main category
                if 'main_category' in product and 'main_category' in encoders:
                    feature_values.append(encoders['main_category'].transform([str(product['main_category'])])[0])
                else:
                    feature_values.append(0)
            elif feature == 'sub_category_encoded':
                # Handle the encoded sub category
                if 'sub_category' in product and 'sub_category' in encoders:
                    feature_values.append(encoders['sub_category'].transform([str(product['sub_category'])])[0])
                else:
                    feature_values.append(0)
            elif feature == 'discount_percentage':
                # Calculate discount percentage if not already present
                if 'discount_percentage' in product:
                    feature_values.append(float(product['discount_percentage']))
                else:
                    # Calculate it from discount_price and actual_price
                    if 'discount_price' in product and 'actual_price' in product:
                        discount_pct = ((float(product['actual_price']) - float(product['discount_price'])) / 
                                         float(product['actual_price'])) * 100
                        feature_values.append(discount_pct)
                    else:
                        feature_values.append(0)
            elif feature == 'price_ratio':
                # Calculate price ratio if not already present
                if 'price_ratio' in product:
                    feature_values.append(float(product['price_ratio']))
                else:
                    # Calculate it from discount_price and actual_price
                    if 'discount_price' in product and 'actual_price' in product and float(product['actual_price']) != 0:
                        price_ratio = float(product['discount_price']) / float(product['actual_price'])
                        feature_values.append(price_ratio)
                    else:
                        feature_values.append(1)  # Default to 1 if no discount
            elif feature == 'popularity_score':
                # Calculate popularity score if not already present
                if 'popularity_score' in product:
                    feature_values.append(float(product['popularity_score']))
                else:
                    # Make a simple popularity score from ratings and number of ratings
                    if 'ratings' in product and 'no_of_ratings' in product:
                        pop_score = float(product['ratings']) * np.log1p(float(product['no_of_ratings']))
                        feature_values.append(pop_score)
                    else:
                        feature_values.append(0)
            elif feature == 'price_difference':
                # Calculate price difference if not already present
                if 'price_difference' in product:
                    feature_values.append(float(product['price_difference']))
                else:
                    # Calculate it from discount_price and actual_price
                    if 'discount_price' in product and 'actual_price' in product:
                        price_diff = float(product['actual_price']) - float(product['discount_price'])
                        feature_values.append(price_diff)
                    else:
                        feature_values.append(0)
            elif feature == 'log_no_of_ratings':
                # Calculate log of number of ratings if not already present
                if 'log_no_of_ratings' in product:
                    feature_values.append(float(product['log_no_of_ratings']))
                else:
                    # Calculate it from no_of_ratings
                    if 'no_of_ratings' in product:
                        log_ratings = np.log1p(float(product['no_of_ratings']))
                        feature_values.append(log_ratings)
                    else:
                        feature_values.append(0)
            else:
                # For all other features, use the product value if available
                if feature in product:
                    # Ensure the value is numeric
                    try:
                        feature_values.append(float(product[feature]))
                    except (ValueError, TypeError):
                        # If conversion fails, use 0
                        feature_values.append(0)
                else:
                    # Default to 0 if the feature is missing
                    feature_values.append(0)
        
        # Convert feature values to numpy array
        X = np.array(feature_values, dtype=float).reshape(1, -1)
        
        # Make prediction
        predicted_price = model.predict(X)[0]
        return predicted_price
        
    except Exception as e:
        st.error(f"Error in prediction: {str(e)}")
        st.error(f"Debug info - Feature values: {feature_values if 'feature_values' in locals() else 'Not created'}")
        return None

  
# Function to generate historical price data from discounted prices
def generate_historical_prices(product):
    # Use the discounted price columns to create historical data
    price_columns = [col for col in product.index if col.startswith('discounted_price_')]
    prices = [product[col] for col in price_columns if not pd.isna(product[col])]
    
    # Add current discount price
    prices.append(product['discount_price'])
    
    # Generate dates for the past few days/weeks
    today = datetime.now()
    dates = [(today - timedelta(days=i*7)).strftime('%Y-%m-%d') for i in range(len(prices)-1, -1, -1)]
    
    return dates, prices

# Function to show search page
def show_search_page():
    st.title("Amazon Product Search")
    st.write("Search for products based on keywords. Click on any product to see price prediction and trends.")
    
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
    
    if not df.empty:
        # Search input
        search_query = st.text_input("Search for products", "")
        
        # Define function to search products
        def search_products(df, search_query):
            if not search_query:
                return df
            
            # Convert search query to lowercase for case-insensitive search
            search_query = search_query.lower()
            
            # Create a mask for filtering products
            mask = df['name'].fillna('').str.lower().str.contains(search_query)
            # Return filtered dataframe
            return df[mask]
        
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
                        product_index = filtered_df.index[i + j]
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
                            
                            # Button to view price prediction and trends
                            if st.button(f"View Price Prediction", key=f"view_{product_index}"):
                                st.session_state.selected_product = product
                                st.session_state.page = 'prediction'
                                st.rerun()
                            
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

# Function to show prediction page
def show_prediction_page():
    if st.session_state.selected_product is None:
        st.error("No product selected. Please go back and select a product.")
        return
    
    # Get the selected product
    product = st.session_state.selected_product
    
    # Back button
    if st.button("← Back to Search"):
        st.session_state.page = 'search'
        st.rerun()
    
    # Title
    st.title("Price Recommendation & Trends")
    
    # Display product details
    col1, col2 = st.columns([1, 2])
    
    with col1:
        if 'image' in product and pd.notna(product['image']):
            st.image(product['image'], width=200)
    
    with col2:
        st.subheader(product['name'])
        st.write(f"Current Price: **₹{int(product['discount_price']):,}**")
        st.write(f"Original Price: ₹{int(product['actual_price']):,}")
        if 'ratings' in product and pd.notna(product['ratings']):
            st.write(f"Rating: ⭐ {product['ratings']} ({product['no_of_ratings']} reviews)")
        if 'link' in product and pd.notna(product['link']):
            st.markdown(f"[View on Amazon]({product['link']})")
    
    # Load prediction model and encoders
    model, encoders = load_model_and_encoders()
    
    # Divider
    st.markdown("---")
    
    # Create two columns for price prediction and price trend
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Price Prediction")
        
        if model is not None and encoders is not None:
            # Make prediction
            predicted_price = predict_price(model, encoders, product)
            
            if predicted_price is not None:
                st.metric(
                    label="Predicted Future Price",
                    value=f"₹{int(predicted_price):,}",
                    delta=f"{int(predicted_price - product['discount_price']):,}"
                )
                
                # Add prediction explanation
                current_price = product['discount_price']
                if predicted_price > current_price:
                    st.info(f"The price is predicted to increase by ₹{int(predicted_price - current_price):,} in the near future. Consider buying now.")
                elif predicted_price < current_price:
                    st.success(f"The price is predicted to decrease by ₹{int(current_price - predicted_price):,} in the near future. Consider waiting for a better deal.")
                else:
                    st.info("The price is predicted to remain stable in the near future.")
            else:
                st.warning("Unable to make a price prediction for this product.")
        else:
            if model is None:
                st.warning("Random Forest model not available. Please upload the model file.")
                
                # Model upload option
                model_file = st.file_uploader("Upload random_forest_model.pkl", type=['pkl'])
                if model_file is not None:
                    # Save the uploaded model file
                    with open('random_forest_model.pkl', 'wb') as f:
                        f.write(model_file.getbuffer())
                    st.success("Model file uploaded successfully! Please refresh the page.")
            
            if encoders is None:
                st.warning("Label encoders not available. Please upload the encoders file.")
                
                # Encoders upload option
                encoders_file = st.file_uploader("Upload label_encoders.pkl", type=['pkl'])
                if encoders_file is not None:
                    # Save the uploaded encoders file
                    with open('label_encoders.pkl', 'wb') as f:
                        f.write(encoders_file.getbuffer())
                    st.success("Encoders file uploaded successfully! Please refresh the page.")
    
    with col2:
        st.subheader("Price History Trend")
        
        # Generate historical price data
        dates, prices = generate_historical_prices(product)
        
        # Create price trend chart
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(dates, prices, marker='o', linestyle='-', color='#1f77b4')
        
        # Add labels and title
        ax.set_xlabel('Date')
        ax.set_ylabel('Price (₹)')
        ax.set_title('Historical Price Trend')
        
        # Format y-axis ticks as rupees
        ax.set_yticks(sorted(prices))
        ax.set_yticklabels([f'₹{int(price):,}' for price in sorted(prices)])
        
        # Rotate x-axis labels for better readability
        plt.xticks(rotation=45)
        
        # Show grid
        ax.grid(True, linestyle='--', alpha=0.7)
        
        # Tight layout
        plt.tight_layout()
        
        # Display the chart
        st.pyplot(fig)
        
        # Add price trend explanation
        price_diff = prices[-1] - prices[0]
        percent_change = (price_diff / prices[0]) * 100
        
        if percent_change > 0:
            st.info(f"The price has increased by {abs(percent_change):.1f}% over the displayed period.")
        elif percent_change < 0:
            st.success(f"The price has decreased by {abs(percent_change):.1f}% over the displayed period.")
        else:
            st.info("The price has remained stable over the displayed period.")

# Main app logic to show the appropriate page
if st.session_state.page == 'search':
    show_search_page()
elif st.session_state.page == 'prediction':
    show_prediction_page()

# Add about section in sidebar
st.sidebar.markdown("---")
st.sidebar.header("About")
st.sidebar.info(
    "This is a product search engine with price prediction functionality. "
    "Search for products and click on any product to see its predicted future price and historical price trends."
)

# Add model files upload option in sidebar
st.sidebar.markdown("---")
st.sidebar.header("Model Files Upload")

# Random Forest model upload
rf_model_file = st.sidebar.file_uploader("Upload random_forest_model.pkl", type=['pkl'], key="rf_model_sidebar")
if rf_model_file is not None:
    # Save the uploaded model file
    with open('random_forest_model.pkl', 'wb') as f:
        f.write(rf_model_file.getbuffer())
    st.sidebar.success("Random Forest model uploaded successfully!")

# Label encoders upload
encoders_file = st.sidebar.file_uploader("Upload label_encoders.pkl", type=['pkl'], key="encoders_sidebar")
if encoders_file is not None:
    # Save the uploaded encoders file
    with open('label_encoders.pkl', 'wb') as f:
        f.write(encoders_file.getbuffer())
    st.sidebar.success("Label encoders uploaded successfully!")