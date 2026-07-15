import { useEffect, useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import client from "../api/client";

export default function Dashboard() {
  const [interns, setInterns] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    load();
  }, []);

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
        {loading ? (
          <p className="text-gray-500">Loading...</p>
        ) : interns.length === 0 ? (
          <p className="text-gray-500">No interns yet. Add one to get started.</p>
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
                {interns.map((intern) => (
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
                    <td className="px-4 py-3 space-y-2">
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
                        className="text-pia-green underline"
                      >
                        Security Letter
                      </button>
                      <button
                        onClick={() => downloadDocument(intern.id, "offer-letter")}
                        className="text-pia-green underline"
                      >
                        Offer Letter
                      </button>
                      <button
                        onClick={() => downloadDocument(intern.id, "certificate")}
                        className="text-pia-green underline"
                      >
                        Certificate
                      </button>
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