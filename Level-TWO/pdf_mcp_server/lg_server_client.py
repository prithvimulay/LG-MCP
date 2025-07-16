import sys
import requests
import json

class LangGraphServerClient:
    def __init__(self, server_url: str = "http://localhost:5001"):
        self.server_url = server_url
        self.session = requests.Session()

        try:
            r = self.session.get(f"{self.server_url}/health")
            if r.status_code != 200:
                print("❌ MCP server not reachable")
                sys.exit(1)
        except requests.RequestException:
            print("❌ MCP server not reachable")
            sys.exit(1)

    def process_query(self, query: str) -> str:
        """Send query and stream response"""
        print(f"📤 Streaming query to MCP: {query}")
        try:
            with self.session.post(
                f"{self.server_url}/query",
                json={"query": query},
                headers={"Accept": "text/event-stream"},
                stream=True
            ) as response:
                if response.status_code != 200:
                    return f"❌ Server error: {response.status_code} - {response.text}"

                output = ""
                for line in response.iter_lines():
                    if line:
                        decoded = line.decode("utf-8").replace("data: ", "")
                        try:
                            data = json.loads(decoded)
                            if "response" in data:
                                output = data["response"]
                            elif "error" in data:
                                output = f"❌ Error: {data['error']}"
                        except json.JSONDecodeError:
                            output += decoded + "\n"
                return output
        except Exception as e:
            return f"❌ Error streaming query: {str(e)}"

    def display_help(self):
        print("🧠 PDF Assistant — Streamed LangGraph/MCP Server")
        print("• Ask questions, summarize PDFs, generate podcasts")
        print("• Type 'help' or 'exit' at any time\n")

    def run(self):
        print("🚀 PDF Assistant CLI (Streaming)")
        while True:
            try:
                query = input("\n🤖 Your Query: ").strip()
                if not query:
                    continue
                if query.lower() in ("exit", "quit"):
                    print("👋 Goodbye!")
                    break
                if query.lower() == "help":
                    self.display_help()
                    continue

                result = self.process_query(query)
                print("\n📝 Response:\n" + result)
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break

def main():
    client = LangGraphServerClient()
    client.run()

if __name__ == "__main__":
    main()
