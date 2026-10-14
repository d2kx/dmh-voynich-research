# Attack 239: Empirical Test of the Self-Citation / Autocopy Hypothesis (Timm & Schinner 2019/2020)

- **Script**: [`tools/attack239_self_citation_autocopy.py`](../tools/attack239_self_citation_autocopy.py)
- **Dataset**: [`data/attack239_self_citation_autocopy.json`](../data/attack239_self_citation_autocopy.json)
- **Corpus**: [`data/ZL3b-n.txt`](../data/ZL3b-n.txt) via [`tools/voynich_corpus.py`](../tools/voynich_corpus.py), restricted to running-text lines (`unit == 'P'`), clean tokens only (`207` folios, `34,780` clean tokens, `6,983` word types; `1,751,316` type pairs in raw `eva_chars` and `1,752,275` in collapsed `units`).

---

## 1. Executive Summary & Verdict

The **self-citation (autocopying) hypothesis** advanced by Torsten Timm and Andreas Schinner (2019/2020) proposes that the Voynich Manuscript was generated without an underlying text or cipher by a mechanical copying process: as the scribe wrote each word in line $i$, he allegedly glanced back at a recently written word on the same folio—most often in the **line directly above ($i-1$) at roughly the same horizontal position**—and copied it with a small graphic modification (e.g., substituting `ch <-> sh`, adding/removing a minim in `aiin <-> ain`, or swapping a prefix/suffix).

To test this hypothesis rigorously without unstated distributional confounds, Attack 239 evaluates **four falsifiable predictions** across **34,780 clean running-text tokens on 207 folios** under two orthographies:
1. **Raw EVA characters (`eva_chars`)**: standard character-by-character Levenshtein distance.
2. **Collapsed EVA units (`units`)**: multi-character ligatures and minim groups collapsed into single atomic symbols (`aiiin -> N`, `aiin -> M`, `ain -> L`, `cth -> T`, `ckh -> K`, `cph -> P`, `cfh -> F`, `ch -> C`, `sh -> S`) so that a single bench/gallows or minim-count change (`ch <-> sh`, `cth <-> ch`, `aiin <-> ain`) counts as a single edit ($d_{\text{Lev}} = 1$).

### Core Empirical Findings
1. **Genuine Local Similarity & Distance Decay Exist ($z = 11.88\text{–}19.25$, $p < 0.01$), But 94% of Multi-Line Match Rates Are Global Morphological Baseline**:
   - At lag $d = 1$ line back ($N = 32,983$), **25.55%** of raw EVA tokens (**30.30%** in collapsed `units`) have a $\le 1$-edit neighbor in the line immediately above, compared to **19.27%** (**23.29%** in `units`) against a random line of identical word length from a *different* folio of the same `(Language, Hand, Section)` stratum.
   - However, decomposing this **+6.28 percentage-point (`pp`)** total excess (`+7.01 pp` in `units`) reveals three distinct layers:
     - **39.2% (`+2.46 pp`)** is **whole-folio vocabulary/topic specificity** (preserved when all lines on the folio are randomly shuffled).
     - **23.0% (`+1.44 pp`)** is **paragraph-level clustering** (preserved when lines are shuffled *within* each paragraph).
     - Only **37.8% (`+2.38 pp`, `eva_chars`) to 38.0% (`+2.66 pp`, `units`)** is genuine **within-paragraph line-to-line proximity** ($z = 11.88$ and $z = 13.78$).
   - Over a cumulative 10-line backward window (`window_k = 10`), **69.50%** of tokens (`eva_chars`) and **74.41%** (`units`) have a $\le 1$-edit match. Yet **65.35%** (`eva_chars`) and **70.41%** (`units`) of tokens *also* find a $\le 1$-edit match in 10 random lines drawn from **completely different folios of the same stratum**! Thus **94.0%–94.6%** of the high cumulative match rate cited by Timm & Schinner is an automatic byproduct of the Voynich Manuscript's compact, low-entropy templatic morphology rather than page-local copying.
2. **Time-Reversal (Backward vs. Forward) Asymmetry Is Completely Null Inside Paragraph Interiors ($p = 0.358\text{–}0.467$)**:
   - When candidate-set sizes are equalized exactly via hypergeometric expectation ($m = \min(n_{\text{bwd}}, n_{\text{fwd}})$), tokens on unrestricted lines (`all_lines`) or full paragraphs (`same_paragraph`) are actually **closer to the line *below* ($i+1$) than to the line *above* ($i-1$)** (`fwd_minus_bwd_min = -0.0277` edits on `all_lines`, `-0.0499` edits on `same_paragraph`, $p = 0.0005$).
   - This reverse asymmetry is driven by **paragraph-initial header lines (`pfirst`)**: line 1 of a paragraph carries specialized top-line gallows (`p/f`) and opening formulas, making line 2 more similar to line 3 (below it) than to line 1 (above it).
   - Once boundary lines (`pfirst` and `plast`) are excluded (`same_paragraph_no_boundary_lines`, $N = 12,379$), **backward vs. forward asymmetry vanishes**: `fwd_minus_bwd_min = +0.0111` edits (95% CI `[-0.0111, +0.0321]`, $p = 0.358$) and `bwd_minus_fwd_P_le1 = +0.37 pp` (95% CI `[-0.37 pp, +1.12 pp]`, $p = 0.369$) in `eva_chars` (`+0.32 pp`, $p = 0.467$ in `units`). Within-line left-vs-right interior asymmetry is likewise null ($p = 0.085\text{–}0.763$).
3. **Vertical Alignment to the Line Directly Above Collapses to Zero Once Line-Boundary Slots Are Removed ($95\%\text{ CI Spans }0$)**:
   - Across all tokens (`variant = all`, $N = 32,797$), best matches in line $i-1$ sit `1.38%` closer horizontally than random word-slot shuffling (`obs_minus_expected = -0.01378`, 95% CI `[-0.01590, -0.01164]`).
   - However, **72% of this effect (`-0.00991`) occurs even against a line from a completely different folio (`cross_folio_matched`)** because line-initial words match line-initial words and line-final words match line-final words across the entire manuscript!
   - Furthermore, **lag 1 (`-0.01378`) has *weaker* horizontal alignment than lags 2–5 (`-0.01648`)** (`lag1_minus_lag2to5 = +0.00270`, 95% CI `[+0.00075, +0.00518]`).
   - In the **`strict` test**—restricting to line-interior tokens (`0 < k < n - 1`) with a close match ($d_{\text{Lev}} \le 1$, $N = 6,239$ in `eva_chars`, $N = 7,403$ in `units`)—**vertical alignment at lag 1 disappears completely**: `obs_minus_expected = -0.00347` (95% CI `[-0.00775, +0.00102]`) in `eva_chars` and `-0.00319` (95% CI `[-0.00735, +0.00088]`) in `units`.

