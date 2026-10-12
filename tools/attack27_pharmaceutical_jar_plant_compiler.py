#!/usr/bin/env python3
"""
Phase 38 / Attack 27: Pharmaceutical (f88r-f102v2) Container-to-Plant Recipe Compiler
& Quantitative Ingredient-to-Clause Scaling Law.

Investigates the 16 Pharmaceutical folios ($I=P: f88r..f102v2) in data/ZL3b-n.txt:
1. Container (@Lc) vs. Botanical Specimen (@Lf/@Ln/@L0) Morphological Divergence:
   - Tests whether apothecary jar labels (@Lc) systematically enrich specific onset/gallows
     or suffix classes compared to botanical root/leaf labels (@Lf).
2. Same-Folio & Same-Bifolium/Quire Label-to-Recipe Compilation Test (1,000 permutations):
   - Tests whether rare/canonical @Lf and @Lc labels on a Pharmaceutical folio (or quire)
     recur inside the prose recipe paragraphs (@P0/+P0) of the SAME folio or SAME quire
     significantly above random folio-assignment baselines.
3. Quantitative Ingredient-to-Clause Scaling Law:
   - Correlates the number of illustrated botanical specimens (@Lf/@Ln) and jars (@Lc)
     per folio with recipe paragraph count, clause count, and unit-measure (-aiin) /
     ablative (dar/dal) token counts.
4. Full 16-Folio Apothecary Formulary Compiler:
   - Compiles each Pharmaceutical folio's jars (@Lc), plant specimens (@Lf), Herbal ($I=H)
     source cross-references, and compiled recipe clauses.
"""

import json
import math
import random
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ZL_PATH = ROOT / "data" / "ZL3b-n.txt"
OUT_JSON = ROOT / "data" / "attack27_pharmaceutical_jar_plant_compiler.json"


def normalize_eva(word: str) -> str:
    w = re.sub(r"\[([^:\]]+):[^\]]+\]", r"\1", word)
    w = re.sub(r"\{[^}]*\}", "", w)
    w = re.sub(r"<[^>]*>", "", w)
    w = re.sub(r"[^a-zA-Z]", "", w).lower()
    return w


def canonical_4rule(w: str) -> str:
    if not w:
        return ""
    s = w
    if s.startswith("qo") and len(s) > 2:
        s = s[2:]
    elif s.startswith("q") and len(s) > 1:
        s = s[1:]
    s = s.replace("ckh", "kh").replace("cth", "th").replace("cph", "ph").replace("cfh", "fh")
    s = re.sub(r"i{2,}", "i", s)
    s = re.sub(r"e{2,}", "e", s)
    if len(s) > 1 and s.startswith("p"):
        s = "t" + s[1:]
    elif len(s) > 1 and s.startswith("f"):
        s = "k" + s[1:]
    return s


PREFIXES = ["qok", "qot", "qo", "ok", "ot", "ol", "or", "ar", "al", "op", "of", "yk", "yt", "ch", "sh", "d", "s", "y", "o", "k", "t", "p", "f"]
SUFFIXES = ["aiin", "oiin", "iiin", "iin", "in", "edy", "eedy", "dy", "ey", "eey", "ol", "or", "ar", "al", "am", "om", "an", "y", "l", "r", "m", "n", "g"]


def extract_core_root(w: str) -> str:
    s = canonical_4rule(w)
    if len(s) <= 2:
        return s
    for p in sorted(PREFIXES, key=len, reverse=True):
        if s.startswith(p) and len(s) - len(p) >= 2:
            s = s[len(p):]
            break
    for sfx in sorted(SUFFIXES, key=len, reverse=True):
        if s.endswith(sfx) and len(s) - len(sfx) >= 1:
            s = s[:-len(sfx)]
            break
    return s


def edit_distance(a: str, b: str) -> int:
    if len(a) < len(b):
        return edit_distance(b, a)
    if len(b) == 0:
        return len(a)
    prev = list(range(len(b) + 1))
    for i, c1 in enumerate(a):
        curr = [i + 1]
        for j, c2 in enumerate(b):
            curr.append(min(prev[j + 1] + 1, curr[j] + 1, prev[j] + (c1 != c2)))
        prev = curr
    return prev[-1]


