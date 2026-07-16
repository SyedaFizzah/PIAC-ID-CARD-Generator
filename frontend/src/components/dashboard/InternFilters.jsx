import { departments } from "../../data/departments";
import { genders } from "../../data/genders";

export const EMPTY_FILTERS = {
  search: "",
  gender: "",
  department: "",
};

const LABEL = "block text-xs font-semibold text-gray-500 uppercase tracking-wide mb-1.5";
const FIELD =
  "w-full rounded-lg border border-gray-300 px-3 py-2 text-sm text-gray-800 " +
  "focus:outline-none focus:ring-2 focus:ring-pia-green focus:border-pia-green";

const hasActiveFilters = (filters) =>
  Object.values(filters).some((value) => value !== "");

// Controlled filter bar. Dashboard owns the `filters` state object and
// passes it down along with a setter; this component just renders inputs
// and patches individual keys via `set`.
export default function InternFilters({ filters, onChange, resultCount, totalCount }) {
  function set(key, value) {
    onChange({ ...filters, [key]: value });
  }

  function reset() {
    onChange(EMPTY_FILTERS);
  }

  return (
    <div className="mb-6 rounded-xl border border-gray-200 bg-white shadow-sm">
      <div className="grid grid-cols-1 gap-4 p-5 sm:grid-cols-3">
        <div>
          <label className={LABEL}>Search</label>
          <input
            type="text"
            value={filters.search}
            onChange={(e) => set("search", e.target.value)}
            placeholder="Name, ID, department, university, CNIC..."
            className={FIELD}
          />
        </div>

        <div>
          <label className={LABEL}>Gender</label>
          <select
            value={filters.gender}
            onChange={(e) => set("gender", e.target.value)}
            className={FIELD}
          >
            <option value="">All</option>
            {genders.map((gender) => (
              <option key={gender} value={gender}>
                {gender}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className={LABEL}>Department</label>
          <select
            value={filters.department}
            onChange={(e) => set("department", e.target.value)}
            className={FIELD}
          >
            <option value="">All</option>
            {departments.map((dept) => (
              <option key={dept} value={dept}>
                {dept}
              </option>
            ))}
          </select>
        </div>
      </div>

      <div className="flex items-center justify-between gap-3 rounded-b-xl border-t border-gray-100 bg-pia-tint/60 px-5 py-3">
        <span className="text-sm text-gray-600">
          Showing <span className="font-semibold text-gray-800">{resultCount}</span> of{" "}
          <span className="font-semibold text-gray-800">{totalCount}</span> interns
        </span>

        <button
          onClick={reset}
          disabled={!hasActiveFilters(filters)}
          className="text-sm font-medium text-pia-green hover:text-pia-greenDark disabled:text-gray-300 disabled:cursor-not-allowed"
        >
          Reset filters
        </button>
      </div>
    </div>
  );
}
