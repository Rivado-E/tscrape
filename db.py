from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from tscrape import run as scrape

with open('.mongodb_connection', 'r') as file:
    connection_string = file.read().strip()

uri = connection_string

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
    db = client.spring24
    res = scrape()
    if "courses" not in db.list_collection_names():
        db.create_collection("courses")

    courses_collection = db.courses
    courses_collection.insert_many(dict(res["courses"]))

except Exception as e:
    print(e)
