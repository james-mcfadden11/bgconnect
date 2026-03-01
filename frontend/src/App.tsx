import { useEffect, useState } from "react";

type Status = "checking" | "ok" | "error";

function StatusRow({ label, status }: { label: string; status: Status }) {
  const indicator = status === "checking" ? "..." : status === "ok" ? "OK" : "FAIL";
  return (
    <p>
      {label}: <strong>{indicator}</strong>
    </p>
  );
}

export default function App() {
  const [backend, setBackend] = useState<Status>("checking");
  const [nightscout, setNightscout] = useState<Status>("checking");

  useEffect(() => {
    fetch("/health")
      .then((r) => (r.ok ? setBackend("ok") : setBackend("error")))
      .catch(() => setBackend("error"));

    fetch("/health/nightscout")
      .then((r) => (r.ok ? setNightscout("ok") : setNightscout("error")))
      .catch(() => setNightscout("error"));
  }, []);

  return (
    <div style={{ fontFamily: "monospace", padding: "2rem" }}>
      <h1>BGConnect</h1>
      <StatusRow label="Backend" status={backend} />
      <StatusRow label="Nightscout" status={nightscout} />
    </div>
  );
}
