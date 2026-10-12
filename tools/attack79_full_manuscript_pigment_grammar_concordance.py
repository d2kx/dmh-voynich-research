#!/usr/bin/env python3
"""
Attack 79: Full-Manuscript Computer-Vision Pigment & Spatial-Zone Extractor on `2002046.pdf`
vs. Dual-Matrix, 10-Bit Feature & Stem Concordance (Stratified by Section $I and Dialect $L)

Extracts objective RGB chromaticity and vertical spatial-zone coverage directly from
`2002046.pdf` across all transcribed folios:
  - `green_pct`: Verdigris/Malachite Green pigment fraction
  - `red_pct`  : Vermilion/Crimson Red pigment fraction
  - `blue_pct` : Azurite Blue/Violet pigment fraction
  - `dark_pct` : Heavy Dark Root/Pod/Wash pigment fraction
  - `top_paint_pct`, `mid_paint_pct`, `bot_paint_pct`: Painted illustration density in
    Upper Third (`y=0.10..0.38`), Middle Third (`y=0.38..0.66`), and Lower Third (`y=0.66..0.92`).

Tests (with 400-trial ($I, $L)-stratified permutation baselines):
1. Correlation between Visual Pigment Channels (`GREEN`, `RED`, `BLUE`, `DARK`, `BOT_MINUS_TOP`)
   and the 10-Bit Grammatical Features (`F1_OPEN`, `F2_Q_ACT`, `F3_L_APPL`, `F4_S_Y`, `F5_GALLOWS`,
   `F6_T_CLASS`, `F7_COMPOUND`, `F8_VERBAL_Y`, `F9_DENTAL_D`, `F10_A_RHO`).
2. Top Open-Class Stems & Words enriched on High-Red, High-Blue, High-Green, and Bottom-Root
   folios within the same Currier Language.
"""

import json
import math
import random
import re
from collections import Counter, defaultdict
from pathlib import Path

import fitz  # PyMuPDF
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
PDF_PATH = ROOT / "2002046.pdf"
INDEX_PATH = DATA_DIR / "folio_index.json"
ZL_PATH = DATA_DIR / "ZL3b-n.txt"
OUT_JSON = DATA_DIR / "attack79_full_manuscript_pigment_grammar_concordance.json"

LOCUS_RE = re.compile(r"^<f([0-9]+[rv][0-9]*|Ros)\.([^,>]+),([^>]+)>\s*(.*)$")


def clean_tokens(raw: str):
    s = re.sub(r"\{[^}]*\}", "", raw)
    s = re.sub(r"\[([^:\]]+):[^\]]+\]", r"\1", s)
    s = s.replace("<%>", " ").replace("<$>", " ").replace("<->", " ")
    s = re.sub(r"<[^>]*>", " ", s)
    s = re.sub(r"@[0-9]+;", "", s)
    s = re.sub(r"[^a-zA-Z.\s]", "", s).lower()
    return [t for t in s.replace(".", " ").split() if t]


