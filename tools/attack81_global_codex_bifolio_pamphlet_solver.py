#!/usr/bin/env python3
"""
Attack 81 (Discovery 98): Complete 20-Quire Bifolio Pamphlet Reconstruction &
Global Codex Ordering / Displaced-Sheet Solver

Tests across all 20 Quires ($Q = A..T) and all 61 physical parchment bifolio sheets ($Q, $B):
1. Maps every physical bifolio sheet ($Q, $B) into:
   - Standard 4-page folded bifolio (`f_left_r, f_left_v, f_right_r, f_right_v`)
   - Multi-panel foldout sheet (>4 pages)
   - Singleton / missing conjugate (<4 pages)
2. Compares Cross-Fold Pamphlet Bridge (`f_left_v -> f_right_r`) vs. Bound Next-Leaf
   Bridge (`f_left_v -> f_{left+1}_r`) across:
   - Mixed-Language Quires (`D, E, F, G, H, Q`)
   - Uniform-Language Quires (`A, B, C, I, J, K, L, M, N, O, P, R, S, T`)
   - Non-Centerfold Bifolia (`$B < max_B`, where Bound Next-Leaf and Cross-Fold differ!)
3. Compares Flat-Sheet Spread Geometries:
   - Inside Spread (`f_left_v <-> f_right_r`)
   - Outside Spread (`f_right_v <-> f_left_r`, the outer face of the unfolded sheet!)
   - Recto-Verso Same-Half (`f_left_r <-> f_left_v` and `f_right_r <-> f_right_v`)
4. Optimal Bifolio Sheet Nesting & Displaced-Sheet Solver:
   - Within each multi-sheet quire ($Q with >=3 standard bifolia), tests whether:
     (a) Outer-to-Inner Pamphlet Drafting (`B=1 -> B=2 -> B=3 -> B=4`)
     (b) Inner-to-Outer Pamphlet Drafting (`B=4 -> B=3 -> B=2 -> B=1`)
     (c) Dialect-Grouped / Optimal Hamiltonian Sheet Permutation (`pi(B)`)
     maximizes inter-sheet boundary continuity (`Page 4 of Sheet i -> Page 1 of Sheet j`)
     and within-quire adjacent-sheet similarity!
   - Also tests Cross-Quire Misplaced Bifolio Sheets across all Herbal Quires (`A..H`).
"""

import itertools
import json
import math
import random
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
ZL_PATH = DATA_DIR / "ZL3b-n.txt"
OUT_JSON = DATA_DIR / "attack81_global_codex_bifolio_pamphlet_solver.json"

LOCUS_RE = re.compile(r"^<f([0-9]+[rv][0-9]*|Ros)\.([^,>]+),([^>]+)>\s*(.*)$")


def clean_tokens(raw: str):
    s = re.sub(r"\{[^}]*\}", "", raw)
    s = re.sub(r"\[([^:\]]+):[^\]]+\]", r"\1", s)
    s = s.replace("<%>", " ").replace("<$>", " ").replace("<->", " ")
    s = re.sub(r"<[^>]*>", " ", s)
    s = re.sub(r"@[0-9]+;", "", s)
    s = re.sub(r"[^a-zA-Z.\s]", "", s).lower()
    return [t for t in s.replace(".", " ").split() if t]


def extract_open_stem(w: str):
    if not any(g in w for g in ("k", "t", "p", "f", "ch", "sh")):
        return None
    rem = w
    for p in ("qol", "dal", "ol", "al", "qo", "po", "fo", "o", "y", "s", "d", "l", "q"):
        if rem.startswith(p) and len(rem) > len(p) + 1 and any(g in rem[len(p):] for g in ("k", "t", "p", "f", "ch", "sh")):
            rem = rem[len(p):]
            break
    s_norm = rem.replace("cph", "cth").replace("cfh", "ckh").replace("p", "t").replace("f", "k")
    s_norm = re.sub(r"e+", "e", s_norm)
    s_norm = re.sub(r"i+", "i", s_norm)
    return s_norm


