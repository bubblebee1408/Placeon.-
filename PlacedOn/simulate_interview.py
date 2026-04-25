import asyncio
import json

from aot_layer.config import AoTConfig
from aot_layer.models import StartInput
from aot_layer.orchestrator import AoTOrchestrator
from layer2.embedding import embed_text
from layer3.bias_classifier import BiasEnforcer
from backend.llm.claude_axis import ClaudeAxisEvaluator
from layer5.aggregator import AggregationEngine
from layer5.models import AxisSignal, CandidateState, InterviewTurn, SkillTurnSignal

# Mock Candidate and Config
# We will simulate a Gen AI intern interview
SKILLS = ["gen_ai", "prompt_engineering", "rag_architecture", "block_8_curiosity", "block_10_calibration"]

class InterviewSimulator:
    def __init__(self):
        self.orchestrator = AoTOrchestrator(config=AoTConfig(skills=SKILLS, total_turn_limit=12, max_retries_per_skill=1))
        self.bias_enforcer = BiasEnforcer()
        self.aggregator = AggregationEngine()
        self.axis_evaluator = ClaudeAxisEvaluator()
        
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

            # The AI Agent (me) will be the candidate. The script pauses here to let you paste the question to me, and then you can paste my answer back here!
            print("\n" + "="*50)
            print("⏳ WAITING FOR CANDIDATE (Paste this question to me in the chat):")
            print(f"'{question}'")
            ans = input("📝 Paste the candidate's answer here: ")
            print("="*50 + "\n")
                
            print(f"<- Answer:   {ans}")
            return ans

        print("\n=== STAGE 2: AoT Orchestrator Trajectory ===")
        # Run orchestrator
        result = await self.orchestrator.run(start_input=start, answer_provider=mock_answer_provider, max_turns=12)
        
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
            # Evaluate along Claude Axes
            axis_result = await self.axis_evaluator.evaluate_answer(log.question, log.answer)
            axes_signals = {
                name: AxisSignal(score=data.score, reasoning=data.reasoning)
                for name, data in axis_result.axes.items()
            }
            
            turn = InterviewTurn(
                turn_index=log.turn,
                confidence=log.judge.confidence,
                embedding=embedding,
                skills={log.skill: signal},
                axes=axes_signals
            )
            turns.append(turn)
            
        print(f"Gathered {len(turns)} turns of data.")
        
        final_aggregate = await self.aggregator.aggregate(turns)
        print("\n=== FINAL RESULTS (Learned Profile) ===")
        print("🤖 AI Interviewer: 'Thank you for your time today! That concludes both the technical and behavioral portions of our interview. We have gathered all the information we need. Our team will review your profile and be in touch soon!'\n")
        
        for skill_name, data in final_aggregate.skills.items():
            print(f"- {skill_name.ljust(15)} : Score={data.score:.2f} | Uncertainty={data.uncertainty:.2f}")

        print("\n=== CLAUDE AXIS PROFILE ===")
        for axis_name, data in final_aggregate.axes.items():
            print(f"- {axis_name.ljust(15)} : Score={data.score:.2f} | Uncertainty={data.uncertainty:.2f}")
            if data.reasoning_summary:
                print(f"   Reasoning: {data.reasoning_summary[0]}")

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
