import { useState } from "react";
import { useNavigate } from "react-router-dom";
import client from "../api/client";

export default function Login() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const navigate = useNavigate();

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    try {
      const res = await client.post("/auth/login", { username, password });
      localStorage.setItem("pia_admin_token", res.data.access_token);
      navigate("/");
    } catch (err) {
      setError("Invalid username or password.");
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-pia-cream">
      <form
        onSubmit={handleSubmit}
        className="bg-white rounded-2xl shadow-lg p-8 w-full max-w-sm border-t-4 border-pia-green"
      >
        <h1 className="text-xl font-bold text-pia-green mb-1">PIA Intern ID System</h1>
        <p className="text-sm text-gray-500 mb-6">Admin sign in</p>

        {error && (
          <div className="mb-4 text-sm text-red-600 bg-red-50 rounded p-2">{error}</div>
        )}

        <label className="block text-sm font-medium text-gray-700 mb-1">Username</label>
        <input
          className="w-full border rounded-lg px-3 py-2 mb-4 focus:outline-none focus:ring-2 focus:ring-pia-green"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          required
        />

        <label className="block text-sm font-medium text-gray-700 mb-1">Password</label>
        <input
          type="password"
          className="w-full border rounded-lg px-3 py-2 mb-6 focus:outline-none focus:ring-2 focus:ring-pia-green"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />

        <button
          type="submit"
          className="w-full bg-pia-green hover:bg-pia-greenDark text-white font-semibold rounded-lg py-2 transition"
        >
          Sign In
        </button>
      </form>
    </div>
  );
}
