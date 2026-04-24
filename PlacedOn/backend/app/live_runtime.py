from __future__ import annotations

import os
import sys
from typing import Any

CODE_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
if CODE_ROOT not in sys.path:
    sys.path.append(CODE_ROOT)

from aot_layer.config import AoTConfig
from aot_layer.models import InterviewState as AoTInterviewState
from aot_layer.models import QuestionRequest, StartInput
from aot_layer.orchestrator import AoTOrchestrator
from .models import InterviewState
from layer2.adapter import CapabilityAdapter
from layer2.ast_evaluator import ASTEvaluator
from layer2.behavioral import BehavioralSignalTracker
from layer2.models import Layer2Output
from layer3.integrity import BehavioralIntegrityEngine
from layer3.models import IntegrityInput
from layer5.aggregator import AggregationEngine
from layer5.matcher import FitMatcher
from layer5.models import FitInput, InterviewTurn, RenderInput, SkillTurnSignal
from layer5.renderer import ProfileRenderer
from layer5.storage import CandidateRepository

MIN_TURNS = 10
MAX_TURNS = 15
SKILL_SCORE_THRESHOLD = 0.7


def should_end_interview(state: InterviewState) -> bool:
    if state.turn_count < MIN_TURNS:
        return False

    hr_skills_asked = any(s.startswith("hr_") for s in state.skill_scores.keys())

    if (
        state.turn_count >= MIN_TURNS
        and state.skill_coverage >= 0.7
        and state.avg_confidence >= 0.7
        and hr_skills_asked
    ):
        return True

    if state.turn_count >= MAX_TURNS:
        return True

    return False


