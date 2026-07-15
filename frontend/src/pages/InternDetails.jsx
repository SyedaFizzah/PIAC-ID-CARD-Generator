import { useEffect, useState } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import CreatableSelect from "react-select/creatable";
import client, { API_BASE_URL } from "../api/client";
import { skills as skillOptions } from "../data/skills";

const FIELDS = [
  { key: "name", label: "Name" },
  { key: "gender", label: "Gender" },
  { key: "university", label: "University" },
  { key: "discipline", label: "Discipline" },
  { key: "department", label: "Department" },
  { key: "skills", label: "Skills" },
  { key: "cnic", label: "CNIC" },
  { key: "start_date", label: "Start date", type: "date" },
  { key: "duration_weeks", label: "Duration (weeks)", type: "number" },
  { key: "end_date", label: "Valid until", type: "date" }, // maps onto Intern.valid_until
];

const SKILL_OPTIONS = skillOptions.map((skill) => ({ value: skill, label: skill }));

// "Python, SQL, Leadership" -> [{ value: "Python", label: "Python" }, ...]
const skillsStringToOptions = (value) =>
  (value || "")
    .split(",")
    .map((s) => s.trim())
    .filter(Boolean)
    .map((s) => ({ value: s, label: s }));

// [{ value: "Python" }, ...] -> "Python, SQL, Leadership"
const skillsOptionsToString = (options) =>
  (options || []).map((option) => option.value).join(", ");

