#!/usr/bin/env python3
"""
Phase 26 / Attack 15: Parallel Alignment of All 10 Same-Star Chained Recipe Pairs
(on the 20 Binary-Alternating Folios) & All 14 Crimson-Star (D -> L_1 -> L_2)
Triads (on f103r, f104r, f108r) in Quire 20 (f103r-f116r).

Tests:
1. Full structural, lexical, Core-Root (Attack 7 FST), and Elementary-Radical (Attack 12/14)
   alignment of the 10 Same-Star Chained Recipe Pairs on the 20 binary-alternating folios
   (where L. <-> L alternates 95.28% = 202/212 times, with only 10 same-star exceptions).
2. Positional Parallelism vs. Tail-to-Head Catenation test on the 10 Same-Star Pairs:
   - Header-to-Header (Line 1 <-> Line 1) vs. Tail-to-Head (Last Line of P_i <-> Line 1 of P_{i+1})
   - Exact word-level and radical-level alignments for each of the 10 pairs.
3. Structural & Radical Architecture of the 14 Crimson-Star (D) Recipes and their
   D -> L_1 -> L_2 Triads on f103r, f104r, and f108r:
   - How Slot 1 (D, Master Recipe), Slot 2 (L_1, Sub-Recipe 1), and Slot 3 (L_2, Sub-Recipe 2)
     differ in word length, opener prefixes/gallows, closer suffixes, and Elementary Radicals.
   - Cross-recipe root and radical sharing across the 14 D recipes vs. null baseline.
"""

import json
import math
import random
import re
from collections import Counter, defaultdict
from pathlib import Path

from attack7_positional_envelope_fst import (
    stage3_positional_proclitic_margin,
    extract_core_root_and_envelope,
)

ROOT = Path(__file__).resolve().parents[1]
ZL_PATH = ROOT / "data" / "ZL3b-n.txt"
RAD_LEX_PATH = ROOT / "data" / "attack12_core_root_radical_decomposition.json"
RAD_TABLE_PATH = ROOT / "data" / "attack14_elementary_radical_lexicon.json"
OUT_JSON = ROOT / "data" / "attack15_chained_recipes_and_d_triads.json"


def clean_tok(t: str) -> str:
    t = re.sub(r"\{[^}]*\}", "", t)
    t = re.sub(r"\[([^]:]+):[^\]]+\]", r"\1", t)
    t = t.replace("[", "").replace("]", "").replace("!", "").replace("?", "").replace("*", "")
    return t.strip(".,-<> ")


def short_star_code(sc: str | None) -> str:
    if not sc:
        return "N"
    s = sc.lower()
    if "dark" in s:
        return "D"
    if "dotted" in s:
        return "L."
    if "light" in s:
        return "L"
    return "*"


