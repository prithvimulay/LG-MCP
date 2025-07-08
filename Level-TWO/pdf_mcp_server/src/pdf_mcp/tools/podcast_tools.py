"""
MCP tools for podcast generation
"""

from mcp.server.fastmcp import FastMCP
from ..podcast.agent import PodcastAgent

# Initialize podcast agent
podcast_agent = PodcastAgent()

def register_podcast_tools(mcp: FastMCP):
    """Register podcast tools with FastMCP server"""

    @mcp.tool()
    async def generate_podcast(question: str, style: str = "interview") -> str:
        """Generate a podcast from selected PDFs based on your question. 
        
        Args:
            question: The topic or question for the podcast
            style: Podcast style - 'interview' or 'educational'
        """
        try:
            result = podcast_agent.create_podcast_from_query(
                question=question,
                style=style.lower(),
                generate_audio=True
            )
            
            if not result["success"]:
                return f"❌ {result['message']}"
            
            # Format response
            response_parts = [
                f"🎙️ **Podcast Generated Successfully!**\n",
                f"📝 **Topic:** {result['topic']}",
                f"🎨 **Style:** {result['style'].title()}",
                f"📚 **Sources:** {', '.join(result['sources'])}",
                f"📊 **Content:** Used {result['chunks_used']} text chunks\n"
            ]
            
            if "audio_path" in result:
                response_parts.append(f"🔊 **Audio:** {result['audio_filename']}")
                response_parts.append(f"📄 **Script:** {result.get('script_path', 'Saved')}")
            else:
                response_parts.append("📝 **Script only** (audio generation failed)")
            
            response_parts.append(f"\n✅ {result['message']}")
            
            # Include a preview of the script
            script_preview = result['script'][:500] + "..." if len(result['script']) > 500 else result['script']
            response_parts.append(f"\n📜 **Script Preview:**\n```\n{script_preview}\n```")
            
            return "\n".join(response_parts)
            
        except Exception as e:
            return f"❌ Error generating podcast: {str(e)}"

    @mcp.tool()
    async def list_podcast_styles() -> str:
        """List available podcast styles"""
        try:
            styles = podcast_agent.get_podcast_styles()
            
            response_parts = [
                "🎙️ **Available Podcast Styles:**\n"
            ]
            
            for style in styles:
                if style == "interview":
                    response_parts.append("🗣️ **Interview** - Conversational format between Host and Expert")
                elif style == "educational":
                    response_parts.append("📚 **Educational** - Structured learning content with Narrator")
                else:
                    response_parts.append(f"🎨 **{style.title()}** - {style} style podcast")
            
            response_parts.append("\n💡 **Usage:** Use `generate_podcast(question=\"your topic\", style=\"interview\")` to create a podcast")
            
            return "\n".join(response_parts)
            
        except Exception as e:
            return f"❌ Error listing styles: {str(e)}"

    @mcp.tool()
    async def test_podcast_llm() -> str:
        """Test the LLM connection for podcast generation"""
        try:
            result = podcast_agent.test_llm_connection()
            
            if result["success"]:
                return f"✅ **LLM Connection Successful**\n🤖 Model: {result.get('model', 'qwen-qwq-32b')}\n💬 Response: {result.get('response', 'Working correctly')}"
            else:
                return f"❌ **LLM Connection Failed**\n🔧 Error: {result['message']}\n\n💡 **Fix:** Set GROQ_API_KEY environment variable"
                
        except Exception as e:
            return f"❌ Error testing LLM: {str(e)}\n\n💡 **Tip:** Make sure GROQ_API_KEY is set and langchain-groq is installed"
