#!/usr/bin/env python3
"""
Attack 196 (Discovery 213): Wave 46 Master Compendium — Zodiac @Cc-@Lz Register
Split & Unfolded p132-p133 Forensics (Leo 'agost', Virgo 'setembre', Libra
'octobre', Crowned 12:00 Nymphs, f72v1 Vellum Hole Avoidance & Quire '11m'),
Balneological f80r & f82r Galleries & the 3.57x '-g' Label Suffix Law, and the
Quire 20 Megaparagraph Step-Star Variance Collapse (2.36x SD Reduction to 32.12
Words/Star Unit) & f94r Maidenhair Fern Bridge (92.21% Recipe Stem Echo).
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
A193_JSON = ROOT / "data" / "attack193_zodiac_ring_to_nymph_coupling_and_crowned_loci.json"
A194_JSON = ROOT / "data" / "attack194_balneo_f80r_f82r_and_rare_velar_suffixes.json"
A195_JSON = ROOT / "data" / "attack195_f108v_megaparagraph_compiler_and_f94r_fern.json"
OUT_JSON = ROOT / "data" / "attack196_wave46_master_compendium.json"
OUT_MD = ROOT / "notes" / "ZODIAC_RING_COUPLING_BALNEO_GALLERIES_AND_F108V_MEGAPARAGRAPH.md"


def main():
    a193 = json.loads(A193_JSON.read_text(encoding="utf-8"))
    a194 = json.loads(A194_JSON.read_text(encoding="utf-8"))
    a195 = json.loads(A195_JSON.read_text(encoding="utf-8"))

    compendium = {
        "wave": 46,
        "attacks": [193, 194, 195, 196],
        "discoveries": [210, 211, 212, 213],
        "edition": "v12.0",
        "attack193_summary": a193["summary"],
        "attack193_cc_vs_lz": a193["cc_vs_lz_morphology"],
        "attack194_summary": a194["summary"],
        "attack195_summary": a195["summary"],
        "attack195_pre_star_cadence": a195["pre_star_line_end_profiles"],
        "attack195_megaparagraph_table": a195["quire20_step_star_megaparagraphs"][:8],
    }

    OUT_JSON.write_text(json.dumps(compendium, indent=2), encoding="utf-8")

    cc_m = a193["cc_vs_lz_morphology"]["cc_rings"]
    lz_m = a193["cc_vs_lz_morphology"]["lz_labels"]

    folio_rows_md = "\n".join(
        f"| `{r['folio']}` | **{r['sign']}** (`{r['month']}`) | `{r['pdf_page']}` | `{r['n_cc_words']}` | `{r['n_lz_loci']}` (`{r['n_lz_words']}` w) | `{r['lz_in_same_cc_exact_count']}` (`{r['lz_in_same_cc_exact_rate']*100:.1f}%`) | `{r['lz_in_same_cc_stem_count']}` (`{r['lz_in_same_cc_stem_rate']*100:.1f}%`) | `{', '.join(r['shared_exact_words'][:6])}` |"
        for r in a193["folio_breakdown"]
    )

    f80r_rows_md = "\n".join(
        f"| `{r['locus']}` (`{r['ltype']}`) | **`{r['label']}`** | `{r['stem']}` | {r['position']} | `{'Yes' if r['in_same_folio_prose_stem'] else 'No'}` | `{'Yes' if r['in_balneo_prose_stem'] else 'No'}` |"
        for r in a194["f80r_profile"]["labels"]
    )

    f82r_rows_md = "\n".join(
        f"| `{r['locus']}` (`{r['ltype']}`) | **`{r['label']}`** | `{r['stem']}` | {r['position']} | `{'Yes' if r['in_same_folio_prose_stem'] else 'No'}` | `{'Yes' if r['in_balneo_prose_stem'] else 'No'}` |"
        for r in a194["f82r_profile"]["labels"]
    )

    mega_rows_md = "\n".join(
        f"| `{r['folio']}` | `{r['start_locus']}–{r['end_locus']}` | `{r['n_lines']}` | **`{r['n_words']}`** | **`{r['n_step_stars']}`** | **`{r['total_subclauses']}`** | **`{r['mean_words_per_subclause']}`** | `{r['first_word']} ... {r['last_word']}` |"
        for r in a195["quire20_step_star_megaparagraphs"][:8]
    )

    f108v_sc_md = "\n".join(
        f"| **Sub-Clause #{r['subclause_num']}** | {r['tier']} | `{r['start_locus']}–{r['end_locus']}` | `{r['n_lines']}` (`{r['n_words']}` w) | **`{r['first_word']}`** | **`{r['last_word']}`** | `qo-`: `{r['qo_count']}` / `-edy`: `{r['edy_count']}` | `{r['n_shared_stems_with_prev']}` stems (`{', '.join(r['shared_stems_with_prev'][:5])}`) |"
        for r in a195["f108v_megaparagraph_10_subclauses"]
    )

    md = f"""# Zodiac Concentric Ring vs. Degree-Label Register Split (`f72v3–f72v1`), Balneological `f80r / f82r` Galleries & `3.57×` `-g` Label Suffixes, and the Quire 20 Megaparagraph Step-Star Variance Collapse (`2.36×` SD Reduction to `32.12` Words/Star Unit)

