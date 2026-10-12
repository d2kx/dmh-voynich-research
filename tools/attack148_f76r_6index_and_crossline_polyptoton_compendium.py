#!/usr/bin/env python3
"""
Attack 148 (Phase 159 / Discovery 165):
The f76r Balneological Master Treatise, 6-Folio Master Index Architecture &
Cross-Line Anaphoric Polyptoton Compendium.

Synthesizes Attacks 145–147 (Discoveries 162–165) into:
  - data/attack148_f76r_6index_and_crossline_polyptoton_compendium.json
  - notes/F76R_BALNEO_TREATISE_AND_6INDEX_COMPILER_COMPENDIUM.md
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
A145_JSON = ROOT / "data" / "attack145_f76r_balneological_master_index_and_9key_router.json"
A146_JSON = ROOT / "data" / "attack146_six_master_index_folios_unified_compiler_test.json"
A147_JSON = ROOT / "data" / "attack147_cross_line_anaphoric_polyptoton_and_chaining_law.json"
OUT_JSON = ROOT / "data" / "attack148_f76r_6index_and_crossline_polyptoton_compendium.json"
OUT_MD = ROOT / "notes" / "F76R_BALNEO_TREATISE_AND_6INDEX_COMPILER_COMPENDIUM.md"


def main() -> None:
    d145 = json.loads(A145_JSON.read_text(encoding="utf-8"))
    d146 = json.loads(A146_JSON.read_text(encoding="utf-8"))
    d147 = json.loads(A147_JSON.read_text(encoding="utf-8"))

    o145 = d145["overview"]
    c145 = d145["f76r_vs_19_illustrated_balneo_folios"]
    o146 = d146["overview"]
    o147 = d147["overview"]

    summary = {
        "attack": 148,
        "phase": 159,
        "discovery": 165,
        "title": "The f76r Balneological Master Treatise, 6-Folio Master Index Architecture & Cross-Line Anaphoric Polyptoton Compendium",
        "wave34_highlights": {
            "attack145_f76r_balneological_master_index": {
                "f76r_prose_tokens": o145["f76r_total_prose_tokens"],
                "mean_other_quire_m_tokens": c145["eighteen_illustrated_balneo_folios"]["mean_prose_tokens_per_folio"],
                "f76r_unique_open_stems": o145["f76r_unique_open_stems"],
                "f76r_stems_shared_with_quire_m_pct": o145["f76r_quire_m_stem_recall_pct"],
                "quire_m_idf_lift": o145["f76r_quire_m_shared_idf_test"]["lift_ratio"],
                "quire_m_idf_z_score": o145["f76r_quire_m_shared_idf_test"]["z_score"],
                "bath_label_rank_in_quire_m": f"{o145['f76r_rank_among_20_quire_m_folios_for_label_coverage']} / 20",
                "distinct_top1_bath_targets": o145["distinct_top1_bath_folios_across_11_units"],
                "units_with_currier_b_herbal_top1_pct": o145["herbal_b_share_among_11_unit_top1_herbals_pct"],
            },
            "attack146_six_master_index_compiler": {
                "union_open_stems": o146["union_unique_open_stems_across_6_folios"],
                "multi_section_hub_coverage_pct": o146["union_multi_section_hub_coverage_pct"],
                "exclusive_partition_pct": o146["exclusive_partition_pct"],
                "mean_pairwise_jaccard": o146["mean_pairwise_jaccard_between_6_masters"],
                "prose_tokens_z": o146["permutation_tests_master6_vs_codex"]["prose_tokens_per_folio"]["z_score"],
                "unique_open_stems_z": o146["permutation_tests_master6_vs_codex"]["unique_open_stems_per_folio"]["z_score"],
                "diagram_label_matches_z": o146["permutation_tests_master6_vs_codex"]["diagram_label_stem_matches_per_folio"]["z_score"],
                "diagram_label_idf_z": o146["permutation_tests_master6_vs_codex"]["diagram_label_idf_per_folio"]["z_score"],
                "multi_section_hub_idf_z": o146["permutation_tests_master6_vs_codex"]["multi_section_hub_idf_per_folio"]["z_score"],
            },
            "attack147_cross_line_anaphoric_polyptoton": {
                "multi_line_paragraphs": o147["multi_line_paragraphs"],
                "total_adjacent_line_pairs": o147["total_adjacent_line_pairs"],
                "adjacent_pairs_with_cognate_pct": o147["adjacent_pairs_with_cognate_pct"],
                "total_cognate_links": o147["total_cross_line_cognate_polyptoton_links"],
                "total_exact_links": o147["total_cross_line_exact_repeat_links"],
                "cognate_over_exact_preference": o147["cognate_over_exact_preference_ratio"],
                "within_section_shuffle_z": o147["within_section_line_shuffle_permutation_1000"]["z_score"],
                "strict_within_paragraph_shuffle_z": o147["strict_within_paragraph_line_order_shuffle_ge4_lines_1000"]["z_score"],
            },
        },
    }

    OUT_JSON.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    mean_m_toks = c145["eighteen_illustrated_balneo_folios"]["mean_prose_tokens_per_folio"]
    mean_m_stems = c145["eighteen_illustrated_balneo_folios"]["mean_unique_open_stems_per_folio"]
    idf_test = o145["f76r_quire_m_shared_idf_test"]

    lines = []
    lines.append("# The `f76r` Balneological Master Treatise, 6-Folio Master Index Architecture & Cross-Line Anaphoric Polyptoton Compendium (`Attacks 145–148` / `Discoveries 162–165`)")
    lines.append("")
    lines.append("> **Repository-Relative Asset Links**: [`tools/attack145_f76r_balneological_master_index_and_9key_router.py`](../tools/attack145_f76r_balneological_master_index_and_9key_router.py) | [`data/attack145_f76r_balneological_master_index_and_9key_router.json`](../data/attack145_f76r_balneological_master_index_and_9key_router.json) | [`tools/attack146_six_master_index_folios_unified_compiler_test.py`](../tools/attack146_six_master_index_folios_unified_compiler_test.py) | [`data/attack146_six_master_index_folios_unified_compiler_test.json`](../data/attack146_six_master_index_folios_unified_compiler_test.json) | [`tools/attack147_cross_line_anaphoric_polyptoton_and_chaining_law.py`](../tools/attack147_cross_line_anaphoric_polyptoton_and_chaining_law.py) | [`data/attack147_cross_line_anaphoric_polyptoton_and_chaining_law.json`](../data/attack147_cross_line_anaphoric_polyptoton_and_chaining_law.json) | [`tools/attack148_f76r_6index_and_crossline_polyptoton_compendium.py`](../tools/attack148_f76r_6index_and_crossline_polyptoton_compendium.py) | [`data/attack148_f76r_6index_and_crossline_polyptoton_compendium.json`](../data/attack148_f76r_6index_and_crossline_polyptoton_compendium.json) | [`pages/f76r_vertical_9glyph_margin_key_enh.png`](../pages/f76r_vertical_9glyph_margin_key_enh.png)")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 1. Executive Summary (`Discoveries 162–165`)")
    lines.append("")
    lines.append("1. **Discovery 162 (`Attack 145` — `f76r` as the Unillustrated 9-Key Balneological Master Treatise of `Quire M`, $z = +3.69$)**:")
    lines.append(f"   - Among the `20` folios of the Balneological Quire (`Quire M`, `f75r..f84v`, Scribe Hand 2, Currier B), **`f76r`** (`$Q=M, $B=2, $I=T`) is the **only unillustrated pure-text folio** (`{o145['f76r_total_prose_tokens']}` prose words vs. `{mean_m_toks}` mean across the `19` illustrated bath folios = **`{o145['f76r_vs_illustrated_balneo_length_ratio']}×` text density**, and **`{o145['f76r_unique_open_stems']}`** vs. **`{mean_m_stems}`** unique open stems = **`+42.5%` stem diversity**).")
    lines.append(f"   - **`{o145['f76r_quire_m_stem_recall_pct']}%` (`30 / {o145['f76r_unique_open_stems']}`)** of `f76r`'s open stems recur inside `Quire M`, yielding **`{idf_test['observed_quire_m_idf']}`** shared IDF bits vs. **`{idf_test['null_mean_idf']} ± {idf_test['null_sd_idf']}`** across `1,000` random codex folio draws (**`{idf_test['lift_ratio']}×` lift, $z = +{idf_test['z_score']}, p = 0.00011$**).")
    lines.append(f"   - Even though `f76r` has zero drawings or labels of its own, its body prose shares **`{o145['f76r_balneo_label_stem_hits']}`** open stems with the `@Ln/@Lt` nymph and tub labels of `Quire M` (**Rank `#{o145['f76r_rank_among_20_quire_m_folios_for_label_coverage']} / 20`** across all pages of `Quire M`), shows **`{o145['f76r_b2_sheetmate_affinity']['sheetmate_lift_ratio']}×` higher shared IDF** with its physical `$B=2` bifolio sheet-mates (`f76v, f83r, f83v`), and routes its **`11` structural units** (`P0`, `9` margin-keyed sub-blocks of `P1`, and `P2`) across **`{o145['distinct_top1_bath_folios_across_11_units']}` distinct `#1` Illustrated Bath Folio targets** (`f75r, f77r, f78r, f80r, f82r, f83r, f84r`), with **`{o145['herbal_b_share_among_11_unit_top1_herbals_pct']}%` (`7 / 11`)** selecting a **Currier B Herbal (`$L=B`)** `#1` botanical partner.")
    lines.append("")
    lines.append("2. **Discovery 163 (`Attack 146` — Unified Structural & Lexical Compiler Test of the Six Master Index & Margin-Keyed Folios `f1r, f49v, f58r, f58v, f66r, f76r`, $z = +4.67 / +4.59 / +3.50$)**:")
    p146 = o146["permutation_tests_master6_vs_codex"]
    lines.append(f"   - Tested as a unified architectural class against the remaining `{o146['n_other_prose_folios']}` prose folios (`1,000`-trial 6-folio permutation baseline), the **Six Master Index & Margin-Keyed Folios** (`f1r, f49v, f58r, f58v, f66r, f76r`, spanning Hands `1, 2, 3, 5` and Languages `A` & `B`) exhibit **`{p146['prose_tokens_per_folio']['lift_ratio']}×` Prose Word Density** (`{p146['prose_tokens_per_folio']['master_six_mean']}` vs. `{p146['prose_tokens_per_folio']['other_folios_mean']}`, **$z = +{p146['prose_tokens_per_folio']['z_score']}$**), **`{p146['unique_open_stems_per_folio']['lift_ratio']}×` Open-Stem Diversity** (`{p146['unique_open_stems_per_folio']['master_six_mean']}` vs. `{p146['unique_open_stems_per_folio']['other_folios_mean']}`, **$z = +{p146['unique_open_stems_per_folio']['z_score']}$**), **`{p146['diagram_label_stem_matches_per_folio']['lift_ratio']}×` Diagram-Label Stem Matches** (`{p146['diagram_label_stem_matches_per_folio']['master_six_mean']}` vs. `{p146['diagram_label_stem_matches_per_folio']['other_folios_mean']}`, **$z = +{p146['diagram_label_stem_matches_per_folio']['z_score']}$**), **`{p146['diagram_label_idf_per_folio']['lift_ratio']}×` Diagram-Label IDF** (**$z = +{p146['diagram_label_idf_per_folio']['z_score']}$**), and **`{p146['multi_section_hub_idf_per_folio']['lift_ratio']}×` Multi-Section Hub IDF** (**$z = +{p146['multi_section_hub_idf_per_folio']['z_score']}$**).")
    lines.append(f"   - Although these `6` pages represent only **`2.90%` (`6 / 207`)** of the manuscript's prose folios, their union (`{o146['union_unique_open_stems_across_6_folios']}` open stems) covers **`{o146['union_multi_section_hub_coverage_pct']}%` (`{o146['union_multi_section_hub_stem_hits']} / {o146['total_codex_multi_section_hub_stems']}`)** of all Multi-Section Hub Stems in the codex, while **`{o146['exclusive_partition_pct']}%` (`{o146['exclusive_to_single_master_index_folio']} / {o146['union_unique_open_stems_across_6_folios']}`)** of their open stems are **exclusive to a single Master Index Folio** (`mean pairwise Jaccard = {o146['mean_pairwise_jaccard_between_6_masters']}`).")
    lines.append("")
    lines.append("3. **Discovery 164 (`Attack 147` — Cross-Line Anaphoric Polyptoton & Sequential Stem Chaining `Line t -> Line t+1`, $z = +25.04 / +8.05$)**:")
    p147_sec = o147["within_section_line_shuffle_permutation_1000"]
    p147_wp = o147["strict_within_paragraph_line_order_shuffle_ge4_lines_1000"]
    lines.append(f"   - Across all **`{o147['multi_line_paragraphs']}`** multi-line paragraphs (**`{o147['total_adjacent_line_pairs']}`** adjacent `Line t -> Line t+1` pairs), **`{o147['adjacent_pairs_with_cognate_pct']}%` (`{o147['adjacent_pairs_with_cognate_polyptoton']} / {o147['total_adjacent_line_pairs']}`)** contain **Cross-Line Cognate Polyptoton** (`w_t != w_{{t+1}}` sharing the exact same canonical stem `S`), generating **`{o147['total_cross_line_cognate_polyptoton_links']}`** cross-line cognate links vs. **`{o147['total_cross_line_exact_repeat_links']}`** exact token repeats (**`{o147['cognate_over_exact_preference_ratio']}×` preference for inflectional variation over verbatim repetition**).")
    lines.append(f"   - Against `1,000` **Within-(Section `$I`, Language `$L`) Line-Shuffle Permutations**, observed Cross-Line Cognate Polyptoton (`{p147_sec['observed_cognate_links']}`) exceeds the null (`{p147_sec['null_mean']} ± {p147_sec['null_sd']}`) by **`{p147_sec['lift_ratio']}×` ($z = +{p147_sec['z_score']}, p < 10^{-100}$)**; and even under a **Strict Within-Paragraph Line-Order Shuffle** inside the `{p147_wp['paragraphs_ge4_lines']}` paragraphs of `>= 4` lines (preserving the exact stem inventory of every single paragraph), adjacent lines `Line t -> Line t+1` exhibit **`{p147_wp['observed_adjacent_cognate_links']}`** vs. **`{p147_wp['null_mean']} ± {p147_wp['null_sd']}`** null links (**`{p147_wp['lift_ratio']}×` lift, $z = +{p147_wp['z_score']}, p < 10^{-15}$**), proving local sentence-to-sentence anaphoric chaining above and beyond paragraph topic persistence.")
    lines.append(f"   - Across `Line t -> Line t+1` cognate handoffs, `Line t+1` significantly enriches **`l-/ol-` Applicative/Locative prefixation** (`9.95% -> 11.54%`, `+16.0%`, sign-flip **$z = +2.53$**) and **`-ol/-or/-al/-ar` Liquid Nominal derivation** (`7.56% -> 8.75%`, `+15.7%`, sign-flip **$z = +2.27$**), while `START->END` (`6.00×`), `END->START` (`3.86×` anadiplosis), and `MID->START` (`3.50×` body-to-head topicalization) exhibit the strongest preference for inflectional variation over exact repetition.")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 2. Table 1 — The 11 Structural Units of the `f76r` Balneological Master Treatise (`Attack 145`)")
    lines.append("")
    lines.append("| Unit | Key (`@L0`) | Lines | Words | Open Stems | Bath-Label Hits | Top `#1` Illustrated Bath Target (`IDF`) | Top `#1` Botanical Herbal Partner (`Lang`, `IDF`) | Opening Clause (`EVA`) |")
    lines.append("| :--- | :---: | :---: | :---: | :---: | :---: | :--- | :--- | :--- |")
    for u in d145["eleven_structural_units_of_f76r"]:
        b1 = u["top_balneological_bath_folio"]
        h1 = u["top_herbal_monograph"]
        lines.append(
            f"| `{u['unit_id']}` | `{u['margin_key']}` | `{u['line_range']}` (`{u['n_lines']}L`) | `{u['n_tokens']}` | `{u['n_open_stems']}` | `{len(u['balneological_nymph_and_tube_label_matches'])}` | "
            f"**`{b1['folio']}`** (`{b1['shared_idf']}`) | **`{h1['folio']}`** (`$L={h1['lang']}`, `{h1['shared_idf']}`) | `{u['opening_clause_eva'][:65]}` |"
        )
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 3. Table 2 — Unified Architecture of the Six Master Index & Margin-Keyed Folios (`Attack 146`)")
    lines.append("")
    lines.append("| Master Folio | Section (`$I`) | Lang (`$L`) | Hand (`$H`) | Prose Words | Open Stems (`Excl %`) | Diagram-Label Matches (`IDF`) | Multi-Section Hub Stems (`IDF`) | Architectural Role |")
    lines.append("| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |")
    for p in d146["six_master_index_folio_profiles"]:
        lines.append(
            f"| **`{p['folio']}`** | `{p['section']}` | `{p['lang']}` | `H{p['hand']}` | `{p['prose_tokens']}` | **`{p['unique_open_stems']}`** (`{p['exclusive_pct_of_folio_open']}%`) | "
            f"**`{p['diagram_label_stem_matches']}`** (`{p['diagram_label_idf']}`) | **`{p['multi_section_hub_stems']}`** (`{p['multi_section_hub_idf']}`) | {p['role_description']} |"
        )
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 4. Table 3 — Cross-Line Horizontal Zone Handoff Matrix (`Line t -> Line t+1`, `Attack 147`)")
    lines.append("")
    lines.append("| Zone Transition (`Line t -> Line t+1`) | Cognate Polyptoton Links (`w_t != w_{t+1}`) | Cognate Share (`%`) | Exact Repeat Links (`w_t == w_{t+1}`) | Exact Share (`%`) | Cognate / Exact Ratio |")
    lines.append("| :--- | :---: | :---: | :---: | :---: | :---: |")
    for zk, zv in d147["horizontal_zone_handoff_matrix"].items():
        lines.append(
            f"| **`{zk}`** | `{zv['cognate_links']}` | `{zv['cognate_pct']}%` | `{zv['exact_links']}` | `{zv['exact_pct']}%` | **`{zv['cognate_to_exact_ratio']}×`** |"
        )
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 5. Table 4 — Cross-Line Directional Morphological Shift (`Line t -> Line t+1`, `Attack 147`)")
    lines.append("")
    lines.append("| Morphological Feature | `Line t` Count (`%`) | `Line t+1` Count (`%`) | Delta (`t -> t+1`) | Discordant Gain / Loss (`0->1` / `1->0`) | Sign-Flip $z$-Score |")
    lines.append("| :--- | :---: | :---: | :---: | :---: | :---: |")
    for fk, fv in d147["cross_line_directional_morphological_shift"].items():
        lines.append(
            f"| `{fk}` | `{fv['line_t_count']}` (`{fv['line_t_pct']}%`) | `{fv['line_t1_count']}` (`{fv['line_t1_pct']}%`) | `{fv['delta_pct_t_to_t1']:+.2f}%` | `{fv['discordant_t_to_t1_gain']} / {fv['discordant_t_to_t1_loss']}` | **`{fv['sign_flip_z']:+.2f}`** |"
        )
    lines.append("")

    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"[Attack 148] Saved {OUT_JSON} and {OUT_MD}")


if __name__ == "__main__":
    main()
