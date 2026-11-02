#!/usr/bin/env python3
"""Put every teaching figure from the corpus repo onto the site, grouped by topic (Nicole 2026-11-02:
「全部擺上條link啦我要睇㗎嘛」).

Copies images from ~/MyGithub/sat-math-corpus-analysis/docs/teaching-figures/ into assets/fig/ and regenerates the
HTML between the GALLERY markers (sections) and NAV-GALLERY markers (rail links) in index.html.
Add a new figure: append it to SECTIONS below and re-run.

Usage: python3 tools/build_galleries.py
"""
from __future__ import annotations

import html
import logging
import shutil
from pathlib import Path

SITE = Path(__file__).resolve().parents[1]
SRC = Path.home() / "MyGithub/sat-math-corpus-analysis/docs/teaching-figures"
DEST = SITE / "assets/fig"
INDEX = SITE / "index.html"

log = logging.getLogger("galleries")

# (anchor, number, title, subtitle, [(file, source question, caption)])
SECTIONS = [
    ("trig-signs", "09", "三角比：正負同細角",
     "數值永遠用「條線同最近 x 軸」嘅細角；大角只係話你知方向（正定負）。sin 睇上下，cos 睇左右，tan 睇斜度。",
     [("sin-cos-sign.png", "亞太C M1 Q15", "sin = 上下、cos = 左右、tan = 斜度；135° 指左上 → sin 正"),
      ("sin-sign-why.png", "亞太C M1 Q15", "三角形喺左上：直邊 +、橫邊 −、斜邊永遠 +"),
      ("135-split.png", "亞太C M1 Q15", "x 軸係直線 180°：135° + 45°，三角形用剩低嗰份"),
      ("sin45-sin135.png", "亞太C M1 Q15", "sin 45° = sin 135°：照鏡，高度一樣"),
      ("four-45s.png", "亞太C M1 Q15", "四支針細角都係 45°，所以統一由右邊逆時針數"),
      ("sin-height.gif", "亞太C M1 Q15", "動畫：sin = 針尖有幾高"),
      ("tan-as-slope.png", "PT5 M1 Q19", "tan = 斜度：60° 同 120°"),
      ("full-turn.gif", "PT5 M1 Q19", "動畫：轉成個圈等於冇轉")]),
    ("special-triangles", "10", "特別三角形",
     "30-60-90 = 1 : √3 : 2（斜邊 = 短邊 × 2），由等邊三角形切一半得嚟；45-45-90 = 1 : 1 : √2。",
     [("30-60-90.png", "PT5 M2 Q21", "30-60-90 由嚟同點認"),
      ("m2q21-inscribed-rect.png", "PT5 M2 Q21", "長方形喺圓入面：對角線 = 直徑 = 2s")]),
    ("exponential", "11", "指數圖",
     "x 喺頭頂 = 指數。負號反轉；尾嗰個數係掂唔到嘅線；一定冇最細值、冇最大值。",
     [("what-is-exponential.png", "PT5 M1 Q24", "指數圖係乜：x 喺頭頂，每格 ×3"),
      ("exp-flip.gif", "PT5 M1 Q24", "動畫：3ˣ → 反轉 → 搬低 3 → 冇最低點"),
      ("exp-no-min.png", "PT5 M1 Q24", "負號反轉；-3 係掂唔到嘅天花板"),
      ("m2q16-read-graph.png", "亞太C M2 Q16", "點睇 -3ˣ + k 嘅圖：紅點 (0, k − 1)，左邊貼住 y = k"),
      ("m2q22-divide.png", "亞太C M2 Q22", "固定動作：指數 + 兩個值 → 兩條式相除"),
      ("m2q22-steps.png", "亞太C M2 Q22", "每行 1 步乘同一個數"),
      ("m2q25-simple.png", "PT5 M2 Q25", "頭頂 t 前面個數 = 一年乘幾多次（未教明，要再教）"),
      ("m2q25-exp-period.png", "PT5 M2 Q25", "計數器 = 1 嗰陣係幾耐")]),
    ("lines", "12", "直線",
     "3 款寫法：y = mx + b、y = m(x − Px) + Py、Ax + By = C。平行 = 斜度一樣；垂直 = 反轉 + 變號。",
     [("line-forms.png", "PT5 M2 Q26", "直線 3 款寫法 + 特別直線"),
      ("m2q26-tangent.png", "PT5 M2 Q26", "切線 ⊥ 半徑：斜度反轉變號"),
      ("m2q26-check-options.png", "PT5 M2 Q26", "寫條線，逐個選項代 x 對 y"),
      ("m2q13-no-solution.png", "亞太C M2 Q13", "冇解 = 平行；同一條線 = 無限多解"),
      ("m2q12-boundary-points.png", "亞太C M2 Q12", "陰影不等式：界線上兩點代入"),
      ("m2q20-system.png", "PT5 M2 Q20", "兩條聯立：直接加；或者 Casio EQN"),
      ("m2q19-risky-row.png", "PT5 M2 Q19", "邊個表啱：逐行代入，一見唔過關就刪")]),
    ("quadratics", "13", "二次方程",
     "3 款寫法：標準式、頂點式、因式式。乘埋 = 0 先可以逐個括號 = 0；幾多個解睇 b² − 4ac。",
     [("quadratic-forms.png", "亞太C M2 Q6", "二次 3 款寫法"),
      ("zeros-to-factors.png", "PT5 M1 Q26", "掂 x 軸兩點 → a(x − r)(x − s)"),
      ("q26-fast-methods.png", "PT5 M1 Q26", "Vx = 兩個 zero 中間 = −b/(2a)"),
      ("m2q7-zero-product.png", "PT5 M2 Q7", "兩邊一樣嘅數消走 → 乘埋 = 0"),
      ("apacc-q19-move-to-zero.png", "亞太C M1 Q19", "右邊唔係 0 → 先全部搬去一邊"),
      ("q27-methods.png", "PT5 M1 Q27", "g(7 − w) = 0 → 7 − w 係紅點"),
      ("q27-new-curve.png", "PT5 M1 Q27", "代入 = 第二條線；expand 唔會變線"),
      ("m2q24-discriminant.png", "PT5 M2 Q24", "冇實數解：先刪 a、c 一正一負"),
      ("m2q18-line-parabola.png", "亞太C M2 Q18", "直線同拋物線交點數 = b² − 4ac")]),
    ("misc", "14", "百分比、代數字、情境、幾何",
     "冇實數嘅百分比題代 100；只知正負代 ±1；代數字揀選項默認代 2，要代兩個數驗證。",
     [("apacc-q22-plug100.png", "亞太C M1 Q22", "百分比題代 c = 100"),
      ("m2q23-plug-k2.png", "PT5 M2 Q23", "代 k = 1 會呃人，代 2"),
      ("m2q14-classes.png", "亞太C M2 Q14", "分段收費：逐堂畫出嚟再對選項"),
      ("m2q17-map.png", "亞太C M2 Q17", "地圖縮細 70%：剩 30%，每吋代表多啲"),
      ("abs-two-cases.png", "亞太C M2 Q9", "絕對值 = 離 0 有幾遠 → 兩個情況"),
      ("m2q19-similar.png", "亞太C M2 Q19", "證相似：AA 或 SAS（夾住等角嗰兩條邊）")]),
]

