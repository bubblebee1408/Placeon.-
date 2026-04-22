# Thinking Model Specification

## Why This Document Exists

PlacedOn already has the beginnings of a **brain**:
- interview orchestration
- question generation
- answer judging
- integrity checks
- profile aggregation

What is still missing is the explicit **thinking model**:
- how the system decides what to ask next
- how it turns one answer into structured evidence
- how it updates confidence
- how it knows when it has enough evidence
- how it produces a report that companies can trust

This document defines that missing layer.

---

## Core Product Thesis

PlacedOn is not just an AI interviewer.

It is a **decision system** that:
1. gathers evidence over a 30-40 minute interview,
2. updates a live internal model of the candidate,
3. decides which missing uncertainty matters most,
4. stops only when confidence is high enough or time runs out,
5. turns the final state into a report, star rating, and role/company fit recommendation.

The job of the thinking model is not to "sound intelligent".
Its job is to **make disciplined decisions under incomplete evidence**.

---

## Design Principle

The model must think like a strong human interviewer:

- Start broad
- Notice strong or weak signals
- Probe where signal is unclear
- Challenge polished but shallow answers
- Separate evidence from impression
- Record uncertainty honestly
- Never act more certain than the interview supports

That means PlacedOn needs two layers:

### 1. Conversational Brain
This is what the candidate feels.
- asks questions
- listens
- responds naturally
- keeps the interview flowing

### 2. Thinking Backbone
This is invisible.
- stores state
- scores dimensions
- tracks confidence
- detects contradictions
- chooses next targets
- determines final report structure

The conversational brain should never directly decide hiring quality on its own.
It should feed the thinking backbone.

---

## What Already Exists in Code

Today the codebase already contains useful pieces:

- `PlacedOn/aot_layer/` handles question flow, retries, and probing.
- `PlacedOn/backend/app/live_runtime.py` connects the interview runtime, judging, integrity, aggregation, and fit scoring.
- `PlacedOn/layer2/` extracts technical and behavioral signals.
- `PlacedOn/layer3/` handles safety, fallback, and integrity signals.
- `PlacedOn/layer5/` aggregates turn-level evidence into profile outputs.

This is a real foundation.

But the implemented runtime is still mostly reasoning over:
- a smaller skill/state vector
- confidence
- interview coverage

It does **not yet fully operationalize the 16-dimension framework** described in:
- `PlacedOn_Dimensions.pdf`
- `PlacedOn_ScoringFoundation.pdf`
- `PlacedOn_ResearchReport.pdf`

That is the gap this document closes.

---

## The Internal Candidate State

The thinking model should maintain a live state for all 16 dimensions.

### Canonical state per dimension

Each dimension stores:
- `score`: current estimate from 1.0 to 5.0
- `confidence`: how trustworthy the estimate is
- `evidence_count`: number of useful supporting signals
- `contradiction_flags`: count of direct inconsistencies
- `latest_rationale`: short explanation of why the score moved
- `evidence_history`: the exact turn-level evidence objects

### The 16 dimensions

#### Bucket 1 — Who They Are
1. Personality & Character
2. Creativity & Innovation
3. Self Awareness
4. Motivation Type

#### Bucket 2 — How They Work
5. Work Environment Fit
6. Collaboration Style
7. Ownership & Accountability
8. Consistency & Reliability

#### Bucket 3 — How They Think
9. Problem Solving Under Pressure
10. Learning Speed
11. Communication Clarity
12. Performance Under Pressure

#### Bucket 4 — What They Know
13. Technical Skills
14. Soft Skills
15. Corporate World Readiness
16. Cultural Alignment

### Bucket state

Each of the 4 buckets also stores:
- bucket score
- bucket confidence
- dominant strengths
- dominant risks

### Global state

The session also stores:
- candidate baseline from resume + pre-interview form
- job role target
- role-specific dimension weights
- remaining time
- already asked question IDs
- integrity/trust score
- interview phase
- completion readiness

