import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom"
import Home from "./pages/Home"
import Alerts from "./pages/Alerts"
import Endpoints from "./pages/Endpoints"
import Analytics from "./pages/Analytics"
import BottomNav from "./components/layout/BottomNav"

function App() {
  return (
    <BrowserRouter>
      <div style={{ paddingBottom: "60px" }}>
        <Routes>
          <Route path="/" element={<Navigate to="/home" />} />
          <Route path="/home" element={<Home />} />
          <Route path="/alerts" element={<Alerts />} />
          <Route path="/endpoints" element={<Endpoints />} />
          <Route path="/analytics" element={<Analytics />} />
        </Routes>
      </div>
      <BottomNav />
    </BrowserRouter>
  )
}

export default App