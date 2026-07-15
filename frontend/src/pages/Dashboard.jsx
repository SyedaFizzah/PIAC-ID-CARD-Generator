import { useEffect, useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import client from "../api/client";

export default function Dashboard() {
  const [interns, setInterns] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const navigate = useNavigate();

  useEffect(() => {
    load();
  }, []);

  // Client-side filter -- the full intern list is already fetched on load,
  // so there's no need for a server round-trip on every keystroke. Matches
  // against unique ID, name, department, university, and CNIC, so an admin
  // can search by whichever detail they remember first.
  const filteredInterns = interns.filter((intern) => {
    const query = search.trim().toLowerCase();
    if (!query) return true;

    return [
      intern.unique_id,
      intern.name,
      intern.department,
      intern.university,
      intern.discipline,
      intern.cnic,
    ]
      .filter(Boolean)
      .some((field) => field.toLowerCase().includes(query));
  });

  async function load() {
    setLoading(true);
    const res = await client.get("/interns");
    setInterns(res.data);
    setLoading(false);
  }

  async function generateCard(id) {
    await client.post(`/interns/${id}/generate-card`);
    load();
  }

  function downloadBlobPdf(response, defaultName) {
    const url = window.URL.createObjectURL(
      new Blob([response.data], { type: "application/pdf" })
    );

    const disposition = response.headers["content-disposition"];
    let filename = defaultName;

    if (disposition) {
      const match = disposition.match(/filename="(.+)"/);
      if (match) {
        filename = match[1];
      }
    }

    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    a.click();
    window.URL.revokeObjectURL(url);
  }

  function downloadCardPdf(id, uniqueId) {
    client
      .get(`/interns/${id}/card/pdf`, { responseType: "blob" })
      .then((res) => downloadBlobPdf(res, `${uniqueId}.pdf`));
  }

  function downloadDocument(id, documentType) {
    client
      .get(`/interns/${id}/${documentType}/pdf`, { responseType: "blob" })
      .then((res) => {
        const defaultName = `${id}_${documentType}.pdf`;
        downloadBlobPdf(res, defaultName);
      });
  }

  function logout() {
    localStorage.removeItem("pia_admin_token");
    navigate("/login");
  }

  return (
    <div className="min-h-screen bg-pia-cream">
      <header className="bg-pia-green text-white px-8 py-4 flex justify-between items-center">
        <h1 className="font-bold text-lg">PIA Intern System</h1>
        <div className="flex gap-3">
          <Link
            to="/add-intern"
            className="bg-pia-gold text-white px-4 py-2 rounded-lg text-sm font-semibold hover:opacity-90"
          >
            + Add Intern
          </Link>
          <button
            onClick={logout}
            className="bg-white/10 px-4 py-2 rounded-lg text-sm hover:bg-white/20"
          >
            Logout
          </button>
        </div>
      </header>

      <main className="p-8">
        {!loading && interns.length > 0 && (
          <div className="mb-4 flex items-center gap-2">
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search by name, ID, department, university, or CNIC..."
              className="w-full max-w-md rounded-lg border border-gray-300 px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-pia-green"
            />
            {search && (
              <button
                onClick={() => setSearch("")}
                className="text-sm text-gray-500 hover:text-pia-green"
              >
                Clear
              </button>
            )}
            <span className="text-sm text-gray-500 whitespace-nowrap">
              {filteredInterns.length} of {interns.length}
            </span>
          </div>
        )}

        {loading ? (
          <p className="text-gray-500">Loading...</p>
        ) : interns.length === 0 ? (
          <p className="text-gray-500">No interns yet. Add one to get started.</p>
        ) : filteredInterns.length === 0 ? (
          <p className="text-gray-500">No interns match "{search}".</p>
        ) : (
          <div className="bg-white rounded-xl shadow overflow-hidden">
            <table className="w-full text-sm">
              <thead className="bg-pia-tint text-pia-green text-left">
                <tr>
                  <th className="px-4 py-3">Unique ID</th>
                  <th className="px-4 py-3">Name</th>
                  <th className="px-4 py-3">Department</th>
                  <th className="px-4 py-3">Valid Until</th>
                  <th className="px-4 py-3">Actions</th>
                </tr>
              </thead>
              <tbody>
                {filteredInterns.map((intern) => (
                  <tr key={intern.id} className="border-t">
                    <td className="px-4 py-3 font-mono">{intern.unique_id}</td>
                    <td className="px-4 py-3">
                      <Link
                        to={`/interns/${intern.id}`}
                        className="text-pia-green underline font-semibold"
                      >
                        {intern.name}
                      </Link>
                    </td>
                    <td className="px-4 py-3">{intern.department || "—"}</td>
                    <td className="px-4 py-3">{intern.valid_until}</td>
                    <td className="px-4 py-3">
                      <div className="flex flex-col items-start gap-2">
                        {intern.card_front_path ? (
                          <button
                            onClick={() => downloadCardPdf(intern.id, intern.unique_id)}
                            className="text-pia-green underline"
                          >
                            Download Card
                          </button>
                        ) : (
                          <button
                            onClick={() => generateCard(intern.id)}
                            className="bg-pia-green text-white px-3 py-1 rounded-lg text-xs"
                          >
                            Generate Card
                          </button>
                        )}
                        <button
                          onClick={() => downloadDocument(intern.id, "security-letter")}
                          className="bg-pia-green text-white px-3 py-1 rounded-lg text-xs"
                        >
                          Generate Security Letter
                        </button>
                        <button
                          onClick={() => downloadDocument(intern.id, "offer-letter")}
                          className="bg-pia-green text-white px-3 py-1 rounded-lg text-xs"
                        >
                          Generate Offer Letter
                        </button>
                        {/* Certificate template not ready yet -- re-enable once
                            the design is approved. Backend route still works
                            fine if you need to test it directly.
                        <button
                          onClick={() => downloadDocument(intern.id, "certificate")}
                          className="bg-pia-green text-white px-3 py-1 rounded-lg text-xs"
                        >
                          Generate Certificate
                        </button>
                        */}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </main>
    </div>
  );
}