---

## Evidence Object

Every meaningful answer fragment should become an evidence object.

Each evidence object should contain:
- `question_id`
- `dimension`
- `quote`
- `micro_score`
- `evidence_quality`
- `contradiction_penalty`
- `source_turn_index`
- `confidence_label`

### Why this matters

This gives you:
- auditability
- explainability
- human review support
- candidate dispute resolution
- better second-round handoff to employers

Without evidence objects, the report becomes "AI opinion".
With evidence objects, the report becomes "traceable assessment".

---

## Inputs to the Thinking Model

The model should not think from the live answer alone.
It should think from four input streams:

### 1. Pre-interview context
- resume
- candidate form
- years of experience
- claimed tech stack
- project summaries
- role target

### 2. Live interview transcript
- answer text
- timestamps
- pauses
- reformulations
- candidate corrections

### 3. Runtime signal extractors
- technical depth signals
- behavioral signals
- consistency/drift signals
- clarity markers
- trade-off markers
- uncertainty markers

### 4. Job/company context
- required skills
- experience band
- company style
- environment preference
- critical dimensions for the role

---

## The Thinking Loop

Every turn should follow the same internal loop.

## Step 1: Parse the answer

The system extracts:
- direct factual signals
- behavioral signals
- missing concepts
- contradiction clues
- evidence quotes

This stage should ask:
- what did the candidate actually claim?
- what did they explain clearly?
- what did they avoid?
- what did they soften or overstate?

## Step 2: Score local evidence

For each relevant dimension, compare the answer against anchor descriptions:
- 1-star anchor
- 3-star anchor
- 5-star anchor

Then assign:
- micro score
- evidence quality
- contradiction penalty
- confidence label

This is the cold-start-safe layer from the scoring foundation PDF.

## Step 3: Update dimension state

Each new evidence object updates the dimension state:
- strengthen if aligned with prior evidence
- weaken if contradictory
- raise confidence when repeated evidence agrees
- keep uncertainty high if answer is vague

## Step 4: Update interview trust layer

Integrity signals do not directly define ability.
They define how carefully the system should trust the answer.

Trust layer inputs:
- consistency drift
- suspiciously generic answer patterns
- mismatch between polished language and missing mechanism
- answer collapse on follow-up

Trust score should influence confidence more than raw score.

Example:
- polished but generic answer -> moderate score, low confidence
- detailed imperfect answer -> good score, higher confidence

## Step 5: Recalculate what matters next

The model now decides:
- which dimension has the highest uncertainty
- which critical role-weighted area is still under-evidenced
- whether contradiction resolution is more important than breadth
- whether the interview should deepen or move on

## Step 6: Choose next question type

The model should choose among:
- warm-up
- technical
- behavioral
- scenario
- reflective
- contradiction probe
- clarification
- pressure test

The type depends on what kind of uncertainty remains.

---

## Decision Matrix for Next Question Selection

This is the actual missing thinking logic.

Each candidate dimension gets a dynamic priority score:

`dimension_priority = role_weight x uncertainty x evidence_gap x contradiction_boost x phase_factor x time_factor x trust_factor`

### The factors

#### 1. Role weight
How important is this dimension for this job?

Examples:
- backend fresher: Technical Skills, Learning Speed, Communication Clarity, Ownership are high
- frontend fresher: Communication Clarity, Collaboration Style, Creativity, Technical Skills are high
- startup role: Ownership, Learning Speed, Performance Under Pressure rise

#### 2. Uncertainty
How little do we currently know?

High when:
- only one weak answer exists
- answers were generic
- confidence is low

#### 3. Evidence gap
How far are we from minimum required evidence coverage?

Examples:
- no real example yet
- no failure story yet
- no conflict/pressure example yet
- no technical trade-off example yet

#### 4. Contradiction boost
Did the candidate say something that needs testing?

Examples:
- says "I always take ownership" but gives blame-heavy story
- says "I learn fast" but cannot explain how they learned

