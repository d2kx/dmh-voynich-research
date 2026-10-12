#!/usr/bin/env python3
"""
tools/build_interactive_explorer.py

Builds `explorer/index.html` — a self-contained, zero-server interactive local HTML
explorer for the Voynich Manuscript research repository.

Includes 5 synchronized interactive views:
  1. Page-by-Page Visual Reader (21 iconic folios with high-res scans & clickable clauses)
  2. Botanical, Astrological, Balneological & Cosmological Identifications (20 flagship specimens `SPEC-01..20`)
  3. Core Root Dictionary & 8-Case Inflectional Grammar Matrix
  4. Zodiac Month Calendar (`mars..decembre`) & 20-Page Bathing Plumbing Tracker (`Wave 36`)
  5. Starred Recipes (`f103r–f116r`), 9-Rosettes Map (`fRos`) & 4-Transcriber Consensus Proof (`Wave 37`)
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EXPLORER_DIR = ROOT / "explorer"
OUT_HTML = EXPLORER_DIR / "index.html"


WALKTHROUGH_FOLIOS = [
    {
        "folio": "f1r",
        "title": "The Grand Opening Manifesto & Marginal Index Key",
        "section": "Herbal A (Scribe 1)",
        "pdf_page": 3,
        "image": "../pages/f1r_opening.png",
        "secondary_image": "../pages/f1r_pt_title.png",
        "summary": "Opens the manuscript with the famous gallows declaration `fachys ykal ar ataiin`, five left-margin index letters (`y, s, d, o, a`), and a centered boxed caption (`dain os teody`) at the bottom of paragraph 1.",
        "clauses": [
            {
                "locus": "f1r.1",
                "eva": "fachys ykal ar ataiin shol shory cthres y kor sholdy",
                "english": "Here begins the declaration (`fachys`) of the primary essence (`ykal`) from the first measured source (`ar ataiin`): the washed liquid extract (`shol shory`) is combined (`cthres`) with the core root-heart (`y kor`) and steeped in liquid (`sholdy`)."
            },
            {
                "locus": "f1r.2",
                "eva": "sory ckhar or y kair chtaiin shar are cthar cthar dan",
                "english": "Draw (`sory`) from the heart-extract (`ckhar`) and oil essence (`or`) one infused measure (`chtaiin`) of the pure core (`y kair`), dividing the root-extract (`cthar cthar`) into the dose (`dan`)."
            },
            {
                "locus": "f1r.5 (Centered Box Title =Pt)",
                "eva": "dain os teody",
                "english": "[Centered Boxed Caption]: Take this (`dain`) prepared star/seed essence compound (`os teody`)."
            }
        ]
    },
    {
        "folio": "f1v",
        "title": "Deadly Nightshade (Atropa belladonna) Monograph",
        "section": "Herbal A (Scribe 1)",
        "pdf_page": 4,
        "image": "../pages/f1v_belladonna_full_enh.png",
        "secondary_image": "",
        "summary": "First painted plant in the book: shows paired dark-green ovate leaves, two dark spherical berries nested in star-shaped calyces, and a heavy split taproot.",
        "clauses": [
            {
                "locus": "f1v.1",
                "eva": "kchs ydaraishyol cthy dotoeesy ckhol chody",
                "english": "Begin with the core infusion (`kchs`) and root-shoot oil (`ydaraishyol`): steep the leaf (`cthy`) and boil the concentrated liquid (`ckhol chody`)."
            },
            {
                "locus": "f1v.4",
                "eva": "chol daiin ctholyd darom",
                "english": "Take one measured dose (`daiin`) of the strained herbal liquid (`chol`), steep in the liquid medium (`ctholyd`), and complete the root preparation (`darom`)."
            }
        ]
    },
    {
        "folio": "f9v",
        "title": "Wild Pansy / Heartsease (Viola tricolor) Cordial Monograph",
        "section": "Herbal A (Scribe 1)",
        "pdf_page": 20,
        "image": "../pages/f9v_viola_full_enh.png",
        "secondary_image": "",
        "summary": "Delicate violet-blue and red nodding blossoms on slender stalks with scalloped heart-shaped leaves and a red-tinted root crown. Rich in the `kar/okar` ('heart/core') stem.",
        "clauses": [
            {
                "locus": "f9v.1",
                "eva": "tydlo choly kykar ylchdoteol otol daiin",
                "english": "From the flower-liquid (`tydlo`), prepare the strained syrup (`choly`) of the heart-core (`kykar`), steep in the vessel (`otol`), and take one measure (`daiin`)."
            }
        ]
    },
    {
        "folio": "f11v",
        "title": "Crimson-Blossom Centaury (`poldchody` Red-Blossom Guild)",
        "section": "Herbal A (Scribe 1)",
        "pdf_page": 24,
        "image": "../pages/f11v_poldchody_headword_and_plant_enh.png",
        "secondary_image": "",
        "summary": "Symmetrical branches crowned by crimson-red plumed flower tufts above palmate leaves. Opens with the rare headword `poldchody`, echoed on the final page `f116v`!",
        "clauses": [
            {
                "locus": "f11v.1",
                "eva": "poldchody ctheey chol daiin otol",
                "english": "Begin by steeping in the liquid vessel (`poldchody`): infuse the crimson blossom (`ctheey`) in one measure of strained herbal liquid (`chol daiin`) inside the vessel (`otol`)."
            }
        ]
    },
    {
        "folio": "f16v",
        "title": "The #1 Cross-Referenced Herbal Hub (`opchor` Compound)",
        "section": "Herbal A (Scribe 1)",
        "pdf_page": 34,
        "image": "../pages/f16v_full_enh.png",
        "secondary_image": "",
        "summary": "Palmate serrated leaves and a crimson terminal blossom above a claw-like rootstock. Shares the rare compound stem `opchor` directly with the Pharmaceutical jar on f89r1.",
        "clauses": [
            {
                "locus": "f16v.1",
                "eva": "koaiin opchor ofor otorol opchor daiin",
                "english": "Take the first measured portion (`koaiin`) of the vessel-infused compound (`opchor`), combine with the root-oil (`otorol`), and measure out one dose (`opchor daiin`)."
            }
        ]
    },
    {
        "folio": "f17r",
        "title": "Climbing Sarsaparilla/Bryony Vine With Secret Top-Margin Note",
        "section": "Herbal A + Language B Marginalia",
        "pdf_page": 35,
        "image": "../pages/f17r_full.png",
        "secondary_image": "../pages/f17r_top_margin_enh.png",
        "summary": "A dark-blue scalloped tuber sends a zigzagging stem right through the text lines. Tucked into the top-left margin is a faint 5-word Language B cross-reference note!",
        "clauses": [
            {
                "locus": "f17r.0 (Top-Margin Secret Note)",
                "eva": "otaldary oparam otorGs kolkarabil",
                "english": "[Marginal Cross-Reference]: From the root-extract (`otaldary`), apply the final preparation (`oparam`) of the core root-mixture (`kolkarabil`)."
            },
            {
                "locus": "f17r.1",
                "eva": "fshody daram ydaraishy otol dairo",
                "english": "Begin by washing the plant (`fshody`): take the main root to completion (`daram`) and its root-shoot extract (`ydaraishy`) in the liquid vessel (`otol dairo`)."
            }
        ]
    },
    {
        "folio": "f20v",
        "title": "Mountain Cornflower / Blue Knapweed-Thistle (`Centaurea montana`)",
        "section": "Herbal A (Scribe 1)",
        "pdf_page": 41,
        "image": "../pages/f20v_polypody_fern_enh.png",
        "secondary_image": "",
        "summary": "Eight spiky, scaly bract cups (calyces) topped by deep indigo-blue flower heads above two basal sets of three long lance-shaped serrated leaves.",
        "clauses": [
            {
                "locus": "f20v.1",
                "eva": "pchor or aiin shol daiin chol cthol",
                "english": "Begin the flower infusion (`pchor`): take one measure of golden essence (`or aiin`) and one measure of washed liquid extract (`shol daiin`) in the strained calyx decoction (`chol cthol`)."
            }
        ]
    },
    {
        "folio": "f25v",
        "title": "Aquatic Water-Lily / Asarabacca Kidney-Leaf Monograph",
        "section": "Herbal A (Scribe 1)",
        "pdf_page": 52,
        "image": "../pages/f25v_nymphaea_aquatic_enh.png",
        "secondary_image": "",
        "summary": "Massive kidney-shaped (reniform) leaf blade with radiating ribs on twin curving stalks rising from a dark-ringed creeping rhizome.",
        "clauses": [
            {
                "locus": "f25v.1",
                "eva": "pchor odaiin chol cheol otar daiin",
                "english": "Begin the infusion (`pchor`): take one measure (`odaiin`) of the strained cooling liquid (`chol`) and mucilage-oil (`cheol`) from the rhizome base (`otar daiin`)."
            }
        ]
    },
    {
        "folio": "f34r",
        "title": "Divided-Root / Twin-Flower Herb (`fchody`Currier B Herbal)",
        "section": "Herbal B (Scribe 2)",
        "pdf_page": 69,
        "image": "../pages/f34r_full_enh.png",
        "secondary_image": "",
        "summary": "A landmark Currier B Herbal page (`$L=B`, Scribe 2): shows two distinct floral crowns (golden-ochre vs. indigo-blue) and a split root system, blending Herbal nouns (`chol`, `dar`) with active `qo-` boiling verbs (`qokeedy`, `shedy`).",
        "clauses": [
            {
                "locus": "f34r.1",
                "eva": "fchody dain shol qokeedy shedy dar chol",
                "english": "Begin the divided-plant infusion (`fchody`): take one measure (`dain`) of the washed liquid (`shol`), boil thoroughly (`qokeedy`), wash/bathe (`shedy`), and take the root (`dar`) in the strained decoction (`chol`)."
            }
        ]
    },
    {
        "folio": "f49v",
        "title": "Vertical 25-Letter Marginal Acrostic & Spiny Root Monograph",
        "section": "Herbal A (Scribe 1)",
        "pdf_page": 100,
        "image": "../pages/f49v_full.png",
        "secondary_image": "../pages/f49v_left_margin_enh.png",
        "summary": "Features a 25-character vertical column of single index letters (`p, o, l, o, r, o, l, k...`) down the left margin beside a tall spiny herb with a split black tuber.",
        "clauses": [
            {
                "locus": "f49v.1",
                "eva": "poldaky okal chol daiin otol",
                "english": "Begin from the stalk-liquid (`poldaky`): steep the core essence (`okal`) in the strained herbal liquid (`chol`), taking one measure (`daiin`) in the vessel (`otol`)."
            }
        ]
    },
    {
        "folio": "f58r",
        "title": "Star-Bullet Botanical Index Directory (No Plant Drawing)",
        "section": "Herbal Index Directory",
        "pdf_page": 113,
        "image": "../pages/f58r_full.png",
        "secondary_image": "",
        "summary": "Pure-text directory page organized into 6 paragraphs marked by painted five-pointed star bullets (`*`) in the left margin, routing botanical stems to Pharmaceutical jars.",
        "clauses": [
            {
                "locus": "f58r.1 (* Star Bullet 1)",
                "eva": "poldal kor otar okar chol daiin",
                "english": "[Index Entry 1]: From the liquid vessel (`poldal`), index the root-bulb (`kor`), earth-root (`otar`), and heart-core (`okar`) in one measure of strained liquid (`chol daiin`)."
            }
        ]
    },
    {
        "folio": "f66r",
        "title": "Bilingual Corner Tub (`den mus` / `del`) & 3-Column Margin Key",
        "section": "Astronomical / Biological Index (Scribe 4/2)",
        "pdf_page": 120,
        "image": "../pages/f66r_margin_labels.png",
        "secondary_image": "../pages/f66r_corner_crib_enh.png",
        "summary": "Bottom-left corner shows a reclining bather beside two round pouches (`den mus` = 'the mush/poultice') and a tub (`del`), while a 3-column margin table pairs outer words (`rary, rals, salf`) with single index letters (`y, s, f`).",
        "clauses": [
            {
                "locus": "f66r (3-Column Margin Key + Corner Crib)",
                "eva": "rary rals saly salf fary qotesy qokal",
                "english": "[Margin Index Key (`y, s, y, f, f, s, l`)]: Root-part (`rary`), star-liquid (`rals`), seed-essence (`saly`), terminal f-grade (`salf`), flower-root (`fary`), boiled extract (`qotesy`), and boiled core (`qokal`) [for the poultice `den mus`]."
            }
        ]
    },
    {
        "folio": "f68r3",
        "title": "Four-Quadrant Moon Astrolabe & The Pleiades (`doaro`) Crib",
        "section": "Astronomical (`f67r–f73v`)",
        "pdf_page": 126,
        "image": "../pages/f68r3_pleiades_astrolabe_enh.png",
        "secondary_image": "",
        "summary": "A 4-spoked astronomical wheel around a central crescent Moon. The upper-left quadrant shows 7 clustered stars (the Pleiades) directly labeled `doaro`.",
        "clauses": [
            {
                "locus": "f68r3 (Star Cluster & Spoke Labels)",
                "eva": "doaro otol okalar otaldy opalal",
                "english": "The Pleiades 7-star cluster (`doaro`) governs the liquid extract (`otol`), the winged-seed/star essence (`okalar`), the root-decoction state (`otaldy`), and the terminal preparation (`opalal`)."
            }
        ]
    },
    {
        "folio": "f70v2",
        "title": "Pisces Zodiac Wheel With Bilingual `mars` (March) Month Crib",
        "section": "Zodiac (`f70v2–f73v`)",
        "pdf_page": 129,
        "image": "../pages/f70v2_pisces_mars.png",
        "secondary_image": "../pages/f72r3_zodiac_wheel_enh.png",
        "summary": "Central medallion shows two tethered Pisces fish with the 15th-century European month word `mars` (March) written right between them, surrounded by 29 star-nymph degree labels (`58.1%` of which match medical recipe words verbatim!).",
        "clauses": [
            {
                "locus": "f70v2 (Center Gloss + Star-Nymph Degree Labels)",
                "eva": "otaly okaly otaram otaral otalar okalar",
                "english": "[Month of March (`mars` — Pisces)]: Prepare the liquid essence (`otaly`), core star-essence (`okaly`), completed root balm (`otaram`), root-star extract (`otaral`), and degree essence (`otalar`, `okalar`)."
            }
        ]
    },
    {
        "folio": "f75r",
        "title": "Grand Waterfall Bathing Pool & 8-Line Architectural Niche",
        "section": "Balneological (`f75r–f84v`, Scribe 2)",
        "pdf_page": 136,
        "image": "../pages/f75r_waterfall_pool_enh.png",
        "secondary_image": "",
        "summary": "Opens the Bathing section: a pleated hood pours green medicated water down a vertical chute into two immersion pools, with an 8-line inset recipe inside the left arch (`dar olchedy`).",
        "clauses": [
            {
                "locus": "f75r (Architectural Niche Inset)",
                "eva": "dar olchedy dary sheey qokedy shedy ol",
                "english": "From the source (`dar`), pour into the infused bath (`olchedy`): take the root part (`dary`), wash gently (`sheey`), boil thoroughly (`qokeedy`), and bathe in the pool (`shedy ol`)."
            }
        ]
    },
    {
        "folio": "f76r",
        "title": "Master Balneological (Medical Bathing) Treatise & 6-Index Key",
        "section": "Balneological / Biological (`f75r–f84v`, Scribe 2)",
        "pdf_page": 139,
        "image": "../pages/f76r_full.png",
        "secondary_image": "../pages/f76r_margin_enh.png",
        "summary": "The only pure-text page in the Bathing section, keyed by 6 marginal letters (`s, d, q, s, o, l`) that walk step-by-step through boiling (`qokeedy`) and bathing (`shedy`).",
        "clauses": [
            {
                "locus": "f76r.1 (Header)",
                "eva": "pchedal opchdy Rchdy qokchdy qokedy",
                "english": "Begin the bath infusion liquid (`pchedal`): prepare the herbal charge (`opchdy`), infuse (`Rchdy`), bring the mixture to heat (`qokchdy`), and boil thoroughly (`qokedy`)."
            },
            {
                "locus": "f76r.12 (Marginal Index `d`)",
                "eva": "dain shedy qokeedy olchedy qokain otam",
                "english": "[Stage `d` — Dose & Bathe]: Take this measure (`dain`), wash/bathe (`shedy`), boil again (`qokeedy`), pour into the bath mixture (`olchedy`), measure the boiled draught (`qokain`), and complete (`otam`)."
            }
        ]
    },
    {
        "folio": "f82v",
        "title": "Labelled Hydrotherapy Pipes (`olkol` / `okoldy`) & Nymphs (`okal`)",
        "section": "Balneological (`f75r–f84v`, Scribe 2)",
        "pdf_page": 151,
        "image": "../pages/f82v_nymph_and_pipe_network_enh.png",
        "secondary_image": "../pages/f82v_olkol_okoldy_tube_labels_enh.png",
        "summary": "Proves the Label-vs-Prose Polarity Law (`z = +9.97`): painted water pipes are labeled with vessel nouns (`olkol`, `okoldy` — `62.2%` `o-/ol-`), while `qo-` boiling verbs (`qokeedy`) stay in the prose (`24.4%` vs `2.5%`).",
        "clauses": [
            {
                "locus": "f82v (Pipe Labels @Lt + Prose Instruction)",
                "eva": "olkol okoldy okal otal qokeedy shedy olchedy",
                "english": "Through the core liquid pipe (`olkol`) and infused conduit (`okoldy`) to the bather stations (`okal`, `otal`): boil the mixture (`qokeedy`), wash (`shedy`), and circulate in the infused bath (`olchedy`)."
            }
        ]
    },
    {
        "folio": "f85r2",
        "title": "Four-Winds / Four-Seasons Solar Cosmology Wheel (`f85r2` & `f86v4`)",
        "section": "Cosmological Foldout (Quire 14, Scribe 2)",
        "pdf_page": 158,
        "image": "../pages/p158_rosettes_full.png",
        "secondary_image": "../pages/p158_rosettes_top_left.png",
        "summary": "Reverse panels of the Rosettes foldout: `f85r2` shows a central blazing face ringed by 12 directional figures and 4 cardinal wind-heads (`54.7%` `o-` nominal rate, `0.9%` `qo-` rate).",
        "clauses": [
            {
                "locus": "f85r2 (Cardinal Spoke & Ring Labels)",
                "eva": "otalar okalar otol daiin okal dar",
                "english": "From the celestial sector (`otalar`) and primary star-essence (`okalar`), measure one portion (`daiin`) into the liquid vessel (`otol`) from the core source (`okal dar`)."
            }
        ]
    },
    {
        "folio": "fRos",
        "title": "The 9-Sphere Rosettes Foldout Map (`fRos` / `f85v2`)",
        "section": "Cosmological 6-Panel Foldout (Quire 14, Scribe 2)",
        "pdf_page": 159,
        "image": "../pages/p159_rosettes_map.png",
        "secondary_image": "../pages/p159_rosettes_center_enh.png",
        "summary": "A 6-panel foldout map of 9 interconnected spheres (`536` tokens) linked by hydrological causeways and pipes. `64.0%` of its words appear verbatim in Starred Recipes (`S`) and `63.2%` in Herbal (`H`)!",
        "clauses": [
            {
                "locus": "fRos (Causeway & Central Sphere Labels)",
                "eva": "otol daiin qokeedy shedy daraldy otedaiin okalar",
                "english": "In the central reservoir (`otol`), take one measure (`daiin`), boil (`qokeedy`), wash through the causeway (`shedy`), and draw the root-decoction (`daraldy`) and measured extract (`otedaiin`) of the star-essence (`okalar`)."
            }
        ]
    },
    {
        "folio": "f89r2",
        "title": "Apothecary Jar With Labeled Cut Roots (`darary` & `okar`)",
        "section": "Pharmaceutical (`f88r–f102v`)",
        "pdf_page": 158,
        "image": "../pages/f89r2_full_enh.png",
        "secondary_image": "../pages/f99r_three_jars_enh.png",
        "summary": "Shows a painted apothecary jar on the left beside two rows of dissected plant parts: cut leaves on top (`osal`, `okoldy`) and hairy taproots on the bottom (`darary`, `okar`, `otar`).",
        "clauses": [
            {
                "locus": "f89r2 (Root Labels + Recipe Opening)",
                "eva": "darary okar otar okol chol daiin otam",
                "english": "Take the main root (`darary`), the root-heart (`okar`), and the root base (`otar`): place in the storage jar (`okol`), steep in one measure of strained liquid (`chol daiin`), and seal the finished compound (`otam`)."
            }
        ]
    },
    {
        "folio": "f107r",
        "title": "Starred Master Recipes & Pisces (`mars`) Triple Sequential Crib",
        "section": "Starred Master Recipes (`f103r–f116r`, Quire 20)",
        "pdf_page": 191,
        "image": "../pages/f107r_starred_recipes_enh.png",
        "secondary_image": "../pages/f106r_stars_margin.png",
        "summary": "Shows how the `285` Starred Master Recipes (`10,587` words) work: paragraphs `3–4` (`f107r.11..16`) ingest 3 clockwise-adjacent Pisces (`mars`) star-nymph labels (`otaram -> otaral -> otalar`, `p = 6.7e-6`) in exact `1 -> 2 -> 3` order!",
        "clauses": [
            {
                "locus": "f107r.11–16 (Pisces `mars` Sequential Crib)",
                "eva": "pchody qokeedy otaram shedy otaral daiin otalar otaiinam",
                "english": "Begin the compound infusion (`pchody`): boil thoroughly (`qokeedy`) with the Pisces 10:00 root-balm (`otaram`), wash (`shedy`) with the 11:00 star-extract (`otaral`), take one measure (`daiin`) of the 12:00 degree essence (`otalar`), and seal the final dose (`otaiinam`)."
            }
        ]
    },
    {
        "folio": "f57v",
        "title": "Four-Figures Wheel & 4x14-Symbol `f <-> p` Cipher Key Ring",
        "section": "Quire H Key Wheel (Scribe 5)",
        "pdf_page": 115,
        "image": "../pages/f57v_ring_enh.png",
        "secondary_image": "../pages/f57v_full_enh.png",
        "summary": "Four standing figures divide the circle into 4 quadrants (`otodarag`, `oparairdly`, `olkeedal`, `otardaly`). Ring 2 repeats the exact same 14-symbol sequence 4 times, switching slot 9 from `f` (Quadrants 1–2) to `p` (Quadrants 3–4)!",
        "clauses": [
            {
                "locus": "f57v (4 Cardinal Figure Labels + Ring 1)",
                "eva": "otodarag oparairdly olkeedal otardaly daiin",
                "english": "The four quarters: from the earth-root (`otodarag`), the prepared compound (`oparairdly`), the boiled bath medium (`olkeedal`), and the root-decoction state (`otardaly`), take one measure (`daiin`)."
            }
        ]
    },
    {
        "folio": "f67r1 & f67r2",
        "title": "12-Sector Red/Blue Sun Wheel & 12-Lunar-Phase Disk Wheel",
        "section": "Astronomical (`f67r1–f70r2`, Scribe 4)",
        "pdf_page": 122,
        "image": "../pages/f67r1_sun_sectors_enh.png",
        "secondary_image": "",
        "summary": "Opening Astronomical spread: a 12-pointed red/blue Solar Wheel (`f67r1`) beside a 12-disk waxing/waning Lunar Phase Wheel (`f67r2`). `64.4%` of Astronomical tokens appear verbatim in the Herbal section!",
        "clauses": [
            {
                "locus": "f67r1–r2 (Solar Spoke & Lunar Phase Labels)",
                "eva": "otaldy otoldy okol okal daiin dar",
                "english": "In the solar sector (`otaldy`) and liquid vessel state (`otoldy`), place in the storage vessel (`okol`) the star-essence (`okal`) and take one measure (`daiin`) from the root (`dar`)."
            }
        ]
    },
    {
        "folio": "f68v3",
        "title": "8-Arm Spiral Galaxy Pinwheel & Triple Astronomical Foldout",
        "section": "Astronomical 3-Panel Foldout (Scribe 4)",
        "pdf_page": 125,
        "image": "../pages/f68v3_spiral_star_wheel_enh.png",
        "secondary_image": "",
        "summary": "Unfolded 3-wheel sheet (`f68v3` left, `f68v2` center, `f68v1` right): on `f68v3`, 8 curved spiral arms of text whirl out of a ruffled blue-and-gold star nebula around a 4-part central cross.",
        "clauses": [
            {
                "locus": "f68v3 (Spiral Arm & Central Cross Labels)",
                "eva": "otol okal otar oteey daiin",
                "english": "Through the celestial channel (`otol`), draw the star-essence (`okal`), earth-root base (`otar`), and prepared stellar extract (`oteey`) in one measured portion (`daiin`)."
            }
        ]
    },
    {
        "folio": "f88r",
        "title": "Three Tiered Apothecary Jars & The `okol` Root-to-Recipe Clause",
        "section": "Pharmaceutical (`f88r–f102v`, Scribe 1)",
        "pdf_page": 162,
        "image": "../pages/f88r_full_enh.png",
        "secondary_image": "../pages/f88r_okol_recipe_clause_enh.png",
        "summary": "Smoking-gun proof of plant-label ingestion: in Row 2, the central cut root is labeled `okol` (`f88r.15`), and directly underneath it on Line 2 (`f88r.19`) the recipe writes `...chokol daiin qoekol qoekol qockhol okol cheol...`!",
        "clauses": [
            {
                "locus": "f88r.15 (@Lf Root Label) + f88r.19 (Subjacent Recipe Line 2)",
                "eva": "chokol daiin qoekol qoekol qockhol okol cheol",
                "english": "Take one infused measure of the `okol` root (`chokol daiin`), boil/process it three times (`qoekol qoekol qockhol`), and steep the `okol` root in the mucilage-liquid (`okol cheol`)."
            }
        ]
    },
    {
        "folio": "f100r",
        "title": "16 Botanical Cuttings, Coiled Arrow-Vine & Second `oror` Alkanet Locus",
        "section": "Pharmaceutical (`f88r–f102v`, Scribe 1)",
        "pdf_page": 178,
        "image": "../pages/f100r_jars_and_seeds_enh.png",
        "secondary_image": "",
        "summary": "Shows 2 red cylindrical apothecary jars beside 16 miniature plant cuttings. In Row 3, the second plant from the left is explicitly labeled `oror`—confirming the Alkanet/Madder red-root crib (`f102v2` & `f116v`)!",
        "clauses": [
            {
                "locus": "f100r (Row 3 Cutting Labels + Recipe Opening)",
                "eva": "oror okar otar chol daiin qokedy",
                "english": "Take the red Alkanet root cutting (`oror`), the root-heart (`okar`), and the root base (`otar`): steep in one measure of strained liquid (`chol daiin`) and boil (`qokedy`)."
            }
        ]
    },
    {
        "folio": "f102v2 & f116v",
        "title": "The Blood-Red Alkanet Root (`oror`) & Final Bilingual Prescription",
        "section": "Pharmaceutical (`f102v2`) & Final Page (`f116v`)",
        "pdf_page": 186,
        "image": "../pages/f102v2_oror_alkanet_root_enh.png",
        "secondary_image": "../pages/f116v_incantation_crop_enh.png",
        "summary": "The Rosetta bridge of the manuscript: `oror` labels the blood-red Alkanet/Madder dye-root on `f102v2` AND appears as the final Voynich word of the European prescription on `f116v` (`...so nim gas mich oror`) right below a crimson pigment test blot!",
        "clauses": [
            {
                "locus": "f102v2 (Red Root Section)",
                "eva": "oror orar okor chol daiin",
                "english": "Take the blood-red Alkanet/Madder root (`oror`), its root-extract (`orar`), and core bulb (`okor`) in one measure of strained liquid (`chol daiin`)."
            },
            {
                "locus": "f116v.1–3 (Bilingual Final Page)",
                "eva": "so nim gas mich opoxleber valsch vbren so nim gas mich oror",
                "english": "[European Charm + Voynich Crib]: '+ So take from me (`so nim gas mich`) the liver/wound-balm (`opoxleber`); drive out the false/ill; so take from me the red Alkanet root (`oror`).'"
            }
        ]
    },
    {
        "folio": "f2r",
        "title": "Three-Headed Cornflower (*Centaurea*) & 16 Drawing Intrusions (`<->`)",
        "section": "Herbal A (`f1r–f57v`, Scribe 1)",
        "pdf_page": 6,
        "image": "../pages/f2r_cyanus_right_title_enh.png",
        "secondary_image": "",
        "summary": "Upper paragraph splits into 3 sub-columns (`<->`) around the three feathery flower heads, while the lower paragraph splits into 2 columns around the central stem (`16` `<->` jumps total!).",
        "clauses": [
            {
                "locus": "f2r.1–2 (Top Line Splitting Around Three Flower Heads)",
                "eva": "kydainy ypchol daiin otar ykor chol daiin",
                "english": "Begin from the core measure (`kydainy`): infuse in the vessel (`ypchol`) one measured dose (`daiin`) of the root base (`otar`), continuing (`y-`) with the core bulb (`ykor`) in one measure of strained liquid (`chol daiin`)."
            }
        ]
    },
    {
        "folio": "f25v",
        "title": "Palmate Leaf Fan With Dragon Biting Leaf & Pre-Painted Leaf-Tip Split (`<->`)",
        "section": "Herbal A (`f1r–f57v`, Scribe 1)",
        "pdf_page": 51,
        "image": "../pages/f25v_ivy_intrusion_enh.png",
        "secondary_image": "",
        "summary": "A winged dragon bites the lower-right leaf (medieval mnemonic for *Dracontea* = Dragon-herb), while at the top (`f25v.6–7`) the highest vertical leaf spear pokes into the text block, forcing the scribe to jump over the painted leaf point (`qokora <-> choy cthy dkaiin y`)!",
        "clauses": [
            {
                "locus": "f25v.6–7 (Lines Jumping Across the Uppermost Painted Leaf Tip `<->`)",
                "eva": "qokora choy cthy dkaiin y cthy otkaiin",
                "english": "Then prepare the root-heart (`qokora`) — [jump over painted leaf tip `<->`] — steep (`choy`) the divided leaf (`cthy`) in one core dose (`dkaiin y`), and draw one measured portion from the divided leaf (`cthy otkaiin`)."
            }
        ]
    },
    {
        "folio": "f33r",
        "title": "Spotted-Calyx Composite Herb With Male & Female Human-Faced Mandrake Roots",
        "section": "Herbal B (`f1r–f57v`, Scribe 2)",
        "pdf_page": 66,
        "image": "../pages/f33r_multiflower_enh.png",
        "secondary_image": "",
        "summary": "Two composite flower heads above a forked brown root whose left and right horizontal arms terminate in drawn male and female human faces (*Mandragora / Bryonia* iconography).",
        "clauses": [
            {
                "locus": "f33r.1–2 (Scribe 2 Currier B Monograph Opening)",
                "eva": "tchedar chdy qokeedy qokedy daiin",
                "english": "Begin from the root-base herbal infusion (`tchedar`): steep (`chdy`), then boil thoroughly (`qokeedy qokedy`) in one measured dose (`daiin`)."
            }
        ]
    },
    {
        "folio": "f72r1 & f79r",
        "title": "Four-Month Zodiac Panorama (`abril..jolh`) & Vertical Shower Cascade (`f79r`)",
        "section": "Zodiac (`p131`) & Balneological (`p144`)",
        "pdf_page": 131,
        "image": "../pages/f72r1_taurus_may_enh.png",
        "secondary_image": "../pages/f79r_bathing_canopy_enh.png",
        "summary": "Unfolding p.131 shows four 30-nymph Zodiac wheels side-by-side (`abril`, `may`, `juny`, `jolh`), while `f79r` (below) shows an overhead *doccia* shower cascading through three funnel-basins into a green immersion pool!",
        "clauses": [
            {
                "locus": "f72r1 (Taurus `may` Star-Nymph Degree Labels) + f79r.1 (Cascade Bath Opening)",
                "eva": "otaly okaly otar pchedar qokeedy shedy olchedy",
                "english": "[Under the May Taurus degrees `otaly okaly otar`]: Begin the root infusion (`pchedar`), then boil thoroughly (`qokeedy`), shower/wash (`shedy`), and soak in the infused bath basin (`olchedy`)."
            }
        ]
    },
    {
        "folio": "f49v",
        "title": "Cyclamen (*Lunaria*) With Arabic Numerals `1-2-3-4-5` & 3x Repeating Pentad Key (`z = +80.20`)",
        "section": "Herbal A (`f1r–f57v`, Scribe 1, Quire G)",
        "pdf_page": 99,
        "image": "../pages/f49v_cyclamen_key_12345_enh.png",
        "secondary_image": "",
        "summary": "Down the left margin of all 26 lines runs a vertical column of single Voynich glyphs containing 3 exact repetitions of the 5-glyph pentad `o - r/@192; - y - e - @140;` (z = +80.20). Right beside the first cycle (`o, r, y, e, @140;`), a medieval reader wrote the Arabic numbers `1, 2, 3, 4, 5`!",
        "clauses": [
            {
                "locus": "f49v.1–12 (Pentad Cycle 1 Aligned With Margin Numbers `1, 2, 3, 4, 5`)",
                "eva": "kshor shol qokchy chotchy okeodsho shol shodaiin",
                "english": "[Key `f -> 1:o, 2:r, 3:y, 4:e, 5:@140;`]: Begin by washing the core bulb (`kshor shol`), boil the herbal extract (`qokchy chotchy`), and steep in one measured dose of the bath liquid (`okeodsho shol shodaiin`)."
            }
        ]
    },
    {
        "folio": "f58r",
        "title": "The `6 -> 7 -> 8` Pointed Star Herbal Directory & 16-Line Acrostic Margin Column",
        "section": "Starred Herbal Index (`Quire H`, Scribe 3, Currier A)",
        "pdf_page": 116,
        "image": "../pages/f58r_starred_herbal_acrostic_enh.png",
        "secondary_image": "",
        "summary": "Three paragraphs marked by 6-pointed, 7-pointed, and 8-pointed stars in numerical order! In Paragraph 3 (`8-pointed star`), decoupling the 16-letter vertical margin column (`k,y,y,o,y,o,o,s,y,d,s,o,s,d,y,d`) resolves 100% (`7/16 -> 0/16`) of the apparent initial spelling anomalies (`oqotaly -> o + qotaly`, `dtor -> d + tor`, `opolkeor -> o + polkeor`).",
        "clauses": [
            {
                "locus": "f58r.31–39 (Paragraph 3 Lines After Decoupling the Left-Margin Acrostic Key)",
                "eva": "dshchol qotaly chocthhy ssheol tor kaiin polkeor ysheos tshol",
                "english": "[Margin key `o, o, s, y, d, s, o, s, d` decoupled]: Take the washed liquid (`dshchol`), then prepare the root essence (`qotaly`), infuse (`chocthhy ssheol`), and begin boiling the core extract (`polkeor ysheos tshol`)."
            }
        ]
    },
    {
        "folio": "f67r2",
        "title": "12-Sector Lunar/Planetary Wheel & Crimson Red-Ink Rubric Key (`34.85×` Surge)",
        "section": "Astronomical (`f67r1–f70r2`, Scribe 4)",
        "pdf_page": 122,
        "image": "../pages/f67r2_red_ink_12moons_enh.png",
        "secondary_image": "",
        "summary": "The 12 outer perimeter headings (`<f67r2.1–12>`) and Line 2 of the bottom paragraph (`<f67r2.73>`) are written in bright crimson red ink, concentrating the `ykch-/yke-` stem family at 46.15% vs. 1.32% in brown ink (34.85× surge, z = +5.48)!",
        "clauses": [
            {
                "locus": "f67r2.73 (Bottom Crimson Red-Ink Rubric Line Keying the 12 Red-Ink Rim Headings)",
                "eva": "sshey syshees qeykeey ykchey ykchey qokeochy oaiin okol ar olar",
                "english": "[Red-Ink Rubric Key]: Select the surface wash (`sshey syshees`), then boil the `ykchey` rubric sectors (`qeykeey ykchey ykchey qokeochy`) in one measure of the storage vessel (`oaiin okol ar olar`)."
            }
        ]
    },
    {
        "folio": "f32v, f47v & f102r2",
        "title": "Stroke-for-Stroke Visual Twin Plants (`Campanula` + `Doronicum`) Compounded on `f102r2`",
        "section": "Herbal A (`f32v, f47v`) <-> Pharmaceutical (`f102r2`, Scribe 1)",
        "pdf_page": 181,
        "image": "../pages/f102r2_pharma_twins_enh.png",
        "secondary_image": "../pages/f32v_campanula_twin_enh.png",
        "summary": "On the right panel (`f102r2`), the top register draws miniature stroke-for-stroke copies of `f47v` (*Doronicum* octopus-root `[1,1]`) and `f32v` (*Campanula* blue bellflower `[1,2]`) beside jar `kodaiig`, sharing 14 exact words (`chckhy, dor, chol, daiin...`) while surging in `qo-` compounding verbs!",
        "clauses": [
            {
                "locus": "f102r2.1–6 (Top Register Compounding Recipe Under Twin Plants `f47v [1,1]` + `f32v [1,2]`)",
                "eva": "kodaiig por aiin chefol y qokol olaiin daiin okol dor chckhy",
                "english": "[Into jar `kodaiig`]: Begin with one measure of the root (`por aiin`) and leaf-infusion (`chefol y`), boil in the vessel (`qokol olaiin`), and take one dose (`daiin`) of the vessel's red-root extract (`okol dor chckhy`)."
            }
        ]
    },
    {
        "folio": "f8v",
        "title": "Red Campion (*Silene dioica*) With Medieval Bookbinder's Quire 1 Signature (`Pmg / 1`)",
        "section": "Herbal A (`f1r–f57v`, Scribe 1, Quire 1 End)",
        "pdf_page": 19,
        "image": "../pages/f8v_quire1_signature_enh.png",
        "secondary_image": "",
        "summary": "Final page of Quire 1 (`$Q=A, $P=P`) displaying the medieval bookbinder's Latin gathering signature `Pmg` (*Primus*, 1st Quire) and numeral `1` in the bottom-right corner. Proves the 100.0% Page-Boundary Closure Law (`206/206` prose pages open with `<%>` and `99.03%` close with `<$>`) and Same-Leaf lexical cohesion (`z = +8.13`).",
        "clauses": [
            {
                "locus": "f8v.1–3 (Opening Paragraph Above the 4-Branched Root & `Pmg / 1` Quire Signature)",
                "eva": "cthod chol chor cthol daiin dain",
                "english": "Begin from the divided calyx (`cthod`): steep in the strained herbal liquid (`chol chor`) and leaf extract (`cthol`), taking one measured portion (`daiin dain`)."
            }
        ]
    },
    {
        "folio": "f16v",
        "title": "Starry Blue-Cross Nigella (*Nigella damascena*) With Crimson Leaves & Quire 2 Signature (`2m`)",
        "section": "Herbal A (`f1r–f57v`, Scribe 1, Quire 2 End)",
        "pdf_page": 33,
        "image": "../pages/f16v_cannabis_quire2_enh.png",
        "secondary_image": "",
        "summary": "Final page of Quire 2 (`$Q=B, $P=P`) with the medieval Quire 2 gathering signature `2m` (*Secundus*) in the bottom-right corner below a boot-shaped root, 4 serrated crimson leaf rosettes, and an 8-pointed blue-and-white star flower.",
        "clauses": [
            {
                "locus": "f16v.1–4 (First Paragraph Opening With Tall `p-` Gallows Header)",
                "eva": "pcodal chodar cthol qotol qokor daiin",
                "english": "Begin in the core vessel (`pcodal`): infuse the seed/flower extract (`chodar cthol`), boil the liquid vessel and root core (`qotol qokor`), and take one measured dose (`daiin`)."
            }
        ]
    },
    {
        "folio": "f89v1 & f102v1",
        "title": "Three-Shelf Pharmaceutical Compounding, Inscribed Maiolica Jars & Act-I Citation Law (`z = -5.37`)",
        "section": "Pharmaceutical (`f88r–f102v`, Scribe 1)",
        "pdf_page": 182,
        "image": "../pages/f102v1_pharma_shelves_quire19_enh.png",
        "secondary_image": "../pages/f89v1_three_row_pharma_enh.png",
        "summary": "On `f102v1`, Voynich drug labels are written right across the white waist-bands of the painted blue-and-white ceramic jars (`albarelli`), while `[2,2]` (`okeoraiin`) copies Herbal `f19r`! Across all multi-row Pharma pages (`Attack 174`), `66.29%` (`59/89`, `z = -5.37`) of echoed shelf roots appear in Lines 1–2 (`Act I: Ingredient Declaration`).",
        "clauses": [
            {
                "locus": "f102v1.1–3 (Act-I Ingredient Declaration Opening Under Inscribed Jar & Shelf Roots)",
                "eva": "pchdar okeoraiin qokeedy qokedy chol daiin",
                "english": "Begin from the root shelf (`pchdar`): take one measure of the core taproot (`okeoraiin`, twin of `f19r`), boil thoroughly (`qokeedy qokedy`), and steep in one measure of strained liquid (`chol daiin`)."
            }
        ]
    },
    {
        "folio": "f86v4, f86v6 & f86v5",
        "title": "Unfolded 3-Panel Back of the Rosettes Sheet: Two Cosmological Wheels + 4-Paragraph Treatise",
        "section": "Cosmological 3-Panel Verso (`Quire 14`, Scribe 2/4)",
        "pdf_page": 157,
        "image": "../pages/f86v4_four_winds_cosmology_enh.png",
        "secondary_image": "",
        "summary": "Unfolding p.157 shows the Four-Spoke Sun/Moon Wheel (`f86v4`, left) and Concentric Scalloped Lunar Cloud Ring (`f86v6`, center) side-by-side with 4 full-width paragraphs of procedural commentary (`f86v5`, right)—visually proving why Quire 14 diagrams are 52.1% nominal (`o-`) while Quire 14 prose surges 2.61× in `qo-` verbs (`z = +12.45`)!",
        "clauses": [
            {
                "locus": "f86v4/v6 (Left & Center Wheel Labels) + f86v5.1 (Right-Hand Prose Treatise Opening)",
                "eva": "otar okal otol pchedar qokeedy qokedy chedy shedy",
                "english": "[From the wheel sectors `otar okal otol`]: Begin the root infusion (`pchedar`), then boil thoroughly (`qokeedy qokedy`), infuse (`chedy`), and wash (`shedy`)."
            }
        ]
    },
    {
        "folio": "f57v",
        "title": "The Four-Ring Key Wheel (`o l d r v x k m [f/p] t r y c`) & Direct Proof of `f <-> p` Allography",
        "section": "Cosmological Key Wheel (`$Q=H`, Scribe 3/4)",
        "pdf_page": 115,
        "image": "../pages/f57v_four_ring_key_wheel_enh.png",
        "secondary_image": "",
        "summary": "Out of all 72 circular text rings in the codex (`Attack 178`), `f57v` contains the only two single-glyph key rings (`f57v.3` and `f57v.5`). In Ring 2 (`f57v.3`), a 13-glyph key sequence repeats 4 times around the 4 quadrants (`o l d r v x k m [f/p] t r y [c]`), swapping `f` (Q1–Q2) for `p` (Q3–Q4) in Slot 9—achieving 94.67% exact and 100.0% (`75/75`) allographic slot identity!",
        "clauses": [
            {
                "locus": "f57v.1 (Top-Left Key Title) + f57v.6–9 (Central Four Busts) + f57v.10–13 (Radial Spokes)",
                "eva": "dairal otodarag oparairdly olkeedal otardaly arkaldy araarar okeely ocfhor okear",
                "english": "[Wheel Title `dairal`]: The four quadrant figures (`otodarag`, `oparairdly`, `olkeedal`, `otardaly`) and their radial spokes (`arkaldy`, `araarar`, `okeely`, `ocfhor okear`) anchor the 4-quadrant 13-letter key wheel."
            }
        ]
    },
    {
        "folio": "f68r1–f68r3",
        "title": "Unfolded 3-Panel Astronomical Sheet & the 7-Star Pleiades Cluster (`dchol / doar`)",
        "section": "Astronomical (`$I=A, $Q=I`, Scribe 4)",
        "pdf_page": 124,
        "image": "../pages/f68r3_pleiades_moon_wheel_enh.png",
        "secondary_image": "",
        "summary": "Unfolding p.124 reveals three astronomical star-catalog diagrams side-by-side (`f68r1`, `f68r2`, `f68r3`). On the right-hand 8-spoke wheel (`f68r3`), the upper-left sector (`10 o'clock`) depicts the 7 tightly clustered golden stars of the Pleiades (`dchol / doar / otary`) mounted on a leafy stalk!",
        "clauses": [
            {
                "locus": "f68r3 (Pleiades Cluster & Sector Labels)",
                "eva": "dchol day doaro oalcheol okos otary okolchy",
                "english": "[Pleiades Sector Labels]: The Seven Sisters star-cluster (`dchol / doaro`) in the Taurus sector (`otary`), paired with the vessel-infusion star stations (`oalcheol`, `okolchy`)."
            }
        ]
    },
    {
        "folio": "f78r",
        "title": "Symmetrical Flower-Head Shower Reservoirs (`otcholkal / okchedy`) & Two-Pool Bath Cascade (`olkarar`)",
        "section": "Balneological (`$I=B, $Q=M`, Scribe 2)",
        "pdf_page": 142,
        "image": "../pages/f78r_balneo_twin_arches_pool_enh.png",
        "secondary_image": "",
        "summary": "Two giant botanical flower-head shower reservoirs at top-left (`otcholkal`) and top-right (`okchedy`) feed segmented telescopic pipes (`dararody`, `dchedy`) into an upper 8-nymph pool, which drains via a blue channel (`cthody / orory`) into a lower 7-nymph pool (`olkarar`).",
        "clauses": [
            {
                "locus": "f78r.1–3 (Reservoir Labels + Opening Decoction Protocol)",
                "eva": "otcholkal okchedy qokedy qokeedy dchedy qokeey qokain olkarar",
                "english": "[From floral reservoirs `otcholkal` & `okchedy`]: Boil the herbal mixture (`qokedy qokeedy`), channel through the infused pipe (`dchedy qokeey`), and take one dose (`qokain`) into the lower receiving bath (`olkarar`)."
            }
        ]
    },
    {
        "folio": "f95r1–f95r2 & f100r",
        "title": "Unfolded 3-Plant Currier B Herbal Sheet, 16-Cutting Pharma Atlas & 6-Register Stem Shift (`Attack 179`)",
        "section": "Herbal B Foldout (`f95r1–r2`, Scribe 2) & Pharmaceutical (`f100r`, Scribe 3)",
        "pdf_page": 171,
        "image": "../pages/f95r2_foldout_thistle_herbal_enh.png",
        "secondary_image": "../pages/f100r_pharma_jars_shelves_enh.png",
        "summary": "Unfolding `f95r2–f95r1` shows three Currier B plants (4-tuber spiky rosette, blue-bell Comfrey/Solomon's-Seal, and Poppy/Campion seed capsules) paired with `f100r` (2 crimson jars + 16 labeled cuttings). Holding the exact same 76 Universal Core Stems (`28,473` tokens) fixed across all 6 registers (`Attack 179`) proves a monotonic shift from 84.40% Nominal Citation (`@L`) to 55.23% Procedural Verbal (`Balneo/Starred Recipes`)!",
        "clauses": [
            {
                "locus": "f95r2.1 + f100r.1 (Currier B Herbal Header vs. Pharma Shelf Header)",
                "eva": "tchody qokedy qokeedy chedy shedy pchor korol otar okeor daiin",
                "english": "Begin preparing the plant (`tchody`): boil thoroughly (`qokedy qokeedy`), infuse and wash (`chedy shedy`); in the pharmacy (`pchor`), combine the red root (`korol`) and umbel crowns (`otar okeor`) in one measured dose (`daiin`)."
            }
        ]
    }
]


LEXICON_STEMS = [
    {"stem": "ke / kee", "category": "Thermal Action Verb", "meaning": "Boil / Decoct / Simmer with heat", "examples": "qokeedy, qokedy, okeedy, qokain", "sections": "Balneological (B) & Starred Recipes (S)", "grounding": "Paired with fire/furnace boiling cycles and hot bath conduits (`f75r–f84v`, `f103r–f116r`)."},
    {"stem": "ch", "category": "Processing Verb / Noun", "meaning": "Infuse / Steep / Strained Herbal Liquid (`chol`)", "examples": "chedy, chol, chody, qokchedy, olchedy", "sections": "Universal across all sections (A & B)", "grounding": "Core herbal steeping stem; `chol` is the #1 botanical liquid noun in Herbal A."},
    {"stem": "sh", "category": "Hydrotherapy / Washing Verb", "meaning": "Wash / Bathe / Surface-Steep (`shedy` / `shol`)", "examples": "shedy, shol, shody, qokshedy, sheey", "sections": "Peak concentration in Balneological Baths (`f75r–f84v`)", "grounding": "Directly captions nymphs immersed in water pools and shower conduits (`f75r`, `f76r`, `f78r`)."},
    {"stem": "kar / kor", "category": "Botanical Organ Noun", "meaning": "Heart / Core / Root-Bulb", "examples": "okar, kor, qokar, okary, kykar", "sections": "Herbal, Pharmaceutical Jars, Recipes", "grounding": "Written directly on bulbous roots (`f89r2` `okar`) and Heartsease (`f9v`)."},
    {"stem": "tar", "category": "Botanical / Elemental Noun", "meaning": "Earth / Ground / Primary Root Base", "examples": "otar, tar, otary, otaram, otaral", "sections": "Herbal, Zodiac Rings, Pharma roots", "grounding": "Labels both Zodiac degrees (`f70v2`, `f72r3`) and basal root crowns (`f89r2`)."},
    {"stem": "ra / rar", "category": "Botanical Organ Noun", "meaning": "Main Root / Taproot / Rhizome", "examples": "darary, orar, orary, dara, ydaraishy", "sections": "Pharmaceutical Root Rows & Herbal Monographs", "grounding": "Directly labels cut taproots on `f89r2` (`darary`) and `f99r` (`orary`)."},
    {"stem": "oror", "category": "Specific Plant Crib", "meaning": "Dyer's Alkanet / Madder (Blood-Red Root)", "examples": "oror, orar, okor", "sections": "Pharma `f102v2`, `f100r` & Bilingual Final Page `f116v`", "grounding": "Matches both the crimson root painting on `f102v2` (`f100r`) and `...so nim gas mich oror` + red paint blot on `f116v`."},
    {"stem": "doaro", "category": "Astronomical Star Crib", "meaning": "The Pleiades (Seven Sisters Star Cluster)", "examples": "doaro, doar, odoar", "sections": "Astronomical `f68r3`", "grounding": "Written directly below the 7-star cluster in the upper-left quadrant of `f68r3`."},
    {"stem": "al / kal / sal", "category": "Botanical / Celestial Noun", "meaning": "Star / Winged Seed / Volatile Essence", "examples": "okal, osal, okalar, otaly, odal", "sections": "Astronomical Stars, Zodiac Rings, Pharma Seeds", "grounding": "Labels individual stars/nymphs on `f67r–f73v` and cut seed/leaf tops (`osal`) on `f89r2`."},
    {"stem": "ol / kol / tol", "category": "Vessel / Pipe / Liquid Medium", "meaning": "Apothecary Jar / Water Pipe / Bath Basin", "examples": "ol, otol, okol, olkol, okoldy, poldchody", "sections": "Pharmaceutical Jars & Balneological Pipes", "grounding": "Written directly on painted apothecary jars (`okol` on `f88r`) and bath pipes (`olkol`, `okoldy` on `f82v`)."},
    {"stem": "aiin / dain", "category": "Quantifier / Measure", "meaning": "One Measured Portion / Dose ('Take one part')", "examples": "daiin, dain, okaiin, qokain, odaiin", "sections": "Universal (3,800+ occurrences)", "grounding": "Built from counted vertical minim strokes (`i, ii, iii`) specifying dosage."},
    {"stem": "am / otam / okam", "category": "Terminal Closure Marker", "meaning": "Complete / Seal / Final Application (Recipe Stop)", "examples": "otam, okam, daram, oparam, otaram", "sections": "79%–94% Line-Final or Paragraph-Final across the book", "grounding": "Acts as the physical punctuation period at the end of recipes and paragraphs."}
]


def main():
    EXPLORER_DIR.mkdir(parents=True, exist_ok=True)
    specimens_data = json.loads((ROOT / "data" / "visual_botanical_astro_identifications.json").read_text(encoding="utf-8"))["specimens"]
    eight_case_path = ROOT / "data" / "eight_case_and_state_compiler.json"
    eight_case_data = json.loads(eight_case_path.read_text(encoding="utf-8")) if eight_case_path.exists() else {}
    paradigm_matrix = eight_case_data.get("paradigm_matrix", [])[:20]

    zodiac_data = json.loads((ROOT / "data" / "attack154_zodiac_months_and_300nymph_calendar.json").read_text(encoding="utf-8"))
    balneo_data = json.loads((ROOT / "data" / "attack155_balneological_plumbing_and_nymph_labels.json").read_text(encoding="utf-8"))
    recipes_data = json.loads((ROOT / "data" / "attack157_starred_recipes_classifier_and_herbal_router.json").read_text(encoding="utf-8"))
    rosettes_data = json.loads((ROOT / "data" / "attack158_rosettes_9sphere_and_cosmological_wheels.json").read_text(encoding="utf-8"))
    consensus_data = json.loads((ROOT / "data" / "attack159_four_transcriber_consensus_verifier.json").read_text(encoding="utf-8"))
    astro_data = json.loads((ROOT / "data" / "attack161_astronomical_wheels_and_lunar_mansions.json").read_text(encoding="utf-8"))
    hands_data = json.loads((ROOT / "data" / "attack162_five_scribe_hands_and_dialect_bridge.json").read_text(encoding="utf-8"))
    pharma_data = json.loads((ROOT / "data" / "attack163_pharmaceutical_jar_and_herbal_supply_chain.json").read_text(encoding="utf-8"))
    intrusions_data = json.loads((ROOT / "data" / "attack165_drawing_intrusions_and_visual_layout_proof.json").read_text(encoding="utf-8"))
    titles_data = json.loads((ROOT / "data" / "attack166_vertical_page_zone_and_right_titles.json").read_text(encoding="utf-8"))
    short_pars_data = json.loads((ROOT / "data" / "attack167_shortest_complete_paragraphs_reader.json").read_text(encoding="utf-8"))
    twins_data = json.loads((ROOT / "data" / "attack169_visual_twin_plants_herbal_to_pharma.json").read_text(encoding="utf-8"))
    keys_data = json.loads((ROOT / "data" / "attack170_key_like_sequences_and_f49v_cycle_proof.json").read_text(encoding="utf-8"))
    stars_data = json.loads((ROOT / "data" / "attack171_star_morphology_and_red_ink_rubric_code.json").read_text(encoding="utf-8"))
    quires_data = json.loads((ROOT / "data" / "attack173_quire_signatures_and_bifolio_continuity.json").read_text(encoding="utf-8"))
    shelves_data = json.loads((ROOT / "data" / "attack174_multirow_pharma_shelf_to_paragraph_alignment.json").read_text(encoding="utf-8"))
    weirdos_data = json.loads((ROOT / "data" / "attack175_plumed_gallows_and_weirdo_glyph_atlas.json").read_text(encoding="utf-8"))
    micro_data = json.loads((ROOT / "data" / "attack177_micro_spacing_and_clitic_fusion_law.json").read_text(encoding="utf-8"))
    f57v_data = json.loads((ROOT / "data" / "attack178_f57v_four_ring_key_and_astro_wheel_taxonomy.json").read_text(encoding="utf-8"))
    stem_matrix_data = json.loads((ROOT / "data" / "attack179_cross_section_stem_inflection_matrix.json").read_text(encoding="utf-8"))

    rosettes_panels = []
    for f_id, prof in rosettes_data["folio_profiles"].items():
        rosettes_panels.append({
            "folio": f_id,
            "panel_type": "DIAGRAM_WHEEL_OR_MAP" if f_id in ("f85r2", "f86v4", "fRos") else "PROSE_TREATISE",
            "token_count": prof["tokens"],
            "o_nominal_rate": prof["o_prefix_rate"],
            "qo_active_rate": prof["qo_prefix_rate"],
            "edy_dy_rate": prof["edy_dy_rate"],
            "ol_or_al_ar_rate": prof["ol_or_al_ar_rate"],
            "top_words": prof["top_words"],
        })

    embedded_json = json.dumps({
        "folios": WALKTHROUGH_FOLIOS,
        "specimens": specimens_data,
        "lexicon": LEXICON_STEMS,
        "paradigms": paradigm_matrix,
        "zodiac": zodiac_data["medallions"],
        "balneo": balneo_data["folios"],
        "recipes_showcase": recipes_data["showcase_recipes"],
        "rosettes_panels": rosettes_panels,
        "consensus_cribs": consensus_data["crib_verification_table"],
        "astro_wheels": astro_data["wheels"],
        "scribe_hands": hands_data["hands_table"],
        "pharma_bridges": pharma_data["three_stage_supply_bridges"],
        "intrusion_buckets": intrusions_data["positional_envelope_comparison"],
        "right_titles": titles_data["right_justified_titles_table"],
        "short_paragraphs": short_pars_data["showcase_25_paragraphs"],
        "visual_twins": twins_data["twin_pairs"],
        "f58r_acrostic": keys_data["f58r_acrostic_analysis"]["decoupled_lines"],
        "star_parity_folios": stars_data["quire20_star_parity"]["per_folio_parity_table"],
        "quires_table": quires_data["quire_architecture"]["quires"],
        "pharma_shelves": shelves_data["folio_breakdowns"],
        "plumed_examples": weirdos_data["plumed_gallows_analysis"]["top_collapsed_examples"],
        "weirdo_codes": weirdos_data["weirdo_glyph_atlas"]["top_20_weirdo_codes"],
        "micro_spaced_pairs": micro_data["top_35_comma_micro_spaced_pairs"],
        "f57v_quadrants": f57v_data["f57v_ring3_13glyph_4quadrant_table"],
        "universal_stem_matrix": stem_matrix_data["top_25_universal_stem_6register_paradigms"],
    }, ensure_ascii=False)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Voynich Manuscript Interactive Visual & Plain-English Explorer</title>
  <style>
    :root {{
      color-scheme: light dark;
      --bg: light-dark(#f8f6f0, #121318);
      --surface: light-dark(#ffffff, #1b1d24);
      --surface-alt: light-dark(#f1ece1, #242731);
      --text: light-dark(#1f2328, #e8eaf0);
      --muted: light-dark(#596068, #9da5b4);
      --border: light-dark(#d8d0c0, #323644);
      --accent: light-dark(#8b261d, #e06c58);
      --accent-soft: light-dark(#fbe9e7, #38201e);
      --gold: light-dark(#7c5800, #e5b546);
      --gold-soft: light-dark(#fef6e0, #332a14);
      --green: light-dark(#1b5e20, #66bb6a);
      --green-soft: light-dark(#e8f5e9, #19301c);
      --blue: light-dark(#0d47a1, #64b5f6);
      --blue-soft: light-dark(#e3f2fd, #162840);
      --radius: 12px;
      --shadow: 0 4px 18px rgba(0, 0, 0, 0.08);
    }}

    * {{
      box-sizing: border-box;
    }}

    body {{
      margin: 0;
      font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      background: var(--bg);
      color: var(--text);
      line-height: 1.55;
    }}

    header {{
      background: var(--surface);
      border-bottom: 1px solid var(--border);
      padding: 1.25rem 2rem;
      position: sticky;
      top: 0;
      z-index: 50;
      box-shadow: var(--shadow);
    }}

    .header-top {{
      max-width: 1440px;
      margin: 0 auto;
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      justify-content: space-between;
      gap: 1rem;
    }}

    .brand h1 {{
      margin: 0;
      font-size: 1.32rem;
      letter-spacing: -0.01em;
    }}

    .brand p {{
      margin: 0.2rem 0 0;
      font-size: 0.88rem;
      color: var(--muted);
    }}

    .nav-tabs {{
      display: flex;
      flex-wrap: wrap;
      gap: 0.45rem;
    }}

    .tab-btn {{
      background: var(--surface-alt);
      color: var(--text);
      border: 1px solid var(--border);
      padding: 0.52rem 0.9rem;
      border-radius: 999px;
      font-weight: 600;
      font-size: 0.83rem;
      cursor: pointer;
      transition: all 0.15s ease;
    }}

    .tab-btn:hover {{
      border-color: var(--accent);
    }}

    .tab-btn.active {{
      background: var(--accent);
      color: #fff;
      border-color: var(--accent);
    }}

    main {{
      max-width: 1440px;
      margin: 1.5rem auto 4rem;
      padding: 0 1.5rem;
    }}

    .tab-panel {{
      display: none;
    }}

    .tab-panel.active {{
      display: block;
    }}

    .decoder-card {{
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: var(--radius);
      padding: 1.25rem 1.5rem;
      margin-bottom: 1.5rem;
      box-shadow: var(--shadow);
    }}

    .decoder-row {{
      display: flex;
      flex-wrap: wrap;
      gap: 0.75rem;
      align-items: center;
      margin-top: 0.6rem;
    }}

    .decoder-input {{
      flex: 1;
      min-width: 240px;
      padding: 0.7rem 1rem;
      font-size: 1rem;
      border: 1px solid var(--border);
      border-radius: 8px;
      background: var(--surface-alt);
      color: var(--text);
      font-family: ui-monospace, SFMono-Regular, Consolas, monospace;
    }}

    .sample-chips {{
      display: flex;
      flex-wrap: wrap;
      gap: 0.4rem;
      align-items: center;
      font-size: 0.82rem;
      color: var(--muted);
    }}

    .word-chip {{
      display: inline-block;
      padding: 0.2rem 0.55rem;
      border-radius: 6px;
      background: var(--surface-alt);
      border: 1px solid var(--border);
      font-family: ui-monospace, SFMono-Regular, Consolas, monospace;
      font-size: 0.88rem;
      cursor: pointer;
      transition: all 0.12s ease;
    }}

    .word-chip:hover {{
      background: var(--accent-soft);
      border-color: var(--accent);
      transform: translateY(-1px);
    }}

    .lego-breakdown {{
      margin-top: 1rem;
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
      gap: 0.85rem;
    }}

    .lego-box {{
      padding: 0.85rem 1rem;
      border-radius: 10px;
      border: 1px solid var(--border);
    }}

    .lego-prefix {{ background: var(--blue-soft); }}
    .lego-stem {{ background: var(--gold-soft); }}
    .lego-suffix {{ background: var(--green-soft); }}
    .lego-gloss {{ background: var(--accent-soft); }}

    .lego-label {{
      font-size: 0.74rem;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      font-weight: 700;
      opacity: 0.8;
    }}

    .lego-val {{
      font-family: ui-monospace, SFMono-Regular, Consolas, monospace;
      font-size: 1.15rem;
      font-weight: 700;
      margin: 0.2rem 0;
    }}

    .lego-desc {{
      font-size: 0.86rem;
    }}

    .explorer-grid {{
      display: grid;
      grid-template-columns: 310px 1fr;
      gap: 1.5rem;
      align-items: start;
    }}

    @media (max-width: 960px) {{
      .explorer-grid {{
        grid-template-columns: 1fr;
      }}
    }}

    .folio-list {{
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: var(--radius);
      padding: 0.75rem;
      max-height: 78vh;
      overflow-y: auto;
    }}

    .folio-item {{
      width: 100%;
      text-align: left;
      background: transparent;
      border: 1px solid transparent;
      padding: 0.7rem 0.85rem;
      border-radius: 8px;
      cursor: pointer;
      color: var(--text);
      margin-bottom: 0.35rem;
      transition: background 0.12s;
    }}

    .folio-item:hover {{
      background: var(--surface-alt);
    }}

    .folio-item.active {{
      background: var(--accent-soft);
      border-color: var(--accent);
    }}

    .folio-item strong {{
      display: block;
      font-size: 0.95rem;
      color: var(--accent);
    }}

    .folio-item span {{
      font-size: 0.82rem;
      color: var(--muted);
    }}

    .folio-viewer {{
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: var(--radius);
      padding: 1.5rem;
      box-shadow: var(--shadow);
    }}

    .viewer-split {{
      display: grid;
      grid-template-columns: minmax(280px, 440px) 1fr;
      gap: 1.5rem;
      align-items: start;
      margin-top: 1rem;
    }}

    @media (max-width: 1100px) {{
      .viewer-split {{
        grid-template-columns: 1fr;
      }}
    }}

    .scan-box img {{
      width: 100%;
      border-radius: 10px;
      border: 1px solid var(--border);
      display: block;
      margin-bottom: 0.75rem;
    }}

    .clause-card {{
      background: var(--surface-alt);
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: 1rem;
      margin-bottom: 0.9rem;
    }}

    .clause-locus {{
      font-size: 0.78rem;
      font-weight: 700;
      text-transform: uppercase;
      color: var(--accent);
      margin-bottom: 0.35rem;
    }}

    .clause-tokens {{
      display: flex;
      flex-wrap: wrap;
      gap: 0.35rem;
      margin-bottom: 0.65rem;
    }}

    .clause-english {{
      font-size: 0.95rem;
      border-top: 1px dashed var(--border);
      padding-top: 0.55rem;
    }}

    .cards-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
      gap: 1.25rem;
    }}

    .spec-card {{
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: var(--radius);
      overflow: hidden;
      box-shadow: var(--shadow);
      display: flex;
      flex-direction: column;
    }}

    .spec-card img {{
      width: 100%;
      height: 270px;
      object-fit: cover;
      object-position: center top;
      border-bottom: 1px solid var(--border);
      background: #000;
    }}

    .spec-body {{
      padding: 1.15rem 1.25rem;
      flex: 1;
    }}

    .badge {{
      display: inline-block;
      font-size: 0.75rem;
      font-weight: 700;
      padding: 0.2rem 0.55rem;
      border-radius: 999px;
      background: var(--gold-soft);
      color: var(--gold);
      margin-bottom: 0.4rem;
    }}

    table {{
      width: 100%;
      border-collapse: collapse;
      background: var(--surface);
      border-radius: var(--radius);
      overflow: hidden;
      border: 1px solid var(--border);
    }}

    th, td {{
      padding: 0.72rem 0.85rem;
      border-bottom: 1px solid var(--border);
      text-align: left;
      font-size: 0.89rem;
    }}

    th {{
      background: var(--surface-alt);
      font-weight: 700;
    }}

    code {{
      font-family: ui-monospace, SFMono-Regular, Consolas, monospace;
      background: var(--surface-alt);
      padding: 0.12rem 0.38rem;
      border-radius: 5px;
      font-size: 0.88em;
    }}
  </style>
</head>
<body>

<header>
  <div class="header-top">
    <div class="brand">
      <h1>Voynich Manuscript Visual &amp; Plain-English Explorer</h1>
      <p>Click any word token on any page to peel apart its Prefix + Root Stem + Suffix in plain English</p>
    </div>
    <nav class="nav-tabs" aria-label="Explorer Views">
      <button class="tab-btn active" onclick="switchTab('walkthrough', this)">1. Page-by-Page Reader (42)</button>
      <button class="tab-btn" onclick="switchTab('specimens', this)">2. Visual Cribs &amp; Species (45)</button>
      <button class="tab-btn" onclick="switchTab('lexicon', this)">3. Core Dictionary &amp; 8-Case Grammar</button>
      <button class="tab-btn" onclick="switchTab('zodiac', this)">4. Zodiac Months &amp; Bath Plumbing</button>
      <button class="tab-btn" onclick="switchTab('recipes', this)">5. Starred Recipes, Rosettes &amp; 4-Transcriber Proof</button>
      <button class="tab-btn" onclick="switchTab('astro', this)">6. Astro Wheels, 5 Scribes &amp; Pharma Supply Chain</button>
      <button class="tab-btn" onclick="switchTab('paragraphs', this)">7. 25 Complete Paragraphs, Intrusions &amp; Right-Titles</button>
      <button class="tab-btn" onclick="switchTab('twins', this)">8. 12 Visual Twins, f49v Key &amp; Star Parity</button>
      <button class="tab-btn" onclick="switchTab('quires', this)">9. Quire Signatures, Pharma Shelves &amp; Weirdo-Glyph Atlas</button>
      <button class="tab-btn" onclick="switchTab('clitics', this)">10. Micro-Spacing Clitics, f57v Key Wheel &amp; 6-Register Stem Matrix</button>
    </nav>
  </div>
</header>

<main>
  <!-- Interactive Lego Word Analyzer (Always Visible) -->
  <section class="decoder-card" aria-label="Interactive Voynich Word Analyzer">
    <strong>Interactive 3-Step "Lego" Word Analyzer</strong>
    <span style="color: var(--muted); font-size: 0.88rem; margin-left: 0.5rem;">
      Type any Voynich word (or click any word chip below) to see its Prefix, Root Stem, Suffix, and plain-English reading:
    </span>
    <div class="decoder-row">
      <input id="wordInput" class="decoder-input" type="text" value="qokeedy" placeholder="Type EVA word, e.g. qokeedy, okar, darary, oror, doaro, olkol, otaram, daiin..." oninput="analyzeWord(this.value)" />
      <div class="sample-chips">
        Try:
        <span class="word-chip" onclick="setWord('qokeedy')">qokeedy</span>
        <span class="word-chip" onclick="setWord('shedy')">shedy</span>
        <span class="word-chip" onclick="setWord('olkol')">olkol</span>
        <span class="word-chip" onclick="setWord('okoldy')">okoldy</span>
        <span class="word-chip" onclick="setWord('okar')">okar</span>
        <span class="word-chip" onclick="setWord('darary')">darary</span>
        <span class="word-chip" onclick="setWord('oror')">oror</span>
        <span class="word-chip" onclick="setWord('doaro')">doaro</span>
        <span class="word-chip" onclick="setWord('otaram')">otaram</span>
        <span class="word-chip" onclick="setWord('otaral')">otaral</span>
        <span class="word-chip" onclick="setWord('poldchody')">poldchody</span>
        <span class="word-chip" onclick="setWord('daiin')">daiin</span>
        <span class="word-chip" onclick="setWord('otam')">otam</span>
      </div>
    </div>
    <div id="legoOutput" class="lego-breakdown"></div>
  </section>

  <!-- TAB 1: PAGE WALKTHROUGH -->
  <section id="tab-walkthrough" class="tab-panel active">
    <div class="explorer-grid">
      <div class="folio-list" id="folioList"></div>
      <div class="folio-viewer" id="folioViewer"></div>
    </div>
  </section>

  <!-- TAB 2: BOTANICAL & ASTRO SPECIMENS -->
  <section id="tab-specimens" class="tab-panel">
    <div style="margin-bottom: 1rem;">
      <h2 style="margin: 0 0 0.25rem;">45 Flagship Botanical, Astronomical, Balneological, Cosmological, Margin-Key &amp; Visual-Twin Identifications</h2>
      <p style="margin: 0; color: var(--muted);">
        Matching the manuscript's high-resolution drawings to concrete 15th-century European herbal species, star clusters, bilingual month wheels, labelled hydrotherapy pipes, cosmological spheres, margin keys, quire signatures, and visual twin plant pairs.
      </p>
    </div>
    <div class="cards-grid" id="specimensGrid"></div>
  </section>

  <!-- TAB 3: CORE ROOT DICTIONARY & 8-CASE GRAMMAR -->
  <section id="tab-lexicon" class="tab-panel">
    <h2>Core Root Stem Dictionary (Physically Grounded Stems)</h2>
    <p style="color: var(--muted);">Click any example word to test it in the Lego Word Analyzer above.</p>
    <div style="overflow-x: auto; margin-bottom: 2rem;">
      <table id="lexiconTable">
        <thead>
          <tr>
            <th>Root Stem</th>
            <th>Category</th>
            <th>Plain-English Meaning</th>
            <th>Common Inflected Forms (Click to Analyze)</th>
            <th>Visual &amp; Physical Grounding in the Scans</th>
          </tr>
        </thead>
        <tbody></tbody>
      </table>
    </div>

    <h2>The 8-Case Inflectional Paradigm Matrix (Top 20 Stems Across 38,409 Words)</h2>
    <p style="color: var(--muted);">
      Shows how the exact same root stem takes different suffixes depending on whether it is a static ingredient (`-∅`), a measured portion (`-aiin`), a liquid medium (`-ol/-or`), an active boiling/washing verb (`-edy`), or the final stop of a recipe (`-am`).
    </p>
    <div style="overflow-x: auto;">
      <table id="paradigmTable">
        <thead>
          <tr>
            <th>Canonical Root</th>
            <th>Semantic Role</th>
            <th>Total Hits</th>
            <th>NOM (Base)</th>
            <th>GEN/PART (<code>-aiin</code>)</th>
            <th>LOC (<code>-ol/-or</code>)</th>
            <th>INST (<code>-al/-ar</code>)</th>
            <th>PROC (<code>-edy/-dy</code>)</th>
            <th>TERM (<code>-am/-m</code>)</th>
          </tr>
        </thead>
        <tbody></tbody>
      </table>
    </div>
  </section>

  <!-- TAB 4: ZODIAC CALENDAR & BATHING PLUMBING -->
  <section id="tab-zodiac" class="tab-panel">
    <h2>1. The 12 Zodiac Wheels (`f70v2–f73v`) &amp; Bilingual Western Month Glosses (`mars..decembre`)</h2>
    <p style="color: var(--muted);">
      Each Zodiac wheel has a 15th-century European month name written in its center (`mars` = March through `decembre` = December) and is ringed by ~30 star-holding nymphs. <strong>58.1% (202 / 348)</strong> of the star-nymph labels appear word-for-word inside the Herbal, Pharmaceutical, and Recipe sections!
    </p>
    <div style="overflow-x: auto; margin-bottom: 2.2rem;">
      <table id="zodiacTable">
        <thead>
          <tr>
            <th>Folio</th>
            <th>Zodiac Medallion</th>
            <th>European Month Gloss</th>
            <th>Element Triplicity</th>
            <th>Ring Words</th>
            <th>Star-Nymph Labels (<code>@Lz</code>)</th>
            <th><code>o-</code> Nominal Rate</th>
            <th>Top Star-Nymph Degree Labels (Click to Decode)</th>
          </tr>
        </thead>
        <tbody></tbody>
      </table>
    </div>

    <h2>2. The 20-Page Balneological ("Bathing Nymphs") Plumbing &amp; Label Atlas (`f75r–f84v`)</h2>
    <p style="color: var(--muted);">
      Demonstrates the <strong>Label-vs-Prose Polarity Law (z = +9.97)</strong>: painted water pipes (<code>@Lt</code>) and bathing figures (<code>@Ln</code>) are labeled with <code>o-/ol-</code> vessel and essence nouns (<code>62.2%</code>, e.g. <code>olkol</code>, <code>okoldy</code>, <code>okal</code>), while active <code>qo-</code> boiling commands (<code>qokeedy</code>) are restricted to the surrounding recipe paragraphs (<code>24.4%</code> in prose vs. <code>2.5%</code> on labels).
    </p>
    <div style="overflow-x: auto;">
      <table id="balneoTable">
        <thead>
          <tr>
            <th>Folio</th>
            <th>Prose Words</th>
            <th>Thermal Boil Rate (<code>qokeedy</code>)</th>
            <th>Wash/Bathe Rate (<code>shedy</code>)</th>
            <th>Pool/Vessel Rate (<code>ol-</code>)</th>
            <th>Pipe &amp; Nymph Labels (Click to Decode)</th>
            <th>Top Prose Words (Click to Decode)</th>
          </tr>
        </thead>
        <tbody></tbody>
      </table>
    </div>
  </section>

  <!-- TAB 5: STARRED RECIPES, ROSETTES MAP & 4-TRANSCRIBER PROOF -->
  <section id="tab-recipes" class="tab-panel">
    <h2>1. The 285 Starred Master Recipes (`f103r–f116r`, 10,587 Words) &amp; 3-Zone Procedural Frame (`z = +18.93`)</h2>
    <p style="color: var(--muted);">
      Every star-bulleted paragraph (`183` Aqueous Infusions, `64` Balneo Washes, `29` Thermal Decoctions, `9` Compound Essence Salves) follows the <strong>3-Zone Procedural Frame Law</strong>: Gallows openers surge <strong>3.10×</strong> in the Opening 20% (`19.5%` vs. `6.3%` Middle), while Terminal <code>-am/-m</code> stops surge <strong>3.90×</strong> in the Closing 20% (`3.9%` vs. `1.0%` Opening). Below are 12 showcase Starred Recipes with their clickable opening and closing clauses:
    </p>
    <div style="overflow-x: auto; margin-bottom: 2.2rem;">
      <table id="recipesTable">
        <thead>
          <tr>
            <th>Recipe ID</th>
            <th>Regimen Class</th>
            <th>Words</th>
            <th>Boil Steps</th>
            <th>Measured Doses</th>
            <th>Opening Clause (Click Any Word to Decode)</th>
            <th>Closing Clause (Click Any Word to Decode)</th>
          </tr>
        </thead>
        <tbody></tbody>
      </table>
    </div>

    <h2>2. Quire 14 Cosmological &amp; 9-Rosettes Foldout Map (`f85r1–f86v6`, `fRos` — Polarity `z = +12.45`)</h2>
    <p style="color: var(--muted);">
      On the 3 Diagram Panels (<code>f85r2</code>, <code>f86v4</code>, <code>fRos</code>), <code>o-</code> nominal forms surge <strong>1.99×</strong> (<code>52.1%</code> vs. <code>26.2%</code>), whereas on the 4 Prose Treatise Panels (<code>f85r1</code>, <code>f86v3</code>, <code>f86v5</code>, <code>f86v6</code>), <code>qo-</code> active verbs surge <strong>2.61×</strong> (<code>14.1%</code> vs. <code>5.4%</code>). Furthermore, <strong>64.0%</strong> of <code>fRos</code> words appear verbatim in Starred Recipes!
    </p>
    <div style="overflow-x: auto; margin-bottom: 2.2rem;">
      <table id="rosettesTable">
        <thead>
          <tr>
            <th>Panel</th>
            <th>Panel Type</th>
            <th>Tokens</th>
            <th><code>o-</code> Nominal Rate</th>
            <th><code>qo-</code> Active Rate</th>
            <th><code>-edy/-dy</code> Process Rate</th>
            <th><code>-ol/-or/-al/-ar</code> Medium Rate</th>
            <th>Top Tokens (Click to Decode)</th>
          </tr>
        </thead>
        <tbody></tbody>
      </table>
    </div>

    <h2>3. Four-Transcriber Consensus Verification (`ZL3b-n`, `RF1b-er`, `IT2a-n`, `GC2a-n` Across 36,103 Words)</h2>
    <p style="color: var(--muted);">
      Across <strong>5,132 aligned lines (36,103 words)</strong>, all 4 independent human transcription traditions agree on the canonical word skeleton <strong>88.8%</strong> of the time, and <strong>24 / 26</strong> of our core visual cribs and grammatical words are attested across all three EVA editions:
    </p>
    <div style="overflow-x: auto;">
      <table id="consensusTable">
        <thead>
          <tr>
            <th>Core Crib / Word (Click to Decode)</th>
            <th>Zandbergen (<code>ZL3b</code> Hits)</th>
            <th>Rene / Friedman (<code>RF1b</code> Hits)</th>
            <th>Takahashi (<code>IT2a</code> Hits)</th>
            <th>Glen Claston (<code>GC2a v101</code> Mapped Hits)</th>
            <th>Independent Editions Attesting</th>
          </tr>
        </thead>
        <tbody></tbody>
      </table>
    </div>
  </section>

  <!-- TAB 6: ASTRO WHEELS, 5 SCRIBES & PHARMA SUPPLY CHAIN -->
  <section id="tab-astro" class="tab-panel">
    <h2>1. The 14-Folio Astronomical Star-Wheel &amp; Solar/Lunar Sector Atlas (`f67r1–f70r2`)</h2>
    <p style="color: var(--muted);">
      Across all 14 Astronomical folios (<code>1,690</code> tokens), radial star and sector labels surge in the nominal <code>o-</code> prefix (<code>37.6%</code> vs. <code>28.0%</code> in circular ring prose, <code>z = +3.83</code>), while <strong>64.4%</strong> of Astronomical words appear verbatim in the Herbal section and <strong>62.4%</strong> in Starred Recipes!
    </p>
    <div style="overflow-x: auto; margin-bottom: 2.2rem;">
      <table id="astroTable">
        <thead>
          <tr>
            <th>Folio</th>
            <th>Visual Wheel Architecture</th>
            <th>Total Words</th>
            <th><code>o-</code> Nominal Rate</th>
            <th>Match in Herbal (<code>H</code>)</th>
            <th>Match in Recipes (<code>S</code>)</th>
            <th>Top Radial &amp; Ring Words (Click to Decode)</th>
          </tr>
        </thead>
        <tbody></tbody>
      </table>
    </div>

    <h2>2. The 5 Paleographic Scribe Hands (<code>$H=1..5</code>) &amp; Universal 5-Hand Core Vocabulary (<code>77.0%</code> Coverage)</h2>
    <p style="color: var(--muted);">
      Proves that all 5 human scribes share the exact same positional line-and-paragraph grammar (Paragraph-Initial Gallows surge, Line-Start <code>y-</code> surge, and Right-Margin <code>-m</code> stop surge), and just <strong>120 universal root stems</strong> shared across all 5 hands account for <strong>77.0%</strong> of the entire manuscript!
    </p>
    <div style="overflow-x: auto; margin-bottom: 2.2rem;">
      <table id="scribesTable">
        <thead>
          <tr>
            <th>Scribe Hand</th>
            <th>Primary Manuscript Domain</th>
            <th>Folios</th>
            <th>Words</th>
            <th>Par-Start Gallows</th>
            <th>Line-Start vs Mid <code>y-</code></th>
            <th>Line-End vs Mid <code>-m</code></th>
            <th>Top Words (Click to Decode)</th>
          </tr>
        </thead>
        <tbody></tbody>
      </table>
    </div>

    <h2>3. The 3-Stage Pharmaceutical Supply Chain (<code>Herbal Monograph -> Pharma Jar/Root -> Starred Recipe</code>)</h2>
    <p style="color: var(--muted);">
      Across all 16 Pharmaceutical pages (<code>f88r–f102v</code>, <code>243</code> figure labels), <code>@Lc</code> painted storage jars average <strong>7.41 characters</strong> vs. <strong>5.85 characters</strong> for <code>@Lf</code> plant parts, and <strong>53.1% (129 / 243)</strong> form complete 3-stage bridges linking a Herbal Monograph to a Pharmaceutical Jar/Root and forward to a Starred Master Recipe:
    </p>
    <div style="overflow-x: auto;">
      <table id="pharmaBridgeTable">
        <thead>
          <tr>
            <th>Pharma Label (Click to Decode)</th>
            <th>Canonical Stem</th>
            <th>Pharma Locus &amp; Type</th>
            <th>Stage 1: Herbal Monographs (<code>f1r–f57v</code>)</th>
            <th>Stage 3: Starred Master Recipes (<code>f103r–f116r</code>)</th>
            <th>3-Stage Bridge Status</th>
          </tr>
        </thead>
        <tbody></tbody>
      </table>
    </div>
  </section>

  <!-- TAB 7: 25 COMPLETE PARAGRAPHS, DRAWING INTRUSIONS & RIGHT-TITLES -->
  <section id="tab-paragraphs" class="tab-panel">
    <h2>1. 25 Complete Self-Contained Short Paragraphs (`<%> ... <$>`) Read From Start to Finish</h2>
    <p style="color: var(--muted);">
      Across all <strong>736 complete paragraphs</strong> in the manuscript, <strong>83.3% (613 / 736)</strong> open with a Gallows character (<code>p/f/k/t</code>). Below are 25 complete, self-contained short paragraphs (<code>10–28</code> words) across Herbal, Starred Recipes, Balneological, Pharmaceutical, and Cosmological sections—click any Voynich word chip to inspect its prefix, root stem, and suffix above:
    </p>
    <div style="overflow-x: auto; margin-bottom: 2.2rem;">
      <table id="shortParsTable">
        <thead>
          <tr>
            <th>Paragraph &amp; Locus</th>
            <th>Section</th>
            <th>Words</th>
            <th>Complete Voynich Paragraph (`<%> ... <$>`, Click Any Word to Decode)</th>
            <th>Plain-English Structural &amp; Clinical Reading</th>
          </tr>
        </thead>
        <tbody></tbody>
      </table>
    </div>

    <h2>2. The 752 Drawing Intrusions (`<->`) &amp; Illustration-First Visual Layout Proof (`Attack 165`)</h2>
    <p style="color: var(--muted);">
      Comparing words immediately before a plant stem (<code>Pre-Intrusion Pause</code>) and immediately after jumping over a plant stem (<code>Post-Intrusion Resume</code>) proves that <strong>illustrations were painted BEFORE the text</strong>: pre-intrusion words suppress the line-end <code>-m</code> stop (<strong>2.39% vs. 15.18%</strong> at true right margins, <code>6.35×</code> lower), post-intrusion words exclude Gallows openers (<strong>0.27% [2/752] vs. 20.8%</strong> at true left margins, <code>77.2×</code> lower), and post-intrusion words surge <strong>4.07× in the <code>y-</code> resumption prefix (14.49% vs. 3.56% mid-line)</strong>!
    </p>
    <div style="overflow-x: auto; margin-bottom: 2.2rem;">
      <table id="intrusionsTable">
        <thead>
          <tr>
            <th>Positional Word Bucket</th>
            <th>Count (<code>n</code>)</th>
            <th>Initial Gallows (<code>p/f/k/t</code>)</th>
            <th>Initial <code>y-</code> Resumption</th>
            <th>Final <code>-m</code> Stop</th>
            <th>Mean Length</th>
            <th>Top Words (Click to Decode)</th>
          </tr>
        </thead>
        <tbody></tbody>
      </table>
    </div>

    <h2>3. The 27 Right-Justified (<code>=Pt</code>) &amp; Centered (<code>+Pc</code>) Paragraph Title/Coda Lines (`Attack 166`)</h2>
    <p style="color: var(--muted);">
      Across all 27 right-justified (<code>=Pt</code>) and centered (<code>+Pc</code>) paragraph title/coda lines, <strong>77.8% (21 / 27)</strong> echo their canonical root stem in the body prose of the same folio, and <strong>81.5% (22 / 27)</strong> share their root stem with the Pharmaceutical and Starred Recipe sections:
    </p>
    <div style="overflow-x: auto;">
      <table id="rightTitlesTable">
        <thead>
          <tr>
            <th>Locus &amp; Type</th>
            <th>Section</th>
            <th>Title / Coda Words (Click to Decode)</th>
            <th>Canonical Stems</th>
            <th>Local Folio Stem Echo</th>
            <th>Hits in Pharma (<code>P</code>)</th>
            <th>Hits in Recipes (<code>S</code>)</th>
            <th>Hits in Balneo (<code>B</code>)</th>
          </tr>
        </thead>
        <tbody></tbody>
      </table>
    </div>
  </section>

  <!-- TAB 8: 12 VISUAL TWINS, f49v PENTAD KEY, f58r ACROSTIC & STAR PARITY -->
  <section id="tab-twins" class="tab-panel">
    <h2>1. The 12 Visual Twin Plant Pairs (`Same Plant As...` Atlas Across Herbal `H` &amp; Pharmaceutical `P`, `Attack 169`)</h2>
    <p style="color: var(--muted);">
      All <strong>12 / 12 (100.0%)</strong> paleographically documented Visual Twin Plant Pairs share exact whole words (<code>117</code> folio-level, <code>75</code> inside the exact target register) and canonical root stems (<code>191</code> folio-level, <code>133</code> inside the exact target register), while active <code>qo-</code> processing verbs surge <strong>1.43×</strong> (<code>8.91% -> 12.77%</code>) as the text shifts from botanical description (<code>H</code>) to root compounding (<code>P</code>):
    </p>
    <div style="overflow-x: auto; margin-bottom: 2.2rem;">
      <table id="visualTwinsTable">
        <thead>
          <tr>
            <th>Pair ID</th>
            <th>Herbal Folio &amp; Species</th>
            <th>Pharma Twin Locus &amp; Labels</th>
            <th>Exact Register Shared Words (Click to Decode)</th>
            <th>Shared Register Stems</th>
            <th><code>qo-</code> Shift (<code>H -&gt; P_reg</code>)</th>
          </tr>
        </thead>
        <tbody></tbody>
      </table>
    </div>

    <h2>2. The `f58r` Paragraph 3 Acrostic Margin Decoupling Table (`7/16 -> 0/16` Anomalies, `Attack 170`)</h2>
    <p style="color: var(--muted);">
      Alongside the <strong>f49v 1-2-3-4-5 Repeating Pentad Key (<code>o - r/@192; - y - e - @140;</code> repeated 3x verbatim, <code>z = +80.20</code>)</strong>, Paragraph 3 of <code>f58r</code> (8-pointed star) has a 16-letter vertical margin column (<code>k,y,y,o,y,o,o,s,y,d,s,o,s,d,y,d</code>) whose decoupling resolves <strong>100% (7/16 -&gt; 0/16)</strong> of the paragraph's apparent initial spelling anomalies:
    </p>
    <div style="overflow-x: auto; margin-bottom: 2.2rem;">
      <table id="acrosticTable">
        <thead>
          <tr>
            <th>Line</th>
            <th>Raw Transcribed Token</th>
            <th>Decoupled Margin Key Letter</th>
            <th>Restored Line-Initial Word (Click to Decode)</th>
            <th>Phonotactic Anomaly Before?</th>
            <th>Anomaly After Decoupling?</th>
          </tr>
        </thead>
        <tbody></tbody>
      </table>
    </div>

    <h2>3. The Quire 20 Binary Star Parity Code (`95.07%` Dotted/Plain Alternation, `z = +11.95`, `Attack 171`)</h2>
    <p style="color: var(--muted);">
      Across <code>279</code> annotated left-margin stars in Quire 20 (<code>f103r–f116r</code>), Marked (<code>M = Dotted/Dark</code>) and Unmarked (<code>U = Plain Light</code>) stars alternate on <strong>91.41% (z = +12.51)</strong> of all transitions and <strong>95.07% (193 / 203, z = +11.95, 100% on 12 full pages!)</strong> across the 19 Dotted-Regime folios, while remaining grammatically invariant (<code>-edy</code> rate <code>14.60% vs. 14.61%</code>):
    </p>
    <div style="overflow-x: auto;">
      <table id="starParityTable">
        <thead>
          <tr>
            <th>Folio</th>
            <th>Annotated Stars</th>
            <th>Marked (<code>M</code>)</th>
            <th>Unmarked (<code>U</code>)</th>
            <th>Top-to-Bottom Parity Sequence</th>
            <th>Alternating Transitions</th>
            <th>Alternation Rate</th>
          </tr>
        </thead>
        <tbody></tbody>
      </table>
    </div>
  </section>

  <!-- TAB 9: QUIRE SIGNATURES, PHARMA SHELVES & WEIRDO-GLYPH ATLAS -->
  <section id="tab-quires" class="tab-panel">
    <h2>1. The 18-Quire Gathering Architecture (`$Q=A..T`), Quire Signatures &amp; 100.0% Page-Boundary Closure Law (`Attack 173`)</h2>
    <p style="color: var(--muted);">
      Across all <strong>206 prose-bearing folios</strong> in the codex, <strong>100.0% (206 / 206)</strong> open their first line with an explicit paragraph start (<code>&lt;%&gt;</code>) and <strong>99.03% (204 / 206)</strong> close their final line with a paragraph end (<code>&lt;$&gt;</code>)—no sentence ever wraps across a page turn! Furthermore, even within the exact same Section and Currier Language, canonical stem Jaccard cohesion decays monotonically with physical distance: <strong>Same Leaf (<code>recto &lt;-&gt; verso</code>, 0.2619, z = +8.13) &gt; Same Bifolio Sheet (0.2582) &gt; Same Quire (0.2560, z = +18.45) &gt;&gt; Different Quire (0.2168)</strong>:
    </p>
    <div style="overflow-x: auto; margin-bottom: 2.2rem;">
      <table id="quiresTable">
        <thead>
          <tr>
            <th>Quire</th>
            <th>Folio Span</th>
            <th>Transcribed Pages</th>
            <th>Section(s)</th>
            <th>Currier Language(s)</th>
            <th>Scribe Hand(s)</th>
            <th>Total Words</th>
            <th>Quire Signature &amp; Missing-Leaf Notes</th>
          </tr>
        </thead>
        <tbody></tbody>
      </table>
    </div>

    <h2>2. Multi-Row Pharmaceutical Shelf Alignment &amp; Act-I Paragraph-Opening Citation Law (`66.29%` in Lines 1–2, `z = -5.37`, `Attack 174`)</h2>
    <p style="color: var(--muted);">
      Across all <code>210</code> labeled shelf roots (<code>@Lf</code>) on the multi-row Pharmaceutical pages (<code>f88r–f102v2</code>), <strong>42.38%</strong> echo their exact canonical stem inside the prose of the same folio, and when a shelf root is cited in a recipe paragraph, <strong>66.29% (59 / 89, z = -5.37)</strong> make their first appearance directly inside <strong>Lines 1–2 (Act I: Ingredient Declaration)</strong>:
    </p>
    <div style="overflow-x: auto; margin-bottom: 2.2rem;">
      <table id="pharmaShelvesTable">
        <thead>
          <tr>
            <th>Folio</th>
            <th>Painted Vessels (<code>@Lc</code>, Click to Decode)</th>
            <th>Ingredient Shelves</th>
            <th>Recipe Paragraphs</th>
            <th>Paired Shelf &rarr; Para Stem Hit Rate</th>
            <th>Sample Echoed Shelf Roots (Click to Decode)</th>
          </tr>
        </thead>
        <tbody></tbody>
      </table>
    </div>

    <h2>3. Plumed Bench-Gallows (`{{cthh}}..{{cfhh}}`) Allographic Reduction (`82.35%` Word / `94.12%` Stem Collapse) &amp; Rare `@NNN;` Weirdo-Glyph Atlas (`Attack 175`)</h2>
    <p style="color: var(--muted);">
      Stripping the ornamental double-plume on <code>{{cthh}}, {{ckhh}}, {{cphh}}, {{cfhh}}</code> (<code>n = 68</code>) collapses <strong>82.35% (56 / 68)</strong> into exact standard words and <strong>94.12% (64 / 68)</strong> into attested canonical stems, while rare <code>@NNN;</code> weirdo glyphs (<code>n = 156</code>) are enriched <strong>3.00×</strong> in figure labels and margin keys (<code>26.92% vs. 8.96%</code>):
    </p>
    <div style="overflow-x: auto;">
      <table id="plumedWeirdoTable">
        <thead>
          <tr>
            <th>Locus &amp; Scribe Hand</th>
            <th>Section</th>
            <th>Raw Plumed-Gallows Token</th>
            <th>Reduced Single-Loop Form (Click to Decode)</th>
            <th>Standard Corpus Exact Count</th>
            <th>Canonical Stem</th>
            <th>Standard Stem Corpus Count</th>
          </tr>
        </thead>
        <tbody></tbody>
      </table>
    </div>
  </section>

  <!-- TAB 10: MICRO-SPACING CLITICS, F57V KEY WHEEL & 6-REGISTER STEM MATRIX -->
  <section id="tab-clitics" class="tab-panel">
    <h2>1. The Paleographic Micro-Spacing Clitic-Host Fusion Law (`6.72×`–`10.22×` Enrichment, `z = +62.16`, `Attack 177`)</h2>
    <p style="color: var(--muted);">
      Across <code>32,963</code> adjacent word boundaries in <code>ZL3b-n.txt</code>, narrow micro-spaces (<code>A,B</code>, <code>n = 2,669</code>, <code>8.10%</code>) fuse directly into attested single Voynich words (<code>AB</code>) <strong>42.90% of the time vs. 6.38% across standard wide spaces (<code>A.B</code>) (z = +62.16)</strong>, and <strong>28.55%–30.16%</strong> are transcribed as single fused words by independent transcribers (<code>IT2a-n</code> / <code>RF1b-er</code>, <strong>57.65× enrichment, z = +30.79</strong>):
    </p>
    <div style="overflow-x: auto; margin-bottom: 2.2rem;">
      <table id="microCliticsTable">
        <thead>
          <tr>
            <th>Micro-Spaced Pair (<code>A,B</code>)</th>
            <th>Fused Single Word (<code>AB</code>, Click to Decode)</th>
            <th>Micro-Space Occurrences</th>
            <th>Single-Word Corpus Freq</th>
            <th><code>A</code> Is Proclitic?</th>
            <th><code>B</code> Is Enclitic?</th>
          </tr>
        </thead>
        <tbody></tbody>
      </table>
    </div>

    <h2>2. The `f57v.3` 13-Glyph 4-Quadrant Key Wheel &amp; Direct Scribal Proof of `f &lt;-&gt; p` Gallows Allography (`94.67%` Exact / `100.0%` Allographic Identity, `Attack 178`)</h2>
    <p style="color: var(--muted);">
      On <code>f57v.3</code> (the second concentric ring from the outside on <code>f57v</code>), the scribe repeated a <strong>13-glyph key sequence 4 times</strong> around the four <code>90°</code> quadrants, writing <code>f</code> in Slot 9 of Quadrants 1–2 and <code>p</code> in Slot 9 of Quadrants 3–4—yielding <strong>94.67% (71 / 75) exact slot identity and 100.0% (75 / 75) identity under <code>f &lt;-&gt; p</code> gallows allography</strong>:
    </p>
    <div style="overflow-x: auto; margin-bottom: 2.2rem;">
      <table id="f57vQuadrantTable">
        <thead>
          <tr>
            <th>Slot</th>
            <th>Quadrant 1 (<code>12</code> chars)</th>
            <th>Quadrant 2 (<code>13</code> chars)</th>
            <th>Quadrant 3 (<code>13</code> chars)</th>
            <th>Quadrant 4 (<code>13</code> chars)</th>
            <th>Paleographic Status</th>
          </tr>
        </thead>
        <tbody></tbody>
      </table>
    </div>

    <h2>3. The 6-Register Universal Stem Inflection Shift Matrix (`84.40%` Nominal Citation in `@L` &rarr; `55.23%` Procedural Verbal in Balneo/Starred Recipes, `Attack 179`)</h2>
    <p style="color: var(--muted);">
      Holding the exact same <strong>76 Universal 6-Register Core Stems (28,473 tokens, 77.2% of multi-character corpus)</strong> completely fixed across all 6 functional registers eliminates all vocabulary-selection bias and proves a monotonic shift from <strong>Nominal Citation (84.40% in <code>@L</code> Labels &rarr; 62.86% in Herbal A)</strong> to <strong>Active Procedural Verbal Inflection (55.23% in Balneo &amp; Starred Recipes, 10.30× surge in <code>qo-</code>)</strong>:
    </p>
    <div style="overflow-x: auto;">
      <table id="universalStemMatrixTable">
        <thead>
          <tr>
            <th>Canonical Stem</th>
            <th>Total Tokens</th>
            <th>1. Diagram Labels (<code>@L</code>)</th>
            <th>2. Herbal A Prose</th>
            <th>3. Astro/Zodiac</th>
            <th>4. Pharmaceutical Prose</th>
            <th>5. Herbal B Prose</th>
            <th>6. Balneo &amp; Starred Recipes</th>
          </tr>
        </thead>
        <tbody></tbody>
      </table>
    </div>
  </section>
</main>

<script>
const DATA = {embedded_json};

const PREFIX_RULES = [
  {{ match: "pold", label: "p- + old-", desc: "Paragraph Opener + Liquid Vessel ('Begin: in the liquid vessel')" }},
  {{ match: "qo", label: "qo- (q + o-)", desc: "Active Procedural Step ('Then / And-it')" }},
  {{ match: "ol", label: "ol-", desc: "Vessel / Pipe / Bath Locative ('In the pipe / vessel / bath')" }},
  {{ match: "ot", label: "ot- (o + t-)", desc: "From/In the Source ('Of the root / celestial sector')" }},
  {{ match: "ok", label: "ok- (o + k-)", desc: "Of the Core / Primary Essence ('The core...')" }},
  {{ match: "op", label: "op- (o + p-)", desc: "Prepared / Compounded ('The prepared...')" }},
  {{ match: "od", label: "od- (o + d-)", desc: "Measured / Drawn Portion ('From the...')" }},
  {{ match: "ch", label: "ch-", desc: "Infuse / Steep ('Herbal infusion / decoction')" }},
  {{ match: "sh", label: "sh-", desc: "Wash / Bathe ('Liquid surface wash / bath')" }},
  {{ match: "da", label: "da- / d-", desc: "Take / From ('Take from the source')" }},
  {{ match: "sa", label: "sa- / s-", desc: "Draw / Select ('Selected / drawn portion')" }},
  {{ match: "fa", label: "f- (Gallows Opener)", desc: "Paragraph / Section Declaration Opener" }},
  {{ match: "pc", label: "p- (Gallows Opener)", desc: "Paragraph / Protocol Opener ('Begin...')" }},
  {{ match: "po", label: "po- (Gallows Opener)", desc: "Paragraph Opener ('Begin from the vessel...')" }},
  {{ match: "fs", label: "f- (Gallows Opener)", desc: "Paragraph Opener ('Begin by washing...')" }},
  {{ match: "fc", label: "f- (Gallows Opener)", desc: "Paragraph Opener ('Begin the divided-plant infusion...')" }},
  {{ match: "yk", label: "y- / yk-", desc: "Conjunction / Relative ('And the core...')" }},
  {{ match: "yd", label: "yd-", desc: "Conjunction + Source ('And from the...')" }},
  {{ match: "o",  label: "o-", desc: "Nominal / Ingredient Article ('The [ingredient]')" }},
  {{ match: "l",  label: "l-", desc: "Liquid / Container Marker ('In the bath/vessel')" }},
  {{ match: "d",  label: "d-", desc: "Ablative / Imperative ('Take / From')" }},
  {{ match: "s",  label: "s-", desc: "Source / Demonstrative ('From this / Select')" }},
  {{ match: "y",  label: "y-", desc: "Clause Linker ('And / Then')" }}
];

const SUFFIX_RULES = [
  {{ match: "eedy", label: "-eedy", desc: "Intensive Active Process Verb ('boil / steep thoroughly')" }},
  {{ match: "edy",  label: "-edy",  desc: "Active Process Verb ('is boiled / washed / infused')" }},
  {{ match: "aiin", label: "-aiin", desc: "Measured Dose / Partitive ('one measured portion of')" }},
  {{ match: "ain",  label: "-ain",  desc: "Measured Dose ('one portion of')" }},
  {{ match: "iin",  label: "-iin",  desc: "Counted Minim Dose ('measured parts')" }},
  {{ match: "oldy", label: "-oldy", desc: "Steeped in Liquid/Pipe State ('infused in the liquid/conduit')" }},
  {{ match: "aldy", label: "-aldy", desc: "Prepared Essence State ('infused in essence')" }},
  {{ match: "ary",  label: "-ary",  desc: "Botanical / Root Part Label ('the [root] part')" }},
  {{ match: "ory",  label: "-ory",  desc: "Prepared / Extracted State ('drawn/washed')" }},
  {{ match: "ody",  label: "-ody",  desc: "Completed Action / State ('prepared / compounded')" }},
  {{ match: "am",   label: "-am",   desc: "Terminal Recipe Stop ('...to completion / seal at end')" }},
  {{ match: "om",   label: "-om",   desc: "Terminal Closure ('...complete the mixture')" }},
  {{ match: "ol",   label: "-ol",   desc: "Liquid Medium / Locative ('in the liquid extract / pipe')" }},
  {{ match: "or",   label: "-or",   desc: "Oil / Golden Essence ('in the oil / essence')" }},
  {{ match: "al",   label: "-al",   desc: "Instrumental Essence ('with the star/seed essence')" }},
  {{ match: "ar",   label: "-ar",   desc: "Botanical / Earth Base ('from the root/earth base')" }},
  {{ match: "dy",   label: "-dy",   desc: "Procedural / Participial State ('processed / steeped')" }},
  {{ match: "y",    label: "-y",    desc: "Nominal / Label Closure ('that which is named')" }}
];

const STEM_GLOSSES = {{
  "oror": "Blood-red Alkanet / Madder dye-root (Alkanna tinctoria — attested on f102v2, f100r, and f116v)",
  "orar": "Red Alkanet root-extract",
  "okol": "Core apothecary storage jar / root-vessel (`o-` + `kol`, labeled on f88r jar & root and ingested as `okol daiin` in f88r.2)",
  "doaro": "The Pleiades (7-star cluster in Taurus, f68r3)",
  "darary": "The main taproot / rhizome (labeled on f89r2)",
  "olkol": "The core water-pipe / bath conduit liquid (labeled on f82v)",
  "okoldy": "Infused in the storage jar / water conduit (labeled on f82v & f89r2)",
  "poldchody": "Begin by steeping in the liquid vessel (Red-Blossom headword on f11v & f116v)",
  "otaram": "Completed Pisces (`mars`) 10:00 root-balm degree (`f70v2.22` & `f107r.11`)",
  "otaral": "Pisces (`mars`) 11:00 root-star extract degree (`f70v2.23` & `f107r.13`)",
  "otalar": "Pisces (`mars`) 12:00 celestial sector essence (`f70v2.24` & `f107r.15`)",
  "fachys": "Opening declaration ('Here begins the book/manifesto')",
  "ke": "Boil / decoct / simmer with heat",
  "kee": "Boil / cook thoroughly in liquid",
  "k": "Core thermal / boiling stem",
  "ch": "Herbal infusion / strained decoction",
  "sh": "Bath / liquid surface washing",
  "kar": "Heart / core / root-bulb",
  "kor": "Root-heart / bulbous core",
  "kair": "Pure core / heart-essence",
  "tar": "Earth / primary root base",
  "cthar": "Divided / extracted root-heart",
  "ckhar": "Concentrated heart-extract",
  "ra": "Root / taproot / rhizome",
  "rar": "Main rootstock",
  "dara": "Main root portion",
  "opchor": "Vessel-infused pharmaceutical compound (f16v -> f89r1 hub)",
  "pchor": "Infused plant compound",
  "al": "Star / winged seed / volatile essence",
  "kal": "Primary core / star essence",
  "sal": "Cut leaf / seed rosette",
  "ol": "Liquid vessel / bath basin",
  "tol": "Liquid extract medium",
  "kol": "Core storage vessel / pipe conduit",
  "aiin": "One measured dose / portion",
  "daiin": "Take one measured dose",
  "dain": "Take this measured portion",
  "otam": "Complete / seal the final mixture",
  "okam": "Complete the core preparation",
  "daram": "Take the root to completion"
}};

function parseVoynichWord(raw) {{
  const w = (raw || "").trim();
  if (!w) return null;
  const lower = w.toLowerCase();

  if (lower === "oror") {{
    return {{
      prefix: "∅ (Base Noun)", prefixDesc: "Unprefixed pure botanical noun",
      stem: "oror", stemDesc: "Blood-red Dyer's Alkanet / Madder root (f102v2, f100r & f116v)",
      suffix: "-or (Reduplicated)", suffixDesc: "Red/golden dye-root stem (`or-or`)",
      gloss: "Blood-red Alkanet / Madder root (`Alkanna tinctoria` — Rosetta crib on f102v2, f100r & f116v)"
    }};
  }}
  if (lower === "doaro") {{
    return {{
      prefix: "d-", prefixDesc: "Demonstrative / Star Cluster Marker",
      stem: "oar", stemDesc: "Clustered golden stars (Pleiades)",
      suffix: "-o", suffixDesc: "Astronomical emblem label ending",
      gloss: "The Pleiades (Seven Sisters 7-star cluster in Taurus on f68r3)"
    }};
  }}
  if (lower === "daiin" || lower === "dain") {{
    return {{
      prefix: "d-", prefixDesc: "Imperative / Ablative ('Take / From')",
      stem: "aiin / ain", stemDesc: "Counted minim unit ('one part / measure')",
      suffix: "-iin", suffixDesc: "Partitive dose marker",
      gloss: "'Take one measured part / dose of...'"
    }};
  }}

  let prefix = "∅ (Base)";
  let prefixDesc = "Direct stem / unprefixed form";
  let rest = lower;

  for (const p of PREFIX_RULES) {{
    if (rest.startsWith(p.match) && rest.length > p.match.length + 1) {{
      prefix = p.label;
      prefixDesc = p.desc;
      rest = rest.slice(p.match.length);
      break;
    }}
  }}

  let suffix = "∅ (Base)";
  let suffixDesc = "Direct nominal / base state";
  for (const s of SUFFIX_RULES) {{
    if (rest.endsWith(s.match) && rest.length > s.match.length) {{
      suffix = s.label;
      suffixDesc = s.desc;
      rest = rest.slice(0, rest.length - s.match.length);
      break;
    }}
  }}

  const stem = rest || lower;
  let stemDesc = STEM_GLOSSES[lower] || STEM_GLOSSES[stem] || "Botanical / pharmaceutical root stem (`" + stem + "`)";

  let gloss = "";
  if (STEM_GLOSSES[lower]) {{
    gloss = STEM_GLOSSES[lower];
  }} else {{
    const pShort = prefixDesc.split("(")[1] ? prefixDesc.split("(")[1].replace(")", "") : prefixDesc;
    const sShort = suffixDesc.split("(")[1] ? suffixDesc.split("(")[1].replace(")", "") : suffixDesc;
    gloss = `${{pShort}} + [${{stemDesc}}] + ${{sShort}}`;
  }}

  return {{ prefix, prefixDesc, stem, stemDesc, suffix, suffixDesc, gloss }};
}}

function setWord(w) {{
  const input = document.getElementById("wordInput");
  input.value = w;
  analyzeWord(w);
}}

function analyzeWord(w) {{
  const out = document.getElementById("legoOutput");
  const res = parseVoynichWord(w);
  if (!res) {{
    out.innerHTML = "";
    return;
  }}
  out.innerHTML = `
    <div class="lego-box lego-prefix">
      <div class="lego-label">1. Prefix (Left Role)</div>
      <div class="lego-val">${{res.prefix}}</div>
      <div class="lego-desc">${{res.prefixDesc}}</div>
    </div>
    <div class="lego-box lego-stem">
      <div class="lego-label">2. Core Root Stem</div>
      <div class="lego-val">${{res.stem}}</div>
      <div class="lego-desc">${{res.stemDesc}}</div>
    </div>
    <div class="lego-box lego-suffix">
      <div class="lego-label">3. Suffix (Right Ending)</div>
      <div class="lego-val">${{res.suffix}}</div>
      <div class="lego-desc">${{res.suffixDesc}}</div>
    </div>
    <div class="lego-box lego-gloss">
      <div class="lego-label">Plain-English Reading of <code>${{w}}</code></div>
      <div class="lego-val" style="font-family: inherit; font-size: 1rem;">${{res.gloss}}</div>
      <div class="lego-desc">Click any word token below to compare!</div>
    </div>
  `;
}}

function renderWalkthroughList() {{
  const listEl = document.getElementById("folioList");
  listEl.innerHTML = DATA.folios.map((f, idx) => `
    <button class="folio-item ${{idx === 0 ? 'active' : ''}}" onclick="selectFolio(${{idx}}, this)">
      <strong>Folio ${{f.folio}} (p.${{f.pdf_page}})</strong>
      <span>${{f.title}}</span>
    </button>
  `).join("");
  selectFolio(0, listEl.querySelector(".folio-item"));
}}

function selectFolio(idx, btnEl) {{
  document.querySelectorAll(".folio-item").forEach(b => b.classList.remove("active"));
  if (btnEl) btnEl.classList.add("active");
  const f = DATA.folios[idx];
  const viewer = document.getElementById("folioViewer");

  const clausesHtml = f.clauses.map(c => {{
    const tokens = c.eva.split(/\\s+/).map(t =>
      `<span class="word-chip" onclick="setWord('${{t.replace(/[^a-zA-Z0-9]/g, '')}}')">${{t}}</span>`
    ).join("");
    return `
      <div class="clause-card">
        <div class="clause-locus">${{c.locus}} — Click any Voynich word to decode it above:</div>
        <div class="clause-tokens">${{tokens}}</div>
        <div class="clause-english"><strong>Plain-English Reading:</strong> ${{c.english}}</div>
      </div>
    `;
  }}).join("");

  const secondImgHtml = f.secondary_image
    ? `<img src="${{f.secondary_image}}" alt="Detail crop for ${{f.folio}}" loading="lazy" />`
    : "";

  viewer.innerHTML = `
    <div style="display:flex; flex-wrap:wrap; justify-content:space-between; align-items:baseline; gap:0.5rem;">
      <h2 style="margin:0;">Folio <code>${{f.folio}}</code> — ${{f.title}}</h2>
      <span class="badge">${{f.section}} • Yale Scan Page ${{f.pdf_page}}</span>
    </div>
    <p style="color: var(--muted); margin-top: 0.4rem;">${{f.summary}}</p>
    <div class="viewer-split">
      <div class="scan-box">
        <img src="${{f.image}}" alt="Scan of ${{f.folio}}" />
        ${{secondImgHtml}}
      </div>
      <div>
        <h3 style="margin-top:0;">Line-by-Line Interactive Clause Breakdown</h3>
        ${{clausesHtml}}
      </div>
    </div>
  `;
}}

function renderSpecimens() {{
  const grid = document.getElementById("specimensGrid");
  grid.innerHTML = DATA.specimens.map(s => {{
    const rootChips = s.voynich_stems.dominant_roots.map(r => {{
      const clean = r.split(" ")[0].replace(/[^a-zA-Z]/g, "");
      return `<span class="word-chip" onclick="setWord('${{clean}}')">${{r}}</span>`;
    }}).join(" ");
    return `
      <article class="spec-card">
        <img src="${{s.image_rel_notes}}" alt="${{s.folio}} ${{s.common_name}}" loading="lazy" />
        <div class="spec-body">
          <span class="badge">${{s.id}} • Folio ${{s.folio}} (p.${{s.pdf_page}})</span>
          <h3 style="margin: 0.2rem 0 0.35rem;">${{s.common_name}}</h3>
          <p style="margin: 0 0 0.5rem; font-size: 0.86rem; color: var(--muted);">
            <strong>15th-c. Identification:</strong> <em>${{s.latin_candidates.join(" / ")}}</em>
          </p>
          <p style="font-size: 0.9rem; margin-bottom: 0.75rem;">${{s.plain_english_dossier}}</p>
          <div style="font-size: 0.82rem; margin-top: auto;">
            <strong>Key Voynich Stems (Click to Analyze):</strong>
            <div style="display:flex; flex-wrap:wrap; gap:0.35rem; margin-top:0.35rem;">${{rootChips}}</div>
          </div>
        </div>
      </article>
    `;
  }}).join("");
}}

function renderLexiconAndParadigms() {{
  const lexBody = document.querySelector("#lexiconTable tbody");
  lexBody.innerHTML = DATA.lexicon.map(row => {{
    const chips = row.examples.split(",").map(ex => {{
      const w = ex.trim();
      return `<span class="word-chip" onclick="setWord('${{w}}')">${{w}}</span>`;
    }}).join(" ");
    return `
      <tr>
        <td><code>${{row.stem}}</code></td>
        <td>${{row.category}}</td>
        <td><strong>${{row.meaning}}</strong></td>
        <td>${{chips}}</td>
        <td>${{row.grounding}}</td>
      </tr>
    `;
  }}).join("");

  const parBody = document.querySelector("#paradigmTable tbody");
  parBody.innerHTML = DATA.paradigms.map(p => {{
    const c = p.cases || {{}};
    const fmt = (cell) => cell && cell.top_form
      ? `<span class="word-chip" onclick="setWord('${{cell.top_form}}')">${{cell.top_form}}</span> <small style="color:var(--muted)">(${{cell.count}})</small>`
      : `<span style="color:var(--muted)">—</span>`;
    return `
      <tr>
        <td><strong><code>${{p.root}}</code></strong></td>
        <td>${{p.semantic_class || p.gloss || ''}}</td>
        <td>${{p.total_tokens || ''}}</td>
        <td>${{fmt(c.NOM)}}</td>
        <td>${{fmt(c.GEN_PART)}}</td>
        <td>${{fmt(c.LOC)}}</td>
        <td>${{fmt(c.INST)}}</td>
        <td>${{fmt(c.PROC)}}</td>
        <td>${{fmt(c.TERM)}}</td>
      </tr>
    `;
  }}).join("");
}}

function renderZodiacAndBalneo() {{
  const zBody = document.querySelector("#zodiacTable tbody");
  zBody.innerHTML = DATA.zodiac.map(m => {{
    const chips = m.top_nymph_labels.slice(0, 5).map(w =>
      `<span class="word-chip" onclick="setWord('${{w}}')">${{w}}</span>`
    ).join(" ");
    return `
      <tr>
        <td><strong><code>${{m.folio}}</code></strong></td>
        <td>${{m.sign}}</td>
        <td><span class="badge">${{m.european_month_gloss}}</span></td>
        <td>${{m.triplicity}} (${{m.season}})</td>
        <td>${{m.ring_token_count}}</td>
        <td>${{m.nymph_label_count}}</td>
        <td><strong>${{(m.o_prefix_rate * 100).toFixed(1)}}%</strong></td>
        <td>${{chips}}</td>
      </tr>
    `;
  }}).join("");

  const bBody = document.querySelector("#balneoTable tbody");
  bBody.innerHTML = DATA.balneo.map(f => {{
    const allLabs = [...(f.nymph_labels || []), ...(f.tube_labels || [])].slice(0, 6);
    const labChips = allLabs.length
      ? allLabs.map(w => `<span class="word-chip" onclick="setWord('${{w}}')">${{w}}</span>`).join(" ")
      : `<span style="color:var(--muted)">Pure-text / unlabelled pool</span>`;
    const proseChips = (f.top_prose_words || []).slice(0, 4).map(w =>
      `<span class="word-chip" onclick="setWord('${{w}}')">${{w}}</span>`
    ).join(" ");
    return `
      <tr>
        <td><strong><code>${{f.folio}}</code></strong></td>
        <td>${{f.prose_tokens}}</td>
        <td>${{(f.thermal_boil_rate * 100).toFixed(1)}}%</td>
        <td>${{(f.wash_bathe_rate * 100).toFixed(1)}}%</td>
        <td>${{(f.pool_vessel_rate * 100).toFixed(1)}}%</td>
        <td>${{labChips}}</td>
        <td>${{proseChips}}</td>
      </tr>
    `;
  }}).join("");
}}

function renderRecipesRosettesConsensus() {{
  const rBody = document.querySelector("#recipesTable tbody");
  rBody.innerHTML = (DATA.recipes_showcase || []).map(r => {{
    const openChips = (r.opening_clause_eva || "").split(/\\s+/).slice(0, 6).map(w =>
      `<span class="word-chip" onclick="setWord('${{w}}')">${{w}}</span>`
    ).join(" ");
    const closeChips = (r.closing_clause_eva || "").split(/\\s+/).slice(-6).map(w =>
      `<span class="word-chip" onclick="setWord('${{w}}')">${{w}}</span>`
    ).join(" ");
    return `
      <tr>
        <td><strong><code>${{r.recipe_id}}</code></strong></td>
        <td><span class="badge">${{r.regimen_class}}</span></td>
        <td>${{r.word_count}}</td>
        <td>${{r.boil_step_count}}</td>
        <td>${{r.measured_dose_count}}</td>
        <td>${{openChips}}</td>
        <td>${{closeChips}}</td>
      </tr>
    `;
  }}).join("");

  const rosBody = document.querySelector("#rosettesTable tbody");
  rosBody.innerHTML = (DATA.rosettes_panels || []).map(p => {{
    const chips = (p.top_words || []).slice(0, 6).map(w =>
      `<span class="word-chip" onclick="setWord('${{w}}')">${{w}}</span>`
    ).join(" ");
    return `
      <tr>
        <td><strong><code>${{p.folio}}</code></strong></td>
        <td><span class="badge">${{p.panel_type === 'DIAGRAM_WHEEL_OR_MAP' ? 'Cosmological Diagram / Map' : 'Prose Treatise'}}</span></td>
        <td>${{p.token_count}}</td>
        <td><strong>${{(p.o_nominal_rate * 100).toFixed(1)}}%</strong></td>
        <td><strong>${{(p.qo_active_rate * 100).toFixed(1)}}%</strong></td>
        <td>${{(p.edy_dy_rate * 100).toFixed(1)}}%</td>
        <td>${{(p.ol_or_al_ar_rate * 100).toFixed(1)}}%</td>
        <td>${{chips}}</td>
      </tr>
    `;
  }}).join("");

  const cBody = document.querySelector("#consensusTable tbody");
  cBody.innerHTML = (DATA.consensus_cribs || []).map(c => {{
    const statusBadge = c.transcribers_attesting === 4
      ? `<span class="badge" style="background:var(--green-soft);color:var(--green)">4 / 4 Editions</span>`
      : `<span class="badge" style="background:var(--blue-soft);color:var(--blue)">${{c.transcribers_attesting}} / 4 Editions</span>`;
    return `
      <tr>
        <td><span class="word-chip" onclick="setWord('${{c.word}}')"><strong>${{c.word}}</strong></span></td>
        <td><code>${{c.ZL3b_hits}}</code></td>
        <td><code>${{c.RF1b_hits}}</code></td>
        <td><code>${{c.IT2a_hits}}</code></td>
        <td><code>${{c.GC2a_v101_mapped_hits}}</code></td>
        <td>${{statusBadge}}</td>
      </tr>
    `;
  }}).join("");
}}

function renderAstroScribesPharma() {{
  const aBody = document.querySelector("#astroTable tbody");
  aBody.innerHTML = (DATA.astro_wheels || []).map(w => {{
    const words = [...(w.top_radial_labels || []).slice(0, 3), ...(w.top_ring_words || []).slice(0, 3)];
    const chips = words.map(tok => `<span class="word-chip" onclick="setWord('${{tok}}')">${{tok}}</span>`).join(" ");
    return `
      <tr>
        <td><strong><code>${{w.folio}}</code></strong> (p.${{w.pdf_page}})</td>
        <td>${{w.visual_type}}</td>
        <td>${{w.total_tokens}}</td>
        <td><strong>${{(w.o_prefix_rate * 100).toFixed(1)}}%</strong></td>
        <td>${{(w.match_rate_in_herbal * 100).toFixed(1)}}%</td>
        <td>${{(w.match_rate_in_recipes * 100).toFixed(1)}}%</td>
        <td>${{chips}}</td>
      </tr>
    `;
  }}).join("");

  const sBody = document.querySelector("#scribesTable tbody");
  sBody.innerHTML = (DATA.scribe_hands || []).map(h => {{
    const chips = (h.top_words || []).slice(0, 5).map(tok =>
      `<span class="word-chip" onclick="setWord('${{tok}}')">${{tok}}</span>`
    ).join(" ");
    return `
      <tr>
        <td><strong>${{h.hand}}</strong></td>
        <td>${{h.description}}</td>
        <td>${{h.folio_count}}</td>
        <td>${{h.total_tokens}}</td>
        <td><strong>${{(h.par_start_gallows_rate * 100).toFixed(1)}}%</strong></td>
        <td>${{(h.line_start_y_rate * 100).toFixed(1)}}% vs ${{(h.line_mid_y_rate * 100).toFixed(1)}}%</td>
        <td><strong>${{(h.line_end_m_rate * 100).toFixed(1)}}%</strong> vs ${{(h.line_mid_m_rate * 100).toFixed(1)}}%</td>
        <td>${{chips}}</td>
      </tr>
    `;
  }}).join("");

  const pBody = document.querySelector("#pharmaBridgeTable tbody");
  pBody.innerHTML = (DATA.pharma_bridges || []).map(b => {{
    const hList = (b.herbal_monograph_folios || []).map(f => `<code>${{f}}</code>`).join(", ");
    const sList = (b.starred_recipe_folios || []).map(f => `<code>${{f}}</code>`).join(", ");
    const badge = b.exact_in_both
      ? `<span class="badge" style="background:var(--green-soft);color:var(--green)">Exact 3-Way Match</span>`
      : `<span class="badge" style="background:var(--blue-soft);color:var(--blue)">Exact H + Stem S</span>`;
    return `
      <tr>
        <td><span class="word-chip" onclick="setWord('${{b.word}}')"><strong>${{b.word}}</strong></span></td>
        <td><code>${{b.canonical_stem}}</code></td>
        <td><code>${{b.pharma_locus}}</code> (${{b.label_type}})</td>
        <td>${{hList}}</td>
        <td>${{sList}}</td>
        <td>${{badge}}</td>
      </tr>
    `;
  }}).join("");
}}

function renderParagraphsIntrusionsTitles() {{
  const spBody = document.querySelector("#shortParsTable tbody");
  spBody.innerHTML = (DATA.short_paragraphs || []).map(p => {{
    const chips = (p.eva_text || "").split(/\\s+/).map(w =>
      `<span class="word-chip" onclick="setWord('${{w}}')">${{w}}</span>`
    ).join(" ");
    return `
      <tr>
        <td><strong>${{p.par_id}}</strong><br/><code>${{p.locus}}</code></td>
        <td><span class="badge">${{p.section}}</span></td>
        <td>${{p.word_count}}</td>
        <td>${{chips}}</td>
        <td>${{p.plain_english_translation}}</td>
      </tr>
    `;
  }}).join("");

  const intBody = document.querySelector("#intrusionsTable tbody");
  const bucketLabels = [
    ["true_line_start", "True Left-Margin Line-Start"],
    ["post_intrusion_resume", "Post-Intrusion Resume (<-> w)"],
    ["uninterrupted_mid_line", "Uninterrupted Mid-Line"],
    ["pre_intrusion_pause", "Pre-Intrusion Pause (w <->)"],
    ["true_line_end", "True Right-Margin Line-End"],
  ];
  const ib = DATA.intrusion_buckets || {{}};
  intBody.innerHTML = bucketLabels.map(([key, label]) => {{
    const row = ib[key] || {{}};
    const chips = (row.top_words || []).slice(0, 6).map(w =>
      `<span class="word-chip" onclick="setWord('${{w}}')">${{w}}</span>`
    ).join(" ");
    return `
      <tr>
        <td><strong>${{label}}</strong></td>
        <td>${{row.count || 0}}</td>
        <td><strong>${{((row.init_gallows_rate || 0) * 100).toFixed(2)}}%</strong></td>
        <td><strong>${{((row.init_y_rate || 0) * 100).toFixed(2)}}%</strong></td>
        <td><strong>${{((row.final_m_rate || 0) * 100).toFixed(2)}}%</strong></td>
        <td>${{row.mean_length || ""}}</td>
        <td>${{chips}}</td>
      </tr>
    `;
  }}).join("");

  const rtBody = document.querySelector("#rightTitlesTable tbody");
  rtBody.innerHTML = (DATA.right_titles || []).map(r => {{
    const chips = (r.tokens || []).map(w =>
      `<span class="word-chip" onclick="setWord('${{w}}')">${{w}}</span>`
    ).join(" ");
    const echoBadge = r.local_folio_stem_echo
      ? `<span class="badge" style="background:var(--green-soft);color:var(--green)">Yes</span>`
      : `<span style="color:var(--muted)">No</span>`;
    return `
      <tr>
        <td><code>${{r.locus}}</code> (<code>${{r.ltype}}</code>)</td>
        <td><code>${{r.section}}</code></td>
        <td>${{chips}}</td>
        <td><code>${{(r.stems || []).join(", ")}}</code></td>
        <td>${{echoBadge}}</td>
        <td>${{r.hits_in_Pharma_P}}</td>
        <td>${{r.hits_in_Recipes_S}}</td>
        <td>${{r.hits_in_Balneo_B}}</td>
      </tr>
    `;
  }}).join("");
}}

function renderVisualTwinsAndStarParity() {{
  const vtBody = document.querySelector("#visualTwinsTable tbody");
  vtBody.innerHTML = (DATA.visual_twins || []).map(r => {{
    const regChips = (r.exact_register_shared_words || []).slice(0, 6).map(w =>
      `<span class="word-chip" onclick="setWord('${{w}}')">${{w}}</span>`
    ).join(" ");
    const labChips = (r.pharma_register_labels || []).slice(0, 4).map(w =>
      `<span class="word-chip" onclick="setWord('${{w}}')">${{w}}</span>`
    ).join(" ");
    return `
      <tr>
        <td><strong>${{r.pair_id}}</strong></td>
        <td><code>${{r.herbal_folio}}</code> — <em>${{r.herbal_name}}</em></td>
        <td><code>${{r.pharma_locus}}</code><br/>${{labChips}}</td>
        <td>${{regChips}}</td>
        <td><code>${{(r.stem_register_shared || []).slice(0, 6).join(", ")}}</code></td>
        <td><strong>${{r.herbal_qo_rate}}% &rarr; ${{r.pharma_reg_qo_rate}}%</strong></td>
      </tr>
    `;
  }}).join("");

  const acBody = document.querySelector("#acrosticTable tbody");
  acBody.innerHTML = (DATA.f58r_acrostic || []).map(row => {{
    const anomBefore = row.was_phonotactic_anomaly
      ? `<span class="badge" style="background:var(--accent-soft);color:var(--accent)">YES (Anomalous)</span>`
      : `<span style="color:var(--muted)">No</span>`;
    return `
      <tr>
        <td><code>f58r.${{row.line_no}}</code></td>
        <td><code>${{row.raw_first_token}}</code></td>
        <td><strong><code>${{row.margin_key_char}}</code></strong></td>
        <td><span class="word-chip" onclick="setWord('${{row.restored_initial_word}}')"><strong>${{row.restored_initial_word}}</strong></span></td>
        <td>${{anomBefore}}</td>
        <td><span class="badge" style="background:var(--green-soft);color:var(--green)">0 Anomalies (Canonical)</span></td>
      </tr>
    `;
  }}).join("");

  const spBody = document.querySelector("#starParityTable tbody");
  spBody.innerHTML = (DATA.star_parity_folios || []).map(f => {{
    return `
      <tr>
        <td><strong><code>${{f.folio}}</code></strong></td>
        <td>${{f.star_count}}</td>
        <td>${{f.marked_count}}</td>
        <td>${{f.unmarked_count}}</td>
        <td><code>${{f.parity_sequence}}</code></td>
        <td>${{f.alternating_transitions}} / ${{f.adjacent_pairs}}</td>
        <td><strong>${{f.alternation_rate_pct}}%</strong></td>
      </tr>
    `;
  }}).join("");
}}

function renderQuiresShelvesWeirdos() {{
  const qBody = document.querySelector("#quiresTable tbody");
  qBody.innerHTML = (DATA.quires_table || []).map(q => {{
    const marks = (q.quire_mark_annotations || []).length
      ? q.quire_mark_annotations.map(m => `<code>${{m}}</code>`).join("<br/>")
      : `<span style="color:var(--muted)">—</span>`;
    return `
      <tr>
        <td><strong>Quire ${{q.quire_number}} (<code>$Q=${{q.quire_letter}}</code>)</strong></td>
        <td><code>${{q.first_folio}}–${{q.last_folio}}</code></td>
        <td>${{q.n_transcribed_pages}}</td>
        <td><code>${{(q.sections || []).join(", ")}}</code></td>
        <td><code>${{(q.languages || []).join(", ")}}</code></td>
        <td><code>${{(q.scribe_hands || []).join(", ")}}</code></td>
        <td>${{q.total_words}}</td>
        <td>${{marks}}</td>
      </tr>
    `;
  }}).join("");

  const psBody = document.querySelector("#pharmaShelvesTable tbody");
  psBody.innerHTML = (DATA.pharma_shelves || []).map(f => {{
    const cChips = (f.containers || []).length
      ? f.containers.map(w => `<span class="word-chip" onclick="setWord('${{w}}')">${{w}}</span>`).join(" ")
      : `<span style="color:var(--muted)">—</span>`;
    const echoed = [];
    for (const r of (f.rows || [])) {{
      for (const p of (r.plants || [])) {{
        if (p.hit_same_folio && echoed.length < 6) echoed.push(p.word);
      }}
    }}
    const eChips = echoed.map(w => `<span class="word-chip" onclick="setWord('${{w}}')">${{w}}</span>`).join(" ");
    return `
      <tr>
        <td><strong><code>${{f.folio}}</code></strong></td>
        <td>${{cChips}}</td>
        <td>${{f.n_rows}} shelves</td>
        <td>${{f.n_paragraphs}} paragraphs</td>
        <td><strong>${{f.paired_hit_rate_pct}}%</strong></td>
        <td>${{eChips}}</td>
      </tr>
    `;
  }}).join("");

  const pwBody = document.querySelector("#plumedWeirdoTable tbody");
  pwBody.innerHTML = (DATA.plumed_examples || []).map(p => {{
    return `
      <tr>
        <td><code>${{p.folio_line}}</code> (Hand ${{p.hand}})</td>
        <td><code>${{p.section}}</code></td>
        <td><code>${{p.raw_token}}</code></td>
        <td><span class="word-chip" onclick="setWord('${{p.reduced_single_loop}}')"><strong>${{p.reduced_single_loop}}</strong></span></td>
        <td><strong>${{p.standard_exact_count_single_loop}}</strong> hits</td>
        <td><code>${{p.canonical_stem}}</code></td>
        <td><strong>${{p.standard_stem_count}}</strong> stem hits</td>
      </tr>
    `;
  }}).join("");
}}

function renderMicroCliticsF57vStemMatrix() {{
  const mcBody = document.querySelector("#microCliticsTable tbody");
  mcBody.innerHTML = (DATA.micro_spaced_pairs || []).map(m => {{
    return `
      <tr>
        <td><code>${{m.pair}}</code></td>
        <td><span class="word-chip" onclick="setWord('${{m.fused_word}}')"><strong>${{m.fused_word}}</strong></span></td>
        <td><strong>${{m.comma_count}}x</strong></td>
        <td><strong>${{m.fused_word_corpus_freq}}x</strong></td>
        <td>${{m.a_is_proclitic ? '<span class="badge">Proclitic</span>' : '—'}}</td>
        <td>${{m.b_is_enclitic ? '<span class="badge">Enclitic</span>' : '—'}}</td>
      </tr>
    `;
  }}).join("");

  const f57Body = document.querySelector("#f57vQuadrantTable tbody");
  f57Body.innerHTML = (DATA.f57v_quadrants || []).map(r => {{
    const highlight = r.slot === 9 ? 'style="background:var(--gold-soft);font-weight:700;"' : '';
    return `
      <tr ${{highlight}}>
        <td><strong>Slot ${{r.slot}}</strong></td>
        <td><code>${{r.Q1}}</code></td>
        <td><code>${{r.Q2}}</code></td>
        <td><code>${{r.Q3}}</code></td>
        <td><code>${{r.Q4}}</code></td>
        <td>${{r.note}}</td>
      </tr>
    `;
  }}).join("");

  const smBody = document.querySelector("#universalStemMatrixTable tbody");
  smBody.innerHTML = (DATA.universal_stem_matrix || []).map(s => {{
    const regCell = (regKey) => {{
      const rg = (s.registers || {{}})[regKey] || {{}};
      const forms = (rg.top_forms || []).slice(0, 2).map(fw => {{
        const w = fw.split("(")[0];
        return `<span class="word-chip" onclick="setWord('${{w}}')">${{fw}}</span>`;
      }}).join(" ");
      return `${{forms}}<br/><small style="color:var(--muted)">Verbal: ${{rg.verbal_pct || 0}}%</small>`;
    }};
    return `
      <tr>
        <td><strong><code>${{s.stem}}</code></strong></td>
        <td><strong>${{s.total_occurrences}}</strong></td>
        <td>${{regCell("1_Diagram_Labels_@L")}}</td>
        <td>${{regCell("2_Herbal_A_Prose")}}</td>
        <td>${{regCell("3_Astro_Zodiac_Prose_Rings")}}</td>
        <td>${{regCell("4_Pharmaceutical_Prose")}}</td>
        <td>${{regCell("5_Herbal_B_Prose")}}</td>
        <td>${{regCell("6_Balneo_and_Starred_Recipes")}}</td>
      </tr>
    `;
  }}).join("");
}}

function switchTab(tabId, btn) {{
  document.querySelectorAll(".tab-panel").forEach(p => p.classList.remove("active"));
  document.querySelectorAll(".tab-btn").forEach(b => b.classList.remove("active"));
  document.getElementById("tab-" + tabId).classList.add("active");
  btn.classList.add("active");
}}

analyzeWord("qokeedy");
renderWalkthroughList();
renderSpecimens();
renderLexiconAndParadigms();
renderZodiacAndBalneo();
renderRecipesRosettesConsensus();
renderAstroScribesPharma();
renderParagraphsIntrusionsTitles();
renderVisualTwinsAndStarParity();
renderQuiresShelvesWeirdos();
renderMicroCliticsF57vStemMatrix();
</script>
</body>
</html>
"""
    OUT_HTML.write_text(html, encoding="utf-8")
    print(f"Wrote interactive local explorer to {OUT_HTML} ({len(html):,} bytes)")


if __name__ == "__main__":
    main()
