import React, { useState } from "react";
import "./WarehouseTwin.css";


function WarehouseTwin({ warehouse }) {

    const [selectedBox, setSelectedBox] = useState(null);


    if (!warehouse) {
        return <div>Loading warehouse...</div>;
    }


    const details = warehouse.warehouse_details;

    const storage = warehouse.Storage || {};

    const products = warehouse.products || {};


    // --------------------------------
    // Create product lookup
    // --------------------------------

    const productLookup = {};


    Object.entries(products).forEach(
        ([productId, product]) => {

            productLookup[productId] = {
                productId,
                name: product.product_details?.name,
                storage: product.storage || {}
            };

        }
    );


    // --------------------------------
    // Find product information
    // for a storage box
    // --------------------------------

    const getBoxProduct = (boxId) => {

        for (
            const [productId, product]
            of Object.entries(productLookup)
        ) {

            const productBox =
                product.storage?.[boxId];

            if (productBox) {

                return {

                    productId,

                    productName:
                        product.name,

                    quantity:
                        productBox.quantity ?? 0

                };

            }

        }

        return null;
    };


    const boxes = Object.entries(storage);


    return (

        <div className="twin-container">

            {/* ========================= */}
            {/* HEADER */}
            {/* ========================= */}

            <div className="twin-header">

                <div>

                    <h2>
                        {details.name}
                    </h2>

                    <p>
                        {details.location}
                    </p>

                </div>


                <div className="status">

                    ● {details.status}

                </div>

            </div>


            {/* ========================= */}
            {/* WAREHOUSE */}
            {/* ========================= */}

            <div className="warehouse-layout">

                {boxes.map(([boxId, box], index) => {
    const product = getBoxProduct(boxId);

    const capacity =
        box.capacity ??
        details.Dimensions?.box_capacity_units ??
        20;

    const quantity =
        product?.quantity ??
        box.quantity ??
        0;

    const fillPercentage = Math.min(
        100,
        Math.max(0, (quantity / capacity) * 100)
    );

    // First row = top 10 boxes
    const isTopRow = index < 10;

    return (
        <div
            key={boxId}
            className={`storage-box ${isTopRow ? "top-row-box" : ""}`}
            onMouseEnter={() => setSelectedBox(boxId)}
            onMouseLeave={() => setSelectedBox(null)}
        >
            <div
                className="box-fill"
                style={{ height: `${fillPercentage}%` }}
            />

            <div className="box-content">
                <div className="box-id">{boxId}</div>

                <div className="box-icon">
                    {quantity > 0 ? "📦" : ""}
                </div>

                <div className="box-quantity">
                    {quantity}/{capacity}
                </div>
            </div>

            {selectedBox === boxId && (
                <div className="box-tooltip">
                    <h3>{boxId}</h3>

                    {product ? (
                        <>
                            <p>
                                <strong>Product ID:</strong>
                                <br />
                                {product.productId}
                            </p>

                            <p>
                                <strong>Product:</strong>
                                <br />
                                {product.productName}
                            </p>

                            <p>
                                <strong>Quantity:</strong>
                                <br />
                                {quantity} units
                            </p>

                            <p>
                                <strong>Capacity:</strong>
                                <br />
                                {capacity} units
                            </p>

                            <p>
                                <strong>Occupancy:</strong>
                                <br />
                                {Math.round(fillPercentage)}%
                            </p>
                        </>
                    ) : (
                        <p>Empty storage box</p>
                    )}
                </div>
            )}
        </div>
    );
})}

            </div>


            {/* ========================= */}
            {/* LEGEND */}
            {/* ========================= */}

            <div className="legend">

                <div>

                    <span className="legend-box">
                    </span>

                    Empty

                </div>


                <div>

                    <span className="legend-box
                        legend-filled">
                    </span>

                    Occupied

                </div>

            </div>

        </div>

    );

}


export default WarehouseTwin;