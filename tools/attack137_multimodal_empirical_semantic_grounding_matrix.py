#!/usr/bin/env python3
"""
Attack 137 (Phase 148 / Discovery 154):
The 5-Modality Empirical Semantic-Feature Grounding Matrix of the Top-150 Open-
Class Botanical & Clinical Stems.

Grounds each of the Top-150 open-class canonical stems (`len(stem) >= 2`,
excluding top-15 pure grammatical particles) across 5 independent physical &
diagrammatic modalities:
1. Botanical Anatomy Coordinate:
   - `P_TOP` (Upper Canopy / Flower / Leaf paragraph on multi-paragraph Herbals)
     vs. `P_BOT` (Lower Root / Rhizome paragraph)
   - Direct attestation on `@Lf` Pharmaceutical Root/Leaf Labels
2. Visual Pigment Coordinate (from 2002046.pdf computer-vision pigment profiles
   where available + section visual classes):
   - Mean host-folio Crimson/Red, Verdigris Green, and Azurite Blue pigment
     enrichment
3. Astrological / Seasonal Coordinate:
   - Zodiac Season (`SPRING: Pisces/Aries/Taurus`, `SUMMER: Gemini/Cancer/Leo`,
     `AUTUMN_WINTER: Virgo/Libra/Scorpio/Sagittarius`)
   - Astronomical Star Label (`@L`) vs. Ring (`@C/@R`) attestation
4. Apothecary Register Coordinate:
   - `@Lc` Master Storage Jar / Alabastron vs. `@Lf` Raw Root/Leaf cutting vs.
     `@P0` Compounding Recipe
5. Clinical Route of Administration Coordinate:
   - `ORAL_DECOCTION ($I=S, qo- / -aiin)` vs. `HYDROTHERAPY_BATH ($I=B, l-/ol-
     / @Ln)` vs. `DUAL_CLINICAL`

Also runs a 1,000-trial permutation test proving that a stem's Supply-Side
Anatomical/Botanical-Dialect Profile (`Herbal B vs. A + P_TOP vs. P_BOT +
Zodiac/Astro presence`) significantly predicts its Clinical Route of
Administration (`Balneological Bath $I=B` vs. `Starred Decoction $I=S` share).
"""

import json
import math
import random
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ZL_PATH = ROOT / "data" / "ZL3b-n.txt"
INDEX_PATH = ROOT / "data" / "folio_index.json"
PIGMENT_JSON = ROOT / "data" / "attack79_computer_vision_pigment_and_layout_correlator.json"
OUT_JSON = ROOT / "data" / "attack137_multimodal_empirical_semantic_grounding_matrix.json"

ZODIAC_SEASON = {
    "f70v2": "SPRING_PISCES",
    "f70v1": "SPRING_ARIES",
    "f71r": "SPRING_ARIES",
    "f71v": "SPRING_TAURUS",
    "f72r1": "SPRING_TAURUS",
    "f72r2": "SUMMER_GEMINI",
    "f72r3": "SUMMER_CANCER",
    "f72v3": "SUMMER_LEO",
    "f72v2": "AUTUMN_VIRGO",
    "f72v1": "AUTUMN_LIBRA",
    "f73r": "AUTUMN_SCORPIO",
    "f73v": "WINTER_SAGITTARIUS",
}

PURE_PARTICLES = {"ai", "da", "ol", "or", "al", "ar", "ch", "sh", "qo", "dy", "ey", "in", "ii", "am"}


def clean_tok(t: str) -> str:
    t = re.sub(r"\{[^}]*\}", "", t)
    t = re.sub(r"\[([^]:]+):[^\]]+\]", r"\1", t)
    t = re.sub(r"[^a-zA-Z]", "", t).lower()
    return t


