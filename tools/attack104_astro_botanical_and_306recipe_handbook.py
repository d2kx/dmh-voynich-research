#!/usr/bin/env python3
"""
Attack 104 (Discovery 121): The Astro-Botanical Calendar, Quire 14 Cosmological Companion
& 292-Recipe Stoichiometric Procedural Handbook (`notes/ASTRO_BOTANICAL_AND_306RECIPE_HANDBOOK.md`)

Synthesizes Attacks 101–103 (Discoveries 118–120) into a unified reference edition:
1. Part I: The 12-Medallion Zodiac (`f70v2–f73v`) Astro-Botanical Calendar (`10 / 12 = 83.33%`
   Herbal-B Top-1 Selectivity = `3.39x` Enrichment; Mean Max IDF = `15.496` vs. `13.323` Null,
   $z = +3.34$; Taurus Split-Sign Coherence `+61.8%`; `15.6x` Autumn/Winter `y-` Onset Surge).
2. Part II: The Quire 14 (`f85r1–f86v6` + `fRos`) Cosmological Diagram <-> Prose Treatise
   Exegetical Bridge (`+43.20%` Open-Stem Jaccard Lift over other Currier B prose folios,
   $z = +3.11$; `2.08x` `o- -> qo-` Active Verb Transformation from Diagram to Treatise).
3. Part III: The Quire 20 (`f103r–f116r`, `292` Starred Recipes) Three-Phase Procedural
   Trajectory (`+60.6%` `-aiin` Dose Surge & `+41.4%` `l-` Applicative Surge from Opening
   to Final Line; `5.67x` Opening Gallows Header Drop $z = +15.21$; `0.964` ~ `1:1`
   Stoichiometric Verb-to-Dose Ratio, $r = +0.7476$).
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
NOTES_DIR = ROOT / "notes"

A101_JSON = DATA_DIR / "attack101_zodiac_10sign_nymph_and_herbal_astro_calendar.json"
A102_JSON = DATA_DIR / "attack102_quire14_f85_f86_and_rosettes_bridge.json"
A103_JSON = DATA_DIR / "attack103_quire20_recipe_step_and_dosing_parser.json"

OUT_JSON = DATA_DIR / "attack104_astro_botanical_and_306recipe_handbook.json"
OUT_MD = NOTES_DIR / "ASTRO_BOTANICAL_AND_306RECIPE_HANDBOOK.md"


def main():
    a101 = json.loads(A101_JSON.read_text(encoding="utf-8"))
    a102 = json.loads(A102_JSON.read_text(encoding="utf-8"))
    a103 = json.loads(A103_JSON.read_text(encoding="utf-8"))

    summary = {
        "edition": "ASTRO_BOTANICAL_AND_306RECIPE_HANDBOOK",
        "discoveries_covered": [118, 119, 120, 121],
        "attacks_covered": [101, 102, 103, 104],
        "zodiac_astro_botanical_validation": a101["astro_botanical_validation"],
        "zodiac_calendar_wheel_continuity": a101["calendar_wheel_continuity"],
        "quire14_exegetical_cohesion": a102["quire14_exegetical_cohesion"],
        "quire20_corpus_summary": a103["quire20_corpus_summary"],
        "quire20_stoichiometric_dosing_law": a103["stoichiometric_dosing_law"],
    }
    OUT_JSON.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    md = []
    md.append("# The Astro-Botanical Calendar, Quire 14 Cosmological Companion & Quire 20 Stoichiometric Procedural Handbook (`Attacks 101–104` / `Discoveries 118–121`)")
    md.append("")
    md.append("> **Repository-Relative Asset Links**:")
    md.append("> - **Scripts**: [`tools/attack101_zodiac_10sign_nymph_and_herbal_astro_calendar.py`](../tools/attack101_zodiac_10sign_nymph_and_herbal_astro_calendar.py), [`tools/attack102_quire14_f85_f86_and_rosettes_bridge.py`](../tools/attack102_quire14_f85_f86_and_rosettes_bridge.py), [`tools/attack103_quire20_recipe_step_and_dosing_parser.py`](../tools/attack103_quire20_recipe_step_and_dosing_parser.py), [`tools/attack104_astro_botanical_and_306recipe_handbook.py`](../tools/attack104_astro_botanical_and_306recipe_handbook.py)")
    md.append("> - **Structured Datasets**: [`data/attack101_zodiac_10sign_nymph_and_herbal_astro_calendar.json`](../data/attack101_zodiac_10sign_nymph_and_herbal_astro_calendar.json), [`data/attack102_quire14_f85_f86_and_rosettes_bridge.json`](../data/attack102_quire14_f85_f86_and_rosettes_bridge.json), [`data/attack103_quire20_recipe_step_and_dosing_parser.json`](../data/attack103_quire20_recipe_step_and_dosing_parser.json), [`data/attack104_astro_botanical_and_306recipe_handbook.json`](../data/attack104_astro_botanical_and_306recipe_handbook.json)")
    md.append("")
    md.append("---")
    md.append("")
    md.append("## Part I: The 12-Medallion Zodiac (`f70v2–f73v`) Astro-Botanical Calendar (`Attack 101` / `Discovery 118`)")
    md.append("")
    v101 = a101["astro_botanical_validation"]
    c101 = a101["calendar_wheel_continuity"]
    md.append(f"- **Astro-Botanical Herbal Correspondence ($z = +{v101['z_score']}$)**: Across the `12` Zodiac medallions (`f70v2` Pisces through `f73v` Sagittarius), the mean Top-1 IDF-weighted open-class stem overlap with Herbal Monographs (`$I=H`) is **`{v101['observed_mean_max_idf_across_12_medallions']}` vs. `{v101['null_mean_max_idf']} ± {v101['null_std_max_idf']}` under 300-trial vocabulary-preserving permutation ($z = +{v101['z_score']}$)**.")
    md.append("- **`3.39×` Herbal-B Selectivity (`10 / 12 = 83.33%`)**: Although Herbal-B comprises only `31 / 126` (`24.60%`) of Herbal folios, **`10 / 12` (`83.33%`) of Zodiac medallions match a Herbal-B folio as their `#1` botanical partner (`3.39×` enrichment)**, led by `f43v` (`Quire F, B=3`), `f34r` (`Quire E, B=2`, matching `f73r` Scorpio at `IDF = 23.42` with `8` shared open stems), `f40r`, and `f48r`!")
    md.append(f"- **Taurus Split-Sign Coherence (`+61.8%`) & Distinct Medallion Inventories ($z = {c101['z_calendar_adjacency']}$)**: Facing halves of Taurus (`f71v` Taurus-Light and `f72r1` Taurus-Dark) share **`{c101['taurus_split_pair_f71v_f72r1_jaccard']}` stem Jaccard (`+61.8%` above non-adjacent medallion pairs `{c101['non_adjacent_pairs_mean_jaccard']}`)**, while across different signs each medallion maintains a distinct 30-degree lexical inventory (`adjacent_mean = {c101['calendar_adjacent_11pairs_mean_jaccard']}`, $z = {c101['z_calendar_adjacency']}$). In the split Aries/Taurus medallions, **Dark-Star halves (`f70v1, f72r1`) enrich `-aiin` quantifiers by `1.70×` (`13.48%` vs. `7.95%` Light)**, while across the annual wheel `y-` onset rises **`15.6×` from Spring (`1.14%` on `f71r/f71v`) to Autumn/Winter (`11.83%` on `f72v1` Libra, `17.78%` on `f73v` Sagittarius)**.")
    md.append("")
    md.append("| Zodiac Folio | Zodiac Sign & Month | `#1` Herbal Monograph (`$L`) | Runner-Up Herbal Folios | Shared Open Stems | IDF Overlap Score | Top Shared Astro-Botanical Stems (`Zodiac <-> Herbal`) |")
    md.append("| :---: | :--- | :---: | :--- | :---: | :---: | :--- |")
    for r in a101["twelve_medallion_astro_botanical_correspondences"]:
        runners = ", ".join(f"`{x}`" for x in r["runner_up_herbal_folios"])
        stems = "; ".join(f"`{x}`" for x in r["shared_stems_with_surface_forms"][:4])
        md.append(f"| **`{r['zodiac_folio']}`** | `{r['zodiac_sign']}` | **`{r['top_herbal_folio']}`** (`{r['herbal_lang']}`) | {runners} | `{r['shared_open_stems_count']}` | **`{r['idf_overlap_score']}`** | {stems} |")
    md.append("")
    md.append("---")
    md.append("")
    md.append("## Part II: The Quire 14 (`f85r1–f86v6` + `fRos`) Cosmological Diagram $\\leftrightarrow$ Prose Treatise Exegetical Bridge (`Attack 102` / `Discovery 119`)")
    md.append("")
    q102 = a102["quire14_exegetical_cohesion"]
    t102 = a102["quire14_shared_stem_transformation"]
    md.append(f"- **`+43.20%` Within-Quire Exegetical Stem Cohesion ($z = +{q102['z_score']}$)**: The `4` Quire 14 Prose Treatise surfaces (`f85r1, f86v3, f86v5, f86v6`) share **`{q102['observed_4x4_mean_jaccard']}` mean open-class stem Jaccard** (`{t102['shared_open_stems_count']}` shared open stems = `{t102['pct_of_diagram_stems_in_treatises']}%` of all Diagram open stems) with the `3` Quire 14 Cosmological Diagram surfaces (`f85r2, f86v4, fRos`), beating all other Currier B prose folios (`{q102['other_currier_b_folios_mean_jaccard']}`) by **`+{q102['jaccard_lift_vs_other_currier_b_pct']}%` ($z = +{q102['z_score']}$)**.")
    md.append(f"- **`2.08×` `o- -> qo-` Active Verb Transformation (`Diagrams -> Treatises`)**: Holding the exact `{t102['shared_open_stems_count']}` shared stems fixed, their occurrences on the **Quire 14 Diagrams (`n={t102['diagram_surface_profile']['n_tokens']}`)** are **`{t102['diagram_surface_profile']['o_nominal_pct']}%` Nominal `o-` (`{t102['diagram_surface_profile']['qo_active_pct']}%` `qo-`)**, whereas in the **Quire 14 Prose Treatises (`n={t102['treatise_surface_profile']['n_tokens']}`)** Active `qo-` more than doubles to **`{t102['treatise_surface_profile']['qo_active_pct']}%` (`2.08×`, e.g. `otchdaiin -> qotchdaiin`)** and Applicative `l-/ol-/qol-` rises from **`{t102['diagram_surface_profile']['l_applicative_pct']}% -> {t102['treatise_surface_profile']['l_applicative_pct']}%`**.")
    md.append("")
    md.append("| Quire 14 Diagram Surface | Quire 14 Exegetical Treatise | Shared Open Stems | Open-Stem Jaccard | IDF Overlap Score | Top Shared Cosmological Bridges (`Diagram -> Treatise`) |")
    md.append("| :---: | :---: | :---: | :---: | :---: | :--- |")
    for r in a102["full_4x4_routing_matrix"]:
        bridges = "; ".join(f"`{x}`" for x in r["top_shared_bridges"][:4])
        md.append(f"| **`{r['diagram_folio']}`** | **`{r['treatise_folio']}`** | `{r['shared_open_stems']}` | `{r['jaccard']}` | **`{r['idf_score']}`** | {bridges} |")
    md.append("")
    md.append("---")
    md.append("")
    md.append("## Part III: The Quire 20 (`f103r–f116r`, `292` Starred Recipes) Three-Phase Procedural Trajectory & `1:1` Stoichiometric Dosing Law (`Attack 103` / `Discovery 120`)")
    md.append("")
    s103 = a103["quire20_corpus_summary"]
    d103 = a103["stoichiometric_dosing_law"]
    p103 = a103["three_phase_recipe_trajectory"]
    md.append(f"- **Three-Phase Internal Recipe Trajectory (`{s103['multi_line_recipes_ge3']}` Multi-Line Starred Recipes)**: Moving from `PHASE_1_OPENING_LINE` (`2,358` tokens) through `PHASE_2_MIDDLE_PROCESSING_LINES` (`6,046` tokens) to `PHASE_3_FINAL_CLOSING_LINE` (`1,469` tokens):")
    md.append(f"  1. **Gallows/Header Onsets (`p-/f-/t-/k-/po-/fo-/to-/ko-`)** drop **`5.67×` from `16.62% -> 4.27% -> 2.93%` ($z = +{p103['z_opening_gallows_header']}$)**.")
    md.append("  2. **Imperative Action Verbs (`qo-` and `-edy`)** peak on the **Opening Line (`20.02% qo-`, `17.43% -edy`)** and step down monotonically (`20.02% -> 17.93% -> 13.55% qo-`; `17.43% -> 13.51% -> 12.53% -edy`).")
    md.append("  3. **Liquid Applicatives (`l-/ol-/qol-`)** rise monotonically by **`+41.4%` (`8.57% -> 11.18% -> 12.12%`)**.")
    md.append("  4. **Measured Dose Quantifiers (`-aiin / -ain / -iin`)** surge monotonically by **`+60.6%` (`1.61×`, from `14.84% -> 20.91% -> 23.83%`)** into the final dosing/administration line!")
    md.append(f"- **The `0.964` (`~1:1`) Stoichiometric Verb-to-Dose Scaling Law ($r = +{d103['pearson_r_dose_vs_verb']}$)**: Across all `{s103['total_starred_recipes']}` Starred Recipes (`mean = {s103['mean_tokens_per_recipe']}` tokens, `{s103['mean_lines_per_recipe']}` lines, `{s103['mean_procedural_steps_per_recipe']}` procedural steps), each recipe pairs a mean of **`{d103['mean_measured_doses_per_recipe']}` measured doses/containers** with **`{d103['mean_active_verbs_per_recipe']}` active verbs**, maintaining a **mean per-recipe `Verb : Dose` ratio of `{d103['mean_verb_to_dose_ratio']}` (`~1:1`, Pearson $r = +{d103['pearson_r_dose_vs_verb']}$)**.")
    md.append("")
    md.append("| Internal Recipe Phase | Tokens | Gallows Header `%` | `qo-` Active Verb `%` | `-edy` Processual `%` | `l-/ol-` Applicative `%` | `-aiin` Measured Dose `%` | `-ol/-or` Container `%` |")
    md.append("| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |")
    for ph_name, pv in p103["phase_profiles"].items():
        md.append(f"| `{ph_name}` | `{pv['n_tokens']}` | **`{pv['gallows_header_p_f_t_k_onset_pct']}%`** | **`{pv['qo_active_verb_pct']}%`** | **`{pv['edy_processual_verb_pct']}%`** | **`{pv['l_liquid_applicative_pct']}%`** | **`{pv['aiin_measured_dose_pct']}%`** | `{pv['ol_or_container_pct']}%` |")
    md.append("")

    OUT_MD.write_text("\n".join(md) + "\n", encoding="utf-8")
    print(f"Saved {OUT_JSON} and {OUT_MD}")


if __name__ == "__main__":
    main()
