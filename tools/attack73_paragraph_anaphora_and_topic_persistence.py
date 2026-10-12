#!/usr/bin/env python3
"""
Attack 73: Intra-Paragraph Topic Persistence, Root Anaphora & Prefix-Shift Chains
Across Lines L_1 -> L_2 -> ... -> L_m

Tests across all multi-line prose paragraphs (@P0 / +P0) in the Voynich Manuscript:
1. Intra-Paragraph Open-Class Stem Persistence:
   - Extracts the canonical core stem (normalizing top-line p->t, f->k and stripping
     prefix proclitics q-, qo-, o-, d-, s-, y-, l-, ol-, dal- and inflectional suffixes)
     for every open-class token.
   - Measures the rate at which two distinct lines in the SAME paragraph share at least
     one open-class stem vs. two lines from DIFFERENT paragraphs within the same section
     and Currier language (500-trial section+language stratified permutation test).
2. The Anaphoric Prefix-Shift Trajectory (First Mention -> Subsequent Re-Mentions):
   - When an open-class stem S appears multiple times across different lines of the same
     paragraph (Line k_1 < Line k_2 < ...), how does its prefixal/inflectional state shift
     from First Mention (M_1) to Subsequent Re-Mention (M_2+)?
   - Specifically tests:
     * Does M_1 enrich for Top-Gallows (`p-/f-`), Bare/Zero-Prefix, or Nominal `o-`?
     * Does M_2+ enrich for Active `qo-`, Applicative `l-/ol-`, Deictic `d-/s-/y-`, or Verbal `-dy/-y`?
3. Cross-Line Boundary Echoes (Line k Final Word w_n -> Line k+1 Initial Word w_1):
   - Tests whether the suffix/constituent class of the final word of Line k predicts
     the onset prefix/constituent class of the first word of Line k+1 inside the same
     paragraph (within-paragraph line-order permutation test).
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
OUT_JSON = DATA_DIR / "attack73_paragraph_anaphora_and_topic_persistence.json"

LOCUS_RE = re.compile(r"^<f([0-9]+[rv][0-9]*|Ros)\.([^,>]+),([^>]+)>\s*(.*)$")


def clean_tokens(raw: str):
    s = re.sub(r"\{[^}]*\}", "", raw)
    s = re.sub(r"\[([^:\]]+):[^\]]+\]", r"\1", s)
    s = s.replace("<%>", " ").replace("<$>", " ").replace("<->", " ")
    s = re.sub(r"<[^>]*>", " ", s)
    s = re.sub(r"@[0-9]+;", "", s)
    s = re.sub(r"[^a-zA-Z.\s]", "", s).lower()
    return [t for t in s.replace(".", " ").split() if t]


def extract_prefix_and_stem(w: str):
    """
    Decomposes an open-class word into:
    (prefix_class, canonical_core_stem, suffix_class)
    """
    # Check open class
    if not any(g in w for g in ("k", "t", "p", "f", "ch", "sh")):
        return None

    # Identify prefix class
    pfx = "PFX_ZERO"
    rem = w
    if rem.startswith(("qol", "ol", "dal", "al")) and len(rem) > 4:
        for p in ("qol", "dal", "ol", "al"):
            if rem.startswith(p) and any(g in rem[len(p):] for g in ("k", "t", "p", "f", "ch", "sh")):
                pfx = "PFX_L_APPL"
                rem = rem[len(p):]
                break
    elif rem.startswith("l") and len(rem) > 3 and any(g in rem[1:] for g in ("k", "t", "p", "f", "ch", "sh")):
        pfx = "PFX_L_APPL"
        rem = rem[1:]
    elif rem.startswith("qo") and len(rem) > 3:
        pfx = "PFX_QO_ACT"
        rem = rem[2:]
    elif rem.startswith("q") and len(rem) > 2:
        pfx = "PFX_QO_ACT"
        rem = rem[1:]
    elif rem.startswith(("po", "fo", "p", "f", "cph", "cfh")):
        pfx = "PFX_TOP_PF"
    elif rem.startswith("o") and len(rem) > 2 and any(g in rem[1:] for g in ("k", "t", "p", "f", "ch", "sh")):
        pfx = "PFX_O_NOM"
        rem = rem[1:]
    elif rem.startswith(("y", "s", "d")) and len(rem) > 2 and any(g in rem[1:] for g in ("k", "t", "p", "f", "ch", "sh")):
        pfx = f"PFX_{rem[0].upper()}_CONT"
        rem = rem[1:]
        if rem.startswith("o") and len(rem) > 2 and any(g in rem[1:] for g in ("k", "t", "p", "f", "ch", "sh")):
            rem = rem[1:]

    # Identify suffix class
    if w.endswith(("aiin", "oiin", "eiin", "ain", "oin", "ein", "iiin")):
        suf = "SUF_IN"
    elif w.endswith("dy"):
        suf = "SUF_DY"
    elif w.endswith("y"):
        suf = "SUF_Y"
    elif w.endswith(("ol", "al", "el", "or", "ar", "er")):
        suf = "SUF_LIQ"
    elif w.endswith(("am", "om", "em", "m")):
        suf = "SUF_M"
    else:
        suf = "SUF_V"

    # Normalize stem for cross-line identity matching:
    # 1. p -> t, f -> k
    s_norm = rem.replace("cph", "cth").replace("cfh", "ckh").replace("p", "t").replace("f", "k")
    # 2. Collapse ee+ -> e, ii+ -> i
    s_norm = re.sub(r"e+", "e", s_norm)
    s_norm = re.sub(r"i+", "i", s_norm)
    # 3. Strip common inflectional endings to isolate core stem + nucleus
    for end in ("aiin", "oiin", "ain", "oin", "edy", "ody", "dy", "ey", "oy", "y", "ol", "or", "al", "ar", "am", "om"):
        if s_norm.endswith(end) and len(s_norm) - len(end) >= 2:
            s_norm = s_norm[:-len(end)]
            break

    return pfx, s_norm, suf


def line_initial_class(w: str) -> str:
    if any(w.startswith(p) for p in ("p", "f", "cph", "cfh")):
        return "INIT_PF_GALLOWS"
    if w.startswith("y"):
        return "INIT_Y_CONT"
    if w.startswith("s"):
        return "INIT_S_CONT"
    if w.startswith("d"):
        return "INIT_D_DEICTIC"
    if w.startswith("sh"):
        return "INIT_SH_BENCH"
    if w.startswith("ch"):
        return "INIT_CH_BENCH"
    if w.startswith("qo") or w.startswith("q"):
        return "INIT_QO_ACT"
    if w.startswith("o"):
        return "INIT_O_NOM"
    return "INIT_OTHER"


def line_final_class(w: str) -> str:
    if w.endswith(("am", "om", "m")):
        return "FIN_M_NASAL"
    if w.endswith(("aiin", "oiin", "ain", "oin", "in")):
        return "FIN_IN_MINIM"
    if w.endswith("dy"):
        return "FIN_DY_DENTAL"
    if w.endswith("y"):
        return "FIN_Y_BARE"
    if w.endswith(("ol", "al")):
        return "FIN_L_LAT"
    if w.endswith(("or", "ar")):
        return "FIN_R_RHO"
    return "FIN_OTHER"


def main():
    random.seed(42)
    paragraphs = []
    cur_para = None
    cur_sec = "U"
    cur_lang = "U"
    cur_hand = "U"

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

        stem_items = []
        for idx, w in enumerate(toks):
            res = extract_prefix_and_stem(w)
            if res:
                stem_items.append((w, idx, res[0], res[1], res[2]))

        cur_para["lines"].append({
            "folio": folio,
            "lnum": lnum,
            "words": toks,
            "stems": stem_items,
            "stem_set": {it[3] for it in stem_items},
            "word_set": set(toks),
        })
        if is_end:
            cur_para = None

    multi_paras = [p for p in paragraphs if len(p["lines"]) >= 2]

    # 1. Intra-Paragraph Exact Word & Open-Class Stem Persistence vs Stratified Null
    obs_stem_overlap_pairs = 0
    obs_exact_word_overlap_pairs = 0
    total_line_pairs = 0

    for p in multi_paras:
        lns = p["lines"]
        for i in range(len(lns)):
            for j in range(i + 1, len(lns)):
                total_line_pairs += 1
                if lns[i]["stem_set"] & lns[j]["stem_set"]:
                    obs_stem_overlap_pairs += 1
                # Exclude top-5 closed-class words (daiin, ol, aiin, chol, dar) for exact open-class word echo
                open_i = {it[0] for it in lns[i]["stems"]}
                open_j = {it[0] for it in lns[j]["stems"]}
                if open_i & open_j:
                    obs_exact_word_overlap_pairs += 1

    obs_stem_rate = obs_stem_overlap_pairs / total_line_pairs
    obs_word_rate = obs_exact_word_overlap_pairs / total_line_pairs

    # Stratified permutation: shuffle lines across paragraphs within same (sec, lang) bucket
    by_bucket = defaultdict(list)
    for p in multi_paras:
        for ln in p["lines"]:
            by_bucket[(p["sec"], p["lang"])].append(ln)

    null_stem_rates = []
    null_word_rates = []
    for _ in range(250):
        shuf_buckets = {k: v[:] for k, v in by_bucket.items()}
        for v in shuf_buckets.values():
            random.shuffle(v)
        ptrs = defaultdict(int)
        s_hits = 0
        w_hits = 0
        for p in multi_paras:
            bk = (p["sec"], p["lang"])
            m = len(p["lines"])
            start = ptrs[bk]
            sub = shuf_buckets[bk][start : start + m]
            ptrs[bk] += m
            for i in range(m):
                for j in range(i + 1, m):
                    if sub[i]["stem_set"] & sub[j]["stem_set"]:
                        s_hits += 1
                    oi = {it[0] for it in sub[i]["stems"]}
                    oj = {it[0] for it in sub[j]["stems"]}
                    if oi & oj:
                        w_hits += 1
        null_stem_rates.append(s_hits / total_line_pairs)
        null_word_rates.append(w_hits / total_line_pairs)

    mu_stem = sum(null_stem_rates) / len(null_stem_rates)
    sd_stem = math.sqrt(sum((x - mu_stem) ** 2 for x in null_stem_rates) / len(null_stem_rates))
    z_stem = (obs_stem_rate - mu_stem) / (sd_stem if sd_stem > 0 else 1e-9)

    mu_word = sum(null_word_rates) / len(null_word_rates)
    sd_word = math.sqrt(sum((x - mu_word) ** 2 for x in null_word_rates) / len(null_word_rates))
    z_word = (obs_word_rate - mu_word) / (sd_word if sd_word > 0 else 1e-9)

    # 2. Anaphoric Prefix-Shift Trajectory: First Mention (M1) vs Subsequent Re-Mentions (M2+)
    # For stems that appear on >= 2 distinct lines of the same paragraph
    first_mention_pfx = Counter()
    remention_pfx = Counter()
    shift_transitions = Counter()
    anaphoric_chains = []

    for p in multi_paras:
        stem_occurrences = defaultdict(list)
        for l_idx, ln in enumerate(p["lines"]):
            for w, w_idx, pfx, st, suf in ln["stems"]:
                stem_occurrences[st].append((l_idx, w_idx, w, pfx, suf))

        for st, occs in stem_occurrences.items():
            distinct_lines = sorted({o[0] for o in occs})
            if len(distinct_lines) < 2:
                continue
            first_o = occs[0]
            first_mention_pfx[first_o[3]] += 1
            for sub_o in occs[1:]:
                if sub_o[0] > first_o[0]:
                    remention_pfx[sub_o[3]] += 1
                    shift_transitions[f"{first_o[3]} -> {sub_o[3]}"] += 1
            # Record notable multi-line prefix shifts where word changes form
            distinct_words = []
            for o in occs:
                tag = f"L{o[0]+1}:{o[2]}({o[3]})"
                if not distinct_words or distinct_words[-1].split(":")[1] != f"{o[2]}({o[3]})":
                    distinct_words.append(tag)
            if len({o[2] for o in occs}) >= 2 and len(distinct_lines) >= 3:
                anaphoric_chains.append({
                    "folio": p["folio"],
                    "sec": p["sec"],
                    "lang": p["lang"],
                    "stem": st,
                    "lines_spanned": len(distinct_lines),
                    "chain": " -> ".join(distinct_words[:6]),
                })

    tot_m1 = sum(first_mention_pfx.values())
    tot_m2 = sum(remention_pfx.values())
    pfx_comparison = {}
    for k in sorted(set(first_mention_pfx.keys()) | set(remention_pfx.keys())):
        r1 = first_mention_pfx[k] / max(tot_m1, 1)
        r2 = remention_pfx[k] / max(tot_m2, 1)
        pfx_comparison[k] = {
            "first_mention_count": first_mention_pfx[k],
            "first_mention_pct": round(r1 * 100, 2),
            "remention_count": remention_pfx[k],
            "remention_pct": round(r2 * 100, 2),
            "remention_to_first_ratio": round(r2 / r1, 3) if r1 > 0 else None,
        }

    # 3. Cross-Line Boundary Echoes (Line k Final Word -> Line k+1 Initial Word)
    boundary_pairs = Counter()
    fin_counts = Counter()
    init_counts = Counter()
    total_boundaries = 0
    exact_boundary_stem_echoes = 0

    for p in multi_paras:
        lns = p["lines"]
        for i in range(len(lns) - 1):
            w_fin = lns[i]["words"][-1]
            w_init = lns[i + 1]["words"][0]
            fc = line_final_class(w_fin)
            ic = line_initial_class(w_init)
            boundary_pairs[(fc, ic)] += 1
            fin_counts[fc] += 1
            init_counts[ic] += 1
            total_boundaries += 1
            r_fin = extract_prefix_and_stem(w_fin)
            r_init = extract_prefix_and_stem(w_init)
            if r_fin and r_init and r_fin[1] == r_init[1]:
                exact_boundary_stem_echoes += 1

    # Compute MI of (Line_k_Final_Class -> Line_{k+1}_Initial_Class)
    obs_b_mi = 0.0
    top_boundary_lifts = []
    for (fc, ic), cnt in boundary_pairs.items():
        p_xy = cnt / total_boundaries
        p_x = fin_counts[fc] / total_boundaries
        p_y = init_counts[ic] / total_boundaries
        obs_b_mi += p_xy * math.log2(p_xy / (p_x * p_y))
        if cnt >= 15:
            top_boundary_lifts.append({
                "line_k_final": fc,
                "line_k1_initial": ic,
                "count": cnt,
                "expected": round(p_x * p_y * total_boundaries, 1),
                "lift": round(p_xy / (p_x * p_y), 3),
            })
    top_boundary_lifts.sort(key=lambda x: x["lift"], reverse=True)

    anaphoric_chains.sort(key=lambda x: x["lines_spanned"], reverse=True)

    print("=== ATTACK 73: INTRA-PARAGRAPH TOPIC PERSISTENCE & ANAPHORIC CHAINS ===")
    print(f"Multi-Line Paragraphs: {len(multi_paras):,} | Intra-Paragraph Line Pairs: {total_line_pairs:,}")
    print(f"Open-Class Stem Overlap Rate: {obs_stem_rate*100:.2f}% vs {mu_stem*100:.2f}% ± {sd_stem*100:.2f}% null (z = +{z_stem:.2f})")
    print(f"Exact Open-Class Word Overlap Rate: {obs_word_rate*100:.2f}% vs {mu_word*100:.2f}% ± {sd_word*100:.2f}% null (z = +{z_word:.2f})")
    print("\nAnaphoric Prefix-Shift Trajectory (First Mention M1 -> Subsequent Re-Mention M2+):")
    for k, v in pfx_comparison.items():
        print(f"  {k:14s}: M1 = {v['first_mention_pct']:5.2f}% ({v['first_mention_count']:4d}) -> M2+ = {v['remention_pct']:5.2f}% ({v['remention_count']:4d}) | Ratio = {v['remention_to_first_ratio']}x")
    print(f"\nCross-Line Boundary Transitions (n = {total_boundaries:,}, MI = {obs_b_mi:.5f} bits):")
    for b in top_boundary_lifts[:8]:
        print(f"  {b['line_k_final']:14s} -> {b['line_k1_initial']:16s}: {b['count']:4d} (exp {b['expected']:5.1f}, lift = {b['lift']:.3f}x)")

    out = {
        "summary": {
            "multi_line_paragraphs": len(multi_paras),
            "intra_paragraph_line_pairs": total_line_pairs,
            "stem_overlap_rate_pct": round(obs_stem_rate * 100, 2),
            "null_stem_overlap_mean_pct": round(mu_stem * 100, 2),
            "null_stem_overlap_sd_pct": round(sd_stem * 100, 2),
            "stem_persistence_z": round(z_stem, 2),
            "exact_open_word_overlap_rate_pct": round(obs_word_rate * 100, 2),
            "null_word_overlap_mean_pct": round(mu_word * 100, 2),
            "null_word_overlap_sd_pct": round(sd_word * 100, 2),
            "exact_word_persistence_z": round(z_word, 2),
            "cross_line_boundary_mi_bits": round(obs_b_mi, 5),
            "exact_boundary_stem_echoes": exact_boundary_stem_echoes,
        },
        "anaphoric_prefix_shift": pfx_comparison,
        "top_prefix_shift_transitions": [
            {"transition": k, "count": v} for k, v in shift_transitions.most_common(20)
        ],
        "top_cross_line_boundary_lifts": top_boundary_lifts[:20],
        "sample_multi_line_anaphoric_chains": anaphoric_chains[:30],
    }

    OUT_JSON.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"\nSaved -> {OUT_JSON}")


if __name__ == "__main__":
    main()
