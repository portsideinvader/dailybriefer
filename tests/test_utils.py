"""Tests for utility functions."""

import pytest
from src.utils import (
    preprocess_title,
    get_title_tokens,
    jaccard_similarity,
    title_similarity,
    make_guid_hash
)


class TestTitlePreprocessing:
    """Test title preprocessing functions."""

    def test_preprocess_title_lowercase(self):
        """Test that titles are lowercased."""
        title = "Breaking News: Major Event"
        processed = preprocess_title(title)
        assert processed == "breaking news major event"

    def test_preprocess_title_removes_punctuation(self):
        """Test that punctuation is removed."""
        title = "What's happening? Big news!"
        processed = preprocess_title(title)
        assert "?" not in processed
        assert "!" not in processed
        assert "'" not in processed

    def test_preprocess_title_removes_stopwords(self):
        """Test that common stopwords are removed."""
        title = "The cat is on the mat"
        processed = preprocess_title(title)
        # 'the', 'is', 'on' should be removed
        assert "the" not in processed.split()
        assert "is" not in processed.split()
        assert "on" not in processed.split()
        # Content words should remain
        assert "cat" in processed.split()
        assert "mat" in processed.split()

    def test_get_title_tokens(self):
        """Test token extraction."""
        title = "US President announces new policy"
        tokens = get_title_tokens(title)
        # Should be a set
        assert isinstance(tokens, set)
        # Should contain meaningful words
        assert "president" in tokens
        assert "announces" in tokens
        assert "new" in tokens
        assert "policy" in tokens


class TestSimilarity:
    """Test similarity functions."""

    def test_jaccard_similarity_identical(self):
        """Test Jaccard similarity with identical sets."""
        set1 = {"apple", "banana", "orange"}
        set2 = {"apple", "banana", "orange"}
        assert jaccard_similarity(set1, set2) == 1.0

    def test_jaccard_similarity_disjoint(self):
        """Test Jaccard similarity with disjoint sets."""
        set1 = {"apple", "banana"}
        set2 = {"car", "bike"}
        assert jaccard_similarity(set1, set2) == 0.0

    def test_jaccard_similarity_partial_overlap(self):
        """Test Jaccard similarity with partial overlap."""
        set1 = {"apple", "banana", "orange"}
        set2 = {"banana", "orange", "grape"}
        # Intersection: {banana, orange} = 2
        # Union: {apple, banana, orange, grape} = 4
        # Similarity: 2/4 = 0.5
        assert jaccard_similarity(set1, set2) == 0.5

    def test_jaccard_similarity_empty_sets(self):
        """Test Jaccard similarity with empty sets."""
        assert jaccard_similarity(set(), set()) == 0.0
        assert jaccard_similarity({"a"}, set()) == 0.0

    def test_title_similarity_identical(self):
        """Test title similarity with identical titles."""
        title1 = "US President announces new policy"
        title2 = "US President announces new policy"
        # Should be 1.0 or very close
        assert title_similarity(title1, title2) == 1.0

    def test_title_similarity_similar_titles(self):
        """Test title similarity with similar titles."""
        title1 = "US President announces new climate policy"
        title2 = "President announces new climate policy"
        # Should have high similarity
        sim = title_similarity(title1, title2)
        assert sim > 0.7

    def test_title_similarity_different_titles(self):
        """Test title similarity with completely different titles."""
        title1 = "US President announces new policy"
        title2 = "Stock market reaches record high"
        # Should have low similarity
        sim = title_similarity(title1, title2)
        assert sim < 0.3


class TestGuidHash:
    """Test GUID hashing for deduplication."""

    def test_make_guid_hash_deterministic(self):
        """Test that hash is deterministic."""
        text = "https://example.com/article/123"
        hash1 = make_guid_hash(text)
        hash2 = make_guid_hash(text)
        assert hash1 == hash2

    def test_make_guid_hash_unique(self):
        """Test that different inputs produce different hashes."""
        text1 = "https://example.com/article/123"
        text2 = "https://example.com/article/456"
        hash1 = make_guid_hash(text1)
        hash2 = make_guid_hash(text2)
        assert hash1 != hash2

    def test_make_guid_hash_length(self):
        """Test that hash has expected length (16 chars)."""
        text = "test"
        hash_val = make_guid_hash(text)
        assert len(hash_val) == 16
