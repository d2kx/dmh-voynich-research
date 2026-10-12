#!/usr/bin/env python3
"""
Attack 78: The 4-Page Bifolio Pamphlet Hypothesis & Reconstructing the Original
Scribal Compositional Order of Quires D, E, F, G, H, and Q

Tests:
1. In the 6 Mixed-Language Quires ($Q = D, E, F, G, H, Q), bound reading order
   fragments Scribe Hands 1, 2, 4, and 5 into 18 separate language/hand blocks
   (12 mid-quire dialect/hand switches).
2. However, every single physical parchment Bifolio Sheet ($B) is 100.00% uniform
   in Currier Language ($L) and Scribe Hand ($H):
     Page 1 (f_left_r) -> Page 2 (f_left_v) -> Page 3 (f_right_r) -> Page 4 (f_right_v).
3. Compares Page-to-Page Continuity across the 6 Mixed Quires under three ordering models:
   - Model 1 (`BOUND_CODEX_ORDER`): Current bound folio sequence (`f_1r -> f_1v -> f_2r -> ...`).
   - Model 2 (`BIFOLIO_PAMPHLET_ORDER`): Reading each folded 4-page bifolio sheet
     continuously (`f_left_r -> f_left_v -> f_right_r -> f_right_v`) before moving to the next bifolio.
   - Model 3 (`DIALECT_GROUPED_BIFOLIO_ORDER`): Grouping the $L=A (Hand 1) bifolia and
     $L=B (Hand 2 / Hand 5) bifolia within each quire and reading each 4-page bifolio in order.
4. Identifies the highest-continuity Cross-Fold Bifolio Bridges (`f_left_v <-> f_right_r`)
   across the entire manuscript, including shared rare open-class stems across the fold!
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
OUT_JSON = DATA_DIR / "attack78_scribal_bifolio_compositional_order.json"

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
                "B": tags.get("B", "U"),
                "I": tags.get("I", "U"),
                "L": tags.get("L", "U"),
                "H": tags.get("H", "U"),
                "words": [],
            }
            folios.append(cur_meta)
            continue

        m = LOCUS_RE.match(raw_s)
        if not m or cur_meta is None:
            continue
        ltype, raw_txt = m.group(3), m.group(4)
        if not ltype.startswith(("@P", "+P", "*P", "=P")):
            continue
        toks = clean_tokens(raw_txt)
        cur_meta["words"].extend(toks)

    for f in folios:
        stems = [extract_open_stem(w) for w in f["words"]]
        stems = [s for s in stems if s]
        f["stems"] = stems
        f["stem_set"] = set(stems)
        f["stem_counts"] = Counter(stems)
        f["feat"] = feature_profile(f["words"])
        for s in stems:
            global_stem_counts[s] += 1

    # Group by Quire
    by_quire = defaultdict(list)
    for f in folios:
        if f["words"]:
            by_quire[f["Q"]].append(f)

    mixed_quires = ["D", "E", "F", "G", "H", "Q"]

    def evaluate_order(seq):
        if len(seq) < 2:
            return {"transitions": 0, "lang_switches": 0, "hand_switches": 0, "mean_feat_cos": 0.0, "mean_stem_jacc": 0.0, "mean_stem_cos": 0.0}
        lang_sw = 0
        hand_sw = 0
        f_cos = []
        s_jacc = []
        s_cos = []
        for i in range(len(seq) - 1):
            a, b = seq[i], seq[i + 1]
            if a["L"] != b["L"]:
                lang_sw += 1
            if a["H"] != b["H"]:
                hand_sw += 1
            f_cos.append(cosine_dict(a["feat"], b["feat"]))
            s_jacc.append(jaccard(a["stem_set"], b["stem_set"]))
            s_cos.append(cosine_dict(a["stem_counts"], b["stem_counts"]))
        n = len(f_cos)
        return {
            "transitions": n,
            "lang_switches": lang_sw,
            "hand_switches": hand_sw,
            "mean_feat_cos": round(sum(f_cos) / n, 4),
            "mean_stem_jacc": round(sum(s_jacc) / n, 4),
            "mean_stem_cos": round(sum(s_cos) / n, 4),
        }

    quire_comparisons = {}
    all_bound_metrics = {"lang_sw": 0, "hand_sw": 0, "f_cos": [], "s_jacc": [], "s_cos": []}
    all_pamphlet_metrics = {"lang_sw": 0, "hand_sw": 0, "f_cos": [], "s_jacc": [], "s_cos": []}
    all_grouped_metrics = {"lang_sw": 0, "hand_sw": 0, "f_cos": [], "s_jacc": [], "s_cos": []}

    cross_fold_bridges = []

    for q in mixed_quires:
        q_fols = by_quire[q]
        # Model 1: Bound codex order
        bound_seq = q_fols[:]

        # Model 2: 4-page Bifolio Pamphlet order (sorted by B=1,2,3,4, and within B by bound order: f_left_r, f_left_v, f_right_r, f_right_v)
        b_groups = defaultdict(list)
        for f in q_fols:
            b_groups[f["B"]].append(f)
        pamphlet_seq = []
        for b_key in sorted(b_groups.keys()):
            b_fols = b_groups[b_key]
            pamphlet_seq.extend(b_fols)
            # Record cross-fold bridge (f_left_v -> f_right_r) if len == 4
            if len(b_fols) == 4:
                f_lv, f_rr = b_fols[1], b_fols[2]
                shared_stems = f_lv["stem_set"] & f_rr["stem_set"]
                rare_shared = sorted(
                    [s for s in shared_stems if global_stem_counts[s] <= 25],
                    key=lambda s: global_stem_counts[s],
                )
                cross_fold_bridges.append({
                    "quire": q,
                    "bifolio": b_key,
                    "lang": f_lv["L"],
                    "hand": f_lv["H"],
                    "bridge": f"{f_lv['folio']} -> {f_rr['folio']}",
                    "bound_next_rejected": f"{f_lv['folio']} -> {q_fols[q_fols.index(f_lv)+1]['folio']} (L={q_fols[q_fols.index(f_lv)+1]['L']},H={q_fols[q_fols.index(f_lv)+1]['H']})",
                    "bridge_feat_cos": round(cosine_dict(f_lv["feat"], f_rr["feat"]), 4),
                    "bound_next_feat_cos": round(cosine_dict(f_lv["feat"], q_fols[q_fols.index(f_lv)+1]["feat"]), 4),
                    "bridge_stem_jacc": round(jaccard(f_lv["stem_set"], f_rr["stem_set"]), 4),
                    "bound_next_stem_jacc": round(jaccard(f_lv["stem_set"], q_fols[q_fols.index(f_lv)+1]["stem_set"]), 4),
                    "shared_rare_stems": [f"{s}(n={global_stem_counts[s]})" for s in rare_shared[:8]],
                })

        # Model 3: Dialect/Hand-Grouped Bifolio Pamphlet Order
        grouped_seq = []
        for b_key in sorted(b_groups.keys(), key=lambda k: (b_groups[k][0]["L"], b_groups[k][0]["H"], k)):
            grouped_seq.extend(b_groups[b_key])

        m_bound = evaluate_order(bound_seq)
        m_pamph = evaluate_order(pamphlet_seq)
        m_group = evaluate_order(grouped_seq)

        quire_comparisons[q] = {
            "bound_order": [f"{x['folio']}({x['L']}{x['H']},B{x['B']})" for x in bound_seq],
            "pamphlet_order": [f"{x['folio']}({x['L']}{x['H']},B{x['B']})" for x in pamphlet_seq],
            "dialect_grouped_bifolio_order": [f"{x['folio']}({x['L']}{x['H']},B{x['B']})" for x in grouped_seq],
            "metrics_bound": m_bound,
            "metrics_pamphlet": m_pamph,
            "metrics_grouped_bifolio": m_group,
        }

        for acc, seq in ((all_bound_metrics, bound_seq), (all_pamphlet_metrics, pamphlet_seq), (all_grouped_metrics, grouped_seq)):
            for i in range(len(seq) - 1):
                a, b = seq[i], seq[i + 1]
                if a["L"] != b["L"]:
                    acc["lang_sw"] += 1
                if a["H"] != b["H"]:
                    acc["hand_sw"] += 1
                acc["f_cos"].append(cosine_dict(a["feat"], b["feat"]))
                acc["s_jacc"].append(jaccard(a["stem_set"], b["stem_set"]))
                acc["s_cos"].append(cosine_dict(a["stem_counts"], b["stem_counts"]))

    def summarize_acc(acc):
        n = len(acc["f_cos"])
        return {
            "total_transitions": n,
            "language_switches": acc["lang_sw"],
            "hand_switches": acc["hand_sw"],
            "mean_feature_cosine": round(sum(acc["f_cos"]) / n, 4),
            "mean_stem_jaccard": round(sum(acc["s_jacc"]) / n, 4),
            "mean_stem_cosine": round(sum(acc["s_cos"]) / n, 4),
        }

    sum_bound = summarize_acc(all_bound_metrics)
    sum_pamph = summarize_acc(all_pamphlet_metrics)
    sum_group = summarize_acc(all_grouped_metrics)

    # Compare Cross-Fold Bridges (f_left_v -> f_right_r) against Discontinuous Bound Transitions
    mean_bridge_fcos = sum(b["bridge_feat_cos"] for b in cross_fold_bridges) / len(cross_fold_bridges)
    mean_bound_fcos = sum(b["bound_next_feat_cos"] for b in cross_fold_bridges) / len(cross_fold_bridges)
    mean_bridge_sjacc = sum(b["bridge_stem_jacc"] for b in cross_fold_bridges) / len(cross_fold_bridges)
    mean_bound_sjacc = sum(b["bound_next_stem_jacc"] for b in cross_fold_bridges) / len(cross_fold_bridges)

    print("=== ATTACK 78: SCRIBAL BIFOLIO PAMPHLET ORDER VS BOUND CODEX ORDER ===")
    print(f"Across All 6 Mixed Quires ({sum_bound['total_transitions']} intra-quire page transitions):")
    print(f"  1. BOUND_CODEX_ORDER            : LangSwitches={sum_bound['language_switches']:2d} | HandSwitches={sum_bound['hand_switches']:2d} | FeatCos={sum_bound['mean_feature_cosine']:.4f} | StemJacc={sum_bound['mean_stem_jaccard']:.4f} | StemCos={sum_bound['mean_stem_cosine']:.4f}")
    print(f"  2. BIFOLIO_PAMPHLET_ORDER       : LangSwitches={sum_pamph['language_switches']:2d} | HandSwitches={sum_pamph['hand_switches']:2d} | FeatCos={sum_pamph['mean_feature_cosine']:.4f} | StemJacc={sum_pamph['mean_stem_jaccard']:.4f} | StemCos={sum_pamph['mean_stem_cosine']:.4f}")
    print(f"  3. DIALECT_GROUPED_BIFOLIO_ORDER: LangSwitches={sum_group['language_switches']:2d} | HandSwitches={sum_group['hand_switches']:2d} | FeatCos={sum_group['mean_feature_cosine']:.4f} | StemJacc={sum_group['mean_stem_jaccard']:.4f} | StemCos={sum_group['mean_stem_cosine']:.4f}")
    print(f"\nCross-Fold Pamphlet Bridges (`f_left_v -> f_right_r`, n={len(cross_fold_bridges)}):")
    print(f"  Mean Feature Cosine: {mean_bridge_fcos:.4f} (Pamphlet Bridge) vs {mean_bound_fcos:.4f} (Bound Next Leaf)")
    print(f"  Mean Stem Jaccard  : {mean_bridge_sjacc:.4f} (Pamphlet Bridge) vs {mean_bound_sjacc:.4f} (Bound Next Leaf)")
    for b in cross_fold_bridges[:10]:
        print(f"  Q={b['quire']} B={b['bifolio']} ({b['lang']}{b['hand']}): {b['bridge']:14s} (FeatCos={b['bridge_feat_cos']:.4f}, StemJacc={b['bridge_stem_jacc']:.4f}) vs Bound {b['bound_next_rejected']:24s} (FeatCos={b['bound_next_feat_cos']:.4f}) | RareShared={b['shared_rare_stems'][:4]}")

    out = {
        "overall_comparison": {
            "bound_codex_order": sum_bound,
            "bifolio_pamphlet_order": sum_pamph,
            "dialect_grouped_bifolio_order": sum_group,
            "cross_fold_bridge_mean_feat_cos": round(mean_bridge_fcos, 4),
            "bound_next_mean_feat_cos": round(mean_bound_fcos, 4),
            "cross_fold_bridge_mean_stem_jacc": round(mean_bridge_sjacc, 4),
            "bound_next_mean_stem_jacc": round(mean_bound_sjacc, 4),
        },
        "quire_details": quire_comparisons,
        "cross_fold_bifolio_bridges": cross_fold_bridges,
    }
    OUT_JSON.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"\nSaved -> {OUT_JSON}")


if __name__ == "__main__":
    main()
