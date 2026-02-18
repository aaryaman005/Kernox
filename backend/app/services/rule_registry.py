from dataclasses import dataclass
from typing import Callable, List
from sqlalchemy.orm import Session

from app.models.event import Event
from app.services.time_window_query import TimeWindowQueryEngine


# ─────────────────────────────────────────────
# Rule Definition
# ─────────────────────────────────────────────


@dataclass(frozen=True)
class DetectionResult:
    rule_name: str
    severity: str
    risk_score: int
    matched_events: List[Event]


@dataclass(frozen=True)
class Rule:
    name: str
    description: str
    evaluate: Callable[[Session, Event], List[DetectionResult]]


# ─────────────────────────────────────────────
# Static Detection Parameters
# ─────────────────────────────────────────────

AUTH_FAILURE_THRESHOLD = 5
AUTH_FAILURE_WINDOW_SECONDS = 60

SUSPICIOUS_PROCESS_NAMES = {
    "mimikatz",
    "nc",
    "netcat",
    "ncat",
    "powershell.exe",
    "cmd.exe",
}


# ─────────────────────────────────────────────
# Rule 1 — Suspicious Process Name
# ─────────────────────────────────────────────


def rule_suspicious_process_name(
    db: Session,
    event: Event,
) -> List[DetectionResult]:
    if event.flat_event_type != "process_start":
        return []

    process_info = event.payload.get("process") or {}
    name = process_info.get("name")

    if not name:
        return []

    if name.lower() not in SUSPICIOUS_PROCESS_NAMES:
        return []

    return [
        DetectionResult(
            rule_name="SUSPICIOUS_PROCESS_NAME",
            severity="high",
            risk_score=70,
            matched_events=[event],
        )
    ]


# ─────────────────────────────────────────────
# Rule 2 — Auth Brute Force
# ─────────────────────────────────────────────


def rule_auth_bruteforce(
    db: Session,
    event: Event,
) -> List[DetectionResult]:
    if event.flat_event_type != "auth_failure":
        return []

    if not event.timestamp:
        return []

    events = TimeWindowQueryEngine.get_events_within_window(
        db,
        endpoint_id=event.endpoint_id,
        event_type="auth_failure",
        reference_time=event.timestamp,
        window_seconds=AUTH_FAILURE_WINDOW_SECONDS,
    )

    if len(events) < AUTH_FAILURE_THRESHOLD:
        return []

    return [
        DetectionResult(
            rule_name="AUTH_BRUTE_FORCE",
            severity="critical",
            risk_score=90,
            matched_events=events,
        )
    ]


# ─────────────────────────────────────────────
# Rule Registry (STATIC)
# ─────────────────────────────────────────────

RULES: List[Rule] = [
    Rule(
        name="SUSPICIOUS_PROCESS_NAME",
        description="Detect execution of known suspicious tools",
        evaluate=rule_suspicious_process_name,
    ),
    Rule(
        name="AUTH_BRUTE_FORCE",
        description="Detect repeated authentication failures within short time window",
        evaluate=rule_auth_bruteforce,
    ),
]
