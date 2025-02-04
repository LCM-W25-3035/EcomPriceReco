from pymongo import MongoClient, errors
import csv

def get_database():
    """Establish a connection to the MongoDB database."""
    try:
        # Provide the MongoDB URI here (modify as per your setup)
        mongo_uri = "mongodb+srv://<ecomadmin>:<password>@ecomcluster.tlxtn.mongodb.net/?retryWrites=true&w=majority&appName=EcomCluster"
        client = MongoClient(mongo_uri)

        # Connect to a specific database
        db = client['ecomdb']
        print("Connected to MongoDB successfully.")
        return db
    except Exception as e:
        print("Error connecting to MongoDB:", e)
        raise

# Optionally define additional helper functions here to encapsulate operations

def get_collection(db, collection_name):
    """Fetch a collection from the database."""
    return db[collection_name]

def insert_file_into_collection(collection_name, file_path):
    """Insert the contents of a file into a specified collection."""
    try:
        # Get the database connection
        db = get_database()
        collection = get_collection(db, collection_name)
        with open(file_path,  'r', encoding='utf-8', errors='replace') as file:  # Explicit encoding
            reader = csv.DictReader(file)  # Use DictReader to read rows as dictionaries
            rows = list(reader)  # Convert the reader object to a list of rows
        if rows:
            collection.insert_many(rows)
            print(f"CSV file '{file_path}' inserted successfully into collection '{collection_name}'.")
        else:
            print(f"CSV file '{file_path}' is empty. No data inserted.")
    except Exception as e:
        print("Error inserting CSV file into collection:", e)
