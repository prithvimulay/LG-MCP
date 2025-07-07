from mcp.server.fastmcp import FastMCP
from ..pdf.manager import PDFManager

# Initialize PDF manager
pdf_manager = PDFManager()

def register_tools(mcp: FastMCP):
    """Register all PDF tools with FastMCP server"""

    @mcp.tool()
    async def upload_pdfs() -> str:
        """Scan and process PDFs in the data/pdfs/ directory"""
        try:
            processed_files = pdf_manager.scan_and_process_pdfs()
            if processed_files:
                return f"✅ Processed {len(processed_files)} new PDFs: {', '.join(processed_files)}"
            else:
                return "ℹ️ No new PDFs found in data/pdfs/ directory"
        except Exception as e:
            return f"❌ Error processing PDFs: {str(e)}"

    @mcp.tool()
    async def list_pdfs() -> str:
        """List all available PDFs with their selection status"""
        try:
            all_pdfs = pdf_manager.mongo.get_all_pdfs()
            if not all_pdfs:
                return "📂 No PDFs available. Place PDF files in data/pdfs/ and run 'upload_pdfs'"

            pdf_list = ["📚 **Available PDFs:**\n"]
            for i, pdf in enumerate(all_pdfs, 1):
                status = "✅" if pdf.is_selected else "⬜"
                size_mb = pdf.file_size / (1024 * 1024)
                pdf_list.append(
                    f"{i}. {status} **{pdf.filename}** "
                    f"({pdf.page_count} pages, {size_mb:.1f}MB, {pdf.chunk_count} chunks)"
                )

            selected_count = len([pdf for pdf in all_pdfs if pdf.is_selected])
            pdf_list.append(f"\n📊 **Selected:** {selected_count}/{len(all_pdfs)} PDFs")

            return "\n".join(pdf_list)
        except Exception as e:
            return f"❌ Error listing PDFs: {str(e)}"

    @mcp.tool()
    async def select_pdfs(pdf_identifiers: str) -> str:
        """Select PDFs for querying. Use PDF numbers (from list_pdfs) or filenames, separated by commas"""
        try:
            identifiers = [id.strip() for id in pdf_identifiers.split(",")]
            selected_names = pdf_manager.select_pdfs(identifiers)

            if selected_names:
                return f"✅ Selected PDFs: {', '.join(selected_names)}"
            else:
                return "⚠️ No PDFs were selected. Check PDF identifiers and try again."
        except Exception as e:
            return f"❌ Error selecting PDFs: {str(e)}"

    @mcp.tool()
    async def deselect_pdfs(pdf_identifiers: str) -> str:
        """Deselect PDFs. Use PDF numbers (from list_pdfs) or filenames, separated by commas"""
        try:
            identifiers = [id.strip() for id in pdf_identifiers.split(",")]
            deselected_names = pdf_manager.deselect_pdfs(identifiers)

            if deselected_names:
                return f"➖ Deselected PDFs: {', '.join(deselected_names)}"
            else:
                return "⚠️ No PDFs were deselected. Check PDF identifiers and try again."
        except Exception as e:
            return f"❌ Error deselecting PDFs: {str(e)}"

    @mcp.tool()
    async def query_pdfs(question: str) -> str:
        """Search through selected PDFs for information related to your question"""
        try:
            result = pdf_manager.query_selected_pdfs(question)

            if not result["success"]:
                return result["message"]

            if not result["results"]:
                return "🔍 No relevant information found in the selected PDFs for your question."

            # Format response
            response_parts = [
                f"🎯 **Query Results** (from {len(result['sources'])} selected PDFs):\n"
            ]

            for i, chunk in enumerate(result["results"], 1):
                content = chunk["content"]
                pdf_id = chunk["metadata"]["pdf_id"]

                # Find PDF filename
                pdf_name = "Unknown PDF"
                for source in result["sources"]:
                    if pdf_id in source or source in pdf_id:
                        pdf_name = source
                        break

                response_parts.append(f"**{i}. From {pdf_name}:**")
                response_parts.append(content.strip())
                response_parts.append("")  # Empty line

            response_parts.append(f"📚 **Sources:** {', '.join(result['sources'])}")
            response_parts.append(f"🔍 **Note:** Results are based solely on the content of selected PDFs.")

            return "\n".join(response_parts)

        except Exception as e:
            return f"❌ Error querying PDFs: {str(e)}"

    @mcp.tool()
    async def clear_selection() -> str:
        """Clear all PDF selections"""
        try:
            pdf_manager.mongo.clear_all_selections()
            return "🗑️ All PDF selections cleared"
        except Exception as e:
            return f"❌ Error clearing selections: {str(e)}"
