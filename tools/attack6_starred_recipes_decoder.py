#!/usr/bin/env python3
"""
Phase 17 / Attack 6: The Starred Recipes (f103r-f116r, Quire 20) &
Painted Marginal Star (*) Astrological-Medical Compendium Decoder.

1. Parses all 285 Starred Recipe paragraphs across the 23 extant pages of Quire 20
   (f103r-f108v, f111r-f116r) from ZL3b-n.txt, capturing the exact paleographic
   star comment (# ... star ...) preceding each paragraph:
   - D  (Dark / Red-filled star)
   - L. (Light / Yellow star with dark ink dot in center/tail)
   - L  (Light / Yellow plain un-dotted star)
   - Plus tailed vs. untailed star morphology.
2. Compares D, L., and L Starred Recipes across paragraph length, opener gallows
   (p/f vs t/k), closer suffixes (-am/-m, -ry/-ly, -y, -in), qo- density, ch/sh
   action-verb density, and section-specific label cross-reference rates (Zodiac,
   Pharmaceutical, Biological, Rosettes, Astronomical).
3. Builds the 23-Page x Section / Zodiac-Sign / Pharma-Folio Cross-Reference Matrix
   for rare labels (global prose count <= 10) and tests whether Scribe Hand 3 vs.
   Scribe Hand 4 or specific recipe folios specialize in specific diagram sections.
4. Identifies the highest-density multi-crib Starred Recipes and generates complete
   word-by-word structural & ingredient/degree decodings for the top 6 recipes.
"""

import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ZL_PATH = ROOT / "data" / "ZL3b-n.txt"
OUT_JSON = ROOT / "data" / "attack6_starred_recipes_decoder.json"


def clean_tok(t: str) -> str:
    t = re.sub(r"\{[^}]*\}", "", t)
    t = re.sub(r"\[([^]:]+):[^\]]+\]", r"\1", t)
    t = re.sub(r"[@&!?\*\(\)<>\[\]\'\"]", "", t)
    return t.strip()


def canonicalize(w: str, is_top_line: bool = False, is_line_end: bool = False) -> str:
    if not w:
        return ""
    s = w
    if len(s) > 2 and s[0] in ("q", "y") and s[1] in ("o", "e", "a"):
        s = s[1:]
    s = s.replace("p", "t").replace("f", "k")
    s = re.sub(r"e+", "e", s)
    s = re.sub(r"i+", "i", s)
    s = re.sub(r"o+", "o", s)
    s = re.sub(r"a+", "a", s)
    if s.endswith("m") and len(s) > 2:
        s = s[:-1] + "r"
    return s


ZODIAC_SIGN_MAP = {
    "f70v2": "Pisces (f70v2)",
    "f70v1": "Aries I (f70v1)",
    "f71r": "Aries II (f71r)",
    "f71v": "Taurus I (f71v)",
    "f72r1": "Taurus II (f72r1)",
    "f72r2": "Gemini (f72r2)",
    "f72r3": "Cancer (f72r3)",
    "f72v3": "Leo (f72v3)",
    "f72v2": "Virgo (f72v2)",
    "f72v1": "Libra (f72v1)",
    "f73r": "Scorpio (f73r)",
    "f73v": "Sagittarius (f73v)",
}


def classify_star_comment(sc: str) -> str:
    if not sc:
        return "Unmarked"
    s = sc.lower()
    if "dark" in s:
        return "D (Dark/Red Star)"
    if "dotted" in s:
        return "L. (Light Dotted Star)"
    if "light" in s:
        return "L (Light Plain Star)"
    return "Other Star"


def short_star_code(sc: str) -> str:
    if not sc:
        return "?"
    s = sc.lower()
    if "dark" in s:
        return "D"
    if "dotted" in s:
        return "L."
    if "light" in s:
        return "L"
    return "*"


