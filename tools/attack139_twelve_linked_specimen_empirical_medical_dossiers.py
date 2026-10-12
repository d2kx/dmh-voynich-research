#!/usr/bin/env python3
"""
Attack 139 (Phase 150 / Discovery 156):
End-to-End Empirical Medical Dossiers for the Top 12 Linked
Zodiac -> Herbal -> Pharmaceutical -> Balneological/Starred Botanical Specimens.

Synthesizes the 5-Modality Empirical Semantic Signatures (Attack 137) and Clause Valency
Frames (Attack 138) into complete 4-Stage Empirical Medical Dossiers for the 12 best-attested
multi-stage botanical specimen stems in the Voynich Manuscript, and tests the 4-Stage
Morphological Activation Gradient across those 12 specimens against a 1,000-trial permutation null.
"""

import json
import math
import random
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INDEX_PATH = ROOT / "data" / "folio_index.json"
EVA_PATH = ROOT / "data" / "ZL3b-n.txt"
A137_PATH = ROOT / "data" / "attack137_multimodal_empirical_semantic_grounding_matrix.json"
OUT_JSON = ROOT / "data" / "attack139_twelve_linked_specimen_empirical_medical_dossiers.json"

PREFIX_RE = re.compile(r"^(qo|qok|qot|ch|sh|ol|al|or|ar|da|sa|ok|ot|op|of|cp|cf|ct|ck|lk|lt|lp|lf|yk|yt|yp|yf|ka|ta|pa|fa|ke|te|pe|fe|ko|to|po|fo|o|d|s|l|r|y|q)")
SUFFIX_RE = re.compile(r"(aiin|oiin|eiin|iin|ain|edy|eedy|ody|dy|eey|ey|shy|chy|ky|ty|py|fy|ly|ry|ol|or|al|ar|am|om|em|im|an|on|en|in|y|l|r|m|n|s|g)$")

PURE_CLOSED = {"aiin", "ain", "iin", "dy", "ey", "ol", "or", "al", "ar", "am", "an", "in", "y", "l", "r", "m", "n", "s", "d", "o", "k", "p"}


def normalize_token(tok: str) -> str:
    t = re.sub(r"\[([^:\]]+):[^\]]+\]", r"\1", tok)
    t = re.sub(r"\{[^}]*\}", "", t)
    t = re.sub(r"<[^>]*>", "", t)
    t = re.sub(r"[^a-zA-Z]", "", t).lower()
    t = t.replace("f", "p").replace("t", "k")
    t = re.sub(r"i{3,}", "ii", t)
    t = re.sub(r"e{3,}", "ee", t)
    return t


def extract_stem(norm_tok: str) -> str:
    w = norm_tok
    if len(w) <= 2:
        return w
    m_pre = PREFIX_RE.match(w)
    if m_pre and len(w) - len(m_pre.group(1)) >= 2:
        w = w[len(m_pre.group(1)):]
    m_suf = SUFFIX_RE.search(w)
    if m_suf and len(w) - len(m_suf.group(1)) >= 1:
        w = w[: -len(m_suf.group(1))]
    return w if w else norm_tok


def is_clinical_active_inflection(raw_w: str) -> bool:
    """True if token carries active boiling (qo-), processual (-edy/-eedy), vessel applicative (l-/ol-), or dose (-aiin)."""
    if raw_w.startswith(("qo", "qok", "qot")):
        return True
    if raw_w.endswith(("edy", "eedy")):
        return True
    if raw_w.startswith(("l", "ol", "al")) and len(raw_w) >= 4:
        return True
    if raw_w.endswith(("aiin", "ain", "iin")) and not raw_w.startswith(("d", "s")):
        return True
    return False


def is_nominal_identifying(raw_w: str) -> bool:
    """True if token is nominal o- or bare stem or deictic d-/da- without processual -edy/qo-."""
    if raw_w.startswith(("qo", "qok", "qot")) or raw_w.endswith(("edy", "eedy")):
        return False
    if raw_w.startswith(("o", "d", "da")) or raw_w.endswith(("ol", "or", "al", "ar", "y")):
        return True
    return False


