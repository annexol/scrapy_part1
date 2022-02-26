import pymongo


def insert_db(data, name):
    data = {name: data}
    db_client = pymongo.MongoClient("mongodb://localhost:27017/")
    current_db = db_client["git_test"]
    collection = current_db["git_data"]
    ins_result = collection.insert_one(data)
