import pandas as pd
import re
from app import get_database, get_collection
import streamlit as st
import pandas as pd
from PIL import Image
import requests
from io import BytesIO
from elasticsearch import Elasticsearch

def es_conn():
    # Elastic Cloud connection
    cloud_id = "4ea8fd76720743838f054f0b1c7b82bb:dXMtY2VudHJhbDEuZ2NwLmNsb3VkLmVzLmlvJDJiMWMzMDFhYWU2ODQyMWY5NmFiNDY4ZTQzOTQxN2RiJGE3MDY3MDg1ZGI4MzQwZDJiN2Q0YzBjOTcwMGYwYjFh"
    api_key = "V0VoTWZaVUI2NmlvZUVMd1M5Q2g6Q2ZBNkR4ZzhURk9zb0NUMUlxazduZw=="
    # Connect to Elastic Cloud
    es = Elasticsearch(
        cloud_id=cloud_id,
        api_key=api_key
    )
    index_name="data_ecom"
    return es, index_name

def index_mongodb_data(collection_name):
    index_name="data_ecom"
    es = es_conn()
    collection_mapping = {
    "settings": {
        "analysis": {
            "tokenizer": {
                "edge_ngram_tokenizer": {
                    "type": "edge_ngram",
                    "min_gram": 1,
                    "max_gram": 25,
                    "token_chars": ["letter", "digit"]
                }
            },
            "analyzer": {
                "edge_ngram_analyzer": {
                    "type": "custom",
                    "tokenizer": "edge_ngram_tokenizer"
                }
            }
        }
    },
    "mappings": {
        "properties": {
            "name": {
                "type": "text",
                "analyzer": "edge_ngram_analyzer"
            },
            "main_category": {
                "type": "keyword"
            },
            "sub_category": {
                "type": "keyword"
            },
            "image": {
                "type": "text"
            },
            "link": {
                "type": "keyword"
            },
            "ratings": {
                "type": "float"
            },
            "no_of_ratings": {
                "type": "float"
            },
            "discount_price": {
                "type": "float"
            },
            "actual_price": {
                "type": "float"
            }
        }
    }}
    # Create the index with this mapping
    response = es.indices.create(index=index_name, body=collection_mapping)
    print(response)

    print("Fetching Data from Mongodb.")
    # Get the database connection
    db = get_database()

    # Get the collection
    collection = get_collection(db, collection_name)
    for doc in collection.find().batch_size(2000):
        # Prepare the document for indexing (without the '_id' field inside the document)
        document = {
            "name": doc["name"],
            "main_category": doc["main_category"],
            "sub_category": doc["sub_category"],
            "image": doc["image"],
            "link": doc["link"],
            "ratings": doc["ratings"],
            "no_of_ratings": doc["no_of_ratings"],
            "discount_price": doc["discount_price"],
            "actual_price": doc["actual_price"]
        }
        
        # Use MongoDB _id as the document ID in Elastic, pass it as a parameter, not in the document
        response = es.index(index=index_name, id=str(doc["_id"]), document=document)
        print(f"Indexed document: {response}")
    print("Insert Successful!")    

# Function to get distinct values for a field from Elasticsearch
def get_distinct_values(index, field, es):
    response = es.search(index="data_ecom", body={
    "size": 0,
    "aggs": {
        "unique_categories": {
            "terms": {
                "field": field,  
                "size": 10000
            }
        }
    }})
    unique_values = [bucket["key"] for bucket in response["aggregations"]["unique_categories"]["buckets"]]
    return unique_values

# User search from UI
def search_products(index_name,search_query,sub_category,min_price,max_price,min_rating, es):
    """Search for relevant products based on selected filters."""
    query = {
        "size": 8,  # Limit results to 8
        "query": {
            "bool": {
                "must": []
            }
        }
    }

    # Apply filters dynamically
    # if main_category and main_category != "All":
    #     query["query"]["bool"]["must"].append({"match": {"main_category.keyword": main_category}})
    
    if sub_category != "All":
        query["query"]["bool"]["must"].append({"match": {"sub_category": sub_category}})
    
    if min_price and max_price:
        query["query"]["bool"]["must"].append({"range": {"actual price":{"gte": min_price, "lte": max_price }}})

    if min_rating:
        query["query"]["bool"]["must"].append({"match": {"ratings": min_rating}})
    
    if search_query != "":
        query["query"]["bool"]["must"].append({"match": {"name": {"query": search_query, "fuzziness": "AUTO" }}})
    print(query)
    response = es.search(index=index_name, body=query)
    print(response)
    return response["hits"]["hits"]

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

# Fetch products based on the review range
def fetch_products_by_reviews(collection_name, reviews_range):
    db = get_database()
    collection = db[collection_name]     
    # Query to fetch products with reviews within the specified range
    filtered_products = collection.find({
        "no_of_ratings": {"$gte": reviews_range[0], "$lte": reviews_range[1]}
    })
    
    return list(filtered_products)

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

