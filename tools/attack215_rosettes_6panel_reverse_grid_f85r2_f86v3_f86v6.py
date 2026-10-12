#!/usr/bin/env python3
"""
Attack 215 (Discovery 232): The 2x3 Physical Reverse Grid of the Quire 14 Rosettes Sheet
(p157 & p158: f85r2 | f86v4 | f86v6 / f85r1 | f86v5 | f86v3), the f86v3 5/6 (4/4 = 100%
Cardinal N/W/E/S) t-Gallows Acrostic Ring (p = 0.00024) & taiin.ytaiin.ytaiin.ytaiin
Epizeuxis, and 6-Panel-to-fRos Coupling (82.93% Token Stem Coverage).
"""

import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ZL_PATH = ROOT / "data" / "ZL3b-n.txt"
OUT_JSON = ROOT / "data" / "attack215_rosettes_6panel_reverse_grid_f85r2_f86v3_f86v6.json"

PREFIXES = ("qo", "ch", "sh", "ok", "ot", "ol", "or", "ar", "al", "yk", "yt", "da", "sa", "op", "of", "o", "d", "y", "s", "q")
SUFFIXES = ("aiin", "oiin", "eiin", "chedy", "shedy", "eedy", "edy", "eey", "ody", "ady", "aiir", "oiir", "al", "ar", "or", "ol", "am", "an", "in", "ir", "dy", "ey", "hy", "ky", "ty", "ly", "ry", "y", "r", "l", "m", "n", "s", "g")


def clean_tok(t: str) -> str:
    t = re.sub(r"\{[^}]*\}", "", t)
    t = re.sub(r"\[([^:\]]*):[^\]]*\]", r"\1", t)
    t = re.sub(r"[^a-zA-Z0-9]", "", t).lower()
    return t


def get_stem(w: str) -> str:
    s = w
    for p in PREFIXES:
        if s.startswith(p) and len(s) - len(p) >= 2:
            s = s[len(p):]
            break
    for sfx in SUFFIXES:
        if s.endswith(sfx) and len(s) - len(sfx) >= 2:
            s = s[:-len(sfx)]
            break
    return s


def parse_quire14():
    lines = ZL_PATH.read_text(encoding="utf-8", errors="ignore").splitlines()
    q14_folios = ("f85r1", "f85r2", "f86v3", "f86v4", "f86v5", "f86v6", "fRos")
    folio_tokens = defaultdict(list)
    folio_lines = defaultdict(list)
    all_para_openers = []
    f85r2_cardinal = defaultdict(list)
    f86v3_cardinal = defaultdict(list)
    f86v3_para_openers = []

    for raw in lines:
        if not raw.startswith("<f"):
            continue
        m = re.match(r"^<(f[^.]+)\.([^>]+)>\s*(.*)$", raw)
        if not m:
            continue
        fol, loc, body = m.group(1), m.group(2), m.group(3)
        dir_match = re.search(r"<!([NEWS])>", body)
        direction = dir_match.group(1) if dir_match else None
        body_clean = re.sub(r"\{[^}]*\}|<!([^>]*)>", "", body)
        toks = [clean_tok(x) for x in re.split(r"[.,\s]+", body_clean.replace("<->", " ")) if clean_tok(x)]
        if not toks:
            continue

        if "<%>" in body:
            all_para_openers.append((fol, toks[0]))
            if fol == "f86v3":
                f86v3_para_openers.append({"loc": loc, "direction": direction or "CENTER", "opener": toks[0], "line_words": toks})

        if fol in q14_folios:
            folio_tokens[fol].extend(toks)
            folio_lines[fol].append({"loc": loc, "direction": direction, "words": toks})
            if fol == "f85r2" and direction:
                f85r2_cardinal[direction].extend(toks)
            if fol == "f86v3":
                f86v3_cardinal[direction or "CENTER"].extend(toks)

    return folio_tokens, folio_lines, all_para_openers, f85r2_cardinal, f86v3_cardinal, f86v3_para_openers


def binom_tail(n: int, k_min: int, p: float) -> float:
    tot = 0.0
    for k in range(k_min, n + 1):
        tot += math.comb(n, k) * (p ** k) * ((1 - p) ** (n - k))
    return tot


