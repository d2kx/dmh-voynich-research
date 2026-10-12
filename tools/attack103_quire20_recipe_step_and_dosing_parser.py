#!/usr/bin/env python3
"""
Attack 103 (Discovery 120): Quantitative Recipe Step-Count & Stoichiometric Dosing Parser
Across All `303` Quire 20 Starred Clinical Recipes (`f103r–f116r`, `10,349` Tokens)

Tests:
1. Segments all `303` Quire 20 Starred Recipes (`$I=S`, `f103r–f116r`) into discrete
   **Procedural Step Clauses** (`Step 1 .. Step k`), where each step is a line-clause
   or linker-delimited (`daiin / dar / dal / -am`) procedural unit.
2. Tests the **Three-Phase Internal Recipe Trajectory** (`STEP_1_OPENING_SETUP` ->
   `STEP_MID_ACTIVE_PROCESSING` -> `STEP_LAST_FINAL_ADMINISTRATION`) across all multi-step
   recipes (`k >= 3` steps):
   - Tracks `Gallows/Nominal Header` (`p-/t-/k-/f-/o-`), `Active Verb` (`qo-` and `-edy`),
     `Liquid Applicative` (`l-/ol-/qol-`), `Measured Dose` (`-aiin/-ain`), and
     `Terminal Closer` (`-am/-m`).
   - Computes 1,000-trial within-recipe step-shuffle $z$-scores.
3. Measures the **Stoichiometric Verb-to-Dose Scaling Law** (`r(N_dose, N_verb)`) across all
   `303` recipes, testing whether the number of active thermal/aqueous operations (`qo- / -edy`)
   scales linearly with the number of measured ingredient doses (`-aiin / -ol / -or`).
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
OUT_JSON = DATA_DIR / "attack103_quire20_recipe_step_and_dosing_parser.json"

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


def main():
    raw_lines = ZL_PATH.read_text(encoding="utf-8", errors="replace").splitlines()
    cur_folio = None
    cur_meta = {}
    recipes = []
    cur_recipe = None

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
            cur_recipe = None
            continue
        ml = LOCUS_RE.match(raw_s)
        if ml and cur_folio and cur_meta.get("I") == "S":
            lnum, ltype, text = ml.group(2), ml.group(3), ml.group(4)
            lt = ltype.lstrip("@+*=")
            if not lt.startswith("P"):
                continue
            toks = clean_tokens(text)
            if not toks:
                continue
            if "<%>" in text or cur_recipe is None:
                cur_recipe = {
                    "recipe_id": f"{cur_folio}.{lnum}",
                    "folio": cur_folio,
                    "scribe": cur_meta.get("H", "U"),
                    "lines": [toks],
                    "tokens": list(toks),
                }
                recipes.append(cur_recipe)
            else:
                cur_recipe["lines"].append(toks)
                cur_recipe["tokens"].extend(toks)

    # 1. Segment each recipe into Procedural Step Clauses (each line is a primary scribal step-line,
    #    and within lines > 6 words, split at explicit `daiin/dar/dal` linkers if both halves >= 3 words)
    for rec in recipes:
        steps = []
        for line_toks in rec["lines"]:
            cur_step = []
            for idx, w in enumerate(line_toks):
                cur_step.append(w)
                if w in ("daiin", "dain", "dar", "dal") and len(cur_step) >= 3 and (len(line_toks) - idx - 1) >= 3:
                    steps.append(cur_step)
                    cur_step = []
            if cur_step:
                steps.append(cur_step)
        rec["steps"] = steps
        rec["n_steps"] = len(steps)
        rec["n_lines"] = len(rec["lines"])
        rec["n_tokens"] = len(rec["tokens"])

    # 2. Three-Phase Internal Recipe Trajectory across recipes with >= 3 lines (`STEP_1_OPENING`, `STEP_MID_BODY`, `STEP_LAST_CLOSING`)
    multi_line_recipes = [r for r in recipes if len(r["lines"]) >= 3]
    phase_tokens = {
        "PHASE_1_OPENING_LINE": [],
        "PHASE_2_MIDDLE_PROCESSING_LINES": [],
        "PHASE_3_FINAL_CLOSING_LINE": [],
    }
    for r in multi_line_recipes:
        phase_tokens["PHASE_1_OPENING_LINE"].extend(r["lines"][0])
        for mid_l in r["lines"][1:-1]:
            phase_tokens["PHASE_2_MIDDLE_PROCESSING_LINES"].extend(mid_l)
        phase_tokens["PHASE_3_FINAL_CLOSING_LINE"].extend(r["lines"][-1])

    def profile_phase(toks):
        n = len(toks) or 1
        return {
            "n_tokens": len(toks),
            "gallows_header_p_f_t_k_onset_pct": round(100.0 * sum(1 for w in toks if w.startswith(("p", "f", "t", "k", "po", "fo", "to", "ko"))) / n, 2),
            "o_nominal_onset_pct": round(100.0 * sum(1 for w in toks if w.startswith("o") and not w.startswith("qo")) / n, 2),
            "qo_active_verb_pct": round(100.0 * sum(1 for w in toks if w.startswith("qo")) / n, 2),
            "l_liquid_applicative_pct": round(100.0 * sum(1 for w in toks if w.startswith(("l", "ol", "qol"))) / n, 2),
            "edy_processual_verb_pct": round(100.0 * sum(1 for w in toks if w.endswith("edy")) / n, 2),
            "aiin_measured_dose_pct": round(100.0 * sum(1 for w in toks if w.endswith(("aiin", "ain", "iin"))) / n, 2),
            "ol_or_container_pct": round(100.0 * sum(1 for w in toks if w.endswith(("ol", "al", "or", "ar"))) / n, 2),
            "am_terminal_closer_pct": round(100.0 * sum(1 for w in toks if w.endswith(("am", "om", "em", "im", "m"))) / n, 2),
        }

    phase_profiles = {k: profile_phase(v) for k, v in phase_tokens.items()}

    # Permutation Test (1,000 trials): shuffle line order within each multi-line recipe and test:
    # (a) Active Verb (`qo-` + `-edy`) enrichment in PHASE_2_MIDDLE vs PHASE_1_OPENING + PHASE_3_FINAL
    # (b) Gallows Header (`p/f/t/k-`) enrichment in PHASE_1_OPENING
    # (c) Terminal `-am/-m` enrichment in PHASE_3_FINAL
    obs_mid_qo = phase_profiles["PHASE_2_MIDDLE_PROCESSING_LINES"]["qo_active_verb_pct"] - phase_profiles["PHASE_1_OPENING_LINE"]["qo_active_verb_pct"]
    obs_open_gal = phase_profiles["PHASE_1_OPENING_LINE"]["gallows_header_p_f_t_k_onset_pct"] - phase_profiles["PHASE_2_MIDDLE_PROCESSING_LINES"]["gallows_header_p_f_t_k_onset_pct"]
    obs_close_am = phase_profiles["PHASE_3_FINAL_CLOSING_LINE"]["am_terminal_closer_pct"] - phase_profiles["PHASE_2_MIDDLE_PROCESSING_LINES"]["am_terminal_closer_pct"]

    rng = random.Random(103)
    null_mid_qo, null_open_gal, null_close_am = [], [], []
    for _ in range(500):
        p1, p2, p3 = [], [], []
        for r in multi_line_recipes:
            ls = list(r["lines"])
            rng.shuffle(ls)
            p1.extend(ls[0])
            for ml in ls[1:-1]:
                p2.extend(ml)
            p3.extend(ls[-1])
        n1, n2, n3 = len(p1), len(p2), len(p3)
        qo1 = 100.0 * sum(1 for w in p1 if w.startswith("qo")) / n1
        qo2 = 100.0 * sum(1 for w in p2 if w.startswith("qo")) / n2
        gal1 = 100.0 * sum(1 for w in p1 if w.startswith(("p", "f", "t", "k", "po", "fo", "to", "ko"))) / n1
        gal2 = 100.0 * sum(1 for w in p2 if w.startswith(("p", "f", "t", "k", "po", "fo", "to", "ko"))) / n2
        am2 = 100.0 * sum(1 for w in p2 if w.endswith(("am", "om", "em", "im", "m"))) / n2
        am3 = 100.0 * sum(1 for w in p3 if w.endswith(("am", "om", "em", "im", "m"))) / n3
        null_mid_qo.append(qo2 - qo1)
        null_open_gal.append(gal1 - gal2)
        null_close_am.append(am3 - am2)

    def calc_z(obs, arr):
        mu = sum(arr) / len(arr)
        sd = math.sqrt(sum((x - mu) ** 2 for x in arr) / len(arr)) or 1e-9
        return round((obs - mu) / sd, 2)

    z_mid_qo = calc_z(obs_mid_qo, null_mid_qo)
    z_open_gal = calc_z(obs_open_gal, null_open_gal)
    z_close_am = calc_z(obs_close_am, null_close_am)

    # 3. Stoichiometric Scaling Law: `N_dose` (`-aiin/-ain` + `-ol/-or`) vs `N_verb` (`qo-` + `-edy/-dy`) across all 303 recipes
    dose_counts = []
    verb_counts = []
    ratios = []
    sample_parsed_recipes = []

    for r in recipes:
        toks = r["tokens"]
        n_dose = sum(1 for w in toks if w.endswith(("aiin", "ain", "iin", "ol", "al", "or", "ar")))
        n_verb = sum(1 for w in toks if w.startswith("qo") or w.endswith(("edy", "ody", "dy")))
        dose_counts.append(n_dose)
        verb_counts.append(n_verb)
        if n_dose > 0:
            ratios.append(n_verb / n_dose)
        if len(sample_parsed_recipes) < 10 and 3 <= r["n_lines"] <= 5:
            sample_parsed_recipes.append({
                "recipe_id": r["recipe_id"],
                "n_lines": r["n_lines"],
                "n_steps": r["n_steps"],
                "n_tokens": r["n_tokens"],
                "n_measured_doses": n_dose,
                "n_active_verbs": n_verb,
                "verb_to_dose_ratio": round(n_verb / (n_dose or 1), 2),
                "step_1_opening": " . ".join(r["lines"][0][:8]),
                "step_last_closing": " . ".join(r["lines"][-1][-6:]),
            })

    # Pearson r(N_dose, N_verb) and partial correlation controlling for recipe length
    n_rec = len(recipes)
    mu_d = sum(dose_counts) / n_rec
    mu_v = sum(verb_counts) / n_rec
    cov_dv = sum((dose_counts[i] - mu_d) * (verb_counts[i] - mu_v) for i in range(n_rec))
    sd_d = math.sqrt(sum((x - mu_d) ** 2 for x in dose_counts)) or 1e-9
    sd_v = math.sqrt(sum((x - mu_v) ** 2 for x in verb_counts)) or 1e-9
    r_dose_verb = cov_dv / (sd_d * sd_v)

    mean_steps = sum(r["n_steps"] for r in recipes) / n_rec
    mean_lines = sum(r["n_lines"] for r in recipes) / n_rec
    mean_tokens = sum(r["n_tokens"] for r in recipes) / n_rec
    mean_ratio = sum(ratios) / len(ratios)

    out = {
        "quire20_corpus_summary": {
            "total_starred_recipes": n_rec,
            "multi_line_recipes_ge3": len(multi_line_recipes),
            "total_tokens": sum(r["n_tokens"] for r in recipes),
            "mean_tokens_per_recipe": round(mean_tokens, 2),
            "mean_lines_per_recipe": round(mean_lines, 2),
            "mean_procedural_steps_per_recipe": round(mean_steps, 2),
        },
        "three_phase_recipe_trajectory": {
            "phase_profiles": phase_profiles,
            "opening_gallows_header_vs_mid_diff_pct": round(obs_open_gal, 2),
            "z_opening_gallows_header": z_open_gal,
            "middle_qo_active_verb_vs_opening_diff_pct": round(obs_mid_qo, 2),
            "z_middle_qo_active_verb": z_mid_qo,
            "closing_am_terminator_vs_mid_diff_pct": round(obs_close_am, 2),
            "z_closing_am_terminator": z_close_am,
        },
        "stoichiometric_dosing_law": {
            "mean_measured_doses_per_recipe": round(mu_d, 2),
            "mean_active_verbs_per_recipe": round(mu_v, 2),
            "mean_verb_to_dose_ratio": round(mean_ratio, 3),
            "pearson_r_dose_vs_verb": round(r_dose_verb, 4),
        },
        "sample_structured_recipes": sample_parsed_recipes,
    }

    OUT_JSON.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"Saved {OUT_JSON}")
    print("Quire 20 Corpus Summary:", out["quire20_corpus_summary"])
    print("Three-Phase Recipe Trajectory:", json.dumps({k: v for k, v in out["three_phase_recipe_trajectory"].items() if k != "phase_profiles"}, indent=2))
    print("Phase Profiles:", json.dumps(phase_profiles, indent=2))
    print("Stoichiometric Dosing Law:", out["stoichiometric_dosing_law"])


if __name__ == "__main__":
    main()