def extract_page_pigments(doc, pdf_page_1based: int) -> dict:
    page = doc[pdf_page_1based - 1]
    pix = page.get_pixmap(dpi=36)
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    w, h = img.size
    pixels = img.load()

    green = 0
    red = 0
    blue = 0
    dark = 0
    top_paint = 0
    mid_paint = 0
    bot_paint = 0
    top_tot = 0
    mid_tot = 0
    bot_tot = 0
    total = 0

    for y in range(int(0.10 * h), int(0.92 * h) - 1, 2):
        yf = y / h
        for x in range(int(0.12 * w), int(0.88 * w) - 1, 2):
            r0, g0, b0 = pixels[x, y]
            r1, g1, b1 = pixels[x + 1, y]
            r2, g2, b2 = pixels[x, y + 1]
            r3, g3, b3 = pixels[x + 1, y + 1]
            r = (r0 + r1 + r2 + r3) * 0.25
            g = (g0 + g1 + g2 + g3) * 0.25
            b = (b0 + b1 + b2 + b3) * 0.25
            s_rgb = r + g + b

            is_green = (g >= r - 6) and (g - b > 18) and (s_rgb < 520)
            is_red = (r - g > 40) and (r - b > 58) and (r > 95) and (g < 148)
            is_blue = (b >= g - 4) and (r - b < 22) and (s_rgb < 470)
            is_dark = (s_rgb < 235) and (max(abs(r0 - r3), abs(g0 - g3)) < 35) and not is_green

            is_any = is_green or is_red or is_blue or is_dark
            total += 1
            if is_green:
                green += 1
            if is_red:
                red += 1
            if is_blue:
                blue += 1
            if is_dark:
                dark += 1

            if yf < 0.38:
                top_tot += 1
                if is_any:
                    top_paint += 1
            elif yf < 0.66:
                mid_tot += 1
                if is_any:
                    mid_paint += 1
            else:
                bot_tot += 1
                if is_any:
                    bot_paint += 1

    tot = max(total, 1)
    tp = top_paint / max(top_tot, 1) * 100.0
    mp = mid_paint / max(mid_tot, 1) * 100.0
    bp = bot_paint / max(bot_tot, 1) * 100.0
    return {
        "green_pct": round(green / tot * 100.0, 3),
        "red_pct": round(red / tot * 100.0, 3),
        "blue_pct": round(blue / tot * 100.0, 3),
        "dark_pct": round(dark / tot * 100.0, 3),
        "painted_total_pct": round((green + red + blue + dark) / tot * 100.0, 3),
        "top_paint_pct": round(tp, 3),
        "mid_paint_pct": round(mp, 3),
        "bot_paint_pct": round(bp, 3),
        "bot_minus_top_pct": round(bp - tp, 3),
    }


def compute_10bit_rates(words: list) -> dict:
    n = max(len(words), 1)
    f1 = sum(1 for w in words if any(g in w for g in ("k", "t", "p", "f", "ch", "sh"))) / n
    f2 = sum(1 for w in words if w.startswith("q")) / n
    f3 = sum(1 for w in words if w.startswith(("l", "ol", "qol", "dal")) and len(w) > 3) / n
    f4 = sum(1 for w in words if w.startswith(("s", "y")) or w.startswith("sh")) / n
    f5 = sum(1 for w in words if any(g in w for g in ("k", "t", "p", "f"))) / n
    f6 = sum(1 for w in words if any(g in w for g in ("t", "p"))) / n
    f7 = sum(1 for w in words if any(c in w for c in ("ckh", "cth", "cph", "cfh", "kch", "tch", "pch", "fch"))) / n
    f8 = sum(1 for w in words if w.endswith("y")) / n
    f9 = sum(1 for w in words if w.endswith("dy") or w.startswith("d")) / n
    f10 = sum(1 for w in words if "a" in w or w.endswith("r")) / n
    return {
        "F1_OPEN": f1,
        "F2_Q_ACT": f2,
        "F3_L_APPL": f3,
        "F4_S_Y_PLUME": f4,
        "F5_GALLOWS": f5,
        "F6_T_CLASS": f6,
        "F7_COMPOUND": f7,
        "F8_VERBAL_Y": f8,
        "F9_DENTAL_D": f9,
        "F10_A_RHOTIC": f10,
    }


def pearson_r(xs, ys) -> float:
    n = len(xs)
    if n < 3:
        return 0.0
    mx = sum(xs) / n
    my = sum(ys) / n
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    dx = sum((x - mx) ** 2 for x in xs)
    dy = sum((y - my) ** 2 for y in ys)
    return num / math.sqrt(dx * dy) if dx > 0 and dy > 0 else 0.0


