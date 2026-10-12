#!/usr/bin/env python3
"""
Attack 38 (Phase 49): Full-Manuscript Vertical Line-Initial (`w_1`) Acrostic Scanner
& Cross-Line Enjambment (`w_n[i] -> w_1[i+1]`) Continuity Test.

Strictly controls for paragraph boundaries (`<%>`, `<$>`, and `@P` locus headers) so that
paragraph-initial top-line gallows (`G-`) cannot confound intra-paragraph vertical transitions:
1. Intra-Paragraph Vertical Line-Initial (`w_1[i] -> w_1[i+1]`) Test on Non-Header Lines (`2..m`):
   - Splits paragraphs on `<%>`, `<$>`, or `@P` and tests only strictly interior/continuation
     adjacent line pairs `(line_i, line_{i+1})` where `i >= 2` (neither line is a paragraph opener).
   - Permutes lines `2..m` within each paragraph (`1,000` trials) to test whether consecutive
     continuation lines repel identical onset prefixes (`qo-`, `ch-`, `sh-`, `o-`, `d-`, `s-`, `y-`).
2. Folio-Level & Paragraph-Level Vertical Acrostic Detector (Strictly Inside Single Paragraphs & Whole Folios):
   - Identifies single continuous paragraphs (`m >= 7` continuation lines, zero internal paragraph breaks)
     and whole folios that exhibit extreme adjacent onset repulsion or Period-2 / Period-3 vertical
     acrostic cycles (such as `f49v` Paragraph 1 `13` lines and Paragraph 3 `9` lines `qo- -> ch- -> o-`,
     `f83v`, `f78v`, `f36v`, `f80r`).
3. Cross-Line Enjambment vs. Line-Record Independence (`w_n[i] -> w_1[i+1]`):
   - Tests Currier's line-as-functional-record law by computing `I(Class(w_n[i]) ; Class(w_1[i+1]))`
     across strictly interior line breaks (`2 <= i < m-1`) against 1,000 within-paragraph line shuffles.
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
OUT_JSON = ROOT / "data" / "attack38_vertical_line_initial_acrostic_scanner.json"


def clean_tok(t: str) -> str:
    t = re.sub(r"<!.*?>", "", t)
    t = re.sub(r"<[^>]+>", "", t)
    t = re.sub(r"\[([^:\]]+):[^\]]+\]", r"\1", t)
    t = t.replace("[", "").replace("]", "").replace("?", "").replace("!", "").replace("*", "")
    t = t.replace(",", "").replace("'", "").strip()
    return t


def onset_class(w: str) -> str:
    if w.startswith("qo"):
        return "qo-"
    if w.startswith("ch"):
        return "ch-"
    if w.startswith("sh"):
        return "sh-"
    if w.startswith("o"):
        return "o-"
    if w.startswith("d"):
        return "d-"
    if w.startswith("s"):
        return "s-"
    if w.startswith("y"):
        return "y-"
    if w.startswith(("k", "t", "p", "f", "ck", "ct", "cp", "cf")):
        return "G-"
    return "OTHER"


def end_class(w: str) -> str:
    if w in ("daiin", "dain", "daiiin"):
        return "DAIIN"
    if w.endswith(("am", "om", "aim", "oim", "an")):
        return "AM_CLOSER"
    if w.endswith(("edy", "dy")):
        return "EDY_VERB"
    if re.search(r"i+n$", w):
        return "AIIN_QUANT"
    if w.endswith(("ol", "or", "ar", "al")):
        return "LIQ_INGR"
    if w.endswith("y"):
        return "Y_STATE"
    return "OTHER_END"


def parse_paragraphs() -> Tuple[List[Dict], Dict[str, List[Dict]]]:
    paragraphs: List[Dict] = []
    folio_lines: Dict[str, List[Dict]] = defaultdict(list)

    current_folio = None
    header_meta: Dict[str, str] = {}
    curr_para: List[Dict] = []
    para_idx_on_folio = 0

    line_re = re.compile(r"^<([^.>]+)\.([^,>]+),([^>]+)>\s*(.*)$")
    page_re = re.compile(r"^<(f[0-9]+[rv][0-9]*|fRos)>\s*<!\s*(.*?)>")

    with open(ZL_PATH, "r", encoding="utf-8") as f:
        for raw in f:
            line = raw.strip()
            if not line:
                continue
            pm = page_re.match(line)
            if pm:
                if curr_para and current_folio:
                    para_idx_on_folio += 1
                    paragraphs.append({
                        "folio": current_folio,
                        "para_id": f"{current_folio}:P{para_idx_on_folio}",
                        "section": header_meta.get("I", "?"),
                        "language": header_meta.get("L", "?"),
                        "hand": header_meta.get("H", "?"),
                        "lines": curr_para,
                    })
                    curr_para = []
                current_folio = pm.group(1)
                para_idx_on_folio = 0
                meta_str = pm.group(2)
                header_meta = dict(re.findall(r"\$([A-Z])=([A-Za-z0-9]+)", meta_str))
                continue
            if line.startswith("#"):
                continue
            lm = line_re.match(line)
            if not lm or not current_folio:
                continue
            _, loc_id, ltype, body = lm.groups()
            if "@L" in ltype or "+L" in ltype or "*L" in ltype or ltype.startswith("L") or "Cc" in ltype or "Ro" in ltype:
                continue
            body_clean = re.sub(r"<!.*?>", "", body)
            raw_toks = re.split(r"[.\s]+", body_clean)
            toks = [clean_tok(t) for t in raw_toks]
            toks = [t for t in toks if t and not t.startswith("<")]
            if not toks:
                continue

            is_new_para = ("<%>" in body) or ltype.startswith("@P") or ("=Pt" in ltype)
            if is_new_para and curr_para:
                para_idx_on_folio += 1
                paragraphs.append({
                    "folio": current_folio,
                    "para_id": f"{current_folio}:P{para_idx_on_folio}",
                    "section": header_meta.get("I", "?"),
                    "language": header_meta.get("L", "?"),
                    "hand": header_meta.get("H", "?"),
                    "lines": curr_para,
                })
                curr_para = []

            rec = {
                "folio": current_folio,
                "loc_id": loc_id,
                "ltype": ltype,
                "w1": toks[0],
                "wn": toks[-1],
                "w1_onset": onset_class(toks[0]),
                "wn_end": end_class(toks[-1]),
                "n_tokens": len(toks),
                "has_para_start": is_new_para,
                "has_para_end": "<$>" in body,
            }
            curr_para.append(rec)
            folio_lines[current_folio].append(rec)

            if "<$>" in body and curr_para:
                para_idx_on_folio += 1
                paragraphs.append({
                    "folio": current_folio,
                    "para_id": f"{current_folio}:P{para_idx_on_folio}",
                    "section": header_meta.get("I", "?"),
                    "language": header_meta.get("L", "?"),
                    "hand": header_meta.get("H", "?"),
                    "lines": curr_para,
                })
                curr_para = []

    if curr_para and current_folio:
        para_idx_on_folio += 1
        paragraphs.append({
            "folio": current_folio,
            "para_id": f"{current_folio}:P{para_idx_on_folio}",
            "section": header_meta.get("I", "?"),
            "language": header_meta.get("L", "?"),
            "hand": header_meta.get("H", "?"),
            "lines": curr_para,
        })

    return paragraphs, folio_lines


def compute_pair_mi(pairs: List[Tuple[str, str]]) -> float:
    n = len(pairs)
    if n == 0:
        return 0.0
    ab = Counter(pairs)
    a_cnt = Counter(x[0] for x in pairs)
    b_cnt = Counter(x[1] for x in pairs)
    mi = 0.0
    for (a, b), c in ab.items():
        p_ab = c / n
        p_a = a_cnt[a] / n
        p_b = b_cnt[b] / n
        if p_ab > 0 and p_a > 0 and p_b > 0:
            mi += p_ab * math.log2(p_ab / (p_a * p_b))
    return mi


def main() -> None:
    paragraphs, folio_lines = parse_paragraphs()

    # 1. Strictly Continuation-Only Lines (lines 2..m within single paragraphs, zero paragraph breaks!)
    body_paras = [p for p in paragraphs if len(p["lines"]) >= 4]
    obs_vertical_same = 0
    total_vertical_pairs = 0
    obs_vert_pairs: List[Tuple[str, str]] = []
    obs_enjamb_pairs: List[Tuple[str, str]] = []

    for p in body_paras:
        sub = p["lines"][1:]  # strictly continuation lines 2..m inside a single paragraph
        for i in range(len(sub) - 1):
            a = sub[i]["w1_onset"]
            b = sub[i + 1]["w1_onset"]
            if a == b:
                obs_vertical_same += 1
            total_vertical_pairs += 1
            obs_vert_pairs.append((a, b))
        if len(p["lines"]) >= 5:
            mid = p["lines"][1:-1]  # strictly interior lines 2..m-1
            for i in range(len(mid) - 1):
                obs_enjamb_pairs.append((mid[i]["wn_end"], mid[i + 1]["w1_onset"]))

    obs_vert_mi = compute_pair_mi(obs_vert_pairs)
    obs_enjamb_mi = compute_pair_mi(obs_enjamb_pairs)

    rng = random.Random(42)
    n_trials = 500
    null_vert_same = []
    null_vert_mi = []
    null_enjamb_mi = []

    for _ in range(n_trials):
        t_same = 0
        t_vert_pairs = []
        t_enj_pairs = []
        for p in body_paras:
            sub = list(p["lines"][1:])
            rng.shuffle(sub)
            for i in range(len(sub) - 1):
                a = sub[i]["w1_onset"]
                b = sub[i + 1]["w1_onset"]
                if a == b:
                    t_same += 1
                t_vert_pairs.append((a, b))
            if len(p["lines"]) >= 5:
                mid = list(p["lines"][1:-1])
                rng.shuffle(mid)
                for i in range(len(mid) - 1):
                    t_enj_pairs.append((mid[i]["wn_end"], mid[i + 1]["w1_onset"]))
        null_vert_same.append(t_same)
        null_vert_mi.append(compute_pair_mi(t_vert_pairs))
        null_enjamb_mi.append(compute_pair_mi(t_enj_pairs))

    mu_same = sum(null_vert_same) / n_trials
    sd_same = math.sqrt(sum((x - mu_same) ** 2 for x in null_vert_same) / n_trials) or 1e-9
    z_same = (obs_vertical_same - mu_same) / sd_same

    mu_vmi = sum(null_vert_mi) / n_trials
    sd_vmi = math.sqrt(sum((x - mu_vmi) ** 2 for x in null_vert_mi) / n_trials) or 1e-9
    z_vmi = (obs_vert_mi - mu_vmi) / sd_vmi

    mu_emi = sum(null_enjamb_mi) / n_trials
    sd_emi = math.sqrt(sum((x - mu_emi) ** 2 for x in null_enjamb_mi) / n_trials) or 1e-9
    z_emi = (obs_enjamb_mi - mu_emi) / sd_emi

    # 2. Scan Single Continuous Paragraphs (with >= 7 continuation lines, i.e., len >= 8 lines)
    # for Vertical Acrostic Repulsion or Period-2 / Period-3 Cycling!
    single_para_acrostics = []
    for p in paragraphs:
        sub = p["lines"][1:]  # exclude Line 1 (<%>)
        if len(sub) < 7:
            continue
        seq = [r["w1_onset"] for r in sub]
        n_adj = len(seq) - 1
        obs_p_same = sum(1 for i in range(n_adj) if seq[i] == seq[i + 1])
        obs_p_lag2 = sum(1 for i in range(len(seq) - 2) if seq[i] == seq[i + 2])
        obs_p_lag3 = sum(1 for i in range(len(seq) - 3) if seq[i] == seq[i + 3])

        p_null_same = []
        p_null_lag2 = []
        p_null_lag3 = []
        for _ in range(400):
            s_copy = list(seq)
            rng.shuffle(s_copy)
            p_null_same.append(sum(1 for i in range(n_adj) if s_copy[i] == s_copy[i + 1]))
            p_null_lag2.append(sum(1 for i in range(len(seq) - 2) if s_copy[i] == s_copy[i + 2]))
            p_null_lag3.append(sum(1 for i in range(len(seq) - 3) if s_copy[i] == s_copy[i + 3]))

        p_mu = sum(p_null_same) / 400
        p_sd = math.sqrt(sum((x - p_mu) ** 2 for x in p_null_same) / 400) or 1.0
        p_z_same = (obs_p_same - p_mu) / p_sd

        l2_mu = sum(p_null_lag2) / 400
        l2_sd = math.sqrt(sum((x - l2_mu) ** 2 for x in p_null_lag2) / 400) or 1.0
        p_z_lag2 = (obs_p_lag2 - l2_mu) / l2_sd

        l3_mu = sum(p_null_lag3) / 400
        l3_sd = math.sqrt(sum((x - l3_mu) ** 2 for x in p_null_lag3) / 400) or 1.0
        p_z_lag3 = (obs_p_lag3 - l3_mu) / l3_sd

        single_para_acrostics.append({
            "para_id": p["para_id"],
            "folio": p["folio"],
            "section": p["section"],
            "language": p["language"],
            "hand": p["hand"],
            "n_continuation_lines": len(sub),
            "obs_adjacent_same": obs_p_same,
            "null_adjacent_same": round(p_mu, 2),
            "z_adjacent_same": round(p_z_same, 2),
            "z_lag2": round(p_z_lag2, 2),
            "z_lag3": round(p_z_lag3, 2),
            "w1_onset_sequence": [r["w1_onset"] for r in p["lines"]],
            "w1_words": [r["w1"] for r in p["lines"]],
        })

    top_repulsion_paras = sorted(single_para_acrostics, key=lambda x: x["z_adjacent_same"])[:12]
    top_lag2_paras = sorted(single_para_acrostics, key=lambda x: -x["z_lag2"])[:10]
    top_lag3_paras = sorted(single_para_acrostics, key=lambda x: -x["z_lag3"])[:10]

    # 3. Vertical (Lines 2..m) w1[i]->w1[i+1] transitions
    vert_counts = Counter(obs_vert_pairs)
    vert_left = Counter(x[0] for x in obs_vert_pairs)
    vert_right = Counter(x[1] for x in obs_vert_pairs)
    tot_vert = len(obs_vert_pairs) or 1
    vert_transitions = []
    for (a, b), c in vert_counts.most_common(30):
        cond = c / max(1, vert_left[a])
        base = vert_right[b] / tot_vert
        vert_transitions.append({
            "line_i_w1": a,
            "line_i_plus_1_w1": b,
            "is_same_onset": a == b,
            "count": c,
            "cond_prob": round(cond, 4),
            "lift": round(cond / max(1e-9, base), 3),
        })

    out = {
        "strict_intra_paragraph_vertical_tests": {
            "n_paragraphs_len_ge_4": len(body_paras),
            "total_continuation_line_pairs_lines_2_to_m": total_vertical_pairs,
            "observed_adjacent_same_w1_onset": obs_vertical_same,
            "observed_adjacent_same_rate": round(obs_vertical_same / max(1, total_vertical_pairs), 4),
            "null_adjacent_same_mean": round(mu_same, 2),
            "null_adjacent_same_std": round(sd_same, 2),
            "z_adjacent_same": round(z_same, 2),
            "vertical_w1_mi_bits": round(obs_vert_mi, 5),
            "null_vertical_w1_mi_bits": round(mu_vmi, 5),
            "z_vertical_w1_mi": round(z_vmi, 2),
            "cross_line_enjambment_wn_to_w1_mi_bits": round(obs_enjamb_mi, 5),
            "null_enjambment_mi_bits": round(mu_emi, 5),
            "z_enjambment_mi": round(z_emi, 2),
        },
        "vertical_lines_2_to_m_transitions": vert_transitions,
        "top_repulsion_single_paragraphs": top_repulsion_paras,
        "top_period2_single_paragraphs": top_lag2_paras,
        "top_period3_single_paragraphs": top_lag3_paras,
    }

    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)

    print("=== ATTACK 38 (STRICT INTRA-PARAGRAPH CONTINUATION LINES 2..m) ===")
    print(
        f"1. Strictly Continuation Lines (2..m) Same-Onset: "
        f"obs={obs_vertical_same}/{total_vertical_pairs} ({obs_vertical_same/total_vertical_pairs*100:.2f}%) "
        f"vs null={mu_same:.1f}+/-{sd_same:.1f} (z={z_same:+.2f})"
    )
    print(
        f"2. Strictly Continuation Lines (2..m) Vertical MI: obs={obs_vert_mi:.5f} vs null={mu_vmi:.5f} (z={z_vmi:+.2f})"
    )
    print(
        f"3. Strictly Interior Enjambment wn[i]->w1[i+1] MI: obs={obs_enjamb_mi:.5f} vs null={mu_emi:.5f} (z={z_emi:+.2f})"
    )
    print("\n--- Top 10 Single-Paragraph Anti-Repetition Acrostics (Lines 2..m) ---")
    for r in top_repulsion_paras[:10]:
        print(
            f"  {r['para_id']:10s} ($I={r['section']}, $L={r['language']}, cont_lines={r['n_continuation_lines']:2d}): "
            f"adj_same={r['obs_adjacent_same']:2d} vs {r['null_adjacent_same']:5.2f} "
            f"(z={r['z_adjacent_same']:+5.2f}, z_lag2={r['z_lag2']:+5.2f}, z_lag3={r['z_lag3']:+5.2f}) | "
            f"seq={' '.join(r['w1_onset_sequence'][:12])}"
        )
    print("\n--- Top 8 Single-Paragraph Period-2 (Lag-2 Alternating) Acrostics ---")
    for r in top_lag2_paras[:8]:
        print(
            f"  {r['para_id']:10s} ($I={r['section']}, cont_lines={r['n_continuation_lines']:2d}): "
            f"z_lag2={r['z_lag2']:+5.2f}, z_same={r['z_adjacent_same']:+5.2f} | "
            f"seq={' '.join(r['w1_onset_sequence'][:12])}"
        )
    print("\n--- Top 8 Single-Paragraph Period-3 (Lag-3 Cycling) Acrostics ---")
    for r in top_lag3_paras[:8]:
        print(
            f"  {r['para_id']:10s} ($I={r['section']}, cont_lines={r['n_continuation_lines']:2d}): "
            f"z_lag3={r['z_lag3']:+5.2f}, z_same={r['z_adjacent_same']:+5.2f} | "
            f"seq={' '.join(r['w1_onset_sequence'][:12])}"
        )


if __name__ == "__main__":
    main()
