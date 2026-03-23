import React, { useEffect, useRef, useState } from "react";

const SEVERITY_COLOR = {
  low: "#22c55e",
  medium: "#f59e0b",
  high: "#f97316",
  critical: "#ef4444",
};

export default function LiveSimulator({ api, onSelectAlert }) {
  const [events, setEvents] = useState([]);
  const wsRef = useRef(null);
  const listRef = useRef(null);

  useEffect(() => {
    const wsUrl = api
      ? api.replace(/^http/, "ws") + "/ws"
      : `ws://${window.location.host}/ws`;

    function connect() {
      const ws = new WebSocket(wsUrl);
      wsRef.current = ws;

      ws.onmessage = (msg) => {
        try {
          const { type, data } = JSON.parse(msg.data);
          if (type === "alert") {
            setEvents((prev) => {
              const next = [data, ...prev].slice(0, 100);
              return next;
            });
          }
        } catch (_) {}
      };

      ws.onclose = () => {
        // Reconnect after 2 s
        setTimeout(connect, 2000);
      };
    }

    connect();

    // Fallback polling in case WebSocket is blocked
    const poll = setInterval(async () => {
      if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) return;
      try {
        const res = await fetch(`${api}/alerts`);
        const data = await res.json();
        setEvents(data.slice().reverse().slice(0, 100));
      } catch (_) {}
    }, 2000);

    return () => {
      clearInterval(poll);
      if (wsRef.current) wsRef.current.close();
    };
  }, [api]);

  // Auto-scroll to top on new event
  useEffect(() => {
    if (listRef.current) listRef.current.scrollTop = 0;
  }, [events]);

  return (
    <div style={styles.card}>
      <h2 style={styles.title}>⚡ Live Attack Feed</h2>
      <div style={styles.list} ref={listRef}>
        {events.length === 0 && (
          <div style={styles.empty}>No events yet — click ▶ Start Live Attack Demo</div>
        )}
        {events.map((e, i) => (
          <div
            key={e.id || i}
            style={{ ...styles.event, cursor: "pointer" }}
            onClick={() => onSelectAlert && onSelectAlert(e)}
          >
            <div style={styles.eventHeader}>
              <span
                style={{
                  ...styles.badge,
                  background: SEVERITY_COLOR[e.severity] || "#6b7280",
                }}
              >
                {e.severity?.toUpperCase()}
              </span>
              <span style={styles.eventType}>
                ⚠️ {e.type?.replace(/_/g, " ")}
              </span>
              <span style={styles.eventMeta}>
                {e.user} · {e.ip}
              </span>
            </div>
            {e.description && (
              <div style={styles.desc}>{e.description}</div>
            )}
            {e.action_taken && (
              <div style={styles.action}>
                🤖 Auto-action: <strong>{e.action_taken}</strong>{" "}
                <span style={styles.actionStatus}>[{e.action_status}]</span>
              </div>
            )}
            <div style={styles.ts}>
              {new Date(e.timestamp * 1000).toLocaleTimeString()}
            </div>
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
    display: "flex",
    flexDirection: "column",
    minHeight: 400,
  },
  title: {
    margin: "0 0 12px",
    fontSize: 16,
    color: "#ef4444",
    fontWeight: 700,
  },
  list: {
    flex: 1,
    overflowY: "auto",
    maxHeight: 520,
    display: "flex",
    flexDirection: "column",
    gap: 8,
  },
  empty: { color: "#4b5563", fontSize: 13, padding: "20px 0", textAlign: "center" },
  event: {
    background: "#1a1a1a",
    border: "1px solid #2d2d2d",
    borderRadius: 6,
    padding: "10px 12px",
  },
  eventHeader: { display: "flex", alignItems: "center", gap: 8, marginBottom: 4 },
  badge: {
    padding: "2px 8px",
    borderRadius: 4,
    fontSize: 10,
    fontWeight: 700,
    color: "#000",
  },
  eventType: { fontSize: 13, fontWeight: 600, color: "#e0e0e0" },
  eventMeta: { fontSize: 11, color: "#6b7280", marginLeft: "auto" },
  desc: { fontSize: 12, color: "#9ca3af", marginBottom: 4 },
  action: { fontSize: 12, color: "#93c5fd" },
  actionStatus: { color: "#6b7280" },
  ts: { fontSize: 10, color: "#374151", marginTop: 4 },
};
