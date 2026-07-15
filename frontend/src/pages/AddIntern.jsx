import { useState } from "react";
import Select from "react-select";
import CreatableSelect from "react-select/creatable";
import { useNavigate, Link } from "react-router-dom";
import client from "../api/client";
import { universities } from "../data/universities";
import { disciplines } from "../data/disciplines";
import { genders } from "../data/genders";
import { departments } from "../data/departments";
import { skills as skillOptions } from "../data/skills";

export default function AddIntern() {
  const [name, setName] = useState("");
  const [university, setUniversity] = useState("");
  const [discipline, setDiscipline] = useState("");
  const [gender, setGender] = useState("");
  const [cnic, setCnic] = useState("");
  const [department, setDepartment] = useState("");
  const [skills, setSkills] = useState([]);
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [photo, setPhoto] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");

  const navigate = useNavigate();

  const universityOptions = universities.map((uni) => ({
    value: uni,
    label: uni,
  }));

  const disciplineOptions = disciplines.map((discipline) => ({
    value: discipline,
    label: discipline,
  }));

  const departmentOptions = departments.map((dept) => ({
    value: dept,
    label: dept,
  }));

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

    if (new Date(endDate) <= new Date(startDate)) {
      setError("End date must be after the start date.");
      setSubmitting(false);
      return;
    }

    try {
      const formData = new FormData();
      formData.append("name", name);
      formData.append("university", university);
      formData.append("discipline", discipline);
      formData.append("department", department);
      formData.append("skills", skills.map((item) => item.value).join(", "));
      formData.append("gender", gender);
      formData.append("cnic", cnic);
      formData.append("start_date", startDate);
      formData.append("end_date", endDate);

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
          required
        />

        <label className="block text-sm font-medium text-gray-700 mb-1">
          University *
        </label>

        <Select
          options={universityOptions}
          value={universityOptions.find(
            (option) => option.value === university
          )}
          onChange={(selected) => setUniversity(selected.value)}
          placeholder="Select University"
          isSearchable
          className="mb-4"
          classNamePrefix="react-select"
        />

        <label className="block text-sm font-medium text-gray-700 mb-1">
          Discipline *
        </label>

        <Select
          options={disciplineOptions}
          value={disciplineOptions.find(
            (option) => option.value === discipline
          )}
          onChange={(selected) => setDiscipline(selected.value)}
          placeholder="Select Discipline"
          isSearchable
          className="mb-4"
          classNamePrefix="react-select"
        />

        <label className="block text-sm font-medium text-gray-700 mb-1">
          Gender *
        </label>

        <select
          className="w-full border rounded-lg px-3 py-2 mb-4"
          value={gender}
          onChange={(e) => setGender(e.target.value)}
          required
        >
          <option value="">Select Gender</option>

          {genders.map((g) => (
            <option key={g} value={g}>
              {g}
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

        <label className="block text-sm font-medium text-gray-700 mb-1">
          Department *
        </label>
        <Select
          options={departmentOptions}
          value={departmentOptions.find(
            (option) => option.value === department
          )}
          onChange={(selected) => setDepartment(selected.value)}
          placeholder="Select Department"
          isSearchable
          className="mb-4"
          classNamePrefix="react-select"
        />

        <label className="block text-sm font-medium text-gray-700 mb-1">
          Skills
        </label>
        <CreatableSelect
          options={skillOptions.map((skill) => ({ value: skill, label: skill }))}
          value={skills}
          onChange={(newValue) => setSkills(newValue || [])}
          placeholder="Select or type skills"
          isMulti
          isSearchable
          closeMenuOnSelect={false}
          className="mb-4"
          classNamePrefix="react-select"
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
              End Date *
            </label>

            <input
              type="date"
              className="w-full border rounded-lg px-3 py-2"
              value={endDate}
              onChange={(e) => setEndDate(e.target.value)}
              min={startDate}
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