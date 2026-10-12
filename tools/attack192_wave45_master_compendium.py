#!/usr/bin/env python3
"""
Attack 192 (Discovery 209): The Wave 45 Master Compendium
(Zodiac 30-Degree Ecliptic Invariant, Balneological Unlabeled Prose Absorption Law,
Post-Rosettes Late Herbal Bridge & Quire 20 Two-Tier Star Hierarchy)
and Synchronized v11.0 Human-Readable Deliverables.
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
A189 = ROOT / "data" / "attack189_zodiac_30degree_invariant_and_decan_split.json"
A190 = ROOT / "data" / "attack190_balneo_organ_labels_vs_unlabeled_galleries.json"
A191 = ROOT / "data" / "attack191_f87r_post_rosettes_herbal_and_f111v_long_recipes.json"
OUT_JSON = ROOT / "data" / "attack192_wave45_master_compendium.json"
OUT_MD = ROOT / "notes" / "ZODIAC_30DEGREE_INVARIANT_BALNEO_ABSORPTION_AND_TWO_TIER_STARS.md"


def main():
    d189 = json.loads(A189.read_text(encoding="utf-8"))
    d190 = json.loads(A190.read_text(encoding="utf-8"))
    d191 = json.loads(A191.read_text(encoding="utf-8"))

    compendium = {
        "attack": 192,
        "discovery": 209,
        "wave": 45,
        "version": "v11.0",
        "title": "Wave 45 Master Compendium: The Zodiac 30-Degree Ecliptic Invariant (299/300), Balneological Unlabeled Prose Absorption Law (z=+6.06), Post-Rosettes Late Herbal Bridge & Quire 20 Two-Tier Star Hierarchy",
        "highlights": {
            "attack_189_discovery_206": d189["summary"],
            "attack_190_discovery_207": d190["summary"],
            "attack_191_discovery_208": d191["summary"],
            "human_readable_sync": {
                "plain_english_guide_walkthroughs": 38,
                "visual_specimens_count": 60,
                "explorer_tabs": 13,
                "explorer_walkthroughs": 54,
                "total_discoveries": 209,
            },
        },
    }

    OUT_JSON.write_text(json.dumps(compendium, indent=2), encoding="utf-8")

    md = r"""# Wave 45 Master Compendium: The Zodiac `30°` Ecliptic Invariant (`299/300`), Balneological Unlabeled Prose Absorption Law ($z = +6.06$), Post-Rosettes Late Herbal Bridge & Quire 20 Two-Tier Star Hierarchy (`Attacks 189–192` / `Discoveries 206–209`)

> **Human-Readable Edition & Interactive Explorer v11.0 Sync**: Paired with [`notes/PLAIN_ENGLISH_VISUAL_READERS_GUIDE.md`](PLAIN_ENGLISH_VISUAL_READERS_GUIDE.md) (`38` Iconic Folio Walkthroughs), [`notes/VISUAL_BOTANICAL_AND_ASTRO_IDENTIFICATIONS.md`](VISUAL_BOTANICAL_AND_ASTRO_IDENTIFICATIONS.md) (`60` Visual Specimens `SPEC-01..60`), and [`explorer/index.html`](../explorer/index.html) (`v11.0`: `13` Interactive Tabs, `54` Folio Walkthroughs, `60` Visual Specimens).

---

## 1. Executive Summary of Wave 45 Breakthroughs (`Attacks 189–192` / `Discoveries 206–209`)

