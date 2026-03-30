"""
AI SOC Agent.

Provides threat narrative and recommended actions for a detection result.
By default the agent uses a built-in rule-based knowledge base so the system
works fully offline.  When an OPENAI_API_KEY is configured, richer GPT-powered
narratives are generated instead.
"""

from __future__ import annotations

from typing import Any

from config import OPENAI_API_KEY

# ---------------------------------------------------------------------------
# Built-in threat knowledge base (rule-based, no external dependency)
# ---------------------------------------------------------------------------
_KNOWLEDGE: dict[str, dict[str, Any]] = {
    "phishing_click": {
        "summary": "A user clicked a phishing link, indicating a potential account-takeover attempt.",
        "attack_chain": "Email delivered → Link clicked → Credentials entered → Suspicious login",
        "risk": "HIGH – credential compromise is likely; account takeover imminent.",
        "recommended_actions": ["revoke_session", "flag_account", "block_ip"],
        "mitre_technique": "T1566.002 – Spearphishing Link",
    },
    "credential_stuffing": {
        "summary": "Automated credential-stuffing attack detected from an external IP.",
        "attack_chain": "Leaked credential list → Automated login attempts → Account compromise",
        "risk": "CRITICAL – multiple accounts at risk; brute-force in progress.",
        "recommended_actions": ["block_ip", "revoke_session"],
        "mitre_technique": "T1110.004 – Credential Stuffing",
    },
    "impossible_travel": {
        "summary": "User authenticated from two geographically distant locations within minutes.",
        "attack_chain": "Legitimate login → Stolen session token → Login from foreign IP",
        "risk": "HIGH – session hijacking or stolen credentials.",
        "recommended_actions": ["flag_account", "revoke_session"],
        "mitre_technique": "T1078 – Valid Accounts",
    },
    "data_exfiltration": {
        "summary": "Abnormally large outbound data transfer detected from an internal host.",
        "attack_chain": "Malware installed → Data staged → Exfiltration to C2 server",
        "risk": "CRITICAL – sensitive data may already be leaving the network.",
        "recommended_actions": ["isolate_device", "block_ip"],
        "mitre_technique": "T1041 – Exfiltration Over C2 Channel",
    },
    "email_delivered": {
        "summary": "A phishing email was delivered to a user mailbox.",
        "attack_chain": "Phishing email crafted → Sent → Delivered to inbox",
        "risk": "LOW – no interaction yet, but user is at risk.",
        "recommended_actions": ["flag_account"],
        "mitre_technique": "T1566 – Phishing",
    },
    "link_clicked": {
        "summary": "User clicked a suspicious link inside an email.",
        "attack_chain": "Email delivered → Link clicked",
        "risk": "MEDIUM – browser may be compromised; credential phishing likely.",
        "recommended_actions": ["flag_account", "revoke_session"],
        "mitre_technique": "T1566.002 – Spearphishing Link",
    },
    "credential_entered": {
        "summary": "User submitted credentials on a suspected phishing page.",
        "attack_chain": "Link clicked → Fake login page → Credentials captured",
        "risk": "HIGH – password is now in attacker hands.",
        "recommended_actions": ["revoke_session", "flag_account"],
        "mitre_technique": "T1056.003 – Web Portal Capture",
    },
    "suspicious_login": {
        "summary": "Login attempt from an IP address with a poor reputation.",
        "attack_chain": "Credential obtained → Login from suspicious IP",
        "risk": "HIGH – may indicate successful credential compromise.",
        "recommended_actions": ["block_ip", "flag_account"],
        "mitre_technique": "T1078 – Valid Accounts",
    },
}

_DEFAULT_ANALYSIS: dict[str, Any] = {
    "summary": "Unknown threat type detected.",
    "attack_chain": "Unknown",
    "risk": "UNKNOWN – manual investigation required.",
    "recommended_actions": ["flag_account"],
    "mitre_technique": "N/A",
}


# ---------------------------------------------------------------------------
# OpenAI-powered narrative (optional)
# ---------------------------------------------------------------------------

def _openai_analyze(detection_result: dict[str, Any]) -> dict[str, Any] | None:
    """Return GPT-powered analysis or *None* if unavailable/disabled."""
    if not OPENAI_API_KEY:
        return None
    try:
        import openai  # type: ignore[import]

        openai.api_key = OPENAI_API_KEY
        event = detection_result.get("event", {})
        prompt = (
            f"You are a senior SOC analyst. Briefly explain the following security event "
            f"and recommend three response actions:\n{event}"
        )
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300,
        )
        content: str = response.choices[0].message.content or ""
        return {
            "summary": content,
            "attack_chain": detection_result.get("description", ""),
            "risk": detection_result.get("severity", "unknown").upper(),
            "recommended_actions": detection_result.get("recommended_action", "flag_account").split(","),
            "mitre_technique": "See MITRE ATT&CK",
        }
    except Exception:  # pragma: no cover
        return None


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def analyze(detection_result: dict[str, Any]) -> dict[str, Any]:
    """
    Produce a threat narrative for *detection_result*.

    Tries OpenAI first (if configured), then falls back to the built-in
    knowledge base.
    """
    if not detection_result.get("alert"):
        return {"summary": "No threat detected.", "recommended_actions": []}

    # Try AI-powered analysis first
    ai_result = _openai_analyze(detection_result)
    if ai_result:
        return ai_result

    # Rule-based fallback
    event = detection_result.get("event", {})
    attack_type: str = event.get("type") or event.get("event") or ""
    knowledge = _KNOWLEDGE.get(attack_type, _DEFAULT_ANALYSIS)

    return {
        "summary": knowledge["summary"],
        "attack_chain": knowledge["attack_chain"],
        "risk": knowledge["risk"],
        "recommended_actions": knowledge["recommended_actions"],
        "mitre_technique": knowledge["mitre_technique"],
        "event": event,
    }
