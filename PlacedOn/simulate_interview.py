import asyncio
import json

from aot_layer.config import AoTConfig
from aot_layer.models import StartInput
from aot_layer.orchestrator import AoTOrchestrator
from layer2.embedding import embed_text
from layer3.bias_classifier import BiasEnforcer
from layer5.aggregator import AggregationEngine
from layer5.models import CandidateState, InterviewTurn, SkillTurnSignal

# Mock Candidate and Config
# We will simulate a mid-level backend engineer interview
SKILLS = ["caching", "concurrency", "api_design", "system_design"]

class InterviewSimulator:
    def __init__(self):
        self.orchestrator = AoTOrchestrator(config=AoTConfig(skills=SKILLS, total_turn_limit=8, max_retries_per_skill=1))
        self.bias_enforcer = BiasEnforcer()
        self.aggregator = AggregationEngine()
        
    async def run_simulation(self):
        print("=== STAGE 1: Generating Starting State ===")
        # Initialize CandidateState
        candidate = CandidateState(
            candidate_id="sim_user_1",
            embedding=[0.0] * 384,
            skills={}
        )
        
        # Initial Vectors
        start = StartInput(
            skill_vector=[0.5] * len(SKILLS),
            sigma2=[0.95] * len(SKILLS),
            past_attempts_per_skill={s: 0 for s in SKILLS},
        )
        
        print(f"Skills targeted: {SKILLS}")
        
        async def mock_answer_provider(turn: int, question: str, skill: str, mode: str) -> str:
            print(f"\n[Turn {turn}] Skill: {skill} | Mode: {mode}")
            print(f"-> Question: {question}")
            
            # Use BiasEnforcer to ensure the question is safe
            try:
                assessment = await self.bias_enforcer.assess(question)
                if not assessment.approved:
                    print(f"   [!] BIAS DETECTED! Score: {assessment.bias_score}")
                else:
                    print(f"   [+] Question passed bias check (Score: {assessment.bias_score}).")
            except Exception as e:
                print(f"   [!] Failed bias check execution: {e}")

            # Define behaviors
            answers = {
                "caching": "I love using Redis! Usually, I set a TTL mechanism and write-through cache to avoid database hit latency. The biggest tradeoff is memory eviction when caching keys.",
                "concurrency": "I run processes in parallel.",
                "api_design": "I usually use REST with standard HTTP verbs and JSON payloads. I also add versioning in the headers to prevent breaking clients.",
                "system_design": "I just put everything in a single monolith because microservices are complicated."
            }
            
            # Evolve answers based on mode (probe means the AI asked a follow-up)
            ans = answers.get(skill, "I am not sure how to answer that.")
            if mode == "probe" and skill == "concurrency":
                ans = "Oh, you mean handling race conditions? I lock the database row and use message queues like RabbitMQ to decouple the process."
                
            print(f"<- Answer:   {ans}")
            return ans

        print("\n=== STAGE 2: AoT Orchestrator Trajectory ===")
        # Run orchestrator
        result = await self.orchestrator.run(start_input=start, answer_provider=mock_answer_provider, max_turns=8)
        
        print("\n=== STAGE 3: Extracting Signals & Attention Aggregation ===")
        turns = []
        score_map = {"correct": 1.0, "partial": 0.5, "wrong": 0.2}
        for log in result.logs:
            # Generate Embedding for answer
            embedding = await embed_text(log.answer)
            # Evaluate using Attention Aggregation
            signal = SkillTurnSignal(
                score=score_map.get(log.judge.direction, 0.5),
                confidence=log.judge.confidence,
                evidence=["Simulated hit"]
            )
            turn = InterviewTurn(
                turn_index=log.turn,
                confidence=log.judge.confidence,
                embedding=embedding,
                skills={log.skill: signal}
            )
            turns.append(turn)
            
        print(f"Gathered {len(turns)} turns of data.")
        
        final_aggregate = await self.aggregator.aggregate(turns)
        print("\n=== FINAL RESULTS (Learned Profile) ===")
        for skill_name, data in final_aggregate.skills.items():
            print(f"- {skill_name.ljust(15)} : Score={data.score:.2f} | Uncertainty={data.uncertainty:.2f}")

        print("\nSimulation complete. Analyzing convergence...")
        for skill in SKILLS:
            # We check if AoT successfully converged by hitting target_sigma2
            sigma = result.final_state.sigma2.get(skill, 1.0)
            if sigma <= self.orchestrator.config.target_sigma2:
                print(f"  [CONVERGED] {skill} reached low uncertainty ({sigma:.2f}).")
            else:
                print(f"  [ONGOING]   {skill} needs more data (uncertainty {sigma:.2f}).")


if __name__ == "__main__":
    sim = InterviewSimulator()
    asyncio.run(sim.run_simulation())
