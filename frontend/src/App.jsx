import { Routes, Route, Navigate } from "react-router-dom";
import Login from "./pages/Login.jsx";
import Dashboard from "./pages/Dashboard.jsx";
import AddIntern from "./pages/AddIntern.jsx";

function ProtectedRoute({ children }) {
  const token = localStorage.getItem("pia_admin_token");
  return token ? children : <Navigate to="/login" replace />;
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <Dashboard />
          </ProtectedRoute>
        }
      />
      <Route
        path="/add-intern"
        element={
          <ProtectedRoute>
            <AddIntern />
          </ProtectedRoute>
        }
      />
    </Routes>
  );
}
