# ADR-0001: Chat modeli olarak qwen2.5-1.5b (instruct)

**Durum:** Kabul edildi
**Tarih:** 2026-07-21

## Baglam

Program plani chat modeli icin "Phi-3.5 Mini veya benzeri 3-5B parametreli bir
model" oneriyordu. Hedef donanim 2 GB VRAM'li bir dizustu GPU (GeForce MX450) ve
uygulamanin birincil dili Turkce.

Denenen alternatiflerde iki ayri sorun gozlendi:

- **Reasoning modelleri (`qwen3-0.6b` sinifi):** Yanittan once uzun bir `<think>`
  blogu uretiyor. Bu blok token butcesini tuketiyor; `MAX_TOKENS` sinirina think
  blogunun icinde ulasilinca kullaniciya bos yanit donuyor.
- **Cok kucuk modeller (0.5B):** Turkce dilbilgisi ve terim tutarliligi kabul
  edilemez seviyede.

## Karar

Chat modeli olarak **`qwen2.5-1.5b`** (instruct varyanti) kullanilir.

## Gerekce

- Instruct modeller `<think>` blogu uretmez; token butcesinin tamami gorunur
  yanita gider.
- 1.5B, hedef donanimda chat modelinin GPU'ya sigmasina izin verirken 0.5B'ye
  gore belirgin sekilde daha iyi Turkce uretiyor.
- Plan "bu programda hiz onceliklidir, ogrenciler hizli geri bildirim alsin"
  diyor; 1.5B bu onceligi 3-5B'den daha iyi karsiliyor.

## Sonuclar

- Yanit kalitesi 3-5B bir modelin altinda. Karmasik cok adimli cikarim isteyen
  sorularda zayif kalir; bu bilinen ve kabul edilmis bir sinirdir.
- Model aliasi `CHAT_MODEL_ALIAS` ile degistirilebilir birakildi. Daha guclu
  donanimda `phi-4-mini` tek satirlik degisiklikle denenebilir.
- `<think>` blogu ihtimaline karsi hem streaming hem streaming olmayan yolda
  filtreleme kodu korundu ([rag_engine.py](../../rag_engine.py)); model degistirilirse
  bu koruma hala gereklidir.

## Reddedilen alternatifler

| Alternatif | Neden reddedildi |
|---|---|
| Phi-3.5 / phi-4-mini (planin onerisi) | Hedef donanimda bellek basincı; yanit suresi hedefin uzerine cikiyor |
| qwen3-0.6b (reasoning) | `<think>` blogu token butcesini tuketip bos yanit uretiyor |
| qwen2.5-0.5b | Turkce kalitesi yetersiz |