class LiveInterviewRuntime:
    def __init__(self, config: AoTConfig | None = None, repository: CandidateRepository | None = None) -> None:
        from layer3.bias_classifier import BiasEnforcer
        from layer3.fallback import SafeQuestionPipeline

        self._aot = AoTOrchestrator(config=config or AoTConfig())
        self._safe_pipeline = SafeQuestionPipeline(bias_enforcer=BiasEnforcer())

        self._ast = ASTEvaluator()
        self._behavioral = BehavioralSignalTracker()
        self._integrity = BehavioralIntegrityEngine()

        self._aggregator = AggregationEngine()
        self._matcher = FitMatcher()
        self._renderer = ProfileRenderer()
        self._repo = repository or CandidateRepository()

    async def bootstrap_question(self, state: InterviewState) -> InterviewState:
        if state.last_question and state.turn > 0:
            return state

        aot_state = await self._load_or_initialize_aot_state(state)
        mode = state.current_mode or "new"

        safe_question = await self._next_safe_question(
            skill=aot_state.current_skill,
            difficulty=aot_state.current_difficulty,
            mode=mode,
        )

        updated_history = state.question_history[:] if state.question_history else []
        if not updated_history or updated_history[-1] != safe_question:
            updated_history.append(safe_question)

        snapshot = state.candidate_snapshot.copy()
        snapshot["aot_state"] = aot_state.model_dump()

        return state.model_copy(
            update={
                "turn": aot_state.turn_index + 1,
                "last_question": safe_question,
                "last_answer": None,
                "question_history": updated_history,
                "current_skill": aot_state.current_skill,
                "current_difficulty": aot_state.current_difficulty,
                "current_mode": mode,
                "candidate_snapshot": snapshot,
            }
        )

    async def process_answer(self, state: InterviewState, answer: str, message_id: str) -> InterviewState:
        aot_state = await self._load_or_initialize_aot_state(state)
        mode = state.current_mode or "new"
        active_skill = aot_state.current_skill

        judge_result = await self._aot.judge.evaluate(active_skill, answer)

        answers = state.answer_history[:] if state.answer_history else []
        answers.append(answer)
        layer2_series = await self._replay_layer2(answers)
        latest_layer2 = layer2_series[-1]["layer2"]

        behavioral = await self._behavioral.track([item["adapter"] for item in layer2_series])
        integrity = await self._integrity.evaluate(
            IntegrityInput(
                embeddings=[item["adapter"].embedding for item in layer2_series],
                consistency_score=behavioral.consistency_score,
                drift_score=behavioral.drift_score,
                confidence_signal=behavioral.confidence_signal,
            )
        )

        trust_factor = 0.7 + (0.3 * integrity.trust_score)
        adjusted_confidence = round(max(0.0, min(judge_result.confidence * trust_factor, 1.0)), 2)

        aot_state.turn_index += 1
        aot_state.turns_per_skill[active_skill] = aot_state.turns_per_skill.get(active_skill, 0) + 1
        aot_state.consecutive_turns[active_skill] = aot_state.consecutive_turns.get(active_skill, 0) + 1
        aot_state.skill_vector[active_skill] = adjusted_confidence
        aot_state.sigma2[active_skill] = round(1.0 - adjusted_confidence, 2)

        tracked_skill_scores = self._build_skill_scores(state.skill_scores, aot_state.skill_vector)
        tracked_skill_scores[active_skill] = adjusted_confidence

        next_turn_count = max(state.turn_count, 0) + 1
        previous_confidence_total = max(state.avg_confidence, 0.0) * max(state.turn_count, 0)
        next_avg_confidence = (previous_confidence_total + float(judge_result.confidence)) / next_turn_count

        total_skills = max(len(tracked_skill_scores), 1)
        covered_skills = sum(1 for score in tracked_skill_scores.values() if score >= SKILL_SCORE_THRESHOLD)
        next_skill_coverage = covered_skills / total_skills

        runtime_state = state.model_copy(
            update={
                "turn_count": next_turn_count,
                "skill_scores": tracked_skill_scores,
                "skill_coverage": round(next_skill_coverage, 4),
                "avg_confidence": round(next_avg_confidence, 4),
            }
        )

        if should_end_interview(runtime_state):
            closing_message = "Thanks, I have enough information to evaluate your profile."
            layer5_turns = self._layer5_turns_from_series(layer2_series)
            aggregate = await self._aggregator.aggregate(layer5_turns)

            candidate = await self._repo.save_from_aggregate(
                candidate_id=state.interview_id,
                embedding=aggregate.embedding,
                skills=aggregate.skills,
                metadata={
                    "latest_trust": integrity.trust_score,
                    "anomaly_flag": integrity.anomaly_flag,
                    "answered_turns": len(answers),
                },
            )

            fit = await self._matcher.predict(
                FitInput(
                    candidate_embedding=candidate.embedding,
                    role_vector=candidate.embedding,
                    preference_vector=None,
                )
            )
            profile = await self._renderer.render(
                RenderInput(candidate_id=candidate.candidate_id, skills=candidate.skills),
                top_n=3,
            )

            snapshot = {
                "aot_state": aot_state.model_dump(),
                "fit": fit.model_dump(),
                "profile": profile.model_dump(),
                "latest_layer2": latest_layer2.model_dump(),
            }

            updated_questions = state.question_history[:] if state.question_history else []
            if not updated_questions or updated_questions[-1] != closing_message:
                updated_questions.append(closing_message)

            return state.model_copy(
                update={
                    "turn": aot_state.turn_index + 1,
                    "turn_count": next_turn_count,
                    "last_question": closing_message,
                    "last_answer": None,
                    "last_message_id": message_id,
                    "question_history": updated_questions,
                    "answer_history": answers,
                    "current_mode": "complete",
                    "current_skill": aot_state.current_skill,
                    "current_difficulty": aot_state.current_difficulty,
                    "skill_vector": [aot_state.skill_vector.get(skill, 0.5) for skill in self._aot.config.skills],
                    "skill_scores": tracked_skill_scores,
                    "skill_coverage": round(next_skill_coverage, 4),
                    "avg_confidence": round(next_avg_confidence, 4),
                    "sigma2": [aot_state.sigma2.get(skill, 0.5) for skill in self._aot.config.skills],
                    "performance": {
                        "trust_score": integrity.trust_score,
                        "anomaly_flag": integrity.anomaly_flag,
                        "controller_action": "complete",
                        "fit": fit.fit_score,
                        "fit_interpretation": fit.interpretation,
                    },
                    "latest_trust_score": integrity.trust_score,
                    "anomaly_flag": integrity.anomaly_flag,
                    "candidate_snapshot": snapshot,
                }
            )

        end_decision = await self._aot.controller.decide_end(aot_state, judge_result)
        if end_decision.action == "probe":
            aot_state.probes_per_skill[active_skill] = aot_state.probes_per_skill.get(active_skill, 0) + 1
        elif end_decision.action == "retry":
            aot_state.retries_per_skill[active_skill] = aot_state.retries_per_skill.get(active_skill, 0) + 1
        else:
            if end_decision.next_skill != active_skill:
                aot_state.consecutive_turns[active_skill] = 0
            aot_state.current_skill = end_decision.next_skill
            aot_state.current_difficulty = self._aot.controller.difficulty_for_skill(
                aot_state,
                end_decision.next_skill,
            )

        next_mode = end_decision.next_mode
        next_question = await self._next_safe_question(
            skill=aot_state.current_skill,
            difficulty=aot_state.current_difficulty,
            mode=next_mode,
        )

        layer5_turns = self._layer5_turns_from_series(layer2_series)
        aggregate = await self._aggregator.aggregate(layer5_turns)

        candidate = await self._repo.save_from_aggregate(
            candidate_id=state.interview_id,
            embedding=aggregate.embedding,
            skills=aggregate.skills,
            metadata={
                "latest_trust": integrity.trust_score,
                "anomaly_flag": integrity.anomaly_flag,
                "answered_turns": len(answers),
            },
        )

        fit = await self._matcher.predict(
            FitInput(
                candidate_embedding=candidate.embedding,
                role_vector=candidate.embedding,
                preference_vector=None,
            )
        )
        profile = await self._renderer.render(
            RenderInput(candidate_id=candidate.candidate_id, skills=candidate.skills),
            top_n=3,
        )

        updated_questions = state.question_history[:] if state.question_history else []
        if not updated_questions or updated_questions[-1] != next_question:
            updated_questions.append(next_question)

        snapshot = {
            "aot_state": aot_state.model_dump(),
            "fit": fit.model_dump(),
            "profile": profile.model_dump(),
            "latest_layer2": latest_layer2.model_dump(),
        }

        return state.model_copy(
            update={
                "turn": aot_state.turn_index + 1,
                "turn_count": next_turn_count,
                "last_question": next_question,
                "last_answer": None,
                "last_message_id": message_id,
                "question_history": updated_questions,
                "answer_history": answers,
                "current_mode": next_mode,
                "current_skill": aot_state.current_skill,
                "current_difficulty": aot_state.current_difficulty,
                "skill_vector": [aot_state.skill_vector.get(skill, 0.5) for skill in self._aot.config.skills],
                "skill_scores": tracked_skill_scores,
                "skill_coverage": round(next_skill_coverage, 4),
                "avg_confidence": round(next_avg_confidence, 4),
                "sigma2": [aot_state.sigma2.get(skill, 0.5) for skill in self._aot.config.skills],
                "performance": {
                    "trust_score": integrity.trust_score,
                    "anomaly_flag": integrity.anomaly_flag,
                    "controller_action": end_decision.action,
                    "fit": fit.fit_score,
                    "fit_interpretation": fit.interpretation,
                },
                "latest_trust_score": integrity.trust_score,
                "anomaly_flag": integrity.anomaly_flag,
                "candidate_snapshot": snapshot,
            }
        )

    async def _load_or_initialize_aot_state(self, state: InterviewState) -> AoTInterviewState:
        raw_aot = state.candidate_snapshot.get("aot_state") if state.candidate_snapshot else None
        if raw_aot:
            return AoTInterviewState.model_validate(raw_aot)

        start = StartInput(
            skill_vector=self._fit_dimension(state.skill_vector, len(self._aot.config.skills), 0.5),
            sigma2=self._fit_dimension(state.sigma2, len(self._aot.config.skills), 0.5),
            past_attempts_per_skill={skill: 0 for skill in self._aot.config.skills},
        )
        return await self._aot.initialize_state(start)

    async def _next_safe_question(self, skill: str, difficulty: str, mode: str) -> str:
        question_out = await self._aot.generator.generate(
            QuestionRequest(target_skill=skill, difficulty=difficulty, mode=mode)
        )
        guardrail = await self._safe_pipeline.validate(
            question=question_out.question,
            skill=question_out.skill,
            difficulty=question_out.difficulty,
        )
        return guardrail.question

    async def _replay_layer2(self, answers: list[str]) -> list[dict[str, Any]]:
        adapter = CapabilityAdapter()
        series: list[dict[str, Any]] = []
        for answer in answers:
            adapter_out = await adapter.process(answer)
            code_analysis = await self._ast.analyze(answer)
            behavioral = await self._behavioral.track([item["adapter"] for item in series] + [adapter_out])

            series.append(
                {
                    "adapter": adapter_out,
                    "layer2": Layer2Output(
                        skills=adapter_out.skills,
                        embedding=adapter_out.embedding,
                        behavioral_signals=behavioral,
                        code_analysis=code_analysis,
                    ),
                }
            )
        return series

    def _layer5_turns_from_series(self, series: list[dict[str, Any]]) -> list[InterviewTurn]:
        if not series:
            return []

        target_dim = max(len(series[0]["layer2"].embedding), 1)
        turns: list[InterviewTurn] = []
        for idx, item in enumerate(series, start=1):
            layer2_out: Layer2Output = item["layer2"]
            embedding = self._fit_dimension(layer2_out.embedding, target_dim, 0.0)
            skills: dict[str, SkillTurnSignal] = {}
            for skill, skill_state in layer2_out.skills.items():
                confidence = round(max(0.05, min(1.0 - skill_state.uncertainty, 1.0)), 4)
                evidence = [
                    f"layer2:{skill}:score={skill_state.score}",
                    f"layer2:{skill}:uncertainty={skill_state.uncertainty}",
                ]
                skills[skill] = SkillTurnSignal(score=skill_state.score, confidence=confidence, evidence=evidence)

            turns.append(
                InterviewTurn(
                    turn_index=idx,
                    confidence=layer2_out.behavioral_signals.confidence_signal,
                    embedding=embedding,
                    skills=skills,
                )
            )

        return turns

    def _fit_dimension(self, values: list[float], target: int, default: float) -> list[float]:
        if target <= 0:
            return []
        if len(values) == target:
            return values
        if len(values) > target:
            return values[:target]
        return values + [default] * (target - len(values))

    def _build_skill_scores(self, existing: dict[str, float], aot_scores: dict[str, float]) -> dict[str, float]:
        skill_scores: dict[str, float] = {}

        for skill in self._aot.config.skills:
            value = existing.get(skill)
            if value is None:
                value = aot_scores.get(skill, 0.0)
            skill_scores[skill] = round(max(0.0, min(float(value), 1.0)), 4)

        for skill, value in existing.items():
            if skill not in skill_scores:
                skill_scores[skill] = round(max(0.0, min(float(value), 1.0)), 4)

        return skill_scores
