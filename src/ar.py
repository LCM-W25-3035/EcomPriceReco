import streamlit as st
import pandas as pd
import pickle
import matplotlib.pyplot as plt
import numpy as np
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

# Function to load data from CSV file
@st.cache_data
def load_data_from_csv():
    # Load the data from the CSV file
    df = pd.read_csv(r"C:\Users\Diksha\Downloads\Diksha_ecom_try\Diksha_ecom\test.csv")
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

# Function to predict price
def predict_price(model, encoders, product):
    if model is None or encoders is None:
        return None
    
    try:
        expected_features = [
            'name', 'main_category', 'sub_category', 'ratings', 'no_of_ratings',
            'discount_price', 'actual_price', 'discounted_price_1', 'discounted_price_2',
            'discounted_price_3', 'discounted_price_4', 'discounted_price_5',
            'discounted_price_6', 'discounted_price_7', 'discount_percentage',
            'price_ratio', 'popularity_score', 'price_difference', 'log_no_of_ratings',
            'main_category_encoded', 'sub_category_encoded'
        ]
        
        feature_values = []
        
        for feature in expected_features:
            if feature == 'name':
                feature_values.append(0)
            elif feature == 'main_category_encoded':
                if 'main_category' in product and 'main_category' in encoders:
                    feature_values.append(encoders['main_category'].transform([product['main_category']])[0])
                else:
                    feature_values.append(0)
            elif feature == 'sub_category_encoded':
                if 'sub_category' in product and 'sub_category' in encoders:
                    feature_values.append(encoders['sub_category'].transform([product['sub_category']])[0])
                else:
                    feature_values.append(0)
            elif feature == 'discount_percentage':
                if 'discount_percentage' in product:
                    feature_values.append(product['discount_percentage'])
                else:
                    if 'discount_price' in product and 'actual_price' in product:
                        discount_pct = ((product['actual_price'] - product['discount_price']) / 
                                         product['actual_price']) * 100
                        feature_values.append(discount_pct)
                    else:
                        feature_values.append(0)
            elif feature == 'price_ratio':
                if 'price_ratio' in product:
                    feature_values.append(product['price_ratio'])
                else:
                    if 'discount_price' in product and 'actual_price' in product and product['actual_price'] != 0:
                        price_ratio = product['discount_price'] / product['actual_price']
                        feature_values.append(price_ratio)
                    else:
                        feature_values.append(1)
            elif feature == 'popularity_score':
                if 'popularity_score' in product:
                    feature_values.append(product['popularity_score'])
                else:
                    if 'ratings' in product and 'no_of_ratings' in product:
                        pop_score = product['ratings'] * np.log1p(product['no_of_ratings'])
                        feature_values.append(pop_score)
                    else:
                        feature_values.append(0)
            elif feature == 'price_difference':
                if 'price_difference' in product:
                    feature_values.append(product['price_difference'])
                else:
                    if 'discount_price' in product and 'actual_price' in product:
                        price_diff = product['actual_price'] - product['discount_price']
                        feature_values.append(price_diff)
                    else:
                        feature_values.append(0)
            elif feature == 'log_no_of_ratings':
                if 'log_no_of_ratings' in product:
                    feature_values.append(product['log_no_of_ratings'])
                else:
                    if 'no_of_ratings' in product:
                        log_ratings = np.log1p(product['no_of_ratings'])
                        feature_values.append(log_ratings)
                    else:
                        feature_values.append(0)
            else:
                if feature in product:
                    feature_values.append(product[feature])
                else:
                    feature_values.append(0)
        
        X = np.array(feature_values).reshape(1, -1)
        
        predicted_price = model.predict(X)[0]
        return predicted_price
        
    except Exception as e:
        st.error(f"Error in prediction: {str(e)}")
        return None
    
# Function to generate historical price data from discounted prices
def generate_historical_prices(product):
    price_columns = [col for col in product.index if col.startswith('discounted_price_')]
    prices = [product[col] for col in price_columns if not pd.isna(product[col])]
    prices.append(product['discount_price'])
    today = datetime.now()
    dates = [(today - timedelta(days=i*7)).strftime('%Y-%m-%d') for i in range(len(prices)-1, -1, -1)]
    return dates, prices

