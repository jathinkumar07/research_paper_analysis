from flask import Blueprint, request, jsonify
from src.services.citations_service import validate_citations, validate
from src.services.pdf_service import extract_text_and_meta
from src.models.document import Document

citations_bp = Blueprint("citations", __name__)


@citations_bp.route("/validate", methods=["POST"])
def validate_citations_endpoint():
    """
    Validate a list of citations.
    
    POST /api/citations/validate
    
    Request body (JSON):
        - Option 1: {"citations": ["citation1", "citation2", ...]} - validate provided citations
        - Option 2: {"document_id": 123} - extract and validate citations from database document
        - Option 3: {"text": "..."} - extract and validate citations from provided text
    
    Returns:
        200: {
            "status": "success",
            "message": "Citations validated successfully", 
            "data": {
                "citations": [...],
                "total_citations": N,
                "valid_count": N,
                "invalid_count": N,
                "source": "crossref|semantic_scholar|mock"
            }
        }
        400: {"status": "error", "message": "error message", "data": None} - for validation errors
        404: {"status": "error", "message": "document not found", "data": None} - if document_id doesn't exist
        500: {"status": "error", "message": "error message", "data": None} - for server errors
    """
    try:
        # Parse JSON payload
        payload = request.get_json(force=True, silent=True) or {}
        
        citations_data = None
        source_type = None
        
        # Handle direct citations list input
        if "citations" in payload:
            citations_list = payload.get("citations")
            
            if not isinstance(citations_list, list):
                return jsonify({
                    "status": "error",
                    "message": "citations must be a list of strings",
                    "data": None
                }), 400
            
            if not citations_list:
                return jsonify({
                    "status": "success",
                    "message": "No citations provided",
                    "data": {
                        "citations": [],
                        "total_citations": 0,
                        "valid_count": 0,
                        "invalid_count": 0,
                        "source": "none"
                    }
                }), 200
            
            citations_data = validate_citations(citations_list)
            source_type = "citations_list"
        
        # Handle document_id input
        elif "document_id" in payload:
            doc_id = payload.get("document_id")
            
            if not isinstance(doc_id, int):
                return jsonify({
                    "status": "error",
                    "message": "document_id must be an integer",
                    "data": None
                }), 400
            
            # Find document in database
            document = Document.query.get(doc_id)
            if not document:
                return jsonify({
                    "status": "error",
                    "message": "document not found",
                    "data": None
                }), 404
            
            try:
                # Extract text from stored PDF file
                text, word_count, title = extract_text_and_meta(document.stored_path)
                
                if not text or len(text.strip()) < 100:
                    return jsonify({
                        "status": "error",
                        "message": "Document text too short for citation analysis",
                        "data": None
                    }), 400
                
                citations_data = validate(text)
                source_type = "document"
                    
            except Exception as e:
                return jsonify({
                    "status": "error",
                    "message": f"Failed to extract text from document: {str(e)}",
                    "data": None
                }), 500
        
        # Handle direct text input
        elif "text" in payload:
            text = payload.get("text")
            
            if not isinstance(text, str):
                return jsonify({
                    "status": "error",
                    "message": "text must be a string",
                    "data": None
                }), 400
                
            if not text or len(text.strip()) < 100:
                return jsonify({
                    "status": "error",
                    "message": "Text too short for citation analysis",
                    "data": None
                }), 400
            
            citations_data = validate(text)
            source_type = "text"
        
        # No valid input provided
        else:
            return jsonify({
                "status": "error",
                "message": "Provide either 'citations' (list), 'document_id' (integer), or 'text' (string) in JSON body",
                "data": None
            }), 400

        # Process results
        if not citations_data:
            return jsonify({
                "status": "success",
                "message": "No citations found for validation",
                "data": {
                    "citations": [],
                    "total_citations": 0,
                    "valid_count": 0,
                    "invalid_count": 0,
                    "source": "none"
                }
            }), 200

        # Count valid/invalid citations
        valid_count = 0
        invalid_count = 0
        
        for citation in citations_data:
            if source_type == "citations_list":
                # For direct citation validation
                if citation.get("valid", False):
                    valid_count += 1
                else:
                    invalid_count += 1
            else:
                # For text-based validation
                status = citation.get("status", "").lower()
                if status == "valid":
                    valid_count += 1
                else:
                    invalid_count += 1

        # Determine source API used
        from src.services.citations_service import CROSSREF_API_KEY, SEMANTIC_SCHOLAR_KEY
        if SEMANTIC_SCHOLAR_KEY:
            api_source = "semantic_scholar"
        elif CROSSREF_API_KEY:
            api_source = "crossref"
        else:
            api_source = "mock"

        return jsonify({
            "status": "success",
            "message": f"Validated {len(citations_data)} citations successfully",
            "data": {
                "citations": citations_data,
                "total_citations": len(citations_data),
                "valid_count": valid_count,
                "invalid_count": invalid_count,
                "source": api_source
            }
        }), 200
            
    except Exception as e:
        # Catch-all for unexpected errors
        return jsonify({
            "status": "error",
            "message": f"Internal server error: {str(e)}",
            "data": None
        }), 500


@citations_bp.route("/health", methods=["GET"])
def citations_health():
    """
    Health check endpoint for the citations service.
    
    Returns:
        200: {"status": "success", "message": "Citations service is running", "data": {...}}
    """
    from src.services.citations_service import CROSSREF_API_KEY, SEMANTIC_SCHOLAR_KEY
    
    # Check which APIs are configured
    configured_apis = []
    if CROSSREF_API_KEY:
        configured_apis.append("CrossRef")
    if SEMANTIC_SCHOLAR_KEY:
        configured_apis.append("Semantic Scholar")
    
    return jsonify({
        "status": "success",
        "message": "Citations service is running",
        "data": {
            "service": "citations",
            "health": "healthy",
            "configured_apis": configured_apis,
            "fallback_mode": len(configured_apis) == 0
        }
    }), 200