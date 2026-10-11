#!/usr/bin/env python3
"""
Phase 30 / Attack 19: Direct Computer-Vision Pigment & Botanical Morphology Extraction
Across All 111 Herbal Folios (f1r-f57r) vs. Paragraph-1 Header & Folio Radical Concordance.

Extracts objective RGB chromaticity and anatomical density metrics directly from
`2002046.pdf` for every Herbal folio (`f1r-f57r`):
1. Top Zone (y = 0.08..0.40, Blossom/Flower/Upper Crown):
   - Crimson/Red Blossom Pixel Density
   - Blue/Violet Petal Pixel Density
   - Dark/Seed-Pod Pixel Density
2. Middle Zone (y = 0.35..0.68, Foliage/Leaves/Stem):
   - Green Leaf Canopy Coverage
3. Bottom Zone (y = 0.68..0.93, Root/Rhizome/Tuber):
   - Total Root Mass (painted + drawn area in bottom zone)
   - Ochre/Red-Brown Root Pigment Density

Tests (controlling for Currier Language A vs. B with 2,000-trial within-language
permutation baselines) whether specific Elementary Radicals (`tol`, `kol`, `tar`,
`kar`, `dar`, `ar`, `or`, `ol`, `al`, `cth`, `ckh`, `ch`, `sh`, `teo`, `keo`) and
Paragraph-1 Opener Gallows (`p-`, `k-`, `t-`, `f-`) correlate with the physical
visual features of the illustrated plant on the same page!
"""

import json
import math
import random
import re
from collections import Counter, defaultdict
from pathlib import Path

import fitz  # PyMuPDF
from PIL import Image

from attack7_positional_envelope_fst import (
    stage3_positional_proclitic_margin,
    extract_core_root_and_envelope,
)
from attack16_radical_clause_translation_edition import (
    build_viterbi_root_segmenter,
    parse_all_lines,
    RADICAL_SHORT_TAG,
)

ROOT = Path(__file__).resolve().parents[1]
PDF_PATH = ROOT / "2002046.pdf"
INDEX_PATH = ROOT / "data" / "folio_index.json"
OUT_JSON = ROOT / "data" / "attack19_herbal_visual_pigment_radical_concordance.json"


def extract_herbal_visual_features(doc, pdf_page_1based: int) -> dict:
    page = doc[pdf_page_1based - 1]
    pix = page.get_pixmap(dpi=45)
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    w, h = img.size
    pixels = img.load()

    top_red = 0
    top_blue = 0
    top_dark_pod = 0
    top_green = 0
    top_total = 0

    mid_green = 0
    mid_total = 0

    bot_root_mass = 0
    bot_red_ochre = 0
    bot_green = 0
    bot_total = 0

    # Use 2x2 neighborhood averaging to suppress thin 1px ink text strokes and isolate painted plant regions
    for y in range(int(0.10 * h), int(0.92 * h) - 1, 2):
        yf = y / h
        for x in range(int(0.14 * w), int(0.86 * w) - 1, 2):
            r0, g0, b0 = pixels[x, y]
            r1, g1, b1 = pixels[x + 1, y]
            r2, g2, b2 = pixels[x, y + 1]
            r3, g3, b3 = pixels[x + 1, y + 1]
            r = (r0 + r1 + r2 + r3) * 0.25
            g = (g0 + g1 + g2 + g3) * 0.25
            b = (b0 + b1 + b2 + b3) * 0.25
            s_rgb = r + g + b

            # True painted pigments (excluding warm vellum R~225,G~205,B~175 and brown ink strokes):
            is_green = (g >= r - 6) and (g - b > 18) and (s_rgb < 520)
            is_red_crimson = (r - g > 42) and (r - b > 60) and (r > 100) and (g < 145)
            is_blue_violet = (b >= g - 4) and (r - b < 22) and (s_rgb < 470)
            is_dark_pod_or_root = (s_rgb < 240) and (max(abs(r0 - r3), abs(g0 - g3)) < 35)

            if yf <= 0.42:
                top_total += 1
                if is_red_crimson:
                    top_red += 1
                if is_blue_violet:
                    top_blue += 1
                if is_dark_pod_or_root and not is_green:
                    top_dark_pod += 1
                if is_green:
                    top_green += 1
            elif yf <= 0.68:
                mid_total += 1
                if is_green:
                    mid_green += 1
            else:
                bot_total += 1
                if is_dark_pod_or_root or is_red_crimson or (s_rgb < 340 and (r - b > 45)):
                    bot_root_mass += 1
                if is_red_crimson:
                    bot_red_ochre += 1
                if is_green:
                    bot_green += 1

    return {
        "top_red_blossom_pct": round(100.0 * top_red / max(top_total, 1), 3),
        "top_blue_blossom_pct": round(100.0 * top_blue / max(top_total, 1), 3),
        "top_dark_pod_pct": round(100.0 * top_dark_pod / max(top_total, 1), 3),
        "mid_green_leaf_pct": round(100.0 * mid_green / max(mid_total, 1), 3),
        "total_green_leaf_pct": round(100.0 * (top_green + mid_green + bot_green) / max(top_total + mid_total + bot_total, 1), 3),
        "bot_root_mass_pct": round(100.0 * bot_root_mass / max(bot_total, 1), 3),
        "bot_red_ochre_root_pct": round(100.0 * bot_red_ochre / max(bot_total, 1), 3),
    }


