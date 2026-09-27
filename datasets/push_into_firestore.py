import json
import firebase_admin
from firebase_admin import credentials, firestore
from pathlib import Path

# Get the folder where this Python script is located
BASE_DIR = Path(__file__).resolve().parent

# File paths
SERVICE_ACCOUNT_FILE = BASE_DIR / "serviceAccountKey.json"
DATABASE_FILE = BASE_DIR / "twinmind_warehouse_db.json"

# Initialize Firebase
cred = credentials.Certificate(str(SERVICE_ACCOUNT_FILE))
firebase_admin.initialize_app(cred)

db = firestore.client()

# Load JSON file
with open(DATABASE_FILE, "r", encoding="utf-8") as file:
    data = json.load(file)

# Get the warehouses
warehouses = data["warehouses"]

# Upload each warehouse as a document
for warehouse_id, warehouse_data in warehouses.items():

    db.collection("warehouses").document(warehouse_id).set(
        warehouse_data
    )

    print(f"{warehouse_id} uploaded successfully!")

print("All warehouses uploaded successfully!")