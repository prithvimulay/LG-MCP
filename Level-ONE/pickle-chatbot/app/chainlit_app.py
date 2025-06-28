import chainlit as cl
from langgraph_builder import build_graph

graph = None

@cl.on_chat_start
async def start():
    global graph
    graph = build_graph()
    await cl.Message("Hello! I’m your Pickleball rule and info assistant. Ask me anything !").send()

@cl.on_message
async def handle_message(message: cl.Message):
    global graph
    if graph is None:
        await cl.Message("⚠️ Graph not ready yet.").send()
        return

    user_message = message.content  

    spinner = cl.Message(content="⏳ Working on it...")
    await spinner.send()

    async with cl.Step(name="Thinking", type="run"):
        result = graph.invoke({"messages": [user_message]})

    await spinner.remove()

    for m in result['messages']:
        if m.type == "ai":
            await cl.Message(m.content).send()