def feature_profile(words: list) -> dict:
    n = max(len(words), 1)
    return {
        "open_cls": sum(1 for w in words if any(g in w for g in ("k", "t", "p", "f", "ch", "sh"))) / n,
        "qo": sum(1 for w in words if w.startswith("q")) / n,
        "l_appl": sum(1 for w in words if w.startswith(("l", "ol", "qol", "dal")) and len(w) > 3) / n,
        "s_y": sum(1 for w in words if w.startswith(("s", "y"))) / n,
        "gallows": sum(1 for w in words if any(g in w for g in ("k", "t", "p", "f"))) / n,
        "t_class": sum(1 for w in words if any(g in w for g in ("t", "p"))) / n,
        "dy": sum(1 for w in words if w.endswith("dy")) / n,
        "y_bare": sum(1 for w in words if w.endswith("y") and not w.endswith("dy")) / n,
        "in_min": sum(1 for w in words if w.endswith(("aiin", "ain", "oiin", "in"))) / n,
        "liq_l": sum(1 for w in words if w.endswith(("ol", "al"))) / n,
        "liq_r": sum(1 for w in words if w.endswith(("or", "ar"))) / n,
    }


def cosine_dict(d1: dict, d2: dict) -> float:
    keys = set(d1.keys()) & set(d2.keys())
    if not keys:
        return 0.0
    num = sum(d1[k] * d2[k] for k in keys)
    den1 = sum(v * v for v in d1.values())
    den2 = sum(v * v for v in d2.values())
    return num / math.sqrt(den1 * den2) if den1 and den2 else 0.0


def jaccard(s1: set, s2: set) -> float:
    if not s1 or not s2:
        return 0.0
    return len(s1 & s2) / len(s1 | s2)