# Function to show search page
def show_search_page():
    st.title("Product Search")
    st.write("Search for products based on keywords. Click on any product to see price prediction and trends.")
    
    # Load data from CSV
    df = load_data_from_csv()
    
    if not df.empty:
        # Search input
        search_query = st.text_input("Search for products", "")
        
        # Define function to search products
        def search_products(df, search_query):
            if not search_query:
                return df
            
            search_query = search_query.lower()
            mask = df['name'].fillna('').str.lower().str.contains(search_query)
            return df[mask]
        
        filtered_df = search_products(df, search_query)
        
        st.write(f"Found {len(filtered_df)} results")
        
        if not filtered_df.empty:
            num_cols = 3
            for i in range(0, len(filtered_df), num_cols):
                cols = st.columns(num_cols)
                for j in range(num_cols):
                    if i + j < len(filtered_df):
                        product_index = filtered_df.index[i + j]
                        product = filtered_df.iloc[i + j]
                        with cols[j]:
                            if 'image' in product and pd.notna(product['image']):
                                st.image(product['image'], width=150)
                            name_display = product['name']
                            if len(name_display) > 50:
                                name_display = name_display[:50] + "..."
                            st.write(f"**{name_display}**")
                            if 'ratings' in product and pd.notna(product['ratings']):
                                st.write(f"Rating: ⭐ {product['ratings']} ({product['no_of_ratings']} reviews)")
                            discount = round(((product['actual_price'] - product['discount_price']) / product['actual_price']) * 100)
                            st.write(f"**₹{int(product['discount_price']):,}**  ~~₹{int(product['actual_price']):,}~~  ({discount}% off)")
                            if st.button(f"View Price Prediction", key=f"view_{product_index}") :
                                st.session_state.selected_product = product
                                st.session_state.page = 'prediction'
                                st.rerun()
                            st.markdown("---")
        else:
            st.warning("No products found matching your search query.")
    else:
        st.warning("No product data available in the CSV file.")

# Function to show prediction page
def show_prediction_page():
    if st.session_state.selected_product is None:
        st.error("No product selected. Please go back and select a product.")
        return
    
    product = st.session_state.selected_product
    
    if st.button("← Back to Search"):
        st.session_state.page = 'search'
        st.rerun()
    
    st.title("Price Prediction & Trends")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        if 'image' in product and pd.notna(product['image']):
            st.image(product['image'], width=150)
        
    with col2:
        # Show product name and details
        st.write(f"**{product['name']}**")
        st.write(f"**Category:** {product['main_category']} > {product['sub_category']}")
        st.write(f"**Rating:** ⭐ {product['ratings']} ({product['no_of_ratings']} reviews)")
        st.write(f"**Actual Price:** ₹{int(product['actual_price']):,}")
        st.write(f"**Discount Price:** ₹{int(product['discount_price']):,}")
        
        # Load the model and encoders
        model, encoders = load_model_and_encoders()
        
        # Predict the price
        predicted_price = predict_price(model, encoders, product)
        
        if predicted_price is not None:
            st.write(f"### Predicted Price: ₹{int(predicted_price):,}")
        else:
            st.warning("Price prediction not available for this product.")
        
        # Historical price trend (if applicable)
        if 'discounted_price_1' in product and 'discounted_price_2' in product:
            dates, prices = generate_historical_prices(product)
            st.write("### Price Trend Over Time")
            fig, ax = plt.subplots(figsize=(10, 5))
            ax.plot(dates, prices, marker='o', linestyle='-', color='b')
            ax.set_xlabel('Date')
            ax.set_ylabel('Price (₹)')
            ax.set_title(f"Price Trend for {product['name']}")
            plt.xticks(rotation=45)
            st.pyplot(fig)

# Main function to route between pages
def main():
    if st.session_state.page == 'search':
        show_search_page()
    elif st.session_state.page == 'prediction':
        show_prediction_page()

if __name__ == "__main__":
    main()
