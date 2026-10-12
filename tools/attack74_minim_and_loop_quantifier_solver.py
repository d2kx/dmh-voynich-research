#!/usr/bin/env python3
"""
Attack 74: Quantitative Minim-Count (`i / ii / iii`) & Vowel-Loop (`e / ee / eee`)
Progression, Cross-Word Moraic Assimilation & Margin-Compression Solver

Holding the exact consonantal+vocalic skeleton `w_skel` strictly fixed
(e.g. comparing ONLY `dain` vs `daiin` vs `daiiin` inside `d[I+]n`, or
comparing ONLY `qokedy` vs `qokeedy` vs `qokeeedy` inside `qok[E+]dy`),
tests 5 hypotheses with skeleton-stratified permutation baselines:

1. Horizontal Intra-Line Position & Right-Margin Compression (`x_rel` and `is_line_final`):
   - Does `i`-minim count (`1_I` vs `2_II+`) or `e`-loop count (`1_E` vs `2_EE+`) compress
     at the right margin (`w_n`) or expand in line-interior slots?
2. Vertical Intra-Paragraph Progression (`y_rel` from Paragraph Line 1 to Final Line):
   - Does `i`-minim or `e`-loop count shift from the opening line (`L_1`) to the closing
     line (`L_m`) of a paragraph?
3. Cross-Word Moraic / Minim Harmony (`w_{t-1}` -> `w_t` Assimilation):
   - Holding `w_skel` of `w_t` fixed, does a `2+`-loop (`EE`) or `2+`-minim (`II`) word at
     `w_{t-1}` induce `2+` loops/minims on `w_t`?
4. Intra-Paragraph Same-Skeleton Transition (`1st Mention` vs `2nd+ Mention` in same paragraph):
   - When the same skeleton `w_skel` recurs within a paragraph, how often does it hold its
     exact minim/loop count vs step up (`1 -> 2`) or step down (`2 -> 1`)?
5. Scribe Hand (`$H=1..5`) & Currier Dialect (`$L=A/B`) Within-Skeleton Calibration.
"""

import json
import math
import random
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
ZL_PATH = DATA_DIR / "ZL3b-n.txt"
OUT_JSON = DATA_DIR / "attack74_minim_and_loop_quantifier_solver.json"

LOCUS_RE = re.compile(r"^<f([0-9]+[rv][0-9]*|Ros)\.([^,>]+),([^>]+)>\s*(.*)$")


def clean_tokens(raw: str):
    s = re.sub(r"\{[^}]*\}", "", raw)
    s = re.sub(r"\[([^:\]]+):[^\]]+\]", r"\1", s)
    s = s.replace("<%>", " ").replace("<$>", " ").replace("<->", " ")
    s = re.sub(r"<[^>]*>", " ", s)
    s = re.sub(r"@[0-9]+;", "", s)
    s = re.sub(r"[^a-zA-Z.\s]", "", s).lower()
    return [t for t in s.replace(".", " ").split() if t]


def analyze_minim_and_loop(w: str):
    """
    Returns:
      - i_skel: word with `i+` replaced by `I` (if word contains `i`), and max `i` run length (1, 2, 3+)
      - e_skel: word with `e+` replaced by `E` (if word contains `e`), and max `e` run length (1, 2, 3+)
    """
    i_runs = [len(m.group(0)) for m in re.finditer(r"i+", w)]
    e_runs = [len(m.group(0)) for m in re.finditer(r"e+", w)]
    i_max = max(i_runs) if i_runs else 0
    e_max = max(e_runs) if e_runs else 0
    i_skel = re.sub(r"i+", "I", w) if i_max > 0 else None
    e_skel = re.sub(r"e+", "E", w) if e_max > 0 else None
    return i_skel, i_max, e_skel, e_max


