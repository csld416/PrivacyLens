"""Load and validate the user-provided privacy context."""

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Set

import yaml


@dataclass(frozen=True)
class SensitiveTerm:
    value: str
    entity_type: str


@dataclass(frozen=True)
class PrivacyContext:
    purpose: str
    audience: str
    guidance: List[str]
    always_replace: Set[str]
    safe_literals: Set[str]
    safe_networks: List[str]
    sensitive_context: List[str]
    safe_context: List[str]
    sensitive_terms: List[SensitiveTerm]


def load_context(path: Path) -> PrivacyContext:
    with path.open("r", encoding="utf-8") as handle:
        raw: Dict[str, object] = yaml.safe_load(handle) or {}

    video = raw.get("video", {})
    policy = raw.get("policy", {})
    if not isinstance(video, dict) or not isinstance(policy, dict):
        raise ValueError("context file must contain 'video' and 'policy' mappings")

    terms = []
    for item in policy.get("sensitive_terms", []):
        if not isinstance(item, dict) or not item.get("value") or not item.get("type"):
            raise ValueError("each sensitive term requires value and type")
        terms.append(SensitiveTerm(str(item["value"]), str(item["type"])))

    return PrivacyContext(
        purpose=str(video.get("purpose", "")),
        audience=str(video.get("audience", "")),
        guidance=[str(value) for value in policy.get("guidance", [])],
        always_replace={str(value).upper() for value in policy.get("always_replace", [])},
        safe_literals={str(value).upper() for value in policy.get("safe_literals", [])},
        safe_networks=[str(value) for value in policy.get("safe_networks", [])],
        sensitive_context=[str(value).lower() for value in policy.get("sensitive_context", [])],
        safe_context=[str(value).lower() for value in policy.get("safe_context", [])],
        sensitive_terms=terms,
    )

