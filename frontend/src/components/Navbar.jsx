import React from "react";
import { Link, useLocation } from "react-router-dom";
import "./Navbar.css";

function Navbar() {
    const location = useLocation();

    return (
        <aside className="sidebar">

            <div className="sidebar-brand">
                <div className="brand-icon">
                    T
                </div>

                <div>
                    <h2>TwinMind</h2>
                    <span>AI Warehouse</span>
                </div>
            </div>


            <div className="sidebar-menu">

                <div className="menu-title">
                    WORKSPACE
                </div>

                <Link
                    to="/"
                    className={
                        location.pathname === "/"
                            ? "sidebar-link active"
                            : "sidebar-link"
                    }
                >
                    <span className="menu-icon">🏭</span>

                    <span>
                        Digital Twin
                    </span>
                </Link>


                <Link
                    to="/simulate"
                    className={
                        location.pathname === "/simulate"
                            ? "sidebar-link active"
                            : "sidebar-link"
                    }
                >
                    <span className="menu-icon">🔄</span>

                    <span>
                        Simulate Scenario
                    </span>
                </Link>

            </div>


            <div className="sidebar-footer">

                <div className="system-status">
                    <span className="status-dot"></span>

                    <div>
                        <span className="status-title">
                            System Online
                        </span>

                        <span className="status-subtitle">
                            Warehouse W001
                        </span>
                    </div>
                </div>

            </div>

        </aside>
    );
}

export default Navbar;