import React, { useEffect, useState } from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";

import WarehouseTwin from "./components/WarehouseTwin";
import Navbar from "./components/Navbar";
import ScenarioSimulation from "./components/ScenarioSimulation";

import { getWarehouse } from "./services/api";

import "./App.css";


function DigitalTwinPage({ warehouse }) {
    return (
        <div className="digital-twin-page">
            <WarehouseTwin warehouse={warehouse} />
        </div>
    );
}


function App() {

    const [warehouse, setWarehouse] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);


    useEffect(() => {

        const loadWarehouse = async () => {

            try {

                console.log("Fetching W001...");

                const data = await getWarehouse("W001");

                console.log("Warehouse data:", data);

                setWarehouse(data);

            } catch (error) {

                console.error(
                    "Failed to load warehouse:",
                    error
                );

                setError(
                    error.message ||
                    "Failed to connect to backend"
                );

            } finally {

                setLoading(false);

            }

        };

        loadWarehouse();

    }, []);


    if (loading) {

        return (
            <div className="loading-screen">
                Loading warehouse...
            </div>
        );

    }


    if (error) {

        return (
            <div className="error-screen">

                <h2>
                    Failed to load warehouse
                </h2>

                <p>{error}</p>

                <p>
                    Make sure FastAPI is running at:
                    <br />
                    http://127.0.0.1:8000
                </p>

            </div>
        );

    }


    return (
        <BrowserRouter>

            <Navbar />

            <Routes>

                <Route
                    path="/"
                    element={
                        <DigitalTwinPage
                            warehouse={warehouse}
                        />
                    }
                />

                <Route
                    path="/simulate"
                    element={
                        <ScenarioSimulation
                            warehouse={warehouse}
                        />
                    }
                />

            </Routes>

        </BrowserRouter>
    );
}


export default App;