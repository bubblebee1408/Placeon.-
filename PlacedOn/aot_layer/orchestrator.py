from collections.abc import Awaitable, Callable
from typing import Optional

from aot_layer.config import AoTConfig
from aot_layer.controller import Controller
from aot_layer.decomposer import Decomposer
from aot_layer.generator import QuestionGenerator
from aot_layer.judge import Judge
from aot_layer.models import InterviewState, OrchestrationResult, QuestionRequest, StartInput, TurnLog

AnswerProvider = Callable[[int, str, str, str], Awaitable[str]]


class AoTOrchestrator:
    def __init__(self, config: Optional[AoTConfig] = None) -> None:
        self.config = config or AoTConfig()
        self.controller = Controller(self.config)
        self.decomposer = Decomposer()
        self.generator = QuestionGenerator()
        self.judge = Judge()

    async def initialize_state(self, start_input: StartInput) -> InterviewState:
        skills = self.config.skills
        sigma_map = {skill: start_input.sigma2[idx] for idx, skill in enumerate(skills)}
        vector_map = {skill: start_input.skill_vector[idx] for idx, skill in enumerate(skills)}

        state = InterviewState(
            skills=skills,
            skill_vector=vector_map,
            sigma2=sigma_map,
            current_skill=skills[0],
            current_difficulty=self.config.default_difficulty,
            consecutive_turns={skill: 0 for skill in skills},
            turns_per_skill={skill: start_input.past_attempts_per_skill.get(skill, 0) for skill in skills},
            probes_per_skill={skill: 0 for skill in skills},
            retries_per_skill={skill: 0 for skill in skills},
        )

        start_decision = await self.controller.decide_start(state, self.decomposer)
        state.current_skill = start_decision.target_skill
        state.current_difficulty = start_decision.difficulty
        return state

    async def run(
        self,
        start_input: StartInput,
        answer_provider: AnswerProvider,
        max_turns: int = 5,
    ) -> OrchestrationResult:
        state = await self.initialize_state(start_input)
        logs: list[TurnLog] = []
        mode = "new"
        prev_question = ""
        prev_answer = ""
        prev_score = 0.5

        while len(logs) < max_turns and state.turn_index < self.config.total_turn_limit:
            turn_mode = mode
            active_skill = state.current_skill
            state.current_difficulty = self.controller.difficulty_for_skill(state, active_skill)
            question_out = await self.generator.generate(
                QuestionRequest(
                    target_skill=active_skill,
                    difficulty=state.current_difficulty,
                    mode=turn_mode,
                    last_question=prev_question,
                    last_answer=prev_answer,
                    last_score=prev_score,
                    minimal_state=state.compress_to_markov_state(),
                )
            )

            answer = await answer_provider(
                state.turn_index,
                question_out.question,
                active_skill,
                turn_mode,
            )

            judge_result = await self.judge.evaluate(active_skill, answer)

            state.turn_index += 1
            state.turns_per_skill[active_skill] = state.turns_per_skill.get(active_skill, 0) + 1
            state.consecutive_turns[active_skill] = (
                state.consecutive_turns.get(active_skill, 0) + 1
            )
            # --- BEGIN IMPROVED KALMAN UPDATE ---
            current_score = state.skill_vector.get(active_skill, 0.5)
            current_p = state.sigma2.get(active_skill, 0.8)
            
            # 1. Prediction (small drift Q=0.005)
            p_prior = current_p + 0.005
            
            # 2. Measurement Noise R (lower confidence => higher R)
            obs_score = judge_result.score
            obs_confidence = judge_result.confidence
            r = 0.2 * (2.0 - obs_confidence)
            
            # 3. Kalman Gain K
            k = p_prior / (p_prior + r)
            
            # 4. Update
            new_score = current_score + k * (obs_score - current_score)
            new_p = (1.0 - k) * p_prior
            
            state.skill_vector[active_skill] = round(max(0.0, min(new_score, 1.0)), 3)
            state.sigma2[active_skill] = round(max(0.01, min(new_p, 1.0)), 3)
            # --- END IMPROVED KALMAN UPDATE ---

            state.atomic_knowledge[active_skill] = judge_result.atomic_summary
            state.latest_summary = judge_result.atomic_summary

            end_decision = await self.controller.decide_end(state, judge_result)

            if end_decision.action == "probe":
                state.probes_per_skill[active_skill] = state.probes_per_skill.get(active_skill, 0) + 1
            elif end_decision.action == "retry":
                state.retries_per_skill[active_skill] = (
                    state.retries_per_skill.get(active_skill, 0) + 1
                )
            else:
                if end_decision.next_skill != active_skill:
                    state.consecutive_turns[active_skill] = 0
                state.current_skill = end_decision.next_skill
                state.current_difficulty = self.controller.difficulty_for_skill(
                    state, end_decision.next_skill
                )

            mode = end_decision.next_mode

            logs.append(
                TurnLog(
                    turn=state.turn_index,
                    skill=question_out.skill,
                    mode=turn_mode,
                    question=question_out.question,
                    answer=answer,
                    judge=judge_result,
                    controller_action=end_decision.action,
                )
            )

            # Track context for next turn's question generation
            prev_question = question_out.question
            prev_answer = answer
            prev_score = judge_result.score

            if end_decision.action == "finish":
                print("\n[Orchestrator] All targeted skills have converged. Ending interview naturally.")
                break

        return OrchestrationResult(final_state=state, logs=logs)
