import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { API_BASE_URL } from "../api/client";

const PIA_GREEN = "#0A5C36";
const PIA_GOLD = "#A6873C";

export default function VerifyIntern() {
  const { uniqueId } = useParams();
  const [intern, setIntern] = useState(null);
  const [status, setStatus] = useState("loading"); // loading | found | not_found | error

  useEffect(() => {
    let cancelled = false;

    async function load() {
      try {
        const res = await fetch(`${API_BASE_URL}/interns/verify/${uniqueId}`);
        if (res.status === 404) {
          if (!cancelled) setStatus("not_found");
          return;
        }
        if (!res.ok) throw new Error("Verification failed");
        const data = await res.json();
        if (!cancelled) {
          setIntern(data);
          setStatus("found");
        }
      } catch {
        if (!cancelled) setStatus("error");
      }
    }

    load();
    return () => {
      cancelled = true;
    };
  }, [uniqueId]);

  const isExpired =
    intern && new Date(intern.valid_until) < new Date(new Date().toDateString());

  return (
    <div className="min-h-screen bg-[#F5F0E6] flex items-center justify-center px-4 py-10">
      <div className="w-full max-w-sm">
        <p className="text-center text-xs tracking-[0.2em] uppercase text-[#A6873C] mb-6">
          PIA Intern Verification
        </p>

        {status === "loading" && (
          <div className="bg-white rounded-2xl border border-[#0A5C36]/15 p-8 text-center text-sm text-gray-500">
            Checking ID {uniqueId}…
          </div>
        )}

        {status === "not_found" && (
          <div className="bg-white rounded-2xl border-2 border-red-400 p-8 text-center">
            <div className="text-red-600 text-lg font-semibold mb-1">Not a valid ID</div>
            <p className="text-sm text-gray-500">
              No intern record matches ID{" "}
              <span className="font-mono">{uniqueId}</span>.
            </p>
          </div>
        )}

        {status === "error" && (
          <div className="bg-white rounded-2xl border border-gray-200 p-8 text-center text-sm text-gray-500">
            Couldn't reach the verification service. Try again in a moment.
          </div>
        )}

        {status === "found" && intern && (
          <div
            className="bg-white rounded-2xl overflow-hidden shadow-sm"
            style={{ border: `2px solid ${isExpired ? "#DC2626" : PIA_GREEN}` }}
          >
            <div
              className="px-5 py-2 text-center text-xs font-semibold tracking-wide uppercase"
              style={{
                backgroundColor: isExpired ? "#FEE2E2" : "#EAF3EE",
                color: isExpired ? "#DC2626" : PIA_GREEN,
              }}
            >
              {isExpired ? "Expired" : "Valid Intern ID"}
            </div>

            <div className="p-6 flex flex-col items-center text-center">
              <img
                src={`${API_BASE_URL}/interns/verify/${uniqueId}/photo`}
                alt={intern.name}
                className="w-24 h-32 object-cover rounded-lg border mb-4"
                style={{ borderColor: PIA_GREEN }}
                onError={(e) => {
                  e.currentTarget.style.display = "none";
                }}
              />

              <h1 className="text-lg font-bold" style={{ color: PIA_GREEN }}>
                {intern.name}
              </h1>
              <p className="text-sm mb-4" style={{ color: PIA_GOLD }}>
                ID No: {intern.unique_id}
              </p>

              <dl className="w-full text-sm text-left space-y-2 border-t border-gray-100 pt-4">
                <Row label="University" value={intern.university} />
                <Row label="Discipline" value={intern.discipline} />
                <Row label="Department" value={intern.department} />
                <Row label="Duration" value={intern.duration_weeks ? `${intern.duration_weeks} weeks` : "—"} />
                <Row
                  label="Valid until"
                  value={new Date(intern.valid_until).toLocaleDateString("en-GB", {
                    day: "2-digit",
                    month: "short",
                    year: "numeric",
                  })}
                />
              </dl>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

function Row({ label, value }) {
  return (
    <div className="flex justify-between gap-3">
      <dt className="text-gray-500">{label}</dt>
      <dd className="font-medium text-gray-900 text-right">{value || "—"}</dd>
    </div>
  );
}