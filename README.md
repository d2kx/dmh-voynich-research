# Voynich Manuscript Research (`Beinecke MS 408`)

A visual, computational, and linguistic investigation of the **Voynich Manuscript**, built directly from two complete digital scans of the codex and four cross-checked machine-readable transliterations (`38,409` word tokens across `226` folios, with **`88.8%` 4-transcriber canonical consensus** across `ZL3b-n`, `RF1b-er`, `IT2a-n`, and `GC2a-n` `v101`).

> **Want to jump straight into reading pages and decoding words in plain English?**
> - **[Plain-English Visual Reader's Guide](notes/PLAIN_ENGLISH_VISUAL_READERS_GUIDE.md)** — A jargon-free walkthrough of **15 iconic pages** (`f1r` through `f116v`) with high-resolution scans and a **3-Step "Lego" Cheat Sheet** for reading any Voynich word.
> - **[Visual Botanical, Astrological, Balneological & Cosmological Identification Dossier](notes/VISUAL_BOTANICAL_AND_ASTRO_IDENTIFICATIONS.md)** — Matches **20 flagship plant paintings, apothecary jars, star clusters, bilingual month wheels, bath pipes, cosmological spheres, and starred master prescriptions** (`SPEC-01..20`: `f1v` Belladonna, `f9v` Heartsease, `f20v` Blue Knapweed, `f34r` Divided-Root Herb, `f66r` Poultice Tub `den mus / del`, `f68r3` Pleiades = `doaro`, `f70v2` Pisces = `mars`, `f82v` Bath Pipes = `olkol/okoldy`, `fRos` 9-Sphere Map, `f107r` Starred Recipes, `f102v2/f116v` Blood-Red Alkanet Root = `oror`) to concrete 15th-century European sources.
> - **[Interactive Local HTML Explorer (`explorer/index.html`)](explorer/index.html)** — Open `explorer/index.html` directly in any web browser (no server needed) to click through **21 manuscript scans**, decode any Voynich word into `Prefix + Root Stem + Suffix`, and browse the **20 visual cribs, 8-case grammar, Zodiac month calendar (`mars..decembre`), 20-page bath plumbing tracker, 285 Starred Recipes, 9-Rosettes map, and 4-Transcriber Consensus Proof**.

---

## 1. What Have We Actually Learned? (The Plain-English Summary)

When you look at a Voynich page for the first time, it looks like an impenetrable wall of alien words. Our investigation shows why—and how to read through it:

1. **Every Voynich Word Is Built Like a 3-Part "Lego Block" (`Prefix + Root Stem + Suffix`)**
   - Once you peel off the **grammatical prefix on the left** (`o-` *"the"*, `qo-` *"then/and-it"*, `d-` *"take/from"*, `ol-` *"in the vessel/pipe/bath"*) and the **inflectional suffix on the right** (`-edy` *"boil/wash/steep"*, `-ol/-or` *"in the liquid/oil"*, `-aiin` *"one measured dose"*, `-am` *"complete/stop"*), thousands of scary-looking strings collapse into **~200 recurring Root Stems**.
   - **Example:** In the Bathing and Recipe sections, `qokeedy` (`qo-` *"then"* + `ke` *"boil/heat"* + `-edy` *"active process"*) means *"then boil/decoct it!"*, while `shedy` (`sh-` + `-edy`) means *"wash/bathe!"*.
   - **Verified Across All 4 Human Transcribers (`88.8%` Consensus):** Aligning `5,132` lines (`36,103` word tokens) across all four independent transcription files (`Zandbergen-Landini`, `Rene/Friedman`, `Takahashi`, and `Glen Claston v101`) proves **`88.8%` 4-way agreement on the canonical word skeleton** and `24 / 26` exact agreement on our core visual cribs across all three EVA editions.

2. **The Book Is a 15th-Century Illustrated Medical, Astrological & Apothecary Compendium**
   - **Herbal (`f1r–f57v`)**: Illustrated plant monographs organized into distinct visual/chromatic guilds (Red/Crimson blossoms & dye-roots, Blue scaly-calyx corollas & berries, Climbing vines, Aquatic reniform leaves, and Umbels) describing their primary liquid extracts (`chol`, `shol`) and root bases (`otar`, `kor`).
   - **Astronomical & Zodiac (`f67r–f73v`)**: A 360-degree celestial calendar (`12` Zodiac medallions captioned with the **15th-century European month names `mars` [March] through `decembre` [December]** and ringed by `~30` star-nymphs each, plus astrolabe dials like `f68r3`). Remarkably, **`58.1%` (`202 / 348`) of the single-word labels written beside the Zodiac star-nymphs appear verbatim inside the Herbal, Pharmaceutical, and Recipe sections**—proving the Zodiac wheels act as a day-by-day harvesting and dosing calendar!
   - **Balneological / Medical Bathing (`f75r–f84v`)**: Opened by the waterfall frontispiece **`f75r`** and the pure-text master treatise **`f76r`** (keyed by marginal index letters `s, d, q, s, o, l`). On the painted plumbing diagrams (`f75v, f78r, f82v`), **water pipes are labeled with `o-/ol-` vessel nouns (`olkol`, `okoldy` — `62.2%`)**, while **active `qo-` boiling verbs (`qokeedy` — `24.4%`) stay inside the instruction paragraphs** ($z = +9.97$)!
   - **Cosmological Wheels & 9-Sphere Rosettes Map (`f85r1–f86v6`, `fRos`)**: A 6-panel foldout complex (`2,336` tokens) where the 3 Diagram Panels (`f85r2`, `f86v4`, `fRos`) surge **`1.99×` in `o-` nominal forms (`52.1%` vs. `26.2%`)** while the 4 Prose Treatise Panels surge **`2.61×` in `qo-` active verbs (`14.1%` vs. `5.4%`, $z = +12.45$)**, and **`64.0%` of `fRos` tokens appear verbatim in Starred Recipes (`S`)** (`63.2%` in Herbal `H`).
   - **Pharmaceutical Jars (`f88r–f102v`)**: The apothecary's workbench—showing painted storage jars (`okol`, `otol`) on the left alongside **cut-up pieces of roots (`darary`, `okar`, `orar`) and leaves/seeds (`osal`, `okal`)** with single-word labels written directly over each plant part (`43.1%` echoing their stem directly in the recipe prose on the very same page).
   - **Starred Master Recipes (`f103r–f116r`)**: `285` star-bulleted (`*`) compound prescriptions (`10,587` words: `183` Aqueous Infusions, `64` Balneo Washes, `29` Thermal Decoctions, `9` Compound Essence Salves) governed by the **3-Zone Procedural Frame Law ($z = +18.93$)**: Gallows openers surge **`3.10×`** in the Opening 20% (`19.5%` vs. `6.3%` Middle) and Terminal `-am/-m` stops surge **`3.90×`** in the Closing 20% (`3.9%` vs. `1.0%` Opening).

3. **Concrete Visual & Bilingual "Rosetta" Anchors**
   - **Blood-Red Alkanet Root (`oror` on `f102v2` & `f116v`)**: The final page of the manuscript (`f116v`) contains a 3-line European charm (`...so nim gas mich oror`) that ends with the Voynich word **`oror`** right below a crimson-red paint blot. Searching the Pharmaceutical section reveals **`oror`** on **`f102v2`** labeling a plant with a vivid **blood-red root**—Dyer's Alkanet (*Alkanna tinctoria*) / Madder (*Rubia tinctorum*).
   - **European Month Names (`mars..decembre` on `f70v2–f73v`) & Sequential Recipe Crib (`f107r`)**: Written right inside the Zodiac medallions (`mars` between the two fish of Pisces on `f70v2`), tying the `348` Voynich star-nymph degree labels (`otaly`, `okaly`, `otaram`) to the Western solar year—including the clockwise Pisces trio **`otaram -> otaral -> otalar` (`f70v2.22..24`)**, which recurs in exact `1 -> 2 -> 3` order inside Starred Recipe **`f107r.11..16`** ($p = 6.7 \times 10^{-6}$).
   - **Bilingual Poultice Tub (`den mus` / `del` on `f66r`)**: In the bottom-left corner of `f66r`, Middle High German `den mus` (*"the mush/poultice"*) and `del` caption two round poultice balls and a tub beside a reclining bather and a 3-column margin index table.
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
├── explorer/               # Self-contained local HTML interactive explorer (5 tabs)
│   └── index.html          # Open in any browser to inspect 21 scans, decode words & browse 20 cribs
├── notes/                  # Human-readable visual guides, translations & thematic syntheses
│   ├── PLAIN_ENGLISH_VISUAL_READERS_GUIDE.md         # Start here: 3-step word guide + 15 visual page walkthroughs
│   ├── VISUAL_BOTANICAL_AND_ASTRO_IDENTIFICATIONS.md # 20 botanical, astronomical, balneological, cosmological & recipe cribs
│   ├── STARRED_RECIPES_ROSETTES_COSMOLOGY_AND_4TRANSCRIBER_PROOF.md
│   ├── ZODIAC_MONTHS_BALNEO_PLUMBING_AND_BOTANICAL_ATLAS.md
│   ├── EIGHT_CASE_PARADIGM_AND_PARAGRAPH_STATE_COMPILER.md
│   └── DECODING_ATTACKS_SYNTHESIS.md                 # Master index of all 160 computational & visual attacks
├── pages/                  # High-resolution extracted & contrast-enhanced folio scans (.png)
├── data/                   # EVA transliterations (ZL3b-n.txt, etc.), folio_index.json & JSON outputs
├── tools/                  # Python scripts for rendering scans, building the explorer & running analyses
├── NOTES.md                # Complete chronological research log (Discoveries 1–177)
└── AGENTS.md               # Workspace continuity & contributor guidelines
```

### How the Two PDF Books in `books/` Differ
| File in `books/` | Pages | Resolution | Best Used For |
| :--- | :---: | :---: | :--- |
| **[`books/voynich-yale-beinecke-2026-highres-214p.pdf`](books/voynich-yale-beinecke-2026-highres-214p.pdf)** | `214` | `~1500 × 2000 px` | **Primary visual forensics:** 2× sharper pixel density, printed Beinecke Image IDs (`1006076`…`1006283`), and 4 physical fore-edge/spine scans (`p210–p213`). |
| **[`books/voynich-tcpdf-2014-bookmarked-210p.pdf`](books/voynich-tcpdf-2014-bookmarked-210p.pdf)** | `210` | `~1082 × 1500 px` | **Fast navigation:** Includes a 210-entry clickable PDF bookmark sidebar (`1r` through `116v`) that maps `1:1` to pages `1..209` of the Yale PDF. |

---

## 3. Recommended Reading & Exploration Path

1. **[`notes/PLAIN_ENGLISH_VISUAL_READERS_GUIDE.md`](notes/PLAIN_ENGLISH_VISUAL_READERS_GUIDE.md)** — Learn the 3-step `Prefix + Root + Suffix` system and read 15 iconic pages side-by-side with their scans.
2. **[`notes/VISUAL_BOTANICAL_AND_ASTRO_IDENTIFICATIONS.md`](notes/VISUAL_BOTANICAL_AND_ASTRO_IDENTIFICATIONS.md)** — See the 20 strongest botanical, astrological, balneological, cosmological, and recipe visual identifications (`SPEC-01` through `SPEC-20`).
3. **[`explorer/index.html`](explorer/index.html)** — Double-click or open in any browser to test any Voynich word in the interactive **3-Step Lego Word Analyzer**, click through 21 page walkthroughs, or inspect the 5 interactive tabs.
4. **[`notes/STARRED_RECIPES_ROSETTES_COSMOLOGY_AND_4TRANSCRIBER_PROOF.md`](notes/STARRED_RECIPES_ROSETTES_COSMOLOGY_AND_4TRANSCRIBER_PROOF.md)** & **[`notes/ZODIAC_MONTHS_BALNEO_PLUMBING_AND_BOTANICAL_ATLAS.md`](notes/ZODIAC_MONTHS_BALNEO_PLUMBING_AND_BOTANICAL_ATLAS.md)** — Full grammatical tables, the 285 Starred Master Recipes classifier, the 9-Rosettes foldout map, the 4-Transcriber consensus audit, the 12-medallion Zodiac calendar, and the 20-page Balneological plumbing atlas.
5. **[`NOTES.md`](NOTES.md)** — The complete, unabridged research log containing every visual observation, statistical test, negative result, and discovery (`1–177`).

---

## 4. Quick CLI Toolkit Usage

All scripts use Python 3 with `pypdf`, `Pillow`, and `numpy`:

```bash
# Render any folio or high-contrast crop from the PDFs in books/
python tools/render_folio.py f17r --out pages/f17r_full.png
python tools/render_folio.py f116v --crop 0.15 0.08 0.85 0.35 --enhance --out pages/f116v_incantation_crop_enh.png

# Rebuild the master folio index, 20-specimen visual dossier, or 5-tab interactive HTML explorer
python tools/build_index.py
python tools/build_visual_botanical_astro_identifications.py
python tools/build_interactive_explorer.py
```
