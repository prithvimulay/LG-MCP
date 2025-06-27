from langchain_community.utilities import WikipediaAPIWrapper
from langchain_community.tools import WikipediaQueryRun

wiki_api = WikipediaAPIWrapper(top_k_results=2, doc_content_chars_max=500)
wiki_tool = WikipediaQueryRun(api_wrapper=wiki_api, description="Query Wikipedia for general knowledge")
