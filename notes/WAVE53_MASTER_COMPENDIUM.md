# Wave 53 Master Compendium (`Attacks 221–224` / `Discoveries 238–241` / Explorer `v19.0` — Milestone `100` Flagship Visual Specimens `SPEC-01..100`)

> **Executive Summary**: Wave 53 achieves four major codicological and visual-forensic milestones across the Voynich Manuscript (`Beinecke MS 408`):
> 1. **`100.0%` Visual Coverage of Late Herbal (`16/16` in `Quires 15 & 17`, `f87r–f96v`) & `100.0%` of the Entire Second Half of the Codex (`117/117` in `f57r–f116v`, `Quires 8–20`)**, extending the **Palindromic Bifolio Law to `20/20 = 100.0%` across all `6` mixed-language Herbal quires (`Quires 4, 5, 6, 7, 8, and 17`, $p = 9.29 \times 10^{-10}$, or `1 in 1.08 billion`)** and establishing the **Twin Inward Foldout Foliation Law (`f90v2` `'90'` & `f95v2` `'95'`)** ([`tools/attack221_late_herbal_100pct_and_second_half_codex_completion.py`](../tools/attack221_late_herbal_100pct_and_second_half_codex_completion.py)).
> 2. **`100.0%` (`16/16`) Visual Coverage of Opening Quire 1 (`$Q=A`, `f1r–f8v`)**, proving that the `386` canonical root stems introduced in Quire 1 alone seed **`87.48%` (`68.84%` raw words) of all `8,050` word tokens across the entire `95`-folio Currier A Herbal corpus** ([`tools/attack222_quire1_100pct_completion_and_opening_bifolia_f1_f8.py`](../tools/attack222_quire1_100pct_completion_and_opening_bifolia_f1_f8.py)).
> 3. **`100.0%` (`32/32`) Visual Coverage of Currier B Herbal, `100.0%` (`83/83`) of Currier Language B (`$L=B`), and `100.0%` of Scribes `2, 3, 4, and 5` (`$H=2..5`) Across the Entire Manuscript**, raising Global Codex Visual Coverage to **`171/227 = 75.33%`** and proving the **`f50r <-> f50v <-> f51r` Eye-Flower Vellum-Hole Pupil Registration Law** ([`tools/attack223_100pct_currier_b_and_scribes_2345_visual_completion.py`](../tools/attack223_100pct_currier_b_and_scribes_2345_visual_completion.py)).
> 4. **Milestone `100` Flagship Visual Specimens (`SPEC-01..100`) & Interactive Explorer `v19.0` (`21` Tabs, `86` Walkthroughs, `70` Plain-English Folio Guides)** ([`tools/attack224_wave53_master_compendium.py`](../tools/attack224_wave53_master_compendium.py)).

---

## 1. Attack 221 (`Discovery 238`): `100.0%` Late Herbal (`f87r–f96v`) & `100.0%` Second-Half Codex (`f57r–f116v`) Visual Completion, the `20/20 = 100.0%` Palindromic Bifolio Law ($p = 9.29 \times 10^{-10}$), and Twin Inward Foldout Foliation Law (`f90` & `f95`)
- **Script & Data**: [`tools/attack221_late_herbal_100pct_and_second_half_codex_completion.py`](../tools/attack221_late_herbal_100pct_and_second_half_codex_completion.py) | [`data/attack221_late_herbal_100pct_and_second_half_codex_completion.json`](../data/attack221_late_herbal_100pct_and_second_half_codex_completion.json)
- **Newly Rendered & Inspected Late Herbal Scans (`6` High-Res Plates)**:
  - [`pages/f87v_late_herbal_quire15_verso_enh.png`](../pages/f87v_late_herbal_quire15_verso_enh.png) (`p161` `f87v`, `1565x2000`): Dimorphic 2-plant Late Herbal verso (`Quire 15`, Scribe 1 / Currier A, `77` words, `10` lines, `3` prose paragraphs opening `pchor.odaiin...`, `tchol.daiin...`, `kydain...`) with a tall dark-green daisy-head plant on left and a yellow-flowered feverfew/yarrow corymb on right.
  - [`pages/f94v_single_page_verso_enh.png`](../pages/f94v_single_page_verso_enh.png) (`p170` `f94r`, `1453x2000`): Single-leaf Maidenhair Fern (*Adiantum*) with numeral `94` at top-right (`49` words, `7` lines).
  - [`pages/f94v_late_herbal_scribe3_verso_enh.png`](../pages/f94v_late_herbal_scribe3_verso_enh.png) (`p171`, `2000x995`): Unfolded 3-panel panoramic spread `f94v | f95r1 | f95r2` (`97 + 84 + 79 = 260` words by Scribe 3 / Currier B).
  - [`pages/f95v2_f95v1_unfolded_herbal_verso_enh.png`](../pages/f95v2_f95v1_unfolded_herbal_verso_enh.png) (`p172` `f95v2` folded shut over `f95r1`, `1457x2000`): Shows `f95v2` (`67` words, `11` lines) folded inward so `f95v2` forms the apparent front of leaf `95` with Arabic numeral **`95`** at top-right while `f95r1`'s blue flower heads peek out along the left gutter.
  - [`pages/f95v2_f95v1_true_unfolded_sheet_enh.png`](../pages/f95v2_f95v1_true_unfolded_sheet_enh.png) (`p173` `f95v1`, `1535x2000`): True inner verso panel `f95v1` (`159` words, `15` lines, opening `pchdlar.sheod...`) with `2` arching stems bearing `11 + 15 = 26` blue composite flower heads over a 5-clawed red rhizome.
  - [`pages/f96v_quire17_closing_verso_enh.png`](../pages/f96v_quire17_closing_verso_enh.png) (`p175` `f96v`, `1546x2000`): Closing page of Quire 17 (`76` words, `11` lines, Scribe 1 / Currier A, opening `kor.shol.shol.sheol.qokol...`) with a weeping arrow-leaf vine, `4 + 3 = 7` red-centered white berry racemes, and medieval Quire 17 signature **`17m`** at bottom-right.
