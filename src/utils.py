"""Utility functions for the news brief system."""

import hashlib
import re
import string
from pathlib import Path
from typing import Any, Dict, List, Set
import yaml


# Common English stopwords for title similarity
STOPWORDS: Set[str] = {
    'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from',
    'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the',
    'to', 'was', 'will', 'with', 's', 't'
}


def load_yaml(file_path: str) -> Dict[str, Any]:
    """Load and parse a YAML configuration file."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {file_path}")

    with open(path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def make_guid_hash(text: str) -> str:
    """Create a deterministic hash for deduplication."""
    return hashlib.sha256(text.encode('utf-8')).hexdigest()[:16]


def preprocess_title(title: str) -> str:
    """
    Preprocess a news title for similarity comparison.

    - Lowercase
    - Remove punctuation
    - Remove stopwords
    - Normalize whitespace
    """
    # Lowercase
    title = title.lower()

    # Remove punctuation
    title = title.translate(str.maketrans('', '', string.punctuation))

    # Split into tokens
    tokens = title.split()

    # Remove stopwords
    tokens = [t for t in tokens if t not in STOPWORDS]

    # Join back
    return ' '.join(tokens)


def get_title_tokens(title: str) -> Set[str]:
    """Get set of tokens from preprocessed title."""
    preprocessed = preprocess_title(title)
    return set(preprocessed.split())


def jaccard_similarity(set1: Set[str], set2: Set[str]) -> float:
    """
    Calculate Jaccard similarity between two sets.

    Returns value between 0 (no overlap) and 1 (identical).
    """
    if not set1 or not set2:
        return 0.0

    intersection = len(set1 & set2)
    union = len(set1 | set2)

    return intersection / union if union > 0 else 0.0


def title_similarity(title1: str, title2: str) -> float:
    """
    Calculate similarity between two news titles using Jaccard similarity.

    Returns value between 0 (completely different) and 1 (identical).
    """
    tokens1 = get_title_tokens(title1)
    tokens2 = get_title_tokens(title2)

    return jaccard_similarity(tokens1, tokens2)


def ensure_directory(path: str) -> None:
    """Ensure a directory exists, creating it if necessary."""
    Path(path).mkdir(parents=True, exist_ok=True)


def get_project_root() -> Path:
    """Get the project root directory."""
    # Assumes this file is in src/
    return Path(__file__).parent.parent


def get_config_path(filename: str) -> Path:
    """Get path to a config file."""
    return get_project_root() / 'config' / filename


def get_data_path(filename: str) -> Path:
    """Get path to a data file."""
    return get_project_root() / 'data' / filename


def get_output_path(filename: str) -> Path:
    """Get path to an output file."""
    return get_project_root() / 'output' / filename
