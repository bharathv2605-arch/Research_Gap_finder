"""
pdf_reader.py - File Reading Module
Handles reading text from PDF, TXT, and DOCX files.
Supports multiple file formats for research paper upload.
"""

import os


def read_pdf(filepath):
    """
    Extract text from a PDF file using PyPDF2.
    Args:
        filepath: Path to the PDF file
    Returns:
        Extracted text as a string
    """
    try:
        import PyPDF2
        text = ""
        with open(filepath, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            # Loop through each page and extract text
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        return text.strip()
    except Exception as e:
        print(f"[ERROR] Failed to read PDF: {e}")
        return ""


def read_txt(filepath):
    """
    Read text from a plain text file.
    Args:
        filepath: Path to the TXT file
    Returns:
        File contents as a string
    """
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as file:
            return file.read().strip()
    except Exception as e:
        print(f"[ERROR] Failed to read TXT: {e}")
        return ""


def read_docx(filepath):
    """
    Extract text from a DOCX (Word) file using python-docx.
    Args:
        filepath: Path to the DOCX file
    Returns:
        Extracted text as a string
    """
    try:
        import docx
        doc = docx.Document(filepath)
        text = ""
        # Loop through each paragraph in the document
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text.strip()
    except Exception as e:
        print(f"[ERROR] Failed to read DOCX: {e}")
        return ""


def extract_text(filepath):
    """
    Main function to extract text from any supported file format.
    Detects file type by extension and calls the appropriate reader.
    Args:
        filepath: Path to the file
    Returns:
        Extracted text as a string
    """
    # Get the file extension (lowercase)
    ext = os.path.splitext(filepath)[1].lower()

    if ext == '.pdf':
        return read_pdf(filepath)
    elif ext == '.txt':
        return read_txt(filepath)
    elif ext == '.docx':
        return read_docx(filepath)
    else:
        print(f"[ERROR] Unsupported file format: {ext}")
        return ""
