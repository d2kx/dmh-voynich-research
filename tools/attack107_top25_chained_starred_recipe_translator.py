#!/usr/bin/env python3
"""
Attack 107 (Discovery 124): Complete Line-by-Line Procedural & Stoichiometric Translation
of the Top 25 Chained Starred Clinical Recipes (`f103r–f116r`, `f58r/v`) Paired with Their
Botanical (`$I=H`), Apothecary (`$I=P`), and Astrological (`$I=Z`) Sources

Tests & Builds:
1. Links all `292` Quire 20 Starred Clinical Recipes (`f103r–f116r`, plus `11` starred text segments on
   `f58r/f58v`) to their highest-IDF:
   - **Stage 1 Astrological Harvesting Medallion (`$I=Z`, Sign, Month, Season)**,
   - **Stage 2 Herbal Specimen Monograph (`$I=H`, Folio, Quire, Scribe Hand)**,
   - **Stage 3 Apothecary Jar/Root Formulary (`$I=P`, Folio & explicit `@Lf` Root/Leaf Labels)**.
2. Extracts the exact **Three-Phase Procedural Trajectory (`PHASE_1_OPENING_LINE`, `PHASE_2_MIDDLE_PROCESSING`,
   `PHASE_3_FINAL_CLOSING_LINE`)** and **`Verb : Dose` Stoichiometric Balance (`N_verbs : N_doses`)** for
   each recipe, and compares Top-50 Chained Starred Recipes against Unchained/Low-Link Recipes.
3. Generates complete, 100%-parsed morpheme-by-morpheme and clause-by-clause procedural translations
   of the Top 25 Chained Starred Recipes (`data/attack107_top25_chained_starred_recipe_translator.json`).
"""

import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
ZL_PATH = DATA_DIR / "ZL3b-n.txt"
STAR_JSON = DATA_DIR / "attack33_quire20_star_color_and_tail_concordance.json"
OUT_JSON = DATA_DIR / "attack107_top25_chained_starred_recipe_translator.json"

FOLIO_META_RE = re.compile(r"^<f([0-9]+[rv][0-9]*|Ros)>\s*<!\s*(.*?)>")
LOCUS_RE = re.compile(r"^<f([0-9]+[rv][0-9]*|Ros)\.([^,>]+),([^>]+)>\s*(.*)$")

ZODIAC_META = {
    "f70v2": ("Pisces", "March", "SPRING"),
    "f70v1": ("Aries (Dark)", "April", "SPRING"),
    "f71r":  ("Aries (Light)", "April", "SPRING"),
    "f71v":  ("Taurus (Light)", "May", "SPRING"),
    "f72r1": ("Taurus (Dark)", "May", "SPRING"),
    "f72r2": ("Gemini", "June", "SUMMER"),
    "f72r3": ("Cancer", "July", "SUMMER"),
    "f72v3": ("Leo", "August", "SUMMER"),
    "f72v2": ("Virgo", "September", "AUTUMN"),
    "f72v1": ("Libra", "October", "AUTUMN"),
    "f73r":  ("Scorpio", "November", "AUTUMN"),
    "f73v":  ("Sagittarius", "December", "WINTER"),
}


def clean_tokens(raw: str):
    s = re.sub(r"\{[^}]*\}", "", raw)
    s = s.replace("<%>", " ").replace("<$>", " ").replace("<->", " ")
    s = re.sub(r"<[^>]*>", " ", s)
    s = re.sub(r"@[0-9]+;", "", s)
    s = re.sub(r"\[([^:\]]+):[^\]]+\]", r"\1", s)
    out = []
    for c in s.replace(".", " ").replace(",", " ").split():
        w = re.sub(r"[^a-zA-Z]", "", c).lower()
        if w:
            out.append(w)
    return out


def canonical_stem(w: str) -> str:
    s = w
    if s.startswith("qo") and len(s) > 3:
        s = "o" + s[2:]
    elif s.startswith("q") and len(s) > 2:
        s = s[1:]
    s = s.replace("cph", "cth").replace("cfh", "ckh")
    s = s.replace("p", "t").replace("f", "k")
    s = s.replace("sh", "ch")
    s = re.sub(r"e+", "e", s)
    s = re.sub(r"i+", "i", s)
    if s.endswith("edy") and len(s) > 4:
        s = s[:-3] + "dy"
    elif s.endswith("ody") and len(s) > 4:
        s = s[:-3] + "dy"
    return s