> **Verdict**: The physical mechanism of Timm & Schinner's self-citation hypothesis—**copying and mutating words by glancing vertically at the line directly above (`lag 1`, same horizontal coordinate `x_rel`)**—is **refuted** by the vertical alignment test (null on interior $\le 1$-edit matches, and weaker at lag 1 than at lags 2–5) and by the cross-folio baseline (which reproduces 94% of the 10-line cumulative match rate). What **is** empirically real is **symmetric, non-vertically-aligned local lexical and paradigmatic clustering** across a 1–5 line neighborhood within paragraphs and folios—the exact signature of topical coherence and repeated morphological paradigms in thematic/procedural text.

---

## 2. Test 1: Distance Decay Across Lags ($d = 1..10$) and Cumulative Windows ($k = 1..10$)

### 2.1 Methodology & Null Models
For every clean running-text token $w$ in line $i$ of a folio, we compute the minimum glyph-level Levenshtein distance $d_{\min}(w, L_{i-d}) = \min_{v \in L_{i-d}} d_{\text{Lev}}(w, v)$, the exact-repeat fraction $P(d_{\min} = 0)$, and the $\le 1$-edit fraction $P(d_{\min} \le 1)$ at single-line lags $d \in \{1, \dots, 10\}$ and cumulative backward windows $[i-k, i-1]$ for $k \in \{1, \dots, 10\}$. We compare the observed backward curve (`ob` / `wb`) against four baselines:
- **Forward observed (`of` / `wf`)**: line $i+d$ (or cumulative window $[i+1, i+k]$) on the same folio.
- **Null (a) Cross-folio same-stratum (`cr` / `wcr`)**: a running-text line with the **exact same clean-word count** drawn from a *different* folio in the same `(Currier Language, Scribe Hand, Section)` stratum (with hierarchical fallback `(lang, section) -> (lang) -> all`).
- **Null (c1) Within-folio shuffled lines (`sh` / `wsh`)**: all running-text lines on the same folio randomly permuted (`100` permutations for `eva_chars`, `40` for `units`).
- **Null (c2) Within-paragraph shuffled lines (`ps` / `wps`)**: lines randomly permuted *within each paragraph* on the folio, preserving paragraph boundaries and paragraph-specific vocabularies.

### 2.2 Single-Lag Distance Decay ($d = 1..10$)

#### Table 1A: Raw EVA Characters (`eva_chars`, $207$ Folios, $34,780$ Tokens)

| Lag $d$ | $N_{\text{obs}}$ | Obs Mean $\min d$ | Shuf (`sh`) Mean $\min d$ | Para-Shuf (`ps`) Mean $\min d$ | Cross-Folio (`cr`) Mean $\min d$ | Obs Exact ($d=0$) | Shuf (`sh`) Exact | Cross (`cr`) Exact | Obs $\le 1$ Edit | Shuf (`sh`) $\le 1$ Edit | Para-Shuf (`ps`) $\le 1$ Edit | Cross (`cr`) $\le 1$ Edit |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **1** | 32,983 | **2.4152** | 2.5653 | 2.5090 | 2.6514 | **6.725%** | 5.537% | 4.393% | **25.553%** | 21.733% | 23.177% | 19.274% |
| **2** | 31,025 | **2.4638** | 2.5652 | 2.5117 | 2.6544 | **6.385%** | 5.533% | 4.345% | **23.961%** | 21.744% | 23.075% | 19.194% |
| **3** | 29,199 | **2.4770** | 2.5647 | 2.5167 | 2.6461 | **5.973%** | 5.505% | 4.425% | **23.730%** | 21.761% | 22.918% | 19.521% |
| **4** | 27,476 | **2.5120** | 2.5631 | 2.5220 | 2.6470 | **5.798%** | 5.495% | 4.404% | **22.849%** | 21.796% | 22.782% | 19.148% |
| **5** | 25,803 | **2.5120** | 2.5631 | 2.5274 | 2.6498 | **5.953%** | 5.488% | 4.298% | **22.947%** | 21.788% | 22.607% | 18.978% |
| **6** | 24,173 | **2.5156** | 2.5624 | 2.5309 | 2.6456 | **5.887%** | 5.460% | 4.348% | **22.732%** | 21.843% | 22.460% | 19.232% |
| **7** | 22,609 | **2.5262** | 2.5607 | 2.5338 | 2.6433 | **5.622%** | 5.456% | 4.481% | **22.562%** | 21.872% | 22.427% | 19.386% |
| **8** | 21,114 | **2.5192** | 2.5589 | 2.5352 | 2.6365 | **5.873%** | 5.456% | 4.211% | **22.398%** | 21.929% | 22.393% | 19.400% |
| **9** | 19,690 | **2.5216** | 2.5561 | 2.5349 | 2.6347 | **5.612%** | 5.483% | 4.185% | **22.702%** | 22.016% | 22.428% | 19.040% |
| **10** | 18,374 | **2.5376** | 2.5573 | 2.5351 | 2.6323 | **5.769%** | 5.474% | 4.452% | **22.347%** | 22.001% | 22.410% | 19.685% |

#### Table 1B: Collapsed EVA Units (`units`, $207$ Folios, $34,780$ Tokens)

