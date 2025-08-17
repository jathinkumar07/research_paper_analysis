from flask import Flask, request, jsonify
from flask_cors import CORS
import fitz  # PyMuPDF
from transformers import pipeline
from crossref.restful import Works
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import os
import re
import requests
import json
import google.auth
from googleapiclient.discovery import build

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "./uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

works = Works()

# ----------- UTILITIES -----------

def extract_text_from_pdf(pdf_path):
    text = ""
    doc = fitz.open(pdf_path)
    for page in doc:
        text += page.get_text("text") + "\n"
    return text.strip()

def detect_plagiarism(text):
    words = re.findall(r'\b\w+\b', text.lower())
    common_words = [w for w in words if len(w) > 4]
    keywords = " ".join(common_words[:6])

    search_url = f"https://api.semanticscholar.org/graph/v1/paper/search?query={keywords}&fields=title,abstract&limit=5"
    response = requests.get(search_url)
    data = response.json()

    abstracts = []
    if "data" in data:
        for paper in data["data"]:
            abstract = paper.get("abstract", "")
            if abstract:
                abstracts.append(abstract)

    documents = [text] + abstracts
    if len(documents) == 1:
        return 0

    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(documents)
    similarity_scores = cosine_similarity(tfidf_matrix[0], tfidf_matrix[1:])[0]
    max_score = max(similarity_scores) * 100
    return round(max_score, 2) if max_score > 10 else 0

def extract_citations(text):
    references_start = text.lower().find("references")
    if references_start == -1:
        return []
    references_text = text[references_start:]
    references = references_text.split("\n")[:10]
    return references

def clean_citation(citation):
    citation = citation.replace("\n", " ").strip()
    title_match = re.search(r'“([^”]+)”', citation)
    if title_match:
        return title_match.group(1)
    title_candidate = citation.split(".")[0]
    return title_candidate if len(title_candidate) > 5 else citation

def validate_citations(citations):
    citation_results = {}
    for citation in citations:
        cleaned_title = clean_citation(citation)
        try:
            url = f"https://api.semanticscholar.org/graph/v1/paper/search?query={citation}&fields=title,authors"
            response = requests.get(url, timeout=5)
            data = response.json()
            if "data" in data and len(data["data"]) > 0:
                citation_results[citation] = data["data"][0]["title"]
                continue
            url = f"https://api.semanticscholar.org/graph/v1/paper/search?query={cleaned_title}&fields=title,authors"
            response = requests.get(url, timeout=5)
            data = response.json()
            if "data" in data and len(data["data"]) > 0:
                citation_results[citation] = data["data"][0]["title"]
                continue
            keywords = " ".join(cleaned_title.split()[:4])
            url = f"https://api.semanticscholar.org/graph/v1/paper/search?query={keywords}&fields=title,authors"
            response = requests.get(url, timeout=5)
            data = response.json()
            if "data" in data and len(data["data"]) > 0:
                citation_results[citation] = data["data"][0]["title"]
            else:
                citation_results[citation] = "Not Found"
        except requests.exceptions.Timeout:
            citation_results[citation] = "API Timeout"
        except Exception as e:
            citation_results[citation] = f"API Error: {str(e)}"
    return citation_results

# ----------- CRITIQUE MODULE -----------

def critique_paper(text):
    critique_result = {}

    methodology_keywords = [
        "sample size", "experiment", "survey", "hypothesis",
        "qualitative", "quantitative", "interview", "randomized"
    ]
    found_keywords = [kw for kw in methodology_keywords if kw in text.lower()]
    if not found_keywords:
        critique_result["methodology_issues"] = "No standard research methodology terms found."
    else:
        critique_result["methodology_issues"] = f"Methodology terms found: {', '.join(found_keywords)}."

    bias_terms = ["clearly", "obviously", "undoubtedly", "without a doubt", "everyone knows", "we believe"]
    found_bias = [term for term in bias_terms if term in text.lower()]
    if found_bias:
        critique_result["bias_language"] = found_bias

    if not found_keywords:
        critique_result["suggestion"] = "Consider describing your research methods in detail."
    elif found_bias:
        critique_result["suggestion"] = "Avoid subjective language to maintain objectivity."
    else:
        critique_result["suggestion"] = "The methodology appears sound and objective."

    return critique_result

# ----------- API ENDPOINT -----------

@app.route("/analyze", methods=["POST"])
def analyze_paper():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    pdf_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(pdf_path)

    text = extract_text_from_pdf(pdf_path)
    if not text:
        return jsonify({"error": "No readable text found in PDF"}), 400

    summary = summarizer(text[:1024], max_length=200, min_length=50, do_sample=False)[0]["summary_text"]
    plagiarism_score = detect_plagiarism(text)
    citations = extract_citations(text)
    citation_results = validate_citations(citations)
    critique_result = critique_paper(text)

    return jsonify({
        "summary": summary,
        "plagiarism_score": plagiarism_score,
        "citations": citation_results,
        "critique": critique_result
    })

if __name__ == "__main__":
    app.run(debug=False)
