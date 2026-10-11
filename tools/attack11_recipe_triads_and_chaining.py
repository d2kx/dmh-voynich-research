#!/usr/bin/env python3
"""
Phase 22 / Attack 11: The `D, L, L` Triad Cycle, Multi-Recipe Chaining & Anaphoric
Opener Taxonomy Across the 285 Starred Recipes (`f103r–f116r`).

Tests:
1. Folio-by-Folio Marginal Star Sequences (`D` Crimson, `L` Plain Yellow, `L.` Dotted Yellow):
   - Full sequence map across all 23 folios (`f103r–f116r`), testing run-lengths, triad cycles
     (`D, L, L` on `f103r`), and structural contrasts between `D`, `L`, and `L.`.
2. Consecutive Recipe Chaining (`P_i -> P_{i+1}`, 5,000-Trial Within-Folio Permutation Test):
   - Tests whether immediately consecutive recipes `(P_i, P_{i+1})` on the same folio share
     significantly more:
       a) Rare Canonical Stems (global count <= 25 and <= 50)
       b) Rare Core Roots (global count <= 50)
       c) Boundary Echoes (Last line of P_i <-> First line of P_{i+1} sharing a Core Root or Stem)
       d) Overall Vocabulary Jaccard similarity
     compared to 5,000 random permutations of paragraph order within each folio!
3. Deep Forensics of the Crimson-Star (`D`) Triads on `f103r`, `f104r`, and `f108r`:
   - Compares Triad Slot 1 (`D`), Slot 2 (`L_1`), and Slot 3 (`L_2`) on `f103r`, and inspects
     exact stem/root chaining inside each triad and across `f108r`.
4. Recipe Opener (`w_0`) & Closer (`w_last`) Formula Taxonomy across all 285 Starred Recipes.
"""

import json
import math
import os
import random
import re
from collections import Counter, defaultdict

from attack7_positional_envelope_fst import (
    stage3_positional_proclitic_margin,
    extract_core_root_and_envelope,
)

ZL_PATH = os.path.join("data", "ZL3b-n.txt")
INDEX_PATH = os.path.join("data", "folio_index.json")
OUT_JSON = os.path.join("data", "attack11_recipe_triads_and_chaining.json")


def clean_tok(t: str) -> str:
    t = re.sub(r"\{[^}]*\}", "", t)
    t = re.sub(r"\[([^]:]+):[^\]]+\]", r"\1", t)
    t = t.replace("[", "").replace("]", "").replace("?", "").replace("!", "").replace("*", "")
    t = t.replace(",", "").replace("-", "").strip()
    return t


def short_star_code(sc: str) -> str:
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


