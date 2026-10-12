# Wave 51 Master Compendium (`Attacks 213–216` / `Discoveries 230–233`, `v17.0 Edition`)

This compendium synthesizes the four empirical, visual, paleographic, codicological, and statistical breakthroughs of **Wave 51 (`Attacks 213–216` / `Discoveries 230–233`)**, accompanied by **`11` new high-resolution contrast-enhanced folio scans** in `pages/*.png`, **`4` new Plain-English Visual Walkthroughs (`#59..#62`)**, **`5` new Flagship Visual Specimens (`SPEC-86..90`)**, and **`Interactive Explorer v17.0` (`19` Interactive Tabs, `78` Page Walkthroughs, `90` Visual Specimens)**.

---

## 1. Attack 213 (`Discovery 230`): The `18/18 = 100.0%` Palindromic Bifolio Scribe & Currier-Language Nesting Law of Quires 4–8 (`f25r–f66v`, $p = 8.37 	imes 10^{-9}$) & Trans-Gutter Conjugate Sheet Continuity ($z = +4.49$)
- **Script, Data & Scans**: [`tools/attack213_palindromic_bifolio_nesting_and_conjugate_sheets.py`](../tools/attack213_palindromic_bifolio_nesting_and_conjugate_sheets.py) $\to$ [`data/attack213_palindromic_bifolio_nesting_and_conjugate_sheets.json`](../data/attack213_palindromic_bifolio_nesting_and_conjugate_sheets.json), [`pages/f26r_first_currier_b_bifolio_herbal_enh.png`](../pages/f26r_first_currier_b_bifolio_herbal_enh.png), [`pages/f31r_conjugate_currier_b_bifolio_enh.png`](../pages/f31r_conjugate_currier_b_bifolio_enh.png), [`pages/f41r_scribe5_quire6_outer_recto_enh.png`](../pages/f41r_scribe5_quire6_outer_recto_enh.png), [`pages/f48r_scribe5_quire6_conjugate_recto_enh.png`](../pages/f48r_scribe5_quire6_conjugate_recto_enh.png)
- **Key Breakthroughs**:
  1. **Why Currier A & B Appear "Interleaved" in Quires 4–8 (`18/18 = 100.0%` Palindromic Bifolio Nesting)**:
     - Across all `5` mixed-language Herbal quires (`Quires 4–8` = `D, E, F, G, H`, `f25r–f66v`, `18` surviving bifolia = `36` leaves = `72` pages across Scribes `1, 2, 3, 5`), **every single quire is a `100.0%` palindrome of both Scribe Hand (`$H`) and Currier Language (`$L`) across the central sewing fold (`leaf i <-> leaf N+1-i`)**:
       - **Quire 4 (`D`, `f25–f32`)**: Hands `[1, 2, 1, 1, 1, 1, 2, 1]` / Lang `[A, B, A, A, A, A, B, A]` (`f26 <-> f31` is a single Scribe 2 / Currier B bifolio sheet nested at Position 2!).
       - **Quire 5 (`E`, `f33–f40`)**: Hands `[2, 2, 1, 1, 1, 1, 2, 2]` / Lang `[B, B, A, A, A, A, B, B]` (`f33 <-> f40` and `f34 <-> f39` are two Scribe 2 / Currier B outer bifolia!).
       - **Quire 6 (`F`, `f41–f48`)**: Hands `[5, 1, 2, 1, 1, 2, 1, 5]` / Lang `[B, A, B, A, A, B, A, B]` (`f41 <-> f48` is Scribe 5's outer bifolium; `f43 <-> f46` is Scribe 2's inner bifolium; `f42 <-> f47` and `f44 <-> f45` are Scribe 1's bifolia!).
       - **Quire 7 (`G`, `f49–f56`)**: Hands `[1, 2, 1, 1, 1, 1, 2, 1]` / Lang `[A, B, A, A, A, A, B, A]` (`f50 <-> f55` is Scribe 2's nested bifolium!).
       - **Quire 8 (`H`, `f57–f66`)**: Hands `[5, 3, ..., 3, 5]` (`f57 <-> f66` is Scribe 5's outer bifolium; `f58 <-> f65` is Scribe 3's inner bifolium!).
     - The exact combinatoric probability that `18/18` (`100.0%`) bifolia pair identical Scribe Hands is **$p = 1.67 \times 10^{-5}$ (`1 in 60,025`) within quires and $p = 8.37 \times 10^{-9}$ (`1 in 119.4 million`) globally across the `36` leaves**!
  2. **Trans-Gutter Conjugate Sheet Continuity ($z = +4.49, p < 0.0002$) & `f41r <-> f48r` Botanical Pairing**:
     - Even when separated by up to `14` pages of another scribe in the bound quire, **Conjugate Bifolio Leaves (`leaf i <-> leaf N+1-i`) achieve a mean Canonical Stem Jaccard of `0.2737` vs `0.2439` for non-conjugate leaves in the same quire and `0.2259` for cross-scribe leaves (`1.21×` lift; within-quire permutation $z = +4.49, p < 0.0002$)**.
     - On Scribe 2's first conjugate bifolium `f26 <-> f31`, **`74.32%` of tokens on `f26r/v` reuse stems from `f31r/v`**, and on Scribe 5's outer bifolium `f41 <-> f48`, **`68.71%` of tokens on `f41r/v` reuse stems from `f48r/v`** while `f41r` (`p82`) and `f48r` (`p96`) depict **conjugate hand/finger-lobed green cup-leaf plants** painted on the two halves of the same unfolded sheet!

---

## 2. Attack 214 (`Discovery 231`): Completing `20/20` (`100.0%`) High-Resolution Visual Coverage of Quire 13 Balneological (`f78v, f79v, f80v`) & Trans-Leaf Callout Propagation (`64.22%` Opposite-Side Echo)
- **Script, Data & Scans**: [`tools/attack214_balneo_20page_completion_f78v_f79v_f80v_and_transleaf_echo.py`](../tools/attack214_balneo_20page_completion_f78v_f79v_f80v_and_transleaf_echo.py) $\to$ [`data/attack214_balneo_20page_completion_f78v_f79v_f80v_and_transleaf_echo.json`](../data/attack214_balneo_20page_completion_f78v_f79v_f80v_and_transleaf_echo.json), [`pages/f78v_balneo_ten_nymph_tube_pool_enh.png`](../pages/f78v_balneo_ten_nymph_tube_pool_enh.png), [`pages/f79v_balneo_nymph_ring_canopy_verso_enh.png`](../pages/f79v_balneo_nymph_ring_canopy_verso_enh.png), [`pages/f80v_balneo_left_margin_nymph_ladder_enh.png`](../pages/f80v_balneo_left_margin_nymph_ladder_enh.png)
- **Key Breakthroughs**:
  1. **`20/20` (`100.0%`) Visual Forensics of Quire 13 (`f78v`, `f79v`, `f80v`)**:
     - **`f78v` (`p143`, `294` words)**: Depicts `8` nymphs in a horizontal green kidney-shaped bath pool over `5` blue arcade windows, fed by a left-margin pipe from a top plume bracket (`79.93%` stem coverage from `f78r`).
     - **`f79v` (`p145`, `356` words)**: Depicts a top nymph under a blue shower canopy holding a **cross (`+`) in her raised left hand**, pouring water down a multi-stage funnel column into a bottom green pool where a mermaid/web-footed nymph sits surrounded by **four small quadrupeds (`4` dog/lamb-like animals)** (`84.83%` stem coverage from `f79r`, and **`85.11%`** from facing `f80r`!).
     - **`f80v` (`p147`, `376` words)**: Depicts a crowned top-left nymph holding a **horizontal spindle/flask** above a **scaly armored armadillo/pangolin-like quadruped**, two funnel nymphs, and a `6`-nymph bottom blue pool (`82.98%` stem coverage from `f80r`).
  2. **Trans-Leaf Callout-to-Opposite-Prose Propagation (`64.22%` Opposite-Side vs `59.31%` Same-Side, `67.16%` Combined Leaf)**:
     - Across all `204` diagram/margin callout tokens in Quire 13 (`@L, +L, =L, ~L, *L, @Pb, +Pb, @P1`), **`64.22%` (`131/204`) echo their root stem in the prose on the opposite side of the same physical leaf** (`67.16%` across the combined leaf), and at the central sewing fold (`f79v <-> f80r`), **`70.00%` (`7/10`) of `f80r`'s Upper 8-Nymph Gallery labels echo directly in facing `f79v`'s prose**!

---

## 3. Attack 215 (`Discovery 232`): The `2×3` Physical Reverse Grid of the Quire 14 Rosettes Sheet (`p157` & `p158`), the `f86v3` `5/6` (`4/4 = 100%` Cardinal N/W/E/S) `t-` Gallows Acrostic Ring ($p = 0.00285$), & `81.82%` `fRos` Token Stem Coverage
- **Script, Data & Scans**: [`tools/attack215_rosettes_6panel_reverse_grid_f85r2_f86v3_f86v6.py`](../tools/attack215_rosettes_6panel_reverse_grid_f85r2_f86v3_f86v6.py) $\to$ [`data/attack215_rosettes_6panel_reverse_grid_f85r2_f86v3_f86v6.json`](../data/attack215_rosettes_6panel_reverse_grid_f85r2_f86v3_f86v6.json), [`pages/f85r1_f86v4_f86v3_rosettes_reverse_top_enh.png`](../pages/f85r1_f86v4_f86v3_rosettes_reverse_top_enh.png), [`pages/f86v4_f86v6_f86v5_rosettes_reverse_full_enh.png`](../pages/f86v4_f86v6_f86v5_rosettes_reverse_full_enh.png)
- **Key Breakthroughs**:
  1. **Exact `2×3` Reverse Grid of Quire 14 (`1,855` Words) & `81.82%` `fRos` Token Stem Coverage**:
     - Comparing unfolded scans `p157` and `p158` establishes the exact `2×3` panel layout on the reverse of the 9-Sphere Rosettes Map (`fRos` / `f85v2`, `539` words):
       - **Top Row (`p157`)**: `f85r2` (4-Cardinal Sun Wheel with N/E/S/W Busts, `166` words) | `f86v4` (Scalloped Moon Wheel, `169` words) | `f86v6` (`479`-word 4-Paragraph Treatise — covering **`70.50%`** of `fRos` word tokens' stems by itself!).
       - **Bottom Row (`p156/p158`)**: `f85r1` (`343`-word Frontispiece Treatise + `+Pr` Coda) | `f86v5` (`382`-word `'86'` Treatise) | `f86v3` (`281`-word 4-Corner Scaly Cones & 4-Cardinal Perimeter Treatise).
     - Together, the `6` reverse panels cover **`81.82%` (`441/539`) of all word tokens' stems on the `fRos` 9-Sphere Cosmos Map**.
  2. **The `f86v3` `4/4 = 100.0%` Cardinal (`5/6 = 83.33%` Total) `t-` Gallows Acrostic Ring ($p = 0.00285$) & `taiin.ytaiin.ytaiin.ytaiin` Epizeuxis**:
     - On `f86v3` (`p158` Right Panel), **`4/4` (`100.0%`) of the Cardinal Perimeter Treatises (`<!N> tchedy`, `<!W> tchol`, `<!E> tshedal`, `<!S> toeeedchy`, $p = 0.00285$) and `5/6` (`83.33%`, $+ \text{Center } \text{tshdchey}$, $p = 0.00319$) of all paragraphs open with a `t-` gallows (`3.61×` over the `23.11%` manuscript baseline)**, while Line 3 (`<f86v3.3,+Pb>`) writes **`taiin.ytaiin.ytaiin.ytaiin.or.ar.ytas.am`** (`4` consecutive `[y]taiin` tokens + `ytas`).

---

## 4. Attack 216 (`Discovery 233`): Quire 20 Opening Leaf (`f103r–f103v` = `985` Words, `31` Starred Recipes — `#1` Highest-Recipe-Count Leaf in the Codex, `86.12%` Leaf Coupling) & First Facing Spread (`f103v–f104r` = `902` Words, `26` Recipes, `87.60%` Quire 20 Stem Seeding)
- **Script, Data & Scans**: [`tools/attack216_quire20_opening_spread_f103v_f104r_and_wave51_compendium.py`](../tools/attack216_quire20_opening_spread_f103v_f104r_and_wave51_compendium.py) $\to$ [`data/attack216_quire20_opening_spread_f103v_f104r_and_wave51_compendium.json`](../data/attack216_quire20_opening_spread_f103v_f104r_and_wave51_compendium.json), [`pages/f103v_quire20_opening_verso_13stars_enh.png`](../pages/f103v_quire20_opening_verso_13stars_enh.png), [`pages/f104r_quire20_second_recto_13stars_enh.png`](../pages/f104r_quire20_second_recto_13stars_enh.png)
- **Key Breakthroughs**:
  1. **The `#1` Highest-Recipe-Count Vellum Leaf in the Voynich Manuscript (`f103r–f103v` = `985` Words, `31` Starred Recipes, `86.12%` Leaf Coupling)**:
     - Across the entire codex, leaf **`f103` (`f103r` `531` words + `f103v` `454` words = `985` words, `18 + 13 = 31` `<%>` starred recipes)** is the `#1` highest-recipe-count single vellum leaf in the manuscript.
     - **`86.12%` of tokens on `f103v` reuse canonical root stems from `f103r`**, and **`65.85%` of tokens on facing `f104r` (`448` words, `13` recipes, featuring `10` consecutive Red-Painted / Plain-Dotted margin star alternations from Star 4 to Star 13) reuse canonical stems from `f103v`**.
  2. **Lexical Seeding of Quire 20 (`81.54% -> 87.60%` Token Stem Coverage Across All `10,892` Words)**:
     - The canonical root stems introduced on the opening leaf `f103r–f103v` alone cover **`81.54%` of all `10,892` word tokens across the entire 23-page Quire 20 Starred Recipe section**, rising to **`87.60%`** when including the facing page `f104r` (`1,433` words across the first `3` pages = `44` recipes)!
