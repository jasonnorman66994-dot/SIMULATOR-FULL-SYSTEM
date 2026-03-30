"""
Global configuration for the SIMULATOR-FULL-SYSTEM.

Set SIMULATION_MODE = True (default) to run in safe demo mode where no real
infrastructure actions are executed.  Flip to False only in a controlled
production environment.
"""

import os

# ---------------------------------------------------------------------------
# Safety switch – NEVER set False unless you intend real infrastructure calls
# ---------------------------------------------------------------------------
SIMULATION_MODE: bool = os.getenv("SIMULATION_MODE", "true").lower() != "false"

# ---------------------------------------------------------------------------
# Event pipeline
# ---------------------------------------------------------------------------
# Set KAFKA_BOOTSTRAP_SERVERS to use a real Kafka cluster.
# When empty the system falls back to an in-process queue.
KAFKA_BOOTSTRAP_SERVERS: str = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "")
KAFKA_TOPIC: str = os.getenv("KAFKA_TOPIC", "soc-events")

# ---------------------------------------------------------------------------
# AI SOC Agent
# ---------------------------------------------------------------------------
# Optionally provide an OpenAI key to enable GPT-powered threat narratives.
# Leave blank to use the built-in rule-based analyser.
OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")

# ---------------------------------------------------------------------------
# Simulator timing
# ---------------------------------------------------------------------------
SIMULATOR_INTERVAL_SECONDS: float = float(
    os.getenv("SIMULATOR_INTERVAL_SECONDS", "3")
)
SCENARIO_STEP_DELAY_SECONDS: float = float(
    os.getenv("SCENARIO_STEP_DELAY_SECONDS", "2")
)