def parse_manuscript():
    with open(INDEX_PATH, "r", encoding="utf-8") as f:
        folio_index = json.load(f)["folios"]

    prose_paragraphs = []
    cur_folio = None
    cur_sec = "?"
    cur_lang = "?"
    cur_hand = "?"
    cur_para_lines = []
    cur_star = "N"
    pending_star_comment = None
    p_idx_by_folio = Counter()

    line_re = re.compile(r"^<([^.]+)\.([^,>]+),([^>]+)>\s+(.*)$")

    with open(ZL_PATH, "r", encoding="utf-8") as f:
        for raw_line in f:
            raw_line = raw_line.strip()
            if not raw_line:
                continue
            if raw_line.startswith("#"):
                c = raw_line.lstrip("#").strip()
                if "star" in c.lower():
                    pending_star_comment = c
                continue
            m_f = re.match(r"^<f?([^>]+)>\s*<!(.*)$", raw_line)
            if m_f and "." not in m_f.group(1):
                if cur_para_lines and cur_folio:
                    p_idx_by_folio[cur_folio] += 1
                    prose_paragraphs.append({
                        "folio": cur_folio,
                        "sec": cur_sec,
                        "lang": cur_lang,
                        "hand": cur_hand,
                        "p_idx": p_idx_by_folio[cur_folio],
                        "star": cur_star,
                        "lines": cur_para_lines,
                    })
                    cur_para_lines = []
                    cur_star = "N"
                cur_folio = "f" + m_f.group(1) if not m_f.group(1).startswith("f") else m_f.group(1)
                meta = folio_index.get(cur_folio, {})
                cur_sec = meta.get("section", "?")
                cur_lang = meta.get("currier_language", "?")
                cur_hand = str(meta.get("hand", "?"))
                pending_star_comment = None
                continue

            m = line_re.match(raw_line)
            if not m:
                continue
            folio, loc_num, tag, rest = m.group(1), m.group(2), m.group(3), m.group(4)
            if tag.startswith(("@L", "&L", "@C", "&C", "@R", "&R")):
                continue

            meta = folio_index.get(folio, {})
            sec = meta.get("section", cur_sec if folio == cur_folio else "?")
            lang = meta.get("currier_language", cur_lang if folio == cur_folio else "?")
            hand = str(meta.get("hand", cur_hand if folio == cur_folio else "?"))

            has_para_start = "<%>" in rest
            has_para_end = "<$>" in rest

            if has_para_start:
                if cur_para_lines:
                    p_idx_by_folio[folio] += 1
                    prose_paragraphs.append({
                        "folio": folio,
                        "sec": sec,
                        "lang": lang,
                        "hand": hand,
                        "p_idx": p_idx_by_folio[folio],
                        "star": cur_star,
                        "lines": cur_para_lines,
                    })
                    cur_para_lines = []
                cur_star = short_star_code(pending_star_comment)
                pending_star_comment = None

            rest_clean = re.sub(r"<!([^>]*)>", "", rest)
            rest_clean = rest_clean.replace("<%>", "").replace("<$>", "").replace("<->", " ")
            raw_toks = [clean_tok(t) for t in rest_clean.split(".") if clean_tok(t)]
            if not raw_toks:
                continue

            line_objs = []
            for w_i, tok in enumerate(raw_toks):
                canon = stage3_positional_proclitic_margin(tok)
                pos_sig, env_sig, core_root = extract_core_root_and_envelope(tok, "MEDIAL")
                sfx = [p[2:] for p in env_sig.split("|") if p.startswith("S:")][0]
                line_objs.append({
                    "folio": folio,
                    "loc": f"{folio}.{loc_num}",
                    "surface": tok,
                    "canon": canon,
                    "core_root": core_root,
                    "env_sig": env_sig,
                    "suffix": sfx,
                    "w_idx": w_i,
                    "line_len": len(raw_toks),
                })
            cur_para_lines.append(line_objs)

            if has_para_end and cur_para_lines:
                p_idx_by_folio[folio] += 1
                prose_paragraphs.append({
                    "folio": folio,
                    "sec": sec,
                    "lang": lang,
                    "hand": hand,
                    "p_idx": p_idx_by_folio[folio],
                    "star": cur_star,
                    "lines": cur_para_lines,
                })
                cur_para_lines = []
                cur_star = "N"

    if cur_para_lines and cur_folio:
        p_idx_by_folio[cur_folio] += 1
        prose_paragraphs.append({
            "folio": cur_folio,
            "sec": cur_sec,
            "lang": cur_lang,
            "hand": cur_hand,
            "p_idx": p_idx_by_folio[cur_folio],
            "star": cur_star,
            "lines": cur_para_lines,
        })

    return prose_paragraphs


