"""
Foundry RAG Assistant - Performance Benchmark Tool
Milisaniye bazında Arama Latency'si, TTFT (Time-to-First-Token) ve TPS (Tokens/sec) ölçümü.
"""

import time
import json
import logging
import numpy as np
from database import db
from embeddings import vectorized_find_top_k
from retriever import Retriever
from config import CONFIG

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("benchmark")


def benchmark_vector_search(num_iterations: int = 100):
    """NumPy matris matris çarpımı ile vektör arama hızını ölçer."""
    print("\n" + "=" * 60)
    print(" 1. VEKTÖR ARAMA VE RAM CACHE BENCHMARK'I")
    print("=" * 60)

    # DB'den verileri al
    candidates, matrix = db.get_all_chunks_vector_data()
    if not candidates or matrix is None:
        print("  [UYARI] Veritabanında henüz parça yok. Rastgele 500 vektör ile simülasyon yapılıyor...")
        dim = 1024
        n_chunks = 500
        matrix = np.random.randn(n_chunks, dim).astype(np.float32)
        candidates = [{"id": i, "chunk_text": f"Parça {i}", "source": "test.txt"} for i in range(n_chunks)]

    num_chunks = len(candidates)
    query_vec = np.random.randn(matrix.shape[1]).astype(np.float32)

    # Sıcak başlatma (warmup)
    vectorized_find_top_k(query_vec, candidates, k=3, embeddings_matrix=matrix)

    start_time = time.perf_counter()
    for _ in range(num_iterations):
        results = vectorized_find_top_k(query_vec, candidates, k=3, embeddings_matrix=matrix)
    total_time = time.perf_counter() - start_time

    avg_ms = (total_time / num_iterations) * 1000.0

    print(f"  Tarayanan Parça Sayısı : {num_chunks} adet")
    print(f"  Toplam Test Sayısı    : {num_iterations} sorgu")
    print(f"  Ortalama Arama Süresi : {avg_ms:.4f} ms / sorgu")
    print(f"  Saniyedeki Sorgu (QPS): {num_iterations / total_time:.2f} query/sec")
    print("=" * 60)
    return avg_ms


def benchmark_end_to_end_rag():
    """RAG Engine yanıt üretimi TTFT ve TPS performans ölçümü."""
    print("\n" + "=" * 60)
    print(" 2. RAG ENGINE TTFT VE TPS BENCHMARK'I")
    print("=" * 60)

    try:
        from rag_engine import RAGEngine
        engine = RAGEngine()
        print("  RAG Engine yükleniyor...")
        engine.initialize()

        test_query = "Sistem nasıl çalışır?"
        print(f"  Test Sorgusu: '{test_query}'")

        start_time = time.perf_counter()
        first_token_time = None
        token_count = 0

        print("  Streaming başlatıldı: ", end="", flush=True)
        for event_str in engine.answer_stream(test_query):
            if event_str.startswith("data: "):
                try:
                    payload = json.loads(event_str[6:].strip())
                    if payload.get("type") == "delta" and payload.get("content"):
                        if first_token_time is None:
                            first_token_time = time.perf_counter()
                        token_count += 1
                        print(".", end="", flush=True)
                except Exception:
                    pass

        total_time = time.perf_counter() - start_time
        print(" Tamamlandı.")

        ttft_s = (first_token_time - start_time) if first_token_time else total_time
        generation_time = total_time - ttft_s
        tps = token_count / generation_time if generation_time > 0 else 0

        print(f"\n  Time to First Token (TTFT) : {ttft_s * 1000.0:.2f} ms")
        print(f"  Üretilen Chunk Sayısı      : {token_count} adet")
        print(f"  Üretim Hızı (TPS)          : {tps:.2f} tokens/sec")
        print(f"  Toplam Cevap Süresi        : {total_time:.2f} saniye")
        print("=" * 60)

    except Exception as e:
        print(f"  [BİLGİ] LLM modeli yüklenemedi veya SDK kurulu değil: {e}")
        print("=" * 60)


if __name__ == "__main__":
    benchmark_vector_search()
    benchmark_end_to_end_rag()
