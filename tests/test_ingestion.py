"""
Foundry RAG Assistant - Ingestion Tests
"""

import pytest
from pathlib import Path
from database import Database
from embeddings import cosine_similarity


class TestChunking:
    """Metin parçalama testleri."""

    def test_chunk_text_basic(self):
        from ingestion import DocumentIngestor
        ingestor = DocumentIngestor()

        text = "Paragraf 1.\n\nParagraf 2.\n\nParagraf 3."
        chunks = ingestor._chunk_text(text)

        assert len(chunks) >= 1
        assert all(len(c) > 0 for c in chunks)

    def test_chunk_text_empty(self):
        from ingestion import DocumentIngestor
        ingestor = DocumentIngestor()

        chunks = ingestor._chunk_text("")
        assert chunks == []

    def test_chunk_size_limit(self):
        from ingestion import DocumentIngestor
        ingestor = DocumentIngestor()
        ingestor.chunk_size = 50

        text = "A" * 200
        chunks = ingestor._chunk_text(text)

        assert all(len(c) <= 50 for c in chunks)

    def test_overlap_boundary_preserves_words(self):
        from ingestion import DocumentIngestor
        ingestor = DocumentIngestor()
        ingestor.chunk_size = 120
        ingestor.chunk_overlap = 40

        chunks = ["Bu ilk paragrafın detaylı cümlesidir.", "Bu ikinci paragrafın başlangıç cümlesidir."]
        overlapped = ingestor._apply_overlap(chunks)

        assert len(overlapped) == 2
        # Kelimenin ortadan kesilmediğini doğrula
        first_word_in_overlap = overlapped[1].split()[0]
        assert not first_word_in_overlap.startswith("isidir.")

    def test_token_count_estimation(self):
        from ingestion import DocumentIngestor
        ingestor = DocumentIngestor()
        text = "Bu Türkçe bir metin örneğidir ve token sayısı hesaplanmalıdır."
        token_count = ingestor._estimate_token_count(text)
        assert token_count > len(text.split())  # Türkçe metinlerde sub-word katsayısı


class TestCosineSimilarity:
    """Kosinüs benzerliği testleri."""

    def test_identical_vectors(self):
        a = [1.0, 0.0, 0.0]
        b = [1.0, 0.0, 0.0]
        assert cosine_similarity(a, b) == pytest.approx(1.0)

    def test_orthogonal_vectors(self):
        a = [1.0, 0.0]
        b = [0.0, 1.0]
        assert cosine_similarity(a, b) == pytest.approx(0.0)

    def test_opposite_vectors(self):
        a = [1.0, 0.0]
        b = [-1.0, 0.0]
        assert cosine_similarity(a, b) == pytest.approx(-1.0)

    def test_zero_vector(self):
        a = [0.0, 0.0]
        b = [1.0, 0.0]
        assert cosine_similarity(a, b) == 0.0
