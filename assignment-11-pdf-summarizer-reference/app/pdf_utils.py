import fitz  # PyMuPDF


def extract_text_from_pdf(file_path: str) -> str:
    """
    PDF file path-ah eduthukondu, ulla irukra ella pages-oda
    text-ah extract pannitu, oru single string ah return pannum.

    PyMuPDF (fitz) use pannurom - idhu malformed/corrupted PDFs-ah
    kooda PyPDF2-vida better ah handle pannum.
    """
    extracted_text = ""

    try:
        document = fitz.open(file_path)
    except Exception as e:
        raise ValueError(f"Could not read PDF file - it may be corrupted: {e}")

    if document.page_count == 0:
        document.close()
        raise ValueError("PDF file has no pages / is empty")

    for page_number in range(document.page_count):
        page = document.load_page(page_number)
        page_text = page.get_text()
        if page_text:
            extracted_text += f"\n--- Page {page_number + 1} ---\n"
            extracted_text += page_text

    document.close()

    if not extracted_text.strip():
        raise ValueError("No extractable text found in this PDF (might be a scanned image PDF)")

    return extracted_text