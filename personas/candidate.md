# Candidate Persona

## Who They Are

Primary target: Indian tech freshers (1.5M graduate annually). No significant work experience to draw from. Looking for their first or early-career job. May also include experienced professionals pivoting roles or updating their assessed skill set.

---

## Core Experience Flow

### Before the Interview
- **Role selection** — candidate picks a specific role to be assessed for (e.g., Backend Engineer, Data Engineer). The interview engine tailors questions to that role.
- Role browser available so candidates can see what roles exist and what skills each assesses before committing.

### During the Interview
- Text-based chat interface (voice in Phase 2)
- Candidate sees a **progress indicator** showing percentage of interview remaining
- No real-time feedback on performance — clean conversational experience
- ~30 minute interview broken into ~5-minute segments, each running through the Markov engine loop

### After the Interview
- **1-minute generation delay** — "Your profile is being generated" screen, then notification when ready
- Candidate sees their full AI-generated inference: skills assessed, observations, atomic traits, confidence levels
- **No disputes or edits** — the inference is final for that interview. Any changes require a retake.

---

## Profile Structure

### Public Tier (visible to all employers browsing)
- Professional summary (AI-generated)
- Top 3 strengths with confidence
- Verified achievements and certifications
- Education details
- Skills (AI-inferred from interviews)

### Detailed Tier (revealed only when candidate applies to or matches with a specific company)
- Full AI inference across all assessed skills
- Evidence behind each skill assessment
- Growth trajectory across multiple interviews
- Uncertainty levels per skill
- Weak areas and gaps

---

## Core Features

### AI-Inferred Profile
- Generated entirely from the Markov interview engine output
- Candidate does not write their own skills or summary — the AI does
- Candidate validates but cannot edit the inference

### Achievements & Certifications (Hybrid Verification)
- Candidates self-post achievements, certifications, and education
- All self-posted items are flagged as **"unverified"** by default
- During subsequent interviews, the AI probes relevant claims ("You listed AWS certification — walk me through a time you used VPC networking")
- Once probed and validated through interview, items are marked as **"verified through interview"**
- Employers can see verification status

### Education & Skills
- Education details are self-entered
- Skills are AI-inferred from interviews, not self-reported
- Skills displayed as tags/pills on the profile

### Interview Retake
Candidates can retake interviews for any reason:
- **Skill growth** — learned something new, want profile updated
- **Bad day recovery** — underperformed, want a fresh assessment
- **Role pivot** — assessed for Backend Engineer, now want Data Engineer profile
- **General update** — keep profile current

The system tracks **trajectory over time**, not just the latest score. Employers see growth curves in the detailed tier (e.g., "weak in system design in March, strong signal by June").

Cooldown period between retakes (duration TBD).

### Offers & Applications
- Section showing all active applications and their status
- Section showing offers/interest received from companies
- Saved/bookmarked jobs (TBD — discussed but not confirmed as core)

### Interview History
- Timeline of all past interviews
- Profile generated from each interview visible
- Growth trajectory visualized here

---

## Matching & Discovery

- **Active matching** — system surfaces candidates to companies AND notifies candidates ("3 companies are interested in your profile")
- **Two-way opt-in** — no contact happens until both sides express interest
- Match alerts pull candidates back into the platform

---

## What Candidates Cannot Do

- Edit or dispute AI inference (must retake interview instead)
- Hide skills or observations from the detailed tier (tiered visibility controls what's shown when, not what exists)
- Self-report skills (all skills come from AI assessment)
- Contact companies directly without mutual match/application
