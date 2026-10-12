#!/usr/bin/env python3
"""
Attack 132 (Phase 143 / Discovery 149):
The Milestone 150-Discovery & Complete 226-Folio Master Compendium Generator.

Synthesizes:
- Attack 129 (Discovery 146): Complete Quire 14 (`f85r1–f86v3` + `fRos`, `$Q=N`)
  7-Page Foldout & 21-Paragraph Exegetical Translator (`z = +15.19` Nominal vs.
  Procedural Locus Split).
- Attack 130 (Discovery 147): Complete Master Preface (`f1r`), All 10 Right-
  Justified Titles (`=Pt`, `80.0%` on `$B=1` Outer Wrapper Bifolios, `z = +4.81`
  Nominal/Deictic Polarity Law), Special Folios (`f57v`, `f65r/v`, `f116v`), and
  the 20-Quire Opening vs. Closing Boundary Law.
- Attack 131 (Discovery 148): Global 226-Folio Master Citation & Cross-Reference
  Graph (`25,651` pairs, `z = +12.41` Same-Bifolio Affinity, Cross-Section
  Citation > Same-Section Diff-Quire Citation `1.58x`, PageRank Centrality,
  Top-25 Master Hubs, Top-25 Cross-Section Routers, and Top-25 6-Domain Bridges).
- Generates `data/attack132_milestone_150_discoveries_and_226folio_compendium.json`
  and `notes/MILESTONE_150_DISCOVERIES_AND_226FOLIO_INDEX.md`.
"""

import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
A129_JSON = ROOT / "data" / "attack129_quire14_7page_exegetical_translator.json"
A130_JSON = ROOT / "data" / "attack130_preface_titles_and_quire_boundary_translator.json"
A131_JSON = ROOT / "data" / "attack131_global_226folio_citation_pagerank_graph.json"
OUT_JSON = ROOT / "data" / "attack132_milestone_150_discoveries_and_226folio_compendium.json"
OUT_MD = ROOT / "notes" / "MILESTONE_150_DISCOVERIES_AND_226FOLIO_INDEX.md"


