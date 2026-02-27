import { NavLink } from "react-router-dom"

export default function BottomNav() {
  return (
    <div
      style={{
        position: "fixed",
        bottom: 0,
        left: 0,
        right: 0,
        display: "flex",
        borderTop: "1px solid #ddd",
        backgroundColor: "#ffffff",
      }}
    >
      <NavLink
        to="/home"
        style={{ flex: 1, textAlign: "center", padding: "12px" }}
      >
        Home
      </NavLink>

      <NavLink
        to="/alerts"
        style={{ flex: 1, textAlign: "center", padding: "12px" }}
      >
        Alerts
      </NavLink>

      <NavLink
        to="/endpoints"
        style={{ flex: 1, textAlign: "center", padding: "12px" }}
      >
        Endpoints
      </NavLink>

      <NavLink
        to="/analytics"
        style={{ flex: 1, textAlign: "center", padding: "12px" }}
      >
        Analytics
      </NavLink>
    </div>
  )
}