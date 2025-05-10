from Core.skill import Skill
from typing import Dict, Any
import os
import docx
import PyPDF2
import openpyxl


class DocumentIOSkill(Skill):
    """Skill for reading and processing documents like PDFs, Word, and Excel files."""

    def describe(self) -> Dict[str, Any]:
        return {
            "name": "document_io",
            "trigger": ["read file", "write file", "load document", "pdf", "docx", "xlsx"],
            "description": "Reads and processes documents such as PDFs, Word, and Excel files."
        }

    def handle(self, user_input: str, context: Dict[str, Any]) -> str:
        """Reads or summarizes uploaded documents based on the file type."""
        tokens = user_input.lower().split()
        if "read" in tokens and any(ext in tokens for ext in ["pdf", "docx", "xlsx"]):
            path = user_input.split()[-1]
            if not os.path.exists(path):
                return f"File not found: {path}"

            try:
                if path.endswith(".pdf"):
                    with open(path, "rb") as f:
                        reader = PyPDF2.PdfReader(f)
                        text = " ".join(page.extract_text() for page in reader.pages if page.extract_text())
                        return text[:1000] + "..."

                if path.endswith(".docx"):
                    doc = docx.Document(path)
                    return " ".join(p.text for p in doc.paragraphs)[:1000] + "..."

                if path.endswith(".xlsx"):
                    wb = openpyxl.load_workbook(path)
                    sheet = wb.active
                    content = "\n".join(
                        ", ".join(str(cell.value) for cell in row)
                        for row in sheet.iter_rows(max_row=10)
                    )
                    return content

                return "Unsupported file format."
            except Exception as e:
                return f"Error processing file: {e}"

        return "Usage: read <pdf|docx|xlsx> <filepath>"
