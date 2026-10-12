#!/usr/bin/env python3
"""
Attack 217 (Discovery 234): 100% Quire 20 Visual & Structural Completion (f105v, f112r/v, f114r, f115v),
12-Leaf Recto-Verso Mirroring, and 6-Bifolium Architecture across f103r-f116v.
"""

import json
import math
import os
import random
import re
from collections import Counter, defaultdict

def normalize_word(w: str) -> str:
    w = re.sub(r"\[([^:\]]+):[^\]]+\]", r"\1", w)
    w = re.sub(r"\{[^}]*\}", "", w)
    w = w.replace("<->", "").replace("!", "").replace("*", "").replace("%", "").replace("$", "")
    w = re.sub(r"[^a-zA-Z0-9']", "", w)
    return w.strip().lower()

def canonical_stem(w: str) -> str:
    s = w
    if s.startswith("qo") and len(s) > 3:
        s = s[2:]
    elif s.startswith("q") and len(s) > 2:
        s = s[1:]
    s = re.sub(r"^p", "t", s)
    s = re.sub(r"^f", "k", s)
    s = re.sub(r"^cph", "cth", s)
    s = re.sub(r"^cfh", "ckh", s)
    s = s.replace("iin", "N").replace("in", "n")
    for suf in ["edy", "ody", "ey", "dy", "y", "aN", "oN", "eN", "N", "ar", "or", "al", "ol", "am", "om", "an", "on"]:
        if s.endswith(suf) and len(s) - len(suf) >= 2:
            s = s[:-len(suf)]
            break
    return s

def parse_quire20(zl_path: str):
    q20_folios = [
        "f103r", "f103v", "f104r", "f104v", "f105r", "f105v",
        "f106r", "f106v", "f107r", "f107v", "f108r", "f108v",
        "f111r", "f111v", "f112r", "f112v", "f113r", "f113v",
        "f114r", "f114v", "f115r", "f115v", "f116r", "f116v"
    ]
    q20_set = set(q20_folios)
    folio_words = defaultdict(list)
    folio_recipes = defaultdict(list)
    folio_meta = {}
    current_folio = None
    current_recipe = None

    with open(zl_path, "r", encoding="utf-8", errors="ignore") as f:
        for raw in f:
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            m_fol = re.match(r"^<(f\d+[rv]\d*)>\s*(.*)$", line)
            if m_fol:
                current_folio = m_fol.group(1)
                hdr = m_fol.group(2)
                if current_folio in q20_set:
                    meta = {}
                    for k, v in re.findall(r"\$([A-Z])=([A-Za-z0-9]+)", hdr):
                        meta[k] = v
                    folio_meta[current_folio] = meta
                current_recipe = None
                continue
            m_loc = re.match(r"^<(f\d+[rv]\d*)\.([^>]+)>\s+(.*)$", line)
            if not m_loc:
                continue
            fol, loc, body = m_loc.group(1), m_loc.group(2), m_loc.group(3)
            if fol not in q20_set:
                continue
            has_star = "<%>" in body or "@P0" in loc or "+P0" in loc
            clean_body = re.sub(r"<[^>]*>", " ", body)
            tokens = [normalize_word(t) for t in re.split(r"[.\s,]+", clean_body)]
            tokens = [t for t in tokens if t]
            if not tokens:
                continue
            folio_words[fol].extend(tokens)
            if "<%>" in body or current_recipe is None:
                if current_recipe is not None:
                    folio_recipes[fol].append(current_recipe)
                current_recipe = {"loc": f"{fol}.{loc}", "words": list(tokens)}
            else:
                current_recipe["words"].extend(tokens)

    for fol in q20_folios:
        if current_recipe and current_recipe["loc"].startswith(fol + "."):
            folio_recipes[fol].append(current_recipe)
            current_recipe = None
    return q20_folios, folio_words, folio_recipes, folio_meta

def jaccard(s1: set, s2: set) -> float:
    if not s1 or not s2:
        return 0.0
    return len(s1 & s2) / len(s1 | s2)

def token_coverage(target_words, source_stems: set) -> float:
    if not target_words:
        return 0.0
    hits = sum(1 for w in target_words if canonical_stem(w) in source_stems)
    return hits / len(target_words)

