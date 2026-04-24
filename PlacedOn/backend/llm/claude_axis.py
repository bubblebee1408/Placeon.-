import asyncio
import json
import re
from typing import Dict, List, Optional

from backend.llm.ollama_client import call_ollama
from backend.utils.json_utils import extract_json
from pydantic import BaseModel, Field

_AXIS_MODEL = "llama3"  # Using llama3 for all LLM components

class AxisScore(BaseModel):
    score: float = Field(ge=0.0, le=1.0)
    reasoning: str

class ClaudeAxisResult(BaseModel):
    axes: Dict[str, AxisScore]
    overall_confidence: float = Field(ge=0.0, le=1.0)
    nuance_notes: str

class ClaudeAxisEvaluator:
    """
    Evaluates interview responses along 10 Claude-specific axes.
    Bridges the gap between raw keyword matching and high-level psychometrics.
    """
    
    AXES_DEFINITIONS = {
        "grit": "Persistence and follow-through on complex problems or setbacks.",
        "resilience": "Maintaining logical clarity and tone under pressure.",
        "social": "Collaboration, listening, and stakeholder alignment.",
        "ownership": "Accountability for outcomes and proactive root-cause analysis.",
        "curiosity": "Depth of inquiry and speed of adapting to new constraints.",
        "calibration": "Recognition of uncertainty and explicit assumption checking.",
        "technical_depth": "Mechanical understanding of low-level implementation (e.g. Redis TTL).",
        "tradeoff_reasoning": "Architectural maturity and balancing competing constraints.",
        "clarity": "Nuance of language, lack of buzzwords, and concrete evidence usage.",
        "integrity": "Adherence to safety guardrails and absence of biased steering."
    }

    def __init__(self, model_name: str = _AXIS_MODEL):
        self.model_name = model_name

    def _build_prompt(self, question: str, answer: str) -> str:
        axes_formatted = "\n".join([f"- {name}: {desc}" for name, desc in self.AXES_DEFINITIONS.items()])
        
        return f"""
Analyze the following interview response along 10 specific axes of competency and behavioral traits.
Do not reward buzzwords. Look for concrete mechanisms, evidence, and logical reasoning.

### Axes to Evaluate:
{axes_formatted}

### Evaluation Criteria:
- Score 0.0-1.0 for each axis.
- Provide a brief reasoning for each score.
- Be extremely critical of vague or short answers.

### Input:
Question: {question}
Answer: {answer}

### Output:
Return JSON only in this format:
{{
  "axes": {{
    "grit": {{ "score": 0.5, "reasoning": "..." }},
    ... (total 10 axes)
  }},
  "overall_confidence": 0.8,
  "nuance_notes": "Summary of the candidate's communication style."
}}
"""

    async def evaluate_answer(self, question: str, answer: str) -> ClaudeAxisResult:
        prompt = self._build_prompt(question, answer)
        
        try:
            output = await asyncio.to_thread(
                call_ollama,
                prompt,
                self.model_name,
                {
                    "temperature": 0.1,
                    "top_p": 0.9,
                    "num_predict": 512,
                    "timeout_seconds": 300,
                },
            )
            payload = extract_json(output)
            return ClaudeAxisResult.model_validate(payload)
            
        except Exception as e:
            # Fallback in case of model failure during simulation
            return self._generate_fallback(f"Axis evaluation failed: {str(e)}")

    def _generate_fallback(self, reason: str) -> ClaudeAxisResult:
        fallback_axis = AxisScore(score=0.2, reasoning=reason)
        return ClaudeAxisResult(
            axes={name: fallback_axis for name in self.AXES_DEFINITIONS.keys()},
            overall_confidence=0.5,
            nuance_notes="Evaluation fallback triggered."
        )

if __name__ == "__main__":
    # Quick test harness
    async def test():
        evaluator = ClaudeAxisEvaluator()
        result = await evaluator.evaluate_answer(
            "How do you handle a database race condition?",
            "I use Redis as a write-through cache with a TTL to avoid stale data, but I'm careful about memory eviction."
        )
        print(json.dumps(result.model_dump(), indent=2))
        
    asyncio.run(test())
