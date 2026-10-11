# Voynich Manuscript Research Log & Structural Findings

This directory contains our ongoing computational, paleographic, and visual forensic investigation of the **Voynich Manuscript (Beinecke MS 408)** using the two local PDF scans (`2002046.pdf` and `voynich-manuscript.pdf`) cross-referenced with machine-readable EVA transliterations (`data/ZL3b-n.txt`, `data/RF1b-er.txt`, `data/IT2a-n.txt`, `data/GC2a-n.txt`).

---

## 1. Directory & Tooling Overview

### Source PDFs
| File | Pages | Export Date | Typical Resolution | Notes |
| :--- | :---: | :---: | :---: | :--- |
| [`2002046.pdf`](file:///c:/Users/denni/Documents/voynich/2002046.pdf) | 214 | 2026-08-17 | ~1500 × 2000 px | Official Yale Digital Collections export. Higher spatial resolution (~1.8× more pixels), embedded Beinecke Image IDs and folio labels per page, plus 4 physical book-edge scans at the end (`p210` `[Head]`, `p211` `[Tail]`, `p212` `[Fore-edge]`, `p213` `[Spine]`). |
| [`voynich-manuscript.pdf`](file:///c:/Users/denni/Documents/voynich/voynich-manuscript.pdf) | 210 | 2014-02-22 | ~1082 × 1500 px | Older TCPDF export with a 210-entry PDF bookmark outline (TOC). Pages `1..209` align 1-to-1 with `2002046.pdf` (`p210` is `[Back cover]`, which is `p214` in `2002046.pdf`). Has brighter highlight clipping, useful for cross-checking midtone contrast. |

### Custom Scripts (`tools/`)
- [`tools/build_index.py`](file:///c:/Users/denni/Documents/voynich/tools/build_index.py): Parses both PDFs and `data/ZL3b-n.txt` to generate [`data/folio_index.json`](file:///c:/Users/denni/Documents/voynich/data/folio_index.json), mapping all 226 transcribed folios (`38,409` words, `892` figure labels, `754` drawing intrusions) to their exact PDF page numbers, Beinecke Image IDs, sections, Currier languages (`A`/`B`), and Lisa Fagin Davis scribe hands (`1..5`).
- [`tools/render_folio.py`](file:///c:/Users/denni/Documents/voynich/tools/render_folio.py): Extracts high-resolution folio images from either PDF, supports normalized bounding-box cropping (`--crop x0 y0 x1 y1`), faded-ink channel contrast enhancement (`--enhance`), and side-by-side cross-PDF comparisons (`--compare`). *(Note: fixes a TCPDF quirk in `voynich-manuscript.pdf` where all 209 images are listed in every page's global resource dictionary by resolving `page.get_image_info(xrefs=True)`).*
- [`tools/analyze_structure.py`](file:///c:/Users/denni/Documents/voynich/tools/analyze_structure.py): Computes positional morphology across line/paragraph/drawing boundaries, Herbal-to-Pharmaceutical visual cross-references, and Currier language / scribe hand statistics ([`data/structural_analysis.json`](file:///c:/Users/denni/Documents/voynich/data/structural_analysis.json)).
- [`tools/test_q_prefix_and_labels.py`](file:///c:/Users/denni/Documents/voynich/tools/test_q_prefix_and_labels.py): Tests the `q-` proclitic hypothesis (`qoX = q + oX`) and same-folio label-to-paragraph matching against shuffled null baselines ([`data/q_and_label_analysis.json`](file:///c:/Users/denni/Documents/voynich/data/q_and_label_analysis.json)).
- [`tools/deep_grammar_and_cipher_test.py`](file:///c:/Users/denni/Documents/voynich/tools/deep_grammar_and_cipher_test.py): Tests top-line gallows allography (`p/f` vs `t/k`), 5-slot word automaton coverage, adjacent-word lockstep, and block-level label matches ([`data/deep_grammar_analysis.json`](file:///c:/Users/denni/Documents/voynich/data/deep_grammar_analysis.json)).
- [`tools/test_unified_normalization.py`](file:///c:/Users/denni/Documents/voynich/tools/test_unified_normalization.py): Applies our 4-Rule Canonical Normalization across the corpus and runs a 1,000-trial permutation test on same-folio figure-label to paragraph matching ([`data/canonical_normalization_test.json`](file:///c:/Users/denni/Documents/voynich/data/canonical_normalization_test.json)).
- [`tools/analyze_recipes_and_stars.py`](file:///c:/Users/denni/Documents/voynich/tools/analyze_recipes_and_stars.py): Analyzes Starred Recipes (`f103r–f116r`) margin star classifications, cross-section rare label concordances (`241` rare label roots), and right-justified `=Pt` titles ([`data/recipes_and_stars_analysis.json`](file:///c:/Users/denni/Documents/voynich/data/recipes_and_stars_analysis.json)).
- [`tools/test_cross_section_links.py`](file:///c:/Users/denni/Documents/voynich/tools/test_cross_section_links.py): Tests horizontal ($x$-coordinate) alignment of label references, binary alternation pairing in Starred Recipes, and section-specific rare label enrichment ([`data/cross_section_and_alignment.json`](file:///c:/Users/denni/Documents/voynich/data/cross_section_and_alignment.json)).
- [`tools/analyze_zodiac_and_hands.py`](file:///c:/Users/denni/Documents/voynich/tools/analyze_zodiac_and_hands.py): Tests invariance of our 4 morphological rules across all 5 paleographic Scribe Hands (`$H=1..5`) and analyzes Zodiac (`f70v2–f73v`) nymph ring sequences ([`data/zodiac_and_hands_analysis.json`](file:///c:/Users/denni/Documents/voynich/data/zodiac_and_hands_analysis.json)).
- [`tools/inspect_zodiac_details.py`](file:///c:/Users/denni/Documents/voynich/tools/inspect_zodiac_details.py): Tests the `ot-/op-` vs. `ok-/of-` prefix split between barreled and unbarreled Zodiac nymphs and across label categories (`@Lc`, `@Lf`, `@Lt`, `@Ln`, `@Lz`) ([`data/zodiac_prefix_split.json`](file:///c:/Users/denni/Documents/voynich/data/zodiac_prefix_split.json)).

---

## 2. Visual & Codicological Forensics on the Scans

### A. Folio `1r` Marginalia & Alphabetic Key ([`pages/f1r_top_cmp_enh.png`](file:///c:/Users/denni/Documents/voynich/pages/f1r_top_cmp_enh.png))
- Enhancing the RGB channels side-by-side between `2002046.pdf` and `voynich-manuscript.pdf` reveals the faded vertical column of Latin letters (`a, b, c, d, e, f, g, h, i, k...`) in the right margin alongside the red-brown symbol (`29` underlined) at the end of line 1 and thick paragraph-initial symbols at paragraphs 2 and 3.
- Also clearly visible are the right-justified single words (`=Pt`) at the bottom-right of each paragraph (`ydaraishy`, `dain.os.teody`, `otol.daiiin`, `dchaiin`), formatted like medieval author attributions or paragraph catchwords/summaries.

### B. Folio `116v` Multilingual Charm & Illustration ([`pages/f116v_text_cmp_enh.png`](file:///c:/Users/denni/Documents/voynich/pages/f116v_text_cmp_enh.png))
- On the final page (`f116v`, `p207`), channel enhancement brings out the 4 lines at the top next to a biological-style nymph and quadruped:
  - Top margin: `pox leber ...`
  - Line 1: `+ anchiton oladabas + multos + te + tce + cerc + portas + m...`
  - Line 2: `six + maria + morix + vix + abra + matra +` (standard medieval Latin/magical charm structure with crosses `+` separating words of power)
  - Line 3: `[Voynich glyphs: olad ceccy] valsch ubren so nim gas mich o` (Middle High German / early New High German words embedded directly between Voynich script tokens).

### C. Folio `66r` Corner Scene & Margin Key ([`pages/f66r_margin_labels.png`](file:///c:/Users/denni/Documents/voynich/pages/f66r_margin_labels.png))
- In the bottom-left corner of `f66r` (`p120`), a reclining nude figure is drawn beside two round objects and a small tub. Written in Latin/Germanic script above the round objects is `den mus` and above the tub is `del`, while a 4-word Voynich line stands over the reclining figure.
- Along the left margin above it is a vertical column of 9 single Voynich symbols (`o, r, s, y, sh, o, x, f, d`) paired with 4 marginal words (`sain`, `qokal`, `qorda`, `saral`).

### D. Physical Fold-Out Forensics on `f101v–f102v`: Solving an "Untranscribed Label" Mystery
- Comparing the full-page botanical drawing on [`pages/f1v_full.png`](file:///c:/Users/denni/Documents/voynich/pages/f1v_full.png) (`Atropa belladonna` / `Solanum`, with its distinctive two-tiered hatched cushion root and rootlet spikes in [`pages/f1v_root_crop.png`](file:///c:/Users/denni/Documents/voynich/pages/f1v_root_crop.png)) against the Pharmaceutical foldout [`pages/f101v_102r_foldout.png`](file:///c:/Users/denni/Documents/voynich/pages/f101v_102r_foldout.png) (`p181`) confirms that miniature plant `f102r1[3,2]` ([`pages/f102r1_plant32_crop.png`](file:///c:/Users/denni/Documents/voynich/pages/f102r1_plant32_crop.png)) is unmistakably the same plant species drawn in miniature (and `f102r1[3,1]` next to it is the miniature of `f37v`).
- **Forensic catch**: In [`pages/f102r1_bottom_right_zoom.png`](file:///c:/Users/denni/Documents/voynich/pages/f102r1_bottom_right_zoom.png), a two-word Voynich inscription is visible directly beneath the green scaly root of `f102r1[3,2]`, yet no transcription (`ZL`, `RF`, `IT`, `GC`) records a label for `f102r1[3,2]`.
- By inspecting the verso scans [`pages/p182_102v.png`](file:///c:/Users/denni/Documents/voynich/pages/p182_102v.png) (`f102v2`) and [`pages/p183_102v_part.png`](file:///c:/Users/denni/Documents/voynich/pages/p183_102v_part.png) (`f102v1`), we proved why: the bottom margin of `f102r1` was torn and **folded upward onto the back (`f102v1`)** (where the red root tips of `f102r1[3,1]` can be seen sticking onto the folded flap at the bottom of `p183_102v_part.png`). That cutaway exposes the folded panel behind `f102r1` (`f102v2`), and the two words peeking out directly under the root of `f102r1[3,2]` are `cheekey.orain` — the end of line `<f102v2.39>`!

### E. Starred Recipes Margin Forensics (`f103r–f116r`): Strict `1-to-1` Zebra Alternation ([`pages/f106r_stars_margin.png`](file:///c:/Users/denni/Documents/voynich/pages/f106r_stars_margin.png) & [`pages/f103r_stars_margin.png`](file:///c:/Users/denni/Documents/voynich/pages/f103r_stars_margin.png))
- Extracting and enhancing the left margin of `f106r` ([`pages/f106r_stars_margin.png`](file:///c:/Users/denni/Documents/voynich/pages/f106r_stars_margin.png)) visually confirms a striking codicological rule discovered in [`data/recipes_and_stars_analysis.json`](file:///c:/Users/denni/Documents/voynich/data/recipes_and_stars_analysis.json): on **12 out of the 26 Starred Recipe pages** (`f103v`, `f104v`, `f105v`, `f106r`, `f106v`, `f107v`, `f108v`, `f112v`, `f113v`, `f114r`, `f114v`, `f115v`), the tailed left-margin stars **strictly alternate `1-to-1` (`L. L L. L L. L...`) between a central dark ink dot (`L.`) and a plain yellow wash (`L`) without a single exception** (e.g., 15 paragraphs in a row on `f106r` and 13 in a row on `f104v`).
- On `f103r` ([`pages/f103r_stars_margin.png`](file:///c:/Users/denni/Documents/voynich/pages/f103r_stars_margin.png)), `f104r`, and `f108r`, the stars lack tails on `f103r` and instead alternate between solid **dark red/crimson painted stars (`D`)** and **unpainted/yellow stars (`L` / `L.`)**.

### F. Right-Justified Paragraph Titles (`=Pt`) vs. Leaf-Tip Indentation (`f1r`, `f8r`, `f25r`, `f42v`, `f46v`)
- In `ZL3b-n.txt`, 8 lines across the manuscript are tagged `=Pt` (right-justified title/catchword lines): 4 on `f1r` (`ydaraishy`, `dain.os.teody`, `otol.daiiin`, `dchaiin`) and 4 on Herbal folios (`f8r.21` `schol.saiin`, `f25r.6` `dan.okain.otody`, `f42v.7` `ockhodody`, `f46v.8` `tchodar`).
- Visual inspection of [`pages/f8r_pt_title.png`](file:///c:/Users/denni/Documents/voynich/pages/f8r_pt_title.png), [`pages/f25r_pt_title.png`](file:///c:/Users/denni/Documents/voynich/pages/f25r_pt_title.png), [`pages/f42v_pt_title.png`](file:///c:/Users/denni/Documents/voynich/pages/f42v_pt_title.png), and [`pages/f46v_pt_title.png`](file:///c:/Users/denni/Documents/voynich/pages/f46v_pt_title.png) reveals an important physical distinction:
  - On `f1r` and `f8r` ([`pages/f8r_pt_title.png`](file:///c:/Users/denni/Documents/voynich/pages/f8r_pt_title.png)), there is open blank vellum to the left of the `=Pt` words (`schol.saiin` on `f8r`), proving they are genuine **right-justified colophon/catchword lines** (and `schol` recurs in only two other Herbal paragraphs, `f14r.3` and `f56r.3`, while `dchaiin` from `f1r.28` recurs in only 4 Herbal paragraphs: `f20r`, `f25r`, `f35r`, `f35v`).
  - By contrast, on `f25r` ([`pages/f25r_pt_title.png`](file:///c:/Users/denni/Documents/voynich/pages/f25r_pt_title.png)), `f42v` ([`pages/f42v_pt_title.png`](file:///c:/Users/denni/Documents/voynich/pages/f42v_pt_title.png)), and `f46v` ([`pages/f46v_pt_title.png`](file:///c:/Users/denni/Documents/voynich/pages/f46v_pt_title.png)), the final line of the paragraph appears right-indented **only because the tallest green leaf or flower head rises directly into the left half of that line**, forcing the scribe to indent the paragraph's final words to the right of the illustration!

### G. Zodiac Medallions, Occidental Month Glosses & Barrel-to-Naked Nymph Transition (`f70v2–f73v`)
- Extracting and enhancing the central medallions across the Zodiac section (`p128–p135`) reveals both the Western (Occitan/Franco-Provençal) month names added in the center medallions and a sharp visual transition in the surrounding ~30 degree-nymphs:
  - [`pages/f70v2_pisces_mars.png`](file:///c:/Users/denni/Documents/voynich/pages/f70v2_pisces_mars.png) (`Pisces` / **`mars`**): Two scaly fish tethered to gold stars; surrounding nymphs stand inside green-painted **cylindrical barrels/turrets**.
  - [`pages/f72r2_gemini_juny.png`](file:///c:/Users/denni/Documents/voynich/pages/f72r2_gemini_juny.png) (`Taurus II` **`may`** on left, `Gemini` **`juny`** in center): On `f72r1` (`Taurus II`), the nymphs are still inside barrels; on `f72r2` (`Gemini`, showing a courtly couple in green and blue holding hands), the barrels disappear!
  - [`pages/f72r3_cancer_jolh.png`](file:///c:/Users/denni/Documents/voynich/pages/f72r3_cancer_jolh.png) (`Cancer` / **`jolh`**): Two red/green crayfish in the center medallion surrounded by **unbarreled** nymphs.
  - [`pages/f72v3_leo_agost.png`](file:///c:/Users/denni/Documents/voynich/pages/f72v3_leo_agost.png) (`Leo` / **`agost`**), [`pages/f72v2_virgo_setembre.png`](file:///c:/Users/denni/Documents/voynich/pages/f72v2_virgo_setembre.png) (`Virgo` / **`septemb'`**), [`pages/f72v1_libra_octobre.png`](file:///c:/Users/denni/Documents/voynich/pages/f72v1_libra_octobre.png) (`Libra` / **`octobre`**), and [`pages/f73r_scorpio_novembre.png`](file:///c:/Users/denni/Documents/voynich/pages/f73r_scorpio_novembre.png) (`Scorpio` / **`novembre`**): All feature **unbarreled** full-body nymphs holding stars (and on `f72v2` Virgo, the rare label `<f72v2.10,@Lz> sheoeky` at 11 o'clock matches `<f72v2.4,@Cc> sheeoeky` at 6 o'clock of the inner ring, global canonical count = 3).

---

## 3. Eight Quantitative & Structural Discoveries

### Discovery 1: The Physical Line & Drawing-Intrusion State Machine
Voynich word morphology is governed not just by sentence syntax, but by **physical layout coordinates on the vellum** (left margin, line interior, plant-stem interruption `<->`, right margin, and top line of a paragraph):

| Position Bucket | Token Count | Avg Len | Initial Gallows (`t/k/p/f`) | Starts with `qo-` | Starts with `y-` | Starts with `o-` (non-`qo`) | Ends with `-m` (`-am/-om`) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Paragraph Start (`<%>`)** | 736 | **6.49** | **83.6%** | 3.3% | 1.6% | 3.9% | 1.0% |
| **Line Start (Left Margin)** | 3,373 | 5.24 | 8.9% | 14.7% | **17.6%** | 15.4% | 0.4% |
| **Line Interior (`line_mid`)** | 25,497 | 4.98 | 8.9% | **16.7%** | 3.4% | 21.3% | 0.9% |
| **Before Drawing (`w <->`)** | 746 | **4.31** | 12.5% | 9.7% | 4.3% | 15.7% | 2.4% |
| **After Drawing (`<-> w`)** | 746 | 4.89 | 2.5% | **3.1%** | **14.5%** | 24.4% | 1.9% |
| **Line End (Right Margin)** | 3,382 | 4.63 | 8.4% | 8.9% | 4.2% | 22.1% | **16.8%** |
| **Paragraph End (`<$>`)** | 727 | 5.45 | 5.9% | 4.7% | 3.2% | 27.1% | **9.2%** |
| **Isolated Labels (`@L`)** | 1,033 | 5.26 | 4.1% | **0.9%** | 8.4% | **52.7%** | 5.6% |

**Key Implications:**
1. **Drawing Interruptions Trigger a Line-Start Reset**: When a pre-drawn plant stem (`<->`) bisects a line of text, the word immediately before the stem compresses in length (`4.31` chars, dominated by short words like `dy`, `s`, `sy`), and the word immediately **after** the stem (`<-> w`) resets to the **left-margin state**: `y-` jumps over **4×** (`3.4%` $\to$ `14.5%`, matching `line_start`'s `17.6%`) while `qo-` drops over **5×** (`16.7%` $\to$ `3.1%`).
2. **Right-Margin `-m` Marker**: Words ending in `-m` (`-am`, `-om`, `-aim`, `dam`) occur **18.6× more frequently** at the physical right end of a line (`16.8%`) than inside a line (`0.9%`).
3. **Top-Line Gallows Allography (`p/f` are Top-Line Allographs of `t/k`)**:
   - In the first line of a paragraph (`Line 0`), **22.08%** of all words contain a looped gallows (`p` or `f`), and **50.81%** of paragraph-opening words begin with `p`/`f`.
   - In all lower lines of a paragraph (`Line 1+`), `p`/`f` drop **17-fold** to **1.30%**, whereas unlooped `k`/`t` remain constant (`41.60%` in Line 0 vs `46.28%` in Line 1+).
   - This indicates `p` and `f` are positional/calligraphic top-line allographs of `t` and `k`.

---

### Discovery 2: The `q-` Proclitic Rule (`qoX` = `q-` + Nominal `oX`)
One of the most striking asymmetries in the entire manuscript is the behavior of `qo-` vs `o-` between running prose and isolated picture labels (`@L`):
- In running prose (`line_mid`), `qo-` accounts for **16.7%** of all words and `o-` accounts for **21.3%**.
- In isolated picture labels (`@L` — single words attached to plants, jars, stars, and nymphs), **`qo-` practically vanishes (`0.9%`, an 18.5× suppression)**, while bare **`o-` surges to `52.7%` of all labels**!
- Across the entire manuscript, **92.9% of all `qo-...` word tokens (`4,785 / 5,149`) have an exact bare `o-...` twin (`w[1:]`)** in the corpus (e.g., `qokeedy`/`okeedy`, `qokeey`/`okeey`, `qokain`/`okain`, `qokal`/`okal`, `qokol`/`okol`, `qotedy`/`otedy`, `qotar`/`otar`).
- Similarly, **85%–93%** of `y-...` tokens (`yk-`, `yt-`, `ych-`, `ysh-`) have an exact `y`-less twin (`k-`, `t-`, `ch-`, `sh-`).
- **Linguistic/Cryptographic Conclusion**: `q-` is **not part of any noun's root stem**. Standalone nouns (figure labels) are written in the bare `o-...` form (`okal`, `otar`, `okol`, `okoldy`, `olol`, `opol`, `okeos`). When those nouns are embedded inside a running clause, `q-` is prepended as a **clause-internal proclitic** (functioning like a conjunction *"and"*, preposition *"of/with/in"*, article, or object/verb marker), whereas `y-` functions as a **line/segment-initial proclitic**.

---

### Discovery 3: Direct Same-Folio Label-to-Paragraph Cross-Referencing ($z = +2.79, p = 0.002$)
Previously, researchers struggled to find links between the single-word labels on illustrations (`@L`) and the adjacent text paragraphs (`@P0`). By applying our **4-Rule Canonical Normalization**:
1. Strip proclitics (`qoX` $\to$ `oX`, `yX` $\to$ `X`)
2. Collapse top-line gallows allographs (`p` $\to$ `t`, `f` $\to$ `k`, `cph` $\to$ `cth`, `cfh` $\to$ `ckh`)
3. Compress vowel runs (`e+` $\to$ `e`, `i+` $\to$ `i`, `o+` $\to$ `o`, `a+` $\to$ `a`)
4. Neutralize line-final `-m` coda (`-m` $\to$ `-r`)

the manuscript's raw vocabulary compresses by **26.5%** (`8,101` raw types $\to$ `5,956` canonical roots), and a 1,000-trial permutation test (shuffling paragraphs strictly within the same Currier language `A`/`B`) proves that **labels on a folio match the paragraph text on that exact same folio significantly above chance ($71$ observed vs $57.78 \pm 4.73$ expected, $z = +2.79, p = 0.002$)**.

#### Smoking-Gun Rare Same-Folio Label $\leftrightarrow$ Paragraph Pairs:
1. **Folio `f99v` (`doldam` $\leftrightarrow$ `doldam`, Global MS Count = 2)** — [View Scan `pages/f99v_doldam_pair.png`](file:///c:/Users/denni/Documents/voynich/pages/f99v_doldam_pair.png)
   - The 6-letter word `doldam` occurs **only twice in the entire 38,409-word manuscript**:
     - `<f99v.31,@Lf> doldam`: The label directly above the 5th (rightmost) crossed root in Row 2 of `f99v`.
     - `<f99v.34,+P0> ...qokeeor.or.aiin.doldam`: Three lines below that exact root, at the rightmost end of line 34!
2. **Folio `f89r2` (`opcheor` $\leftrightarrow$ `opcheor`, Global MS Count = 2)** — [View Scan `pages/f89r2_opcheor_crop.png`](file:///c:/Users/denni/Documents/voynich/pages/f89r2_opcheor_crop.png)
   - The word `opcheor` occurs **only twice in the entire manuscript**:
     - `<f89r2.5,@Lf> opcheor`: Plant label in Row 1 of `f89r2`.
     - `<f89r2.22,@P0> kolches.sheol.qokeoefy.sheey.opcheor.opcheol...`: First line of the third recipe paragraph on `f89r2`.
3. **Folio `f75v` (`olol` $\leftrightarrow$ `qolol`, Global MS Count of `qolol` = 1)**
   - A bathing nymph on `f75v` is labeled `olol`. In the paragraph text on the same page (`<f75v.16,+P0>`) appears `qolol` (`q-` + `olol`) — its **only occurrence in the entire manuscript** (and `olol` itself also appears at the end of line `<f75v.40>`).
4. **Folio `f82v` (`okoldy` $\leftrightarrow$ `qokoldy` and `olkol` $\leftrightarrow$ `olkol`)** — [View Scan `pages/f82v_okoldy_olkol_crop.png`](file:///c:/Users/denni/Documents/voynich/pages/f82v_okoldy_olkol_crop.png)
   - Out of the 10 labels around the bottom pool of `f82v` (`f82v.39..48`), **6 (`60%`)** appear in the paragraph text on `f82v`:
     - Label `<f82v.45,@Lt> okoldy` $\to$ Paragraph `<f82v.13,+P0> ...qokoldy` (`qokoldy` occurs only **2 times** in the entire manuscript!).
     - Label `<f82v.46,@Lt> olkol` $\to$ Paragraph `<f82v.37,+P0> ...olkol...` (`olkol` occurs only **3 times** in the entire manuscript!).
     - Notice also the structural split: `ol-` labels (`olkeedy`, `olkol`) appear in `f82v` prose **verbatim without `q-`**, whereas `ok-`/`ot-` labels (`okoldy`, `okol`, `okain`, `otedy`, `oteedy`) all take **`q-`** (`qokoldy`, `qokol`, `qokain`, `qotedy`, `qoteedy`)!
5. **Folio `f84r` (`otoly` $\leftrightarrow$ `opoly` and `shekar` $\leftrightarrow$ `shekam`)** — [View Scan `pages/f84r_top_crop.png`](file:///c:/Users/denni/Documents/voynich/pages/f84r_top_crop.png)
   - Under the top canopy of `f84r`, the second nymph from the right is labeled `<f84r.11,@Ln> otoly` (global count = 4). Directly below her, at the right end of Line 1 of the paragraph (`<f84r.13,@P0>`), is **`opoly`** (global count = 2) — the exact same word with the top-line gallows allograph `p` replacing `t`!
   - Also in the top canopy of `f84r` is the unique label `<f84r.2,@Lt> shekar` (global count = 1). At the right end of line `<f84r.30,+P0>` on the same page is **`shekam`** (global count = 2) — the exact same stem with the line-final `-m` ending replacing `-r`!

---

### Discovery 4: Line-End Clustering of Referenced Figure Labels (and Horizontal Position Analysis)
When a rare figure label (`MS canonical count <= 30`) is referenced inside a paragraph on the same folio:
- **Line-Initial (`line_start`)**: `0 / 830` (**0.00 per 1,000 words**)
- **Line-Interior (`line_mid`)**: `10 / 5,545` (**1.80 per 1,000 words**)
- **Line-Final (`line_end`)**: `6 / 825` (**7.27 per 1,000 words — 4.0× higher than line interior!**)

Testing the horizontal ordinal position of the label in its row ($x_{\text{label}} \in [0, 1]$) against the word's ordinal position in its paragraph line ($x_{\text{word}} \in [0, 1]$) in [`tools/test_cross_section_links.py`](file:///c:/Users/denni/Documents/voynich/tools/test_cross_section_links.py) (`n=16`) reveals why:
- **75% (`12 / 16`)** of referenced rare labels come from the **right half of their label group** ($x_{\text{label}} \ge 0.5$, including 4 that are the rightmost label in their row, $x_{\text{label}} = 1.0$: `okan` on `f80r`, `opcheor` on `f89r2`, `doldam` on `f99v`), AND
- **62.5% (`10 / 16`)** of prose occurrences sit in the **rightmost 25% of the paragraph line** ($x_{\text{word}} \ge 0.75$, with 6 at the exact end of the line, $x_{\text{word}} = 1.0$), **even when the figure label itself sits on the far left of the page** (e.g., `shekar` at $x_{\text{label}} = 0.167$ on `f84r` is placed at the right end of line 30 as `shekam`, $x_{\text{word}} = 1.000$; `dary` at $x_{\text{label}} = 0.067$ on `f66r` is placed at $x_{\text{word}} = 0.750$). Thus, line-final position is a **syntactic/prosodic slot** for nominal label references rather than a mechanical vertical column drop.

---

### Discovery 5: Starred Recipes (`f103r–f116r`) Binary Alternation & Star-Type Morphology
Analyzing all 308 paragraphs in the Starred Recipes section (`$I=S`, [`data/recipes_and_stars_analysis.json`](file:///c:/Users/denni/Documents/voynich/data/recipes_and_stars_analysis.json) & [`data/cross_section_and_alignment.json`](file:///c:/Users/denni/Documents/voynich/data/cross_section_and_alignment.json)) uncovers three systematic patterns:
1. **Strict `1-to-1` Dotted vs. Plain Yellow Alternation (`L. L L. L...`)**:
   - On 12 of the 26 pages (`f103v`, `f104v`, `f105v`, `f106r`, `f106v`, `f107v`, `f108v`, `f112v`, `f113v`, `f114r`, `f114v`, `f115v`), the margin stars strictly alternate between **Light Dotted (`L.`, ink dot in center)** and **Light Plain (`L`, yellow wash without dot)** ([`pages/f106r_stars_margin.png`](file:///c:/Users/denni/Documents/voynich/pages/f106r_stars_margin.png)).
   - On those 12 strictly alternating pages, `L.` (odd-numbered) paragraphs average **37.2 words** (`n=80`) vs **32.7 words** (`n=72`) for `L` (even-numbered) paragraphs, while vocabulary Jaccard similarity between adjacent `(L., L)` pairs (`0.0855`) is nearly identical to `(L, L.)` (`0.0829`) and non-adjacent paragraphs on the same folio (`0.0809`). This indicates the binary star alternation functions as a **visual zebra-striping / rubrication aid** so a reader consulting a dense page of 12–15 unnumbered recipes does not lose their place.
2. **Dark Red Stars (`D`) vs. Light Stars (`L` / `L.`) on `f103r`, `f104r`, `f108r`**:
   - Paragraphs marked with solid dark red/crimson stars (`n=14`, [`pages/f103r_stars_margin.png`](file:///c:/Users/denni/Documents/voynich/pages/f103r_stars_margin.png)) are significantly shorter (**30.2 words** vs **40.0 words** for light-star paragraphs), have higher `-edy` verbal/participial endings (**20.8%** vs **14.0%**), lower `-aiin` nominal endings (**7.1%** vs **11.9%**), and **21.4%** of dark-star paragraphs begin directly with `q-` (`qokeey` / `qokeedy`) vs **0.0%** of dotted-star paragraphs!
3. **Tailed vs. Tailless Stars**:
   - Paragraphs with tailed stars (`n=264`) have **more than double the `-aiin` frequency (`12.84%`)** of paragraphs with tailless stars (`n=24`, `5.53%`), largely reflecting the shift between `f103r` (tailless, high `-edy`) and `f103v–f116r` (tailed, high `-aiin`).

---

### Discovery 6: Section-Specific Rare Label Enrichment & Pharmaceutical-to-Recipe Ingredient Links
Testing all rare figure labels (`global canonical frequency 2..15`, length $\ge 4$) across manuscript sections ([`data/cross_section_and_alignment.json`](file:///c:/Users/denni/Documents/voynich/data/cross_section_and_alignment.json)) reveals strong section-specific and language-specific vocabulary bridges:

| Label Section (`@L`) | Rare Label Roots (`freq 2..15`) | Recurrence in **Starred Recipes (`S`)** | Recurrence in **Herbal (`H`)** | Recurrence in **Biological (`B`)** | Recurrence in **Pharmaceutical (`P`)** |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Pharmaceutical (`P`)** | 63 | **58.7%** | 50.8% | 28.6% | **30.2%** |
| **Biological (`B`)** | 34 | **58.8%** | 50.0% | **47.1%** | 11.8% |
| **Zodiac (`Z`)** | 80 | **61.3%** | 45.0% | 20.0% | 17.5% |
| **Astronomical (`A`)** | 37 | **62.2%** | **83.8%** | 18.9% | 27.0% |
| **Cosmological (`C`)** | 15 | 53.3% | 46.7% | 6.7% | 0.0% |

- **Self-Section Enrichment**: Rare Biological (`B`) labels recur in `B` prose at **47.1%** (over **2.3×** the rate of Zodiac/Astro/Cosmo labels in `B`), and rare Pharmaceutical (`P`) labels recur in `P` prose at **30.2%** (**2.5×** the rate of `B` labels in `P`).Meanwhile, rare Astronomical (`A`) labels recur in Herbal (`H`) prose at **83.8%** ( reflecting shared Currier Language A roots).
- **Direct Pharmaceutical Container/Plant Label $\to$ Starred Recipe Matches**:
  1. `<f102v1.1,@Lc> keoraiiin` (apothecary jar label on `f102v1`, global canonical count = **2**) $\to$ occurs only once more in the entire manuscript, in the opening line of the top Starred Recipe on `f106v`: `<f106v.2,@P0> ...keorain...` ([`pages/f106v_keorain_crop.png`](file:///c:/Users/denni/Documents/voynich/pages/f106v_keorain_crop.png))!
  2. `<f102v2.24,@Lc> okolky` (jar label on `f102v2`, global canonical count = **2**) $\to$ occurs only once more in the entire manuscript, with the `q-` proclitic attached (`qokolky`), inside a Starred Recipe on `f105r`: `<f105r.30,+P0> ...qokolky...` ([`pages/f105r_qokolky_crop.png`](file:///c:/Users/denni/Documents/voynich/pages/f105r_qokolky_crop.png))!
  3. `<f100r.6,@Lf> oraro` (plant label on `f100r`, global canonical count = **2**) $\to$ occurs only once more in the entire manuscript, in the opening line of the top Starred Recipe on `f115r`: `<f115r.1,@P0> pol.chdar.oraro...`!
  4. `<f99v.9,@Lf> otoky` (plant label on `f99v`, global canonical count = **4**) $\to$ occurs with the `q-` proclitic (`qotoky`) in Starred Recipe `<f106r.10,+P0>`!
  5. `<f99r.19,@Lc> oparal` (tall apothecary jar label on `f99r`, global canonical count = **3**) $\to$ recurs in two Starred Recipes (`<f107r.13,+P0> otaral` and `<f111r.36,+P0> otaral`) with the regular interior gallows `t` replacing the label's `p`!

---

### Discovery 7: Five-Scribe Invariance (`$H=1..5`) of the Physical Line & Proclitic Grammar
Lisa Fagin Davis's paleographic analysis established that **five distinct human scribes** (`$H=1..5`) wrote the Voynich Manuscript across Currier Languages `A` and `B`. Testing our four structural rules independently across each of the 5 scribe hands ([`tools/analyze_zodiac_and_hands.py`](file:///c:/Users/denni/Documents/voynich/tools/analyze_zodiac_and_hands.py) $\to$ [`data/zodiac_and_hands_analysis.json`](file:///c:/Users/denni/Documents/voynich/data/zodiac_and_hands_analysis.json)) proves that **all 5 scribes independently obey the exact same orthographic and positional grammar**:

| Scribe Hand (`$H`) | Folios | Words | Currier Lang | Top-Line `p/f` vs Lower-Line `p/f` | `y-` Init: `LineMid` $\to$ `AfterDraw (<->)` (vs `LineStart`) | `qo-` Init: `LineMid` $\to$ `AfterDraw (<->)` $\to$ `Labels (@L)` | `-m` End: `LineMid` $\to$ `LineEnd` |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Hand 1** | 113 | 11,037 | `A` | **21.7%** vs **1.1%** (**19.5×**) | `4.7%` $\to$ **12.5%** (`14.7%`) | `9.4%` $\to$ **1.3%** $\to$ **0.0%** (`47.9%` bare `o-`) | `1.6%` $\to$ **10.1%** (**6.2×**) |
| **Hand 2** | 46 | 11,177 | `B` | **25.4%** vs **1.6%** (**16.3×**) | `3.8%` $\to$ **14.9%** (`12.0%`) | `20.4%` $\to$ **8.7%** $\to$ **2.2%** (`56.6%` bare `o-`) | `0.5%` $\to$ **13.5%** (**26.0×**) |
| **Hand 3** | 33 | 11,766 | `B` / `A` | **20.7%** vs **1.2%** (**17.9×**) | `2.4%` $\to$ **30.4%** (`16.6%`) | `18.2%` $\to$ **0.0%** $\to$ **0.0%** (`40.0%` bare `o-`) | `0.8%` $\to$ **23.6%** (**30.3×**) |
| **Hand 4** | 26 | 3,083 | `A/Z` | **10.7%** vs **2.5%** (**4.3×**) | `7.5%` $\to$ **25.0%** (`20.2%`) | `6.9%` $\to$ **0.0%** $\to$ **0.4%** (`58.1%` bare `o-`) | `1.8%` $\to$ **19.1%** (**10.5×**) |
| **Hand 5** | 7 | 926 | `B` | **38.0%** vs **1.9%** (**19.7×**) | `8.3%` $\to$ **30.6%** (`14.9%`) | `11.8%` $\to$ **5.6%** $\to$ **7.7%** | `0.9%` $\to$ **19.2%** (**22.0×**) |

**Key Implication**: Because all five paleographically distinct scribes execute the exact same 4-part system—(1) `p/f` top-line gallows allography (`4.3×–19.7×`), (2) drawing-interruption `<->` reset to `y-` initial and `qo-` suppression, (3) `q-` proclitic omission in `@L` labels, and (4) line-final `-m` termination (`6.2×–30.3×`)—these patterns **cannot be the unconscious personal tic of a single hoaxer**. All 5 scribes were trained in (or copying from exemplars governed by) a shared, explicit rule system.

---

### Discovery 8: The Zodiac `ot-` $\to$ `ok-` Barrel-Nymph Shift ($\chi^2 = 24.01, p = 9.6 \times 10^{-7}$) & Label Prefix Taxonomy
Analyzing all 350 Zodiac degree-nymph labels (`@Lz`) across the 12 Zodiac pages ([`tools/inspect_zodiac_details.py`](file:///c:/Users/denni/Documents/voynich/tools/inspect_zodiac_details.py) $\to$ [`data/zodiac_prefix_split.json`](file:///c:/Users/denni/Documents/voynich/data/zodiac_prefix_split.json)) uncovers a striking correlation between **visual iconography** and **noun prefix (`ot-/op-` vs. `ok-/of-`)**:
1. **Barreled Nymphs (`f70v2–f72r1`: Pisces, Aries I/II, Taurus I/II)**:
   - On the first 5 Zodiac pages, the degree-nymphs emerge from cylindrical **barrels/turrets** ([`pages/f70v2_pisces_mars.png`](file:///c:/Users/denni/Documents/voynich/pages/f70v2_pisces_mars.png)).
   - On every single one of these 5 pages, **`ot-/op-` outnumbers `ok-/of-`**, totaling **56 `ot-/op-` vs. 20 `ok-/of-` (`73.7%` `ot-/op-`)**!
2. **Unbarreled Nymphs (`f72r2–f73v`: Gemini through Sagittarius)**:
   - Starting on `f72r2` (`Gemini`, [`pages/f72r2_gemini_juny.png`](file:///c:/Users/denni/Documents/voynich/pages/f72r2_gemini_juny.png)), the barrels disappear and the nymphs stand naked/unbarreled ([`pages/f72v2_virgo_setembre.png`](file:///c:/Users/denni/Documents/voynich/pages/f72v2_virgo_setembre.png)).
   - Immediately, the prefix ratio inverts: **`ok-/of-` outnumbers `ot-/op-` on every page**, totaling **68 `ok-/of-` vs. 40 `ot-/op-` (`63.0%` `ok-/of-`, `37.0%` `ot-/op-`)** — a highly significant contingency shift ($\chi^2 = 24.01, p = 9.6 \times 10^{-7}$)!
   - Even more remarkably, the exact same `ot-/op-` vs. `ok-/of-` polarity recurs in the **Biological section (`$I=B`, `f75r–f84v`)**: labels on **tubes/barrels/pools (`*Lt`, `n=55`)** favor **`ot-/op-` over `ok-/of-` (`16` vs. `11`, `59.3%` `ot-/op-`)**, whereas labels on **free-standing nymphs (`*Ln`, `n=60`)** favor **`ok-/of-` over `ot-/op-` (`15` vs. `9`, `62.5%` `ok-/of-`)**!
3. **The Cancer (`f72r3`) `ol-/or-` Anomaly**:
   - On `f72r3` (`Cancer` / `jolh`, [`pages/f72r3_cancer_jolh.png`](file:///c:/Users/denni/Documents/voynich/pages/f72r3_cancer_jolh.png)), both `ok-` (`2`) and `ot-` (`2`) collapse to `<10%` of the 41 nymph labels and are replaced by liquid-initial **`ol-` (`6`) and `or-` (`5`)** labels.
4. **Verified Negative Result on Zodiac Nymph-to-Ring Matching ($p = 0.85$)**:
   - Unlike Herbal, Biological, and Pharmaceutical pages—where `@L` labels recur significantly inside the same folio's `@P0` paragraphs ($p = 0.002$)—Zodiac nymph labels (`@Lz`) do not generally repeat in the continuous `@Cc` ring text of the same diagram (`obs = 2` vs `null = 3.40 ± 1.82`), with the notable exception of `<f72v2.10,@Lz> sheoeky` $\leftrightarrow$ `<f72v2.4,@Cc> sheeoeky` (global count = 3) on Virgo (`f72v2`).

---

## 4. Open Questions & Next Avenues to Explore
1. **Multi-Word Collocations, Repeated Phrases & Formulaic Templates**: What are the most frequent 2-word and 3-word collocations across the manuscript, and do specific multi-word formulas mark paragraph openings, endings, or transitions?
2. **Glen Claston (`v101`, `GC2a-n.txt`) vs. EVA (`ZL3b-n.txt`) Plumed Gallows & Rare Glyph Forensics**: Do rare or compound glyphs distinguished in `GC2a-n.txt` / `IT2a-n.txt` clarify any of our canonical roots or label pairs?
3. **Physical Book-Edge Scans (`p210–p213` in `2002046.pdf`) & Quire Structure**: What codicological details (quire signatures, foliation jumps, missing folios, edge markings) can we extract from the 4 physical book-edge scans and quire metadata?