def main():
    folios = []
    cur_meta = None
    global_stem_counts = Counter()

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
                "P": tags.get("P", "U"),
                "F": tags.get("F", "U"),
                "B": int(tags["B"]) if tags.get("B", "").isdigit() else 0,
                "I": tags.get("I", "U"),
                "L": tags.get("L", "U"),
                "H": tags.get("H", "U"),
                "words": [],
                "stems": set(),
            }
            folios.append(cur_meta)
            continue
        m = LOCUS_RE.match(raw_s)
        if m and cur_meta is not None:
            toks = clean_tokens(m.group(4))
            cur_meta["words"].extend(toks)
            for w in toks:
                st = extract_open_stem(w)
                if st:
                    cur_meta["stems"].add(st)
                    global_stem_counts[st] += 1

    for idx, f in enumerate(folios):
        f["seq_idx"] = idx
        f["feat"] = feature_profile(f["words"])
        f["word_set"] = set(f["words"])

    # Group by Quire ($Q) and Bifolio ($B)
    quires = defaultdict(list)
    bifolia = defaultdict(list)
    for f in folios:
        quires[f["Q"]].append(f)
        bifolia[(f["Q"], f["B"])].append(f)

    # 1. Inventory of all 20 Quires and 61 Bifolia
    quire_inventory = []
    for q_code in sorted(quires.keys()):
        q_pages = quires[q_code]
        b_groups = defaultdict(list)
        for p in q_pages:
            b_groups[p["B"]].append(p)
        langs = sorted(set(p["L"] for p in q_pages if p["L"] in ("A", "B")))
        hands = sorted(set(p["H"] for p in q_pages if p["H"] != "U"))
        secs = sorted(set(p["I"] for p in q_pages))
        std_4p = sum(1 for bg in b_groups.values() if len(bg) == 4)
        foldouts = sum(1 for bg in b_groups.values() if len(bg) > 4)
        singletons = sum(1 for bg in b_groups.values() if len(bg) < 4)
        quire_inventory.append({
            "quire": q_code,
            "n_pages": len(q_pages),
            "n_bifolia": len(b_groups),
            "std_4p_bifolia": std_4p,
            "foldout_bifolia": foldouts,
            "singleton_bifolia": singletons,
            "languages": langs,
            "hands": hands,
            "sections": secs,
            "is_mixed_lang": len(langs) > 1,
        })

    # 2. Flat-Sheet Spread Geometry Analysis across all 4-page standard bifolia
    # For a standard 4-page bifolio [p1=f_left_r, p2=f_left_v, p3=f_right_r, p4=f_right_v]:
    # - Inside Spread: p2 <-> p3 (`f_left_v <-> f_right_r`)
    # - Outside Spread: p4 <-> p1 (`f_right_v <-> f_left_r`, outer side of flat sheet!)
    # - Same-Leaf Recto-Verso: p1 <-> p2 (`f_left_r <-> f_left_v`) and p3 <-> p4 (`f_right_r <-> f_right_v`)
    # - Bound Next-Leaf (for non-centerfold bifolia where p2's bound successor is NOT p3): p2 <-> folios[p2.seq_idx + 1]
    spread_stats = defaultdict(lambda: {"feat_cos": [], "stem_jacc": [], "word_jacc": [], "same_lang": []})
    non_centerfold_bridges = []

    for (q_code, b_num), bg in sorted(bifolia.items()):
        if len(bg) != 4:
            continue
        bg_sorted = sorted(bg, key=lambda x: x["seq_idx"])
        p1, p2, p3, p4 = bg_sorted
        if min(len(x["words"]) for x in (p1, p2, p3, p4)) < 15:
            continue

        is_centerfold = (p3["seq_idx"] == p2["seq_idx"] + 1)
        q_is_mixed = len(set(x["L"] for x in quires[q_code] if x["L"] in ("A", "B"))) > 1

        def add_pair(bucket: str, a: dict, b: dict):
            spread_stats[bucket]["feat_cos"].append(cosine_dict(a["feat"], b["feat"]))
            spread_stats[bucket]["stem_jacc"].append(jaccard(a["stems"], b["stems"]))
            spread_stats[bucket]["word_jacc"].append(jaccard(a["word_set"], b["word_set"]))
            spread_stats[bucket]["same_lang"].append(1.0 if a["L"] == b["L"] else 0.0)

        add_pair("ALL_INSIDE_SPREAD_p2_p3", p2, p3)
        add_pair("ALL_OUTSIDE_SPREAD_p4_p1", p4, p1)
        add_pair("ALL_SAME_LEAF_RV_p1_p2_p3_p4", p1, p2)
        add_pair("ALL_SAME_LEAF_RV_p1_p2_p3_p4", p3, p4)

        if not is_centerfold and p2["seq_idx"] + 1 < len(folios):
            p_next = folios[p2["seq_idx"] + 1]
            if len(p_next["words"]) >= 15:
                add_pair("NON_CENTER_PAMPHLET_p2_p3", p2, p3)
                add_pair("NON_CENTER_BOUND_NEXT_p2_next", p2, p_next)
                add_pair("NON_CENTER_OUTSIDE_p4_p1", p4, p1)
                bucket_prefix = "MIXED_QUIRE" if q_is_mixed else "UNIFORM_QUIRE"
                add_pair(f"{bucket_prefix}_NON_CENTER_PAMPHLET_p2_p3", p2, p3)
                add_pair(f"{bucket_prefix}_NON_CENTER_BOUND_NEXT_p2_next", p2, p_next)

                pam_jacc = jaccard(p2["stems"], p3["stems"])
                bnd_jacc = jaccard(p2["stems"], p_next["stems"])
                shared_stems = sorted(
                    p2["stems"] & p3["stems"],
                    key=lambda s: (global_stem_counts[s], s),
                )
                non_centerfold_bridges.append({
                    "quire": q_code,
                    "bifolio": b_num,
                    "is_mixed_quire": q_is_mixed,
                    "p2_left_v": p2["folio"],
                    "p3_right_r": p3["folio"],
                    "bound_next_r": p_next["folio"],
                    "p2_lang_hand": f"{p2['L']}/H{p2['H']}",
                    "p3_lang_hand": f"{p3['L']}/H{p3['H']}",
                    "bound_next_lang_hand": f"{p_next['L']}/H{p_next['H']}",
                    "pamphlet_feat_cos": round(cosine_dict(p2["feat"], p3["feat"]), 4),
                    "bound_feat_cos": round(cosine_dict(p2["feat"], p_next["feat"]), 4),
                    "pamphlet_stem_jacc": round(pam_jacc, 4),
                    "bound_stem_jacc": round(bnd_jacc, 4),
                    "delta_stem_jacc": round(pam_jacc - bnd_jacc, 4),
                    "rare_shared_stems": shared_stems[:6],
                })

    spread_summary = {}
    for k, v in spread_stats.items():
        n = len(v["feat_cos"])
        if n == 0:
            continue
        spread_summary[k] = {
            "n_pairs": n,
            "mean_feat_cos": round(sum(v["feat_cos"]) / n, 4),
            "mean_stem_jacc": round(sum(v["stem_jacc"]) / n, 4),
            "mean_word_jacc": round(sum(v["word_jacc"]) / n, 4),
            "same_lang_rate": round(100.0 * sum(v["same_lang"]) / n, 2),
        }

    # 3. Sheet-to-Sheet Nesting Direction & Optimal Hamiltonian Sheet Permutation within each Quire
    # For each multi-sheet quire with >= 3 standard 4-page bifolia, each bifolio sheet B_i has:
    # - Sheet-level aggregated vocabulary & feature vector (all 4 pages combined)
    # - Page 1 (`p1 = f_left_r`) and Page 4 (`p4 = f_right_v`)
    # When sheets are read as 4-page pamphlets in sequence `B_(pi_1) -> B_(pi_2) -> ... -> B_(pi_k)`:
    # - Sheet-to-Sheet Similarity: mean Stem Jaccard & Feature Cosine between consecutive sheets `(S_i, S_{i+1})`
    # - Pamphlet Boundary Transition: mean Stem Jaccard & Feature Cosine from `p4(S_i) -> p1(S_{i+1})`
    quire_nesting_tests = []
    for q_code in sorted(quires.keys()):
        q_bifolia = []
        for (q, b_num), bg in sorted(bifolia.items()):
            if q == q_code and len(bg) == 4:
                bg_sorted = sorted(bg, key=lambda x: x["seq_idx"])
                all_words = [w for p in bg_sorted for w in p["words"]]
                if len(all_words) < 60:
                    continue
                all_stems = set().union(*(p["stems"] for p in bg_sorted))
                q_bifolia.append({
                    "B": b_num,
                    "L": bg_sorted[0]["L"],
                    "H": bg_sorted[0]["H"],
                    "pages": [p["folio"] for p in bg_sorted],
                    "p1": bg_sorted[0],
                    "p2": bg_sorted[1],
                    "p3": bg_sorted[2],
                    "p4": bg_sorted[3],
                    "all_stems": all_stems,
                    "sheet_feat": feature_profile(all_words),
                })
        if len(q_bifolia) < 3:
            continue

        def eval_sheet_order(order_list):
            sheet_jaccs = []
            sheet_fcos = []
            boundary_p4_p1_jacc = []
            boundary_p1_p4_inner_jacc = []
            lang_switches = 0
            for i in range(len(order_list) - 1):
                s_a = order_list[i]
                s_b = order_list[i + 1]
                sheet_jaccs.append(jaccard(s_a["all_stems"], s_b["all_stems"]))
                sheet_fcos.append(cosine_dict(s_a["sheet_feat"], s_b["sheet_feat"]))
                boundary_p4_p1_jacc.append(jaccard(s_a["p4"]["stems"], s_b["p1"]["stems"]))
                # Also check Bound Half-Quire transition: p2(s_a) -> p1(s_b)
                boundary_p1_p4_inner_jacc.append(jaccard(s_a["p2"]["stems"], s_b["p1"]["stems"]))
                if s_a["L"] != s_b["L"]:
                    lang_switches += 1
            m = len(sheet_jaccs)
            return {
                "order_B": [s["B"] for s in order_list],
                "order_L_H": [f"B{s['B']}:{s['L']}/H{s['H']}({s['pages'][0]}-{s['pages'][-1]})" for s in order_list],
                "lang_switches": lang_switches,
                "mean_sheet_stem_jacc": round(sum(sheet_jaccs) / m, 4),
                "mean_sheet_feat_cos": round(sum(sheet_fcos) / m, 4),
                "mean_p4_to_p1_jacc": round(sum(boundary_p4_p1_jacc) / m, 4),
                "mean_p2_to_p1_jacc": round(sum(boundary_p1_p4_inner_jacc) / m, 4),
            }

        outer_to_inner = sorted(q_bifolia, key=lambda x: x["B"])
        inner_to_outer = list(reversed(outer_to_inner))
        res_outer = eval_sheet_order(outer_to_inner)
        res_inner = eval_sheet_order(inner_to_outer)

        best_perm = None
        best_score = -1.0
        for perm in itertools.permutations(q_bifolia):
            ev = eval_sheet_order(list(perm))
            # Composite continuity score: sheet_stem_jacc + p4_to_p1_jacc - 0.05 * lang_switches
            score = ev["mean_sheet_stem_jacc"] + ev["mean_p4_to_p1_jacc"] - 0.05 * ev["lang_switches"]
            if score > best_score:
                best_score = score
                best_perm = ev

        quire_nesting_tests.append({
            "quire": q_code,
            "n_sheets": len(q_bifolia),
            "outer_to_inner_B1_to_Bk": res_outer,
            "inner_to_outer_Bk_to_B1": res_inner,
            "optimal_hamiltonian_order": best_perm,
            "delta_opt_vs_outer_sheet_jacc": round(
                best_perm["mean_sheet_stem_jacc"] - res_outer["mean_sheet_stem_jacc"], 4
            ),
            "delta_opt_vs_outer_p4_p1_jacc": round(
                best_perm["mean_p4_to_p1_jacc"] - res_outer["mean_p4_to_p1_jacc"], 4
            ),
        })

    # 4. Cross-Quire Misplaced Bifolio Sheet Test across Herbal Quires A..H
    # For every standard bifolio sheet in Quires A..H (31 sheets total), compute its average
    # Stem Jaccard & Feature Cosine to:
    # (a) Other sheets in its OWN Quire ($Q) of the same Language ($L)
    # (b) Sheets of the same Language ($L) in OTHER Herbal Quires ($Q' != $Q)
    # Identify whether any bifolio sheet has a stronger lexical affinity to a neighbor quire!
    herbal_sheets = []
    for (q_code, b_num), bg in sorted(bifolia.items()):
        if q_code in ("A", "B", "C", "D", "E", "F", "G", "H") and len(bg) == 4:
            bg_sorted = sorted(bg, key=lambda x: x["seq_idx"])
            all_words = [w for p in bg_sorted for w in p["words"]]
            all_stems = set().union(*(p["stems"] for p in bg_sorted))
            herbal_sheets.append({
                "id": f"Q{q_code}_B{b_num}",
                "Q": q_code,
                "B": b_num,
                "L": bg_sorted[0]["L"],
                "H": bg_sorted[0]["H"],
                "span": f"{bg_sorted[0]['folio']}..{bg_sorted[-1]['folio']}",
                "stems": all_stems,
                "feat": feature_profile(all_words),
            })

    sheet_affinity_rows = []
    same_quire_same_lang_jaccs = []
    diff_quire_same_lang_jaccs = []
    for s1 in herbal_sheets:
        quire_scores = defaultdict(list)
        for s2 in herbal_sheets:
            if s1["id"] == s2["id"]:
                continue
            j = jaccard(s1["stems"], s2["stems"])
            quire_scores[s2["Q"]].append(j)
            if s1["L"] == s2["L"]:
                if s1["Q"] == s2["Q"]:
                    same_quire_same_lang_jaccs.append(j)
                else:
                    diff_quire_same_lang_jaccs.append(j)

        q_means = {q: round(sum(vals) / len(vals), 4) for q, vals in quire_scores.items() if vals}
        own_q_mean = q_means.get(s1["Q"], 0.0)
        best_q, best_q_mean = max(q_means.items(), key=lambda kv: kv[1])
        best_match_sheet = max(
            (s2 for s2 in herbal_sheets if s2["id"] != s1["id"]),
            key=lambda s2: jaccard(s1["stems"], s2["stems"]),
        )
        sheet_affinity_rows.append({
            "sheet_id": s1["id"],
            "span": s1["span"],
            "L_H": f"{s1['L']}/H{s1['H']}",
            "own_quire": s1["Q"],
            "own_quire_mean_jacc": own_q_mean,
            "best_quire": best_q,
            "best_quire_mean_jacc": best_q_mean,
            "closest_single_sheet": f"{best_match_sheet['id']}({best_match_sheet['span']}:{best_match_sheet['L']}/H{best_match_sheet['H']})",
            "closest_sheet_jacc": round(jaccard(s1["stems"], best_match_sheet["stems"]), 4),
        })

    # Stratified permutation test for Same-Quire vs Diff-Quire within the same Language ($L)
    obs_quire_cohesion = (
        sum(same_quire_same_lang_jaccs) / len(same_quire_same_lang_jaccs)
        - sum(diff_quire_same_lang_jaccs) / len(diff_quire_same_lang_jaccs)
    )
    rng = random.Random(81)
    null_diffs = []
    for _ in range(500):
        # Permute Quire labels within each Language L
        by_lang = defaultdict(list)
        for idx, s in enumerate(herbal_sheets):
            by_lang[s["L"]].append(idx)
        perm_Q = {}
        for l_code, idxs in by_lang.items():
            q_labels = [herbal_sheets[i]["Q"] for i in idxs]
            rng.shuffle(q_labels)
            for i, ql in zip(idxs, q_labels):
                perm_Q[i] = ql
        sq, dq = [], []
        for i in range(len(herbal_sheets)):
            for j in range(i + 1, len(herbal_sheets)):
                if herbal_sheets[i]["L"] == herbal_sheets[j]["L"]:
                    jv = jaccard(herbal_sheets[i]["stems"], herbal_sheets[j]["stems"])
                    if perm_Q[i] == perm_Q[j]:
                        sq.append(jv)
                    else:
                        dq.append(jv)
        null_diffs.append(sum(sq) / len(sq) - sum(dq) / len(dq))

    null_mean = sum(null_diffs) / len(null_diffs)
    null_std = math.sqrt(sum((x - null_mean) ** 2 for x in null_diffs) / len(null_diffs)) or 1e-9
    z_quire_cohesion = (obs_quire_cohesion - null_mean) / null_std

    non_centerfold_bridges.sort(key=lambda x: -x["delta_stem_jacc"])

    out = {
        "quire_inventory": quire_inventory,
        "spread_geometry_summary": spread_summary,
        "quire_nesting_tests": quire_nesting_tests,
        "herbal_quire_cohesion_test": {
            "n_herbal_sheets": len(herbal_sheets),
            "same_quire_same_lang_mean_jacc": round(sum(same_quire_same_lang_jaccs) / len(same_quire_same_lang_jaccs), 4),
            "diff_quire_same_lang_mean_jacc": round(sum(diff_quire_same_lang_jaccs) / len(diff_quire_same_lang_jaccs), 4),
            "obs_delta": round(obs_quire_cohesion, 4),
            "null_mean_delta": round(null_mean, 4),
            "z_score": round(z_quire_cohesion, 2),
        },
        "top_non_centerfold_pamphlet_bridges": non_centerfold_bridges[:20],
        "herbal_sheet_affinities": sheet_affinity_rows,
    }
    OUT_JSON.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"Saved {OUT_JSON}")
    print("Spread Geometry Summary:")
    for k, v in spread_summary.items():
        print(f"  {k}: {v}")
    print("Herbal Quire Cohesion:", out["herbal_quire_cohesion_test"])
    print("Top 8 Non-Centerfold Pamphlet Bridges:")
    for b in non_centerfold_bridges[:8]:
        print(" ", b)
    print("Quire Nesting Tests:")
    for qn in quire_nesting_tests:
        print(
            f"  Q={qn['quire']} (n={qn['n_sheets']}): "
            f"Outer={qn['outer_to_inner_B1_to_Bk']['mean_sheet_stem_jacc']}/{qn['outer_to_inner_B1_to_Bk']['mean_p4_to_p1_jacc']} "
            f"Opt={qn['optimal_hamiltonian_order']['order_B']} -> "
            f"{qn['optimal_hamiltonian_order']['mean_sheet_stem_jacc']}/{qn['optimal_hamiltonian_order']['mean_p4_to_p1_jacc']} "
            f"(switches={qn['optimal_hamiltonian_order']['lang_switches']})"
        )


if __name__ == "__main__":
    main()
