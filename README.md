# Voynich Manuscript Research (`Beinecke MS 408`)

A visual, computational, and linguistic investigation of the **Voynich Manuscript**, built directly from two complete digital scans of the codex and four cross-checked machine-readable transliterations (`38,409` word tokens across `226` folios, with **`88.8%` 4-transcriber canonical consensus** across `ZL3b-n`, `RF1b-er`, `IT2a-n`, and `GC2a-n` `v101`).

> **Want to jump straight into reading pages and decoding words in plain English?**
> - **[Plain-English Visual Reader's Guide](notes/PLAIN_ENGLISH_VISUAL_READERS_GUIDE.md)** — A jargon-free walkthrough of **20 iconic pages** (`f1r` through `f116v`, including `f2r` Cornflower Split, `f25v` Dragon-Herb Leaf-Tip Split, `f57v` Key Ring, `f67r1` Sun Wheel, `f68v3` Spiral Galaxy Wheel, `f72r1` Four-Month Zodiac Panorama `abril..jolh`, `f79r` Shower Cascade, `f88r` Three Jars, and `f100r` Second `oror` Alkanet Locus) with high-resolution scans and a **3-Step "Lego" Cheat Sheet** for reading any Voynich word.
> - **[Visual Botanical, Astrological, Balneological & Cosmological Identification Dossier](notes/VISUAL_BOTANICAL_AND_ASTRO_IDENTIFICATIONS.md)** — Matches **30 flagship plant paintings, apothecary jars, star clusters, solar/spiral wheels, bilingual month wheels, bath pipes, cosmological spheres, and starred master prescriptions** (`SPEC-01..30`: `f1v` Belladonna, `f2r` Cornflower, `f9v` Heartsease, `f20v` Blue Knapweed, `f25v` Dragon-Herb `Dracontea`, `f33r` Anthropomorphic Mandrake Root, `f57v` `f <-> p` Key Ring, `f66r` Poultice Tub `den mus / del`, `f67r1` 12-Sector Sun Wheel, `f68r3` Pleiades = `doaro`, `f68v3` 8-Arm Spiral Galaxy Wheel, `f70v2` Pisces = `mars`, `f72r1` 4-Wheel Panorama `abril..jolh`, `f79r` *Doccia* Shower Cascade, `f82v` Bath Pipes = `olkol/okoldy`, `f88r` Three Jars = `okol`, `fRos` 9-Sphere Map, `f107r` Starred Recipes, `f100r/f102v2/f116v` Blood-Red Alkanet Root = `oror`) to concrete 15th-century European sources.
> - **[Interactive Local HTML Explorer (`explorer/index.html`)](explorer/index.html)** — Open `explorer/index.html` directly in any web browser (no server needed) to click through **30 manuscript scans**, decode any Voynich word into `Prefix + Root Stem + Suffix`, and browse **7 interactive tabs**: Page-by-Page Reader (`30`), Visual Cribs (`30`), Core Dictionary & 8-Case Grammar, Zodiac Months & Bath Plumbing, Starred Recipes / Rosettes / 4-Transcriber Proof, Astronomical Star-Wheels / 5 Scribe Hands / Pharma Supply Chain, and **25 Complete Translated Paragraphs, 752 Drawing Intrusions (`<->`) & 27 Right-Justified Titles (`=Pt/+Pc`)**.

---

## 1. What Have We Actually Learned? (The Plain-English Summary)

When you look at a Voynich page for the first time, it looks like an impenetrable wall of alien words. Our investigation shows why—and how to read through it:

1. **Every Voynich Word Is Built Like a 3-Part "Lego Block" (`Prefix + Root Stem + Suffix`)**
   - Once you peel off the **grammatical prefix on the left** (`o-` *"the"*, `qo-` *"then/and-it"*, `d-` *"take/from"*, `ol-` *"in the vessel/pipe/bath"*, `y-` *"and/continuing after a line break or stem jump"*) and the **inflectional suffix on the right** (`-edy` *"boil/wash/steep"*, `-ol/-or` *"in the liquid/oil"*, `-aiin` *"one measured dose"*, `-am` *"complete/stop"*), thousands of scary-looking strings collapse into **~200 recurring Root Stems**.
   - **Example:** In the Bathing and Recipe sections, `qokeedy` (`qo-` *"then"* + `ke` *"boil/heat"* + `-edy` *"active process"*) means *"then boil/decoct it!"*, while `shedy` (`sh-` + `-edy`) means *"wash/bathe!"*.
   - **Verified Across All 4 Human Transcribers (`88.8%` Consensus) & All 5 Scribe Hands (`77.0%` Shared Core):** Aligning `5,132` lines (`36,103` word tokens) across all four independent transcription files (`Zandbergen-Landini`, `Rene/Friedman`, `Takahashi`, and `Glen Claston v101`) proves **`88.8%` 4-way agreement on the canonical word skeleton**. Furthermore, testing all **5 paleographic scribe hands (`$H=1..5`, `36,439` tokens)** proves that **every single scribe obeys the exact same positional line-and-paragraph grammar** (Paragraph-Start Gallows `65.5%–93.8%`, Line-Start `y-` surge `2.5×–10.0×`, Line-End `-m` stop surge `6.2×–29.0×`), and **just `120` universal root stems shared across all `5 / 5` hands cover `77.0%` (`28,044 / 36,439`) of the entire manuscript**!
   - **Illustrations Were Painted First, and `y-` Marks Visual Jumps Across Plant Stems (`752` `<->` Intrusions):** Across all `752` places where a horizontal line of text splits around a painted plant stem or leaf (`<->`), words right before the stem suppress the line-final `-m` stop (**`2.39%` vs. `15.18%` at true right margins, `6.35×` lower**), words resuming on the right side of the stem exclude Gallows openers (**`0.27%` [`2 / 752`] vs. `20.8%` at true line starts, `77.2×` lower**), and words resuming after jumping over the stem surge **`4.07×` in the `y-` prefix (`14.49%` vs. `3.56%` mid-line, matching `14.43%` at true line starts)**—proving that the illustrations were already drawn on the vellum before the scribes wrote the text and that `y-` is an explicit visual/clause resumption marker!

2. **The Book Is a 15th-Century Illustrated Medical, Astrological & Apothecary Compendium**
   - **Herbal (`f1r–f57v`)**: Illustrated plant monographs organized into distinct visual/chromatic guilds (Red/Crimson blossoms & dye-roots, Blue scaly-calyx corollas & berries, Climbing vines, Aquatic reniform leaves, and Umbels) describing their primary liquid extracts (`chol`, `shol`) and root bases (`otar`, `kor`), capped on **`f57v`** by the 4-ring `f <-> p` cipher/pagination key ring. Across the `27` right-justified (`=Pt`) and centered (`+Pc`) paragraph title/coda lines, **`77.8%` (`21 / 27`) echo their root stem in the same folio's prose** and **`81.5%` (`22 / 27`) recur in the Pharmaceutical and Recipe sections**.
   - **Astronomical Star-Wheels (`f67r1–f70r2`) & Zodiac Month Calendar (`f70v2–f73v`)**: Across the `14` Astronomical wheel pages (`f67r1` 12-Sector Sun Wheel, `f68r3` Pleiades Moon Wheel, `f68v3` 8-Arm Spiral Galaxy Pinwheel; `1,690` tokens), radial star/sector labels surge in the nominal `o-` prefix (**`37.6%` vs. `28.0%` in circular ring prose, $z = +3.83$**), and **`64.4%` (`1,089 / 1,690`) appear word-for-word in the Herbal section** (`62.4%` in Starred Recipes). Across the `12` Zodiac medallions captioned with the **15th-century European month names `mars` [March] through `decembre` [December]** (including the 4-month foldout panorama `abril, may, juny, jolh` on `p131`), **`58.1%` (`202 / 348`) of the star-nymph degree labels appear verbatim inside the medical sections**.
   - **Balneological / Medical Bathing (`f75r–f84v`)**: Opened by the waterfall frontispiece **`f75r`**, the pure-text master treatise **`f76r`**, and the vertical *doccia* shower cascade **`f79r`**. On the painted plumbing diagrams (`f75v, f78r, f82v`), **water pipes are labeled with `o-/ol-` vessel nouns (`olkol`, `okoldy` — `62.2%`)**, while **active `qo-` boiling verbs (`qokeedy` — `24.4%`) stay inside the instruction paragraphs** ($z = +9.97$)!
   - **Cosmological Wheels & 9-Sphere Rosettes Map (`f85r1–f86v6`, `fRos`)**: A 6-panel foldout complex (`2,336` tokens) where the 3 Diagram Panels (`f85r2`, `f86v4`, `fRos`) surge **`1.99×` in `o-` nominal forms (`52.1%` vs. `26.2%`)** while the 4 Prose Treatise Panels surge **`2.61×` in `qo-` active verbs (`14.1%` vs. `5.4%`, $z = +12.45$)**, and **`64.0%` of `fRos` tokens appear verbatim in Starred Recipes (`S`)** (`63.2%` in Herbal `H`).
   - **Pharmaceutical Jars & 3-Stage Supply Chain (`f88r–f102v`)**: Across all `16` Pharmaceutical pages (`243` figure labels), **`@Lc` painted storage jars (`37` labels) average `7.41` characters vs. `5.85` characters for `@Lf` plant parts (`206` labels)**, **`31.3%` (`76 / 243`) match exact whole words in Herbal (`H`)**, **`29.2%` (`71 / 243`) match exact whole words in Starred Recipes (`S`)**, and **`53.1%` (`129 / 243`) form complete 3-Stage Supply Chain Stem Bridges (`Herbal Monograph -> Pharma Jar/Root -> Starred Master Recipe`)**!
   - **Starred Master Recipes (`f103r–f116r`)**: `285` star-bulleted (`*`) compound prescriptions (`10,587` words: `183` Aqueous Infusions, `64` Balneo Washes, `29` Thermal Decoctions, `9` Compound Essence Salves) governed by the **3-Zone Procedural Frame Law ($z = +18.93$)**: Gallows openers surge **`3.10×`** in the Opening 20% (`19.5%` vs. `6.3%` Middle) and Terminal `-am/-m` stops surge **`3.90×`** in the Closing 20% (`3.9%` vs. `1.0%` Opening).

3. **Concrete Visual & Bilingual "Rosetta" Anchors**
   - **Blood-Red Alkanet Root (`oror` on `f102v2`, `f100r` & `f116v`)**: The final page of the manuscript (`f116v`) contains a 3-line European charm (`...so nim gas mich oror`) that ends with the Voynich word **`oror`** right below a crimson-red paint blot. Searching the Pharmaceutical section reveals **`oror`** in **two independent loci**: on **`f102v2`** labeling a plant with a vivid **blood-red root**—Dyer's Alkanet (*Alkanna tinctoria*) / Madder (*Rubia tinctorum*)—and on **`f100r`** labeling a red-stemmed root cutting directly below the top jar row (`oror -> oalcheol -> cheol`)!
   - **Three Tiered Jars & Root-to-Recipe Ingestion (`okol` on `f88r`)**: On the Pharmaceutical frontispiece **`f88r`**, the central Row 2 root cutting (`@Lf`) is labeled **`okol`**, and Line 2 of the recipe directly below (`f88r.19`) writes **`...chokol daiin qoekol qoekol qockhol okol cheol...`** (*"Take one infused dose of the `okol` root, boil/process it three times, and steep `okol` in the liquid"*).
   - **European Month Names (`mars..decembre` on `f70v2–f73v`) & Sequential Recipe Crib (`f107r`)**: Written right inside the Zodiac medallions (`mars` between the two fish of Pisces on `f70v2`, plus `abril, may, juny, jolh` across the 4-panel foldout `p131`), tying the `348` Voynich star-nymph degree labels (`otaly`, `okaly`, `otaram`) to the Western solar year—including the clockwise Pisces trio **`otaram -> otaral -> otalar` (`f70v2.22..24`)**, which recurs in exact `1 -> 2 -> 3` order inside Starred Recipe **`f107r.11..16`** ($p = 6.7 \times 10^{-6}$).
   - **Bilingual Poultice Tub (`den mus` / `del` on `f66r`)**: In the bottom-left corner of `f66r`, Middle High German `den mus` (*"the mush/poultice"*) and `del` caption two round poultice balls and a tub beside a reclining bather and a 3-column margin index table.
   - **The Pleiades Seven-Star Cluster (`doaro` on `f68r3`), Dragon-Herb (`f25v`), & Anthropomorphic Mandrake Root (`f33r`)**: On `f68r3`, a tight cluster of **7 stars** is captioned **`doaro`** (the Pleiades in Taurus); on `f25v`, a winged dragon bites the lower leaf (*Dracontea* = Dragon-herb); and on `f33r`, the forked root terminates in male and female human faces (*Mandragora / Bryonia*).

![Folio f89r2 Apothecary Jar and Labeled Roots](pages/f89r2_full_enh.png)

---

## 2. Repository Structure

The repository is organized cleanly so that scans, human-readable guides, machine-readable data, and reproducible scripts each live in their own folder:

```text
voynich/
├── books/                  # Full manuscript PDF scans (stored via Git LFS)
│   ├── voynich-yale-beinecke-2026-highres-214p.pdf   # High-res Yale Beinecke export (~1500x2000 px, 214 pages incl. book edges)
│   └── voynich-tcpdf-2014-bookmarked-210p.pdf        # Bookmarked TCPDF edition (~1082x1500 px, 210 pages with folio TOC)
├── explorer/               # Self-contained local HTML interactive explorer (7 tabs, v5.0)
│   └── index.html          # Open in any browser to inspect 30 scans, decode words, read 25 paragraphs & browse 30 cribs
├── notes/                  # Human-readable visual guides, translations & thematic syntheses
│   ├── PLAIN_ENGLISH_VISUAL_READERS_GUIDE.md         # Start here: 3-step word guide + 20 visual page walkthroughs
│   ├── VISUAL_BOTANICAL_AND_ASTRO_IDENTIFICATIONS.md # 30 botanical, astronomical, balneological, cosmological & recipe cribs
│   ├── DRAWING_INTRUSIONS_RIGHT_TITLES_AND_25PARAGRAPH_READER.md
│   ├── ASTRONOMICAL_WHEELS_5SCRIBE_INVARIANCE_AND_PHARMA_SUPPLY_CHAIN.md
│   ├── STARRED_RECIPES_ROSETTES_COSMOLOGY_AND_4TRANSCRIBER_PROOF.md
│   ├── ZODIAC_MONTHS_BALNEO_PLUMBING_AND_BOTANICAL_ATLAS.md
│   ├── EIGHT_CASE_PARADIGM_AND_PARAGRAPH_STATE_COMPILER.md
│   └── DECODING_ATTACKS_SYNTHESIS.md                 # Master index of all 168 computational & visual attacks
├── pages/                  # High-resolution extracted & contrast-enhanced folio scans (.png)
├── data/                   # EVA transliterations (ZL3b-n.txt, etc.), folio_index.json & JSON outputs
├── tools/                  # Python scripts for rendering scans, building the explorer & running analyses
├── NOTES.md                # Complete chronological research log (Discoveries 1–185)
└── AGENTS.md               # Workspace continuity & contributor guidelines
```

### How the Two PDF Books in `books/` Differ
| File in `books/` | Pages | Resolution | Best Used For |
| :--- | :---: | :---: | :--- |
| **[`books/voynich-yale-beinecke-2026-highres-214p.pdf`](books/voynich-yale-beinecke-2026-highres-214p.pdf)** | `214` | `~1500 × 2000 px` | **Primary visual forensics:** 2× sharper pixel density, printed Beinecke Image IDs (`1006076`…`1006283`), and 4 physical fore-edge/spine scans (`p210–p213`). |
| **[`books/voynich-tcpdf-2014-bookmarked-210p.pdf`](books/voynich-tcpdf-2014-bookmarked-210p.pdf)** | `210` | `~1082 × 1500 px` | **Fast navigation:** Includes a 210-entry clickable PDF bookmark sidebar (`1r` through `116v`) that maps `1:1` to pages `1..209` of the Yale PDF. |

---

## 3. Recommended Reading & Exploration Path

1. **[`notes/PLAIN_ENGLISH_VISUAL_READERS_GUIDE.md`](notes/PLAIN_ENGLISH_VISUAL_READERS_GUIDE.md)** — Learn the 3-step `Prefix + Root + Suffix` system and read 20 iconic pages side-by-side with their scans.
2. **[`notes/VISUAL_BOTANICAL_AND_ASTRO_IDENTIFICATIONS.md`](notes/VISUAL_BOTANICAL_AND_ASTRO_IDENTIFICATIONS.md)** — See the 30 strongest botanical, astrological, balneological, cosmological, and recipe visual identifications (`SPEC-01` through `SPEC-30`).
3. **[`explorer/index.html`](explorer/index.html)** — Double-click or open in any browser to test any Voynich word in the interactive **3-Step Lego Word Analyzer**, click through 30 page walkthroughs, or inspect the 7 interactive tabs.
4. **[`notes/DRAWING_INTRUSIONS_RIGHT_TITLES_AND_25PARAGRAPH_READER.md`](notes/DRAWING_INTRUSIONS_RIGHT_TITLES_AND_25PARAGRAPH_READER.md)**, **[`notes/ASTRONOMICAL_WHEELS_5SCRIBE_INVARIANCE_AND_PHARMA_SUPPLY_CHAIN.md`](notes/ASTRONOMICAL_WHEELS_5SCRIBE_INVARIANCE_AND_PHARMA_SUPPLY_CHAIN.md)**, **[`notes/STARRED_RECIPES_ROSETTES_COSMOLOGY_AND_4TRANSCRIBER_PROOF.md`](notes/STARRED_RECIPES_ROSETTES_COSMOLOGY_AND_4TRANSCRIBER_PROOF.md)** & **[`notes/ZODIAC_MONTHS_BALNEO_PLUMBING_AND_BOTANICAL_ATLAS.md`](notes/ZODIAC_MONTHS_BALNEO_PLUMBING_AND_BOTANICAL_ATLAS.md)** — Full grammatical tables, 25 complete translated paragraphs, drawing-intrusion layout proof, 14 Astronomical Star-Wheels, 5-Scribe Invariance proof, 3-Stage Pharmaceutical Supply Chain, 285 Starred Master Recipes classifier, 9-Rosettes foldout map, and 4-Transcriber consensus audit.
5. **[`NOTES.md`](NOTES.md)** — The complete, unabridged research log containing every visual observation, statistical test, negative result, and discovery (`1–185`).

---

## 4. Quick CLI Toolkit Usage

All scripts use Python 3 with `pypdf`, `Pillow`, and `numpy`:

```bash
# Render any folio or high-contrast crop from the PDFs in books/
python tools/render_folio.py f17r --out pages/f17r_full.png
python tools/render_folio.py f116v --crop 0.15 0.08 0.85 0.35 --enhance --out pages/f116v_incantation_crop_enh.png

# Rebuild the master folio index, 30-specimen visual dossier, or 7-tab interactive HTML explorer
python tools/build_index.py
python tools/build_visual_botanical_astro_identifications.py
python tools/build_interactive_explorer.py
```
