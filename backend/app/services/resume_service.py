import pymupdf as fitz
from fastapi import HTTPException, status

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB limit

def extract_text_from_pdf(file_bytes: bytes, filename: str) -> str:
    """
    Validates PDF file bytes and extracts clean text page by page using PyMuPDF.
    """
    if not file_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The uploaded file is empty."
        )

    if len(file_bytes) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File size exceeds maximum allowed limit of {MAX_FILE_SIZE // (1024 * 1024)} MB."
        )

    if not filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file extension. Only PDF files are allowed."
        )

    try:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or corrupted PDF file."
        )

    if doc.page_count == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="PDF file contains no pages."
        )

    extracted_pages = []
    for page_num in range(doc.page_count):
        page = doc.load_page(page_num)
        text = page.get_text("text")
        if text:
            extracted_pages.append(text.strip())

    doc.close()

    full_text = "\n\n".join(extracted_pages).strip()

    if not full_text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No readable text could be extracted from the PDF. Scanned images without OCR are not supported."
        )

    return full_text
