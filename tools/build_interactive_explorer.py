#!/usr/bin/env python3
"""
tools/build_interactive_explorer.py

Builds `explorer/index.html` — a self-contained, zero-server interactive local HTML
explorer for the Voynich Manuscript research repository.

Includes 4 synchronized interactive views:
  1. Page-by-Page Visual Reader (16 iconic folios with high-res scans & clickable clauses)
  2. Botanical, Astrological & Balneological Identifications (15 flagship specimens `SPEC-01..15`)
  3. Core Root Dictionary & 8-Case Inflectional Grammar Matrix
  4. Zodiac Month Calendar (`mars..decembre`) & 20-Page Bathing Plumbing Tracker (`Wave 36`)
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
                "eva": "otaly okaly otaram otaral okal ar al",
                "english": "[Month of March (`mars` — Pisces)]: Prepare the liquid essence (`otaly`), core star-essence (`okaly`), completed root balm (`otaram`), and root-star extract (`otaral`)."
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
    }
]


LEXICON_STEMS = [
    {"stem": "ke / kee", "category": "Thermal Action Verb", "meaning": "Boil / Decoct / Simmer with heat", "examples": "qokeedy, qokedy, okeedy, qokain", "sections": "Balneological (B) & Starred Recipes (S)", "grounding": "Paired with fire/furnace boiling cycles and hot bath conduits (`f75r–f84v`, `f103r–f116r`)."},
    {"stem": "ch", "category": "Processing Verb / Noun", "meaning": "Infuse / Steep / Strained Herbal Liquid (`chol`)", "examples": "chedy, chol, chody, qokchedy, olchedy", "sections": "Universal across all sections (A & B)", "grounding": "Core herbal steeping stem; `chol` is the #1 botanical liquid noun in Herbal A."},
    {"stem": "sh", "category": "Hydrotherapy / Washing Verb", "meaning": "Wash / Bathe / Surface-Steep (`shedy` / `shol`)", "examples": "shedy, shol, shody, qokshedy, sheey", "sections": "Peak concentration in Balneological Baths (`f75r–f84v`)", "grounding": "Directly captions nymphs immersed in water pools and shower conduits (`f75r`, `f76r`, `f78r`)."},
    {"stem": "kar / kor", "category": "Botanical Organ Noun", "meaning": "Heart / Core / Root-Bulb", "examples": "okar, kor, qokar, okary, kykar", "sections": "Herbal, Pharmaceutical Jars, Recipes", "grounding": "Written directly on bulbous roots (`f89r2` `okar`) and Heartsease (`f9v`)."},
    {"stem": "tar", "category": "Botanical / Elemental Noun", "meaning": "Earth / Ground / Primary Root Base", "examples": "otar, tar, otary, otaram, otaral", "sections": "Herbal, Zodiac Rings, Pharma roots", "grounding": "Labels both Zodiac degrees (`f70v2`, `f72r3`) and basal root crowns (`f89r2`)."},
    {"stem": "ra / rar", "category": "Botanical Organ Noun", "meaning": "Main Root / Taproot / Rhizome", "examples": "darary, orar, orary, dara, ydaraishy", "sections": "Pharmaceutical Root Rows & Herbal Monographs", "grounding": "Directly labels cut taproots on `f89r2` (`darary`) and `f99r` (`orary`)."},
    {"stem": "oror", "category": "Specific Plant Crib", "meaning": "Dyer's Alkanet / Madder (Blood-Red Root)", "examples": "oror, orar, okor", "sections": "Pharma `f102v2` & Bilingual Final Page `f116v`", "grounding": "Matches both the crimson root painting on `f102v2` and `...so nim gas mich oror` + red paint blot on `f116v`."},
    {"stem": "doaro", "category": "Astronomical Star Crib", "meaning": "The Pleiades (Seven Sisters Star Cluster)", "examples": "doaro, doar, odoar", "sections": "Astronomical `f68r3`", "grounding": "Written directly below the 7-star cluster in the upper-left quadrant of `f68r3`."},
    {"stem": "al / kal / sal", "category": "Botanical / Celestial Noun", "meaning": "Star / Winged Seed / Volatile Essence", "examples": "okal, osal, okalar, otaly, odal", "sections": "Astronomical Stars, Zodiac Rings, Pharma Seeds", "grounding": "Labels individual stars/nymphs on `f67r–f73v` and cut seed/leaf tops (`osal`) on `f89r2`."},
    {"stem": "ol / kol / tol", "category": "Vessel / Pipe / Liquid Medium", "meaning": "Apothecary Jar / Water Pipe / Bath Basin", "examples": "ol, otol, okol, olkol, okoldy, poldchody", "sections": "Pharmaceutical Jars & Balneological Pipes", "grounding": "Written directly on painted apothecary jars (`okol`) and bath pipes (`olkol`, `okoldy` on `f82v`)."},
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

    embedded_json = json.dumps({
        "folios": WALKTHROUGH_FOLIOS,
        "specimens": specimens_data,
        "lexicon": LEXICON_STEMS,
        "paradigms": paradigm_matrix,
        "zodiac": zodiac_data["medallions"],
        "balneo": balneo_data["folios"],
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
      max-width: 1400px;
      margin: 0 auto;
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      justify-content: space-between;
      gap: 1rem;
    }}

    .brand h1 {{
      margin: 0;
      font-size: 1.35rem;
      letter-spacing: -0.01em;
    }}

    .brand p {{
      margin: 0.2rem 0 0;
      font-size: 0.9rem;
      color: var(--muted);
    }}

    .nav-tabs {{
      display: flex;
      flex-wrap: wrap;
      gap: 0.5rem;
    }}

    .tab-btn {{
      background: var(--surface-alt);
      color: var(--text);
      border: 1px solid var(--border);
      padding: 0.55rem 1rem;
      border-radius: 999px;
      font-weight: 600;
      font-size: 0.86rem;
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
      max-width: 1400px;
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
      padding: 0.75rem 0.9rem;
      border-bottom: 1px solid var(--border);
      text-align: left;
      font-size: 0.9rem;
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
      <button class="tab-btn active" onclick="switchTab('walkthrough', this)">1. Page-by-Page Reader (16)</button>
      <button class="tab-btn" onclick="switchTab('specimens', this)">2. Botanical, Star &amp; Bath Cribs (15)</button>
      <button class="tab-btn" onclick="switchTab('lexicon', this)">3. Core Dictionary &amp; 8-Case Grammar</button>
      <button class="tab-btn" onclick="switchTab('zodiac', this)">4. Zodiac Months &amp; Bath Plumbing</button>
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
      <input id="wordInput" class="decoder-input" type="text" value="qokeedy" placeholder="Type EVA word, e.g. qokeedy, okar, darary, oror, doaro, olkol, daiin..." oninput="analyzeWord(this.value)" />
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
        <span class="word-chip" onclick="setWord('otaly')">otaly</span>
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
      <h2 style="margin: 0 0 0.25rem;">15 Flagship Botanical, Astronomical, Balneological &amp; Apothecary Identifications</h2>
      <p style="margin: 0; color: var(--muted);">
        Matching the manuscript's high-resolution drawings to concrete 15th-century European herbal species, star clusters, bilingual month wheels, and labelled hydrotherapy pipes.
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
  "oror": "Blood-red Alkanet / Madder dye-root (Alkanna tinctoria)",
  "orar": "Red Alkanet root-extract",
  "doaro": "The Pleiades (7-star cluster in Taurus, f68r3)",
  "darary": "The main taproot / rhizome (labeled on f89r2)",
  "olkol": "The core water-pipe / bath conduit liquid (labeled on f82v)",
  "okoldy": "Infused in the storage jar / water conduit (labeled on f82v & f89r2)",
  "poldchody": "Begin by steeping in the liquid vessel (Red-Blossom headword on f11v & f116v)",
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
      stem: "oror", stemDesc: "Blood-red Dyer's Alkanet / Madder root (f102v2 & f116v)",
      suffix: "-or (Reduplicated)", suffixDesc: "Red/golden dye-root stem (`or-or`)",
      gloss: "Blood-red Alkanet / Madder root (`Alkanna tinctoria` — Rosetta crib on f102v2 & f116v)"
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
</script>
</body>
</html>
"""
    OUT_HTML.write_text(html, encoding="utf-8")
    print(f"Wrote interactive local explorer to {OUT_HTML} ({len(html):,} bytes)")


if __name__ == "__main__":
    main()
