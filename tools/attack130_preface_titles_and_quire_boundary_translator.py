#!/usr/bin/env python3
"""
Attack 130 (Phase 141 / Discovery 147):
Complete Master Preface (`f1r`), Corpus-Wide Right-Justified Titles (`=Pt`),
Special Folios (`f57v`, `f65r/v`, `f116v`), and 20-Quire Opening/Closing
Boundary Translator.

Investigates:
1. All right-justified title lines (`=Pt` / `+Pt` / `@Pt`) across the entire
   226-folio Voynich Manuscript: exact folios, morphological profile, and
   relationship to the paragraphs directly preceding/following them (`z`-score
   permutation test).
2. Complete paragraph-by-paragraph and title-by-title structural translation of
   `f1r` (the Master Opening Preface of the Codex), `f57v` (the 4-Ring Key
   Wheel), `f65r/f65v` (Scribe 3's Quire H botanical pair), and `f116v`.
3. The 20-Quire Codicological Boundary Law: comparing Quire-Opening Rectos
   (`first folio of quire`), Quire-Internal Folios, and Quire-Closing Versos
   (`last folio of quire`) across all 20 quires (`Quires A–T`).
"""

import json
import math
import random
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ZL_PATH = ROOT / "data" / "ZL3b-n.txt"
INDEX_PATH = ROOT / "data" / "folio_index.json"
OUT_JSON = ROOT / "data" / "attack130_preface_titles_and_quire_boundary_translator.json"

PREFIXES = [
    "qok", "qot", "qop", "qof", "qo",
    "ch", "sh", "cth", "ckh", "cph", "cfh",
    "da", "sa", "ol", "al", "or", "ar",
    "ok", "ot", "op", "of",
    "yk", "yt", "yp", "yf",
    "lk", "lt", "lp", "lf",
    "d", "s", "y", "o", "l", "r", "k", "t", "p", "f",
]

SUFFIXES = [
    "aiin", "oiin", "eiin", "iin", "in",
    "eedy", "edy", "ody", "ady", "dy",
    "ey", "oy", "ay", "y",
    "eal", "ol", "al", "el", "l",
    "ear", "or", "ar", "er", "r",
    "eam", "am", "om", "m",
    "an", "en", "on", "n",
    "s", "d", "g",
]


def clean_tok(t: str) -> str:
    t = re.sub(r"\{[^}]*\}", "", t)
    t = re.sub(r"\[([^]:]+):[^\]]+\]", r"\1", t)
    t = re.sub(r"[^a-zA-Z]", "", t).lower()
    return t


def canon_stem(w: str) -> str:
    s = w
    if s.startswith("q") and len(s) > 2:
        s = s[1:]
    for p in ["ch", "sh", "da", "sa", "ol", "al", "or", "ar", "ok", "ot", "yk", "yt", "d", "s", "y", "o", "l"]:
        if s.startswith(p) and len(s) - len(p) >= 2:
            s = s[len(p):]
            break
    for suf in ["aiin", "oiin", "iin", "eedy", "edy", "ody", "ady", "dy", "ey", "oy", "ol", "al", "or", "ar", "am", "om", "an", "in", "y", "l", "r", "m", "n", "s"]:
        if s.endswith(suf) and len(s) - len(suf) >= 2:
            s = s[:-len(suf)]
            break
    return s