| Lag $d$ | $N_{\text{obs}}$ | Obs Mean $\min d$ | Shuf (`sh`) Mean $\min d$ | Para-Shuf (`ps`) Mean $\min d$ | Cross-Folio (`cr`) Mean $\min d$ | Obs $\le 1$ Edit | Shuf (`sh`) $\le 1$ Edit | Para-Shuf (`ps`) $\le 1$ Edit | Cross (`cr`) $\le 1$ Edit |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **1** | 32,983 | **2.1047** | 2.2337 | 2.1855 | 2.3027 | **30.297%** | 26.034% | 27.634% | 23.288% |
| **2** | 31,025 | **2.1496** | 2.2362 | 2.1895 | 2.2962 | **28.306%** | 25.906% | 27.452% | 23.665% |
| **3** | 29,199 | **2.1593** | 2.2349 | 2.1938 | 2.3001 | **28.213%** | 25.988% | 27.263% | 23.378% |
| **4** | 27,476 | **2.1867** | 2.2345 | 2.1984 | 2.3035 | **27.264%** | 26.032% | 27.056% | 23.097% |
| **5** | 25,803 | **2.1904** | 2.2336 | 2.2030 | 2.3154 | **27.133%** | 25.998% | 26.836% | 23.067% |
| **6** | 24,173 | **2.1981** | 2.2363 | 2.2093 | 2.3029 | **26.757%** | 25.983% | 26.579% | 23.183% |
| **7** | 22,609 | **2.2068** | 2.2334 | 2.2132 | 2.3102 | **26.582%** | 25.995% | 26.443% | 22.929% |
| **8** | 21,114 | **2.2033** | 2.2360 | 2.2145 | 2.3058 | **26.286%** | 25.929% | 26.445% | 22.710% |
| **9** | 19,690 | **2.2077** | 2.2386 | 2.2180 | 2.2943 | **26.790%** | 25.831% | 26.257% | 23.352% |
| **10** | 18,374 | **2.2147** | 2.2398 | 2.2199 | 2.2986 | **26.227%** | 25.813% | 26.202% | 23.174% |

### 2.3 Three-Way Decomposition of Lag-1 Similarity & Distance Decay
Comparing the four curves at lag $d = 1$ allows us to partition the total local similarity excess (`observed - cross_folio`) into three orthogonal components:

| Component | `eva_chars` ($\le 1$ Edit) | Share of Total | `units` ($\le 1$ Edit) | Share of Total | Statistical Support (`eva_chars` / `units`) |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Total Local Excess (`ob - cr`)** | **+6.279 pp** | 100.0% | **+7.010 pp** | 100.0% | 95% CI `[+5.37, +7.08] pp` / `[+6.06, +7.98] pp` |
| 1. **Folio Vocabulary Effect (`sh - cr`)** | **+2.459 pp** | **39.2%** | **+2.746 pp** | **39.2%** | 95% CI `[+1.74, +3.10] pp` / `[+2.01, +3.48] pp` |
| 2. **Paragraph Clustering Effect (`ps - sh`)** | **+1.444 pp** | **23.0%** | **+1.600 pp** | **22.8%** | Paragraph-specific lexical domains on multi-paragraph pages |
| 3. **Within-Paragraph Line Proximity (`ob - ps`)** | **+2.376 pp** | **37.8%** | **+2.664 pp** | **38.0%** | 95% CI `[+1.94, +2.85] pp` ($z=11.88$) / `[+2.23, +3.10] pp` ($z=13.78$) |

- **Characteristic Decay Horizon ($d = 1..4$ lines)**:
  - Notice in Tables 1A and 1B that the observed $\le 1$-edit fraction (`ob`) converges onto the within-paragraph shuffled baseline (`ps`) by **lag $d = 4$** (`22.85%` vs. `22.78%` in `eva_chars`; `27.26%` vs. `27.06%` in `units`) and remains indistinguishable from `ps` across lags $d = 4..10$.
  - That is, **all distance decay beyond 3–4 lines is simply paragraph-boundary decay** (at larger lags, line $i-d$ is increasingly likely to belong to a different paragraph). Within a paragraph, local clustering operates over a short **1–3 line horizon** (`+2.38 pp` at $d=1$, `+0.89 pp` at $d=2$, `+0.81 pp` at $d=3$ over `ps` in `eva_chars`).

### 2.4 Cumulative Backward Windows ($k = 1..10$ Lines Back)

#### Table 1C: Cumulative Window Match Rates (`window_k_lines_back`)

| Window $k$ Lines Back | $N_{\text{obs}}$ | `eva_chars` Obs Exact | `eva_chars` Cross (`wcr`) Exact | `eva_chars` Obs $\le 1$ Edit | `eva_chars` Para-Shuf (`wps`) $\le 1$ Edit | `eva_chars` Cross (`wcr`) $\le 1$ Edit | `units` Obs $\le 1$ Edit | `units` Para-Shuf (`wps`) $\le 1$ Edit | `units` Cross (`wcr`) $\le 1$ Edit |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **1** | 32,983 | 6.725% | 4.393% | **25.553%** | 23.177% | 19.274% | **30.297%** | 27.634% | 23.288% |
| **2** | 31,025 | 11.762% | 8.077% | **38.930%** | 36.935% | 31.504% | **44.616%** | 42.655% | 37.602% |
| **3** | 29,199 | 15.525% | 11.175% | **47.324%** | 45.810% | 40.186% | **53.293%** | 51.852% | 46.745% |
| **5** | 25,803 | 21.494% | 16.421% | **57.451%** | 56.681% | 51.304% | **63.214%** | 62.492% | 57.652% |
| **10** | 18,374 | 31.523% | 25.618% | **69.500%** | 69.272% | 65.348% | **74.415%** | 74.089% | 70.415% |

- **Why High Multi-Line Match Rates Do Not Prove Self-Citation**:
  - In a 10-line backward window (`window_k = 10`), **69.50%** of raw EVA tokens (`74.41%` in `units`) have a $\le 1$-edit relative in the preceding 10 lines.
  - However, when those 10 lines are drawn from **completely different folios of the same stratum (`wcr`)**, **65.35%** of raw EVA tokens (`70.41%` in `units`) *still* have a $\le 1$-edit match!
  - Because Voynich words are short (`mean ~5 chars`, `~4 units`) and drawn from a tightly constrained prefix–root–suffix slot grammar (`qo-`, `ch-/sh-`, `o-/d-/s-` + core stems + `-dy/-edy/-aiin/-ol/-ar/-y`), any pool of ~90 words (10 lines) from the same Currier language and section covers nearly three-quarters of the active 1-edit neighborhood of any token.

---

## 3. Test 2: Backward vs. Forward Asymmetry Test (Time-Reversal Control)

### 3.1 Methodology: Exact Hypergeometric Candidate-Count Matching
A naive comparison of line $i-d$ (above) vs. line $i+d$ (below) is biased by **line-length asymmetry**: paragraph-final lines (`plast`) are often short partial lines, whereas paragraph-initial lines (`pfirst`) span the full width of the text block. Consequently, for a token inside a paragraph, line $i-d$ contains more words on average than line $i+d$, mechanically lowering the raw minimum distance in the backward direction.