def main():
    random.seed(42)
    idx_data = json.loads(INDEX_PATH.read_text(encoding="utf-8"))
    folio_to_pdf1 = {}
    for p in idx_data["pdf_pages"]:
        pnum = p["pdf1_page"]
        for fol in p.get("folios", []):
            folio_to_pdf1[fol] = pnum

    folios = []
    cur_meta = None
    for raw_line in ZL_PATH.read_text(encoding="utf-8", errors="replace").splitlines():
        raw_s = raw_line.strip()
        if not raw_s or raw_s.startswith("#"):
            continue
        if raw_s.startswith("<f") and ">" in raw_s and "." not in raw_s.split(">")[0]:
            fname = raw_s.split(">")[0][1:]
            tags = dict(re.findall(r"\$([A-Z])=([0-9A-Za-z]+)", raw_s))
            cur_meta = {
                "folio": fname,
                "Q": tags.get("Q", "U"),
                "I": tags.get("I", "U"),
                "L": tags.get("L", "U"),
                "H": tags.get("H", "U"),
                "words": [],
            }
            folios.append(cur_meta)
            continue

        m = LOCUS_RE.match(raw_s)
        if not m or cur_meta is None:
            continue
        ltype, raw_txt = m.group(3), m.group(4)
        if not ltype.startswith(("@P", "+P", "*P", "=P")):
            continue
        toks = clean_tokens(raw_txt)
        cur_meta["words"].extend(toks)

    doc = fitz.open(str(PDF_PATH))
    page_cache = {}
    valid_folios = []

    for f in folios:
        if len(f["words"]) < 25:
            continue
        pnum = folio_to_pdf1.get(f["folio"])
        if not pnum:
            continue
        if pnum not in page_cache:
            page_cache[pnum] = extract_page_pigments(doc, pnum)
        f["pigment"] = page_cache[pnum]
        f["f10"] = compute_10bit_rates(f["words"])
        valid_folios.append(f)

    # 1. Section-Level Pigment & Spatial Profiles
    by_sec = defaultdict(list)
    for f in valid_folios:
        by_sec[f["I"]].append(f)

    sec_pigment_summary = {}
    for sec, flist in sorted(by_sec.items()):
        n = len(flist)
        sec_pigment_summary[sec] = {
            "folios": n,
            "mean_green_pct": round(sum(x["pigment"]["green_pct"] for x in flist) / n, 3),
            "mean_red_pct": round(sum(x["pigment"]["red_pct"] for x in flist) / n, 3),
            "mean_blue_pct": round(sum(x["pigment"]["blue_pct"] for x in flist) / n, 3),
            "mean_dark_pct": round(sum(x["pigment"]["dark_pct"] for x in flist) / n, 3),
            "mean_painted_total_pct": round(sum(x["pigment"]["painted_total_pct"] for x in flist) / n, 3),
            "mean_bot_minus_top_pct": round(sum(x["pigment"]["bot_minus_top_pct"] for x in flist) / n, 3),
        }

    # 2. Within-(Section $I, Language $L) Stratified Permutation Test of Pigment <-> 10-Bit Features
    pigment_keys = ["green_pct", "red_pct", "blue_pct", "dark_pct", "painted_total_pct", "bot_minus_top_pct"]
    feat_keys = ["F1_OPEN", "F2_Q_ACT", "F3_L_APPL", "F4_S_Y_PLUME", "F5_GALLOWS", "F6_T_CLASS", "F7_COMPOUND", "F8_VERBAL_Y", "F9_DENTAL_D", "F10_A_RHOTIC"]

    buckets = defaultdict(list)
    for idx, f in enumerate(valid_folios):
        buckets[(f["I"], f["L"])].append(idx)

    significant_couplings = []
    for pk in pigment_keys:
        xs = [f["pigment"][pk] for f in valid_folios]
        for fk in feat_keys:
            ys = [f["f10"][fk] for f in valid_folios]
            obs_r = pearson_r(xs, ys)

            null_rs = []
            for _ in range(300):
                perm_ys = ys[:]
                for b_idxs in buckets.values():
                    if len(b_idxs) > 1:
                        vals = [ys[i] for i in b_idxs]
                        random.shuffle(vals)
                        for i, v in zip(b_idxs, vals):
                            perm_ys[i] = v
                null_rs.append(pearson_r(xs, perm_ys))

            mu = sum(null_rs) / len(null_rs)
            sd = math.sqrt(sum((x - mu) ** 2 for x in null_rs) / len(null_rs))
            z = (obs_r - mu) / (sd if sd > 0 else 1e-9)
            if abs(z) >= 1.8:
                significant_couplings.append({
                    "pigment_metric": pk,
                    "grammar_feature": fk,
                    "observed_r": round(obs_r, 4),
                    "stratified_null_r_mean": round(mu, 4),
                    "stratified_null_r_sd": round(sd, 4),
                    "stratified_z": round(z, 2),
                })

    significant_couplings.sort(key=lambda x: abs(x["stratified_z"]), reverse=True)

    # 3. Top Words Enriched on High-Blue, High-Red, High-Green, and High-Dark-Root Herbal Folios (Currier A controlled)
    herbal_a = [f for f in valid_folios if f["I"] == "H" and f["L"] == "A"]
    def top_pigment_words(flist, pk, top_q=0.25):
        s_fols = sorted(flist, key=lambda x: x["pigment"][pk], reverse=True)
        k = max(int(len(s_fols) * top_q), 1)
        hi_fols = s_fols[:k]
        lo_fols = s_fols[k:]
        c_hi = Counter(w for f in hi_fols for w in f["words"])
        c_lo = Counter(w for f in lo_fols for w in f["words"])
        t_hi = sum(c_hi.values())
        t_lo = sum(c_lo.values())
        scored = []
        for w in set(c_hi.keys()) | set(c_lo.keys()):
            if c_hi[w] + c_lo[w] >= 12 and c_hi[w] >= 5:
                r_hi = (c_hi[w] + 0.5) / (t_hi + 1.0)
                r_lo = (c_lo[w] + 0.5) / (t_lo + 1.0)
                scored.append({
                    "word": w,
                    "hi_count": c_hi[w],
                    "lo_count": c_lo[w],
                    "lift": round(r_hi / r_lo, 3),
                })
        scored.sort(key=lambda x: x["lift"], reverse=True)
        return {
            "top_folios": [f"{x['folio']}({x['pigment'][pk]:.2f}%)" for x in hi_fols[:8]],
            "top_words": scored[:10],
        }

    herbal_a_pigment_lexicon = {
        "HIGH_RED_CRIMSON": top_pigment_words(herbal_a, "red_pct"),
        "HIGH_BLUE_AZURE": top_pigment_words(herbal_a, "blue_pct"),
        "HIGH_GREEN_CANOPY": top_pigment_words(herbal_a, "green_pct"),
        "HIGH_DARK_ROOT": top_pigment_words(herbal_a, "dark_pct"),
    }

    print("=== ATTACK 79: FULL-MANUSCRIPT COMPUTER-VISION PIGMENT <-> GRAMMAR CONCORDANCE ===")
    print(f"Total Valid Folios Scanned from 2002046.pdf: {len(valid_folios)}")
    print("\nSection-Level Pigment & Spatial Profiles:")
    for sec, st in sec_pigment_summary.items():
        print(f"  $I={sec} (n={st['folios']:3d}): TotalPaint={st['mean_painted_total_pct']:5.2f}% | Green={st['mean_green_pct']:5.2f}% | Red={st['mean_red_pct']:4.2f}% | Blue={st['mean_blue_pct']:4.2f}% | Dark={st['mean_dark_pct']:4.2f}% | BotMinusTop={st['mean_bot_minus_top_pct']:+5.2f}%")

    print("\nTop ($I,$L)-Stratified Pigment <-> 10-Bit Feature Couplings (|z| >= 1.8):")
    for c in significant_couplings[:12]:
        print(f"  {c['pigment_metric']:18s} <-> {c['grammar_feature']:14s}: r = {c['observed_r']:+.4f} vs {c['stratified_null_r_mean']:+.4f} ± {c['stratified_null_r_sd']:.4f} null (z = {c['stratified_z']:+.2f})")

    print("\nHerbal-A ($I=H, $L=A) Pigment-Enriched Vocabulary:")
    for pk, info in herbal_a_pigment_lexicon.items():
        w_str = ", ".join(f"{w['word']}({w['lift']}x)" for w in info["top_words"][:6])
        print(f"  {pk:18s}: Folios={info['top_folios'][:4]} | Words: {w_str}")

    out = {
        "summary": {
            "folios_analyzed": len(valid_folios),
            "section_pigment_profiles": sec_pigment_summary,
        },
        "stratified_pigment_feature_couplings": significant_couplings,
        "herbal_a_pigment_lexicon": herbal_a_pigment_lexicon,
    }
    OUT_JSON.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"\nSaved -> {OUT_JSON}")


if __name__ == "__main__":
    main()
