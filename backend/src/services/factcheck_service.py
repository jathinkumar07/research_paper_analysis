"""
Fact-checking service using Google Fact Check Tools API.

Environment variables:
- GOOGLE_FACTCHECK_SERVICE_ACCOUNT_FILE: Path to JSON service account file
- GOOGLE_API_KEY: Simple API key for REST endpoint access
- FACTCHECK_USE: "service_account" | "api_key" | "disabled"
- FACTCHECK_TIMEOUT: API timeout in seconds (default: 8.0)
- FACTCHECK_MAX_RETRIES: Maximum retry attempts (default: 3)
- FACTCHECK_DELAY: Delay between API calls in seconds (default: 0.5)
"""

import os
import time
import requests
import logging
from typing import List, Dict, Optional
import nltk

# Download punkt tokenizer if not already present
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)

# Also try punkt_tab for newer NLTK versions
try:
    nltk.data.find('tokenizers/punkt_tab')
except LookupError:
    try:
        nltk.download('punkt_tab', quiet=True)
    except:
        pass  # Fallback to punkt if punkt_tab not available

logger = logging.getLogger(__name__)

# Environment configuration
GOOGLE_SERVICE_ACCOUNT_FILE = os.getenv("GOOGLE_FACTCHECK_SERVICE_ACCOUNT_FILE")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
FACTCHECK_USE = os.getenv("FACTCHECK_USE", "api_key")  # service_account | api_key | disabled
FACTCHECK_TIMEOUT = float(os.getenv("FACTCHECK_TIMEOUT", "8.0"))
MAX_RETRIES = int(os.getenv("FACTCHECK_MAX_RETRIES", "3"))
DELAY_BETWEEN_CALLS = float(os.getenv("FACTCHECK_DELAY", "0.5"))


def extract_claims(text: str) -> List[str]:
    """
    Extract candidate claim sentences from text.
    
    Uses NLTK sentence tokenization and filters out short sentences
    that are unlikely to be factual claims.
    
    Args:
        text: Input text to extract claims from
        
    Returns:
        List of candidate claim sentences (max 20)
    """
    if not text or not text.strip():
        return []
    
    try:
        # Split text into sentences
        sentences = nltk.tokenize.sent_tokenize(text)
        
        # Filter sentences to find potential claims
        claims = []
        for sentence in sentences:
            sentence = sentence.strip()
            
            # Skip very short sentences (likely not factual claims)
            if len(sentence) < 40:
                continue
                
            # Skip questions and commands
            if sentence.endswith('?') or sentence.startswith(('How', 'What', 'Why', 'Where', 'When')):
                continue
                
            # Skip sentences that are likely headers or references
            if sentence.isupper() or sentence.startswith(('Figure', 'Table', 'References')):
                continue
                
            claims.append(sentence)
            
            # Limit to first 20 potential claims to avoid API quota issues
            if len(claims) >= 20:
                break
                
        logger.info(f"Extracted {len(claims)} potential claims from {len(sentences)} sentences")
        return claims
        
    except Exception as e:
        logger.error(f"Error extracting claims: {e}")
        return []


def _call_google_factcheck_rest(query: str) -> Dict:
    """
    Call Google Fact Check Tools API using REST endpoint with API key.
    
    Args:
        query: The claim to fact-check
        
    Returns:
        API response as dictionary
        
    Raises:
        RuntimeError: If API key not configured
        requests.RequestException: If API call fails after retries
    """
    api_key = GOOGLE_API_KEY
    if not api_key:
        raise RuntimeError("GOOGLE_API_KEY not configured")
        
    url = "https://factchecktools.googleapis.com/v1alpha1/claims:search"
    params = {
        "query": query[:500],  # Limit query length
        "key": api_key
    }
    
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            logger.debug(f"Fact-check API call attempt {attempt} for query: {query[:50]}...")
            response = requests.get(url, params=params, timeout=FACTCHECK_TIMEOUT)
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.Timeout:
            logger.warning(f"Fact-check API timeout on attempt {attempt}")
            if attempt < MAX_RETRIES:
                time.sleep(0.5 * attempt)
            else:
                raise
                
        except requests.exceptions.RequestException as e:
            logger.warning(f"Fact-check API error on attempt {attempt}: {e}")
            if attempt < MAX_RETRIES:
                time.sleep(0.5 * attempt)
            else:
                raise


def _call_google_factcheck_service_account(service, query: str) -> Dict:
    """
    Call Google Fact Check Tools API using service account credentials.
    
    Args:
        service: Authenticated Google API client service
        query: The claim to fact-check
        
    Returns:
        API response as dictionary
    """
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            logger.debug(f"Fact-check service account call attempt {attempt} for query: {query[:50]}...")
            request = service.claims().search(query=query[:500])
            response = request.execute()
            return response
            
        except Exception as e:
            logger.warning(f"Fact-check service account error on attempt {attempt}: {e}")
            if attempt < MAX_RETRIES:
                time.sleep(0.5 * attempt)
            else:
                raise


