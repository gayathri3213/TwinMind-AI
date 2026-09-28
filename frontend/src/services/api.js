import axios from "axios";

const API = axios.create({
    baseURL: "http://127.0.0.1:8000"
});

export const getWarehouse = async (warehouseId) => {
    const response = await API.get(`/warehouse/${warehouseId}`);
    return response.data;
};

export const simulateScenario = async (productId, query) => {
    const response = await API.post("/scenario/simulate", {
        product_id: productId,
        query: query
    });

    return response.data;
};

export const getScenarioExplanation = async (
    productId,
    query,
    impact,
    direction
) => {
    const response = await API.post("/scenario/explain", {
        product_id: productId,
        query: query,
        impact_percentage: impact,
        direction: direction
    });

    return response.data;
};