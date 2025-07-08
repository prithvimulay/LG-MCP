"""
Podcast agent that orchestrates PDF-to-podcast conversion
"""

from typing import List, Dict, Any
from ..pdf.manager import PDFManager
from .processor import SimplePodcastProcessor

class PodcastAgent:
    """Agent that handles the complete PDF-to-podcast workflow"""
    
    def __init__(self):
        self.pdf_manager = PDFManager()
        self.processor = SimplePodcastProcessor()
    
    def create_podcast_from_query(self, 
                                 question: str, 
                                 style: str = "interview",
                                 generate_audio: bool = True) -> Dict[str, Any]:
        """Create podcast from PDF query"""
        
        try:
            # Step 1: Query selected PDFs
            query_result = self.pdf_manager.query_selected_pdfs(question)
            
            if not query_result["success"] or not query_result["results"]:
                return {
                    "success": False,
                    "message": query_result.get("message", "No content found for podcast generation")
                }
            
            # Step 2: Generate podcast script
            script_result = self.processor.generate_podcast(
                content_chunks=query_result["results"],
                style=style,
                topic=question
            )
            
            if not script_result["success"]:
                return {
                    "success": False,
                    "message": f"Failed to generate script: {script_result.get('error', 'Unknown error')}"
                }
            
            result = {
                "success": True,
                "script": script_result["script"],
                "topic": question,
                "style": style,
                "sources": query_result["sources"],
                "chunks_used": script_result["chunks_used"]
            }
            
            # Step 3: Generate audio if requested
            if generate_audio:
                audio_result = self.processor.generate_audio(
                    script=script_result["script"],
                    filename=f"podcast_{style}"
                )
                
                if audio_result["success"]:
                    result["audio_path"] = audio_result["audio_path"]
                    result["audio_filename"] = audio_result["filename"]
                    
                    # Step 4: Save both files
                    save_result = self.processor.save_podcast_files(
                        script=script_result["script"],
                        audio_path=audio_result["audio_path"],
                        topic=question,
                        style=style
                    )
                    
                    if save_result["success"]:
                        result["script_path"] = save_result["script_path"]
                        result["message"] = "Podcast created successfully with audio"
                    else:
                        result["message"] = "Podcast created but failed to save files"
                else:
                    result["audio_error"] = audio_result.get("error", "Audio generation failed")
                    result["message"] = "Podcast script created, but audio generation failed"
            else:
                result["message"] = "Podcast script created successfully"
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Error creating podcast: {str(e)}",
                "error": str(e)
            }
    
    def get_podcast_styles(self) -> List[str]:
        """Get available podcast styles"""
        return ["interview", "educational"]
    
    def test_llm_connection(self) -> Dict[str, Any]:
        """Test LLM connection"""
        try:
            from ..langchain_integration import langchain_manager
            return langchain_manager.test_connection()
        except Exception as e:
            return {
                "success": False,
                "message": f"LLM test failed: {str(e)}"
            }
