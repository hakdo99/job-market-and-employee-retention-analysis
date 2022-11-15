#*************************************
# Created by: Kukpyo (Andrew) Han  - kha107@sfu.ca
# Created on: April 1, 2022
# Last Updated on: April 1, 2022
# Objective: This python code is intended to provide a common connector method for MongoDB collections
#             set up for CMPT 733 final final project.
#*************************************

## pip install pymongo dnspython

from pymongo import MongoClient

def connect_to_collection(collection_name):
    # URL to the cluster is to be obtained from MongoDB Altas
    # when mongodb is installed on the local machine, "+srv" is not required.
    cluster = "mongodb+srv://admin:QEH3uMoNdXTXD5mA@cmpt733-final-project.ikzc6.mongodb.net" \
              "/EmployeeRetentionDB?retryWrites=true&w=majority"
    client = MongoClient(cluster)
    # This command will create a database. (If it already exists, this will access the existing database.)
    db = client["EmployeeRetentionDB"]
    # Following commands will create a collection. (If it already exists, this will access the existing collection.)
    doc = db[collection_name]

    return doc