- **`20/20 = 100.0%` Palindromic Bifolio Law Across All `6` Mixed-Language Herbal Quires**:
  - Including Quire 17 (`$Q=Q`, `f93–f96`: `[H1/A, H3/B, H3/B, H1/A]`, where Outer Bifolium #1 `f93 <-> f96` is `100%` Scribe 1 / Currier A and Inner Foldout Bifolium #2 `f94 <-> f95` is `100%` Scribe 3 / Currier B), all **`20/20 = 100.0%` of the conjugate bifolia across all `6` mixed-language Herbal quires (`Quires 4, 5, 6, 7, 8, and 17`) have identical Scribe Hand and identical Currier Language on both halves of every folded vellum sheet** (within-quire product $p = 5.56 \times 10^{-6}$, global 40-leaf pairing $p = 9.29 \times 10^{-10}$, or `1 in 1.08 billion`).
- **Scribe 3 Quire 17 $\to$ Quire 20 Lexical Seeding**:
  - Scribe 3's Inner Quire 17 Foldout Bifolium (`f94r/v + f95r1/r2/v1/v2`, `535` words) achieves **`94.39%` canonical stem coverage (`78.32%` raw word coverage) in Scribe 3's Quire 20 Starred Recipes (`96.91%` on `f94v`, `96.20%` on `f95r2`)**, seeding **`74.67%`** of all word tokens in Quire 20.

---

## 2. Attack 222 (`Discovery 239`): `100.0%` (`16/16`) Opening Quire 1 (`f1r–f8v`) Visual Completion & `87.48%` Currier A Herbal Lexical Seeding
- **Script & Data**: [`tools/attack222_quire1_100pct_completion_and_opening_bifolia_f1_f8.py`](../tools/attack222_quire1_100pct_completion_and_opening_bifolia_f1_f8.py) | [`data/attack222_quire1_100pct_completion_and_opening_bifolia_f1_f8.json`](../data/attack222_quire1_100pct_completion_and_opening_bifolia_f1_f8.json)
- **Newly Rendered & Inspected Quire 1 Scans (`7` High-Res Plates Completing `16/16` of Quire 1)**:
  - [`pages/f2v_quire1_waterlily_pad_verso_enh.png`](../pages/f2v_quire1_waterlily_pad_verso_enh.png) (`p7` `f2v`, `87` words): Round kidney-notched *Nymphaea* waterlily pad, white 3-lobed flower, ring-scarred creeping rhizome, and marginal `fo/fe` doodle above `<f2v.5> kooiin`.
  - [`pages/f3v_quire1_blue_bell_root_verso_enh.png`](../pages/f3v_quire1_blue_bell_root_verso_enh.png) (`p9` `f3v`, `90` words): Two dark-blue nodding bell pouches (*Campanula/Gentiana*), horned green leaves, and segmented scorpion-tail taproot.
  - [`pages/f4r_quire1_compound_bush_recto_enh.png`](../pages/f4r_quire1_compound_bush_recto_enh.png) (`p10` `f4r`, `90` words): Five-stemmed bush with alternating red and green V-paired leaflets.
  - [`pages/f5v_quire1_mallow_red_flower_verso_enh.png`](../pages/f5v_quire1_mallow_red_flower_verso_enh.png) (`p13` `f5v`, `61` words): Palmate-leaved mallow/geranium with `5` red-petalled flowers.
  - [`pages/f6v_quire1_thistle_leaf_verso_enh.png`](../pages/f6v_quire1_thistle_leaf_verso_enh.png) (`p15` `f6v`, `102` words): Spiky 6-pointed star-leaved thistle (*Eryngium*) with `6` green/blue spiny flower heads.
  - [`pages/f7r_quire1_paeonia_bulb_recto_enh.png`](../pages/f7r_quire1_paeonia_bulb_recto_enh.png) (`p16` `f7r`, `69` words): Seven-sepal green star calyx enclosing an 8-petalled white flower over an inverted-Y forked root.
  - [`pages/f7v_quire1_lobed_herb_verso_enh.png`](../pages/f7v_quire1_lobed_herb_verso_enh.png) (`p17` `f7v`, `68` words): Ciliated green/white/red oval leaves each marked by a central dark-blue eye-spot, and `<f7v.7,+P0> ...dol.dol.dor.aiin` exact reduplication.
- **Quire 1 Lexical Seeding**:
  - The `386` canonical root stems introduced in Opening Quire 1 (`f1r–f8v`, `1,537` words) cover **`87.48%` (`68.84%` raw words) of all `8,050` word tokens across the entire `95`-folio Currier A Herbal corpus** and **`84.22%` (`54.05%` raw words)** of the Pharmaceutical Recipe Compendium (`Quires 15 & 19`).

---

## 3. Attack 223 (`Discovery 240`): `100.0%` (`32/32`) Currier B Herbal & `100.0%` (`$L=B` / `$H=2..5`) Visual Completion, the `f50r <-> f50v <-> f51r` Eye-Flower Vellum-Hole Registration Proof, and 3-Scribe Herbal-B Stratification
- **Script & Data**: [`tools/attack223_100pct_currier_b_and_scribes_2345_visual_completion.py`](../tools/attack223_100pct_currier_b_and_scribes_2345_visual_completion.py) | [`data/attack223_100pct_currier_b_and_scribes_2345_visual_completion.json`](../data/attack223_100pct_currier_b_and_scribes_2345_visual_completion.json)
- **Visual Coverage Milestones Achieved**:
  - **Currier B Herbal (`$I=H, $L=B`)**: **`32/32 = 100.0%`**
  - **All Currier Language B (`$L=B`) Across the Entire Voynich Manuscript**: **`83/83 = 100.0%`**
  - **Scribe 2 (`$H=2`)**: **`46/46 = 100.0%`**
  - **Scribe 3 (`$H=3`)**: **`33/33 = 100.0%`**
  - **Scribe 4 (`$H=4`)**: **`27/27 = 100.0%`**
  - **Scribe 5 (`$H=5`)**: **`7/7 = 100.0%`**
  - **Scribe 1 (`$H=1`)**: **`57/113 = 50.44%`** (crossing `50%`, with only `56` Scribe 1 Herbal folios in `Quires 2–7` remaining unscanned in the entire codex)
  - **Global Voynich Codex Visual Coverage**: **`171/227 = 75.33%` (`> 3/4` of the entire manuscript)**
- **The `f50r <-> f50v <-> f51r` Eye-Flower Vellum-Hole Pupil Registration Proof**:
  - On [`pages/f50r_currier_b_herbal_recto_enh.png`](../pages/f50r_currier_b_herbal_recto_enh.png) (`p100` `f50r`) and zoom crop [`pages/f50r_flower_eye_inscription_crop_enh.png`](../pages/f50r_flower_eye_inscription_crop_enh.png), the artist painted a giant **eye-shaped blue-and-white composite flower centered directly over a natural vertical oval vellum hole (`x≈0.38, y≈0.38`)** so the parchment hole forms the **pupil of the flower-eye**, through which `<f51r.11> ...otar.aiin` and `<f51r.12> ...ytor.otaiin` on underlying [`pages/f51r_quire7_herbal_recto_enh.png`](../pages/f51r_quire7_herbal_recto_enh.png) (`p102`) peek out as apparent secret letters inside the pupil!
  - On the reverse side [`pages/f50v_currier_b_herbal_verso_enh.png`](../pages/f50v_currier_b_herbal_verso_enh.png) (`p101` `f50v`) and zoom crop [`pages/f50v_flower_stalk_hole_crop_enh.png`](../pages/f50v_flower_stalk_hole_crop_enh.png), the exact same oval hole at the mirror coordinate (`x≈0.62, y≈0.38`, `0.38 + 0.62 = 1.00`) is framed by the **3 diverging green flower stalks of `f50v`'s blue flower head**, exposing the dark-green leaf of underlying `f49v` (`p99`) as an apparent central green seed-pod/ovule!
- **Additional Newly Rendered Currier B Herbal Highlights**:
  - [`pages/f33v_currier_b_herbal_verso_enh.png`](../pages/f33v_currier_b_herbal_verso_enh.png) (`p67` `f33v`): **Three circular solar/gear-wheel root discs** with radial spokes and perimeter pegs, `6` star-lobed peltate green leaves, and `2` giant oval blue-heart/yellow-scale flower heads.
  - [`pages/f40v_currier_b_herbal_verso_enh.png`](../pages/f40v_currier_b_herbal_verso_enh.png) (`p81` `f40v`): Two-plant page with `3 + 7 = 10` turnip/radish root bulbs, red-striped funnel calyx, blue-and-green polka-dot corona flower, and **Quire 5 signature `5m`** at bottom-right.
  - [`pages/f55v_currier_b_herbal_verso_enh.png`](../pages/f55v_currier_b_herbal_verso_enh.png) (`p111` `f55v`): Pointed dark-green strap-leaf sheaf with brown flower spike on left and a **zoomorphic bird/squid/elephant-headed root creature** at bottom-right.
  -Plus [`pages/f26v_currier_b_herbal_verso_enh.png`](../pages/f26v_currier_b_herbal_verso_enh.png) (`p53`), [`pages/f31v_currier_b_herbal_verso_enh.png`](../pages/f31v_currier_b_herbal_verso_enh.png) (`p63`), [`pages/f34v_currier_b_herbal_verso_enh.png`](../pages/f34v_currier_b_herbal_verso_enh.png) (`p69`), [`pages/f40r_currier_b_herbal_recto_enh.png`](../pages/f40r_currier_b_herbal_recto_enh.png) (`p80`), [`pages/f43r_currier_b_herbal_recto_enh.png`](../pages/f43r_currier_b_herbal_recto_enh.png) (`p86`), and [`pages/f55r_currier_b_herbal_recto_enh.png`](../pages/f55r_currier_b_herbal_recto_enh.png) (`p110`).
- **3-Scribe Herbal-B Stratification (`$H=2, 3, 5`) & Downstream Seeding**:
  - Across the `32` Currier B Herbal folios (`3,476` words), **Scribe 2** (`20` folios, `2,360` words: `qok/qot = 7.42%`, `-edy = 13.39%`, `-ody = 3.81%`, ratio `3.51`), **Scribe 3** (`6` folios, `535` words: `qok/qot = 11.21%`, `-edy = 8.97%`, `-ody = 3.55%`, ratio `2.53`), and **Scribe 5** (`6` folios, `581` words: `qok/qot = 8.26%`, `-edy = 17.56%`, `-ody = 7.57%`, ratio `2.32`) exhibit distinct morphological dialects while seeding **`92.11%` of Balneological (`$I=B`) stems (`77.21%` raw words)**, **`89.81%` of Cosmological (`$I=C`) stems**, and **`88.30%` of Quire 20 Starred Recipe (`$I=S`) stems (`66.03%` raw words)**.

---

## 4. Summary Table of Wave 53 Deliverables (`v19.0`)

| Metric | Wave 52 (`v18.0`) | Wave 53 (`v19.0`) | Delta |
| :--- | :---: | :---: | :---: |
| **Quantitative Decoding Attacks** | `220` | **`224`** | `+4` (`Attacks 221–224`) |
| **Empirical Discoveries Logged** | `237` | **`241`** | `+4` (`Discoveries 238–241`) |
| **Flagship Visual Specimens (`SPEC`)** | `95` | **`100` (Milestone!)** | `+5` (`SPEC-96..100`) |
| **Plain-English Guide Walkthroughs** | `66` | **`70`** | `+4` (`Walkthroughs #67..#70`) |
| **Interactive Explorer Tabs / Cards** | `20` tabs / `82` cards | **`21` tabs / `86` cards** | `+1` tab (`Tab 21`) / `+4` cards |
| **Global Codex Visual Scan Coverage** | `146 / 227` (`64.32%`) | **`171 / 227` (`75.33%`)** | `+25` folios (`27` new PNG plates) |
