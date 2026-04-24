#!/usr/bin/env python3
"""
PlacedOn — Realistic Backend Intern Interview Simulation
The AI acts as a REAL candidate — sometimes strong, sometimes weak, sometimes lost.
Interviewer judges candidate on backend engineering skills for an intern opening.
"""
import sys, time, random

class C:
    BOLD="\033[1m"; DIM="\033[2m"; RED="\033[91m"; GREEN="\033[92m"
    YELLOW="\033[93m"; BLUE="\033[94m"; MAGENTA="\033[95m"; CYAN="\033[96m"
    WHITE="\033[97m"; GRAY="\033[90m"; RESET="\033[0m"

def typ(text, spd=0.012, col=""):
    for ch in text:
        sys.stdout.write(f"{col}{ch}{C.RESET}"); sys.stdout.flush()
        if ch in ".!?": time.sleep(spd*6)
        elif ch == ",": time.sleep(spd*3)
        elif ch == "\n": time.sleep(spd*2)
        else: time.sleep(spd + random.uniform(-0.004, 0.004))
    print()

def banner(t, col=C.CYAN):
    b = "═"*66
    print(f"\n{col}{C.BOLD}╔{b}╗\n║{t.center(66)}║\n╚{b}╝{C.RESET}\n")

def section(t):
    print(f"\n{C.YELLOW}{C.BOLD}{'─'*60}\n  {t}\n{'─'*60}{C.RESET}\n")

def interviewer(t):
    print(f"{C.BLUE}{C.BOLD}🎙  INTERVIEWER:{C.RESET}")
    typ(f"   {t}", spd=0.008, col=C.BLUE); print()

def candidate(t, mood="normal"):
    print(f"{C.GREEN}{C.BOLD}👤 CANDIDATE:{C.RESET}")
    if mood == "nervous":
        sys.stdout.write(f"   {C.DIM}(hesitating...){C.RESET}"); sys.stdout.flush()
        time.sleep(random.uniform(2.0, 3.0))
    elif mood == "confident":
        sys.stdout.write(f"   {C.DIM}(nods){C.RESET}"); sys.stdout.flush()
        time.sleep(random.uniform(0.5, 0.8))
    elif mood == "stuck":
        sys.stdout.write(f"   {C.DIM}(long pause...){C.RESET}"); sys.stdout.flush()
        time.sleep(random.uniform(3.0, 4.0))
    else:
        sys.stdout.write(f"   {C.DIM}(thinking...){C.RESET}"); sys.stdout.flush()
        time.sleep(random.uniform(1.0, 1.5))
    sys.stdout.write("\r" + " "*40 + "\r")
    col = C.GREEN if mood in ["confident","normal"] else C.YELLOW if mood=="nervous" else C.RED
    typ(f"   {t}", spd=0.010, col=col); print()

def judge_note(verdict, reason, score):
    colors = {"correct": C.GREEN, "partial": C.YELLOW, "wrong": C.RED}
    icons = {"correct": "✅", "partial": "⚠️ ", "wrong": "❌"}
    c = colors.get(verdict, C.GRAY)
    filled = int(score * 20); empty = 20 - filled
    bar = f"{c}{'█'*filled}{C.GRAY}{'░'*empty}{C.RESET}"
    print(f"   {C.MAGENTA}── AI Judge Evaluation ──{C.RESET}")
    print(f"   {icons[verdict]} Verdict: {c}{C.BOLD}{verdict.upper()}{C.RESET}")
    print(f"   {bar} {score:.1f}")
    print(f"   {C.DIM}{reason}{C.RESET}")
    print(f"\n{C.GRAY}   {'·'*45}{C.RESET}\n")

def pause(s=1.0): time.sleep(s)

# ═══════════════════════════════════════════════════
# THE INTERVIEW
# ═══════════════════════════════════════════════════

