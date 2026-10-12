#!/usr/bin/env python3
"""
Attack 214 (Discovery 231): Completing 20/20 (100.0%) High-Resolution Coverage of Quire 13
Balneological (f78v, f79v, f80v), Trans-Leaf Callout-to-Opposite-Prose Propagation
(f75r->f75v, f79r->f79v, f80r->f80v, f81v->f81r), and 5-Bifolium Quire 13 Architecture.
"""

import json
import math
import random
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ZL_PATH = ROOT / "data" / "ZL3b-n.txt"
OUT_JSON = ROOT / "data" / "attack214_balneo_20page_completion_f78v_f79v_f80v_and_transleaf_echo.json"

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


def parse_balneo():
    lines = ZL_PATH.read_text(encoding="utf-8", errors="ignore").splitlines()
    balneo_folios = [f"f{n}{s}" for n in range(75, 85) for s in ("r", "v")]
    balneo_set = set(balneo_folios)

    prose_tokens = defaultdict(list)
    callout_tokens = defaultdict(list)
    paragraphs = defaultdict(list)
    cur_para = []
    cur_fol = None

    for raw in lines:
        if not raw.startswith("<f"):
            continue
        m = re.match(r"^<(f\d+[rv]\d*)\.([^>]+)>\s*(.*)$", raw)
        if not m:
            continue
        fol, loc, body = m.group(1), m.group(2), m.group(3)
        if fol not in balneo_set:
            continue
        ltype = loc.split(",")[-1] if "," in loc else ""
        body_clean = re.sub(r"\{[^}]*\}", "", body)
        toks = [clean_tok(x) for x in re.split(r"[.,\s]+", body_clean.replace("<->", " ")) if clean_tok(x)]
        if not toks:
            continue

        # In Quire 13, all L* (@/+/=/~/* Ln, Lt, L0) plus Pb (@Pb/+Pb) and f84v P1 are callout/margin loci
        is_callout = (len(ltype) >= 2 and (ltype[1:].startswith("L") or ltype[1:] == "Pb" or (fol == "f84v" and ltype[1:] == "P1")))
        if is_callout:
            callout_tokens[fol].extend(toks)
        else:
            prose_tokens[fol].extend(toks)
            if "<%>" in body:
                if cur_para and cur_fol:
                    paragraphs[cur_fol].append(cur_para)
                cur_para = list(toks)
                cur_fol = fol
            else:
                if cur_fol != fol and cur_para:
                    paragraphs[cur_fol].append(cur_para)
                    cur_para = []
                cur_fol = fol
                cur_para.extend(toks)
            if "<$>" in body and cur_para:
                paragraphs[fol].append(cur_para)
                cur_para = []

    if cur_para and cur_fol:
        paragraphs[cur_fol].append(cur_para)

    return balneo_folios, prose_tokens, callout_tokens, paragraphs