BEGIN, END = "<!-- BEGIN GALLERY (tools/build_galleries.py) -->", "<!-- END GALLERY -->"
NBEGIN, NEND = "<!-- BEGIN NAV-GALLERY -->", "<!-- END NAV-GALLERY -->"


def section_html(anchor: str, num: str, title: str, sub: str, figs: list[tuple[str, str, str]]) -> str:
    e = html.escape
    parts = [f'      <section class="lesson gallery" id="{anchor}" aria-labelledby="{anchor}Title">',
             '        <header class="lesson-head">',
             f'          <div class="lesson-number">{num}</div>',
             '          <div>',
             '            <p class="section-kicker"><span class="status">圖庫</span></p>',
             f'            <h2 id="{anchor}Title">{e(title)}</h2>',
             '          </div>',
             f'          <p class="lesson-subtitle">{e(sub)}</p>',
             '        </header>',
             '        <div class="gallery-grid">']
    for f, src, cap in figs:
        parts += ['          <figure class="diagram-panel">',
                  f'            <a href="assets/fig/{f}" aria-label="打開大圖"><img src="assets/fig/{f}" alt="{e(cap)}" loading="lazy"></a>',
                  f'            <figcaption class="diagram-caption"><strong>{e(src)}</strong>：{e(cap)}</figcaption>',
                  '          </figure>']
    parts += ['        </div>', '      </section>', '']
    return "\n".join(parts)


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    DEST.mkdir(parents=True, exist_ok=True)
    n = 0
    for *_, figs in SECTIONS:
        for f, _, _ in figs:
            src = SRC / f
            if not src.exists():
                raise SystemExit(f"missing figure {src}")
            shutil.copy2(src, DEST / f)
            n += 1
    log.info("copied %d figures into %s", n, DEST)

    s = INDEX.read_text()
    body = "\n".join(section_html(*sec) for sec in SECTIONS)
    block = f"      {BEGIN}\n{body}      {END}\n"
    if BEGIN in s:
        s = s[:s.index(BEGIN) - 6] + block + s[s.index(END) + len(END) + 1:]
        log.info("replaced existing gallery block")
    else:
        anchor = '      <aside class="not-yet">'
        assert s.count(anchor) == 1
        s = s.replace(anchor, block + "\n" + anchor)
        log.info("inserted new gallery block before not-yet aside")

    nav = "".join(f'      <a href="#{a}" data-no="{num}">{html.escape(t)}</a>\n' for a, num, t, _, _ in SECTIONS)
    nblock = f"      {NBEGIN}\n{nav}      {NEND}\n"
    if NBEGIN in s:
        s = s[:s.index(NBEGIN) - 6] + nblock + s[s.index(NEND) + len(NEND) + 1:]
    else:
        anchor = '      <a href="#tan-angles" data-no="08">Tan 大角 / π</a>\n'
        assert s.count(anchor) == 1
        s = s.replace(anchor, anchor + nblock)
    css = "    .gallery-grid { display: grid; gap: 1.5rem; }\n"
    if css not in s:
        anchor = "    .diagram-panel img { width: 100%; height: auto; display: block; }\n"
        assert s.count(anchor) == 1
        s = s.replace(anchor, anchor + css + "    @media (min-width: 64rem) { .gallery-grid { grid-template-columns: 1fr 1fr; } }\n"
                      + "    .gallery figure.diagram-panel { margin: 0; padding: .35rem; }\n")
    INDEX.write_text(s)
    log.info("wrote %s: %d sections", INDEX.name, len(SECTIONS))


if __name__ == "__main__":
    main()
