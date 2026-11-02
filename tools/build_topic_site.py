#!/usr/bin/env python3
"""Rebuild the site as 6 topic pages-in-one: each topic = one cheat-sheet image (everything to memorise), with the
per-question teaching figures folded inside a <details> box so nothing needs long scrolling.

Nicole 2026-11-02: 「睇吓有冇啲重複咗…集中啲即係一幅圖可以講晒啦唔想要scroll好耐囉」; calculator = Casio only
(TI-84 / Desmos removed). The pre-consolidation page is kept at archive/index-2026-11-02-before-consolidation.html.

Sheets come from ~/MyGithub/sat-math-corpus-analysis/docs/teaching-figures/make_topic_sheets.py
(sheet-<key>.png wide, sheet-<key>-tall.png phone). Add a new example figure: append to TOPICS and re-run.

Usage: python3 tools/build_topic_site.py
"""
from __future__ import annotations

import html
import logging
import re
import shutil
from pathlib import Path

SITE = Path(__file__).resolve().parents[1]
SRC = Path.home() / "MyGithub/sat-math-corpus-analysis/docs/teaching-figures"
DEST = SITE / "assets/fig"
INDEX = SITE / "index.html"
log = logging.getLogger("topic_site")

# key, number, title, [(file, source question, caption)]
TOPICS = [
    ("lines", "01", "直線", [
        ("line-forms.png", "PT5 M2 Q26", "直線 3 款寫法 + 特別直線"),
        ("m2q26-tangent.png", "PT5 M2 Q26", "切線 ⊥ 半徑：斜度反轉變號"),
        ("m2q26-check-options.png", "PT5 M2 Q26", "寫條線，逐個選項代 x 對 y"),
        ("m2q13-no-solution.png", "亞太C M2 Q13", "冇解 = 平行；同一條線 = 無限多解"),
        ("m2q20-system.png", "PT5 M2 Q20", "兩條聯立：直接加；或者 Casio EQN"),
        ("m2q12-boundary-points.png", "亞太C M2 Q12", "陰影不等式：界線上兩點代入"),
        ("m2q19-risky-row.png", "PT5 M2 Q19", "邊個表啱：逐行代入，一見唔過關就刪"),
        ("na2509-m1q17-quadrants.png", "2025-09 北美A M1 Q17", "不等式區域：逐格睇邊格冇陰影")]),
    ("quadratics", "02", "二次方程", [
        ("quadratic-forms.png", "亞太C M2 Q6", "二次 3 款寫法"),
        ("zeros-to-factors.png", "PT5 M1 Q26", "掂 x 軸兩點 → a(x − r)(x − s)"),
        ("q26-fast-methods.png", "PT5 M1 Q26", "Vx = 兩個 zero 中間 = −b/(2a)"),
        ("m2q7-zero-product.png", "PT5 M2 Q7", "兩邊一樣嘅數消走 → 乘埋 = 0"),
        ("apacc-q19-move-to-zero.png", "亞太C M1 Q19", "右邊唔係 0 → 先全部搬去一邊"),
        ("q27-methods.png", "PT5 M1 Q27", "g(7 − w) = 0 → 7 − w 係紅點"),
        ("q27-new-curve.png", "PT5 M1 Q27", "代入 = 第二條線；expand 唔會變線"),
        ("m2q24-discriminant.png", "PT5 M2 Q24", "冇實數解：先刪 a、c 一正一負"),
        ("m2q18-line-parabola.png", "亞太C M2 Q18", "直線同拋物線交點數 = b² − 4ac")]),
    ("trig", "03", "三角", [
        ("tan-cheatsheet.png", "PT5 M1 Q19", "tan 大角要背 6 樣"),
        ("sin-cos-sign.png", "亞太C M1 Q15", "sin = 上下、cos = 左右、tan = 斜度"),
        ("sin-sign-why.png", "亞太C M1 Q15", "三角形喺左上：直邊 +、橫邊 −、斜邊永遠 +"),
        ("135-split.png", "亞太C M1 Q15", "x 軸係直線 180°：135° + 45°"),
        ("sin45-sin135.png", "亞太C M1 Q15", "sin 45° = sin 135°：照鏡，高度一樣"),
        ("four-45s.png", "亞太C M1 Q15", "四支針細角都係 45°"),
        ("sin-height.gif", "亞太C M1 Q15", "動畫：sin = 針尖有幾高"),
        ("tan-as-slope.png", "PT5 M1 Q19", "tan = 斜度"),
        ("full-turn.gif", "PT5 M1 Q19", "動畫：轉成個圈等於冇轉"),
        ("30-60-90.png", "PT5 M2 Q21", "30-60-90 由嚟同點認"),
        ("m2q21-inscribed-rect.png", "PT5 M2 Q21", "長方形喺圓入面：對角線 = 直徑")]),
    ("exponential", "04", "指數", [
        ("what-is-exponential.png", "PT5 M1 Q24", "指數圖係乜：x 喺頭頂，每格 ×3"),
        ("exp-flip.gif", "PT5 M1 Q24", "動畫：3ˣ → 反轉 → 搬低 3 → 冇最低點"),
        ("exp-no-min.png", "PT5 M1 Q24", "負號反轉；-3 係掂唔到嘅天花板"),
        ("m2q16-read-graph.png", "亞太C M2 Q16", "點睇 -3ˣ + k 嘅圖"),
        ("m2q22-divide.png", "亞太C M2 Q22", "指數 + 兩個值 → 兩條式相除"),
        ("m2q22-steps.png", "亞太C M2 Q22", "每行 1 步乘同一個數"),
        ("m2q25-simple.png", "PT5 M2 Q25", "頭頂 t 前面個數 = 一年乘幾多次（未教明）"),
        ("m2q25-exp-period.png", "PT5 M2 Q25", "計數器 = 1 嗰陣係幾耐")]),
    ("geometry", "05", "幾何", [
        ("m2q19-similar.png", "亞太C M2 Q19", "證相似：AA 或 SAS"),
        ("m2q17-map.png", "亞太C M2 Q17", "地圖縮細 70%：剩 30%，每吋代表多啲"),
        ("na2509-m1q7-pyramid.png", "2025-09 北美A M1 Q7", "金字塔／圓錐體積 = 底 × 高 ÷ 3"),
        ("na2509-m2q21-units.png", "2025-09 北美A M2 Q21", "單位鏈：面積要除 3.28 兩次")]),
    ("moves", "06", "固定動作", [
        ("apacc-q22-plug100.png", "亞太C M1 Q22", "百分比題代 c = 100"),
        ("m2q23-plug-k2.png", "PT5 M2 Q23", "代 k = 1 會呃人，代 2"),
        ("m2q14-classes.png", "亞太C M2 Q14", "分段收費：逐堂畫出嚟再對選項"),
        ("abs-two-cases.png", "亞太C M2 Q9", "絕對值 = 離 0 有幾遠 → 兩個情況")]),
]