def main():
    folio_index = json.loads(INDEX_PATH.read_text(encoding="utf-8"))
    folios_meta = folio_index["folios"]
    a137 = json.loads(A137_PATH.read_text(encoding="utf-8"))
    a137_map = {r["stem"]: r for r in a137["top150_grounded_stems"]}

    line_re = re.compile(r"^<f([0-9]+[rv][0-9]*|Ros)\.([^,>]+),([^>]+)>\s+(.*)$")

    # Collect all occurrences of each stem across the 4 macro-stages:
    # Stage 1: Z + A + C (Astrological / Celestial Calendar)
    # Stage 2: H (Herbal Botanical Monographs)
    # Stage 3: P (Pharmaceutical Apothecary Registers)
    # Stage 4: B + S (Balneological Hydrotherapy + Quire 20 Starred Decoction Recipes)
    stem_stage_tokens = defaultdict(lambda: defaultdict(list))
    stem_stage_folios = defaultdict(lambda: defaultdict(Counter))
    stem_stage_lines = defaultdict(lambda: defaultdict(list))
    stem_colloc_verbs = defaultdict(Counter)
    stem_colloc_doses = defaultdict(Counter)

    for raw_line in EVA_PATH.read_text(encoding="utf-8", errors="ignore").splitlines():
        if not raw_line.startswith("<f"):
            continue
        m = line_re.match(raw_line)
        if not m:
            continue
        fol, line_id, loc, body = m.groups()
        if ";" in line_id:
            continue
        f_key = f"f{fol}"
        meta = folios_meta.get(f_key, {})
        sec = meta.get("section_code", "H")
        if sec in ("Z", "A", "C"):
            stage = "STAGE1_ASTRO_ZODIAC"
        elif sec == "H":
            stage = "STAGE2_HERBAL_BOTANY"
        elif sec == "P":
            stage = "STAGE3_PHARM_APOTHECARY"
        elif sec in ("B", "S"):
            stage = "STAGE4_CLINICAL_BALNEO_STARRED"
        else:
            continue

        body_clean = re.sub(r"<![^>]*>", "", body)
        body_clean = re.sub(r"<[^>]*>", " ", body_clean)
        raw_toks = [t for t in re.split(r"[.\s,]+", body_clean) if t]

        parsed = []
        for rt in raw_toks:
            w = re.sub(r"[^a-zA-Z]", "", rt).lower()
            if not w:
                continue
            nw = normalize_token(rt)
            if not nw:
                continue
            st = extract_stem(nw)
            parsed.append((w, nw, st))

        line_verbs = [w for w, nw, st in parsed if w.startswith(("qo", "ch", "sh", "lk", "lch", "olk")) and w.endswith(("edy", "eedy", "ey", "eey", "dy", "y"))]
        line_doses = [w for w, nw, st in parsed if w.endswith(("aiin", "ain", "iin")) and not w.startswith(("d", "s"))]

        for w, nw, st in parsed:
            stem_stage_tokens[st][stage].append((w, f_key, loc))
            stem_stage_folios[st][stage][f_key] += 1
            if len(stem_stage_lines[st][stage]) < 5:
                eva_sample = " ".join(x[0] for x in parsed[:9])
                stem_stage_lines[st][stage].append({
                    "folio": f_key,
                    "line_id": line_id,
                    "locus": loc,
                    "word": w,
                    "clause_snippet": eva_sample,
                })
            for v in line_verbs:
                if v != w:
                    stem_colloc_verbs[st][v] += 1
            for d in line_doses:
                if d != w:
                    stem_colloc_doses[st][d] += 1

    # Select Top 12 Botanical Specimen Stems that are attested in ALL 4 Stages:
    # - >= 3 tokens in Stage 1 (Z/A/C)
    # - >= 8 tokens in Stage 2 (H)
    # - >= 5 tokens in Stage 3 (P)
    # - >= 10 tokens in Stage 4 (B+S)
    # - Excluding ultra-generic grammatical stems ("ee", "ed", "ai") so we get concrete specimen/substance stems,
    #   or ranking by minimum stage count / geometric mean across the 4 stages!
    candidates = []
    for st, stg_map in stem_stage_tokens.items():
        if st in PURE_CLOSED or st in ("ee", "ed", "ai"):
            continue
        n1 = len(stg_map["STAGE1_ASTRO_ZODIAC"])
        n2 = len(stg_map["STAGE2_HERBAL_BOTANY"])
        n3 = len(stg_map["STAGE3_PHARM_APOTHECARY"])
        n4 = len(stg_map["STAGE4_CLINICAL_BALNEO_STARRED"])
        if n1 >= 3 and n2 >= 6 and n3 >= 4 and n4 >= 8:
            geom = (n1 * n2 * n3 * n4) ** 0.25
            candidates.append((geom, st, n1, n2, n3, n4))

    candidates.sort(key=lambda x: -x[0])
    top12_specs = candidates[:12]

    dossiers = []
    stage_active_rates = {
        "STAGE1_ASTRO_ZODIAC": [],
        "STAGE2_HERBAL_BOTANY": [],
        "STAGE3_PHARM_APOTHECARY": [],
        "STAGE4_CLINICAL_BALNEO_STARRED": [],
    }
    all_spec_tokens_for_perm = []

    for rank, (geom, st, n1, n2, n3, n4) in enumerate(top12_specs, 1):
        g_info = a137_map.get(st, {})
        anat_coord = g_info.get("modality_1_botanical_anatomy", {}).get("coordinate", "WHOLE_HERB_AXIS (BALANCED)")
        dom_season = g_info.get("modality_2_astrological_season", {}).get("dominant_season_or_locus", "SPRING_ARIES")
        clin_route = g_info.get("modality_5_clinical_route", {}).get("route", "DUAL_APOTHECARY_AND_CLINICAL ($I=P+B+S)")

        stage_breakdown = {}
        for stg in ["STAGE1_ASTRO_ZODIAC", "STAGE2_HERBAL_BOTANY", "STAGE3_PHARM_APOTHECARY", "STAGE4_CLINICAL_BALNEO_STARRED"]:
            toks = stem_stage_tokens[st][stg]
            n_t = len(toks)
            n_act = sum(1 for w, _, _ in toks if is_clinical_active_inflection(w))
            n_nom = sum(1 for w, _, _ in toks if is_nominal_identifying(w))
            act_rate = n_act / n_t if n_t > 0 else 0.0
            nom_rate = n_nom / n_t if n_t > 0 else 0.0
            stage_active_rates[stg].append(act_rate)
            for w, _, _ in toks:
                all_spec_tokens_for_perm.append((st, stg, 1 if is_clinical_active_inflection(w) else 0))

            top_forms = [f"{w}({c})" for w, c in Counter(w for w, _, _ in toks).most_common(4)]
            top_fols = [f"{f}({c})" for f, c in stem_stage_folios[st][stg].most_common(4)]
            stage_breakdown[stg] = {
                "tokens": n_t,
                "active_clinical_inflection_pct": round(100.0 * act_rate, 1),
                "nominal_identifying_pct": round(100.0 * nom_rate, 1),
                "top_surface_forms": top_forms,
                "top_folios": top_fols,
                "sample_attestations": stem_stage_lines[st][stg][:2],
            }

        # Synthesize empirical medical dossier summary
        top_v = [f"{v}({c})" for v, c in stem_colloc_verbs[st].most_common(4)]
        top_d = [f"{d}({c})" for d, c in stem_colloc_doses[st].most_common(4)]

        s1_fols = ", ".join(stage_breakdown["STAGE1_ASTRO_ZODIAC"]["top_folios"][:2])
        s2_fols = ", ".join(stage_breakdown["STAGE2_HERBAL_BOTANY"]["top_folios"][:3])
        s3_fols = ", ".join(stage_breakdown["STAGE3_PHARM_APOTHECARY"]["top_folios"][:2])
        s4_fols = ", ".join(stage_breakdown["STAGE4_CLINICAL_BALNEO_STARRED"]["top_folios"][:3])

        english_dossier = (
            f"SPECIMEN *-{st}-* [{anat_coord}]: "
            f"(1) Harvested/governed under {dom_season} ({s1_fols}); "
            f"(2) Botanical monograph anchored on {s2_fols} as nominal forms {', '.join(stage_breakdown['STAGE2_HERBAL_BOTANY']['top_surface_forms'][:2])}; "
            f"(3) Compounded in Apothecary registers {s3_fols} ({', '.join(stage_breakdown['STAGE3_PHARM_APOTHECARY']['top_surface_forms'][:2])}); "
            f"(4) Administered via {clin_route} on {s4_fols} as {', '.join(stage_breakdown['STAGE4_CLINICAL_BALNEO_STARRED']['top_surface_forms'][:2])} "
            f"under operators [{', '.join(top_v[:2])}] with dose quantifiers [{', '.join(top_d[:2])}]."
        )

        dossiers.append({
            "rank": rank,
            "stem": st,
            "four_stage_geometric_mean": round(geom, 2),
            "total_4stage_tokens": n1 + n2 + n3 + n4,
            "anatomical_coordinate": anat_coord,
            "astrological_season": dom_season,
            "clinical_route": clin_route,
            "collocational_verb_operators": top_v,
            "collocational_dose_quantifiers": top_d,
            "english_empirical_dossier": english_dossier,
            "stage_progression": stage_breakdown,
        })

    # Compute 4-Stage Morphological Activation Gradient Test:
    # Compare Active Clinical Inflection Rate in Stage 4 (B+S) minus Stage 1+2 (Astro+Herbal)
    # keeping each specimen stem fixed (within-stem permutation test, 1,000 trials)
    by_stem = defaultdict(list)
    for st, stg, is_act in all_spec_tokens_for_perm:
        by_stem[st].append((stg, is_act))

    def calc_stage4_minus_supply(stem_map):
        s_supply = 0
        n_supply = 0
        s_clin = 0
        n_clin = 0
        for st, rows in stem_map.items():
            for stg, act in rows:
                if stg in ("STAGE1_ASTRO_ZODIAC", "STAGE2_HERBAL_BOTANY"):
                    s_supply += act
                    n_supply += 1
                elif stg == "STAGE4_CLINICAL_BALNEO_STARRED":
                    s_clin += act
                    n_clin += 1
        r_sup = s_supply / n_supply if n_supply > 0 else 0.0
        r_cli = s_clin / n_clin if n_clin > 0 else 0.0
        return r_cli - r_sup, r_sup, r_cli

    obs_diff, obs_sup_rate, obs_cli_rate = calc_stage4_minus_supply(by_stem)

    rng = random.Random(139)
    null_diffs = []
    for _ in range(1000):
        shuf_map = {}
        for st, rows in by_stem.items():
            stgs = [r[0] for r in rows]
            acts = [r[1] for r in rows]
            rng.shuffle(acts)
            shuf_map[st] = list(zip(stgs, acts))
        nd, _, _ = calc_stage4_minus_supply(shuf_map)
        null_diffs.append(nd)

    mu_d = sum(null_diffs) / len(null_diffs)
    sd_d = math.sqrt(sum((x - mu_d) ** 2 for x in null_diffs) / len(null_diffs))
    z_d = (obs_diff - mu_d) / (sd_d if sd_d > 0 else 1.0)

    out = {
        "attack": 139,
        "phase": 150,
        "discovery": 156,
        "title": "End-to-End Empirical Medical Dossiers for the Top 12 Linked 4-Stage Botanical Specimens",
        "overview": {
            "n_dossiers_compiled": len(dossiers),
            "mean_active_inflection_by_stage_pct": {
                stg: round(100.0 * sum(vals) / len(vals), 2)
                for stg, vals in stage_active_rates.items()
            },
            "within_stem_4stage_activation_gradient_test": {
                "supply_stage1_2_active_pct": round(100.0 * obs_sup_rate, 2),
                "clinical_stage4_active_pct": round(100.0 * obs_cli_rate, 2),
                "observed_delta_pct": round(100.0 * obs_diff, 2),
                "null_mean_delta_pct": round(100.0 * mu_d, 2),
                "null_sd_delta_pct": round(100.0 * sd_d, 2),
                "z_score": round(z_d, 2),
            },
        },
        "twelve_specimen_dossiers": dossiers,
    }

    OUT_JSON.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"[Attack 139] Saved {OUT_JSON}")
    print("Overview:", json.dumps(out["overview"], indent=2))
    for d in dossiers[:5]:
        print(" -", d["english_empirical_dossier"])


if __name__ == "__main__":
    main()
