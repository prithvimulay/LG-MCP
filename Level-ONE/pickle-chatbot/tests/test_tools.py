from dotenv import load_dotenv
load_dotenv()

import sys
import os
print("TAVILY_API_KEY loaded as:", os.getenv("TAVILY_API_KEY"))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "app"))

from langgraph_builder import build_graph

graph = build_graph()

test_prompts = [
    "What is pickleball? (should trigger Wikipedia)",             
    "What is the latest news about pickleball tournaments?",      
    "Tell me the scoring rules from the official rulebook.",      
    "What does the YouTube video about pickleball explain?"       
]

print("\n Starting offline tool test:\n")

state = {"messages": [], "tool_metadata": {}}

for idx, msg in enumerate(test_prompts, start=1):
    print(f"USER ({idx}): {msg}")
    state["messages"] = [msg]

    result = graph.invoke(state)

    for m in result["messages"]:
        print(f" BOT: {m}")

    meta = result.get("tool_metadata", {})
    print(f" Tool Trace: {meta}\n")

    print("-" * 60)

print("\n Tool test script finished.\n")
