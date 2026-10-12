#!/usr/bin/env python3
"""
Attack 220 (Discovery 237): Wave 52 Master Synthesis & Compendium (Attacks 217-220 / Discoveries 234-237).
Consolidates the 100% Non-Herbal Visual Scan Milestone (98/98 folios), 100% Quire 20 Recipe Completion (25/25 folios),
and 100% Quire 8 Scribe-3/Scribe-5 Bifolium Architecture (8/8 folios).
"""

import json
import os

def main():
    with open(os.path.join("data", "attack217_quire20_25page_completion_f105v_f112_f114r_f115v.json"), "r", encoding="utf-8") as f:
        a217 = json.load(f)
    with open(os.path.join("data", "attack218_100pct_nonherbal_visual_completion_f69v_f70r1_f71r.json"), "r", encoding="utf-8") as f:
        a218 = json.load(f)
    with open(os.path.join("data", "attack219_quire8_f58_f65_conjugate_index_and_missing_bifolia.json"), "r", encoding="utf-8") as f:
        a219 = json.load(f)

    summary = {
        "attack": 220,
        "discovery": 237,
        "wave": 52,
        "release": "v18.0",
        "title": "Wave 52 Master Compendium: 100% Non-Herbal Visual Scan Milestone (98/98 Folios), Quire 20 12-Leaf Recto-Verso Architecture, and Scribe 3's Cross-Language Bridge (f58r-v <-> Quire 20)",
        "milestones": {
            "total_attacks": 220,
            "total_discoveries": 237,
            "non_herbal_visual_coverage": "98/98 (100.0%)",
            "quire20_visual_coverage": "26/26 (100.0%)",
            "quire8_visual_coverage": "8/8 (100.0%)",
            "new_scans_rendered_in_wave52": [
                "pages/f105v_quire20_third_verso_recipes_enh.png",
                "pages/f112r_quire20_tenth_recto_recipes_enh.png",
                "pages/f112v_quire20_tenth_verso_recipes_enh.png",
                "pages/f114r_quire20_twelfth_recto_recipes_enh.png",
                "pages/f115v_quire20_penultimate_verso_recipes_enh.png",
                "pages/f69v_cosmological_28spoke_wheel_enh.png",
                "pages/f70r1_cosmological_6lobe_nebula_wheel_enh.png",
                "pages/f71r_aries_ii_abril_full_medallion_enh.png",
                "pages/f57r_quire8_opening_scribe5_herbal_enh.png",
                "pages/f58v_starred_herbal_index_verso_enh.png",
                "pages/f65v_quire8_scribe3_conjugate_herbal_enh.png"
            ]
        },
        "wave52_highlights": {
            "attack217_discovery234": {
                "quire20_rendered": f"{a217['quire20_visual_completion']['rendered_folios']}/{a217['quire20_visual_completion']['total_folios']} ({a217['quire20_visual_completion']['completion_pct']}%)",
                "same_leaf_mean_jaccard": a217["same_leaf_recto_verso_coupling"]["mean_same_leaf_jaccard"],
                "non_same_leaf_mean_jaccard": a217["same_leaf_recto_verso_coupling"]["mean_non_same_leaf_jaccard"],
                "same_leaf_permutation_z": a217["same_leaf_recto_verso_coupling"]["permutation_z"],
                "same_leaf_permutation_p": a217["same_leaf_recto_verso_coupling"]["permutation_p"],
                "bifolium3_nominal_spike_f105v_aiin_pct": 21.05,
                "bifolium3_nominal_spike_f114r_aiin_pct": 19.35,
                "bifolium6_centerfold_f108v_f111r_jaccard": 0.3087,
                "first_half_seeds_second_half_pct": a217["first_vs_second_half_across_missing_f109_f110"]["first_half_seeds_second_half_token_pct"]
            },
            "attack218_discovery235": {
                "non_herbal_coverage": f"{a218['non_herbal_completion']['rendered_non_herbal_folios']}/{a218['non_herbal_completion']['total_non_herbal_folios']} ({a218['non_herbal_completion']['non_herbal_coverage_pct']}%)",
                "f69v_spoke_o_initial_pct": a218["f69v_28spoke_wheel_analysis"]["spoke_o_initial_pct"],
                "f69v_spokes_covered_by_azc_pct": a218["f69v_28spoke_wheel_analysis"]["spokes_covered_by_azc_corpus_pct"],
                "p127_f70r2_covers_f69v_pct": a218["p127_three_panel_foldout_progression"]["f70r2_to_f69v_token_cov_pct"],
                "p127_f70r2_covers_f70r1_pct": a218["p127_three_panel_foldout_progression"]["f70r2_to_f70r1_token_cov_pct"],
                "aries_spread_nymphs": a218["aries_30degree_spread_f70v1_f71r"]["total_aries_nymphs"],
                "f71r_o_initial_pct": a218["aries_30degree_spread_f70v1_f71r"]["f71r_o_initial_pct"]
            },
            "attack219_discovery236": {
                "quire8_rendered": "8/8 (100.0%)",
                "f58r_q_pct": 7.41,
                "f58v_q_pct": 19.20,
                "f58r_edy_pct": 0.53,
                "f58v_edy_pct": 1.07,
                "f58_raw_cov_by_quire20_pct": a219["f58_cross_section_routing"]["f58_raw_word_covered_by_quire20_pct"],
                "f58_canonical_cov_by_quire20_pct": a219["f58_cross_section_routing"]["f58_canonical_stem_covered_by_quire20_pct"],
                "f58_seeds_quire20_pct": a219["f58_cross_section_routing"]["f58_seeds_quire20_token_pct"],
                "f65v_covered_by_quire20_pct": a219["f65v_conjugate_and_facing_bridge"]["covered_by_quire20_pct"],
                "f65v_covered_by_quire8_rest_pct": a219["f65v_conjugate_and_facing_bridge"]["covered_by_quire8_rest_pct"]
            }
        }
    }

    out_json = os.path.join("data", "attack220_wave52_master_compendium.json")
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    md = """# Wave 52 Master Compendium (`Attacks 217–220` / `Discoveries 234–237` / `v18.0`)

## 1. Executive Summary & Milestone Achievements
In **Wave 52 (`v18.0`)**, we rendered and visually inspected **11 new high-resolution enhanced scans** (`f105v`, `f112r`, `f112v`, `f114r`, `f115v`, `f69v`, `f70r1`, `f71r`, `f57r`, `f58v`, `f65v`), achieving three major visual and codicological milestones across the Voynich Manuscript (`Beinecke MS 408`):
1. **`100.0%` (`98/98` Folios) Visual Scan Coverage of Every Single Non-Herbal Folio in the Manuscript**:
   - **Astronomical (`$I=A`)**: `8/8` (`100.0%`)
   - **Zodiac (`$I=Z`)**: `12/12` (`100.0%`)
   - **Balneological (`$I=B`)**: `19/19` (`100.0%`)
   - **Cosmological (`$I=C`)**: `11/11` (`100.0%`)
   - **Pharmaceutical (`$I=P`)**: `16/16` (`100.0%`)
   - **Text-Only (`$I=T`)**: `7/7` (`100.0%`)
   - **Starred Recipes (`$I=S`)**: `25/25` (`100.0%`)
2. **`100.0%` (`26/26` Folios) Visual & Bifolium Completion of Quire 20 (`f103r–f116v`) and All `$I=S` Starred Pages**:
   - Proved that same-leaf recto-verso pairs (`fXXr <-> fXXv`) across Quire 20 achieve a mean Canonical Stem Jaccard of **`0.2496` vs `0.2247` across non-same-leaf pairs ($z = +3.87, p = 0.00020$)**, while the inner sheet of **Bifolium #3 (`f105v <-> f114r`)** contains the **`#1` (`21.05%`) and `#2` (`19.35%`) highest `-aiin` nominal-suffix pages in all of Quire 20**.
3. **`100.0%` (`8/8` Folios) Visual & Bifolium Completion of Quire 8 (`f57r–f66v`) & Scribe 3's Cross-Language Bridge (`f58r–v` vs Quire 20)**:
   - Proved that Scribe 3's pure-text Starred Herbal Index (`f58r–f58v`, `$H=3, $L=A, $I=S`, `753` words, `7` paragraphs matching the `7` herbal leaves of Quire 8!) decouples `q-` proclitic density (`7.41%` on `f58r` $\to$ `19.20%` on `f58v`, `2.59×` jump) from `-edy` verbal suffixation (`0.53%` on `f58r`, `1.07%` on `f58v`), and that 4-Rule Canonical Normalization lifts coverage of `f58r–v` by Scribe 3's Quire 20 Starred Recipes from **`68.66%` raw words to `84.86%` canonical stems (`1.24×` lift)**.

---

## 2. Summary Table of Wave 52 Attacks (`Attacks 217–220` / `Discoveries 234–237`)

| Attack | Discovery | Focus / Target Folios | Primary Quantitative Finding | Visual & Codicological Proof |
| :--- | :--- | :--- | :--- | :--- |
| **Attack 217** | **Discovery 234** | **Quire 20 (`f103r–f116v`) `100%` Visual & 6-Bifolium Completion (`f105v`, `f112r/v`, `f114r`, `f115v`)** | Same-leaf recto-verso stem Jaccard = **`0.2496` vs `0.2247` ($z = +3.87, p = 0.00020$)**; Bifolium #3 inner sheet (`f105v` `21.05%` `-aiin` + `f114r` `19.35%` `-aiin`) = `#1` and `#2` nominal-suffix pages in Quire 20; Bifolium #6 centerfold (`f108v <-> f111r`) Jaccard = **`0.3087`** (`75.48%` / `81.41%` token cov). | [f105v](../pages/f105v_quire20_third_verso_recipes_enh.png), [f112r](../pages/f112r_quire20_tenth_recto_recipes_enh.png), [f112v](../pages/f112v_quire20_tenth_verso_recipes_enh.png), [f114r](../pages/f114r_quire20_twelfth_recto_recipes_enh.png), [f115v](../pages/f115v_quire20_penultimate_verso_recipes_enh.png) |
| **Attack 218** | **Discovery 235** | **`100%` Non-Herbal Visual Completion (`98/98` Folios): `f69v`, `f70r1`, `f71r`** | `98/98` (`100.0%`) non-Herbal folios rendered; `f69v` (`28` blue/green lunar-mansion turret spokes) has **`60.61%` `o-` initial (`51.52%` `ok-/ot-`)** and **`81.82%` AZC stem coverage**; `f70r2` covers **`57.04%` of `f69v`** and **`50.89%` of `f70r1`** across `p127`; `f70v1 + f71r` = **`15 + 15 = 30` Aries nymphs** (`58.89%` `o-` initial on `f71r`). | [f69v](../pages/f69v_cosmological_28spoke_wheel_enh.png), [f70r1](../pages/f70r1_cosmological_6lobe_nebula_wheel_enh.png), [f71r](../pages/f71r_aries_ii_abril_full_medallion_enh.png) |
| **Attack 219** | **Discovery 236** | **Quire 8 (`f57r–f66v`) `8/8 = 100%` Visual Completion & Scribe 3 Cross-Language Index (`f58r–v`, `f65v`)** | `f58r -> f58v` (`$H=3, $L=A, $I=S`) jumps **`2.59×` in `q-` initial rate (`7.41%` $\to$ `19.20%`)** while keeping `-edy` near zero (`0.53%` / `1.07%`); Quire 20 covers **`84.86%` of `f58r–v` canonical stems** (`68.66%` raw, `1.24×` lift); `f65v` (`45w`) is **`82.22%` covered by Quire 20** and **`73.33%` by Quire 8**. | [f57r](../pages/f57r_quire8_opening_scribe5_herbal_enh.png), [f58v](../pages/f58v_starred_herbal_index_verso_enh.png), [f65v](../pages/f65v_quire8_scribe3_conjugate_herbal_enh.png) |
| **Attack 220** | **Discovery 237** | **Wave 52 Master Synthesis & `v18.0` Explorer Release** | Synchronized `220` Attacks, `237` Discoveries, `66` Plain-English Walkthroughs, `95` Visual Specimens (`SPEC-01..95`), and `20` Interactive Explorer Tabs (`v18.0`). | [explorer/index.html](../explorer/index.html), [notes/PLAIN_ENGLISH_VISUAL_READERS_GUIDE.md](PLAIN_ENGLISH_VISUAL_READERS_GUIDE.md), [notes/VISUAL_BOTANICAL_AND_ASTRO_IDENTIFICATIONS.md](VISUAL_BOTANICAL_AND_ASTRO_IDENTIFICATIONS.md) |

---

## 3. Reproducible Artifacts & Scripts
- [`tools/attack217_quire20_25page_completion_f105v_f112_f114r_f115v.py`](../tools/attack217_quire20_25page_completion_f105v_f112_f114r_f115v.py) $\to$ [`data/attack217_quire20_25page_completion_f105v_f112_f114r_f115v.json`](../data/attack217_quire20_25page_completion_f105v_f112_f114r_f115v.json)
- [`tools/attack218_100pct_nonherbal_visual_completion_f69v_f70r1_f71r.py`](../tools/attack218_100pct_nonherbal_visual_completion_f69v_f70r1_f71r.py) $\to$ [`data/attack218_100pct_nonherbal_visual_completion_f69v_f70r1_f71r.json`](../data/attack218_100pct_nonherbal_visual_completion_f69v_f70r1_f71r.json)
- [`tools/attack219_quire8_f58_f65_conjugate_index_and_missing_bifolia.py`](../tools/attack219_quire8_f58_f65_conjugate_index_and_missing_bifolia.py) $\to$ [`data/attack219_quire8_f58_f65_conjugate_index_and_missing_bifolia.json`](../data/attack219_quire8_f58_f65_conjugate_index_and_missing_bifolia.json)
- [`tools/attack220_wave52_master_compendium.py`](../tools/attack220_wave52_master_compendium.py) $\to$ [`data/attack220_wave52_master_compendium.json`](../data/attack220_wave52_master_compendium.json)
"""
    out_md = os.path.join("notes", "WAVE52_MASTER_COMPENDIUM.md")
    with open(out_md, "w", encoding="utf-8") as f:
        f.write(md)
    print(f"Wrote {out_json} and {out_md}")

if __name__ == "__main__":
    main()
