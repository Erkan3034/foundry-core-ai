"""
Foundry RAG Assistant - CLI Interface
Komut satirindan calisan interaktif arayuz.
"""

import argparse
import logging
import sys
from pathlib import Path

from config import CONFIG
from database import db
from ingestion import DocumentIngestor, run_ingestion
from rag_engine import RAGEngine

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def interactive_mode():
    """Interaktif sohbet modu."""
    print("\n" + "="*60)
    print("FOUNDRY RAG ASISTAN")
    print("Yerel belgeleriniz uzerinde soru-cevap yapin")
    print("="*60)
    print("Komutlar:")
    print("  /quit  - Cikis")
    print("  /stats - Istatistikler")
    print("  /clear - Ekrani temizle")
    print("="*60 + "\n")

    with RAGEngine() as engine:
        while True:
            try:
                query = input("\nSorunuz: ").strip()

                if not query:
                    continue

                if query.lower() == "/quit":
                    break

                if query.lower() == "/stats":
                    stats = db.get_stats()
                    print(f"\nIstatistikler:")
                    print(f"   Belgeler: {stats['documents']}")
                    print(f"   Parcalar: {stats['chunks']}")
                    print(f"   Embedding'li: {stats['embedded_chunks']}")
                    continue

                if query.lower() == "/clear":
                    print("\033[H\033[J", end="")
                    continue

                # Yanit al
                print("\n", end="", flush=True)
                result = engine.answer(query)

                print(result["answer"])

                if result["sources"]:
                    print(f"\nKaynaklar: {', '.join(result['sources'])}")

                print(f"\nGuven: {result['confidence']:.2%} | Parca: {result['retrieved_chunks']}")

            except KeyboardInterrupt:
                print("\n\nCikiliyor...")
                break
            except Exception as e:
                logger.error(f"Hata: {e}")
                print(f"Hata: {e}")

    print("\nGorusmek uzere!\n")


def ingest_command(args):
    """Belge ingestion komutu."""
    docs_path = Path(args.path) if args.path else CONFIG.docs_path
    run_ingestion(docs_path, force=args.force)


def stats_command():
    """Istatistikleri goster."""
    stats = db.get_stats()
    print("\nVeritabani Istatistikleri")
    print("-" * 40)
    print(f"Belgeler:        {stats['documents']}")
    print(f"Toplam Parca:    {stats['chunks']}")
    print(f"Embedding'li:    {stats['embedded_chunks']}")
    print(f"Embedding'siz:   {stats['chunks'] - stats['embedded_chunks']}")
    print("-" * 40)


def main():
    parser = argparse.ArgumentParser(
        description="Foundry RAG Assistant - Yerel AI Asistani",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ornek kullanim:
  python main.py                        # Interaktif mod
  python main.py ingest                 # Belgeleri isle
  python main.py ingest --path ./docs   # Belirli dizini isle
  python main.py ingest --force         # Tum dosyalari yeniden isle
  python main.py stats                  # Istatistikleri goster
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="Komutlar")

    # Ingest komutu
    ingest_parser = subparsers.add_parser("ingest", help="Belgeleri isle")
    ingest_parser.add_argument("--path", type=str, help="Belgeler dizini")
    ingest_parser.add_argument("--force", action="store_true", help="Daha once islenmis dosyalari yeniden isle")

    # Stats komutu
    subparsers.add_parser("stats", help="Istatistikleri goster")

    args = parser.parse_args()

    if args.command == "ingest":
        ingest_command(args)
    elif args.command == "stats":
        stats_command()
    else:
        interactive_mode()


if __name__ == "__main__":
    main()
