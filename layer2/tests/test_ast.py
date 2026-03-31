import asyncio

from layer2.ast_evaluator import ASTEvaluator


VALID_CODE = """
def fn(nums):
    total = 0
    for n in nums:
        if n % 2 == 0:
            total += n
    return total
"""

INVALID_CODE = "def bad(:\n pass"


def test_valid_code_complexity_computed() -> None:
    evaluator = ASTEvaluator()
    result = asyncio.run(evaluator.analyze(VALID_CODE))

    assert result is not None
    assert result.parse_success is True
    assert result.time_complexity in {"O(n)", "O(n^2)", "O(n^k)"}
    assert result.cyclomatic_complexity >= 2


def test_invalid_code_handled_gracefully() -> None:
    evaluator = ASTEvaluator()
    result = asyncio.run(evaluator.analyze(INVALID_CODE))

    assert result is not None
    assert result.active is True
    assert result.parse_success is False
    assert result.time_complexity == "unknown"