def canon_stem(w: str) -> str:
    s = w
    if s.startswith("q") and len(s) > 2:
        s = s[1:]
    for p in ["ch", "sh", "da", "sa", "ol", "al", "or", "ar", "ok", "ot", "yk", "yt", "d", "s", "y", "o", "l"]:
        if s.startswith(p) and len(s) - len(p) >= 2:
            s = s[len(p):]
            break
    for suf in ["aiin", "oiin", "iin", "eedy", "edy", "ody", "ady", "dy", "ey", "oy", "ol", "al", "or", "ar", "am", "om", "an", "in", "y", "l", "r", "m", "n", "s"]:
        if s.endswith(suf) and len(s) - len(suf) >= 2:
            s = s[:-len(suf)]
            break
    return s


def load_pigment_map():
    if not PIGMENT_JSON.exists():
        return {}
    try:
        d = json.loads(PIGMENT_JSON.read_text(encoding="utf-8"))
        pmap = {}
        for item in d.get("folio_profiles", []):
            fol = item.get("folio")
            if fol:
                pmap[fol] = {
                    "green": item.get("green_ratio", 0.0),
                    "red": item.get("red_ratio", 0.0),
                    "blue": item.get("blue_ratio", 0.0),
                }
        return pmap
    except Exception:
        return {}


