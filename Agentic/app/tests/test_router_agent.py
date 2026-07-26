from app.agents.router_agent import RouterAgent

router = RouterAgent()

questions = [
    "What company is this report about?",
    "What did I ask previously?",
    "What is AI?",
]

for question in questions:

    print("=" * 60)

    print(question)

    print(router.route(question))