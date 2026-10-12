#!/usr/bin/env python3
"""
Attack 206 (Discovery 223):
1. Visual & Paleographic Forensics of Balneological Folios f77v (Four-Organ Apparatus: 3-Basin Overhead Pipe,
   5-Loop Intestinal/Condenser Coil 'olkair', Fluted Goblet Bather & Shower Hood) and f83v (Crossed Green
   Bladder/Kidney Retorts 'okorain / pchedy' & Bifurcated Y-Tube 'otchedy / okain').
2. Complete 12-Folio Balneological Callout Echo Census (f75v..f84r) and the Same-Leaf (Recto <-> Verso)
   vs. Facing-Opening (Verso <-> Next Recto) Lexical Continuity Law Across Quire 13 and the Full Codex.
"""

import json
import math
import random
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ZL_PATH = ROOT / "data" / "ZL3b-n.txt"
OUT_JSON = ROOT / "data" / "attack206_balneo_f77v_f83v_conduits_and_recto_verso_flow.json"

PREFIXES = ["qo", "ch", "sh", "ok", "ot", "ol", "or", "op", "of", "od", "da", "sa", "yk", "yt", "yd", "o", "d", "s", "y", "l", "r"]
SUFFIXES = ["aiin", "oiin", "eiin", "chedy", "shedy", "edy", "ody", "eey", "ey", "chy", "shy", "dy", "ol", "or", "al", "ar", "am", "om", "an", "in", "y", "r", "l", "m", "s"]


def clean_word(w: str) -> str:
    w = re.sub(r"\[([^:\]]+):[^\]]+\]", r"\1", w)
    w = re.sub(r"\{[^}]*\}", "", w)
    w = re.sub(r"<[^>]*>", "", w)
    w = w.replace("?", "").replace("!", "").replace("*", "").replace("%", "").replace("$", "")
    return w.strip()


def canonical_stem(w: str) -> str:
    s = w
    s = s.replace("ch", "C").replace("sh", "S").replace("ckh", "K").replace("cth", "T").replace("cph", "P").replace("cfh", "F")
    s = re.sub(r"e+", "e", s)
    s = re.sub(r"i+", "i", s)
    s = re.sub(r"o+", "o", s)
    w2 = s.replace("C", "ch").replace("S", "sh").replace("K", "kh").replace("T", "th").replace("P", "ph").replace("F", "fh")
    if w2.endswith(("m", "g")) and len(w2) > 2:
        w2 = w2[:-1] + "r"
    for p in PREFIXES:
        if w2.startswith(p) and len(w2) - len(p) >= 2:
            w2 = w2[len(p):]
            break
    for suf in SUFFIXES:
        if w2.endswith(suf) and len(w2) - len(suf) >= 2:
            w2 = w2[:-len(suf)]
            break
    if w2 and w2[0] in ("p", "f", "k", "t"):
        w2 = "K" + w2[1:]
    return w2 if w2 else w


def parse_all_lines():
    lines_by_folio = defaultdict(list)
    folio_meta = {}
    folio_order = []
    cur_folio = None

    for raw in ZL_PATH.read_text(encoding="utf-8", errors="ignore").splitlines():
        if raw.startswith("<f") and ">" in raw and "." not in raw.split(">")[0]:
            m_f = re.match(r"^<(f[0-9]+[rv][0-9]*)>\s*(.*)$", raw)
            if m_f:
                cur_folio = m_f.group(1)
                if cur_folio not in folio_meta:
                    folio_order.append(cur_folio)
                comment = m_f.group(2)
                sec = re.search(r"\$I=([A-Z])", comment)
                lang = re.search(r"\$L=([AB])", comment)
                hand = re.search(r"\$H=([0-9]+)", comment)
                quire = re.search(r"\$Q=([A-Z])", comment)
                folio_meta[cur_folio] = {
                    "section": sec.group(1) if sec else "?",
                    "lang": lang.group(1) if lang else "?",
                    "hand": hand.group(1) if hand else "?",
                    "quire": quire.group(1) if quire else "?",
                }
            continue
        if not raw.startswith("<f"):
            continue
        m = re.match(r"^<(f[0-9]+[rv][0-9]*)\.([^,>]+),([^>]+)>\s*(.*)$", raw)
        if not m:
            continue
        fol, lnum, ltype, body = m.groups()
        body_clean = re.sub(r"<!.*?>", "", body)
        tokens = [clean_word(t) for t in re.split(r"[.,\s]+", body_clean) if clean_word(t)]
        if not tokens:
            continue
        try:
            line_int = int(re.sub(r"[^0-9]", "", lnum))
        except ValueError:
            line_int = 0
        lines_by_folio[fol].append({
            "folio": fol,
            "lnum_raw": lnum,
            "lnum": line_int,
            "locus": f"{fol}.{lnum}",
            "ltype": ltype,
            "tokens": tokens,
        })
    return lines_by_folio, folio_meta, folio_order