export default function InternDetails() {
  const { internId } = useParams();
  const navigate = useNavigate();

  const [intern, setIntern] = useState(null);
  const [form, setForm] = useState(null);
  const [editing, setEditing] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [status, setStatus] = useState("loading"); // loading | ready | error

  // Function *expressions* (const x = () => {}) rather than function
  // *declarations* (function x() {}) -- declarations inside a block get
  // hoisted, and hoisting behaves inconsistently across browsers/tooling,
  // so expressions are the safer default here.
  const toFormValues = (data) => ({
    name: data.name || "",
    gender: data.gender || "",
    university: data.university || "",
    discipline: data.discipline || "",
    department: data.department || "",
    skills: skillsStringToOptions(data.skills),
    cnic: data.cnic || "",
    start_date: data.start_date || "",
    end_date: data.valid_until || "", // "end_date" here is a form-only alias for valid_until
  });

  useEffect(() => {
    let cancelled = false;

    client
      .get(`/interns/${internId}`)
      .then(({ data }) => {
        if (cancelled) return;
        setIntern(data);
        setForm(toFormValues(data));
        setStatus("ready");
      })
      .catch(() => !cancelled && setStatus("error"));

    return () => {
      cancelled = true;
    };
  }, [internId]);

  const originalValue = (key) => (key === "end_date" ? intern.valid_until : intern[key]);

  const handleChange = (key, value) => {
    setForm((prev) => ({ ...prev, [key]: value }));
  };

  const cancelEdit = () => {
    setForm(toFormValues(intern));
    setEditing(false);
    setError("");
  };

  const saveChanges = async () => {
    setSaving(true);
    setError("");

    if (form.end_date <= form.start_date) {
      setError("End date must be after the start date.");
      setSaving(false);
      return;
    }

    const payload = {};
    for (const { key } of FIELDS) {
      const original = originalValue(key) ?? "";
      // Skills lives in form state as an array of react-select options,
      // but the backend just wants the same comma-joined string it sent us.
      const current = key === "skills" ? skillsOptionsToString(form.skills) : form[key];
      if (String(current) !== String(original)) {
        payload[key] = current;
      }
    }

    if (Object.keys(payload).length === 0) {
      setEditing(false);
      setSaving(false);
      return;
    }

    try {
      const { data } = await client.patch(`/interns/${internId}`, payload);
      setIntern(data);
      setForm(toFormValues(data));
      setEditing(false);
    } catch (err) {
      setError(err.response?.data?.detail || "Couldn't save changes.");
    } finally {
      setSaving(false);
    }
  };

  if (status === "loading") {
    return <div className="p-8 text-sm text-gray-500">Loading intern…</div>;
  }

  if (status === "error" || !intern) {
    return (
      <div className="p-8">
        <p className="text-sm text-red-600 mb-2">Couldn't load this intern.</p>
        <div className="flex gap-4">
          <button onClick={() => navigate(-1)} className="text-sm text-[#0A5C36] underline">
            Go back
          </button>
          <Link to="/" className="text-sm text-[#0A5C36] underline">
            Back to dashboard
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto p-6">
      <div className="mb-4">
        <Link to="/" className="text-sm text-[#0A5C36] hover:underline">
          ← Back to dashboard
        </Link>
      </div>

      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-4">
          <img
            src={`${API_BASE_URL}/interns/verify/${intern.unique_id}/photo`}
            alt={intern.name}
            className="w-20 h-20 rounded-full object-cover border-2 border-[#0A5C36]/30 bg-gray-100"
            onError={(e) => {
              e.currentTarget.onerror = null;
              e.currentTarget.style.display = "none";
            }}
          />
          <div>
            <h1 className="text-xl font-bold text-[#0A5C36]">{intern.name}</h1>
            <p className="text-sm text-[#A6873C]">ID No: {intern.unique_id}</p>
          </div>
        </div>

        {!editing ? (
          <button
            onClick={() => setEditing(true)}
            className="px-4 py-2 text-sm rounded-lg bg-[#0A5C36] text-white hover:opacity-90"
          >
            Edit details
          </button>
        ) : (
          <div className="flex gap-2">
            <button
              onClick={cancelEdit}
              disabled={saving}
              className="px-4 py-2 text-sm rounded-lg border border-gray-300 text-gray-600"
            >
              Cancel
            </button>
            <button
              onClick={saveChanges}
              disabled={saving}
              className="px-4 py-2 text-sm rounded-lg bg-[#0A5C36] text-white hover:opacity-90 disabled:opacity-50"
            >
              {saving ? "Saving…" : "Save changes"}
            </button>
          </div>
        )}
      </div>

      {error && (
        <div className="mb-4 px-4 py-2 rounded-lg bg-red-50 text-red-600 text-sm">{error}</div>
      )}

      <dl className="bg-white rounded-xl border border-gray-200 divide-y divide-gray-100">
        {FIELDS.map(({ key, label, type }) => (
          <div key={key} className="flex items-center gap-4 px-5 py-3">
            <dt className="w-40 shrink-0 text-sm text-gray-500">{label}</dt>
            <dd className="flex-1 text-sm">
              {editing ? (
                key === "skills" ? (
                  <CreatableSelect
                    options={SKILL_OPTIONS}
                    value={form.skills}
                    onChange={(selected) => handleChange("skills", selected || [])}
                    placeholder="Select or type skills"
                    isMulti
                    isSearchable
                    closeMenuOnSelect={false}
                    classNamePrefix="react-select"
                  />
                ) : (
                  <input
                    type={type || "text"}
                    value={form[key]}
                    onChange={(e) => handleChange(key, e.target.value)}
                    min={key === "end_date" ? form.start_date : undefined}
                    className="w-full border border-gray-300 rounded-md px-2 py-1 focus:outline-none focus:ring-2 focus:ring-[#0A5C36]/40"
                  />
                )
              ) : key === "skills" ? (
                <div className="flex flex-wrap gap-1">
                  {form.skills.length === 0 ? (
                    <span className="text-gray-900">—</span>
                  ) : (
                    form.skills.map((skill) => (
                      <span
                        key={skill.value}
                        className="px-2 py-0.5 rounded-full bg-[#EAF2EC] text-[#0A5C36] text-xs"
                      >
                        {skill.value}
                      </span>
                    ))
                  )}
                </div>
              ) : (
                <span className="text-gray-900">{originalValue(key) || "—"}</span>
              )}
            </dd>
          </div>
        ))}
      </dl>
    </div>
  );
}