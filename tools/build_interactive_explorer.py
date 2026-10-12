#!/usr/bin/env python3
"""
tools/build_interactive_explorer.py

Builds `explorer/index.html` — a self-contained, zero-server interactive local HTML
explorer for the Voynich Manuscript research repository (v14.0 Grand Release).

Includes 16 synchronized interactive views:
  1. Page-by-Page Visual Reader (66 iconic folios with high-res scans & clickable clauses)
  2. Botanical, Astrological, Balneological & Cosmological Identifications (75 flagship specimens `SPEC-01..75`)
  ...
  15. Wave 47: Milestone 200 Attacks — Gemini/Cancer Decans, f67v Diptych & f75r Balneo Hub
  16. Wave 48: Post-200 Synthesis — Sagittarius Centaur, Albarelli Registers & Binary Star Parity
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
    },
    {
        "folio": "f85r1",
        "title": "The Rosettes Frontispiece Treatise & Right-Justified Summary Coda (`<f85r1.19,+Pr>`, `z = +4.40`)",
        "section": "Rosettes Frontispiece (`$I=T, $Q=N, $L=B`, Scribe 2/3)",
        "pdf_page": 156,
        "image": "../pages/f85r1_rosettes_frontispiece_text_enh.png",
        "secondary_image": "",
        "summary": "Outer recto frontispiece of the 6-panel Rosettes foldout sheet (`Quire 14`). While the inner 9-Sphere Cosmos Map (`f85v2`) is 98% nominal (`qo-` only 2.04%), the 6 treatise panels on the reverse/adjacent folds (`f85r1–f86v6`, 1,855 words) surge 6.76× in `qo-` verbs (13.80%) and cover 73.46% of all root stems on the map! At line 19 sits a right-justified summary coda (`okchy.okchdy.otchedy.daiin.dy`, `Attack 181`).",
        "clauses": [
            {
                "locus": "f85r1.19 (+Pr Right-Justified Paragraph 4 Coda Colophon)",
                "eva": "okchy okchdy otchedy daiin dy",
                "english": "[Right-Justified Summary Colophon]: The core herbal infusion (`okchy okchdy`) and prepared root decoction (`otchedy`), taken in one measured dose (`daiin dy`)."
            }
        ]
    },
    {
        "folio": "f69r",
        "title": "The 22-Spoke 3-Color 'Organ-Pipe' Wheel, 02:00 Cross-Hatched Start Spoke & 6 Central Star Numerals",
        "section": "Cosmological Wheel (`$I=C, $Q=K, $L=A`, Scribe 4)",
        "pdf_page": 126,
        "image": "../pages/f69r_swirling_spoke_wheel_enh.png",
        "secondary_image": "",
        "summary": "Contains all 4 wheel tiers (`Attack 182`): a 4-line header (`@P0`), 17 outer perimeter sectors (`@Ls`), 22 radial 'organ-pipe' spokes (`@Ro`, 3.00 words/spoke) alternating Blue -> White -> Green with 1 cross-hatched start-indicator spoke at 02:00 (`dar.doaiin.okal`), and 6 late-medieval Arabic digits (`8, 9, 2, 3, 6, 9`) inside the central 6-pointed star bays!",
        "clauses": [
            {
                "locus": "f69r.22 (@Ro 02:00 Cross-Hatched Index Spoke) + f69r.43 (@Cc Inner Star Ring)",
                "eva": "dar doaiin okal dchodees okody chody sar ar chey",
                "english": "[02:00 Start Spoke `dar doaiin okal`]: From the source take one measure of star-essence (`dar doaiin okal`); around the numbered central star (`8,9,2,3,6,9`), infuse the core sectors (`dchodees okody chody sar ar chey`)."
            }
        ]
    },
    {
        "folio": "f83r & f93r",
        "title": "Balneological Rainbow Arch Conduit (`otedy / okain`) & Giant Stippled Elecampane/Sunflower (`f93r`)",
        "section": "Balneological (`f83r`, Scribe 2) & Herbal A (`f93r`, Scribe 1)",
        "pdf_page": 152,
        "image": "../pages/f83r_balneo_tubes_and_pool_enh.png",
        "secondary_image": "../pages/f93r_giant_sunflower_elecampane_enh.png",
        "summary": "On `f83r` (above), a 3-color rainbow arch tube (`otedy`, `okain`) connects a left bather to a right bather seated in a white conical chalice funnel draining into a spoked blue rosette bladder (`roldal`, `dalchedy`). On `f93r` (below), a giant seed-stippled composite flower receptacle (*Inula helenium / Helianthus*) shelters a 3-line right-rim caption (`chodaiin qotcho / okan qokcho / chokaiin`).",
        "clauses": [
            {
                "locus": "f83r (Arch & Funnel Labels) + f93r (3-Line Right-Rim Flower Caption)",
                "eva": "otedy okain roldal dalchedy chodaiin qotcho okan qokcho chokaiin",
                "english": "[Bath Conduit `f83r`]: Flow through the arch (`otedy okain`) into the rosette basin (`roldal dalchedy`); [Flower Caption `f93r`]: Take one measure of the flower head (`chodaiin qotcho`), boil the core (`okan qokcho`), and steep (`chokaiin`)."
            }
        ]
    },
    {
        "folio": "f100v–f102r",
        "title": "Unfolded Quire 19 Pharma Sheets, Human-Faced Mandrake Root (`f101v`) & Milestone 200 State Machine",
        "section": "Pharmaceutical Multi-Panel Foldouts (`$I=P, $Q=S, $L=A`, Scribe 3)",
        "pdf_page": 180,
        "image": "../pages/f101v_pharma_five_rows_roots_enh.png",
        "secondary_image": "../pages/f101v_unfolded_five_row_pharma_enh.png",
        "summary": "On `p180` (`f101v` outer panel, above), Row 3 (4th plant from left) features an anthropomorphic human-faced Mandrake root (*Mandragora*) with eyes, nose, and mouth beside 3 painted jars, unfolding into `p181` (`f101v1 + f102r`, below). Exemplifies our Milestone 200th Discovery (`Attack 183`): the 8-State Syntactic State Machine (`Chi2 = 2,545.0, z = +254.84`).",
        "clauses": [
            {
                "locus": "f101v.1–3 (Compounding Recipe Below the Human-Faced Mandrake Root & 3 Jars)",
                "eva": "pchor odaiin otol okol chol daiin qokeedy shedy dam",
                "english": "[8-State Syntax Chain `S1 -> S5 -> S6 -> S7 -> S3 -> S4 -> S8`]: Begin (`pchor`) with one measure from the storage jars (`odaiin otol okol`), take one dose of strained liquid (`chol daiin`), boil and wash (`qokeedy shedy`), and seal to completion (`dam`)."
            }
        ]
    },
    {
        "folio": "f69v–f70r2",
        "title": "Unfolded 3-Wheel Astronomical Trifecta (`p127`), `f70r2`'s 16-Line Treatise (`z=+2.62`) & Scribe 4 Signature",
        "section": "Astronomical Unfolded 3-Panel Sheet (`$I=A, $Q=J, $L=B`, Scribe 4)",
        "pdf_page": 127,
        "image": "../pages/f70r2_astro_concentric_prose_wheel_enh.png",
        "secondary_image": "",
        "summary": "Unfolding `p127` displays three circular wheels (`f69v` 28-spoke wheel, `f70r1` 6-lobe nebula wheel opening with `ooooooooolar.sasa`, and `f70r2` 10-ray Sun wheel) plus a 16-line right-margin treatise on `f70r2` (`94` words) that surges `6.54×` in `qo-` verbs (`7.45%`) and repeats `38.30%` exact words (`69.15%` root stems) from the 3 wheels (`Attack 185`, z = +2.62).",
        "clauses": [
            {
                "locus": "f70r1.1 (@Cc Ring Call-Sign) + f70r2.3–5 (@P1 Right-Margin Treatise)",
                "eva": "ooooooooolar sasa daiin okeey shoaiin ckhhey otal shshy tal dam",
                "english": "[Ring Call-Sign]: 9-measure cycle (`ooooooooolar sasa`); [Right-Margin Canon `f70r2`]: Take one measure of prepared extract (`daiin okeey`), infuse with the divided core (`shoaiin ckhhey`), and complete the celestial sector (`otal shshy tal dam`)."
            }
        ]
    },
    {
        "folio": "f84r",
        "title": "Three-Pool Vertical Hydro-Cascade & Overhead Canopy Minimal-Pair Sequence (`z=+7.74`)",
        "section": "Balneological / Biological (`$I=B, $Q=M, $L=B`, Scribe 2)",
        "pdf_page": 154,
        "image": "../pages/f84r_balneo_canopy_pool_enh.png",
        "secondary_image": "",
        "summary": "A single left-margin conduit feeds 3 stacked pools (`Top`: 8 nymphs under a scalloped canopy; `Middle`: 7 nymphs with a blue sponge and red/blue jar labeled `otaly`; `Bottom`: 7 nymphs in a clear basin). `64.29%` of label stems echo in `f84r` prose (`Attack 186`), and adjacent diagram labels globally form minimal pairs (`Lev <= 2`) at `1.98×` null (`z = +7.74`).",
        "clauses": [
            {
                "locus": "f84r Canopy Minimal Pairs (@Ln) + f84r.13 (@P0 Bath Protocol Opener)",
                "eva": "okedy otedy olshy okolshy otoly otaly kol chedy qokeey otedy",
                "english": "[Canopy Minimal Pairs]: Core bath (`okedy`) vs source bath (`otedy`), surface wash (`olshy`) vs vessel wash (`okolshy`), liquid sector (`otoly`) vs essence sector (`otaly`); [Bath Opener]: In the core basin infuse, boil, and bathe (`kol chedy qokeey otedy`)."
            }
        ]
    },
    {
        "folio": "f90r1–r2 & f96r",
        "title": "Unfolded Blue Cup-Poppy & 31-Leaf Navelwort (`f90r1–r2`) + 11-Tuber Palmate Monograph (`f96r`)",
        "section": "Herbal A Unfolded Sheet (`f90r1–r2`, Scribe 1) & Late Herbal A (`f96r`, Scribe 1/4)",
        "pdf_page": 165,
        "image": "../pages/f90r1_f90r2_unfolded_herbal_enh.png",
        "secondary_image": "../pages/f96r_herbal_monograph_gap_enh.png",
        "summary": "On `p165` (above), Pharmaceutical `f89v1` faces unfolded Herbal `f90r1` (giant blue cup-capsules, `25.00%` `qo-` verbs) and `f90r2` (31-leaf button Navelwort, `18.18%` `-aiin` doses). On `f96r` (below), a drooping bell-flower with 7 palmate claw-leaves and 11 banana-tuber roots splits lines 11–12 (`<->`) with `20.24%` `cth/ckh` (`Attack 185`).",
        "clauses": [
            {
                "locus": "f90r1.1 (Blue Cup-Poppy Opener) + f96r.11 (Palmate Leaf `<->` Intrusion Line)",
                "eva": "pchodar qokchol chckhy teol cheody shodol qokchod s aiin chokey",
                "english": "[f90r1 Opener]: Begin from the flower stem and boil the strained liquid (`pchodar qokchol chckhy`); [f96r.11 Leaf Split]: Steep the root-tubers in liquid (`teol cheody shodol`), boil the core (`qokchod`), and take one measured dose (`s aiin chokey`)."
            }
        ]
    },
    {
        "folio": "f103r & p213",
        "title": "Quire 20 Grand Opening (`18` Alternating Red/White Stars, `'20'` Quire Mark & `z=+11.89` Chaining) + Spine",
        "section": "Starred Master Recipes Opening (`$I=S, $Q=T, $L=B`, Scribe 3) & Limp-Vellum Spine (`p213`)",
        "pdf_page": 184,
        "image": "../pages/f103r_quire20_opening_recipes_enh.png",
        "secondary_image": "../pages/p213_physical_spine_head_edge_scan.png",
        "summary": "On `f103r` (above), 18 left-margin stars strictly alternate Odd = Solid Red vs Even = Outlined White above the bottom-left Arabic numeral `20` (Quire 20), with both Recipe #1 and Recipe #18 opening with `pchedal`. Consecutive recipes across Quire 20 share `3.105` exact words (`z = +11.89`, `Attack 187`). Below (`p213`) is the physical limp-vellum spine with 3 raised sewing bands.",
        "clauses": [
            {
                "locus": "f103r.1 (Recipe #1 Red Star Opener) + f103r.52 (Recipe #18 White Star Framing Closer)",
                "eva": "pchedal oees earal qokeedy shedy qokedy pchedal qokeey qokedy qoty",
                "english": "[Recipe #1 Top Frame `pchedal`]: Begin the herbal infusion (`pchedal`), boil thoroughly and wash (`qokeedy shedy qokedy`); [Recipe #18 Bottom Frame `pchedal`]: Begin the infusion (`pchedal`) and boil to completion (`qokeey qokedy qoty`)."
            }
        ]
    },
    {
        "folio": "f71r & f70v2",
        "title": "Zodiac `30°`-Per-Sign Ecliptic Calibration (`299/300 = 99.67%`), Aries `15+15=30°` Split, Quire `10m` & Barreled `ot-/op-` Law",
        "section": "Zodiac Medallions (`$I=Z, $Q=J, $L=A`, Scribe 4)",
        "pdf_page": 129,
        "image": "../pages/f70v1_aries_dark_abril_p129_enh.png",
        "secondary_image": "../pages/f70v1_aries_dark_split_zodiac_enh.png",
        "summary": "On `f71r` (above, `abril`, Quire 10 signature `10m`), 15 barreled nymphs (`5` inner + `10` outer) pair with `f70v1`'s 15 nymphs to total 30 exact Aries degrees (`15+15=30°`), while `f70v2` (below, `mars`) has 29 barreled nymphs + 1 star (`oteos`) = 30 `@Lz` loci (`Attack 189`: `299/300` = `99.67%` across all 10 surviving signs, `73.97%` `ot-/op-` on barreled pages, `z = +4.83`).",
        "clauses": [
            {
                "locus": "f70v2.1 (@Lz Pisces Star) + f71r.1–5 (@Lz Aries II Barreled Nymphs)",
                "eva": "oteos oteos arar okldam oteoaldy oteolar okeoaly otaleky otalsar",
                "english": "[Pisces Star `oteos` & Aries II Degrees]: From the celestial degree (`oteos arar`), complete the core vessel (`okldam`), and prepare the starry liquid degrees (`oteoaldy oteolar okeoaly otaleky otalsar`)."
            }
        ]
    },
    {
        "folio": "f73r",
        "title": "Scorpio (`octobre`) Lizard-Scorpion Medallion, Central Star `otedy` & `10 + 16 + 4 = 30°` Top Overflow Arc",
        "section": "Zodiac Medallions (`$I=Z, $Q=J, $L=A`, Scribe 4)",
        "pdf_page": 134,
        "image": "../pages/f73r_scorpio_octobre_zodiac_enh.png",
        "secondary_image": "",
        "summary": "A green 4-legged Scorpio lizard (`octobre`) below a golden star (`otedy`) is encircled by 10 inner + 16 middle nymphs (`26`), plus 4 overflow nymphs standing in a row across the top outside the outer prose ring (`26 + 4 = 30` exact degrees, `100%` compressed to single-word labels, `Attack 189`).",
        "clauses": [
            {
                "locus": "f73r.1 (Central Scorpio Star) + f73r.29–32 (Top 4-Nymph Overflow Arc)",
                "eva": "otedy oktody chockhy otedy opchody otaly yteeody okeody ykeedy",
                "english": "[Scorpio Star `otedy` & Top 4-Degree Overflow Arc]: Prepared Scorpio degree (`otedy`); top overflow degrees (`oktody chockhy otedy opchody`) and ring degrees (`otaly yteeody okeody ykeedy`)."
            }
        ]
    },
    {
        "folio": "f77r & f81r",
        "title": "Six-Spout Aqueduct (`f77r`, `70%` Stem Echo) vs. Unlabeled Pool Gallery (`f81r`) & Prose Absorption Law (`z=+6.06`)",
        "section": "Balneological / Biological (`$I=B, $Q=M, $L=B`, Scribe 2)",
        "pdf_page": 140,
        "image": "../pages/f77r_balneo_five_organ_ring_enh.png",
        "secondary_image": "../pages/f81r_balneo_arcade_pool_gallery_enh.png",
        "summary": "On `f77r` (above), 6 `@Lt` spouts (`olkchs..soral`), 2 arch nymphs (`darchdar, dotedy`), a 4-nozzle spraying womb/ampulla (`otchdy`), and a blue-sphere tub (`otolaiin`) echo `70.0%` of their stems in `f77r` prose (`Attack 190`). On `f81r` (below, 7-to-6 nymph connected pools with 0 labels), the unlabeled prose absorbs `ok-/ot-` (`1.56×`, `z = +6.06`) and `ol-` articles (`22.34%`, `z = +5.19`) directly into the sentences!",
        "clauses": [
            {
                "locus": "f77r (@Lt/@Ln Labels) + f81r.1 & f81r.16 (Minimal-Pair Paragraph Openers)",
                "eva": "otedy otol dchdy soral otchdy otolaiin polchoy qokeedy polchdy shedy olchedy",
                "english": "[f77r Spouts & Ampulla]: Flow from the arch spouts (`otedy otol dchdy soral`) through the 4-nozzle sprayer (`otchdy`) into the blue-sphere basin (`otolaiin`); [f81r Unlabeled Pools]: Begin the upper 7-nymph bath (`polchoy qokeedy`) and lower 6-nymph bath (`polchdy shedy olchedy`)."
            }
        ]
    },
    {
        "folio": "f87r & f111v",
        "title": "Post-Rosettes Parallel `pchor` Herbal (`f87r`) & Quire 20 Two-Tier Margin Star Hierarchy (`f111v`, `88.1%` vs `81.5%`)",
        "section": "Late Herbal A (`f87r`, Quire 15) & Starred Master Recipes (`f111v`, Quire 20)",
        "pdf_page": 160,
        "image": "../pages/f87r_herbal_terrace_root_enh.png",
        "secondary_image": "../pages/f111v_quire20_long_recipes_enh.png",
        "summary": "On `f87r` (above, opening Quire 15 right after the Rosettes foldout), both paragraphs open with `pchor` (`pchor.odaiin` & `pchor.daiin`). On `f111v` (below, 14 margin stars), the top 25-line (`294`-word) protocol contains 7 Secondary Intra-Paragraph Step Stars (`daiin, okeeo, sho, y, sheaiin...`), while the bottom 7 recipes open 100% with `p-` Gallows (`polar, polkiin, pochey, polar, polchey, pollaiin, psalar`, `Attack 191`).",
        "clauses": [
            {
                "locus": "f87r.1 & f87r.11 (Parallel `pchor` Openers) + f111v (7 Bottom `p-` Gallows Recipe Openers)",
                "eva": "pchor odaiin pchor daiin koshey polar polkiin pochey polar polchey pollaiin psalar",
                "english": "[f87r Parallel Paragraphs]: Begin the herbal compound (`pchor odaiin / pchor daiin`); [f111v Starred Recipes]: Top megaparagraph (`koshey`) followed by 7 consecutive `p-` Gallows recipes (`polar, polkiin, pochey, polar, polchey, pollaiin, psalar`)."
            }
        ]
    },
    {
        "folio": "f72v3–v2 & f72v1",
        "title": "Unfolded Leo (`agost`) & Virgo (`setembre`) Sheet (`p132`), Libra (`octobre`) Scale (`p133`), Crowned Nymphs, Vellum Hole, Quire `11m` & `@Cc` vs `@Lz` Split",
        "section": "Zodiac Medallions (`$I=Z, $Q=K, $L=A`, Scribe 4)",
        "pdf_page": 132,
        "image": "../pages/f72v3_leo_agost_zodiac_enh.png",
        "secondary_image": "../pages/f72v1_libra_octobre_p133_enh.png",
        "summary": "On `p132` (above), Leo (`agost`, `30°`) and Virgo (`setembre`, `30°` with stemmed stars) sit side by side; on `p133` (below), Libra (`octobre`, `30°`) displays a blue-and-gold balance scale, a pre-existing vellum hole at 03:00 avoided by the ring text, and Quire 11 signature `11m`. Both Leo and Libra feature a 3-crowned leader-nymph at 12:00 (`or.aiin/otedy` & `okchey/otedy`), while `@Lz` labels use `68.0%` `o-` nominal citation (`z = +8.81`) vs `@Cc` rings surging `3.14×` in `ch-/sh-` participles (`26.04%`, `z = +7.00`, `Attack 193`).",
        "clauses": [
            {
                "locus": "f72v3.13–14 (Leo 12:00 Crowned Nymph) + f72v1.12–13 (Libra 12:30 Crowned Nymph) + f72v1 (@Cc Ring)",
                "eva": "or aiin otedy okchey otedy oteey chody chokody otal dar choty",
                "english": "[Crowned 12:00 Cusp Leaders]: Primary degree measure (`or aiin otedy / okchey otedy`); [`@Cc` Seasonal Ring Clause]: Steep the celestial degree (`oteey chody chokody`) and draw from the sector (`otal dar choty`)."
            }
        ]
    },
    {
        "folio": "f80r & f82r",
        "title": "Blue-Basin Gallery (`f80r`, `100%` Balneo Stem Echo), Dual-Arc Fountain & `darol / darary` Shower Plumes (`f82r`) & `3.57×` `-g` Label Suffix Law",
        "section": "Balneological / Biological (`$I=B, $Q=M, $L=B`, Scribe 2)",
        "pdf_page": 146,
        "image": "../pages/f80r_balneo_eleven_nymph_gallery_enh.png",
        "secondary_image": "../pages/f82r_balneo_rainbow_shower_pool_enh.png",
        "summary": "On `f80r` (above), 8 upper bathers (`toroly, olchdy, okaly, okolo, okary, opor, olky, otalshedy`) + right conduit (`okar`) achieve `100.0%` (`10/10`) Balneo stem echo (`70.0%` on `f80r`). On `f82r` (below), a dual-arc fountain rises above a horizontal jet bather (`oroldair`) and a green pool fed by two `dar-` shower plumes (`darol` & `darary`) beside minimal pair `okal -> okaldy` (`Attack 194`, `-g` enriched `3.57×` in labels, `z = +5.42`).",
        "clauses": [
            {
                "locus": "f80r.3–5 (`okaly -> okolo -> okary` Gradation) + f82r.35–38 (`darol / okal / okaldy / darary` Shower Pool)",
                "eva": "okaly okolo okary okar darol okal okaldy darary olaiin",
                "english": "[f80r Upper Gallery]: Volatile essence (`okaly`), liquid vessel (`okolo`), core basin (`okary`) fed by the conduit (`okar`); [f82r Green Pool]: Left shower plume (`darol`), adjacent bathers (`okal -> okaldy`), right geyser plume (`darary`), and measured pool (`olaiin`)."
            }
        ]
    },
    {
        "folio": "f94r",
        "title": "Opposite-Leaflet Maidenhair Fern / Spleenwort Monograph (`Asplenium / Adiantum`) & `92.21%` Recipe Stem Bridge",
        "section": "Post-Rosettes Late Herbal (`$I=H, $Q=R, $L=A`, Scribe 1)",
        "pdf_page": 170,
        "image": "../pages/f94r_late_herbal_monograph_enh.png",
        "secondary_image": "",
        "summary": "Four arching fronds with opposite pairs of fan-shaped, white-scalloped leaflets (*Capillus Veneris / Asplenium*) and 6 dark-blue sporangia/berries rise from a 5-pronged brown rhizome below a 9-line (`66`-word) paragraph (`koaiin.cheo.pchor.qooldy...`) whose stems recur `87.01%` in Pharmaceutical and `92.21%` (`77.92%` exact words!) in Quire 20 Starred Recipes (`Attack 195`).",
        "clauses": [
            {
                "locus": "f94r.1–2 (Maidenhair Fern Monograph Opener) + f94r.9 (Terminal Closure)",
                "eva": "koaiin cheo pchor qooldy sory choldy qokchor chol daiin",
                "english": "[f94r Opener]: Take one measure of the fern infusion (`koaiin cheo pchor`), decoct in liquid (`qooldy sory choldy`), boil the core (`qokchor`), and draw one strained dose (`chol daiin`)."
            }
        ]
    },
    {
        "folio": "f108v",
        "title": "The `581`-Word Starred Recipe Folio (`16` Stars), `261`-Word 8-Sub-Clause Megaparagraph & `2.36×` Step-Star Variance Collapse (`32.12` Words/Star Unit)",
        "section": "Starred Master Recipes (`$I=S, $Q=T, $L=B`, Scribe 3)",
        "pdf_page": 195,
        "image": "../pages/f108v_quire20_megaparagraph_recipes_enh.png",
        "secondary_image": "",
        "summary": "`f108v` carries 16 left-margin stars (`7` Primary `<%>` Recipe-Start Stars + `9` Intra-Paragraph `+P0` Step Stars). Across Quire 20, lines right before a Step Star end at the full right margin (`33.33%` `-m` stop vs `8.40%` at `<$>` half-lines = `3.97×` surge!), explaining why transcribers merged them; splitting at the 54 Step Stars (`339` star units) collapses Quire 20 SD by `2.36×` (`33.14 -> 14.02` words) onto the `32.12`-word canonical recipe length (`32.6` words/sub-clause on `f108v.30–53`, `Attack 195`)!",
        "clauses": [
            {
                "locus": "f108v.30 (`261`-Word Megaparagraph Opener) + Step-Star Sub-Clause Openers (`f108v.34..51`)",
                "eva": "polshedaiin qokeedy shedy dchedy qokedy saiin qokeey daiin otedy",
                "english": "[Megaparagraph Opener `f108v.30`]: Begin by washing one measure (`polshedaiin`), boil and bathe (`qokeedy shedy`); [Step-Star Sub-Clauses]: Take the infused mixture (`dchedy qokedy`), add one measure (`saiin qokeey daiin`), and complete (`otedy`)."
            }
        ]
    },
    {
        "folio": "f72r2",
        "title": "Gemini (`juny`) Dual-Figures Medallion, 29 Nymphs (Nameless 12:00 Nymph Anomaly), 3 Barreled Bathers & Concentric Text Rings",
        "section": "Zodiac Medallions (`$I=Z, $Q=K, $L=A`, Scribe 4)",
        "pdf_page": 131,
        "image": "../pages/f72r2_gemini_medallion_enh.png",
        "secondary_image": "",
        "summary": "Two youths embracing in an oval wooden tub under cursive Catalan/Occitan month gloss `juny`; 3 concentric rings (112 words) enclosing 29 transcribed nymphs; high-resolution scan inspection reveals a 30th star-bearing nymph at 12:00 in the middle ring whose label was left blank by the scribe, restoring the universal 30° decan blueprint; 3 nymphs stand in wooden tubs with hoops (05:00, 06:30, 08:00); structural pivot to summer prefix parity (`21.24%` `ot-/op-` vs `23.89%` `ok-/of-`, `Attack 197`).",
        "clauses": [
            {
                "locus": "f72r2.1 (Concentric Ring C1) + f72r2.29 (Degree Label)",
                "eva": "okaiin otedy chody okar otedy juny okedy ykeor olchedy",
                "english": "[Concentric Ring & Degree Labels]: Measure the celestial essence (`okaiin otedy`), steep the core root (`chody okar`), and decoct the golden core in the infused bath (`juny okedy ykeor olchedy`)."
            }
        ]
    },
    {
        "folio": "f72r3",
        "title": "Cancer (`jolh`) 10-Legged Crayfish Medallion, 4 Concentric Bands & 30 Decan Degree-Nymphs (`12°` Decan System)",
        "section": "Zodiac Medallions (`$I=Z, $Q=K, $L=A`, Scribe 4)",
        "pdf_page": 131,
        "image": "../pages/f72r3_cancer_medallion_enh.png",
        "secondary_image": "",
        "summary": "Ten-legged freshwater crayfish (*Astacus astacus*) with jointed claws under Catalan/Occitan month gloss `jolh` (July); 4 concentric rings (165 words); exactly 30 star-holding nymphs arranged in three decan rings of 12 outer + 11 middle + 7 inner = 30° (`30/30 = 100%`); cardinal cusp nymph at 12:00 labeled `ykolairol`; highest concentration of active operational verbs in Zodiac (`41/164 = 25.0%` `ch-/sh-`, `Attack 197`).",
        "clauses": [
            {
                "locus": "f72r3.1 (Cardinal 12:00 Nymph) + f72r3.4 (Concentric Ring C2)",
                "eva": "ykolairol otedy okain shol chedy qokedy chckhy olchedy",
                "english": "[Cardinal Cusp Leader & Verbal Ring]: Cusp leader nymph (`ykolairol otedy`), active liquid measure (`okain shol`), steep and boil the decoction (`chedy qokedy chckhy olchedy`)."
            }
        ]
    },
    {
        "folio": "f67v1 & f67v2",
        "title": "12-Sector Smiling Sun Wheel (`f67v1`, 17 Spokes, 39 Stars) & Four-Corner Cosmological Diagram (`f67v2`, Dendritic Terminals & `-g` Epicenter)",
        "section": "Astronomical & Cosmological (`$I=A/$I=C, $Q=I, $L=A`, Scribe 4)",
        "pdf_page": 123,
        "image": "../pages/f67v1_smiling_sun_wheel_enh.png",
        "secondary_image": "../pages/f67v2_four_corner_cosmology_enh.png",
        "summary": "On `f67v1` (above), 12-sector Sun Wheel with smiling face, 17 radiating text spokes alternating reading direction, 39 stars (3 cobalt-blue, 36 yellow-ochre), opening with terminal-flourished `damamm`. On `f67v2` (below), four-corner diagram with square-in-circle star, 8 dendritic spoke terminals, 4 corner face blowers, and Quire 9 velar `-g` stop epicenter (`daig, okydseog, olcheeg, ypcheg, [g:m]`, `9.31×` enrichment, `z = +6.10`, `Attack 198`).",
        "clauses": [
            {
                "locus": "f67v1.1 (Spoke Terminators) + f67v2.7 (Corner 3 daig)",
                "eva": "damamm olcheeg ypcheg tol or ain taol daig sakar dam solal daly",
                "english": "[f67v1 Solar Terminal Stops]: Final flourishing cadence (`damamm`) with velar spoke stops (`olcheeg, ypcheg`); [f67v2 Corner 3 Prose]: Take the dental order (`taol daig`), prepare the essence (`sakar dam`), and complete the cadence (`solal daly`)."
            }
        ]
    },
    {
        "folio": "f75v",
        "title": "Balneological Gastric/Organ Conduit System, Vertical `s-l-l-o-r-s` Gutter Key & Explicit Hydro-Tube Nomenclature (`@Lt`)",
        "section": "Balneological / Biological (`$I=B, $Q=M, $L=B`, Scribe 2)",
        "pdf_page": 137,
        "image": "../pages/f75v_gastric_stream_conduits_enh.png",
        "secondary_image": "../pages/f75v_gutter_acrostic_sllors_enh.png",
        "summary": "Central descending organ/oesophageal fluid channel into an asymmetrical reservoir; 20 bather nymphs (`@Ln`: `okshy/saral, dokal/darol`) favoring `ok-/of-` (`65.4%`); 7 mechanical tube callouts (`@Lt`: `otal opal, okeey lol, olol, ytedy, otedy, oteey, qotedy`) favoring `ot-/op-` (`57.7%`); upper-left gutter margin features 5-line terminal vertical alignment spelling `s-l-l-o-r-s`; downstream coverage from `f75r` hits `88.25%` on `f75v` (`Attack 199`).",
        "clauses": [
            {
                "locus": "f75v.1 (Nymph Label) + f75v.23 (Mechanical Tube Label)",
                "eva": "okshy saral dokal darol otal opal okeey lol olol ytedy otedy qotedy",
                "english": "[Bather Nymph Pair]: Guarded essence and source extract (`okshy saral / dokal darol`); [Hydro-Tube Nomenclature]: Primary conduits (`otal opal`), heated tube (`okeey lol`), fluid channel (`olol`), and heating pipe (`ytedy otedy qotedy`)."
            }
        ]
    },
    {
        "folio": "f73v",
        "title": "Sagittarius (`novembre`) Centaur-Archer Medallion, `10 + 16 + 4 = 30°` Top Overflow Arc & Quire 11 Boundary Forensics",
        "section": "Zodiac Medallions (`$I=Z, $Q=K, $L=A`, Scribe 4)",
        "pdf_page": 135,
        "image": "../pages/f73v_sagittarius_medallion_enh.png",
        "secondary_image": "",
        "summary": "Central galloping Centaur-Archer drawing a composite bow toward central star under month gloss `novembre`; 3 circular text rings (99 words); strictly replicates Scorpio `f73r`'s layout with 10 inner + 16 middle + 4 top overflow nymphs (`okol, oteody, oteedy, eeeody`) = 30° (`100%` calibration); physical verso of Quire 11 immediately preceding excised Folio 74 (Capricorn/Aquarius); autumn return to `ot-/op-` preference (`21.87%` vs `14.74%`, ratio = `1.48`, `Attack 201`).",
        "clauses": [
            {
                "locus": "f73v.1–4 (Top Overflow Arc) + f73v.23 (Inner Degree Locus)",
                "eva": "okol oteody oteedy eeeody otedy okedy otol ykor daiin",
                "english": "[Top Overflow Degree Nymphs]: Liquid vessel (`okol`), prepared degrees (`oteody oteedy`), final celestial state (`eeeody`); [Inner Decan Nymphs]: Compounded star degree (`otedy okedy otol`), golden core (`ykor`), and measured portion (`daiin`)."
            }
        ]
    },
    {
        "folio": "f99v & f88v",
        "title": "Pharmaceutical Shelf Sheets & Compounding Formulary: 25 Inscribed Albarelli (`f99v`), Container vs Flora Inversion ($t = +4.356$) & `otar arody` Bridge (`f88v`)",
        "section": "Pharmaceutical Storage & Formulary (`$I=P, $Q=O/$Q=R, $L=A`, Scribe 1/4)",
        "pdf_page": 177,
        "image": "../pages/f99v_three_row_jars_and_roots_enh.png",
        "secondary_image": "../pages/f88v_three_register_pharma_enh.png",
        "summary": "On `f99v` (above), 3 shelves hold 15 maiolica albarelli alternating with 10 root cuttings (25 labels); container labels (`@Lc`) are long compound formulas (mean `7.11` chars) vs short root simples (`@Lf`, mean `5.77` chars, `t = +4.356, p < 10^-5`, `Attack 202`). On `f88v` (below), 3 compounding registers with running prose (`@P0`) feature taproot `<f88v.4,@Lf> otar arody`, which bridges directly into Quire 20 recipe openers (`par arody, tar arody, qotar ar arody`, `64.29%` stem concordance)!",
        "clauses": [
            {
                "locus": "f99v.1 (@Lc Albarello) + f88v.4 (@Lf Taproot) + f88v.1 (@P0 Compounding Prose)",
                "eva": "olsy doldam doldam otar arody otoram cheor daiin qokar",
                "english": "[f99v Inscribed Albarelli]: Liquid vessel (`olsy`) and albarello pair formula (`doldam doldam`); [f88v Taproot & Compounding Prose]: The earth-root formula (`otar arody`), root decoction in infused oil (`otoram cheor`), taking one measure of boiled core (`daiin qokar`)."
            }
        ]
    },
    {
        "folio": "f105r & f116r",
        "title": "Quire 20 Starred Formulary Architecture: Dotted vs Plain Star Dyads (`f105r`), `par arody` Opener, Penultimate Chaining (`f116r`) & Binary Parity Invariant ($z = +12.20$)",
        "section": "Starred Master Recipes (`$I=S, $Q=T, $L=B`, Scribe 3)",
        "pdf_page": 188,
        "image": "../pages/f105r_dotted_star_dyads_enh.png",
        "secondary_image": "../pages/f116r_penultimate_recipes_enh.png",
        "summary": "On `f105r` (above), 10 painted stars accompany 8 recipes with deliberate contrast between Dotted (D) solid centers and Plain (P) open centers, opening with `par arody` on line 6; across Quire 20, margin stars alternate strictly 1-to-1 across `85.28%` of transitions (`z = +12.20, p < 10^-33`), hitting `100.0%` on 17 of 23 folios (`Attack 203`). On `f116r` (below), penultimate recipes 279..285 close with rhyming dyad `cthan cphan`, exhibiting strict convergence onto the `32.12`-word canonical recipe invariant before the multilingual prescription leaf `f116v`.",
        "clauses": [
            {
                "locus": "f105r.6 (`par arody` Recipe Opener) + f116r.47–48 (`cthan cphan` Rhyming Incipits)",
                "eva": "par arody shedeeey qopchedy cthan cphan qokeedy otchedey",
                "english": "[f105r Header Formula]: Begin the prepared root compound (`par arody`), bathe thoroughly (`shedeeey`), and decoct (`qopchedy`); [f116r Penultimate Rhyming Dyad]: Clinical compound pair (`cthan cphan`), then boil thoroughly in the infused process (`qokeedy otchedey`)."
            }
        ]
    },
    {
        "folio": "f71v & f72r1",
        "title": "Split-Sign Taurus Medallions (`may`): `(10° + 5°) + (10° + 5°) = 30°` Decan Law (`4/4 = 100%`), Barrel-to-Naked Hinge ($z = +15.98$) & `09:00` Vellum Hole",
        "section": "Zodiac Medallions (`$I=Z, $Q=K, $L=A`, Scribe 4)",
        "pdf_page": 131,
        "image": "../pages/f71v_taurus_manger_medallion_enh.png",
        "secondary_image": "../pages/f72r1_taurus_dark_bull_hole_enh.png",
        "summary": "On `p131`, Taurus I (`f71v`, white bull at woven manger) and Taurus II (`f72r1`, dark bull beside foliage) divide their 15 `@Lz` degree-nymphs into `10` Inner Full-Circle Nymphs (`1` full `10°` Decan) + `5` Outer Top-Arc Nymphs (`1/2` Decan = `5°`), reconciling two 15° half-signs with three 10° Decans (`10° + [5°+5°] + 10° = 30°`, `4/4 = 100%` across Aries & Taurus, `Attack 205`). On `f72r1`, `5/10` inner nymphs are barreled vs `0/5` (`0%`) outer top-arc nymphs (`100%` naked, `z = +15.98`), while a circular vellum hole at `09:00` (mirroring `f72v1` Libra's `03:00` hole) forces `<f72r1.6,@Lz> otal.kshy` below the defect.",
        "clauses": [
            {
                "locus": "f71v.7 & f71v.15 (`12:00` Inner/Outer Cusp Leaders) + f72r1.6 (`09:00` Hole Label) + f72r1.15 (`12:00` Naked Cusp)",
                "eva": "otar ar aly char aiin otal kshy otaiin okal otedy",
                "english": "[f71v Taurus I Cusp Leaders]: Primary decan root-star degree (`otar ar aly`) and measured outer-arc cusp (`char aiin`); [f72r1 Taurus II Hole & Naked Cusp]: Guarded sector degree below the vellum hole (`otal kshy`), outer-arc cusp measure (`otaiin`), and prepared degree (`okal otedy`)."
            }
        ]
    },
    {
        "folio": "f68v3, f68v2 & f68v1",
        "title": "Unfolded 3-Panel Astronomical Verso (`p125`): 8-Spoke & 6-Spoke Star Wheels, 4-Quadrant Moon Wheel, `71.13%` Header Echo & `66.12%` Recto-Verso Continuity",
        "section": "Astronomical Unfolded Sheet (`$I=A, $Q=I, $L=A`, Scribe 4)",
        "pdf_page": 125,
        "image": "../pages/f68v1_f68v2_astro_sectors_moon_enh.png",
        "secondary_image": "",
        "summary": "Unfolding `p125` reveals the 3-panel reverse of the `f68r` Pleiades sheet (`425` words): `f68v3` (left, 8 spiral spokes & 8 star sectors), `f68v2` (center, 6 radial spokes & 6 star sectors), and `f68v1` (right, 4-quadrant Moon phase wheel). Across `p125`, `71.13%` (`69/97`) of top `@P` paragraph tokens share their root stem with the wheel rings/spokes/star-labels below (`3.38×` `qo-` verb surge in `@P`), and `66.12%` of token stems echo `f68r1–r3` on the recto (`44` shared stems, `1.16×` lift, `Attack 205`).",
        "clauses": [
            {
                "locus": "f68v3.1, f68v2.1 & f68v1.1 (`@P0` Header Openers) + Wheel Sector Labels (`@Ls`)",
                "eva": "tchoep cheor pchodar opafal tchodar shecthedy dary okoldy octholey okeodar",
                "english": "[3-Panel `@P0` Header Openers]: Infused oil canon (`tchoep cheor`), compounded root header (`pchodar opafal`), and lunar phase canon (`tchodar shecthedy`); [Sector Star Labels]: Root-star degree (`dary okoldy`), divided ring star (`octholey`), and lunar quadrant (`okeodar`)."
            }
        ]
    },
    {
        "folio": "f77v & f83v",
        "title": "5-Loop Intestinal/Condenser Coil (`okalo`, `f77v` `81.82%` Local Echo), Crossed Bladder Retorts (`f83v` `100%` Echo) & Same-Leaf ($z=+6.31$) / Facing ($z=+5.18$) Continuity",
        "section": "Balneological / Biological (`$I=B, $Q=M, $L=B`, Scribe 2)",
        "pdf_page": 141,
        "image": "../pages/f77v_balneo_four_organ_tubes_enh.png",
        "secondary_image": "../pages/f83v_balneo_two_tier_nymph_gallery_enh.png",
        "summary": "On `f77v` (above), 4 vertical organ/condenser conduits—including the 5-loop serpentine coil `<f77v.13,@Lt> okalo` and a bather holding a fluted goblet (`okol, dar, chdy`)—echo `81.82%` (`9/11`) of their stems inside `f77v`'s own prose (`90.91%` in Balneo). On `f83v` (below), crossed green kidney/bladder retorts (`okyd, otal, sheol, okal, qokl`) and a central Y-tube (`otedy, dchedy`) achieve `100.0%` (`7/7`) Balneo stem echo (`84.13%` across all `126` Balneo callouts, alongside codex-wide Same-Leaf `z = +6.31` & Facing-Opening `z = +5.18` continuity, `Attack 206`).",
        "clauses": [
            {
                "locus": "f77v.1–16 (4 Vertical Organ/Condenser Conduits) + f83v.1–7 (Crossed Bladder Retorts & Y-Tube)",
                "eva": "otedar okedy qokedy olol otaldy olkedy okalo okol dar chdy sheol okal otedy dchedy",
                "english": "[f77v 4 Conduits]: Floral calyx tube (`otedar okedy qokedy`), bulbous ampulla (`olol otaldy olkedy`), 5-loop serpentine coil (`okalo`), and goblet bath (`okol dar chdy`); [f83v Retorts & Y-Tube]: Crossed bladder retorts (`sheol okal`) and central Y-tube (`otedy dchedy`)."
            }
        ]
    },
    {
        "folio": "f89r1–r2, f100v–101r & f34r/f39r",
        "title": "Unfolded Pharma Sheets `p163` (Numeral `'48'`) & `p179` (`6.00×` Cross-Fold Echo, Nominal Absorption $z=-3.54$) + Currier B Herbal Clinical Bridge (`f34r/f39r`, $z=+4.75$)",
        "section": "Pharmaceutical (`$I=P`, Quires 15 & 19) & Currier B Herbal (`$I=H`, Quires 5 & 6)",
        "pdf_page": 179,
        "image": "../pages/f101r_unfolded_pharma_compendium_enh.png",
        "secondary_image": "../pages/f34r_currier_b_polychrome_herbal_enh.png",
        "summary": "On `p179` (above, `f100v | f101r`), `42.86%` (`6/14`) of `f100v`'s left-column plant labels (`okam, sory, choldy, opakam, opor, otar`) echo across the vertical fold inside `f101r`'s wide prose (`6.00×` jump over `7.14%` self-echo!), while `f101r`'s 28 unlabeled plants drive `55.07%` `o-/d-/s-` nominal absorption (`qo-` suppressed `2.67×`, `z = -3.54`, `Attack 207`). Below (`f34r`, 3-headed polychrome thistle with `20` `<->` intrusions), the `32` Currier B Herbal folios surge `5.82×` in `-edy/-eey` (`16.18%` vs `2.78%` in Currier A), bridging directly into Balneological (`z = +4.75`) and Quire 20 Recipes (`z = +3.68`, `89.81%` on `f39r`, `Attack 208`).",
        "clauses": [
            {
                "locus": "f100v -> f101r (Cross-Fold Echoes) + f89r1.15 (`'48'` + `korary`) + f34r.1 & f39r.1 (Currier B Herbal Bridge)",
                "eva": "okam sory choldy opakam opor otar korary fataiin okor qokeedy tedcheo pchedar",
                "english": "[p179 Cross-Fold Pharma Echoes]: Left-column shelf roots echoed in wide right prose (`okam sory choldy opakam opor otar`) and numeral `'48'` paragraph (`korary`); [Currier B Herbal Bridge]: Polychrome thistle opener (`fataiin okor qokeedy`) and stolon monograph (`tedcheo pchedar`)."
            }
        ]
    },
    {
        "folio": "f41v & f65r",
        "title": "Scribe 5's Labeled Crossed-Root Umbel (`<f41v.1,@Lp> keer[e:o]dal`) & The Shortest Herbal Page (`<f65r.1,@Lp> otaim.dam.alam` — `3/3 = 100%` `-m` Triad, $p = 2.68 \\times 10^{-5}$)",
        "section": "Herbal (`$I=H`, Scribe 5 on `f41v`, Scribe 4 on `f65r`)",
        "pdf_page": 83,
        "image": "../pages/f41v_scribe5_labeled_herbal_enh.png",
        "secondary_image": "../pages/f65r_minimal_caption_herbal_enh.png",
        "summary": "Scribe 5 (`$H=5`) writes exactly `7` folios across the codex (`f41r, f41v, f48r, f48v, f57r, f66r, f66v` = `925` words, `18.38%` `-edy/-eey`, `Attack 209`). On `f41v` (above), a fan-shaped dotted umbel and two crossed red bulbous roots split the 7-line paragraph (`6` `<->` intrusions) beneath one of only `3` `@Lp` plant-header captions in the manuscript (`<f41v.1,@Lp> keer[e:o]dal`). On `f65r` (below, `p118`), a 9-tuber chain root and 15 star flowers carry `0` body paragraphs—only a standalone 3-word `@Lp` caption `otaim.dam.alam` where `3/3 = 100.0%` of the words end in `-aim/-am` vs `2.993%` Herbal baseline (`p = 2.68e-5`)!",
        "clauses": [
            {
                "locus": "f41v.1 (`@Lp` Header) + f41v.2 (`+P0` Opener) + f65r.1 (`@Lp` 3-Word `-m` Triad)",
                "eva": "keeredal pcheody qofcheepy ofchdy cfhekchdy ypchedy otaim dam alam",
                "english": "[f41v Scribe 5 Umbel Header & Opener]: Named umbel root-herb (`keeredal`), begin steeping and boiling the divided plant (`pcheody qofcheepy ofchdy cfhekchdy ypchedy`); [f65r 3-Word Alliterative `-m` Caption]: Complete the root-tuber measure, take to completion, seal the essence (`otaim dam alam`)."
            }
        ]
    },
    {
        "folio": "f76v & f81v",
        "title": "Illustrated Verso of the `f76r` Master Treatise (`79.50%` Stem Continuity, Shower Canopy & Red Bladder) & 14-Nymph Pool with Single Callout (`otain.olkal`, `100%` Echo)",
        "section": "Balneological / Hydrotherapy (`$I=B, $Q=M, $L=B`, Scribe 2)",
        "pdf_page": 139,
        "image": "../pages/f76v_balneo_shower_canopy_verso_enh.png",
        "secondary_image": "../pages/f81v_balneo_two_tier_single_label_enh.png",
        "summary": "On `f76v` (above, the physical back of the pure-text `613`-word Master Treatise `f76r`), marginal hydrotherapy drawings return—a top-right barrel sprayer interrupting Lines 1–6 via `6` `<->` intrusions, a left-margin shower canopy, a nymph holding a red pear-shaped bladder/organ, and a water chute—while `79.50%` (`318/400`) of `f76v`'s words reuse stems from `f76r` (`Attack 210`). On `f81v` (below, `p149`), `14` nymphs bathe in a two-tier green pool with only `1` callout locus (`<f81v.28,@Lt> otain.olkal`) at bottom-left, and `2/2 = 100.0%` of its stems echo inside `f81v`'s own prose!",
        "clauses": [
            {
                "locus": "f76v.1 (`@P0` Opener & `<->` Right Coda) + f81v.28 (`@Lt` Single Callout) + f81v.5 (Body Match)",
                "eva": "polarar okor opcheey yteey opchaly lshedy qofchdal lkodol opa korols otain olkal okaiin daiin otain chckhy okeedy",
                "english": "[f76v Treatise-to-Diagram Verso]: Begin from the core vessel, steep and wash (`polarar okor opcheey yteey opchaly lshedy qofchdal lkodol <-> opa korols`); [f81v Single Pool Callout & Body Echo]: The two-tier bath pool title (`otain olkal`) echoed directly in Line 5 (`okaiin daiin otain chckhy okeedy`)."
            }
        ]
    },
    {
        "folio": "f84v",
        "title": "Quire 13 Closing Folio (`13m`): Two Stacked Blue Pools, `@P1` Showerhead Header & `@Pb` 10-Line Right-Margin Callout Column (`60.0%` Local / `80.0%` Balneo Echo, $z = +3.96$)",
        "section": "Balneological Closing Verso (`$I=B, $Q=M` End, `$L=B`, Scribe 2)",
        "pdf_page": 155,
        "image": "../pages/f84v_balneo_closing_folio_quire13_enh.png",
        "secondary_image": "",
        "summary": "Final page of Quire 13 (`p155`), bearing the medieval quire signature `13m` in the bottom-right corner beside the lower S-curved blue drain pipe. Visually inspecting `f84v` resolves why standard tables list `0` `@L` labels: its 2-line top-pool showerhead header (`@P1`, `9` tokens) and its 10 single-word callouts down the right margin beside the two blue pools (`@Pb`, `11` tokens: `okar, ydairol, ychckhy, dshedy, okchdy, solchey, dair, oldy, darchy, ycthy, ochedy`) are encoded as `@P1/@Pb` blocks—and `12/20` (`60.00%`) echo inside `f84v`'s own prose (`z = +3.96, p = 0.0010`; `80.00%` across Quire 13, `Attack 210`)!",
        "clauses": [
            {
                "locus": "f84v.1–2 (`@P1` Top-Pool Showerhead Header) + f84v.42–51 (`@Pb` 10-Line Right-Margin Callout Stack)",
                "eva": "otdy dar chdy dar oram soiin okeeey sol okaly okar ydairol ychckhy dshedy okchdy solchey dair oldy darchy ycthy ochedy",
                "english": "[@P1 Showerhead Pool Header]: Steeped from the source to completion (`otdy dar chdy dar oram`), boiled in the bath vessel (`soiin okeeey sol okaly`); [@Pb 10 Right-Margin Pool Callouts]: Core vessel (`okar`), source flow (`ydairol`), infused wash (`ychckhy dshedy okchdy solchey`), and drained bath (`dair oldy darchy ycthy ochedy`)."
            }
        ]
    },
    {
        "folio": "f89v1–f90v1, f93v & f113v",
        "title": "The `f90` Foldout Inversion & Beinecke `'90r'` Mislabel Proof (`p165–p167`), Multi-Intrusion Micro-Corridor Law (`f90v1/f93v`, $z = -4.00$) & `93.33%` Gallows Star Openers (`f113v`, $z = +10.52$)",
        "section": "Post-Rosettes Foldout Herbal (`Quires 15–16`) & Quire 20 Starred Recipes (`p201`)",
        "pdf_page": 165,
        "image": "../pages/f89v_f90r1_f90r2_unfolded_sheet_enh.png",
        "secondary_image": "../pages/f93v_herbal_verso_18intrusions_enh.png",
        "summary": "On `p165` (above, `f89v1 | f90r1 | f90r2`), `f90r1` has 2 giant blue cup pods and `f90r2` has 32 green coin discs. When folded shut (`p166`), the outer flap folds inward over `f90r1`, exposing `f90v2` as the apparent recto—so the early modern foliator wrote `'90'` in the top-right corner of `f90v2` (causing both PDF catalogs to mislabel `p166` as `'90r'`, proven by the 32-coin bleed-through!), while `p167` (`f90v1`) bears the Quire 15 closing signature `'15m'` (`Attack 211`). On `f90v1` & `f93v` (below, 3 red-berry spikes), `59.54%` of interior `<-> X <->` micro-corridors hold a single compressed word (`4.087` vs `4.660` chars, `z = -4.00`). On `f113v` (`499` words, `15` starred recipes), `14/15` (`93.33%`) open with `p-/f-/t-` gallows (`z = +10.52`, `Attack 212`)!",
        "clauses": [
            {
                "locus": "f90v1.1 & f93v.1–2 (`<-> X <->` Inter-Stem Corridors) + f113v.1–15 (`93.33%` Gallows Recipe-Star Openers)",
                "eva": "pcheor chodar oleees chepy shol shckheo otol shey cheo r cheokeey possheody qoteeo opchy otchdal folorarom fchoctheody polaiin poraiin tokary",
                "english": "[f90v1 & f93v Inter-Stem Micro-Corridors]: Short 1–2 word bridge tokens threaded between flower stems and red-berry spikes (`<-> shckheo <-> otol shey <->`, `<-> opchy <->`); [f113v Starred Recipe Openers]: `14/15` (`93.33%`) gallows recipe headers (`folorarom, fchoctheody, polaiin, poraiin, tokary...`)."
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
    pt_pr_data = json.loads((ROOT / "data" / "attack181_rosettes_treatise_envelope_and_pt_titles.json").read_text(encoding="utf-8"))
    f69r_data = json.loads((ROOT / "data" / "attack182_f69r_star_numerals_and_spoke_ring_coupling.json").read_text(encoding="utf-8"))
    state_machine_data = json.loads((ROOT / "data" / "attack183_milestone200_syntactic_state_machine.json").read_text(encoding="utf-8"))
    a185_data = json.loads((ROOT / "data" / "attack185_f70r2_astro_treatise_and_scribe4_bridge.json").read_text(encoding="utf-8"))
    a186_data = json.loads((ROOT / "data" / "attack186_f84r_canopy_minimal_pairs_and_balneo_cascade.json").read_text(encoding="utf-8"))
    a187_data = json.loads((ROOT / "data" / "attack187_f103r_quire20_architecture_and_recipe_chaining.json").read_text(encoding="utf-8"))
    a189_data = json.loads((ROOT / "data" / "attack189_zodiac_30degree_invariant_and_decan_split.json").read_text(encoding="utf-8"))
    a190_data = json.loads((ROOT / "data" / "attack190_balneo_organ_labels_vs_unlabeled_galleries.json").read_text(encoding="utf-8"))
    a191_data = json.loads((ROOT / "data" / "attack191_f87r_post_rosettes_herbal_and_f111v_long_recipes.json").read_text(encoding="utf-8"))
    a193_data = json.loads((ROOT / "data" / "attack193_zodiac_ring_to_nymph_coupling_and_crowned_loci.json").read_text(encoding="utf-8"))
    a194_data = json.loads((ROOT / "data" / "attack194_balneo_f80r_f82r_and_rare_velar_suffixes.json").read_text(encoding="utf-8"))
    a195_data = json.loads((ROOT / "data" / "attack195_f108v_megaparagraph_compiler_and_f94r_fern.json").read_text(encoding="utf-8"))
    a197_data = json.loads((ROOT / "data" / "attack197_gemini_cancer_decans_and_p131_sheet.json").read_text(encoding="utf-8"))
    a198_data = json.loads((ROOT / "data" / "attack198_f67v_cardinal_treatises_and_velar_stop_network.json").read_text(encoding="utf-8"))
    a199_data = json.loads((ROOT / "data" / "attack199_f75r_waterfall_basin_and_hydraulic_master_hub.json").read_text(encoding="utf-8"))
    a200_data = json.loads((ROOT / "data" / "attack200_milestone200_master_compendium.json").read_text(encoding="utf-8"))
    a201_data = json.loads((ROOT / "data" / "attack201_sagittarius_centaur_archer_and_ecliptic_drift.json").read_text(encoding="utf-8"))
    a202_data = json.loads((ROOT / "data" / "attack202_pharmaceutical_albarelli_registers_and_recipe_bridge.json").read_text(encoding="utf-8"))
    a203_data = json.loads((ROOT / "data" / "attack203_quire20_star_point_morphology_and_formulary_clusters.json").read_text(encoding="utf-8"))
    a204_data = json.loads((ROOT / "data" / "attack204_wave48_master_compendium.json").read_text(encoding="utf-8"))
    a205_data = json.loads((ROOT / "data" / "attack205_taurus_split_barrel_transition_and_f68v_sectors.json").read_text(encoding="utf-8"))
    a206_data = json.loads((ROOT / "data" / "attack206_balneo_f77v_f83v_conduits_and_recto_verso_flow.json").read_text(encoding="utf-8"))
    a207_data = json.loads((ROOT / "data" / "attack207_pharma_unfolded_sheets_f89_f101_and_shelf_row_alignment.json").read_text(encoding="utf-8"))
    a208_data = json.loads((ROOT / "data" / "attack208_currier_b_herbal_clinical_bridge_and_wave49_compendium.json").read_text(encoding="utf-8"))
    a209_data = json.loads((ROOT / "data" / "attack209_scribe5_corpus_and_lp_plant_captions.json").read_text(encoding="utf-8"))
    a210_data = json.loads((ROOT / "data" / "attack210_balneo_f76v_f81v_f84v_closure_and_pb_callouts.json").read_text(encoding="utf-8"))
    a211_data = json.loads((ROOT / "data" / "attack211_f90_foldout_inversion_and_f93v_triple_split_syntax.json").read_text(encoding="utf-8"))
    a212_data = json.loads((ROOT / "data" / "attack212_quire20_f113v_f114r_and_milestone_wave50_compendium.json").read_text(encoding="utf-8"))

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
        "pt_pr_lines": pt_pr_data["pt_pr_lines_summary"]["all_lines"],
        "wheel_tiers": list(f69r_data["four_tier_wheel_locus_hierarchy"].values()),
        "state_profiles": state_machine_data["state_profiles"],
        "state_attractions": state_machine_data["top_syntactic_attractions"][:10],
        "state_prohibitions": state_machine_data["top_syntactic_prohibitions"][:10],
        "scribe4_profiles": a185_data["scribe_4_forensics"]["scribe_profiles_all_5_hands"],
        "minimal_pairs": a186_data["global_diagram_label_minimal_pairs"]["top_minimal_pair_chains"][:30],
        "f103r_recipes": a187_data["f103r_opening_forensics"]["recipes"],
        "q20_vertical": a187_data["within_page_vertical_trajectory"],
        "zodiac_30_invariant": a189_data["folio_summaries"],
        "f77r_labels": a190_data["f77r_label_details"],
        "intra_para_stars": a191_data["summary"]["intra_para_stars_examples"][:30],
        "q20_tiers": [
            a191_data["summary"]["quire20_short_recipes_tier"],
            a191_data["summary"]["quire20_medium_recipes_tier"],
            a191_data["summary"]["quire20_long_recipes_tier"],
        ],
        "zodiac_cc_lz_rows": a193_data["folio_breakdown"],
        "f80r_f82r_labels": a194_data["f80r_profile"]["labels"] + a194_data["f82r_profile"]["labels"],
        "megaparagraph_table": a195_data["quire20_step_star_megaparagraphs"][:12],
        "f108v_subclauses": a195_data["f108v_megaparagraph_10_subclauses"],
        "wave47_p131_panels": [
            {
                "folio": "f72r1",
                "sign": "Taurus II",
                "month": "may",
                "quadrant": "Q2",
                "rings": 2,
                "ring_words": 82,
                "degree_loci": 15,
                "degree_words": 23,
                "decan_calibration": "15° (Half-Sign)",
                "barreled_bathers": "5 / 15 (10 Inner / 5 Outer Hinge)",
                "ch_sh_rate": "26.67% (28/105)",
                "ot_bias": "1.50×"
            },
            {
                "folio": "f72r2",
                "sign": "Gemini",
                "month": "juny",
                "quadrant": "Q3",
                "rings": 3,
                "ring_words": 82,
                "degree_loci": 29,
                "degree_words": 31,
                "decan_calibration": "29/30 (1 Uncaptioned Nymph at 12:00)",
                "barreled_bathers": "3 / 30 (10%)",
                "ch_sh_rate": "15.04% (17/113)",
                "ot_bias": "0.89× (Parity)"
            },
            {
                "folio": "f72r3",
                "sign": "Cancer",
                "month": "jolh",
                "quadrant": "Q4",
                "rings": 4,
                "ring_words": 123,
                "degree_loci": 30,
                "degree_words": 41,
                "decan_calibration": "30/30 (100% Decan System)",
                "barreled_bathers": "0 / 30 (0% Unbarreled)",
                "ch_sh_rate": "25.00% (41/164 Active Surge)",
                "ot_bias": "1.25×"
            }
        ],
        "wave47_velar_g_tokens": a198_data["velar_g_network_analysis"]["f67_velar_g_tokens"],
        "wave47_balneo_hub_coverage": a199_data["master_hub_coverage_analysis"]["per_folio_coverage"],
        "wave48_ecliptic_drift": a201_data["ecliptic_drift_analysis"]["folio_stats"],
        "wave48_scorpio_sagittarius": a201_data["scorpio_sagittarius_architecture"],
        "wave48_lc_vs_lf": a202_data["lc_vs_lf_analysis"],
        "wave48_star_morphology": a203_data["star_point_morphology"]["points_summary"],
        "wave48_star_parity": a203_data["star_parity_alternation"]["folio_alternation_breakdown"],
        "wave49_split_signs": a205_data["split_zodiac_analysis"]["split_sign_profiles"],
        "wave49_barrel_census": a205_data["split_zodiac_analysis"]["barrel_transition_table"],
        "wave49_balneo_callouts": a206_data["balneo_label_and_f77v_f83v_analysis"]["f77v_label_details"] + a206_data["balneo_label_and_f77v_f83v_analysis"]["f83v_label_details"],
        "wave49_pharma_folios": a207_data["pharma_sheets_analysis"]["folio_profiles"],
        "wave49_currier_b_herbal": a208_data["currier_b_herbal_analysis"]["all_32_currier_b_herbal_folios"],
        "wave50_scribe5_folios": a209_data["scribe5_folio_breakdown"],
        "wave50_f84v_callouts": a210_data["f84v_closing_folio_callouts"]["callout_details"],
        "wave50_f90_pairs": a211_data["f90_foldout_inversion_proof"]["pairwise_stem_sharing"],
        "wave50_multi_intrusions": a211_data["f93r_f93v_leaf_coupling"]["f93v_multi_intrusion_lines"] + a211_data["multi_intrusion_micro_corridor_law"]["f90v1_multi_intrusion_lines"],
        "wave50_f113v_recipes": a212_data["f113v_starred_recipes"]["recipes"],
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
      <button class="tab-btn active" onclick="switchTab('walkthrough', this)">1. Page-by-Page Reader (74)</button>
      <button class="tab-btn" onclick="switchTab('specimens', this)">2. Visual Cribs &amp; Species (85)</button>
      <button class="tab-btn" onclick="switchTab('lexicon', this)">3. Core Dictionary &amp; 8-Case Grammar</button>
      <button class="tab-btn" onclick="switchTab('zodiac', this)">4. Zodiac Months &amp; Bath Plumbing</button>
      <button class="tab-btn" onclick="switchTab('recipes', this)">5. Starred Recipes, Rosettes &amp; 4-Transcriber Proof</button>
      <button class="tab-btn" onclick="switchTab('astro', this)">6. Astro Wheels, 5 Scribes &amp; Pharma Supply Chain</button>
      <button class="tab-btn" onclick="switchTab('paragraphs', this)">7. 25 Complete Paragraphs, Intrusions &amp; Right-Titles</button>
      <button class="tab-btn" onclick="switchTab('twins', this)">8. 12 Visual Twins, f49v Key &amp; Star Parity</button>
      <button class="tab-btn" onclick="switchTab('quires', this)">9. Quire Signatures, Pharma Shelves &amp; Weirdo-Glyph Atlas</button>
      <button class="tab-btn" onclick="switchTab('clitics', this)">10. Micro-Spacing Clitics, f57v Key Wheel &amp; 6-Register Stem Matrix</button>
      <button class="tab-btn" onclick="switchTab('state200', this)">11. Milestone 200: 8-State Syntactic Machine, =Pt/+Pr Codas &amp; f69r Wheel</button>
      <button class="tab-btn" onclick="switchTab('wave44', this)">12. Astro Trifecta (p127), Diagram-Label Minimal Pairs &amp; Quire 20 Chaining</button>
      <button class="tab-btn" onclick="switchTab('wave45', this)">13. Wave 45: Zodiac 30° Invariant, Balneo Absorption &amp; Two-Tier Stars</button>
      <button class="tab-btn" onclick="switchTab('wave46', this)">14. Wave 46: Zodiac @Cc-@Lz Split, f80r/f82r Galleries &amp; 32-Word Star Invariant</button>
      <button class="tab-btn" onclick="switchTab('wave47', this)">15. Wave 47: Milestone 200 Attacks — Gemini/Cancer Decans, f67v Diptych &amp; f75r Balneo Hub</button>
      <button class="tab-btn" onclick="switchTab('wave48', this)">16. Wave 48: Sagittarius Centaur, Albarelli Registers &amp; Binary Star Parity</button>
      <button class="tab-btn" onclick="switchTab('wave49', this)">17. Wave 49: 10°+5° Decan Law, Barrel Hinge, Unfolded Sheets &amp; Currier B Herbal Bridge</button>
      <button class="tab-btn" onclick="switchTab('wave50', this)">18. Wave 50: Milestone 50th Wave — Scribe 5, f65r -m Triad, f84v @Pb Callouts, f90 Foldout Inversion &amp; f113v Star Openers (v16.0)</button>
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
      <h2 style="margin: 0 0 0.25rem;">85 Flagship Botanical, Astronomical, Balneological, Cosmological, Margin-Key &amp; Visual-Twin Identifications</h2>
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

  <!-- TAB 11: MILESTONE 200 SYNTACTIC STATE MACHINE, =Pt/+Pr CODAS & 4-TIER WHEEL HIERARCHY -->
  <section id="tab-state200" class="tab-panel">
    <h2>1. MILESTONE 200TH DISCOVERY — The 8-State Voynich Syntactic State Machine (`39,001` Tokens, `&chi;² = 2,545.0`, `z = +254.84`, `Attack 183`)</h2>
    <p style="color: var(--muted);">
      Classifying all <strong>39,001 tokens</strong> (<strong>30,924 adjacent paragraph transitions</strong>) into <strong>8 Deterministic Morpho-Syntactic States</strong> reveals a rigid natural-language phrase state machine (<code>&chi;² = 2,545.0</code> vs <code>49.2</code> null, <strong>z = +254.84</strong>; Mutual Information <code>I = 0.05743 bits</code>, <strong>z = +247.60</strong>):
    </p>
    <div style="overflow-x: auto; margin-bottom: 2rem;">
      <table id="stateMachineProfilesTable">
        <thead>
          <tr>
            <th>State ID</th>
            <th>Tokens (<code>%</code>)</th>
            <th>Line-Initial Lift</th>
            <th>Line-Medial Lift</th>
            <th>Line-Final Lift</th>
            <th>Top Exemplar Words (Click to Analyze)</th>
          </tr>
        </thead>
        <tbody></tbody>
      </table>
    </div>

    <h2>2. Top Syntactic Transition Attractions (`S4 &rarr; S3` `2.16×`) vs. Prohibitions (`S2 &rarr; S3` `0.21×` Suppression, `Attack 183`)</h2>
    <p style="color: var(--muted);">
      Nearly <strong>one-third (31.61%, 2.16× lift)</strong> of all <code>ch-/sh-</code> verbal participles (<code>S4: chedy, shedy</code>) chain immediately into a <code>qo-</code> active procedural verb (<code>S3: qokeedy, qokedy</code>), whereas standalone <code>1–2</code> char prepositions/particles (<code>S2: ol, or, ar, al, dar, dal</code>) <strong>govern following Core Nouns (<code>S6</code>, 45.37%, 1.39× lift)</strong> and <strong>strictly prohibit following finite <code>qo-</code> Verbs (<code>S3</code>, 0.21× lift = 79% suppression!)</strong>:
    </p>
    <div style="overflow-x: auto; margin-bottom: 2rem;">
      <table id="stateTransitionsTable">
        <thead>
          <tr>
            <th>Rule Type</th>
            <th>From State (<code>S_t-1</code>)</th>
            <th>To State (<code>S_t</code>)</th>
            <th>Observed</th>
            <th>Expected</th>
            <th>Transition Prob</th>
            <th>Lift (<code>O/E</code>)</th>
          </tr>
        </thead>
        <tbody></tbody>
      </table>
    </div>

    <h2>3. All 22 Right-Justified Title &amp; Paragraph Coda Colophons (`=Pt` &amp; `+Pr`, `z = +4.40`, `Attack 181`)</h2>
    <p style="color: var(--muted);">
      Across the entire manuscript, <strong>22 right-justified lines (10 <code>=Pt</code> + 12 <code>+Pr</code>, 76 words)</strong> act as topical summary colophons—repeating exact words from their host paragraph at <strong>2.37× enrichment (z = +3.52, 51.32% stem overlap)</strong> and from their host folio at <strong>2.19× enrichment (z = +4.40, 63.16% stem overlap)</strong>:
    </p>
    <div style="overflow-x: auto; margin-bottom: 2rem;">
      <table id="ptPrColophonsTable">
        <thead>
          <tr>
            <th>Folio &amp; Line</th>
            <th>Tag</th>
            <th>Section &amp; Lang</th>
            <th>Right-Justified Text (Click to Analyze)</th>
            <th>Shared Stems in Host Folio</th>
          </tr>
        </thead>
        <tbody></tbody>
      </table>
    </div>

    <h2>4. The 4-Tier Astronomical/Cosmological Wheel Locus Hierarchy (`569` Loci, `3,610` Words, `Attack 182`)</h2>
    <p style="color: var(--muted);">
      Across all 18 circular/wheel folios (including <code>f69r</code> with its 22 3-color periodic spokes, 02:00 cross-hatched index spoke, and 6 central star Arabic numerals), inscriptions follow a strict 4-tier length hierarchy while adjacent radial spokes match in length within &plusmn;1 word <strong>91.55% of the time (z = +10.15)</strong>:
    </p>
    <div style="overflow-x: auto;">
      <table id="wheelTiersTable">
        <thead>
          <tr>
            <th>Wheel Locus Tier</th>
            <th>Loci Count</th>
            <th>Total Words</th>
            <th>Mean Words / Locus</th>
            <th>Nominal (<code>-aiin/-ar/-al/-ol/-or</code>)</th>
            <th>Verbal (<code>-edy/-dy/-eey/-ey</code>)</th>
          </tr>
        </thead>
        <tbody></tbody>
      </table>
    </div>
  </section>

  <!-- TAB 12: WAVE 44 ASTRO TRIFECTA, DIAGRAM-LABEL MINIMAL PAIRS & QUIRE 20 RECIPE CHAINING -->
  <section id="tab-wave44" class="tab-panel">
    <h2>1. Scribe 4 (`$H=4`) Orthographic Signature (`2.46×` `ok-/ot-` Prefix Surge &amp; `1.91×` `-ody/-ady` Surge, `Attack 185`)</h2>
    <p style="color: var(--muted);">
      On the unfolded 3-wheel sheet <code>f69v | f70r1 | f70r2</code> (<code>p127</code>), the 16-line right-margin treatise on <code>f70r2</code> (<code>94</code> words) surges <strong>6.54× in <code>qo-</code> verbs (7.45% vs 1.14%)</strong> and echoes <strong>38.30% exact words / 69.15% root stems</strong> from the 3 wheels (<code>z = +2.62</code>). Across all 5 Scribe Hands, Scribe 4 exhibits a distinct personal spelling signature:
    </p>
    <div style="overflow-x: auto; margin-bottom: 2rem;">
      <table id="scribe4Table">
        <thead>
          <tr>
            <th>Scribe Hand</th>
            <th>Total Words</th>
            <th>Unique Types (TTR)</th>
            <th><code>ok-/ot-</code> Prefix Rate</th>
            <th><code>-ody/-ady</code> Suffix Rate</th>
            <th><code>qo-</code> Verb Rate</th>
            <th><code>-edy/-eey</code> Rate</th>
          </tr>
        </thead>
        <tbody></tbody>
      </table>
    </div>

    <h2>2. Global Adjacent Diagram-Label Minimal-Pair Chains (`Lev &lt;= 2` `1.98×` Lift, `z = +7.74`; Same Stem `2.48×` Lift, `z = +6.40`, `Attack 186`)</h2>
    <p style="color: var(--muted);">
      Inspired by the overhead canopy labels on <code>f84r</code> (<code>okedy &lt;-&gt; otedy</code>, <code>olshy &lt;-&gt; okolshy</code>, <code>otoly &lt;-&gt; otaly</code>), testing all <strong>1,071 adjacent diagram-label pairs</strong> across 52 folios proves that neighboring labels form minimal pairs (<code>edit distance &lt;= 2</code>) at <strong>9.15% vs 4.62% null (z = +7.74)</strong> and share the exact same root stem at <strong>3.83% vs 1.54% null (z = +6.40)</strong>:
    </p>
    <div style="overflow-x: auto; margin-bottom: 2rem;">
      <table id="minimalPairsTable">
        <thead>
          <tr>
            <th>Folio (Section)</th>
            <th>Label 1 (Click to Decode)</th>
            <th>Label 2 (Click to Decode)</th>
            <th>Edit Distance</th>
            <th>Same Canonical Stem?</th>
            <th>Stem(s)</th>
          </tr>
        </thead>
        <tbody></tbody>
      </table>
    </div>

    <h2>3. Folio `f103r` Opening Quire 20 Architecture (`18` Alternating Red/White Stars + Bottom-Left `'20'` Mark) &amp; Consecutive Recipe Chaining (`z = +11.89`, `Attack 187`)</h2>
    <p style="color: var(--muted);">
      Across all <strong>292 starred recipes (267 adjacent within-page pairs)</strong> in Quire 20 (<code>f103r–f116r</code>), consecutive recipes share <strong>3.105 exact words (1.50× Jaccard lift, z = +11.89)</strong> and <strong>6.071 canonical stems (z = +9.03)</strong>. Below are the 18 opening recipes on <code>f103r</code> showing the strict Red / White-Outline star alternation and the <code>pchedal</code> top/bottom framing opener:
    </p>
    <div style="overflow-x: auto;">
      <table id="f103rRecipesTable">
        <thead>
          <tr>
            <th>Recipe #</th>
            <th>Left-Margin Star Type</th>
            <th>Start Line</th>
            <th>Lines / Words</th>
            <th>Opening Word (Click)</th>
            <th>Closing Word (Click)</th>
            <th><code>qo-</code> / <code>-edy</code> Counts</th>
          </tr>
        </thead>
        <tbody></tbody>
      </table>
    </div>
  </section>

  <!-- TAB 13: WAVE 45 (ZODIAC 30° INVARIANT, BALNEO ABSORPTION, TWO-TIER STARS) -->
  <section id="tab-wave45" class="tab-panel">
    <div class="stat-grid">
      <div class="stat-card">
        <div class="num">299 / 300</div>
        <div class="lbl">Exact 30°-Per-Sign Zodiac Calibration (99.67% across 10 Signs, <code>Attack 189</code>)</div>
      </div>
      <div class="stat-card">
        <div class="num">+4.83 z</div>
        <div class="lbl">Barreled (<code>ot-/op-</code> 73.97%) vs. Unbarreled (<code>ok-/of-</code> 62.62%) Zodiac Split (<code>p &lt; 2×10⁻⁶</code>)</div>
      </div>
      <div class="stat-card">
        <div class="num">+6.06 z</div>
        <div class="lbl">Unlabeled Balneo Prose Absorption of <code>ok-/ot-</code> Nouns (12.34% vs. 7.92%, <code>1.56×</code>)</div>
      </div>
      <div class="stat-card">
        <div class="num">269 + 54</div>
        <div class="lbl">Two-Tier Quire 20 Stars: 269 Primary Recipe Stars (88.1% Gallows) + 54 Step Stars (81.5% Particles)</div>
      </div>
    </div>

    <h2>1. The <code>30°</code>-Per-Sign Ecliptic Degree Invariant (<code>299 / 300 = 99.67%</code> Exact Calibration, <code>Attack 189</code>)</h2>
    <p style="color: var(--muted);">
      Across all <strong>10 surviving Zodiac signs (12 folios, <code>f70v2–f73v</code>)</strong>, the Voynich Zodiac is a mathematically exact <strong>30°-per-sign ecliptic degree register</strong>: <code>9 of 10</code> signs contain literally <strong>30</strong> <code>@Lz</code> degree loci (and Gemini has 29 transcribed + 1 faint locus = 30). Notice how Aries and Taurus are split across Dark (<code>I</code>) + Light (<code>II</code>) spreads of exactly <code>15° + 15° = 30°</code>, while Scorpio (<code>f73r</code>) and Sagittarius (<code>f73v</code>) pack <code>10 inner + 16 middle + 4 top-arc overflow = 30°</code>:
    </p>
    <div style="overflow-x: auto;">
      <table id="zodiac30Table">
        <thead>
          <tr>
            <th>Zodiac Sign</th>
            <th>Roman Month Gloss</th>
            <th>Folios</th>
            <th>Ring Breakdown</th>
            <th>Total <code>@Lz</code> Degree Loci</th>
            <th>30° Target Match</th>
          </tr>
        </thead>
        <tbody></tbody>
      </table>
    </div>

    <h2>2. Balneological Organ Callout Echoes on <code>f77r</code> (<code>70.0%</code> Local Stem Echo) &amp; Unlabeled Prose Absorption (<code>z = +6.06</code>, <code>Attack 190</code>)</h2>
    <p style="color: var(--muted);">
      When a Balneological folio has <strong>0 diagram labels</strong> (<code>8</code> folios: <code>f75r, f76v, f78v, f79r, f79v, f80v, f81r, f84v</code>), its body prose absorbs the missing anatomical/hydraulic nouns: <code>ok-/ot-</code> tokens surge from <strong>7.92% to 12.34% (1.56× lift, z = +6.06)</strong> and <code>ol-/or-</code> articles rise from <strong>9.38% to 13.39% (1.43× lift, z = +5.19)</strong>. On labeled pages like <code>f77r</code> (Six-Spout Overhead Aqueduct Arch), <strong>70.0% (7/10)</strong> of the diagram callout stems are echoed directly inside <code>f77r</code>'s own prose:
    </p>
    <div style="overflow-x: auto;">
      <table id="f77rLabelsTable">
        <thead>
          <tr>
            <th>Locus</th>
            <th>Type</th>
            <th>Callout Label (Click to Decode)</th>
            <th>Canonical Stem</th>
            <th>Physical Organ / Bather Position on <code>f77r</code></th>
            <th>In <code>f77r</code> Prose?</th>
            <th>In Balneo Prose?</th>
          </tr>
        </thead>
        <tbody></tbody>
      </table>
    </div>

    <h2>3. The Two-Tier Quire 20 Margin Star Hierarchy (<code>269</code> Primary Recipe Stars vs. <code>54</code> Intra-Paragraph Step Stars, <code>Attack 191</code>)</h2>
    <p style="color: var(--muted);">
      Why do folios like <code>f108v</code>, <code>f111r</code>, <code>f111v</code>, and <code>f116r</code> have 14–16 painted stars in the left margin yet contain 250–365 word megaparagraphs? Across all <strong>323 paleographically annotated margin stars</strong> in Quire 20, there is a strict two-tier hierarchy: <strong>269 Primary Recipe-Start Stars (<code>&lt;%&gt;</code>, 88.10% Gallows-initial)</strong> vs. <strong>54 Secondary Intra-Paragraph Step Stars (<code>+P0</code> without half-line break, only 25.93% Gallows-initial, 81.48% <code>s-/d-/y-/o-/q-</code> step-particle initial)</strong>:
    </p>
    <div style="overflow-x: auto;">
      <table id="intraParaStarsTable">
        <thead>
          <tr>
            <th>Locus</th>
            <th>Star Code</th>
            <th>Star Color / Tail</th>
            <th>Step Opener Word (Click to Decode)</th>
            <th>Initial Class</th>
            <th>Preceding Line End Word (Click)</th>
          </tr>
        </thead>
        <tbody></tbody>
      </table>
    </div>
  </section>

  <!-- TAB 14: WAVE 46 (ZODIAC @CC-@LZ SPLIT, F80R/F82R GALLERIES & 32.12-WORD STAR INVARIANT) -->
  <section id="tab-wave46" class="tab-panel">
    <div class="stat-grid">
      <div class="stat-card">
        <div class="num">+8.81 z</div>
        <div class="lbl">Zodiac <code>@Lz</code> Degree Labels Surge <code>1.68×</code> in <code>o-</code> Nominal Prefixes (68.00% vs. 40.56%, <code>Attack 193</code>)</div>
      </div>
      <div class="stat-card">
        <div class="num">+7.00 z</div>
        <div class="lbl">Zodiac <code>@Cc</code> Concentric Rings Surge <code>3.14×</code> in <code>ch-/sh-</code> Verbal Stems (26.04% vs. 8.29%, <code>Attack 193</code>)</div>
      </div>
      <div class="stat-card">
        <div class="num">+5.42 z</div>
        <div class="lbl">Rare Velar <code>-g</code> Label Stop Enriched <code>3.57×</code> in Diagram Labels (91.33% Word-Final, <code>Attack 194</code>)</div>
      </div>
      <div class="stat-card">
        <div class="num">2.36× SD Drop</div>
        <div class="lbl">Splitting Quire 20 at 54 Step Stars Collapses SD from <code>33.14 &rarr; 14.02</code> Words onto <code>32.12</code>-Word Invariant (<code>Attack 195</code>)</div>
      </div>
    </div>

    <h2>1. The Zodiac <code>@Cc</code> Ring vs. <code>@Lz</code> Degree-Label Syntactic Split (<code>z = +8.81 / +7.00</code>) &amp; <code>75.14%</code> Root Stem Sharing (<code>Attack 193</code>)</h2>
    <p style="color: var(--muted);">
      Across all <strong>12 Zodiac folios (<code>964</code> <code>@Cc</code> ring words + <code>350</code> <code>@Lz</code> degree-label words)</strong>, <strong>75.14% (<code>263/350</code>) of <code>@Lz</code> degree tokens share their canonical root stem with the <code>@Cc</code> concentric rings</strong> (<code>35.71%</code> exact words across the Zodiac, <code>53.43%</code> stem match on the exact same medallion). Yet the two registers divide into complementary grammatical roles: <code>@Lz</code> degree labels surge <strong>1.68× in <code>o-</code> nominal citation prefixes (68.00% vs. 40.56%, z = +8.81)</strong>, while <code>@Cc</code> concentric rings surge <strong>3.14× in <code>ch-/sh-</code> verbal participles (26.04% vs. 8.29%, z = +7.00)</strong>:
    </p>
    <div style="overflow-x: auto; margin-bottom: 2.2rem;">
      <table id="zodiacCcLzTable">
        <thead>
          <tr>
            <th>Folio</th>
            <th>Sign &amp; Month</th>
            <th><code>@Cc</code> Ring Words</th>
            <th><code>@Lz</code> Degree Words</th>
            <th>Same-Wheel Exact Match</th>
            <th>Same-Wheel Stem Match</th>
            <th>Shared Exact Words (Click to Decode)</th>
          </tr>
        </thead>
        <tbody></tbody>
      </table>
    </div>

    <h2>2. Balneological Galleries on <code>f80r</code> (<code>100.0%</code> Balneo Stem Echo) &amp; <code>f82r</code> Dual-Arc Fountain + Rare <code>-g</code> Label Stop (<code>z = +5.42</code>, <code>Attack 194</code>)</h2>
    <p style="color: var(--muted);">
      On <code>f80r</code> (Upper 8-Nymph Gallery with Nymph #5 <code>okary</code> inside a tiered blue pedestal basin + right-margin water conduit <code>okar</code> feeding a pitcher), <strong>100.0% (<code>10/10</code>) of diagram callout stems are echoed across Balneological prose (<code>70.0%</code> on <code>f80r</code> itself)</strong>, forming the 3-step vowel-liquid gradation <code>okaly &rarr; okolo &rarr; okary</code>. On <code>f82r</code> (Dual-Arc Central Fountain), two vertical shower plumes labeled with <code>dar-</code> ablative stems (<code>darol</code> &amp; <code>darary</code>, with rare <code>-adag</code> in <code>RF1b/IT2a</code>) flank the minimal pair <code>okal &rarr; okaldy</code>:
    </p>
    <div style="overflow-x: auto; margin-bottom: 2.2rem;">
      <table id="f80rF82rLabelsTable">
        <thead>
          <tr>
            <th>Locus</th>
            <th>Type</th>
            <th>Callout Label (Click to Decode)</th>
            <th>Stem</th>
            <th>Physical Position on <code>f80r</code> / <code>f82r</code></th>
            <th>Same-Folio Stem Echo?</th>
            <th>Balneo Prose Stem Echo?</th>
          </tr>
        </thead>
        <tbody></tbody>
      </table>
    </div>

    <h2>3. The Quire 20 Megaparagraph Step-Star Variance Collapse (<code>33.14 &rarr; 14.02</code> Words SD, <code>2.36×</code> Reduction) &amp; <code>32.12</code>-Word Recipe Invariant (<code>Attack 195</code>)</h2>
    <p style="color: var(--muted);">
      Why did EVA transcribers encode <code>f111r.6–35</code> (365 words), <code>f111v.1–25</code> (294 words), and <code>f108v.30–53</code> (261 words) as giant megaparagraphs? Because on the line immediately preceding an Intra-Paragraph Step Star (<code>Line L-1</code>), the scribe finished writing right at the <strong>full right margin</strong> (<strong>33.33% [<code>18/54</code>] right-margin <code>-m</code> stop vs. 8.40% at <code>&lt;$&gt;</code> half-line breaks = 3.97× surge!</strong>), leaving no blank half-line gap on the vellum. Splitting Quire 20's <code>285</code> paragraphs at the <code>54</code> Intra-Paragraph Step Stars (<code>339</code> total star-marked units) collapses the standard deviation by <strong>2.36× (from 33.14 down to 14.02 words)</strong> and brings every megaparagraph into exact alignment with the <strong>32.12-word canonical recipe length</strong>:
    </p>
    <div style="overflow-x: auto; margin-bottom: 2.2rem;">
      <table id="megaparagraphsTable">
        <thead>
          <tr>
            <th>Folio</th>
            <th>Locus Range</th>
            <th>Lines</th>
            <th>Raw Megaparagraph Words</th>
            <th>Step Stars Inside</th>
            <th>Total Star Units</th>
            <th>Mean Words / Star Unit</th>
            <th>First &rarr; Last Word (Click)</th>
          </tr>
        </thead>
        <tbody></tbody>
      </table>
    </div>

    <h2>4. Inside the <code>f108v.30–53</code> Megaparagraph: All <code>8</code> Star-Marked Sub-Clauses (<code>261</code> Words = <code>32.62</code> Words/Unit, <code>Attack 195</code>)</h2>
    <div style="overflow-x: auto;">
      <table id="f108vSubclausesTable">
        <thead>
          <tr>
            <th>Unit #</th>
            <th>Star Tier</th>
            <th>Locus Range</th>
            <th>Words</th>
            <th>First &rarr; Last Word (Click)</th>
            <th><code>qo-</code> / <code>-edy</code></th>
            <th>Shared Exact Words with Previous Unit (Click to Decode)</th>
          </tr>
        </thead>
        <tbody></tbody>
      </table>
    </div>
  </section>

  <!-- TAB 15: WAVE 47 (MILESTONE 200TH DECODING ATTACK COMPENDIUM) -->
  <section id="tab-wave47" class="tab-panel">
    <div class="stat-grid">
      <div class="stat-card">
        <div class="num">25.0% ch/sh</div>
        <div class="lbl">Cancer (<code>f72r3</code>, <code>jolh</code>) Active Verbal Surge (<code>41 / 164</code> Active Stems vs. 21.23% Baseline, <code>Attack 197</code>)</div>
      </div>
      <div class="stat-card">
        <div class="num">+6.10 z</div>
        <div class="lbl">Quire 9 (<code>f67v1/v2</code>) Velar <code>-g</code> Stop Epicenter (<code>9.31×</code> Lift vs. Corpus Baseline, p &lt; 10⁻⁹, <code>Attack 198</code>)</div>
      </div>
      <div class="stat-card">
        <div class="num">86.97% Stem Echo</div>
        <div class="lbl"><code>f75r</code> Grand Waterfall Basin Acts as Master Lexical Hub for All 18 Downstream Balneo Folios (<code>Attack 199</code>)</div>
      </div>
      <div class="stat-card">
        <div class="num">Milestone 200</div>
        <div class="lbl">Master Retrospective &amp; Macro-Synthesis across 200 Computational Decoding Attacks (<code>Attack 200</code>)</div>
      </div>
    </div>

    <h2>1. The Unfolded <code>p131</code> Zodiac Sheet: Taurus II (<code>f72r1</code>), Gemini (<code>f72r2</code>), Cancer (<code>f72r3</code>) &amp; Prefix Inversion (<code>Attack 197</code>)</h2>
    <p style="color: var(--muted);">
      Unfolding the three-panel foldout sheet on Yale Beinecke page 131 reveals a continuous 18-stem lexical continuum linking the Taurus barrel bathers, the Gemini twin youths with their uncaptioned 12:00 nymph (restoring the universal 30-degree layout), and the Cancer 10-legged crayfish with its 30 decan degree-nymphs (<code>12 + 11 + 7 = 30°</code>). Across the foldout, vocabulary inverts from early spring <code>ot-/op-</code> prefix dominance (<code>1.50×</code>) to summer prefix parity and a <code>25.0%</code> active verbal surge (<code>ch-/sh-</code>):
    </p>
    <div style="overflow-x: auto; margin-bottom: 2.2rem;">
      <table id="wave47ZodiacTable">
        <thead>
          <tr>
            <th>Folio (Panel)</th>
            <th>Sign &amp; Month</th>
            <th>Concentric Rings</th>
            <th>Degree Loci</th>
            <th>Decan Calibration</th>
            <th>Barreled Bathers</th>
            <th>Active <code>ch-/sh-</code> Rate</th>
            <th>Prefix Bias (<code>ot/ok</code>)</th>
          </tr>
        </thead>
        <tbody></tbody>
      </table>
    </div>

    <h2>2. Astronomical Diptych <code>f67v1</code> &amp; <code>f67v2</code> (Yale <code>p123</code>): Smiling Sun Wheel, Four-Corner Cosmology &amp; Velar <code>-g</code> Stop Epicenter (<code>Attack 198</code>)</h2>
    <p style="color: var(--muted);">
      Folio <code>f67v1</code> features a 12-sector Sun Wheel with a central smiling face, 17 radiating text spokes, and 39 painted stars (3 cobalt-blue, 36 yellow-ochre), opening with <code>damamm</code>. Facing it on <code>f67v2</code> is a four-corner cosmological diagram with 8 dendritic spoke terminals and 4 corner prose paragraphs (8.5 &plusmn; 1.8 words) alternating between dental <code>t-</code> and nominal <code>ok-</code> initials. Together they form the densest cluster of rare velar <code>-g</code> stops across the entire codex (<code>3.70%</code> vs. <code>0.40%</code> corpus rate, <strong>z = +6.10, p &lt; 10⁻⁹</strong>):
    </p>
    <div style="overflow-x: auto; margin-bottom: 2.2rem;">
      <table id="wave47F67vTable">
        <thead>
          <tr>
            <th>Locus</th>
            <th>Velar Token (Click to Decode)</th>
            <th>Context Snippet</th>
            <th>Grammatical / Structural Function</th>
          </tr>
        </thead>
        <tbody></tbody>
      </table>
    </div>

    <h2>3. Folio <code>f75r</code> Grand Waterfall Basin: Master Lexical Reservoir for the Balneological Section (<code>86.97%</code> Stem Coverage, <code>Attack 199</code>)</h2>
    <p style="color: var(--muted);">
      Folio <code>f75r</code> (385 words, 53 lines) serves as the introductory reservoir for the entire 19-folio Balneological section. Across all 18 downstream folios (<code>f75v–f84v</code>, 5,941 words), <strong>86.97% (5,167 / 5,941) of all words share their canonical root stem with <code>f75r</code></strong>, and <strong>53.63% (3,186 / 5,941) are exact vocabulary matches</strong>, proving that the balneological section is linguistically unified:
    </p>
    <div style="overflow-x: auto;">
      <table id="wave47BalneoHubTable">
        <thead>
          <tr>
            <th>Downstream Balneo Folio</th>
            <th>Total Words</th>
            <th>Exact Matches with <code>f75r</code></th>
            <th>Stem Matches with <code>f75r</code></th>
            <th>Stem Coverage Rate (%)</th>
          </tr>
        </thead>
        <tbody></tbody>
      </table>
    </div>
  </section>

  <!-- TAB 16: WAVE 48 (POST-200 SYNTHESIS & V14.0 MASTER RELEASE) -->
  <section id="tab-wave48" class="tab-panel">
    <div class="stat-grid">
      <div class="stat-card">
        <div class="num">10+16+4 = 30°</div>
        <div class="lbl">Sagittarius (<code>f73v</code>) Replicates Scorpio (<code>f73r</code>) 30-Nymph Overflow Architecture with 100% Precision (<code>Attack 201</code>)</div>
      </div>
      <div class="stat-card">
        <div class="num">+2.26 z</div>
        <div class="lbl">360° Ecliptic Prefix Drift: Spring <code>ot-/op-</code> (<code>2.30×</code>) &rarr; Summer Parity (<code>1.00×</code>) &rarr; Autumn Return (<code>1.48×</code>, <code>Attack 201</code>)</div>
      </div>
      <div class="stat-card">
        <div class="num">t = +4.36</div>
        <div class="lbl">Pharmaceutical Container (<code>@Lc</code>, 7.11 chars) vs. Flora Simple (<code>@Lf</code>, 5.77 chars) Morphological Inversion (<code>Attack 202</code>)</div>
      </div>
      <div class="stat-card">
        <div class="num">+12.20 z</div>
        <div class="lbl">Quire 20 Binary Star Parity Alternation: 85.28% Consecutive Dotted &harr; Plain Stars (100% on 17 Folios, <code>Attack 203</code>)</div>
      </div>
    </div>

    <h2>1. The 360° Ecliptic Seasonal Prefix Drift across All 12 Surviving Zodiac Folios (<code>Attack 201</code>)</h2>
    <p style="color: var(--muted);">
      Mapping word counts and nominal prefixes across celestial longitude reveals a highly significant seasonal drift (contingency &chi;² = 14.653, permutation test <strong>z = +2.26, p = 0.023</strong>). Spring Equinox signs (Pisces &rarr; Taurus) heavily favor <code>ot-/op-</code> ablative/source prefixes (<code>2.30×</code>); Summer Solstice signs (Gemini &rarr; Leo) collapse into exact 1-to-1 parity (<code>18.99%</code> vs. <code>18.99%</code>, ratio = <code>1.00</code>); and Autumn Equinox signs (Virgo &rarr; Sagittarius) swing back toward <code>ot-/op-</code> (<code>1.48×</code>):
    </p>
    <div style="overflow-x: auto; margin-bottom: 2.2rem;">
      <table id="wave48EclipticTable">
        <thead>
          <tr>
            <th>Folio</th>
            <th>Zodiac Sign</th>
            <th>Season</th>
            <th>Longitude λ</th>
            <th>Words</th>
            <th><code>ot-/op-</code> Count (%)</th>
            <th><code>ok-/of-</code> Count (%)</th>
            <th>Ratio <code>ot / ok</code></th>
            <th><code>ch-/sh-</code> Count (%)</th>
          </tr>
        </thead>
        <tbody></tbody>
      </table>
    </div>

    <h2>2. Quire 20 Star-Point Morphology vs. Gallows Opening Grammar (<code>Attack 203</code>)</h2>
    <p style="color: var(--muted);">
      Across all 322 margin stars in Quire 20 (<code>f103r–f116r</code>), the physical number of star points directly governs the syntactic opening of the subsequent recipe: <strong>7-point stars open with <code>P/F</code> Gallows at 56.04% vs. <code>T/K</code> Gallows at 21.98% (ratio = 2.55)</strong>, whereas <strong>8-point stars exhibit near gallows parity (40.65% <code>P/F</code> vs. 33.33% <code>T/K</code>, ratio = 1.22)</strong> (<strong>&chi;² = 6.9728, z = +2.64, p = 0.0083</strong>, Odds Ratio <strong>OR = 2.091</strong>):
    </p>
    <div style="overflow-x: auto; margin-bottom: 2.2rem;">
      <table id="wave48StarMorphTable">
        <thead>
          <tr>
            <th>Star Morphology Type</th>
            <th>Total Star Units</th>
            <th>Mean Words / Unit</th>
            <th><code>P/F</code> Gallows Opener (%)</th>
            <th><code>T/K</code> Gallows Opener (%)</th>
            <th>Ratio <code>P/F</code> to <code>T/K</code></th>
            <th>Procedural Step Particles</th>
          </tr>
        </thead>
        <tbody></tbody>
      </table>
    </div>

    <h2>3. Quire 20 Binary Star Parity Alternation Census (Dotted &harr; Plain Star Centers, <code>Attack 203</code>)</h2>
    <p style="color: var(--muted);">
      Across all 299 margin star transitions in Quire 20, margin stars alternate strictly 1-to-1 between Dotted (D) and Plain (P) centers across <strong>85.28% (255 / 299) of all consecutive transitions (z = +12.20, p &lt; 10⁻³³ vs. binomial 50% null)</strong>. On <strong>17 out of 23 folios (73.91%)</strong>, the alternation rate is literally <strong>100.0% perfect</strong>:
    </p>
    <div style="overflow-x: auto; margin-bottom: 2.2rem;">
      <table id="wave48StarParityTable">
        <thead>
          <tr>
            <th>Folio</th>
            <th>Star Count</th>
            <th>Transitions</th>
            <th>Alternations</th>
            <th>Alternation Status</th>
            <th>Sequence Sample (D=Dotted, P=Plain)</th>
          </tr>
        </thead>
        <tbody></tbody>
      </table>
    </div>

    <h2>4. The <code>otar arody</code> Stoichiometric Formulation Bridge into Quire 20 Recipes (<code>Attack 202</code>)</h2>
    <p style="color: var(--muted);">
      Pharmaceutical albarelli registers and cut-root monographs form a direct stoichiometric bridge into clinical recipe formulations: <strong>64.49% of all Pharmaceutical labels share their canonical stem with Quire 20 Starred Recipes</strong>, and <strong>47.35% match the opening 3 words of recipes</strong>. The branching taproot label <code>&lt;f88v.4,@Lf&gt; otar.arody</code> directly anticipates the universal recipe openers across the entire formulary:
    </p>
    <div style="overflow-x: auto;">
      <table>
        <thead>
          <tr>
            <th>Locus</th>
            <th>Section</th>
            <th>Transcribed Token / Clause</th>
            <th>Syntactic / Pharmaceutical Role</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><code>f88v.4</code></td>
            <td>Pharmaceutical (<span class="badge">@Lf</span>)</td>
            <td><span class="word-chip" onclick="setWord('otar.arody')"><strong>otar.arody</strong></span></td>
            <td>Source Cut Root Label: "Earth/Root Essence Formula"</td>
          </tr>
          <tr>
            <td><code>f105r.6</code></td>
            <td>Starred Recipes (<span class="badge">&lt;%&gt;</span>)</td>
            <td><span class="word-chip" onclick="setWord('par.arody')"><strong>par.arody</strong></span> .shedeeey.qopchedy</td>
            <td>Recipe Opener: Primary Root Compound Infusion</td>
          </tr>
          <tr>
            <td><code>f112v.39</code></td>
            <td>Starred Recipes (<span class="badge">&lt;%&gt;</span>)</td>
            <td><span class="word-chip" onclick="setWord('teodarody')"><strong>teodarody</strong></span> .opcheed.okaiin</td>
            <td>Starred Recipe Opener: Compounded Root Decoction</td>
          </tr>
          <tr>
            <td><code>f114v.37</code></td>
            <td>Starred Recipes (<span class="badge">+P0</span>)</td>
            <td>chey. <span class="word-chip" onclick="setWord('tar.arody')"><strong>tar.arody</strong></span></td>
            <td>Terminal Recipe Clause: Compounded Root Finish</td>
          </tr>
          <tr>
            <td><code>f115v.13</code></td>
            <td>Starred Recipes (<span class="badge">&lt;%&gt;</span>)</td>
            <td><span class="word-chip" onclick="setWord('pchdarody')"><strong>pchdarody</strong></span> .pcheed.rar.tcheody</td>
            <td>Gallows Starred Recipe Opener: Master Root Extract</td>
          </tr>
          <tr>
            <td><code>f116r.19</code></td>
            <td>Starred Recipes (<span class="badge">&lt;%&gt;</span>)</td>
            <td>chetar. <span class="word-chip" onclick="setWord('qotar.ar.arody')"><strong>qotar.ar.arody</strong></span> .chcthy</td>
            <td>Penultimate Formulary Clause: Active Root Compound</td>
          </tr>
        </tbody>
      </table>
    </div>
  </section>

  <!-- TAB 17: WAVE 49 (10°+5° DECAN LAW, BARREL HINGE, UNFOLDED SHEETS & CURRIER B HERBAL BRIDGE V15.0) -->
  <section id="tab-wave49" class="tab-panel">
    <div class="stat-grid">
      <div class="stat-card">
        <div class="num">(10°+5°)×2 = 30°</div>
        <div class="lbl">4/4 Split Aries &amp; Taurus Medallions Reconcile 15° Half-Signs With Three 10° Decans + <code>f72r1</code> Barrel-to-Naked Hinge (z = +15.98, <code>Attack 205</code>)</div>
      </div>
      <div class="stat-card">
        <div class="num">84.13% / +6.31 z</div>
        <div class="lbl">Global Balneo Callout Stem Echo (<code>106/126</code>; <code>okalo</code> 5-Loop Coil &amp; Crossed Retorts) + Codex-Wide Same-Leaf (z = +6.31) &amp; Facing (z = +5.18) Continuity (<code>Attack 206</code>)</div>
      </div>
      <div class="stat-card">
        <div class="num">6.00× / -3.54 z</div>
        <div class="lbl">Unfolded <code>p179</code> (<code>f100v | f101r</code>) Cross-Fold Label Echo Jump (<code>7.14% &rarr; 42.86%</code>) &amp; Unlabeled <code>f101r</code> Nominal Absorption (<code>Attack 207</code>)</div>
      </div>
      <div class="stat-card">
        <div class="num">+4.75 z / +3.68 z</div>
        <div class="lbl">The 32-Folio Currier B Herbal Clinical Bridge (<code>5.82×</code> <code>-edy/-eey</code> Surge) Into Balneological (z = +4.75) &amp; Quire 20 Recipes (z = +3.68, <code>Attack 208</code>)</div>
      </div>
    </div>

    <h2>1. The <code>(10° + 5°) + (10° + 5°) = 30°</code> Decan Reconciliation Law &amp; <code>f72r1</code> Barrel-to-Naked Hinge (<code>Attack 205</code>)</h2>
    <p style="color: var(--muted);">
      All 4 split-sign Zodiac medallions (<code>f70v1</code> Aries I, <code>f71r</code> Aries II, <code>f71v</code> Taurus I Manger, <code>f72r1</code> Taurus II Dark Bull) divide their 15 <code>@Lz</code> degree-nymphs into <strong>10 Inner Full-Circle Nymphs (1 full 10° Decan) + 5 Outer Top-Arc Nymphs (1/2 Decan = 5°)</strong>, so combining Medallion I + Medallion II reconciles two 15° half-signs with three 10° classical Decans (<code>10° + [5°+5°] + 10° = 30°</code>). Furthermore, <code>f72r1</code> (Taurus II) is the exact mid-medallion hinge (<strong>&chi;² = 255.28, z = +15.98</strong>) where the artist transitioned from barreled nymphs (<code>5/10</code> inner) to full-body naked nymphs (<code>0/5</code> outer top arc):
    </p>
    <div style="overflow-x: auto; margin-bottom: 2.2rem;">
      <table id="wave49BarrelTable">
        <thead>
          <tr>
            <th>Folio</th>
            <th>Sign &amp; Month</th>
            <th>Painted Nymphs</th>
            <th>Barreled Nymphs</th>
            <th>Naked Full-Body Nymphs</th>
            <th>Barreled Rate (%)</th>
            <th>Decan &amp; Visual Architecture</th>
          </tr>
        </thead>
        <tbody></tbody>
      </table>
    </div>

    <h2>2. Balneological Organ/Condenser Conduits on <code>f77v</code> (5-Loop Coil <code>okalo</code>) &amp; <code>f83v</code> (Crossed Bladder Retorts, <code>Attack 206</code>)</h2>
    <p style="color: var(--muted);">
      Across all 126 Balneological callout words on 11 bath folios, <strong>84.13% (106 / 126) share their canonical root stem with Balneological prose (68.25% on the exact same folio)</strong>. Below are the 18 callout labels across <code>f77v</code> (<code>81.82%</code> local stem echo, featuring the 5-loop intestinal/condenser coil <code>&lt;f77v.13,@Lt&gt; okalo</code>) and <code>f83v</code> (<code>100.0%</code> Balneo stem echo, featuring crossed green kidney/bladder retorts and bifurcated Y-tube):
    </p>
    <div style="overflow-x: auto; margin-bottom: 2.2rem;">
      <table id="wave49BalneoCalloutsTable">
        <thead>
          <tr>
            <th>Locus</th>
            <th>Type</th>
            <th>Callout Word(s) (Click to Decode)</th>
            <th>Canonical Stem(s)</th>
            <th>Echo in Same-Folio Prose</th>
            <th>Echo in Balneo Prose</th>
            <th>Echo in Quire 20 Recipes</th>
          </tr>
        </thead>
        <tbody></tbody>
      </table>
    </div>

    <h2>3. The 16-Folio Pharmaceutical Supply Chain &amp; Unfolded Sheets <code>p163</code> (<code>f88v–f89r2</code>) and <code>p179</code> (<code>f100v | f101r</code>, <code>Attack 207</code>)</h2>
    <p style="color: var(--muted);">
      On unfolded sheet <code>p179</code> (<code>f100v | f101r</code>), left-column <code>f100v</code> echoes only <code>7.14%</code> (<code>1/14</code>) of its plant labels in its own short paragraph, but <strong>42.86% (6 / 14: <code>okam, sory, choldy, opakam, opor, otar</code>) echo across the vertical fold inside <code>f101r</code>'s ultra-wide prose (6.00× jump!)</strong>, while <code>f101r</code>'s 28 unlabeled plants drive <strong>55.07% <code>o-/d-/s-</code> nominal absorption (<code>qo-</code> suppressed 2.67×, z = -3.54)</strong>:
    </p>
    <div style="overflow-x: auto; margin-bottom: 2.2rem;">
      <table id="wave49PharmaTable">
        <thead>
          <tr>
            <th>Folio (PDF Page)</th>
            <th>Labels (<code>@Lc / @Lf</code>)</th>
            <th>Prose Lines (Words/Line)</th>
            <th><code>qo-</code> Rate (%)</th>
            <th>Same-Folio Stem Echo</th>
            <th>Same-Sheet Stem Echo</th>
            <th>3-Stage Supply Chain Bridge</th>
          </tr>
        </thead>
        <tbody></tbody>
      </table>
    </div>

    <h2>4. Top 12 Currier B Herbal Clinical Bridge Folios Into Balneology (z = +4.75) &amp; Quire 20 Recipes (z = +3.68, <code>Attack 208</code>)</h2>
    <p style="color: var(--muted);">
      Compared to the 94 Currier A Herbal folios (<code>2.78%</code> <code>-edy/-eey</code>), the 32 Currier B Herbal folios (<code>3,365</code> words by Scribes 2 &amp; 3, including <code>f34r</code> and <code>f39r</code>) surge <strong>5.82× in <code>-edy/-eey</code> active decoction suffixes (16.18%)</strong>, achieving a <strong>1.26× Stem Jaccard Lift with Balneological (z = +4.75, 79.68% token coverage)</strong> and a <strong>1.20× Lift with Quire 20 Starred Recipes (z = +3.68, 82.61% token coverage)</strong>:
    </p>
    <div style="overflow-x: auto;">
      <table id="wave49CurrierBHerbalTable">
        <thead>
          <tr>
            <th>Folio (PDF Page)</th>
            <th>Scribe Hand</th>
            <th>Words (<code>&lt;-&gt;</code> Intrusions)</th>
            <th><code>qo-</code> Rate (%)</th>
            <th><code>-edy/-eey</code> Rate (%)</th>
            <th>Balneo Token Stem Match</th>
            <th>Quire 20 Recipe Token Stem Match</th>
          </tr>
        </thead>
        <tbody></tbody>
      </table>
    </div>
  </section>

  <!-- TAB 18: MILESTONE WAVE 50 (v16.0) -->
  <section id="tab-wave50" class="tab-panel">
    <h2>1. The Complete Scribe 5 (<code>$H=5</code>) 7-Folio Corpus (<code>925</code> Words) &amp; Global <code>@Lp</code> Plant-Header Census (<code>f2r, f41v, f65r</code> — <code>Attack 209</code>)</h2>
    <p style="color: var(--muted);">
      Across the entire manuscript, <strong>Scribe 5 (<code>$H=5</code>)</strong> writes exactly <strong>7 folios (<code>925</code> words, <code>18.38%</code> <code>-edy/-eey</code>, <code>36</code> <code>&lt;-&gt;</code> intrusions)</strong>, including <code>f41v</code> (bearing <code>&lt;f41v.1,@Lp&gt; keer[e:o]dal</code>—one of only 3 <code>@Lp</code> plant headers in the codex alongside <code>f2r</code> <code>ytoail</code> and <code>f65r</code>'s 3-word alliterative <code>-m</code> triad <code>otaim.dam.alam</code>, <code>p = 2.68e-5</code>):
    </p>
    <div style="overflow-x: auto; margin-bottom: 2.2rem;">
      <table id="wave50Scribe5Table">
        <thead>
          <tr>
            <th>Folio (Quire)</th>
            <th>Section &amp; Language</th>
            <th>Words (Body / Labels)</th>
            <th><code>@Lp</code> Plant Header</th>
            <th><code>-edy/-eey</code> Rate</th>
            <th><code>q-</code> Initial Rate</th>
            <th>Top Canonical Stems</th>
          </tr>
        </thead>
        <tbody></tbody>
      </table>
    </div>

    <h2>2. Folio <code>f84v</code> Quire 13 Closing (<code>13m</code>): The 20-Word <code>@P1</code> Showerhead Header &amp; <code>@Pb</code> Right-Margin Callout Column (<code>60.0%</code> Local / <code>80.0%</code> Balneo Echo, <code>z = +3.96</code>, <code>Attack 210</code>)</h2>
    <p style="color: var(--muted);">
      Alongside <code>f76r &lt;-&gt; f76v</code> (<code>79.50%</code> stem continuity onto the illustrated verso) and <code>f81v</code> (14-nymph pool with single 2-word callout <code>otain.olkal</code>, <code>100%</code> echo), visual inspection of <code>f84v</code> (<code>p155</code>, bearing quire signature <code>13m</code>) reveals 20 callout tokens in <code>@P1</code> and <code>@Pb</code> with <strong>60.00% local prose stem echo (z = +3.96, p = 0.0010) and 80.00% Balneological stem echo</strong>:
    </p>
    <div style="overflow-x: auto; margin-bottom: 2.2rem;">
      <table id="wave50F84vCalloutsTable">
        <thead>
          <tr>
            <th>Callout Word (Click to Decode)</th>
            <th>Margin Zone</th>
            <th>Canonical Stem</th>
            <th>Exact Match in <code>f84v</code> Prose?</th>
            <th>Stem Match in <code>f84v</code> Prose?</th>
            <th>Stem Match in Balneo (<code>Quire 13</code>)?</th>
            <th><code>f84v</code> Prose Cognates (Click to Decode)</th>
          </tr>
        </thead>
        <tbody></tbody>
      </table>
    </div>

    <h2>3. The <code>f90</code> Foldout Inversion (<code>p165–p167</code>) &amp; Multi-Intrusion (<code>&lt;-&gt; X &lt;-&gt;</code>) Micro-Corridor Compression Law on <code>f93v</code> &amp; <code>f90v1</code> (<code>59.54%</code> Single-Token, <code>z = -4.00</code>, <code>Attack 211</code>)</h2>
    <p style="color: var(--muted);">
      While physical bleed-through proves that <code>p166</code> (bearing the foliator's <code>90</code> in the top-right corner and mislabeled <code>90r</code> in both PDF catalogs) is actually <strong><code>f90v2</code></strong> (and <code>p167</code> is <strong><code>f90v1</code></strong> bearing quire signature <code>15m</code>), lines threading across 3 flower stems on <code>f90v1</code> and 3 red-berry spikes on <code>f93v</code> exemplify the <strong>Multi-Intrusion Micro-Corridor Law (z = -4.00, p &lt; 0.0001)</strong>:
    </p>
    <div style="overflow-x: auto; margin-bottom: 2.2rem;">
      <table id="wave50MultiIntrusionsTable">
        <thead>
          <tr>
            <th>Folio &amp; Line</th>
            <th><code>&lt;-&gt;</code> Intrusions</th>
            <th>Line Segments</th>
            <th>Interior Micro-Corridor Tokens (Click to Decode)</th>
            <th>Full Segmented Line Breakdown</th>
          </tr>
        </thead>
        <tbody></tbody>
      </table>
    </div>

    <h2>4. Folio <code>f113v</code> Ultra-Dense Quire 20 Recipe Compendium (<code>499</code> Words, <code>15</code> Starred Recipes): The <code>93.33%</code> <code>p-/f-/t-</code> Gallows Star-Opener Law (<code>z = +10.52</code>, <code>Attack 212</code>)</h2>
    <p style="color: var(--muted);">
      On <code>f113v</code> (<code>p201</code>, paired with <code>f114r</code> in a <code>947</code>-word facing spread with <code>65.65%</code> token stem continuity), <strong>14 / 15 (93.33%) of the starred recipes begin with a <code>p-/f-/t-</code> gallows word</strong> (and <code>#11</code> <code>ofaral</code> is <code>o+f</code> gallows = <code>15/15 = 100%</code> vs <code>10.36%</code> baseline, <code>z = +10.52</code>), including <strong>7 / 15 (46.67%) opening with the <code>pol-/por-</code> recipe header</strong>:
    </p>
    <div style="overflow-x: auto;">
      <table id="wave50F113vRecipesTable">
        <thead>
          <tr>
            <th>Starred Recipe #</th>
            <th>Start Line</th>
            <th>Word Count</th>
            <th>Star-Opener Word (Click to Decode)</th>
            <th>Opener Canonical Stem</th>
            <th>Closing Word (Click to Decode)</th>
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

function renderMilestone200Tab() {{
  const spBody = document.querySelector("#stateMachineProfilesTable tbody");
  spBody.innerHTML = (DATA.state_profiles || []).map(sp => {{
    const chips = (sp.top_words || []).map(tw =>
      `<span class="word-chip" onclick="setWord('${{tw.word}}')">${{tw.word}} (${{tw.count}})</span>`
    ).join(" ");
    return `
      <tr>
        <td><strong><code>${{sp.state}}</code></strong></td>
        <td><strong>${{sp.count}}</strong> (${{sp.corpus_pct}}%)</td>
        <td><strong>${{sp.line_initial_lift}}×</strong></td>
        <td><strong>${{sp.line_medial_lift}}×</strong></td>
        <td><strong>${{sp.line_final_lift}}×</strong></td>
        <td>${{chips}}</td>
      </tr>
    `;
  }}).join("");

  const stBody = document.querySelector("#stateTransitionsTable tbody");
  const attrRows = (DATA.state_attractions || []).slice(0, 6).map(r => `
    <tr>
      <td><span class="badge" style="background:var(--green-soft);color:var(--green);">Attraction</span></td>
      <td><code>${{r.from}}</code></td>
      <td><code>${{r.to}}</code></td>
      <td><strong>${{r.observed}}</strong></td>
      <td>${{r.expected}}</td>
      <td>${{(r.prob * 100).toFixed(2)}}%</td>
      <td><strong>${{r.lift}}×</strong></td>
    </tr>
  `);
  const prohibRows = (DATA.state_prohibitions || []).slice(0, 6).map(r => `
    <tr>
      <td><span class="badge" style="background:var(--accent-soft);color:var(--accent);">Prohibition</span></td>
      <td><code>${{r.from}}</code></td>
      <td><code>${{r.to}}</code></td>
      <td><strong>${{r.observed}}</strong></td>
      <td>${{r.expected}}</td>
      <td>${{(r.prob * 100).toFixed(2)}}%</td>
      <td><strong>${{r.lift}}×</strong></td>
    </tr>
  `);
  stBody.innerHTML = [...attrRows, ...prohibRows].join("");

  const ptBody = document.querySelector("#ptPrColophonsTable tbody");
  ptBody.innerHTML = (DATA.pt_pr_lines || []).map(l => {{
    const wChips = (l.words || []).map(w => `<span class="word-chip" onclick="setWord('${{w}}')">${{w}}</span>`).join(" ");
    const sChips = (l.stem_shared_in_folio || []).map(w => `<span class="word-chip" onclick="setWord('${{w}}')">${{w}}</span>`).join(" ") || "—";
    return `
      <tr>
        <td><strong><code>${{l.folio}}.${{l.line_no}}</code></strong></td>
        <td><code>${{l.loc}}</code></td>
        <td>${{l.section}} (<code>$L=${{l.language}}</code>)</td>
        <td>${{wChips}}</td>
        <td>${{sChips}}</td>
      </tr>
    `;
  }}).join("");

  const wtBody = document.querySelector("#wheelTiersTable tbody");
  wtBody.innerHTML = (DATA.wheel_tiers || []).map(t => `
    <tr>
      <td><strong><code>${{t.category}}</code></strong></td>
      <td><strong>${{t.loci_count}}</strong></td>
      <td><strong>${{t.total_words}}</strong></td>
      <td><strong>${{t.mean_words_per_locus}}</strong> words/locus</td>
      <td>${{t.nominal_aiin_ar_al_pct}}%</td>
      <td>${{t.verbal_edy_ey_pct}}%</td>
    </tr>
  `).join("");
}}

function renderWave44Tab() {{
  const s4Body = document.querySelector("#scribe4Table tbody");
  const s4 = DATA.scribe4_profiles || {{}};
  s4Body.innerHTML = Object.entries(s4).map(([hand, p]) => {{
    const hl = hand === "Scribe_4" ? 'style="background:var(--gold-soft);font-weight:700;"' : '';
    return `
      <tr ${{hl}}>
        <td><strong>${{hand.replace("_", " ")}}</strong></td>
        <td>${{p.n_words}}</td>
        <td>${{p.n_types}} (${{(p.ttr * 100).toFixed(1)}}%)</td>
        <td><strong>${{(p.ok_ot_rate * 100).toFixed(2)}}%</strong></td>
        <td><strong>${{(p.ody_ady_rate * 100).toFixed(2)}}%</strong></td>
        <td>${{(p.qo_rate * 100).toFixed(2)}}%</td>
        <td>${{(p.edy_rate * 100).toFixed(2)}}%</td>
      </tr>
    `;
  }}).join("");

  const mpBody = document.querySelector("#minimalPairsTable tbody");
  mpBody.innerHTML = (DATA.minimal_pairs || []).map(m => {{
    const badge = m.same_stem
      ? `<span class="badge" style="background:var(--green-soft);color:var(--green)">Yes (Same Stem)</span>`
      : `<span class="badge">Minimal Pair</span>`;
    return `
      <tr>
        <td><strong><code>${{m.folio}}</code></strong> (<code>$I=${{m.sec}}</code>)</td>
        <td><span class="word-chip" onclick="setWord('${{m.w1}}')"><strong>${{m.w1}}</strong></span></td>
        <td><span class="word-chip" onclick="setWord('${{m.w2}}')"><strong>${{m.w2}}</strong></span></td>
        <td><strong>${{m.edit_distance}}</strong></td>
        <td>${{badge}}</td>
        <td><code>${{m.stem}}</code></td>
      </tr>
    `;
  }}).join("");

  const f103Body = document.querySelector("#f103rRecipesTable tbody");
  f103Body.innerHTML = (DATA.f103r_recipes || []).map(r => {{
    const starBadge = r.star_visual_type === "Solid_Red"
      ? `<span class="badge" style="background:var(--accent-soft);color:var(--accent)">Solid Red Star (Odd)</span>`
      : `<span class="badge" style="background:var(--blue-soft);color:var(--blue)">Outlined White Star (Even)</span>`;
    return `
      <tr>
        <td><strong>Recipe #${{r.recipe_num}}</strong></td>
        <td>${{starBadge}}</td>
        <td><code>${{r.start_line}}</code></td>
        <td>${{r.n_lines}} lines (${{r.n_words}} words)</td>
        <td><span class="word-chip" onclick="setWord('${{r.first_word}}')"><strong>${{r.first_word}}</strong></span></td>
        <td><span class="word-chip" onclick="setWord('${{r.last_word}}')"><strong>${{r.last_word}}</strong></span></td>
        <td><code>qo-</code>: ${{r.qo_count}} | <code>-edy</code>: ${{r.edy_count}}</td>
      </tr>
    `;
  }}).join("");
}}

function renderWave45Tab() {{
  const zBody = document.querySelector("#zodiac30Table tbody");
  zBody.innerHTML = (DATA.zodiac_30_invariant || []).map(z => {{
    const badge = z.exact_30
      ? `<span class="badge" style="background:var(--green-soft);color:var(--green)">Exact 30° Invariant</span>`
      : `<span class="badge" style="background:var(--accent-soft);color:var(--accent)">29 Transcribed / 30 Painted</span>`;
    return `
      <tr>
        <td><strong>${{z.sign}}</strong></td>
        <td><code>${{z.month}}</code></td>
        <td><strong><code>${{z.folios.join(" + ")}}</code></strong></td>
        <td>${{z.breakdown}}</td>
        <td><strong>${{z.total_lz}}</strong></td>
        <td>${{badge}}</td>
      </tr>
    `;
  }}).join("");

  const f77Body = document.querySelector("#f77rLabelsTable tbody");
  f77Body.innerHTML = (DATA.f77r_labels || []).map(l => {{
    const f77Badge = l.in_f77r_prose
      ? `<span class="badge" style="background:var(--green-soft);color:var(--green)">Yes (In f77r Prose)</span>`
      : `<span class="badge">No</span>`;
    const balBadge = l.in_balneo_prose
      ? `<span class="badge" style="background:var(--blue-soft);color:var(--blue)">Yes (In Balneo)</span>`
      : `<span class="badge">No</span>`;
    return `
      <tr>
        <td><code>${{l.locus}}</code></td>
        <td><code>@${{l.ltype}}</code></td>
        <td><span class="word-chip" onclick="setWord('${{l.word}}')"><strong>${{l.word}}</strong></span></td>
        <td><code>${{l.stem}}</code></td>
        <td>${{l.organ}}</td>
        <td>${{f77Badge}}</td>
        <td>${{balBadge}}</td>
      </tr>
    `;
  }}).join("");

  const ipBody = document.querySelector("#intraParaStarsTable tbody");
  ipBody.innerHTML = (DATA.intra_para_stars || []).map(s => {{
    const initBadge = s.is_gallows
      ? `<span class="badge" style="background:var(--accent-soft);color:var(--accent)">Gallows Opener</span>`
      : `<span class="badge" style="background:var(--green-soft);color:var(--green)">Step Particle (${{s.first_word[0]}}-)</span>`;
    return `
      <tr>
        <td><strong><code>${{s.locus}}</code></strong></td>
        <td><code>${{s.star_code}}</code></td>
        <td>${{s.color}} / ${{s.tail}}</td>
        <td><span class="word-chip" onclick="setWord('${{s.first_word}}')"><strong>${{s.first_word}}</strong></span></td>
        <td>${{initBadge}}</td>
        <td><span class="word-chip" onclick="setWord('${{s.prev_last_word}}')"><code>${{s.prev_last_word}}</code></span></td>
      </tr>
    `;
  }}).join("");
}}

function renderWave46Tab() {{
  const zBody = document.querySelector("#zodiacCcLzTable tbody");
  zBody.innerHTML = (DATA.zodiac_cc_lz_rows || []).map(z => {{
    const sharedChips = (z.shared_exact_words || []).length
      ? z.shared_exact_words.map(w => `<span class="word-chip" onclick="setWord('${{w}}')"><strong>${{w}}</strong></span>`).join(" ")
      : `<span style="color:var(--muted)">— (Stem overlap only)</span>`;
    return `
      <tr>
        <td><strong><code>${{z.folio}}</code></strong> (${{z.pdf_page}})</td>
        <td><strong>${{z.sign}}</strong> (<code>${{z.month}}</code>)</td>
        <td>${{z.n_cc_words}} words (${{z.n_cc_rings}} rings)</td>
        <td>${{z.n_lz_words}} words (${{z.n_lz_loci}} loci)</td>
        <td><strong>${{z.lz_in_same_cc_exact_count}} / ${{z.n_lz_words}}</strong> (${{(z.lz_in_same_cc_exact_rate * 100).toFixed(1)}}%)</td>
        <td><strong>${{z.lz_in_same_cc_stem_count}} / ${{z.n_lz_words}}</strong> (${{(z.lz_in_same_cc_stem_rate * 100).toFixed(1)}}%)</td>
        <td>${{sharedChips}}</td>
      </tr>
    `;
  }}).join("");

  const bBody = document.querySelector("#f80rF82rLabelsTable tbody");
  bBody.innerHTML = (DATA.f80r_f82r_labels || []).map(l => {{
    const sameBadge = l.in_same_folio_prose_stem
      ? `<span class="badge" style="background:var(--green-soft);color:var(--green)">Yes (Same Folio)</span>`
      : `<span class="badge">No</span>`;
    const balBadge = l.in_balneo_prose_stem
      ? `<span class="badge" style="background:var(--blue-soft);color:var(--blue)">Yes (In Balneo)</span>`
      : `<span class="badge">No</span>`;
    return `
      <tr>
        <td><strong><code>${{l.locus}}</code></strong></td>
        <td><code>${{l.ltype}}</code></td>
        <td><span class="word-chip" onclick="setWord('${{l.label}}')"><strong>${{l.label}}</strong></span></td>
        <td><code>${{l.stem}}</code></td>
        <td>${{l.position}}</td>
        <td>${{sameBadge}}</td>
        <td>${{balBadge}}</td>
      </tr>
    `;
  }}).join("");

  const mBody = document.querySelector("#megaparagraphsTable tbody");
  mBody.innerHTML = (DATA.megaparagraph_table || []).map(m => {{
    const hl = m.n_step_stars >= 7 ? 'style="background:var(--gold-soft);"' : '';
    return `
      <tr ${{hl}}>
        <td><strong><code>${{m.folio}}</code></strong></td>
        <td><code>${{m.start_locus}}–${{m.end_locus.split('.')[1]}}</code></td>
        <td>${{m.n_lines}} lines</td>
        <td><strong>${{m.n_words}} words</strong></td>
        <td><span class="badge" style="background:var(--accent-soft);color:var(--accent)">+${{m.n_step_stars}} Step Stars</span></td>
        <td><strong>${{m.total_subclauses}} Star Units</strong></td>
        <td><span class="badge" style="background:var(--green-soft);color:var(--green)">${{m.mean_words_per_subclause}} words/unit</span></td>
        <td>
          <span class="word-chip" onclick="setWord('${{m.first_word}}')">${{m.first_word}}</span> &rarr;
          <span class="word-chip" onclick="setWord('${{m.last_word}}')">${{m.last_word}}</span>
        </td>
      </tr>
    `;
  }}).join("");

  const scBody = document.querySelector("#f108vSubclausesTable tbody");
  scBody.innerHTML = (DATA.f108v_subclauses || []).map(sc => {{
    const tierBadge = sc.subclause_num === 1
      ? `<span class="badge" style="background:var(--accent-soft);color:var(--accent)">Primary &lt;%&gt; Start</span>`
      : `<span class="badge" style="background:var(--blue-soft);color:var(--blue)">+P0 Step Star</span>`;
    const sharedChips = (sc.shared_exact_with_prev || []).length
      ? sc.shared_exact_with_prev.map(w => `<span class="word-chip" onclick="setWord('${{w}}')">${{w}}</span>`).join(" ")
      : `<span style="color:var(--muted)">Opening sub-clause</span>`;
    return `
      <tr>
        <td><strong>Unit #${{sc.subclause_num}}</strong></td>
        <td>${{tierBadge}}</td>
        <td><code>${{sc.start_locus}}–${{sc.end_locus.split('.')[1]}}</code> (${{sc.n_lines}}L)</td>
        <td><strong>${{sc.n_words}} words</strong></td>
        <td>
          <span class="word-chip" onclick="setWord('${{sc.first_word}}')"><strong>${{sc.first_word}}</strong></span> &rarr;
          <span class="word-chip" onclick="setWord('${{sc.last_word}}')"><code>${{sc.last_word}}</code></span>
        </td>
        <td><code>qo-</code>: ${{sc.qo_count}} | <code>-edy</code>: ${{sc.edy_count}}</td>
        <td>${{sharedChips}}</td>
      </tr>
    `;
  }}).join("");
}}

function renderWave47Tab() {{
  const p131Body = document.querySelector("#wave47ZodiacTable tbody");
  if (p131Body) {{
    p131Body.innerHTML = (DATA.wave47_p131_panels || []).map(p => `
      <tr>
        <td><strong><code>${{p.folio}}</code></strong> (${{p.quadrant}})</td>
        <td><strong>${{p.sign}}</strong> (<code>${{p.month}}</code>)</td>
        <td>${{p.rings}} rings (${{p.ring_words}} words)</td>
        <td>${{p.degree_loci}} loci (${{p.degree_words}} words)</td>
        <td><span class="badge" style="background:var(--accent-soft);color:var(--accent)">${{p.decan_calibration}}</span></td>
        <td>${{p.barreled_bathers}}</td>
        <td><strong>${{p.ch_sh_rate}}</strong></td>
        <td><span class="badge" style="background:var(--blue-soft);color:var(--blue)">${{p.ot_bias}}</span></td>
      </tr>
    `).join("");
  }}

  const gBody = document.querySelector("#wave47F67vTable tbody");
  if (gBody) {{
    gBody.innerHTML = (DATA.wave47_velar_g_tokens || []).map(g => `
      <tr>
        <td><strong><code>${{g.locus}}</code></strong></td>
        <td><span class="word-chip" onclick="setWord('${{g.token}}')"><strong>${{g.token}}</strong></span></td>
        <td><code>${{g.context || ''}}</code></td>
        <td>${{g.category || 'Velar -g stop'}}</td>
      </tr>
    `).join("");
  }}

  const hBody = document.querySelector("#wave47BalneoHubTable tbody");
  if (hBody) {{
    hBody.innerHTML = (DATA.wave47_balneo_hub_coverage || []).map(h => {{
      const pct = (h.stem_match_rate * 100).toFixed(1);
      const exactPct = (h.exact_match_rate * 100).toFixed(1);
      const hl = h.stem_match_rate >= 0.88 ? 'style="background:var(--green-soft);"' : '';
      return `
        <tr ${{hl}}>
          <td><strong><code>${{h.folio}}</code></strong></td>
          <td>${{h.words}} words</td>
          <td><strong>${{h.exact_matches}}</strong> (${{exactPct}}%)</td>
          <td><strong>${{h.stem_matches}}</strong></td>
          <td><span class="badge" style="background:var(--accent-soft);color:var(--accent)">${{pct}}%</span></td>
        </tr>
      `;
    }}).join("");
  }}
}}

function renderWave48Tab() {{
  const eBody = document.querySelector("#wave48EclipticTable tbody");
  if (eBody) {{
    eBody.innerHTML = (DATA.wave48_ecliptic_drift || []).map(d => {{
      const seasonColor = d.season === 'Spring' ? 'var(--green-soft)' : d.season === 'Summer' ? 'var(--gold-soft)' : 'var(--accent-soft)';
      return `
        <tr>
          <td><strong><code>${{d.folio}}</code></strong></td>
          <td><strong>${{d.sign}}</strong> (<code>${{d.month}}</code>)</td>
          <td><span class="badge" style="background:${{seasonColor}}">${{d.season}}</span></td>
          <td>${{d.longitude_deg}}°</td>
          <td>${{d.words}}</td>
          <td>${{d.ot_op_count}} (${{d.ot_op_pct.toFixed(1)}}%)</td>
          <td>${{d.ok_of_count}} (${{d.ok_of_pct.toFixed(1)}}%)</td>
          <td><strong>${{d.ratio_ot_to_ok.toFixed(2)}}</strong></td>
          <td>${{d.ch_sh_count}} (${{d.ch_sh_pct.toFixed(1)}}%)</td>
        </tr>
      `;
    }}).join("");
  }}

  const morphBody = document.querySelector("#wave48StarMorphTable tbody");
  if (morphBody && DATA.wave48_star_morphology) {{
    const morphs = [
      {{ key: "7_points", label: "7-Point Stars", data: DATA.wave48_star_morphology["7_points"] }},
      {{ key: "8_points", label: "8-Point Stars", data: DATA.wave48_star_morphology["8_points"] }},
      {{ key: "9_points", label: "9-Point Stars", data: DATA.wave48_star_morphology["9_points"] }}
    ];
    morphBody.innerHTML = morphs.filter(m => m.data).map(m => `
      <tr>
        <td><strong>${{m.label}}</strong></td>
        <td><strong>${{m.data.total_units}}</strong> units</td>
        <td>${{m.data.mean_word_count.toFixed(1)}} words</td>
        <td><strong>${{m.data.pf_gallows_count}}</strong> (${{m.data.pf_gallows_pct.toFixed(1)}}%)</td>
        <td>${{m.data.tk_gallows_count}} (${{m.data.tk_gallows_pct.toFixed(1)}}%)</td>
        <td><span class="badge" style="background:var(--accent-soft);color:var(--accent)">${{m.data.ratio_pf_to_tk.toFixed(2)}}×</span></td>
        <td>${{m.data.ds_particle_count}} particles | ${{m.data.qo_verb_count}} qo-verbs</td>
      </tr>
    `).join("");
  }}

  const pBody = document.querySelector("#wave48StarParityTable tbody");
  if (pBody) {{
    pBody.innerHTML = (DATA.wave48_star_parity || []).map(p => {{
      const strictBadge = p.is_100pct_strict
        ? `<span class="badge" style="background:var(--green-soft);color:var(--green)">100.0% Strict</span>`
        : `<span class="badge">${{p.alternation_pct.toFixed(1)}}%</span>`;
      return `
        <tr>
          <td><strong><code>${{p.folio}}</code></strong></td>
          <td>${{p.star_count}} stars</td>
          <td>${{p.transitions}}</td>
          <td><strong>${{p.alternations}}</strong></td>
          <td>${{strictBadge}}</td>
          <td><code>${{p.sequence_preview || ''}}</code></td>
        </tr>
      `;
    }}).join("");
  }}
}}

function renderWave49Tab() {{
  const bBody = document.querySelector("#wave49BarrelTable tbody");
  if (bBody) {{
    bBody.innerHTML = (DATA.wave49_barrel_census || []).map(r => {{
      const isHinge = r.folio === "f72r1";
      const hl = isHinge ? 'style="background:var(--gold-soft);font-weight:700;"' : '';
      const arch = ["f70v1", "f71r", "f71v", "f72r1"].includes(r.folio)
        ? (isHinge ? "10 Inner (5 Barreled) + 5 Outer Top Arc (0% Barreled = HINGE!)" : "10 Inner Full-Circle + 5 Outer Top Arc = 15°")
        : "30° Full-Sign Medallion";
      return `
        <tr ${{hl}}>
          <td><strong><code>${{r.folio}}</code></strong></td>
          <td><strong>${{r.sign}}</strong></td>
          <td>${{r.inner_band}}</td>
          <td>${{r.outer_band}}</td>
          <td colspan="2"><span class="badge" style="background:var(--blue-soft);color:var(--blue)">${{r.total_barreled}}</span></td>
          <td>${{arch}}</td>
        </tr>
      `;
    }}).join("");
  }}

  const cBody = document.querySelector("#wave49BalneoCalloutsTable tbody");
  if (cBody) {{
    cBody.innerHTML = (DATA.wave49_balneo_callouts || []).map(l => {{
      const words = (l.text || "").split(".").filter(Boolean);
      const chips = words.map(w => `<span class="word-chip" onclick="setWord('${{w}}')"><strong>${{w}}</strong></span>`).join(" ");
      const b1 = l.in_same_folio_stem ? `<span class="badge" style="background:var(--green-soft);color:var(--green)">Yes (Same Folio)</span>` : `—`;
      const b2 = l.in_balneo_prose_stem ? `<span class="badge" style="background:var(--blue-soft);color:var(--blue)">Yes (In Balneo)</span>` : `—`;
      const b3 = l.in_same_folio_exact ? `<span class="badge" style="background:var(--gold-soft);color:var(--gold)">Exact Match</span>` : `Stem Match`;
      return `
        <tr>
          <td><strong><code>${{l.locus}}</code></strong></td>
          <td><code>${{l.ltype}}</code></td>
          <td>${{chips}}</td>
          <td><code>${{(l.stems || []).join(", ")}}</code></td>
          <td>${{b1}}</td>
          <td>${{b2}}</td>
          <td>${{b3}}</td>
        </tr>
      `;
    }}).join("");
  }}

  const pBody = document.querySelector("#wave49PharmaTable tbody");
  if (pBody) {{
    pBody.innerHTML = (DATA.wave49_pharma_folios || []).map(f => {{
      const hl = (f.folio === "f100v" || f.folio === "f101r" || f.folio === "f89r1") ? 'style="background:var(--gold-soft);"' : '';
      return `
        <tr ${{hl}}>
          <td><strong><code>${{f.folio}}</code></strong></td>
          <td>${{f.total_label_words}} words (${{f.lc_loci}} <code>@Lc</code> / ${{f.lf_loci}} <code>@Lf</code>)</td>
          <td>${{f.prose_lines}}L (<strong>${{f.mean_words_per_line}}</strong> w/L)</td>
          <td><strong>${{((f.herbal_stem_rate || 0) * 100).toFixed(1)}}%</strong> Herbal</td>
          <td>${{((f.same_folio_stem_rate || 0) * 100).toFixed(1)}}%</td>
          <td><strong>${{((f.pharma_prose_stem_rate || 0) * 100).toFixed(1)}}%</strong></td>
          <td><span class="badge" style="background:var(--green-soft);color:var(--green)">${{((f.three_stage_supply_chain_rate || 0) * 100).toFixed(1)}}%</span></td>
        </tr>
      `;
    }}).join("");
  }}

  const hBody = document.querySelector("#wave49CurrierBHerbalTable tbody");
  if (hBody) {{
    hBody.innerHTML = (DATA.wave49_currier_b_herbal || []).slice(0, 16).map(h => {{
      const hl = (h.folio === "f34r" || h.folio === "f39r") ? 'style="background:var(--gold-soft);"' : '';
      return `
        <tr ${{hl}}>
          <td><strong><code>${{h.folio}}</code></strong> (Quire ${{h.quire}})</td>
          <td>Scribe ${{h.hand}}</td>
          <td>${{h.words}} words (${{h.drawing_intrusions}} <code>&lt;-&gt;</code>)</td>
          <td>${{((h.qo_rate || 0) * 100).toFixed(1)}}%</td>
          <td><strong>${{((h.edy_eey_rate || 0) * 100).toFixed(1)}}%</strong></td>
          <td><span class="badge" style="background:var(--blue-soft);color:var(--blue)">${{((h.balneo_stem_rate || 0) * 100).toFixed(1)}}%</span></td>
          <td><span class="badge" style="background:var(--green-soft);color:var(--green)">${{((h.quire20_stem_rate || 0) * 100).toFixed(1)}}%</span></td>
        </tr>
      `;
    }}).join("");
  }}
}}

function renderWave50Tab() {{
  const s5Body = document.querySelector("#wave50Scribe5Table tbody");
  if (s5Body) {{
    s5Body.innerHTML = (DATA.wave50_scribe5_folios || []).map(f => {{
      const hl = f.folio === "f41v" ? 'style="background:var(--gold-soft);"' : '';
      const lpChips = (f.lp_words || []).length
        ? f.lp_words.map(w => `<span class="word-chip" onclick="setWord('${{w}}')"><strong>${{w}}</strong></span>`).join(" ")
        : "—";
      const stems = (f.top_stems || []).map(s => `<code>${{s[0]}}</code> (${{s[1]}})`).join(", ");
      return `
        <tr ${{hl}}>
          <td><strong><code>${{f.folio}}</code></strong> (Quire ${{f.quire}})</td>
          <td><span class="badge">${{f.section}} / Currier ${{f.language}}</span></td>
          <td><strong>${{f.word_count}}</strong> (${{f.body_words}} body / ${{f.label_words}} labels, ${{f.intrusions}} <code>&lt;-&gt;</code>)</td>
          <td>${{lpChips}}</td>
          <td><strong>${{f.edy_eey_pct}}%</strong></td>
          <td>${{f.q_initial_pct}}%</td>
          <td>${{stems}}</td>
        </tr>
      `;
    }}).join("");
  }}

  const c84Body = document.querySelector("#wave50F84vCalloutsTable tbody");
  if (c84Body) {{
    c84Body.innerHTML = (DATA.wave50_f84v_callouts || []).map(c => {{
      const exBadge = c.exact_in_f84v_body
        ? `<span class="badge" style="background:var(--gold-soft);color:var(--gold)">Exact Match</span>`
        : "—";
      const stBadge = c.stem_in_f84v_body
        ? `<span class="badge" style="background:var(--green-soft);color:var(--green)">Yes (Local Prose)</span>`
        : "—";
      const balBadge = c.stem_in_balneo_section
        ? `<span class="badge" style="background:var(--blue-soft);color:var(--blue)">Yes (Quire 13)</span>`
        : "—";
      const cogChips = (c.f84v_body_cognates || []).slice(0, 6).map(w =>
        `<span class="word-chip" onclick="setWord('${{w}}')">${{w}}</span>`
      ).join(" ");
      return `
        <tr>
          <td><span class="word-chip" onclick="setWord('${{c.token}}')"><strong>${{c.token}}</strong></span></td>
          <td><code>${{c.zone}}</code></td>
          <td><code>${{c.canonical_stem}}</code></td>
          <td>${{exBadge}}</td>
          <td>${{stBadge}}</td>
          <td>${{balBadge}}</td>
          <td>${{cogChips || "—"}}</td>
        </tr>
      `;
    }}).join("");
  }}

  const miBody = document.querySelector("#wave50MultiIntrusionsTable tbody");
  if (miBody) {{
    miBody.innerHTML = (DATA.wave50_multi_intrusions || []).map(m => {{
      const intChips = (m.interior_tokens || []).map(w =>
        `<span class="word-chip" onclick="setWord('${{w}}')"><strong>${{w}}</strong></span>`
      ).join(" ");
      const segsHtml = (m.segments || []).map(seg =>
        seg.map(w => `<span class="word-chip" onclick="setWord('${{w}}')">${{w}}</span>`).join(" ")
      ).join(' <strong style="color:var(--accent)">&lt;-&gt;</strong> ');
      return `
        <tr>
          <td><strong><code>${{m.folio}}.${{m.lnum}}</code></strong></td>
          <td><span class="badge">${{m.intrusion_count}} <code>&lt;-&gt;</code></span></td>
          <td>${{m.segment_count}} segments</td>
          <td>${{intChips}}</td>
          <td>${{segsHtml}}</td>
        </tr>
      `;
    }}).join("");
  }}

  const r113Body = document.querySelector("#wave50F113vRecipesTable tbody");
  if (r113Body) {{
    r113Body.innerHTML = (DATA.wave50_f113v_recipes || []).map(r => {{
      const isPol = (r.opener || "").startsWith("pol") || (r.opener || "").startsWith("por");
      const hl = isPol ? 'style="background:var(--gold-soft);"' : '';
      return `
        <tr ${{hl}}>
          <td><strong>Recipe #${{r.recipe_num}}</strong></td>
          <td><code>f113v.${{r.start_line}}</code></td>
          <td>${{r.word_count}} words</td>
          <td><span class="word-chip" onclick="setWord('${{r.opener}}')"><strong>${{r.opener}}</strong></span></td>
          <td><code>${{r.opener_stem}}</code></td>
          <td><span class="word-chip" onclick="setWord('${{r.closer}}')">${{r.closer}}</span></td>
        </tr>
      `;
    }}).join("");
  }}
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
renderMilestone200Tab();
renderWave44Tab();
renderWave45Tab();
renderWave46Tab();
renderWave47Tab();
renderWave48Tab();
renderWave49Tab();
renderWave50Tab();
</script>
</body>
</html>
"""
    OUT_HTML.write_text(html, encoding="utf-8")
    print(f"Wrote interactive local explorer to {OUT_HTML} ({len(html):,} bytes)")


if __name__ == "__main__":
    main()
