from __future__ import annotations

DEFAULT_TRACKED_SKILLS = [
    "block_4_grit",
    "block_5_resilience",
    "block_6_social",
    "block_6_leadership",
    "block_8_ownership",
    "block_8_curiosity",
    "block_10_calibration",
]

DEFAULT_AOT_SKILLS = [
    "block_4_grit",
    "block_6_social",
    "block_8_ownership",
    "block_10_calibration",
    "hr_conflict_resolution",
    "hr_prioritization",
]

SKILL_LABELS = {
    "block_4_grit": "grit and follow-through",
    "block_5_resilience": "stress resilience",
    "block_6_social": "collaboration and empathy",
    "block_6_leadership": "leadership and influence",
    "block_8_ownership": "ownership",
    "block_8_curiosity": "curiosity and learning agility",
    "block_10_calibration": "self-awareness and calibration",
    "backend": "backend engineering",
    "frontend": "frontend engineering",
    "ui": "ui engineering",
    "performance": "performance engineering",
    "db_design": "database design",
    "caching": "caching",
    "system_design": "system design",
    "hr_conflict_resolution": "conflict resolution and stakeholder mediation",
    "hr_ethics_scenario": "ethical decision making",
    "hr_prioritization": "prioritization and tight deadlines",
}

HR_SCENARIO_SKILLS = [
    "hr_conflict_resolution",
    "hr_ethics_scenario",
    "hr_prioritization",
]

TECHNICAL_SKILL_KEYWORDS = {
    "caching": ["cache", "ttl", "invalidation", "redis", "cache key", "eviction", "warm up"],
    "system_design": ["scale", "throughput", "partition", "latency", "reliability", "availability", "cap theorem"],
    "db_design": ["database", "sql", "schema", "index", "query", "normalization", "acid"],
    "backend": ["api", "backend", "service", "queue", "worker", "grpc", "rest"],
    "frontend": ["react", "frontend", "state", "render", "component", "virtual dom", "hooks"],
    "ui": ["accessibility", "design system", "usability", "interaction", "layout", "visual hierarchy"],
    "performance": ["profiling", "bundle", "latency", "render", "virtualization", "memory leak", "heap"],
    "hr_conflict_resolution": ["disagreement", "dispute", "compromise", "mediated", "deescalated", "alignment"],
    "hr_ethics_scenario": ["policy", "integrity", "dilemma", "whistleblower", "compliance", "honest"],
    "hr_prioritization": ["trade-off", "deadline", "urgent", "resources", "reprioritized", "pushback"],
}

# SEMA-Match: Multi-Aspect Decomposition
SKILL_ASPECTS = {
    "caching": ["latency reduction", "data consistency", "invalidation strategy"],
    "system_design": ["scalability", "fault tolerance", "load balancing"],
    "db_design": ["data integrity", "query optimization", "schema flexibility"],
    "block_4_grit": ["persistence", "follow-through", "long-term focus"],
    "block_8_ownership": ["proactivity", "accountability", "outcome-driven"],
    "block_10_calibration": ["self-awareness", "uncertainty management", "ego-check"],
    "hr_conflict_resolution": ["empathy", "mediation", "assertiveness"],
    "hr_ethics_scenario": ["moral courage", "compliance", "fairness"],
    "hr_prioritization": ["time management", "trade-off analysis", "urgency handling"],
}

BEHAVIORAL_SKILL_KEYWORDS = {
    "block_4_grit": [
        "grit",
        "persistent",
        "persevered",
        "kept going",
        "follow through",
        "discipline",
        "stayed with",
        "did not give up",
    ],
    "block_5_resilience": [
        "pressure",
        "stress",
        "setback",
        "recovered",
        "bounce back",
        "calm",
        "de-escalated",
        "regulated",
    ],
    "block_6_social": [
        "team",
        "collaborated",
        "stakeholder",
        "listened",
        "empathy",
        "aligned",
        "relationship",
        "communicated",
    ],
    "block_6_leadership": [
        "led",
        "mentored",
        "guided",
        "delegated",
        "influenced",
        "initiative",
        "motivated",
        "coached",
    ],
    "block_8_ownership": [
        "ownership",
        "owned",
        "accountable",
        "responsibility",
        "proactive",
        "drove",
        "decided",
        "followed up",
    ],
    "block_8_curiosity": [
        "curious",
        "asked why",
        "explored",
        "experimented",
        "learned",
        "investigated",
        "feedback",
        "iterated",
    ],
    "block_10_calibration": [
        "not sure",
        "uncertain",
        "assumption",
        "validated",
        "checked",
        "estimate",
        "confidence",
        "i do not know",
    ],
}

