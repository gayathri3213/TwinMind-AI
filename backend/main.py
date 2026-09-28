from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from firebase import db

from pydantic import BaseModel
from gemini_service import predict_scenario, explain_scenario


class ScenarioRequest(BaseModel):
    product_id: str
    query: str


class ExplanationRequest(BaseModel):
    product_id: str
    query: str
    impact_percentage: float
    direction: str

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

@app.post("/scenario/simulate")
def simulate_scenario(request: ScenarioRequest):

    warehouse_document = (
        db.collection("warehouses")
        .document("W001")
        .get()
    )

    if not warehouse_document.exists:
        return {
            "error": "Warehouse not found"
        }

    warehouse = warehouse_document.to_dict()

    products = warehouse.get("products", {})

    product = products.get(request.product_id)

    if not product:
        return {
            "error": "Product not found"
        }

    product_details = product.get(
        "product_details",
        {}
    )

    product_name = product_details.get(
        "name",
        "Unknown Product"
    )

    result = predict_scenario(
        request.product_id,
        product_name,
        request.query
    )

    return {
        "product_id": request.product_id,
        "product_name": product_name,
        "impact_percentage": result["impact_percentage"],
        "direction": result["direction"]
    }

@app.post("/scenario/explain")
def explain_scenario_endpoint(
    request: ExplanationRequest
):

    warehouse_document = (
        db.collection("warehouses")
        .document("W001")
        .get()
    )

    if not warehouse_document.exists:
        return {
            "error": "Warehouse not found"
        }

    warehouse = warehouse_document.to_dict()

    products = warehouse.get("products", {})

    product = products.get(request.product_id)

    if not product:
        return {
            "error": "Product not found"
        }

    product_details = product.get(
        "product_details",
        {}
    )

    product_name = product_details.get(
        "name",
        "Unknown Product"
    )

    explanation = explain_scenario(
        request.product_id,
        product_name,
        request.query,
        request.impact_percentage,
        request.direction
    )

    return {
        "product_id": request.product_id,
        "product_name": product_name,
        "explanation": explanation
    }

