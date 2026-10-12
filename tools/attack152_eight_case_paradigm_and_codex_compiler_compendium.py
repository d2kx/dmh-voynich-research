#!/usr/bin/env python3
"""
Attack 152 (Phase 163 / Discovery 169):
The 8-Case Inflectional Paradigm Atlas, 3-Act Paragraph Discourse State Machine &
6-Index Codex Routing Compendium.

Synthesizes Attacks 149–151 (Discoveries 166–168) into:
  - data/attack152_eight_case_paradigm_and_codex_compiler_compendium.json
  - notes/EIGHT_CASE_PARADIGM_AND_PARAGRAPH_STATE_COMPILER.md
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
A149_JSON = ROOT / "data" / "attack149_eight_case_inflectional_paradigm_matrix.json"
A150_JSON = ROOT / "data" / "attack150_paragraph_discourse_state_machine_and_inclusio.json"
A151_JSON = ROOT / "data" / "attack151_six_master_index_codex_routing_compiler.json"
OUT_JSON = ROOT / "data" / "attack152_eight_case_paradigm_and_codex_compiler_compendium.json"
OUT_MD = ROOT / "notes" / "EIGHT_CASE_PARADIGM_AND_PARAGRAPH_STATE_COMPILER.md"

CASE_SLOTS = [
    "C1_CIT_BARE",
    "C2_NOM_O",
    "C3_DEIC_DS",
    "C4_ACT_QO",
    "C5_PROC_EDY",
    "C6_APPL_L",
    "C7_LIQ_CONT",
    "C8_QUANT_TERM",
]


def main() -> None:
    d149 = json.loads(A149_JSON.read_text(encoding="utf-8"))
    d150 = json.loads(A150_JSON.read_text(encoding="utf-8"))
    d151 = json.loads(A151_JSON.read_text(encoding="utf-8"))

    o149 = d149["overview"]
    o150 = d150["overview"]
    o151 = d151["overview"]

    pb = o149["paradigm_breadth_summary"]
    mi_test = o149["stem_by_case_mutual_information_test"]
    vs_test = o149["within_stem_clinical_vs_supply_voice_shift_test"]

    summary = {
        "attack": 152,
        "phase": 163,
        "discovery": 169,
        "title": "The 8-Case Inflectional Paradigm Atlas, 3-Act Paragraph Discourse State Machine & 6-Index Codex Routing Compendium",
        "wave35_highlights": {
            "attack149_eight_case_paradigm": {
                "total_tokens": o149["total_corpus_tokens"],
                "stems_all_8_slots": pb["stems_with_all_8_slots"],
                "tokens_in_8slot_stems_pct": pb["tokens_in_8slot_stems_pct"],
                "stems_ge6_slots_full_paradigm": pb["stems_with_ge6_slots_full_paradigm"],
                "tokens_in_ge6_slot_stems_pct": pb["tokens_in_ge6_slot_stems_pct"],
                "stems_ge4_slots_broad_paradigm": pb["stems_with_ge4_slots_broad_paradigm"],
                "tokens_in_ge4_slot_stems_pct": pb["tokens_in_ge4_slot_stems_pct"],
                "stems_ge2_slots_multi_form": pb["stems_with_ge2_slots_multi_form"],
                "tokens_in_ge2_slot_stems_pct": pb["tokens_in_ge2_slot_stems_pct"],
                "stem_case_mi_bits": mi_test["observed_mi_bits"],
                "stem_case_mi_z": mi_test["z_score"],
                "within_stem_clinical_voice_shift_pct": vs_test["observed_clinical_minus_supply_active_voice_pct"],
                "within_stem_clinical_voice_shift_z": vs_test["z_score"],
            },
            "attack150_paragraph_state_machine_and_inclusio": {
                "paragraphs_ge3_lines": o150["paragraphs_ge3_lines"],
                "paragraphs_with_3line_chain_pct": o150["paragraphs_with_3line_chain_pct"],
                "contiguous_3line_within_section_z": o150["contiguous_3line_stem_triplets_within_section_test"]["z_score"],
                "contiguous_3line_strict_within_para_z": o150["contiguous_3line_stem_triplets_strict_within_para_test"]["z_score"],
                "paragraphs_with_inclusio_pct": o150["paragraphs_with_inclusio_pct"],
                "inclusio_paragraphs_position_stratified_z": o150["inclusio_paragraphs_within_section_test"]["z_score"],
                "inclusio_shared_stems_position_stratified_z": o150["inclusio_shared_stems_within_section_test"]["z_score"],
                "cognate_share_of_inclusio_pairs_pct": o150["cognate_share_of_inclusio_pairs_pct"],
                "inclusio_appl_l_gain_z": d150["inclusio_line1_to_linem_morphological_shift"]["C6_APPL_L"]["sign_flip_z"],
            },
            "attack151_six_master_index_codex_compiler": {
                "non_index_target_folios": o151["non_index_target_folios"],
                "target_folios_linked": o151["target_folios_linked_to_ge1_master_index"],
                "target_folio_coverage_pct": o151["target_folio_coverage_pct"],
                "primary_master_index_win_counts": o151["primary_master_index_win_counts"],
                "three_pole_routing_lift": o151["three_pole_domain_routing_permutation_test_1000"]["lift_ratio"],
                "three_pole_routing_z": o151["three_pole_domain_routing_permutation_test_1000"]["z_score"],
            },
        },
    }

    OUT_JSON.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    lines = []
    lines.append("# The 8-Case Inflectional Paradigm Atlas, 3-Act Paragraph Discourse State Machine & 6-Index Codex Routing Compendium (`Attacks 149–152` / `Discoveries 166–169`)")
    lines.append("")
    lines.append("> **Repository-Relative Asset Links**: [`tools/attack149_eight_case_inflectional_paradigm_matrix.py`](../tools/attack149_eight_case_inflectional_paradigm_matrix.py) | [`data/attack149_eight_case_inflectional_paradigm_matrix.json`](../data/attack149_eight_case_inflectional_paradigm_matrix.json) | [`tools/attack150_paragraph_discourse_state_machine_and_inclusio.py`](../tools/attack150_paragraph_discourse_state_machine_and_inclusio.py) | [`data/attack150_paragraph_discourse_state_machine_and_inclusio.json`](../data/attack150_paragraph_discourse_state_machine_and_inclusio.json) | [`tools/attack151_six_master_index_codex_routing_compiler.py`](../tools/attack151_six_master_index_codex_routing_compiler.py) | [`data/attack151_six_master_index_codex_routing_compiler.json`](../data/attack151_six_master_index_codex_routing_compiler.json) | [`tools/attack152_eight_case_paradigm_and_codex_compiler_compendium.py`](../tools/attack152_eight_case_paradigm_and_codex_compiler_compendium.py) | [`data/attack152_eight_case_paradigm_and_codex_compiler_compendium.json`](../data/attack152_eight_case_paradigm_and_codex_compiler_compendium.json) | [`pages/f1r_opening_master_preface_rubrics_enh.png`](../pages/f1r_opening_master_preface_rubrics_enh.png) | [`pages/f58r_starred_botanical_master_index_enh.png`](../pages/f58r_starred_botanical_master_index_enh.png)")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 1. Executive Summary (`Discoveries 166–169`)")
    lines.append("")
    lines.append("1. **Discovery 166 (`Attack 149` — The 8-Case/Voice Inflectional Paradigm Matrix of the Voynich Lexicon, Stem×Case MI $z = +712.94$, Within-Stem Clinical Voice Activation $z = +23.59$)**:")
    lines.append(f"   - Mapping all `{o149['total_corpus_tokens']}` canonical tokens into the **8 Core Grammatical Case/Voice Slots** (`C1_CIT_BARE, C2_NOM_O, C3_DEIC_DS, C4_ACT_QO, C5_PROC_EDY, C6_APPL_L, C7_LIQ_CONT, C8_QUANT_TERM`) reveals that just **`{pb['stems_with_all_8_slots']}` Canonical Stems** populate **all `8 / 8` slots** and account for **`{pb['tokens_in_8slot_stems_pct']}%` (`{pb['tokens_in_8slot_stems']} / {o149['total_corpus_tokens']}`)** of the entire manuscript; **`{pb['stems_with_ge6_slots_full_paradigm']}` Full-Paradigm Stems** (`>= 6` slots) account for **`{pb['tokens_in_ge6_slot_stems_pct']}%` (`{pb['tokens_in_ge6_slot_stems']}` tokens)**; **`{pb['stems_with_ge4_slots_broad_paradigm']}` Broad-Paradigm Stems** (`>= 4` slots) account for **`{pb['tokens_in_ge4_slot_stems_pct']}%` (`{pb['tokens_in_ge4_slot_stems']}` tokens)**; and **`{pb['stems_with_ge2_slots_multi_form']}` Multi-Form Stems** (`>= 2` slots) account for **`{pb['tokens_in_ge2_slot_stems_pct']}%` (`{pb['tokens_in_ge2_slot_stems']}` tokens)**.")
    lines.append(f"   - Stem $\\times$ Case/Voice Mutual Information across stems with count $\\ge 10$ (`{mi_test['tokens_tested_ge10']}` tokens) reaches **`{mi_test['observed_mi_bits']}` bits** vs. **`{mi_test['within_section_lang_null_mean_bits']} ± {mi_test['within_section_lang_null_sd_bits']}` bits** under Within-`(Section $I, Language $L)` Case-Shuffle Permutations (**`{mi_test['lift_ratio']}×` lift, $z = +{mi_test['z_score']}$**).")
    lines.append(f"   - Across the 4 Macro-Domains, **Active Clinical Voice (`C4_ACT_QO + C5_PROC_EDY + C6_APPL_L`)** rises from **`20.94%` in `1_APPARATUS_LABELS_RINGS`** and **`23.87%` in `3_SUPPLY_HERBAL_PHARM`** to **`36.24%` in `2_ASTRO_COSMO_TREATISE`** and **`47.99%` in `4_CLINICAL_BALNEO_STARRED`**. Holding each of the `{vs_test['full_paradigm_stems_tested']}` Full-Paradigm Stems (`{vs_test['tokens_tested']}` tokens) strictly fixed across domains (`500`-trial within-stem domain shuffle) proves a **`+{vs_test['observed_clinical_minus_supply_active_voice_pct']}%` Clinical-minus-Supply Active Voice surge** vs. **`+{vs_test['within_stem_shuffle_null_mean_pct']}% ± {vs_test['within_stem_shuffle_null_sd_pct']}%` null ($z = +{vs_test['z_score']}, p < 10^{-100}$)**.")
    lines.append("")
    lines.append("2. **Discovery 167 (`Attack 150` — The 3-Act Paragraph Discourse State Machine, Contiguous 3-Line Stem Execution Chains $z = +26.95 / +9.20$, and Paragraph Frame-Ring Closure `Inclusio` $z = +6.63$)**:")
    c3_sec = o150["contiguous_3line_stem_triplets_within_section_test"]
    c3_wp = o150["contiguous_3line_stem_triplets_strict_within_para_test"]
    inc_p = o150["inclusio_paragraphs_within_section_test"]
    inc_s = o150["inclusio_shared_stems_within_section_test"]
    lines.append(f"   - Across all **`{o150['paragraphs_ge3_lines']}`** multi-line paragraphs (`>= 3` lines), **`{o150['paragraphs_with_3line_chain_pct']}%` (`{o150['paragraphs_with_3line_contiguous_stem_chain']} / {o150['paragraphs_ge3_lines']}`)** contain at least one **Contiguous 3-Line Stem Execution Chain (`L_t -> L_{{t+1}} -> L_{{t+2}}` sharing the exact same canonical stem `S`)**, totaling **`{c3_sec['observed']}`** triplets vs. **`{c3_sec['null_mean']} ± {c3_sec['null_sd']}`** under Within-Section Line Shuffles (**`{c3_sec['lift_ratio']}×` lift, $z = +{c3_sec['z_score']}$**), and **`{c3_wp['observed']}`** vs. **`{c3_wp['null_mean']} ± {c3_wp['null_sd']}`** under **Strict Within-Paragraph Line-Order Shuffles** inside the `{o150['paragraphs_ge4_lines']}` paragraphs of `>= 4` lines (**`{c3_wp['lift_ratio']}×` lift, $z = +{c3_wp['z_score']}, p < 10^{-18}$**).")
    lines.append(f"   - **`{o150['paragraphs_with_inclusio_pct']}%` (`{o150['paragraphs_with_inclusio_line1_to_linem']} / {o150['paragraphs_ge3_lines']}`)** of multi-line paragraphs exhibit **Paragraph Frame-Ring Closure (`Inclusio`: `Line 1 <-> Line m` sharing the exact same canonical stem `S`)**, exceeding `1,000` Position-Stratified `(Line 1 Pool <-> Line m Pool)` Permutations both by paragraph count (`{inc_p['observed']}` vs. `{inc_p['null_mean']} ± {inc_p['null_sd']}`, **`{inc_p['lift_ratio']}×` lift, $z = +{inc_p['z_score']}$**) and by shared stem links (`{inc_s['observed']}` vs. `{inc_s['null_mean']} ± {inc_s['null_sd']}`, **`{inc_s['lift_ratio']}×` lift, $z = +{inc_s['z_score']}, p = 1.7 \\times 10^{{-11}}$**).")
    lines.append(f"   - **`{o150['cognate_share_of_inclusio_pairs_pct']}%` (`{o150['cognate_inclusio_token_pairs_w1_ne_wm']} / {o150['total_inclusio_token_pairs']}`)** of `Line 1 <-> Line m` token pairs are **Cognate Polyptoton pairs (`w_1 != w_m`)**, where the stem transforms from **Opening Top-Gallows `p/f` (`16.89% -> 0.44%`, $z = -8.49$) & Processual `-edy` (`27.78% -> 20.00%`, $z = -3.84$)** in `Line 1` into **Vessel Applicative `l-/ol-/qol-` (`5.78% -> 12.44%`, `2.15×` surge, sign-flip $z = +3.49$)** in `Line m`.")
    lines.append("")
    lines.append("3. **Discovery 168 (`Attack 151` — Complete Six-Index-Folio Master Compiler & Full-Codex Cross-Reference Atlas Routing `99.10%` of the Manuscript, 3-Pole Specialization $z = +6.32$)**:")
    tp = o151["three_pole_domain_routing_permutation_test_1000"]
    lines.append(f"   - Across all **`{o151['non_index_target_folios']}`** non-index folios in the Voynich Manuscript, **`{o151['target_folio_coverage_pct']}%` (`{o151['target_folios_linked_to_ge1_master_index']} / {o151['non_index_target_folios']}`)** are directly indexed via open-class stems (`DF in 2..45`) by the **Six Master Index Folios (`f1r, f49v, f58r, f58v, f66r, f76r`)**: `#1` primary index wins split across **`f58r` (`92` folios)**, **`f66r` (`41` folios)**, **`f76r` (`29` folios, `#1` governing index for Balneological `B` at `24.036` bits/folio)**, **`f49v` (`22` folios, `2.24×` Currier-A Herbal selectivity)**, **`f58v` (`19` folios)**, and **`f1r` (`16` folios)**.")
    lines.append(f"   - In **`H_A` (`96` Currier A Herbals)**, the Hand 1 Currier-A Index Pole (`f1r + f49v = 11.939` bits/folio) exceeds the Currier-B Clinical Index Pole (`f66r + f76r = 7.358` bits/folio) by **`1.62×`**, whereas in **`H_B` (`32` Currier B Herbals)** the polarity **reverses (`f66r + f76r = 15.941` vs. `f1r + f49v = 7.096` = `2.25×` advantage, `3.65×` crossover odds ratio)**; globally across all `{o151['non_index_target_folios']}` target folios, the **3-Pole Domain-to-Index Routing Law** achieves **`{tp['observed_normalized_diagonal_affinity']}`** vs. **`{tp['null_mean']} ± {tp['null_sd']}`** null (**`{tp['lift_ratio']}×` lift, $z = +{tp['z_score']}, p < 1.5 \\times 10^{{-10}}$**).")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 2. Table 1 — Top-35 Full-Paradigm Canonical Stems Across the 8 Grammatical Case/Voice Slots (`Attack 149`)")
    lines.append("")
    lines.append("| Rank | Stem | Tokens | Slots | `C1_CIT` (Bare) | `C2_NOM` (`o-/y-`) | `C3_DEIC` (`d-/s-`) | `C4_ACT` (`qo-`) | `C5_PROC` (`-edy`) | `C6_APPL` (`l-/ol-`) | `C7_LIQ` (`-ol/-ar`) | `C8_QUANT` (`-aiin/-am`) |")
    lines.append("| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |")
    for idx, r in enumerate(d149["top_60_full_paradigm_stems"][:35], 1):
        pc = r["paradigm_cells"]
        lines.append(
            f"| `{idx}` | **`-{r['stem']}-`** | `{r['total_tokens']}` | `{r['slots_populated']}/8` | "
            f"`{pc['C1_CIT_BARE']['top_form']}` | `{pc['C2_NOM_O']['top_form']}` | `{pc['C3_DEIC_DS']['top_form']}` | "
            f"`{pc['C4_ACT_QO']['top_form']}` | `{pc['C5_PROC_EDY']['top_form']}` | `{pc['C6_APPL_L']['top_form']}` | "
            f"`{pc['C7_LIQ_CONT']['top_form']}` | `{pc['C8_QUANT_TERM']['top_form']}` |"
        )
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 3. Table 2 — The 3-Act Paragraph Discourse State Machine & `Line 1 -> Line m` Inclusio Shift (`Attack 150`)")
    lines.append("")
    lines.append("| Grammatical Feature / Case Slot | `Act I: Line 1 Header` (`5,652` tok) | `Act II: Interior Body` (`21,343` tok) | `Act III: Final Line m` (`3,627` tok) | `Inclusio Line 1` (`450` cognate) | `Inclusio Line m` (`450` cognate) | `Inclusio` Sign-Flip $z$ |")
    lines.append("| :--- | :---: | :---: | :---: | :---: | :---: | :---: |")
    a1 = d150["three_act_paragraph_state_machine"]["ACT1_LINE1_HEADER"]
    a2 = d150["three_act_paragraph_state_machine"]["ACT2_INTERIOR_BODY"]
    a3 = d150["three_act_paragraph_state_machine"]["ACT3_FINAL_CLOSURE"]
    im = d150["inclusio_line1_to_linem_morphological_shift"]
    lines.append(
        f"| **`top_gallows_pf` (`p-/f-` Header)** | **`{a1['top_gallows_pf_pct']}%`** | `{a2['top_gallows_pf_pct']}%` | `{a3['top_gallows_pf_pct']}%` | **`{im['top_gallows_pf']['line1_pct']}%`** | `{im['top_gallows_pf']['linem_pct']}%` | **`{im['top_gallows_pf']['sign_flip_z']:+.2f}`** |"
    )
    for cs in CASE_SLOTS:
        lines.append(
            f"| **`{cs}`** | `{a1['case_pct'][cs]}%` | `{a2['case_pct'][cs]}%` | `{a3['case_pct'][cs]}%` | `{im[cs]['line1_pct']}%` | `{im[cs]['linem_pct']}%` | **`{im[cs]['sign_flip_z']:+.2f}`** |"
        )
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 4. Table 3 — Stratum × Six Master Index Folios Mean Shared IDF Matrix (`Attack 151`)")
    lines.append("")
    lines.append("| Target Stratum (`$I, $L`) | Folios | `#1` Master Index | `f1r` (`H1, A`) | `f49v` (`H1, A`) | `f58r` (`H3, S`) | `f58v` (`H3, S`) | `f66r` (`H5, B`) | `f76r` (`H2, B`) |")
    lines.append("| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |")
    for st, row in d151["stratum_by_master_mean_idf_matrix"].items():
        m = row["mean_shared_idf_by_master"]
        lines.append(
            f"| **`{st}`** | `{row['n_folios']}` | **`{row['top_governing_master_index']}`** | `{m['f1r']}` | `{m['f49v']}` | `{m['f58r']}` | `{m['f58v']}` | `{m['f66r']}` | `{m['f76r']}` |"
        )
    lines.append("")

    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"[Attack 152] Saved {OUT_JSON} and {OUT_MD}")


if __name__ == "__main__":
    main()
