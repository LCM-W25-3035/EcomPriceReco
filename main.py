from app import get_database, get_collection,insert_file_into_collection

def fetch_data_from_collection(collection_name):
    """Fetch all documents from the specified collection."""
    try:
        # Get the database connection
        db = get_database()

        # Get the collection
        collection = get_collection(db, collection_name)

        # Fetch all documents
        documents = collection.find()

        print("Documents fetched successfully:")
        for doc in documents:
            print(doc)
    except Exception as e:
        print("Error fetching data:", e)

if __name__ == "__main__":
    # Specify the collection name to fetch data from
    collection_name = "ecomprod"
    file_path = "C://Users//jesel sequeira//Downloads//output_data2.csv"
    insert_file_into_collection(collection_name, file_path)
    # Fetch and display data
    # fetch_data_from_collection(collection_name)

