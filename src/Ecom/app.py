from pymongo import MongoClient, errors
import csv
import time

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

def get_collection(db, collection_name):
    """Fetch a collection from the database."""
    return db[collection_name]

def delete_collection(db, collection_name):
    try:
        print("Deleting contents before inserting.")
        collection = db[collection_name]
        result = collection.delete_many({})  # Empty filter deletes everything
        if result.deleted_count==0:
            print("No data to delete.")
        else:
            print(f"Deleted {result.deleted_count} documents.")
        print("Deletion completed.\n")
    except Exception as e:
        print("Error deleting from collection:", e)

def backup_before_insert(db, collection_name):
    try:
        print("\nStarting Backup.")
        collection = db[collection_name]
        # Retrieve all existing data from the original collection
        existing_data = list(collection.find())

        backup_date = time.strftime("%Y%m%d")  # Format: YYYYMMDD
        backup_collection_name = "backup_" + backup_date
        backup_collection = get_collection(db, backup_collection_name)
        # Insert the existing data into the backup collection
        if existing_data:
            backup_collection.insert_many(existing_data)
            print(f"Moved {len(existing_data)} documents to the backup collection.")
            print("Backup Completed.\n")
    except Exception as e:
        print(f"Error occurred: {e}")

def create_indexes(db, collection_name):
    try:
        print("Creating Indexes.")
        collection = get_collection(db, collection_name)
        # 1. Compound Indexes : queried t0gether
        collection.create_index([('main_category', 1), ('sub_category', 1)], name="main_category_sub_category_index") 
        collection.create_index([('ratings', -1), ('no_of_ratings', 1)], name="ratings_no_of_ratings_index")  

        # 2. Unique Index : Ensures product names are unique
        collection.create_index([('link', 1)], unique=True, name="unique_product_name_index")  

        # 3. Text Index : support text search functionality
        collection.create_index([('name', 'text')], name="product_name_text_search_index")

        # collection.drop_index('ratings_-1_no_of_ratings_1') 
        print("Indexes created.\n")
    except Exception as e:
        print("Error creating indexes", e)

def insert_file_into_collection(collection_name, file_path):
    """Insert the contents of a file into a specified collection."""
    try:
        # Get the database connection
        db = get_database()
        collection = get_collection(db, collection_name)
        backup_before_insert(db, collection_name)
        delete_collection(db, collection_name)
        create_indexes(db, collection_name)
        print("Inserting data to the collection.")
        with open(file_path,  'r', encoding='utf-8', errors='replace') as file:  # Explicit encoding
            reader = csv.DictReader(file)  # Use DictReader to read rows as dictionaries
            rows = list(reader)  # Convert the reader object to a list of rows
        if rows:
            collection.insert_many(rows)
            print(f"CSV file '{file_path}' inserted successfully into collection '{collection_name}'.")
        else:
            print(f"CSV file '{file_path}' is empty. No data inserted.")
        print("Data Insertion completed.\n")
    except Exception as e:
        print("Error inserting CSV file into collection:", e)
