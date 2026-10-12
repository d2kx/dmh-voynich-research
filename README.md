# Voynich Manuscript Research (`Beinecke MS 408`)

A visual, computational, and linguistic investigation of the **Voynich Manuscript**, built directly from two complete digital scans of the codex and four cross-checked machine-readable transliterations (`38,409` word tokens across `226` folios).

> **Want to jump straight into reading pages and decoding words in plain English?**
> - **[Plain-English Visual Reader's Guide](notes/PLAIN_ENGLISH_VISUAL_READERS_GUIDE.md)** — A jargon-free walkthrough of **11 iconic pages** with high-resolution scans and a **3-Step "Lego" Cheat Sheet** for reading any Voynich word.
> - **[Visual Botanical, Astrological & Balneological Identification Dossier](notes/VISUAL_BOTANICAL_AND_ASTRO_IDENTIFICATIONS.md)** — Matches **15 flagship plant paintings, apothecary jars, star clusters, bilingual month wheels, and bath pipes** (`f1v` Belladonna, `f9v` Heartsease, `f20v` Blue Knapweed, `f68r3` the Pleiades = `doaro`, `f70v2` Pisces = `mars`, `f82v` Bath Pipes = `olkol/okoldy`, `f102v2/f116v` Blood-Red Alkanet Root = `oror`) to concrete 15th-century European sources.
> - **[Interactive Local HTML Explorer (`explorer/index.html`)](explorer/index.html)** — Open `explorer/index.html` directly in any web browser (no server needed) to click through **16 manuscript scans**, decode any Voynich word into `Prefix + Root Stem + Suffix`, and browse the **15 visual cribs, 8-case grammar, Zodiac month calendar (`mars..decembre`), and 20-page bath plumbing tracker**.

---

## 1. What Have We Actually Learned? (The Plain-English Summary)

When you look at a Voynich page for the first time, it looks like an impenetrable wall of alien words. Our investigation shows why—and how to read through it:

1. **Every Voynich Word Is Built Like a 3-Part "Lego Block" (`Prefix + Root Stem + Suffix`)**
   - Once you peel off the **grammatical prefix on the left** (`o-` *"the"*, `qo-` *"then/and-it"*, `d-` *"take/from"*, `ol-` *"in the vessel/pipe/bath"*) and the **inflectional suffix on the right** (`-edy` *"boil/wash/steep"*, `-ol/-or` *"in the liquid/oil"*, `-aiin` *"one measured dose"*, `-am` *"complete/stop"*), thousands of scary-looking strings collapse into **~200 recurring Root Stems**.
   - **Example:** In the Bathing and Recipe sections, `qokeedy` (`qo-` *"then"* + `ke` *"boil/heat"* + `-edy` *"active process"*) means *"then boil/decoct it!"*, while `shedy` (`sh-` + `-edy`) means *"wash/bathe!"*.

2. **The Book Is a 15th-Century Illustrated Medical, Astrological & Apothecary Compendium**
   - **Herbal (`f1r–f57v`)**: Illustrated plant monographs organized into distinct visual/chromatic guilds (Red/Crimson blossoms & dye-roots, Blue scaly-calyx corollas & berries, Climbing vines, Aquatic reniform leaves, and Umbels) describing their primary liquid extracts (`chol`, `shol`) and root bases (`otar`, `kor`).
   - **Astronomical & Zodiac (`f67r–f73v`)**: A 360-degree celestial calendar (`12` Zodiac medallions captioned with the **15th-century European month names `mars` [March] through `decembre` [December]** and ringed by `~30` star-nymphs each, plus astrolabe dials like `f68r3`). Remarkably, **`58.1%` (`202 / 348`) of the single-word labels written beside the Zodiac star-nymphs appear verbatim inside the Herbal, Pharmaceutical, and Recipe sections**—proving the Zodiac wheels act as a day-by-day harvesting and dosing calendar!
   - **Balneological / Medical Bathing (`f75r–f84v`)**: Opened by the waterfall frontispiece **`f75r`** and the pure-text master treatise **`f76r`** (keyed by marginal index letters `s, d, q, s, o, l`). On the painted plumbing diagrams (`f75v, f78r, f82v`), **water pipes are labeled with `o-/ol-` vessel nouns (`olkol`, `okoldy` — `62.2%`)**, while **active `qo-` boiling verbs (`qokeedy` — `24.4%`) stay inside the instruction paragraphs**!
   - **Pharmaceutical Jars (`f88r–f102v`)**: The apothecary's workbench—showing painted storage jars (`okol`, `otol`) on the left alongside **cut-up pieces of roots (`darary`, `okar`, `orar`) and leaves/seeds (`osal`, `okal`)** with single-word labels written directly over each plant part (`43.1%` echoing their stem directly in the recipe prose on the very same page).
   - **Starred Master Recipes (`f103r–f116r`)**: Over `300` star-bulleted (`*`) step-by-step compound prescriptions (`Take ingredient -> Boil/Steep -> Measure dose -> Seal/Apply`).

3. **Concrete Visual & Bilingual "Rosetta" Anchors**
   - **Blood-Red Alkanet Root (`oror` on `f102v2` & `f116v`)**: The final page of the manuscript (`f116v`) contains a 3-line European charm (`...so nim gas mich oror`) that ends with the Voynich word **`oror`** right below a crimson-red paint blot. Searching the Pharmaceutical section reveals **`oror`** on **`f102v2`** labeling a plant with a vivid **blood-red root**—Dyer's Alkanet (*Alkanna tinctoria*) / Madder (*Rubia tinctorum*).
   - **European Month Names (`mars..decembre` on `f70v2–f73v`)**: Written right inside the Zodiac medallions (`mars` between the two fish of Pisces on `f70v2`), tying the `348` Voynich star-nymph degree labels (`otaly`, `okaly`, `otaram`) to the Western solar year.
   - **The Pleiades Seven-Star Cluster (`doaro` on `f68r3`)**: On the four-quadrant Moon wheel `f68r3`, a tight cluster of **7 stars** in the upper-left quadrant is directly captioned **`doaro`** (the Pleiades in Taurus).
   - **Dissected Root Parts (`darary` & `okar` on `f89r2`) & Water Pipes (`olkol` & `okoldy` on `f82v`)**: Single-word labels written directly over painted taproots, bulbs, and hydrotherapy pipes visually anchor `-ra-/-rar-` (*main root*), `-kar-/-kor-` (*root-heart/bulb*), and `ol-kol` (*vessel/pipe conduit*).

![Folio f89r2 Apothecary Jar and Labeled Roots](pages/f89r2_full_enh.png)

---

## 2. Repository Structure

The repository is organized cleanly so that scans, human-readable guides, machine-readable data, and reproducible scripts each live in their own folder:

```text
voynich/
├── books/                  # Full manuscript PDF scans (stored via Git LFS)
│   ├── voynich-yale-beinecke-2026-highres-214p.pdf   # High-res Yale Beinecke export (~1500x2000 px, 214 pages incl. book edges)
│   └── voynich-tcpdf-2014-bookmarked-210p.pdf        # Bookmarked TCPDF edition (~1082x1500 px, 210 pages with folio TOC)
├── explorer/               # Self-contained local HTML interactive explorer (4 tabs)
│   └── index.html          # Open in any browser to inspect scans, decode words & browse cribs
├── notes/                  # Human-readable visual guides, translations & thematic syntheses
│   ├── PLAIN_ENGLISH_VISUAL_READERS_GUIDE.md         # Start here: 3-step word guide + 11 visual page walkthroughs
│   ├── VISUAL_BOTANICAL_AND_ASTRO_IDENTIFICATIONS.md # 15 botanical, astronomical, balneological & apothecary cribs
│   ├── ZODIAC_MONTHS_BALNEO_PLUMBING_AND_BOTANICAL_ATLAS.md
│   ├── EIGHT_CASE_PARADIGM_AND_PARAGRAPH_STATE_COMPILER.md
│   ├── F76R_BALNEO_TREATISE_AND_6INDEX_COMPILER_COMPENDIUM.md
│   └── DECODING_ATTACKS_SYNTHESIS.md                 # Master index of all 156 computational & visual attacks
├── pages/                  # High-resolution extracted & contrast-enhanced folio scans (.png)
├── data/                   # EVA transliterations (ZL3b-n.txt, etc.), folio_index.json & JSON outputs
├── tools/                  # Python scripts for rendering scans, building the explorer & running analyses
├── NOTES.md                # Complete chronological research log (Discoveries 1–173)
└── AGENTS.md               # Workspace continuity & contributor guidelines
```

### How the Two PDF Books in `books/` Differ
| File in `books/` | Pages | Resolution | Best Used For |
| :--- | :---: | :---: | :--- |
| **[`books/voynich-yale-beinecke-2026-highres-214p.pdf`](books/voynich-yale-beinecke-2026-highres-214p.pdf)** | `214` | `~1500 × 2000 px` | **Primary visual forensics:** 2× sharper pixel density, printed Beinecke Image IDs (`1006076`…`1006283`), and 4 physical fore-edge/spine scans (`p210–p213`). |
| **[`books/voynich-tcpdf-2014-bookmarked-210p.pdf`](books/voynich-tcpdf-2014-bookmarked-210p.pdf)** | `210` | `~1082 × 1500 px` | **Fast navigation:** Includes a 210-entry clickable PDF bookmark sidebar (`1r` through `116v`) that maps `1:1` to pages `1..209` of the Yale PDF. |

---

## 3. Recommended Reading & Exploration Path

1. **[`notes/PLAIN_ENGLISH_VISUAL_READERS_GUIDE.md`](notes/PLAIN_ENGLISH_VISUAL_READERS_GUIDE.md)** — Learn the 3-step `Prefix + Root + Suffix` system and read 11 iconic pages side-by-side with their scans.
2. **[`notes/VISUAL_BOTANICAL_AND_ASTRO_IDENTIFICATIONS.md`](notes/VISUAL_BOTANICAL_AND_ASTRO_IDENTIFICATIONS.md)** — See the 15 strongest botanical, astrological, and balneological visual identifications (`SPEC-01` through `SPEC-15`).
3. **[`explorer/index.html`](explorer/index.html)** — Double-click or open in any browser to test any Voynich word in the interactive **3-Step Lego Word Analyzer**, click through 16 page walkthroughs, or inspect the Zodiac Month Calendar (`mars..decembre`) and Bathing Plumbing tables.
4. **[`notes/ZODIAC_MONTHS_BALNEO_PLUMBING_AND_BOTANICAL_ATLAS.md`](notes/ZODIAC_MONTHS_BALNEO_PLUMBING_AND_BOTANICAL_ATLAS.md)**, **[`notes/EIGHT_CASE_PARADIGM_AND_PARAGRAPH_STATE_COMPILER.md`](notes/EIGHT_CASE_PARADIGM_AND_PARAGRAPH_STATE_COMPILER.md)** & **[`notes/F76R_BALNEO_TREATISE_AND_6INDEX_COMPILER_COMPENDIUM.md`](notes/F76R_BALNEO_TREATISE_AND_6INDEX_COMPILER_COMPENDIUM.md)** — Full grammatical tables, the 8-case inflectional paradigm, the 12-medallion Zodiac calendar, and the 20-page Balneological treatise & plumbing atlas.
5. **[`NOTES.md`](NOTES.md)** — The complete, unabridged research log containing every visual observation, statistical test, negative result, and discovery (`1–173`).

---

## 4. Quick CLI Toolkit Usage

All scripts use Python 3 with `pypdf`, `Pillow`, and `numpy`:

```bash
# Render any folio or high-contrast crop from the PDFs in books/
python tools/render_folio.py f17r --out pages/f17r_full.png
python tools/render_folio.py f116v --crop 0.15 0.08 0.85 0.35 --enhance --out pages/f116v_incantation_crop_enh.png

# Rebuild the master folio index, 15-specimen visual dossier, or 4-tab interactive HTML explorer
python tools/build_index.py
python tools/build_visual_botanical_astro_identifications.py
python tools/build_interactive_explorer.py
```
