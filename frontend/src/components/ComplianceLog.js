import React, { useEffect, useState } from "react";

export default function ComplianceLog({ api }) {
  const [log, setLog] = useState([]);

  useEffect(() => {
    const poll = setInterval(async () => {
      try {
        const res = await fetch(`${api}/compliance/log`);
        const data = await res.json();
        setLog(data.slice().reverse().slice(0, 30));
      } catch (_) {}
    }, 3000);
    return () => clearInterval(poll);
  }, [api]);

  return (
    <div style={styles.card}>
      <h2 style={styles.title}>📋 Compliance / Audit Log</h2>
      <div style={styles.list}>
        {log.length === 0 && (
          <div style={styles.empty}>No actions logged yet.</div>
        )}
        {log.map((entry, i) => (
          <div key={i} style={styles.entry}>
            <span style={styles.action}>{entry.action?.replace(/_/g, " ")}</span>
            <span style={styles.target}>{entry.details?.target}</span>
            <span style={styles.ts}>
              {new Date(entry.timestamp * 1000).toLocaleTimeString()}
            </span>
            {entry.details?.simulated && (
              <span style={styles.simTag}>SIMULATED</span>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

const styles = {
  card: {
    background: "#111",
    border: "1px solid #1e1e1e",
    borderRadius: 8,
    padding: 16,
  },
  title: { margin: "0 0 10px", fontSize: 16, color: "#f59e0b", fontWeight: 700 },
  list: { maxHeight: 220, overflowY: "auto", display: "flex", flexDirection: "column", gap: 4 },
  empty: { fontSize: 12, color: "#4b5563", textAlign: "center", padding: "12px 0" },
  entry: {
    display: "flex",
    alignItems: "center",
    gap: 8,
    padding: "6px 10px",
    background: "#1a1a1a",
    borderRadius: 4,
    fontSize: 12,
  },
  action: { color: "#93c5fd", fontWeight: 600, flex: "0 0 auto" },
  target: { color: "#d1d5db", flex: 1 },
  ts: { color: "#4b5563", flex: "0 0 auto" },
  simTag: {
    background: "#374151",
    color: "#9ca3af",
    padding: "1px 6px",
    borderRadius: 3,
    fontSize: 10,
  },
};
