import { Link } from "react-router-dom";
import InternRowActions from "./InternRowActions";

export default function InternTable({
  loading,
  totalCount,
  interns,
  searchTerm,
  onGenerateCard,
  onDownloadCard,
  onDownloadDocument,
}) {
  if (loading) {
    return <p className="text-gray-500">Loading...</p>;
  }

  if (totalCount === 0) {
    return <p className="text-gray-500">No interns yet. Add one to get started.</p>;
  }

  if (interns.length === 0) {
    return <p className="text-gray-500">No interns match "{searchTerm}".</p>;
  }

  return (
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
              <td className="px-4 py-3">
                <InternRowActions
                  intern={intern}
                  onGenerateCard={onGenerateCard}
                  onDownloadCard={onDownloadCard}
                  onDownloadDocument={onDownloadDocument}
                />
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