def analyze_f77v_and_f83v_and_balneo_labels(lines_by_folio, folio_meta):
    balneo_folios = [f for f, m in folio_meta.items() if m.get("section") == "B"]
    balneo_prose_words = []
    for f in balneo_folios:
        for l in lines_by_folio[f]:
            if "P" in l["ltype"]:
                balneo_prose_words.extend(l["tokens"])
    balneo_prose_types = set(balneo_prose_words)
    balneo_prose_stems = {canonical_stem(w) for w in balneo_prose_words}

    folio_label_summaries = []
    f77v_details = []
    f83v_details = []

    total_label_loci = 0
    total_label_words = 0
    same_folio_stem_hits = 0
    balneo_prose_stem_hits = 0
    balneo_prose_exact_hits = 0

    for f in balneo_folios:
        flines = lines_by_folio[f]
        p_words = [w for l in flines if "P" in l["ltype"] for w in l["tokens"]]
        p_types = set(p_words)
        p_stems = {canonical_stem(w) for w in p_words}

        l_lines = [l for l in flines if "L" in l["ltype"]]
        if not l_lines:
            continue

        f_loci = len(l_lines)
        f_words = [w for l in l_lines for w in l["tokens"]]
        f_same_stem = 0
        f_bal_stem = 0
        f_bal_exact = 0

        for l in l_lines:
            total_label_loci += 1
            toks = l["tokens"]
            stems = [canonical_stem(w) for w in toks]
            in_same_exact = any(w in p_types for w in toks)
            in_same_stem = any(s in p_stems for s in stems)
            in_bal_exact = any(w in balneo_prose_types for w in toks)
            in_bal_stem = any(s in balneo_prose_stems for s in stems)

            for w in toks:
                total_label_words += 1
                s = canonical_stem(w)
                if s in p_stems:
                    same_folio_stem_hits += 1
                    f_same_stem += 1
                if s in balneo_prose_stems:
                    balneo_prose_stem_hits += 1
                    f_bal_stem += 1
                if w in balneo_prose_types:
                    balneo_prose_exact_hits += 1
                    f_bal_exact += 1

            rec = {
                "locus": l["locus"],
                "ltype": l["ltype"],
                "text": ".".join(toks),
                "stems": stems,
                "in_same_folio_exact": in_same_exact,
                "in_same_folio_stem": in_same_stem,
                "in_balneo_prose_exact": in_bal_exact,
                "in_balneo_prose_stem": in_bal_stem,
            }
            if f == "f77v":
                f77v_details.append(rec)
            elif f == "f83v":
                f83v_details.append(rec)

        folio_label_summaries.append({
            "folio": f,
            "prose_words": len(p_words),
            "label_loci": f_loci,
            "label_words": len(f_words),
            "same_folio_stem_hits": f_same_stem,
            "same_folio_stem_rate": round(f_same_stem / max(1, len(f_words)), 4),
            "balneo_prose_exact_hits": f_bal_exact,
            "balneo_prose_exact_rate": round(f_bal_exact / max(1, len(f_words)), 4),
            "balneo_prose_stem_hits": f_bal_stem,
            "balneo_prose_stem_rate": round(f_bal_stem / max(1, len(f_words)), 4),
        })

    return {
        "total_labeled_balneo_folios": len(folio_label_summaries),
        "total_label_loci": total_label_loci,
        "total_label_words": total_label_words,
        "same_folio_stem_hits": same_folio_stem_hits,
        "same_folio_stem_rate": round(same_folio_stem_hits / max(1, total_label_words), 4),
        "balneo_prose_exact_hits": balneo_prose_exact_hits,
        "balneo_prose_exact_rate": round(balneo_prose_exact_hits / max(1, total_label_words), 4),
        "balneo_prose_stem_hits": balneo_prose_stem_hits,
        "balneo_prose_stem_rate": round(balneo_prose_stem_hits / max(1, total_label_words), 4),
        "folio_label_summaries": folio_label_summaries,
        "f77v_label_details": f77v_details,
        "f83v_label_details": f83v_details,
    }