**Wave 46 Master Compendium (`Attacks 193–196` / `Discoveries 210–213` — Synchronized v12.0 Edition)**

---

## 1. Executive Summary of Wave 46 Breakthroughs

1. **Discovery 210 (`Attack 193`): The Zodiac Concentric Ring (`@Cc`) vs. Degree Label (`@Lz`) Functional Register Split (`3.14×` `ch-/sh-` Participle Surge in `@Cc` Rings vs. `68.00%` `o-` Nominal Citation in `@Lz` Labels) & Unfolded `p132–p133` Forensics (`f72v3` Leo `agost`, `f72v2` Virgo `setembre`, `f72v1` Libra `octobre`, Crowned 12:00 Leader-Nymphs, `f72v1` Vellum Hole Avoidance & Quire 11 Signature `11m`)**
   - Across all `12` Zodiac folios (`f70v2–f73v`, `964` `@Cc` ring words + `350` `@Lz` degree-label words), **`75.14%` (`263 / 350`) of all `@Lz` degree tokens share their canonical root stem with the `@Cc` concentric rings** (`35.71%` [`125 / 350`] exact words, `53.43%` [`187 / 350`] on the **exact same medallion**).
   - Holding that shared 12-month Scribe 4 astronomical vocabulary constant, `@Cc` concentric rings and `@Lz` degree labels exhibit a sharp **functional register split**:
     - **`@Lz` Degree Labels (`350` words) are Nominal Degree Citations**: **`68.00%` open with `o-` (`52.86%` `ok-/ot-/op-/of-`)** vs. `40.56%` `o-` (`34.75%` `ok-/ot-`) in `@Cc` rings (**`1.68×` lift, $z = +8.81, p < 10^{-17}$**), and `-y/-dy/-ey` nominal/adjectival endings reach **`46.00%`** vs. `38.49%` in `@Cc` rings.
     - **`@Cc` Concentric Rings (`964` words) are Continuous Seasonal/Astrological Clauses**: **`ch-/sh-` verbal/participle prefixes surge `3.14×` (`26.04%` in `@Cc` rings vs. `8.29%` in `@Lz` labels, $z = +7.00, p < 10^{-11}$)**, while `-aiin` quantitative endings rise **`1.53×` (`10.48%` vs. `6.86%`)**!
   - **Visual Forensics of `p132` ([`pages/f72v3_leo_agost_zodiac_enh.png`](../pages/f72v3_leo_agost_zodiac_enh.png)) & `p133` ([`pages/f72v1_libra_octobre_p133_enh.png`](../pages/f72v1_libra_octobre_p133_enh.png))**:
     - On **`f72v3` (Leo `agost`, left panel of `p132`)** and **`f72v1` (Libra `octobre`, `p133`)**, the **12:00 top-center nymph of the outer ring wears a 3-pointed crown** (`<f72v3.13,@Lz> or.aiin / <f72v3.14,@Lz> otedy` and `<f72v1.12,@Lz> okchey / <f72v1.13,@Lz> otedy`), visually marking the **0° / 30° cardinal cusp** of the sign!
     - On **`f72v2` (Virgo `setembre`, right panel of `p132`)**, a maiden in a pleated blue-and-white gown holds a star on a stem while all 30 nymphs hold their stars on **vertical floral/staff stems**.
     - On **`f72v1` (Libra `octobre`, `p133`)**, a large circular **pre-existing vellum hole** (`~100 px`) sits at 03:00 on the inner ring; the circular frame, the `@Cc` ring inscription, and the neighboring nymphs curve cleanly around the hole without losing a single character, while the bottom-right corner preserves the medieval bookbinder's **Quire 11 signature `11m`**!

