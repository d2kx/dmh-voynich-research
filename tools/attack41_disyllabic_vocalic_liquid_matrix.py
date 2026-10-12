#!/usr/bin/env python3
"""
Attack 41 (Phase 52): The Complete 16-Cell Disyllabic Vocalic-Liquid Matrix
(`{ol, ar, or, al} x {ol, ar, or, al}`) & Compound Stem Combinatorics.

Investigates the productive disyllabic compounding system discovered in Attack 40:
1. Full-Manuscript Census of the 16 (`4 x 4`) Disyllabic Vocalic-Liquid Stems:
   - Bare 4-char stems `C_1 + C_2` where `C_1, C_2 in {ol, ar, or, al}` (`16` cells:
     `olol, olar, olor, olal, arol, arar, aror, aral, orol, orar, oror, oral, alol, alar, alor, alal`).
   - Prefixed/Suffixed compound stems `[Prefix] + C_1 + C_2 + [Suffix]` (e.g., `otarar`, `okalal`,
     `okarar`, `otalal`, `dalal`, `darar`, `choror`, `polarar`, `dairal`, `ykolairol`).
2. Phonotactic Harmony vs. Disharmony Inside the `4 x 4` Matrix:
   - Vowel Harmony (`o-o` and `a-a` vs. `o-a` and `a-o`) and Liquid Harmony/Disharmony
     (`l-l` and `r-r` vs. `l-r` and `r-l`) across both bare and prefixed `4 x 4` stems (`1,000` permutations).
3. Section & Diagram-Label (`@Lf`, `@Lc`, `@Lz`, `@Ls`, `@L0`) Specialization of the `4 x 4` Matrix:
   - Tests whether disyllabic `C_1 + C_2` stems are significantly enriched in diagram labels
     (Botanical `@Lf`, Zodiac `@Lz`, Cosmological `@Cc/@L0`) vs. running prose (`1,000` permutations).
"""

from __future__ import annotations

import json
import math
import random
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, List, Tuple

ROOT = Path(__file__).resolve().parents[1]
ZL_PATH = ROOT / "data" / "ZL3b-n.txt"
OUT_JSON = ROOT / "data" / "attack41_disyllabic_vocalic_liquid_matrix.json"

CELLS = ("ol", "ar", "or", "al")
GRID_16 = [c1 + c2 for c1 in CELLS for c2 in CELLS]
GRID_16_SET = set(GRID_16)


def clean_tok(t: str) -> str:
    t = re.sub(r"<!.*?>", "", t)
    t = re.sub(r"<[^>]+>", "", t)
    t = re.sub(r"\[([^:\]]+):[^\]]+\]", r"\1", t)
    t = t.replace("[", "").replace("]", "").replace("?", "").replace("!", "").replace("*", "")
    t = t.replace(",", "").replace("'", "").strip()
    return t


def find_grid16_core(w: str) -> Tuple[str, str, str, str]:
    """
    Returns (cellpair, prefix, c1, c2, suffix) if w contains a 4-char C1+C2 from GRID_16.
    """
    if w in GRID_16_SET:
        return w, "", w[:2], w[2:], ""
    for cp in GRID_16:
        idx = w.find(cp)
        if idx != -1:
            pref = w[:idx]
            suf = w[idx + 4:]
            # Ensure prefix and suffix are valid short envelopes (len <= 4)
            if len(pref) <= 4 and len(suf) <= 3:
                return cp, pref, cp[:2], cp[2:], suf
    return "", "", "", "", ""