To eliminate candidate-count bias exactly, for every token at line $i$ where both $L_{i-d}$ (with $n_b$ clean words) and $L_{i+d}$ (with $n_f$ clean words) exist on the folio, [`tools/attack239_self_citation_autocopy.py`](../tools/attack239_self_citation_autocopy.py) sets $m = \min(n_b, n_f)$ and computes the **exact hypergeometric expectation** over a uniformly random subset of size $m$ from each comparison line:
- $\Delta E_{\min} = E[\min_{\text{fwd}}] - E[\min_{\text{bwd}}]$ (`fwd_minus_bwd_expected_min_dist`): **positive ($>0$)** if backward is closer than forward; **negative ($<0$)** if forward is closer than backward.
- $\Delta P_{\le 1} = P_{\text{bwd}}(\min \le 1) - P_{\text{fwd}}(\min \le 1)$ (`bwd_minus_fwd_P_le1`): **positive ($>0$)** if backward has more $\le 1$-edit matches than forward.

We evaluate three structural subsets:
1. **`all_lines` (`all`)**: all line pairs $(i-d, i+d)$ on the same folio.
2. **`same_paragraph` (`par`)**: lines $i-d$, $i$, and $i+d$ all belong to the same paragraph.
3. **`same_paragraph_no_boundary_lines` (`cor`)**: lines $i-d$, $i$, and $i+d$ all belong to the same paragraph, **and** $L_{i-d}$ is not the paragraph-initial header line (`not pfirst`) and $L_{i+d}$ is not the paragraph-final line (`not plast`).

### 3.2 Results: Boundary-Line Reversal vs. Interior Symmetry

#### Table 2A: Paired Backward vs. Forward Asymmetry Across Lags & Windows (`eva_chars` and `units`)

| Test Kind & Lag/Window | Subset Variant | $N_{\text{tokens}}$ | `eva_chars` $\Delta E_{\min}$ (`fwd - bwd`) | `eva_chars` 95% CI ($\Delta E_{\min}$) | `eva_chars` Sign-Flip $p$ | `eva_chars` $\Delta P_{\le 1}$ (`bwd - fwd`) | `units` $\Delta E_{\min}$ (`fwd - bwd`) | `units` $\Delta P_{\le 1}$ (`bwd - fwd`) | `units` Sign-Flip $p$ ($\Delta E_{\min}$) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Lag $d=1$** | `all_lines` | 31,916 | **-0.02765** | `[-0.0402, -0.0163]` | **0.0005** | **-0.655 pp** | **-0.01784** | **-0.845 pp** | **0.0010** |
| **Lag $d=1$** | `same_paragraph` | 23,529 | **-0.04990** | `[-0.0676, -0.0319]` | **0.0005** | **-1.506 pp** | **-0.03194** | **-1.666 pp** | **0.0005** |
| **Lag $d=1$** | **`same_para_no_boundary` (`cor`)** | **12,379** | **+0.01114** | **`[-0.0111, +0.0321]`** | **0.3583** | **+0.373 pp** | **+0.00916** | **+0.316 pp** | **0.3713** |
| **Lag $d=2$** | `all_lines` | 28,281 | -0.01837 | `[-0.0347, -0.0043]` | 0.0100 | -0.415 pp | -0.01443 | -0.430 pp | — |
| **Lag $d=2$** | `same_paragraph` | 12,378 | -0.04530 | `[-0.0754, -0.0156]` | 0.0050 | -1.194 pp | -0.02287 | -1.202 pp | — |
| **Lag $d=2$** | **`same_para_no_boundary` (`cor`)** | **6,990** | **+0.02141** | **`[-0.0101, +0.0509]`** | **0.1854** | **+0.232 pp** | **+0.02271** | **+0.157 pp** | — |
| **Lag $d=3$** | `all_lines` | 24,779 | -0.01724 | `[-0.0343, -0.0026]` | 0.0355 | -0.133 pp | -0.01049 | -0.192 pp | — |
| **Lag $d=3$** | `same_paragraph` | 6,991 | -0.00939 | `[-0.0513, +0.0304]` | 0.6667 | +0.032 pp | -0.00722 | -0.690 pp | 0.6847 |
| **Lag $d=3$** | **`same_para_no_boundary` (`cor`)** | **4,439** | **+0.03577** | **`[-0.0071, +0.0812]`** | **0.1184** | **+0.039 pp** | **+0.02670** | **-0.091 pp** | **0.1414** |
| **Window $w=2$** | `all_lines` | 28,283 | -0.01045 | `[-0.0206, -0.0006]` | 0.0460 | -0.300 pp | -0.01003 | -0.475 pp | — |
| **Window $w=2$** | `same_paragraph` | 12,380 | -0.00866 | `[-0.0295, +0.0114]` | 0.3808 | -0.258 pp | -0.01032 | -0.450 pp | — |
| **Window $w=2$** | **`same_para_no_boundary` (`cor`)** | **6,992** | **+0.02044** | **`[-0.0009, +0.0433]`** | **0.0665** | **+0.549 pp** | **+0.01108** | **+0.374 pp** | — |
| **Window $w=3$** | `all_lines` | 24,780 | -0.00583 | `[-0.0146, +0.0043]` | 0.2079 | -0.374 pp | -0.00587 | -0.481 pp | — |
| **Window $w=3$** | `same_paragraph` | 6,992 | +0.01383 | `[-0.0043, +0.0326]` | 0.1704 | +0.235 pp | +0.00844 | +0.174 pp | 0.3388 |
| **Window $w=3$** | **`same_para_no_boundary` (`cor`)** | **4,440** | **+0.02297** | **`[+0.0019, +0.0484]`** | **0.0485** | **+0.224 pp** | **+0.02103** | **+0.703 pp** | **0.0490** |
| **Within-Line $w=1$** | `interior_words` | 18,717 | **-0.00257** | `[-0.0186, +0.0145]` | **0.7626** | **-0.118 pp** | **-0.00037** | **-0.053 pp** | **0.9675** |
| **Within-Line $w=2$** | `interior_words` | 11,724 | **+0.02098** | `[-0.0016, +0.0412]` | **0.0850** | **+0.205 pp** | **+0.01953** | **+0.316 pp** | **0.0505** |
| **Within-Line $w=3$** | `interior_words` | 6,060 | **+0.01436** | `[-0.0205, +0.0527]` | **0.4613** | **+0.182 pp** | **+0.00644** | **+0.083 pp** | **0.6922** |

