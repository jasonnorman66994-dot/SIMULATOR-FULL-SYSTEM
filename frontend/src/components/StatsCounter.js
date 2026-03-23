import React, { useEffect, useState } from "react";

export default function StatsCounter({ api }) {
  const [stats, setStats] = useState({
    attacks_per_min: 0,
    ai_actions: 0,
    threats_blocked: 0,
    compliance_score: 50,
  });

  useEffect(() => {
    const poll = setInterval(async () => {
      try {
        const res = await fetch(`${api}/stats`);
        const data = await res.json();
        setStats(data);
      } catch (_) {}
    }, 2000);
    return () => clearInterval(poll);
  }, [api]);

  const items = [
    { label: "Attacks / min", value: stats.attacks_per_min, icon: "💥", color: "#ef4444" },
    { label: "AI Actions", value: stats.ai_actions, icon: "🤖", color: "#3b82f6" },
    { label: "Threats Blocked", value: stats.threats_blocked, icon: "🛡️", color: "#22c55e" },
    { label: "Compliance Score", value: `${stats.compliance_score}%`, icon: "📋", color: "#f59e0b" },
  ];

  return (
    <div style={styles.bar}>
      {items.map((item) => (
        <div key={item.label} style={styles.card}>
          <span style={styles.icon}>{item.icon}</span>
          <span style={{ ...styles.value, color: item.color }}>{item.value}</span>
          <span style={styles.label}>{item.label}</span>
        </div>
      ))}
    </div>
  );
}

const styles = {
  bar: {
    display: "flex",
    gap: 12,
    padding: "12px 24px",
    background: "#0f0f0f",
    borderBottom: "1px solid #1e1e1e",
  },
  card: {
    flex: 1,
    background: "#111",
    border: "1px solid #1e1e1e",
    borderRadius: 8,
    padding: "10px 16px",
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    gap: 2,
  },
  icon: { fontSize: 20 },
  value: { fontSize: 26, fontWeight: 700 },
  label: { fontSize: 11, color: "#6b7280" },
};
