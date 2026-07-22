"""
Foundry RAG Assistant - RAG Engine Tests
"""

import pytest


class TestSystemPrompt:
    """Sistem promptu ve yapılandırma testleri."""

    def test_prompt_contains_context_placeholder(self):
        from rag_engine import RAGEngine
        assert "{context}" in RAGEngine.SYSTEM_PROMPT

    def test_prompt_references_context(self):
        from rag_engine import RAGEngine
        prompt = RAGEngine.SYSTEM_PROMPT
        assert "BAĞLAM" in prompt or "BAGLAM" in prompt

    def test_prompt_does_not_ask_for_inline_citations(self):
        """Satir ici [Kaynak: ...] kurali BILEREK kaldirildi.

        Model kurala zaten uymuyordu; kaynaklar arayuzde API'nin dondurdugu
        listeden gosteriliyor. Kurali silmek olculebilir bir kazanc sagladi:
        cevaplanabilir sorular 11/12 -> 12/12, genel %74 -> %79.
        Modelin uymadigi bir kural bedava degil; uydugu kurallarin talimat
        butcesini tuketiyor. Bkz. docs/ogrenilenler.md
        """
        from rag_engine import RAGEngine
        assert "[Kaynak:" not in RAGEngine.SYSTEM_PROMPT

    def test_config_max_tokens_default(self):
        from config import CONFIG
        assert CONFIG.max_tokens >= 1024

    def test_clean_response_removes_think_tags(self):
        from rag_engine import RAGEngine
        raw = "<think>Düşünme aşaması...</think>Cevap metni."
        cleaned = RAGEngine._clean_response(raw)
        assert cleaned == "Cevap metni."

    def test_prompt_leads_with_refusal_check(self):
        """Reddetme kurali promptun ilk yarisinda olmali.

        Kural en sona yazildiginda kucuk model onu yok sayip cevap uyduruyordu
        (bkz. eval/RESULTS-baseline-01.md).
        """
        from rag_engine import RAGEngine
        prompt = RAGEngine.SYSTEM_PROMPT
        refusal_at = prompt.find("bilgi bulunmuyor")
        assert refusal_at != -1
        assert refusal_at < len(prompt) / 2


class TestRepetitionLoopGuard:
    """Paragraf ici tekrar dongusu tespiti (ADR-0007)."""

    def test_truncates_repeated_phrase(self):
        from rag_engine import RAGEngine
        phrase = "ayni cumle tekrar ediyor. "
        looped = "Gecerli bir giris. " + phrase * 5
        cleaned = RAGEngine._clean_response(looped)
        assert cleaned.startswith("Gecerli bir giris.")
        assert len(cleaned) < len(looped)

    def test_leaves_normal_text_untouched(self):
        from rag_engine import RAGEngine
        text = (
            "Yillik izin ilk yil 14 is gunudur. Kidem 5 yili astiginda 20 is "
            "gunune cikar. [Kaynak: izin_politikasi.txt]"
        )
        assert RAGEngine._clean_response(text) == text

    def test_streaming_and_batch_share_thresholds(self):
        """Iki yol ayni esikleri kullanmali; yoksa degerlendirme kullanicinin
        gordugu davranisi olcmez."""
        from rag_engine import RAGEngine
        assert RAGEngine._LOOP_WINDOW > 0
        assert RAGEngine._LOOP_THRESHOLD >= 2
