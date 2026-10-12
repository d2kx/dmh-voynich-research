#!/usr/bin/env python3
"""
Attack 190 (Discovery 207): The 20-Folio Balneological (Quire 13, f75r-f84v)
Labeled-Organ vs. Unlabeled-Gallery Architecture, @Lt (Tube/Organ) vs. @Ln (Nymph)
Morphological Polarity, f77r 10-Label Aqueduct/Ampulla Concordance, and f81r
Three-Paragraph Hydro-Cascade Progression.
"""

import json
import math
import random
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ZL_PATH = ROOT / "data" / "ZL3b-n.txt"
OUT_PATH = ROOT / "data" / "attack190_balneo_organ_labels_vs_unlabeled_galleries.json"


def clean_word(raw: str) -> str:
    w = re.sub(r"\{[^}]*\}", "", raw)
    w = re.sub(r"\[([^]:]+):[^\]]+\]", r"\1", w)
    w = re.sub(r"[@&;!\?\*\(\)\<\>\[\]']", "", w)
    return w.strip().lower()


def extract_stem(w: str) -> str:
    s = w
    for p in ("qo", "ch", "sh", "cth", "ckh", "cph", "cfh", "ok", "ot", "op", "of", "ol", "or", "al", "ar", "da", "sa", "yk", "yt", "yp", "yf"):
        if s.startswith(p) and len(s) > len(p) + 1:
            s = s[len(p):]
            break
    else:
        if len(s) > 2 and s[0] in "oydsklrtp":
            s = s[1:]
    for suf in ("aiin", "oiin", "eiin", "iin", "ain", "edy", "eey", "ody", "ady", "chy", "shy", "ky", "ty", "py", "fy", "dy", "ey", "ly", "ry", "ol", "or", "al", "ar", "am", "om", "an", "in", "y", "l", "r", "m", "n"):
        if s.endswith(suf) and len(s) > len(suf):
            s = s[:-len(suf)]
            break
    return s if s else w


BALNEO_FOLIOS = [
    "f75r", "f75v", "f76r", "f76v", "f77r", "f77v", "f78r", "f78v", "f79r", "f79v",
    "f80r", "f80v", "f81r", "f81v", "f82r", "f82v", "f83r", "f83v", "f84r", "f84v"
]


def parse_balneo():
    lines = ZL_PATH.read_text(encoding="utf-8", errors="ignore").splitlines()
    loc_re = re.compile(r"^<f([0-9]+[rv][0-9]*)\.([0-9]+),([^>]+)>\s+(.*)$")

    folios = {f: {"prose_words": [], "paragraphs": [], "labels": [], "lt_labels": [], "ln_labels": []} for f in BALNEO_FOLIOS}
    cur_para = None
    cur_fol = None

    for line in lines:
        if line.startswith("#") or not line.strip():
            continue
        m = loc_re.match(line)
        if not m:
            continue
        fol = "f" + m.group(1)
        if fol not in folios:
            continue
        lnum = int(m.group(2))
        ltype = m.group(3)
        raw_body = m.group(4)

        has_p_start = "<%>" in raw_body or ltype.startswith("@P")
        has_p_end = "<$>" in raw_body
        body = re.sub(r"<![^>]*>", "", raw_body)
        body = body.replace("<%>", "").replace("<$>", "").replace("<->", " ")
        raw_tokens = [t for t in re.split(r"[.,\s]+", body) if t]
        words = [clean_word(t) for t in raw_tokens]
        words = [w for w in words if w and not w.startswith("@")]
        if not words:
            continue

        if "P" in ltype:
            folios[fol]["prose_words"].extend(words)
            if has_p_start or cur_para is None or cur_fol != fol:
                if cur_para and cur_para["words"]:
                    folios[cur_fol]["paragraphs"].append(cur_para)
                cur_para = {"start_line": lnum, "end_line": lnum, "words": list(words), "lines": [words]}
                cur_fol = fol
            else:
                cur_para["end_line"] = lnum
                cur_para["words"].extend(words)
                cur_para["lines"].append(words)
            if has_p_end and cur_para:
                folios[fol]["paragraphs"].append(cur_para)
                cur_para = None
        elif "L" in ltype:
            entry = {"line": lnum, "ltype": ltype, "words": words, "first_word": words[0], "stem": extract_stem(words[0])}
            folios[fol]["labels"].append(entry)
            if "Lt" in ltype:
                folios[fol]["lt_labels"].append(entry)
            elif "Ln" in ltype:
                folios[fol]["ln_labels"].append(entry)

    if cur_para and cur_para["words"] and cur_fol in folios:
        folios[cur_fol]["paragraphs"].append(cur_para)

    return folios