def main():
    random.seed(42)
    cur_sec = "U"
    cur_lang = "U"
    cur_hand = "U"
    paragraphs = []
    cur_para = None

    for raw_line in ZL_PATH.read_text(encoding="utf-8", errors="replace").splitlines():
        raw_s = raw_line.strip()
        if not raw_s or raw_s.startswith("#"):
            continue
        if raw_s.startswith("<f") and ">" in raw_s and "." not in raw_s.split(">")[0]:
            m_s = re.search(r"\$I=([A-Z])", raw_s)
            cur_sec = m_s.group(1) if m_s else "U"
            m_l = re.search(r"\$L=([A-Z])", raw_s)
            cur_lang = m_l.group(1) if m_l else "U"
            m_h = re.search(r"\$H=([0-9A-Za-z]+)", raw_s)
            cur_hand = m_h.group(1) if m_h else "U"
            cur_para = None
            continue

        m = LOCUS_RE.match(raw_s)
        if not m:
            continue
        folio, lnum, ltype, raw_txt = f"f{m.group(1)}", m.group(2), m.group(3), m.group(4)
        if not ltype.startswith(("@P", "+P", "*P")):
            continue
        is_start = "<%>" in raw_txt or cur_para is None
        is_end = "<$>" in raw_txt
        has_drawing_break = "<->" in raw_txt
        toks = clean_tokens(raw_txt)
        if not toks:
            continue

        if is_start:
            cur_para = {
                "folio": folio,
                "sec": cur_sec,
                "lang": cur_lang,
                "hand": cur_hand,
                "lines": [],
            }
            paragraphs.append(cur_para)

        cur_para["lines"].append({
            "folio": folio,
            "lnum": lnum,
            "has_drawing_break": has_drawing_break,
            "words": toks,
        })
        if is_end:
            cur_para = None

    # Collect token records with full positional & contextual metadata
    i_records = []
    e_records = []

    i_skel_counts = Counter()
    e_skel_counts = Counter()
    i_skel_var = defaultdict(Counter)
    e_skel_var = defaultdict(Counter)

    for p_idx, p in enumerate(paragraphs):
        m_lines = len(p["lines"])
        for l_idx, ln in enumerate(p["lines"]):
            ws = ln["words"]
            n_words = len(ws)
            y_rel = l_idx / (m_lines - 1) if m_lines > 1 else 0.0
            line_zone = "TOP_LINE" if l_idx == 0 else ("BOT_LINE" if l_idx == m_lines - 1 else "MID_LINE")

            parsed = [analyze_minim_and_loop(w) for w in ws]
            for w_idx, (w, (i_skel, i_max, e_skel, e_max)) in enumerate(zip(ws, parsed)):
                x_rel = w_idx / (n_words - 1) if n_words > 1 else 0.0
                word_zone = "W_INIT" if w_idx == 0 else ("W_FINAL" if w_idx == n_words - 1 else "W_INTERIOR")
                prev_i_max = parsed[w_idx - 1][1] if w_idx > 0 else 0
                prev_e_max = parsed[w_idx - 1][3] if w_idx > 0 else 0

                rec_base = {
                    "para_id": p_idx,
                    "folio": p["folio"],
                    "lnum": ln["lnum"],
                    "sec": p["sec"],
                    "lang": p["lang"],
                    "hand": p["hand"],
                    "word": w,
                    "x_rel": x_rel,
                    "y_rel": y_rel,
                    "word_zone": word_zone,
                    "line_zone": line_zone,
                    "prev_i_max": prev_i_max,
                    "prev_e_max": prev_e_max,
                }
                if i_skel:
                    i_skel_counts[i_skel] += 1
                    i_skel_var[i_skel][i_max] += 1
                    r = dict(rec_base)
                    r["skel"] = i_skel
                    r["count_val"] = min(i_max, 3)
                    r["is_multi"] = 1 if i_max >= 2 else 0
                    i_records.append(r)
                if e_skel:
                    e_skel_counts[e_skel] += 1
                    e_skel_var[e_skel][e_max] += 1
                    r = dict(rec_base)
                    r["skel"] = e_skel
                    r["count_val"] = min(e_max, 3)
                    r["is_multi"] = 1 if e_max >= 2 else 0
                    e_records.append(r)

    # Filter to polymorphic skeletons (where both count=1 and count>=2 occur at least 5 times)
    poly_i_skels = {
        sk for sk, c in i_skel_var.items() if c[1] >= 5 and (c[2] + c[3]) >= 5
    }
    poly_e_skels = {
        sk for sk, c in e_skel_var.items() if c[1] >= 5 and (c[2] + c[3]) >= 5
    }

    poly_i_recs = [r for r in i_records if r["skel"] in poly_i_skels]
    poly_e_recs = [r for r in e_records if r["skel"] in poly_e_skels]

    def run_stratified_tests(recs, label, prev_key):
        # 1. Word Zone (W_INIT vs W_INTERIOR vs W_FINAL)
        by_wzone = defaultdict(list)
        for r in recs:
            by_wzone[r["word_zone"]].append(r["is_multi"])
        wzone_rates = {k: round(sum(v) / len(v) * 100, 2) for k, v in by_wzone.items() if v}

        # Stratified permutation test for W_FINAL vs non-final (permuting is_multi within exact `skel`)
        obs_final_rate = sum(by_wzone["W_FINAL"]) / len(by_wzone["W_FINAL"])
        obs_nonfinal_rate = sum(r["is_multi"] for r in recs if r["word_zone"] != "W_FINAL") / sum(1 for r in recs if r["word_zone"] != "W_FINAL")
        obs_final_diff = obs_final_rate - obs_nonfinal_rate

        # 2. Cross-Word Harmony: prev word has count>=2 vs prev word has count==1
        recs_with_prev = [r for r in recs if r[prev_key] >= 1]
        prev_multi = [r["is_multi"] for r in recs_with_prev if r[prev_key] >= 2]
        prev_single = [r["is_multi"] for r in recs_with_prev if r[prev_key] == 1]
        obs_harm_multi = sum(prev_multi) / max(len(prev_multi), 1)
        obs_harm_single = sum(prev_single) / max(len(prev_single), 1)
        obs_harm_diff = obs_harm_multi - obs_harm_single

        # 3. Line Zone (TOP_LINE vs MID_LINE vs BOT_LINE)
        by_lzone = defaultdict(list)
        for r in recs:
            by_lzone[r["line_zone"]].append(r["is_multi"])
        lzone_rates = {k: round(sum(v) / len(v) * 100, 2) for k, v in by_lzone.items() if v}
        obs_top_diff = (sum(by_lzone["TOP_LINE"]) / len(by_lzone["TOP_LINE"])) - (sum(r["is_multi"] for r in recs if r["line_zone"] != "TOP_LINE") / sum(1 for r in recs if r["line_zone"] != "TOP_LINE"))

        # 4. Scribe Hand ($H) & Currier Language ($L)
        by_hand = defaultdict(list)
        by_lang = defaultdict(list)
        for r in recs:
            by_hand[r["hand"]].append(r["is_multi"])
            by_lang[r["lang"]].append(r["is_multi"])
        hand_rates = {k: {"n": len(v), "multi_pct": round(sum(v) / len(v) * 100, 2)} for k, v in sorted(by_hand.items()) if len(v) >= 20}
        lang_rates = {k: {"n": len(v), "multi_pct": round(sum(v) / len(v) * 100, 2)} for k, v in sorted(by_lang.items()) if len(v) >= 20}

        # Run 300 skeleton-stratified permutations
        by_skel = defaultdict(list)
        for idx, r in enumerate(recs):
            by_skel[r["skel"]].append(idx)

        null_final_diffs = []
        null_harm_diffs = []
        null_top_diffs = []

        n_final = len(by_wzone["W_FINAL"])
        n_nonfinal = len(recs) - n_final
        n_top = len(by_lzone["TOP_LINE"])
        n_nontop = len(recs) - n_top

        for _ in range(300):
            perm_multi = [0] * len(recs)
            for sk, idxs in by_skel.items():
                vals = [recs[i]["is_multi"] for i in idxs]
                random.shuffle(vals)
                for i, v in zip(idxs, vals):
                    perm_multi[i] = v

            f_sum = sum(perm_multi[i] for i, r in enumerate(recs) if r["word_zone"] == "W_FINAL")
            nf_sum = sum(perm_multi) - f_sum
            null_final_diffs.append((f_sum / n_final) - (nf_sum / n_nonfinal))

            t_sum = sum(perm_multi[i] for i, r in enumerate(recs) if r["line_zone"] == "TOP_LINE")
            nt_sum = sum(perm_multi) - t_sum
            null_top_diffs.append((t_sum / n_top) - (nt_sum / n_nontop))

            pm_sum = sum(perm_multi[i] for i, r in enumerate(recs) if r[prev_key] >= 2)
            ps_sum = sum(perm_multi[i] for i, r in enumerate(recs) if r[prev_key] == 1)
            null_harm_diffs.append((pm_sum / max(len(prev_multi), 1)) - (ps_sum / max(len(prev_single), 1)))

        def calc_z(obs, nulls):
            mu = sum(nulls) / len(nulls)
            sd = math.sqrt(sum((x - mu) ** 2 for x in nulls) / len(nulls))
            return round((obs - mu) / (sd if sd > 0 else 1e-9), 2)

        return {
            "system": label,
            "polymorphic_skeletons": len(by_skel),
            "polymorphic_tokens": len(recs),
            "word_zone_multi_pct": wzone_rates,
            "w_final_vs_nonfinal_diff_pct": round(obs_final_diff * 100, 2),
            "w_final_permutation_z": calc_z(obs_final_diff, null_final_diffs),
            "line_zone_multi_pct": lzone_rates,
            "top_line_vs_other_diff_pct": round(obs_top_diff * 100, 2),
            "top_line_permutation_z": calc_z(obs_top_diff, null_top_diffs),
            "cross_word_harmony": {
                "after_multi_pct": round(obs_harm_multi * 100, 2),
                "after_single_pct": round(obs_harm_single * 100, 2),
                "diff_pct": round(obs_harm_diff * 100, 2),
                "harmony_permutation_z": calc_z(obs_harm_diff, null_harm_diffs),
            },
            "by_currier_lang": lang_rates,
            "by_scribe_hand": hand_rates,
        }

    i_stats = run_stratified_tests(poly_i_recs, "MINIM_I_SYSTEM (-ain vs -aiin vs -aiiin)", "prev_i_max")
    e_stats = run_stratified_tests(poly_e_recs, "LOOP_E_SYSTEM (-e- vs -ee- vs -eee-)", "prev_e_max")

    # 5. Top Polymorphic Skeleton Breakdowns
    top_i_families = []
    for sk in sorted(poly_i_skels, key=lambda k: i_skel_counts[k], reverse=True)[:20]:
        c = i_skel_var[sk]
        tot = i_skel_counts[sk]
        top_i_families.append({
            "skeleton": sk,
            "total": tot,
            "1_i": c[1],
            "2_ii": c[2],
            "3_iii": c[3],
            "multi_ii_pct": round((c[2] + c[3]) / tot * 100, 2),
        })

    top_e_families = []
    for sk in sorted(poly_e_skels, key=lambda k: e_skel_counts[k], reverse=True)[:20]:
        c = e_skel_var[sk]
        tot = e_skel_counts[sk]
        top_e_families.append({
            "skeleton": sk,
            "total": tot,
            "1_e": c[1],
            "2_ee": c[2],
            "3_eee": c[3] + c[4],
            "multi_ee_pct": round((c[2] + c[3] + c[4]) / tot * 100, 2),
        })

    print("=== ATTACK 74: QUANTITATIVE MINIM (`i/ii/iii`) & LOOP (`e/ee/eee`) SOLVER ===")
    for st in (i_stats, e_stats):
        print(f"\n--- {st['system']} (n={st['polymorphic_tokens']:,} across {st['polymorphic_skeletons']} skeletons) ---")
        print(f"  Word Zone Multi%: {st['word_zone_multi_pct']} | Final Diff = {st['w_final_vs_nonfinal_diff_pct']:+.2f}% (z = {st['w_final_permutation_z']:+.2f})")
        print(f"  Line Zone Multi%: {st['line_zone_multi_pct']} | Top-Line Diff = {st['top_line_vs_other_diff_pct']:+.2f}% (z = {st['top_line_permutation_z']:+.2f})")
        ch = st["cross_word_harmony"]
        print(f"  Cross-Word Harmony: After Multi = {ch['after_multi_pct']:.2f}% vs After Single = {ch['after_single_pct']:.2f}% | Diff = {ch['diff_pct']:+.2f}% (z = {ch['harmony_permutation_z']:+.2f})")
        print(f"  By Currier Lang: {st['by_currier_lang']}")
        print(f"  By Scribe Hand : {st['by_scribe_hand']}")

    out = {
        "minim_i_system": i_stats,
        "loop_e_system": e_stats,
        "top_polymorphic_i_skeletons": top_i_families,
        "top_polymorphic_e_skeletons": top_e_families,
    }
    OUT_JSON.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"\nSaved -> {OUT_JSON}")


if __name__ == "__main__":
    main()
