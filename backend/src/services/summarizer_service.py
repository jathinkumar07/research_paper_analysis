import re
import logging
import os
from flask import current_app

# Global model cache to prevent reloading models on each request
_model_cache = {}

def summarize_text(text: str) -> str:
    """
    Summarize text using HuggingFace transformers BART model.
    
    Args:
        text: Input text to summarize
        
    Returns:
        Summary text (100-300 tokens)
    """
    if not text or len(text.strip()) < 100:
        return text.strip()  # Return original text if too short
    
    try:
        return _summarize_with_hf(text)
    except Exception as e:
        logging.error(f"HF summarization failed, falling back to heuristic: {e}")
        return _summarize_heuristic(text)

def summarize(text: str, use_hf: bool = True) -> str:
    """
    Summarize text using HuggingFace transformers or fallback heuristic.
    
    Args:
        text: Input text to summarize
        use_hf: Whether to use HuggingFace model (from config)
    
    Returns:
        Summary text (150-220 words)
    """
    if not text or len(text.strip()) < 100:
        return "Document too short to summarize effectively."
    
    # Check if we should use HuggingFace
    use_hf_config = current_app.config.get('USE_HF_SUMMARIZER', True)
    
    if use_hf and use_hf_config:
        try:
            return _summarize_with_hf(text)
        except Exception as e:
            print(f"HF summarization failed, falling back to heuristic: {e}")
            return _summarize_heuristic(text)
    else:
        return _summarize_heuristic(text)

def _get_summarizer():
    """Get or create cached HuggingFace summarizer."""
    if 'summarizer' not in _model_cache:
        try:
            from transformers import pipeline
            
            # Get model configuration from Flask config
            model_name = current_app.config.get('HF_MODEL_NAME', 'facebook/bart-large-cnn')
            cache_dir = current_app.config.get('HF_CACHE_DIR', './models_cache')
            
            # Ensure cache directory exists
            os.makedirs(cache_dir, exist_ok=True)
            
            logging.info(f"Loading HuggingFace model: {model_name}")
            
            # Initialize summarizer with caching
            _model_cache['summarizer'] = pipeline(
                "summarization",
                model=model_name,
                cache_dir=cache_dir,
                device=-1,  # Use CPU (-1) or 0 for GPU
                framework="pt"  # PyTorch
            )
            
            logging.info("HuggingFace summarizer loaded successfully")
            
        except ImportError as e:
            raise Exception(f"transformers library not available: {e}")
        except Exception as e:
            raise Exception(f"Failed to load HuggingFace model: {e}")
    
    return _model_cache['summarizer']

def _summarize_with_hf(text: str) -> str:
    """Summarize using HuggingFace BART model."""
    try:
        summarizer = _get_summarizer()
        
        # Clean and prepare text
        text = text.strip()
        if len(text) < 100:
            return text
        
        # Chunk text to fit model limits (~1024 tokens ≈ 1200-1600 chars)
        chunk_size = 1000  # Conservative chunk size
        chunks = []
        
        # Split into chunks, preserving sentence boundaries
        if len(text) <= chunk_size:
            chunks = [text]
        else:
            # Split by paragraphs first
            paragraphs = text.split('\n\n')
            current_chunk = ""
            
            for paragraph in paragraphs:
                if len(current_chunk) + len(paragraph) <= chunk_size:
                    current_chunk += paragraph + "\n\n"
                else:
                    if current_chunk:
                        chunks.append(current_chunk.strip())
                    current_chunk = paragraph + "\n\n"
            
            if current_chunk:
                chunks.append(current_chunk.strip())
        
        # Summarize each chunk
        summaries = []
        for chunk in chunks:
            if len(chunk.strip()) < 50:  # Skip very short chunks
                continue
                
            try:
                summary = summarizer(
                    chunk,
                    max_length=150,  # Shorter summaries per chunk
                    min_length=50,
                    do_sample=False,
                    truncation=True
                )[0]['summary_text']
                
                summaries.append(summary.strip())
                
            except Exception as e:
                logging.warning(f"Failed to summarize chunk: {e}")
                continue
        
        if not summaries:
            raise Exception("Failed to generate any summaries")
        
        # Combine summaries
        final_summary = ' '.join(summaries)
        
        # If combined summary is too long, summarize it again
        if len(final_summary.split()) > 250:
            try:
                final_summary = summarizer(
                    final_summary,
                    max_length=200,
                    min_length=100,
                    do_sample=False,
                    truncation=True
                )[0]['summary_text']
            except Exception as e:
                logging.warning(f"Failed to re-summarize combined text: {e}")
                # Just truncate if re-summarization fails
                words = final_summary.split()
                final_summary = ' '.join(words[:200])
        
        return final_summary.strip()
        
    except Exception as e:
        logging.error(f"HuggingFace summarization error: {e}")
        raise Exception(f"HuggingFace summarization error: {str(e)}")

