#!/usr/bin/env python3
r"""
Attack 115 (Discovery 132): Register-by-Register (`@Lc` Apothecary Vessel + `@Lf` Root/Leaf Row
+ `<%> @P0` Preparation Paragraph) Spatial & Lexical Decomposition of All 16 Pharmaceutical Folios (`f88r–f102v2`)

Tests & Builds:
1. Parses all `16` Pharmaceutical Formulary folios (`f88r–f102v2`) into their exact Tripartite
   Horizontal Compounding Registers:
   `Register R_k = [@Lc (+Lc) Apothecary Vessel Label] + [@Lf (+Lf) Botanical Root/Leaf Row] + [<%> @P0 Preparation Paragraph]`
2. Quantitative Comparison of `@Lc` (Apothecary Vessel/Jar Labels) vs. `@Lf` (Botanical Root/Leaf Row Labels)
   vs. `@P0` (Preparation Register Prose):
   - Compares word length (`mean_chars`), morphological profiles (`o-`, `qo-`, `d-/da-`, `-ol/-or/-al/-ar`, `-y/-dy`, `-aiin`),
   - Compares Radical Family distributions (`Compound Gallows-Bench cph/cfh/kch/tch`, `Simplex Gallows`, `Bench`, `Vocalic/Liquid`),
   - Compares corpus document frequency (`mean_df`, singleton rate) and cross-section attestation (`H`, `S`, `B`).
3. Multi-Register Specialization & Row-by-Row Botanical Routing:
   - Tests whether distinct `<%> @P0` registers (`Row 1, Row 2, Row 3, Row 4`) on the same Pharmaceutical
     folio cite **distinct `#1` Herbal Monographs (`$I=H`)** AND **distinct `#1` Starred Clinical Recipes (`$I=S`)**,
   - Tests whether each row's `@Lf_k` plant-part labels and `@P_k` prose share canonical roots (`core`) or
     converge on the same downstream Starred Recipes (`$I=S`) / Herbal Monographs (`$I=H`),
   - Compares Top-Row (`Register 1`) vs. Middle-Row (`Register 2`) vs. Bottom-Row (`Register 3–4`) morphology.
"""

import json
import math
import random
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ZL_PATH = ROOT / "data" / "ZL3b-n.txt"
OUT_PATH = ROOT / "data" / "attack115_pharmaceutical_register_row_decomposition.json"


def normalize_token(w: str) -> str:
    w = re.sub(r"\[([^:\]]+):[^\]]+\]", r"\1", w)
    w = re.sub(r"\{[^}]*\}", "", w)
    w = re.sub(r"<[^>]*>", "", w)
    w = w.replace("?", "").replace("!", "").replace("*", "").replace("%", "").strip()
    return w


def canonical_stem(w: str, is_top_line: bool = False) -> str:
    s = w
    if is_top_line:
        s = s.replace("p", "t").replace("f", "k")
    if s.startswith("qo") and len(s) > 2:
        s = s[1:]
    elif s.startswith("q") and len(s) > 2:
        s = s[1:]
    s = re.sub(r"i{2,}", "ii", s)
    s = re.sub(r"e{2,}", "ee", s)
    if len(s) >= 4 and s.endswith("dy"):
        s = s[:-2] + "y"
    return s


def label_gallows_folded_stem(w: str) -> str:
    """Fold p->t and f->k even on labels (@Lc/@Lf often use ornate initial/medial p/f gallows)."""
    s = w.replace("p", "t").replace("f", "k")
    return canonical_stem(s, is_top_line=True)


def strip_affixes(cs: str) -> str:
    s = cs.replace("p", "t").replace("f", "k")
    for pref in ("qo", "qok", "qot", "ol", "ot", "ok", "od", "os", "or", "al", "ar", "da", "sa", "yk", "yt", "o", "y", "d", "s", "l", "r"):
        if s.startswith(pref) and len(s) - len(pref) >= 2:
            s = s[len(pref):]
            break
    for suf in ("aiin", "oiin", "eiin", "edy", "ody", "aiir", "oiir", "al", "ar", "ol", "or", "am", "om", "an", "in", "ir", "dy", "ey", "ly", "ry", "y", "l", "r", "m", "n", "s", "d"):
        if s.endswith(suf) and len(s) - len(suf) >= 2:
            s = s[:-len(suf)]
            break
    return s


