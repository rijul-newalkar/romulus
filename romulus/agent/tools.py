import ast
import operator
import platform
from datetime import datetime


async def get_time() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


async def get_system_info() -> str:
    return (
        f"OS: {platform.system()} {platform.release()}, "
        f"Python: {platform.python_version()}, "
        f"Host: {platform.node()}, "
        f"Arch: {platform.machine()}"
    )


async def calculate(expression: str) -> str:
    allowed_ops = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.Mod: operator.mod,
        ast.Pow: operator.pow,
        ast.USub: operator.neg,
    }

    def _eval(node):
        if isinstance(node, ast.Expression):
            return _eval(node.body)
        elif isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return node.value
        elif isinstance(node, ast.BinOp):
            op_type = type(node.op)
            if op_type not in allowed_ops:
                raise ValueError(f"Unsupported operation: {op_type.__name__}")
            return allowed_ops[op_type](_eval(node.left), _eval(node.right))
        elif isinstance(node, ast.UnaryOp):
            op_type = type(node.op)
            if op_type not in allowed_ops:
                raise ValueError(f"Unsupported operation: {op_type.__name__}")
            return allowed_ops[op_type](_eval(node.operand))
        else:
            raise ValueError(f"Unsupported expression: {ast.dump(node)}")

    try:
        tree = ast.parse(expression.strip(), mode="eval")
        result = _eval(tree)
        return str(result)
    except Exception as e:
        return f"Error: {e}"
