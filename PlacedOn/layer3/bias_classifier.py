"""
PlacedOn Layer 3 — ABLEIST Bias Classifier

Expanded using the ABLEIST framework (arXiv:2510.10998):
- 5 ableism-specific harm categories
- 3 intersectional harm categories
- India-specific patterns (caste, college tier, regional origin)

Total: 55 safe + 65 unsafe = 120 training examples
"""

from __future__ import annotations

from sklearn.feature_extraction.text import HashingVectorizer
from sklearn.linear_model import LogisticRegression

from layer3.config import Layer3Config
from layer3.models import BiasAssessment

# --- High-risk patterns (keyword match, catches anything the model misses) ---

_HIGH_RISK_PATTERNS = [
    # Protected characteristics
    "how old",
    "year were you born",
    "married",
    "relationship status",
    "pregnant",
    "children soon",
    "religion",
    "nationality",
    "parents from",
    "caste",
    "ethnic background",
    "gender identity",
    "political party",
    "disabilities",
    "medical condition",
    # ABLEIST-specific (arXiv:2510.10998)
    "wheelchair",
    "blind",
    "deaf",
    "mental health",
    "psychiatric",
    "autistic",
    "neurodivergent",
    "medication",
    "therapy sessions",
    "special needs",
    # India-specific intersectional
    "which college tier",
    "tier 3 college",
    "tier 2 college",
    "reserved category",
    "quota",
    "sc/st",
    "obc",
    "mother tongue",
    "native place",
    "family business",
]


