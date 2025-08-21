import re
import requests
import logging
from flask import current_app
from urllib.parse import quote
import os
from dotenv import load_dotenv

load_dotenv()

def validate_citations(citations: list) -> list:
    """
    Validate citations using CrossRef API.
    
    Args:
        citations: List of citation strings
        
    Returns:
        List of dictionaries with citation, valid, and doi fields
    """
    validated_citations = []
    
    for citation_text in citations:
        if not citation_text or len(citation_text.strip()) < 10:
            continue
            
        # Clean and extract title from citation
        cleaned_title = _clean_citation_title(citation_text)
        
        # Validate using CrossRef API
        validation_result = _validate_citation_with_crossref(cleaned_title)
        
        validated_citations.append({
            "citation": citation_text,
            "valid": validation_result["valid"],
            "doi": validation_result["doi"]
        })
    
    return validated_citations

def _validate_citation_with_crossref(title: str) -> dict:
    """Validate a citation title using CrossRef API."""
    if not title or len(title.strip()) < 5:
        return {"valid": False, "doi": None}
    
    try:
        # CrossRef API endpoint
        base_url = "https://api.crossref.org/works"
        params = {
            "query": title.strip()[:200],  # Limit query length
            "rows": 1,
            "select": "title,DOI"
        }
        
        headers = {
            "User-Agent": "Research Paper Analysis Tool (mailto:your-email@example.com)"
        }
        
        response = requests.get(base_url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        if 'message' in data and 'items' in data['message'] and len(data['message']['items']) > 0:
            item = data['message']['items'][0]
            doi = item.get('DOI')
            return {"valid": True, "doi": doi}
        else:
            return {"valid": False, "doi": None}
            
    except requests.exceptions.Timeout:
        logging.warning(f"CrossRef API timeout for title: {title[:50]}...")
        return {"valid": False, "doi": None}
    except requests.exceptions.RequestException as e:
        logging.error(f"CrossRef API request error: {e}")
        return {"valid": False, "doi": None}
    except Exception as e:
        logging.error(f"Citation validation error: {e}")
        return {"valid": False, "doi": None}

def validate(full_text: str) -> list[dict]:
    """
    Extract and validate citations from document text.
    
    Args:
        full_text: Complete document text
    
    Returns:
        List of citation dictionaries with raw, cleaned_title, and status
    """
    # Extract references section
    references_text = _extract_references_section(full_text)
    
    if not references_text:
        return []
    
    # Parse individual citations
    citations = _parse_citations(references_text)
    
    # Validate each citation
    validated_citations = []
    for citation_text in citations[:50]:  # Limit to 50 citations
        if len(citation_text.strip()) < 10:  # Skip very short citations
            continue
            
        cleaned_title = _clean_citation_title(citation_text)
        status = _validate_citation_with_api(cleaned_title)
        
        validated_citations.append({
            "raw": citation_text,
            "cleaned_title": cleaned_title,
            "status": status
        })
    
    return validated_citations

def _extract_references_section(text: str) -> str:
    """Extract the references section from document text."""
    # Find references header (case insensitive)
    references_pattern = r'\b(?:references|bibliography|works\s+cited)\b'
    match = re.search(references_pattern, text, re.IGNORECASE)
    
    if not match:
        return ""
    
    # Extract text from references section onwards
    references_start = match.start()
    references_text = text[references_start:]
    
    return references_text

def _parse_citations(references_text: str) -> list[str]:
    """Parse individual citations from references section."""
    lines = references_text.split('\n')
    citations = []
    current_citation = ""
    
    for line in lines[1:]:  # Skip the "References" header line
        line = line.strip()
        
        if not line:
            # Empty line - end current citation if it exists
            if current_citation.strip():
                citations.append(current_citation.strip())
                current_citation = ""
        else:
            # Check if this line starts a new citation (common patterns)
            if _is_new_citation_start(line):
                # Save previous citation
                if current_citation.strip():
                    citations.append(current_citation.strip())
                current_citation = line
            else:
                # Continue current citation
                current_citation += " " + line
        
        # Stop if we've collected enough citations
        if len(citations) >= 50:
            break
    
    # Add the last citation if it exists
    if current_citation.strip():
        citations.append(current_citation.strip())
    
    return citations

def _is_new_citation_start(line: str) -> bool:
    """Check if a line starts a new citation."""
    line = line.strip()
    
    # Common patterns for citation starts:
    # - Starts with number: "1. ", "[1]", "(1)"
    # - Starts with author name (capital letter)
    # - After substantial whitespace from previous
    
    patterns = [
        r'^\d+\.',           # "1. "
        r'^\[\d+\]',         # "[1]"
        r'^\(\d+\)',         # "(1)"
        r'^[A-Z][a-z]+,\s*[A-Z]',  # "Author, A."
    ]
    
    for pattern in patterns:
        if re.match(pattern, line):
            return True
    
    return False

def _clean_citation_title(citation_text: str) -> str:
    """Extract and clean the title from a citation."""
    citation = citation_text.strip()
    
    # Remove common prefixes (numbers, brackets, etc.)
    citation = re.sub(r'^\d+\.\s*', '', citation)
    citation = re.sub(r'^\[\d+\]\s*', '', citation)
    citation = re.sub(r'^\(\d+\)\s*', '', citation)
    
    # Look for quoted titles first
    quoted_match = re.search(r'"([^"]+)"', citation)
    if quoted_match:
        title = quoted_match.group(1)
        if 5 < len(title) < 160:
            return title.strip()
    
    # Look for titles after author names and before publication info
    # Common pattern: Author, A. (Year). Title. Journal...
    
    # Try to find title between author and journal/conference
    # Remove author part (everything before first period after author name)
    parts = citation.split('.')
    if len(parts) >= 2:
        # Skip author part, take potential title
        for i in range(1, len(parts)):
            potential_title = parts[i].strip()
            
            # Clean up common artifacts
            potential_title = re.sub(r'^\(\d{4}\)', '', potential_title)  # Remove (year)
            potential_title = re.sub(r'^\d{4}\.?', '', potential_title)   # Remove year
            potential_title = potential_title.strip()
            
            # Check if this looks like a title
            if 5 < len(potential_title) < 160 and not _looks_like_journal_info(potential_title):
                return potential_title
    
    # Fallback: take first substantial part after cleaning
    cleaned = re.sub(r'[^\w\s]', ' ', citation)  # Remove punctuation
    words = cleaned.split()
    
    # Skip author-like words at the beginning
    start_idx = 0
    for i, word in enumerate(words[:5]):  # Check first 5 words
        if len(word) == 1 or (len(word) == 2 and word.endswith('.')):
            # Looks like initials, skip
            start_idx = i + 1
        elif word.isdigit() or (word.startswith('(') and word.endswith(')')):
            # Year or similar, skip
            start_idx = i + 1
        else:
            break
    
    # Take next 5-15 words as potential title
    title_words = words[start_idx:start_idx + 15]
    title = ' '.join(title_words)
    
    if 5 < len(title) < 160:
        return title.strip()
    
    # Ultimate fallback: first part of original citation
    fallback = citation[:100].strip()
    return fallback if len(fallback) > 5 else citation[:50]

def _looks_like_journal_info(text: str) -> bool:
    """Check if text looks like journal/conference information."""
    journal_indicators = [
        'journal', 'proceedings', 'conference', 'vol', 'volume', 
        'pp', 'pages', 'doi', 'isbn', 'issn', 'retrieved'
    ]
    
    text_lower = text.lower()
    return any(indicator in text_lower for indicator in journal_indicators)

def _validate_citation_with_api(title: str) -> str:
    """Validate a citation title using Semantic Scholar API."""
    if not title or len(title.strip()) < 5:
        return "Error"
    
    try:
        base_url = current_app.config.get('SEMANTIC_SCHOLAR_BASE')
        fields = current_app.config.get('SEMANTIC_SCHOLAR_FIELDS')
        
        # Clean title for API query
        query = title.strip()[:200]  # Limit query length
        encoded_query = quote(query)
        
        url = f"{base_url}?query={encoded_query}&limit=1&fields={fields}"
        
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        if 'data' in data and len(data['data']) > 0:
            return "Valid"
        else:
            return "Not Found"
            
    except requests.exceptions.Timeout:
        return "API Timeout"
    except requests.exceptions.RequestException as e:
        print(f"API request error: {e}")
        return "Error"
    except Exception as e:
        print(f"Citation validation error: {e}")
        return "Error"