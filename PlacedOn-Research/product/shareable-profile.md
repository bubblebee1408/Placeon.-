# Shareable Verified Profile

## The Core Tension

A shareable profile feels like a revenue threat if you think of it as a resume replacement — something candidates send instead of a PDF, cutting PlacedOn out of the hiring loop.

It is only a threat if companies can extract full value from the share without needing PlacedOn. The question is: what is in the share, and what is held back?

---

## What Makes the Profile Valuable to a Company

There are two distinct components:

**1. The data** — skills, role, summary, scores
**2. The verification** — the fact that these signals were produced by a neutral, bias-checked AI interview under controlled conditions, not self-reported

A PDF can carry the data. It cannot carry the verification. That is PlacedOn's moat.

A candidate could screenshot their profile and send it on WhatsApp. The company sees numbers but has no reason to trust those numbers unless they trust the source. Once PlacedOn has a reputation, a "Verified by PlacedOn" badge on a hosted link means something a screenshot never will.

---

## Architecture: Two-Tier Sharing

### Tier 1 — Public Summary Card (shareable freely)

Hosted at `placedon.com/p/{candidate_id}`. This is what the candidate shares with:
- College placement cells
- Recruiters
- LinkedIn
- WhatsApp
- Direct applications

**Contains:**
- Name
- Role assessed
- Verification date
- Top 3 skill badges (labels only, no raw scores)
- Single AI-generated summary sentence ("Strong backend fundamentals, demonstrated caching and API design depth")
- "Verified by PlacedOn" badge with visual trust indicator

**Does not contain:**
- Contact details
- Detailed scores
- Interview signals
- Behavioral integrity data

This is a **certification card**, not a resume. Comparable to Credly badges. The page always ends with a "View Full Verified Profile →" CTA that requires a company account.

### Tier 2 — Full Profile (company platform only)

Accessible only after a company creates an account on PlacedOn.

**Contains:**
- Full skill scores with confidence levels
- Evidence-backed signals
- Behavioral integrity score
- Weak and under-evidenced areas
- Role fit percentage
- Candidate contact (only after two-way opt-in)
- Application pipeline management

---

## Why This Protects Revenue Instead of Threatening It

The shareable link is not a revenue leak. It is a **company acquisition funnel that costs nothing**.

```
Candidate shares link with college placement cell
    → Placement officer clicks it
    → Sees verified summary card
    → Sees "View Full Profile" CTA
    → Creates free company account
    → Becomes a paying customer
```

Every share is a warm inbound lead. The candidate does the B2B marketing. Companies that receive profiles via shared links are already sold on the product before any sales pitch — they just saw a verified candidate. That is the conversion moment.

---

## Additional Guardrails

**Expiring links** — public card links expire every 90 days and require the candidate to re-activate. This keeps profiles fresh and creates a reason for companies to stay on the platform rather than saving a static snapshot.

**No score export** — the summary card never shows raw numbers, only labels (Strong / Developing). Precise scores exist only inside PlacedOn. A screenshot is a weaker trust signal than the hosted card.

**"Apply with PlacedOn" button** — an embeddable apply button that companies can add to their own job postings, similar to "Apply with LinkedIn". Turns PlacedOn into hiring infrastructure, not just a marketplace.

**Success fee for external hires** — if a company hires a candidate who came in via a shared link outside the PlacedOn matching flow, charge a placement fee. Detect this by tracking whether a company account engaged with a profile before a hire was recorded.

---

## The Real Risk to Watch

The actual threat is not candidates sharing profiles. It is companies receiving enough inbound shared profiles that they feel they do not need to pay for proactive matching — they will just wait for candidates to find them.

Protect against this by making **proactive matching** clearly more valuable than inbound shares:

- Shared profiles are **reactive** — the candidate has to choose to send them.
- PlacedOn matching is **proactive** — companies are surfaced candidates they would never have found otherwise.

Companies pay for discovery, not just verification. The shared profile proves the product works. The matching subscription is how they scale it.

