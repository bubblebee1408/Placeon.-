# PlacedOn

An AI-powered interviewer that replaces the resume as the primary signal for hiring decisions.

## Layout

- `PlacedOn/` contains runtime code and implementation modules
- `PlacedOn-Research/` contains product, business, research, and inspiration material

## What This Solves

Resumes are a poor judge of character. Soft skills — how someone thinks, communicates, handles ambiguity, collaborates — are often more important than credentials but invisible on paper. PlacedOn conducts a 30-40 minute adaptive AI interview when a candidate onboards, building a rich behavioral profile that captures what resumes cannot.

## How It Works

1. **Candidate signs up** and enters a conversational AI interview (~30-40 min)
2. **AI adaptively assesses** technical depth, soft skills, thinking patterns, and character traits
3. **Atomic trait profile** is generated — specific, evidence-grounded, actionable insights
4. **Employers search profiles** to find candidates who match their needs beyond keywords
5. **Better matches** lead to better hires, lower turnover, reduced hiring costs

## Core Technology

Built on **Markovian Reasoning** (from the Atom of Thoughts framework, NeurIPS 2025):

- **Markov State Management** — maintains a compressed candidate understanding instead of full transcript history, enabling cost-efficient 40-minute conversations
- **DAG Decomposition** — dynamically identifies what to assess next based on dependencies between assessment goals
- **Contraction** — progressively refines candidate understanding into atomic, irreducible behavioral traits
- **Judge Verification** — ensures the AI's model of the candidate stays faithful to what was actually said
- **ABLEIST Bias Protection** — integrated bias detection across disability, gender, nationality, and caste dimensions

## Value Proposition

| For Candidates | For Employers |
|---|---|
| Interview once, apply everywhere | See who candidates actually are, not just their credentials |
| Showcase soft skills that resumes can't capture | Reduce cost-per-hire from $4,700 to <$500 |
| Fair assessment with built-in bias protection | Regulatory compliance (NYC LL144, EU AI Act) baked in |
| No more tailoring 20 resumes | Lower turnover from better matches |

## Project Structure

```
PlacedOn/
├── README.md
├── PlacedOn/                  ← implementation code
│   ├── backend/
│   ├── interaction_layer/
│   ├── interview_system/
│   ├── aot_layer/
│   ├── layer2/
│   ├── layer3/
│   ├── layer5/
│   ├── tests/
│   └── training/
└── PlacedOn-Research/         ← product, research, business, docs, inspiration
    ├── product/
    ├── business/
    ├── research/
    ├── Markovian-Reasoning/
    ├── docs/
    └── Inspo/
```

## Key Numbers

- Cost per AI interview: **$0.03** (with Markovian approach)
- Gross margin: **>90%**
- Target break-even: **~12 months, ~25 paying companies**
- Year 2 revenue (moderate): **$600K**
- Market size (AI recruitment tools): **$3.1B and growing**
