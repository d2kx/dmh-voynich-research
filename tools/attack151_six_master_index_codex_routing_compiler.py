#!/usr/bin/env python3
"""
Attack 151 (Phase 162 / Discovery 168):
Complete Six-Index-Folio Master Compiler & Full-Codex Cross-Reference Atlas
(f1r, f49v, f58r, f58v, f66r, f76r Routing All 220 Non-Index Folios).

Tests:
1. Across all 226 transcribed folios (6 Master Index Folios + 220 Non-Index Target
   Folios), computes the exact IDF-weighted Open-Class Stem Overlap (DF in 2..45
   folios) between each of the 6 Master Index Folios:
   - f1r  (Hand 1, Lang A, Opening Preface with =Pt Right-Justified Rubrics)
   - f49v (Hand 1, Lang A, 26-Glyph + Arabic Numeral 1..5 Margin-Keyed Herbal)
   - f58r (Hand 3, Quire H Unillustrated Starred Botanical-Apothecary Index I)
   - f58v (Hand 3, Quire H Unillustrated Starred Botanical-Apothecary Index II)
   - f66r (Hand 5, Lang B, Quire H 15-Word + 34-Key Dual-Margin Clinical Index)
   - f76r (Hand 2, Lang B, Quire M Unillustrated 9-Key Balneological Treatise)
   and all 220 Non-Index Target Folios across 8 Section/Language Strata:
   [H_A (Herbal-A), H_B (Herbal-B), A (Astronomical), Z (Zodiac), B (Balneological),
    C (Cosmological/Rosettes), P (Pharmaceutical), S (Starred Recipes)].
2. Quantifies Global Codex Index Coverage (% of the 220 target folios and % of
   target prose folios directly linked to >= 1 of the 6 Master Index Folios).
3. Tests the 3-Pole Domain-to-Index Specialization Law via 1,000-Trial Permutation:
   - Pole I   (f1r + f49v, Hand 1 Currier A): Supply-Side Currier A Herbals (H_A) & Pharma (P)
   - Pole II  (f58r + f58v, Hand 3 Quire H Starred Index): Astro/Zodiac/Cosmo (A, Z, C) & Starred Recipes (S)
   - Pole III (f66r + f76r, Hands 5 & 2 Currier B Treatises): Currier B Herbals (H_B) & Balneological (B)
   Using Row/Column-Normalized Pointwise Affiliation (or Z-normalized Pole Share)
   tested against 1,000 random permutations of target folio strata.
"""

from __future__ import annotations

import json
import math
import random
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, List, Set, Tuple

ROOT = Path(__file__).resolve().parents[1]
ZL_PATH = ROOT / "data" / "ZL3b-n.txt"
FOLIO_INDEX_PATH = ROOT / "data" / "folio_index.json"
OUT_JSON = ROOT / "data" / "attack151_six_master_index_codex_routing_compiler.json"

MASTER_SIX = ["f1r", "f49v", "f58r", "f58v", "f66r", "f76r"]

CLOSED_FUNCTORS = {
    "daiin", "ol", "chedy", "aiin", "shedy", "chol", "or", "ar", "chey", "qokeey",
    "qokedy", "dar", "shey", "qokeedy", "al", "dal", "dy", "chy", "okaiin", "qokaiin",
    "okain", "qokain", "otaiin", "qotaiin", "dair", "shol", "chor", "okal", "otal",
    "otar", "okar", "sal", "sar", "sol", "sor", "ral", "rar", "rol", "ror", "lar",
    "lol", "lor", "lain", "laiin", "raiin", "rain", "saiin", "sain", "dain", "oiin",
}


def clean_tok(t: str) -> str:
    t = re.sub(r"\[([^:\]]+):[^\]]+\]", r"\1", t)
    t = re.sub(r"\{[^}]*\}", "", t)
    t = re.sub(r"<[^>]*>", "", t)
    t = re.sub(r"[^a-zA-Z0-9]", "", t).lower()
    return t


def extract_stem(w: str) -> str:
    if not w or len(w) < 3 or w in CLOSED_FUNCTORS:
        return ""
    s = w
    for p in ["qok", "qot", "qop", "qof", "qo", "ch", "sh", "cth", "ckh", "cph", "cfh", "da", "ok", "ot", "op", "of", "ol", "or", "al", "ar", "yk", "yt", "yp", "yf", "d", "s", "y", "l", "r", "o"]:
        if s.startswith(p) and len(s) - len(p) >= 2:
            s = s[len(p):]
            break
    for suf in ["aiin", "oiin", "iin", "eedy", "edy", "ody", "ady", "dy", "ey", "oy", "ol", "al", "or", "ar", "am", "om", "an", "in", "y", "l", "r", "m", "n", "s"]:
        if s.endswith(suf) and len(s) - len(suf) >= 2:
            s = s[:-len(suf)]
            break
    return s


