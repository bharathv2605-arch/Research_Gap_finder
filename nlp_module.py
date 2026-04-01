"""
nlp_module.py - Natural Language Processing Module
Handles text cleaning, tokenization, stopword removal,
and text preprocessing for analysis.
"""

import re
import string
import nltk

# Download required NLTK data (only needed once)
nltk.download('punkt', quiet=True)
nltk.download('punkt_tab', quiet=True)
nltk.download('stopwords', quiet=True)
nltk.download('wordnet', quiet=True)

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer


def clean_text(text):
    """
    Clean raw text by removing special characters, numbers,
    extra whitespace, and converting to lowercase.
    Args:
        text: Raw text string
    Returns:
        Cleaned text string
    """
    if not text:
        return ""

    # Convert to lowercase
    text = text.lower()

    # Remove URLs
    text = re.sub(r'http\S+|www\S+', '', text)

    # Remove email addresses
    text = re.sub(r'\S+@\S+', '', text)

    # Remove numbers
    text = re.sub(r'\d+', '', text)

    # Remove special characters and punctuation
    text = re.sub(r'[^\w\s]', ' ', text)

    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()

    return text


def remove_stopwords(text):
    """
    Remove common English stopwords from text.
    Stopwords are common words like 'the', 'is', 'at' that
    don't carry significant meaning.
    Args:
        text: Cleaned text string
    Returns:
        Text with stopwords removed
    """
    stop_words = set(stopwords.words('english'))

    # Add custom academic stopwords
    custom_stopwords = {
        'paper', 'research', 'study', 'result', 'method',
        'approach', 'propose', 'proposed', 'using', 'based',
        'also', 'however', 'therefore', 'thus', 'hence',
        'fig', 'figure', 'table', 'section', 'chapter',
        'abstract', 'introduction', 'conclusion', 'reference',
        'et', 'al', 'vol', 'pp', 'doi', 'isbn', 'issn',
        'would', 'could', 'may', 'might', 'shall', 'must',
        'one', 'two', 'three', 'first', 'second', 'new'
    }
    stop_words.update(custom_stopwords)

    # Tokenize and filter
    words = word_tokenize(text)
    filtered_words = [
        word for word in words
        if word not in stop_words and len(word) > 2
    ]

    return ' '.join(filtered_words)


def lemmatize_text(text):
    """
    Lemmatize words to their base form.
    Example: 'running' -> 'run', 'studies' -> 'study'
    Args:
        text: Text string
    Returns:
        Lemmatized text string
    """
    lemmatizer = WordNetLemmatizer()
    words = word_tokenize(text)
    lemmatized = [lemmatizer.lemmatize(word) for word in words]
    return ' '.join(lemmatized)


def preprocess_text(text):
    """
    Complete text preprocessing pipeline.
    Applies cleaning, stopword removal, and lemmatization.
    Args:
        text: Raw text from a research paper
    Returns:
        Fully preprocessed text ready for analysis
    """
    # Step 1: Clean the text
    text = clean_text(text)

    # Step 2: Remove stopwords
    text = remove_stopwords(text)

    # Step 3: Lemmatize
    text = lemmatize_text(text)

    return text


def get_word_frequency(text, top_n=20):
    """
    Get the most frequent words in the text.
    Args:
        text: Preprocessed text string
        top_n: Number of top words to return
    Returns:
        List of (word, count) tuples sorted by frequency
    """
    words = word_tokenize(text)
    freq_dist = nltk.FreqDist(words)
    return freq_dist.most_common(top_n)