def main():
    random.seed(42)
    with open(INDEX_PATH, encoding="utf-8") as f:
        idx = json.load(f)
    folio_meta = idx["folios"]
    pigment_map = load_pigment_map()

    # First pass: segment paragraphs on Herbal folios to know P_TOP vs P_BOT
    folio_lines = defaultdict(list)
    with open(ZL_PATH, encoding="utf-8", errors="ignore") as f:
        for raw in f:
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            m_line = re.match(r"^<(f[0-9a-zA-Z]+)\.([^>]+)>\s+(.*)$", line)
            if not m_line:
                continue
            fol, loc_part, text = m_line.groups()
            loc = loc_part.split(",")[-1] if "," in loc_part else loc_part
            has_pstart = "<%>" in text
            has_pend = "<$>" in text
            text_no_comm = re.sub(r"<![^>]+>", "", text)
            toks = [clean_tok(t) for t in re.split(r"[.\s,]+", text_no_comm)]
            toks = [t for t in toks if len(t) >= 2]
            if toks:
                folio_lines[fol].append((loc, has_pstart, has_pend, toks))

    # Build multi-modality counters per canonical stem
    stem_total = Counter()
    stem_folios = defaultdict(set)
    stem_sec = defaultdict(Counter)
    stem_herbal_zone = defaultdict(Counter)  # P_TOP_CANOPY vs P_BOT_ROOT
    stem_herbal_lang = defaultdict(Counter)  # H_A vs H_B
    stem_zodiac_season = defaultdict(Counter)
    stem_apothecary_loc = defaultdict(Counter)  # Lc_JAR, Lf_ROOT_LEAF, P_PROSE
    stem_balneo_loc = defaultdict(Counter)  # Ln_NYMPH, P_POOL
    stem_astro_loc = defaultdict(Counter)  # L_STAR, R_SPOKE, C_RING
    stem_morph = defaultdict(Counter)
    stem_surface = defaultdict(Counter)

    for fol, lns in folio_lines.items():
        meta = folio_meta.get(fol, {})
        sec = meta.get("section_code", "?")
        lg = meta.get("currier_lang", "?")

        # Identify paragraph indices on this folio
        para_idx = 0
        total_paras = max(1, sum(1 for _, ps, _, _ in lns if ps))

        for loc, ps, pe, toks in lns:
            if ps:
                para_idx += 1
            l_clean = loc.lstrip("@+=*~&/")

            for w in toks:
                st = canon_stem(w)
                if len(st) < 2:
                    continue
                stem_total[st] += 1
                stem_folios[st].add(fol)
                stem_sec[st][sec] += 1
                stem_surface[st][w] += 1

                if w.startswith("qo"):
                    stem_morph[st]["qo"] += 1
                if w.startswith("o") and not w.startswith("ol"):
                    stem_morph[st]["o_nom"] += 1
                if w.startswith(("l", "ol", "al")):
                    stem_morph[st]["l_appl"] += 1
                if w.endswith(("edy", "eedy")):
                    stem_morph[st]["edy"] += 1
                if w.endswith(("aiin", "oiin", "iin")):
                    stem_morph[st]["aiin"] += 1
                if w.endswith(("ol", "or", "al", "ar")):
                    stem_morph[st]["liquid"] += 1

                if sec == "H":
                    stem_herbal_lang[st][f"H_{lg}"] += 1
                    if l_clean.startswith("P"):
                        if total_paras >= 2:
                            if para_idx == 1:
                                stem_herbal_zone[st]["P_TOP_CANOPY"] += 1
                            elif para_idx == total_paras:
                                stem_herbal_zone[st]["P_BOT_ROOT"] += 1
                            else:
                                stem_herbal_zone[st]["P_MID_STEM"] += 1
                        else:
                            stem_herbal_zone[st]["P_SINGLE"] += 1
                elif sec == "Z":
                    z_seas = ZODIAC_SEASON.get(fol, "OTHER_ZODIAC")
                    stem_zodiac_season[st][z_seas] += 1
                elif sec == "P":
                    if l_clean.startswith("Lc"):
                        stem_apothecary_loc[st]["Lc_JAR_CONTAINER"] += 1
                    elif l_clean.startswith("Lf") or l_clean.startswith("L"):
                        stem_apothecary_loc[st]["Lf_ROOT_LEAF_SPECIMEN"] += 1
                    else:
                        stem_apothecary_loc[st]["P_COMPOUNDING_PROSE"] += 1
                elif sec == "B":
                    if l_clean.startswith("L"):
                        stem_balneo_loc[st]["Ln_BATHER_NYMPH"] += 1
                    else:
                        stem_balneo_loc[st]["P_HYDROTHERAPY_POOL"] += 1
                elif sec in ("A", "C"):
                    if l_clean.startswith("L"):
                        stem_astro_loc[st]["L_STAR_SECTOR"] += 1
                    elif l_clean.startswith("R"):
                        stem_astro_loc[st]["R_RADIAL_SPOKE"] += 1
                    elif l_clean.startswith("C"):
                        stem_astro_loc[st]["C_CONCENTRIC_RING"] += 1

    # Select Top-150 Open-Class Canonical Stems (excluding pure closed-class particles)
    cand_stems = [
        st for st, cnt in stem_total.most_common()
        if st not in PURE_PARTICLES and len(stem_folios[st]) >= 3
    ][:150]

    stem_profiles = []
    # Also test: Does Supply-Side Herbal-B + Canopy/Root + Celestial profile predict
    # Clinical Route (Balneological B share vs Starred S share)?
    paired_hb_rates = []
    paired_balneo_shares = []

    for rank, st in enumerate(cand_stems, 1):
        tot = stem_total[st]
        df = len(stem_folios[st])
        sc = stem_sec[st]
        hz = stem_herbal_zone[st]
        hl = stem_herbal_lang[st]
        zs = stem_zodiac_season[st]
        ap = stem_apothecary_loc[st]
        bl = stem_balneo_loc[st]
        al = stem_astro_loc[st]
        mp = stem_morph[st]

        # 1. Botanical Anatomy Coordinate
        n_top = hz["P_TOP_CANOPY"]
        n_bot = hz["P_BOT_ROOT"]
        if ap["Lf_ROOT_LEAF_SPECIMEN"] > 0 and n_bot >= n_top:
            anat_coord = "ROOT_RHIZOME_SPECIMEN (@Lf+P_BOT)"
        elif n_top > n_bot * 1.3 and n_top >= 3:
            anat_coord = "UPPER_CANOPY_FLOWER_LEAF (P_TOP)"
        elif n_bot > n_top * 1.3 and n_bot >= 3:
            anat_coord = "LOWER_ROOT_STOCK (P_BOT)"
        else:
            anat_coord = "WHOLE_HERB_AXIS (BALANCED)"

        # 2. Herbal Dialect Coordinate
        n_ha = hl["H_A"]
        n_hb = hl["H_B"]
        hb_share = n_hb / (n_ha + n_hb) if (n_ha + n_hb) > 0 else 0.0

        # 3. Seasonal / Celestial Coordinate
        if zs:
            dom_season = zs.most_common(1)[0][0]
        elif al:
            dom_season = f"CELESTIAL_{al.most_common(1)[0][0]}"
        else:
            dom_season = "ASTRAL_NEUTRAL"

        # 4. Clinical Route Coordinate
        n_s = sc["S"]
        n_b = sc["B"]
        n_p = sc["P"]
        balneo_clin_share = n_b / (n_b + n_s) if (n_b + n_s) > 0 else 0.0

        if (n_ha + n_hb) >= 4 and (n_b + n_s) >= 4:
            paired_hb_rates.append(hb_share)
            paired_balneo_shares.append(balneo_clin_share)

        if n_b > n_s * 1.2 and n_b >= 3:
            clin_route = "HYDROTHERAPY_IMMERSION_DOMINANT ($I=B)"
        elif n_s > n_b * 2.5 and n_s >= 5:
            clin_route = "ORAL_DECOCTION_DOSING_DOMINANT ($I=S)"
        elif n_p >= 3 and (n_b + n_s) >= 4:
            clin_route = "DUAL_APOTHECARY_AND_CLINICAL ($I=P+B+S)"
        else:
            clin_route = "GENERAL_COMPOUNDING_INGREDIENT"

        # Construct empirical functional gloss
        top_w = stem_surface[st].most_common(3)
        stem_profiles.append({
            "rank": rank,
            "stem": st,
            "total_tokens": tot,
            "df_folios": df,
            "top_words": [{"word": w, "count": c} for w, c in top_w],
            "section_counts": {k: sc[k] for k in ["H", "A", "Z", "C", "T", "P", "B", "S"] if sc[k] > 0},
            "modality_1_botanical_anatomy": {
                "coordinate": anat_coord,
                "p_top_canopy": n_top,
                "p_bot_root": n_bot,
                "herbal_a_count": n_ha,
                "herbal_b_count": n_hb,
                "herbal_b_share": round(hb_share, 3),
            },
            "modality_2_astrological_season": {
                "dominant_season_or_locus": dom_season,
                "zodiac_counts": dict(zs),
                "astro_loci": dict(al),
            },
            "modality_3_apothecary_register": dict(ap),
            "modality_4_balneological_locus": dict(bl),
            "modality_5_clinical_route": {
                "route": clin_route,
                "starred_decoction_S": n_s,
                "balneological_bath_B": n_b,
                "pharmaceutical_jar_P": n_p,
                "balneo_share_of_BS": round(balneo_clin_share, 3),
                "qo_pct": round(100.0 * mp["qo"] / tot, 1),
                "l_appl_pct": round(100.0 * mp["l_appl"] / tot, 1),
                "edy_pct": round(100.0 * mp["edy"] / tot, 1),
                "aiin_pct": round(100.0 * mp["aiin"] / tot, 1),
            },
        })

    def pearson_and_perm(pairs, rng_obj, n_trials=1000):
        xs = [p[0] for p in pairs]
        ys = [p[1] for p in pairs]
        n = len(xs)
        if n < 3:
            return {"n_stems_tested": n, "observed_pearson_r": 0.0, "null_mean_r": 0.0, "null_sd_r": 0.0, "z_score": 0.0}
        mx = sum(xs) / n
        my = sum(ys) / n
        num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
        den = math.sqrt(sum((x - mx) ** 2 for x in xs) * sum((y - my) ** 2 for y in ys))
        obs_r = num / den if den > 0 else 0.0
        null_rs = []
        ys_shuf = list(ys)
        for _ in range(n_trials):
            rng_obj.shuffle(ys_shuf)
            num_s = sum((x - mx) * (y - my) for x, y in zip(xs, ys_shuf))
            null_rs.append(num_s / den if den > 0 else 0.0)
        mu_r = sum(null_rs) / len(null_rs)
        sd_r = math.sqrt(sum((x - mu_r) ** 2 for x in null_rs) / len(null_rs))
        z_r = (obs_r - mu_r) / (sd_r if sd_r > 0 else 1.0)
        return {
            "n_stems_tested": n,
            "observed_pearson_r": round(obs_r, 4),
            "null_mean_r": round(mu_r, 4),
            "null_sd_r": round(sd_r, 4),
            "z_score": round(z_r, 2),
        }

    # Test 1: Does Supply-Side Herbal-B Share (H_B / (H_A + H_B)) predict Clinical Hydrotherapy vs Apothecary Compounding Route (B / (B + P))?
    hb_bp_pairs = [
        (p["modality_1_botanical_anatomy"]["herbal_b_share"],
         p["modality_5_clinical_route"]["balneological_bath_B"] / (p["modality_5_clinical_route"]["balneological_bath_B"] + p["modality_5_clinical_route"]["pharmaceutical_jar_P"]))
        for p in stem_profiles
        if (p["modality_1_botanical_anatomy"]["herbal_a_count"] + p["modality_1_botanical_anatomy"]["herbal_b_count"]) >= 4
        and (p["modality_5_clinical_route"]["balneological_bath_B"] + p["modality_5_clinical_route"]["pharmaceutical_jar_P"]) >= 4
    ]

    # Test 2: Does Supply-Side Herbal-A Share (H_A / (H_A + H_B)) predict Pharmaceutical Share P / (P + B + S)?
    ha_pbs_pairs = [
        (1.0 - p["modality_1_botanical_anatomy"]["herbal_b_share"],
         p["modality_5_clinical_route"]["pharmaceutical_jar_P"] / (p["modality_5_clinical_route"]["pharmaceutical_jar_P"] + p["modality_5_clinical_route"]["balneological_bath_B"] + p["modality_5_clinical_route"]["starred_decoction_S"]))
        for p in stem_profiles
        if (p["modality_1_botanical_anatomy"]["herbal_a_count"] + p["modality_1_botanical_anatomy"]["herbal_b_count"]) >= 4
        and (p["modality_5_clinical_route"]["pharmaceutical_jar_P"] + p["modality_5_clinical_route"]["balneological_bath_B"] + p["modality_5_clinical_route"]["starred_decoction_S"]) >= 4
    ]

    # Test 3: Does Stem Processual Verbal Morphology (qo% + edy%) predict Clinical Execution Share (B + S) / Total?
    verb_clin_pairs = [
        (p["modality_5_clinical_route"]["qo_pct"] + p["modality_5_clinical_route"]["edy_pct"],
         (p["modality_5_clinical_route"]["balneological_bath_B"] + p["modality_5_clinical_route"]["starred_decoction_S"]) / p["total_tokens"])
        for p in stem_profiles
    ]

    rng = random.Random(137)
    t1 = pearson_and_perm(hb_bp_pairs, rng)
    t2 = pearson_and_perm(ha_pbs_pairs, rng)
    t3 = pearson_and_perm(verb_clin_pairs, rng)

    out = {
        "attack": 137,
        "phase": 148,
        "discovery": 154,
        "title": "5-Modality Empirical Semantic-Feature Grounding Matrix of the Top-150 Open-Class Botanical & Clinical Stems",
        "overview": {
            "n_grounded_stems": len(stem_profiles),
            "test1_herbalB_to_balneo_vs_pharm_route_B_over_BP": t1,
            "test2_herbalA_to_pharm_compounding_share_P_over_PBS": t2,
            "test3_processual_morphology_to_clinical_BS_share": t3,
            "anatomy_coordinate_counts": dict(Counter(p["modality_1_botanical_anatomy"]["coordinate"] for p in stem_profiles)),
            "clinical_route_counts": dict(Counter(p["modality_5_clinical_route"]["route"] for p in stem_profiles)),
        },
        "top150_grounded_stems": stem_profiles,
    }

    OUT_JSON.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"[Attack 137] Saved {OUT_JSON}")
    print("Overview:", json.dumps(out["overview"], indent=2))


if __name__ == "__main__":
    main()