SKILL_KEYWORDS = {**TECHNICAL_SKILL_KEYWORDS, **BEHAVIORAL_SKILL_KEYWORDS}

SKILL_PROMPTS = {
    "block_4_grit": "persistence perseverance follow through long-term effort after setbacks",
    "block_5_resilience": "stays calm under pressure recovers from setbacks and regulates stress",
    "block_6_social": "collaborates listens builds trust shows empathy and aligns stakeholders",
    "block_6_leadership": "leads influences mentors creates clarity and drives others forward",
    "block_8_ownership": "takes responsibility acts proactively owns outcomes and follows through",
    "block_8_curiosity": "asks thoughtful questions learns quickly experiments and seeks feedback",
    "block_10_calibration": "admits uncertainty checks assumptions validates confidence and self-corrects",
    "caching": "design cache invalidation ttl consistency redis key strategy",
    "system_design": "system design trade offs partitioning reliability bottlenecks",
    "db_design": "database design schema indexing query performance and correctness",
    "backend": "backend services api contracts queues resilience and observability",
    "frontend": "frontend state management accessibility async flows and rendering",
    "ui": "interaction design accessibility visual hierarchy and usability decisions",
    "performance": "profiling bottlenecks bundle size render cost and optimization",
}

JD_SKILL_MAP = {
    "redis": "caching",
    "cache": "caching",
    "caching": "caching",
    "api": "backend",
    "rest": "backend",
    "database": "db_design",
    "sql": "db_design",
    "scaling": "system_design",
    "microservices": "system_design",
    "leadership": "block_6_leadership",
    "mentor": "block_6_leadership",
    "coaching": "block_6_leadership",
    "stakeholder": "block_6_social",
    "collaboration": "block_6_social",
    "teamwork": "block_6_social",
    "empathy": "block_6_social",
    "resilience": "block_5_resilience",
    "pressure": "block_5_resilience",
    "stress": "block_5_resilience",
    "persistent": "block_4_grit",
    "grit": "block_4_grit",
    "perseverance": "block_4_grit",
    "ownership": "block_8_ownership",
    "accountability": "block_8_ownership",
    "initiative": "block_8_ownership",
    "curiosity": "block_8_curiosity",
    "learning agility": "block_8_curiosity",
    "feedback": "block_8_curiosity",
    "self-awareness": "block_10_calibration",
    "calibration": "block_10_calibration",
    "judgment": "block_10_calibration",
}

ROLE_KEYWORD_TEMPLATES = {
    "backend": ["backend", "db_design", "caching", "system_design"],
    "frontend": ["frontend", "ui", "performance"],
    "product": ["block_6_social", "block_8_ownership", "block_10_calibration"],
    "manager": ["block_6_leadership", "block_6_social", "block_5_resilience"],
    "lead": ["block_6_leadership", "block_8_ownership", "block_10_calibration"],
    "founder": ["block_6_leadership", "block_8_ownership", "block_5_resilience"],
    "operations": ["block_8_ownership", "block_6_social", "block_10_calibration"],
    "sales": ["block_6_social", "block_6_leadership", "block_5_resilience"],
    "support": ["block_6_social", "block_5_resilience", "block_10_calibration"],
    "recruit": ["block_6_social", "block_8_curiosity", "block_10_calibration"],
}


def is_behavioral_skill(skill: str) -> bool:
    normalized = str(skill or "").strip().lower()
    return normalized.startswith("block_") or normalized.startswith("hr_")

def display_skill(skill: str) -> str:
    normalized = str(skill or "").strip().lower()
    if normalized in SKILL_LABELS:
        return SKILL_LABELS[normalized]
    return normalized.replace("_", " ")


def role_defaults(role: str) -> list[str]:
    normalized = str(role or "").strip().lower()
    defaults: list[str] = []
    for keyword, skills in ROLE_KEYWORD_TEMPLATES.items():
        if keyword in normalized:
            for skill in skills:
                if skill not in defaults:
                    defaults.append(skill)

    if defaults:
        return defaults

    return [
        "block_6_social",
        "block_8_ownership",
        "block_10_calibration",
    ]


def signal_terms() -> set[str]:
    terms = {
        "because",
        "therefore",
        "however",
        "tradeoff",
        "trade-off",
        "result",
        "outcome",
        "impact",
        "example",
        "decision",
        "constraint",
    }
    for keywords in SKILL_KEYWORDS.values():
        for keyword in keywords:
            for part in keyword.split():
                if len(part) >= 3:
                    terms.add(part)
    return terms