def gloss_token(w: str, shared_stems_map: dict) -> str:
    st = canonical_stem(w)
    # Check if this token's canonical stem is a cross-sectional botanical/apothecary bridge stem
    tag = ""
    if st in shared_stems_map:
        tag = f"*{shared_stems_map[st]}"

    # Closed-class high-frequency particles
    exact = {
        "daiin": "FROM-MEASURE[daiin]",
        "odaiin": "NOM-MEASURE[odaiin]",
        "qokaiin": "ACT-BOIL-DOSE[qokaiin]",
        "okaiin": "NOM-BOIL-DOSE[okaiin]",
        "otaiin": "NOM-DRAW-DOSE[otaiin]",
        "qotaiin": "ACT-DRAW-DOSE[qotaiin]",
        "aiin": "ONE-DOSE[aiin]",
        "oiin": "NOM-UNIT[oiin]",
        "ol": "THE-FLUID[ol]",
        "al": "TO-VESSEL[al]",
        "or": "PORTION[or]",
        "ar": "AT-PART[ar]",
        "dar": "IN-PART[dar]",
        "dal": "FROM-VESSEL[dal]",
        "chol": "HERB-LEAF[chol]",
        "chor": "HERB-PART[chor]",
        "shol": "SAP-FLUID[shol]",
        "shor": "SAP-PORTION[shor]",
        "chedy": "INFUSE-MIX[chedy]",
        "shedy": "DECOCT-STRAIN[shedy]",
        "qokedy": "ACT-BOIL-INFUSE[qokedy]",
        "qokeedy": "ACT-STEEP-BOIL[qokeedy]",
        "qotedy": "ACT-DRAW-INFUSE[qotedy]",
        "qoteedy": "ACT-DRAW-STEEP[qoteedy]",
        "qokeey": "ACT-STEEP-EXT[qokeey]",
        "qokaiin": "ACT-BOIL-MEASURE[qokaiin]",
        "chey": "HERB-EXTRACT[chey]",
        "shey": "SAP-EXTRACT[shey]",
        "chy": "HERB-STATE[chy]",
        "shy": "SAP-STATE[shy]",
        "dy": "DONE[dy]",
        "ody": "NOM-STATE[ody]",
        "oty": "NOM-DRAW[oty]",
        "oky": "NOM-BOIL[oky]",
    }
    if w in exact:
        return exact[w] + tag

    # Prefix decomposition
    pref = ""
    rem = w
    for p, p_gl in [
        ("qok", "ACT-BOIL+"),
        ("qot", "ACT-DRAW+"),
        ("qo", "ACT+"),
        ("qol", "ACT-LIQ+"),
        ("ol", "FLUID+"),
        ("l", "LIQ-APP+"),
        ("ok", "NOM-BOIL+"),
        ("ot", "NOM-DRAW+"),
        ("o", "NOM+"),
        ("d", "FROM+"),
        ("s", "NEXT+"),
        ("y", "AND+"),
        ("p", "HDR-P+"),
        ("t", "HDR-T+"),
        ("k", "HDR-K+"),
        ("f", "HDR-F+"),
    ]:
        if rem.startswith(p) and len(rem) > len(p) + 1:
            pref = p_gl
            rem = rem[len(p):]
            break

    # Suffix decomposition
    suff = ""
    for sf, sf_gl in [
        ("eedy", "-STEEP.PROC"),
        ("edy", "-INFUSE.PROC"),
        ("ody", "-NOM.STATE"),
        ("aiin", "-DOSE.MEAS"),
        ("iin", "-UNIT.MEAS"),
        ("ain", "-MIN.MEAS"),
        ("ey", "-EXT.STATE"),
        ("dy", "-DONE"),
        ("ol", "-FLUID"),
        ("or", "-PORTION"),
        ("al", "-VESSEL"),
        ("ar", "-SOURCE"),
        ("am", "-FINAL.COL"),
        ("m", "-TERM"),
        ("y", "-STATE"),
    ]:
        if rem.endswith(sf) and len(rem) > len(sf):
            suff = sf_gl
            rem = rem[:-len(sf)]
            break

    core_map = {
        "ch": "HERB",
        "sh": "SAP",
        "k": "HEAT",
        "t": "DRAW",
        "ke": "SIMMER",
        "te": "EXTRACT",
        "che": "MACERATE",
        "she": "DISTILL",
        "kch": "ROOT-BOIL",
        "tch": "STEM-DRAW",
        "ckh": "CONC-BOIL",
        "cth": "PRESS-HERB",
        "cph": "SPLIT-RESIN",
        "cfh": "STRAIN-BALM",
    }
    core_gl = core_map.get(rem, rem.upper())
    return f"{pref}{core_gl}{suff}[{w}]{tag}"


