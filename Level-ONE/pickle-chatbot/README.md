# Pickleball Chatbot POC

- Uses Chainlit + LangGraph
- 4 tools:
  - Wikipedia
  - Tavily
  - Pickleball PDF
  - Pickleball YouTube
- Powered by Groq LLM (`qwen2-72b-chat`)

## Running

```bash
cl run app/chainlit_app.py
or 
chainlit run app/chainlit_app.py 