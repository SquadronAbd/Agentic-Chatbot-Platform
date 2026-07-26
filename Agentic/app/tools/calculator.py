import math
import operator


class CalculatorTool:
    """
    Performs safe mathematical calculations.
    """

    OPERATORS = {
        "+": operator.add,
        "-": operator.sub,
        "*": operator.mul,
        "/": operator.truediv,
        "**": operator.pow,
        "%": operator.mod,
    }

    def calculate(self, expression: str):

        try:

            allowed = {
                "sqrt": math.sqrt,
                "pow": pow,
                "abs": abs,
                "round": round,
            }

            result = eval(
                expression,
                {"__builtins__": {}},
                allowed,
            )

            return {
                "success": True,
                "result": result,
            }

        except Exception as e:

            return {
                "success": False,
                "error": str(e),
            }