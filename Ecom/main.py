from app import get_database, get_collection,insert_file_into_collection, delete_collection, create_indexes,backup_before_insert
from preprocessing import preprocessing, fetch_data_from_collection, integrate

if __name__ == "__main__":
    collection_name = "ecomprod"
    # Insert data into collection.
    # raw_file_path = "C://Users//jesel sequeira//Downloads//output_data2.csv"
    # prod_file_path = "C://Users//jesel sequeira//Downloads//Ecom//pre-processed_data0302.csv"
    # insert_file_into_collection(collection_name, raw_file_path)

    # Fetch and display data
    # fetch_data_from_collection(collection_name)

    # Preprocessing
    # preprocessing(collection_name)

    # Create indexes
    # create_indexes(collection_name)

    # UI Integration
    integrate(collection_name)