def main():
    balneo_folios, prose_tokens, callout_tokens, paragraphs = parse_balneo()
    all_balneo_prose_stems = {get_stem(w) for f in balneo_folios for w in prose_tokens[f]}

    # 1. Detailed profiles of the 3 newly rendered Balneological versos: f78v, f79v, f80v
    verso_profiles = {}
    for fol in ("f78v", "f79v", "f80v"):
        toks = prose_tokens[fol]
        stems = [get_stem(w) for w in toks]
        paras = paragraphs[fol]
        recto = fol[:-1] + "r"
        recto_toks = prose_tokens[recto] + callout_tokens[recto]
        recto_stems = {get_stem(w) for w in recto_toks}

        recto_cov = sum(1 for w in toks if get_stem(w) in recto_stems) / len(toks) if toks else 0.0
        qo_rate = sum(1 for w in toks if w.startswith("qo")) / len(toks) if toks else 0.0
        edy_rate = sum(1 for w in toks if w.endswith(("edy", "eey"))) / len(toks) if toks else 0.0
        ok_ot_rate = sum(1 for w in toks if w.startswith(("ok", "ot"))) / len(toks) if toks else 0.0
        ol_or_rate = sum(1 for w in toks if w.startswith(("ol", "or"))) / len(toks) if toks else 0.0

        verso_profiles[fol] = {
            "folio": fol,
            "prose_words": len(toks),
            "callout_words": len(callout_tokens[fol]),
            "paragraph_count": len(paras),
            "paragraph_lengths": [len(p) for p in paras],
            "paragraph_openers": [p[0] for p in paras if p],
            "unique_stems": len(set(stems)),
            "same_leaf_recto_stem_token_coverage": round(recto_cov, 4),
            "qo_rate": round(qo_rate, 4),
            "edy_eey_rate": round(edy_rate, 4),
            "ok_ot_rate": round(ok_ot_rate, 4),
            "ol_or_rate": round(ol_or_rate, 4),
            "top_words": Counter(toks).most_common(10),
        }

    # 2. Trans-Leaf Callout-to-Opposite-Prose Propagation across all 10 leaves (f75..f84)
    # Specifically check how callouts on one side of a leaf echo in:
    # (a) same-side prose, (b) opposite-side prose (same physical leaf!), and (c) combined leaf prose
    transleaf_reports = []
    total_callout_toks = 0
    total_same_side_echo = 0
    total_opp_side_echo = 0
    total_leaf_echo = 0

    # Also track leaves where ONE side has callouts and the OTHER side has 0 callouts:
    # f75 (f75r=38, f75v=0), f79 (f79r=11, f79v=0), f80 (f80r=11, f80v=0), f81 (f81r=0, f81v=2)
    asymmetric_callout_toks = 0
    asymmetric_opp_echo = 0

    for leaf_n in range(75, 85):
        for side, opp in (("r", "v"), ("v", "r")):
            fol = f"f{leaf_n}{side}"
            opp_fol = f"f{leaf_n}{opp}"
            c_toks = callout_tokens[fol]
            if not c_toks:
                continue
            same_stems = {get_stem(w) for w in prose_tokens[fol]}
            opp_stems = {get_stem(w) for w in prose_tokens[opp_fol]}
            leaf_stems = same_stems | opp_stems

            same_hits = [w for w in c_toks if get_stem(w) in same_stems]
            opp_hits = [w for w in c_toks if get_stem(w) in opp_stems]
            leaf_hits = [w for w in c_toks if get_stem(w) in leaf_stems]
            opp_exact = [w for w in c_toks if w in set(prose_tokens[opp_fol])]

            total_callout_toks += len(c_toks)
            total_same_side_echo += len(same_hits)
            total_opp_side_echo += len(opp_hits)
            total_leaf_echo += len(leaf_hits)

            is_asym = (len(callout_tokens[opp_fol]) == 0)
            if is_asym:
                asymmetric_callout_toks += len(c_toks)
                asymmetric_opp_echo += len(opp_hits)

            transleaf_reports.append({
                "callout_folio": fol,
                "opposite_folio": opp_fol,
                "opposite_is_unlabeled": is_asym,
                "callout_tokens": len(c_toks),
                "callout_words": c_toks,
                "same_side_stem_hits": len(same_hits),
                "same_side_stem_rate": round(len(same_hits) / len(c_toks), 4),
                "opposite_side_stem_hits": len(opp_hits),
                "opposite_side_stem_rate": round(len(opp_hits) / len(c_toks), 4),
                "opposite_side_exact_hits": len(opp_exact),
                "opposite_side_matching_words": opp_hits,
                "combined_leaf_stem_hits": len(leaf_hits),
                "combined_leaf_stem_rate": round(len(leaf_hits) / len(c_toks), 4),
            })

    # 3. Complete 20-Page Quire 13 Census & 5-Bifolium Conjugate Architecture
    # Bifolia of Quire 13: (f75,f84), (f76,f83), (f77,f82), (f78,f81), (f79,f80)
    bifolia_q13 = [(75, 84), (76, 83), (77, 82), (78, 81), (79, 80)]
    q13_bifolia_reports = []
    for i, (l1, l2) in enumerate(bifolia_q13, 1):
        t1 = prose_tokens[f"f{l1}r"] + callout_tokens[f"f{l1}r"] + prose_tokens[f"f{l1}v"] + callout_tokens[f"f{l1}v"]
        t2 = prose_tokens[f"f{l2}r"] + callout_tokens[f"f{l2}r"] + prose_tokens[f"f{l2}v"] + callout_tokens[f"f{l2}v"]
        s1 = {get_stem(w) for w in t1}
        s2 = {get_stem(w) for w in t2}
        wj = len(set(t1) & set(t2)) / len(set(t1) | set(t2))
        sj = len(s1 & s2) / len(s1 | s2)
        cov_1_in_2 = sum(1 for w in t1 if get_stem(w) in s2) / len(t1)
        q13_bifolia_reports.append({
            "bifolium": i,
            "pair": f"f{l1} <-> f{l2}",
            "left_words": len(t1),
            "right_words": len(t2),
            "word_jaccard": round(wj, 4),
            "stem_jaccard": round(sj, 4),
            "token_stem_coverage_left_in_right": round(cov_1_in_2, 4),
        })

    # Center opening f79v <-> f80r (facing pages across the sewing fold of Quire 13!)
    f79v_stems = {get_stem(w) for w in prose_tokens["f79v"]}
    f80r_callouts = callout_tokens["f80r"]
    f80r_callouts_in_f79v = [w for w in f80r_callouts if get_stem(w) in f79v_stems]
    f80r_stems = {get_stem(w) for w in prose_tokens["f80r"] + callout_tokens["f80r"]}
    f79v_in_f80r_cov = sum(1 for w in prose_tokens["f79v"] if get_stem(w) in f80r_stems) / len(prose_tokens["f79v"])

    out = {
        "attack": 214,
        "discovery": 231,
        "title": "Completing 20/20 (100.0%) High-Resolution Visual Coverage of Quire 13 Balneological (f78v, f79v, f80v) & Trans-Leaf Callout Propagation",
        "summary": {
            "quire13_total_pages": 20,
            "quire13_rendered_pages": 20,
            "quire13_visual_coverage_rate": 1.0,
            "total_callout_tokens": total_callout_toks,
            "same_side_prose_stem_echo_count": total_same_side_echo,
            "same_side_prose_stem_echo_rate": round(total_same_side_echo / total_callout_toks, 4),
            "opposite_side_prose_stem_echo_count": total_opp_side_echo,
            "opposite_side_prose_stem_echo_rate": round(total_opp_side_echo / total_callout_toks, 4),
            "combined_leaf_prose_stem_echo_count": total_leaf_echo,
            "combined_leaf_prose_stem_echo_rate": round(total_leaf_echo / total_callout_toks, 4),
            "asymmetric_labeled_to_unlabeled_tokens": asymmetric_callout_toks,
            "asymmetric_labeled_to_unlabeled_echo_count": asymmetric_opp_echo,
            "asymmetric_labeled_to_unlabeled_echo_rate": round(asymmetric_opp_echo / asymmetric_callout_toks, 4),
            "center_opening_f80r_callouts_in_facing_f79v": len(f80r_callouts_in_f79v),
            "center_opening_f80r_callouts_in_facing_f79v_rate": round(len(f80r_callouts_in_f79v) / len(f80r_callouts), 4),
            "center_opening_f79v_token_coverage_in_f80r": round(f79v_in_f80r_cov, 4),
        },
        "newly_rendered_verso_profiles": verso_profiles,
        "transleaf_callout_reports": transleaf_reports,
        "quire13_bifolia_reports": q13_bifolia_reports,
    }

    OUT_JSON.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"Saved {OUT_JSON}")
    print("Summary:", json.dumps(out["summary"], indent=2))


if __name__ == "__main__":
    main()
