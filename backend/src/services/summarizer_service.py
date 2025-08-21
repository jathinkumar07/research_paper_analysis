import re
import logging
from flask import current_app

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

def _summarize_with_hf(text: str) -> str:
    """Summarize using HuggingFace BART model."""
    try:
        from transformers import pipeline
        
        # Initialize summarizer (cached after first use)
        if not hasattr(_summarize_with_hf, 'summarizer'):
            _summarize_with_hf.summarizer = pipeline(
                "summarization", 
                model="facebook/bart-large-cnn",
                device=-1  # Use CPU
            )
        
        # Chunk text to fit model limits (~1024 tokens ≈ 1200-1600 chars)
        chunk_size = 1200
        chunk = text[:chunk_size]
        
        # Ensure we don't cut off mid-sentence
        last_period = chunk.rfind('.')
        if last_period > chunk_size * 0.7:  # If we find a period in the last 30%
            chunk = chunk[:last_period + 1]
        
        # Generate summary with specified token limits
        summary = _summarize_with_hf.summarizer(
            chunk, 
            max_length=300, 
            min_length=100, 
            do_sample=False
        )[0]['summary_text']
        
        return summary.strip()
        
    except ImportError:
        raise Exception("transformers library not available")
    except Exception as e:
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