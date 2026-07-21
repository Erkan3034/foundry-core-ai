"""
Foundry RAG Assistant - Vector Search & Cache Tests
"""

import pytest
import numpy as np
from database import pack_embedding, unpack_embedding
from embeddings import vectorized_find_top_k


class TestVectorBLOBPacking:
    """Float32 binary packing ve unpacking testleri."""

    def test_pack_unpack_consistency(self):
        original = [0.123456, -0.987654, 0.0, 1.5]
        packed = pack_embedding(original)
        assert isinstance(packed, bytes)
        assert len(packed) == len(original) * 4  # 4 bytes per float32

        unpacked = unpack_embedding(packed)
        assert isinstance(unpacked, np.ndarray)
        assert unpacked.dtype == np.float32
        np.testing.assert_allclose(unpacked, original, rtol=1e-5)

    def test_pack_none_or_empty(self):
        assert pack_embedding(None) is None
        assert pack_embedding([]) is None
        assert unpack_embedding(None) is None


class TestVectorizedFindTopK:
    """NumPy matris tabanlı vectorized top-k arama testleri."""

    def test_vectorized_basic_retrieval(self):
        candidates = [
            {"id": 1, "chunk_text": "Python programlama", "embedding": [1.0, 0.0, 0.0]},
            {"id": 2, "chunk_text": "JavaScript web", "embedding": [0.0, 1.0, 0.0]},
            {"id": 3, "chunk_text": "Python kodu", "embedding": [0.8, 0.2, 0.0]},
        ]

        query = [1.0, 0.0, 0.0]
        results = vectorized_find_top_k(query, candidates, k=2)

        assert len(results) == 2
        assert results[0]["id"] == 1  # En yüksek benzerlik (1.0)
        assert results[1]["id"] == 3  # İkinci en yüksek benzerlik (~0.97)
        assert results[0]["similarity"] > results[1]["similarity"]

    def test_vectorized_empty_candidates(self):
        results = vectorized_find_top_k([1.0, 0.0], [], k=3)
        assert results == []

    def test_vectorized_normalized_matrices(self):
        matrix = np.array([
            [1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
            [0.0, 0.0, 1.0]
        ], dtype=np.float32)

        metadata = [
            {"id": 1, "text": "A"},
            {"id": 2, "text": "B"},
            {"id": 3, "text": "C"}
        ]

        query = [0.0, 0.9, 0.1]
        results = vectorized_find_top_k(query, metadata, k=2, embeddings_matrix=matrix)

        assert len(results) == 2
        assert results[0]["id"] == 2  # B (y ekseninde en yakın)
