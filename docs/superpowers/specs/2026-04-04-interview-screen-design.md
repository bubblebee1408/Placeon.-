# Interview Screen Design Spec

## Overview

Design specification for PlacedOn's video interview screen — the core candidate experience. Covers the pre-interview lobby and live interview screen. Post-interview profile review is out of scope for this spec.

**Primary audience:** Tech freshers (Indian market, first-time interviewees), with support for experienced candidates too.

**Interview format:** 30-40 minute AI video interview with integrated IDE and whiteboard for technical assessment.

---

## Screen 1: Pre-Interview Lobby

A separate page from the interview. Candidate must complete all checks and give consent before starting.

### Features

1. **Camera & Mic Check** — live video preview, mic level indicator, device switcher for multiple cameras/mics
2. **Screen Share Permission** — candidate must share their entire screen. Mandatory, not optional. Part of the anti-cheating layer.
3. **System Check** — browser compatibility, internet speed test. Flag if connection is too poor for video.
4. **Disclaimer & Consent** — what data is collected, where the profile goes, who sees it, data retention policy. Candidate must explicitly accept before proceeding.
5. **Accommodation Request** — "Do you need any accommodations?" with examples (more time between questions, etc.)
6. **What to Expect** — brief overview: ~30 min conversation, AI interviewer, no right/wrong answers, you'll see your profile at the end
7. **Role Confirmation** — confirm the role they're interviewing for. This initializes the Markov engine's initial state Q0.
8. **"Start Interview" button** — disabled until: consent given, camera working, mic working, screen sharing active, system checks pass.

---

## Screen 2: Live Interview

A separate page. Split layout: 75% main area (left) + 25% sidebar (right).

### 75% Main Area

Three swappable views accessed via tabs at the top of the main area: **Interview | IDE | Whiteboard**

#### Interview Tab (default)

- AI avatar — prominent, center of the area. This is the interviewer's visual presence.
- Candidate's video feed — smaller, positioned in the corner of the main area.
- Subtle phase indicator showing where the candidate is in the interview (Opening / Scenarios / Deep Dive / Close). Phase transitions are driven by the AI's dialogue, not hard UI breaks.

#### IDE Tab

- Full code editor replacing the AI avatar and candidate video
- **Pinned problem statement** at the top — when the AI gives a coding problem, it pins here and stays visible while the candidate codes. Does not scroll away.
- Language selector (Python, Java, JavaScript, C++ at minimum)
- Run/execute button with console output panel below the editor
- Line numbers, syntax highlighting, basic autocomplete

#### Whiteboard Tab

- Freehand drawing canvas replacing the AI avatar and candidate video
- **Pinned problem statement** at the top — same behavior as IDE, stays visible while candidate draws/diagrams
- Tools: pen, eraser, shapes (rectangles, circles, arrows), text input, color picker
- Controls: undo, redo, clear board

### 25% Sidebar (always visible)

The sidebar is the persistent anchor — it never changes regardless of which tab is active in the main area.

#### Top Section: Candidate Video

- Candidate's video feed moves here when IDE or whiteboard is open
- Hidden when in Interview tab (since the video is already in the main area)

#### Main Section: Live Chat Transcript

- Full verbatim transcript of everything the AI and candidate say
- Auto-scrolling to latest message
- AI messages and candidate messages visually distinct (different styling/colors)
- Scrollable — candidate can scroll up to re-read earlier parts of the conversation

#### Bottom Section: Controls

- **"Done Speaking" button** — large, prominent, the primary action. Candidate taps this when they've finished their thought. The AI does not respond until this is pressed.
- **Timer** — elapsed time / remaining time display

---

## Interview Controls & Behavior

### Mic & Audio

- **Mic is always on. No mute option.** This is intentional — prevents candidates from muting to seek external help.
- Candidate hears the AI through speakers/headphones
- Live mic indicator visible to the candidate (waveform or pulsing dot) so they know the mic is active
- If mic disconnects mid-interview, show a warning prompting them to reconnect

### Screen Sharing

- **Always on. Mandatory.** Candidate shares their entire screen for the duration of the interview.
- The AI/system monitors the shared screen in the background — nothing changes visually for the candidate.
- If screen sharing stops mid-interview, the interview pauses and prompts the candidate to re-enable it.
- Combined with always-on mic, this forms the anti-cheating layer.

### "Done Speaking" Flow

1. Candidate speaks freely while the AI listens silently
2. Candidate clicks "Done Speaking" when they've finished their thought
3. AI processes the response (Markov loop: contract -> judge -> bias check -> decompose -> generate question)
4. Thinking indicator appears while AI processes (e.g., avatar shows a thinking expression or subtle loading state)
5. AI responds with next question via voice + transcript updates simultaneously

### Interview Phases

- Phase 1 — Opening (~5 min): warm-up, open-ended questions
- Phase 2 — Situational Exploration (~15 min): 2-3 scenario-based questions
- Phase 3 — Deep Dive (~8 min): probing the area with strongest signal
- Phase 4 — Close (~2 min): warm wrap-up, explain next steps

Phase transitions happen naturally through the AI's dialogue. The phase indicator updates subtly — candidate doesn't click anything.

### Disconnect & Resume

- If candidate loses connection, Markov state is saved at the last contraction
- On reconnect, they land back on the interview screen and resume from where they left off
- AI acknowledges the disconnect: "Welcome back — let's pick up where we left off"

### Interview End

- AI delivers the warm close from Phase 4
- Interview auto-ends or candidate confirms
- Redirects to the post-interview page (separate spec)

---

## Anti-Cheating Measures Summary

| Measure | Purpose |
|---|---|
| Mic always on, no mute | Prevents verbal coaching or looking up answers |
| Screen sharing always on | Monitors if candidate opens external resources |
| Tap-to-send (not push-to-talk) | Candidate can't mute between presses to get help |
| Screen share pause = interview pause | Enforces continuous monitoring |

---

## Out of Scope (for this spec)

- Post-interview profile review screen (separate spec)
- Text-based response fallback (future accessibility feature)
- Voice interview without video (future)
- Mobile interview experience (future)