def classify_radical_family(w: str) -> str:
    if any(r in w for r in ("kch", "tch", "pch", "fch", "ckh", "cth", "cph", "cfh")):
        return "COMPOUND_GALLOWS_BENCH"
    if any(r in w for r in ("ke", "te", "pe", "fe")):
        return "EXTENDED_GALLOWS"
    if any(r in w for r in ("k", "t", "p", "f")):
        return "SIMPLEX_GALLOWS"
    if "ch" in w or "sh" in w:
        return "BENCH_ONLY"
    return "VOCALIC_LIQUID_ONLY"


def morph_profile(words_with_top):
    n = len(words_with_top)
    if n == 0:
        return {}
    mean_chars = sum(len(w) for w, _ in words_with_top) / n
    has_pf_gallows = sum(1 for w, _ in words_with_top if "p" in w or "f" in w)
    has_kt_gallows = sum(1 for w, _ in words_with_top if "k" in w or "t" in w)
    o_pref = sum(1 for w, _ in words_with_top if w.startswith("o") and not w.startswith(("ol", "or")))
    qo_pref = sum(1 for w, _ in words_with_top if w.startswith("qo"))
    l_app = sum(1 for w, _ in words_with_top if w.startswith(("l", "ol", "qol")) and len(w) >= 3)
    d_pref = sum(1 for w, _ in words_with_top if w.startswith(("d", "da")))
    s_pref = sum(1 for w, _ in words_with_top if w.startswith(("s", "sa")))
    edy_suf = sum(1 for w, _ in words_with_top if w.endswith("edy"))
    aiin_suf = sum(1 for w, _ in words_with_top if w.endswith(("aiin", "oiin", "iin")))
    y_dy_suf = sum(1 for w, _ in words_with_top if w.endswith("y") and not w.endswith("edy"))
    liquid_suf = sum(1 for w, _ in words_with_top if w.endswith(("ol", "or", "al", "ar", "am", "om")))

    fam_counts = Counter(classify_radical_family(w) for w, _ in words_with_top)

    return {
        "n_tokens": n,
        "mean_word_length_chars": round(mean_chars, 2),
        "pf_ornate_gallows_pct": round(100.0 * has_pf_gallows / n, 2),
        "kt_standard_gallows_pct": round(100.0 * has_kt_gallows / n, 2),
        "o_nominal_pct": round(100.0 * o_pref / n, 2),
        "qo_active_pct": round(100.0 * qo_pref / n, 2),
        "l_ol_qol_applicative_pct": round(100.0 * l_app / n, 2),
        "d_da_pct": round(100.0 * d_pref / n, 2),
        "s_sa_pct": round(100.0 * s_pref / n, 2),
        "edy_processual_pct": round(100.0 * edy_suf / n, 2),
        "aiin_measured_pct": round(100.0 * aiin_suf / n, 2),
        "y_dy_nominal_pct": round(100.0 * y_dy_suf / n, 2),
        "liquid_nasal_coda_pct": round(100.0 * liquid_suf / n, 2),
        "radical_families_pct": {k: round(100.0 * v / n, 2) for k, v in sorted(fam_counts.items())},
    }