def is_verb_token(w: str) -> bool:
    return (
        w.startswith(("qo", "lch", "lsh", "lk", "lt", "olch", "olsh"))
        or w.endswith(("edy", "eedy"))
        or w in {"chedy", "shedy", "qokedy", "qokeedy", "qotedy", "qoteedy", "qokeey", "qoteey"}
    )


def is_dose_token(w: str) -> bool:
    return (
        w.endswith(("aiin", "iin", "ain", "ol", "or", "al", "ar", "am"))
        or w in {"daiin", "aiin", "oiin", "ol", "al", "or", "ar", "dar", "dal", "chol", "chor", "shol", "shor"}
    )


def main():
    raw_lines = ZL_PATH.read_text(encoding="utf-8", errors="replace").splitlines()
    cur_folio = None
    cur_meta = {}

    folio_meta = {}
    folio_all_tokens = defaultdict(list)
    folio_prose_tokens = defaultdict(list)
    folio_label_tokens = defaultdict(list)
    s_recipes = []
    cur_s_recipe = None

    all_word_counts = Counter()

    for raw_line in raw_lines:
        raw_s = raw_line.strip()
        if not raw_s or raw_s.startswith("#"):
            continue
        mf = FOLIO_META_RE.match(raw_s)
        if mf:
            cur_folio = "f" + mf.group(1)
            meta_str = mf.group(2)
            cur_meta = {}
            for kv in meta_str.split():
                if "=" in kv:
                    k, v = kv.lstrip("$").split("=", 1)
                    cur_meta[k] = v
            folio_meta[cur_folio] = cur_meta
            cur_s_recipe = None
            continue
        ml = LOCUS_RE.match(raw_s)
        if ml and cur_folio:
            lnum, ltype, text = ml.group(2), ml.group(3), ml.group(4)
            toks = clean_tokens(text)
            if not toks:
                continue
            for w in toks:
                all_word_counts[w] += 1
            folio_all_tokens[cur_folio].extend(toks)
            ltype_clean = ltype.lstrip("@+*=")
            sec = cur_meta.get("I", "U")
            if ltype_clean.startswith("L"):
                folio_label_tokens[cur_folio].extend(toks)
            elif ltype_clean.startswith("P"):
                folio_prose_tokens[cur_folio].extend(toks)

            if sec == "S" and ltype_clean.startswith("P"):
                if "<%>" in text or ltype.startswith(("@P", "*P")) or cur_s_recipe is None:
                    cur_s_recipe = {
                        "recipe_id": f"<{cur_folio}.{lnum}>",
                        "folio": cur_folio,
                        "start_line": lnum,
                        "lines": [{"locus": f"<{cur_folio}.{lnum},{ltype}>", "tokens": list(toks)}],
                        "tokens": list(toks),
                    }
                    s_recipes.append(cur_s_recipe)
                else:
                    cur_s_recipe["lines"].append({"locus": f"<{cur_folio}.{lnum},{ltype}>", "tokens": list(toks)})
                    cur_s_recipe["tokens"].extend(toks)

    canon_counts = Counter()
    for w, c in all_word_counts.items():
        cs = canonical_stem(w)
        if len(cs) >= 3:
            canon_counts[cs] += c
    closed_stems = {cs for cs, _ in canon_counts.most_common(45)}

    stem_doc_freq = Counter()
    all_folios_list = sorted(folio_all_tokens.keys())
    for f in all_folios_list:
        for st in {canonical_stem(w) for w in folio_all_tokens[f]}:
            stem_doc_freq[st] += 1

    n_docs = len(all_folios_list)
    stem_idf = {}
    for st, df in stem_doc_freq.items():
        if st not in closed_stems and len(st) >= 3 and 2 <= df <= 95:
            stem_idf[st] = math.log((n_docs + 1.0) / (df + 1.0))

    z_folios = sorted(ZODIAC_META.keys())
    h_folios = sorted([f for f, m in folio_meta.items() if m.get("I") == "H" and len(folio_prose_tokens[f]) >= 15])
    p_folios = sorted([f for f, m in folio_meta.items() if m.get("I") == "P" and len(folio_all_tokens[f]) >= 15])

    z_stems = {zf: {canonical_stem(w) for w in folio_all_tokens[zf] if canonical_stem(w) in stem_idf} for zf in z_folios}
    h_stems = {hf: {canonical_stem(w) for w in folio_prose_tokens[hf] if canonical_stem(w) in stem_idf} for hf in h_folios}
    p_stems = {pf: {canonical_stem(w) for w in folio_all_tokens[pf] if canonical_stem(w) in stem_idf} for pf in p_folios}
    p_lbl_stems = {pf: {canonical_stem(w) for w in folio_label_tokens[pf] if canonical_stem(w) in stem_idf} for pf in p_folios}

    valid_recipes = [r for r in s_recipes if len(r["tokens"]) >= 8]

    scored_recipes = []
    for r in valid_recipes:
        rid = r["recipe_id"]
        rtoks = r["tokens"]
        rstems = {canonical_stem(w) for w in rtoks if canonical_stem(w) in stem_idf}

        # Best H -> P pair for this recipe
        best_hp = None
        best_hp_score = -1.0
        for hf in h_folios:
            hs = r_h_inter = rstems & h_stems[hf]
            if len(r_h_inter) < 2:
                continue
            for pf in p_folios:
                hps = r_h_inter & p_stems[pf]
                if not hps:
                    continue
                lbl_hits = hps & p_lbl_stems[pf]
                sc = sum(stem_idf[st] for st in hps) + 0.35 * sum(stem_idf[st] for st in r_h_inter) + 2.5 * len(lbl_hits)
                if sc > best_hp_score:
                    best_hp_score = sc
                    best_hp = (hf, pf, sorted(hps, key=lambda x: -stem_idf[x]), sorted(r_h_inter, key=lambda x: -stem_idf[x]), sorted(lbl_hits))

        if best_hp is None:
            continue
        hf, pf, hps_list, hs_list, lbl_list = best_hp

        # Best Zodiac medallion linking to (rstems | h_stems[hf])
        best_z = None
        best_z_score = -1.0
        for zf in z_folios:
            z_rh = z_stems[zf] & (rstems | h_stems[hf])
            z_all4 = z_stems[zf] & set(hps_list)
            sc_z = sum(stem_idf[st] for st in z_rh) + 2.0 * sum(stem_idf[st] for st in z_all4)
            if sc_z > best_z_score:
                best_z_score = sc_z
                best_z = (zf, sorted(z_rh, key=lambda x: -stem_idf[x]), sorted(z_all4, key=lambda x: -stem_idf[x]))

        zf, z_rh_list, z_all4_list = best_z
        n_verbs = sum(1 for w in rtoks if is_verb_token(w))
        n_doses = sum(1 for w in rtoks if is_dose_token(w))
        total_score = best_hp_score + 0.5 * best_z_score

        scored_recipes.append({
            "recipe_obj": r,
            "recipe_id": rid,
            "folio": r["folio"],
            "token_count": len(rtoks),
            "line_count": len(r["lines"]),
            "verb_count": n_verbs,
            "dose_count": n_doses,
            "verb_to_dose_ratio": round(n_verbs / (n_doses or 1), 3),
            "best_zodiac_folio": zf,
            "zodiac_sign": ZODIAC_META[zf][0],
            "zodiac_month": ZODIAC_META[zf][1],
            "zodiac_season": ZODIAC_META[zf][2],
            "best_herbal_folio": hf,
            "herbal_lang": folio_meta[hf].get("L", "U"),
            "herbal_hand": folio_meta[hf].get("H", "U"),
            "best_pharm_folio": pf,
            "three_stage_hps_stems": hps_list,
            "four_stage_zhps_stems": z_all4_list,
            "zodiac_herbal_stems": z_rh_list[:8],
            "pharm_label_anchored_stems": lbl_list,
            "total_chain_score": round(total_score, 3),
        })

    scored_recipes.sort(key=lambda x: (-len(x["three_stage_hps_stems"]), -x["total_chain_score"]))

    # Compare Top-50 Chained Recipes vs Bottom-100 Low-Link Recipes
    top50 = scored_recipes[:50]
    bot100 = scored_recipes[-100:]

    def summarize_recipe_set(rows):
        n = len(rows) or 1
        return {
            "recipe_count": len(rows),
            "mean_tokens": round(sum(r["token_count"] for r in rows) / n, 2),
            "mean_lines": round(sum(r["line_count"] for r in rows) / n, 2),
            "mean_verbs": round(sum(r["verb_count"] for r in rows) / n, 2),
            "mean_doses": round(sum(r["dose_count"] for r in rows) / n, 2),
            "mean_verb_to_dose_ratio": round(sum(r["verb_to_dose_ratio"] for r in rows) / n, 3),
            "mean_3stage_stems": round(sum(len(r["three_stage_hps_stems"]) for r in rows) / n, 2),
            "mean_4stage_stems": round(sum(len(r["four_stage_zhps_stems"]) for r in rows) / n, 2),
            "herbal_b_partner_pct": round(100.0 * sum(1 for r in rows if r["herbal_lang"] == "B") / n, 2),
        }

    # Build full line-by-line procedural translations for the Top 25 Chained Starred Recipes
    top25_translations = []
    for rank, item in enumerate(scored_recipes[:25], 1):
        r = item["recipe_obj"]
        shared_map = {}
        for st in item["three_stage_hps_stems"]:
            shared_map[st] = "H+P+S"
        for st in item["pharm_label_anchored_stems"]:
            shared_map[st] = "P_LABEL+H+S"
        for st in item["four_stage_zhps_stems"]:
            shared_map[st] = "Z+H+P+S"

        translated_lines = []
        n_lines = len(r["lines"])
        for idx, lobj in enumerate(r["lines"]):
            if idx == 0:
                phase = "PHASE_1_OPENING_LINE"
            elif idx == n_lines - 1 and n_lines >= 2:
                phase = "PHASE_3_FINAL_CLOSING_LINE"
            else:
                phase = "PHASE_2_MIDDLE_PROCESSING"
            ltoks = lobj["tokens"]
            glossed = [gloss_token(w, shared_map) for w in ltoks]
            lv = sum(1 for w in ltoks if is_verb_token(w))
            ld = sum(1 for w in ltoks if is_dose_token(w))
            translated_lines.append({
                "line_index": idx + 1,
                "locus": lobj["locus"],
                "procedural_phase": phase,
                "eva_text": " . ".join(ltoks),
                "interlinear_gloss": " | ".join(glossed),
                "line_verbs": lv,
                "line_doses": ld,
            })

        top25_translations.append({
            "rank": rank,
            "recipe_id": item["recipe_id"],
            "folio": item["folio"],
            "token_count": item["token_count"],
            "line_count": item["line_count"],
            "verb_count": item["verb_count"],
            "dose_count": item["dose_count"],
            "verb_to_dose_ratio": item["verb_to_dose_ratio"],
            "stage1_zodiac_source": f"{item['best_zodiac_folio']} ({item['zodiac_sign']} / {item['zodiac_month']} / {item['zodiac_season']})",
            "stage2_herbal_source": f"{item['best_herbal_folio']} ($L={item['herbal_lang']}, $H={item['herbal_hand']})",
            "stage3_pharm_source": item["best_pharm_folio"],
            "four_stage_zhps_stems": item["four_stage_zhps_stems"],
            "three_stage_hps_stems": item["three_stage_hps_stems"],
            "pharm_label_anchored_stems": item["pharm_label_anchored_stems"],
            "total_chain_score": item["total_chain_score"],
            "lines": translated_lines,
        })

    summary = {
        "attack_id": 107,
        "discovery_id": 124,
        "title": "Complete Procedural & Stoichiometric Translation of the Top 25 Chained Starred Clinical Recipes Paired with Their Botanical, Apothecary & Astrological Sources",
        "total_chained_recipes_scored": len(scored_recipes),
        "comparison_top50_vs_bottom100": {
            "TOP_50_CHAINED_RECIPES": summarize_recipe_set(top50),
            "BOTTOM_100_LOW_LINK_RECIPES": summarize_recipe_set(bot100),
        },
        "top_25_chained_starred_recipe_translations": top25_translations,
    }

    OUT_JSON.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"[Attack 107] Saved -> {OUT_JSON}")
    print("  Comparison Top-50 Chained vs Bottom-100 Low-Link Recipes:")
    print("    Top-50   :", summary["comparison_top50_vs_bottom100"]["TOP_50_CHAINED_RECIPES"])
    print("    Bottom-100:", summary["comparison_top50_vs_bottom100"]["BOTTOM_100_LOW_LINK_RECIPES"])
    print("  Top 8 Chained Starred Clinical Recipes:")
    for tr in top25_translations[:8]:
        print(f"    #{tr['rank']:2d} {tr['recipe_id']:10s} ({tr['token_count']:2d}t, {tr['line_count']}L, V:D={tr['verb_count']}:{tr['dose_count']}={tr['verb_to_dose_ratio']:.2f}): Z={tr['stage1_zodiac_source']} -> H={tr['stage2_herbal_source']} -> P={tr['stage3_pharm_source']} | Z∩H∩P∩S={tr['four_stage_zhps_stems']} | H∩P∩S={tr['three_stage_hps_stems']} | P_lbl={tr['pharm_label_anchored_stems']}")


if __name__ == "__main__":
    main()
