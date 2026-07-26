from app.tools.calculator import CalculatorTool

tool = CalculatorTool()

questions = [
    "10+20",
    "15*8",
    "100/4",
    "sqrt(81)",
    "pow(5,2)",
]

for q in questions:

    result = tool.calculate(q)

    print("=" * 60)
    print(q)
    print(result)