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

---

## 3. Four Quantitative & Structural Discoveries

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

### Discovery 4: Line-End Clustering of Referenced Figure Labels
When a rare figure label (`MS canonical count <= 30`) is referenced inside a paragraph on the same folio:
- **Line-Initial (`line_start`)**: `0 / 830` (**0.00 per 1,000 words**)
- **Line-Interior (`line_mid`)**: `10 / 5,545` (**1.80 per 1,000 words**)
- **Line-Final (`line_end`)**: `6 / 825` (**7.27 per 1,000 words — 4.0× higher than line interior!**)

Furthermore, several of the line-final matches (`doldam` on `f99v.34`, `opoly` on `f84r.13`, `qokoldy` on `f82v.13`) are **vertically aligned on the right side of the page** with the corresponding right-side figure label above or below them.

---

## 4. Open Questions & Next Avenues to Explore
1. **Vertical / Columnar Alignment Test**: On pages with horizontal rows of labels (Pharmaceutical `f88r–f102v` and Biological `f75r–f84v`), do words in the paragraph below a row of labels correlate with the **horizontal $x$-coordinate** of the label directly above/below them?
2. **Starred Recipes (`f103r–f116r`) Ingredient Lookup**: Do the rare plant labels from the Pharmaceutical section (`f88r–f102v`) recur inside specific Starred Recipe paragraphs (`f103r–f116r`), allowing us to link individual recipes to specific illustrated plants?
3. **Zodiac & Star Labels (`f67r–f73v`)**: Can we apply our 4-Rule Canonical Normalization to map the Zodiac nymph labels (`f70v–f73v`) against medieval astrological decan / degree lists or the Western month names written on those folios?
4. **Scribe Hand Transitions (`$H=1..5`)**: How do the 4 morphological rules vary across Lisa Fagin Davis's 5 paleographic scribe hands?