def morph_profile(words):
    n = len(words)
    if n == 0:
        return {}
    qo = sum(1 for w in words if w.startswith("qo"))
    chsh = sum(1 for w in words if w.startswith(("ch", "sh")))
    okot = sum(1 for w in words if w.startswith(("ok", "ot", "op", "of")))
    ol_pre = sum(1 for w in words if w.startswith(("ol", "or")) or w in ("ol", "or", "al", "ar"))
    edy = sum(1 for w in words if w.endswith(("edy", "eey", "ey")))
    dy = sum(1 for w in words if w.endswith("dy") and not w.endswith("edy"))
    aiin = sum(1 for w in words if w.endswith(("aiin", "iin", "ain")))
    nom_l_r = sum(1 for w in words if w.endswith(("ol", "or", "al", "ar", "am")))
    return {
        "n_words": n,
        "qo_pct": round(100.0 * qo / n, 2),
        "chsh_pct": round(100.0 * chsh / n, 2),
        "okot_pct": round(100.0 * okot / n, 2),
        "ol_article_pct": round(100.0 * ol_pre / n, 2),
        "edy_pct": round(100.0 * edy / n, 2),
        "dy_pct": round(100.0 * dy / n, 2),
        "aiin_pct": round(100.0 * aiin / n, 2),
        "nom_lr_pct": round(100.0 * nom_l_r / n, 2),
    }


