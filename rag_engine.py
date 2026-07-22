"""
Foundry RAG Assistant - RAG Engine Module
Retrieval + Generation pipeline. LLM ile yanit uretimi.

API: model.get_chat_client() -> client.complete_chat() / client.complete_streaming_chat()
"""

import json
import logging
import re
import threading
from typing import List, Optional, Iterator
from foundry_local_sdk import Configuration, FoundryLocalManager
from retriever import Retriever
from embeddings import select_device_variant
from config import CONFIG

logger = logging.getLogger(__name__)


class RAGEngine:
    """RAG pipeline motoru: Retrieve -> Augment -> Generate."""

    # Sistem promptu - modelin davranisini kontrol eder.
    # Reddetme kurali BILEREK en basta: kucuk modellerde son siradaki kural
    # yok sayiliyor ve model, baglam alakasiz oldugunda bile cevap uyduruyordu.
    # Bkz. eval/RESULTS.md
    SYSTEM_PROMPT = """Sen kurumsal bir bilgi asistanisin. Yalnizca asagidaki BAGLAM'a dayanarak konusursun.

ONCE SUNU KONTROL ET: Kullanicinin sordugu bilgi BAGLAM'da acikca yaziyor mu?

Yazmiyorsa, baska HICBIR SEY ekleme ve sadece su cumleyi yaz:
"Bu konuda elimdeki belgelerde bilgi bulunmuyor."
(Soru Ingilizce ise: "No information found in documents.")

BAGLAM konuyla ilgili gorunse bile, sorulan seyin cevabi orada yazmiyorsa yine
bu cumleyi yaz. Tahmin etme, benzer bir bilgiyi cevap yerine koyma.

Cevap BAGLAM'da yaziyorsa:
1. Yalnizca BAGLAM'daki gercekleri kullan. BAGLAM'da GECMEYEN sayi, tutar, tarih,
   yuzde veya isim URETME.
2. Kullanicinin sordugu dilde (Turkce soruya Turkce, Ingilizce soruya Ingilizce)
   kisa ve net yaz.

BAGLAM:
{context}
"""

    # Tekrar dongusu tespiti. Streaming ve streaming olmayan yollar AYNI
    # esikleri kullanir; aksi halde iki yol farkli davranir ve degerlendirme
    # kullanicinin gordugu davranisi olcmemis olur. Bkz. ADR-0007.
    _LOOP_WINDOW = 16
    _LOOP_THRESHOLD = 3

    @classmethod
    def _truncate_repetition_loop(cls, text: str) -> str:
        """Ayni kisa dizinin defalarca tekrarlandigi noktadan itibaren kes.

        Paragraf ici donguleri yakalar; satir bazli temizlik bunlari kaciriyordu.
        """
        for end in range(cls._LOOP_WINDOW, len(text) + 1):
            window = text[end - cls._LOOP_WINDOW:end]
            if text.count(window, 0, end) >= cls._LOOP_THRESHOLD:
                logger.warning(f"Tekrar dongusu kesildi: {window!r}")
                return text[:end - cls._LOOP_WINDOW].rstrip()
        return text

    @classmethod
    def _clean_response(cls, text: str) -> str:
        text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL).strip()
        text = re.sub(r'\?\?\S*', '?', text)
        text = re.sub(r'\.\.\.+', '.', text)

        # Ardışık tekrarlanan aynı cümle/satır döngülerini engelle
        lines = text.split('\n')
        cleaned_lines = []
        for line in lines:
            if not cleaned_lines or line.strip() != cleaned_lines[-1].strip():
                cleaned_lines.append(line)
        text = '\n'.join(cleaned_lines)

        return cls._truncate_repetition_loop(text.strip())

    def __init__(self):
        self.model_alias = CONFIG.chat_model_alias
        self.retriever = Retriever()
        self._chat_model = None
        self._chat_client = None
        self._manager = None
        self._initialized = False
        # Chat LLM cikarim kilit mekanizmasi (Embedding islemlerini engellemez)
        self._infer_lock = threading.Lock()

    def initialize(self):
        """Tum modelleri baslat."""
        if self._initialized:
            return

        logger.info("RAG Engine baslatiliyor...")

        # Embedding modelini baslat
        self.retriever.initialize()

        # Chat modelini baslat
        logger.info(f"Chat modeli yukleniyor: {self.model_alias}")

        # Manager zaten baslatilmis olmali (retriever tarafindan)
        self._manager = FoundryLocalManager.instance

        self._chat_model = self._manager.catalog.get_model(self.model_alias)
        select_device_variant(self._chat_model, CONFIG.chat_device)
        if not self._chat_model.is_cached:
            self._chat_model.download(
                progress_callback=lambda p: logger.info(f"  Chat modeli indiriliyor: {p:.1f}%")
            )
        else:
            logger.info("  Chat modeli zaten var, indirme atlandi")
        self._chat_model.load()
        self._chat_client = self._chat_model.get_chat_client()
        self._chat_client.settings.max_tokens = CONFIG.max_tokens
        self._chat_client.settings.temperature = CONFIG.temperature
        # DIKKAT: frequency_penalty'yi 0.0 GONDERMEK modeli tamamen bozar
        # (sadece noktalama uretir). 0 ise hic gonderme (None birak).
        if CONFIG.frequency_penalty > 0:
            self._chat_client.settings.frequency_penalty = CONFIG.frequency_penalty

        self._initialized = True
        logger.info("RAG Engine hazir")

    def answer(self, query: str, stream: bool = False) -> dict:
        """Soruyu cevapla.

        Args:
            query: Kullanici sorusu
            stream: True ise Iterator dondurur (SSE icin)

        Returns:
            {
                'query': str,
                'answer': str,
                'sources': List[str],
                'retrieved_chunks': int,
                'confidence': float
            }
        """
        self.initialize()

        # Bos sorgu embedding katmaninda ValueError firlatir; burada karsilanir.
        if not query or not query.strip():
            empty = "Lutfen bir soru yazin."
            if stream:
                return self._stream_fallback(query, empty)
            return {
                "query": query,
                "answer": empty,
                "sources": [],
                "retrieved_chunks": 0,
                "confidence": 0.0
            }

        # 1. RETRIEVE - Ilgili parcalari bul
        retrieval_result = self.retriever.retrieve_with_context(query)

        if not retrieval_result["results"]:
            fallback = "Bu konuda elimdeki belgelerde bilgi bulunmuyor."
            if stream:
                return self._stream_fallback(query, fallback)
            return {
                "query": query,
                "answer": fallback,
                "sources": [],
                "retrieved_chunks": 0,
                "confidence": 0.0
            }

        context = retrieval_result["context"]
        sources = retrieval_result["sources"]
        confidence = retrieval_result["results"][0]["similarity"] if retrieval_result["results"] else 0.0

        # 2. AUGMENT - Prompt olustur
        system_prompt = self.SYSTEM_PROMPT.format(context=context)

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query}
        ]

        # 3. GENERATE - LLM'den yanit al
        if stream:
            return self._stream_answer(messages, query, sources, retrieval_result["results"])

        logger.info("LLM yaniti bekleniyor...")
        with self._infer_lock:
            response = self._chat_client.complete_chat(messages)
        answer = self._clean_response(response.choices[0].message.content)

        if not answer:
            # Reasoning modellerde think blogu token limitini tuketebilir
            logger.warning("Model gorunur yanit uretemedi (token limiti think blogunda tukenmis olabilir)")
            answer = "Yanit uretilemedi, lutfen soruyu tekrar deneyin."

        logger.info(f"Yanit uretildi ({len(answer)} karakter)")

        return {
            "query": query,
            "answer": answer,
            "sources": sources,
            "retrieved_chunks": len(retrieval_result["results"]),
            "confidence": confidence
        }

    @staticmethod
    def _sse_event(payload: dict) -> str:
        """SSE olayi olustur. Icerik JSON'a sarilir; boylece token'lardaki
        satir sonlari SSE cercevesini bozamaz."""
        return f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"

    def _stream_fallback(self, query: str, message: str) -> Iterator[str]:
        """Sonuc bulunamadiginda stream protokolune uygun yanit."""
        yield self._sse_event({
            "type": "metadata",
            "query": query,
            "sources": [],
            "retrieved_chunks": 0,
            "confidence": 0.0
        })
        yield self._sse_event({"type": "delta", "content": message})
        yield self._sse_event({"type": "done"})

    def _stream_answer(self, messages: List[dict], query: str,
                       sources: List[str], results: List[dict]) -> Iterator[str]:
        """Streaming yanit uretimi."""
        confidence = results[0]["similarity"] if results else 0.0

        # Metadata header
        yield self._sse_event({
            "type": "metadata",
            "query": query,
            "sources": sources,
            "retrieved_chunks": len(results),
            "confidence": confidence
        })

        # Yanit chunk'lari (think bloklarini gec)
        # Etiketler ("<think>", "</think>") stream'de birden fazla chunk'a
        # bolunebilir; bu yuzden olasi etiket baslangiclarini tamponlayarak ilerle.
        # Uretim boyunca kilit tutulur: tek model instance'inda es zamanli
        # ikinci bir uretim baslarsa cikti bozulur.
        buffer = ""
        emitted_text = ""
        in_think = False
        loop_broken = False
        self._infer_lock.acquire()
        try:
            for chunk in self._chat_client.complete_streaming_chat(messages):
                if loop_broken:
                    break
                if not chunk.choices:
                    continue
                content = chunk.choices[0].delta.content
                if not content:
                    continue
                buffer += content

                while buffer:
                    tag = "</think>" if in_think else "<think>"
                    idx = buffer.find(tag)

                    if idx != -1:
                        if not in_think and buffer[:idx]:
                            emit_chunk = buffer[:idx]
                            emitted_text += emit_chunk
                            yield self._sse_event({"type": "delta", "content": emit_chunk})
                        buffer = buffer[idx + len(tag):]
                        in_think = not in_think
                        continue

                    # Tampon sonunda yarim etiket olabilir; o kismi beklet
                    keep = 0
                    for k in range(min(len(tag) - 1, len(buffer)), 0, -1):
                        if tag.startswith(buffer[-k:]):
                            keep = k
                            break

                    emit, buffer = buffer[:len(buffer) - keep], buffer[len(buffer) - keep:]
                    if emit and not in_think:
                        emitted_text += emit
                        yield self._sse_event({"type": "delta", "content": emit})

                        # Streaming Repetition Loop Guard (Döngü Tespiti)
                        if len(emitted_text) >= self._LOOP_WINDOW * 2:
                            tail = emitted_text[-self._LOOP_WINDOW:]
                            if emitted_text.count(tail) >= self._LOOP_THRESHOLD:
                                logger.warning(f"Streaming tekrar dongusu engellendi: {tail}")
                                loop_broken = True
                                break
                    break

            if buffer and not in_think and not loop_broken:
                yield self._sse_event({"type": "delta", "content": buffer})
        finally:
            self._infer_lock.release()

        yield self._sse_event({"type": "done"})

    def answer_stream(self, query: str):
        """Streaming yanit icin generator."""
        yield from self.answer(query, stream=True)

    def shutdown(self):
        """Tum kaynaklari temizle."""
        if self._chat_model:
            self._chat_model.unload()
        self.retriever.shutdown()
        self._initialized = False
        logger.info("RAG Engine durduruldu")

    def __enter__(self):
        self.initialize()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.shutdown()
