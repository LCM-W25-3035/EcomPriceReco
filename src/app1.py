#llm used:chatgpt
#prompt: this is my app.py. im building a ui to show a price recommendation for a product ive a .pkl file for that. i want to integrate that with this

from app import get_database, get_collection, insert_file_into_collection, delete_collection, create_indexes, backup_before_insert
from preprocessing import preprocessing, fetch_data_from_collection, integrate_ui, index_mongodb_data
import streamlit as st
import pickle
import pandas as pd

# Load the trained model
model_path = "price_model.pkl" S
with open(model_path, "rb") as file:
    model = pickle.load(file)

# Function to create the Streamlit UI for price prediction
def price_prediction_ui():
    st.title("E-Commerce Product Price Recommendation")

    # User inputs for price prediction (Modify based on your model's features)
    main_category = st.selectbox("Main Category", ["Electronics", "Clothing", "Home", "Beauty"])
    sub_category = st.text_input("Sub Category")
    ratings = st.slider("Ratings", min_value=1.0, max_value=5.0, step=0.1)
    no_of_ratings = st.number_input("Number of Ratings", min_value=0, step=1)
    brand = st.text_input("Brand Name")
    description_length = st.number_input("Product Description Length", min_value=1, step=1)

    # Prepare input data for the model
    input_data = pd.DataFrame([{
        "main_category": main_category,
        "sub_category": sub_category,
        "ratings": ratings,
        "no_of_ratings": no_of_ratings,
        "brand": brand,
        "description_length": description_length
    }])

    # Predict Button
    if st.button("Recommend Price"):
        try:
            predicted_price = model.predict(input_data)[0]  # Get the predicted price
            st.success(f"Recommended Price: ${predicted_price:.2f}")
        except Exception as e:
            st.error(f"Error: {str(e)}")

# Modify integrate_ui to include the price prediction UI
def integrate_ui(collection_name):
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Select Page", ["Price Recommendation", "Database Operations"])

    if page == "Price Recommendation":
        price_prediction_ui()
    elif page == "Database Operations":
        st.write("Database operations coming soon...")

if __name__ == "__main__":
    collection_name = "ecomprod"

    # UI Integration with Streamlit
    integrate_ui(collection_name)