2. **Discovery 211 (`Attack 194`): Balneological `f80r` (11-Nymph Gallery, `100%` Balneo Stem Echo) & `f82r` (Dual-Arc Central Fountain, `oroldair` Horizontal Jet & `darol / darary` Shower Plumes), and the `3.57×` `-g / -adag` Diagram-Label Suffix Law ($z = +5.42$)**
   - Across the entire Voynich Manuscript (`38,409` tokens), **`150` tokens contain `EVA g`**, of which **`91.33%` (`137 / 150`) end in word-final `-g` (`75.33%` [`113 / 150`] at line-final or label-final position)**, and **`EVA g` is enriched `3.57×` in Diagram Labels (`1.30%` [`18 / 1,388`] vs. `0.36%` [`132 / 36,360`] in body prose, $z = +5.42, p = 6.0 \times 10^{-8}$)**—including the compound jar-rim suffix **`-adag`** (`<f99r.1,@Lc> okaradag` and `<f102r2.13,@Lc> loeekadag`).
   - On **`f80r`** ([`pages/f80r_balneo_eleven_nymph_gallery_enh.png`](../pages/f80r_balneo_eleven_nymph_gallery_enh.png)), **`70.0%` (`7 / 10`) of the upper-gallery nymph & right-pipe labels echo their canonical stem inside `f80r`'s own prose** and **`100.0%` (`10 / 10`) echo across Balneological prose**, with Nymphs #3–#5 forming the liquid-stem gradation **`okaly -> okolo -> okary`** and Nymph #5 (`okary` in the blue pedestal basin) echoing the right-margin water conduit (`okar`).
   - On **`f82r`** ([`pages/f82r_balneo_rainbow_shower_pool_enh.png`](../pages/f82r_balneo_rainbow_shower_pool_enh.png)), a central red-and-blue fountain splits into two overhead arcs above a middle-left bather (`<f82r.10,@Lt> oroldair`) firing a horizontal multi-stream jet toward a reclining bather under a blue-and-gold star, while at the bottom **two vertical shower/geyser plumes both carry `dar-` source labels (`<f82r.35,@Lt> darol` and `<f82r.38,@Lt> darary`)** flanking the adjacent minimal pair **`<f82r.36,@Ln> okal -> <f82r.37,@Ln> okaldy`**!

3. **Discovery 212 (`Attack 195`): The Quire 20 Megaparagraph Step-Star Variance Collapse (`2.36×` Standard Deviation Reduction to `32.12` Words/Star Unit), the `3.97×` Pre-Step-Star Right-Margin `-m` Stop Law, and the `f94r` Maidenhair Fern (`Asplenium / Adiantum`) `92.21%` Recipe Stem Bridge**
   - Across all `285` `<%>` paragraphs in Quire 20 (`f103r–f116r`), raw paragraph length exhibits **mean `38.21` words and standard deviation $\\sigma = 33.14$ words ($CV = 0.867$)** due to massive `119–365` word megaparagraphs (`f111r.6–35` = `365` words, `f111v.1–25` = `294` words, `f108v.30–53` = `261` words).
   - **Splitting the megaparagraphs at their `54` Intra-Paragraph `+P0` Step Stars (`285 + 54 = 339` Star-Marked Units) collapses the standard deviation across Quire 20 by `2.36×` from $\\sigma = 33.14$ down to $\\sigma = 14.02$ words ($CV = 0.867 \\to 0.436$), and every megaparagraph converges onto the ~`32`-word canonical recipe length (`33.2` words on `f111r`, `29.4` words on `f111v`, `32.6` words on `f108v.30–53`, matching the `32.12`-word global mean across all `339` star units!)**!
   - Why did modern IVTFF transcribers merge those `54` step-star units into megaparagraphs? Because **on the line immediately preceding an Intra-Paragraph Step Star (`Line L-1`), the scribe wrote all the way to the right margin (`33.33%` [`18 / 54`] right-margin `-m` stop vs. only `8.40%` at `<$>` half-line paragraph ends — a `3.97×` surge!)**, leaving no blank half-line gap on the vellum!
   - On **`f94r`** ([`pages/f94r_late_herbal_monograph_enh.png`](../pages/f94r_late_herbal_monograph_enh.png)), a Late Herbal monograph depicting **Maidenhair Fern / Spleenwort (*Adiantum capillus-veneris* / *Asplenium trichomanes*)** with 4 opposite-leaflet pinnate fronds and 6 blue sporangia/berries (`66` words, opening `koaiin.cheo.pchor.qooldy`), **`87.01%` of token stems appear in Pharmaceutical (`48.05%` exact words)** and **`92.21%` of token stems (`77.92%` exact words!) appear in Quire 20 Starred Recipes**!