# Fetch products based on price range
def fetch_products_by_price(collection_name, price_range):
    db = get_database()
    collection = db[collection_name] 
    
    # Query to fetch products within the selected price range
    filtered_products = collection.find({
        "discount_price": {"$gte": price_range[0], "$lte": price_range[1]}
    })
    
    return list(filtered_products)

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
def integrate_old(collection_name):
    st.set_page_config(page_title="PriceReco - Pricing Optimization", page_icon="💰", layout="centered")

    ### Prompt : Make background dark ###
    # Inject custom CSS for dark background
    st.markdown("""
        <style>
            body {
                background-color: #121212;  /* Dark background color */
                color: #ffffff;  /* White text color */
            }
            .stTextInput>div>div>input {
                background-color: #333333;  /* Dark background for text input */
                color: white;  /* White text for input fields */
            }
            .stButton>button {
                background-color: #444444;  /* Dark background for buttons */
                color: white;  /* White text for buttons */
            }
            .stSelectbox, .stRadio>div>div>label {
                color: white;  /* White color for selectbox and radio button labels */
            }
            .stSlider>div>label {
                color: white;  /* White label for sliders */
            }
        </style>
    """, unsafe_allow_html=True)


    # Title and description
    st.title("PriceReco")
    st.subheader("Analyze, Adjust & Optimize your pricing")
    # st.write("Unlock the full potential of your pricing strategy with our insights.")
    # st.write("Browse through the recommended products based on your selection!")

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

def integrate(collection_name):
    st.set_page_config(page_title="PriceReco - Pricing Optimization", page_icon="💰", layout="centered")

    # Title and description
    st.title("PriceReco")

    # Input box for searching by product name directly
    search_query = st.text_input("Search by product name:")

    # Create a column layout for compact filters
    col1, col2, col3 = st.columns([1, 2, 1])  # Adjust column widths as needed

    with col1:
        # Fetch categories dropdown
        categories = fetch_categories(collection_name)
        main_category = st.selectbox("Category", [""] + categories, key="main_category")

    with col2:
        # Fetch sub-categories dropdown only if a main category is selected
        sub_category = None
        if main_category:
            sub_categories = fetch_sub_categories(collection_name, main_category)
            sub_category = st.selectbox("Sub-category", [""] + sub_categories, key="sub_category")

    with col3:
        # Slider for price range filter (optional)
        price_range = st.slider("Price", min_value=0, max_value=5000, value=(0, 1000), step=50, key="price_range")

    # Slider for reviews filter (optional)
    reviews_range = st.slider("Reviews", min_value=0, max_value=10000, value=(0, 500), step=50, key="reviews_range")

    # Add a button to trigger the search manually
    search_button = st.button("Search")

    # Filter products based on the selected category, sub-category, price range, reviews, or search query
    if search_button:  # Display results only when the user clicks 'Search'
        if search_query:  # Search by product name directly
            filtered_products = fetch_products_by_name(collection_name, search_query)
            if filtered_products:  # Check if the list is not empty
                st.subheader(f"Search Results for '{search_query}':")
                for product in filtered_products:
                    st.write(f"**Name**: {product['name']}")
                    st.write(f"**Category**: {product['main_category']} - {product['sub_category']}")
                    st.write(f"**Ratings**: {product['ratings']} ({product['no_of_ratings']} reviews)")
                    st.write(f"**Discounted Price**: ₹{product['discount_price']}")
                    st.write(f"**Original Price**: ₹{product['actual_price']}")
                    st.write(f"[View Product on Amazon]({product['link']})")
            else:
                st.write(f"No products found for '{search_query}'.")

        elif main_category and sub_category:  # Show products based on category and sub-category selection
            filtered_products = fetch_products(collection_name, main_category, sub_category)
            if filtered_products:  # Check if the list is not empty
                st.subheader(f"Products in {main_category} - {sub_category}:")
                for product in filtered_products:
                    st.write(f"**Name**: {product['name']}")
                    st.write(f"**Category**: {product['main_category']} - {product['sub_category']}")
                    st.write(f"**Ratings**: {product['ratings']} ({product['no_of_ratings']} reviews)")
                    st.write(f"**Discounted Price**: ₹{product['discount_price']}")
                    st.write(f"**Original Price**: ₹{product['actual_price']}")
                    st.write(f"[View Product on Amazon]({product['link']})")
            else:
                st.write("No products found for the selected category and sub-category.")

        elif price_range:  # If price range is selected, filter by price
            filtered_products = fetch_products_by_price(collection_name, price_range)
            if filtered_products:  # Check if the list is not empty
                st.subheader(f"Products in the price range ₹{price_range[0]} - ₹{price_range[1]}:")
                for product in filtered_products:
                    st.write(f"**Name**: {product['name']}")
                    st.write(f"**Category**: {product['main_category']} - {product['sub_category']}")
                    st.write(f"**Ratings**: {product['ratings']} ({product['no_of_ratings']} reviews)")
                    st.write(f"**Discounted Price**: ₹{product['discount_price']}")
                    st.write(f"**Original Price**: ₹{product['actual_price']}")
                    st.write(f"[View Product on Amazon]({product['link']})")
            else:
                st.write(f"No products found in the price range ₹{price_range[0]} - ₹{price_range[1]}.")

        elif reviews_range:  # If reviews range is selected, filter by reviews count
            filtered_products = fetch_products_by_reviews(collection_name, reviews_range)
            if filtered_products:  # Check if the list is not empty
                st.subheader(f"Products with {reviews_range[0]} - {reviews_range[1]} reviews:")
                for product in filtered_products:
                    st.write(f"**Name**: {product['name']}")
                    st.write(f"**Category**: {product['main_category']} - {product['sub_category']}")
                    st.write(f"**Ratings**: {product['ratings']} ({product['no_of_ratings']} reviews)")
                    st.write(f"**Discounted Price**: ₹{product['discount_price']}")
                    st.write(f"**Original Price**: ₹{product['actual_price']}")
                    st.write(f"[View Product on Amazon]({product['link']})")
            else:
                st.write(f"No products found with {reviews_range[0]} - {reviews_range[1]} reviews.")

    else:
        st.write("Please enter a product name or apply the filters and press 'Search' to see the results.")