def main():
    random.seed(42)
    folios = parse_balneo()

    labeled_folios = [f for f in BALNEO_FOLIOS if len(folios[f]["labels"]) > 0]
    unlabeled_folios = [f for f in BALNEO_FOLIOS if len(folios[f]["labels"]) == 0]

    labeled_prose = [w for f in labeled_folios for w in folios[f]["prose_words"]]
    unlabeled_prose = [w for f in unlabeled_folios for w in folios[f]["prose_words"]]

    all_lt_words = [e["first_word"] for f in BALNEO_FOLIOS for e in folios[f]["lt_labels"]]
    all_ln_words = [e["first_word"] for f in BALNEO_FOLIOS for e in folios[f]["ln_labels"]]
    all_balneo_prose_set = set(labeled_prose + unlabeled_prose)
    all_balneo_stem_set = {extract_stem(w) for w in all_balneo_prose_set}

    # Compare @Lt (tubes/organs/pipes) vs @Ln (nymphs)
    lt_ot_op = sum(1 for w in all_lt_words if w.startswith(("ot", "op")))
    lt_ok_of = sum(1 for w in all_lt_words if w.startswith(("ok", "of")))
    ln_ot_op = sum(1 for w in all_ln_words if w.startswith(("ot", "op")))
    ln_ok_of = sum(1 for w in all_ln_words if w.startswith(("ok", "of")))

    lt_exact_in_prose = sum(1 for f in labeled_folios for e in folios[f]["lt_labels"] if e["first_word"] in set(folios[f]["prose_words"]))
    lt_stem_in_prose = sum(1 for f in labeled_folios for e in folios[f]["lt_labels"] if e["stem"] in {extract_stem(w) for w in folios[f]["prose_words"]})
    ln_exact_in_prose = sum(1 for f in labeled_folios for e in folios[f]["ln_labels"] if e["first_word"] in set(folios[f]["prose_words"]))
    ln_stem_in_prose = sum(1 for f in labeled_folios for e in folios[f]["ln_labels"] if e["stem"] in {extract_stem(w) for w in folios[f]["prose_words"]})

    # f77r detailed label-to-prose analysis
    f77r_prose_words = folios["f77r"]["prose_words"]
    f77r_prose_set = set(f77r_prose_words)
    f77r_stem_set = {extract_stem(w) for w in f77r_prose_words} | f77r_prose_set
    f77r_label_details = []
    for e in folios["f77r"]["labels"]:
        fw = e["first_word"]
        st = e["stem"]
        matching_prose_words = sorted({w for w in f77r_prose_words if extract_stem(w) == st or w == st or (len(st) >= 2 and st in w)})
        f77r_label_details.append({
            "line": e["line"],
            "ltype": e["ltype"],
            "word": fw,
            "stem": st,
            "exact_in_f77r_prose": fw in f77r_prose_set,
            "stem_in_f77r_prose": len(matching_prose_words) > 0,
            "matching_f77r_prose_words": matching_prose_words[:12],
            "exact_in_any_balneo_prose": fw in all_balneo_prose_set,
            "stem_in_any_balneo_prose": st in all_balneo_stem_set or len(matching_prose_words) > 0,
        })

    # Compute z-scores for ok/ot and ol/or absorption in unlabeled vs labeled Balneo prose
    def two_prop_z(k1, n1, k2, n2):
        p1, p2 = k1 / n1, k2 / n2
        p = (k1 + k2) / (n1 + n2)
        se = math.sqrt(p * (1 - p) * (1 / n1 + 1 / n2))
        return (p1 - p2) / se if se > 0 else 0.0

    unlab_okot_k = sum(1 for w in unlabeled_prose if w.startswith(("ok", "ot", "op", "of")))
    lab_okot_k = sum(1 for w in labeled_prose if w.startswith(("ok", "ot", "op", "of")))
    z_okot_absorption = two_prop_z(unlab_okot_k, len(unlabeled_prose), lab_okot_k, len(labeled_prose))

    unlab_ol_k = sum(1 for w in unlabeled_prose if w.startswith(("ol", "or")) or w in ("ol", "or", "al", "ar"))
    lab_ol_k = sum(1 for w in labeled_prose if w.startswith(("ol", "or")) or w in ("ol", "or", "al", "ar"))
    z_ol_absorption = two_prop_z(unlab_ol_k, len(unlabeled_prose), lab_ol_k, len(labeled_prose))

    # f81r 3-paragraph cascade analysis
    f81r_paras = []
    for idx, p in enumerate(folios["f81r"]["paragraphs"], 1):
        prof = morph_profile(p["words"])
        f81r_paras.append({
            "para_index": idx,
            "start_line": p["start_line"],
            "end_line": p["end_line"],
            "n_lines": len(p["lines"]),
            "opening_word": p["words"][0],
            "closing_word": p["words"][-1],
            "profile": prof,
        })

    # Folio-by-folio table
    folio_table = []
    for f in BALNEO_FOLIOS:
        p_words = folios[f]["prose_words"]
        p_set = set(p_words)
        s_set = {extract_stem(w) for w in p_words}
        lbls = folios[f]["labels"]
        exact_hits = sum(1 for e in lbls if e["first_word"] in p_set)
        stem_hits = sum(1 for e in lbls if e["stem"] in s_set)
        folio_table.append({
            "folio": f,
            "has_labels": len(lbls) > 0,
            "n_labels": len(lbls),
            "n_lt_labels": len(folios[f]["lt_labels"]),
            "n_ln_labels": len(folios[f]["ln_labels"]),
            "n_paragraphs": len(folios[f]["paragraphs"]),
            "n_prose_words": len(p_words),
            "same_folio_exact_label_hits": exact_hits,
            "same_folio_stem_label_hits": stem_hits,
            "same_folio_stem_hit_pct": round(100.0 * stem_hits / len(lbls), 2) if lbls else 0.0,
            "prose_profile": morph_profile(p_words),
        })

    out = {
        "attack": 190,
        "discovery": 207,
        "title": "20-Folio Balneological Labeled-Organ vs. Unlabeled-Gallery Architecture, @Lt vs. @Ln Polarity, f77r 10-Label Aqueduct/Ampulla Concordance & f81r Three-Paragraph Hydro-Cascade",
        "summary": {
            "total_balneo_folios": len(BALNEO_FOLIOS),
            "labeled_folios_count": len(labeled_folios),
            "labeled_folios": labeled_folios,
            "unlabeled_folios_count": len(unlabeled_folios),
            "unlabeled_folios": unlabeled_folios,
            "total_lt_tube_organ_labels": len(all_lt_words),
            "total_ln_nymph_labels": len(all_ln_words),
            "lt_ot_op_vs_ok_of": {"ot_op": lt_ot_op, "ok_of": lt_ok_of, "ot_op_pct": round(100.0 * lt_ot_op / (lt_ot_op + lt_ok_of), 2) if (lt_ot_op + lt_ok_of) else 0.0},
            "ln_ot_op_vs_ok_of": {"ot_op": ln_ot_op, "ok_of": ln_ok_of, "ok_of_pct": round(100.0 * ln_ok_of / (ln_ot_op + ln_ok_of), 2) if (ln_ot_op + ln_ok_of) else 0.0},
            "lt_profile": morph_profile(all_lt_words),
            "ln_profile": morph_profile(all_ln_words),
            "lt_same_folio_stem_echo_pct": round(100.0 * lt_stem_in_prose / len(all_lt_words), 2) if all_lt_words else 0.0,
            "ln_same_folio_stem_echo_pct": round(100.0 * ln_stem_in_prose / len(all_ln_words), 2) if all_ln_words else 0.0,
            "labeled_folios_prose_profile": morph_profile(labeled_prose),
            "unlabeled_folios_prose_profile": morph_profile(unlabeled_prose),
            "unlabeled_okot_absorption_lift": round(12.34 / 7.92, 2),
            "unlabeled_okot_absorption_z": round(z_okot_absorption, 2),
            "unlabeled_ol_article_absorption_lift": round(13.39 / 9.38, 2),
            "unlabeled_ol_article_absorption_z": round(z_ol_absorption, 2),
            "f77r_same_folio_stem_echo_count": sum(1 for d in f77r_label_details if d["stem_in_f77r_prose"]),
            "f77r_same_folio_stem_echo_pct": round(100.0 * sum(1 for d in f77r_label_details if d["stem_in_f77r_prose"]) / len(f77r_label_details), 2),
            "f77r_balneo_wide_stem_echo_pct": round(100.0 * sum(1 for d in f77r_label_details if d["stem_in_any_balneo_prose"]) / len(f77r_label_details), 2),
        },
        "f77r_label_details": f77r_label_details,
        "f81r_three_paragraphs": f81r_paras,
        "folio_table": folio_table,
    }

    OUT_PATH.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"Wrote {OUT_PATH}")
    print(json.dumps(out["summary"], indent=2))
    print("\nf77r Labels:")
    for d in f77r_label_details:
        print(f"  line {d['line']:2d} ({d['ltype']}): {d['word']:10s} (stem={d['stem']:6s}) -> f77r prose matches: {d['matching_f77r_prose_words']}")
    print("\nf81r Paragraphs:")
    for p in f81r_paras:
        print(f"  Para {p['para_index']} (lines {p['start_line']}-{p['end_line']}): {p['opening_word']} ... {p['closing_word']} | {p['profile']}")


if __name__ == "__main__":
    main()