def pearson_r(xs, ys):
    n = len(xs)
    if n < 2:
        return 0.0
    mx = sum(xs) / n
    my = sum(ys) / n
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    denx = math.sqrt(sum((x - mx) ** 2 for x in xs))
    deny = math.sqrt(sum((y - my) ** 2 for y in ys))
    if denx == 0 or deny == 0:
        return 0.0
    return num / (denx * deny)


def parse_zl():
    folios = {}
    current_folio = None
    meta = {}

    line_re = re.compile(r"^<([^.>]+)\.([^,>]+),([^>]+)>\s*(.*)$")
    meta_re = re.compile(r"\$([A-Z])=([A-Za-z0-9]+)")

    with open(ZL_PATH, "r", encoding="utf-8", errors="ignore") as f:
        for raw in f:
            raw = raw.strip()
            if not raw:
                continue
            if raw.startswith("<f") and ">" in raw and "." not in raw.split(">")[0]:
                m_f = re.match(r"^<(f[0-9]+[rv][0-9]*)>", raw)
                if m_f:
                    current_folio = m_f.group(1)
                    meta = dict(meta_re.findall(raw))
                    folios[current_folio] = {
                        "folio": current_folio,
                        "section": meta.get("I", ""),
                        "language": meta.get("L", ""),
                        "hand": meta.get("H", ""),
                        "quire": meta.get("Q", ""),
                        "lines": [],
                    }
                continue
            m = line_re.match(raw)
            if m and current_folio:
                f_id, loc_id, loc_type, body = m.groups()
                body_clean = re.sub(r"<!.*?>", "", body)
                raw_tokens = re.split(r"[.\s,]+", body_clean)
                tokens = [normalize_eva(t) for t in raw_tokens]
                tokens = [t for t in tokens if t]
                folios[current_folio]["lines"].append({
                    "loc_id": loc_id,
                    "loc_type": loc_type,
                    "tokens": tokens,
                    "has_para_start": "<%>" in body or loc_type.startswith("@P"),
                    "has_para_end": "<$>" in body,
                })
    return folios