def parse_zl_corpus(zl_path: Path):
    text = zl_path.read_text(encoding="utf-8", errors="ignore")
    folios = {}
    current_folio = None
    pending_star_comment = None

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("#"):
            c = line.lstrip("#").strip()
            if "star" in c.lower():
                pending_star_comment = c
            continue

        m_page = re.match(r"^<(f[\w]+)>\s*(?:<!\s*(.*?)\s*>)?", line)
        if m_page and "." not in m_page.group(1):
            current_folio = m_page.group(1)
            meta = {}
            if m_page.group(2):
                for kv in re.findall(r"\$([A-Z])=([A-Za-z0-9]+)", m_page.group(2)):
                    meta[kv[0]] = kv[1]
            folios[current_folio] = {"meta": meta, "lines": []}
            pending_star_comment = None
            continue

        m_loc = re.match(r"^<([^>]+)>\s*(.*)$", line)
        if not m_loc or not current_folio:
            continue
        loc_header = m_loc.group(1)
        body = m_loc.group(2)
        parts = loc_header.split(",")
        loc_id = parts[0]
        unit_type = parts[1] if len(parts) > 1 else ""

        comments = re.findall(r"<!([^>]*)>", body)
        has_par_start = "<%>" in body
        has_par_end = "<$>" in body
        body_no_comments = re.sub(r"<!([^>]*)>", "", body)
        body_no_comments = body_no_comments.replace("<%>", "").replace("<$>", "").replace("<->", " . ")

        raw_toks = [t for t in re.split(r"[\.\s,]+", body_no_comments) if t]
        words = [clean_tok(t) for t in raw_toks]
        words = [w for w in words if w and not w.startswith("@") and not w.startswith("H=")]

        folios[current_folio]["lines"].append(
            {
                "loc": loc_id,
                "unit": unit_type,
                "comments": comments,
                "star_comment": pending_star_comment if has_par_start else None,
                "has_par_start": has_par_start,
                "has_par_end": has_par_end,
                "words": words,
            }
        )
        if has_par_start:
            pending_star_comment = None

    return folios


def tag_word_role(w: str, pos_in_line: int, line_len: int, is_par_start: bool, is_par_end: bool) -> str:
    if is_par_start and pos_in_line == 0:
        return "RECIPE_OPENER"
    if is_par_end and pos_in_line == line_len - 1:
        return "RECIPE_CLOSER"
    if w in ("daiin", "dain"):
        return "CLAUSE_BOUNDARY"
    if w in ("ol", "al", "dal", "dar", "or", "ar"):
        return "PREP/REL"
    if w.startswith(("ch", "sh")) and w.endswith(("edy", "ey", "dy", "y")):
        return "ACTION_VERB"
    if w.startswith("qo"):
        return f"PROCLITIC_OBJ(q+{w[1:]})"
    if w.startswith("y") and len(w) > 2:
        return f"CONJ_INIT(y+{w[1:]})"
    if w.startswith(("o", "d", "s")):
        return "NOMINAL/INGRED"
    return "MOD/OTHER"


