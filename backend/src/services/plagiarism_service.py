import os
import glob
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from flask import current_app

def check(text: str) -> float:
    """
    Check plagiarism score against local corpus using TF-IDF similarity.
    
    Args:
        text: Document text to check
    
    Returns:
        Plagiarism score as percentage (0.0-100.0)
    """
    if not text or len(text.strip()) < 100:
        return 0.0
    
    # Load corpus files
    corpus_texts = _load_corpus()
    
    if not corpus_texts:
        print("Warning: No corpus files found, returning 0.0 plagiarism score")
        return 0.0
    
    try:
        # Prepare documents for comparison
        documents = [text] + corpus_texts
        
        # Create TF-IDF vectorizer
        vectorizer = TfidfVectorizer(
            stop_words='english',
            lowercase=True,
            max_df=0.9,  # Ignore terms that appear in >90% of docs
            min_df=1,    # Include terms that appear in at least 1 doc
            ngram_range=(1, 2)  # Include unigrams and bigrams
        )
        
        # Fit and transform documents
        tfidf_matrix = vectorizer.fit_transform(documents)
        
        # Calculate cosine similarity between uploaded doc (index 0) and corpus docs
        similarity_scores = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:])
        
        # Get maximum similarity score
        max_similarity = similarity_scores.max() if similarity_scores.size > 0 else 0.0
        
        # Convert to percentage and round
        plagiarism_score = round(max_similarity * 100, 1)
        
        return plagiarism_score
        
    except Exception as e:
        print(f"Error in plagiarism detection: {e}")
        return 0.0

def _load_corpus() -> list[str]:
    """Load all .txt files from the corpus directory."""
    corpus_texts = []
    corpus_dir = current_app.config.get('CORPUS_DIR', 'corpus')
    
    if not os.path.exists(corpus_dir):
        print(f"Corpus directory {corpus_dir} does not exist")
        return corpus_texts
    
    # Find all .txt files recursively
    pattern = os.path.join(corpus_dir, '**', '*.txt')
    txt_files = glob.glob(pattern, recursive=True)
    
    for file_path in txt_files:
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read().strip()
                if len(content) > 100:  # Only include substantial texts
                    corpus_texts.append(content)
        except Exception as e:
            print(f"Error reading corpus file {file_path}: {e}")
            continue
    
    print(f"Loaded {len(corpus_texts)} corpus documents from {len(txt_files)} files")
    return corpus_texts

def add_to_corpus(text: str, filename: str) -> bool:
    """
    Add a text document to the corpus for future plagiarism checks.
    
    Args:
        text: Text content to add
        filename: Name for the corpus file
    
    Returns:
        True if successful, False otherwise
    """
    try:
        corpus_dir = current_app.config.get('CORPUS_DIR', 'corpus')
        os.makedirs(corpus_dir, exist_ok=True)
        
        # Create safe filename
        safe_filename = filename.replace(' ', '_').replace('.pdf', '.txt')
        file_path = os.path.join(corpus_dir, safe_filename)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(text)
        
        return True
        
    except Exception as e:
        print(f"Error adding document to corpus: {e}")
        return False