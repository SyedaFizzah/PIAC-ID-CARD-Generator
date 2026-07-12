import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import client from "../api/client";

export default function AddIntern() {
  const [name, setName] = useState("");
  const [department, setDepartment] = useState("");
  const [cnic, setCnic] = useState("");
  const [startDate, setStartDate] = useState("");
  const [durationWeeks, setDurationWeeks] = useState(8);
  const [photo, setPhoto] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");

  const navigate = useNavigate();

  const departments = [
    "Employees Resource Planning",
    "IT",
    "Facilitation Works",
    "Flight Operations",
    "Corporate Safety",
    "Engineering",
    "Passenger Handling Services",
    "Accounts & Finance",
    "Audit",
    "Supply Chain & Logistics",
    "Corporate Planning",
    "Cyber Security",
    "Networking",
    "Human Resource",
    "Marketing",
    "Payroll",
  ];

  async function handleSubmit(e) {
    e.preventDefault();
    setSubmitting(true);
    setError("");

    const cnicDigits = cnic.replace(/\D/g, "");

    if (cnicDigits.length !== 13) {
      setError("CNIC must contain exactly 13 digits.");
      setSubmitting(false);
      return;
    }

    try {
      const formData = new FormData();
      formData.append("name", name);
      formData.append("department", department);
      formData.append("cnic", cnic);
      formData.append("start_date", startDate);
      formData.append("duration_weeks", durationWeeks);

      if (photo) {
        formData.append("photo", photo);
      }

      await client.post("/interns", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });

      navigate("/");
    } catch (err) {
      const detail = err.response?.data?.detail;
      setError(detail || "Could not save intern. Check the backend is running.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="min-h-screen bg-pia-cream p-8">
      <Link to="/" className="text-pia-green text-sm mb-4 inline-block">
        ← Back to dashboard
      </Link>

      <form
        onSubmit={handleSubmit}
        className="bg-white rounded-2xl shadow-lg p-8 max-w-md mx-auto border-t-4 border-pia-gold"
      >
        <h1 className="text-lg font-bold text-pia-green mb-6">
          Add Intern
        </h1>

        {error && (
          <div className="mb-4 text-sm text-red-600 bg-red-50 rounded p-2">
            {error}
          </div>
        )}

        <label className="block text-sm font-medium text-gray-700 mb-1">
          Full Name
        </label>

        <input
          className="w-full border rounded-lg px-3 py-2 mb-4"
          value={name}
          onChange={(e) => {
            const formatted = e.target.value
              .replace(/[^a-zA-Z\s]/g, "") // Only letters and spaces
              .replace(/\s+/g, " ") // Remove extra spaces
              .replace(/^\s/, "") // No leading space
              .toLowerCase()
              .replace(/\b\w/g, (char) => char.toUpperCase());

            setName(formatted);
          }}
          placeholder="e.g. Fizzah Masroor"
          required
        />

        <label className="block text-sm font-medium text-gray-700 mb-1">
          Department *
        </label>
        <select
          className="w-full border rounded-lg px-3 py-2 mb-4"
          value={department}
          onChange={(e) => setDepartment(e.target.value)}
          required
        >
          <option value="">Select Department</option>

          {departments.map((dept) => (
            <option key={dept} value={dept}>
              {dept}
            </option>
          ))}
        </select>

        <label className="block text-sm font-medium text-gray-700 mb-1">
          CNIC *
        </label>
        <input
          inputMode="numeric"
          className={`w-full rounded-lg px-3 py-2 mb-4 border ${error.includes("CNIC")
            ? "border-red-500"
            : "border-gray-300"
            }`}
          value={cnic}
          onChange={(e) => {
            const digits = e.target.value.replace(/\D/g, "").slice(0, 13);

            let formatted = digits;

            if (digits.length > 5) {
              formatted = `${digits.slice(0, 5)}-${digits.slice(5)}`;
            }

            if (digits.length > 12) {
              formatted = `${digits.slice(0, 5)}-${digits.slice(
                5,
                12
              )}-${digits.slice(12)}`;
            }

            setCnic(formatted);

            if (error.includes("CNIC")) {
              setError("");
            }
          }}
          placeholder="XXXXX-XXXXXXX-X"
          required
        />

        <div className="grid grid-cols-2 gap-3 mb-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Start Date *
            </label>
            <input
              type="date"
              className="w-full border rounded-lg px-3 py-2"
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Duration (weeks) *
            </label>
            <input
              type="number"
              min="1"
              className="w-full border rounded-lg px-3 py-2"
              value={durationWeeks}
              onChange={(e) => setDurationWeeks(e.target.value)}
              required
            />
          </div>
        </div>

        <label className="block text-sm font-medium text-gray-700 mb-1">
          Photo *
        </label>
        <input
          type="file"
          accept="image/*"
          className="w-full mb-6"
          onChange={(e) => setPhoto(e.target.files[0])}
          required
        />

        <button
          type="submit"
          disabled={submitting}
          className="w-full bg-pia-green hover:bg-pia-greenDark text-white font-semibold rounded-lg py-2 transition disabled:opacity-50"
        >
          {submitting ? "Saving..." : "Save Intern"}
        </button>
      </form>
    </div>
  );
}