def main() -> None:
    index_raw = json.loads(FOLIO_INDEX_PATH.read_text(encoding="utf-8"))
    folios_meta = index_raw.get("folios", index_raw)

    line_re = re.compile(r"^<f([0-9]+[rv][0-9]*|Ros)\.([^,>]+),([^>]+)>\s+(.*)$")

    folio_all_tokens = defaultdict(list)
    folio_open_stems = defaultdict(set)
    stem_folios = defaultdict(set)

    for raw_line in ZL_PATH.read_text(encoding="utf-8", errors="ignore").splitlines():
        if not raw_line.startswith("<f"):
            continue
        m = line_re.match(raw_line)
        if not m:
            continue
        fol, line_id, loc, body = m.groups()
        if ";" in line_id:
            continue
        f_key = f"f{fol}"
        body_clean = re.sub(r"<![^>]*>", "", body)
        body_clean = re.sub(r"<[^>]*>", " ", body_clean)
        words = [clean_tok(t) for t in re.split(r"[.\s,]+", body_clean)]
        words = [w for w in words if w]
        if not words:
            continue
        folio_all_tokens[f_key].extend(words)
        for w in words:
            st = extract_stem(w)
            if len(st) >= 2:
                folio_open_stems[f_key].add(st)
                stem_folios[st].add(f_key)

    all_folios = sorted(folio_all_tokens.keys())
    n_folios_total = len(all_folios)

    # Open-class stems with DF in [2, 45]
    open_idf = {}
    for st, fset in stem_folios.items():
        df = len(fset)
        if 2 <= df <= 45:
            open_idf[st] = math.log2(n_folios_total / df)

    folio_filtered_stems = {
        f: {s for s in folio_open_stems[f] if s in open_idf}
        for f in all_folios
    }

    master_set = set(MASTER_SIX)
    target_folios = [f for f in all_folios if f not in master_set]

    def get_stratum(f: str) -> str:
        meta = folios_meta.get(f, {})
        sec = meta.get("section_code", meta.get("section", "H"))
        lang = meta.get("currier_lang", meta.get("currier_language", "A"))
        if sec == "H":
            return "H_B" if lang == "B" else "H_A"
        if sec in {"C", "T"} or f == "fRos":
            return "C_T"
        return sec

    # Compute shared IDF between every target folio and each of the 6 Master Index Folios
    target_routing = []
    linked_target_count = 0
    master_win_counts = Counter()
    stratum_master_idf_sum = defaultdict(lambda: Counter())
    stratum_folio_counts = Counter()

    for tf in target_folios:
        tstems = folio_filtered_stems[tf]
        strat = get_stratum(tf)
        stratum_folio_counts[strat] += 1
        scores = {}
        shared_lists = {}
        for mf in MASTER_SIX:
            inter = tstems & folio_filtered_stems[mf]
            idf_val = sum(open_idf[s] for s in inter)
            scores[mf] = round(idf_val, 3)
            shared_lists[mf] = sorted(inter, key=lambda x: -open_idf[x])
            stratum_master_idf_sum[strat][mf] += idf_val

        best_mf = max(MASTER_SIX, key=lambda m: scores[m])
        best_score = scores[best_mf]
        if best_score > 0:
            linked_target_count += 1
            master_win_counts[best_mf] += 1
        else:
            master_win_counts["UNLINKED"] += 1

        target_routing.append({
            "folio": tf,
            "stratum": strat,
            "total_words": len(folio_all_tokens[tf]),
            "open_stems": len(tstems),
            "primary_master_index": best_mf if best_score > 0 else "NONE",
            "primary_shared_idf": best_score,
            "primary_shared_stems": shared_lists[best_mf][:6] if best_score > 0 else [],
            "all_6_index_idf_scores": scores,
        })

    # Mean shared IDF matrix: 8 Strata × 6 Master Index Folios
    strata_order = ["H_A", "H_B", "A", "Z", "B", "C_T", "P", "S"]
    stratum_mean_idf_matrix = {}
    for st in strata_order:
        cnt = stratum_folio_counts[st]
        if cnt == 0:
            continue
        row = {mf: round(stratum_master_idf_sum[st][mf] / cnt, 3) for mf in MASTER_SIX}
        best_m = max(MASTER_SIX, key=lambda m: row[m])
        stratum_mean_idf_matrix[st] = {
            "n_folios": cnt,
            "top_governing_master_index": best_m,
            "mean_shared_idf_by_master": row,
        }

    # Test 3-Pole Domain-to-Index Specialization Law via 1,000-Trial Target-Folio Permutation:
    # For each target folio, standardize its 3 Pole Scores by the Pole's global mean so size differences
    # between Poles are equalized:
    #   Pole_A_H1 = f1r + f49v   <--> Target Domain A: {H_A, P}
    #   Pole_S_H3 = f58r + f58v  <--> Target Domain S: {A, Z, C_T, S}
    #   Pole_B_H25 = f66r + f76r <--> Target Domain B: {H_B, B}
    pole_defs = {
        "POLE_1_H1_CURRIER_A (f1r+f49v)": (["f1r", "f49v"], {"H_A", "P"}),
        "POLE_2_H3_STARRED_INDEX (f58r+f58v)": (["f58r", "f58v"], {"A", "Z", "C_T", "S"}),
        "POLE_3_H25_CLINICAL_B (f66r+f76r)": (["f66r", "f76r"], {"H_B", "B"}),
    }
    pole_keys = list(pole_defs.keys())

    # Compute raw pole score per target folio
    folio_pole_raw = []
    pole_global_sums = Counter()
    for tr in target_routing:
        sc = tr["all_6_index_idf_scores"]
        p_scores = {}
        for pk, (mfs, _) in pole_defs.items():
            val = sum(sc[m] for m in mfs)
            p_scores[pk] = val
            pole_global_sums[pk] += val
        folio_pole_raw.append((tr["stratum"], p_scores))

    # Normalized pole affinity for each folio: p_scores[pk] / pole_global_mean[pk]
    pole_means = {pk: pole_global_sums[pk] / len(target_routing) for pk in pole_keys}
    folio_norm_vec = []
    strata_labels = []
    for strat, p_scores in folio_pole_raw:
        strata_labels.append(strat)
        folio_norm_vec.append({pk: p_scores[pk] / max(pole_means[pk], 1e-6) for pk in pole_keys})

    def compute_diagonal_trace(s_labels: List[str]) -> float:
        tot = 0.0
        for idx, st in enumerate(s_labels):
            nv = folio_norm_vec[idx]
            for pk, (_, dom_set) in pole_defs.items():
                if st in dom_set:
                    tot += nv[pk]
        return tot / len(s_labels)

    obs_trace = compute_diagonal_trace(strata_labels)
    rng = random.Random(151)
    null_traces = []
    for _ in range(1000):
        shuf = list(strata_labels)
        rng.shuffle(shuf)
        null_traces.append(compute_diagonal_trace(shuf))

    mu_tr = sum(null_traces) / len(null_traces)
    sd_tr = math.sqrt(sum((x - mu_tr) ** 2 for x in null_traces) / len(null_traces))
    z_tr = (obs_trace - mu_tr) / (sd_tr if sd_tr > 0 else 1.0)

    # Top-5 Target Folios routed by each of the 6 Master Index Folios
    top_targets_per_master = {}
    for mf in MASTER_SIX:
        ranked = sorted(
            target_routing,
            key=lambda r: -r["all_6_index_idf_scores"][mf],
        )[:8]
        top_targets_per_master[mf] = [
            {
                "target_folio": r["folio"],
                "stratum": r["stratum"],
                "shared_idf": r["all_6_index_idf_scores"][mf],
                "shared_stems": sorted(
                    folio_filtered_stems[r["folio"]] & folio_filtered_stems[mf],
                    key=lambda x: -open_idf[x],
                )[:6],
            }
            for r in ranked
        ]

    out = {
        "attack": 151,
        "phase": 162,
        "discovery": 168,
        "title": "Complete Six-Index-Folio Master Compiler & Full-Codex Cross-Reference Atlas (f1r, f49v, f58r, f58v, f66r, f76r Routing All 220 Non-Index Folios)",
        "overview": {
            "total_codex_folios": n_folios_total,
            "master_index_folios": MASTER_SIX,
            "non_index_target_folios": len(target_folios),
            "target_folios_linked_to_ge1_master_index": linked_target_count,
            "target_folio_coverage_pct": round(100.0 * linked_target_count / len(target_folios), 2),
            "primary_master_index_win_counts": dict(master_win_counts),
            "three_pole_domain_routing_permutation_test_1000": {
                "observed_normalized_diagonal_affinity": round(obs_trace, 4),
                "null_mean": round(mu_tr, 4),
                "null_sd": round(sd_tr, 4),
                "lift_ratio": round(obs_trace / max(mu_tr, 1e-6), 3),
                "z_score": round(z_tr, 2),
            },
        },
        "stratum_by_master_mean_idf_matrix": stratum_mean_idf_matrix,
        "top_routed_targets_per_master_index": top_targets_per_master,
        "sample_target_folio_routing_records": target_routing[:30],
    }

    OUT_JSON.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"[Attack 151] Saved {OUT_JSON}")
    print("Overview:", json.dumps(out["overview"], indent=2))
    print("Stratum × Master Mean IDF Matrix:", json.dumps(stratum_mean_idf_matrix, indent=2))


if __name__ == "__main__":
    main()
