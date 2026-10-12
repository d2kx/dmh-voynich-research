# Voynich Manuscript Research (`Beinecke MS 408`)

A visual, computational, and linguistic investigation of the **Voynich Manuscript**, built directly from two complete digital scans of the codex and four cross-checked machine-readable transliterations (`38,409` word tokens across `226` folios).

> **Want to jump straight into reading pages and decoding words in plain English?**
> - **[Plain-English Visual Reader's Guide](notes/PLAIN_ENGLISH_VISUAL_READERS_GUIDE.md)** — A jargon-free walkthrough of 8 iconic pages with high-resolution scans and a **3-Step "Lego" Cheat Sheet** for reading any Voynich word.
> - **[Visual Botanical & Astrological Identification Dossier](notes/VISUAL_BOTANICAL_AND_ASTRO_IDENTIFICATIONS.md)** — Matches 10 flagship plant paintings, apothecary jars, and star clusters (`f1v` Belladonna, `f9v` Heartsease, `f68r3` the Pleiades = `doaro`, `f102v2/f116v` Blood-Red Alkanet Root = `oror`) to concrete 15th-century European herbal and astronomical sources.
> - **[Interactive Local HTML Explorer (`explorer/index.html`)](explorer/index.html)** — Open `explorer/index.html` directly in any web browser (no server needed) to click through manuscript scans, decode any Voynich word into `Prefix + Root Stem + Suffix`, and browse the botanical and grammatical dictionaries.

---

## 1. What Have We Actually Learned? (The Plain-English Summary)

When you look at a Voynich page for the first time, it looks like an impenetrable wall of alien words. Our investigation shows why—and how to read through it:

1. **Every Voynich Word Is Built Like a 3-Part "Lego Block" (`Prefix + Root Stem + Suffix`)**
   - Once you peel off the **grammatical prefix on the left** (`o-` *"the"*, `qo-` *"then/and-it"*, `d-` *"take/from"*, `ol-` *"in the vessel/bath"*) and the **inflectional suffix on the right** (`-edy` *"boil/wash/steep"*, `-ol/-or` *"in the liquid/oil"*, `-aiin` *"one measured dose"*, `-am` *"complete/stop"*), thousands of scary-looking strings collapse into **~200 recurring Root Stems**.
   - **Example:** In the Bathing and Recipe sections, `qokeedy` (`qo-` *"then"* + `ke` *"boil/heat"* + `-edy` *"active process"*) means *"then boil/decoct it!"*, while `shedy` (`sh-` + `-edy`) means *"wash/bathe!"*.

2. **The Book Is a 15th-Century Illustrated Medical, Astrological & Apothecary Compendium**
   - **Herbal (`f1r–f57v`)**: Illustrated plant monographs showing whole living plants in the ground and describing their primary liquid extracts (`chol`) and root bases (`otar`, `kor`).
   - **Astronomical & Zodiac (`f67r–f73v`)**: A 360-degree celestial calendar (`10` Zodiac wheels ringed by `30` star-nymphs each, plus astrolabe dials like `f68r3`) that schedules **when** to harvest or administer specific herbal essences.
   - **Balneological / Medical Bathing (`f75r–f84v`)**: Opened by the pure-text master treatise **`f76r`** (keyed by marginal index letters `s, d, q, s, o, l`), instructing how herbal decoctions are boiled (`qokeedy`) and piped into immersion pools (`ol`, `shedy`).
   - **Pharmaceutical Jars (`f88r–f102v`)**: The apothecary's workbench—showing painted storage jars (`okol`, `otol`) on the left alongside **cut-up pieces of roots (`darary`, `okar`, `orar`) and leaves/seeds (`osal`, `okal`)** with single-word labels written directly over each plant part, followed by the compounding recipes underneath.
   - **Starred Master Recipes (`f103r–f116r`)**: Over `300` star-bulleted (`*`) step-by-step compound prescriptions (`Take ingredient -> Boil/Steep -> Measure dose -> Seal/Apply`).

3. **Concrete Visual & Bilingual "Rosetta" Anchors**
   - **Blood-Red Alkanet Root (`oror` on `f102v2` & `f116v`)**: The final page of the manuscript (`f116v`) contains a 3-line European charm (`...so nim gas mich oror`) that ends with the Voynich word **`oror`** right below a crimson-red paint blot. Searching the Pharmaceutical section reveals **`oror`** on **`f102v2`** labeling a plant with a vivid **blood-red root**—Dyer's Alkanet (*Alkanna tinctoria*) / Madder (*Rubia tinctorum*).
   - **The Pleiades Seven-Star Cluster (`doaro` on `f68r3`)**: On the four-quadrant Moon wheel `f68r3`, a tight cluster of **7 stars** in the upper-left quadrant is directly captioned **`doaro`** (the Pleiades in Taurus).
   - **Dissected Root Parts (`darary` & `okar` on `f89r2`)**: Single-word labels written directly over painted taproots and bulbs visually anchor the `-ra-/-rar-` (*main root*) and `-kar-/-kor-` (*root-heart/bulb*) stems.

![Folio f89r2 Apothecary Jar and Labeled Roots](pages/f89r2_full_enh.png)

---

## 2. Repository Structure

The repository is organized cleanly so that scans, human-readable guides, machine-readable data, and reproducible scripts each live in their own folder:

```text
voynich/
├── books/                  # Full manuscript PDF scans (stored via Git LFS)
│   ├── voynich-yale-beinecke-2026-highres-214p.pdf   # High-res Yale Beinecke export (~1500x2000 px, 214 pages incl. book edges)
│   └── voynich-tcpdf-2014-bookmarked-210p.pdf        # Bookmarked TCPDF edition (~1082x1500 px, 210 pages with folio TOC)
├── explorer/               # Self-contained local HTML interactive explorer
│   └── index.html          # Open in any browser to inspect scans, decode words & browse cribs
├── notes/                  # Human-readable visual guides, translations & thematic syntheses
│   ├── PLAIN_ENGLISH_VISUAL_READERS_GUIDE.md         # Start here: 3-step word guide + 8 visual page walkthroughs
│   ├── VISUAL_BOTANICAL_AND_ASTRO_IDENTIFICATIONS.md # 10 botanical, astronomical & apothecary identifications
│   ├── EIGHT_CASE_PARADIGM_AND_PARAGRAPH_STATE_COMPILER.md
│   ├── F76R_BALNEO_TREATISE_AND_6INDEX_COMPILER_COMPENDIUM.md
│   └── DECODING_ATTACKS_SYNTHESIS.md                 # Master index of all 152 computational & visual attacks
├── pages/                  # High-resolution extracted & contrast-enhanced folio scans (.png)
├── data/                   # EVA transliterations (ZL3b-n.txt, etc.), folio_index.json & JSON outputs
├── tools/                  # Python scripts for rendering scans, building the explorer & running analyses
├── NOTES.md                # Complete chronological research log (Discoveries 1–169+)
└── AGENTS.md               # Workspace continuity & contributor guidelines
```

### How the Two PDF Books in `books/` Differ
| File in `books/` | Pages | Resolution | Best Used For |
| :--- | :---: | :---: | :--- |
| **[`books/voynich-yale-beinecke-2026-highres-214p.pdf`](books/voynich-yale-beinecke-2026-highres-214p.pdf)** | `214` | `~1500 × 2000 px` | **Primary visual forensics:** 2× sharper pixel density, printed Beinecke Image IDs (`1006076`…`1006283`), and 4 physical fore-edge/spine scans (`p210–p213`). |
| **[`books/voynich-tcpdf-2014-bookmarked-210p.pdf`](books/voynich-tcpdf-2014-bookmarked-210p.pdf)** | `210` | `~1082 × 1500 px` | **Fast navigation:** Includes a 210-entry clickable PDF bookmark sidebar (`1r` through `116v`) that maps `1:1` to pages `1..209` of the Yale PDF. |

---

## 3. Recommended Reading & Exploration Path

1. **[`notes/PLAIN_ENGLISH_VISUAL_READERS_GUIDE.md`](notes/PLAIN_ENGLISH_VISUAL_READERS_GUIDE.md)** — Learn the 3-step `Prefix + Root + Suffix` system and read 8 iconic pages side-by-side with their scans.
2. **[`notes/VISUAL_BOTANICAL_AND_ASTRO_IDENTIFICATIONS.md`](notes/VISUAL_BOTANICAL_AND_ASTRO_IDENTIFICATIONS.md)** — See the 10 strongest botanical and astrological visual identifications (`f1v` Nightshade, `f2r` Cornflower, `f9v` Heartsease, `f16v` Palmate Hub, `f17r` Sarsaparilla/Bryony Vine, `f25v` Water-Lily, `f68r3` Pleiades, `f72r3` Zodiac Nymphs, `f89r2` Cut Roots, `f102v2/f116v` Blood-Red Alkanet).
3. **[`explorer/index.html`](explorer/index.html)** — Double-click or open in any browser to test any Voynich word in the interactive **3-Step Lego Word Analyzer** and click through page clauses.
4. **[`notes/EIGHT_CASE_PARADIGM_AND_PARAGRAPH_STATE_COMPILER.md`](notes/EIGHT_CASE_PARADIGM_AND_PARAGRAPH_STATE_COMPILER.md)** & **[`notes/F76R_BALNEO_TREATISE_AND_6INDEX_COMPILER_COMPENDIUM.md`](notes/F76R_BALNEO_TREATISE_AND_6INDEX_COMPILER_COMPENDIUM.md)** — Full grammatical tables, the 8-case inflectional paradigm, the 6-State recipe flowchart (`99.0%` forward monotonicity), and the complete line-by-line translation of the `f76r` Balneological treatise.
5. **[`NOTES.md`](NOTES.md)** — The complete, unabridged research log containing every visual observation, statistical test, negative result, and discovery (`1–169+`).

---

## 4. Quick CLI Toolkit Usage

All scripts use Python 3 with `pypdf`, `Pillow`, and `numpy`:

```bash
# Render any folio or high-contrast crop from the PDFs in books/
python tools/render_folio.py f17r --out pages/f17r_full.png
python tools/render_folio.py f116v --crop 0.15 0.08 0.85 0.35 --enhance --out pages/f116v_incantation_crop_enh.png

# Rebuild the master folio index, botanical dossier, or interactive HTML explorer
python tools/build_index.py
python tools/build_visual_botanical_astro_identifications.py
python tools/build_interactive_explorer.py
```
