import pdfplumber

def extract_text_from_pdf(pdf_path: str) -> str:
    """Extracts text from a PDF file."""
    with pdfplumber.open(pdf_path) as pdf:
        text = "\n".join([page.extract_text() for page in pdf.pages if page.extract_text()])
    return text