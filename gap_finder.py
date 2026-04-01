"""
gap_finder.py - Research Gap Detection Module
Compares multiple research papers to identify:
- Common topics across papers
- Missing/uncovered topics
- Research gaps (less-researched areas)
- Suggested new research ideas
"""

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np


# ============================================================
# Predefined research topic areas for gap detection
# These represent common research domains that papers may cover
# ============================================================
RESEARCH_TOPIC_AREAS = {
    "machine_learning": [
        "machine learning", "deep learning", "neural network",
        "classification", "regression", "clustering", "supervised",
        "unsupervised", "reinforcement learning", "training",
        "prediction", "model", "algorithm", "feature extraction"
    ],
    "data_analysis": [
        "data analysis", "data mining", "big data", "dataset",
        "statistical analysis", "visualization", "preprocessing",
        "data collection", "pattern recognition", "anomaly detection"
    ],
    "security": [
        "security", "privacy", "encryption", "authentication",
        "cyber", "threat", "vulnerability", "intrusion detection",
        "malware", "firewall", "access control"
    ],
    "networking": [
        "network", "protocol", "bandwidth", "latency",
        "routing", "wireless", "iot", "cloud computing",
        "distributed", "communication", "server"
    ],
    "natural_language_processing": [
        "nlp", "natural language", "text mining", "sentiment",
        "tokenization", "word embedding", "language model",
        "text classification", "named entity", "information extraction"
    ],
    "image_processing": [
        "image processing", "computer vision", "object detection",
        "image classification", "segmentation", "convolutional",
        "recognition", "feature detection", "image enhancement"
    ],
    "optimization": [
        "optimization", "genetic algorithm", "swarm", "evolutionary",
        "heuristic", "metaheuristic", "objective function",
        "convergence", "performance improvement", "efficiency"
    ],
    "healthcare": [
        "healthcare", "medical", "diagnosis", "patient",
        "clinical", "disease", "treatment", "health monitoring",
        "biomedical", "drug", "electronic health"
    ],
    "methodology": [
        "methodology", "framework", "architecture", "design",
        "implementation", "evaluation", "comparison", "benchmark",
        "experimental", "validation", "testing"
    ],
    "ethics_and_society": [
        "ethical", "bias", "fairness", "transparency",
        "explainability", "accountability", "social impact",
        "regulation", "governance", "responsible"
    ]
}


def calculate_similarity(texts):
    """
    Calculate cosine similarity between multiple documents.
    Cosine similarity measures how similar two documents are
    based on their word vectors (0 = different, 1 = identical).
    Args:
        texts: List of preprocessed text strings
    Returns:
        Similarity matrix (numpy array)
    """
    if len(texts) < 2:
        return np.array([[1.0]])

    try:
        vectorizer = TfidfVectorizer(max_features=1000)
        tfidf_matrix = vectorizer.fit_transform(texts)
        similarity_matrix = cosine_similarity(tfidf_matrix)
        return similarity_matrix
    except Exception as e:
        print(f"[ERROR] Similarity calculation failed: {e}")
        return np.eye(len(texts))


def detect_covered_topics(texts):
    """
    Detect which research topic areas are covered by the papers.
    Checks each text against predefined topic keyword lists.
    Args:
        texts: List of preprocessed text strings
    Returns:
        Dictionary with topic names as keys and coverage info as values
    """
    covered = {}

    # Combine all texts for overall analysis
    combined_text = ' '.join(texts).lower()

    for topic_name, topic_keywords in RESEARCH_TOPIC_AREAS.items():
        # Count how many keywords from this topic appear in the texts
        matches = []
        for keyword in topic_keywords:
            if keyword in combined_text:
                matches.append(keyword)

        # A topic is "covered" if at least 3 keywords match
        coverage_ratio = len(matches) / len(topic_keywords)
        covered[topic_name] = {
            'matched_keywords': matches,
            'coverage_ratio': round(coverage_ratio, 2),
            'is_covered': len(matches) >= 3
        }

    return covered


def find_research_gaps(texts, paper_keywords_list):
    """
    Main function to identify research gaps.
    Analyzes papers to find missing topics and under-researched areas.
    Args:
        texts: List of preprocessed text strings
        paper_keywords_list: List of keyword lists (one per paper)
    Returns:
        Dictionary containing gap analysis results
    """
    results = {
        'similarity_scores': [],
        'covered_topics': [],
        'missing_topics': [],
        'gaps': [],
        'suggestions': []
    }

    if not texts:
        return results

    # ---- Step 1: Calculate document similarity ----
    if len(texts) >= 2:
        sim_matrix = calculate_similarity(texts)
        for i in range(len(texts)):
            for j in range(i + 1, len(texts)):
                results['similarity_scores'].append({
                    'paper_1': i + 1,
                    'paper_2': j + 1,
                    'score': round(float(sim_matrix[i][j]), 3)
                })

    # ---- Step 2: Detect covered topics ----
    topic_coverage = detect_covered_topics(texts)

    for topic_name, info in topic_coverage.items():
        display_name = topic_name.replace('_', ' ').title()
        if info['is_covered']:
            results['covered_topics'].append({
                'topic': display_name,
                'keywords_found': info['matched_keywords'],
                'coverage': f"{int(info['coverage_ratio'] * 100)}%"
            })
        else:
            results['missing_topics'].append({
                'topic': display_name,
                'coverage': f"{int(info['coverage_ratio'] * 100)}%"
            })

    # ---- Step 3: Identify specific research gaps ----
    gaps = _identify_gaps(texts, paper_keywords_list, topic_coverage)
    results['gaps'] = gaps

    # ---- Step 4: Generate research suggestions ----
    suggestions = _generate_suggestions(
        results['covered_topics'],
        results['missing_topics'],
        results['gaps']
    )
    results['suggestions'] = suggestions

    return results


