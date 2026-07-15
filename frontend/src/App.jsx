import { Routes, Route, Navigate } from "react-router-dom";
import Login from "./pages/Login.jsx";
import Dashboard from "./pages/Dashboard.jsx";
import AddIntern from "./pages/AddIntern.jsx";
import InternDetails from "./pages/InternDetails.jsx";
import VerifyIntern from "./pages/VerifyIntern.jsx";


function ProtectedRoute({ children }) {
  const token = localStorage.getItem("pia_admin_token");

  return token ? children : <Navigate to="/login" replace />;
}


export default function App() {
  return (
    <Routes>

      {/* Public */}
      <Route
        path="/login"
        element={<Login />}
      />

      <Route
        path="/verify/:uniqueId"
        element={<VerifyIntern />}
      />


      {/* Admin */}
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


      <Route
        path="/interns/:internId"
        element={
          <ProtectedRoute>
            <InternDetails />
          </ProtectedRoute>
        }
      />


    </Routes>
  );
}