def run():
    banner("BACKEND INTERN — LIVE INTERVIEW")
    print(f"""{C.CYAN}  ┌───────────────────────────────────────────────────┐
  │  Company:    TechNova Solutions                    │
  │  Role:       Backend Engineering Intern            │
  │  Candidate:  Arjun M. (Final Year CSE)             │
  │  Duration:   ~30 min (accelerated to ~6 min)       │
  │  Stack:      Python, FastAPI, PostgreSQL, Redis    │
  └───────────────────────────────────────────────────┘{C.RESET}
""")
    for i in [3,2,1]:
        print(f"  {C.DIM}Starting in {i}...{C.RESET}", end="\r", flush=True); time.sleep(1)
    print(" "*30)

    scores = []

    # ── WARMUP ──
    section("ROUND 1 — Warmup & Background")

    interviewer("Hey Arjun, thanks for joining! Tell me a bit about yourself and what you've been working on.")
    candidate(
        "Hi! Thanks for having me. I'm Arjun, final year CSE at VIT Vellore. "
        "I've mostly been into backend development — I did an internship last summer where I worked "
        "on REST APIs using Flask. I also built a small project with FastAPI and PostgreSQL for my "
        "college fest — it was a ticketing system. I'm pretty comfortable with Python and SQL, and "
        "I've been trying to learn Redis and Docker on the side, though I wouldn't say I'm expert level there.",
        mood="confident"
    )
    judge_note("correct", "Honest self-assessment. Mentions relevant stack. Good communication.", 0.8)
    scores.append(0.8)

    # ── REST APIs — STRONG ──
    section("ROUND 2 — REST API Design")

    interviewer("Great. So if I asked you to design a REST API for a simple to-do app — what endpoints would you create?")
    candidate(
        "Okay so... for a basic to-do app, I'd have:\n"
        "   GET /todos — list all to-dos, maybe with pagination like ?page=1&limit=10\n"
        "   POST /todos — create a new to-do, body would have title, description, status\n"
        "   GET /todos/{id} — get a specific to-do\n"
        "   PUT /todos/{id} — update the whole to-do\n"
        "   PATCH /todos/{id} — partial update, like just changing status to done\n"
        "   DELETE /todos/{id} — delete a to-do\n\n"
        "I'd use proper HTTP status codes — 201 for created, 404 if not found, 422 for validation errors. "
        "And I'd probably add a /todos/{id}/subtasks endpoint if we need nested resources.",
        mood="confident"
    )
    judge_note("correct", "Comprehensive REST design. Knows HTTP verbs, status codes, pagination. Mentioned nested resources.", 0.9)
    scores.append(0.9)

    interviewer("Nice. What's the difference between PUT and PATCH? A lot of people mix those up.")
    candidate(
        "Yeah so PUT replaces the entire resource — if you PUT a to-do, you need to send ALL fields, "
        "even the ones you're not changing. If you leave something out, it gets set to null or default. "
        "PATCH is a partial update — you only send the fields you want to change. Like if I just want "
        "to mark a to-do as done, I'd PATCH with just {\"status\": \"done\"} instead of resending everything.",
        mood="confident"
    )
    judge_note("correct", "Clear and accurate distinction with practical example.", 0.85)
    scores.append(0.85)

    # ── DATABASES — PARTIAL ──
    section("ROUND 3 — Database Design")

    interviewer("Let's talk databases. How would you design the schema for this to-do app? What tables and columns?")
    candidate(
        "I'd have a users table with id, email, password_hash, created_at. Then a todos table with "
        "id, user_id as a foreign key, title, description, status — probably an enum like 'pending', "
        "'in_progress', 'done'. And created_at, updated_at timestamps.\n\n"
        "If we're doing subtasks, a subtasks table with id, todo_id as foreign key, title, is_completed. "
        "I'd add indexes on user_id in the todos table since we'll query by user a lot.",
        mood="normal"
    )
    judge_note("correct", "Solid schema. Mentioned foreign keys, enums, timestamps, and indexing.", 0.85)
    scores.append(0.85)

    interviewer("Good. Now tell me — what's the difference between a SQL and NoSQL database? When would you pick one over the other?")
    candidate(
        "SQL databases like PostgreSQL are relational — structured tables, strict schemas, ACID transactions. "
        "Good when you have structured data and need consistency, like financial stuff or user accounts.\n\n"
        "NoSQL like MongoDB is more flexible — schema-less documents, easier to scale horizontally. Good for "
        "things like logs, user activity feeds, or when your data shape changes a lot.\n\n"
        "Honestly though... I've mostly used PostgreSQL, so I might be biased. I know there's also stuff "
        "like Redis which is a key-value store, and Cassandra for write-heavy workloads, but I haven't "
        "used those in production myself.",
        mood="normal"
    )
    judge_note("partial", "Decent overview but surface-level. Honest about limited NoSQL experience. Didn't mention CAP theorem.", 0.6)
    scores.append(0.6)

    # ── SYSTEM DESIGN — WEAK ──
    section("ROUND 4 — System Design Thinking")

    interviewer("Okay, here's a tougher one. Let's say your to-do API starts getting 10,000 requests per second. How would you scale it?")
    candidate(
        "Umm... okay. So first I'd probably put a load balancer in front, like Nginx, to distribute "
        "traffic across multiple server instances. And I'd add caching — maybe Redis — for the GET "
        "endpoints so we don't hit the database every time someone fetches their to-do list.\n\n"
        "Hmm... for the database, maybe read replicas? So writes go to the primary and reads go to "
        "replicas. And... I think there's something about connection pooling that helps too?\n\n"
        "I'm not super confident on the specifics of database sharding or message queues though. "
        "I've read about them but haven't implemented anything at that scale.",
        mood="nervous"
    )
    judge_note("partial", "Got the basics: load balancer, caching, read replicas. But vague on specifics. Honest about gaps.", 0.55)
    scores.append(0.55)

    interviewer("That's a fair start. What about rate limiting? If one user is hammering your API, how would you handle that?")
    candidate(
        "Oh right, rate limiting! So... I'd probably use something like a middleware that tracks "
        "requests per user or IP. Like, allow 100 requests per minute per user, and return a 429 "
        "Too Many Requests if they exceed it.\n\n"
        "I think you can do this with Redis — store a counter with the user ID as the key and set "
        "a TTL of 60 seconds. Each request increments the counter. If it hits the limit, block.\n\n"
        "There's also... I think it's called a token bucket algorithm? But I don't remember exactly "
        "how it works. Something about tokens being added at a fixed rate and each request consuming one.",
        mood="nervous"
    )
    judge_note("partial", "Knows the concept and Redis approach. Mentioned token bucket but couldn't explain it fully.", 0.6)
    scores.append(0.6)

    # ── AUTHENTICATION — BLANK MOMENT ──
    section("ROUND 5 — Authentication & Security")

    interviewer("How does JWT authentication work? Walk me through the flow.")
    candidate(
        "So JWT is JSON Web Token. The flow is... user logs in with email and password, the server "
        "verifies the credentials, and if they're valid, it creates a JWT token that contains the user's "
        "ID and maybe their role. The token is signed with a secret key so it can't be tampered with.\n\n"
        "The client stores the token — usually in localStorage or a cookie — and sends it in the "
        "Authorization header as Bearer <token> with every request. The server decodes it and verifies "
        "the signature to authenticate the user.\n\n"
        "The token has three parts separated by dots — header, payload, signature. The header says "
        "the algorithm, payload has the claims like user_id and expiry, and signature is the HMAC.",
        mood="confident"
    )
    judge_note("correct", "Accurate JWT flow. Knows the three-part structure, Bearer header, and signing.", 0.85)
    scores.append(0.85)

    interviewer("Good. Now — what's the difference between authentication and authorization? And how would you implement role-based access control?")
    candidate(
        "Authentication is verifying WHO you are — like logging in. Authorization is verifying WHAT "
        "you're allowed to do — like can this user delete other users' posts.\n\n"
        "For RBAC, I'd add a role field to the user model — like 'admin', 'user', 'moderator'. Then "
        "in my API endpoints, I'd check the role from the JWT before allowing certain actions. Like "
        "DELETE /users/{id} would require role == 'admin'.\n\n"
        "In FastAPI, I think you can do this with dependency injection — create a function that checks "
        "the role and use it as a Depends() parameter. Something like... get_current_admin_user.",
        mood="normal"
    )
    judge_note("correct", "Clean distinction. Knows FastAPI dependency injection pattern for RBAC.", 0.8)
    scores.append(0.8)

    # ── CONCURRENCY — STRUGGLE ──
    section("ROUND 6 — Concurrency & Async")

    interviewer("You mentioned FastAPI. Can you explain what async/await does in Python and why FastAPI uses it?")
    candidate(
        "Yeah so... async/await is for asynchronous programming. Instead of blocking the thread while "
        "waiting for something like a database query or API call, the function yields control and lets "
        "other tasks run. When the I/O operation completes, it picks up where it left off.\n\n"
        "FastAPI uses it because web servers handle many concurrent requests. If each request blocks "
        "waiting for a DB query, you need lots of threads. With async, a single event loop can handle "
        "thousands of concurrent requests because while one is waiting for I/O, others can run.\n\n"
        "It uses asyncio under the hood... and I think Uvicorn as the ASGI server.",
        mood="normal"
    )
    judge_note("correct", "Good understanding of async I/O and why it matters for web servers.", 0.8)
    scores.append(0.8)

    interviewer("What's a race condition? Can you give me an example in a web application?")
    candidate(
        "A race condition is when two things try to access or modify the same resource at the same "
        "time and the result depends on timing. Like...\n\n"
        "Hmm, okay let me think of a real example. Say you have an e-commerce site and a product has "
        "stock = 1. Two users click 'buy' at the exact same time. Both read stock = 1, both think "
        "it's available, both place the order. Now you've sold 2 items when you only had 1.\n\n"
        "To fix it you'd use... I think database locks? Like SELECT FOR UPDATE in PostgreSQL. Or "
        "maybe optimistic locking with a version counter. I'm a bit fuzzy on the exact implementation "
        "though.",
        mood="nervous"
    )
    judge_note("partial", "Good example. Mentioned locking approaches but uncertain on implementation details.", 0.65)
    scores.append(0.65)

    # ── DOCKER/DEVOPS — TOTAL BLANK ──
    section("ROUND 7 — DevOps & Deployment")

    interviewer("Have you worked with Docker? Can you explain what a Dockerfile does and write a basic one for a FastAPI app?")
    candidate(
        "I've used Docker a little — like pulling images and running containers with docker-compose. "
        "I know a Dockerfile is like... the recipe for building an image.\n\n"
        "A basic one would be something like...\n"
        "   FROM python:3.11\n"
        "   WORKDIR /app\n"
        "   COPY requirements.txt .\n"
        "   RUN pip install -r requirements.txt\n"
        "   COPY . .\n"
        "   CMD uvicorn main:app --host 0.0.0.0 --port 8000\n\n"
        "I think there's also something about multi-stage builds to make the image smaller, but I "
        "haven't done that myself.",
        mood="nervous"
    )
    judge_note("partial", "Basic Dockerfile is correct. Knows the concept but limited hands-on experience.", 0.6)
    scores.append(0.6)

    interviewer("What about CI/CD? If I asked you to set up a GitHub Actions pipeline for this project, what steps would it have?")
    candidate(
        "Oh... CI/CD. So I know the concept — continuous integration means automatically running tests "
        "when you push code, and continuous deployment means automatically deploying if tests pass.\n\n"
        "For GitHub Actions... honestly, I've seen YAML files for it but I've never written one from "
        "scratch. I think you create a .github/workflows folder with a YAML file that specifies "
        "triggers, like on push to main. Then steps like checkout, install dependencies, run pytest...\n\n"
        "But I'd be lying if I said I could write that confidently right now. It's on my list to learn.",
        mood="stuck"
    )
    judge_note("wrong", "Knows CI/CD concept but cannot implement. Honest about the gap — that's good character.", 0.3)
    scores.append(0.3)

    # ── CODING QUESTION — MIXED ──
    section("ROUND 8 — Live Coding")

    interviewer("Last one. Write me a Python function that takes a list of integers and returns the two numbers that add up to a target sum. Classic two-sum.")
    candidate(
        "Okay, two-sum! I know this one.\n\n"
        "   def two_sum(nums, target):\n"
        "       seen = {}\n"
        "       for i, num in enumerate(nums):\n"
        "           complement = target - num\n"
        "           if complement in seen:\n"
        "               return [seen[complement], i]\n"
        "           seen[num] = i\n"
        "       return []\n\n"
        "So we use a hash map — for each number, we check if its complement (target minus current) "
        "has already been seen. If yes, return both indices. If not, store the current number. "
        "Time complexity is O(n), space is O(n) for the dictionary.",
        mood="confident"
    )
    judge_note("correct", "Clean O(n) solution with hash map. Correctly analyzed time and space complexity.", 0.95)
    scores.append(0.95)

    interviewer("Nice. Now, what if I wanted the pair with the SMALLEST absolute difference from the target, not exact match?")
    candidate(
        "Oh... hmm. That's different. So instead of exact match we want the closest sum.\n\n"
        "I think... I'd sort the array first, then use two pointers? One at the start, one at the end. "
        "Calculate the sum, track the closest pair. If the sum is too small, move left pointer right. "
        "If too big, move right pointer left.\n\n"
        "Wait, but that loses the original indices because of sorting... I'd need to store the original "
        "indices somehow. Maybe sort tuples of (value, original_index)?\n\n"
        "The time complexity would be O(n log n) for the sort plus O(n) for the two-pointer pass. "
        "I think that's the best you can do for this variant? I'm not 100% sure though.",
        mood="nervous"
    )
    judge_note("partial", "Right approach with two pointers. Identified the index-tracking issue. Slightly uncertain but solid reasoning.", 0.7)
    scores.append(0.7)

    # ═══════════════════════════════════════════════
    # FINAL REPORT
    # ═══════════════════════════════════════════════
    banner("INTERVIEW COMPLETE — FINAL EVALUATION")

    avg = sum(scores) / len(scores)

    sections_data = [
        ("Warmup & Background",       [scores[0]]),
        ("REST API Design",           [scores[1], scores[2]]),
        ("Database Design",           [scores[3], scores[4]]),
        ("System Design",             [scores[5], scores[6]]),
        ("Auth & Security",           [scores[7], scores[8]]),
        ("Concurrency & Async",       [scores[9], scores[10]]),
        ("DevOps & Deployment",       [scores[11], scores[12]]),
        ("Live Coding",               [scores[13], scores[14]]),
    ]

    print(f"{C.BOLD}{C.WHITE}  ┌────────────────────────────────────────────────────────────┐")
    print(f"  │                       SCORECARD                           │")
    print(f"  ├────────────────────────────────────────────────────────────┤{C.RESET}")

    for name, sc in sections_data:
        s = sum(sc)/len(sc)
        emoji = "🟢" if s >= 0.75 else "🟡" if s >= 0.5 else "🔴"
        filled = int(s * 20)
        bar = f"{C.GREEN if s>=0.75 else C.YELLOW if s>=0.5 else C.RED}{'█'*filled}{C.GRAY}{'░'*(20-filled)}{C.RESET}"
        pct = f"{s*100:.0f}%"
        print(f"  │  {emoji} {name:<30} {bar} {pct:>4}  │")

    print(f"  ├────────────────────────────────────────────────────────────┤")
    print(f"  │  {C.BOLD}OVERALL:{C.RESET} {avg*100:.0f}%                                            │")
    print(f"  └────────────────────────────────────────────────────────────┘")

    # Strengths
    print(f"\n{C.GREEN}{C.BOLD}  ✅ STRENGTHS{C.RESET}")
    for s in [
        "Strong REST API fundamentals — knows verbs, status codes, resource design",
        "Clean coding — two-sum in O(n) without hesitation",
        "Good JWT understanding and FastAPI-specific patterns (Depends)",
        "Honest about what he doesn't know — never bluffed",
        "Solid async/await conceptual understanding",
    ]:
        typ(f"   • {s}", spd=0.004, col=C.GREEN); time.sleep(0.05)

    # Weaknesses
    print(f"\n{C.RED}{C.BOLD}  ⚠️  GAPS{C.RESET}")
    for w in [
        "System design at scale — vague on sharding, message queues, specifics",
        "CI/CD and DevOps — concept-level only, can't implement",
        "Race conditions — knows the problem but not confident on solutions",
        "NoSQL — surface-level, hasn't used in real projects",
    ]:
        typ(f"   • {w}", spd=0.004, col=C.RED); time.sleep(0.05)

    # Behavioral
    print(f"\n{C.CYAN}{C.BOLD}  🧠 BEHAVIORAL NOTES{C.RESET}")
    for b in [
        "Self-aware: explicitly said 'I'd be lying if I said I could do that'",
        "Growth mindset: 'It's on my list to learn'",
        "Thinks out loud: showed problem-solving process on harder questions",
        "No bluffing: said 'I'm not sure' when uncertain instead of faking it",
    ]:
        typ(f"   • {b}", spd=0.004, col=C.CYAN); time.sleep(0.05)

    # Verdict
    if avg >= 0.75:
        v, vc, ve = "HIRE — Strong for intern level", C.GREEN, "🚀"
    elif avg >= 0.6:
        v, vc, ve = "HIRE — With mentorship plan", C.YELLOW, "✅"
    elif avg >= 0.45:
        v, vc, ve = "BORDERLINE — Consider take-home", C.YELLOW, "🔄"
    else:
        v, vc, ve = "PASS — Not ready yet", C.RED, "❌"

    print(f"""
{vc}{C.BOLD}  ╔══════════════════════════════════════════════════╗
  ║                                                  ║
  ║   {ve}  {v:<45}║
  ║                                                  ║
  ╚══════════════════════════════════════════════════╝{C.RESET}
""")

    typ(
        "  Arjun shows strong fundamentals in API design, authentication, and\n"
        "  coding. His gaps in DevOps and system design are expected for an\n"
        "  intern. What stands out is his honesty — he never bluffed and showed\n"
        "  genuine problem-solving instinct on unfamiliar questions. With 3-6\n"
        "  months of mentorship, he'd likely grow into a solid junior engineer.",
        spd=0.005, col=C.CYAN
    )

    print(f"\n{C.DIM}  ─── Interview simulation complete ───{C.RESET}\n")

    # Save report
    save_report(scores, avg, sections_data)

