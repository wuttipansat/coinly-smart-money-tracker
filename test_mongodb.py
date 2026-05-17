from pymongo import MongoClient

MONGODB_URI = "mongodb+srv://wuttipansat:Kim_Kim123456@cluster0.erz0yfk.mongodb.net/"

client = MongoClient(MONGODB_URI)

db = client["coinly"]
collection = db["transactions"]

result = collection.insert_one({
    "date": "2026-05-16",
    "type": "expense",
    "category": "food",
    "amount": 120,
    "note": "test coffee"
})

print("Inserted ID:", result.inserted_id)

for transaction in collection.find():
    print(transaction)