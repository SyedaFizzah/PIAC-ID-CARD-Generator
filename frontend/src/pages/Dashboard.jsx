import { useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useInterns } from "../hooks/useInterns";
import { filterInterns } from "../utils/filters";
import { downloadCardPdf, downloadDocument } from "../utils/download";
import DashboardHeader from "../components/dashboard/DashboardHeader";
import InternFilters, { EMPTY_FILTERS } from "../components/dashboard/InternFilters";
import InternTable from "../components/dashboard/InternTable";

export default function Dashboard() {
  const { interns, loading, generateCard } = useInterns();
  const [filters, setFilters] = useState(EMPTY_FILTERS);
  const navigate = useNavigate();

  // Client-side filter -- the full intern list is already fetched on load,
  // so there's no need for a server round-trip on every keystroke/filter
  // change. See utils/filters.js for the matching rules.
  const filteredInterns = useMemo(
    () => filterInterns(interns, filters),
    [interns, filters]
  );

  function logout() {
    localStorage.removeItem("pia_admin_token");
    navigate("/login");
  }

  return (
    <div className="min-h-screen bg-pia-cream">
      <DashboardHeader onLogout={logout} />

      <main className="p-8">
        {!loading && interns.length > 0 && (
          <InternFilters
            filters={filters}
            onChange={setFilters}
            resultCount={filteredInterns.length}
            totalCount={interns.length}
          />
        )}

        <InternTable
          loading={loading}
          totalCount={interns.length}
          interns={filteredInterns}
          searchTerm={filters.search}
          onGenerateCard={generateCard}
          onDownloadCard={downloadCardPdf}
          onDownloadDocument={downloadDocument}
        />
      </main>
    </div>
  );
}