### 3.3 Interpretation of the Asymmetry Test
1. **Why `all_lines` and `same_paragraph` Show Forward > Backward Similarity ($\Delta E_{\min} < 0$)**:
   - In `same_paragraph` at lag $d = 1$ ($N = 23,529$), a token in line 2 of a paragraph compares line 1 (`pfirst`, above it) against line 3 (an interior body line, below it). Because paragraph-opening lines (`pfirst`) are marked by top-line gallows (`p/f`) and specialized header vocabulary (Attack 209), line 2 is significantly *more divergent* from line 1 above it than from line 3 below it ($\Delta E_{\min} = -0.0499$ edits, $\Delta P_{\le 1} = -1.51\text{ pp}$, $p = 0.0005$).
2. **Complete Symmetry Inside Paragraph Interiors (`cor`)**:
   - When paragraph-boundary lines (`pfirst` and `plast`) are removed (`same_paragraph_no_boundary_lines`, $N = 12,379$), the lag-1 difference between looking 1 line *up* ($i-1$) and 1 line *down* ($i+1$) is **+0.0111 edits** ($p = 0.358$) and **+0.373 pp** on $\le 1$-edit matches ($p = 0.369$)—a complete statistical null.
   - Similarly, within the same line (`within_line_interior`), comparing a word to its $w = 1, 2, 3$ interior neighbors on the left vs. the right yields no significant asymmetry ($p = 0.763$ at $w=1$, $p = 0.085$ at $w=2$, $p = 0.461$ at $w=3$).

---

## 4. Test 3: Vertical Alignment Test (Horizontal Coordinate `x_rel` at Lag 1 vs. Lags 2–5 and Cross-Folio)

### 4.1 Methodology
If scribes generated words in line $i$ by looking directly upward at the word immediately above in line $i-1$ and modifying it, then the nearest-neighbor word(s) $S \subset L_{i-1}$ should sit at nearly the same relative horizontal coordinate $x_{\text{rel}} \in [0, 1]$ as the target word, **specifically at lag 1** and **even for line-interior words**.

For each token at relative position $x$ (measured both by character center `char_centre` and normalized word slot `word_index`), [`tools/attack239_self_citation_autocopy.py`](../tools/attack239_self_citation_autocopy.py) computes:
- $\text{obs} = \frac{1}{|S|} \sum_{q \in S} |x - x'_q|$ (mean horizontal displacement to the best-matching word(s) in the comparison line).
- $\text{exp} = \frac{1}{|\text{idx}|} \sum_{q \in \text{idx}} |x - x'_q|$ (exact expected displacement under random permutation of candidate word positions within that line).
- $\text{obs} - \text{exp} < 0$ indicates horizontal alignment stronger than random within-line word order.

Critically, we evaluate two variants across lags $d = 1..5$ and `cross_folio_matched` (`X`):
- **`all`**: all clean tokens and all candidate slots in the comparison line (which includes line-initial $k=0$ and line-final $k=n-1$ words).
- **`strict`**: restricts both the target token and candidate tokens to **line-interior words (`0 < k < n - 1`)** and requires a **close match ($d_{\text{Lev}} \le 1$)**. This isolates true 0/1-edit copying from line-initial and line-final morphological framing.

### 4.2 Vertical Alignment Results

#### Table 3A: Horizontal Displacement (`obs_minus_expected`) Across Lags 1–5 and Cross-Folio Lines

| Comparison Line | Variant | Position Metric | `eva_chars` $N$ | `eva_chars` Mean Obs $|\Delta x|$ | `eva_chars` Expected $|\Delta x|$ | `eva_chars` `obs - exp` (95% CI) | `units` $N$ | `units` `obs - exp` (95% CI) |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Lag 1 ($i-1$)** | `all` | `char_centre` | 32,797 | 0.32580 | 0.33958 | **-0.01378** (`[-0.01590, -0.01164]`) | 32,719 | **-0.01474** (`[-0.01700, -0.01262]`) |
| **Lag 2 ($i-2$)** | `all` | `char_centre` | 30,836 | 0.32508 | 0.33952 | **-0.01444** (`[-0.01647, -0.01247]`) | 30,757 | **-0.01461** |
| **Lag 3 ($i-3$)** | `all` | `char_centre` | 29,048 | 0.32145 | 0.33936 | **-0.01791** (`[-0.02020, -0.01560]`) | 28,958 | **-0.01740** |
| **Lag 4 ($i-4$)** | `all` | `char_centre` | 27,332 | 0.32380 | 0.33958 | **-0.01579** (`[-0.01818, -0.01337]`) | 27,251 | **-0.01576** |
| **Lag 5 ($i-5$)** | `all` | `char_centre` | 25,669 | 0.32144 | 0.33950 | **-0.01806** (`[-0.02015, -0.01565]`) | 25,602 | **-0.01786** |
| **Cross-Folio (`X`)** | `all` | `char_centre` | 32,804 | 0.32990 | 0.33981 | **-0.00991** (`[-0.01190, -0.00787]`) | 32,693 | **-0.01071** (`[-0.01299, -0.00864]`) |
| **Lag 1 ($i-1$)** | **`strict`** | `char_centre` | **6,239** | **0.26860** | **0.27207** | **-0.00347** (**`[-0.00775, +0.00102]`**) | **7,403** | **-0.00319** (**`[-0.00735, +0.00088]`**) |
| **Lag 1 ($i-1$)** | **`strict`** | `word_index` | **6,239** | **0.25845** | **0.26200** | **-0.00355** (**`[-0.00738, +0.00025]`**) | **7,403** | **-0.00357** (**`[-0.00740, +0.00043]`**) |
| **Lag 2 ($i-2$)** | `strict` | `char_centre` | 5,443 | 0.25954 | 0.27028 | -0.01074 (`[-0.01542, -0.00605]`) | 6,435 | -0.00996 |
| **Lag 3 ($i-3$)** | `strict` | `char_centre` | 5,162 | 0.26413 | 0.27229 | -0.00816 (`[-0.01239, -0.00397]`) | 6,103 | -0.00704 |
| **Lag 4 ($i-4$)** | `strict` | `char_centre` | 4,600 | 0.26904 | 0.27238 | -0.00333 (`[-0.00810, +0.00136]`) | 5,518 | -0.00311 |
| **Lag 5 ($i-5$)** | `strict` | `char_centre` | 4,391 | 0.26537 | 0.27104 | -0.00568 (`[-0.01154, -0.00044]`) | 5,180 | -0.00596 |
| **Cross-Folio (`X`)** | **`strict`** | `char_centre` | **4,630** | **0.27510** | **0.27495** | **+0.00015** (**`[-0.00461, +0.00478]`**) | **5,580** | **-0.00042** (**`[-0.00469, +0.00393]`**) |