def parse_quire20_recipes():
    lines = ZL_PATH.read_text(encoding="utf-8", errors="ignore").splitlines()
    recipes = []
    cur_folio = None
    cur_hand = "?"
    cur_lang = "?"
    cur_para = None
    pending_star = None

    for raw in lines:
        raw = raw.strip()
        if not raw:
            continue
        if raw.startswith("#"):
            c = raw.lstrip("#").strip()
            if "star" in c.lower():
                pending_star = c
            continue

        m_f = re.match(r"^<(f\d+[rv]\d*)>\s*<!(.*)$", raw)
        if m_f:
            if cur_para and cur_para["words"]:
                recipes.append(cur_para)
                cur_para = None
            cur_folio = m_f.group(1)
            meta_str = m_f.group(2)
            m_h = re.search(r"\$H=(\w+)", meta_str)
            m_l = re.search(r"\$L=(\w+)", meta_str)
            cur_hand = m_h.group(1) if m_h else "?"
            cur_lang = m_l.group(1) if m_l else "?"
            pending_star = None
            continue

        if not cur_folio:
            continue
        m_num = re.match(r"^f(\d+)[rv]", cur_folio)
        if not m_num:
            continue
        fnum = int(m_num.group(1))
        if fnum < 103 or fnum > 116:
            continue

        m_line = re.match(r"^<(f\d+[rv]\d*)\.([^,>]+),([^>]+)>\s*(.*)$", raw)
        if not m_line:
            continue
        folio, lnum, loc, body = m_line.groups()
        if "P" not in loc:
            continue

        has_start = "<%>" in body
        has_end = "<$>" in body
        text_no_tags = re.sub(r"<[^>]+>", " ", body)
        raw_toks = [clean_tok(t) for t in re.split(r"[.\s,]+", text_no_tags) if clean_tok(t)]
        if not raw_toks:
            continue

        if has_start or cur_para is None or cur_para["folio"] != folio:
            if cur_para and cur_para["words"]:
                recipes.append(cur_para)
            star_type = short_star_code(pending_star)
            pending_star = None
            cur_para = {
                "folio": folio,
                "hand": cur_hand,
                "lang": cur_lang,
                "star": star_type,
                "start_line": f"{folio}.{lnum}",
                "lines": [],
                "words": [],
            }

        cur_para["lines"].append({
            "loc": f"{folio}.{lnum}",
            "words": raw_toks,
        })
        cur_para["words"].extend(raw_toks)

        if has_end:
            recipes.append(cur_para)
            cur_para = None

    if cur_para and cur_para["words"]:
        recipes.append(cur_para)

    by_folio = defaultdict(int)
    for r in recipes:
        by_folio[r["folio"]] += 1
        r["para_idx"] = by_folio[r["folio"]]

    return recipes


def cosine_counter(c1: Counter, c2: Counter) -> float:
    keys = set(c1.keys()) | set(c2.keys())
    if not keys:
        return 0.0
    dot = sum(c1[k] * c2[k] for k in keys)
    n1 = math.sqrt(sum(v * v for v in c1.values()))
    n2 = math.sqrt(sum(v * v for v in c2.values()))
    return dot / (n1 * n2) if n1 > 0 and n2 > 0 else 0.0


def jaccard(s1: set, s2: set) -> float:
    if not s1 or not s2:
        return 0.0
    return len(s1 & s2) / len(s1 | s2)


