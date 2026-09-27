from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from firebase import db


app = FastAPI()


# ==============================
# CORS CONFIGURATION
# ==============================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==============================
# HOME
# ==============================

@app.get("/")
def home():

    return {
        "message": "TwinMind AI Backend Running"
    }


# ==============================
# GET WAREHOUSE
# ==============================

@app.get("/warehouse/{warehouse_id}")
def get_warehouse(warehouse_id: str):

    document = (
        db.collection("warehouses")
        .document(warehouse_id)
        .get()
    )

    if not document.exists:

        return {
            "error": "Warehouse not found"
        }

    return document.to_dict()