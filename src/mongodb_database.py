from datetime import datetime, timezone

import streamlit as st
from bson import ObjectId
from pymongo import MongoClient, DESCENDING


@st.cache_resource
def get_mongodb_client():
    return MongoClient(st.secrets["MONGODB_URI"])

def get_collection():
    client = get_mongodb_client()

    db_name = st.secrets.get("MONGODB_DB", "coinly")
    collection_name = st.secrets.get("MONGODB_COLLECTION", "transactions")

    return client[db_name][collection_name]

def create_table():
    collection = get_collection()
    
    collection.create_index([("date", DESCENDING)])
    collection.create_index("type")
    collection.create_index("category")

def add_transaction(date, type_, category, amount, note=""):
    collection = get_collection()

    document = {
        "date": str(date),
        "type": str(type_),
        "category": str(category),
        "amount": float(amount),
        "note": str(note),
        "created_at": datetime.now(timezone.utc),
    }

    collection.insert_one(document)


def get_all_transactions():
    collection = get_collection()

    documents = collection.find().sort("date", DESCENDING)

    rows = []

    for doc in documents:
        rows.append(
            (
                str(doc["_id"]),
                doc.get("date", ""),
                doc.get("type", ""),
                doc.get("category", ""),
                float(doc.get("amount", 0)),
                doc.get("note", ""),
            )
        )

    return rows


def update_transaction(transaction_id, date, type_, category, amount, note):
    collection = get_collection()

    collection.update_one(
        {"_id": ObjectId(str(transaction_id))},
        {
            "$set": {
                "date": str(date),
                "type": str(type_),
                "category": str(category),
                "amount": float(amount),
                "note": str(note),
                "updated_at": datetime.now(timezone.utc),
            }
        },
    )


def delete_transaction(transaction_id):
    collection = get_collection()

    collection.delete_one(
        {"_id": ObjectId(str(transaction_id))}
    )


def remove_all_transactions(reset_id: bool = True):
    collection = get_collection()
    collection.delete_many({})