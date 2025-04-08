# code source - chatgpt

# prompt1: i want to make a product recommendation system . a user is typing the name like headphones it should show , 
# related products then show the name, also add misspelling too. you can use chatgpt to integrate with the model

# final prompt: what if i want to add filter like things on the side? so it wont force the user to add the brand too. make a ui


import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from rapidfuzz import process, fuzz
import streamlit as st

# Load product names from CSV
df = pd.read_csv('features.csv', usecols=[0])
df.dropna(inplace=True)  # Remove NaN values

product_list = df.iloc[:, 0].astype(str).tolist()  # Convert column to a list

# Convert product names into TF-IDF vectors
vectorizer = TfidfVectorizer(stop_words='english')
tfidf_matrix = vectorizer.fit_transform(product_list)

def suggest_correction(query, product_list):
    """Check if the query is misspelled and suggest the closest match."""
    
    # Normalize product list for case-insensitive comparison
    product_lower = {p.lower(): p for p in product_list}

    # If the exact product name exists in the list, return None (no correction needed)
    if query.lower() in product_lower:
        return None  # No correction needed

    # Find the closest match using fuzzy matching
    matches = process.extract(query, product_list, scorer=fuzz.ratio, limit=5)

    print(f"Fuzzy Matches for '{query}': {matches}")  # Debug print to see the matches

    # Adjust the threshold to trigger suggestions for a higher range of confidence (e.g., 70% - 95%)
    for match in matches:
        if match[1] >= 70:  # Raise confidence threshold
            return match[0]  # Return closest match

    return None  # No correction if confidence is too low

def recommend_products(query, top_n=5):
    """ Recommend products based on query similarity. """
    query_vec = vectorizer.transform([query.lower()])
    similarity = cosine_similarity(query_vec, tfidf_matrix)
    indices = similarity.argsort()[0][-top_n:][::-1]  # Get top matches

    return [product_list[i] for i in indices]

# Streamlit UI
st.title('Product Recommendation System')

# Product Name Input
user_query = st.text_input('Enter a product name:')

# Optional Brand Filter from Sidebar
brand_filter = st.sidebar.selectbox('Select a Brand (optional)', ['Any', 'Sony', 'Bose', 'Apple', 'Samsung', 'JBL'])

if user_query:
    # If the brand filter is selected and is not 'Any', combine brand with the product name
    if brand_filter != 'Any':
        full_query = f"{brand_filter} {user_query}"
    else:
        full_query = user_query

    correction = suggest_correction(full_query, product_list)
    
    if correction and correction.lower() != full_query.lower():
        st.warning(f"Did you mean: **{correction}**?")
        full_query = correction

    # Recommend products based on corrected or original query
    recommended_products = recommend_products(full_query)
    st.subheader("Recommended Products:")
    for product in recommended_products:
        st.write(f"- {product}")