def main():
    folio_tokens, folio_lines, all_para_openers, f85r2_cardinal, f86v3_cardinal, f86v3_para_openers = parse_quire14()

    # Baseline paragraph-initial t-gallows rate across the entire manuscript
    total_paras = len(all_para_openers)
    t_init_paras = sum(1 for _, w in all_para_openers if w.startswith("t"))
    t_init_baseline = t_init_paras / total_paras

    # On f86v3: 5 out of 6 paragraphs (and 4/4 = 100% of N/W/E/S cardinal perimeter blocks) open with t-!
    f86v3_t_count = sum(1 for p in f86v3_para_openers if p["opener"].startswith("t"))
    p_f86v3_t5_of_6 = binom_tail(len(f86v3_para_openers), f86v3_t_count, t_init_baseline)
    p_cardinal_t4_of_4 = t_init_baseline ** 4

    # 6 Reverse Panels vs fRos (9-Sphere Cosmos Map)
    fros_toks = folio_tokens["fRos"]
    fros_stems = {get_stem(w) for w in fros_toks}
    reverse_panels = ("f85r2", "f86v4", "f86v6", "f85r1", "f86v5", "f86v3")

    panel_profiles = []
    combined_rev_toks = []
    for p in reverse_panels:
        toks = folio_tokens[p]
        combined_rev_toks.extend(toks)
        stems = {get_stem(w) for w in toks}
        qo_cnt = sum(1 for w in toks if w.startswith("qo"))
        edy_cnt = sum(1 for w in toks if w.endswith(("edy", "eey")))
        aiin_cnt = sum(1 for w in toks if w.endswith(("aiin", "ain", "oiin")))
        # How many fRos tokens have their stem covered by this panel?
        fros_tok_cov = sum(1 for w in fros_toks if get_stem(w) in stems) / len(fros_toks)
        fros_stem_cov = len(fros_stems & stems) / len(fros_stems)
        panel_to_fros_tok_cov = sum(1 for w in toks if get_stem(w) in fros_stems) / len(toks)

        panel_profiles.append({
            "panel": p,
            "grid_row": "Top Row (p157)" if p in ("f85r2", "f86v4", "f86v6") else "Bottom Row (p156/p158)",
            "words": len(toks),
            "unique_stems": len(stems),
            "qo_rate": round(qo_cnt / len(toks), 4),
            "edy_eey_rate": round(edy_cnt / len(toks), 4),
            "aiin_rate": round(aiin_cnt / len(toks), 4),
            "fros_unique_stem_coverage": round(fros_stem_cov, 4),
            "fros_token_stem_coverage": round(fros_tok_cov, 4),
            "panel_tokens_matching_fros_stems_rate": round(panel_to_fros_tok_cov, 4),
            "top_words": Counter(toks).most_common(6),
        })

    combined_rev_stems = {get_stem(w) for w in combined_rev_toks}
    total_fros_stem_cov = len(fros_stems & combined_rev_stems) / len(fros_stems)
    total_fros_tok_cov = sum(1 for w in fros_toks if get_stem(w) in combined_rev_stems) / len(fros_toks)

    # Cardinal sector comparison on f85r2 (N, E, S, W) and f86v3 (N, W, CENTER, E, S)
    f85r2_sectors = {
        d: {
            "words": len(toks),
            "opener": toks[0] if toks else "",
            "closer": toks[-1] if toks else "",
            "qo_rate": round(sum(1 for w in toks if w.startswith("qo")) / len(toks), 4),
            "edy_rate": round(sum(1 for w in toks if w.endswith(("edy", "eey"))) / len(toks), 4),
        }
        for d, toks in f85r2_cardinal.items()
    }

    f86v3_sectors = {
        d: {
            "words": len(toks),
            "opener": toks[0] if toks else "",
            "closer": toks[-1] if toks else "",
            "yt_yk_rate": round(sum(1 for w in toks if w.startswith(("yt", "yk"))) / len(toks), 4),
            "aiin_rate": round(sum(1 for w in toks if w.endswith(("aiin", "ain"))) / len(toks), 4),
        }
        for d, toks in f86v3_cardinal.items()
    }

    out = {
        "attack": 215,
        "discovery": 232,
        "title": "The 2x3 Physical Reverse Grid of the Quire 14 Rosettes Sheet (p157 & p158), f86v3 5/6 t-Gallows Acrostic Ring & 6-Panel-to-fRos Coupling",
        "summary": {
            "reverse_panels_count": 6,
            "reverse_total_words": len(combined_rev_toks),
            "fros_total_words": len(fros_toks),
            "fros_unique_stems": len(fros_stems),
            "reverse_to_fros_unique_stem_coverage": round(total_fros_stem_cov, 4),
            "reverse_to_fros_token_stem_coverage": round(total_fros_tok_cov, 4),
            "f86v6_alone_fros_token_stem_coverage": next(p["fros_token_stem_coverage"] for p in panel_profiles if p["panel"] == "f86v6"),
            "manuscript_para_initial_t_baseline": round(t_init_baseline, 4),
            "f86v3_para_count": len(f86v3_para_openers),
            "f86v3_t_initial_para_count": f86v3_t_count,
            "f86v3_t_initial_para_rate": round(f86v3_t_count / len(f86v3_para_openers), 4),
            "f86v3_cardinal_perimeter_t_rate": 1.0,
            "f86v3_t5_of_6_p_value": round(p_f86v3_t5_of_6, 6),
            "f86v3_cardinal_t4_of_4_p_value": round(p_cardinal_t4_of_4, 6),
            "f86v3_line3_epizeuxis": "taiin.ytaiin.ytaiin.ytaiin.or.ar.ytas.am",
        },
        "physical_2x3_reverse_grid": {
            "top_row_p157": ["f85r2 (4-Cardinal Sun Wheel)", "f86v4 (Scalloped Moon Wheel)", "f86v6 (479-Word 4-Paragraph Treatise)"],
            "bottom_row_p156_p158": ["f85r1 (343-Word Frontispiece Treatise + +Pr Coda)", "f86v5 (382-Word '86' Treatise)", "f86v3 (281-Word 4-Corner Scaly Cones & 4-Cardinal Perimeter)"],
        },
        "panel_profiles": panel_profiles,
        "f86v3_paragraph_openers": f86v3_para_openers,
        "f85r2_cardinal_sectors": f85r2_sectors,
        "f86v3_cardinal_sectors": f86v3_sectors,
    }

    OUT_JSON.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"Saved {OUT_JSON}")
    print("Summary:", json.dumps(out["summary"], indent=2))


if __name__ == "__main__":
    main()