### 4.3 Why the Vertical Alignment Test Refutes "Glancing at the Line Above"
Table 3A exposes three decisive facts that falsify mechanical vertical copying from line $i-1$:
1. **Unrestricted Alignment (`all`) Is Driven by Manuscript-Wide Line-Boundary Morphology**:
   - When line-initial and line-final tokens are included (`all`), even a line from a **different folio** (`cross_folio_matched`) shows strong horizontal alignment (`obs - exp = -0.00991` in `eva_chars`, `-0.01071` in `units`—over **72%** of the lag-1 value!). This happens because Voynich lines act as prosodic/syntactic units (Attacks 207 & 210) with dedicated line-initial words (`daiin`, `saiin`, `y-`, `o-`) and line-final closers (`-am`, `-oly`, `-ody`).
2. **Strict Interior $\le 1$-Edit Alignment at Lag 1 Is Statistically Zero**:
   - Once line-initial and line-final boundary words are excluded and we look specifically at $\le 1$-edit matches (`strict`), lag-1 horizontal alignment drops by **75%** to `-0.00347` (95% CI `[-0.00775, +0.00102]`) in `eva_chars` and `-0.00319` (95% CI `[-0.00735, +0.00088]`) in `units`—a displacement of **less than 0.35% of a line width**, with 95% confidence intervals spanning zero on both `char_centre` and `word_index`.
3. **Lag 1 Is Actually *Less* Vertically Aligned Than Lags 2–5**:
   - Under both `all` and `strict`, the horizontal alignment at lag 1 is **weaker** than the average across lags 2–5 (`lag1_minus_lag2to5 = +0.00270`, 95% CI `[+0.00075, +0.00518]` on `all`; `+0.00372`, 95% CI `[-0.00136, +0.00823]` on `strict`). A scribe copying visually from the line directly above cannot align *better* with lines 2 to 5 lines higher up the page than with the line immediately above his pen.
4. **Empirical Examples of Unaligned Lag-1 1-Edit Pairs**:
   - Inspecting the sampled interior 1-edit pairs from [`data/attack239_self_citation_autocopy.json`](../data/attack239_self_citation_autocopy.json) confirms that 1-edit neighbors in line $i-1$ occur at arbitrary horizontal word positions (`pos` vs. `above_pos`):
     - `f10r.7` (`pos=6`, `cth`) vs. `f10r.6` (`above_pos=1`, `cthy`)
     - `f32v.8` (`pos=2`, `daiin`) vs. `f32v.7` (`above_pos=6`, `dain`)
     - `f33r.7` (`pos=2`, `aiin`) vs. `f33r.6` (`above_pos=7`, `daiin`)
     - `f46r.12` (`pos=10`, `chdy`) vs. `f46r.11` (`above_pos=4`, `shdy`)
     - `f55v.11` (`pos=7`, `or`) vs. `f55v.10` (`above_pos=1`, `ol`)
     - `f75r.17` (`pos=7`, `shedy`) vs. `f75r.16` (`above_pos=2`, `sheedy`)
     - `f76v.4` (`pos=1`, `sor`) vs. `f76v.3` (`above_pos=7`, `ror`)

---

## 5. Test 4: Stratification by Currier Language (`A` vs `B`), Scribe Hand (`$H=1..5`), and Section (`$I`)

### 5.1 Comprehensive Stratified Summary (`effects_by_group`)

#### Table 4A: Stratified Lag-1 Similarity, Null Excesses, Asymmetry, and Strict Alignment (`eva_chars`)

