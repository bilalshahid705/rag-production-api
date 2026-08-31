from app.agent import ProductionAgent

def TestProductionAgent():

    agent = ProductionAgent()
    queries = [
        "What is LangGraph in two sentence?",
        "What is 3 + 5",
        "Explain the difference between RAG and fine-tuning in 2 sentences?"
    ]

    for query in queries:
        print(f"Question: {query}")
        result = agent.invoke_agent(query)
        print(f"Response: {result['response'][:150]}...")
        print(f"Model used: {result['model_used']}")


if __name__ == "__main__":
    TestProductionAgent()