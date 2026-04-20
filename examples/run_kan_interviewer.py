import asyncio
import os
import sys
import numpy as np

# Ensure we can import PlacedOn components
base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if base_path not in sys.path:
    sys.path.append(base_path)

from PlacedOn.aot_layer.config import AoTConfig
from PlacedOn.aot_layer.orchestrator import AoTOrchestrator
from PlacedOn.layer2.embedding import embed_text
from PlacedOn.layer3.bias_classifier import BiasEnforcer
from PlacedOn.layer5.aggregator import AggregationEngine
from PlacedOn.layer5.models import InterviewTurn, SkillTurnSignal
from PlacedOn.layer5.scorer import ScoringEngine

async def run_example():
    print("--- 🚀 PlacedOn KAN-Powered Interview Demonstration ---")
    
    # 1. Initialization
    skills = ["caching", "system_design", "api_design"]
    orchestrator = AoTOrchestrator(config=AoTConfig(skills=skills))
    bias_enforcer = BiasEnforcer()
    aggregator = AggregationEngine()
    scorer = ScoringEngine()
    
    print("[+] Components Initialized. Starting Dynamic Interview Loop...")

    # 2. Mock Answer Provider
    async def answer_provider(turn: int, question: str, skill: str, mode: str) -> str:
        await bias_enforcer.assess(question)
        print(f"  [AI Question {turn}]: {question}")
        
        # Simulate a high-performing senior engineer candidate
        senior_answers = {
            "caching": "I prefer using a write-through cache with a strict TTL strategy to avoid stale data, especially in high-concurrency environments.",
            "system_design": "Scaling horizontally requires load balancing at every layer. I'd use consistent hashing to minimize re-mapping during node additions.",
            "api_design": "RESTful principles are key. I'd ensure idempotent keys for all POST requests to prevents duplicate transactions during partial failures."
        }
        answer = senior_answers.get(skill, "I'd use a modular approach with clear interfaces.")
        print(f"  [Candidate Answer]: {answer}")
        return answer

    # 3. Execution
    from PlacedOn.aot_layer.models import StartInput
    start = StartInput(
        skill_vector=[0.8, 0.8, 0.8], 
        sigma2=[0.95] * 3, 
        past_attempts_per_skill={s: 0 for s in skills}
    )
    
    interview_result = await orchestrator.run(start_input=start, answer_provider=answer_provider, max_turns=3)
    
    # 4. Aggregation
    turns = []
    score_map = {"correct": 1.0, "partial": 0.5, "wrong": 0.2}
    for log in interview_result.logs:
        embedding = await embed_text(log.answer)
        signal = SkillTurnSignal(
            score=score_map.get(log.judge.direction, 0.5),
            confidence=log.judge.confidence,
            evidence=["automated demonstration evidence"]
        )
        turn = InterviewTurn(
            turn_index=log.turn,
            confidence=log.judge.confidence,
            embedding=embedding,
            skills={log.skill: signal}
        )
        turns.append(turn)

    print("\n[+] Interview Complete. Aggregating Embedded Semantic State...")
    candidate_aggregate = await aggregator.aggregate(turns)
    
    # 5. KAN Prediction
    print("[+] Running KAN Neural Spline Inference...")
    result = scorer.predict_detailed(candidate_aggregate.embedding)
    
    print("\n" + "="*50)
    print("💎 FINAL PERFORMANCE REPORT (KAN Technology)")
    print("="*50)
    print(f"Candidate ID: DEMO-SENIOR-ENG-1")
    print(f"Aggregated Embedding Dimensions: {len(candidate_aggregate.embedding)} (SBERT)")
    print(f"Neural Prediction Score: {result.score:.4f}")
    print(f"Prediction Confidence: {result.confidence * 100:.1f}%")
    print(f"Model Explanation: {result.explanation}")
    
    if result.score > 0.85:
        print("Recommendation: [STRONGLY HIRE] - High conceptual alignment.")
    elif result.score > 0.65:
        print("Recommendation: [HIRE] - Competent with some variance.")
    else:
        print("Recommendation: [DEFER] - Conceptual gaps detected.")
    print("="*50)

if __name__ == "__main__":
    asyncio.run(run_example())