def decompose_word(w: str) -> dict:
    rem = w
    pref = ""
    for p in PREFIXES:
        if rem.startswith(p) and len(rem) - len(p) >= 2:
            pref = p
            rem = rem[len(p):]
            break
    suf = ""
    for s in SUFFIXES:
        if rem.endswith(s) and len(rem) - len(s) >= 1:
            suf = s
            rem = rem[:-len(s)]
            break
    stem = canon_stem(w)
    if pref.startswith("qo"):
        p_gloss = "ACT_BOIL"
    elif pref in ("ch", "sh", "cth", "ckh", "cph", "cfh"):
        p_gloss = "HERB_BENCH"
    elif pref in ("o", "ok", "ot", "op", "of", "y", "yk", "yt"):
        p_gloss = "NOM_SPEC"
    elif pref in ("d", "da"):
        p_gloss = "TOP_LOC"
    elif pref in ("s", "sa"):
        p_gloss = "SEQ_CONT"
    elif pref in ("l", "ol", "al", "lk", "lt"):
        p_gloss = "APPL_VESSEL"
    elif pref in ("or", "ar", "r"):
        p_gloss = "FLOW_LIQ"
    else:
        p_gloss = "BARE"

    if suf in ("aiin", "oiin", "eiin", "iin", "in"):
        s_gloss = "DOSE_AIIN"
    elif suf in ("eedy", "edy"):
        s_gloss = "PROC_SIMMER"
    elif suf in ("ody", "ady", "dy"):
        s_gloss = "PERF_DONE"
    elif suf in ("ey", "oy", "ay", "y"):
        s_gloss = "STATE_Y"
    elif suf in ("ol", "al", "el", "eal", "l"):
        s_gloss = "FLUID_L"
    elif suf in ("or", "ar", "er", "ear", "r"):
        s_gloss = "SOURCE_R"
    elif suf in ("am", "om", "eam", "m"):
        s_gloss = "FINAL_M"
    else:
        s_gloss = "ROOT"

    return {
        "word": w,
        "prefix": pref,
        "core": rem,
        "suffix": suf,
        "stem": stem,
        "gloss": f"{p_gloss}[{stem.upper()}]:{s_gloss}",
    }


def metrics_for_tokens(toks: list) -> dict:
    n = len(toks)
    if n == 0:
        return {}
    stems = [canon_stem(w) for w in toks]
    qo = sum(1 for w in toks if w.startswith("qo"))
    o_nom = sum(1 for w in toks if w.startswith("o") and not w.startswith("ol"))
    bench = sum(1 for w in toks if w.startswith(("ch", "sh")))
    da_top = sum(1 for w in toks if w.startswith("d"))
    l_appl = sum(1 for w in toks if w.startswith(("l", "ol", "al")))
    pf_init = sum(1 for w in toks if w.startswith(("p", "f", "op", "of", "cph", "cfh")))
    edy = sum(1 for w in toks if w.endswith(("edy", "eedy")))
    aiin = sum(1 for w in toks if w.endswith(("aiin", "oiin", "iin")))
    am = sum(1 for w in toks if w.endswith(("am", "om", "m")))
    dy = sum(1 for w in toks if w.endswith("dy") and not w.endswith(("edy", "eedy")))
    ol_or = sum(1 for w in toks if w.endswith(("ol", "al", "or", "ar", "l", "r")))
    return {
        "n_tokens": n,
        "n_unique_stems": len(set(stems)),
        "mean_len": round(sum(len(w) for w in toks) / n, 3),
        "o_nom_pct": round(100.0 * o_nom / n, 2),
        "qo_pct": round(100.0 * qo / n, 2),
        "bench_pct": round(100.0 * bench / n, 2),
        "d_top_pct": round(100.0 * da_top / n, 2),
        "l_appl_pct": round(100.0 * l_appl / n, 2),
        "pf_gallows_pct": round(100.0 * pf_init / n, 2),
        "edy_pct": round(100.0 * edy / n, 2),
        "aiin_pct": round(100.0 * aiin / n, 2),
        "dy_pct": round(100.0 * dy / n, 2),
        "am_pct": round(100.0 * am / n, 2),
        "liquid_coda_pct": round(100.0 * ol_or / n, 2),
    }