def main():
    random.seed(42)
    prose_paragraphs = parse_manuscript()

    # Compute global canonical & root frequencies across all prose
    global_canon_counts = Counter()
    global_root_counts = Counter()

    for p in prose_paragraphs:
        flat = [t for line in p["lines"] for t in line]
        p["flat_tokens"] = flat
        p["first_line_tokens"] = p["lines"][0] if p["lines"] else []
        p["last_line_tokens"] = p["lines"][-1] if p["lines"] else []
        for t in flat:
            global_canon_counts[t["canon"]] += 1
            global_root_counts[t["core_root"]] += 1

    # Precompute per-paragraph sets of rare canons and rare roots
    for p in prose_paragraphs:
        p["canons_all"] = {t["canon"] for t in p["flat_tokens"] if len(t["canon"]) >= 3}
        p["canons_rare_50"] = {c for c in p["canons_all"] if global_canon_counts[c] <= 50}
        p["canons_rare_25"] = {c for c in p["canons_all"] if global_canon_counts[c] <= 25}
        p["canons_rare_10"] = {c for c in p["canons_all"] if global_canon_counts[c] <= 10}
        p["roots_all"] = {t["core_root"] for t in p["flat_tokens"] if len(t["core_root"]) >= 2}
        p["roots_rare_50"] = {r for r in p["roots_all"] if global_root_counts[r] <= 50}
        p["first_line_canons_50"] = {t["canon"] for t in p["first_line_tokens"] if len(t["canon"]) >= 3 and global_canon_counts[t["canon"]] <= 50}
        p["last_line_canons_50"] = {t["canon"] for t in p["last_line_tokens"] if len(t["canon"]) >= 3 and global_canon_counts[t["canon"]] <= 50}
        p["first_line_roots_50"] = {t["core_root"] for t in p["first_line_tokens"] if len(t["core_root"]) >= 2 and global_root_counts[t["core_root"]] <= 50}
        p["last_line_roots_50"] = {t["core_root"] for t in p["last_line_tokens"] if len(t["core_root"]) >= 2 and global_root_counts[t["core_root"]] <= 50}

    # Filter to Quire 20 Starred Recipes (`f103r..f116r`, 285 recipes across 23 folios)
    starred_paras = [p for p in prose_paragraphs if p["folio"].startswith(("f103", "f104", "f105", "f106", "f107", "f108", "f111", "f112", "f113", "f114", "f115", "f116")) and p["folio"] != "f116v"]
    print(f"Loaded {len(starred_paras)} Starred Recipe paragraphs across Quire 20 (f103r-f116r).")

    # =========================================================================
    # PART 1: Folio-by-Folio Marginal Star Sequences & Alternation Analysis
    # =========================================================================
    paras_by_folio = defaultdict(list)
    for p in starred_paras:
        paras_by_folio[p["folio"]].append(p)

    folio_star_sequences = {}
    for fol, plist in paras_by_folio.items():
        seq = [p["star"] for p in plist]
        counts = dict(Counter(seq))
        # Count transitions (same star vs switch star)
        switches = sum(1 for i in range(len(seq) - 1) if seq[i] != seq[i + 1])
        folio_star_sequences[fol] = {
            "recipe_count": len(plist),
            "star_sequence": " ".join(seq),
            "star_counts": counts,
            "adjacent_switches": switches,
            "switch_rate": round(switches / (len(seq) - 1), 3) if len(seq) > 1 else 0.0,
        }

    # =========================================================================
    # PART 2: 5,000-Trial Within-Folio Permutation Test of Consecutive Recipe Chaining (`P_i -> P_{i+1}`)
    # =========================================================================
    # Test whether adjacent paragraphs `(P_i, P_{i+1})` on the same folio share more rare canons,
    # rare roots, and boundary echoes (`last_line(P_i) <-> first_line(P_{i+1})`) than random within-folio orderings!
    def compute_chaining_metrics(folio_dict):
        shared_canon_25 = 0
        shared_canon_50 = 0
        shared_root_50 = 0
        boundary_canon_50 = 0
        boundary_root_50 = 0
        same_opener_root = 0
        same_closer_suffix = 0
        jaccard_sum = 0.0
        n_adj = 0

        for fol, plist in folio_dict.items():
            for i in range(len(plist) - 1):
                pa, pb = plist[i], plist[i + 1]
                n_adj += 1
                shared_canon_25 += len(pa["canons_rare_25"] & pb["canons_rare_25"])
                shared_canon_50 += len(pa["canons_rare_50"] & pb["canons_rare_50"])
                shared_root_50 += len(pa["roots_rare_50"] & pb["roots_rare_50"])
                boundary_canon_50 += len(pa["last_line_canons_50"] & pb["first_line_canons_50"])
                boundary_root_50 += len(pa["last_line_roots_50"] & pb["first_line_roots_50"])
                if pa["flat_tokens"] and pb["flat_tokens"]:
                    if pa["flat_tokens"][0]["core_root"] == pb["flat_tokens"][0]["core_root"]:
                        same_opener_root += 1
                    if pa["flat_tokens"][-1]["suffix"] == pb["flat_tokens"][-1]["suffix"]:
                        same_closer_suffix += 1
                union_c = len(pa["canons_all"] | pb["canons_all"])
                if union_c > 0:
                    jaccard_sum += len(pa["canons_all"] & pb["canons_all"]) / union_c

        return {
            "adjacent_pairs": n_adj,
            "shared_rare_25_canons": shared_canon_25,
            "shared_rare_50_canons": shared_canon_50,
            "shared_rare_50_roots": shared_root_50,
            "boundary_echo_canons_50": boundary_canon_50,
            "boundary_echo_roots_50": boundary_root_50,
            "same_opener_root": same_opener_root,
            "same_closer_suffix": same_closer_suffix,
            "mean_jaccard": round(jaccard_sum / n_adj, 5) if n_adj else 0.0,
        }

    obs_chaining = compute_chaining_metrics(paras_by_folio)

    n_trials = 5000
    metric_keys = [
        "shared_rare_25_canons",
        "shared_rare_50_canons",
        "shared_rare_50_roots",
        "boundary_echo_canons_50",
        "boundary_echo_roots_50",
        "same_opener_root",
        "same_closer_suffix",
        "mean_jaccard",
    ]
    null_vals = {k: [] for k in metric_keys}

    for _ in range(n_trials):
        shuf_dict = {}
        for fol, plist in paras_by_folio.items():
            cp = list(plist)
            random.shuffle(cp)
            shuf_dict[fol] = cp
        m = compute_chaining_metrics(shuf_dict)
        for k in metric_keys:
            null_vals[k].append(m[k])

    chaining_permutation_results = {}
    for k in metric_keys:
        arr = null_vals[k]
        mean_v = sum(arr) / len(arr)
        std_v = math.sqrt(sum((x - mean_v) ** 2 for x in arr) / len(arr)) or 1e-9
        obs_v = obs_chaining[k]
        z = (obs_v - mean_v) / std_v
        p_val = sum(1 for x in arr if x >= obs_v) / len(arr)
        chaining_permutation_results[k] = {
            "observed": obs_v,
            "expected_mean": round(mean_v, 4),
            "expected_std": round(std_v, 4),
            "enrichment_ratio": round(obs_v / mean_v, 3) if mean_v > 0 else None,
            "z_score": round(z, 2),
            "p_value": round(p_val, 4),
        }

    # Catalog the exact consecutive recipe pairs `(P_i, P_{i+1})` with the strongest rare-stem chaining or boundary echoes!
    chained_recipe_pairs = []
    for fol, plist in paras_by_folio.items():
        for i in range(len(plist) - 1):
            pa, pb = plist[i], plist[i + 1]
            shared_25 = sorted(pa["canons_rare_25"] & pb["canons_rare_25"], key=lambda c: global_canon_counts[c])
            shared_50 = sorted(pa["canons_rare_50"] & pb["canons_rare_50"], key=lambda c: global_canon_counts[c])
            b_echo_c = sorted(pa["last_line_canons_50"] & pb["first_line_canons_50"], key=lambda c: global_canon_counts[c])
            b_echo_r = sorted(pa["last_line_roots_50"] & pb["first_line_roots_50"], key=lambda r: global_root_counts[r])

            if shared_25 or b_echo_c or len(shared_50) >= 2:
                # Find the exact surface loci of the shared rare canons
                loci_details = []
                for sc in (shared_25 or shared_50)[:4]:
                    ta = [f"{t['loc']}:{t['surface']}" for t in pa["flat_tokens"] if t["canon"] == sc][0]
                    tb = [f"{t['loc']}:{t['surface']}" for t in pb["flat_tokens"] if t["canon"] == sc][0]
                    loci_details.append(f"{sc}(cnt={global_canon_counts[sc]}): {ta} -> {tb}")

                chained_recipe_pairs.append({
                    "folio": fol,
                    "pair": f"P{pa['p_idx']}({pa['star']}) -> P{pb['p_idx']}({pb['star']})",
                    "shared_rare_25_canons": [f"{c}(cnt={global_canon_counts[c]})" for c in shared_25],
                    "shared_rare_50_canons": [f"{c}(cnt={global_canon_counts[c]})" for c in shared_50],
                    "boundary_echo_canons_50": [f"{c}(cnt={global_canon_counts[c]})" for c in b_echo_c],
                    "boundary_echo_roots_50": [f"{r}(cnt={global_root_counts[r]})" for r in b_echo_r],
                    "loci_details": loci_details,
                    "pa_opener": pa["flat_tokens"][0]["surface"] if pa["flat_tokens"] else "",
                    "pb_opener": pb["flat_tokens"][0]["surface"] if pb["flat_tokens"] else "",
                })

    chained_recipe_pairs.sort(key=lambda x: (len(x["boundary_echo_canons_50"]), len(x["shared_rare_25_canons"]), len(x["shared_rare_50_canons"])), reverse=True)

    # =========================================================================
    # PART 3: Same-Star Repeat Pairs (`L. -> L.` / `L -> L`) vs. Alternating (`L. <-> L`) on the 20 Non-`D` Folios
    # & Actual `D`-Headed Recipe Groups on `f103r`, `f104r`, `f108r`
    # =========================================================================
    same_star_pairs_non_d = []
    alt_star_pairs_non_d = []
    for fol, plist in paras_by_folio.items():
        if fol in ("f103r", "f104r", "f108r"):
            continue
        for i in range(len(plist) - 1):
            pa, pb = plist[i], plist[i + 1]
            if pa["star"] not in ("L", "L.") or pb["star"] not in ("L", "L."):
                continue
            s25 = len(pa["canons_rare_25"] & pb["canons_rare_25"])
            s50 = len(pa["canons_rare_50"] & pb["canons_rare_50"])
            becho = len(pa["last_line_canons_50"] & pb["first_line_canons_50"])
            uc = len(pa["canons_all"] | pb["canons_all"])
            jacc = len(pa["canons_all"] & pb["canons_all"]) / uc if uc else 0.0
            rec = {
                "folio": fol,
                "pair": f"P{pa['p_idx']}({pa['star']})->P{pb['p_idx']}({pb['star']})",
                "s25": s25,
                "s50": s50,
                "becho": becho,
                "jacc": jacc,
                "shared_25_list": sorted(pa["canons_rare_25"] & pb["canons_rare_25"]),
            }
            if pa["star"] == pb["star"]:
                same_star_pairs_non_d.append(rec)
            else:
                alt_star_pairs_non_d.append(rec)

    def summarize_pair_group(g):
        n = len(g)
        if n == 0:
            return {}
        return {
            "pair_count": n,
            "mean_shared_rare_25": round(sum(x["s25"] for x in g) / n, 4),
            "mean_shared_rare_50": round(sum(x["s50"] for x in g) / n, 4),
            "boundary_echo_rate": round(100.0 * sum(1 for x in g if x["becho"] > 0) / n, 2),
            "mean_jaccard": round(sum(x["jacc"] for x in g) / n, 5),
        }

    non_d_alternation_vs_repeat = {
        "same_star_repeat_pairs": summarize_pair_group(same_star_pairs_non_d),
        "alternating_star_pairs": summarize_pair_group(alt_star_pairs_non_d),
        "same_star_repeat_details": same_star_pairs_non_d,
    }

    # Segment `f103r`, `f104r`, `f108r` by actual `D` (Dark Crimson) star headers!
    d_headed_groups = []
    d_slot_buckets = {"Slot_1_D_Header": [], "Slot_2_First_L_After_D": [], "Slot_3_Second_L_After_D": []}

    for fol in ("f103r", "f104r", "f108r"):
        plist = paras_by_folio[fol]
        cur_group = []
        for p in plist:
            if p["star"] == "D":
                if cur_group and cur_group[0]["star"] == "D":
                    d_headed_groups.append((fol, cur_group))
                cur_group = [p]
            else:
                if cur_group and cur_group[0]["star"] == "D":
                    cur_group.append(p)
        if cur_group and cur_group[0]["star"] == "D":
            d_headed_groups.append((fol, cur_group))

    f103r_triads = []
    for g_idx, (fol, grp) in enumerate(d_headed_groups, 1):
        d_slot_buckets["Slot_1_D_Header"].append(grp[0])
        if len(grp) >= 2:
            d_slot_buckets["Slot_2_First_L_After_D"].append(grp[1])
        if len(grp) >= 3:
            for sub_p in grp[2:]:
                d_slot_buckets["Slot_3_Second_L_After_D"].append(sub_p)

        shared_50_in_grp = set()
        for a_i in range(len(grp)):
            for b_i in range(a_i + 1, len(grp)):
                shared_50_in_grp |= (grp[a_i]["canons_rare_50"] & grp[b_i]["canons_rare_50"])

        f103r_triads.append({
            "group_index": g_idx,
            "folio": fol,
            "pattern": " ".join(p["star"] for p in grp),
            "recipes": [
                {
                    "p_idx": p["p_idx"],
                    "star": p["star"],
                    "n_lines": len(p["lines"]),
                    "n_words": len(p["flat_tokens"]),
                    "opener_w0": p["flat_tokens"][0]["surface"],
                    "opener_w1": p["flat_tokens"][1]["surface"] if len(p["flat_tokens"]) > 1 else "",
                    "closer_w_last": p["flat_tokens"][-1]["surface"],
                    "closer_suffix": p["flat_tokens"][-1]["suffix"],
                }
                for p in grp
            ],
            "shared_rare_50_canons_in_group": sorted(shared_50_in_grp),
        })

    f103r_slot_summary = {}
    for label, plist in d_slot_buckets.items():
        if not plist:
            continue
        f103r_slot_summary[label] = {
            "count": len(plist),
            "mean_words": round(sum(len(p["flat_tokens"]) for p in plist) / len(plist), 2),
            "mean_lines": round(sum(len(p["lines"]) for p in plist) / len(plist), 2),
            "openers": [f"{p['folio']}.P{p['p_idx']}:{p['flat_tokens'][0]['surface']}" for p in plist],
            "closers": [f"{p['folio']}.P{p['p_idx']}:{p['flat_tokens'][-1]['surface']}" for p in plist],
            "closer_in_rate": round(100.0 * sum(1 for p in plist if p["flat_tokens"][-1]["suffix"] in ("-ain", "-in")) / len(plist), 1),
        }

    # =========================================================================
    # PART 4: Recipe Opener (`w_0`) Taxonomy Across All 285 Starred Recipes
    # =========================================================================
    opener_class_counts = Counter()
    opener_roots = Counter()
    opener_surfaces = Counter()
    opener_by_star = {"D": Counter(), "L": Counter(), "L.": Counter()}

    for p in starred_paras:
        if not p["flat_tokens"]:
            continue
        w0 = p["flat_tokens"][0]
        surf = w0["surface"]
        opener_surfaces[surf] += 1
        opener_roots[w0["core_root"]] += 1

        if surf.startswith("p"):
            ocl = "p- (Top-Line Gallows)"
        elif surf.startswith("f"):
            ocl = "f- (Top-Line Gallows)"
        elif surf.startswith("t"):
            ocl = "t- (Gallows)"
        elif surf.startswith("k"):
            ocl = "k- (Gallows)"
        elif surf.startswith("q"):
            ocl = "q- (Proclitic)"
        elif surf.startswith("d"):
            ocl = "d- (Dental)"
        elif surf.startswith("s"):
            ocl = "s- (Sibilant)"
        elif surf.startswith("o"):
            ocl = "o- (Nominal)"
        elif surf.startswith("y"):
            ocl = "y- (Line-Initial)"
        elif surf.startswith(("ch", "sh")):
            ocl = "ch-/sh- (Bench)"
        else:
            ocl = "Other"

        opener_class_counts[ocl] += 1
        if p["star"] in opener_by_star:
            opener_by_star[p["star"]][ocl] += 1

    opener_taxonomy = {
        "class_distribution": {
            k: {"count": v, "pct": round(100.0 * v / len(starred_paras), 2)}
            for k, v in opener_class_counts.most_common()
        },
        "top_20_opener_roots": [
            {"root": k, "count": v, "pct": round(100.0 * v / len(starred_paras), 2)}
            for k, v in opener_roots.most_common(20)
        ],
        "top_20_opener_surfaces": [
            {"surface": k, "count": v}
            for k, v in opener_surfaces.most_common(20)
        ],
        "class_pct_by_star": {
            st: {k: round(100.0 * v / sum(c.values()), 2) for k, v in c.most_common()}
            for st, c in opener_by_star.items() if sum(c.values()) > 0
        },
    }

    output = {
        "summary": {
            "total_starred_recipes": len(starred_paras),
            "total_folios": len(paras_by_folio),
            "total_adjacent_within_folio_pairs": obs_chaining["adjacent_pairs"],
        },
        "folio_star_sequences": folio_star_sequences,
        "within_folio_chaining_permutation_test": chaining_permutation_results,
        "non_d_alternation_vs_repeat": non_d_alternation_vs_repeat,
        "top_chained_consecutive_recipe_pairs": chained_recipe_pairs[:35],
        "d_headed_slot_summary": f103r_slot_summary,
        "d_headed_groups_detail": f103r_triads,
        "opener_taxonomy": opener_taxonomy,
    }

    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)

    print(f"\nSaved Attack 11 analysis to {OUT_JSON}")
    print("\n--- NON-D FOLIOS: SAME-STAR REPEAT PAIRS VS. ALTERNATING-STAR PAIRS ---")
    print(json.dumps({
        "same_star_repeat_pairs": non_d_alternation_vs_repeat["same_star_repeat_pairs"],
        "alternating_star_pairs": non_d_alternation_vs_repeat["alternating_star_pairs"],
    }, indent=2))
    print("Same-Star Repeat Pair Details:")
    for sr in non_d_alternation_vs_repeat["same_star_repeat_details"]:
        print(f"  {sr['folio']} {sr['pair']}: s25={sr['s25']} ({sr['shared_25_list']}), s50={sr['s50']}, becho={sr['becho']}, jacc={sr['jacc']:.4f}")

    print("\n--- D-HEADED GROUPS SLOT SUMMARY (f103r, f104r, f108r) ---")
    print(json.dumps(f103r_slot_summary, indent=2))

    print("\n--- OPENER TAXONOMY BY STAR CLASS ---")
    print(json.dumps(opener_taxonomy["class_pct_by_star"], indent=2))


if __name__ == "__main__":
    main()