def main():
    folios = parse_zl_corpus(ZL_PATH)

    # 1. Build global canonical prose counts and figure label catalog
    prose_canon_counts = Counter()
    labels_by_canon = defaultdict(list)

    for fol, fdata in folios.items():
        sec = fdata["meta"].get("I", "?")
        for l_idx, lobj in enumerate(fdata["lines"]):
            unit = lobj["unit"]
            words = lobj["words"]
            if not words:
                continue
            is_label = "@L" in unit or "&L" in unit
            if is_label:
                w = words[0]
                c = canonicalize(w, is_top_line=False, is_line_end=False)
                labels_by_canon[c].append(
                    {
                        "folio": fol,
                        "section": sec,
                        "loc": lobj["loc"],
                        "unit": unit,
                        "word": w,
                        "canon": c,
                        "comments": lobj["comments"],
                    }
                )
            else:
                is_top = lobj["has_par_start"] or l_idx == 0
                for w_i, w in enumerate(words):
                    c = canonicalize(w, is_top_line=is_top, is_line_end=(w_i == len(words) - 1))
                    prose_canon_counts[c] += 1

    # 2. Extract all Starred Recipe paragraphs across f103r..f116r
    recipe_folios = [
        fol
        for fol in folios.keys()
        if re.match(r"^f1(0[3-8]|1[1-6])[rv]", fol) and fol != "f116v"
    ]

    recipes = []
    global_recipe_idx = 0

    for fol in recipe_folios:
        fdata = folios[fol]
        hand = fdata["meta"].get("H", "?")
        lang = fdata["meta"].get("L", "?")
        cur_par = None
        fol_par_idx = 0

        for lobj in fdata["lines"]:
            unit = lobj["unit"]
            if "@L" in unit or "&L" in unit:
                continue
            words = lobj["words"]
            if not words:
                continue
            if lobj["has_par_start"] or cur_par is None:
                if cur_par is not None:
                    recipes.append(cur_par)
                sc = lobj.get("star_comment") or ""
                global_recipe_idx += 1
                fol_par_idx += 1
                cur_par = {
                    "recipe_id": global_recipe_idx,
                    "folio": fol,
                    "folio_par_index": fol_par_idx,
                    "hand": hand,
                    "lang": lang,
                    "star_comment": sc,
                    "star_code": short_star_code(sc),
                    "star_class": classify_star_comment(sc),
                    "start_loc": lobj["loc"],
                    "end_loc": lobj["loc"],
                    "lines": [],
                    "words": [],
                    "canons": [],
                }

            is_top = lobj["has_par_start"] or len(cur_par["lines"]) == 0
            line_canons = [
                canonicalize(w, is_top_line=is_top, is_line_end=(i == len(words) - 1))
                for i, w in enumerate(words)
            ]
            cur_par["lines"].append(
                {"loc": lobj["loc"], "words": words, "canons": line_canons}
            )
            cur_par["words"].extend(words)
            cur_par["canons"].extend(line_canons)
            cur_par["end_loc"] = lobj["loc"]

            if lobj["has_par_end"]:
                recipes.append(cur_par)
                cur_par = None

        if cur_par is not None:
            recipes.append(cur_par)

    # 3. Analyze Star Classes (D, L., L, Unmarked) AND Scribe Hands (Hand 3 vs Hand 4)
    def init_bucket():
        return {
            "count": 0,
            "total_words": 0,
            "total_lines": 0,
            "gallows_openers": 0,
            "p_openers": 0,
            "t_openers": 0,
            "k_openers": 0,
            "f_openers": 0,
            "closer_am_m": 0,
            "closer_y": 0,
            "closer_in": 0,
            "closer_ry_ly": 0,
            "qo_words": 0,
            "ch_sh_words": 0,
            "rare_label_hits": 0,
            "zodiac_hits": 0,
            "pharma_hits": 0,
            "bio_hits": 0,
            "rosettes_hits": 0,
        }

    star_stats = defaultdict(init_bucket)
    hand_stats = defaultdict(init_bucket)

    folio_to_zodiac = defaultdict(Counter)
    folio_to_pharma = defaultdict(Counter)
    folio_to_section = defaultdict(Counter)
    folio_star_seqs = defaultdict(list)

    for r in recipes:
        sclass = r["star_class"]
        hbucket = f"Hand {r['hand']}"
        folio_star_seqs[r["folio"]].append(r["star_code"])

        for st in (star_stats[sclass], hand_stats[hbucket]):
            st["count"] += 1
            st["total_words"] += len(r["words"])
            st["total_lines"] += len(r["lines"])

            if r["words"]:
                w0 = r["words"][0]
                if any(g in w0[:3] for g in ("p", "f", "t", "k")):
                    st["gallows_openers"] += 1
                if "p" in w0[:3]:
                    st["p_openers"] += 1
                elif "t" in w0[:3]:
                    st["t_openers"] += 1
                elif "k" in w0[:3]:
                    st["k_openers"] += 1
                elif "f" in w0[:3]:
                    st["f_openers"] += 1

                w_end = r["words"][-1]
                if w_end.endswith("m"):
                    st["closer_am_m"] += 1
                if w_end.endswith("ry") or w_end.endswith("ly"):
                    st["closer_ry_ly"] += 1
                elif w_end.endswith("y"):
                    st["closer_y"] += 1
                elif w_end.endswith("in"):
                    st["closer_in"] += 1

            for w in r["words"]:
                if w.startswith("qo"):
                    st["qo_words"] += 1
                if w.startswith("ch") or w.startswith("sh"):
                    st["ch_sh_words"] += 1

        # Match words in this recipe against rare figure labels (prose_count <= 10)
        r_hits = []
        seen_canons = set()
        for line_obj in r["lines"]:
            for w_idx, (w, c) in enumerate(zip(line_obj["words"], line_obj["canons"])):
                if len(c) < 3:
                    continue
                p_cnt = prose_canon_counts[c]
                if p_cnt <= 10 and c in labels_by_canon:
                    lbls = labels_by_canon[c]
                    has_z = any(l["folio"] in ZODIAC_SIGN_MAP for l in lbls)
                    has_p = any(l["section"] == "P" for l in lbls)
                    has_b = any(l["section"] == "B" for l in lbls)
                    has_ros = any(l["folio"] == "fRos" for l in lbls)

                    for st in (star_stats[sclass], hand_stats[hbucket]):
                        st["rare_label_hits"] += 1
                        if has_z:
                            st["zodiac_hits"] += 1
                        if has_p:
                            st["pharma_hits"] += 1
                        if has_b:
                            st["bio_hits"] += 1
                        if has_ros:
                            st["rosettes_hits"] += 1

                    for l in lbls:
                        l_fol = l["folio"]
                        l_sec = "Rosettes" if l_fol == "fRos" else l["section"]
                        folio_to_section[r["folio"]][l_sec] += 1
                        if l_fol in ZODIAC_SIGN_MAP:
                            folio_to_zodiac[r["folio"]][ZODIAC_SIGN_MAP[l_fol]] += 1
                        if l["section"] == "P":
                            folio_to_pharma[r["folio"]][l_fol] += 1

                    r_hits.append(
                        {
                            "loc": line_obj["loc"],
                            "word_pos": w_idx + 1,
                            "recipe_word": w,
                            "canon": c,
                            "global_prose_count": p_cnt,
                            "matched_labels": [
                                {
                                    "folio": l["folio"],
                                    "section": l["section"],
                                    "loc": l["loc"],
                                    "unit": l["unit"],
                                    "label_word": l["word"],
                                }
                                for l in lbls
                            ],
                        }
                    )
                    seen_canons.add(c)

        r["rare_label_hits"] = r_hits
        r["distinct_rare_label_canons"] = len(seen_canons)

    def summarize_buckets(bdict):
        res = {}
        for k, st in bdict.items():
            cnt = max(st["count"], 1)
            tw = max(st["total_words"], 1)
            res[k] = {
                "recipe_count": st["count"],
                "total_words": st["total_words"],
                "mean_words_per_recipe": round(st["total_words"] / cnt, 2),
                "mean_lines_per_recipe": round(st["total_lines"] / cnt, 2),
                "gallows_opener_rate": round(st["gallows_openers"] / cnt, 4),
                "p_opener_rate": round(st["p_openers"] / cnt, 4),
                "t_opener_rate": round(st["t_openers"] / cnt, 4),
                "k_opener_rate": round(st["k_openers"] / cnt, 4),
                "f_opener_rate": round(st["f_openers"] / cnt, 4),
                "closer_am_m_rate": round(st["closer_am_m"] / cnt, 4),
                "closer_ry_ly_rate": round(st["closer_ry_ly"] / cnt, 4),
                "closer_y_rate": round(st["closer_y"] / cnt, 4),
                "closer_in_rate": round(st["closer_in"] / cnt, 4),
                "qo_word_density": round(st["qo_words"] / tw, 4),
                "ch_sh_verb_density": round(st["ch_sh_words"] / tw, 4),
                "rare_label_hits_per_recipe": round(st["rare_label_hits"] / cnt, 3),
                "zodiac_hits_per_recipe": round(st["zodiac_hits"] / cnt, 3),
                "pharma_hits_per_recipe": round(st["pharma_hits"] / cnt, 3),
                "bio_hits_per_recipe": round(st["bio_hits"] / cnt, 3),
                "rosettes_hits_per_recipe": round(st["rosettes_hits"] / cnt, 3),
            }
        return res

    star_summary = summarize_buckets(star_stats)
    hand_summary = summarize_buckets(hand_stats)

    # 4. Rank recipes by number of distinct rare label canons & rarity info bits
    def recipe_score(r):
        best_by_canon = {}
        for h in r["rare_label_hits"]:
            c = h["canon"]
            sc = math.log2(20.0 / max(h["global_prose_count"], 1))
            if c not in best_by_canon or sc > best_by_canon[c]:
                best_by_canon[c] = sc
        # Favor compact recipes (<= 10 lines) when tied on distinct rare canons
        return (len(best_by_canon), round(sum(best_by_canon.values()), 3), -len(r["lines"]))

    ranked_recipes = sorted(recipes, key=recipe_score, reverse=True)
    top_recipes_summary = []
    for r in ranked_recipes[:25]:
        n_dist, r_sc, _ = recipe_score(r)
        # Generate word-by-word interlinear structural & label decoding for the top 8
        decoded_lines = []
        if len(top_recipes_summary) < 8:
            for l_idx, l_obj in enumerate(r["lines"]):
                w_tags = []
                for w_i, (w, c) in enumerate(zip(l_obj["words"], l_obj["canons"])):
                    role = tag_word_role(
                        w,
                        w_i,
                        len(l_obj["words"]),
                        is_par_start=(l_idx == 0),
                        is_par_end=(l_idx == len(r["lines"]) - 1),
                    )
                    lbl_note = ""
                    if c in labels_by_canon and len(c) >= 3:
                        lbls = labels_by_canon[c]
                        p_cnt = prose_canon_counts[c]
                        short_lbls = [f"{l['loc']}({l['unit']}):{l['word']}" for l in lbls[:3]]
                        lbl_note = f" [CRIB cnt={p_cnt} <-> {', '.join(short_lbls)}]"
                    w_tags.append(f"{w}<{role}{lbl_note}>")
                decoded_lines.append({"loc": l_obj["loc"], "glossed": " · ".join(w_tags)})

        top_recipes_summary.append(
            {
                "recipe_id": r["recipe_id"],
                "folio": r["folio"],
                "folio_par_index": r["folio_par_index"],
                "hand": r["hand"],
                "star_code": r["star_code"],
                "star_comment": r["star_comment"],
                "start_loc": r["start_loc"],
                "end_loc": r["end_loc"],
                "num_lines": len(r["lines"]),
                "num_words": len(r["words"]),
                "opener_word": r["words"][0] if r["words"] else "",
                "closer_word": r["words"][-1] if r["words"] else "",
                "distinct_rare_label_canons": n_dist,
                "rarity_info_bits": r_sc,
                "rare_label_hits": r["rare_label_hits"],
                "decoded_lines": decoded_lines,
            }
        )

    # 5. Ultra-rare (global prose count <= 3) label concordances in Starred Recipes
    ultra_rare_concordances = []
    for r in recipes:
        for h in r["rare_label_hits"]:
            if h["global_prose_count"] <= 3:
                ultra_rare_concordances.append(
                    {
                        "recipe_id": r["recipe_id"],
                        "folio": r["folio"],
                        "folio_par_index": r["folio_par_index"],
                        "star_code": r["star_code"],
                        "star_comment": r["star_comment"],
                        "loc": h["loc"],
                        "word_pos": h["word_pos"],
                        "recipe_word": h["recipe_word"],
                        "canon": h["canon"],
                        "global_prose_count": h["global_prose_count"],
                        "matched_labels": h["matched_labels"],
                    }
                )

    # 6. Per-folio summary table across all 23 Starred Recipe pages
    per_folio_summary = []
    for fol in recipe_folios:
        fol_recs = [r for r in recipes if r["folio"] == fol]
        star_seq = folio_star_seqs.get(fol, [])
        per_folio_summary.append(
            {
                "folio": fol,
                "hand": folios[fol]["meta"].get("H", "?"),
                "num_recipes": len(fol_recs),
                "total_words": sum(len(r["words"]) for r in fol_recs),
                "star_sequence": " ".join(star_seq),
                "top_zodiac_signs": folio_to_zodiac[fol].most_common(4),
                "top_pharma_folios": folio_to_pharma[fol].most_common(4),
                "section_hit_counts": dict(folio_to_section[fol]),
            }
        )

    out = {
        "total_starred_recipe_folios": len(recipe_folios),
        "total_starred_recipes": len(recipes),
        "total_starred_recipe_words": sum(len(r["words"]) for r in recipes),
        "star_type_comparison": star_summary,
        "scribe_hand_comparison": hand_summary,
        "ultra_rare_concordances_count_le_3": ultra_rare_concordances,
        "per_folio_summary": per_folio_summary,
        "top_25_multi_crib_recipes": top_recipes_summary,
    }

    OUT_JSON.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"Saved {OUT_JSON}")
    print(f"Total Starred Recipe folios: {len(recipe_folios)}, Total recipes: {len(recipes)}, Total words: {out['total_starred_recipe_words']}")
    print("\n--- Star Type Comparison ---")
    for k, v in star_summary.items():
        print(f"  {k}: {v}")
    print("\n--- Scribe Hand Comparison (Hand 3 vs Hand 4) ---")
    for k, v in hand_summary.items():
        print(f"  {k}: {v}")
    print("\n--- Per-Folio Star Sequences & Top Cross-Referenced Diagram Sections ---")
    for pf in per_folio_summary:
        print(f"  {pf['folio']:6s} (H={pf['hand']}, {pf['num_recipes']:2d} recs): stars=[{pf['star_sequence']}] | secs={pf['section_hit_counts']} | topZ={pf['top_zodiac_signs'][:2]} | topP={pf['top_pharma_folios'][:2]}")
    print("\n--- Top 6 Multi-Crib Starred Recipes (with Word-by-Word Decoding) ---")
    for tr in top_recipes_summary[:6]:
        print(f"\n  Recipe #{tr['recipe_id']} ({tr['folio']} P{tr['folio_par_index']}, star={tr['star_code']} [{tr['star_comment']}], {tr['num_lines']}L/{tr['num_words']}W, opener={tr['opener_word']}, closer={tr['closer_word']}): {tr['distinct_rare_label_canons']} rare canons ({tr['rarity_info_bits']} bits)")
        for dl in tr["decoded_lines"]:
            print(f"    <{dl['loc']}> {dl['glossed']}")


if __name__ == "__main__":
    main()