# Week 11
# first promot: referring to the following elastic search POC code make changes to the existing code making connection to ES instread of mongodb.
# last prompt: Inspite of multiple attempts, the UI produts doesnt show up on the same level.
def integrate_ui(collection_name):
    es, index_name=es_conn()
    st.set_page_config(page_title="PriceReco", page_icon="💰", layout="centered")

    # Title and description
    st.title("PriceReco - Pricing Optimization")

    # Input box for searching by product name directly
    search_query = st.text_input("Search by product name:")

    main_categories = get_distinct_values(index_name, "main_category",es)
    sub_categories = get_distinct_values(index_name, "sub_category",es)

    # Filters for refining search
    with st.expander("Filters"):
        # if isinstance(main_categories, list) and main_categories:
        #     main_category = st.selectbox("Main Category", ["All", *main_categories])
        # else:
        #     main_category = st.selectbox("Main Category", ["All"])

        if isinstance(sub_categories, list) and sub_categories:
            sub_category = st.selectbox("Sub Category", ["All", *sub_categories])
        else:
            sub_category = st.selectbox("Sub Category", ["All"])
        min_price, max_price = st.slider("Price Range", 0, 5000, (0, 5000))
        min_rating = st.slider("Minimum Rating", 0.0, 5.0, 0.0, 0.1)
        # min_reviews = st.number_input("Minimum Number of Ratings", min_value=0, step=1)

    # Search trigger
    if st.button("Search") or search_query:
        st.write("Searching for:", search_query)
        products = search_products(index_name, search_query,sub_category,min_price,max_price,min_rating, es)

        if products:
            st.subheader("Search Results:")
            
            # Create a grid with 3 columns
            columns = st.columns(3)
            
            # Iterate over the products and display each in a separate column
            for index, product in enumerate(products):
                product_data = product["_source"]
                
                # Select the column for this product (cycling through columns)
                col = columns[index % 3]
                
                # Only display fields that have a value
                with col:
                    # Display product name if it exists
                    # Display product name if it exists (limit the name length to avoid overflow)
                    if 'name' in product_data:
                        st.markdown(f"**{product_data['name'][:40]}...**", unsafe_allow_html=True)  # Truncate name
                    
                    # Display category information if both categories exist
                    if 'main_category' in product_data and 'sub_category' in product_data:
                        st.write(f"Category: {product_data['main_category']} / {product_data['sub_category']}")
                    
                    # Display pricing details if both prices are available
                    if 'discount_price' in product_data and 'actual_price' in product_data:
                        st.write(f"Price: ₹{product_data['discount_price']} (Original: ₹{product_data['actual_price']})")
                    
                    # Display ratings if both ratings and number of reviews are available
                    if 'ratings' in product_data and 'no_of_ratings' in product_data:
                        st.write(f"Ratings: {product_data['no_of_ratings']} ({product_data['no_of_ratings']} reviews)")
                    
                    # Display the product image if the image URL is available
                    if 'image' in product_data:
                        st.image(product_data['image'], width=150)  # Resize the image to a smaller size
                    
                    # Display the product link if the link is available
                    if 'link' in product_data:
                        st.write(f"[View Product]({product_data['link']})")
                    
                # Add a separator after every row of 3 products (optional)
                if (index + 1) % 3 == 0:  
                    st.markdown("---")
        else:
            st.write("No matching products found.")
        