---

## 2. Zodiac `@Cc` Concentric Ring vs. `@Lz` Degree-Label Register Split (`Attack 193`)

| Feature | `@Cc` Concentric Rings (`18` Rings) | `@Lz` Degree Labels (`299` Loci) | Ratio / Lift | Interpretation |
| :--- | :---: | :---: | :---: | :--- |
| **Total Word Tokens** | `964` | `350` | `2.75×` | Continuous ring text vs. degree callouts |
| **Mean Word Length** | `5.162` chars | `5.583` chars | `0.92×` | `@Cc` rings include short particles (`ar, al, or, ol`) |
| **`o-` Nominal Initial Rate** | `40.56%` | **`68.00%`** | **`1.68×` in `@Lz` ($z = +8.81$)** | `@Lz` degree labels are **Nominal Citations** |
| **`ok-/ot-/op-/of-` Prefix Rate** | `34.75%` | **`52.86%`** | **`1.52×` in `@Lz`** | Celestial degree-nymph nouns |
| **`ch-/sh-` Verbal/Participle Rate** | **`26.04%`** | `8.29%` | **`3.14×` in `@Cc` ($z = +7.00$)** | `@Cc` rings state **Continuous Seasonal Processes** |
| **`-aiin` Quantitative Suffix Rate** | **`10.48%`** | `6.86%` | **`1.53×` in `@Cc`** | Degree/day counts inside concentric rings |
| **`-y/-dy/-ey` Suffix Rate** | `38.49%` | **`46.00%`** | **`1.20×` in `@Lz`** | Adjectival/nominal degree epithets |

### Complete 12-Folio Zodiac `@Cc <-> @Lz` Concordance Table

| Folio | Zodiac Sign (`Month Gloss`) | PDF Page | `@Cc` Words | `@Lz` Loci (`Words`) | Same-Medallion Exact Overlap | Same-Medallion Stem Overlap | Top Shared Exact Words (`@Cc ∩ @Lz`) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :--- |
{folio_rows_md}

---

## 3. Balneological `f80r` (11-Nymph Gallery) & `f82r` (Dual-Arc Fountain & Green Pool) Callout Concordance (`Attack 194`)

### A. Folio `f80r` (`10` Callout Labels: `70.0%` Same-Folio Stem Echo, `100.0%` Balneo Prose Stem Echo)

| Locus (`Type`) | Voynich Label | Canonical Stem | Physical Position on `f80r` (`p146`) | In `f80r` Prose? | In Balneo Prose? |
| :--- | :--- | :---: | :--- | :---: | :---: |
{f80r_rows_md}

### B. Folio `f82r` (`13` Callout Labels: `46.15%` Same-Folio Stem Echo, `61.54%` Balneo Prose Stem Echo)

| Locus (`Type`) | Voynich Label | Canonical Stem | Physical Position on `f82r` (`p150`) | In `f82r` Prose? | In Balneo Prose? |
| :--- | :--- | :---: | :--- | :---: | :---: |
{f82r_rows_md}

---

## 4. Quire 20 Megaparagraph Step-Star Variance Collapse (`2.36×` SD Reduction to `32.12` Words/Star Unit, `Attack 195`)

### A. How Splitting at the `54` Intra-Paragraph Step Stars Normalizes All Quire 20 Megaparagraphs to `~32` Words

| Folio | Locus Range | Lines | Total Words | Intra-Para Step Stars | Total Star Sub-Clauses | Mean Words / Sub-Clause | Opening ... Closing Word |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :--- |
{mega_rows_md}

### B. Complete 8-Sub-Clause Compiler of the `f108v.30–53` (`261`-Word) Megaparagraph

| Sub-Clause | Star Tier | Line Range | Lines (`Words`) | Opening Word | Closing Word | `qo-` / `-edy` Counts | Shared Stems With Preceding Sub-Clause |
| :--- | :--- | :---: | :---: | :--- | :--- | :---: | :--- |
{f108v_sc_md}
"""

    OUT_MD.write_text(md, encoding="utf-8")
    print(f"Wrote {OUT_JSON} and {OUT_MD} ({len(md):,} bytes)")


if __name__ == "__main__":
    main()
