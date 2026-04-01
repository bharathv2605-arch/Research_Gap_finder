"""
keyword_extractor.py - Keyword Extraction Module
Uses TF-IDF (Term Frequency - Inverse Document Frequency)
to extract important keywords from research papers.
"""

from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np


def extract_keywords_tfidf(text, top_n=15):
    """
    Extract top keywords from a single document using TF-IDF.
    TF-IDF measures how important a word is to a document.
    Args:
        text: Preprocessed text string
        top_n: Number of top keywords to extract
    Returns:
        List of (keyword, score) tuples
    """
    if not text or len(text.split()) < 3:
        return []

    try:
        # Create TF-IDF vectorizer
        # max_features limits the vocabulary size
        # ngram_range=(1,2) captures single words and two-word phrases
        # For a single document, we split it into sentences
        # to create a pseudo-corpus for meaningful TF-IDF scores
        import re
        sentences = re.split(r'[.!?\n]+', text)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 10]

        # If not enough sentences, treat the whole text as one doc
        if len(sentences) < 2:
            sentences = [text]

        vectorizer = TfidfVectorizer(
            max_features=500,
            ngram_range=(1, 2),
            min_df=1,
            max_df=1.0  # Allow terms in all documents
        )

        # Fit on sentences to get meaningful IDF values
        tfidf_matrix = vectorizer.fit_transform(sentences)

        # Get feature names (words)
        feature_names = vectorizer.get_feature_names_out()

        # Get TF-IDF scores (average across all sentences/rows)
        scores = tfidf_matrix.toarray().mean(axis=0)

        # Create (keyword, score) pairs and sort by score
        keyword_scores = list(zip(feature_names, scores))
        keyword_scores.sort(key=lambda x: x[1], reverse=True)

        # Return top N keywords
        return keyword_scores[:top_n]

    except Exception as e:
        print(f"[ERROR] Keyword extraction failed: {e}")
        return []


def extract_keywords_multi(texts, top_n=15):
    """
    Extract keywords from multiple documents using TF-IDF.
    This considers word importance across all documents.
    Args:
        texts: List of preprocessed text strings
        top_n: Number of top keywords per document
    Returns:
        List of lists, each containing (keyword, score) tuples
    """
    if not texts:
        return []

    # Filter out empty texts
    valid_texts = [t for t in texts if t and len(t.split()) >= 3]
    if not valid_texts:
        return [[] for _ in texts]

    try:
        # Create TF-IDF vectorizer for multiple documents
        # max_df=1.0 to handle cases with very few documents
        max_df_val = 0.95 if len(valid_texts) >= 5 else 1.0
        vectorizer = TfidfVectorizer(
            max_features=1000,
            ngram_range=(1, 2),
            min_df=1,
            max_df=max_df_val
        )

        # Fit on all documents
        tfidf_matrix = vectorizer.fit_transform(valid_texts)
        feature_names = vectorizer.get_feature_names_out()

        # Extract keywords for each document
        all_keywords = []
        for i in range(len(valid_texts)):
            scores = tfidf_matrix[i].toarray()[0]
            keyword_scores = list(zip(feature_names, scores))
            keyword_scores.sort(key=lambda x: x[1], reverse=True)
            # Filter out zero-score keywords
            keyword_scores = [(k, s) for k, s in keyword_scores if s > 0]
            all_keywords.append(keyword_scores[:top_n])

        return all_keywords

    except Exception as e:
        print(f"[ERROR] Multi-document keyword extraction failed: {e}")
        return [[] for _ in texts]


def get_common_keywords(keywords_list):
    """
    Find keywords that appear across multiple papers.
    Args:
        keywords_list: List of keyword lists (one per paper)
    Returns:
        Set of common keywords found in multiple papers
    """
    if len(keywords_list) < 2:
        return set()

    # Get keyword sets for each paper
    keyword_sets = []
    for keywords in keywords_list:
        kw_set = set(kw for kw, score in keywords)
        keyword_sets.append(kw_set)

    # Find keywords appearing in at least 2 papers
    all_keywords = {}
    for kw_set in keyword_sets:
        for kw in kw_set:
            all_keywords[kw] = all_keywords.get(kw, 0) + 1

    common = {kw for kw, count in all_keywords.items() if count >= 2}
    return common


def get_unique_keywords(keywords_list):
    """
    Find keywords unique to each paper (not found in other papers).
    Args:
        keywords_list: List of keyword lists (one per paper)
    Returns:
        List of sets, each containing unique keywords for that paper
    """
    if not keywords_list:
        return []

    # Get all keyword sets
    keyword_sets = []
    for keywords in keywords_list:
        kw_set = set(kw for kw, score in keywords)
        keyword_sets.append(kw_set)

    # For each paper, find keywords not in any other paper
    unique_per_paper = []
    for i, kw_set in enumerate(keyword_sets):
        other_keywords = set()
        for j, other_set in enumerate(keyword_sets):
            if i != j:
                other_keywords.update(other_set)
        unique = kw_set - other_keywords
        unique_per_paper.append(unique)

    return unique_per_paper
