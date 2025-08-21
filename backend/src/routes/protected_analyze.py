from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import os
import tempfile
import logging
from src.extensions import db
from src.models.user import User
from src.models.document import Document
from src.models.analysis import Analysis
from src.models.citation import Citation

# Import real services only - no more mock fallbacks
from src.services.pdf_service import extract_text_and_meta
from src.services.summarizer_service import summarize
from src.services.plagiarism_service import check_plagiarism, check
from src.services.citations_service import validate as validate_citations
from src.services.factcheck_service import extract_claims, fact_check_claims

logger = logging.getLogger(__name__)

# Create blueprint for protected analysis (requires authentication)
protected_analyze_bp = Blueprint('protected_analyze', __name__, url_prefix='/api/analyze')

@protected_analyze_bp.route('/upload', methods=['POST'])
@jwt_required()
def analyze_and_save():
    """
    Authenticated document analysis endpoint that saves results to database.
    
    POST /api/analyze/upload
    
    Form data:
        - file: PDF file to analyze
    
    Returns:
        200: Analysis results with saved record ID
        400: Validation error
        401: Authentication required
        500: Server error
    """
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        if not current_user:
            return jsonify({'error': 'User not found'}), 404
        
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Validate file type
        if not file.filename.lower().endswith('.pdf'):
            return jsonify({'error': 'Only PDF files are allowed'}), 400
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            file.save(temp_file.name)
            temp_path = temp_file.name
        
        try:
            # Extract text and metadata
            text, word_count, title = extract_text_and_meta(temp_path)
            
            if not text or len(text.strip()) < 100:
                return jsonify({'error': 'Document text too short for analysis'}), 400
            
            # Create document record
            document = Document(
                user_id=current_user_id,
                filename=file.filename,
                stored_path=temp_path,  # In production, move to permanent storage
                title=title or file.filename,
                extracted_text=text,
                word_count=word_count
            )
            
            db.session.add(document)
            db.session.flush()  # Get the document ID
            
            # Run analysis pipeline
            logger.info(f"Starting analysis for user {current_user.email}: {file.filename}")
            
            # Initialize default values
            summary = "Analysis failed to generate summary."
            plagiarism_result = {"plagiarism_score": 0.0, "matching_sources": []}
            citation_results = []
            fact_check_results = []
            
            # 1. Summarization
            logger.info("Running summarization...")
            try:
                summary = summarize(text)
                logger.info("Summarization completed successfully")
            except Exception as e:
                logger.error(f"Summarization failed: {e}")
                summary = "Unable to generate summary due to processing error."
            
            # 2. Plagiarism detection
            logger.info("Running plagiarism check...")
            try:
                plagiarism_result = check_plagiarism(text)
                if isinstance(plagiarism_result, dict):
                    # New format with details
                    plagiarism_score = plagiarism_result.get('plagiarism_score', 0.0)
                else:
                    # Fallback to simple check function
                    plagiarism_score = check(text) / 100.0  # Convert percentage to decimal
                    plagiarism_result = {"plagiarism_score": plagiarism_score, "matching_sources": []}
                
                logger.info(f"Plagiarism check completed: {plagiarism_result.get('plagiarism_score', 0)}%")
            except Exception as e:
                logger.error(f"Plagiarism check failed: {e}")
                plagiarism_result = {"plagiarism_score": 0.0, "matching_sources": []}
            
            # 3. Citation validation
            logger.info("Validating citations...")
            try:
                citation_results = validate_citations(text)
                logger.info(f"Citation validation completed: {len(citation_results)} citations found")
            except Exception as e:
                logger.error(f"Citation validation failed: {e}")
                citation_results = []
            
            # 4. Fact checking
            logger.info("Running fact check...")
            try:
                claims = extract_claims(text)
                fact_check_results = fact_check_claims(claims) if claims else []
                logger.info(f"Fact checking completed: {len(fact_check_results)} claims checked")
            except Exception as e:
                logger.error(f"Fact check failed: {e}")
                fact_check_results = []
            
            # Create analysis record
            analysis = Analysis(
                document_id=document.id,
                summary=summary,
                plagiarism_score=plagiarism_result.get('plagiarism_score', 0.0),
                plagiarism_details=plagiarism_result.get('matching_sources', []),
                fact_check_results=fact_check_results
            )
            
            db.session.add(analysis)
            
            # Save citation records
            for citation_data in citation_results:
                citation = Citation(
                    analysis_id=analysis.id,
                    raw_text=citation_data.get('raw', citation_data.get('reference', '')),
                    cleaned_title=citation_data.get('cleaned_title', ''),
                    doi=citation_data.get('doi'),
                    status='verified' if citation_data.get('valid', False) else 'unverified'
                )
                db.session.add(citation)
            
            # Commit all changes
            db.session.commit()
            
            logger.info(f"Analysis completed and saved for user {current_user.email}: {file.filename}")
            
            # Format response for frontend compatibility
            formatted_citations = []
            for citation in citation_results:
                formatted_citations.append({
                    "reference": citation.get('raw', citation.get('cleaned_title', 'Unknown citation')),
                    "valid": citation.get('valid', False)
                })
            
            formatted_facts = []
            for fact in fact_check_results:
                formatted_facts.append({
                    "claim": fact.get('claim', 'Unknown claim'),
                    "status": "Verified" if fact.get('status') == 'verified' else "Unverified"
                })
            
            # Return results with database IDs
            return jsonify({
                'analysis_id': analysis.id,
                'document_id': document.id,
                'summary': summary,
                'plagiarism': plagiarism_result.get('plagiarism_score', 0.0),
                'plagiarism_details': plagiarism_result.get('matching_sources', []),
                'citations': formatted_citations,
                'fact_check': {
                    'facts': formatted_facts
                },
                'stats': {
                    'word_count': word_count,
                    'plagiarism_percent': plagiarism_result.get('plagiarism_score', 0.0),
                    'citations_count': len(formatted_citations),
                    'fact_checks_count': len(formatted_facts)
                }
            }), 200
            
        finally:
            # Clean up temporary file
            if os.path.exists(temp_path):
                os.remove(temp_path)
                
    except Exception as e:
        db.session.rollback()
        logger.error(f"Analysis failed for user {current_user_id}: {str(e)}")
        return jsonify({'error': f'Analysis failed: {str(e)}'}), 500

@protected_analyze_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'service': 'protected_analyze',
        'message': 'Protected analyze service is running'
    }), 200