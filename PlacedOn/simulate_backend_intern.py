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

# Backend Intern Skills
SKILLS = ["backend", "db_design", "caching", "system_design", "block_8_ownership", "block_10_calibration"]

class BackendInternSimulator:
    def __init__(self):
        self.orchestrator = AoTOrchestrator(config=AoTConfig(skills=SKILLS, total_turn_limit=12, max_retries_per_skill=1))
        self.bias_enforcer = BiasEnforcer()
        self.aggregator = AggregationEngine()
        self.axis_evaluator = ClaudeAxisEvaluator()
        
    async def run_simulation(self):
        print("=" * 60)
        print("  BACKEND INTERN — LIVE AoT INTERVIEW SIMULATION")
        print("=" * 60)
        
        candidate = CandidateState(
            candidate_id="backend_intern_1",
            embedding=[0.0] * 384,
            skills={}
        )
        
        start = StartInput(
            skill_vector=[0.5] * len(SKILLS),
            sigma2=[0.95] * len(SKILLS),
            past_attempts_per_skill={s: 0 for s in SKILLS},
        )
        
        print(f"\nSkills targeted: {SKILLS}\n")
        
        async def answer_provider(turn: int, question: str, skill: str, mode: str) -> str:
            print(f"\n{'─' * 55}")
            print(f"[Turn {turn}] Skill: {skill} | Mode: {mode}")
            print(f"{'─' * 55}")
            print(f"🎙  INTERVIEWER: {question}")
            
            try:
                assessment = await self.bias_enforcer.assess(question)
                if not assessment.approved:
                    print(f"   🛡️ BIAS DETECTED! Score: {assessment.bias_score}")
                else:
                    print(f"   ✅ Bias check passed (Score: {assessment.bias_score:.4f})")
            except Exception as e:
                print(f"   ⚠️ Bias check failed: {e}")

            print(f"\n👤 CANDIDATE (paste answer below):")
            ans = ""
            while not ans.strip():
                ans = input(">>> ")
                if not ans.strip():
                    print("   (answer cannot be empty, try again)")
            return ans.strip()

        print("\n=== Starting AoT Orchestrator ===\n")
        result = await self.orchestrator.run(start_input=start, answer_provider=answer_provider, max_turns=12)
        
        print("\n\n" + "=" * 60)
        print("  INTERVIEW COMPLETE — PROCESSING RESULTS")
        print("=" * 60)
        
        turns = []
        score_map = {"correct": 1.0, "partial": 0.5, "wrong": 0.2}
        for log in result.logs:
            embedding = await embed_text(log.answer)
            signal = SkillTurnSignal(
                score=score_map.get(log.judge.direction, 0.5),
                confidence=log.judge.confidence,
                evidence=["Simulated hit"]
            )
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
            
        final_aggregate = await self.aggregator.aggregate(turns)
        
        print("\n" + "=" * 60)
        print("  FINAL RESULTS")  
        print("=" * 60)
        
        for skill_name, data in final_aggregate.skills.items():
            print(f"  {skill_name.ljust(20)} : Score={data.score:.2f} | Uncertainty={data.uncertainty:.2f}")

        print(f"\n{'─' * 40}")
        print("  CLAUDE AXIS PROFILE")
        print(f"{'─' * 40}")
        for axis_name, data in final_aggregate.axes.items():
            print(f"  {axis_name.ljust(20)} : Score={data.score:.2f} | Uncertainty={data.uncertainty:.2f}")

        print(f"\n{'─' * 40}")
        print("  CONVERGENCE CHECK")
        print(f"{'─' * 40}")
        for skill in SKILLS:
            sigma = result.final_state.sigma2.get(skill, 1.0)
            if sigma <= self.orchestrator.config.target_sigma2:
                print(f"  ✅ {skill} converged (σ²={sigma:.2f})")
            else:
                print(f"  🔄 {skill} needs more data (σ²={sigma:.2f})")


if __name__ == "__main__":
    sim = BackendInternSimulator()
    asyncio.run(sim.run_simulation())
