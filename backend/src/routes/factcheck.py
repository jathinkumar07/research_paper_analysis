"""
Fact-check routes blueprint.

Provides REST endpoints for fact-checking documents and text.
"""

from flask import Blueprint, request, jsonify
import logging
from marshmallow import Schema, fields, ValidationError
from src.services.factcheck_service import extract_claims, fact_check_claims, get_factcheck_status
from src.services.pdf_service import extract_text_and_meta
from src.models.document import Document
from src.extensions import db

logger = logging.getLogger(__name__)

# Create blueprint
factcheck_bp = Blueprint("factcheck", __name__)


class FactCheckRequestSchema(Schema):
    """Schema for fact-check request validation."""
    document_id = fields.Int(required=False)
    text = fields.Str(required=False)
    
    def validate_request(self, data, **kwargs):
        """Custom validation to ensure either document_id or text is provided."""
        if not data.get('document_id') and not data.get('text'):
            raise ValidationError("Provide either 'document_id' or 'text' in request body")


@factcheck_bp.route("/run", methods=["POST"])
def run_factcheck():
    """
    Run fact-check analysis on document or text.
    
    POST /api/factcheck/run
    
    Request body (JSON):
        - { "document_id": 123 } - Fact-check document from database
        - { "text": "..." } - Fact-check provided text
    
    Returns:
        200: {
            "claims": [
                {
                    "claim": "original sentence",
                    "status": "verified|contradicted|no_verdict|api_error|not_configured",
                    "fact_checks": [...],
                    "error": "error message if any"
                }
            ],
            "source": "google_factcheck",
            "total_claims": 5,
            "processing_time": 2.34
        }
        400: Invalid request
        404: Document not found
        500: Server error
    """
    import time
    start_time = time.time()
    
    try:
        # Validate request
        schema = FactCheckRequestSchema()
        try:
            payload = request.get_json(force=True, silent=True) or {}
            data = schema.load(payload)
            schema.validate_request(data)
        except ValidationError as err:
            return jsonify({
                "error": "Invalid request", 
                "details": err.messages
            }), 400
        
        # Extract text from source
        text = None
        source_info = {}
        
        if "document_id" in payload:
            document_id = payload.get("document_id")
            
            # Find document in database
            document = Document.query.get(document_id)
            if not document:
                return jsonify({"error": "Document not found"}), 404
            
            try:
                # Extract text from stored PDF
                text, word_count, title = extract_text_and_meta(document.stored_path)
                source_info = {
                    "source_type": "document",
                    "document_id": document_id,
                    "filename": document.filename,
                    "title": title,
                    "word_count": word_count
                }
                logger.info(f"Extracted text from document {document_id}: {word_count} words")
                
            except Exception as e:
                logger.error(f"Failed to extract text from document {document_id}: {e}")
                return jsonify({
                    "error": "Failed to extract text from document",
                    "details": str(e)
                }), 500
                
        elif "text" in payload:
            text = payload.get("text")
            source_info = {
                "source_type": "text",
                "text_length": len(text) if text else 0
            }
            logger.info(f"Using provided text: {len(text) if text else 0} characters")
        
        # Validate text content
        if not text or not text.strip():
            return jsonify({"error": "No text content to fact-check"}), 400
        
        if len(text.strip()) < 50:
            return jsonify({"error": "Text too short for fact-checking (minimum 50 characters)"}), 400
        
        # Extract claims from text
        logger.info("Extracting claims from text...")
        claims = extract_claims(text)
        
        if not claims:
            return jsonify({
                "claims": [],
                "source": "google_factcheck",
                "total_claims": 0,
                "processing_time": time.time() - start_time,
                "message": "No factual claims found in the text",
                **source_info
            }), 200
        
        logger.info(f"Found {len(claims)} potential claims")
        
        # Fact-check the claims
        logger.info("Starting fact-check process...")
        fact_check_results = fact_check_claims(claims)
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        # Prepare response
        response = {
            "claims": fact_check_results,
            "source": "google_factcheck",
            "total_claims": len(fact_check_results),
            "processing_time": round(processing_time, 2),
            **source_info
        }
        
        # Add summary statistics
        status_counts = {}
        for result in fact_check_results:
            status = result["status"]
            status_counts[status] = status_counts.get(status, 0) + 1
        
        response["status_summary"] = status_counts
        
        logger.info(f"Fact-check completed: {len(fact_check_results)} claims processed in {processing_time:.2f}s")
        
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Unexpected error in fact-check endpoint: {e}")
        return jsonify({
            "error": "Internal server error",
            "details": "An unexpected error occurred during fact-checking"
        }), 500


@factcheck_bp.route("/status", methods=["GET"])
def get_status():
    """
    Get fact-check service status and configuration.
    
    GET /api/factcheck/status
    
    Returns:
        200: {
            "service_enabled": true,
            "auth_method": "api_key",
            "configuration_valid": true,
            "service_account_available": false,
            "api_key_available": true
        }
    """
    try:
        status = get_factcheck_status()
        return jsonify(status), 200
    except Exception as e:
        logger.error(f"Error getting fact-check status: {e}")
        return jsonify({
            "error": "Failed to get service status",
            "details": str(e)
        }), 500


@factcheck_bp.route("/test", methods=["POST"])
def test_factcheck():
    """
    Test fact-check service with a simple claim.
    
    POST /api/factcheck/test
    
    Request body (JSON):
        { "claim": "The Earth is round" }
    
    Returns:
        200: Fact-check result for the test claim
        400: Invalid request
        500: Server error
    """
    try:
        payload = request.get_json(force=True, silent=True) or {}
        claim = payload.get("claim")
        
        if not claim:
            return jsonify({"error": "Provide 'claim' in request body"}), 400
        
        logger.info(f"Testing fact-check with claim: {claim[:50]}...")
        
        # Fact-check the single claim
        results = fact_check_claims([claim])
        
        if results:
            result = results[0]
            return jsonify({
                "test_claim": claim,
                "result": result,
                "service_status": get_factcheck_status()
            }), 200
        else:
            return jsonify({
                "error": "No results returned from fact-check service"
            }), 500
            
    except Exception as e:
        logger.error(f"Error in fact-check test endpoint: {e}")
        return jsonify({
            "error": "Test failed",
            "details": str(e)
        }), 500


# Error handlers for the blueprint
@factcheck_bp.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({"error": "Endpoint not found"}), 404


@factcheck_bp.errorhandler(405)
def method_not_allowed(error):
    """Handle 405 errors."""
    return jsonify({"error": "Method not allowed"}), 405


@factcheck_bp.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    logger.error(f"Internal server error in fact-check blueprint: {error}")
    return jsonify({"error": "Internal server error"}), 500