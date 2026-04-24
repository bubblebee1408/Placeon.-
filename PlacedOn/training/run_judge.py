from typing import Any

from backend.llm.judge import evaluate_answer
from training.evaluator import evaluate_prediction




async def run_judge_on_dataset(
    dataset: list[dict[str, Any]],
    question: str,
    prompt_template: str,
    model: str = "gemma3:1b",
) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []

    for sample in dataset:
        prediction_obj = await evaluate_answer(
            question=question,
            answer=sample["input_text"],
            prompt_template=prompt_template,
            model=model,
        )
        predicted = prediction_obj.model_dump()
        errors = evaluate_prediction(predicted=predicted, expected=sample["expected"])

        records.append(
            {
                "input_text": sample["input_text"],
                "predicted": predicted,
                "expected": sample["expected"],
                "errors": errors,
            }
        )

    return records