def _identify_gaps(texts, paper_keywords_list, topic_coverage):
    """
    Identify specific research gaps based on analysis.
    Args:
        texts: Preprocessed texts
        paper_keywords_list: Keywords per paper
        topic_coverage: Topic coverage dictionary
    Returns:
        List of gap descriptions
    """
    gaps = []

    # Gap Type 1: Topics with low coverage (partially covered)
    for topic_name, info in topic_coverage.items():
        display_name = topic_name.replace('_', ' ').title()
        if 0 < info['coverage_ratio'] < 0.3 and not info['is_covered']:
            gaps.append({
                'type': 'Low Coverage Topic',
                'description': (
                    f"The topic '{display_name}' is only partially covered "
                    f"({int(info['coverage_ratio'] * 100)}% keyword match). "
                    f"This area needs more in-depth research."
                ),
                'severity': 'Medium'
            })

    # Gap Type 2: Completely missing topics
    for topic_name, info in topic_coverage.items():
        display_name = topic_name.replace('_', ' ').title()
        if info['coverage_ratio'] == 0:
            gaps.append({
                'type': 'Missing Topic',
                'description': (
                    f"The topic '{display_name}' is completely absent "
                    f"from all analyzed papers. This represents a significant "
                    f"research gap that could be explored."
                ),
                'severity': 'High'
            })

    # Gap Type 3: Check for methodology gaps
    combined = ' '.join(texts).lower()
    methodology_checks = {
        'No experimental validation': (
            'experiment' not in combined and 'evaluation' not in combined
        ),
        'No comparison with existing methods': (
            'comparison' not in combined and 'baseline' not in combined
            and 'benchmark' not in combined
        ),
        'No dataset description': (
            'dataset' not in combined and 'data collection' not in combined
        ),
        'No performance metrics discussed': (
            'accuracy' not in combined and 'precision' not in combined
            and 'recall' not in combined and 'f1' not in combined
        ),
        'No future work discussed': (
            'future work' not in combined and 'future research' not in combined
            and 'limitation' not in combined
        )
    }

    for gap_desc, is_gap in methodology_checks.items():
        if is_gap:
            gaps.append({
                'type': 'Methodology Gap',
                'description': f"{gap_desc} in the analyzed papers.",
                'severity': 'Medium'
            })

    # Gap Type 4: Low similarity between papers may indicate
    # fragmented research with no unifying framework
    if len(texts) >= 2:
        sim_matrix = calculate_similarity(texts)
        avg_similarity = np.mean(
            sim_matrix[np.triu_indices(len(texts), k=1)]
        )
        if avg_similarity < 0.15:
            gaps.append({
                'type': 'Fragmentation Gap',
                'description': (
                    f"The analyzed papers have very low average similarity "
                    f"({avg_similarity:.2f}). This suggests the research area "
                    f"is fragmented and lacks a unifying framework or approach."
                ),
                'severity': 'High'
            })

    # If no specific gaps found, provide a general observation
    if not gaps:
        gaps.append({
            'type': 'General',
            'description': (
                "The analyzed papers appear to cover their topics well. "
                "Consider looking for gaps in specific sub-topics, "
                "newer methodologies, or cross-domain applications."
            ),
            'severity': 'Low'
        })

    return gaps


def _generate_suggestions(covered_topics, missing_topics, gaps):
    """
    Generate research suggestions based on the gap analysis.
    Args:
        covered_topics: List of covered topic dictionaries
        missing_topics: List of missing topic dictionaries
        gaps: List of gap dictionaries
    Returns:
        List of suggestion strings
    """
    suggestions = []

    # Suggestion 1: Based on missing topics
    if missing_topics:
        top_missing = missing_topics[:3]
        topic_names = [t['topic'] for t in top_missing]
        suggestions.append(
            f"Explore the uncovered areas: {', '.join(topic_names)}. "
            f"These topics are not addressed in the current papers "
            f"and could lead to novel research contributions."
        )

    # Suggestion 2: Cross-domain research
    if len(covered_topics) >= 2:
        t1 = covered_topics[0]['topic']
        t2 = covered_topics[1]['topic']
        suggestions.append(
            f"Consider a cross-domain study combining "
            f"'{t1}' and '{t2}'. Interdisciplinary research "
            f"often leads to innovative solutions."
        )

    # Suggestion 3: Based on high-severity gaps
    high_gaps = [g for g in gaps if g['severity'] == 'High']
    if high_gaps:
        suggestions.append(
            f"Address the {len(high_gaps)} high-severity gap(s) found. "
            f"These represent significant opportunities for new research."
        )

    # Suggestion 4: Methodology improvement
    method_gaps = [g for g in gaps if g['type'] == 'Methodology Gap']
    if method_gaps:
        suggestions.append(
            "Strengthen the research methodology by including "
            "experimental validation, comparison with baselines, "
            "and clear performance metrics in future work."
        )

    # Suggestion 5: Always suggest a survey/review paper
    suggestions.append(
        "Consider writing a systematic literature review or survey "
        "paper that comprehensively covers the analyzed topic areas "
        "and identifies a structured research agenda."
    )

    # Suggestion 6: Practical applications
    suggestions.append(
        "Explore practical applications and real-world implementations "
        "of the research findings. Industry-relevant research often "
        "has higher impact and citation potential."
    )

    return suggestions
