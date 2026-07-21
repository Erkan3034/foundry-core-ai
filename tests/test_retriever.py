"""
Foundry RAG Assistant - Retriever Tests
"""

import pytest
from embeddings import find_top_k


class TestFindTopK:
    """En iyi k sonuc bulma testleri."""

    def test_basic_retrieval(self):
        candidates = [
            {"id": 1, "chunk_text": "Python programlama", "embedding": [1.0, 0.0, 0.0]},
            {"id": 2, "chunk_text": "JavaScript web", "embedding": [0.0, 1.0, 0.0]},
            {"id": 3, "chunk_text": "Python kodu", "embedding": [0.9, 0.1, 0.0]},
        ]

        query = [1.0, 0.0, 0.0]
        results = find_top_k(query, candidates, k=2)

        assert len(results) == 2
        assert results[0]["id"] == 1  # En benzer
        assert results[0]["similarity"] > 0.9

    def test_empty_candidates(self):
        results = find_top_k([1.0, 0.0], [], k=3)
        assert results == []

    def test_k_larger_than_candidates(self):
        candidates = [
            {"id": 1, "chunk_text": "A", "embedding": [1.0, 0.0]},
        ]
        results = find_top_k([1.0, 0.0], candidates, k=5)
        assert len(results) == 1