class BiasEnforcer:
    def __init__(self, config: Layer3Config | None = None) -> None:
        self._config = config or Layer3Config()
        self._vectorizer = HashingVectorizer(
            n_features=self._config.classifier_features,
            alternate_sign=False,
            norm="l2",
        )
        self._model = LogisticRegression(
            random_state=self._config.classifier_random_state,
            solver="liblinear",
            max_iter=500,
        )
        self._unsafe_index = 1
        self._train()

    async def assess(self, question: str) -> BiasAssessment:
        text = (question or "").strip()
        if not text:
            return BiasAssessment(bias_score=1.0, approved=False)

        matrix = self._vectorizer.transform([text])
        probability = float(self._model.predict_proba(matrix)[0][self._unsafe_index])
        lowered = text.lower()
        if any(pattern in lowered for pattern in _HIGH_RISK_PATTERNS):
            probability = max(probability, 0.9)
        probability = round(max(0.0, min(probability, 1.0)), 4)

        return BiasAssessment(
            bias_score=probability,
            approved=probability <= self._config.bias_reject_threshold,
        )

    def _train(self) -> None:
        safe_questions = [
            # --- Behavioral interview questions (HCV-aligned) ---
            "Tell me about a time you handled a difficult stakeholder conversation.",
            "Describe a situation where you had to rebuild trust after a mistake.",
            "Walk me through a time you showed ownership under pressure.",
            "How do you respond when feedback challenges your approach?",
            "Tell me about a conflict within your team and how you resolved it.",
            "Describe a setback that tested your resilience.",
            "How do you calibrate your confidence when you are unsure?",
            "Tell me about a time you had to influence without formal authority.",
            "How do you decide when to ask for help versus push through yourself?",
            "Describe a decision where you balanced speed against quality.",
            "Tell me about a project where you learned something unexpectedly.",
            "How do you adapt when priorities change late in a project?",
            "Describe a time you coached or mentored someone.",
            "How do you keep communication clear across different stakeholders?",
            "Tell me about a moment when you had to de-escalate tension on a team.",
            "Describe how you reflect after a failure or missed target.",
            "How do you make sure your work is reliable and repeatable?",
            "Tell me about a time you had to make a judgment call with incomplete data.",
            "How do you keep yourself accountable for outcomes?",
            "Describe a situation where empathy changed how you handled a problem.",
            # --- Technical questions (safe) ---
            "Explain how you would optimize cache invalidation in a distributed system.",
            "How would you design a scalable queue processing architecture?",
            "Describe trade-offs between hash maps and balanced trees.",
            "How do you approach debugging a latency issue in production?",
            "Walk through your method for reducing memory usage in a service.",
            "How would you evaluate database indexing strategy for read-heavy traffic?",
            "Explain your approach for handling retries and idempotency.",
            "How do you prioritize correctness and performance in algorithm design?",
            "Describe how you would monitor and tune system throughput.",
            "How would you communicate technical trade-offs to your team?",
            # --- Situational (safe but tricky) ---
            "Describe a time when your team disagreed on a technical direction.",
            "How would you handle a situation where you missed a critical deadline?",
            "Tell me about working with someone whose style was very different from yours.",
            "What do you do when you realize your initial approach was wrong?",
            "How do you handle ambiguity in requirements?",
            "Walk me through your process for onboarding to a new codebase.",
            "Describe how you give constructive feedback to a peer.",
            "How do you manage competing priorities from multiple stakeholders?",
            "Tell me about a time you had to say no to a request.",
            "What is your approach to learning a new technology quickly?",
            # --- Leadership / growth (safe) ---
            "How do you set goals for yourself and track progress?",
            "Describe your approach to continuous learning.",
            "Tell me about a time you took initiative without being asked.",
            "How do you build trust with a new team?",
            "What does accountability mean to you in a professional context?",
            # --- Accessibility-aware (safe — asking about NEEDS, not identity) ---
            "What tools or setup help you do your best work?",
            "Do you have any workspace preferences we should know about?",
            "Is there any accommodation we can provide during this interview?",
            "How do you prefer to receive feedback?",
            "What communication format works best for you in meetings?",
        ]

        unsafe_questions = [
            # --- Category 1: Direct protected characteristic probing ---
            "How old are you and what year were you born?",
            "Are you planning to have children soon?",
            "Which religion do you follow and does it affect your work?",
            "What is your nationality and where are your parents from?",
            "Are you married and what is your relationship status?",
            "What is your gender identity?",
            "Are you pregnant or planning a pregnancy?",
            "Which political party do you support?",
            "Do you plan to get married soon?",
            "Who do you live with and what is your family situation?",
            # --- Category 2: ABLEIST — Disability probing (arXiv:2510.10998) ---
            "Do you have any disabilities we should know about?",
            "Are you neurodivergent or autistic?",
            "Are you taking medication for any condition?",
            "Do you identify as transgender?",
            "Do you have any chronic health issues that would affect attendance?",
            "Have you ever been diagnosed with a mental health condition?",
            "Do you need a wheelchair or any mobility device?",
            "Is your vision or hearing impaired in any way?",
            "Have you ever taken extended medical leave?",
            "Do you attend therapy sessions regularly?",
            # --- Category 3: ABLEIST — Inspiration porn / Superhumanization ---
            "You must be so brave to work despite your condition.",
            "Your disability probably makes you extra focused, right?",
            "It is inspiring that someone like you is applying for this role.",
            "People with your background usually struggle — how did you manage?",
            "You have overcome so much — that must make you extra resilient.",
            # --- Category 4: ABLEIST — Tokenism ---
            "We need someone from your background for our diversity numbers.",
            "Having someone like you would really help our inclusion metrics.",
            "Your profile would be great for our diversity report.",
            "We are looking to fill a diversity quota — would you be interested?",
            "Our team lacks representation from your community.",
            # --- Category 5: India-specific intersectional bias ---
            "What is your caste or ethnic background?",
            "Would your caste create issues with this client-facing role?",
            "Which college tier did you graduate from?",
            "Your college is not from the top tier — how will you keep up?",
            "Are you from a reserved category?",
            "Did you get admission through a quota?",
            "Where is your native place and what is your mother tongue?",
            "What country are you really from?",
            "How much childcare support do you have at home?",
            "Would your religion prevent you from working certain days?",
            # --- Category 6: Subtle / indirect bias ---
            "Do you think your age might affect your ability to learn new tools?",
            "Will your family responsibilities affect your availability?",
            "Can you work late nights or is there a personal situation we should know?",
            "Are there any cultural practices that would conflict with our schedule?",
            "Do you have a support system at home if work gets demanding?",
            "How does your partner feel about you working long hours?",
            "Is English your first language or did you learn it later?",
            "Would you be comfortable in a team where you are the only one from your background?",
            "Do you think your physical condition limits the kind of work you can do?",
            "Some people from your region struggle with our pace — are you sure you can handle it?",
            # --- Category 7: Mental health / neurodiversity probing ---
            "Have you ever had anxiety that affected your work?",
            "Do you have ADHD or any attention-related condition?",
            "Are you on the autism spectrum?",
            "Have you ever had depression?",
            "Do you take any psychiatric medication?",
        ]

        labels = [0] * len(safe_questions) + [1] * len(unsafe_questions)
        texts = safe_questions + unsafe_questions

        features = self._vectorizer.transform(texts)
        self._model.fit(features, labels)
