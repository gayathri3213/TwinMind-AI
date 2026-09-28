import React, { useState } from "react";
import {
    simulateScenario,
    getScenarioExplanation
} from "../services/api";

import "./ScenarioSimulation.css";

function ScenarioSimulation({ warehouse }) {

    const [selectedProduct, setSelectedProduct] = useState("");
    const [query, setQuery] = useState("");

    const [result, setResult] = useState(null);

    const [explanation, setExplanation] = useState("");

    const [loading, setLoading] = useState(false);
    const [explaining, setExplaining] = useState(false);

    const [error, setError] = useState("");


    if (!warehouse) {
        return (
            <div className="scenario-loading">
                Loading products...
            </div>
        );
    }


    const products = warehouse.products || {};


    const handleRunSimulation = async () => {

        if (!selectedProduct || !query.trim()) {
            return;
        }

        setLoading(true);
        setError("");
        setResult(null);
        setExplanation("");

        try {

            const data = await simulateScenario(
                selectedProduct,
                query
            );

            setResult(data);

        } catch (err) {

            console.error(
                "Scenario simulation failed:",
                err
            );

            setError(
                "Unable to run the scenario. Please try again."
            );

        } finally {

            setLoading(false);

        }
    };


    const handleExplanation = async () => {

        if (!result) {
            return;
        }

        setExplaining(true);
        setError("");

        try {

            const data = await getScenarioExplanation(
                selectedProduct,
                query,
                result.impact_percentage,
                result.direction
            );

            setExplanation(data.explanation);

        } catch (err) {

            console.error(
                "Explanation failed:",
                err
            );

            setError(
                "Unable to generate explanation."
            );

        } finally {

            setExplaining(false);

        }
    };


    return (

        <div className="scenario-page">

            <div className="scenario-header">

                <h1>
                    Simulate Scenario
                </h1>

                <p>
                    Analyze how a real-world scenario may affect
                    the supply of a selected product.
                </p>

            </div>


            <div className="scenario-card">


                {/* PRODUCT */}

                <div className="form-group">

                    <label>
                        Select Product
                    </label>

                    <select
                        value={selectedProduct}
                        onChange={(e) => {
                            setSelectedProduct(e.target.value);
                            setResult(null);
                            setExplanation("");
                        }}
                    >

                        <option value="">
                            Select a product
                        </option>

                        {Object.entries(products)
                        .sort(([idA], [idB]) =>
                            idA.localeCompare(idB, undefined, {
                                numeric: true,
                                sensitivity: "base"
                            })
                        )
                        .map(([productId, product]) => (

                                <option
                                    key={productId}
                                    value={productId}
                                >
                                    {productId} -{" "}
                                    {product.product_details?.name}
                                </option>

                            )
                        )}

                    </select>

                </div>


                {/* QUERY */}

                <div className="form-group">

                    <label>
                        Scenario Query
                    </label>

                    <textarea
                        value={query}
                        onChange={(e) => {
                            setQuery(e.target.value);
                            setResult(null);
                            setExplanation("");
                        }}
                        placeholder="Example: How will high tax on exports on chips affect laptop supply?"
                        rows="6"
                    />

                    <div className="query-hint">
                        Describe an external event or scenario that
                        could affect the supply of this product.
                    </div>

                </div>


                {/* BUTTON */}

                <button
                    className="simulate-button"
                    onClick={handleRunSimulation}
                    disabled={
                        !selectedProduct ||
                        !query.trim() ||
                        loading
                    }
                >

                    {loading
                        ? "Analyzing Scenario..."
                        : "▶ Predict Impact"
                    }

                </button>


                {/* ERROR */}

                {error && (
                    <div className="scenario-error">
                        {error}
                    </div>
                )}


                {/* RESULT */}

                {result && (

                    <div className="scenario-result">

                        <div className="result-header">

                            <h2>
                                Scenario Impact
                            </h2>

                            <span>
                                {selectedProduct}
                            </span>

                        </div>


                        <div className="impact-container">


                            <div className="impact-value">

                                <div className="impact-number">
                                    {result.impact_percentage}%
                                </div>

                                <div className="impact-label">
                                    Estimated Impact
                                </div>

                            </div>


                            <div
                                className={`direction-indicator ${
                                    result.direction?.toLowerCase()
                                }`}
                            >

                                <div className="direction-arrow">

                                    {result.direction === "upward"
                                        ? "↑"
                                        : "↓"
                                    }

                                </div>

                                <div className="direction-text">

                                    {result.direction}

                                </div>

                                <div className="direction-description">

                                    {result.direction === "upward"
                                        ? "Supply is expected to increase"
                                        : "Supply is expected to decrease"
                                    }

                                </div>

                            </div>

                        </div>


                        {/* EXPLANATION */}

                        <div className="explanation-section">

                            <button
                                className="explanation-button"
                                onClick={handleExplanation}
                                disabled={explaining}
                            >

                                {explaining
                                    ? "Generating Explanation..."
                                    : "💡 Explain"
                                }

                            </button>


                            {explanation && (
                                <div className="explanation-box">
                                    <div className="explanation-title">
                                        AI Explanation
                                    </div>

                                    <p className="explanation-text">
                                        {explanation}
                                    </p>
                                </div>
                            )}

                        </div>

                    </div>

                )}

            </div>

        </div>
    );
}

export default ScenarioSimulation;