def main():
    d129 = json.loads(A129_JSON.read_text(encoding="utf-8"))
    d130 = json.loads(A130_JSON.read_text(encoding="utf-8"))
    d131 = json.loads(A131_JSON.read_text(encoding="utf-8"))

    summary_out = {
        "attack": 132,
        "phase": 143,
        "discovery": 149,
        "title": "Milestone 150-Discovery & Complete 226-Folio Master Index Compendium",
        "wave30_highlights": {
            "quire14_locus_split_z": d129["summary"]["locus_split_permutation_test"]["z_score"],
            "quire14_total_tokens": d129["summary"]["total_tokens"],
            "quire14_paragraphs": d129["summary"]["n_exegetical_paragraphs"],
            "pt_titles_count": d130["right_justified_pt_titles"]["total_pt_lines"],
            "pt_outer_wrapper_b1_pct": d130["right_justified_pt_titles"]["outer_wrapper_b1_pct"],
            "pt_nominal_deictic_polarity_z": d130["right_justified_pt_titles"]["title_nominal_deictic_polarity_test"]["z_score"],
            "global_graph_pairs": d131["graph_overview"]["n_total_pairs"],
            "same_bifolio_sheet_z": d131["graph_overview"]["same_bifolio_sheet_permutation_test"]["z_score"],
            "cross_section_vs_same_section_diff_quire_norm_lift": round(
                d131["graph_overview"]["codicological_4tier_distance_decay"]["TIER4_CROSS_SECTION"]["mean_size_normalized_idf"]
                / d131["graph_overview"]["codicological_4tier_distance_decay"]["TIER3_SAME_SECTION_DIFF_QUIRE"]["mean_size_normalized_idf"],
                3,
            ),
            "top_pagerank_folio": d131["top25_global_pagerank_hubs"][0]["folio"],
            "top_cross_section_router_folio": d131["top25_normalized_cross_section_routers"][0]["folio"],
            "top_6domain_entropy_bridge_folio": d131["top25_universal_6domain_entropy_bridges"][0]["folio"],
        },
    }
    OUT_JSON.write_text(json.dumps(summary_out, indent=2), encoding="utf-8")

    md = []
    md.append("# Milestone 150-Discovery & Complete 226-Folio Master Index Compendium (`Attacks 129–132` / `Discoveries 146–149`)\n")
    md.append("> **Scope**: This compendium synthesizes **Autonomous Wave 30 (`Phases 140–143` / `Attacks 129–132` / `Discoveries 146–149`)**, completing our full-folio/locus structural translation across every section of the Voynich Manuscript (**Quire 14 `f85r1–f86v3 + fRos`**, **`f1r` Master Preface**, **all `10` Right-Justified `=Pt` Titles**, **Special Folios `f57v, f65r/v, f116v`**, **20-Quire Opening/Closing Boundaries**, and the **Global 226-Folio Citation & PageRank Graph `G = (V_226, E_IDF)` across all `25,651` folio pairs**).\n")

    md.append("---\n")
    md.append("## Part I: Executive Summary of Wave 30 Discoveries (`Discoveries 146–149`)\n")
    md.append("1. **Discovery 146 (`Attack 129` — Complete Quire 14 `f85r1–f86v3 + fRos` 7-Page Foldout & 21-Paragraph Exegetical Translator, $z = +15.19$)**:\n")
    md.append("   - Across all `7` foldout pages of **Quire 14 (`$Q=N`, `2,339` tokens, Scribe 2 `$H=2`, Currier B `$L=B`, `$B=1`)**, tokens stratify into a **4-Tier Functional Locus Step-Function**:\n")
    md.append("     - **Tier 1 (`@L0` Diagram Sphere/Element Labels, `158` tokens)**: **`56.96%` `o-` nominal**, **`0.63%` `qo-` active**, **`4.43%` `ch-/sh-` bench**, **`4.43%` `-aiin` dose**, **`18.35%` `-dy` state** (`mean_len = 5.614` chars).\n")
    md.append("     - **Tier 2 (`@Cc` Circular Ring Inscriptions, `511` tokens)**: **`46.58%` `o-` nominal**, **`3.33%` `qo-` active**, **`13.89%` `ch-/sh-` bench**, **`11.55%` `l-/ol-` applicative**, **`13.11%` `-aiin` dose** (`mean_len = 4.941` chars).\n")
    md.append("     - **Tier 3 (`@Pb` Bounded Seasonal/Sphere Wedges, `365` tokens — the 4 cardinal seasonal quadrants `<!N, E, S, W>` of `f85r2` and the corner/causeway boxes of `fRos`)**: **`o-` drops `2.8×` (`46.58% -> 16.71%`)**, while **Active Boiling `qo-` surges `4.6×` (`3.33% -> 15.34%`)**, `ch-/sh-` bench jumps to **`19.18%`**, `-edy` simmering jumps to **`13.97%`**, and `-aiin` measured dose peaks at **`17.81%`**!\n")
    md.append("     - **Tier 4 (`@P0` Exegetical Prose Paragraphs, `1,305` tokens across `21` paragraphs on `f85r1, f86v4, f86v6, f86v5, f86v3`)**: **`19.62%` `o-` nominal**, **`13.87%` `qo-` active**, **`17.55%` `ch-/sh-` bench**, **`11.95%` `l-/ol-` applicative**, **`16.25%` `-aiin` dose**, **`10.50%` `-dy`**.\n")
    md.append("   - In a `1,000`-trial permutation test of the `(o_nom - qo)` spread between Quire 14's Nominal Loci (`@L0 ∪ @Cc`, `669` tokens) and Procedural Loci (`@Pb ∪ @P0`, `1,670` tokens), the observed `+0.4155` spread vs. `-0.0002 ± 0.0274` null achieves **$z = +15.19$ ($p < 0.0001$)**.\n")
    md.append("   - Visually verified on [pages/f85r1_opening_exegetical_preface_enh.png](../pages/f85r1_opening_exegetical_preface_enh.png) and the 3-panel foldout spread [pages/f85r2_f86v4_f86v6_cosmological_exegetical_spread_enh.png](../pages/f85r2_f86v4_f86v6_cosmological_exegetical_spread_enh.png).\n\n")

    md.append("2. **Discovery 147 (`Attack 130` — Master Preface `f1r`, Corpus-Wide Right-Justified Titles `=Pt` Polarity Law $z = +4.81$, and 20-Quire Boundary Law)**:\n")
    md.append("   - Across all `226` folios of the Voynich Manuscript, there are exactly **`10` right-justified `=Pt` title/rubric lines (`22` tokens)**: **`8 / 10` (`80.0%`) sit on the Outer-Wrapper Bifolio (`$B=1`) of their Quire (`f1r` + `f8r` = Bifolio `A1`, `f25r` = Bifolio `D1`)**, **`5 / 10` (`50.0%`) sit on Quire-Opening Rectos**, and **`0 / 10` (`0.0%`) sit on Quire-Closing Versos**.\n")
    md.append("   - Morphologically, `=Pt` titles invert the prefix-suffix polarity of general prose (`33,217` tokens): **`40.91%` `o-` nominal (`2.53×` lift over `16.19%`)**, **`27.27%` `d-/da-` deictic/topic (`2.90×` lift over `9.40%`)**, vs. **`4.55%` `ch-/sh-` bench (`5.6×` depletion)**, **`4.55%` `qo-` active (`3.4×` depletion)**, and **`0.00%` `l-/ol-` applicative**, achieving a Nominal/Deictic Polarity Index of **`+0.5909` vs. `-0.2122` in general prose (`+0.8031` swing, $z = +4.81$, $p < 0.0001$)**.\n")
    md.append("   - Across all `20` Quires (`18` Opening Rectos, `191` Internal Folios, `18` Closing Versos), **Quire-Closing Versos (`$P=max`) drop by `-44.4%` in prose length (`75.06` vs. `134.94` words on Opening Rectos)**, drop by **`-44.7%` in paragraph count (`1.78` vs. `3.22` paragraphs)**, drop from **`14.74% -> 9.99%` in prose `qo-` active boiling**, and rise to **`30.53%` all-locus `o-` nominal summary closure**.\n")
    md.append("   - Visually verified on [pages/f1r_master_preface_and_pt_titles_enh.png](../pages/f1r_master_preface_and_pt_titles_enh.png).\n\n")

    md.append("3. **Discovery 148 (`Attack 131` — Global 226-Folio Master Citation & PageRank Centrality Graph `G = (V_226, E_IDF)` Across All `25,651` Folio Pairs, $z = +12.41$)**:\n")
    md.append("   - Across all `25,651` folio pairs, size-normalized rare-stem (`2 <= df <= 15`) IDF affinity peaks on **Tier 1 Same Physical Bifolio Sheet-Mates (`0.03253` norm IDF, `38.77%` edges, `2.246×` lift over random node permutation `0.01448 ± 0.00145`, $z = +12.41$, $p < 0.0001$)** and **Tier 2 Same Quire Different Bifolio (`0.03071` norm IDF, `35.89%` edges)**.\n")
    md.append("   - Crucially, **Tier 4 Cross-Section Citation (`0.01510` norm IDF, `1.1335` raw IDF, `25.21%` edges) exceeds Tier 3 Same-Section Different-Quire Citation (`0.00957` norm IDF, `0.4763` raw IDF, `11.98%` edges) by `1.58×` (`2.38×` raw IDF)** — proving mathematically that **Vertical Cross-Section Specimen Referentiality (`Herbal <-> Astro/Zodiac <-> Pharm/Balneo/Starred`) is stronger than horizontal redundancy across different Herbal quires**!\n")
    md.append("   - **Global PageRank Authority (`alpha = 0.85`)** is led by **`f104r` (`3.535×` uniform)** and **`fRos` (`3.265×` uniform)**; **Length-Normalized Cross-Section Routing (`CrossSec_IDF_per_100tok`)** is swept `10 / 10` at the top by **Scribe 4's Astronomical & Zodiac Wheels (`f68r2 = 540.56`, `f67v1 = 380.81`, `f72v2 = 349.49`)**; **Universal 6-Domain Entropy (`max = 2.585` bits)** is led by **`f69v` (`2.438` bits = `94.3%` max)**, **`f83v` (`2.423` bits)**, and **`f69r` (`2.408` bits)**; and the **#1 Cross-Section Edge in the entire codex is `f66r ($I=T) <-> fRos ($I=C)` (`IDF = 32.247`)**!\n\n")

    md.append("---\n")
    md.append("## Part II: Complete Quire 14 (`f85r1–f86v3` + `fRos`, `$Q=N`) 7-Page & 21-Paragraph Exegetical Atlas (`Attack 129`)\n")
    md.append("### 1. The 4-Tier Locus Step-Function Inside Quire 14 ($z = +15.19$)\n")
    md.append("| Locus Tier | Tokens | Unique Stems | Mean Len | `o-` Nom % | `qo-` Act % | `ch-/sh-` % | `l-/ol-` % | `-edy` % | `-aiin` % | `-dy` % |\n")
    md.append("| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |\n")
    for lkey, m in d129["summary"]["locus_summary"].items():
        md.append(
            f"| `{lkey}` | {m['n_tokens']} | {m['n_unique_stems']} | {m['mean_len']} | **{m['o_nom_pct']}%** | **{m['qo_pct']}%** | {m['bench_pct']}% | {m['l_appl_pct']}% | {m['edy_pct']}% | {m['aiin_pct']}% | {m['dy_pct']}% |\n"
        )

    md.append("\n### 2. All 7 Foldout Pages of Quire 14 (`f85r1–f86v3` + `fRos`)\n")
    md.append("| Folio | Section | Title | Tokens | Stems | `o-` % | `qo-` % | `-edy` % | `-aiin` % | Routing IDF (`H / A / Z / B / P / S`) | Top External Match |\n")
    md.append("| :--- | :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |\n")
    for p in d129["page_profiles"]:
        m = p["metrics"]
        sr = p["section_routing_idf"]
        top_ext = p["top_external_folios"][0] if p["top_external_folios"] else {"folio": "-", "idf": 0, "shared_stems": []}
        md.append(
            f"| **`{p['folio']}`** | `{p['section']}` | {p['title']} | {m['n_tokens']} | {m['n_unique_stems']} | {m['o_nom_pct']}% | {m['qo_pct']}% | {m['edy_pct']}% | {m['aiin_pct']}% | `{sr['H']:.1f} / {sr['A']:.1f} / {sr['Z']:.1f} / {sr['B']:.1f} / {sr['P']:.1f} / {sr['S']:.1f}` | `{top_ext['folio']}` (`{top_ext['idf']}`: `{','.join(top_ext['shared_stems'][:3])}`) |\n"
        )

    md.append("\n### 3. Complete 21-Paragraph Exegetical Prose Directory of Quire 14\n")
    md.append("| Paragraph ID | Lines | Tokens | Stems | `o-` % | `qo-` % | `-edy` % | `-aiin` % | Diagram IDF (`Stems`) | Dominant Ext Sec | Opening Structural Gloss |\n")
    md.append("| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- | :---: | :--- |\n")
    for pp in d129["exegetical_paragraphs"]:
        m = pp["metrics"]
        dst = ",".join(pp["diagram_shared_stems"][:4])
        md.append(
            f"| **`{pp['para_id']}`** | `{pp['line_range']}` | {m['n_tokens']} | {m['n_unique_stems']} | {m['o_nom_pct']}% | {m['qo_pct']}% | {m['edy_pct']}% | {m['aiin_pct']}% | `{pp['diagram_shared_idf']}` (`{dst}`) | `{pp['dominant_external_section']}` | `{pp['opening_gloss'][:75]}...` |\n"
        )

    md.append("\n---\n")
    md.append("## Part III: Master Preface (`f1r`), All `10` Right-Justified Titles (`=Pt`), and 20-Quire Boundary Law (`Attack 130`)\n")
    md.append("### 1. Complete Catalogue & Structural Translation of All `10` Right-Justified Titles (`=Pt`, $z = +4.81$)\n")
    md.append("| Folio | Line | Locus | Sec | Hand | Lang | Tokens | EVA Transcription | Interlinear Structural Translation | Same-Folio Shared Stems |\n")
    md.append("| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- | :--- | :--- |\n")
    for pt in d130["right_justified_pt_titles"]["all_pt_titles"]:
        md.append(
            f"| **`{pt['folio']}`** | `{pt['line_id']}` | `{pt['loc']}` | `{pt['section']}` | `{pt['hand']}` | `{pt['language']}` | {pt['n_tokens']} | `{pt['eva']}` | `{pt['gloss']}` | `{','.join(pt['shared_stems_with_same_folio'])}` |\n"
        )

    md.append("\n### 2. Block-by-Block Translation of `f1r` (Master Codex Preface)\n")
    md.append("| Block ID | Type | Lines | Tokens | `o-` % | `d-` % | `ch-/sh-` % | `qo-` % | Routing IDF (`H / P / S`) | Opening Structural Translation | Closing Structural Translation |\n")
    md.append("| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- | :--- |\n")
    for blk in d130["f1r_master_preface_blocks"]:
        m = blk["metrics"]
        sr = blk["section_routing_idf"]
        md.append(
            f"| **`{blk['block_id']}`** | `{blk['type']}` | `{blk['line_range']}` | {m['n_tokens']} | {m['o_nom_pct']}% | {m['d_top_pct']}% | {m['bench_pct']}% | {m['qo_pct']}% | `{sr['H']:.1f} / {sr['P']:.1f} / {sr['S']:.1f}` | `{blk['opening_gloss'][:65]}` | `{blk['closing_gloss'][:55]}` |\n"
        )

    md.append("\n### 3. The 20-Quire Codicological Boundary Law (`Opening Recto` vs. `Internal` vs. `Closing Verso`)\n")
    md.append("| Boundary Position | Scope | Folios | Mean Words/Folio | Mean Paras/Folio | Total `=Pt` Titles | `o-` Nom % | `qo-` Act % | `ch-/sh-` % | `l-/ol-` % | `-edy` % | `-aiin` % |\n")
    md.append("| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |\n")
    for scope_name, sdict in [("ALL_LOCI", d130["quire_boundary_summary"]["ALL_LOCI"]), ("PROSE_ONLY_P0", d130["quire_boundary_summary"]["PROSE_ONLY_P0"])]:
        for bpos, bm in sdict.items():
            md.append(
                f"| **`{bpos}`** | `{scope_name}` | {bm['n_folios']} | **{bm['mean_tokens_per_folio']}** | **{bm['mean_paras_per_folio']}** | **{bm['total_pt_titles']}** | **{bm['o_nom_pct']}%** | **{bm['qo_pct']}%** | {bm['bench_pct']}% | {bm['l_appl_pct']}% | {bm['edy_pct']}% | {bm['aiin_pct']}% |\n"
            )

    md.append("\n---\n")
    md.append("## Part IV: The Global 226-Folio Master Citation & PageRank Centrality Graph (`Attack 131`)\n")
    md.append("### 1. Four-Tier Codicological Distance Decay Across All `25,651` Folio Pairs ($z = +12.41$)\n")
    md.append("| Codicological Distance Tier | Folio Pairs (`N`) | Non-Zero Edge % | Mean Raw Rare-Stem IDF | Mean Size-Normalized IDF | Lift vs. Tier 3 (`Same-Sec Diff-Quire`) |\n")
    md.append("| :--- | :---: | :---: | :---: | :---: | :---: |\n")
    t3_norm = d131["graph_overview"]["codicological_4tier_distance_decay"]["TIER3_SAME_SECTION_DIFF_QUIRE"]["mean_size_normalized_idf"]
    for tkey, tm in d131["graph_overview"]["codicological_4tier_distance_decay"].items():
        lift_t3 = round(tm["mean_size_normalized_idf"] / t3_norm, 2) if t3_norm > 0 else 1.0
        md.append(
            f"| **`{tkey}`** | {tm['n_pairs']} | **{tm['nonzero_edge_pct']}%** | `{tm['mean_raw_idf']}` | **`{tm['mean_size_normalized_idf']}`** | **`{lift_t3}×`** |\n"
        )

    md.append("\n### 2. Top-25 Global PageRank Hub Folios of the Voynich Manuscript\n")
    md.append("| Rank | Folio | Sec (`$I`) | Quire (`$Q`) | Bifolio (`$B`) | Hand (`$H`) | Words | Unique Stems | PageRank Lift (`× Uniform`) | Weighted Degree IDF | Cross-Sec IDF | 6-Domain Entropy (`bits`) | Top-2 Citation Neighbors |\n")
    md.append("| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |\n")
    for idx_r, r in enumerate(d131["top25_global_pagerank_hubs"], 1):
        nb_str = ", ".join(f"{n['folio']}({n['section']}:{n['idf']})" for n in r["top_neighbors"][:2])
        md.append(
            f"| {idx_r} | **`{r['folio']}`** | `{r['section']}` | `{r['quire']}` | `{r['bifolio']}` | `{r['hand']}` | {r['n_tokens']} | {r['n_unique_stems']} | **`{r['pagerank_lift_vs_uniform']}×`** | `{r['total_weighted_degree_idf']}` | `{r['cross_section_idf']}` | `{r['six_domain_entropy_bits']}` | `{nb_str}` |\n"
        )

    md.append("\n### 3. Top-25 Length-Normalized Cross-Section Router Folios (`>= 60` words)\n")
    md.append("| Rank | Folio | Sec (`$I`) | Quire (`$Q`) | Hand (`$H`) | Words | Cross-Section IDF / 100w | PageRank Lift | 6-Domain Entropy (`bits`) | Top-2 Citation Neighbors |\n")
    md.append("| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |\n")
    for idx_r, r in enumerate(d131["top25_normalized_cross_section_routers"], 1):
        nb_str = ", ".join(f"{n['folio']}({n['section']}:{n['idf']})" for n in r["top_neighbors"][:2])
        md.append(
            f"| {idx_r} | **`{r['folio']}`** | `{r['section']}` | `{r['quire']}` | `{r['hand']}` | {r['n_tokens']} | **`{r['cross_section_idf_per_100tok']}`** | `{r['pagerank_lift_vs_uniform']}×` | `{r['six_domain_entropy_bits']}` | `{nb_str}` |\n"
        )

    md.append("\n### 4. Top-25 Universal 6-Domain Entropy Bridge Folios (`max = 2.585` bits)\n")
    md.append("| Rank | Folio | Sec (`$I`) | Quire (`$Q`) | Hand (`$H`) | Words | 6-Domain Entropy (`bits`) | % of Max Entropy | Weighted Degree IDF | PageRank Lift | Top-2 Citation Neighbors |\n")
    md.append("| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |\n")
    for idx_r, r in enumerate(d131["top25_universal_6domain_entropy_bridges"], 1):
        nb_str = ", ".join(f"{n['folio']}({n['section']}:{n['idf']})" for n in r["top_neighbors"][:2])
        pct_max = round(100.0 * r["six_domain_entropy_bits"] / 2.58496, 1)
        md.append(
            f"| {idx_r} | **`{r['folio']}`** | `{r['section']}` | `{r['quire']}` | `{r['hand']}` | {r['n_tokens']} | **`{r['six_domain_entropy_bits']}`** | **{pct_max}%** | `{r['total_weighted_degree_idf']}` | `{r['pagerank_lift_vs_uniform']}×` | `{nb_str}` |\n"
        )

    md.append("\n### 5. Top-30 Strongest Inter-Folio Rare-Stem Citation Edges Across the Entire Manuscript\n")
    md.append("| Rank | Folio A (`Sec, Quire`) | Folio B (`Sec, Quire`) | Codicological Tier | Rare-Stem IDF Weight | Size-Normalized Weight | Top Shared Rare Stems (`2 <= df <= 15`) |\n")
    md.append("| :---: | :--- | :--- | :--- | :---: | :---: | :--- |\n")
    for idx_e, e in enumerate(d131["top30_inter_folio_citation_edges"], 1):
        md.append(
            f"| {idx_e} | **`{e['folio_a']}`** (`{e['section_a']}, Q={e['quire_a']}`) | **`{e['folio_b']}`** (`{e['section_b']}, Q={e['quire_b']}`) | `{e['tier']}` | **`{e['idf_weight']}`** | `{e['norm_weight']}` | `{', '.join(e['shared_rare_stems'])}` |\n"
        )

    OUT_MD.write_text("".join(md), encoding="utf-8")
    print(f"[Attack 132] Saved {OUT_JSON} and {OUT_MD}")


if __name__ == "__main__":
    main()
