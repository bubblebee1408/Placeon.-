import ast
import re

from layer2.models import CodeAnalysis


class ASTEvaluator:
    async def analyze(self, text: str) -> CodeAnalysis | None:
        if not self._looks_like_code(text):
            return None

        try:
            tree = ast.parse(text)
        except SyntaxError as exc:
            return CodeAnalysis(
                active=True,
                parse_success=False,
                time_complexity="unknown",
                cyclomatic_complexity=1,
                detail=f"parse_error:{exc.msg}",
            )

        cyclomatic = self._cyclomatic_complexity(tree)
        time_complexity = self._time_complexity(tree)

        return CodeAnalysis(
            active=True,
            parse_success=True,
            time_complexity=time_complexity,
            cyclomatic_complexity=cyclomatic,
            detail="deterministic-ast-analysis",
        )

    def _looks_like_code(self, text: str) -> bool:
        patterns = [r"\bdef\b", r"\bclass\b", r"\bfor\b", r"\bwhile\b", r":\n", r"return "]
        return any(re.search(pattern, text) for pattern in patterns)

    def _cyclomatic_complexity(self, tree: ast.AST) -> int:
        branch_nodes = (
            ast.If,
            ast.For,
            ast.While,
            ast.Try,
            ast.ExceptHandler,
            ast.With,
            ast.IfExp,
            ast.BoolOp,
            ast.Match,
            ast.comprehension,
        )
        branches = sum(1 for node in ast.walk(tree) if isinstance(node, branch_nodes))
        return max(1, branches + 1)

    def _time_complexity(self, tree: ast.AST) -> str:
        loop_depth = self._max_loop_depth(tree)
        if self._is_recursive(tree):
            return "O(2^n)"
        if loop_depth <= 0:
            return "O(1)"
        if loop_depth == 1:
            return "O(n)"
        if loop_depth == 2:
            return "O(n^2)"
        return "O(n^k)"

    def _max_loop_depth(self, tree: ast.AST) -> int:
        max_depth = 0

        def visit(node: ast.AST, depth: int) -> None:
            nonlocal max_depth
            is_loop = isinstance(node, (ast.For, ast.While, ast.comprehension))
            next_depth = depth + 1 if is_loop else depth
            max_depth = max(max_depth, next_depth)
            for child in ast.iter_child_nodes(node):
                visit(child, next_depth)

        visit(tree, 0)
        return max_depth

    def _is_recursive(self, tree: ast.AST) -> bool:
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                fn_name = node.name
                for child in ast.walk(node):
                    if isinstance(child, ast.Call) and isinstance(child.func, ast.Name) and child.func.id == fn_name:
                        return True
        return False