CSS = """
    .topic { padding: clamp(2rem, 5vw, 3.5rem) 0; border-top: 3px solid var(--ink); scroll-margin-top: 4.5rem; }
    .topic h2 { margin: 0 0 1rem; font-size: clamp(1.8rem, 5vw, 2.6rem); }
    .topic h2 span { color: var(--blue, #1d55be); margin-right: .5rem; }
    .topic .sheet { display: block; width: 100%; height: auto; border: 2px solid var(--ink); background: #fff; }
    .topic details { margin-top: 1rem; border: 2px dashed var(--muted, #888); padding: .6rem .9rem; }
    .topic summary { cursor: pointer; font-weight: 800; font-size: 1.05rem; }
    .topic .examples { display: grid; gap: 1.2rem; margin-top: 1rem; }
    @media (min-width: 64rem) { .topic .examples { grid-template-columns: 1fr 1fr; } }
    .topic .examples figure { margin: 0; padding: .35rem; border: 1.5px solid var(--ink); background: #fff; }
    .topic .examples img { width: 100%; height: auto; display: block; }
    .topic .examples figcaption { font-size: .95rem; padding: .4rem .2rem 0; }
    .page-head { padding: 1.5rem 0 1rem; }
    .page-head h1 { margin: 0; font-size: clamp(1.6rem, 5vw, 2.4rem); }
    .page-head p { margin: .4rem 0 0; }
"""