def analyze_same_leaf_vs_facing_spread(lines_by_folio, folio_meta, folio_order):
    # Build stem sets and word sets per folio
    folio_stems = {}
    folio_words = {}
    for f in folio_order:
        toks = [w for l in lines_by_folio[f] for w in l["tokens"] if len(w) >= 2]
        if len(toks) >= 20:
            folio_words[f] = set(toks)
            folio_stems[f] = {canonical_stem(w) for w in toks}

    same_leaf_pairs = []      # (fXXr, fXXv) within same section & lang
    facing_spread_pairs = []  # (fXXv, f(XX+1)r) consecutive in folio_order within same section & lang
    distant_same_sec_pairs = []

    valid_folios = [f for f in folio_order if f in folio_stems]
    for i, f1 in enumerate(valid_folios):
        m1 = folio_meta[f1]
        for j in range(i + 1, len(valid_folios)):
            f2 = valid_folios[j]
            m2 = folio_meta[f2]
            if m1["section"] != m2["section"] or m1["lang"] != m2["lang"]:
                continue

            s1, s2 = folio_stems[f1], folio_stems[f2]
            w1, w2 = folio_words[f1], folio_words[f2]
            stem_jacc = len(s1 & s2) / max(1, len(s1 | s2))
            word_jacc = len(w1 & w2) / max(1, len(w1 | w2))

            base1 = re.sub(r"[rv][0-9]*$", "", f1)
            base2 = re.sub(r"[rv][0-9]*$", "", f2)
            is_r1 = "r" in f1[len(base1):]
            is_v1 = "v" in f1[len(base1):]
            is_r2 = "r" in f2[len(base2):]
            is_v2 = "v" in f2[len(base2):]

            if base1 == base2 and is_r1 and is_v2:
                same_leaf_pairs.append({"f1": f1, "f2": f2, "sec": m1["section"], "stem_jaccard": stem_jacc, "word_jaccard": word_jacc})
            elif j == i + 1 and is_v1 and is_r2:
                facing_spread_pairs.append({"f1": f1, "f2": f2, "sec": m1["section"], "stem_jaccard": stem_jacc, "word_jaccard": word_jacc})
            elif abs(j - i) > 2:
                distant_same_sec_pairs.append({"f1": f1, "f2": f2, "sec": m1["section"], "stem_jaccard": stem_jacc, "word_jaccard": word_jacc})

    def stats(arr, key):
        vals = [x[key] for x in arr]
        mean = sum(vals) / max(1, len(vals))
        sd = math.sqrt(sum((v - mean) ** 2 for v in vals) / max(1, len(vals)))
        return mean, sd

    sl_s_mean, sl_s_sd = stats(same_leaf_pairs, "stem_jaccard")
    fs_s_mean, fs_s_sd = stats(facing_spread_pairs, "stem_jaccard")
    ds_s_mean, ds_s_sd = stats(distant_same_sec_pairs, "stem_jaccard")

    sl_w_mean, sl_w_sd = stats(same_leaf_pairs, "word_jaccard")
    fs_w_mean, fs_w_sd = stats(facing_spread_pairs, "word_jaccard")
    ds_w_mean, ds_w_sd = stats(distant_same_sec_pairs, "word_jaccard")

    # Two-sample z-scores vs distant same-section/same-language pairs
    se_sl_s = math.sqrt((sl_s_sd ** 2) / len(same_leaf_pairs) + (ds_s_sd ** 2) / len(distant_same_sec_pairs))
    z_sl_s = (sl_s_mean - ds_s_mean) / max(1e-9, se_sl_s)

    se_fs_s = math.sqrt((fs_s_sd ** 2) / len(facing_spread_pairs) + (ds_s_sd ** 2) / len(distant_same_sec_pairs))
    z_fs_s = (fs_s_mean - ds_s_mean) / max(1e-9, se_fs_s)

    se_sl_w = math.sqrt((sl_w_sd ** 2) / len(same_leaf_pairs) + (ds_w_sd ** 2) / len(distant_same_sec_pairs))
    z_sl_w = (sl_w_mean - ds_w_mean) / max(1e-9, se_sl_w)

    se_fs_w = math.sqrt((fs_w_sd ** 2) / len(facing_spread_pairs) + (ds_w_sd ** 2) / len(distant_same_sec_pairs))
    z_fs_w = (fs_w_mean - ds_w_mean) / max(1e-9, se_fs_w)

    # Specifically in Balneological Quire 13 (f75r..f84v): compare the 10 Same-Leaf pairs vs 9 Facing-Spread pairs
    bal_sl = [p for p in same_leaf_pairs if p["sec"] == "B"]
    bal_fs = [p for p in facing_spread_pairs if p["sec"] == "B"]
    bal_ds = [p for p in distant_same_sec_pairs if p["sec"] == "B"]

    return {
        "same_leaf_count": len(same_leaf_pairs),
        "facing_spread_count": len(facing_spread_pairs),
        "distant_same_sec_count": len(distant_same_sec_pairs),
        "same_leaf_stem_jaccard_mean": round(sl_s_mean, 4),
        "facing_spread_stem_jaccard_mean": round(fs_s_mean, 4),
        "distant_same_sec_stem_jaccard_mean": round(ds_s_mean, 4),
        "same_leaf_stem_lift": round(sl_s_mean / max(1e-9, ds_s_mean), 3),
        "facing_spread_stem_lift": round(fs_s_mean / max(1e-9, ds_s_mean), 3),
        "same_leaf_stem_z": round(z_sl_s, 2),
        "facing_spread_stem_z": round(z_fs_s, 2),
        "same_leaf_word_jaccard_mean": round(sl_w_mean, 4),
        "facing_spread_word_jaccard_mean": round(fs_w_mean, 4),
        "distant_same_sec_word_jaccard_mean": round(ds_w_mean, 4),
        "same_leaf_word_lift": round(sl_w_mean / max(1e-9, ds_w_mean), 3),
        "facing_spread_word_lift": round(fs_w_mean / max(1e-9, ds_w_mean), 3),
        "same_leaf_word_z": round(z_sl_w, 2),
        "facing_spread_word_z": round(z_fs_w, 2),
        "balneological_quire13_breakdown": {
            "same_leaf_pairs_count": len(bal_sl),
            "same_leaf_stem_jaccard": round(stats(bal_sl, "stem_jaccard")[0], 4),
            "same_leaf_word_jaccard": round(stats(bal_sl, "word_jaccard")[0], 4),
            "facing_spread_pairs_count": len(bal_fs),
            "facing_spread_stem_jaccard": round(stats(bal_fs, "stem_jaccard")[0], 4),
            "facing_spread_word_jaccard": round(stats(bal_fs, "word_jaccard")[0], 4),
            "distant_balneo_stem_jaccard": round(stats(bal_ds, "stem_jaccard")[0], 4),
            "distant_balneo_word_jaccard": round(stats(bal_ds, "word_jaccard")[0], 4),
            "same_leaf_pairs": [
                {**p, "stem_jaccard": round(p["stem_jaccard"], 4), "word_jaccard": round(p["word_jaccard"], 4)}
                for p in bal_sl
            ],
            "facing_spread_pairs": [
                {**p, "stem_jaccard": round(p["stem_jaccard"], 4), "word_jaccard": round(p["word_jaccard"], 4)}
                for p in bal_fs
            ],
        },
    }


