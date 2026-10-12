#!/usr/bin/env python3
"""
Attack 136 (Phase 147 / Discovery 153):
Complete 9-Sphere Rosettes (`fRos`) Router, 842-Stem Cross-Section Canonical
Root Dictionary & Universal Folio-Discourse Master Compendium Generator.

Synthesizes:
- Attack 133 (Discovery 150): Complete 10-Zone (`CIRCLE_1_NW` .. `CIRCLE_9_SE` +
  `CAUSEWAYS_I_TO_VIII`) Rosettes Map (`fRos`, `518` tokens) Translator and the
  `f66r <-> fRos <-> Quire 20` Master Routing Triad (`10.91x` lift, `z = +8.26`).
- Attack 134 (Discovery 151): Complete `842`-Stem Multi-Folio Cross-Section
  Canonical Root Dictionary (`34,705` tokens) & Within-Stem Supply-to-Clinical
  Inflectional Transformation Law (`220` paired stems, `z = +7.08`).
- Attack 135 (Discovery 152): Universal Intra-Folio Discourse Architecture
  Across All `226` Folios (`TOP_LINE_1 -> INTERIOR_LINES -> BOTTOM_LINE_N`
  vertical frame & `Para 1 -> Para 2..K` Rare-Stem Topic Persistence, `z = +2.82`).
- Generates `data/attack136_rosettes_stem_dict_and_discourse_compendium.json`
  and `notes/ROSETTES_9SPHERE_AND_CROSS_SECTION_ROOT_DICTIONARY.md`.
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
A133_JSON = ROOT / "data" / "attack133_rosettes_9sphere_and_f66r_master_router.json"
A134_JSON = ROOT / "data" / "attack134_complete_cross_section_stem_dictionary.json"
A135_JSON = ROOT / "data" / "attack135_universal_folio_discourse_and_stem_introduction_law.json"
OUT_JSON = ROOT / "data" / "attack136_rosettes_stem_dict_and_discourse_compendium.json"
OUT_MD = ROOT / "notes" / "ROSETTES_9SPHERE_AND_CROSS_SECTION_ROOT_DICTIONARY.md"


def main():
    d133 = json.loads(A133_JSON.read_text(encoding="utf-8"))
    d134 = json.loads(A134_JSON.read_text(encoding="utf-8"))
    d135 = json.loads(A135_JSON.read_text(encoding="utf-8"))

    summary_out = {
        "attack": 136,
        "phase": 147,
        "discovery": 153,
        "title": "Complete 9-Sphere Rosettes (fRos) Router, 842-Stem Cross-Section Root Dictionary & Universal Folio-Discourse Master Compendium",
        "wave31_highlights": {
            "f66r_fros_quire20_triad_z": d133["f66r_fros_quire20_triad_test"]["z_score"],
            "f66r_fros_quire20_triad_lift": d133["f66r_fros_quire20_triad_test"]["lift_ratio"],
            "n_multi_folio_stems": d134["overview"]["n_multi_folio_stems"],
            "within_stem_clinical_shift_z": d134["overview"]["within_stem_supply_to_clinical_shift_test"]["z_score"],
            "proc_edy_within_stem_lift": d134["overview"]["within_stem_supply_to_clinical_shift_test"]["slot_shift_summary"]["PROC_EDY"]["ratio_clinical_over_supply"],
            "appl_l_within_stem_lift": d134["overview"]["within_stem_supply_to_clinical_shift_test"]["slot_shift_summary"]["APPL_L"]["ratio_clinical_over_supply"],
            "same_folio_p1_p2_persistence_z": d135["same_folio_p1_to_p2plus_topic_persistence_test"]["z_score"],
        },
    }
    OUT_JSON.write_text(json.dumps(summary_out, indent=2), encoding="utf-8")

    md = []
    md.append("# Complete 9-Sphere Rosettes (`fRos`) Router, 842-Stem Cross-Section Root Dictionary & Universal Folio-Discourse Compendium (`Attacks 133–136` / `Discoveries 150–153`)\n")
    md.append("> **Scope**: This compendium synthesizes **Autonomous Wave 31 (`Phases 144–147` / `Attacks 133–136` / `Discoveries 150–153`)**, presenting (1) the complete 10-Zone (`CIRCLE_1_NW` .. `CIRCLE_9_SE` + `CAUSEWAYS_I_TO_VIII`) structural translation of `fRos` and the `f66r <-> fRos <-> Quire 20` Master Routing Triad ($z = +8.26$), (2) the complete `842`-Stem Multi-Folio Cross-Section Canonical Root Dictionary (`34,705` tokens) & Within-Stem Supply-to-Clinical Inflectional Transformation Law ($z = +7.08$), and (3) the Universal Intra-Folio Discourse Architecture across all `226` folios ($z = +2.82$).\n\n")

    md.append("---\n")
    md.append("## Part I: Executive Summary of Wave 31 Discoveries (`Discoveries 150–153`)\n")
    md.append("1. **Discovery 150 (`Attack 133` — Complete 10-Zone Rosettes Map `fRos` Translator & `f66r <-> fRos <-> Quire 20` Master Routing Triad, `10.91×` Lift, $z = +8.26$)**:\n")
    md.append("   - Mapping all `160` lines (`509` tokens) of `fRos` via their Petersen circle tags (`<!1:...>` .. `<!9:...>`) and Roman causeway tags (`<!I>` .. `<!VIII>`) into **9 Rosette Spheres (`CIRCLE_1_NW` .. `CIRCLE_9_SE`)** plus **Connecting Causeways (`CAUSEWAYS_I_TO_VIII`)** reveals:\n")
    md.append("     - **`CAUSEWAYS_I_TO_VIII` (`24` lines, `46` words)**: Dominant external section = **`Balneological ($I=B)`**, with **`8.70%` `qo-` active flow/boiling (`5.0×` higher than the 9 Circles' `1.72%` mean)** and lowest `o-` nominal rate (`41.30%` vs. `55.3%` in the 9 Circles) — visually confirmed on [pages/fRos_center_and_east_spheres_causeways_enh.png](../pages/fRos_center_and_east_spheres_causeways_enh.png) where the causeways are stepped hydraulic water conduits connecting the spheres.\n")
    md.append("     - **`CIRCLE_5_CENTER` (`25` lines, `67` words, containing 5 bulbous apothecary/botanical vessels) & `CIRCLE_7_NE` (`15` lines, `70` words)**: Dominant external section = **`Herbal ($I=H)`**, with `CIRCLE_5_CENTER`'s `#1` external folio match = **`f58r` (`Quire H` Starred Botanical Master Index, `IDF = 8.361`: `pchee, kal, py`)** and `CIRCLE_7_NE` matching **`f95r1` (`Quire Q` Scribe 3 Herbal Foldout, `IDF = 5.960`)**.\n")
    md.append("     - **`CIRCLE_8_E` (`36` words) & `CIRCLE_3_SW` (`66` words, Brumbaugh's Starred Clock)**: `#1` external match of `CIRCLE_8_E` = **`f66r` (`IDF = 13.262`: `fchd, far, kar, ad`)**, while `CIRCLE_3_SW` links to **`f105v` (`Quire 20 $B=3`, `IDF = 13.897`)**, **`f86v6` (`IDF = 13.204`)**, and **`f66r` (`IDF = 10.571`)**.\n")
    md.append("     - **The `f66r ($I=T) <-> fRos ($I=C) <-> Quire 20 ($I=S)` Master Routing Triad**: Shares **`9` rare stems (`fchd, xa, far, pchee, efch, kar, pd, ral, ad`)** with a combined Triad IDF of **`29.307` vs. `2.686 ± 3.222` random folio-pair null (`10.91×` lift, $z = +8.26, p < 0.0001$)**.\n\n")

    md.append("2. **Discovery 151 (`Attack 134` — Complete `842`-Stem Multi-Folio Cross-Section Root Dictionary & Paired Within-Stem Supply-to-Clinical Transformation Law, $z = +7.08$)**:\n")
    md.append("   - Catalogues all **`842` multi-folio canonical stems (`df >= 2` folios, covering `34,705` tokens = `95.8%` of the manuscript)** into `6` functional semantic classes: `58` Core Grammatical/Universal Roots (`df > 45`), `225` Pan-Medical Cross-Section Hubs (`>= 4` sections bridging Supply & Clinical), `153` Apothecary Decoction Specimens (`H/P -> S`), `58` Balneological Hydrotherapy Specimens (`H/Z/C -> B`), `47` Celestial/Cosmological Terms (`A/Z/C`), and `301` Botanical/Section-Local Stems.\n")
    md.append("   - Across all **`220` paired stems** attested `>= 3` times in both **Supply/Diagram Sections (`H ∪ A ∪ Z ∪ C`)** and **Clinical Application Sections (`B ∪ P ∪ S`)** — holding the **exact same canonical stem fixed** — moving from Supply to Clinical drives:\n")
    md.append("     - **`3.04×` surge in Processual Simmering `-edy/-eedy` (`2.48% -> 7.54%`, `+5.06%`)**\n")
    md.append("     - **`2.71×` surge in Vessel/Bath Applicative `l-/ol-/al-` (`4.52% -> 12.26%`, `+7.74%`)**\n")
    md.append("     - **`1.54×` surge in Active Boiling `qo-` (`6.56% -> 10.07%`, `+3.51%`)**\n")
    md.append("     - **`-25.9%` drop in Nominal Citation `o-` (`18.72% -> 13.87%`)** and **`-30.5%` drop in Deictic Topic Header `d-` (`11.34% -> 7.88%`)**\n")
    md.append("   - In a `1,000`-trial paired within-stem sign-flip permutation test, the mean Clinical-minus-Supply shift of **`+0.2247` vs. `-0.0007 ± 0.0318` null achieves $z = +7.08$ ($p < 10^{-11}$)**.\n\n")

    md.append("3. **Discovery 152 (`Attack 135` — Universal Intra-Folio Discourse Architecture Across All `226` Folios: Vertical Folio Frame & `Para 1 -> Para 2..K` Topic Persistence, $z = +2.82$)**:\n")
    md.append("   - Across all `@P` prose folios (`>= 3` lines), moving from **`TOP_LINE_1`** to **`INTERIOR_LINES`** to **`BOTTOM_LINE_N`** produces a universal vertical frame:\n")
    md.append("     - **Mean Word Length** compresses monotonically: **`5.601` chars (`TOP_LINE_1`) $\to$ `5.188` chars (`INTERIOR`) $\to$ `4.974` chars (`BOTTOM_LINE_N`)**.\n")
    md.append("     - **Top-Line Gallows (`p/f` / `op/of` / `cph/cfh`)** drops **`15.7×`**: **`18.56%` (`TOP_LINE_1`) $\to$ `3.33%` (`INTERIOR`) $\to$ `1.18%` (`BOTTOM_LINE_N`)**.\n")
    md.append("     - **Active `qo-` & Processual `-edy`** peak in `INTERIOR_LINES` (**`16.25%` `qo-`, `12.56%` `-edy`**) and drop by more than half at `BOTTOM_LINE_N` (**`7.07%` `qo-`, `5.59%` `-edy`**).\n")
    md.append("     - **Measured Dose `-aiin` (`11.40% -> 11.71% -> 14.03%`)** and **Terminal Closure `-am/-m` (`1.75% -> 2.67% -> 3.04%`, `1.74×` surge)** rise monotonically to the bottom of the folio.\n")
    md.append("   - Across `153` multi-paragraph folios (`PARA_1_OPENING -> PARA_2_SECOND -> PARA_3PLUS_LATER`), **Folio-New Rare-Stem Introduction Density (`IDF/100w`)** decays monotonically (**`38.524 -> 35.349 -> 33.665`**) while **Vessel Applicatives `l-/ol-` (`7.98% -> 8.21% -> 12.16%`)** and **Measured Doses `-aiin` (`10.40% -> 11.49% -> 12.56%`)** rise monotonically; and `Para 2..K` shares **`1.387×` higher Rare-Stem IDF with `Para 1` of the SAME folio (`1.243` vs. `0.896 ± 0.123` `($I, $L, $H)`-stratified null, $z = +2.82, p = 0.004$)**.\n\n")

    md.append("---\n")
    md.append("## Part II: Complete 10-Zone Rosettes Map (`fRos`) Atlas (`Attack 133`)\n")
    md.append("| Zone | Lines | Words | Stems | `o-` % | `qo-` % | `-edy` % | `-aiin` % | Dom Sec | `f66r` Shared IDF (`Stems`) | Top-2 External Folios (`Sec: IDF`) |\n")
    md.append("| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- | :--- |\n")
    for zp in d133["zone_profiles"]:
        m = zp["metrics"]
        f66_str = f"{zp['f66r_shared_idf']} ({','.join(zp['f66r_shared_stems'][:4])})" if zp["f66r_shared_stems"] else "0"
        ext_str = ", ".join(f"{e['folio']}({e['section']}:{e['idf']})" for e in zp["top_external_folios"][:2])
        md.append(
            f"| **`{zp['zone']}`** | {zp['n_lines']} | {m['n_tokens']} | {m['n_unique_stems']} | **{m['o_nom_pct']}%** | **{m['qo_pct']}%** | {m['edy_pct']}% | {m['aiin_pct']}% | **`{zp['dominant_section']}`** | `{f66_str}` | `{ext_str}` |\n"
        )

    md.append("\n---\n")
    md.append("## Part III: TheCross-Section Canonical Stem Dictionary & Inflectional Paradigm Table (`Attack 134`)\n")
    md.append("### 1. Paired Within-Stem Supply (`H ∪ A ∪ Z ∪ C`) $\to$ Clinical (`B ∪ P ∪ S`) Inflectional Shift (`220` Paired Stems, $z = +7.08$)\n")
    md.append("| Inflectional Slot | Supply / Diagram (`H, A, Z, C`) Mean % | Clinical (`B, P, S`) Mean % | Shift (`Delta %`) | Clinical / Supply Ratio |\n")
    md.append("| :--- | :---: | :---: | :---: | :---: |\n")
    for sk, sm in d134["overview"]["within_stem_supply_to_clinical_shift_test"]["slot_shift_summary"].items():
        md.append(
            f"| **`{sk}`** | {sm['supply_HAZC_mean_pct']}% | **{sm['clinical_BPS_mean_pct']}%** | `{sm['delta_pct']:+.2f}%` | **`{sm['ratio_clinical_over_supply']}×`** |\n"
        )

    md.append("\n### 2. Top-100 Multi-Folio Canonical Stems & Their 8-Slot Inflectional Paradigms\n")
    md.append("| Rank | Canonical Stem | Tokens | Folios (`DF`) | Semantic Class | Section Breakdown | `NOM_O` Top Form | `ACT_QO` Top Form | `HERB_BENCH` Top Form | `APPL_L` Top Form | `PROC_EDY` Top Form | `DOSE_AIIN` Top Form |\n")
    md.append("| :---: | :--- | :---: | :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |\n")
    for e in d134["top200_canonical_stem_dictionary"][:100]:
        ip = e["inflectional_paradigm"]
        sec_str = " ".join(f"{k}:{v}" for k, v in e["section_counts"].items())
        md.append(
            f"| {e['rank']} | **`{e['stem']}`** | {e['total_tokens']} | {e['df_folios']} | `{e['semantic_class'].split('_', 2)[-1]}` | `{sec_str}` | `{ip['NOM_O']['top_form']}({ip['NOM_O']['count']})` | `{ip['ACT_QO']['top_form']}({ip['ACT_QO']['count']})` | `{ip['HERB_BENCH']['top_form']}({ip['HERB_BENCH']['count']})` | `{ip['APPL_L']['top_form']}({ip['APPL_L']['count']})` | `{ip['PROC_EDY']['top_form']}({ip['PROC_EDY']['count']})` | `{ip['DOSE_AIIN']['top_form']}({ip['DOSE_AIIN']['count']})` |\n"
        )

    md.append("\n### 3. Top-50 Rare Pan-Medical Cross-Section Hub Stems (`4 <= DF <= 25`, Bridging `>= 4` Sections)\n")
    md.append("| Rank | Stem | Tokens | `DF` | `IDF` | Section Counts | Top Attested Surface Forms | `NOM_O` | `ACT_QO` | `APPL_L` | `PROC_EDY` | `DOSE_AIIN` |\n")
    md.append("| :---: | :--- | :---: | :---: | :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- |\n")
    for e in d134["top50_pan_medical_rare_hub_stems"]:
        ip = e["inflectional_paradigm"]
        sec_str = " ".join(f"{k}:{v}" for k, v in e["section_counts"].items())
        top_w = ", ".join(f"{x['word']}({x['count']})" for x in e["top_surface_forms"][:3])
        md.append(
            f"| {e['rank']} | **`{e['stem']}`** | {e['total_tokens']} | {e['df_folios']} | `{e['idf']}` | `{sec_str}` | `{top_w}` | `{ip['NOM_O']['top_form']}` | `{ip['ACT_QO']['top_form']}` | `{ip['APPL_L']['top_form']}` | `{ip['PROC_EDY']['top_form']}` | `{ip['DOSE_AIIN']['top_form']}` |\n"
        )

    md.append("\n---\n")
    md.append("## Part IV: Universal Intra-Folio Discourse Architecture (`Attack 135`)\n")
    md.append("### 1. Vertical Folio-Frame Grammar (`TOP_LINE_1` vs. `INTERIOR_LINES` vs. `BOTTOM_LINE_N`)\n")
    md.append("| Scope | Vertical Zone | Tokens | Stems | Mean Len | `p/f` Gallows % | `o-` % | `qo-` % | `l-/ol-` % | `-edy` % | `-aiin` % | `-am/-m` % | Liquid Coda % |\n")
    md.append("| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |\n")
    for scope, zdict in d135["vertical_folio_frame_summary"].items():
        for zname, zm in zdict.items():
            md.append(
                f"| `{scope}` | **`{zname}`** | {zm['n_tokens']} | {zm['n_unique_stems']} | **{zm['mean_len']}** | **{zm['pf_gallows_pct']}%** | {zm['o_nom_pct']}% | **{zm['qo_pct']}%** | {zm['l_appl_pct']}% | **{zm['edy_pct']}%** | **{zm['aiin_pct']}%** | **{zm['am_pct']}%** | {zm['liquid_coda_pct']}% |\n"
            )

    md.append("\n### 2. Multi-Paragraph Folio Progression (`PARA_1_OPENING` $\to$ `PARA_2_SECOND` $\to$ `PARA_3PLUS_LATER`, `153` Folios, $z = +2.82$)\n")
    md.append("| Paragraph Position | Tokens | Unique Stems | New Rare-Stem `IDF / 100w` | `d-` Topic % | `l-/ol-` Applicative % | `qo-` Active % | `-edy` Simmer % | `-aiin` Dose % |\n")
    md.append("| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |\n")
    for pkey, pm in d135["paragraph_progression_summary"].items():
        md.append(
            f"| **`{pkey}`** | {pm['n_tokens']} | {pm['n_unique_stems']} | **`{pm['mean_new_rare_stem_idf_per_100w']}`** | **{pm['d_top_pct']}%** | **{pm['l_appl_pct']}%** | {pm['qo_pct']}% | {pm['edy_pct']}% | **{pm['aiin_pct']}%** |\n"
        )

    OUT_MD.write_text("".join(md), encoding="utf-8")
    print(f"[Attack 136] Saved {OUT_JSON} and {OUT_MD}")


if __name__ == "__main__":
    main()
