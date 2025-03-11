# searchly unsuccessful
from elasticsearch import Elasticsearch

# Connect to Searchly using the correct API Key for authentication
es = Elasticsearch(
    ['https://oin-us-east-1.searchly.com'],  # The Searchly cluster URL (without the API key in the URL)
    headers={'Authorization': 'Bearer db505810f0ae790d75bca80ef6491fa9'}  # API key as Bearer token in the header
)

# Test the connection by fetching the health of the cluster
print("Im in!")
response = es.cluster.health()
print(response)

# Making Mongodb connection
def get_database():
    """Establish a connection to the MongoDB database."""
    try:
        # Provide the MongoDB URI here (modify as per your setup)
        mongo_uri = "mongodb+srv://ecomadmin:Admin123@ecomcluster.tlxtn.mongodb.net/?retryWrites=true&w=majority&appName=EcomCluster"
        client = MongoClient(mongo_uri)

        # Connect to a specific database
        db = client['ecomdb']
        print("Connected to MongoDB successfully.")
        collection = db[collection_name]
        return collection
    except Exception as e:
        print("Error connecting to MongoDB:", e)
        raise

# Creating indexes with Mappings: ensures fields are optimized for searching.
def create_elasticsearch_indexes():
    # Define the index name
    # collection= get_database(collection_name)
    index_name = "product_index"
    # Define index settings and mappings
    index_body = {
        "settings": {
            "number_of_shards": 1,
            "number_of_replicas": 0
        },
        "mappings": {
            "properties": {
                "ASIN": {"type": "keyword"},  # Use 'keyword' for exact match
                "Title": {"type": "text"},    # Use 'text' for full-text search
                "Brand": {"type": "text"},    # Use 'text' for full-text search
                "Discounted Price": {"type": "float"},
                "Actual Price": {"type": "float"},
                "Stock Status": {"type": "keyword"},  # Use 'keyword' for exact match
                "Rating": {"type": "float"},
                "Review Count": {"type": "integer"},
                "URL": {"type": "keyword"},  # Use 'keyword' for exact match
                "category": {"type": "keyword"}  # Use 'keyword' for exact match
            }
        }
    }

    # Create the index in Elasticsearch
    response = es.indices.create(index=index_name, body=index_body, ignore=400)
    print(response)  # Print response to confirm index creation

# collection_name = "databs"

# create_elasticsearch_indexes()