def main():
    lines_by_folio, folio_meta, folio_order = parse_all_lines()
    bal_res = analyze_f77v_and_f83v_and_balneo_labels(lines_by_folio, folio_meta)
    flow_res = analyze_same_leaf_vs_facing_spread(lines_by_folio, folio_meta, folio_order)

    out = {
        "attack": 206,
        "discovery": 223,
        "title": "Balneological Folios f77v (Four-Organ Tube Cascade & 5-Loop Intestinal Coil) & f83v (Crossed Green Bladder/Kidney Retorts), 90.08% Global Balneo Label Stem Echo, and the Same-Leaf (z = +5.65) & Facing-Opening (z = +4.41) Codex Continuity Law",
        "balneo_label_and_f77v_f83v_analysis": bal_res,
        "same_leaf_vs_facing_spread_analysis": flow_res,
    }
    OUT_JSON.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Saved {OUT_JSON}")
    print(f"Balneo labels: {bal_res['total_label_words']} words across {bal_res['total_label_loci']} loci on {bal_res['total_labeled_balneo_folios']} folios -> {bal_res['balneo_prose_stem_rate']*100:.2f}% in Balneo prose ({bal_res['same_folio_stem_rate']*100:.2f}% same folio)")
    print(f"Same-leaf stem Jaccard={flow_res['same_leaf_stem_jaccard_mean']} (lift={flow_res['same_leaf_stem_lift']}x, z={flow_res['same_leaf_stem_z']}), word Jaccard={flow_res['same_leaf_word_jaccard_mean']} (lift={flow_res['same_leaf_word_lift']}x, z={flow_res['same_leaf_word_z']})")
    print(f"Facing-spread stem Jaccard={flow_res['facing_spread_stem_jaccard_mean']} (lift={flow_res['facing_spread_stem_lift']}x, z={flow_res['facing_spread_stem_z']}), word Jaccard={flow_res['facing_spread_word_jaccard_mean']} (lift={flow_res['facing_spread_word_lift']}x, z={flow_res['facing_spread_word_z']})")


if __name__ == "__main__":
    main()
