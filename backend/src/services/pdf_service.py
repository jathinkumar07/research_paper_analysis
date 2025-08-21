import fitz  # PyMuPDF
import re
import logging

def extract_text_from_pdf(file_path: str) -> str:
    """
    Extract text from PDF file using PyMuPDF.
    
    Args:
        file_path: Path to the PDF file
        
    Returns:
        Extracted text as a single string with extra whitespace stripped
    """
    try:
        doc = fitz.open(file_path)
        text = ""
        
        # Extract text from all pages in order
        for page in doc:
            page_text = page.get_text("text")
            if page_text.strip():  # Only add non-empty pages
                text += page_text + "\n"
        
        doc.close()
        
        # Strip extra whitespace and return
        return text.strip()
        
    except Exception as e:
        logging.error(f"Failed to extract text from PDF {file_path}: {str(e)}")
        raise Exception(f"Failed to extract text from PDF: {str(e)}")

def extract_text_and_meta(path: str) -> tuple[str, int, str|None]:
    """
    Extract text and metadata from PDF file.
    
    Returns:
        tuple: (text, word_count, title)
    """
    try:
        doc = fitz.open(path)
        text = ""
        
        # Extract text from all pages
        for page in doc:
            text += page.get_text("text") + "\n"
        
        text = text.strip()
        
        # Count words
        word_count = len(text.split()) if text else 0
        
        # Extract title - try metadata first, then first line
        title = None
        
        # Try PDF metadata
        metadata_title = doc.metadata.get("title", "").strip()
        if metadata_title and len(metadata_title) > 0:
            title = metadata_title
        else:
            # Try to extract from first few lines
            lines = text.split('\n')[:10]  # Check first 10 lines
            for line in lines:
                line = line.strip()
                # Skip empty lines, abstract headers, etc.
                if (line and 
                    len(line) > 10 and 
                    len(line) < 200 and
                    not line.lower().startswith(('abstract', 'references', 'introduction', 'keywords'))):
                    title = line
                    break
        
        doc.close()
        return text, word_count, title
        
    except Exception as e:
        raise Exception(f"Failed to extract text from PDF: {str(e)}")

def extract_references_section(text: str) -> str:
    """Extract the references section from the document text."""
    # Find references section (case insensitive)
    references_pattern = r'\b(?:references|bibliography|works\s+cited)\b'
    match = re.search(references_pattern, text, re.IGNORECASE)
    
    if match:
        # Return text from references section onwards
        return text[match.start():]
    
    return ""