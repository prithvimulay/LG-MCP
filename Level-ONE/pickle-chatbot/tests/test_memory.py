from app.langgraph_builder import build_graph

def test_memory_conversation():
    """
    Test that the conversation memory is working by asking multi-turn questions.
    """

    graph = build_graph()

    # start with an empty state
    state = {"messages": []}

    # first message
    first_msg = "Hi, what is pickleball?"
    state["messages"] = [first_msg]
    response = graph.invoke(state)
    print(f"BOT: {response['messages'][0].content}")

    # second message (should remember)
    second_msg = "Who invented it?"
    state["messages"] = [second_msg]
    response = graph.invoke(state)
    print(f"BOT: {response['messages'][0].content}")

    # third message (should recall context)
    third_msg = "Where was it invented?"
    state["messages"] = [third_msg]
    response = graph.invoke(state)
    print(f"BOT: {response['messages'][0].content}")

    # fourth message (checks conversation summarization)
    fourth_msg = "Summarize what we discussed so far."
    state["messages"] = [fourth_msg]
    response = graph.invoke(state)
    print(f"BOT: {response['messages'][0].content}")

if __name__ == "__main__":
    test_memory_conversation()