def main():
    print("Running Phase 26 / Attack 15: Chained Recipe Pairs & Crimson-Star (D) Triads...")
    rad_data = json.loads(RAD_LEX_PATH.read_text(encoding="utf-8"))
    root_decomp_map = rad_data.get("root_decompositions", {})

    rad_table_data = json.loads(RAD_TABLE_PATH.read_text(encoding="utf-8"))
    rad_gloss_map = {
        r["radical"]: r["proposed_semantic_syntactic_role"]
        for r in rad_table_data.get("lexicon_table", [])
    }

    recipes = parse_quire20_recipes()
    print(f"Parsed {len(recipes)} Quire 20 recipes across f103r-f116r.")

    # Compute global Core Root frequency across Quire 20
    global_root_freq = Counter()

    for r in recipes:
        roots = []
        rads = []
        prefs = []
        suffs = []
        line_roots = []
        word_analyses = []
        for l_idx, ln in enumerate(r["lines"]):
            lr = []
            for w_idx, w in enumerate(ln["words"]):
                canon = stage3_positional_proclitic_margin(w)
                pos_sig, env_sig, rt = extract_core_root_and_envelope(w, "MEDIAL")
                p = [x[2:] for x in env_sig.split("|") if x.startswith("P:")][0] if "P:" in env_sig else ""
                sf = [x[2:] for x in env_sig.split("|") if x.startswith("S:")][0] if "S:" in env_sig else ""
                if p == "0":
                    p = ""
                if sf == "0":
                    sf = ""
                if len(rt) >= 2:
                    roots.append(rt)
                    lr.append(rt)
                    global_root_freq[rt] += 1
                decomp = root_decomp_map.get(rt, [rt]) if rt else []
                for rd in decomp:
                    if rd:
                        rads.append(rd)
                if p:
                    prefs.append(p)
                if sf:
                    suffs.append(sf)
                word_analyses.append({
                    "raw": w,
                    "canon": canon,
                    "prefix": p,
                    "root": rt,
                    "radicals": decomp,
                    "suffix": sf,
                    "line_idx": l_idx,
                })
            line_roots.append(lr)
        r["roots"] = roots
        r["root_set"] = set(roots)
        r["rads"] = rads
        r["rad_counter"] = Counter(rads)
        r["pref_counter"] = Counter(prefs)
        r["suff_counter"] = Counter(suffs)
        r["line_roots"] = line_roots
        r["opener_roots"] = set(line_roots[0]) if line_roots else set()
        r["closer_roots"] = set(line_roots[-1]) if line_roots else set()
        r["word_analyses"] = word_analyses

    # Distinguish the 3 Crimson-Star (D) Triad Folios (f103r, f104r, f108r) from the 20 Binary-Alternating Folios
    d_folios = {r["folio"] for r in recipes if r["star"] == "D"}
    binary_folios = {r["folio"] for r in recipes} - d_folios

    same_star_binary_pairs = []
    alternating_binary_pairs = []

    for i in range(len(recipes) - 1):
        r1, r2 = recipes[i], recipes[i + 1]
        if r1["folio"] != r2["folio"] or r1["folio"] not in binary_folios:
            continue
        s1, s2 = r1["star"], r2["star"]
        if s1 not in ("L.", "L") or s2 not in ("L.", "L"):
            continue

        shared_roots = sorted(r1["root_set"] & r2["root_set"])
        rare_shared_roots = sorted([rt for rt in shared_roots if global_root_freq[rt] <= 35])
        root_jacc = jaccard(r1["root_set"], r2["root_set"])
        rad_cos = cosine_counter(r1["rad_counter"], r2["rad_counter"])
        suff_cos = cosine_counter(r1["suff_counter"], r2["suff_counter"])

        header_to_header_roots = sorted(r1["opener_roots"] & r2["opener_roots"])
        tail_to_head_roots = sorted(r1["closer_roots"] & r2["opener_roots"])

        shared_word_pairs = []
        for rt in shared_roots:
            w1s = [wa["raw"] for wa in r1["word_analyses"] if wa["root"] == rt]
            w2s = [wa["raw"] for wa in r2["word_analyses"] if wa["root"] == rt]
            rads_rt = root_decomp_map.get(rt, [rt])
            shared_word_pairs.append({
                "root": rt,
                "quire20_freq": global_root_freq[rt],
                "radicals": rads_rt,
                "radical_roles": [rad_gloss_map.get(rd, "") for rd in rads_rt],
                "p1_words": w1s[:4],
                "p2_words": w2s[:4],
                "in_header_to_header": rt in header_to_header_roots,
                "in_tail_to_head": rt in tail_to_head_roots,
            })

        rec = {
            "folio": r1["folio"],
            "pair_id": f"{r1['folio']}:P{r1['para_idx']}->P{r2['para_idx']}",
            "star_transition": f"{s1} -> {s2}",
            "p1_start_line": r1["start_line"],
            "p2_start_line": r2["start_line"],
            "p1_words_count": len(r1["words"]),
            "p2_words_count": len(r2["words"]),
            "p1_opener_5": r1["words"][:5],
            "p1_closer_5": r1["words"][-5:],
            "p2_opener_5": r2["words"][:5],
            "p2_closer_5": r2["words"][-5:],
            "root_jaccard": round(root_jacc, 4),
            "radical_cosine": round(rad_cos, 4),
            "suffix_cosine": round(suff_cos, 4),
            "shared_root_count": len(shared_roots),
            "rare_shared_root_count": len(rare_shared_roots),
            "shared_roots": shared_roots,
            "rare_shared_roots": rare_shared_roots,
            "header_to_header_roots": header_to_header_roots,
            "tail_to_head_roots": tail_to_head_roots,
            "shared_word_realizations": shared_word_pairs,
        }

        if s1 == s2:
            same_star_binary_pairs.append(rec)
        else:
            alternating_binary_pairs.append(rec)

    def summarize_pairs(group):
        if not group:
            return {}
        n = len(group)
        return {
            "count": n,
            "mean_root_jaccard": round(sum(x["root_jaccard"] for x in group) / n, 4),
            "mean_shared_roots": round(sum(x["shared_root_count"] for x in group) / n, 2),
            "mean_rare_shared_roots": round(sum(x["rare_shared_root_count"] for x in group) / n, 2),
            "mean_radical_cosine": round(sum(x["radical_cosine"] for x in group) / n, 4),
            "mean_suffix_cosine": round(sum(x["suffix_cosine"] for x in group) / n, 4),
            "header_to_header_match_rate": round(sum(1 for x in group if x["header_to_header_roots"]) / n, 4),
            "tail_to_head_match_rate": round(sum(1 for x in group if x["tail_to_head_roots"]) / n, 4),
        }

    same_summary = summarize_pairs(same_star_binary_pairs)
    alt_summary = summarize_pairs(alternating_binary_pairs)

    # 2. Align all Crimson-Star (D) Triads on f103r, f104r, f108r
    # Group each D recipe with the immediately following L recipes before the next D recipe on the same folio
    d_triads = []
    for fol in sorted(d_folios):
        fol_recs = [r for r in recipes if r["folio"] == fol]
        cur_group = []
        for r in fol_recs:
            if r["star"] == "D":
                if cur_group:
                    d_triads.append(cur_group)
                cur_group = [r]
            else:
                if cur_group:
                    cur_group.append(r)
        if cur_group:
            d_triads.append(cur_group)

    triad_profiles = []
    slot1_recs = []
    slot2_recs = []
    slot3_recs = []

    for grp in d_triads:
        r_d = grp[0]
        slot1_recs.append(r_d)
        if len(grp) >= 2:
            slot2_recs.append(grp[1])
        if len(grp) >= 3:
            slot3_recs.append(grp[2])

        # Compute intra-triad shared roots
        union_sub_roots = set()
        for sub in grp[1:]:
            union_sub_roots |= sub["root_set"]
        shared_d_to_subs = sorted(r_d["root_set"] & union_sub_roots)
        shared_l1_l2 = sorted(grp[1]["root_set"] & grp[2]["root_set"]) if len(grp) >= 3 else []

        triad_profiles.append({
            "folio": r_d["folio"],
            "triad_id": f"{r_d['folio']}:P{grp[0]['para_idx']}..P{grp[-1]['para_idx']}",
            "star_pattern": " -> ".join(x["star"] for x in grp),
            "member_word_counts": [len(x["words"]) for x in grp],
            "member_openers": [x["words"][:3] for x in grp],
            "member_closers": [x["words"][-3:] for x in grp],
            "shared_roots_D_to_subrecipes": shared_d_to_subs,
            "shared_roots_L1_to_L2": shared_l1_l2,
        })

    def slot_summary(recs, label):
        if not recs:
            return {}
        n = len(recs)
        all_w = [wa for r in recs for wa in r["word_analyses"]]
        opener_w = [r["word_analyses"][0] for r in recs if r["word_analyses"]]
        closer_w = [r["word_analyses"][-1] for r in recs if r["word_analyses"]]
        rad_cnt = Counter(rd for r in recs for rd in r["rads"])
        q_rate = sum(1 for r in recs for w in r["words"] if w.startswith("q")) / max(len(all_w), 1)
        o_rate = sum(1 for r in recs for w in r["words"] if w.startswith("o")) / max(len(all_w), 1)
        edy_rate = sum(1 for wa in all_w if wa["raw"].endswith(("edy", "ody", "dy"))) / max(len(all_w), 1)
        ain_rate = sum(1 for wa in all_w if wa["raw"].endswith(("aiin", "ain", "iin", "in"))) / max(len(all_w), 1)
        return {
            "slot": label,
            "recipe_count": n,
            "mean_word_count": round(sum(len(r["words"]) for r in recs) / n, 2),
            "mean_line_count": round(sum(len(r["lines"]) for r in recs) / n, 2),
            "q_proclitic_rate": round(q_rate, 4),
            "o_nominal_rate": round(o_rate, 4),
            "verbal_edy_dy_rate": round(edy_rate, 4),
            "nominal_aiin_rate": round(ain_rate, 4),
            "top_opener_prefixes": Counter(w["prefix"] or w["raw"][:2] for w in opener_w).most_common(5),
            "top_closer_suffixes": Counter(w["suffix"] or w["raw"][-2:] for w in closer_w).most_common(5),
            "top_radicals": rad_cnt.most_common(8),
        }

    slot_comparison = {
        "slot1_D_crimson_master": slot_summary(slot1_recs, "Slot 1 (D - Crimson Master)"),
        "slot2_L1_first_follower": slot_summary(slot2_recs, "Slot 2 (L_1 - First Follower)"),
        "slot3_L2_second_follower": slot_summary(slot3_recs, "Slot 3 (L_2 - Second Follower)"),
    }

    # Enriched radicals in D (Slot 1) vs all Quire 20
    total_d_rads = sum(len(r["rads"]) for r in slot1_recs)
    total_all_rads = sum(len(r["rads"]) for r in recipes)
    d_rad_counts = Counter(rd for r in slot1_recs for rd in r["rads"])
    all_rad_counts = Counter(rd for r in recipes for rd in r["rads"])

    d_enriched_radicals = []
    for rd, cnt in d_rad_counts.most_common():
        if cnt < 4:
            continue
        p_d = cnt / max(total_d_rads, 1)
        p_all = all_rad_counts[rd] / max(total_all_rads, 1)
        enr = p_d / max(p_all, 1e-9)
        d_enriched_radicals.append({
            "radical": rd,
            "d_count": cnt,
            "quire20_count": all_rad_counts[rd],
            "enrichment_vs_quire20": round(enr, 2),
            "role": rad_gloss_map.get(rd, ""),
        })
    d_enriched_radicals.sort(key=lambda x: (-x["enrichment_vs_quire20"], -x["d_count"]))

    out = {
        "summary": {
            "total_quire20_recipes": len(recipes),
            "binary_alternating_folios_count": len(binary_folios),
            "crimson_triad_folios": sorted(d_folios),
            "same_star_binary_pairs_summary": same_summary,
            "alternating_binary_pairs_summary": alt_summary,
            "triad_slot_comparison": slot_comparison,
        },
        "ten_same_star_chained_pairs": same_star_binary_pairs,
        "crimson_d_triads": triad_profiles,
        "d_enriched_radicals": d_enriched_radicals[:20],
    }

    OUT_JSON.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Saved {OUT_JSON}")
    print("\n--- Binary Folios: 10 Same-Star Pairs vs 202 Alternating Pairs ---")
    print("Same-Star (10 pairs):", same_summary)
    print("Alternating (202 pairs):", alt_summary)

    print("\n--- Detail of the 10 Same-Star Chained Pairs ---")
    for p in same_star_binary_pairs:
        print(f"  {p['pair_id']:14s} [{p['star_transition']}] jacc={p['root_jaccard']:.4f} rad_cos={p['radical_cosine']:.4f} "
              f"shared={p['shared_roots']} H2H={p['header_to_header_roots']} T2H={p['tail_to_head_roots']}")
        print(f"     P1 open: {' . '.join(p['p1_opener_5'])} ... close: {' . '.join(p['p1_closer_5'])}")
        print(f"     P2 open: {' . '.join(p['p2_opener_5'])} ... close: {' . '.join(p['p2_closer_5'])}")

    print("\n--- Crimson-Star (D -> L_1 -> L_2) Triad Slot Comparison ---")
    for k, v in slot_comparison.items():
        print(f"  {k}: words={v['mean_word_count']} lines={v['mean_line_count']} q={v['q_proclitic_rate']:.3f} "
              f"o={v['o_nominal_rate']:.3f} edy={v['verbal_edy_dy_rate']:.3f} aiin={v['nominal_aiin_rate']:.3f}")


if __name__ == "__main__":
    main()
