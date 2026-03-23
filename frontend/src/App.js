import React, { useEffect, useState, useCallback } from "react";
import LiveSimulator from "./components/LiveSimulator";
import StatsCounter from "./components/StatsCounter";
import AIPanel from "./components/AIPanel";
import ComplianceLog from "./components/ComplianceLog";

const API = "";

export default function App() {
  const [running, setRunning] = useState(false);
  const [selectedAlert, setSelectedAlert] = useState(null);

  const startDemo = useCallback(async () => {
    await fetch(`${API}/simulate/start`, { method: "POST" });
    setRunning(true);
  }, []);

  const stopDemo = useCallback(async () => {
    await fetch(`${API}/simulate/stop`, { method: "POST" });
    setRunning(false);
  }, []);

  const resetDemo = useCallback(async () => {
    await fetch(`${API}/simulate/reset`, { method: "POST" });
    setRunning(false);
    setSelectedAlert(null);
  }, []);

  const runScenario = useCallback(async (name) => {
    await fetch(`${API}/simulate/scenario/${name}`, { method: "POST" });
  }, []);

  // Poll simulator status on mount
  useEffect(() => {
    fetch(`${API}/simulate/status`)
      .then((r) => r.json())
      .then((d) => setRunning(d.running))
      .catch(() => {});
  }, []);

  return (
    <div style={styles.root}>
      {/* Header */}
      <header style={styles.header}>
        <div style={styles.headerLeft}>
          <span style={styles.logo}>🛡️ AI SOC Simulator</span>
          <span style={styles.tagline}>Attack → Detection → AI → Auto-Response → Compliance</span>
        </div>
        <div style={styles.headerRight}>
          {!running ? (
            <button style={{ ...styles.btn, ...styles.btnGreen }} onClick={startDemo}>
              ▶ Start Live Attack Demo
            </button>
          ) : (
            <button style={{ ...styles.btn, ...styles.btnRed }} onClick={stopDemo}>
              ⏹ Stop Demo
            </button>
          )}
          <button style={{ ...styles.btn, ...styles.btnGray }} onClick={resetDemo}>
            ↺ Reset
          </button>
        </div>
      </header>

      {/* Scenario buttons */}
      <div style={styles.scenarioBar}>
        <span style={styles.scenarioLabel}>Run Scenario:</span>
        {["phishing", "credential_stuffing", "impossible_travel", "data_exfiltration"].map((s) => (
          <button
            key={s}
            style={{ ...styles.btn, ...styles.btnScenario }}
            onClick={() => runScenario(s)}
          >
            {s.replace(/_/g, " ")}
          </button>
        ))}
      </div>

      {/* Stats banner */}
      <StatsCounter api={API} />

      {/* Main grid */}
      <div style={styles.grid}>
        <div style={styles.col}>
          <LiveSimulator api={API} onSelectAlert={setSelectedAlert} />
        </div>
        <div style={styles.col}>
          <AIPanel alert={selectedAlert} api={API} />
          <ComplianceLog api={API} />
        </div>
      </div>
    </div>
  );
}

const styles = {
  root: {
    minHeight: "100vh",
    background: "#0a0a0a",
    color: "#e0e0e0",
    fontFamily: "'Segoe UI', sans-serif",
    display: "flex",
    flexDirection: "column",
  },
  header: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    padding: "12px 24px",
    borderBottom: "1px solid #1e1e1e",
    background: "#111",
  },
  headerLeft: { display: "flex", flexDirection: "column" },
  logo: { fontSize: 20, fontWeight: 700, color: "#fff" },
  tagline: { fontSize: 11, color: "#666", marginTop: 2 },
  headerRight: { display: "flex", gap: 8 },
  btn: {
    padding: "8px 16px",
    borderRadius: 6,
    border: "none",
    cursor: "pointer",
    fontSize: 13,
    fontWeight: 600,
  },
  btnGreen: { background: "#22c55e", color: "#000" },
  btnRed: { background: "#ef4444", color: "#fff" },
  btnGray: { background: "#374151", color: "#e0e0e0" },
  scenarioBar: {
    display: "flex",
    alignItems: "center",
    gap: 8,
    padding: "8px 24px",
    background: "#111",
    borderBottom: "1px solid #1e1e1e",
  },
  scenarioLabel: { fontSize: 12, color: "#9ca3af" },
  btnScenario: { background: "#1e293b", color: "#93c5fd", fontSize: 12 },
  grid: {
    display: "grid",
    gridTemplateColumns: "1fr 1fr",
    gap: 16,
    padding: 16,
    flex: 1,
  },
  col: { display: "flex", flexDirection: "column", gap: 16 },
};
