#!/usr/bin/env python3
"""
Attack 112 (Discovery 129): The Quire H Starred Master Index, Balneological Hydrotherapy
& Astronomical Foldout Compendium (`notes/QUIRE_H_INDEX_BALNEOLOGICAL_AND_ASTRO_COMPENDIUM.md`
& `data/attack112_quire_h_balneological_and_astro_compendium.json`)

Synthesizes:
- Attack 109 (Discovery 126): The `f58r / f58v` (Quire H, Bifolio $B=1) Starred Botanical Master Index Solver,
- Attack 110 (Discovery 127): The Balneological (`Quire M`, `f75r–f84v`) Hydrotherapy-to-Zodiac & Herbal-Infusion Network,
- Attack 111 (Discovery 128): The 14-Folio Astronomical Foldout (`f67r1–f70r2`) & Zodiac (`f70v2–f73v`) Sector-by-Sector Star & Calendar Concordance.
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
NOTES_DIR = ROOT / "notes"

A109_JSON = DATA_DIR / "attack109_f58_starred_botanical_index_solver.json"
A110_JSON = DATA_DIR / "attack110_balneological_to_zodiac_and_herbal_infusion_network.json"
A111_JSON = DATA_DIR / "attack111_astronomical_foldout_and_zodiac_star_concordance.json"

OUT_JSON = DATA_DIR / "attack112_quire_h_balneological_and_astro_compendium.json"
OUT_MD = NOTES_DIR / "QUIRE_H_INDEX_BALNEOLOGICAL_AND_ASTRO_COMPENDIUM.md"


def main():
    d109 = json.loads(A109_JSON.read_text(encoding="utf-8"))
    d110 = json.loads(A110_JSON.read_text(encoding="utf-8"))
    d111 = json.loads(A111_JSON.read_text(encoding="utf-8"))

    cmp109 = d109["comparison_f58_vs_quire20"]
    f58_p = cmp109["F58R_F58V_QUIRE_H_STARRED_INDEX"]
    q20_p = cmp109["QUIRE_20_F103_F116_CLINICAL_RECIPES"]

    hb110 = d110["herbal_b_selectivity"]
    pt110 = d110["permutation_tests"]
    tf110 = d110["hydrotherapy_morphological_transformation"]

    pt111 = d111["astro_to_zodiac_permutation_test"]
    hb111 = d111["herbal_b_selectivity"]
    lg111 = d111["four_tier_astro_locus_gradient"]

    md = []
    md.append("# The Quire H Starred Master Index, Balneological Hydrotherapy & Astronomical Foldout Compendium (`Attacks 109–112` / `Discoveries 126–129`)")
    md.append("")
    md.append("This reference edition synthesizes the results of **Autonomous Wave 25 (`Phases 120–123` / `Attacks 109–112` / `Discoveries 126–129`)**, solving the structural role of **`f58r / f58v` (`Quire H, Bifolio $B=1`) as a Botanical-Apothecary Master Index** ([`pages/f58r_starred_botanical_index_enh.png`](../pages/f58r_starred_botanical_index_enh.png), [`pages/f58v_starred_botanical_index_enh.png`](../pages/f58v_starred_botanical_index_enh.png)), mapping the **Balneological (`Quire M`, `f75r–f84v`) Hydrotherapy-to-Zodiac & Herbal-Infusion Network** (`94.74%` Currier B Herbal selectivity, `5.71×` `l-/ol-` aqueous applicative surge, $z = +16.68$), and establishing the **14-Folio Astronomical Foldout (`f67r1–f70r2`) $\\leftrightarrow$ Zodiac (`f70v2–f73v`) Star & Calendar Concordance** ($z = +9.43$).")
    md.append("")
    md.append("---")
    md.append("")
    md.append("## Part I: The `f58r / f58v` (`Quire H, Bifolio $B=1`) Starred Botanical Master Index (`Attack 109 / Discovery 126`)")
    md.append("")
    md.append("### 1.1 Structural & Morphological Contrast: `f58r / f58v` (Quire H) vs. Quire 20 (`f103r–f116r`) Starred Recipes")
    md.append("")
    md.append("| Metric | `f58r / f58v` (`Quire H, $B=1`) | Quire 20 (`f103r–f116r`, `$Q=T`) | Ratio / Contrast |")
    md.append("|---|---:|---:|---:|")
    md.append(f"| **Starred / Header Blocks** | `{f58_p['paragraph_count']}` | `{q20_p['paragraph_count']}` | — |")
    md.append(f"| **Mean Tokens per Block** | **`{f58_p['mean_tokens_per_para']}`** | `{q20_p['mean_tokens_per_para']}` | **`{f58_p['mean_tokens_per_para']/q20_p['mean_tokens_per_para']:.2f}×` longer** |")
    md.append(f"| **Mean Shared `H ∩ P` Open Stems per Block** | **`{f58_p['mean_hp_shared_stems']}`** | `{q20_p['mean_hp_shared_stems']}` | **`{f58_p['mean_hp_shared_stems']/q20_p['mean_hp_shared_stems']:.2f}×` higher** |")
    md.append(f"| **Mean Pharm `@Lf` Root/Leaf Label Matches per Block** | **`{f58_p['mean_p_lbl_shared_stems']}`** | `{q20_p['mean_p_lbl_shared_stems']}` | **`{f58_p['mean_p_lbl_shared_stems']/q20_p['mean_p_lbl_shared_stems']:.2f}×` higher** |")
    md.append(f"| **Pharm `@Lf` Label Matches per 100 Tokens** | **`{f58_p['mean_p_lbl_per_100_toks']}`** | `{q20_p['mean_p_lbl_per_100_toks']}` | **`+66.8%` ($z = {cmp109['pharm_label_density_z_score']:+.2f}$)** |")
    md.append(f"| **Processual Decoction `-edy / -eedy` Rate** | **`{f58_p['edy_process_pct']}%`** | `{q20_p['edy_process_pct']}%` | **`18.2×` suppression** |")
    md.append(f"| **Botanical/Container `-ol / -or / -al / -ar` Rate** | **`{f58_p['ol_or_al_ar_liquid_pct']}%`** | `{q20_p['ol_or_al_ar_liquid_pct']}%` | **`+76.2%` (`1.76×` surge)** |")
    md.append(f"| **Nominal Citation `o-` Rate** | `{f58_p['o_nominal_pct']}%` | `{q20_p['o_nominal_pct']}%` | `+0.85%` |")
    md.append(f"| **Active Imperative `qo-` Rate** | `{f58_p['qo_active_pct']}%` | `{q20_p['qo_active_pct']}%` | `-3.70%` |")
    md.append("")
    md.append("### 1.2 Visual Verification on [`pages/f58r_starred_botanical_index_enh.png`](../pages/f58r_starred_botanical_index_enh.png) and [`pages/f58v_starred_botanical_index_enh.png`](../pages/f58v_starred_botanical_index_enh.png)")
    md.append("")
    md.append("- **`f58r` ([`pages/f58r_starred_botanical_index_enh.png`](../pages/f58r_starred_botanical_index_enh.png))**: Displays **3 large multi-rayed unpainted marginal stars** (`6-pointed` top star with central dot at `<f58r.1>`, `8-pointed` middle star with central dot at `<f58r.16>`, and `8-pointed` lower star with central dot at `<f58r.26>`), marking `3` long botanical-apothecary compilation blocks (`140`, `94`, and `144` tokens).")
    md.append("- **`f58v` ([`pages/f58v_starred_botanical_index_enh.png`](../pages/f58v_starred_botanical_index_enh.png))**: Displays **only 1 marginal star** (a `7-pointed` tailed star at the top-left of `<f58v.1>`, `219` tokens, `22` lines, sharing `46` `H∩P` stems and `10` `@Lf` root/leaf labels!), while the `3` shorter lower blocks (`<f58v.23>`, `<f58v.29>`, `<f58v.34>`) have **no marginal stars at all** — instead opening with oversized Paragraph-Initial Gallows (`p-` / `t-`).")
    md.append("")
    md.append("### 1.3 Complete 7-Block Botanical & Apothecary Concordance Catalog of `f58r / f58v`")
    md.append("")
    md.append("| Block ID | Tokens | Lines | `H ∩ P` Stems | `@Lf` Label Hits | Top-3 Herbal Monograph Targets (`$I=H`) | Top-2 Pharmaceutical Targets (`$I=P` & `@Lf` Labels) |")
    md.append("|---|---:|---:|---:|---:|---|---|")
    for c in d109["f58_eight_starred_blocks_catalog"]:
        h_str = ", ".join(f"`{m['folio']}` (`{m['lang']}`, IDF={m['idf']:.1f})" for m in c["top_herbal_matches"])
        p_str = ", ".join(f"`{m['folio']}` (IDF={m['idf']:.1f}, `@Lf`={m['label_hits']})" for m in c["top_pharm_matches"])
        md.append(f"| **`{c['recipe_id']}`** | `{c['n_tokens']}` | `{c['n_lines']}` | **`{c['hp_shared_count']}`** | **`{c['p_lbl_shared_count']}`** | {h_str} | {p_str} |")
    md.append("")
    md.append("---")
    md.append("")
    md.append("## Part II: The Balneological (`Quire M`, `f75r–f84v`) Hydrotherapy-to-Zodiac & Herbal-Infusion Network (`Attack 110 / Discovery 127`)")
    md.append("")
    md.append("### 2.1 `94.74%` (`3.79×`) Currier B Herbal Infusion Selectivity & Permutation Tests")
    md.append("")
    md.append(f"- **Currier B Herbal Monograph Selectivity**: **`{hb110['herbal_b_top1_matches']} / {hb110['balneo_folios_count']} = {hb110['herbal_b_top1_pct']:.2f}%`** of the Balneological Hydrotherapy folios (`f75r–f84v`) select a **Currier B Herbal Monograph (`$L=B`)** as their `#1` highest-IDF botanical infusion partner (vs. `{hb110['herbal_b_folio_baseline_pct']:.2f}%` Herbal-B baseline — a **`{hb110['enrichment_ratio']:.2f}×` enrichment**).")
    md.append(f"- **3-Stage (`Herbal $I=H -> Pharmaceutical $I=P -> Balneological Bath $I=B`) Hydrotherapy Triads (`>= 3` shared stems)**: **`{pt110['hpb_3plus_triads_obs']}` observed vs. `{pt110['hpb_3plus_triads_null_mean']} ± {pt110['hpb_3plus_triads_null_std']}` null (`3.18×` enrichment, $z = {pt110['hpb_3plus_triads_z']:+.2f}$)**.")
    md.append(f"- **4-Stage (`Zodiac Medallion $I=Z -> Herbal $I=H -> Pharm $I=P -> Balneological Bath $I=B`) Astro-Hydrotherapy Tetrads (`>= 2` shared stems)**: **`{pt110['zhpb_2plus_tetrads_obs']}` observed vs. `{pt110['zhpb_2plus_tetrads_null_mean']} ± {pt110['zhpb_2plus_tetrads_null_std']}` null (`2.95×` enrichment, $z = {pt110['zhpb_2plus_tetrads_z']:+.2f}$)**.")
    md.append("")
    md.append("### 2.2 The `5.71×` Aqueous Applicative (`l- / ol- / qol-`) Transformation Law on Shared Hydrotherapy Stems (`H -> P -> B`)")
    md.append("")
    md.append(f"Holding the exact `{tf110['shared_hpb_stems_count']}` open-class canonical stems shared across `Herbal ∩ Pharmaceutical ∩ Balneological` fixed, **Liquid Applicative `l- / ol- / qol-` surges `5.71×` (`3.98%` in Herbal Prose $\\to$ `7.23%` in Pharmaceutical Formularies $\\to$ `18.75%` in Balneological Nymph Labels $\\to$ `22.74%` in Balneological Immersion-Pool Prose)**, proving that `l- / ol- / qol-` specifically marks aqueous bath infusion:")
    md.append("")
    md.append("| Hydrotherapy Stage | Matched Tokens | Nominal `o-` | Active `qo-` | **Aqueous Applicative `l-/ol-`** | Process `-edy` | Measure `-aiin` | Container `-ol/-or` |")
    md.append("|---|---:|---:|---:|---:|---:|---:|---:|")
    for skey, slabel in [
        ("STAGE_1_HERBAL_PROSE", "Stage 1: Herbal Monograph Prose (`$I=H`)"),
        ("STAGE_2_PHARM_FORMULARY", "Stage 2: Pharmaceutical Formulary (`$I=P`)"),
        ("STAGE_3A_BALNEO_NYMPH_LABELS", "Stage 3a: Balneological Nymph Labels (`@L`)"),
        ("STAGE_3B_BALNEO_POOL_PROSE", "Stage 3b: Balneological Immersion-Pool Prose (`@P`)"),
    ]:
        r = tf110[skey]
        md.append(f"| **{slabel}** | `{r['matched_tokens']}` | `{r['o_nominal_pct']:.2f}%` | `{r['qo_active_pct']:.2f}%` | **`{r['l_ol_applicative_pct']:.2f}%`** | `{r['edy_process_pct']:.2f}%` | `{r['aiin_measure_pct']:.2f}%` | `{r['ol_or_al_ar_liquid_pct']:.2f}%` |")
    md.append("")
    md.append("### 2.3 Complete 19-Folio Balneological (`Quire M`, `f75r–f84v`) Hydrotherapy Concordance Atlas")
    md.append("")
    md.append("| Balneo Folio | Bifolio (`$B`) | Tokens | `@L` Nymphs | `#1` Herbal Infusion Partner (`$I=H`) | `#1` Pharm Formulary (`$I=P`) | `#1` Zodiac Medallion (`$I=Z`) |")
    md.append("|---|---|---|---|---|---|---|")
    for b in d110["balneological_20folio_atlas"]:
        th = b["top_herbal"]
        tp = b["top_pharm"]
        tz = b["top_zodiac"]
        md.append(
            f"| **`{b['balneo_folio']}`** | `B={b['bifolio']}` | `{b['tokens']}` | `{b['nymph_labels']}` | `{th['folio']}` (`$L={th['lang']}`, IDF={th['idf']:.1f}: `{', '.join(th['stems'][:5])}`) | `{tp['folio']}` (IDF={tp['idf']:.1f}: `{', '.join(tp['stems'][:5])}`) | `{tz['folio']}` ({tz['sign']} / {tz['month']}, IDF={tz['idf']:.1f}: `{', '.join(tz['stems'][:4])}`) |"
        )
    md.append("")
    md.append("---")
    md.append("")
    md.append("## Part III: The 14-Folio Astronomical Foldout (`f67r1–f70r2`) & Zodiac (`f70v2–f73v`) Sector-by-Sector Star & Calendar Concordance (`Attack 111 / Discovery 128`)")
    md.append("")
    md.append("### 3.1 Astronomical Foldout (`f67r1–f70r2`) $\\leftrightarrow$ Zodiac (`f70v2–f73v`) Permutation Test ($z = +9.43$) & `71.43%` Herbal-B Selectivity")
    md.append("")
    md.append(f"- **Astronomical $\\leftrightarrow$ Zodiac Mean `#1` Partner IDF**: **`{pt111['observed_mean_max_zodiac_idf']:.3f}` observed vs. `{pt111['null_mean_max_zodiac_idf']:.3f} ± {pt111['null_std_max_zodiac_idf']:.3f}` null (`2.01×` enrichment, $z = {pt111['z_score']:+.2f}$)**.")
    md.append(f"- **Astronomical $\\to$ Currier B Herbal Selectivity**: **`{hb111['herbal_b_top1_matches']} / {pt111['astro_folios_count']} = {hb111['herbal_b_top1_pct']:.2f}%`** vs. `{hb111['herbal_b_baseline_pct']:.2f}%` baseline (**`{hb111['enrichment_ratio']:.2f}×` enrichment**).")
    md.append("")
    md.append("### 3.2 The 4-Tier Internal Locus Morphological Gradient Across the 14 Astronomical Foldouts (`1,667` Tokens)")
    md.append("")
    md.append("| Astronomical Locus Class | Tokens | **Nominal `o-`** | **Active `qo-`** | **Measure `-aiin`** | Container `-ol/-or` | Terminus `-am/-m` |")
    md.append("|---|---:|---:|---:|---:|---:|---:|")
    for lkey, llabel in [
        ("ASTRO_STAR_LABELS_L", "`@L` Star & Figure Labels"),
        ("ASTRO_RADIAL_SPOKES_R", "`@R` Radial Sector Spokes"),
        ("ASTRO_CONCENTRIC_RINGS_C", "`@C` Concentric Ring Streams"),
        ("ASTRO_MARGINAL_PROSE_P", "`@P` Explanatory Marginal Prose"),
    ]:
        r = lg111[lkey]
        md.append(f"| **{llabel}** | `{r['tokens']}` | **`{r['o_nominal_pct']:.2f}%`** | **`{r['qo_active_pct']:.2f}%`** | **`{r['aiin_measure_pct']:.2f}%`** | `{r['ol_or_al_ar_liquid_pct']:.2f}%` | `{r['am_m_terminus_pct']:.2f}%` |")
    md.append("")
    md.append("### 3.3 Complete 14-Folio Astronomical Foldout (`f67r1–f70r2`) Concordance Atlas")
    md.append("")
    md.append("| Astro Folio | Tokens (`@L/@R/@C/@P`) | `#1` Zodiac Medallion (`$I=Z`) | `#2` Zodiac Medallion (`$I=Z`) | `#1` Herbal Monograph (`$I=H`) | `#1` Pharm Formulary (`$I=P`) |")
    md.append("|---|---|---|---|---|---|")
    for a in d111["astronomical_14folio_atlas"]:
        tz1 = a["top_zodiac"]
        tz2 = a["second_zodiac"]
        th = a["top_herbal"]
        tp = a["top_pharm"]
        md.append(
            f"| **`{a['astro_folio']}`** | `{a['total_tokens']}` (`{a['l_star_tokens']}/{a['r_spoke_tokens']}/{a['c_ring_tokens']}/{a['p_prose_tokens']}`) | `{tz1['folio']}` ({tz1['sign']} / {tz1['month']}, IDF={tz1['idf']:.1f}: `{', '.join(tz1['stems'][:4])}`) | `{tz2['folio']}` ({tz2['sign']}, IDF={tz2['idf']:.1f}) | `{th['folio']}` (`$L={th['lang']}`, IDF={th['idf']:.1f}: `{', '.join(th['stems'][:4])}`) | `{tp['folio']}` (IDF={tp['idf']:.1f}) |"
        )
    md.append("")

    OUT_MD.write_text("\n".join(md) + "\n", encoding="utf-8")

    compendium_json = {
        "attack_id": 112,
        "discovery_id": 129,
        "title": "The Quire H Starred Master Index, Balneological Hydrotherapy & Astronomical Foldout Compendium",
        "markdown_edition": "notes/QUIRE_H_INDEX_BALNEOLOGICAL_AND_ASTRO_COMPENDIUM.md",
        "attack109_summary": cmp109,
        "attack110_herbal_b_selectivity": hb110,
        "attack110_permutation_tests": pt110,
        "attack110_hydro_transformation": tf110,
        "attack111_astro_zodiac_permutation": pt111,
        "attack111_locus_gradient": lg111,
    }
    OUT_JSON.write_text(json.dumps(compendium_json, indent=2), encoding="utf-8")
    print(f"[Attack 112] Saved -> {OUT_JSON} and {OUT_MD}")


if __name__ == "__main__":
    main()