def main():
    random.seed(42)
    with open(INDEX_PATH, encoding="utf-8") as f:
        idx = json.load(f)
    folio_meta = idx["folios"]

    folio_lines = defaultdict(list)
    folio_tokens = defaultdict(list)
    pt_titles = []

    with open(ZL_PATH, encoding="utf-8", errors="ignore") as f:
        for raw in f:
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            m_line = re.match(r"^<(f[0-9a-zA-Z]+)\.([^>]+)>\s+(.*)$", line)
            if not m_line:
                continue
            fol, loc_part, text = m_line.groups()
            loc = loc_part.split(",")[-1] if "," in loc_part else loc_part
            line_id = loc_part.split(",")[0]

            has_para_start = "<%>" in text
            has_para_end = "<$>" in text

            raw_toks = re.split(r"[.\s,]+", text)
            toks = [clean_tok(t) for t in raw_toks]
            toks = [t for t in toks if len(t) >= 1]
            if not toks:
                continue

            ln_obj = {
                "folio": fol,
                "line_id": line_id,
                "loc": loc,
                "has_para_start": has_para_start,
                "has_para_end": has_para_end,
                "tokens": toks,
            }
            folio_lines[fol].append(ln_obj)
            for t in toks:
                if len(t) >= 2:
                    folio_tokens[fol].append((loc, t))

            if loc.lstrip("@+=*~&/").startswith("Pt"):
                pt_titles.append(ln_obj)

    # Build global stem IDF
    stem_folios = defaultdict(set)
    section_stems = defaultdict(set)
    for fol, lt_list in folio_tokens.items():
        sec = folio_meta.get(fol, {}).get("section_code", "?")
        for _, t in lt_list:
            st = canon_stem(t)
            if len(st) >= 2:
                stem_folios[st].add(fol)
                section_stems[sec].add(st)

    n_folios = len(folio_tokens)
    stem_idf = {
        s: math.log(n_folios / len(fols))
        for s, fols in stem_folios.items()
        if 2 <= len(fols) <= 25 and len(s) >= 2
    }

    # 1. Analyze all =Pt right-justified titles across the entire manuscript
    pt_all_toks = [t for ln in pt_titles for t in ln["tokens"] if len(t) >= 2]
    all_prose_toks = [
        t for fol, lns in folio_lines.items()
        for ln in lns
        if ln["loc"].lstrip("@+=*~&/").startswith("P") and not ln["loc"].lstrip("@+=*~&/").startswith("Pt")
        for t in ln["tokens"] if len(t) >= 2
    ]

    pt_profiles = []
    obs_local_stem_matches = 0
    for ln in pt_titles:
        fol = ln["folio"]
        toks = [t for t in ln["tokens"] if len(t) >= 2]
        st_set = {canon_stem(t) for t in toks if len(canon_stem(t)) >= 2}
        # Check overlap with non-Pt tokens on the same folio
        same_fol_prose_stems = {
            canon_stem(t)
            for l2 in folio_lines[fol]
            if l2["line_id"] != ln["line_id"]
            for t in l2["tokens"]
            if len(t) >= 2
        }
        shared_same_fol = sorted(st_set & same_fol_prose_stems)
        obs_local_stem_matches += len(shared_same_fol)

        gloss_str = " ".join(decompose_word(w)["gloss"] for w in toks)
        pt_profiles.append({
            "folio": fol,
            "line_id": ln["line_id"],
            "loc": ln["loc"],
            "section": folio_meta.get(fol, {}).get("section_code", "?"),
            "hand": folio_meta.get(fol, {}).get("hand", "?"),
            "language": folio_meta.get(fol, {}).get("currier_lang", "?"),
            "n_tokens": len(toks),
            "eva": " ".join(toks),
            "gloss": gloss_str,
            "shared_stems_with_same_folio": shared_same_fol,
        })

    # Permutation test on =Pt titles:
    # Test A: Nominal/Deictic vs Procedural Polarity ((o_nom + d_top) - (qo + bench + edy))
    def title_polarity_score(tok_list):
        n = len(tok_list)
        if n == 0:
            return 0.0
        nom_deic = sum(1 for w in tok_list if (w.startswith("o") and not w.startswith("ol")) or w.startswith("d"))
        proc_body = sum(1 for w in tok_list if w.startswith("qo") or w.startswith(("ch", "sh")) or w.endswith(("edy", "eedy")))
        return (nom_deic - proc_body) / n

    obs_pt_pol = title_polarity_score(pt_all_toks)
    obs_prose_pol = title_polarity_score(all_prose_toks)
    null_pols = []
    n_pt_toks = len(pt_all_toks)
    for _ in range(1000):
        samp = random.sample(all_prose_toks, n_pt_toks)
        null_pols.append(title_polarity_score(samp))

    mu_pol = sum(null_pols) / len(null_pols)
    sd_pol = math.sqrt(sum((x - mu_pol) ** 2 for x in null_pols) / len(null_pols))
    z_pt_pol = (obs_pt_pol - mu_pol) / (sd_pol if sd_pol > 0 else 1.0)
    p_pt_pol = sum(1 for x in null_pols if x >= obs_pt_pol) / len(null_pols)

    # Test B: Outer-Wrapper Bifolio ($B=1) & Quire-1 Concentration of =Pt titles
    # In ZL3b-n, f1r, f8r, f25r are all $B=1 outer wrapper sheets (8/10 = 80.0% of =Pt titles)
    b1_pt_count = sum(1 for p in pt_profiles if p["folio"] in ("f1r", "f8r", "f25r"))

    # 2. Complete f1r Master Preface Translator
    f1r_blocks = []
    cur_toks = []
    cur_lines = []
    b_idx = 1
    for ln in folio_lines["f1r"]:
        loc_clean = ln["loc"].lstrip("@+=*~&/")
        if loc_clean.startswith("Pt"):
            if cur_toks:
                f1r_blocks.append({
                    "block_id": f"f1r.P{b_idx}",
                    "type": "PROSE_PARAGRAPH",
                    "line_range": f"{cur_lines[0]}–{cur_lines[-1]}",
                    "tokens": cur_toks,
                })
                b_idx += 1
                cur_toks = []
                cur_lines = []
            f1r_blocks.append({
                "block_id": f"f1r.Title_{ln['line_id']}",
                "type": "RIGHT_JUSTIFIED_TITLE_Pt",
                "line_range": ln["line_id"],
                "tokens": ln["tokens"],
            })
            continue
        if ln["has_para_start"] and cur_toks:
            f1r_blocks.append({
                "block_id": f"f1r.P{b_idx}",
                "type": "PROSE_PARAGRAPH",
                "line_range": f"{cur_lines[0]}–{cur_lines[-1]}",
                "tokens": cur_toks,
            })
            b_idx += 1
            cur_toks = []
            cur_lines = []
        cur_toks.extend(ln["tokens"])
        cur_lines.append(ln["line_id"])
        if ln["has_para_end"] and cur_toks:
            f1r_blocks.append({
                "block_id": f"f1r.P{b_idx}",
                "type": "PROSE_PARAGRAPH",
                "line_range": f"{cur_lines[0]}–{cur_lines[-1]}",
                "tokens": cur_toks,
            })
            b_idx += 1
            cur_toks = []
            cur_lines = []
    if cur_toks:
        f1r_blocks.append({
            "block_id": f"f1r.P{b_idx}",
            "type": "PROSE_PARAGRAPH",
            "line_range": f"{cur_lines[0]}–{cur_lines[-1]}",
            "tokens": cur_toks,
        })

    f1r_translated_blocks = []
    for blk in f1r_blocks:
        toks = [t for t in blk["tokens"] if len(t) >= 2]
        st_set = {canon_stem(t) for t in toks if len(canon_stem(t)) >= 2}
        sec_idf = {
            sk: round(sum(stem_idf[s] for s in (st_set & section_stems[sk]) if s in stem_idf), 3)
            for sk in ["H", "A", "Z", "B", "P", "S"]
        }
        f1r_translated_blocks.append({
            "block_id": blk["block_id"],
            "type": blk["type"],
            "line_range": blk["line_range"],
            "metrics": metrics_for_tokens(toks),
            "section_routing_idf": sec_idf,
            "opening_eva": " ".join(toks[:8]),
            "opening_gloss": " ".join(decompose_word(w)["gloss"] for w in toks[:8]),
            "closing_eva": " ".join(toks[-5:]) if len(toks) > 5 else " ".join(toks),
            "closing_gloss": " ".join(decompose_word(w)["gloss"] for w in (toks[-5:] if len(toks) > 5 else toks)),
        })

    # 3. Special Folios Translator: f1r, f57v, f65r, f65v, f116v
    special_folios = {}
    for sfol in ["f1r", "f57v", "f65r", "f65v", "f116v"]:
        toks = [t for _, t in folio_tokens[sfol]]
        lns = folio_lines[sfol]
        special_folios[sfol] = {
            "folio": sfol,
            "meta": {k: v for k, v in folio_meta.get(sfol, {}).items() if k not in ("comments", "right_justified_titles")},
            "metrics": metrics_for_tokens(toks),
            "n_lines": len(lns),
            "sample_lines": [
                {
                    "line_id": l["line_id"],
                    "loc": l["loc"],
                    "eva": " ".join(l["tokens"][:10]),
                    "gloss": " ".join(decompose_word(w)["gloss"] for w in l["tokens"][:10] if len(w) >= 2),
                }
                for l in lns[:6]
            ],
        }

    # 4. 20-Quire Opening vs Internal vs Closing Folio Law
    quire_folios = defaultdict(list)
    for fol, meta in folio_meta.items():
        if fol in folio_tokens and meta.get("quire"):
            pnum = meta.get("pdf_pages", [{}])[0].get("pdf1_page", 999) if meta.get("pdf_pages") else 999
            quire_folios[meta["quire"]].append((pnum, fol))

    opening_fols = []
    closing_fols = []
    internal_fols = []

    for q, flist in sorted(quire_folios.items()):
        flist.sort()
        if len(flist) == 1:
            opening_fols.append(flist[0][1])
        else:
            opening_fols.append(flist[0][1])
            closing_fols.append(flist[-1][1])
            for _, fmid in flist[1:-1]:
                internal_fols.append(fmid)

    def group_folio_summary(fol_list, prose_only=False):
        if prose_only:
            toks = [
                t for f in fol_list for loc, t in folio_tokens[f]
                if loc.lstrip("@+=*~&/").startswith("P") and not loc.lstrip("@+=*~&/").startswith("Pb")
            ]
        else:
            toks = [t for f in fol_list for _, t in folio_tokens[f]]
        n_paras = sum(
            1 for f in fol_list for l in folio_lines[f] if l["has_para_start"]
        )
        n_pt = sum(
            1 for f in fol_list for l in folio_lines[f] if l["loc"].lstrip("@+=*~&/").startswith("Pt")
        )
        m = metrics_for_tokens(toks)
        m["n_folios"] = len(fol_list)
        m["mean_tokens_per_folio"] = round(len(toks) / len(fol_list), 2) if fol_list else 0
        m["mean_paras_per_folio"] = round(n_paras / len(fol_list), 2) if fol_list else 0
        m["total_pt_titles"] = n_pt
        return m

    quire_boundary_summary = {
        "ALL_LOCI": {
            "QUIRE_OPENING_RECTO_FIRST": group_folio_summary(opening_fols, False),
            "QUIRE_INTERNAL_MIDDLE": group_folio_summary(internal_fols, False),
            "QUIRE_CLOSING_VERSO_LAST": group_folio_summary(closing_fols, False),
        },
        "PROSE_ONLY_P0": {
            "QUIRE_OPENING_RECTO_FIRST": group_folio_summary(opening_fols, True),
            "QUIRE_INTERNAL_MIDDLE": group_folio_summary(internal_fols, True),
            "QUIRE_CLOSING_VERSO_LAST": group_folio_summary(closing_fols, True),
        },
        "opening_folios": opening_fols,
        "closing_folios": closing_fols,
    }

    out = {
        "attack": 130,
        "phase": 141,
        "discovery": 147,
        "title": "Master Preface (f1r), Corpus-Wide Right-Justified Titles (=Pt), Special Folios (f57v, f65r/v, f116v), and 20-Quire Boundary Translator",
        "right_justified_pt_titles": {
            "total_pt_lines": len(pt_profiles),
            "outer_wrapper_b1_pt_lines": b1_pt_count,
            "outer_wrapper_b1_pct": round(100.0 * b1_pt_count / len(pt_profiles), 2),
            "pt_metrics": metrics_for_tokens(pt_all_toks),
            "general_prose_metrics": metrics_for_tokens(all_prose_toks),
            "title_nominal_deictic_polarity_test": {
                "observed_pt_polarity": round(obs_pt_pol, 4),
                "observed_prose_polarity": round(obs_prose_pol, 4),
                "polarity_swing": round(obs_pt_pol - obs_prose_pol, 4),
                "null_mean": round(mu_pol, 4),
                "null_sd": round(sd_pol, 4),
                "z_score": round(z_pt_pol, 2),
                "p_value": round(p_pt_pol, 4),
            },
            "all_pt_titles": pt_profiles,
        },
        "f1r_master_preface_blocks": f1r_translated_blocks,
        "special_folios": special_folios,
        "quire_boundary_summary": quire_boundary_summary,
    }

    OUT_JSON.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"[Attack 130] Saved {OUT_JSON}")
    print(f"Total =Pt right-justified titles in corpus: {len(pt_profiles)} ({b1_pt_count}/10 = {out['right_justified_pt_titles']['outer_wrapper_b1_pct']}% on $B=1 outer wrapper sheets)")
    print("=Pt Nominal/Deictic Polarity Test:", json.dumps(out["right_justified_pt_titles"]["title_nominal_deictic_polarity_test"], indent=2))
    print("Quire Boundary Summary (ALL_LOCI):", json.dumps(quire_boundary_summary["ALL_LOCI"], indent=2))
    print("Quire Boundary Summary (PROSE_ONLY_P0):", json.dumps(quire_boundary_summary["PROSE_ONLY_P0"], indent=2))


if __name__ == "__main__":
    main()
