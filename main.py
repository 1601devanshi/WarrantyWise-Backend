from fastapi import FastAPI, HTTPException
from pymongo import MongoClient
from pydantic import BaseModel
import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

app = FastAPI()

# Get Mongo URI from environment
MONGO_URI = os.getenv("MONGOURI")

if not MONGO_URI:
    raise Exception("❌ MONGOURI not found in environment variables")

# MongoDB connection
client = MongoClient(MONGO_URI)

# Check connection
try:
    client.admin.command('ping')
    print("✅ MongoDB Connected Successfully")
except Exception as e:
    print("❌ MongoDB Connection Failed:", e)

db = client["warranty_db"]
collection = db["warranties"]


# Model
class Warranty(BaseModel):
    productName: str
    purchaseDate: int
    warrantyMonths: int
    category: str


# ------------------- ROUTES -------------------

# Home route
@app.get("/")
def home():
    return {"message": "Backend running successfully"}


# 🔹 CREATE
@app.post("/add")
def add_warranty(w: Warranty):
    try:
        collection.insert_one(w.dict())
        return {"status": "added"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# 🔹 READ ALL
@app.get("/all")
def get_all():
    try:
        data = list(collection.find({}, {"_id": 0}))
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# 🔹 READ ONE
@app.get("/get/{name}")
def get_warranty(name: str):
    try:
        data = collection.find_one({"productName": name}, {"_id": 0})
        if not data:
            raise HTTPException(status_code=404, detail="Not found")
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# 🔹 UPDATE
@app.put("/update/{name}")
def update_warranty(name: str, w: Warranty):
    try:
        result = collection.update_one(
            {"productName": name},
            {"$set": w.dict()}
        )

        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Not found")

        return {"status": "updated"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# 🔹 DELETE
@app.delete("/delete/{name}")
def delete_warranty(name: str):
    try:
        result = collection.delete_one({"productName": name})

        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Not found")

        return {"status": "deleted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))