import axios from "axios";

const API = axios.create({
    baseURL: "http://127.0.0.1:8000"
});


export const getWarehouse = async (warehouseId) => {

    const response = await API.get(
        `/warehouse/${warehouseId}`
    );

    return response.data;
};


export const startSimulation = async () => {

    const response = await API.post(
        "/simulation/start"
    );

    return response.data;
};