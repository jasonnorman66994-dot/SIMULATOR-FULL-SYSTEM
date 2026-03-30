import React, { useState } from "react";

export default function AIPanel({ alert, api }) {
  const [loading, setLoading] = useState(false);
  const [analysis, setAnalysis] = useState(null);

  const analyze = async () => {
    if (!alert) return;
    setLoading(true);
    try {
      const res = await fetch(`${api}/ai/analyze`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ event: alert }),
      });
      const data = await res.json();
      setAnalysis(data.analysis);
    } catch (_) {
    setAnalysis({ summary: "Error contacting AI agent." });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={styles.card}>
      <div style={styles.header}>
        <h2 style={styles.title}>🧠 AI SOC Agent</h2>
        <button
          style={{ ...styles.btn, opacity: alert ? 1 : 0.4 }}
          onClick={analyze}
          disabled={!alert || loading}
        >
          {loading ? "Analyzing…" : "Ask AI: What's happening?"}
        </button>
      </div>

      {!alert && (
        <div style={styles.hint}>Click an alert in the feed to analyse it.</div>
      )}

      {alert && !analysis && !loading && (
        <div style={styles.hint}>
          Selected: <strong style={{ color: "#e0e0e0" }}>{alert.type?.replace(/_/g, " ")}</strong>{" "}
          — press the button to get AI analysis.
        </div>
      )}

      {analysis && (
        <div style={styles.body}>
          <Row label="Summary" value={analysis.summary} />
          <Row label="Attack Chain" value={analysis.attack_chain} />
          <Row label="Risk" value={analysis.risk} highlight />
          <Row label="MITRE ATT&CK" value={analysis.mitre_technique} />
          {analysis.recommended_actions?.length > 0 && (
            <div style={styles.row}>
              <span style={styles.rowLabel}>Recommended Actions</span>
              <div style={styles.actions}>
                {analysis.recommended_actions.map((a) => (
                  <span key={a} style={styles.actionBadge}>
                    {a.replace(/_/g, " ")}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

function Row({ label, value, highlight }) {
  if (!value) return null;
  return (
    <div style={{ marginBottom: 8 }}>
      <div style={{ fontSize: 10, color: "#6b7280", textTransform: "uppercase", marginBottom: 2 }}>
        {label}
      </div>
      <div style={{ fontSize: 13, color: highlight ? "#ef4444" : "#d1d5db" }}>{value}</div>
    </div>
  );
}

const styles = {
  card: {
    background: "#111",
    border: "1px solid #1e293b",
    borderRadius: 8,
    padding: 16,
  },
  header: { display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 12 },
  title: { margin: 0, fontSize: 16, color: "#3b82f6", fontWeight: 700 },
  btn: {
    background: "#1e40af",
    color: "#fff",
    border: "none",
    borderRadius: 6,
    padding: "7px 14px",
    cursor: "pointer",
    fontSize: 12,
    fontWeight: 600,
  },
  hint: { fontSize: 12, color: "#4b5563", textAlign: "center", padding: "16px 0" },
  body: { display: "flex", flexDirection: "column", gap: 4 },
  row: { marginBottom: 8 },
  rowLabel: { fontSize: 10, color: "#6b7280", textTransform: "uppercase" },
  actions: { display: "flex", flexWrap: "wrap", gap: 6, marginTop: 4 },
  actionBadge: {
    background: "#1e293b",
    color: "#93c5fd",
    padding: "3px 10px",
    borderRadius: 4,
    fontSize: 12,
  },
};
