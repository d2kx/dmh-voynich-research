# Agent Instructions & Research Continuity Guide (`AGENTS.md`)

## 1. Mission & Intention
This repository (`voynich-research`) is an active, long-running research workspace dedicated to investigating the **Voynich Manuscript (Beinecke MS 408)**.

Our objective is to gain any genuine understanding—whether paleographic, codicological, visual, statistical, grammatical, or cryptographic— directly from:
1. **The two full manuscript PDF scans** in the root directory (`2002046.pdf` and `voynich-manuscript.pdf`), which can be cross-checked against each other for resolution, contrast, and physical fold-out details.
2. **Machine-readable EVA transliterations** in `data/` (`ZL3b-n.txt`, `RF1b-er.txt`, `IT2a-n.txt`, `GC2a-n.txt`), paired with our master cross-reference index `data/folio_index.json`.

While you are free to consult external literature or the web for context, **do not make summarizing past failed decipherment attempts your main objective**. Prioritize direct empirical observation, visual inspection of the scans, reproducible computational tests, and original hypothesis testing.

---

## 2. Living Research Log: `NOTES.md` (Mandatory Continuity Rule)
- **[`NOTES.md`](NOTES.md)** is the central, living research log for this project. It contains all visual forensics, cross-PDF comparisons, quantitative discoveries, and open questions established so far.
- **Read [`NOTES.md`](NOTES.md) first** at the beginning of any new research session before writing new scripts or re-running basic checks.
- **Update [`NOTES.md`](NOTES.md) frequently** as you explore further. Because deciphering or understanding the Voynich Manuscript is a long-running, open-ended goal where even small clues matter:
  - Record **every meaningful observation, visual anomaly, statistical pattern, or verified negative result**, even if it is not yet clear whether or how it will help down the line.
  - Keep all scripts in `tools/`, structured outputs in `data/`, and extracted/annotated image crops in `pages/` (or topic notes in `notes/`) so that future agents can immediately verify and build upon your work without starting from scratch.

---

## 3. Workspace Architecture & Existing Toolkit

### Root Assets
- `2002046.pdf`: 214-page Yale Digital Collections export (Aug 2026, ~1500×2000 px per folio, includes Beinecke Image IDs and 4 physical book-edge scans `p210–p213`).
- `voynich-manuscript.pdf`: 210-page TCPDF export (Feb 2014, ~1082×1500 px per folio, includes a 210-entry bookmark TOC; pages `1..209` align 1-to-1 with `2002046.pdf`).
- `NOTES.md`: Living research log of all findings, visual forensics, statistical experiments, and open avenues.
- `README.md`: Overview of the repository, toolkit, and key findings for GitHub.

### Data (`data/`)
- `data/folio_index.json`: Master index linking all 226 transcribed folios (`38,409` words, `892` figure labels, `754` drawing intrusions) to exact PDF page numbers, Beinecke Image IDs, manuscript sections (`$I`), Currier languages (`$L=A/B`), and Lisa Fagin Davis scribe hands (`$H=1..5`).
- `data/ZL3b-n.txt`: Zandbergen-Landini EVA transliteration (v3b, IVTFF 2.0 format) with rich metadata comments, paragraph markers (`<%>`, `<$>`), right-justified titles (`=Pt`), drawing intrusions (`<->`), and figure labels (`@L...`).
- `data/RF1b-er.txt`, `data/IT2a-n.txt`, `data/GC2a-n.txt`: Reference, Takahashi, and Glen Claston (`v101`) transliterations for cross-checking readings.
- `data/structural_analysis.json`, `data/q_and_label_analysis.json`, `data/deep_grammar_analysis.json`, `data/canonical_normalization_test.json`: Reproducible JSON outputs from our quantitative experiments.

### Tools (`tools/`)
- `python tools/build_index.py`: Rebuilds `data/folio_index.json` from both PDFs and `data/ZL3b-n.txt`.
- `python tools/render_folio.py <folio_or_page> [--crop x0 y0 x1 y1] [--enhance] [--compare] [--out pages/name.png]`:
  - Extracts the native embedded scan for any folio (e.g. `f1r`, `f99v`, `p181`), crops normalized `[0..1]` coordinates, applies multi-channel ink contrast enhancement (`--enhance`), or renders side-by-side comparisons between `2002046.pdf` and `voynich-manuscript.pdf` (`--compare`).
- `python tools/analyze_structure.py`: Runs positional morphology & Herbal-to-Pharmaceutical cross-reference analysis.
- `python tools/test_q_prefix_and_labels.py`: Tests the `q-` proclitic rule (`qoX = q + oX`) and label-to-paragraph matching.
- `python tools/deep_grammar_and_cipher_test.py`: Tests top-line gallows allography (`p/f` vs `t/k`), slot-grammar coverage, and block-level label matches.
- `python tools/test_unified_normalization.py`: Runs the 4-Rule Canonical Normalization and 1,000-trial permutation tests.

---

## 4. Guidelines for Future Agents
1. **Always Verify Visually on the Scans**: Whenever a statistical or transliteration pattern points to a specific folio or locus (e.g., a rare label match, a drawing intrusion `<->`, or marginalia), use `tools/render_folio.py` to extract and visually inspect the actual vellum scan. (As demonstrated on `f102r1` in [`NOTES.md`](NOTES.md), physical folds, tears, and bleed-through are only understood when you look at the recto and verso images together.)
2. **Control for Currier Language (`A` vs `B`) and Section (`$I`)**: The manuscript's vocabulary and suffix distributions shift sharply between Currier Language A and B and across the 5 scribe hands. Always stratify or permute within matching language/section buckets when computing null baselines.
3. **Log Everything**: Before ending a turn or completing a task, append your new findings, hypotheses tested, scripts added, and newly generated images to [`NOTES.md`](NOTES.md).
4. **Use Relative Paths in Repository Markdown Files**: When writing or editing markdown files inside the repository (`NOTES.md`, `README.md`, `AGENTS.md`, `notes/*.md`), always use **repository-relative paths** (e.g., `[2002046.pdf](2002046.pdf)`, `[tools/render_folio.py](tools/render_folio.py)`, `[pages/f99r_three_jars_enh.png](pages/f99r_three_jars_enh.png)`) rather than machine-specific `file:///c:/Users/...` URIs, so that all links work portably on GitHub and across any local clone.
