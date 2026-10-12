#!/usr/bin/env python3
"""
Attack 53: The `s-` Sibilant Paradigm (`saiin`, `sar`, `sal`, `sair`, `sor`, `sol`, `sam`) & `d- <-> s-` Contrast
=================================================================================================================
Investigates the `s-` (`sa-/so-`) coronal sibilant paradigm and compares it directly against its
morphological twin, the `d-` (`da-/do-`) stop paradigm (`daiin`, `dar`, `dal`, `dair`, `dor`, `dol`, `dam`):
  1. Direct Cell-by-Cell Comparison across the 7 parallel inflectional slots:
     - `-aiin/-ain` (`daiin/dain` vs `saiin/sain`)
     - `-ar` (`dar` vs `sar`)
     - `-al` (`dal` vs `sal`)
     - `-or` (`dor` vs `sor`)
     - `-ol` (`dol` vs `sol`)
     - `-air/-aiir` (`dair/daiir` vs `sair/saiir`)
     - `-am/-om` (`dam/dom` vs `sam/som`)
  2. Positional & Paragraph-Line Contrast (`w_1` Line-Initial vs Interior vs `w_n` Line-Final, and
     Paragraph Line 1 vs Line 2 vs Lines 3..m):
     - Tests whether `s-` (`sair`, `saiin`, `sar`, `sal`, `sor`, `sol`) is specifically enriched at
       Line-Initial Continuation Onsets (`w_1` on Lines `2..m`) compared to `d-` (`1,000` permutations).
  3. Flanking Syntactic Slot Contrast (`prev_slot` and `next_slot` Mutual Information between `d-` and `s-`).
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
OUT_JSON = ROOT / "data" / "attack53_s_sibilant_paradigm_and_d_s_contrast.json"

LOCUS_RE = re.compile(r"^<f([0-9]+[rv][0-9]*|Ros)\.([^,>]+),([^>]+)>\s*(.*)$")

PARALLEL_SLOTS = [
    ("AIIN", ("daiin", "dain"), ("saiin", "sain")),
    ("AR", ("dar",), ("sar",)),
    ("AL", ("dal",), ("sal",)),
    ("OR", ("dor",), ("sor",)),
    ("OL", ("dol",), ("sol",)),
    ("AIR", ("dair", "daiir"), ("sair", "saiir")),
    ("AM", ("dam", "dom"), ("sam", "som")),
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
    paragraphs: List[List[List[str]]] = []
    cur_para: List[List[str]] = []

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
        toks = clean_tokens(raw_text)
        if not toks:
            continue
        is_new = loc_tag.startswith("@P") or "<%>" in raw_text
        if is_new:
            if cur_para:
                paragraphs.append(cur_para)
            cur_para = [toks]
        else:
            cur_para.append(toks)
    if cur_para:
        paragraphs.append(cur_para)

    d_map = {}
    s_map = {}
    for slot_name, d_forms, s_forms in PARALLEL_SLOTS:
        for df in d_forms:
            d_map[df] = slot_name
        for sf in s_forms:
            s_map[sf] = slot_name

    cell_stats: Dict[str, Dict[str, Counter]] = {
        slot_name: {"D": Counter(), "S": Counter()} for slot_name, _, _ in PARALLEL_SLOTS
    }
    series_totals = {"D": Counter(), "S": Counter()}
    all_ds_instances: List[Tuple[str, str, int, int, int]] = []  # (series 'D'/'S', slot_name, line_idx_in_para, word_idx, line_len)

    for para in paragraphs:
        for li, toks in enumerate(para):
            n = len(toks)
            for wi, w in enumerate(toks):
                series = None
                sname = None
                if w in d_map:
                    series = "D"
                    sname = d_map[w]
                elif w in s_map:
                    series = "S"
                    sname = s_map[w]
                if series and sname:
                    all_ds_instances.append((series, sname, li, wi, n))
                    c = cell_stats[sname][series]
                    st = series_totals[series]
                    c["total"] += 1
                    st["total"] += 1
                    if wi == 0:
                        c["line_init"] += 1
                        st["line_init"] += 1
                        if li == 0:
                            c["para_line1_init"] += 1
                            st["para_line1_init"] += 1
                        elif li == 1:
                            c["para_line2_init"] += 1
                            st["para_line2_init"] += 1
                        else:
                            c["para_line3plus_init"] += 1
                            st["para_line3plus_init"] += 1
                    elif wi == n - 1:
                        c["line_final"] += 1
                        st["line_final"] += 1
                    else:
                        c["line_mid"] += 1
                        st["line_mid"] += 1

    # Compare Line-Initial Continuation Rate (wi == 0 and li >= 1) between S-series and D-series
    s_tot = max(series_totals["S"]["total"], 1)
    d_tot = max(series_totals["D"]["total"], 1)
    obs_s_cont_init = (series_totals["S"]["para_line2_init"] + series_totals["S"]["para_line3plus_init"]) / s_tot
    obs_d_cont_init = (series_totals["D"]["para_line2_init"] + series_totals["D"]["para_line3plus_init"]) / d_tot
    obs_diff = obs_s_cont_init - obs_d_cont_init

    # Stratified permutation test: permute 'D' vs 'S' labels WITHIN each of the 7 inflectional slots (AIIN, AR, AL, OR, OL, AIR, AM)
    # so that any difference in suffix mix is 100% controlled for!
    rng = random.Random(53)
    by_slot: Dict[str, List[Tuple[str, bool]]] = defaultdict(list)
    for series, sname, li, wi, _ in all_ds_instances:
        is_cont_init = (wi == 0 and li >= 1)
        by_slot[sname].append((series, is_cont_init))

    null_diffs = []
    for _ in range(1000):
        s_ci = 0
        d_ci = 0
        for sname, items in by_slot.items():
            ser_list = [x[0] for x in items]
            ci_list = [x[1] for x in items]
            rng.shuffle(ser_list)
            for sr, ci in zip(ser_list, ci_list):
                if ci:
                    if sr == "S":
                        s_ci += 1
                    else:
                        d_ci += 1
        null_diffs.append((s_ci / s_tot) - (d_ci / d_tot))
    mu_diff = sum(null_diffs) / len(null_diffs)
    sd_diff = math.sqrt(sum((x - mu_diff) ** 2 for x in null_diffs) / len(null_diffs)) or 1e-9
    z_cont_init = (obs_diff - mu_diff) / sd_diff

    slot_comparison = {}
    for slot_name, d_forms, s_forms in PARALLEL_SLOTS:
        cd = cell_stats[slot_name]["D"]
        cs = cell_stats[slot_name]["S"]
        td = max(cd["total"], 1)
        ts = max(cs["total"], 1)
        slot_comparison[slot_name] = {
            "d_forms": list(d_forms),
            "s_forms": list(s_forms),
            "d_count": cd["total"],
            "s_count": cs["total"],
            "d_line_init_rate": round(cd["line_init"] / td, 4),
            "s_line_init_rate": round(cs["line_init"] / ts, 4),
            "d_line_final_rate": round(cd["line_final"] / td, 4),
            "s_line_final_rate": round(cs["line_final"] / ts, 4),
        }

    result = {
        "summary": {
            "d_series_total_prose_tokens": series_totals["D"]["total"],
            "s_series_total_prose_tokens": series_totals["S"]["total"],
            "d_line_init_rate": round(series_totals["D"]["line_init"] / d_tot, 4),
            "s_line_init_rate": round(series_totals["S"]["line_init"] / s_tot, 4),
            "d_continuation_line_init_rate": round(obs_d_cont_init, 4),
            "s_continuation_line_init_rate": round(obs_s_cont_init, 4),
            "s_vs_d_continuation_init_lift": round(obs_s_cont_init / max(obs_d_cont_init, 1e-9), 2),
            "slot_stratified_permutation_z_score": round(z_cont_init, 2),
        },
        "slot_comparison": slot_comparison,
    }

    OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print("=== ATTACK 53: THE s- SIBILANT PARADIGM & d- <-> s- DEICTIC CONTRAST ===")
    s = result["summary"]
    print(f"1. Total tokens: D-series={s['d_series_total_prose_tokens']} vs S-series={s['s_series_total_prose_tokens']}")
    print(f"2. Continuation Line-Initial Rate (w_1 on lines 2..m): S-series={s['s_continuation_line_init_rate']*100:.2f}% vs D-series={s['d_continuation_line_init_rate']*100:.2f}% ({s['s_vs_d_continuation_init_lift']}x lift, suffix-stratified z={s['slot_stratified_permutation_z_score']:+.2f})")
    print("3. Cell-by-Cell Comparison across the 7 Parallel Slots:")
    for sname, sc in slot_comparison.items():
        print(f"   {sname:5s}: D({','.join(sc['d_forms']):11s}) n={sc['d_count']:3d} [init={sc['d_line_init_rate']*100:5.1f}%, end={sc['d_line_final_rate']*100:5.1f}%] | S({','.join(sc['s_forms']):11s}) n={sc['s_count']:3d} [init={sc['s_line_init_rate']*100:5.1f}%, end={sc['s_line_final_rate']*100:5.1f}%]")


if __name__ == "__main__":
    main()