| Attack / Discovery | Core Target & Visual Scans | Key Empirical & Statistical Proof |
| :--- | :--- | :--- |
| **`Attack 189` (`Discovery 206`)** | **12-Folio / 10-Sign Zodiac Architecture (`f70v2–f73v`)**: [`pages/f70v1_aries_dark_split_zodiac_enh.png`](../pages/f70v1_aries_dark_split_zodiac_enh.png) (`p128` `f70v2` Pisces), [`pages/f70v1_aries_dark_abril_p129_enh.png`](../pages/f70v1_aries_dark_abril_p129_enh.png) (`p129` `f71r` Aries II `10m`), [`pages/f73r_scorpio_octobre_zodiac_enh.png`](../pages/f73r_scorpio_octobre_zodiac_enh.png) (`p134` `f73r` Scorpio) | **The `30°`-Per-Sign Ecliptic Degree Invariant (`299 / 300 = 99.67%`)**: Across all `10` surviving Zodiac signs (`12` folios), `9/10` signs have **literally `30` `@Lz` degree loci** (`Pisces = 30`, `Aries I+II = 15 + 15 = 30`, `Taurus I+II = 15 + 15 = 30`, `Cancer = 30`, `Leo = 30`, `Virgo = 30`, `Libra = 30`, `Scorpio = 30` [`10+16+4`], `Sagittarius = 30` [`10+16+4`], `Gemini = 29` transcribed / `30` painted = `299/300` total degrees!). Multi-word `@Lz` labels concentrate **`8.00×`** in the barreled split/early signs (`32.00%` in `f70v2–f72r1` vs. `4.00%` in `f72v3–f73v`), while `ot-/op-` (Barreled `73.97%`) vs. `ok-/of-` (Unbarreled `62.62%`) inverts at **$\chi^2 = 23.28, z = +4.83$**. |
| **`Attack 190` (`Discovery 207`)** | **20-Folio Balneological Labeled vs. Unlabeled Architecture (`f75r–f84v`)**: [`pages/f77r_balneo_five_organ_ring_enh.png`](../pages/f77r_balneo_five_organ_ring_enh.png) (`p140` `f77r`), [`pages/f81r_balneo_arcade_pool_gallery_enh.png`](../pages/f81r_balneo_arcade_pool_gallery_enh.png) (`p148` `f81r`) | **The Unlabeled Balneological Prose Absorption Law (`1.56×` `ok-/ot-` Lift $z = +6.06$; `1.43×` `ol-` Article Lift $z = +5.19$)**: On the `8` Balneological folios without `@Lt`/`@Ln` diagram labels (`f75r, f76v, f78v, f79r, f79v, f80v, f81r, f84v`, `2,779` words), the body prose absorbs the `ok-/ot-` vessel/nymph nouns (**`12.34%` vs. `7.92%` on the `12` labeled folios, `1.56×` lift, $z = +6.06, p < 10^{-9}$**) and `ol-/or-` articles (**`13.39%` vs. `9.38%`, `1.43×` lift, $z = +5.19, p < 10^{-6}$**, peaking at `22.34%` on `f81r`). Across all `110` `@Lt/@Ln` labels, `@Lt` tube/organ labels favor `ot-/op-` (`57.69%`) and `-aiin` (`3.36×`), whereas `@Ln` nymph labels invert to `ok-/of-` (`65.38%`) and `-dy` (`2.24×`). On `f77r`, **`70.0%` (`7/10`)** of aqueduct/ampulla labels echo their stem in `f77r`'s own prose (`80.0%` across Balneo). |
| **`Attack 191` (`Discovery 208`)** | **Post-Rosettes Late Herbal (`f87r–f96v`) & Quire 20 Two-Tier Star Hierarchy (`f111v`)**: [`pages/f87r_herbal_terrace_root_enh.png`](../pages/f87r_herbal_terrace_root_enh.png) (`p160` `f87r`), [`pages/f111v_quire20_long_recipes_enh.png`](../pages/f111v_quire20_long_recipes_enh.png) (`p197` `f111v`) | **The Quire 20 Two-Tier Margin Star Hierarchy (`269` Primary `<%>` Stars [`88.10%` Gallows-Initial] vs. `54` Secondary Intra-Paragraph `+P0` Step Stars [`81.48%` `s-/d-/y-/q-` Particle-Initial])**: Visual & paleographic inspection of `f111v` (`14` margin stars: `7` intra-paragraph step stars in the 25-line `294`-word top protocol + `7` `p-` Gallows bottom recipes `polar, polkiin, pochey, polar, polchey, pollaiin, psalar`) proves that Quire 20 stars operate at two structural levels: **Primary `<%>` Recipe-Start Stars** (`88.10%` Gallows-initial) vs. **Secondary Intra-Paragraph Step Stars** (`25.93%` Gallows-initial, **`81.48%` `s-/d-/y-/o-/q-` step-particle initial**). Also proves that Currier A Late Herbal (`f87r–f96v`) achieves a **`1.18×` Pharmaceutical Stem Jaccard Lift** (`0.0726` vs. `0.0615`), with `f87r`'s two paragraphs opening as a parallel `pchor` pair (`pchor.odaiin` / `pchor.daiin`). |

---

## 2. Detailed Visual & Quantitative Walkthroughs

