# 🛡️ AI SOC Simulator — Full System

> **Attack → Detection → AI reasoning → Auto-response → Compliance logging**

A fully automated, AI-driven Security Operations Centre (SOC) demo platform. Simulates realistic attacks, feeds them through a detection engine, triggers an AI SOC agent, executes automated response actions, and logs everything to a compliance audit trail — all viewable in a real-time React dashboard.

---

## 🎯 What It Does

Simulates four realistic attack types:

| Attack | Severity | Auto-Response |
|---|---|---|
| Phishing click | High | Revoke session |
| Credential stuffing | Critical | Block IP |
| Impossible travel | High | Flag account |
| Data exfiltration | Critical | Isolate device |

…and feeds them into your SOC as if they're real.

---

## 🧩 Architecture

```
[Attack Simulator]
        ↓
[Ingestion Queue  (in-process or Kafka)]
        ↓
[Detection Engine]
        ↓
[AI SOC Agent  (rule-based + optional OpenAI)]
        ↓
[Response Actions  (SIMULATION_MODE safe)]
        ↓
[Compliance / Audit Logger]
        ↓
[FastAPI Backend  (/alerts · /stats · /ws)]
        ↓
[React Dashboard  (Live feed · Stats · AI panel · Audit log)]
```

---

## 🚀 Quick Start

### Option A — Backend only (no Node.js required)

```bash
pip install -r requirements.txt
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

Then open <http://localhost:8000/docs> for the interactive Swagger UI.

### Option B — Full stack (backend + React UI)

```bash
# Terminal 1 – API server
pip install -r requirements.txt
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2 – React dev server
cd frontend
npm install
npm start          # opens http://localhost:3000
```

### Option C — Docker Compose

```bash
# Standalone (in-process queue, no Kafka)
docker compose up

# With real Kafka
docker compose --profile kafka up
```

---

## 🔌 API Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/alerts` | Latest enriched alerts (limit param) |
| `GET` | `/stats` | Real-time counters + compliance score |
| `GET` | `/compliance/log` | Full audit trail |
| `POST` | `/simulate/start` | Start random attack generator |
| `POST` | `/simulate/stop` | Stop generator |
| `GET` | `/simulate/status` | Is simulator running? |
| `POST` | `/simulate/reset` | Clear all state (demo reset) |
| `POST` | `/simulate/scenario/{name}` | Run named scenario |
| `POST` | `/ai/analyze` | Analyse a custom event payload |
| `WS` | `/ws` | Real-time push (enriched alerts) |

### Available scenarios

- `phishing`
- `credential_stuffing`
- `impossible_travel`
- `data_exfiltration`

```bash
curl -X POST http://localhost:8000/simulate/scenario/phishing
```

---

## 🧪 Running Tests

```bash
python -m pytest tests/ -v
```

60 tests covering the simulator, detection engine, AI agent, response actions, compliance logger, and ingestion queue.

---

## 🧠 AI SOC Agent

The agent analyses every detected threat and returns:

- **Summary** — plain-English explanation
- **Attack Chain** — step-by-step kill chain
- **Risk Assessment** — severity label
- **MITRE ATT&CK** technique reference
- **Recommended Actions** — list of response steps

By default the agent uses a built-in rule-based knowledge base (no external dependencies).  
Set `OPENAI_API_KEY` to upgrade to GPT-4o-mini powered narratives.

---

## 🔒 Safe Mode

All response actions run in **simulation mode** by default — nothing touches real infrastructure:

```python
# config.py
SIMULATION_MODE = True   # set via SIMULATION_MODE=false env var to enable real actions
```

When `SIMULATION_MODE=True`:
- `block_ip` → logs `[SIMULATION] block_ip → <ip>`
- `revoke_session` → logs `[SIMULATION] revoke_session → <user>`
- etc.

---

## 📁 Project Structure

```
├── config.py                    Global configuration + safety switch
├── ingestion/
│   └── producer.py              In-process queue (Kafka-ready)
├── simulator/
│   ├── engine.py                Random attack generator (start/stop/is_running)
│   └── scenarios/
│       ├── phishing.py          4-step phishing chain
│       ├── credential_stuffing.py
│       ├── impossible_travel.py
│       └── data_exfiltration.py
├── detection/
│   └── engine.py                Rule-based detection engine
├── ai_soc/
│   └── agent.py                 Threat narrative + MITRE mapping
├── response/
│   └── actions.py               block_ip / revoke_session / flag_account / isolate_device
├── compliance/
│   └── logger.py                Append-only audit log + compliance score
├── backend/
│   ├── main.py                  FastAPI app + lifespan event processor
│   ├── router.py                All HTTP + WebSocket endpoints
│   └── state.py                 Shared in-process state
├── frontend/
│   ├── src/
│   │   ├── App.js               Main layout + demo controls
│   │   └── components/
│   │       ├── LiveSimulator.js  WebSocket live feed
│   │       ├── StatsCounter.js   Real-time counters
│   │       ├── AIPanel.js        AI SOC agent panel
│   │       └── ComplianceLog.js  Audit log viewer
│   └── package.json
├── tests/                       60 pytest tests
├── docker-compose.yml
└── requirements.txt
```

---

## 🌍 Environment Variables

| Variable | Default | Description |
|---|---|---|
| `SIMULATION_MODE` | `true` | `false` enables real infra actions |
| `KAFKA_BOOTSTRAP_SERVERS` | `` | Leave empty for in-process queue |
| `KAFKA_TOPIC` | `soc-events` | Kafka topic name |
| `OPENAI_API_KEY` | `` | Enables GPT-powered narratives |
| `SIMULATOR_INTERVAL_SECONDS` | `3` | Seconds between generated attacks |
| `SCENARIO_STEP_DELAY_SECONDS` | `2` | Seconds between scenario steps |