def _summarize_heuristic(text: str) -> str:
    """Fallback heuristic summarization."""
    sentences = _split_into_sentences(text)
    
    # Keywords that indicate important sentences
    important_keywords = [
        'study', 'result', 'method', 'conclude', 'finding', 'research',
        'analysis', 'experiment', 'data', 'significant', 'demonstrate',
        'propose', 'novel', 'approach', 'framework', 'model', 'algorithm'
    ]
    
    # Score sentences
    sentence_scores = []
    for sentence in sentences:
        if len(sentence.split()) < 5:  # Skip very short sentences
            continue
            
        score = 0
        sentence_lower = sentence.lower()
        
        # Length bonus (prefer medium-length sentences)
        word_count = len(sentence.split())
        if 15 <= word_count <= 30:
            score += 2
        elif 10 <= word_count <= 40:
            score += 1
        
        # Keyword bonus
        for keyword in important_keywords:
            if keyword in sentence_lower:
                score += 1
        
        # Position bonus (first and last paragraphs are often important)
        sentence_index = sentences.index(sentence)
        if sentence_index < len(sentences) * 0.2:  # First 20%
            score += 1
        elif sentence_index > len(sentences) * 0.8:  # Last 20%
            score += 1
        
        sentence_scores.append((sentence, score))
    
    # Sort by score and select top sentences
    sentence_scores.sort(key=lambda x: x[1], reverse=True)
    
    # Select top 5-7 sentences, ensuring we don't exceed ~200 words
    selected_sentences = []
    total_words = 0
    target_words = 200
    
    for sentence, score in sentence_scores:
        sentence_words = len(sentence.split())
        if total_words + sentence_words <= target_words:
            selected_sentences.append(sentence)
            total_words += sentence_words
        if len(selected_sentences) >= 7 or total_words >= target_words * 0.9:
            break
    
    # If we don't have enough, add more sentences
    if len(selected_sentences) < 3:
        for sentence, score in sentence_scores:
            if sentence not in selected_sentences:
                selected_sentences.append(sentence)
                if len(selected_sentences) >= 5:
                    break
    
    # Order sentences by their original appearance
    ordered_summary = []
    for sentence in sentences:
        if sentence in selected_sentences:
            ordered_summary.append(sentence)
    
    summary = ' '.join(ordered_summary)
    
    if not summary:
        # Last resort: take first few sentences
        summary = ' '.join(sentences[:3])
    
    return summary.strip()

def _split_into_sentences(text: str) -> list[str]:
    """Split text into sentences using regex."""
    # Simple sentence splitting on periods, exclamation marks, question marks
    sentences = re.split(r'[.!?]+', text)
    
    # Clean up sentences
    cleaned_sentences = []
    for sentence in sentences:
        sentence = sentence.strip()
        if len(sentence) > 10:  # Skip very short fragments
            cleaned_sentences.append(sentence)
    
    return cleaned_sentences