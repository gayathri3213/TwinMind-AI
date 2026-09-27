import React, { useEffect, useState } from "react";

import WarehouseTwin from "./components/WarehouseTwin";

import { getWarehouse } from "./services/api";


function App() {

    const [warehouse, setWarehouse] =
        useState(null);


    const [loading, setLoading] =
        useState(true);


    useEffect(() => {

        loadWarehouse();

    }, []);


    const loadWarehouse = async () => {

        try {

            const data =
                await getWarehouse("W001");

            setWarehouse(data);

        }

        catch (error) {

            console.error(
                "Failed to load warehouse:",
                error
            );

        }

        finally {

            setLoading(false);

        }

    };


    if (loading) {

        return (
            <div>
                Loading TwinMind AI...
            </div>
        );

    }


    return (

        <div className="app">

            <h1>
                TwinMind AI
            </h1>

            <p>
                AI-Driven Warehouse Digital Twin
            </p>


            <WarehouseTwin
                warehouse={warehouse}
            />

        </div>

    );

}


export default App;