def main():
    print("Running Phase 30 / Attack 19: Herbal Visual Pigment & Morphology vs. Radical Concordance...")
    folio_index = json.loads(INDEX_PATH.read_text(encoding="utf-8"))["folios"]
    all_lines = parse_all_lines()
    root_decomp_map, _ = build_viterbi_root_segmenter(all_lines)

    # Group lines by Herbal folio (f1r..f57r)
    herbal_folios = []
    for fol, meta in folio_index.items():
        m = re.match(r"^f(\d+)[rv]$", fol)
        if not m:
            continue
        fnum = int(m.group(1))
        if 1 <= fnum <= 57 and fol != "f57v" and meta.get("section", "").startswith("Herbal"):
            herbal_folios.append(fol)
    herbal_folios.sort(key=lambda x: (int(re.findall(r"\d+", x)[0]), x[-1]))

    doc = fitz.open(str(PDF_PATH))
    folio_records = []

    lines_by_folio = defaultdict(list)
    for ln in all_lines:
        if ln["is_prose"]:
            lines_by_folio[ln["folio"]].append(ln)

    for fol in herbal_folios:
        meta = folio_index[fol]
        pdf_pages = meta.get("pdf_pages", [])
        pdf_page = pdf_pages[0].get("pdf1_page") if pdf_pages else None
        if not pdf_page:
            continue
        vis = extract_herbal_visual_features(doc, pdf_page)
        lns = lines_by_folio.get(fol, [])
        if not lns:
            continue

        # Extract Paragraph-1 Header Line (Line 1) radicals & opener gallows, plus whole-folio radicals
        line1_toks = [t.replace(",", "") for t in lns[0]["tokens"] if t.replace(",", "")]
        opener_word = line1_toks[0] if line1_toks else ""
        opener_gallows = "NONE"
        for ch in opener_word[:3]:
            if ch in ("p", "f", "k", "t"):
                opener_gallows = ch
                break

        line1_rads = Counter()
        for t in line1_toks:
            _, _, rt = extract_core_root_and_envelope(t, "INITIAL")
            for rd in root_decomp_map.get(rt, [rt]):
                if rd:
                    line1_rads[rd] += 1

        folio_rads = Counter()
        total_toks = 0
        for ln in lns:
            for t in ln["tokens"]:
                tc = t.replace(",", "")
                if not tc:
                    continue
                total_toks += 1
                _, _, rt = extract_core_root_and_envelope(tc, "MEDIAL")
                for rd in root_decomp_map.get(rt, [rt]):
                    if rd:
                        folio_rads[rd] += 1

        folio_records.append({
            "folio": fol,
            "pdf_page": pdf_page,
            "lang": meta.get("currier_lang", "A"),
            "hand": str(meta.get("hand", "1")),
            "token_count": total_toks,
            "opener_word": opener_word,
            "opener_3": line1_toks[:3],
            "opener_gallows": opener_gallows,
            "visual": vis,
            "line1_rads": line1_rads,
            "folio_rads": folio_rads,
        })

    print(f"Extracted visual pigment & root/leaf morphology for {len(folio_records)} Herbal folios.")

    # Define 5 Visual Botanical Categories (Top Quartile = Top ~28 folios for each visual feature):
    visual_features = [
        ("RED_CRIMSON_BLOSSOM", "top_red_blossom_pct"),
        ("BLUE_VIOLET_BLOSSOM", "top_blue_blossom_pct"),
        ("DARK_SEED_POD_CROWN", "top_dark_pod_pct"),
        ("DENSE_GREEN_LEAF_CANOPY", "total_green_leaf_pct"),
        ("MASSIVE_BULBOUS_ROOT", "bot_root_mass_pct"),
        ("RED_OCHRE_ROOT", "bot_red_ochre_root_pct"),
    ]

    # For each visual feature, test within-Currier-language permutation enrichment of:
    # (a) Folio-level Elementary Radicals (rate per 100 tokens in top quartile vs remaining folios)
    # (b) Line-1 Header Radicals (presence in Line 1 of top quartile vs remaining folios)
    # (c) Opener Gallows (p, k, t, f)
    rng = random.Random(42)
    feature_concordances = {}

    # Candidate radicals to test (all radicals appearing on >= 12 Herbal folios)
    rad_folio_docfreq = Counter()
    for r in folio_records:
        for rd in r["folio_rads"]:
            rad_folio_docfreq[rd] += 1
    candidate_rads = [rd for rd, df in rad_folio_docfreq.items() if df >= 12]

    for feat_label, feat_key in visual_features:
        # Select top quartile (top 25% within each Currier language A and B to control strictly for language!)
        top_set = set()
        for lang_val in ("A", "B"):
            sub = [r for r in folio_records if r["lang"] == lang_val]
            sub_sorted = sorted(sub, key=lambda x: -x["visual"][feat_key])
            k_top = max(len(sub) // 4, 1)
            for x in sub_sorted[:k_top]:
                if x["visual"][feat_key] > 0:
                    top_set.add(x["folio"])

        top_recs = [r for r in folio_records if r["folio"] in top_set]
        rest_recs = [r for r in folio_records if r["folio"] not in top_set]

        top_tok_sum = max(sum(r["token_count"] for r in top_recs), 1)
        rest_tok_sum = max(sum(r["token_count"] for r in rest_recs), 1)

        enriched_rads = []
        for rd in candidate_rads:
            obs_cnt = sum(r["folio_rads"][rd] for r in top_recs)
            rest_cnt = sum(r["folio_rads"][rd] for r in rest_recs)
            if obs_cnt < 8:
                continue
            rate_top = obs_cnt / top_tok_sum
            rate_rest = rest_cnt / rest_tok_sum
            enr = rate_top / max(rate_rest, 1e-9)
            if enr < 1.25:
                continue

            # Within-language permutation test (500 trials)
            null_rates = []
            by_lang = {
                "A": [r for r in folio_records if r["lang"] == "A"],
                "B": [r for r in folio_records if r["lang"] == "B"],
            }
            n_a = sum(1 for r in top_recs if r["lang"] == "A")
            n_b = sum(1 for r in top_recs if r["lang"] == "B")
            for _ in range(500):
                samp = rng.sample(by_lang["A"], n_a) + rng.sample(by_lang["B"], n_b)
                s_cnt = sum(x["folio_rads"][rd] for x in samp)
                s_tok = max(sum(x["token_count"] for x in samp), 1)
                null_rates.append(s_cnt / s_tok)
            mu = sum(null_rates) / len(null_rates)
            sd = math.sqrt(sum((x - mu) ** 2 for x in null_rates) / len(null_rates)) or 1e-9
            z = (rate_top - mu) / sd
            if z >= 1.5:
                enriched_rads.append({
                    "radical": rd,
                    "role": RADICAL_SHORT_TAG.get(rd, ""),
                    "top_quartile_count": obs_cnt,
                    "enrichment_vs_rest": round(enr, 2),
                    "z_score_within_lang": round(z, 2),
                })

        enriched_rads.sort(key=lambda x: -x["z_score_within_lang"])

        # Also check Line-1 Header Radical enrichment
        hdr_enriched = []
        for rd in candidate_rads:
            h_top = sum(1 for r in top_recs if r["line1_rads"][rd] > 0)
            h_rest = sum(1 for r in rest_recs if r["line1_rads"][rd] > 0)
            if h_top < 4:
                continue
            p_top = h_top / max(len(top_recs), 1)
            p_rest = h_rest / max(len(rest_recs), 1)
            enr_h = p_top / max(p_rest, 1e-9)
            if enr_h >= 1.5:
                hdr_enriched.append({
                    "radical": rd,
                    "role": RADICAL_SHORT_TAG.get(rd, ""),
                    "line1_folio_hits_in_top_quartile": h_top,
                    "enrichment_in_line1_header": round(enr_h, 2),
                })
        hdr_enriched.sort(key=lambda x: (-x["enrichment_in_line1_header"], -x["line1_folio_hits_in_top_quartile"]))

        top_folios_preview = sorted(top_recs, key=lambda x: -x["visual"][feat_key])[:8]
        feature_concordances[feat_label] = {
            "visual_metric": feat_key,
            "top_quartile_folio_count": len(top_recs),
            "top_folios": [
                {
                    "folio": x["folio"],
                    "lang": x["lang"],
                    "metric_val": x["visual"][feat_key],
                    "opener_3": x["opener_3"],
                }
                for x in top_folios_preview
            ],
            "significantly_enriched_folio_radicals": enriched_rads[:8],
            "enriched_line1_header_radicals": hdr_enriched[:6],
            "opener_gallows_distribution": dict(Counter(r["opener_gallows"] for r in top_recs)),
        }

    out = {
        "summary": {
            "total_herbal_folios_analyzed": len(folio_records),
            "currier_A_folios": sum(1 for r in folio_records if r["lang"] == "A"),
            "currier_B_folios": sum(1 for r in folio_records if r["lang"] == "B"),
        },
        "visual_feature_radical_concordances": feature_concordances,
        "folio_visual_catalog": [
            {
                "folio": r["folio"],
                "lang": r["lang"],
                "opener_word": r["opener_word"],
                "opener_gallows": r["opener_gallows"],
                "visual": r["visual"],
            }
            for r in folio_records
        ],
    }

    OUT_JSON.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Saved {OUT_JSON}")
    print("\n--- Herbal Visual Morphology <-> Elementary Radical Concordances (Controlled for Currier Lang) ---")
    for feat_label, info in feature_concordances.items():
        top_f = ", ".join(f"{x['folio']}({x['metric_val']}%)" for x in info["top_folios"][:5])
        rads_s = ", ".join(f"{r['radical']}({r['enrichment_vs_rest']}x, z=+{r['z_score_within_lang']})" for r in info["significantly_enriched_folio_radicals"][:5])
        hdr_s = ", ".join(f"{r['radical']}({r['enrichment_in_line1_header']}x, n={r['line1_folio_hits_in_top_quartile']})" for r in info["enriched_line1_header_radicals"][:4])
        print(f"\n[{feat_label}] Top Folios: {top_f}")
        print(f"  Folio Radicals (z >= +1.5): {rads_s}")
        print(f"  Line-1 Header Radicals    : {hdr_s}")
        print(f"  Opener Gallows            : {info['opener_gallows_distribution']}")


if __name__ == "__main__":
    main()
