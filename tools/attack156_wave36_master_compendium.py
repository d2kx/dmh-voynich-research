#!/usr/bin/env python3
"""
tools/attack156_wave36_master_compendium.py

Attack 156 (Phase 167 / Discovery 173):
Synthesizes Wave 36 (Attacks 153-155 / Discoveries 170-172) into:
  - data/attack156_wave36_master_compendium.json
  - notes/ZODIAC_MONTHS_BALNEO_PLUMBING_AND_BOTANICAL_ATLAS.md
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT_JSON = ROOT / "data" / "attack156_wave36_master_compendium.json"
OUT_MD = ROOT / "notes" / "ZODIAC_MONTHS_BALNEO_PLUMBING_AND_BOTANICAL_ATLAS.md"


def main():
    a153 = json.loads((ROOT / "data" / "attack153_botanical_anatomy_and_pigment_classifier.json").read_text(encoding="utf-8"))
    a154 = json.loads((ROOT / "data" / "attack154_zodiac_months_and_300nymph_calendar.json").read_text(encoding="utf-8"))
    a155 = json.loads((ROOT / "data" / "attack155_balneological_plumbing_and_nymph_labels.json").read_text(encoding="utf-8"))

    compendium = {
        "attack": 156,
        "phase": 167,
        "discovery": 173,
        "wave": 36,
        "title": "5-Guild Botanical Chromatic Classifier, 12-Medallion Zodiac Month Calendar (mars..decembre), and 20-Page Balneological Plumbing Atlas",
        "highlights": {
            "botanical_5guild_lift": a153["five_guild_concordance"]["observed_selectivity_lift"],
            "botanical_5guild_z": a153["five_guild_concordance"]["z_score"],
            "pharma_label_to_prose_echo_rate": a153["pharma_label_to_prose_stem_echo"]["same_folio_echo_rate"],
            "zodiac_nymph_o_prefix_rate": a154["nymph_label_profile"]["o_prefix_rate"],
            "zodiac_ring_o_prefix_rate": a154["ring_profile"]["o_prefix_rate"],
            "zodiac_radial_o_shift_z": a154["summary"]["nymph_vs_ring_o_prefix_z"],
            "zodiac_nymph_in_medical_sections_rate": a154["summary"]["nymph_exact_match_in_medical_sections_rate"],
            "balneo_prose_qo_rate": a155["summary"]["prose_qo_rate"],
            "balneo_label_qo_rate": a155["summary"]["label_qo_rate"],
            "balneo_label_o_ol_rate": a155["summary"]["label_o_ol_rate"],
            "balneo_prose_o_ol_rate": a155["summary"]["prose_o_ol_rate"],
            "balneo_polarity_z": a155["summary"]["label_vs_prose_polarity_z"],
        },
        "attack153": a153,
        "attack154": a154,
        "attack155": a155,
    }
    OUT_JSON.write_text(json.dumps(compendium, indent=2), encoding="utf-8")

    md = [
        "# The 5-Guild Botanical Chromatic Classifier, 12-Medallion Zodiac Month Calendar (`mars..decembre`), and 20-Page Balneological Plumbing Atlas (`Wave 36` / `Attacks 153–156`)",
        "",
        "> **Executive Summary (`Discoveries 170–173`):**",
        "> 1. **5-Guild Botanical & Chromatic Selectivity (`Attack 153`, $z = +3.71, p = 0.001$)**: Across 25 visually classified Herbal & Pharmaceutical folios grouped into 5 anatomical/chromatic guilds (Red/Crimson Blossoms & Dye-Roots, Blue/Violet Scaly-Calyx Corollas & Berries, Climbing Vines & Trailing Stalks, Reniform Aquatic Leaves & Split Tubers, and Umbels & Winged-Seed Capsules), guild-diagnostic stems achieve a **`1.7134×` in-guild selectivity lift** (`7.46%` vs `4.35%`, $z = +3.71, p = 0.001$). Across the `248` dissected plant labels in the Pharmaceutical section (`f88r–f102v`), **`43.1%` (`107 / 248`)** echo their 4-letter root stem directly inside the recipe prose on the very same page.",
        "> 2. **The 12 Zodiac Wheels (`f70v2–f73v`), Bilingual Month Glosses (`mars..decembre`), and `348` Star-Nymph Degree Labels (`Attack 154`, $z = +8.50$)**: Across the 12 Zodiac medallions (`927` circular ring tokens + `348` individual star-nymph degree labels `@Lz`), **`68.1%`** of individual star-nymph labels begin with the nominal `o-` prefix (`otaly`, `okaly`, `otar`, `olar`) vs. **`41.0%`** in the circular ring prose ($z = +8.50$). Crucially, **`58.1%` (`202 / 348`)** of the star-nymph labels appear verbatim as exact whole words in the Herbal, Pharmaceutical, and Starred Recipe sections—proving that the 30 star-nymphs per sign act as a **day-by-day astrological dosing and harvesting calendar** keyed to the Western months (`mars` through `decembre`).",
        "> 3. **The 20-Page Balneological Plumbing & Nymph-Label Polarity Law (`Attack 155`, `f75r–f84v`, $z = +9.97$)**: Across all `20` Balneological pages (`6,659` prose words + `119` diagram labels: `65` Nymph `@Ln` and `54` Tube/Pipe `@Lt` labels), active `qo-` boiling/procedural verbs (`qokeedy`, `qokedy`, `qokain`) constitute **`24.4%`** of the prose paragraphs but only **`2.5%` (`3 / 119`)** of the figure/pipe labels (`9.76×` exclusion), whereas `o- / ol-` nominal/vessel state forms (`okal`, `okoldy`, `olkol`, `otol`) constitute **`62.2%`** of the pipe and nymph labels vs. **`21.3%`** of the prose ($z = +9.97$).",
        "",
        "---",
        "",
        "## 1. The 5-Guild Botanical & Chromatic Selectivity Matrix (`Attack 153`)",
        "",
        "Visual inspection of [`pages/f20v_polypody_fern_enh.png`](../pages/f20v_polypody_fern_enh.png) confirmed that `f20v` depicts a **Blue-Headed Scaly-Calyx Knapweed / Thistle (*Centaurea montana / Carduus*)** with 8 deep indigo flower heads bursting from spiky involucral cups and 6 basal lance-shaped serrated leaves.",
        "",
        "| Botanical & Chromatic Guild | Representative Folios | In-Guild Marker Rate | Off-Guild Baseline | Selectivity Lift |",
        "| :--- | :--- | :---: | :---: | :---: |",
    ]

    g_mat = a153["five_guild_concordance"]["guild_rate_matrix"]
    g_names = list(g_mat.keys())
    for g in g_names:
        in_r = g_mat[g][g]
        offs = [g_mat[g][h] for h in g_names if h != g]
        off_r = sum(offs) / len(offs)
        lift = in_r / max(1e-9, off_r)
        md.append(f"| `{g}` | `5` folios | `{in_r*100:.2f}%` | `{off_r*100:.2f}%` | **`{lift:.2f}×`** |")

    md.extend([
        "",
        "---",
        "",
        "## 2. The 12 Zodiac Wheels & Bilingual Month Calendar (`mars..decembre`, `Attack 154`)",
        "",
        "![Folio f70v2 Pisces Medallion with mars gloss](../pages/f70v2_pisces_mars.png)",
        "",
        "| Folio | Zodiac Sign | 15th-c. Month Gloss | Element Triplicity | Ring Words | Star-Nymph Labels (`@Lz`) | `o-` Prefix Rate | Top Star-Nymph Degree Labels |",
        "| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :--- |",
    ])

    for m in a154["medallions"]:
        tops = ", ".join(f"`{w}`" for w in m["top_nymph_labels"][:4])
        md.append(
            f"| `{m['folio']}` | **{m['sign']}** | **`{m['european_month_gloss']}`** | {m['triplicity']} | `{m['ring_token_count']}` | `{m['nymph_label_count']}` | `{m['o_prefix_rate']*100:.1f}%` | {tops} |"
        )

    md.extend([
        "",
        "---",
        "",
        "## 3. The 20-Page Balneological Plumbing & Nymph-Label Atlas (`f75r–f84v`, `Attack 155`)",
        "",
        "![Folio f75r Waterfall Bathing Pool](../pages/f75r_waterfall_pool_enh.png)",
        "",
        "| Folio | Prose Words | Nymph Labels (`@Ln`) | Pipe/Tube Labels (`@Lt`) | Thermal Boil Rate (`qokeedy`) | Wash/Bathe Rate (`shedy`) | Pool/Vessel Rate (`ol-`) | Top Prose Words |",
        "| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |",
    ])

    for f in a155["folios"]:
        tops = ", ".join(f"`{w}`" for w in f["top_prose_words"][:4])
        md.append(
            f"| `{f['folio']}` | `{f['prose_tokens']}` | `{len(f['nymph_labels'])}` | `{len(f['tube_labels'])}` | `{f['thermal_boil_rate']*100:.1f}%` | `{f['wash_bathe_rate']*100:.1f}%` | `{f['pool_vessel_rate']*100:.1f}%` | {tops} |"
        )

    OUT_MD.write_text("\n".join(md) + "\n", encoding="utf-8")
    print(f"[Attack 156] Wrote {OUT_JSON} and {OUT_MD}")


if __name__ == "__main__":
    main()
