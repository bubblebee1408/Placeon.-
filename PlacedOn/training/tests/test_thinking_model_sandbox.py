from aot_layer.models import InterviewState, JudgeResult, OrchestrationResult, TurnLog
from training.thinking_model_sandbox import ThinkingScenario, _episode_reward, _update_curriculum_weights


def _result(action: str, score: float) -> OrchestrationResult:
    state = InterviewState(
        skills=["system_design", "caching", "backend", "block_10_calibration"],
        skill_vector={
            "system_design": score,
            "caching": score,
            "backend": score,
            "block_10_calibration": score,
        },
        sigma2={skill: 0.2 for skill in ["system_design", "caching", "backend", "block_10_calibration"]},
        current_skill="system_design",
        consecutive_turns={skill: 0 for skill in ["system_design", "caching", "backend", "block_10_calibration"]},
        turns_per_skill={skill: 0 for skill in ["system_design", "caching", "backend", "block_10_calibration"]},
        probes_per_skill={skill: 0 for skill in ["system_design", "caching", "backend", "block_10_calibration"]},
        retries_per_skill={skill: 0 for skill in ["system_design", "caching", "backend", "block_10_calibration"]},
    )
    log = TurnLog(
        turn=1,
        skill="system_design",
        mode="new",
        question="How would you design this?",
        answer="I would reason through it carefully.",
        judge=JudgeResult(
            direction="partial",
            score=score,
            confidence=0.6,
            evidence=[],
            missing=[],
            probe_recommended=True,
            probe_focus=[],
            recovery_possible=False,
            atomic_summary="Synthetic",
        ),
        controller_action=action,
    )
    return OrchestrationResult(final_state=state, logs=[log])


def test_curriculum_weights_shift_toward_low_reward_scenarios() -> None:
    updated = _update_curriculum_weights(
        current_weights={"hard_case": 0.5, "easy_case": 0.5},
        rewards_by_scenario={"hard_case": [0.41, 0.46], "easy_case": [0.82, 0.85]},
    )

    assert updated["hard_case"] > updated["easy_case"]
    assert round(sum(updated.values()), 6) == 1.0


def test_episode_reward_prefers_expected_recovery_action() -> None:
    scenario = ThinkingScenario(
        name="recovering_builder",
        description="Needs a probe to improve.",
        ground_truth={
            "system_design": 0.6,
            "caching": 0.6,
            "backend": 0.6,
            "block_10_calibration": 0.6,
        },
        answers={},
        expected_actions=("probe",),
    )

    rewarded = _episode_reward(_result(action="probe", score=0.5), scenario)
    not_rewarded = _episode_reward(_result(action="move", score=0.5), scenario)

    assert rewarded > not_rewarded