def main():
    folio_meta_re = re.compile(r"^<f([0-9]+[rv][0-9]*)>\s*<!\s*(.*?)\s*>$")
    line_re = re.compile(r"^<f([0-9]+[rv][0-9]*)\.([0-9]+),([^>]+)>\s+(.*)$")

    folios_meta = {}
    canon_counts = Counter()
    folio_canon_set = defaultdict(set)

    # Pharmaceutical folio structured data
    pharm_folios = defaultdict(lambda: {
        "lc_labels": [],      # (loc, w, cs, folded_cs, core, itop)
        "lf_labels": [],      # (loc, w, cs, folded_cs, core, itop)
        "other_labels": [],   # (loc, w, cs, folded_cs, core, itop)
        "registers": [],      # list of dicts for each <%> @P paragraph
        "events": [],         # ordered list of ('LC', item) | ('LF', item) | ('REG_START', reg_idx)
    })

    herbal_folios = defaultdict(set)
    balneo_folios = defaultdict(set)
    starred_recipes = defaultdict(set)

    current_pharm_reg = {}
    current_star_idx = defaultdict(int)
    in_para_top = defaultdict(lambda: True)

    with open(ZL_PATH, "r", encoding="utf-8", errors="replace") as f:
        for raw_line in f:
            sline = raw_line.strip()
            mf = folio_meta_re.match(sline)
            if mf:
                fol = "f" + mf.group(1)
                meta_str = mf.group(2)
                m_dict = {}
                for kv in meta_str.split():
                    if "=" in kv:
                        k, v = kv.lstrip("$").split("=", 1)
                        m_dict[k] = v
                folios_meta[fol] = {
                    "section": m_dict.get("I", ""),
                    "language": m_dict.get("L", ""),
                    "hand": m_dict.get("H", ""),
                    "quire": m_dict.get("Q", ""),
                    "bifolio": m_dict.get("B", ""),
                }
                continue

            m = line_re.match(sline)
            if not m:
                continue
            fol = "f" + m.group(1)
            lnum = int(m.group(2))
            loc = m.group(3)
            text = m.group(4)

            meta = folios_meta.get(fol, {})
            sec = meta.get("section", "")

            has_para_start = "<%>" in text
            has_para_end = "<$>" in text

            clean_line = re.sub(r"<[^>]*>", " ", text)
            raw_tokens = [t for t in re.split(r"[.\s,]+", clean_line) if t]
            words = [normalize_token(t) for t in raw_tokens]
            words = [w for w in words if w and re.search(r"[a-z]", w)]
            if not words:
                if has_para_end:
                    in_para_top[fol] = True
                continue

            is_label = "@L" in loc or "+L" in loc
            is_top = (not is_label) and (has_para_start or lnum == 1 or in_para_top[fol])

            stems = []
            for w in words:
                cs = canonical_stem(w, is_top_line=is_top)
                fcs = label_gallows_folded_stem(w)
                core = strip_affixes(cs)
                canon_counts[cs] += 1
                folio_canon_set[fol].add(cs)
                stems.append((w, cs, fcs, core, is_top))

            if sec == "H" and fol not in ("f58r", "f58v"):
                for _, cs, fcs, _, _ in stems:
                    herbal_folios[fol].add(cs)
                    herbal_folios[fol].add(fcs)
            elif sec == "B":
                for _, cs, fcs, _, _ in stems:
                    balneo_folios[fol].add(cs)
                    balneo_folios[fol].add(fcs)
            elif (sec == "S" or fol in ("f58r", "f58v")) and ("P" in loc or "Pt" in loc):
                if has_para_start or current_star_idx[fol] == 0:
                    current_star_idx[fol] += 1
                rid = f"{fol}.R{current_star_idx[fol]}"
                for _, cs, fcs, _, _ in stems:
                    starred_recipes[rid].add(cs)
                    starred_recipes[rid].add(fcs)

            if sec == "P":
                if "Lc" in loc:
                    for w, cs, fcs, core, itop in stems:
                        item = (f"{fol}.{lnum},{loc}", w, cs, fcs, core, itop)
                        pharm_folios[fol]["lc_labels"].append(item)
                        pharm_folios[fol]["events"].append(("LC", item))
                elif "Lf" in loc:
                    for w, cs, fcs, core, itop in stems:
                        item = (f"{fol}.{lnum},{loc}", w, cs, fcs, core, itop)
                        pharm_folios[fol]["lf_labels"].append(item)
                        pharm_folios[fol]["events"].append(("LF", item))
                elif is_label:
                    for w, cs, fcs, core, itop in stems:
                        item = (f"{fol}.{lnum},{loc}", w, cs, fcs, core, itop)
                        pharm_folios[fol]["other_labels"].append(item)
                else:
                    # @P prose line
                    if has_para_start or fol not in current_pharm_reg:
                        reg_num = len(pharm_folios[fol]["registers"]) + 1
                        reg_obj = {
                            "register_id": f"{fol}.Reg{reg_num}",
                            "folio": fol,
                            "reg_num": reg_num,
                            "start_line": lnum,
                            "end_line": lnum,
                            "loc": loc,
                            "tokens": [],       # (w, cs, fcs, core, is_top)
                            "paired_lc": [],    # assigned @Lc jar labels for this row
                            "paired_lf": [],    # assigned @Lf plant-part labels for this row
                        }
                        pharm_folios[fol]["registers"].append(reg_obj)
                        current_pharm_reg[fol] = reg_obj
                        pharm_folios[fol]["events"].append(("REG", reg_num - 1))
                    reg_obj = current_pharm_reg[fol]
                    reg_obj["end_line"] = lnum
                    reg_obj["tokens"].extend(stems)

            if not is_label:
                in_para_top[fol] = False
            if has_para_end:
                in_para_top[fol] = True

    # Pair each folio's @Lc and @Lf label blocks to their corresponding <%> @P0 Register!
    # Rule: In ZL3b-n.txt, an @Lc + @Lf* block immediately preceding REG_k belongs to REG_k;
    # if an @Lc + @Lf* block appears AFTER the last REG (as on f88v, f89r1, f89v1, f89v2, f99v, f102r2),
    # it belongs to the immediately preceding REG (the bottom register whose jar/roots sit below the text block).
    for fol, pdata in pharm_folios.items():
        regs = pdata["registers"]
        if not regs:
            continue
        pending_lc = []
        pending_lf = []
        last_reg_idx = 0
        for etype, payload in pdata["events"]:
            if etype == "LC":
                pending_lc.append(payload)
            elif etype == "LF":
                pending_lf.append(payload)
            elif etype == "REG":
                ridx = payload
                regs[ridx]["paired_lc"].extend(pending_lc)
                regs[ridx]["paired_lf"].extend(pending_lf)
                pending_lc = []
                pending_lf = []
                last_reg_idx = ridx
        # Any trailing labels after the last @P0 paragraph attach to the bottom register
        if pending_lc or pending_lf:
            regs[last_reg_idx]["paired_lc"].extend(pending_lc)
            regs[last_reg_idx]["paired_lf"].extend(pending_lf)

    # Open-class filter (exclude Top-45 canonical stems)
    top45_cs = {w for w, _ in canon_counts.most_common(45)}
    stem_df = Counter()
    for fol, sset in folio_canon_set.items():
        for cs in sset:
            stem_df[cs] += 1

    N_folios = len(folio_canon_set)
    open_stems = {
        cs for cs, df in stem_df.items()
        if cs not in top45_cs and len(cs) >= 3 and 2 <= df <= 95
    }
    stem_idf = {cs: math.log(N_folios / (1.0 + stem_df[cs])) for cs in open_stems}

    # 1. Compare @Lc (Apothecary Vessel/Jar Labels) vs @Lf (Botanical Root/Leaf Labels) vs @P0 (Preparation Prose)
    all_lc = []
    all_lf = []
    all_p_prose = []
    for fol in sorted(pharm_folios.keys()):
        all_lc.extend(pharm_folios[fol]["lc_labels"])
        all_lf.extend(pharm_folios[fol]["lf_labels"])
        for reg in pharm_folios[fol]["registers"]:
            for w, cs, fcs, core, itop in reg["tokens"]:
                all_p_prose.append((reg["register_id"], w, cs, fcs, core, itop))

    lc_morph = morph_profile([(w, itop) for _, w, _, _, _, itop in all_lc])
    lf_morph = morph_profile([(w, itop) for _, w, _, _, _, itop in all_lf])
    p_morph = morph_profile([(w, itop) for _, w, _, _, _, itop in all_p_prose])

    all_h_all = set().union(*herbal_folios.values())
    all_s_all = set().union(*starred_recipes.values())
    all_b_all = set().union(*balneo_folios.values())

    def cross_sec_stats(items):
        if not items:
            return {}
        n = len(items)
        singleton = sum(1 for _, _, cs, fcs, _, _ in items if stem_df[cs] <= 1 and stem_df[fcs] <= 1)
        in_h = sum(1 for _, _, cs, fcs, _, _ in items if cs in all_h_all or fcs in all_h_all)
        in_s = sum(1 for _, _, cs, fcs, _, _ in items if cs in all_s_all or fcs in all_s_all)
        in_b = sum(1 for _, _, cs, fcs, _, _ in items if cs in all_b_all or fcs in all_b_all)
        mean_df = sum(max(stem_df[cs], stem_df[fcs]) for _, _, cs, fcs, _, _ in items) / n
        return {
            "n_tokens": n,
            "mean_corpus_df": round(mean_df, 2),
            "singleton_rate_pct": round(100.0 * singleton / n, 2),
            "attested_in_herbal_pct": round(100.0 * in_h / n, 2),
            "attested_in_starred_pct": round(100.0 * in_s / n, 2),
            "attested_in_balneo_pct": round(100.0 * in_b / n, 2),
        }

    lc_cross = cross_sec_stats(all_lc)
    lf_cross = cross_sec_stats(all_lf)
    p_cross = cross_sec_stats(all_p_prose)

    # 1b. Decompose @Lc Apothecary Vessel Compound Titles into 2-to-3 attested sub-stems
    attested_vocab = {cs for cs, cnt in canon_counts.items() if cnt >= 2 and len(cs) >= 2}

    def decompose_lc_compound(w: str, fcs: str):
        if stem_df[fcs] >= 2:
            return [fcs], "DIRECT_ATTESTED"
        s = w.replace("p", "t").replace("f", "k")
        if s.endswith("g"):
            s = s[:-1] + "m"
        # Check o- stripped direct
        if s.startswith("o") and len(s) >= 4:
            s_no_o = canonical_stem(s[1:], True)
            if s_no_o in attested_vocab:
                return ["o-", s_no_o], "O_PREFIX_PLUS_STEM"
        # Try 2-way split of s (or o- stripped s)
        for prefix_tag, cand in [("", s), ("o-", s[1:] if s.startswith("o") and len(s) >= 5 else "")]:
            if not cand:
                continue
            best_pair = None
            best_score = -1
            for i in range(2, len(cand) - 1):
                p1, p2 = canonical_stem(cand[:i], True), canonical_stem(cand[i:], True)
                if p1 in attested_vocab and p2 in attested_vocab:
                    sc = canon_counts[p1] + canon_counts[p2]
                    if sc > best_score:
                        best_score = sc
                        best_pair = ([prefix_tag] if prefix_tag else []) + [p1, p2]
            if best_pair:
                return best_pair, "TWO_STEM_COMPOUND"
            # Try 2-way split + 1-char coda
            for i in range(2, len(cand) - 2):
                p1, p2 = canonical_stem(cand[:i], True), canonical_stem(cand[i:-1], True)
                if p1 in attested_vocab and len(p2) >= 2 and p2 in attested_vocab:
                    return ([prefix_tag] if prefix_tag else []) + [p1, p2], "TWO_STEM_PLUS_CODA"
            # Try 3-way split
            for i in range(2, len(cand) - 3):
                for j in range(i + 2, len(cand) - 1):
                    p1 = canonical_stem(cand[:i], True)
                    p2 = canonical_stem(cand[i:j], True)
                    p3 = canonical_stem(cand[j:], True)
                    if p1 in attested_vocab and p2 in attested_vocab and p3 in attested_vocab:
                        return ([prefix_tag] if prefix_tag else []) + [p1, p2, p3], "THREE_STEM_COMPOUND"
        return [fcs], "UNSPLIT"

    lc_decompositions = []
    n_lc_resolved = 0
    for loc, w, cs, fcs, core, _ in all_lc:
        parts, dtype = decompose_lc_compound(w, fcs)
        if dtype != "UNSPLIT":
            n_lc_resolved += 1
        stem_parts = [p for p in parts if p != "o-"]
        lc_decompositions.append({
            "loc": loc,
            "surface": w,
            "folded_cs": fcs,
            "df": max(stem_df[cs], stem_df[fcs]),
            "decomposition_type": dtype,
            "constituent_stems": parts,
            "constituents_in_herbal": [p for p in stem_parts if p in all_h_all],
            "constituents_in_starred": [p for p in stem_parts if p in all_s_all],
        })

    # 2. Analyze all 44 Pharmaceutical Registers across the 16 folios
    register_records = []
    folio_summaries = []

    h_open_map = {h: s & open_stems for h, s in herbal_folios.items()}
    s_open_map = {r: s & open_stems for r, s in starred_recipes.items()}
    b_open_map = {b: s & open_stems for b, s in balneo_folios.items()}

    total_multi_reg_folios = 0
    distinct_top1_herbal_pairs = 0
    distinct_top1_starred_pairs = 0
    total_reg_pairs = 0

    for fol in sorted(pharm_folios.keys()):
        pdata = pharm_folios[fol]
        lc_list = pdata["lc_labels"]
        lf_list = pdata["lf_labels"]
        regs = pdata["registers"]

        fol_reg_top_herbals = []
        fol_reg_top_starred = []

        for reg in regs:
            reg_cs_set = ({cs for _, cs, _, _, _ in reg["tokens"]} | {fcs for _, _, fcs, _, _ in reg["tokens"]}) & open_stems
            reg_all_cs = {cs for _, cs, _, _, _ in reg["tokens"]} | {fcs for _, _, fcs, _, _ in reg["tokens"]}
            reg_cores = {core for _, _, _, core, _ in reg["tokens"] if len(core) >= 2}

            row_lc = reg["paired_lc"]
            row_lf = reg["paired_lf"]

            # Row-specific @Lf matches (stem or core)
            row_lf_matches = []
            for loc, w, cs, fcs, core, _ in row_lf:
                if cs in reg_all_cs or fcs in reg_all_cs:
                    row_lf_matches.append({"loc": loc, "label": w, "cs": fcs, "match_type": "EXACT_STEM"})
                elif len(core) >= 2 and core in reg_cores:
                    # Find prose word with matching core
                    pw = [pw for pw, _, _, pcore, _ in reg["tokens"] if pcore == core][0]
                    row_lf_matches.append({"loc": loc, "label": w, "core": core, "prose_word": pw, "match_type": "SHARED_CORE"})

            # Rank Herbal Monographs ($I=H) cited by this Register (using both prose stems + row @Lf stems!)
            combined_row_open = reg_cs_set | ({fcs for _, _, _, fcs, _, _ in row_lf} & open_stems)
            h_scores = []
            for hfol, hset in h_open_map.items():
                shared_prose = reg_cs_set & hset
                shared_lf = ({fcs for _, _, _, fcs, _, _ in row_lf} & open_stems) & hset
                shared_all = combined_row_open & hset
                if shared_prose:
                    idf_sum = sum(stem_idf[c] for c in shared_prose)
                    h_scores.append({
                        "herbal_folio": hfol,
                        "language": folios_meta.get(hfol, {}).get("language", ""),
                        "idf_score": round(idf_sum, 3),
                        "n_shared_prose": len(shared_prose),
                        "shared_prose_stems": sorted(shared_prose),
                        "shared_row_lf_stems": sorted(shared_lf),
                    })
            h_scores.sort(key=lambda x: (-x["idf_score"], -x["n_shared_prose"]))

            # Rank Starred Recipes ($I=S)
            s_scores = []
            for srid, sset in s_open_map.items():
                shared_prose = reg_cs_set & sset
                shared_lf = ({fcs for _, _, _, fcs, _, _ in row_lf} & open_stems) & sset
                if shared_prose:
                    idf_sum = sum(stem_idf[c] for c in shared_prose)
                    s_scores.append({
                        "recipe_id": srid,
                        "idf_score": round(idf_sum, 3),
                        "n_shared_prose": len(shared_prose),
                        "shared_prose_stems": sorted(shared_prose),
                        "shared_row_lf_stems": sorted(shared_lf),
                    })
            s_scores.sort(key=lambda x: (-x["idf_score"], -x["n_shared_prose"]))

            # Rank Balneological Folios ($I=B)
            b_scores = []
            for bfol, bset in b_open_map.items():
                shared_prose = reg_cs_set & bset
                if shared_prose:
                    idf_sum = sum(stem_idf[c] for c in shared_prose)
                    b_scores.append({
                        "balneo_folio": bfol,
                        "idf_score": round(idf_sum, 3),
                        "n_shared_prose": len(shared_prose),
                        "shared_prose_stems": sorted(shared_prose),
                    })
            b_scores.sort(key=lambda x: (-x["idf_score"], -x["n_shared_prose"]))

            top1_h = h_scores[0]["herbal_folio"] if h_scores else None
            top1_s = s_scores[0]["recipe_id"] if s_scores else None
            fol_reg_top_herbals.append(top1_h)
            fol_reg_top_starred.append(top1_s)

            reg_rec = {
                "register_id": reg["register_id"],
                "folio": fol,
                "reg_num": reg["reg_num"],
                "line_span": f"L{reg['start_line']}-L{reg['end_line']}",
                "n_tokens": len(reg["tokens"]),
                "n_open_stems": len(reg_cs_set),
                "paired_lc_jar_labels": [{"loc": loc, "w": w, "folded_cs": fcs, "core": core} for loc, w, _, fcs, core, _ in row_lc],
                "paired_lf_plant_labels": [{"loc": loc, "w": w, "folded_cs": fcs, "core": core} for loc, w, _, fcs, core, _ in row_lf],
                "row_lf_to_prose_matches": row_lf_matches,
                "opening_words": [w for w, _, _, _, _ in reg["tokens"][:6]],
                "closing_words": [w for w, _, _, _, _ in reg["tokens"][-4:]],
                "morph_profile": morph_profile([(w, itop) for w, _, _, _, itop in reg["tokens"]]),
                "top_herbal_monographs": h_scores[:3],
                "top_starred_recipes": s_scores[:2],
                "top_balneo_folios": b_scores[:2],
            }
            register_records.append(reg_rec)

        if len(regs) >= 2:
            total_multi_reg_folios += 1
            for i in range(len(fol_reg_top_herbals)):
                for j in range(i + 1, len(fol_reg_top_herbals)):
                    total_reg_pairs += 1
                    if fol_reg_top_herbals[i] != fol_reg_top_herbals[j]:
                        distinct_top1_herbal_pairs += 1
                    if fol_reg_top_starred[i] != fol_reg_top_starred[j]:
                        distinct_top1_starred_pairs += 1

        folio_summaries.append({
            "folio": fol,
            "n_lc_jar_labels": len(lc_list),
            "lc_jar_words": [w for _, w, _, _, _, _ in lc_list],
            "n_lf_plant_labels": len(lf_list),
            "lf_words_sample": [w for _, w, _, _, _, _ in lf_list[:10]],
            "n_registers": len(regs),
            "register_top1_herbals": fol_reg_top_herbals,
            "register_top1_starred": fol_reg_top_starred,
        })

    # 3. Permutation Test for Row-Specific (@Lf_k <-> @P_k) Core + Stem Sharing vs Shuffled Registers
    obs_row_core_matches = sum(len(r["row_lf_to_prose_matches"]) for r in register_records)
    rng = random.Random(42)
    all_reg_objs = [r for fol in sorted(pharm_folios.keys()) for r in pharm_folios[fol]["registers"]]
    null_row_matches = []
    for _ in range(1000):
        shuffled_regs = all_reg_objs[:]
        rng.shuffle(shuffled_regs)
        c = 0
        for r_lf_owner, r_prose_owner in zip(all_reg_objs, shuffled_regs):
            p_cs = {cs for _, cs, _, _, _ in r_prose_owner["tokens"]} | {fcs for _, _, fcs, _, _ in r_prose_owner["tokens"]}
            p_cores = {core for _, _, _, core, _ in r_prose_owner["tokens"] if len(core) >= 2}
            for _, _, cs, fcs, core, _ in r_lf_owner["paired_lf"]:
                if cs in p_cs or fcs in p_cs or (len(core) >= 2 and core in p_cores):
                    c += 1
        null_row_matches.append(c)
    nr_mean = sum(null_row_matches) / len(null_row_matches)
    nr_std = math.sqrt(sum((x - nr_mean) ** 2 for x in null_row_matches) / len(null_row_matches)) or 1.0
    z_row_match = (obs_row_core_matches - nr_mean) / nr_std

    # 4. Row-Position Gradient: Register 1 (Top Row) vs Register 2 (Middle Row) vs Register 3+ (Bottom Row)
    pharm_fol_list = sorted(pharm_folios.keys())
    reg1_tokens = [(w, itop) for fol in pharm_fol_list for r in pharm_folios[fol]["registers"] if r["reg_num"] == 1 for w, _, _, _, itop in r["tokens"]]
    reg2_tokens = [(w, itop) for fol in pharm_fol_list for r in pharm_folios[fol]["registers"] if r["reg_num"] == 2 for w, _, _, _, itop in r["tokens"]]
    reg3_tokens = [(w, itop) for fol in pharm_fol_list for r in pharm_folios[fol]["registers"] if r["reg_num"] >= 3 for w, _, _, _, itop in r["tokens"]]

    summary = {
        "n_pharmaceutical_folios": len(pharm_fol_list),
        "n_total_registers": len(register_records),
        "n_lc_jar_labels": len(all_lc),
        "n_lf_plant_labels": len(all_lf),
        "locus_comparison": {
            "lc_apothecary_jar_labels": {
                "morph_profile": lc_morph,
                "cross_section_stats": lc_cross,
                "n_compound_resolved": n_lc_resolved,
                "compound_resolved_pct": round(100.0 * n_lc_resolved / max(1, len(all_lc)), 2),
                "compound_decompositions": lc_decompositions,
            },
            "lf_plant_part_labels": {
                "morph_profile": lf_morph,
                "cross_section_stats": lf_cross,
            },
            "p_register_prose": {
                "morph_profile": p_morph,
                "cross_section_stats": p_cross,
            },
        },
        "register_specialization": {
            "n_multi_register_folios": total_multi_reg_folios,
            "n_same_folio_register_pairs": total_reg_pairs,
            "n_distinct_top1_herbal_pairs": distinct_top1_herbal_pairs,
            "distinct_top1_herbal_rate_pct": round(100.0 * distinct_top1_herbal_pairs / max(1, total_reg_pairs), 2),
            "n_distinct_top1_starred_pairs": distinct_top1_starred_pairs,
            "distinct_top1_starred_rate_pct": round(100.0 * distinct_top1_starred_pairs / max(1, total_reg_pairs), 2),
        },
        "row_specific_lf_to_prose_alignment": {
            "observed_matches": obs_row_core_matches,
            "null_mean": round(nr_mean, 2),
            "null_std": round(nr_std, 2),
            "lift": round(obs_row_core_matches / max(0.01, nr_mean), 2),
            "z_score": round(z_row_match, 2),
        },
        "vertical_register_row_gradient": {
            "register_1_top_row": morph_profile(reg1_tokens),
            "register_2_mid_row": morph_profile(reg2_tokens),
            "register_3plus_bottom_row": morph_profile(reg3_tokens),
        },
        "folio_summaries": folio_summaries,
        "registers": register_records,
    }

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    print("=== ATTACK 115: PHARMACEUTICAL REGISTER ROW DECOMPOSITION ===")
    print(f"Pharm Folios: {len(pharm_fol_list)} | Total <%> @P Registers: {len(register_records)}")
    print(f"@Lc Vessel/Jar Labels: {len(all_lc)} (Compound-Resolved: {n_lc_resolved}/{len(all_lc)} = {100.0*n_lc_resolved/len(all_lc):.2f}%) | @Lf Plant-Part Labels: {len(all_lf)}")
    for d in lc_decompositions[:12]:
        print(f"  @Lc {d['loc']:12s} {d['surface']:12s} -> {d['decomposition_type']:18s} {d['constituent_stems']} (in_H={d['constituents_in_herbal']}, in_S={d['constituents_in_starred']})")
    print(f"Register Specialization (Herbal):  {distinct_top1_herbal_pairs}/{total_reg_pairs} ({summary['register_specialization']['distinct_top1_herbal_rate_pct']}%) same-folio register pairs cite DISTINCT #1 Herbal Monographs!")
    print(f"Register Specialization (Starred): {distinct_top1_starred_pairs}/{total_reg_pairs} ({summary['register_specialization']['distinct_top1_starred_rate_pct']}%) same-folio register pairs route to DISTINCT #1 Starred Recipes!")
    print(f"Row-Specific @Lf_k <-> @P_k Core/Stem Matches: {obs_row_core_matches} vs null {nr_mean:.2f} (lift={obs_row_core_matches/max(0.01,nr_mean):.2f}x, z={z_row_match:+.2f})")


if __name__ == "__main__":
    main()
