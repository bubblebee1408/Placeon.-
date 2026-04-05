# Company / Employer Persona

## Who They Are

Primary target: Indian tech startups (initial pilot phase: 5-10 free, then $299/month). Scaling to mid-size companies. Hiring managers and HR teams screening high volumes of fresher and early-career candidates. Typically evaluating 20-50+ candidates per open role.

---

## Core Experience Flow

### Creating a Job Posting (Guided Hybrid)
1. Company writes a **natural language job description** — title, responsibilities, salary, location, experience level, etc.
2. The AI parses the description and presents structured requirements: "Here's what I understood — Backend Engineer needing problem_solving (high), system design (medium), collaboration (medium). Adjust if needed."
3. Company confirms or tweaks the AI's interpretation
4. Posting goes live with both the human-written description and the structured skill requirements powering the matching engine

### Viewing Candidates

#### Candidate Card (Default Screening View)
Based on the wireframe design:

```
+--------------------------------------------------+
|  [Profile Pic]   Name                            |
|                  Fit Score (stars, contextual)    |
|                  Country, Location                |
|                  Experience                       |
|                                                   |
|  [skill tag] [skill tag] [skill tag]             |
|      ^ hover: popup with AI summary of the       |
|        interview moment that evidenced this skill |
|                                                   |
|  Summary                                          |
|  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~     |
|  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~     |
|  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~                     |
|                                    see more       |
|                                                   |
|  [ View Profile ]                                 |
+--------------------------------------------------+
```

**Key elements:**
- **Fit score** — contextual to the specific job posting. Same candidate may score differently across different roles. Displayed as star rating.
- **Skills as hoverable tags** — on hover, a popup shows an **AI-generated summary** of the interview moment that evidenced that skill. Not a direct quote — a structured paraphrase for consistency.
- **Summary** — AI-generated professional summary, truncated with "see more"
- **View Profile** — navigates to the full detailed profile

#### Expanded View (One Click from Card)
- Full interview highlights with evidence per skill
- All assessed skills with scores
- Growth trajectory ("improved in system design over 3 interviews")
- Comparison against the applicant pool ("top 15% in problem solving for this role")
- Uncertainty levels per skill
- Verified vs. unverified achievements

#### Comparison Mode
- Select 2-3 candidates side by side
- Skills, scores, uncertainty, and evidence shown in parallel
- Useful for final-stage decision making

---

## Core Features

### Job Posting Management
- Create, edit, deactivate, and manage multiple job postings
- Each posting has: title, description, salary, location, experience level, AI-parsed skill requirements
- Guided hybrid input — AI structures the requirements, company validates

### Candidate Discovery (Two Channels)

**1. Applications** — candidates who applied to the posting
- Shown as candidate cards ranked by fit score
- All applicants visible in the detailed tier (full AI inference)

**2. Recommended Matches** — candidates who haven't applied but whose profiles align
- System auto-surfaces high-fit candidates
- Company sends interest → candidate is notified → two-way opt-in before any contact
- Active matching, not passive browsing

### Candidate Evaluation

**Skill hover interaction:**
- Skills displayed as tags on every candidate card
- Hover reveals an AI-summarized interview moment evidencing that skill
- Fast to scan — HR can evaluate evidence quality in seconds without opening the full profile

**Fit score:**
- Star rating contextual to the job posting
- Powered by cosine similarity between candidate embedding and role vector (with optional employer preference blending at 70/30)
- Qualitative interpretation: low / medium / high alignment

---

## Features Discussed but Not Yet Confirmed as Core

These were raised during brainstorming and flagged for later decision:

### Applicant Pipeline Stages
- Moving candidates through stages: Reviewed → Shortlisted → Interviewing → Offered → Rejected
- Kanban or list view
- **Status:** Likely core, but structure not finalized

### Team Access
- Multiple users from the same company (HR shortlists, tech lead reviews detailed profiles)
- Commenting on candidates internally
- **Status:** Important for mid-size+ companies, may be Phase 2

### Posting Analytics
- Views, application count, average fit score of applicants
- Helps companies calibrate: are requirements too narrow or too broad?
- **Status:** Useful but not blocking MVP

### Notifications
- New candidate alerts, pipeline health reminders, comparative insights
- **Status:** Deferred — to be designed separately

---

## What Companies Cannot Do

- View a candidate's detailed tier without the candidate applying or matching (tiered visibility protects candidates)
- Message candidates without two-way opt-in
- See raw interview transcripts (only AI summaries and structured inference)
- Override or edit AI-generated candidate assessments