#### 5. Phase factor
Interview phases have different priorities:
- opening: breadth and comfort
- middle: coverage
- late middle: contradiction and depth
- close: unresolved critical gaps only

#### 6. Time factor
As time drops:
- stop chasing low-value curiosity
- focus on high-weight unresolved dimensions
- avoid introducing new low-priority branches

#### 7. Trust factor
If candidate integrity is dropping:
- prefer personal, specific, experience-based probes
- prefer follow-ups that require real memory

---

## Question Selection Rules

The system should follow these rules:

### Rule 1
Never ask the next question only because it is "interesting".
Ask it because it changes decision quality.

### Rule 2
If a critical dimension is both low-confidence and high-weight, it wins.

### Rule 3
If two dimensions tie, prefer the one with:
- lower confidence
- fewer evidence items
- higher contradiction risk

### Rule 4
If trust is falling, switch from generic questions to personally anchored probes.

### Rule 5
If time remaining is low, ask questions that cover multiple dimensions at once.

Example:
"Tell me about a time you made a bad technical decision under pressure and what you changed after."

This can cover:
- technical skills
- self-awareness
- ownership
- performance under pressure
- learning speed

---

## How the AI Should "Think" in Practice

Below is the internal decision style PlacedOn should follow.

### Example 1: Polished but shallow candidate

Observed:
- candidate sounds fluent
- uses correct tech words
- gives no mechanism
- avoids specifics

Thinking model response:
- do not over-reward fluency
- keep technical score moderate
- mark confidence low
- inject personal/probe question

Next question:
"Tell me about one time this approach failed in your own project. What exactly broke?"

### Example 2: Strong but nervous fresher

Observed:
- candidate pauses a lot
- answer is not polished
- but examples are concrete and thoughtful

Thinking model response:
- do not penalize hesitation
- reward concrete mechanism
- raise score with medium-high confidence
- reduce emphasis on delivery style

### Example 3: High collaboration claim, weak evidence

Observed:
- candidate says they are a team player
- stories are mostly individual

Thinking model response:
- keep collaboration score provisional
- add contradiction flag
- ask social conflict probe

Next question:
"Tell me about a time you and a teammate disagreed on what to do. What did you do next?"

---

## Confidence Model

Confidence should not be a vague feeling.

It should be based on:
- evidence quality
- consistency across turns
- specificity
- contradiction count
- number of independent signals
- whether the signal came under probing or only in an unchallenged answer

### Confidence thresholds

#### High confidence
- 2+ strong aligned evidence items
- low contradiction
- specific examples
- good depth

#### Medium confidence
- some evidence, but incomplete
- one example only
- moderate specificity

#### Low confidence
- vague answer
- no example
- contradiction unresolved
- candidate avoided the core probe

### Important rule

PlacedOn should be willing to say:
- "score looks promising, but confidence is low"

That honesty is a product strength, not a weakness.

---

## Stopping Criteria

The interview should end when one of these is true:

### End because confidence is sufficient
- all critical dimensions have enough evidence
- overall interview confidence passes threshold
- role fit confidence is acceptable

### End because maximum time is reached
- report should explicitly show unresolved low-confidence areas

### End because integrity is too compromised
- system can continue carefully or flag for human review

### Recommended completion rule

For fresher to 5-year software engineering roles:
- at least 10 turns
- no more than 15 turns
- at least one strong signal in each bucket
- at least one contradiction or failure probe
- at least one role-specific technical trade-off question

---

## Report Generation Backbone

The report should be produced from the final dimension state, not from a freeform summary prompt alone.

## Report sections

### A. Executive summary
- one paragraph
- strongest 2-3 takeaways
- plain language

### B. Overall recommendation
- overall star band
- confidence band
- hire / proceed / hold / not enough evidence / do not recommend

### C. 4 bucket scorecard
- Who They Are
- How They Work
- How They Think
- What They Know

Each should show:
- star rating
- confidence
- summary sentence

