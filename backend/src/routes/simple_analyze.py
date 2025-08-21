from flask import Blueprint, request, jsonify
import os
import tempfile
import logging

logger = logging.getLogger(__name__)
try:
    from src.services.pdf_service import extract_text_and_meta
    from src.services.summarizer_service import summarize
    from src.services.plagiarism_service import check as check_plagiarism
    from src.services.citations_service import validate as validate_citations
    from src.services.factcheck_service import extract_claims, fact_check_claims
except ImportError:
    # Use mock services if real ones are not available
    from src.services.pdf_service_mock import extract_text_and_meta
    from src.services.summarizer_service_mock import summarize
    from src.services.plagiarism_service_mock import check as check_plagiarism
    from src.services.citations_service_mock import validate as validate_citations
    from src.services.factcheck_service_mock import extract_claims, fact_check_claims

# Create blueprint for simple analysis (no auth required)
simple_analyze_bp = Blueprint('simple_analyze', __name__)

@simple_analyze_bp.route('/analyze', methods=['POST'])
def analyze_document():
    """
    Simple document analysis endpoint that doesn't require authentication.
    
    POST /analyze
    
    Form data:
        - file: PDF file to analyze
    
    Returns:
        200: Analysis results
        400: Validation error
        500: Server error
    """
    try:
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
            
            # Run analysis pipeline
            print(f"Starting analysis for uploaded file: {file.filename}")
            logger.info(f"Starting analysis for file: {file.filename}")
            
            # Initialize default values
            summary = "Analysis failed to generate summary."
            plagiarism_score = 0.0
            citation_results = []
            fact_check_results = []
            
            # 1. Summarization
            print("Running summarization...")
            try:
                summary = summarize(text)
                logger.info("Summarization completed successfully")
            except Exception as e:
                print(f"Summarization failed: {e}")
                logger.error(f"Summarization failed: {e}")
                summary = "Unable to generate summary due to processing error."
            
            # 2. Plagiarism detection
            print("Running plagiarism check...")
            try:
                plagiarism_score = check_plagiarism(text)
                logger.info(f"Plagiarism check completed: {plagiarism_score}%")
            except Exception as e:
                print(f"Plagiarism check failed: {e}")
                logger.error(f"Plagiarism check failed: {e}")
                plagiarism_score = 0.0
            
            # 3. Citation validation
            print("Validating citations...")
            try:
                citation_results = validate_citations(text)
                logger.info(f"Citation validation completed: {len(citation_results)} citations found")
            except Exception as e:
                print(f"Citation validation failed: {e}")
                logger.error(f"Citation validation failed: {e}")
                citation_results = []
            
            # 4. Fact checking
            print("Running fact check...")
            try:
                claims = extract_claims(text)
                fact_check_results = fact_check_claims(claims) if claims else []
                logger.info(f"Fact checking completed: {len(fact_check_results)} claims checked")
            except Exception as e:
                print(f"Fact check failed: {e}")
                logger.error(f"Fact check failed: {e}")
                fact_check_results = []
            
            print(f"Analysis completed for file: {file.filename}")
            
            # Format citations for frontend
            formatted_citations = []
            for citation in citation_results:
                formatted_citations.append({
                    "reference": citation.get('raw', citation.get('cleaned_title', 'Unknown citation')),
                    "valid": citation.get('status') == 'verified'
                })
            
            # Format fact check results for frontend
            formatted_facts = []
            for fact in fact_check_results:
                formatted_facts.append({
                    "claim": fact.get('claim', 'Unknown claim'),
                    "status": "Verified" if fact.get('status') == 'verified' else "Unverified"
                })
            
            # Return results in the format expected by frontend
            return jsonify({
                'summary': summary,
                'plagiarism': plagiarism_score,
                'citations': formatted_citations,
                'fact_check': {
                    'facts': formatted_facts
                },
                'stats': {
                    'word_count': word_count,
                    'plagiarism_percent': plagiarism_score,
                    'citations_count': len(formatted_citations)
                }
            }), 200
            
        finally:
            # Clean up temporary file
            if os.path.exists(temp_path):
                os.remove(temp_path)
                
    except Exception as e:
        print(f"Analysis failed: {str(e)}")
        return jsonify({'error': f'Analysis failed: {str(e)}'}), 500

@simple_analyze_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'service': 'simple_analyze',
        'message': 'Simple analyze service is running'
    }), 200