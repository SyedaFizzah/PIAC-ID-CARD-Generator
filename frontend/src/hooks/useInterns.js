import { useCallback, useEffect, useState } from "react";
import client from "../api/client";

// Owns the interns list: fetching, loading state, and the "generate card"
// action (which just re-fetches afterwards so the row picks up the new
// card_front_path). Keeping this out of Dashboard.jsx means the page
// component only has to worry about rendering, not data fetching.
export function useInterns() {
  const [interns, setInterns] = useState([]);
  const [loading, setLoading] = useState(true);

  const load = useCallback(async () => {
    setLoading(true);
    const res = await client.get("/interns");
    setInterns(res.data);
    setLoading(false);
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  const generateCard = useCallback(
    async (id) => {
      await client.post(`/interns/${id}/generate-card`);
      await load();
    },
    [load]
  );

  return { interns, loading, reload: load, generateCard };
}