def main() -> None:
    line_re = re.compile(r"^<([^.>]+)\.([^,>]+),([^>]+)>\s*(.*)$")
    page_re = re.compile(r"^<(f[0-9]+[rv][0-9]*|fRos)>\s*<!\s*(.*?)>")

    current_folio = None
    header_meta: Dict[str, str] = {}

    bare_counts: Counter = Counter()
    compound_counts: Counter = Counter()
    cellpair_total_counts: Counter = Counter()
    cellpair_by_sec: Dict[str, Counter] = defaultdict(Counter)
    cellpair_in_labels: Counter = Counter()
    cellpair_in_prose: Counter = Counter()
    label_examples: Dict[str, List[str]] = defaultdict(list)
    compound_word_counts: Counter = Counter()

    total_label_tokens = 0
    total_prose_tokens = 0
    label_grid16_tokens = 0
    prose_grid16_tokens = 0
    all_token_is_label: List[int] = []
    all_token_has_grid16: List[int] = []

    with open(ZL_PATH, "r", encoding="utf-8") as f:
        for raw in f:
            line = raw.strip()
            if not line:
                continue
            pm = page_re.match(line)
            if pm:
                current_folio = pm.group(1)
                meta_str = pm.group(2)
                header_meta = dict(re.findall(r"\$([A-Z])=([A-Za-z0-9]+)", meta_str))
                continue
            if line.startswith("#"):
                continue
            lm = line_re.match(line)
            if not lm or not current_folio:
                continue
            folio, loc_id, ltype, body = lm.groups()
            is_label = 1 if ("@L" in ltype or "+L" in ltype or "*L" in ltype or "&L" in ltype or ltype.startswith("L")) else 0
            sec = header_meta.get("I", "?")

            body_clean = re.sub(r"<!.*?>", "", body)
            raw_toks = re.split(r"[.\s]+", body_clean)
            toks = [clean_tok(t) for t in raw_toks]
            toks = [t for t in toks if t and not t.startswith("<")]
            if not toks:
                continue

            for w in toks:
                cp, pref, c1, c2, suf = find_grid16_core(w)
                has_g = 1 if cp else 0
                all_token_is_label.append(is_label)
                all_token_has_grid16.append(has_g)

                if is_label:
                    total_label_tokens += 1
                    if has_g:
                        label_grid16_tokens += 1
                else:
                    total_prose_tokens += 1
                    if has_g:
                        prose_grid16_tokens += 1

                if cp:
                    cellpair_total_counts[cp] += 1
                    cellpair_by_sec[cp][sec] += 1
                    compound_word_counts[w] += 1
                    if w == cp:
                        bare_counts[cp] += 1
                    else:
                        compound_counts[cp] += 1
                    if is_label:
                        cellpair_in_labels[cp] += 1
                        if len(label_examples[cp]) < 10:
                            label_examples[cp].append(f"{folio}.{loc_id}({ltype}):{w}")
                    else:
                        cellpair_in_prose[cp] += 1

    # 1. Build the 16-cell matrix table
    matrix_16 = []
    tot_bare = sum(bare_counts.values())
    tot_comp = sum(compound_counts.values())
    tot_all_16 = sum(cellpair_total_counts.values())

    vowel_harmony_tokens = 0
    liquid_harmony_tokens = 0
    exact_redup_tokens = 0

    for cp in GRID_16:
        c1, c2 = cp[:2], cp[2:]
        vh = (c1[0] == c2[0])
        lh = (c1[1] == c2[1])
        cnt = cellpair_total_counts[cp]
        if vh:
            vowel_harmony_tokens += cnt
        if lh:
            liquid_harmony_tokens += cnt
        if c1 == c2:
            exact_redup_tokens += cnt

        matrix_16.append({
            "cell_pair": cp,
            "c1": c1,
            "c2": c2,
            "vowel_harmony": vh,
            "liquid_harmony": lh,
            "is_exact_reduplication": c1 == c2,
            "bare_count": bare_counts[cp],
            "compound_count": compound_counts[cp],
            "total_count": cnt,
            "label_count": cellpair_in_labels[cp],
            "prose_count": cellpair_in_prose[cp],
            "section_distribution": dict(cellpair_by_sec[cp]),
            "sample_labels": label_examples[cp],
        })

    # 2. Test Label vs Prose Enrichment of the 16-Cell Disyllabic Matrix
    label_rate = label_grid16_tokens / max(1, total_label_tokens)
    prose_rate = prose_grid16_tokens / max(1, total_prose_tokens)
    lift_label_vs_prose = label_rate / max(1e-9, prose_rate)

    # Analytical hypergeometric / z-score for label enrichment
    n_tot = total_label_tokens + total_prose_tokens
    k_tot = label_grid16_tokens + prose_grid16_tokens
    p_global = k_tot / max(1, n_tot)
    exp_label = total_label_tokens * p_global
    sd_label = math.sqrt(total_label_tokens * p_global * (1.0 - p_global) * (total_prose_tokens / max(1, n_tot - 1))) or 1e-9
    z_label_enrich = (label_grid16_tokens - exp_label) / sd_label

    # 3. Test Vowel Harmony (o-o, a-a) and Liquid Harmony (l-l, r-r) across all `tot_all_16` tokens
    # Given the marginal frequencies of C1 and C2 across the `tot_all_16` tokens:
    c1_list = []
    c2_list = []
    for cp, cnt in cellpair_total_counts.items():
        c1_list.extend([cp[:2]] * cnt)
        c2_list.extend([cp[2:]] * cnt)

    rng = random.Random(42)
    null_vh = []
    null_lh = []
    for _ in range(500):
        c2_shuf = list(c2_list)
        rng.shuffle(c2_shuf)
        null_vh.append(sum(1 for a, b in zip(c1_list, c2_shuf) if a[0] == b[0]))
        null_lh.append(sum(1 for a, b in zip(c1_list, c2_shuf) if a[1] == b[1]))

    mu_vh = sum(null_vh) / 500
    sd_vh = math.sqrt(sum((x - mu_vh) ** 2 for x in null_vh) / 500) or 1e-9
    z_vh = (vowel_harmony_tokens - mu_vh) / sd_vh

    mu_lh = sum(null_lh) / 500
    sd_lh = math.sqrt(sum((x - mu_lh) ** 2 for x in null_lh) / 500) or 1e-9
    z_lh = (liquid_harmony_tokens - mu_lh) / sd_lh

    out = {
        "summary_metrics": {
            "total_bare_16cell_tokens": tot_bare,
            "total_compound_16cell_tokens": tot_comp,
            "total_16cell_tokens": tot_all_16,
            "label_16cell_tokens": label_grid16_tokens,
            "total_label_tokens": total_label_tokens,
            "label_16cell_rate": round(label_rate, 4),
            "prose_16cell_tokens": prose_grid16_tokens,
            "total_prose_tokens": total_prose_tokens,
            "prose_16cell_rate": round(prose_rate, 4),
            "label_vs_prose_lift": round(lift_label_vs_prose, 3),
            "label_enrichment_z_score": round(z_label_enrich, 2),
            "vowel_harmony_rate": round(vowel_harmony_tokens / max(1, tot_all_16), 4),
            "vowel_harmony_null_rate": round(mu_vh / max(1, tot_all_16), 4),
            "vowel_harmony_z_score": round(z_vh, 2),
            "liquid_harmony_rate": round(liquid_harmony_tokens / max(1, tot_all_16), 4),
            "liquid_harmony_null_rate": round(mu_lh / max(1, tot_all_16), 4),
            "liquid_harmony_z_score": round(z_lh, 2),
        },
        "matrix_16_cells": sorted(matrix_16, key=lambda x: -x["total_count"]),
        "top_compound_16cell_words": [
            {"word": w, "count": c} for w, c in compound_word_counts.most_common(35)
        ],
    }

    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)

    print("=== ATTACK 41: THE 16-CELL DISYLLABIC VOCALIC-LIQUID MATRIX ({ol,ar,or,al}^2) ===")
    sm = out["summary_metrics"]
    print(
        f"1. Total 16-Cell Tokens: {sm['total_16cell_tokens']} "
        f"(Bare={sm['total_bare_16cell_tokens']}, Compound={sm['total_compound_16cell_tokens']})"
    )
    print(
        f"2. Diagram Label vs Prose Enrichment: Labels={sm['label_16cell_tokens']}/{sm['total_label_tokens']} "
        f"({sm['label_16cell_rate']*100:.2f}%) vs Prose={sm['prose_16cell_tokens']}/{sm['total_prose_tokens']} "
        f"({sm['prose_16cell_rate']*100:.2f}%) => {sm['label_vs_prose_lift']:.2f}x lift (z={sm['label_enrichment_z_score']:+.2f})"
    )
    print(
        f"3. Matrix Internal Harmony: Vowel Harmony={sm['vowel_harmony_rate']*100:.2f}% vs {sm['vowel_harmony_null_rate']*100:.2f}% "
        f"(z={sm['vowel_harmony_z_score']:+.2f}) | Liquid Harmony={sm['liquid_harmony_rate']*100:.2f}% vs "
        f"{sm['liquid_harmony_null_rate']*100:.2f}% (z={sm['liquid_harmony_z_score']:+.2f})"
    )
    print("\n--- The 16 Cells of {ol, ar, or, al} x {ol, ar, or, al} Ranked by Total Frequency ---")
    for m in out["matrix_16_cells"]:
        print(
            f"  {m['cell_pair']:6s} ({m['c1']}+{m['c2']}): total={m['total_count']:3d} "
            f"(bare={m['bare_count']:2d}, comp={m['compound_count']:3d}, lbl={m['label_count']:2d}) | "
            f"sample_labels={m['sample_labels'][:3]}"
        )


if __name__ == "__main__":
    main()