def _normalize_fact_check_result(claim: str, api_response: Dict) -> Dict:
    """
    Normalize API response into standard format.
    
    Args:
        claim: Original claim text
        api_response: Raw API response
        
    Returns:
        Normalized result dictionary
    """
    fact_checks = api_response.get("claims", []) if isinstance(api_response, dict) else []
    
    # Determine status based on fact-check results
    status = "no_verdict"
    if fact_checks:
        # Simple heuristic: if we have fact-checks, we can't automatically determine
        # verified/contradicted without analyzing the content, so we default to no_verdict
        # In a production system, you might want to analyze the claimReview ratings
        status = "no_verdict"
        
        # Optional: Try to determine status from claimReview ratings
        for fact_check in fact_checks:
            claim_review = fact_check.get("claimReview", [])
            for review in claim_review:
                rating = review.get("textualRating", "").lower()
                if any(word in rating for word in ["true", "correct", "accurate"]):
                    status = "verified"
                    break
                elif any(word in rating for word in ["false", "incorrect", "misleading"]):
                    status = "contradicted"
                    break
    
    return {
        "claim": claim,
        "status": status,
        "fact_checks": fact_checks,
        "error": None
    }


def fact_check_claims(claims: List[str]) -> List[Dict]:
    """
    Fact-check a list of claims using Google Fact Check Tools API.
    
    Supports two authentication modes:
    1. Service account JSON file (GOOGLE_FACTCHECK_SERVICE_ACCOUNT_FILE)
    2. Simple API key (GOOGLE_API_KEY)
    
    Args:
        claims: List of claim strings to fact-check
        
    Returns:
        List of normalized fact-check results, one per claim:
        {
            "claim": "<original sentence>",
            "status": "verified" | "contradicted" | "no_verdict" | "api_error" | "not_configured",
            "fact_checks": [ { "text": "...", "claimReview": {...}, "url": "..." } ... ],
            "error": "<error message if any>"
        }
    """
    results = []
    
    if not claims:
        return results
        
    # Check configuration
    use_service_account = bool(
        GOOGLE_SERVICE_ACCOUNT_FILE and 
        os.path.exists(GOOGLE_SERVICE_ACCOUNT_FILE) and 
        FACTCHECK_USE == "service_account"
    )
    use_api_key = bool(GOOGLE_API_KEY and FACTCHECK_USE == "api_key")
    
    # If disabled or not configured, return not_configured for all claims
    if FACTCHECK_USE == "disabled" or (not use_service_account and not use_api_key):
        error_msg = "Google Fact Check not configured. Set GOOGLE_FACTCHECK_SERVICE_ACCOUNT_FILE or GOOGLE_API_KEY in .env"
        if FACTCHECK_USE == "disabled":
            error_msg = "Fact-checking is disabled via FACTCHECK_USE=disabled"
            
        for claim in claims:
            results.append({
                "claim": claim,
                "status": "not_configured",
                "fact_checks": [],
                "error": error_msg
            })
        return results
    
    # Initialize API client if using service account
    service = None
    call_mode = "api_key"  # Default to API key
    
    if use_service_account:
        try:
            from google.oauth2 import service_account
            from googleapiclient.discovery import build
            
            credentials = service_account.Credentials.from_service_account_file(
                GOOGLE_SERVICE_ACCOUNT_FILE,
                scopes=['https://www.googleapis.com/auth/factchecktools']
            )
            service = build("factchecktools", "v1alpha1", credentials=credentials, cache_discovery=False)
            call_mode = "service_account"
            logger.info("Using service account authentication for fact-checking")
            
        except Exception as e:
            logger.error(f"Failed to initialize service account authentication: {e}")
            # Fallback to API key if available
            if not use_api_key:
                for claim in claims:
                    results.append({
                        "claim": claim,
                        "status": "api_error",
                        "fact_checks": [],
                        "error": f"Service account initialization error: {e}"
                    })
                return results
            call_mode = "api_key"
            logger.info("Falling back to API key authentication")
    
    if call_mode == "api_key":
        logger.info("Using API key authentication for fact-checking")
    
    # Process each claim
    for i, claim in enumerate(claims):
        # Add delay between calls to respect API limits
        if i > 0:
            time.sleep(DELAY_BETWEEN_CALLS)
            
        try:
            logger.debug(f"Fact-checking claim {i+1}/{len(claims)}: {claim[:50]}...")
            
            # Make API call based on authentication method
            if call_mode == "service_account":
                api_response = _call_google_factcheck_service_account(service, claim)
            else:
                api_response = _call_google_factcheck_rest(claim)
            
            # Normalize the response
            result = _normalize_fact_check_result(claim, api_response)
            results.append(result)
            
            logger.debug(f"Fact-check completed for claim {i+1}: status={result['status']}")
            
        except Exception as e:
            logger.error(f"Fact-check API error for claim: {claim[:50]}... - Error: {e}")
            results.append({
                "claim": claim,
                "status": "api_error",
                "fact_checks": [],
                "error": str(e)
            })
    
    logger.info(f"Completed fact-checking {len(claims)} claims")
    return results


def get_factcheck_status() -> Dict:
    """
    Get the current fact-check service configuration status.
    
    Returns:
        Dictionary with configuration status information
    """
    status = {
        "service_enabled": FACTCHECK_USE != "disabled",
        "auth_method": FACTCHECK_USE,
        "service_account_available": bool(
            GOOGLE_SERVICE_ACCOUNT_FILE and os.path.exists(GOOGLE_SERVICE_ACCOUNT_FILE)
        ),
        "api_key_available": bool(GOOGLE_API_KEY),
        "configuration_valid": False
    }
    
    if FACTCHECK_USE == "service_account":
        status["configuration_valid"] = status["service_account_available"]
    elif FACTCHECK_USE == "api_key":
        status["configuration_valid"] = status["api_key_available"]
    elif FACTCHECK_USE == "disabled":
        status["configuration_valid"] = True
    
    return status