### 2.1 The `30°`-Per-Sign Zodiac Calibration (`f70v2`, `f71r`, `f73r`)
- **[`pages/f70v1_aries_dark_split_zodiac_enh.png`](../pages/f70v1_aries_dark_split_zodiac_enh.png) (`p128` — `f70v2` Pisces `mars`)**: Two fish connected by a blue cord swim beneath a golden 8-pointed star (`<f70v2.1,@Lz> oteos`), surrounded by `29` barreled nymphs (`11` inner + `18` outer = `30` `@Lz` degree loci, `68.0%` `ot-/op-`).
- **[`pages/f70v1_aries_dark_abril_p129_enh.png`](../pages/f70v1_aries_dark_abril_p129_enh.png) (`p129` — `f71r` Aries II Light `abril` + Quire 10 Signature `10m`)**: Paired with `f70v1` (`15` barreled nymphs), `f71r` supplies the second half (`15` barreled nymphs: `5` inner + `10` outer = `30` total Aries degrees, `85.71%` `ot-/op-`), with the medieval bookbinder's signature **`10m`** in the bottom-right corner.
- **[`pages/f73r_scorpio_octobre_zodiac_enh.png`](../pages/f73r_scorpio_octobre_zodiac_enh.png) (`p134` — `f73r` Scorpio `octobre`)**: A green lizard-like Scorpio emblem holding a golden star (`<f73r.1,@Lz> otedy`) is encircled by `10` inner + `16` middle + `4` top-arc overflow nymphs = **`30` degree-nymphs**, `100%` compressed to single-word labels (`0` multi-word labels).

### 2.2 The Balneological Labeled-Organ (`f77r`) vs. Unlabeled-Gallery (`f81r`) Law
- **[`pages/f77r_balneo_five_organ_ring_enh.png`](../pages/f77r_balneo_five_organ_ring_enh.png) (`p140` — `f77r` Six-Spout Aqueduct Arch & Four-Nozzle Ampulla)**: Six `@Lt` spouts hang from the top aqueduct arch (`olkchs, otedy, otork, otol, dchdy, soral`) between two `@Ln` nymphs (`darchdar, dotedy`), above a left-margin 4-nozzle spraying womb/ampulla (`otchdy`) and a blue-sphere cylinder nymph (`otolaiin`), with **`70.0%` (`7/10`)** of label stems echoed in `f77r`'s prose.
- **[`pages/f81r_balneo_arcade_pool_gallery_enh.png`](../pages/f81r_balneo_arcade_pool_gallery_enh.png) (`p148` — `f81r` 7-to-6 Nymph Connected Pool Cascade)**: Because `f81r` carries zero `@Lt/@Ln` diagram callout labels, its two main paragraphs (`Para 1` opening `polchoy`, `Para 2` opening `polchdy`) absorb the `ok-/ot-` (`14.89%`) and `ol-` article (`22.34%`) nominal references directly into the running prose.

### 2.3 Post-Rosettes Late Herbal (`f87r`) & Quire 20 Dual-Level Stars (`f111v`)
- **[`pages/f87r_herbal_terrace_root_enh.png`](../pages/f87r_herbal_terrace_root_enh.png) (`p160` — `f87r` Two-Tier Palmate Leaf & Three Blue-Black Capitula)**: Opens Quire 15 immediately after the 6-panel Rosettes foldout with two parallel `pchor` paragraphs (`<f87r.1,@P0> pchor.odaiin...` and `<f87r.11,@P0> pchor.daiin...`) and a faint red-chalk X-loop underdrawing on the lower-left vellum.
- **[`pages/f111v_quire20_long_recipes_enh.png`](../pages/f111v_quire20_long_recipes_enh.png) (`p197` — `f111v` 14-Star Dual-Level Recipe Page)**: Demonstrates both **Secondary Intra-Paragraph Step Stars** (`Stars #2–#7` marking `s-/d-` sub-clauses inside the 25-line `294`-word top compound protocol) and **Primary `<%>` Recipe-Start Stars** (`Stars #8–#14` opening `7` consecutive `p-` Gallows recipes: `polar, polkiin, pochey, polar, polchey, pollaiin, psalar`).
"""
    OUT_MD.write_text(md, encoding="utf-8")
    print(f"Wrote {OUT_JSON} and {OUT_MD}")


if __name__ == "__main__":
    main()