def topic_html(key: str, num: str, title: str, figs: list[tuple[str, str, str]]) -> str:
    e = html.escape
    out = [f'      <section class="topic" id="{key}">',
           f'        <h2><span>{num}</span>{e(title)}</h2>',
           f'        <a href="assets/fig/sheet-{key}-tall.png" aria-label="打開大圖">',
           '          <picture>',
           f'            <source media="(max-width: 48rem)" srcset="assets/fig/sheet-{key}-tall.png">',
           f'            <img class="sheet" src="assets/fig/sheet-{key}.png" alt="{e(title)}：要背嘅嘢一頁睇晒" loading="lazy">',
           '          </picture>',
           '        </a>',
           '        <details>',
           f'          <summary>例題圖（{len(figs)} 張，撳開先睇）</summary>',
           '          <div class="examples">']
    for f, src, cap in figs:
        out += ['            <figure>',
                f'              <a href="assets/fig/{f}"><img src="assets/fig/{f}" alt="{e(cap)}" loading="lazy"></a>',
                f'              <figcaption><strong>{e(src)}</strong>：{e(cap)}</figcaption>',
                '            </figure>']
    out += ['          </div>', '        </details>', '      </section>', '']
    return "\n".join(out)


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    DEST.mkdir(parents=True, exist_ok=True)
    needed = [f"sheet-{k}{s}.png" for k, *_ in TOPICS for s in ("", "-tall")]
    needed += [f for *_, figs in TOPICS for f, _, _ in figs]
    for f in needed:
        src = SRC / f
        if not src.exists():
            raise SystemExit(f"missing {src}")
        shutil.copy2(src, DEST / f)
    used = set(needed)
    stale = [p.name for p in DEST.iterdir() if p.name not in used]
    log.info("copied %d files; files in assets/fig not used by any topic: %s", len(needed), stale or "none")

    s = INDEX.read_text()
    nav = "".join(f'      <a href="#{k}" data-no="{n}">{html.escape(t)}</a>\n' for k, n, t, _ in TOPICS)
    s = re.sub(r'(<nav class="rail"[^>]*>\n).*?(    </nav>)', lambda m: m.group(1) + nav + m.group(2), s, count=1, flags=re.S)
    body = ('      <header class="page-head">\n'
            '        <h1 style="font-size: clamp(1.5rem, 4vw, 2.2rem); line-height: 1.2; max-width: none;">SAT Math 一題型一頁</h1>\n'
            '        <p>每頁一張圖講晒要背嘅嘢；例題圖收埋喺下面，撳開先見。計數機只用 Casio fx-991ES Plus C。</p>\n'
            '      </header>\n\n'
            + "\n".join(topic_html(*t) for t in TOPICS)
            + '      <footer>\n        Nicole’s SAT Math working sheet · 見到乜 → 做乜 · 固定動作，唔靠 pattern\n      </footer>\n')
    s = re.sub(r'(<main id="main">\n).*?(    </main>)', lambda m: m.group(1) + body + m.group(2), s, count=1, flags=re.S)
    marker = "    /* topic-site */\n"
    if marker not in s:
        s = s.replace("  </style>", marker + CSS + "  </style>", 1)
    INDEX.write_text(s)
    log.info("wrote %s with %d topics", INDEX.name, len(TOPICS))


if __name__ == "__main__":
    main()
