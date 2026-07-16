import { Link } from "react-router-dom";

export default function DashboardHeader({ onLogout }) {
  return (
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
          onClick={onLogout}
          className="bg-white/10 px-4 py-2 rounded-lg text-sm hover:bg-white/20"
        >
          Logout
        </button>
      </div>
    </header>
  );
}