### D. 16-dimension breakdown

For each dimension:
- star rating
- confidence
- evidence quote
- short rationale
- any caution if low-confidence

### E. Technical signal section
- strongest technical evidence
- depth level
- areas needing second-round validation

### F. Human/workstyle section
- collaboration style
- ownership style
- pressure pattern
- work environment fit

### G. Risk flags

Examples:
- polished but under-evidenced
- inconsistent ownership language
- low clarity under pressure
- high potential, low corporate readiness
- strong technical signal, uncertain collaboration signal

### H. Interview integrity section
- trust score
- anomaly notes if needed
- never overstate

### I. Recommended second-round questions
- generated only from low-confidence/high-importance dimensions

### J. Company fit snapshot
- best-fit environment
- likely mismatch environments
- role family fit

---

## Star Rating Logic

Do not reduce the entire candidate to one crude number too early.

### Recommended output
- 16 dimension stars
- 4 bucket stars
- 1 overall star
- 1 confidence band

### Example weighting for software engineering MVP

#### Fresher
- Technical Skills: 1.4
- Learning Speed: 1.3
- Communication Clarity: 1.2
- Ownership & Accountability: 1.2
- Problem Solving Under Pressure: 1.2
- Self Awareness: 1.1
- Collaboration Style: 1.0
- Corporate World Readiness: 1.0
- others: baseline 0.8 to 1.0

#### 3-7 years experience
- Technical Skills: 1.3
- Ownership & Accountability: 1.3
- Collaboration Style: 1.2
- Performance Under Pressure: 1.2
- Communication Clarity: 1.1
- Cultural Alignment: 1.1
- others: baseline 0.9 to 1.0

### Gating rule

Do not allow a very high overall recommendation if:
- any critical dimension is both low score and high confidence
- or too many critical dimensions remain low confidence

This avoids fake precision.

---

## Company Matching Backbone

The same 16-dimension state should drive employer matching.

## Job profile structure

Each company role should define:
- target score per dimension
- weight per dimension
- critical dimensions
- company culture vector

## Match output

PlacedOn should generate:
- overall fit
- capability fit
- culture fit
- risk flags
- dimension-by-dimension gaps

This is better than a single fit score because it can detect:
- high skill / low culture fit
- high culture / low skill fit
- good fresher potential / weak current readiness

---

## MVP Recommendation for Your Team

Your team should **not** build the full dream version first.

## Build now

### 1. Thinking state
Implement the 16-dimension state with:
- score
- confidence
- evidence count
- contradiction flags

### 2. Anchor scoring
Write the 48 anchor descriptions:
- 1-star
- 3-star
- 5-star

### 3. Decision matrix
Use a simple explicit formula for next-question priority.
No fancy learned planner needed yet.

### 4. Evidence-first reporting
Every dimension shown to companies must include evidence.

### 5. Confidence gating
If confidence is low, say so.

## Build later

- dynamic learned weights from real hiring outcomes
- richer multimodal integrity models
- custom company-specific dimension templates
- second-round company-interviewer mode
- automatic interviewer self-calibration from thousands of sessions

---

## Product Decision

## My decision: yes, this is worth building

But only if you build it in the right order.

### What is strong
- The problem is real.
- The 16-dimension framework is much more differentiated than coding-test products.
- The report + matching + second-round handoff can become a serious B2B workflow.
- Your research and architecture direction are stronger than most early student teams.

### What is still missing
- a single canonical thinking model
- explicit question-priority math
- evidence-led confidence logic
- clean connection between interview state and shareable/company profile

### What to do next

#### Phase 1
Turn the 16-dimension framework into a real runtime state model.

#### Phase 2
Connect that state model to the interview controller and question policy.

#### Phase 3
Generate the full employer report and shareable profile from that state.

#### Phase 4
Only after this, optimize with more complex ML.

The startup does not need a genius AI first.
It needs a **disciplined evidence machine** first.

That is the right version of the PlacedOn thinking model.
