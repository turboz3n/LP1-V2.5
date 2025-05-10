from Core.skill import Skill


class Document_io(Skill):
    """"""
    def describe(self):
        return "Document io skill"


        from lp1.core.skill import Skill
        from typing import Dict, Any
        import os
        import docx, PyPDF2, openpyxl

        class DocumentIOSkill(Skill):
            def describe(self) -> Dict[str, Any]:
                return {
                    "name": "document_io",
                    "trigger": ["read file", "write file", "load document", "pdf", "docx", "xlsx"]
                }

            async def handle(self, input_text: str, state: Dict[str, Any]) -> str:
                tokens = input_text.lower().split()
                if "read" in tokens and any(ext in tokens for ext in ["pdf", "docx", "xlsx"]):
                    path = input_text.split()[-1]
                    if not os.path.exists(path):
                        return f"File not found: {path}"

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

                return "Usage: read <pdf|docx|xlsx> <filepath>"
def handle(self, user_input, context):
        """Reads or summarizes uploaded documents using simple text processing."""
        return "Document processing stub: Please upload or describe the document to parse."