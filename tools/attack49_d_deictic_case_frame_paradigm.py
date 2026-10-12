#!/usr/bin/env python3
"""
Attack 49: The Five-Way `da-` Deictic & Prepositional Case-Frame Paradigm (`daiin`, `dar`, `dal`, `dair`, `dam`)
=================================================================================================================
Investigates the 5 primary inflections of the `da-` stem (`daiin`, `dar`, `dal`, `dair`, `dam`, plus `dain`/`daly`),
which together account for >1,700 tokens (~5% of all prose in the Voynich Manuscript):
  1. Positional Stratification across Line Initial (`w_1`), Line Interior (`w_2..w_{n-1}`), Line Final (`w_n`),
     and Paragraph Final (`<$>`).
  2. Preceding (`w_{i-1}`) and Following (`w_{i+1}`) Syntactic Slot Selection (`LIQ_NOM`, `CH_VERB`, `Q_ACT`,
     `NOM_OK`, `GALLOWS`, `AIIN`), proving that each of the 5 `da-` endings governs a distinct syntactic frame.
  3. 1,000-trial permutation test shuffling `{daiin, dar, dal, dair, dam}` labels across their attested occurrences
     to measure the exact mutual information $I(\text{da-form} ; \text{Context Frame})$ and z-score.
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
OUT_JSON = ROOT / "data" / "attack49_d_deictic_case_frame_paradigm.json"

LOCUS_RE = re.compile(r"^<f([0-9]+[rv][0-9]*|Ros)\.([^,>]+),([^>]+)>\s*(.*)$")
TARGET_DA = ("daiin", "dar", "dal", "dair", "dam")


def clean_tokens(raw: str) -> List[str]:
    s = re.sub(r"\{[^}]*\}", "", raw)
    s = re.sub(r"\[([^:\]]+):[^\]]+\]", r"\1", s)
    s = s.replace("<%>", " ").replace("<$>", " ").replace("<->", " ")
    s = re.sub(r"<[^>]*>", " ", s)
    s = re.sub(r"@[0-9]+;", "", s)
    s = re.sub(r"[^a-zA-Z.\s]", "", s).lower()
    return [t for t in s.replace(".", " ").split() if t]


def slot_class(w: str) -> str:
    if w == "<BOS>":
        return "LINE_START"
    if w == "<EOS>":
        return "LINE_END"
    if w.startswith(("qok", "qot", "qo")):
        return "Q_ACT"
    if w.startswith(("ch", "sh")):
        if w.endswith(("ol", "or", "al", "ar")):
            return "CH_LIQ_NOM"
        return "CH_VERB"
    if w.startswith(("ok", "ot", "yk", "yt")):
        return "NOM_OK"
    if w[0:1] in ("p", "f", "k", "t"):
        return "GALLOWS"
    if w.endswith(("aiin", "ain")):
        return "AIIN"
    if w.endswith(("ol", "or", "al", "ar")):
        return "LIQ_NOM"
    return "OTHER"


def calc_mi(pairs: List[Tuple[str, str]]) -> float:
    n = len(pairs)
    if n == 0:
        return 0.0
    cx = Counter(x for x, _ in pairs)
    cy = Counter(y for _, y in pairs)
    cxy = Counter(pairs)
    mi = 0.0
    for (x, y), c in cxy.items():
        p_xy = c / n
        p_x = cx[x] / n
        p_y = cy[y] / n
        mi += p_xy * math.log2(p_xy / (p_x * p_y))
    return mi


def main() -> None:
    lines_raw = ZL_PATH.read_text(encoding="utf-8", errors="replace").splitlines()
    prose_lines: List[Tuple[List[str], bool]] = []

    for line in lines_raw:
        line = line.strip()
        if not line or line.startswith("#") or "." not in line.split(">")[0]:
            continue
        m = LOCUS_RE.match(line)
        if not m:
            continue
        loc_tag = m.group(3)
        raw_text = m.group(4)
        if "P" not in loc_tag:
            continue
        is_para_end = "<$>" in raw_text
        toks = clean_tokens(raw_text)
        if toks:
            prose_lines.append((toks, is_para_end))

    pos_stats: Dict[str, Counter] = {w: Counter() for w in TARGET_DA}
    prev_slot_counts: Dict[str, Counter] = {w: Counter() for w in TARGET_DA}
    next_slot_counts: Dict[str, Counter] = {w: Counter() for w in TARGET_DA}
    top_prev_words: Dict[str, Counter] = {w: Counter() for w in TARGET_DA}
    top_next_words: Dict[str, Counter] = {w: Counter() for w in TARGET_DA}

    da_frame_instances: List[Tuple[str, str]] = []  # (da_word, composite_frame)

    for toks, is_para_end in prose_lines:
        n = len(toks)
        for i, w in enumerate(toks):
            if w not in TARGET_DA:
                continue
            pos_stats[w]["total"] += 1
            if i == 0:
                pos_stats[w]["line_initial"] += 1
            elif i == n - 1:
                pos_stats[w]["line_final"] += 1
            else:
                pos_stats[w]["line_interior"] += 1
            if i == n - 1 and is_para_end:
                pos_stats[w]["para_final"] += 1

            prev_w = toks[i - 1] if i > 0 else "<BOS>"
            next_w = toks[i + 1] if i < n - 1 else "<EOS>"
            ps = slot_class(prev_w)
            ns = slot_class(next_w)

            prev_slot_counts[w][ps] += 1
            next_slot_counts[w][ns] += 1
            if prev_w != "<BOS>":
                top_prev_words[w][prev_w] += 1
            if next_w != "<EOS>":
                top_next_words[w][next_w] += 1

            da_frame_instances.append((w, f"{ps}__{ns}"))

    # Compute MI between the 5 da- forms and their (prev_slot, next_slot) syntactic frame
    obs_mi = calc_mi(da_frame_instances)
    rng = random.Random(49)
    da_labels = [x for x, _ in da_frame_instances]
    frames = [f for _, f in da_frame_instances]
    null_mis = []
    for _ in range(1000):
        shuffled_da = da_labels[:]
        rng.shuffle(shuffled_da)
        null_mis.append(calc_mi(list(zip(shuffled_da, frames))))
    mu_mi = sum(null_mis) / len(null_mis)
    sd_mi = math.sqrt(sum((x - mu_mi) ** 2 for x in null_mis) / len(null_mis)) or 1e-9
    z_mi = (obs_mi - mu_mi) / sd_mi

    paradigm_table = {}
    for w in TARGET_DA:
        tot = max(pos_stats[w]["total"], 1)
        paradigm_table[w] = {
            "total_prose_tokens": pos_stats[w]["total"],
            "line_initial_rate": round(pos_stats[w]["line_initial"] / tot, 4),
            "line_interior_rate": round(pos_stats[w]["line_interior"] / tot, 4),
            "line_final_rate": round(pos_stats[w]["line_final"] / tot, 4),
            "para_final_rate": round(pos_stats[w]["para_final"] / tot, 4),
            "prev_slot_rates": {k: round(v / tot, 4) for k, v in prev_slot_counts[w].most_common()},
            "next_slot_rates": {k: round(v / tot, 4) for k, v in next_slot_counts[w].most_common()},
            "top_prev_words": dict(top_prev_words[w].most_common(8)),
            "top_next_words": dict(top_next_words[w].most_common(8)),
        }

    result = {
        "summary": {
            "total_da_paradigm_tokens": len(da_frame_instances),
            "observed_frame_mi_bits": round(obs_mi, 5),
            "null_mean_mi_bits": round(mu_mi, 5),
            "null_sd_mi_bits": round(sd_mi, 5),
            "z_score": round(z_mi, 2),
        },
        "paradigm_table": paradigm_table,
    }

    OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print("=== ATTACK 49: FIVE-WAY da- DEICTIC & PREPOSITIONAL CASE-FRAME PARADIGM ===")
    s = result["summary"]
    print(f"Total tokens={s['total_da_paradigm_tokens']} | Frame MI={s['observed_frame_mi_bits']:.5f} bits vs null={s['null_mean_mi_bits']:.5f} (z={s['z_score']:+.2f})")
    for w in TARGET_DA:
        pt = paradigm_table[w]
        prev_top = ", ".join(f"{k}:{v}" for k, v in list(pt["top_prev_words"].items())[:4])
        next_top = ", ".join(f"{k}:{v}" for k, v in list(pt["top_next_words"].items())[:4])
        print(f"  {w:6s} (n={pt['total_prose_tokens']:3d}): init={pt['line_initial_rate']*100:5.1f}% | mid={pt['line_interior_rate']*100:5.1f}% | end={pt['line_final_rate']*100:5.1f}% (para_end={pt['para_final_rate']*100:4.1f}%)")
        print(f"         prev=[{prev_top}] | next=[{next_top}]")


if __name__ == "__main__":
    main()
