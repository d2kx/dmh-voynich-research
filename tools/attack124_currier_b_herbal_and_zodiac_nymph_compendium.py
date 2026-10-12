#!/usr/bin/env python3
"""
Attack 124 (Phase 135 / Discovery 141):
The Complete 32-Folio Currier B Herbal, 12-Sign Zodiac Nymph & 20-Quire
Codicological Translation Compendium Generator.

Synthesizes Attacks 121-123 (Discoveries 138-140) into:
  - data/attack124_currier_b_herbal_and_zodiac_nymph_compendium.json
  - notes/CURRIER_B_HERBAL_AND_ZODIAC_NYMPH_COMPENDIUM.md
"""

import json
import os


def main():
    with open("data/attack121_twenty_quire_codicological_sheet_position_law.json", "r", encoding="utf-8") as f:
        d121 = json.load(f)
    with open("data/attack122_currier_b_32herbal_monograph_translator.json", "r", encoding="utf-8") as f:
        d122 = json.load(f)
    with open("data/attack123_zodiac_12medallion_nymph_and_ring_translator.json", "r", encoding="utf-8") as f:
        d123 = json.load(f)

    summary = {
        "attack": "Attack 124 (Phase 135 / Discovery 141)",
        "title": "Complete 32-Folio Currier B Herbal, 12-Sign Zodiac Nymph & 20-Quire Codicological Translation Compendium",
        "wave28_highlights": {
            "attack121_codicological_law": {
                "scribe5_outer_wrapper_pct": 100.0,
                "scribe4_single_sheet_quire_pct": 100.0,
                "herbal_inner_centerfold_currier_b_pct": d121["herbal_sheet_tier_metrics"]["INNER_CENTERFOLD"]["pct_currier_B"],
                "herbal_outer_wrapper_currier_b_pct": d121["herbal_sheet_tier_metrics"]["OUTER_WRAPPER"]["pct_currier_B"],
                "herbal_intermediate_currier_b_pct": d121["herbal_sheet_tier_metrics"]["INTERMEDIATE_SHEET"]["pct_currier_B"],
                "outer_wrapper_clinical_hub_idf": d121["herbal_sheet_tier_metrics"]["OUTER_WRAPPER"]["mean_clinical_hub_idf"],
                "inner_centerfold_clinical_hub_idf": d121["herbal_sheet_tier_metrics"]["INNER_CENTERFOLD"]["mean_clinical_hub_idf"],
            },
            "attack122_currier_b_herbal_32": d122["herbal_b_vs_a_comparison"]["permutation_test_total_clinical_PBS"],
            "attack123_zodiac_350_nymphs": {
                "total_nymph_labels": d123["global_summary"]["total_nymph_star_labels"],
                "resolved_pct": d123["global_summary"]["nymph_label_resolved_pct"],
                "in_herbal_pct": d123["global_summary"]["nymph_in_herbal_pct"],
                "in_pharm_pct": d123["global_summary"]["nymph_in_pharm_pct"],
                "in_balneo_pct": d123["global_summary"]["nymph_in_balneo_pct"],
                "in_starred_pct": d123["global_summary"]["nymph_in_starred_pct"],
                "clinical_label_concordance_z": d123["zodiac_nymph_to_clinical_label_permutation_test"]["z_score"],
            },
        },
    }

    with open("data/attack124_currier_b_herbal_and_zodiac_nymph_compendium.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    lines = []
    lines.append("# The Complete 32-Folio Currier B Herbal, 12-Sign Zodiac Nymph & 20-Quire Codicological Compendium (`Attacks 121–124` / `Discoveries 138–141`)")
    lines.append("")
    lines.append("This reference edition synthesizes **Autonomous Wave 28 (`Phases 132–135` / `Attacks 121–124` / `Discoveries 138–141`)**, uniting:")
    lines.append("1. **The 20-Quire Codicological Bifolio Sheet-Position Law & Mixed-Scribe Quire Partition (`Attack 121 / Discovery 138`)**: Proving that across all 7 four-bifolio Herbal Quires (`Quires A–G`), **`100.0%` (`26 / 26`) of Innermost Centerfold (`$B=4`) folios are written by Scribe 1 (`$H=1`, Currier A)** (`0.0%` Currier B!), whereas **100% (`24 / 24`) of the Currier B Herbal Monographs in `Quires D–G` (`Scribe 2 $H=2` and `Scribe 5 $H=5`) occupy Outer/Intermediate Wrapper Bifolios (`$B=1, 2, 3`) wrapped around Scribe 1's Currier A centerfold core**.")
    lines.append("2. **The Complete 32-Monograph Currier B Herbal (`$I=H, $L=B`) Translator (`Attack 122 / Discovery 139`, $z = +4.81$)**: Translating all `32` Currier B Herbal Monographs (`f26r–f95v2`) and proving their `1.473×` Total Clinical Routing IDF lift over Currier A Herbals (`65.398` vs. `44.402`, $z = +4.81$) and their 3-scribe clinical division (`Scribe 2 -> Balneological $I=B`, `Scribe 5 -> Pharmaceutical $I=P & Zodiac $I=Z`, `Scribe 3 -> Starred Decoctions $I=S`).")
    lines.append("3. **The Complete 12-Medallion Zodiac (`f70v2–f73v`) Concentric Ring (`964` words) & `350` Star-Nymph Label (`&Lz`) Translator (`Attack 123 / Discovery 140`, $z = +3.48$)**: Resolving **`348 / 350` (`99.43%`) of the Zodiac Star-Nymph Labels** into Non-Zodiac Corpus Stems (`85.14%` in Herbal `$I=H`, `75.43%` in Pharmaceutical `$I=P`, `65.71%` in Balneological `$I=B`, `87.43%` in Starred Recipes `$I=S`) with a **`2.29×` rare-stem IDF concordance ($z = +3.48$)** with Clinical Bather/Botanical Labels (`@Ln ∪ @Lf`).")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Part I: 20-Quire Codicological Sheet-Position Law (`Attack 121` / `Discovery 138`)")
    lines.append("")
    lines.append("### 1. Five-Scribe (`$H=1..5`) Bifolio Sheet-Tier Allocation")
    lines.append("| Scribe Hand (`$H`) | Total Folios | Multi-Sheet Folios (`max_B >= 2`) | `OUTER_WRAPPER ($B=1)` | `INTERMEDIATE_SHEET` | `INNER_CENTERFOLD ($B=max)` | Quires Occupied |")
    lines.append("| :--- | :---: | :---: | :---: | :---: | :---: | :--- |")
    for h, st in d121["scribe_sheet_distribution"].items():
        tm = st["tiers_multi_sheet_pct"]
        q_str = ", ".join(f"{k}:{v}" for k, v in st["quires"].items())
        lines.append(
            f"| **`{h}`** | `{st['n_folios_total']}` | `{st['n_folios_multi_sheet']}` | `{tm.get('OUTER_WRAPPER', 0.0)}%` | `{tm.get('INTERMEDIATE_SHEET', 0.0)}%` | `{tm.get('INNER_CENTERFOLD', 0.0)}%` | `{q_str}` |"
        )
    lines.append("")
    lines.append("### 2. Multi-Sheet Herbal Quire (`Quires A–G`, `109` Folios) Sheet-Tier Metrics")
    lines.append("| Sheet Tier | Folios | `% Currier B` | Mean Prose Tokens | Mean Unique Stems | Mean Clinical Hub IDF (`P ∪ B ∪ S`) | `% With Marginal Key / Extraneous` |")
    lines.append("| :--- | :---: | :---: | :---: | :---: | :---: | :---: |")
    for tier, m in d121["herbal_sheet_tier_metrics"].items():
        lines.append(
            f"| **`{tier}`** | `{m['n_folios']}` | **`{m['pct_currier_B']}%`** | `{m['mean_prose_tokens']}` | `{m['mean_unique_stems']}` | **`{m['mean_clinical_hub_idf']}`** | `{m['pct_with_extraneous_or_key']}%` |"
        )
    lines.append("")
    lines.append("### 3. Mixed-Scribe Quire Bifolio Partition (`Quires D, E, F, G, H, Q`)")
    lines.append("| Quire | `$B=1` (Outer Wrapper) | `$B=2` | `$B=3` | `$B=4` (Innermost Centerfold) |")
    lines.append("| :---: | :--- | :--- | :--- | :--- |")
    lines.append("| **`Quire D`** | `f25r,f25v,f32r,f32v` (`H=1, L=A`) | **`f26r,f26v,f31r,f31v` (`H=2, L=B`)** | `f27r,f27v,f30r,f30v` (`H=1, L=A`) | `f28r,f28v,f29r,f29v` (`H=1, L=A`) |")
    lines.append("| **`Quire E`** | **`f33r,f33v,f40r,f40v` (`H=2, L=B`)** | **`f34r,f34v,f39r,f39v` (`H=2, L=B`)** | `f35r,f35v,f38r,f38v` (`H=1, L=A`) | `f36r,f36v,f37r,f37v` (`H=1, L=A`) |")
    lines.append("| **`Quire F`** | **`f41r,f41v,f48r,f48v` (`H=5, L=B`)** | `f42r,f42v,f47r,f47v` (`H=1, L=A`) | **`f43r,f43v,f46r,f46v` (`H=2, L=B`)** | `f44r,f44v,f45r,f45v` (`H=1, L=A`) |")
    lines.append("| **`Quire G`** | `f49r,f49v,f56r,f56v` (`H=1, L=A`) | **`f50r,f50v,f55r,f55v` (`H=2, L=B`)** | `f51r,f51v,f54r,f54v` (`H=1, L=A`) | `f52r,f52v,f53r,f53v` (`H=1, L=A`) |")
    lines.append("| **`Quire H`** | **`f57r,f57v,f66r,f66v` (`H=5/1, L=B/?`)** | **`f58r,f58v,f65r,f65v` (`H=3, L=A/?`)** | *(missing f59–f64)* | *(missing)* |")
    lines.append("| **`Quire Q`** | `f93r,f93v,f96r,f96v` (`H=1, L=A`) | **`f94r,f94v,f95r1..v2` (`H=3, L=B`)** | — | — |")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Part II: Complete 32-Monograph Currier B Herbal (`$I=H, $L=B`) Translation Atlas (`Attack 122` / `Discovery 139`)")
    lines.append("")
    lines.append("### 1. `H_B` (`n=32`) vs. `H_A` (`n=95`) & Three-Scribe Specialization (`H=2, H=5, H=3`)")
    lines.append("| Group | Folios | Mean Words | Mean Stems | `% qo-` | `% -edy` | `% l-/ol-` | `% -aiin` | `IDF -> P` | `IDF -> B` | `IDF -> S` | `IDF -> Z` | `Total PBS IDF` |")
    lines.append("| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |")
    for label, g in [
        ("**All `H_B` (`$L=B`)**", d122["herbal_b_vs_a_comparison"]["H_B_32"]),
        ("**All `H_A` (`$L=A`)**", d122["herbal_b_vs_a_comparison"]["H_A_96"]),
        ("**`H_B` Scribe 2 (`$H=2`, Quires D–G)**", d122["three_scribe_hb_specialization"]["H=2"]),
        ("**`H_B` Scribe 5 (`$H=5`, Quires F, H)**", d122["three_scribe_hb_specialization"]["H=5"]),
        ("**`H_B` Scribe 3 (`$H=3`, Quire Q)**", d122["three_scribe_hb_specialization"]["H=3"]),
    ]:
        lines.append(
            f"| {label} | `{g['n_folios']}` | `{g['mean_tokens']}` | `{g['mean_unique_stems']}` | `{g['mean_qo_pct']}%` | `{g['mean_edy_pct']}%` | `{g['mean_l_ol_pct']}%` | `{g['mean_aiin_pct']}%` | `{g['mean_idf_P']}` | `{g['mean_idf_B']}` | `{g['mean_idf_S']}` | `{g['mean_idf_Z']}` | **`{g['mean_total_clinical_PBS']}`** |"
        )
    lines.append("")
    lines.append("- **Visual Verification**: See [pages/f34r_scribe2_currier_b_master_herbal_enh.png](../pages/f34r_scribe2_currier_b_master_herbal_enh.png) (`f34r`, Scribe 2 Quire E `$B=2` Master Hub, `PBS IDF = 98.642`) and [pages/f95r1_scribe3_quire_q_herbal_foldout_enh.png](../pages/f95r1_scribe3_quire_q_herbal_foldout_enh.png) (`f95r1`, Scribe 3 Quire Q `$B=2` 3-Panel Foldout Herbal).")
    lines.append("")
    lines.append("### 2. Monograph-by-Monograph Structural & Botanical Translation of All 32 Currier B Herbals (`f26r–f95v2`)")
    lines.append("| # | Folio (`Q,B,H`) | Sheet-Mates | Words (`Stems`) | Morph (`qo / edy / aiin`) | `PBS IDF` | `#1 Zodiac` | `#1 Pharm` | `#1 Balneo` | `#1 Starred` | Line-1 Botanical Header Interlinear Gloss |")
    lines.append("| :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |")
    for r in d122["monograph_records"]:
        mates_s = ",".join(r["sheet_mates"][:3])
        m = r["morph"]
        lines.append(
            f"| `{r['rank']}` | **`{r['folio']}`** (`{r['quire']},B={r['bifolio_B']},H={r['scribe_H']}`) | `{mates_s}` | `{r['n_tokens']}` (`{r['n_unique_stems']}`) | `{m['qo_pct']}% / {m['edy_pct']}% / {m['aiin_pct']}%` | **`{r['routing_idf']['total_clinical_PBS']}`** | `{r['best_zodiac_match']['folio']}` (`{r['best_zodiac_match']['idf']}`) | `{r['best_pharm_match']['folio']}` (`{r['best_pharm_match']['idf']}`) | `{r['best_balneo_match']['folio']}` (`{r['best_balneo_match']['idf']}`) | `{r['best_starred_match']['folio']}` (`{r['best_starred_match']['idf']}`) | `{r['line1_header_gloss'][:140]}` |"
        )
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Part III: Complete 12-Medallion Zodiac (`f70v2–f73v`) Concentric Ring & `350` Star-Nymph Label (`&Lz`) Translator (`Attack 123` / `Discovery 140`)")
    lines.append("")
    lines.append("### 1. Global Morphological Polarity: `350` Star-Nymph Labels (`&Lz`) vs. `964` Concentric Ring Tokens (`@Cc`)")
    nm = d123["global_summary"]["nymph_morph_global"]
    rm = d123["global_summary"]["ring_morph_global"]
    lines.append("| Locus Class | Tokens | Mean Chars | `% o-` (Spring/Nom) | `% y-` (Autumn/Init) | `% qo-` (Active Boil) | `% -y/-dy` (Star/Bath State) | `% -ol/-or/-al/-ar` (Fluid/Resin) | `% -am/-m` (Ring Seal) | `% -aiin` (Degree/Dose) |")
    lines.append("| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |")
    lines.append(
        f"| **`NYMPH_STAR_LABELS (&Lz)`** | `{nm['n_tokens']}` | `{nm['mean_len_chars']}` | **`{nm['o_onset_pct']}%`** | **`{nm['y_onset_pct']}%`** | **`{nm['qo_onset_pct']}%`** | **`{nm['y_dy_coda_pct']}%`** | `{nm['fluid_resin_ol_or_al_ar_pct']}%` | **`{nm['ring_seal_am_m_pct']}%`** | `{nm['aiin_coda_pct']}%` |"
    )
    lines.append(
        f"| **`CONCENTRIC_RINGS (@Cc)`** | `{rm['n_tokens']}` | `{rm['mean_len_chars']}` | `{rm['o_onset_pct']}%` | `{rm['y_onset_pct']}%` | `{rm['qo_onset_pct']}%` | `{rm['y_dy_coda_pct']}%` | **`{rm['fluid_resin_ol_or_al_ar_pct']}%`** | `{rm['ring_seal_am_m_pct']}%` | **`{rm['aiin_coda_pct']}%`** |"
    )
    lines.append("")
    lines.append("- **Visual Verification**: See [pages/f70v2_pisces_medallion_nymphs_and_rings_enh.png](../pages/f70v2_pisces_medallion_nymphs_and_rings_enh.png) (Pisces `f70v2`, showing barrel-bathing star-nymphs `&Lz` inside three `@Cc` circular rings) and [pages/f72v1_libra_medallion_nymphs_and_rings_enh.png](../pages/f72v1_libra_medallion_nymphs_and_rings_enh.png).")
    lines.append("")
    lines.append("### 2. Medallion-by-Medallion Astro-Medical Translation & Star-Nymph Catalogue (`Pisces f70v2 -> Sagittarius f73v`)")
    for m in d123["medallion_records"]:
        lines.append(f"#### `{m['folio']}` — **{m['sign']}** (`{m['humoral_quality']}`, `{m['n_ring_loci']}` Rings = `{m['n_ring_tokens']}` words; `{m['n_nymph_labels']}` Star-Nymph Labels)")
        lines.append(
            f"- **5-Section Astro-Medical Routing**: `#1 Herbal` = **`{m['best_herbal']['folio']}`** (`IDF={m['best_herbal']['idf']}`, stems `{m['best_herbal']['shared_stems']}`) | `#1 Pharm` = **`{m['best_pharm']['folio']}`** (`IDF={m['best_pharm']['idf']}`) | `#1 Balneo` = **`{m['best_balneo']['folio']}`** (`IDF={m['best_balneo']['idf']}`) | `#1 Starred Recipe` = **`{m['best_starred']['folio']}`** (`IDF={m['best_starred']['idf']}`)"
        )
        lines.append(
            f"- **Nymph Polarity**: `o- = {m['nymph_morph'].get('o_onset_pct')}%`, `y- = {m['nymph_morph'].get('y_onset_pct')}%`, `-y/-dy = {m['nymph_morph'].get('y_dy_coda_pct')}%`, `-ol/-or/-al/-ar = {m['nymph_morph'].get('fluid_resin_ol_or_al_ar_pct')}%`"
        )
        for rl in m["rings"]:
            lines.append(
                f"  - **Ring `<{m['folio']}.{rl['line']},{rl['loc']}>`** (`{rl['n_tokens']}` words, terminal=`{rl['terminal_token']}`): `{rl['gloss_preview']}`"
            )
        sample_nymphs = [
            f"`{nl['raw']}` -> {nl['gloss']} [`{nl['top_herbal']}`, `{nl['in_sections']}`]"
            for nl in m["nymph_labels"][:12]
        ]
        lines.append(f"  - **Star-Nymph Labels (`1..{min(12, len(m['nymph_labels']))}` of `{len(m['nymph_labels'])}`)**: " + " ; ".join(sample_nymphs))
        lines.append("")

    os.makedirs("notes", exist_ok=True)
    with open("notes/CURRIER_B_HERBAL_AND_ZODIAC_NYMPH_COMPENDIUM.md", "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    print("=== ATTACK 124 COMPLETE ===")
    print("Generated notes/CURRIER_B_HERBAL_AND_ZODIAC_NYMPH_COMPENDIUM.md and data/attack124_currier_b_herbal_and_zodiac_nymph_compendium.json")


if __name__ == "__main__":
    main()
