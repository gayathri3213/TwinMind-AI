import React, { useState } from "react";
import {
    simulateScenario,
    getScenarioExplanation
} from "../services/api";

import "./ScenarioSimulation.css";

function ScenarioSimulation({ warehouse }) {

    const [selectedProduct, setSelectedProduct] = useState("");
    const [scenarioType, setScenarioType] = useState("");
    const [severity, setSeverity] = useState("");

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


    // Predefined scenario options
    const scenarioOptions = [
        {
            value: "demand_increase",
            label: "Demand Increase"
        },
        {
            value: "supplier_delay",
            label: "Supplier Delay"
        },
        {
            value: "logistics_disruption",
            label: "Logistics Disruption"
        },
        {
            value: "commodity_price_shock",
            label: "Commodity Price Shock"
        },
        {
            value: "geopolitical_trade_disruption",
            label: "Geopolitical / Trade Disruption"
        }
    ];


    const severityOptions = [
        {
            value: "low",
            label: "Low"
        },
        {
            value: "medium",
            label: "Medium"
        },
        {
            value: "high",
            label: "High"
        }
    ];


    const selectedProductName =
        products[selectedProduct]?.product_details?.name ||
        selectedProduct;


    const selectedScenarioLabel =
        scenarioOptions.find(
            (scenario) => scenario.value === scenarioType
        )?.label || "";


    /*
     * Convert the user's selections into a scenario query
     * that can still be sent to the existing backend API.
     */
    const buildScenarioQuery = () => {

        return `${selectedScenarioLabel} with ${severity} severity for ${selectedProductName}.`;
    };


    const handleRunSimulation = async () => {

        if (
            !selectedProduct ||
            !scenarioType ||
            !severity
        ) {
            return;
        }

        setLoading(true);
        setError("");
        setResult(null);
        setExplanation("");

        try {

            const scenarioQuery = buildScenarioQuery();

            const data = await simulateScenario(
                selectedProduct,
                scenarioQuery
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

            const scenarioQuery = buildScenarioQuery();

            const data = await getScenarioExplanation(
                selectedProduct,
                scenarioQuery,
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
                    TwinMind AI — Scenario Simulation
                </h1>

                <p>
                    Select a product and choose a scenario to
                    evaluate its potential supply-chain impact.
                </p>

            </div>


            <div className="scenario-card">


                {/* PRODUCT */}

                <div className="form-group">

                    <label>
                        Product
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
                                idA.localeCompare(
                                    idB,
                                    undefined,
                                    {
                                        numeric: true,
                                        sensitivity: "base"
                                    }
                                )
                            )
                            .map(
                                ([productId, product]) => (

                                    <option
                                        key={productId}
                                        value={productId}
                                    >
                                        {productId} - {product.product_details?.name || "Unnamed Product"}
                                    </option>

                                )
                            )}

                    </select>

                </div>


                {/* SCENARIO TYPE */}

                <div className="form-group">

                    <label>
                        Scenario type
                    </label>

                    <div className="scenario-options">

                        {scenarioOptions.map((scenario) => (

                            <button
                                key={scenario.value}
                                type="button"
                                className={`scenario-option ${
                                    scenarioType === scenario.value
                                        ? "selected"
                                        : ""
                                }`}
                                onClick={() => {
                                    setScenarioType(
                                        scenario.value
                                    );
                                    setResult(null);
                                    setExplanation("");
                                }}
                            >

                                <span className="scenario-icon">
                                    {scenario.value ===
                                        "demand_increase" && "↗"}

                                    {scenario.value ===
                                        "supplier_delay" && "⏱"}

                                    {scenario.value ===
                                        "logistics_disruption" && "⇄"}

                                    {scenario.value ===
                                        "commodity_price_shock" && "◈"}

                                    {scenario.value ===
                                        "geopolitical_trade_disruption" && "◎"}
                                </span>

                                <span>
                                    {scenario.label}
                                </span>

                            </button>

                        ))}

                    </div>

                </div>


                {/* SCENARIO SEVERITY */}

                <div className="form-group">

                    <label>
                        Scenario severity
                    </label>

                    <div className="severity-options">

                        {severityOptions.map((option) => (

                            <button
                                key={option.value}
                                type="button"
                                className={`severity-option ${
                                    severity === option.value
                                        ? "selected"
                                        : ""
                                }`}
                                onClick={() => {
                                    setSeverity(
                                        option.value
                                    );
                                    setResult(null);
                                    setExplanation("");
                                }}
                            >

                                {option.label}

                            </button>

                        ))}

                    </div>

                </div>


                {/* RUN SIMULATION */}

                <button
                    className="simulate-button"
                    onClick={handleRunSimulation}
                    disabled={
                        !selectedProduct ||
                        !scenarioType ||
                        !severity ||
                        loading
                    }
                >

                    {loading
                        ? "Analyzing Scenario..."
                        : "▶ Predict Impact"}

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
                                {selectedProductName}
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
``