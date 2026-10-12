#!/usr/bin/env python3
"""
Attack 54: The `r-` vs `l-` Liquid Onset System (`raiin`, `ram`, `ral`, `rar`, `rchedy` vs `laiin`, `lam`, `lal`, `lar`, `lchedy`)
===================================================================================================================================
Investigates the `r-` liquid onset paradigm (`raiin`, `ram`, `ral`, `rar`, `rol`, `ror`, `rchedy`, `rshedy`, `rody`, etc.)
and compares it directly against the `l-` liquid onset paradigm:
  1. Cell-by-Cell Comparison across Nominal/Quantitative (`-aiin/-ain`, `-am/-om`, `-al`, `-ar`, `-ol`, `-or`, `-ody/-dy`)
     and Verbal Applicative (`-chedy/-shedy/-chey/-shey/-kedy/-keedy`) slots.
  2. Positional Contrast (`w_1` Line-Initial vs Interior vs `w_n` Line-Final):
     - Tests whether `r-` is enriched at Right-Margin Line-Final (`w_n`) positions compared to `l-`
       using 1,000 slot-stratified permutations.
  3. Cross-Word Sandhi / Liaison Test (`w_{i-1}` ending before `r-` vs `l-`):
     - Tests what precedes `r-` vs `l-` in continuous prose (`cheo/sheo`, `-r`, `-l`, `-aiin`, `-dy`).
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
OUT_JSON = ROOT / "data" / "attack54_r_liquid_onset_and_coda_system.json"

LOCUS_RE = re.compile(r"^<f([0-9]+[rv][0-9]*|Ros)\.([^,>]+),([^>]+)>\s*(.*)$")

RL_SLOTS = [
    ("AIIN", ("raiin", "rain"), ("laiin", "lain")),
    ("AM", ("ram", "rom"), ("lam", "lom")),
    ("AL", ("ral",), ("lal",)),
    ("AR", ("rar",), ("lar",)),
    ("OL", ("rol",), ("lol",)),
    ("OR", ("ror",), ("lor",)),
    ("ODY", ("rody", "rdy", "ry"), ("lody", "ldy", "ly")),
    ("CH_VERB", ("rchedy", "rshedy", "rchey", "rshey"), ("lchedy", "lshedy", "lchey", "lshey")),
    ("K_VERB", ("rkedy", "rkeedy", "rkeey", "rkaiin"), ("lkedy", "lkeedy", "lkeey", "lkaiin")),
]


def clean_tokens(raw: str) -> List[str]:
    s = re.sub(r"\{[^}]*\}", "", raw)
    s = re.sub(r"\[([^:\]]+):[^\]]+\]", r"\1", s)
    s = s.replace("<%>", " ").replace("<$>", " ").replace("<->", " ")
    s = re.sub(r"<[^>]*>", " ", s)
    s = re.sub(r"@[0-9]+;", "", s)
    s = re.sub(r"[^a-zA-Z.\s]", "", s).lower()
    return [t for t in s.replace(".", " ").split() if t]


def main() -> None:
    lines_raw = ZL_PATH.read_text(encoding="utf-8", errors="replace").splitlines()
    prose_lines: List[List[str]] = []

    for line in lines_raw:
        line = line.strip()
        if not line or line.startswith("#") or "." not in line.split(">")[0]:
            continue
        m = LOCUS_RE.match(line)
        if not m:
            continue
        loc_tag = m.group(3)
        if "P" not in loc_tag:
            continue
        toks = clean_tokens(m.group(4))
        if toks:
            prose_lines.append(toks)

    r_map = {}
    l_map = {}
    for sname, r_forms, l_forms in RL_SLOTS:
        for rf in r_forms:
            r_map[rf] = sname
        for lf in l_forms:
            l_map[lf] = sname

    cell_stats: Dict[str, Dict[str, Counter]] = {
        sname: {"R": Counter(), "L": Counter()} for sname, _, _ in RL_SLOTS
    }
    series_totals = {"R": Counter(), "L": Counter()}
    prev_word_counts = {"R": Counter(), "L": Counter()}
    prev_ending_counts = {"R": Counter(), "L": Counter()}
    all_rl_instances: List[Tuple[str, str, bool]] = []  # (series 'R'/'L', sname, is_line_final)

    for toks in prose_lines:
        n = len(toks)
        for i, w in enumerate(toks):
            ser = None
            sname = None
            if w in r_map:
                ser = "R"
                sname = r_map[w]
            elif w in l_map:
                ser = "L"
                sname = l_map[w]
            elif len(w) >= 2 and w[0] in ("r", "l"):
                ser = w[0].upper()
                sname = "OTHER_RL"

            if ser in ("R", "L"):
                if i > 0:
                    pw = toks[i - 1]
                    prev_word_counts[ser][pw] += 1
                    if pw.endswith(("o", "eo", "cheo", "sheo")):
                        prev_ending_counts[ser]["ends_in_o (cheo/sheo/o)"] += 1
                    elif pw.endswith(("r", "ar", "or")):
                        prev_ending_counts[ser]["ends_in_r"] += 1
                    elif pw.endswith(("l", "al", "ol")):
                        prev_ending_counts[ser]["ends_in_l"] += 1
                    elif pw.endswith(("y", "dy", "edy", "ey")):
                        prev_ending_counts[ser]["ends_in_y_dy"] += 1
                    elif pw.endswith(("in", "iin", "aiin")):
                        prev_ending_counts[ser]["ends_in_in"] += 1
                    else:
                        prev_ending_counts[ser]["other"] += 1

                if sname != "OTHER_RL":
                    is_fin = (i == n - 1)
                    is_init = (i == 0)
                    all_rl_instances.append((ser, sname, is_fin))
                    c = cell_stats[sname][ser]
                    st = series_totals[ser]
                    c["total"] += 1
                    st["total"] += 1
                    if is_init:
                        c["init"] += 1
                        st["init"] += 1
                    elif is_fin:
                        c["final"] += 1
                        st["final"] += 1
                    else:
                        c["mid"] += 1
                        st["mid"] += 1

    r_tot = max(series_totals["R"]["total"], 1)
    l_tot = max(series_totals["L"]["total"], 1)
    obs_r_fin = series_totals["R"]["final"] / r_tot
    obs_l_fin = series_totals["L"]["final"] / l_tot
    obs_diff = obs_r_fin - obs_l_fin

    # Slot-stratified permutation test (1,000 trials)
    rng = random.Random(54)
    by_slot: Dict[str, List[Tuple[str, bool]]] = defaultdict(list)
    for ser, sname, is_fin in all_rl_instances:
        by_slot[sname].append((ser, is_fin))

    null_diffs = []
    for _ in range(1000):
        rf = 0
        lf = 0
        for sname, items in by_slot.items():
            s_list = [x[0] for x in items]
            f_list = [x[1] for x in items]
            rng.shuffle(s_list)
            for sr, fn in zip(s_list, f_list):
                if fn:
                    if sr == "R":
                        rf += 1
                    else:
                        lf += 1
        null_diffs.append((rf / r_tot) - (lf / l_tot))
    mu_d = sum(null_diffs) / len(null_diffs)
    sd_d = math.sqrt(sum((x - mu_d) ** 2 for x in null_diffs) / len(null_diffs)) or 1e-9
    z_fin = (obs_diff - mu_d) / sd_d

    slot_comparison = {}
    for sname, r_forms, l_forms in RL_SLOTS:
        cr = cell_stats[sname]["R"]
        cl = cell_stats[sname]["L"]
        tr = max(cr["total"], 1)
        tl = max(cl["total"], 1)
        slot_comparison[sname] = {
            "r_forms": list(r_forms),
            "l_forms": list(l_forms),
            "r_count": cr["total"],
            "l_count": cl["total"],
            "r_init_rate": round(cr["init"] / tr, 4),
            "l_init_rate": round(cl["init"] / tl, 4),
            "r_final_rate": round(cr["final"] / tr, 4),
            "l_final_rate": round(cl["final"] / tl, 4),
        }

    r_prev_tot = max(sum(prev_ending_counts["R"].values()), 1)
    l_prev_tot = max(sum(prev_ending_counts["L"].values()), 1)

    result = {
        "summary": {
            "r_series_tokens_in_9slots": series_totals["R"]["total"],
            "l_series_tokens_in_9slots": series_totals["L"]["total"],
            "r_line_final_rate": round(obs_r_fin, 4),
            "l_line_final_rate": round(obs_l_fin, 4),
            "r_vs_l_line_final_lift": round(obs_r_fin / max(obs_l_fin, 1e-9), 2),
            "slot_stratified_line_final_z_score": round(z_fin, 2),
            "r_preceded_by_o_rate": round(prev_ending_counts["R"]["ends_in_o (cheo/sheo/o)"] / r_prev_tot, 4),
            "l_preceded_by_o_rate": round(prev_ending_counts["L"]["ends_in_o (cheo/sheo/o)"] / l_prev_tot, 4),
        },
        "slot_comparison": slot_comparison,
        "prev_ending_rates": {
            "R": {k: round(v / r_prev_tot, 4) for k, v in prev_ending_counts["R"].most_common()},
            "L": {k: round(v / l_prev_tot, 4) for k, v in prev_ending_counts["L"].most_common()},
        },
        "top_prev_words_before_R": dict(prev_word_counts["R"].most_common(12)),
        "top_prev_words_before_L": dict(prev_word_counts["L"].most_common(12)),
    }

    OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print("=== ATTACK 54: THE r- vs l- LIQUID ONSET & SANDHI SYSTEM ===")
    s = result["summary"]
    print(f"1. Line-Final Rate: R-series={s['r_line_final_rate']*100:.2f}% (n={s['r_series_tokens_in_9slots']}) vs L-series={s['l_line_final_rate']*100:.2f}% (n={s['l_series_tokens_in_9slots']}) -> {s['r_vs_l_line_final_lift']}x lift (slot-stratified z={s['slot_stratified_line_final_z_score']:+.2f})")
    print(f"2. Preceded by -o (cheo/sheo/o): R-series={s['r_preceded_by_o_rate']*100:.2f}% vs L-series={s['l_preceded_by_o_rate']*100:.2f}%")
    print(f"   Top words before R: {result['top_prev_words_before_R']}")
    print(f"   Top words before L: {result['top_prev_words_before_L']}")
    print("3. Cell-by-Cell Comparison across the 9 Parallel Slots:")
    for sname, sc in slot_comparison.items():
        print(f"   {sname:8s}: R n={sc['r_count']:3d} [init={sc['r_init_rate']*100:5.1f}%, end={sc['r_final_rate']*100:5.1f}%] | L n={sc['l_count']:3d} [init={sc['l_init_rate']*100:5.1f}%, end={sc['l_final_rate']*100:5.1f}%]")


if __name__ == "__main__":
    main()