def main():
    zl_path = os.path.join("data", "ZL3b-n.txt")
    idx_path = os.path.join("data", "folio_index.json")
    with open(idx_path, "r", encoding="utf-8") as f:
        idx_data = json.load(f)["folios"]

    q20_folios, folio_words, folio_recipes, folio_meta = parse_quire20(zl_path)

    # 1. Verify 24/24 Quire 20 visual scan completion (+ all 25 section_code=='S' folios)
    pages_files = os.listdir("pages")
    s_section_folios = [k for k, v in idx_data.items() if v.get("section_code") == "S"]
    all_target_folios = sorted(set(q20_folios) | set(s_section_folios), key=lambda x: (int(re.findall(r"\d+", x)[0]), x))
    scan_coverage = {}
    for fol in all_target_folios:
        matching_pngs = [p for p in pages_files if p.startswith(fol + "_") and p.endswith(".png")]
        scan_coverage[fol] = {
            "rendered": len(matching_pngs) > 0,
            "files": sorted(matching_pngs),
            "words": len(folio_words.get(fol, [])),
            "recipes": len(folio_recipes.get(fol, [])),
            "meta": folio_meta.get(fol, {})
        }

    # 2. Detailed profile of the 5 newly rendered Quire 20 pages
    new_five = ["f105v", "f112r", "f112v", "f114r", "f115v"]
    new_five_profiles = {}
    for fol in new_five:
        words = folio_words[fol]
        stems = [canonical_stem(w) for w in words]
        recipes = folio_recipes[fol]
        openers = [r["words"][0] for r in recipes if r["words"]]
        new_five_profiles[fol] = {
            "words": len(words),
            "unique_words": len(set(words)),
            "unique_stems": len(set(stems)),
            "recipes": len(recipes),
            "mean_words_per_recipe": round(len(words) / max(1, len(recipes)), 2),
            "recipe_openers": openers,
            "q_initial_rate_pct": round(100.0 * sum(1 for w in words if w.startswith("q")) / len(words), 2),
            "edy_rate_pct": round(100.0 * sum(1 for w in words if w.endswith("edy")) / len(words), 2),
            "aiin_rate_pct": round(100.0 * sum(1 for w in words if w.endswith("aiin")) / len(words), 2),
            "top_words": Counter(words).most_common(10),
            "top_stems": Counter(stems).most_common(10)
        }

    # 3. 12-Leaf Same-Leaf Recto-Verso Coupling across Quire 20 (f103..f108, f111..f115 + f116r)
    leaves = ["f103", "f104", "f105", "f106", "f107", "f108", "f111", "f112", "f113", "f114", "f115"]
    same_leaf_results = []
    for lf in leaves:
        r_fol, v_fol = lf + "r", lf + "v"
        r_words, v_words = folio_words[r_fol], folio_words[v_fol]
        r_stems, v_stems = set(canonical_stem(w) for w in r_words), set(canonical_stem(w) for w in v_words)
        jac = jaccard(r_stems, v_stems)
        r_to_v_cov = token_coverage(v_words, r_stems)
        v_to_r_cov = token_coverage(r_words, v_stems)
        shared_exact = sorted(set(r_words) & set(v_words))
        same_leaf_results.append({
            "leaf": lf,
            "recto_words": len(r_words),
            "verso_words": len(v_words),
            "recto_recipes": len(folio_recipes[r_fol]),
            "verso_recipes": len(folio_recipes[v_fol]),
            "stem_jaccard": round(jac, 4),
            "recto_seeds_verso_token_pct": round(100.0 * r_to_v_cov, 2),
            "verso_seeds_recto_token_pct": round(100.0 * v_to_r_cov, 2),
            "shared_exact_word_types": len(shared_exact),
            "sample_shared_words": [w for w in shared_exact if len(w) >= 5][:12]
        })

    # 4. 6 Surviving Bifolia Conjugate Architecture (Bif 1..6: f103<->f116, f104<->f115, f105<->f114, f106<->f113, f107<->f112, f108<->f111)
    bifolia = [
        ("Bif_1_outer", "f103", "f116"),
        ("Bif_2", "f104", "f115"),
        ("Bif_3", "f105", "f114"),
        ("Bif_4", "f106", "f113"),
        ("Bif_5", "f107", "f112"),
        ("Bif_6_inner", "f108", "f111"),
    ]
    bifolium_results = []
    for bname, lf_a, lf_b in bifolia:
        a_words = folio_words[lf_a + "r"] + folio_words[lf_a + "v"]
        b_words = folio_words[lf_b + "r"] + folio_words[lf_b + "v"]
        a_stems = set(canonical_stem(w) for w in a_words)
        b_stems = set(canonical_stem(w) for w in b_words)
        jac = jaccard(a_stems, b_stems)
        a_to_b = token_coverage(b_words, a_stems)
        b_to_a = token_coverage(a_words, b_stems)
        bifolium_results.append({
            "bifolium": bname,
            "left_leaf": lf_a,
            "right_leaf": lf_b,
            "left_words": len(a_words),
            "right_words": len(b_words),
            "stem_jaccard": round(jac, 4),
            "left_seeds_right_token_pct": round(100.0 * a_to_b, 2),
            "right_seeds_left_token_pct": round(100.0 * b_to_a, 2),
            "shared_stems_count": len(a_stems & b_stems)
        })

    # Specific sheet-side conjugate pairs for the newly rendered pages:
    # f105v <-> f114r (same side of Bifolium #3!), f107v <-> f112r, f107r <-> f112v, f104r <-> f115v
    sheet_side_pairs = [
        ("Bif3_inner_sheet_f105v_f114r", "f105v", "f114r"),
        ("Bif3_outer_sheet_f105r_f114v", "f105r", "f114v"),
        ("Bif5_inner_sheet_f107v_f112r", "f107v", "f112r"),
        ("Bif5_outer_sheet_f107r_f112v", "f107r", "f112v"),
        ("Bif2_outer_sheet_f104r_f115v", "f104r", "f115v"),
        ("Bif6_centerfold_gap_f108v_f111r", "f108v", "f111r"),
    ]
    sheet_side_results = []
    for pname, fa, fb in sheet_side_pairs:
        wa, wb = folio_words[fa], folio_words[fb]
        sa, sb = set(canonical_stem(w) for w in wa), set(canonical_stem(w) for w in wb)
        sheet_side_results.append({
            "pair": pname,
            "folio_a": fa,
            "folio_b": fb,
            "stem_jaccard": round(jaccard(sa, sb), 4),
            "a_seeds_b_pct": round(100.0 * token_coverage(wb, sa), 2),
            "b_seeds_a_pct": round(100.0 * token_coverage(wa, sb), 2),
            "shared_exact_words": sorted(list(set(wa) & set(wb)))[:15]
        })

    # 5. First-Half (f103r-f108v) vs Second-Half (f111r-f116r) across the Missing Bifolium #7 (f109-f110)
    first_half = ["f103r", "f103v", "f104r", "f104v", "f105r", "f105v", "f106r", "f106v", "f107r", "f107v", "f108r", "f108v"]
    second_half = ["f111r", "f111v", "f112r", "f112v", "f113r", "f113v", "f114r", "f114v", "f115r", "f115v", "f116r"]
    fh_words = [w for f in first_half for w in folio_words[f]]
    sh_words = [w for f in second_half for w in folio_words[f]]
    fh_recipes = [r for f in first_half for r in folio_recipes[f]]
    sh_recipes = [r for f in second_half for r in folio_recipes[f]]
    fh_stems = set(canonical_stem(w) for w in fh_words)
    sh_stems = set(canonical_stem(w) for w in sh_words)

    half_comparison = {
        "first_half_pages": len(first_half),
        "second_half_pages": len(second_half),
        "first_half_words": len(fh_words),
        "second_half_words": len(sh_words),
        "first_half_recipes": len(fh_recipes),
        "second_half_recipes": len(sh_recipes),
        "first_half_words_per_recipe": round(len(fh_words) / len(fh_recipes), 2),
        "second_half_words_per_recipe": round(len(sh_words) / len(sh_recipes), 2),
        "first_half_seeds_second_half_token_pct": round(100.0 * token_coverage(sh_words, fh_stems), 2),
        "second_half_seeds_first_half_token_pct": round(100.0 * token_coverage(fh_words, sh_stems), 2),
        "stem_jaccard_halves": round(jaccard(fh_stems, sh_stems), 4),
        "first_half_q_pct": round(100.0 * sum(1 for w in fh_words if w.startswith("q")) / len(fh_words), 2),
        "second_half_q_pct": round(100.0 * sum(1 for w in sh_words if w.startswith("q")) / len(sh_words), 2),
        "first_half_edy_pct": round(100.0 * sum(1 for w in fh_words if w.endswith("edy")) / len(fh_words), 2),
        "second_half_edy_pct": round(100.0 * sum(1 for w in sh_words if w.endswith("edy")) / len(sh_words), 2),
    }

    # 6. Test Same-Leaf Recto-Verso vs Random Non-Same-Leaf Pairs in Quire 20 (Permutation Test)
    recipe_folios_22 = [lf + s for lf in leaves for s in ["r", "v"]]
    folio_stem_sets = {f: set(canonical_stem(w) for w in folio_words[f]) for f in recipe_folios_22}
    obs_same_leaf_jac = sum(r["stem_jaccard"] for r in same_leaf_results) / len(same_leaf_results)
    all_other_jacs = []
    for i, fa in enumerate(recipe_folios_22):
        for j, fb in enumerate(recipe_folios_22):
            if i < j and fa[:-1] != fb[:-1]:
                all_other_jacs.append(jaccard(folio_stem_sets[fa], folio_stem_sets[fb]))
    mean_other_jac = sum(all_other_jacs) / len(all_other_jacs)

    rng = random.Random(217)
    null_means = []
    for _ in range(5000):
        perm = list(recipe_folios_22)
        rng.shuffle(perm)
        trial_jacs = [jaccard(folio_stem_sets[perm[2*k]], folio_stem_sets[perm[2*k+1]]) for k in range(11)]
        null_means.append(sum(trial_jacs) / 11.0)
    mu_null = sum(null_means) / len(null_means)
    sd_null = math.sqrt(sum((x - mu_null) ** 2 for x in null_means) / len(null_means))
    z_same_leaf = (obs_same_leaf_jac - mu_null) / sd_null if sd_null > 0 else 0.0
    p_same_leaf = sum(1 for x in null_means if x >= obs_same_leaf_jac) / len(null_means)

    # 7. 23-Page Dialect Trajectory across Quire 20 (f103r-f116r)
    trajectory_23 = []
    for fol in first_half + second_half:
        wlist = folio_words[fol]
        recs = folio_recipes[fol]
        trajectory_23.append({
            "folio": fol,
            "words": len(wlist),
            "recipes": len(recs),
            "words_per_recipe": round(len(wlist) / max(1, len(recs)), 2),
            "q_pct": round(100.0 * sum(1 for w in wlist if w.startswith("q")) / len(wlist), 2),
            "edy_pct": round(100.0 * sum(1 for w in wlist if w.endswith("edy")) / len(wlist), 2),
            "aiin_pct": round(100.0 * sum(1 for w in wlist if w.endswith("aiin")) / len(wlist), 2),
            "o_initial_pct": round(100.0 * sum(1 for w in wlist if w.startswith("o")) / len(wlist), 2),
            "meta": folio_meta.get(fol, {})
        })

    out = {
        "attack": 217,
        "discovery": 234,
        "title": "100% Quire 20 Visual & Structural Completion (f105v, f112r/v, f114r, f115v), 12-Leaf Recto-Verso Mirroring, and 6-Bifolium Architecture",
        "quire20_visual_completion": {
            "total_folios": len(scan_coverage),
            "rendered_folios": sum(1 for v in scan_coverage.values() if v["rendered"]),
            "completion_pct": round(100.0 * sum(1 for v in scan_coverage.values() if v["rendered"]) / len(scan_coverage), 2),
            "folios": scan_coverage
        },
        "new_five_folio_profiles": new_five_profiles,
        "per_folio_dialect_trajectory": trajectory_23,
        "same_leaf_recto_verso_coupling": {
            "leaves_tested": len(same_leaf_results),
            "mean_same_leaf_jaccard": round(obs_same_leaf_jac, 4),
            "mean_non_same_leaf_jaccard": round(mean_other_jac, 4),
            "permutation_z": round(z_same_leaf, 2),
            "permutation_p": round(p_same_leaf, 5),
            "leaves": same_leaf_results
        },
        "six_bifolia_architecture": bifolium_results,
        "sheet_side_conjugate_pairs": sheet_side_results,
        "first_vs_second_half_across_missing_f109_f110": half_comparison
    }

    out_path = os.path.join("data", "attack217_quire20_25page_completion_f105v_f112_f114r_f115v.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    print(f"Wrote {out_path}")
    print(f"Quire 20 visual completion: {out['quire20_visual_completion']['rendered_folios']}/{out['quire20_visual_completion']['total_folios']} ({out['quire20_visual_completion']['completion_pct']}%)")
    for row in trajectory_23:
        print(f"  {row['folio']:6s}: {row['words']:3d}w, {row['recipes']:2d}rec ({row['words_per_recipe']:5.2f} w/r), q={row['q_pct']:5.2f}%, edy={row['edy_pct']:5.2f}%, aiin={row['aiin_pct']:5.2f}%, o={row['o_initial_pct']:5.2f}%")
    print(f"Same-leaf mean Jaccard: {obs_same_leaf_jac:.4f} vs non-same-leaf {mean_other_jac:.4f} (z={z_same_leaf:+.2f}, p={p_same_leaf:.5f})")

if __name__ == "__main__":
    main()
