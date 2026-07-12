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

  function downloadCardPdf(id, name) {
    client
      .get(`/interns/${id}/card/pdf`, { responseType: "blob" })
      .then((res) => {
        const url = window.URL.createObjectURL(
          new Blob([res.data], { type: "application/pdf" })
        );
        const a = document.createElement("a");
        a.href = url;
        a.download = `${name}.pdf`;
        a.click();
        window.URL.revokeObjectURL(url);
      });
  }

  function logout() {
    localStorage.removeItem("pia_admin_token");
    navigate("/login");
  }

  return (
    <div className="min-h-screen bg-pia-cream">
      <header className="bg-pia-green text-white px-8 py-4 flex justify-between items-center">
        <h1 className="font-bold text-lg">PIA Intern ID System</h1>
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
                  <th className="px-4 py-3">Added</th>
                  <th className="px-4 py-3">Card</th>
                </tr>
              </thead>
              <tbody>
                {interns.map((intern) => (
                  <tr key={intern.id} className="border-t">
                    <td className="px-4 py-3 font-mono">{intern.unique_id}</td>
                    <td className="px-4 py-3">{intern.name}</td>
                    <td className="px-4 py-3">{intern.department || "—"}</td>
                    <td className="px-4 py-3">{intern.valid_until}</td>
                    <td className="px-4 py-3">
                      {new Date(intern.created_at).toLocaleDateString()}
                    </td>
                    <td className="px-4 py-3">
                      {intern.card_front_path ? (
                        <button
                          onClick={() => downloadCardPdf(intern.id, intern.name)}
                          className="text-pia-green underline"
                        >
                          Download
                        </button>
                      ) : (
                        <button
                          onClick={() => generateCard(intern.id)}
                          className="bg-pia-green text-white px-3 py-1 rounded-lg text-xs"
                        >
                          Generate Card
                        </button>
                      )}
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