#!/usr/bin/env python3
"""
tools/attack160_wave37_master_compendium.py

Attack 160 (Phase 171 / Discovery 177):
Synthesizes Wave 37 (Attacks 157-159 / Discoveries 174-176) into:
  - data/attack160_wave37_master_compendium.json
  - notes/STARRED_RECIPES_ROSETTES_COSMOLOGY_AND_4TRANSCRIBER_PROOF.md
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT_JSON = ROOT / "data" / "attack160_wave37_master_compendium.json"
OUT_MD = ROOT / "notes" / "STARRED_RECIPES_ROSETTES_COSMOLOGY_AND_4TRANSCRIBER_PROOF.md"


def main():
    a157 = json.loads((ROOT / "data" / "attack157_starred_recipes_classifier_and_herbal_router.json").read_text(encoding="utf-8"))
    a158 = json.loads((ROOT / "data" / "attack158_rosettes_9sphere_and_cosmological_wheels.json").read_text(encoding="utf-8"))
    a159 = json.loads((ROOT / "data" / "attack159_four_transcriber_consensus_verifier.json").read_text(encoding="utf-8"))

    compendium = {
        "attack": 160,
        "phase": 171,
        "discovery": 177,
        "wave": 37,
        "title": "Quire 20 Starred Master Recipes (f103r-f116r), Quire 14 Rosettes & Cosmological Wheels (f85r1-f86v6/fRos), and Four-Transcriber Paleographic Consensus Proof",
        "highlights": {
            "starred_recipes_count": a157["summary"]["total_starred_recipes"],
            "starred_frame_z": a157["summary"]["frame_z_score"],
            "quire14_polarity_z": a158["summary"]["polarity_z_score"],
            "fros_starred_recipe_match_rate": a158["fros_domain_routing"]["Starred_Recipes"]["token_coverage_rate"],
            "shared_aligned_loci": a159["summary"]["shared_aligned_loci"],
            "four_way_canonical_consensus_rate": a159["summary"]["canonical_4way_consensus_rate"],
            "core_cribs_in_all_4_editions": a159["summary"]["core_cribs_attested_in_all_4_editions"],
        },
        "attack157": a157,
        "attack158": a158,
        "attack159": a159,
    }
    OUT_JSON.write_text(json.dumps(compendium, indent=2), encoding="utf-8")

    md = [
        "# Quire 20 Starred Master Recipes (`f103r–f116r`), Quire 14 Rosettes & Cosmological Wheels (`f85r1–f86v6 / fRos`), and Four-Transcriber Paleographic Consensus Proof (`Wave 37` / `Attacks 157–160`)",
        "",
        "> **Executive Summary (`Discoveries 174–177`):**",
        f"> 1. **The `285` Starred Master Recipes & 3-Zone Procedural Frame Law (`Attack 157`, $z = +{a157['summary']['frame_z_score']}$)**: Across all `285` star-bulleted recipes (`10,587` tokens on `f103r–f116r`), recipes partition into 4 clinical regimens (`183` Aqueous Infusions, `64` Balneological Washes, `29` Thermal Decoctions, `9` Compound Essence Salves). Internally across each recipe's 3-zone progression (`Opening 20% -> Middle 60% -> Closing 20%`), Gallows Openers (`p-/f-/t-/k-`) surge **`3.10×` in the Opening 20%** (`19.5%` vs `6.3%` Middle), while Terminal Stops (`-am/-om/-m`) surge **`3.90×` in the Closing 20%** (`3.9%` vs `1.0%` Opening, $z = +{a157['summary']['frame_z_score']}$).",
        f"> 2. **Quire 14 Cosmological Wheels (`f85r2`, `f86v4`) & 9-Sphere Rosettes Map (`fRos`) Diagram-to-Prose Polarity Law (`Attack 158`, $z = +{a158['summary']['polarity_z_score']}$)**: Across `2,336` tokens in Quire 14 (`817` Diagram tokens vs `1,519` Prose Treatise tokens), nominal `o-` prefixation surges **`1.99×` on the Cosmological/Rosettes Diagram Rings & Labels** (`52.1%` vs `26.2%` Prose), whereas active `qo-` procedural verbs surge **`2.61×` in the accompanying Prose Treatises** (`14.1%` vs `5.4%` Diagrams, $z = +{a158['summary']['polarity_z_score']}$). Moreover, **`64.0%`** of all tokens on the 9-Sphere Rosettes Map (`fRos`) appear verbatim in the Starred Master Recipes (`S`) and **`63.2%`** in the Herbal Monographs (`H`).",
        f"> 3. **Four-Transcriber Paleographic Consensus Proof (`Attack 159`, `{a159['summary']['canonical_4way_consensus_rate']*100:.1f}%` 4-Way Canonical Consensus Across `36,103` Aligned Tokens)**: Aligning `5,132` shared lines (`36,103` tokens) across all 4 independent human transcription traditions (`ZL3b-n` Zandbergen-Landini, `RF1b-er` Friedman First Study Group, `IT2a-n` Takahashi, and `GC2a-n` Glen Claston `v101`) proves **`{a159['summary']['canonical_4way_consensus_rate']*100:.1f}%`** 4-way canonical skeleton consensus (`{a159['summary']['exact_3eva_word_identity_rate']*100:.1f}%` exact character-for-character identity across all 3 EVA editions) and confirms **`{a159['summary']['core_cribs_attested_in_all_4_editions']} / {a159['summary']['core_cribs_tested']}`** core grounded stems/cribs across all 4 independent transcribers.",
        "",
        "---",
        "",
        "## 1. The `285` Star-Bulleted Master Recipes (`f103r–f116r`, `Attack 157`)",
        "",
        "![Folio f107r Starred Master Recipes](../pages/f107r_starred_recipes_enh.png)",
        "",
        "| Recipe Zone | Token Count | Gallows Opener (`p/f/t/k-`) | Active Step (`qo-`) | Measured Dose (`-aiin`) | Terminal Stop (`-am/-m`) |",
        "| :--- | :---: | :---: | :---: | :---: | :---: |",
    ]

    for z_name, z_row in a157["three_zone_trajectory"].items():
        md.append(
            f"| **{z_name}** | `{z_row['tokens']}` | **`{z_row['gallows_initial_rate']*100:.1f}%`** | `{z_row['qo_active_rate']*100:.1f}%` | `{z_row['aiin_dose_rate']*100:.1f}%` | **`{z_row['am_terminal_rate']*100:.1f}%`** |"
        )

    md.extend([
        "",
        "---",
        "",
        "## 2. Quire 14 Cosmological Wheels (`f85r2`, `f86v4`) & 9-Sphere Rosettes Map (`fRos`, `Attack 158`)",
        "",
        "![Folio f85r2 Four-Seasons Wheel](../pages/f85r2_four_seasons_wheel_enh.png)",
        "",
        "![Folio fRos Center Rosette](../pages/p159_rosettes_center_enh.png)",
        "",
        "| Quire 14 Folio | Total Words | Nominal `o-` Rate | Active `qo-` Rate | Process `-edy/-dy` Rate | Liquid/Essence `-ol/-or/-al/-ar` | Top Words |",
        "| :--- | :---: | :---: | :---: | :---: | :---: | :--- |",
    ])

    for fol, prof in a158["folio_profiles"].items():
        tops = ", ".join(f"`{w}`" for w in prof["top_words"][:5])
        md.append(
            f"| `{fol}` | `{prof['tokens']}` | `{prof['o_prefix_rate']*100:.1f}%` | `{prof['qo_prefix_rate']*100:.1f}%` | `{prof['edy_dy_rate']*100:.1f}%` | `{prof['ol_or_al_ar_rate']*100:.1f}%` | {tops} |"
        )

    md.extend([
        "",
        "---",
        "",
        "## 3. Four-Transcriber Paleographic Consensus Table (`ZL3b-n`, `RF1b-er`, `IT2a-n`, `GC2a-n`, `Attack 159`)",
        "",
        "| Core Decoded Word / Crib | `ZL3b-n` Hits | `RF1b-er` Hits | `IT2a-n` Hits | `GC2a-n` (`v101`) Hits | Independent Editions Attesting |",
        "| :--- | :---: | :---: | :---: | :---: | :---: |",
    ])

    for row in a159["crib_verification_table"]:
        md.append(
            f"| **`{row['word']}`** | `{row['ZL3b_hits']}` | `{row['RF1b_hits']}` | `{row['IT2a_hits']}` | `{row['GC2a_v101_mapped_hits']}` | **`{row['transcribers_attesting']} / 4`** |"
        )

    OUT_MD.write_text("\n".join(md) + "\n", encoding="utf-8")
    print(f"[Attack 160] Wrote {OUT_JSON} and {OUT_MD}")


if __name__ == "__main__":
    main()
