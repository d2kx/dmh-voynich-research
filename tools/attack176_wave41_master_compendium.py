#!/usr/bin/env python3
"""
Attack 176: The Wave 41 Master Compendium (Quire Signatures & 100% Page-Boundary Closure,
Multi-Row Pharmaceutical Shelf-to-Paragraph Act-I Citation Law, and Plumed-Gallows / Weirdo-Glyph Atlas).
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
A173 = ROOT / "data" / "attack173_quire_signatures_and_bifolio_continuity.json"
A174 = ROOT / "data" / "attack174_multirow_pharma_shelf_to_paragraph_alignment.json"
A175 = ROOT / "data" / "attack175_plumed_gallows_and_weirdo_glyph_atlas.json"
OUT_JSON = ROOT / "data" / "attack176_wave41_master_compendium.json"
OUT_MD = ROOT / "notes" / "QUIRE_SIGNATURES_PHARMA_SHELVES_AND_WEIRDO_GLYPH_ATLAS.md"


def main():
    d173 = json.loads(A173.read_text(encoding="utf-8"))
    d174 = json.loads(A174.read_text(encoding="utf-8"))
    d175 = json.loads(A175.read_text(encoding="utf-8"))

    compendium = {
        "attack": "Attack 176: Wave 41 Master Compendium (Attacks 173-176 / Discoveries 190-193)",
        "wave": 41,
        "discoveries": [
            {
                "id": "Discovery 190 (Attack 173)",
                "title": "18-Quire Gathering Architecture, 100.0% Page-Start (<%>) & 99.03% Page-End (<$>) Paragraph Closure Law, and Monotonic Physical Leaf/Bifolio/Quire Lexical Cohesion",
                "headline_metrics": {
                    "page_start_paragraph_open_pct": d173["page_boundary_closure_law"]["pages_starting_with_paragraph_open_pct"],
                    "page_end_paragraph_close_pct": d173["page_boundary_closure_law"]["pages_ending_with_paragraph_close_pct"],
                    "same_leaf_stem_jaccard": d173["physical_codicology_cohesion_controlled_for_section_and_lang"]["mean_jaccard_same_leaf_recto_verso"],
                    "same_leaf_vs_diff_quire_z": d173["physical_codicology_cohesion_controlled_for_section_and_lang"]["same_leaf_vs_diff_quire_z"],
                    "same_quire_stem_jaccard": d173["physical_codicology_cohesion_controlled_for_section_and_lang"]["mean_jaccard_same_quire"],
                    "same_quire_vs_diff_quire_z": d173["physical_codicology_cohesion_controlled_for_section_and_lang"]["same_quire_vs_diff_quire_z"],
                },
            },
            {
                "id": "Discovery 191 (Attack 174)",
                "title": "Multi-Row Pharmaceutical Shelf-to-Paragraph Architecture & Act-I Paragraph-Opening Ingredient Citation Law (66.29% in Lines 1-2, z=-5.37)",
                "headline_metrics": {
                    "whole_folio_stem_echo_pct": d174["shelf_to_paragraph_gradient"]["whole_folio_hit_rate_pct"],
                    "paired_shelf_para_hit_rate_pct": d174["shelf_to_paragraph_gradient"]["paired_shelf_para_hit_rate_pct"],
                    "act1_first_two_lines_hit_pct": d174["act1_paragraph_opening_citation_law"]["first_two_lines_hit_pct"],
                    "act1_mean_first_hit_line_pos": d174["act1_paragraph_opening_citation_law"]["mean_first_hit_normalized_line_pos"],
                    "act1_z_vs_uniform": d174["act1_paragraph_opening_citation_law"]["z_score_vs_uniform"],
                },
            },
            {
                "id": "Discovery 192 (Attack 175)",
                "title": "Plumed Bench-Gallows Allographic Reduction Proof (82.35% Exact Word / 94.12% Canonical Stem Collapse) & Rare Weirdo-Glyph (@NNN;) 3.00x Label/Key Atlas",
                "headline_metrics": {
                    "plumed_exact_word_collapse_pct": d175["plumed_gallows_analysis"]["exact_word_collapse_single_or_ch_pct"],
                    "plumed_canonical_stem_collapse_pct": d175["plumed_gallows_analysis"]["canonical_stem_collapse_pct"],
                    "weirdo_label_enrichment_ratio": d175["weirdo_glyph_atlas"]["label_enrichment_ratio"],
                    "embedded_weirdo_resolved_pct": d175["weirdo_glyph_atlas"]["embedded_weirdo_resolved_pct"],
                },
            },
        ],
        "attack173": d173,
        "attack174": d174,
        "attack175": d175,
    }

    OUT_JSON.write_text(json.dumps(compendium, indent=2), encoding="utf-8")

    md = []
    md.append("# Wave 41 Master Compendium: Quire Signatures, Multi-Row Pharmaceutical Shelves & the Plumed-Gallows / Weirdo-Glyph Atlas (`Attacks 173–176` / `Discoveries 190–193`)\n")
    md.append("> **Visual & Quantitative Synthesis**: This compendium unites the three empirical breakthroughs of Wave 41 (`Attacks 173–175`) with 5 newly rendered high-contrast manuscript scans (`f8v`, `f88r`, `f89v1`, `f75r`, `f86v4`) and the synchronized **v7.0** Interactive Explorer.\n")

    md.append("## 1. Visual Evidence Gallery (`Wave 41 Scans`)\n")
    md.append("| Folio | Section | Visual & Paleographic Highlight | High-Contrast Scan |")
    md.append("| :--- | :--- | :--- | :--- |")
    md.append("| **`f8v`** | Herbal (`H`, Quire 1 End) | *Silene dioica* (Red Campion) with medieval bookbinder's **Quire 1 signature (`Pmg / 1`)** in the bottom-right corner | [`pages/f8v_quire1_signature_enh.png`](../pages/f8v_quire1_signature_enh.png) |")
    md.append("| **`f88r`** | Pharmaceutical (`P`, Quire 15) | **Three-Shelf Compounding Atlas**: 3 cylindrical red-and-green apothecary jars (`otchol, sorald`) + 3 horizontal shelves of 15 labeled roots above 3 dedicated recipe paragraphs (`P1, P2, P3`) | [`pages/f88r_three_rows_jars_enh.png`](../pages/f88r_three_rows_jars_enh.png) |")
    md.append("| **`f89v1`** | Pharmaceutical (`P`, Quire 15) | **Three-Row Pharmaceutical Folio**: 3 blue-and-green apothecary vessels + 3 rows of cut roots (including visual twin of `f48v` at `[1,4]`) and 2 recipe paragraphs | [`pages/f89v1_three_row_pharma_enh.png`](../pages/f89v1_three_row_pharma_enh.png) |")
    md.append("| **`f75r`** | Balneological (`B`, Quire 13 Start) | **Balneological Opening Page**: Upper canopy feeding a green vertical chute with 5 sliding nymphs, an 8-line inner-margin column (`<f75r.14–21>`), and lower communal pool | [`pages/f75r_balneo_nymph_pool_trefoil_enh.png`](../pages/f75r_balneo_nymph_pool_trefoil_enh.png) |")
    md.append("| **`f86v4–v6`** | Cosmological (`C`, Quire 14 Verso) | **Unfolded Three-Panel Cosmological Verso**: Four-Spoke Sun/Moon Wheel (`f86v4`), Concentric Scalloped Lunar Ring (`f86v6`), and 4-Paragraph Prose Treatise (`f86v5`) | [`pages/f86v4_four_winds_cosmology_enh.png`](../pages/f86v4_four_winds_cosmology_enh.png) |\n")

    md.append("## 2. Attack 173 (`Discovery 190`): Quire Gathering Signatures (`1..20`), the `100.0%` Page-Boundary Closure Law & Physical Leaf/Quire Lexical Cohesion\n")
    pb = d173["page_boundary_closure_law"]
    pc = d173["physical_codicology_cohesion_controlled_for_section_and_lang"]
    md.append(f"- **`100.0%` Page-Start (`{pb['pages_starting_with_paragraph_open']} / {pb['total_prose_folios']}`) & `99.03%` Page-End (`{pb['pages_ending_with_paragraph_close']} / {pb['total_prose_folios']}`) Paragraph Closure**: Every single prose page in the Voynich Manuscript opens with an explicit `<%>` paragraph-start marker (`0` pages ever begin mid-sentence from a previous page), and `99.03%` close with `<$>`—even immediately before and after all `6` missing-folio gaps (`f11v -> f13r`, `f58v -> f65r`, `f73v -> f75r`, `f90v2 -> f93r`, `f96v -> f99r`, `f108v -> f111r`).")
    md.append(f"- **Monotonic Physical Codicology Cohesion (Strictly Controlled Within Matching Section `$I` & Language `$L`)**:")
    md.append(f"  - **Same Physical Leaf (`recto <-> verso`, $n = {pc['n_same_leaf_pairs']}$)**: Mean stem Jaccard = **`{pc['mean_jaccard_same_leaf_recto_verso']}`** (**`{pc['same_leaf_vs_diff_quire_ratio']}×` enrichment, $z = +{pc['same_leaf_vs_diff_quire_z']}$** vs. different quires of the exact same section and language).")
    md.append(f"  - **Same Conjoined Bifolio Sheet (`$B`, $n = {pc['n_same_bifolio_pairs']}$)**: Mean stem Jaccard = **`{pc['mean_jaccard_same_bifolio_sheet']}`**.")
    md.append(f"  - **Same Quire Gathering (`$Q`, $n = {pc['n_same_quire_pairs']}$)**: Mean stem Jaccard = **`{pc['mean_jaccard_same_quire']}`** (**`{pc['same_quire_vs_diff_quire_ratio']}×` enrichment, $z = +{pc['same_quire_vs_diff_quire_z']}$** vs. different quires `{pc['mean_jaccard_diff_quire_same_section_lang']}`).\n")

    md.append("## 3. Attack 174 (`Discovery 191`): Multi-Row Pharmaceutical Shelf Alignment & the Act-I Paragraph-Opening Ingredient Citation Law (`66.29%` in Lines `1–2`, $z = -5.37$)\n")
    sg = d174["shelf_to_paragraph_gradient"]
    a1 = d174["act1_paragraph_opening_citation_law"]
    md.append(f"- **Whole-Folio Ingredient Sharing & Proximity Gradient**: Across all `{sg['paired_shelf_para_total']}` labeled plant ingredients (`@Lf`) on multi-row Pharmaceutical pages (`f88r–f102v2`), **`{sg['whole_folio_hit_rate_pct']}%`** echo their exact canonical stem inside the prose of the same folio, following a monotonic gradient from **Paired Shelf $\\to$ Paragraph (`{sg['paired_shelf_para_hit_rate_pct']}%`) > Same-Page Off-Shelf Paragraph (`{sg['off_shelf_same_page_hit_rate_pct']}%`) > Off-Folio Pharmaceutical Paragraph (`{sg['off_folio_pharma_para_hit_rate_pct']}%`)**.")
    md.append(f"- **The Act-I Paragraph-Opening Ingredient Citation Law ($z = {a1['z_score_vs_uniform']}, p < 10^{{-7}}$)**: When a labeled plant ingredient echoes inside a recipe paragraph, **`{a1['first_two_lines_hit_count']} / {a1['n_echoed_plants']}` (`{a1['first_two_lines_hit_pct']}%`)** make their first appearance directly inside **Lines `1–2` (`Act I: Ingredient Declaration`)**, with a mean normalized first-hit line position of **`{a1['mean_first_hit_normalized_line_pos']}`** (vs. `0.500` uniform midpoint, $z = {a1['z_score_vs_uniform']}$).")
    md.append(f"- **Vessel (`@Lc`) vs. Ingredient (`@Lf`) Morphological Split**: Apothecary vessel labels (`@Lc`, $n=40$, e.g. `otchol, sorald`) concentrate `-y` endings at **`50.0%`** (vs. `36.19%` in `@Lf`), whereas cut-root labels (`@Lf`, $n=210$) concentrate `-l/-r/-d/-n` root/liquid endings at **`40.0%`** (vs. `27.5%` in `@Lc`).\n")

    md.append("## 4. Attack 175 (`Discovery 192`): Plumed Bench-Gallows (`{cthh}..{cfhh}`) Allographic Reduction Proof & the Rare Weirdo-Glyph (`@NNN;`) Structural Atlas\n")
    pg = d175["plumed_gallows_analysis"]
    wg = d175["weirdo_glyph_atlas"]
    md.append(f"- **Plumed Bench-Gallows Allographic Reduction (`82.35%` Exact Word / `94.12%` Canonical Stem Collapse)**: Across all `{pg['total_plumed_tokens']}` occurrences of double-plumed bench gallows (`{{cthh}}, {{ckhh}}, {{cphh}}, {{cfhh}}`), stripping the ornamental second loop collapses **`{pg['exact_word_collapse_single_loop_count']} / {pg['total_plumed_tokens']}` (`{pg['exact_word_collapse_single_loop_pct']}%`)** into exact standard single-loop words (`{pg['exact_word_collapse_single_or_ch_count']} / {pg['total_plumed_tokens']}` [`{pg['exact_word_collapse_single_or_ch_pct']}%`] including `ch`), and **`{pg['canonical_stem_collapse_count']} / {pg['total_plumed_tokens']}` (`{pg['canonical_stem_collapse_pct']}%`)** share an attested canonical stem (`qo{{cthh}}y -> qocthy`, `{{cthh}}ol -> cthol`, `o{{cthh}}ody -> octhody`).")
    md.append(f"- **Rare Non-Standard EVA Weirdo Glyphs (`@132;..@252;`, $n = {wg['total_weirdo_tokens']}$ across `{wg['distinct_weirdo_codes']}` codes)**:")
    md.append(f"  - **`{wg['label_enrichment_ratio']}×` Label & Margin-Key Enrichment**: `{wg['in_labels_or_keys_count']} / {wg['total_weirdo_tokens']}` (`{wg['in_labels_or_keys_pct']}%` vs. `{wg['corpus_baseline_label_pct']}%` corpus baseline) occur in figure labels or marginal keys, and `{wg['standalone_single_glyph_count']}` (`{wg['standalone_single_glyph_pct']}%`) are standalone single-glyph margin/index symbols.")
    md.append(f"  - **`{wg['embedded_weirdo_resolved_pct']}%` Allographic Word Resolution**: Among the `{wg['embedded_weirdo_total']}` tokens where `@NNN;` is embedded inside a multi-letter word, single-character substitution resolves **`{wg['embedded_weirdo_resolved_to_attested_word']} / {wg['embedded_weirdo_total']}` (`{wg['embedded_weirdo_resolved_pct']}%`)** directly into attested standard Voynich words.\n")

    OUT_MD.write_text("\n".join(md), encoding="utf-8")
    print(f"Wrote {OUT_JSON} and {OUT_MD}")


if __name__ == "__main__":
    main()