def main():
    random.seed(42)
    folios = parse_zl()

    # Collect Herbal ($I=H) folio vocabulary for source-plant lookups
    herbal_folio_vocab = {}
    herbal_word_to_folios = defaultdict(list)
    for f_id, fdata in folios.items():
        if fdata["section"] == "H":
            c_tokens = set()
            for ln in fdata["lines"]:
                for t in ln["tokens"]:
                    c = canonical_4rule(t)
                    if len(c) >= 3:
                        c_tokens.add(c)
            herbal_folio_vocab[f_id] = c_tokens
            for c in c_tokens:
                herbal_word_to_folios[c].append(f_id)

    # Global document frequency across all 226 folios (in canonical form)
    global_df = Counter()
    for f_id, fdata in folios.items():
        seen = set()
        for ln in fdata["lines"]:
            for t in ln["tokens"]:
                seen.add(canonical_4rule(t))
        for c in seen:
            global_df[c] += 1

    # Extract all Pharmaceutical ($I=P) folios
    pharma_folios = [f_id for f_id, fdata in folios.items() if fdata["section"] == "P"]

    lc_tokens = []
    lf_tokens = []
    ln_tokens = []

    folio_summaries = []
    pharma_labels_by_folio = {}
    pharma_prose_by_folio = {}
    pharma_prose_canonical_by_folio = {}
    pharma_prose_roots_by_folio = {}

    for f_id in pharma_folios:
        fdata = folios[f_id]
        f_lc = []
        f_lf = []
        f_ln = []
        f_prose = []
        para_count = 0

        for ln in fdata["lines"]:
            lt = ln["loc_type"]
            toks = ln["tokens"]
            if not toks:
                continue
            if "Lc" in lt:
                f_lc.extend(toks)
                lc_tokens.extend([(f_id, ln["loc_id"], t) for t in toks])
            elif "Lf" in lt:
                f_lf.extend(toks)
                lf_tokens.extend([(f_id, ln["loc_id"], t) for t in toks])
            elif "Ln" in lt or "L0" in lt:
                f_ln.extend(toks)
                ln_tokens.extend([(f_id, ln["loc_id"], t) for t in toks])
            elif "P" in lt:
                if ln["has_para_start"]:
                    para_count += 1
                f_prose.extend(toks)

        if para_count == 0 and f_prose:
            para_count = 1

        all_labels = f_lc + f_lf + f_ln
        pharma_labels_by_folio[f_id] = all_labels
        pharma_prose_by_folio[f_id] = f_prose
        pharma_prose_canonical_by_folio[f_id] = set(canonical_4rule(t) for t in f_prose if len(canonical_4rule(t)) >= 2)
        pharma_prose_roots_by_folio[f_id] = set(extract_core_root(t) for t in f_prose if len(extract_core_root(t)) >= 2)

        # Count procedural & unit markers in prose
        aiin_count = sum(1 for t in f_prose if t.endswith(("aiin", "iin", "in")))
        dar_dal_count = sum(1 for t in f_prose if t in ("dar", "dal", "dair", "daly", "dam"))
        qok_qot_count = sum(1 for t in f_prose if t.startswith(("qok", "qot", "qo")))
        edy_count = sum(1 for t in f_prose if t.endswith(("edy", "eedy", "dy")))
        ol_or_count = sum(1 for t in f_prose if t in ("ol", "or", "al", "ar", "chol", "chor", "shol"))

        # Check same-folio label->prose matches
        same_folio_exact_hits = []
        same_folio_ed1_hits = []
        herbal_links = []

        for lbl in all_labels:
            c_lbl = canonical_4rule(lbl)
            if len(c_lbl) < 2:
                continue
            if c_lbl in pharma_prose_canonical_by_folio[f_id]:
                same_folio_exact_hits.append({
                    "label": lbl,
                    "canonical": c_lbl,
                    "global_df": global_df[c_lbl],
                })
            else:
                # check ED1 in same folio prose
                for p_tok in f_prose:
                    c_p = canonical_4rule(p_tok)
                    if len(c_lbl) >= 4 and len(c_p) >= 4 and edit_distance(c_lbl, c_p) == 1:
                        same_folio_ed1_hits.append({
                            "label": lbl,
                            "prose_token": p_tok,
                            "canonical_label": c_lbl,
                            "canonical_prose": c_p,
                            "global_df_label": global_df[c_lbl],
                        })
                        break
            # Check rare Herbal folio matches (1 <= herbal_df <= 5)
            h_folios = herbal_word_to_folios.get(c_lbl, [])
            if 1 <= len(h_folios) <= 5:
                herbal_links.append({
                    "label": lbl,
                    "canonical": c_lbl,
                    "herbal_folios": h_folios,
                    "herbal_df": len(h_folios),
                })

        folio_summaries.append({
            "folio": f_id,
            "quire": fdata["quire"],
            "language": fdata["language"],
            "hand": fdata["hand"],
            "jar_count_Lc": len(f_lc),
            "plant_count_Lf": len(f_lf),
            "other_label_count_Ln": len(f_ln),
            "total_labels": len(all_labels),
            "paragraph_count": para_count,
            "prose_word_count": len(f_prose),
            "aiin_unit_count": aiin_count,
            "dar_dal_ablative_count": dar_dal_count,
            "qok_qot_operator_count": qok_qot_count,
            "edy_verbal_count": edy_count,
            "ol_or_fluid_count": ol_or_count,
            "lc_labels": f_lc,
            "lf_labels": f_lf[:25],
            "same_folio_exact_hits": same_folio_exact_hits,
            "same_folio_ed1_hits": same_folio_ed1_hits[:10],
            "rare_herbal_source_links": herbal_links[:15],
        })

    # 1. Morphological comparison: @Lc (apothecary jars) vs @Lf (plant specimens)
    def profile_labels(records):
        toks = [t for _, _, t in records]
        n = max(len(toks), 1)
        has_p_f = sum(1 for t in toks if "p" in t or "f" in t) / n
        has_k_t = sum(1 for t in toks if "k" in t or "t" in t) / n
        starts_o = sum(1 for t in toks if t.startswith("o")) / n
        starts_d_s = sum(1 for t in toks if t.startswith(("d", "s"))) / n
        ends_r_l = sum(1 for t in toks if t.endswith(("r", "l"))) / n
        ends_y = sum(1 for t in toks if t.endswith("y")) / n
        ends_m_n = sum(1 for t in toks if t.endswith(("m", "n"))) / n
        mean_len = sum(len(t) for t in toks) / n
        return {
            "count": len(toks),
            "mean_length": round(mean_len, 3),
            "has_labial_gallows_p_f_rate": round(has_p_f, 4),
            "has_dental_velar_gallows_k_t_rate": round(has_k_t, 4),
            "starts_with_o_rate": round(starts_o, 4),
            "starts_with_d_s_rate": round(starts_d_s, 4),
            "ends_with_liquid_r_l_rate": round(ends_r_l, 4),
            "ends_with_y_rate": round(ends_y, 4),
            "ends_with_nasal_m_n_rate": round(ends_m_n, 4),
            "examples": toks[:20],
        }

    lc_profile = profile_labels(lc_tokens)
    lf_profile = profile_labels(lf_tokens)

    # 2. Permutation test: Do Pharmaceutical labels (@Lc/@Lf/@Ln) recur in the SAME folio or SAME quire
    # prose (exact canonical or ED1 for length>=4) above random folio pairing?
    quire_map = {f_id: folios[f_id]["quire"] for f_id in pharma_folios}

    # Precompute pairwise match matrix: pair_matches[(f_lbl, f_prose)] = set of matched label indices
    filtered_labels_by_folio = {}
    for f_id, lbls in pharma_labels_by_folio.items():
        flist = []
        for idx, lbl in enumerate(lbls):
            c = canonical_4rule(lbl)
            if len(c) >= 3 and global_df[c] <= 40:
                flist.append((idx, c))
        filtered_labels_by_folio[f_id] = flist

    pair_match_sets = {}
    for f_lbl in pharma_folios:
        flist = filtered_labels_by_folio[f_lbl]
        for f_pr in pharma_folios:
            p_set = pharma_prose_canonical_by_folio[f_pr]
            matched_indices = set()
            for idx, c in flist:
                if (c in p_set) or (len(c) >= 4 and any(len(p) >= 4 and edit_distance(c, p) == 1 for p in p_set)):
                    matched_indices.add(idx)
            pair_match_sets[(f_lbl, f_pr)] = matched_indices

    def score_mapping(mapping):
        same_folio_matches = 0
        same_quire_matches = 0
        for f_lbl in pharma_folios:
            f_pr_assigned = mapping[f_lbl]
            same_folio_matches += len(pair_match_sets[(f_lbl, f_pr_assigned)])
            q = quire_map[f_lbl]
            q_matched = set()
            for f2 in pharma_folios:
                if quire_map[f2] == q:
                    q_matched |= pair_match_sets[(f_lbl, mapping[f2])]
            same_quire_matches += len(q_matched)
        return same_folio_matches, same_quire_matches

    identity_map = {f: f for f in pharma_folios}
    obs_folio_hits, obs_quire_hits = score_mapping(identity_map)

    null_folio_hits = []
    null_quire_hits = []
    prose_keys = list(pharma_folios)
    for _ in range(1000):
        shuffled_keys = prose_keys[:]
        random.shuffle(shuffled_keys)
        perm_map = {f_orig: f_shuf for f_orig, f_shuf in zip(prose_keys, shuffled_keys)}
        nf, nq = score_mapping(perm_map)
        null_folio_hits.append(nf)
        null_quire_hits.append(nq)

    mean_nf = sum(null_folio_hits) / len(null_folio_hits)
    std_nf = math.sqrt(sum((x - mean_nf) ** 2 for x in null_folio_hits) / len(null_folio_hits)) or 1.0
    z_folio = (obs_folio_hits - mean_nf) / std_nf
    p_folio = sum(1 for x in null_folio_hits if x >= obs_folio_hits) / len(null_folio_hits)

    mean_nq = sum(null_quire_hits) / len(null_quire_hits)
    std_nq = math.sqrt(sum((x - mean_nq) ** 2 for x in null_quire_hits) / len(null_quire_hits)) or 1.0
    z_quire = (obs_quire_hits - mean_nq) / std_nq
    p_quire = sum(1 for x in null_quire_hits if x >= obs_quire_hits) / len(null_quire_hits)

    # 3. Quantitative scaling correlations across the 16 Pharmaceutical folios
    # Filter to folios that actually have labels (13 labeled folios) as well as all 16 folios
    labeled_folios = [s for s in folio_summaries if s["total_labels"] > 0]
    r_jars_vs_paras_all = pearson_r(
        [s["jar_count_Lc"] for s in folio_summaries],
        [s["paragraph_count"] for s in folio_summaries],
    )
    r_labels_vs_prose_labeled = pearson_r(
        [s["total_labels"] for s in labeled_folios],
        [s["prose_word_count"] for s in labeled_folios],
    )
    r_prose_vs_aiin = pearson_r(
        [s["prose_word_count"] for s in folio_summaries],
        [s["aiin_unit_count"] for s in folio_summaries],
    )
    r_prose_vs_qok = pearson_r(
        [s["prose_word_count"] for s in folio_summaries],
        [s["qok_qot_operator_count"] for s in folio_summaries],
    )

    # Compare jar-to-paragraph ratio on labeled folios with @Lc jars
    jar_folios = [s for s in folio_summaries if s["jar_count_Lc"] > 0]
    total_jars_on_jar_folios = sum(s["jar_count_Lc"] for s in jar_folios)
    total_paras_on_jar_folios = sum(s["paragraph_count"] for s in jar_folios)

    result = {
        "phase": "Phase 38 / Attack 27",
        "title": "Pharmaceutical (f88r-f102v2) Container-to-Plant Recipe Compiler & Quantitative Ingredient-to-Clause Scaling Law",
        "summary_counts": {
            "pharmaceutical_folios": len(pharma_folios),
            "labeled_pharmaceutical_folios": len(labeled_folios),
            "total_Lc_jar_labels": len(lc_tokens),
            "total_Lf_plant_labels": len(lf_tokens),
            "total_Ln_other_labels": len(ln_tokens),
            "total_pharmaceutical_labels": len(lc_tokens) + len(lf_tokens) + len(ln_tokens),
            "total_pharmaceutical_prose_tokens": sum(s["prose_word_count"] for s in folio_summaries),
            "total_pharmaceutical_paragraphs": sum(s["paragraph_count"] for s in folio_summaries),
        },
        "container_Lc_vs_plant_Lf_morphology": {
            "Lc_container_profile": lc_profile,
            "Lf_plant_profile": lf_profile,
            "labial_gallows_p_f_enrichment_Lc_over_Lf": round(
                lc_profile["has_labial_gallows_p_f_rate"] / max(lf_profile["has_labial_gallows_p_f_rate"], 1e-6), 2
            ),
        },
        "label_to_recipe_compilation_permutation_test": {
            "same_folio_exact_or_ed1_hits": obs_folio_hits,
            "null_folio_mean": round(mean_nf, 3),
            "null_folio_std": round(std_nf, 3),
            "same_folio_z_score": round(z_folio, 2),
            "same_folio_p_value": round(p_folio, 4),
            "same_quire_exact_or_ed1_hits": obs_quire_hits,
            "null_quire_mean": round(mean_nq, 3),
            "null_quire_std": round(std_nq, 3),
            "same_quire_z_score": round(z_quire, 2),
            "same_quire_p_value": round(p_quire, 4),
        },
        "quantitative_scaling_laws": {
            "jar_folios_count": len(jar_folios),
            "total_Lc_jars_on_jar_folios": total_jars_on_jar_folios,
            "total_paragraphs_on_jar_folios": total_paras_on_jar_folios,
            "mean_jars_per_jar_folio": round(total_jars_on_jar_folios / max(len(jar_folios), 1), 2),
            "mean_paragraphs_per_jar_folio": round(total_paras_on_jar_folios / max(len(jar_folios), 1), 2),
            "pearson_r_jars_vs_paragraphs": round(r_jars_vs_paras_all, 4),
            "pearson_r_labels_vs_prose_words": round(r_labels_vs_prose_labeled, 4),
            "pearson_r_prose_words_vs_aiin_units": round(r_prose_vs_aiin, 4),
            "pearson_r_prose_words_vs_qok_operators": round(r_prose_vs_qok, 4),
        },
        "folio_compilations": folio_summaries,
    }

    OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(f"Saved {OUT_JSON}")
    print("Summary counts:", json.dumps(result["summary_counts"], indent=2))
    print("Container @Lc vs Plant @Lf:", json.dumps(result["container_Lc_vs_plant_Lf_morphology"], indent=2))
    print("Permutation test:", json.dumps(result["label_to_recipe_compilation_permutation_test"], indent=2))
    print("Scaling laws:", json.dumps(result["quantitative_scaling_laws"], indent=2))


if __name__ == "__main__":
    main()
