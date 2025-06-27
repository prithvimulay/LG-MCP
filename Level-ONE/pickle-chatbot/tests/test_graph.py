from langgraph_builder import build_graph

# Build the graph
graph = build_graph()

# Define a sample conversation
sample_messages = [
    "Hi, can you tell me what pickleball is?",
    "How many points do you need to win in pickleball?",
    "Explain the non-volley zone in pickleball.",
    "Who invented pickleball?",
    "Give me a quick summary of the rules in that rulebook."
]

# Fire them into the graph one by one
for user_message in sample_messages:
    print(f"\n=== USER: {user_message} ===")
    result = graph.invoke({"messages": [user_message]})
    for m in result['messages']:
        print(f"BOT: {m.content}")