---

## Summary

| What gets shared (free) | What stays on PlacedOn (account required) |
|---|---|
| Verification badge | Full scores and signals |
| Top 3 skill labels | Behavioral integrity data |
| Role + verification date | Contact details |
| One-line AI summary | Match percentage |
| Link to full profile | Application pipeline |

The shareable profile is not a substitute for the platform. It is proof-of-concept that drives companies to the platform. Every share is a lead.

---

## How The Shareable Profile Is Produced

The profile should not be a generic marketing page generated from a loose summary prompt.
It should be produced from the same structured interview state that powers matching and employer review.

### Internal source of truth

Every completed interview should yield:
- 16-dimension scores
- 4 bucket scores
- confidence levels
- evidence excerpts
- integrity/trust notes
- role-fit snapshot

This means the shareable profile is an **output view of the thinking model**, not a separate product.

### Public card generation rules

The public card should be generated from:
- the highest-confidence strengths
- the verified role category
- the verification date
- a single plain-language summary line

It should never expose:
- raw star values for all dimensions
- low-confidence judgments without context
- contradiction or integrity flags
- precise employer fit scores

The public profile must feel strong, but it must not leak the premium assessment layer.

---

## Recommended Public Card Structure

### Above the fold
- Candidate name
- Target role
- "Verified by PlacedOn" badge
- Date of last verified interview
- Short summary sentence

### Strength snapshot
- Top 3 strengths only
- Display as labeled badges, not full diagnostic scores

Examples:
- Strong ownership
- Clear technical communication
- Learns quickly

### Readiness panel
- Experience band
- Preferred work style
- Best-fit team environment

These are useful to employers while still being too shallow to replace the full platform.

### CTA block
- "View Full Verified Profile"
- "Request Second-Round Interview"
- "Hire Through PlacedOn"

The share link should always convert curiosity into platform actions.

---

## Recommended Full Company Profile Structure

Once a company account is created, the fuller profile should unlock in layers.

### Layer 1 — Quick scan
- overall rating
- bucket ratings
- confidence band
- fit summary

### Layer 2 — Diagnostic detail
- 16 dimensions with score + confidence
- strongest evidence quotes
- under-evidenced areas
- recommended second-round focus

### Layer 3 — Hiring workflow
- save / shortlist / reject
- request second-round AI interview
- request company-custom round
- candidate opt-in contact unlock

This lets the shareable link function as acquisition, while the account experience functions as the real product.

---

## Confidence and Freshness Rules

The shareable profile should visibly communicate:
- **freshness**: when the interview happened
- **confidence**: whether this is a strong verified profile or still developing

### Freshness recommendation
- public links expire after 90 days unless revalidated
- companies see freshness warnings for stale profiles

### Confidence recommendation
- public card only shows polished strengths above a confidence threshold
- low-confidence traits remain hidden from public view
- company accounts can see where uncertainty remains

This protects candidates from being unfairly defined by early or weak evidence.

---

## Candidate Trust Rules

The shareable profile only works if candidates feel it represents them fairly.

Recommended guardrails:
- candidate sees profile before sharing
- candidate can add short context note
- candidate can hide profile from public view
- candidate can revoke a share link
- candidate can request re-interview after a cooldown

This matters because the shareable profile is part credential, part identity surface.

---

## Revenue Protection Rules

The shareable profile should create leads, not leak value.

### Keep free
- verification badge
- public strengths snapshot
- one-line summary
- freshness signal

### Keep paid / gated
- full diagnostic report
- evidence ledger
- dimension breakdown
- fit decomposition
- second-round orchestration
- hiring workflow

The rule is simple:

**The public link should prove value.  
The company account should deliver value.**

---

## Strategic Role in the Product

The shareable profile is not just a candidate feature.
It plays four jobs at once:

1. candidate credential
2. employer acquisition channel
3. proof that PlacedOn assessments are tangible
4. bridge from interview intelligence to hiring workflow

That makes it one of the highest-leverage features in the product.