def save_report(scores, avg, sections_data):
    import os
    report_dir = os.path.join(os.path.dirname(__file__), "reports")
    os.makedirs(report_dir, exist_ok=True)
    path = os.path.join(report_dir, "backend_intern_interview_report.md")

    with open(path, "w") as f:
        f.write("# Backend Intern Interview — Simulation Report\n\n")
        f.write("**Company:** TechNova Solutions\n")
        f.write("**Role:** Backend Engineering Intern\n")
        f.write("**Candidate:** Arjun M. (Final Year CSE, VIT Vellore)\n")
        f.write(f"**Overall Score:** {avg*100:.0f}%\n")
        v = "HIRE" if avg >= 0.6 else "BORDERLINE"
        f.write(f"**Verdict:** {v}\n\n---\n\n## Scores by Section\n\n")
        f.write("| Section | Score |\n|---|---|\n")
        for name, sc in sections_data:
            s = sum(sc)/len(sc)
            f.write(f"| {name} | {s*100:.0f}% |\n")
        f.write(f"| **Overall** | **{avg*100:.0f}%** |\n")
        f.write("\n---\n\n*Auto-generated from PlacedOn live interview simulation.*\n")

    print(f"{C.DIM}  📄 Report saved: {path}{C.RESET}\n")

if __name__ == "__main__":
    try:
        run()
    except KeyboardInterrupt:
        print(f"\n\n{C.YELLOW}  Interview ended early.{C.RESET}\n")