| Stratum Group | Folios | Tokens | Obs Lag-1 $\le 1$ Edit | Shuf (`sh`) $\le 1$ Edit | Para-Shuf (`ps`) $\le 1$ Edit | Cross (`cr`) $\le 1$ Edit | Excess `ob - sh` ($z$-score) | Excess `ob - ps` ($z$-score) | Folio Topic `sh - cr` | Core Asym $\Delta E_{\min}$ ($p$-val) | Strict Align `obs - exp` (95% CI) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **All (`all`)** | 207 | 34,780 | **25.55%** | 21.73% | 23.18% | 19.27% | **+3.82 pp** ($17.09$) | **+2.38 pp** ($11.88$) | +2.46 pp | +0.0111 ($0.375$) | -0.00347 (`[-0.0073, +0.0005]`) |
| **Lang A (`L:A`)** | 114 | 11,194 | **22.87%** | 19.87% | 20.43% | 17.86% | **+3.00 pp** ($8.75$) | **+2.44 pp** ($7.66$) | +2.01 pp | -0.0144 ($0.459$) | -0.00840 (`[-0.0162, +0.0003]`) |
| **Lang B (`L:B`)** | 83 | 23,039 | **26.99%** | 22.79% | 24.65% | 20.04% | **+4.19 pp** ($15.34$) | **+2.34 pp** ($10.05$) | +2.76 pp | +0.0240 ($0.119$) | -0.00152 (`[-0.0071, +0.0039]`) |
| **Hand 1 (`H:1`)** | 112 | 10,447 | **23.16%** | 20.13% | 20.64% | 18.10% | **+3.03 pp** ($8.37$) | **+2.52 pp** ($8.24$) | +2.03 pp | -0.0040 ($0.822$) | -0.00746 (`[-0.0154, +0.0016]`) |
| **Hand 2 (`H:2`)** | 46 | 10,779 | **31.41%** | 25.57% | 27.63% | 23.66% | **+5.83 pp** ($15.21$) | **+3.78 pp** ($10.96$) | +1.92 pp | +0.0157 ($0.341$) | +0.00317 (`[-0.0032, +0.0100]`) |
| **Hand 3 (`H:3`)** | 31 | 11,685 | **23.27%** | 20.44% | 22.15% | 17.03% | **+2.83 pp** ($7.46$) | **+1.12 pp** ($3.60$) | +3.40 pp | +0.0277 ($0.437$) | -0.00740 (`[-0.0152, -0.0002]`) |
| **Hand 4 (`H:4`)** | 10 | 539 | **15.13%** | 11.81% | 13.35% | 12.94% | **+3.32 pp** ($2.64$) | **+1.79 pp** ($1.78$) | -1.13 pp | +0.1644 ($0.254$) | -0.02047 (`[-0.0801, +0.0342]`) |
| **Hand 5 (`H:5`)** | 7 | 871 | **19.63%** | 17.27% | 18.06% | 14.04% | **+2.36 pp** ($1.96$) | **+1.56 pp** ($1.32$) | +3.23 pp | +0.0038 ($0.989$) | -0.01007 (`[-0.0660, +0.0445]`) |
| **Herbal (`I:H`)** | 128 | 11,436 | **22.80%** | 19.41% | 19.90% | 17.62% | **+3.38 pp** ($9.61$) | **+2.89 pp** ($8.24$) | +1.79 pp | +0.0094 ($0.630$) | -0.00286 (`[-0.0115, +0.0058]`) |
| **Stars/Rec (`I:S`)** | 25 | 11,567 | **23.34%** | 20.51% | 22.22% | 17.01% | **+2.83 pp** ($7.56$) | **+1.12 pp** ($3.48$) | +3.51 pp | +0.0215 ($0.556$) | -0.00732 (`[-0.0142, -0.0010]`) |
| **Biological (`I:B`)** | 19 | 6,226 | **33.71%** | 27.37% | 30.22% | 25.38% | **+6.34 pp** ($11.37$) | **+3.48 pp** ($6.35$) | +1.98 pp | +0.0006 ($0.968$) | +0.00217 (`[-0.0058, +0.0101]`) |
| **Pharma (`I:P`)** | 16 | 2,302 | **28.78%** | 25.07% | 26.11% | 23.24% | **+3.71 pp** ($4.01$) | **+2.67 pp** ($3.55$) | +1.83 pp | -0.0025 ($0.975$) | -0.00542 (`[-0.0194, +0.0073]`) |
| **Text/Cosm (`I:T`)** | 6 | 2,282 | **27.55%** | 23.47% | 24.37% | 20.06% | **+4.07 pp** ($4.30$) | **+3.18 pp** ($4.17$) | +3.41 pp | +0.0270 ($0.501$) | -0.00268 (`[-0.0289, +0.0178]`) |
| **Cosmo (`I:C`)** | 8 | 688 | **19.58%** | 15.35% | 17.71% | 15.89% | **+4.24 pp** ($3.30$) | **+1.87 pp** ($1.72$) | -0.55 pp | +0.0087 ($1.000$) | -0.01296 (`[-0.0508, +0.0108]`) |
| **Astro (`I:A`)** | 5 | 279 | **11.25%** | 9.71% | 10.39% | 9.58% | **+1.54 pp** ($0.87$) | **+0.86 pp** ($0.67$) | +0.13 pp | +0.5625 ($0.515$) | -0.00277 (`[-0.1276, +0.1130]`) |
| **`LHI:A1H`** | 95 | 7,938 | **21.48%** | 18.78% | 19.05% | 16.64% | **+2.70 pp** ($6.49$) | **+2.43 pp** ($6.84$) | +2.15 pp | -0.0073 ($0.702$) | -0.01038 (`[-0.0207, -0.0010]`) |
| **`LHI:A1P`** | 16 | 2,302 | **28.78%** | 25.07% | 26.11% | 23.24% | **+3.71 pp** ($4.01$) | **+2.67 pp** ($3.55$) | +1.83 pp | -0.0025 ($0.975$) | -0.00542 (`[-0.0197, +0.0070]`) |
| **`LHI:B2B`** | 19 | 6,226 | **33.71%** | 27.37% | 30.22% | 25.38% | **+6.34 pp** ($11.37$) | **+3.48 pp** ($6.35$) | +1.98 pp | +0.0006 ($0.975$) | +0.00217 (`[-0.0063, +0.0101]`) |
| **`LHI:B2H`** | 20 | 2,343 | **28.28%** | 22.30% | 23.22% | 22.19% | **+5.98 pp** ($6.79$) | **+5.06 pp** ($6.26$) | +0.11 pp | +0.0682 ($0.248$) | +0.01377 (`[+0.0006, +0.0309]`) |
| **`LHI:B2T`** | 4 | 1,782 | **29.99%** | 25.59% | 26.22% | 21.36% | **+4.40 pp** ($4.22$) | **+3.78 pp** ($4.20$) | +4.23 pp | +0.0265 ($0.630$) | -0.00437 (`[-0.0252, +0.0115]`) |
| **`LHI:B3S`** | 22 | 10,361 | **23.79%** | 20.88% | 22.65% | 17.24% | **+2.91 pp** ($7.61$) | **+1.14 pp** ($3.49$) | +3.64 pp | +0.0637 ($0.092$) | -0.00659 (`[-0.0132, +0.0009]`) |

#### Table 4B: Currier Language A vs. Language B under Collapsed EVA Units (`units`)

| Stratum Group | Folios | Tokens | Obs Lag-1 $\le 1$ Edit | Shuf (`sh`) $\le 1$ Edit | Para-Shuf (`ps`) $\le 1$ Edit | Cross (`cr`) $\le 1$ Edit | Excess `ob - sh` ($z$-score) | Excess `ob - ps` ($z$-score) | Folio Topic `sh - cr` | Core Asym $\Delta E_{\min}$ ($p$-val) | Strict Align `obs - exp` (95% CI) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **All (`all`)** | 207 | 34,780 | **30.30%** | 26.03% | 27.63% | 23.29% | **+4.26 pp** ($19.25$) | **+2.66 pp** ($13.78$) | +2.75 pp | +0.0092 ($0.384$) | -0.00319 (`[-0.0074, +0.0013]`) |
| **Lang A (`L:A`)** | 114 | 11,194 | **29.27%** | 25.29% | 25.97% | 23.25% | **+3.98 pp** ($10.80$) | **+3.30 pp** ($10.76$) | +2.03 pp | -0.0060 ($0.682$) | -0.00662 (`[-0.0153, +0.0022]`) |
| **Lang B (`L:B`)** | 83 | 23,039 | **31.01%** | 26.60% | 28.64% | 23.47% | **+4.41 pp** ($15.46$) | **+2.37 pp** ($9.34$) | +3.14 pp | +0.0168 ($0.221$) | -0.00177 (`[-0.0066, +0.0029]`) |

