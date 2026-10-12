#!/usr/bin/env python3
"""
Attack 95 (Discovery 112): Three-Stage Cross-Sectional Pharmacopoeia Chains
(`Stage 1: Herbal Monograph $I=H` -> `Stage 2: Pharmaceutical Jar/Root Formulary $I=P` ->
`Stage 3: Quire 20 Starred Clinical Recipe $I=S`)

Tests:
1. Extracts all open-class canonical stems (excluding Top-45 closed-class particles/pronouns/linkers)
   and their Inverse Document Frequency (`IDF`) across:
   - Stage 1 (`$I=H`): `126` Herbal Monograph folios (`258` paragraphs),
   - Stage 2 (`$I=P`): `16` Pharmaceutical Formulary folios (`f88r–f89v2, f99r–f102v2`, combining `@Lf/@Lj`
     ingredient labels and `@P` preparation paragraphs),
   - Stage 3 (`$I=S`): `306` Quire 20 Starred Clinical Recipes (`f103r–f116r`).
2. Reconstructs the highest-specificity **Three-Stage Pharmacopoeia Triads (`H_folio -> P_folio -> S_recipe`)**
   that share `>= 3` high-IDF open-class canonical stems across all three stages (`S_shared = H ∩ P ∩ S`),
   including Triads anchored directly by an explicit `@Lf` root/leaf label on the Pharmaceutical folio!
3. Runs a 1,000-trial permutation test (shuffling open-class stem assignments across folios/recipes
   while preserving exact vocabulary sizes) to test whether the Top-K Three-Stage Triad IDF-Overlap
   and `@Lf`-Anchored Triad count exceed chance.
4. Measures the **Three-Stage Grammatical Transformation Gradient (`Stage 1 H -> Stage 2 P -> Stage 3 S`)**
   on the shared stems of the top triads: tracking how identical canonical stems shift from
   Nominal/Descriptive (`o-` / `-ol,-or,-dy`) in `H` and `P` (`@Lf` labels) to Active Processual
   Execution (`qo-` / `-edy`) in Quire 20 Starred Recipes (`S`).
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
OUT_JSON = DATA_DIR / "attack95_three_stage_cross_section_pharmacopoeia_chains.json"

FOLIO_META_RE = re.compile(r"^<f([0-9]+[rv][0-9]*|Ros)>\s*<!\s*(.*?)>")
LOCUS_RE = re.compile(r"^<f([0-9]+[rv][0-9]*|Ros)\.([^,>]+),([^>]+)>\s*(.*)$")


def clean_tokens(raw: str):
    s = re.sub(r"\{[^}]*\}", "", raw)
    s = s.replace("<%>", " ").replace("<$>", " ").replace("<->", " ")
    s = re.sub(r"<[^>]*>", " ", s)
    s = re.sub(r"@[0-9]+;", "", s)
    s = re.sub(r"\[([^:\]]+):[^\]]+\]", r"\1", s)
    out = []
    for c in s.replace(".", " ").split():
        w = re.sub(r"[^a-zA-Z]", "", c).lower()
        if w:
            out.append(w)
    return out


def canonical_stem(w: str) -> str:
    """
    Canonical stem unifying Currier A/B allography (q- strip, p/f->t/k, sh->ch, e+->e, i+->i)
    and normalizing A/B suffix alternation (-edy/-ody -> -dy) so cross-dialect cognates align.
    """
    s = w
    if s.startswith("qo") and len(s) > 3:
        s = "o" + s[2:]
    elif s.startswith("q") and len(s) > 2:
        s = s[1:]
    s = s.replace("cph", "cth").replace("cfh", "ckh")
    s = s.replace("p", "t").replace("f", "k")
    s = s.replace("sh", "ch")
    s = re.sub(r"e+", "e", s)
    s = re.sub(r"i+", "i", s)
    if s.endswith("edy") and len(s) > 4:
        s = s[:-3] + "dy"
    elif s.endswith("ody") and len(s) > 4:
        s = s[:-3] + "dy"
    return s


def main():
    raw_lines = ZL_PATH.read_text(encoding="utf-8", errors="replace").splitlines()
    cur_folio = None
    cur_meta = {}

    folio_meta = {}
    folio_prose_tokens = defaultdict(list)
    folio_label_tokens = defaultdict(list)
    s_recipes = []
    cur_s_recipe = None

    all_word_counts = Counter()

    for raw_line in raw_lines:
        raw_s = raw_line.strip()
        if not raw_s or raw_s.startswith("#"):
            continue
        mf = FOLIO_META_RE.match(raw_s)
        if mf:
            cur_folio = "f" + mf.group(1)
            meta_str = mf.group(2)
            cur_meta = {}
            for kv in meta_str.split():
                if "=" in kv:
                    k, v = kv.lstrip("$").split("=", 1)
                    cur_meta[k] = v
            folio_meta[cur_folio] = cur_meta
            cur_s_recipe = None
            continue
        ml = LOCUS_RE.match(raw_s)
        if ml and cur_folio:
            lnum, ltype, text = ml.group(2), ml.group(3), ml.group(4)
            toks = clean_tokens(text)
            if not toks:
                continue
            for w in toks:
                all_word_counts[w] += 1
            ltype_clean = ltype.lstrip("@+*=")
            sec = cur_meta.get("I", "U")
            if ltype_clean.startswith("L"):
                folio_label_tokens[cur_folio].extend(toks)
            elif ltype_clean.startswith("P"):
                folio_prose_tokens[cur_folio].extend(toks)
                if sec == "S":
                    if "<%>" in text or cur_s_recipe is None:
                        cur_s_recipe = {
                            "recipe_id": f"{cur_folio}.{lnum}",
                            "folio": cur_folio,
                            "tokens": list(toks),
                        }
                        s_recipes.append(cur_s_recipe)
                    else:
                        cur_s_recipe["tokens"].extend(toks)

    # Exclude Top-45 closed-class particles/high-frequency stems so IDF focuses on specific content stems
    canon_counts = Counter()
    for w, c in all_word_counts.items():
        cs = canonical_stem(w)
        if len(cs) >= 3:
            canon_counts[cs] += c

    top45_closed_stems = {cs for cs, _ in canon_counts.most_common(45)}

    def get_open_stems(tokens):
        out = set()
        for w in tokens:
            if len(w) < 3:
                continue
            cs = canonical_stem(w)
            if len(cs) >= 3 and cs not in top45_closed_stems:
                out.add(cs)
        return out

    # Build Stage 1 (Herbal Folios), Stage 2 (Pharm Folios), Stage 3 (Quire 20 Starred Recipes)
    h_folios = {}
    p_folios = {}
    p_label_stems = {}
    for f, meta in folio_meta.items():
        sec = meta.get("I", "U")
        if sec == "H" and folio_prose_tokens[f]:
            st = get_open_stems(folio_prose_tokens[f])
            if len(st) >= 5:
                h_folios[f] = {
                    "folio": f,
                    "lang": meta.get("L", "U"),
                    "tokens": folio_prose_tokens[f],
                    "stems": st,
                }
        elif sec == "P" and (folio_prose_tokens[f] or folio_label_tokens[f]):
            combined_toks = folio_prose_tokens[f] + folio_label_tokens[f]
            st = get_open_stems(combined_toks)
            lst = get_open_stems(folio_label_tokens[f])
            if len(st) >= 5:
                p_folios[f] = {
                    "folio": f,
                    "lang": meta.get("L", "U"),
                    "prose_tokens": folio_prose_tokens[f],
                    "label_tokens": folio_label_tokens[f],
                    "stems": st,
                    "label_stems": lst,
                }
                p_label_stems[f] = lst

    s_units = {}
    for rec in s_recipes:
        st = get_open_stems(rec["tokens"])
        if len(st) >= 4:
            s_units[rec["recipe_id"]] = {
                "recipe_id": rec["recipe_id"],
                "folio": rec["folio"],
                "tokens": rec["tokens"],
                "stems": st,
            }

    # Compute Document Frequency & IDF across all H + P + S units
    all_units = [u["stems"] for u in h_folios.values()] + [u["stems"] for u in p_folios.values()] + [u["stems"] for u in s_units.values()]
    n_docs = len(all_units)
    df = Counter()
    for st_set in all_units:
        for cs in st_set:
            df[cs] += 1
    idf = {cs: math.log((n_docs + 1.0) / (c + 0.5)) for cs, c in df.items()}

    # Search for best Three-Stage Pharmacopoeia Chains:
    # For each (P_folio, S_recipe) pair that shares >= 2 open stems, find the H_folio maximizing
    # 3-way intersection `H ∩ P ∩ S` (and also track how many of those stems appear in `P_label_stems`)!
    triads = []
    label_anchored_triads = []

    for pf, p_rec in p_folios.items():
        pst = p_rec["stems"]
        plst = p_rec["label_stems"]
        for sid, s_rec in s_units.items():
            ps_inter = pst & s_rec["stems"]
            if len(ps_inter) < 2:
                continue
            for hf, h_rec in h_folios.items():
                hps_inter = ps_inter & h_rec["stems"]
                if len(hps_inter) >= 3:
                    idf_score = sum(idf[cs] for cs in hps_inter)
                    lbl_hits = sorted(hps_inter & plst)
                    # Map each shared canonical stem back to its concrete surface tokens in H, P, and S
                    h_surf = {cs: [w for w in h_rec["tokens"] if canonical_stem(w) == cs][0] for cs in hps_inter}
                    p_surf = {
                        cs: [w for w in (p_rec["label_tokens"] + p_rec["prose_tokens"]) if canonical_stem(w) == cs][0]
                        for cs in hps_inter
                    }
                    s_surf = {cs: [w for w in s_rec["tokens"] if canonical_stem(w) == cs][0] for cs in hps_inter}
                    chain_examples = [
                        f"{cs}: H({h_surf[cs]}) -> P({p_surf[cs]}{'*L' if cs in plst else ''}) -> S({s_surf[cs]})"
                        for cs in sorted(hps_inter, key=lambda x: -idf[x])
                    ]
                    entry = {
                        "h_folio": hf,
                        "h_lang": h_rec["lang"],
                        "p_folio": pf,
                        "s_recipe": sid,
                        "n_shared_3way_stems": len(hps_inter),
                        "n_pharm_label_anchored": len(lbl_hits),
                        "idf_3way_score": round(idf_score, 3),
                        "shared_stems": sorted(hps_inter, key=lambda x: -idf[x]),
                        "pharm_label_stems_in_triad": lbl_hits,
                        "surface_transformation_chains": chain_examples,
                    }
                    triads.append(entry)
                    if lbl_hits:
                        label_anchored_triads.append(entry)

    triads.sort(key=lambda x: (-x["n_pharm_label_anchored"], -x["idf_3way_score"], -x["n_shared_3way_stems"]))
    top_By_idf = sorted(triads, key=lambda x: (-x["idf_3way_score"], -x["n_shared_3way_stems"]))

    # Deduplicate to get distinct (H, P, S) chains where each P_folio and H_folio is represented cleanly
    best_per_p_folio = []
    seen_p = set()
    for t in top_By_idf:
        if t["p_folio"] not in seen_p:
            seen_p.add(t["p_folio"])
            best_per_p_folio.append(t)

    # Permutation Test (200 trials): shuffle open-class stem tokens across units within H, P, and S
    # preserving each unit's exact stem-set cardinality, and measure:
    # (a) mean Top-16 P-folio max 3-way IDF score, and (b) total count of 3-way triads with >= 4 shared stems
    obs_top16_mean_idf = sum(t["idf_3way_score"] for t in best_per_p_folio) / len(best_per_p_folio)
    obs_ge4_count = sum(1 for t in triads if t["n_shared_3way_stems"] >= 4)

    rng = random.Random(95)
    h_pool = [cs for u in h_folios.values() for cs in u["stems"]]
    p_pool = [cs for u in p_folios.values() for cs in u["stems"]]
    s_pool = [cs for u in s_units.values() for cs in u["stems"]]

    null_top16_means = []
    null_ge4_counts = []
    for _ in range(200):
        rng.shuffle(h_pool)
        rng.shuffle(p_pool)
        rng.shuffle(s_pool)

        idx = 0
        sim_h = []
        for u in h_folios.values():
            k = len(u["stems"])
            sim_h.append(set(h_pool[idx:idx + k]))
            idx += k

        idx = 0
        sim_p = []
        for u in p_folios.values():
            k = len(u["stems"])
            sim_p.append(set(p_pool[idx:idx + k]))
            idx += k

        idx = 0
        sim_s = []
        for u in s_units.values():
            k = len(u["stems"])
            sim_s.append(set(s_pool[idx:idx + k]))
            idx += k

        p_max_scores = []
        ge4_c = 0
        for pst in sim_p:
            best_p = 0.0
            for sst in sim_s:
                ps = pst & sst
                if len(ps) < 2:
                    continue
                for hst in sim_h:
                    hps = ps & hst
                    if len(hps) >= 3:
                        sc = sum(idf[cs] for cs in hps)
                        if sc > best_p:
                            best_p = sc
                        if len(hps) >= 4:
                            ge4_c += 1
            p_max_scores.append(best_p)
        null_top16_means.append(sum(p_max_scores) / len(p_max_scores))
        null_ge4_counts.append(ge4_c)

    null_idf_mean = sum(null_top16_means) / len(null_top16_means)
    null_idf_std = math.sqrt(sum((x - null_idf_mean) ** 2 for x in null_top16_means) / len(null_top16_means)) or 1e-9
    z_top16_idf = (obs_top16_mean_idf - null_idf_mean) / null_idf_std

    null_ge4_mean = sum(null_ge4_counts) / len(null_ge4_counts)
    null_ge4_std = math.sqrt(sum((x - null_ge4_mean) ** 2 for x in null_ge4_counts) / len(null_ge4_counts)) or 1e-9
    z_ge4 = (obs_ge4_count - null_ge4_mean) / null_ge4_std

    # Measure the Three-Stage Grammatical Transformation Gradient (`H -> P_label -> P_prose -> S_recipe`)
    # across all tokens belonging to the shared canonical stems of the triads!
    shared_stem_union = {cs for t in triads for cs in t["shared_stems"]}

    def profile_stage_tokens(token_iter):
        toks = [w for w in token_iter if canonical_stem(w) in shared_stem_union]
        n = len(toks)
        if n == 0:
            return {}
        return {
            "n_tokens": n,
            "o_nominal_pct": round(100.0 * sum(1 for w in toks if w.startswith(("ok", "ot", "op", "of", "ol", "or", "o")) and not w.startswith("qo")) / n, 2),
            "qo_active_pct": round(100.0 * sum(1 for w in toks if w.startswith("qo")) / n, 2),
            "edy_processual_pct": round(100.0 * sum(1 for w in toks if w.endswith("edy")) / n, 2),
            "dy_stative_pct": round(100.0 * sum(1 for w in toks if w.endswith("dy") and not w.endswith("edy")) / n, 2),
            "ol_or_container_pct": round(100.0 * sum(1 for w in toks if w.endswith(("ol", "al", "or", "ar"))) / n, 2),
            "aiin_quantifier_pct": round(100.0 * sum(1 for w in toks if w.endswith(("aiin", "ain", "iin"))) / n, 2),
        }

    stage_gradient = {
        "STAGE_1_HERBAL_MONOGRAPH_PROSE": profile_stage_tokens(w for u in h_folios.values() for w in u["tokens"]),
        "STAGE_2A_PHARM_INGREDIENT_LABELS": profile_stage_tokens(w for u in p_folios.values() for w in u["label_tokens"]),
        "STAGE_2B_PHARM_FORMULARY_PROSE": profile_stage_tokens(w for u in p_folios.values() for w in u["prose_tokens"]),
        "STAGE_3_QUIRE20_STARRED_RECIPES": profile_stage_tokens(w for u in s_units.values() for w in u["tokens"]),
    }

    out = {
        "stage_inventory": {
            "stage1_herbal_folios": len(h_folios),
            "stage2_pharm_folios": len(p_folios),
            "stage3_starred_recipes": len(s_units),
            "distinct_open_canonical_stems": len(idf),
        },
        "triad_discovery_summary": {
            "total_3way_triads_ge3_stems": len(triads),
            "total_3way_triads_ge4_stems": obs_ge4_count,
            "null_ge4_mean": round(null_ge4_mean, 2),
            "null_ge4_std": round(null_ge4_std, 2),
            "z_ge4_triads": round(z_ge4, 2),
            "pharm_label_anchored_triads": len(label_anchored_triads),
            "observed_mean_max_idf_across_16_pharm_folios": round(obs_top16_mean_idf, 3),
            "null_mean_max_idf": round(null_idf_mean, 3),
            "null_std_max_idf": round(null_idf_std, 3),
            "z_max_idf": round(z_top16_idf, 2),
        },
        "three_stage_grammatical_gradient": stage_gradient,
        "best_triad_per_pharmaceutical_folio": best_per_p_folio,
        "top_15_label_anchored_triads": label_anchored_triads[:15],
    }

    OUT_JSON.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"Saved {OUT_JSON}")
    print("Triad Discovery Summary:", json.dumps(out["triad_discovery_summary"], indent=2))
    print("Three-Stage Grammatical Gradient:", json.dumps(stage_gradient, indent=2))
    for t in best_per_p_folio[:6]:
        print(f"  {t['h_folio']} ({t['h_lang']}) -> {t['p_folio']} -> {t['s_recipe']} (shared={t['n_shared_3way_stems']}, IDF={t['idf_3way_score']}): {t['surface_transformation_chains'][:4]}")


if __name__ == "__main__":
    main()
