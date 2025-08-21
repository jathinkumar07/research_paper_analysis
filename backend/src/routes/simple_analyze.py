from flask import Blueprint, request, jsonify
import os
import tempfile
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
            
            # 1. Summarization
            print("Running summarization...")
            summary = summarize(text)
            
            # 2. Plagiarism detection
            print("Running plagiarism check...")
            plagiarism_score = check_plagiarism(text)
            
            # 3. Citation validation
            print("Validating citations...")
            citation_results = validate_citations(text)
            
            # 4. Fact checking
            print("Running fact check...")
            try:
                claims = extract_claims(text)
                fact_check_results = fact_check_claims(claims) if claims else []
            except Exception as e:
                print(f"Fact check failed: {e}")
                fact_check_results = []
            
            print(f"Analysis completed for file: {file.filename}")
            
            # Return results
            return jsonify({
                'success': True,
                'data': {
                    'title': title or file.filename.replace('.pdf', ''),
                    'word_count': word_count,
                    'summary': summary,
                    'plagiarism_score': plagiarism_score,
                    'citations': [
                        {
                            'raw_line': citation['raw'],
                            'cleaned_title': citation['cleaned_title'],
                            'status': citation['status']
                        }
                        for citation in citation_results
                    ],
                    'fact_check_results': fact_check_results
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