### 5.2 Key Stratified Insights
1. **Language A vs. Language B Convergence Under Paragraph Control**:
   - In raw `eva_chars`, Language B appears to have a larger excess over folio-wide shuffled lines (`+4.19 pp`) than Language A (`+3.00 pp`).
   - However, once paragraph structure is controlled (`ob - ps`), **Language A (`+2.44 pp`) and Language B (`+2.34 pp`) have virtually identical within-paragraph lag-1 clustering** (and in collapsed `units`, Language A is actually *higher* than Language B: `+3.30 pp` vs. `+2.37 pp`)!
   - Why? Because Language B folios (`B2B` Biological and `B3S` Stars/Recipes) contain many separate paragraphs per page, so shuffling lines across the entire folio (`sh`) destroys paragraph-level topic clusters (`ps - sh = +1.85 pp` in `L:B` vs. `+0.56 pp` in `L:A`).
2. **Scribe 2 (`H:2`, `B2B` / `B2H`) vs. Scribe 3 (`H:3`, `B3S`)**:
   - **Scribe 2 (`H:2`)** exhibits the highest baseline morphological density (`31.41%` observed $\le 1$-edit at lag 1; `33.71%` in `B2B` Biological) and the strongest within-paragraph line-to-line clustering (`ob - ps = +3.78 pp`, reaching `+5.06 pp` in `B2H`). Yet Scribe 2 shows **zero** core backward/forward asymmetry (`p = 0.341` in `H:2`, `p = 0.968` in `I:B`) and **slightly positive (anti-aligned)** strict vertical displacement (`+0.00317` in `H:2`, `+0.01377` in `B2H`).
   - **Scribe 3 (`H:3` / `B3S` Recipes)** shows a large folio-topic effect (`sh - cr = +3.64 pp`) and a large paragraph-clustering effect (`ps - sh = +1.77 pp`), but the smallest within-paragraph line-to-line excess among the major hands (`ob - ps = +1.14 pp`, $z = 3.49$). In short recipe paragraphs, vocabulary is tightly bound to the individual recipe paragraph rather than drifting across lines.

---

## 6. Synthesis: What Supports vs. What Refutes Mechanical Self-Citation

| Empirical Criterion | Prediction of Mechanical Autocopying (Timm & Schinner 2019/2020) | Prediction of Topical / Paradigmatic Text Structure | Observed Voynich Manuscript Result (Attack 239) | Verdict |
| :--- | :--- | :--- | :--- | :---: |
| **1. Multi-line 1-edit neighborhood (`window_k = 10`)** | High match rate (~70%) is unique to the local preceding window on the same folio. | High match rate is mostly a global property of the compact prefix–stem–suffix grammar. | **69.50%** observed (`74.41%` in `units`), but **65.35%** (`70.41%` in `units`) in 10 lines from **different folios of the same stratum** (**94% global**). | **Refutes Autocopying** |
| **2. Single-lag excess & distance decay ($d = 1..10$)** | Similarity decays with lag $d$ relative to shuffled lines. | Similarity clusters by folio (`sh - cr`), paragraph (`ps - sh`), and local 1–3 line topic horizon (`ob - ps`). | Total lag-1 excess (`+6.28 pp`) splits into **39.2% folio topic**, **23.0% paragraph**, and **37.8% (`+2.38 pp`) local 1–3 line proximity** ($p < 0.01$). | **Consistent with Both (38% Local)** |
| **3. Causal Direction / Time-Reversal (`bwd` vs. `fwd`)** | Words are copied from earlier lines, or boundary asymmetries reflect sequential generation. | Interior lines are time-reversible ($\Delta E_{\min} \approx 0$); apparent asymmetry comes from `pfirst` header lines and `plast` short lines. | Raw asymmetry reverses on `same_paragraph` ($\Delta E_{\min} = -0.0499$, $p=0.0005$ due to `pfirst` headers) and **vanishes in paragraph interiors (`cor`)** ($\Delta E_{\min} = +0.0111$, $p = 0.358$). | **Supports Structural / Paragraph Model** |
| **4. Vertical Alignment to Line $i-1$ (`x_rel`)** | Strong horizontal alignment at lag 1 (`obs < exp`), persisting on interior $\le 1$-edit pairs and strongest at lag 1. | Apparent alignment is an artifact of line-initial/final slot grammar; interior $\le 1$-edit alignment at lag 1 is null and no stronger than lags 2–5. | **72% of `all` alignment occurs across different folios (`-0.00991`)**; **Lag 1 is weaker than Lags 2–5**; **`strict` interior $\le 1$-edit alignment at Lag 1 is zero** (`-0.00347`, 95% CI `[-0.0078, +0.0010]`). | **Decisively Refutes Vertical Autocopying** |
| **5. Scribe & Section Stratification (`$L, $H, $I`)** | Uniform mechanical copying process across the manuscript. | Varies systematically with paragraph length and section genre (`B2B` balneological prose vs. `B3S` short recipes). | Within-paragraph clustering is identical in `L:A` (`+2.44 pp`) and `L:B` (`+2.34 pp`), peaks in continuous `H:2` prose (`+3.78 pp`), and drops in short `B3S` recipes (`+1.14 pp`). | **Supports Genre / Discourse Clustering** |

### Final Conclusion
Timm & Schinner's empirical observation that similar Voynich words cluster within a few lines of one another is **real** (`+2.38 pp` to `+2.66 pp` within-paragraph lag-1 excess, $z = 11.88\text{–}13.78$), but their proposed **generative mechanism**—that scribes fabricated meaningless text by glancing vertically at the line above (`lag 1`, same `x_rel`) and mutating words—**fails three independent controls**:
1. **94% of the 10-line cumulative $\le 1$-edit match rate** (`65.35% / 69.50%` in `eva_chars`, `70.41% / 74.41%` in `units`) is already present in random lines from *different folios* of the same language, hand, and section.
2. **62% of the remaining lag-1 excess** (`39.2%` folio-wide + `23.0%` paragraph-wide) is static folio-level and paragraph-level vocabulary selection.
3. Most decisively, **interior $\le 1$-edit neighbors in line $i-1$ show zero horizontal alignment** (`obs - exp = -0.00347`, 95% CI `[-0.00775, +0.00102]`), and **lag 1 is less horizontally aligned than lags 2–5**. The residual 1–3 line clustering within paragraphs is completely symmetric in time (`cor` sign-flip $p = 0.358$) and horizontally unanchored—characteristic of local topical/paradigmatic repetition (repeating or inflecting the active plant part, liquid medium, or processing verb across adjacent clauses) rather than mechanical visual autocopying from the line above.
