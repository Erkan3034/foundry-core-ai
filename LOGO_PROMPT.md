# Foundry RAG Assistant — Logo Üretim Prompt'ları

## 0. Neden bu yaklaşım

Görsel modeller "logo" kelimesini duyunca varsayılan olarak *AI slop* üretir:
3B bevel, glow, degrade küre, beyin+devre kartı, altıgen+node ağı, swoosh, sahte metin.
Bunu engellemenin yolu **stil değil, kısıt** yazmaktır: tek renk, düz vektör,
sabit çizgi kalınlığı, metin yok, ızgaraya oturan geometri. Renk ve tipografi
sonradan Figma/Illustrator'da eklenir — modele bırakılmaz.

**Kural: mark (sembol) ürettir, wordmark ürettirme.** Metni sen dizersin.

---

## 1. Ortak stil bloğu (her prompt'un sonuna eklenir)

```
Style constraints: flat 2D vector logo mark, monoline construction with a single
uniform stroke weight, geometry built on a strict 24x24 grid with 2px corner radii,
generous negative space, perfectly balanced optical weight, pure black (#000000)
shape on a flat white (#FFFFFF) background, no color, no gradient, no shading,
no drop shadow, no glow, no bevel, no 3D, no perspective, no texture, no
photorealism, no background scene. Centered, isolated, with even padding on all
sides. Must remain legible and unambiguous when scaled down to 16x16 pixels.
Designed in the tradition of Swiss / International Typographic Style corporate
marks — restrained, rational, timeless, not trendy.
```

## 2. Ortak negatif prompt

```
text, letters, words, typography, wordmark, lettering, watermark, signature,
brain, neural network, connected nodes, circuit board traces, microchip with
glowing lines, hexagon grid, infinity loop, swoosh, ribbon, orbit rings, atom,
lightbulb, robot, mascot, character, hands, sparkles, stars, magic wand,
gradient mesh, holographic, iridescent, chrome, glassmorphism, neon glow,
lens flare, bokeh, drop shadow, 3D render, isometric, embossed, gloss, bevel,
photo, mockup, business card, presentation slide, multiple logo variations,
grid of options, framing border, cluttered detail, thin hairlines
```

---

## 3. Üç kavramsal yön (birbirinden bağımsız, hepsini dene)

### Yön A — "Retrieval" (belge → cevap)
Uygulamanın çekirdek fiili: bir belge yığınından ilgili parçayı çekip getirmek.

```
A minimal geometric logo mark: three stacked rectangular sheets seen head-on,
slightly offset from each other like a fanned deck. The middle sheet is pulled
forward and out of the stack, breaking the alignment — it is the retrieved one.
The pulled sheet's leading edge terminates in a clean angular arrow point.
Only the outlines are drawn; the sheets read as pure rectangles, no page-corner
folds, no lines of fake text inside them.
[ORTAK STİL BLOĞU]
```

### Yön B — "Foundry" (döküm / kıvılcım)
Marka adına bağlanır; mevcut UI'daki kıvılcım ikonunun olgun hâli.

```
A minimal geometric logo mark: a spark rendered as four tapered rays radiating
from a single center point — two long on the vertical axis, two short on the
horizontal — forming a sharp four-pointed star with concave sides. The center
is hollow, an empty square aperture, so the mark reads as a spark struck around
a void rather than a solid burst. Strictly symmetrical on both axes, drawn with
straight edges and precise angles only, no curves, no small satellite sparkles.
[ORTAK STİL BLOĞU]
```

### Yön C — "Local / on-device" (yerelde çalışan zekâ)
Ürünün gerçek farkı: bulut yok, her şey cihazda.

```
A minimal geometric logo mark: a square chip die with four short connector pins
extending from each of its four sides, drawn as a clean outline. Inside the
square, instead of circuitry, sits a single solid horizontal bar offset above
center and a shorter bar below it — an abstract reduction of a line of stored
text. The inner bars never touch the outer square. The whole mark reads as a
memory chip and a document simultaneously, depending on how long you look.
[ORTAK STİL BLOĞU]
```

---

## 4. Sonrası (asıl kaliteyi buradan alırsın)

1. **Model çıktısı taslaktır, final değil.** En iyi 3-4 çıktıyı seç.
2. Illustrator / Figma'da **sıfırdan yeniden çiz** — auto-trace kullanma; AI
   çıktısındaki düzensiz node'lar ölçeklendiğinde kendini belli eder.
3. Geometriyi ızgaraya oturt, çizgi kalınlığını tek değere sabitle.
4. Renk son adımda: marka degradesi `#8b5cf6 → #22d3ee`, 135°.
   Ama **mono siyah ve mono beyaz sürüm de zorunlu** — favicon ve tek renkli
   basımlar degradeyi taşımaz.
5. Test: 16px favicon, koyu zemin, açık zemin, gri tonlama, %50 bulanıklık
   (silüet hâlâ tanınıyor mu?).
6. Wordmark: mark + "Foundry RAG" — Inter Tight / IBM Plex Sans SemiBold,
   hafif negatif harf aralığı. Mark'ın x-yüksekliğine hizala.

## 5. Model bazlı notlar

- **Midjourney**: sona `--style raw --stylize 50 --ar 1:1 --no text` ekle.
  Düşük stylize, süslemeyi kırar.
- **Ideogram**: "Design" modu + Color palette: Monochrome. Metin yeteneği güçlü
  olduğu için negatif prompt'taki `text` maddesini mutlaka koru.
- **DALL·E / GPT Image**: prompt'u düzyazı olarak ver, madde işareti kullanma;
  ayrıca "single centered mark on plain white, no presentation mockup" diye bitir.
- **Flux**: kısıt bloğunu ikiye böl, tek seferde çok kısıt verince geometriyi
  bozuyor.
