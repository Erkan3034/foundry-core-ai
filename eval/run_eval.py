"""
Foundry RAG Assistant - Yanit Kalitesi Degerlendirme Kosucusu

Unit testler kodun calistigini gosterir; bu betik asistanin DOGRU cevap
verdigini olcer. Ciktisi eval/RESULTS.md dosyasina yazilir.

Kullanim:
    python eval/run_eval.py
"""

import json
import logging
import sys
import time
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from rag_engine import RAGEngine  # noqa: E402

logging.basicConfig(level=logging.WARNING, format="%(levelname)s - %(message)s")

EVAL_DIR = Path(__file__).resolve().parent
QUESTIONS_PATH = EVAL_DIR / "questions.json"
RESULTS_PATH = EVAL_DIR / "RESULTS.md"

# Sistem promptunun uretmesi beklenen reddetme ifadeleri.
REFUSAL_MARKERS = (
    "bilgi bulunmuyor",
    "bilgi bulunmamaktadir",
    "no information found",
    "elimdeki belgelerde",
)

MAX_REASONABLE_ANSWER_CHARS = 3000


def is_refusal(answer: str) -> bool:
    low = answer.lower()
    return any(marker in low for marker in REFUSAL_MARKERS)


def score(question: dict, result: dict, error: str | None) -> tuple[str, str]:
    """(durum, not) dondurur. durum: GECTI | KALDI | INCELE"""
    if error:
        return "KALDI", f"istisna: {error}"

    answer = result["answer"]
    sources = result["sources"]
    tip = question["tip"]

    if tip == "cevaplanabilir":
        keys = question["beklenen_anahtarlar"]
        content_ok = any(k.lower() in answer.lower() for k in keys)
        source_ok = question["beklenen_kaynak"] in sources
        if content_ok and source_ok:
            return "GECTI", "icerik + kaynak dogru"
        if content_ok:
            return "KALDI", f"icerik dogru, kaynak yanlis (donen: {sources})"
        if source_ok:
            return "KALDI", f"kaynak dogru, beklenen deger yok ({keys})"
        return "KALDI", f"ne beklenen deger ne dogru kaynak (donen: {sources})"

    if tip in ("cevaplanamaz", "tuzak"):
        if is_refusal(answer):
            return "GECTI", "dogru sekilde reddetti"
        return "KALDI", "UYDURDU - belgede olmayan bilgiye cevap uretti"

    # kenar_durum: cokmemesi ve makul uzunluk yeterli; icerik manuel incelenir.
    if len(answer) > MAX_REASONABLE_ANSWER_CHARS:
        return "KALDI", f"asiri uzun yanit ({len(answer)} karakter) - dongu suphesi"
    return "INCELE", "cokmedi, icerik manuel incelenmeli"


def main() -> int:
    data = json.loads(QUESTIONS_PATH.read_text(encoding="utf-8"))
    questions = data["sorular"]

    print(f"{len(questions)} soru degerlendirilecek. Modeller yukleniyor...")
    engine = RAGEngine()
    engine.initialize()
    print("Modeller hazir.\n")

    rows = []
    for q in questions:
        print(f"[{q['id']}] {q['soru'][:60] or '(bos sorgu)'}", flush=True)
        error = None
        result = {"answer": "", "sources": [], "retrieved_chunks": 0, "confidence": 0.0}
        start = time.perf_counter()
        try:
            result = engine.answer(q["soru"])
        except Exception as exc:  # noqa: BLE001 - degerlendirme her hatayi kaydetmeli
            error = f"{type(exc).__name__}: {exc}"
        elapsed = time.perf_counter() - start

        durum, note = score(q, result, error)
        rows.append({
            "id": q["id"],
            "tip": q["tip"],
            "soru": q["soru"],
            "durum": durum,
            "not": note,
            "yanit": result["answer"],
            "kaynaklar": result["sources"],
            "parca": result["retrieved_chunks"],
            "guven": result["confidence"],
            "sure": elapsed,
        })
        print(f"    -> {durum} ({elapsed:.2f}s) {note}\n", flush=True)

    engine.shutdown()
    write_report(rows)
    print(f"Rapor yazildi: {RESULTS_PATH}")

    failed = sum(1 for r in rows if r["durum"] == "KALDI")
    return 1 if failed else 0


def write_report(rows: list[dict]) -> None:
    total = len(rows)
    passed = sum(1 for r in rows if r["durum"] == "GECTI")
    failed = sum(1 for r in rows if r["durum"] == "KALDI")
    review = sum(1 for r in rows if r["durum"] == "INCELE")
    scored = passed + failed
    latencies = sorted(r["sure"] for r in rows)

    def by_type(tip: str) -> tuple[int, int]:
        subset = [r for r in rows if r["tip"] == tip]
        return sum(1 for r in subset if r["durum"] == "GECTI"), len(subset)

    lines = [
        "# Yanit Kalitesi Degerlendirme Sonuclari",
        "",
        f"Calistirma: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
        "Bu rapor `python eval/run_eval.py` ile uretilir. Unit testlerden farki:",
        "kodun calistigini degil, asistanin **dogru cevap verdigini** olcer.",
        "",
        "## Ozet",
        "",
        f"- Toplam soru: **{total}**",
        f"- Gecti: **{passed}** / {scored} otomatik puanlanan"
        + (f" (%{100 * passed / scored:.0f})" if scored else ""),
        f"- Kaldi: **{failed}**",
        f"- Manuel inceleme: {review}",
        f"- Medyan yanit suresi: **{latencies[len(latencies) // 2]:.2f} s**",
        f"- En yavas yanit: {latencies[-1]:.2f} s",
        "",
        "### Kategori bazinda",
        "",
        "| Kategori | Gecti / Toplam | Ne olcuyor |",
        "|---|---|---|",
    ]

    descriptions = {
        "cevaplanabilir": "Belgedeki bilgiyi bulup dogru kaynakla veriyor mu",
        "cevaplanamaz": "Belgede olmayan bilgiyi uydurmuyor mu",
        "tuzak": "Anahtar kelime eslesiyor ama cevap yok - yine de reddediyor mu",
        "kenar_durum": "Bozuk/asiri genel girdide cokmuyor mu",
    }
    for tip, desc in descriptions.items():
        ok, n = by_type(tip)
        if n:
            lines.append(f"| {tip} | {ok} / {n} | {desc} |")

    lines += ["", "## Soru bazinda sonuclar", "",
              "| ID | Tip | Soru | Durum | Kaynak | Parca | Guven | Sure |",
              "|---|---|---|---|---|---|---|---|"]

    for r in rows:
        soru = r["soru"].replace("|", "\\|") or "_(bos)_"
        kaynak = ", ".join(r["kaynaklar"]) or "-"
        lines.append(
            f"| {r['id']} | {r['tip']} | {soru} | **{r['durum']}** | "
            f"{kaynak} | {r['parca']} | {r['guven']:.3f} | {r['sure']:.2f}s |"
        )

    lines += ["", "## Yanit detaylari", ""]
    for r in rows:
        lines += [
            f"### {r['id']} - {r['durum']}",
            "",
            f"**Soru:** {r['soru'] or '_(bos sorgu)_'}",
            "",
            f"**Degerlendirme:** {r['not']}",
            "",
            "**Yanit:**",
            "",
            "```",
            r["yanit"] or "(bos)",
            "```",
            "",
        ]

    RESULTS_PATH.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    sys.exit(main())
