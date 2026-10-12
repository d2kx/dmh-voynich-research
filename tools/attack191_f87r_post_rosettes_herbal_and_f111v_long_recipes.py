#!/usr/bin/env python3
"""
Attack 191 (Discovery 208): The Post-Rosettes Late Herbal Monographs in Quires 15-17
(f87r-f96v, 16 Folio Panels), the f87r Parallel 'pchor' Paragraph Pair, and the
f111v Long-Recipe Multi-Clause Architecture (80.14 Words/Recipe vs. 36.92 Quire 20 Mean).
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
OUT_PATH = ROOT / "data" / "attack191_f87r_post_rosettes_herbal_and_f111v_long_recipes.json"


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


def parse_corpus():
    lines = ZL_PATH.read_text(encoding="utf-8", errors="ignore").splitlines()
    hdr_re = re.compile(r"^<(f[0-9]+[rv][0-9]*)>\s+<!\s*(.*?)>")
    loc_re = re.compile(r"^<f([0-9]+[rv][0-9]*)\.([0-9]+),([^>]+)>\s+(.*)$")

    fmeta = {}
    folios = defaultdict(lambda: {"words": [], "paragraphs": [], "lines": []})
    cur_para = None
    cur_fol = None

    for line in lines:
        if line.startswith("#") or not line.strip():
            continue
        mh = hdr_re.match(line)
        if mh:
            fol = mh.group(1)
            meta_str = mh.group(2)
            sec_m = re.search(r"\$I=([A-Z])", meta_str)
            lang_m = re.search(r"\$L=([AB])", meta_str)
            hand_m = re.search(r"\$H=([0-9])", meta_str)
            quire_m = re.search(r"\$Q=([A-Z])", meta_str)
            fmeta[fol] = {
                "section": sec_m.group(1) if sec_m else "?",
                "currier_lang": lang_m.group(1) if lang_m else "?",
                "hand": hand_m.group(1) if hand_m else "?",
                "quire": quire_m.group(1) if quire_m else "?",
            }
            continue
        m = loc_re.match(line)
        if not m:
            continue
        fol = "f" + m.group(1)
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

        folios[fol]["words"].extend(words)
        folios[fol]["lines"].append({"lnum": lnum, "ltype": ltype, "words": words})

        if "P" in ltype:
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

    if cur_para and cur_para["words"] and cur_fol:
        folios[cur_fol]["paragraphs"].append(cur_para)

    return folios, fmeta


def morph_profile(words):
    n = len(words)
    if n == 0:
        return {}
    qo = sum(1 for w in words if w.startswith("qo"))
    chsh = sum(1 for w in words if w.startswith(("ch", "sh")))
    cthckh = sum(1 for w in words if "cth" in w or "ckh" in w or "cph" in w or "cfh" in w)
    edy = sum(1 for w in words if w.endswith(("edy", "eey", "ey")))
    dy = sum(1 for w in words if w.endswith("dy") and not w.endswith("edy"))
    aiin = sum(1 for w in words if w.endswith(("aiin", "iin", "ain")))
    am = sum(1 for w in words if w.endswith(("am", "om", "aim")))
    return {
        "n_words": n,
        "qo_pct": round(100.0 * qo / n, 2),
        "chsh_pct": round(100.0 * chsh / n, 2),
        "cth_ckh_pct": round(100.0 * cthckh / n, 2),
        "edy_pct": round(100.0 * edy / n, 2),
        "dy_pct": round(100.0 * dy / n, 2),
        "aiin_pct": round(100.0 * aiin / n, 2),
        "am_pct": round(100.0 * am / n, 2),
    }


def main():
    random.seed(42)
    folios, fmeta = parse_corpus()

    # 1. Late Herbal (f87r-f96v, Quires 15-17) vs Early Herbal (f1r-f57v, Quires 1-7)
    late_herbal_folios = [
        "f87r", "f87v", "f90r1", "f90r2", "f90v1", "f90v2",
        "f93r", "f93v", "f94r", "f94v", "f95r1", "f95r2", "f95v1", "f95v2", "f96r", "f96v"
    ]
    early_herbal_folios = [
        f for f in folios
        if fmeta.get(f, {}).get("section") == "H" and f not in late_herbal_folios and f not in ("f58r", "f58v", "f65r", "f65v", "f66r", "f66v")
    ]
    pharma_folios = [f for f in folios if fmeta.get(f, {}).get("section") == "P"]
    pharma_words = [w for f in pharma_folios for w in folios[f]["words"]]
    pharma_word_set = set(pharma_words)
    pharma_stem_set = {extract_stem(w) for w in pharma_words}

    def pharma_overlap_stats(fol_list):
        exact_rates = []
        stem_rates = []
        jaccards = []
        for f in fol_list:
            ws = folios[f]["words"]
            if not ws:
                continue
            wset = set(ws)
            sset = {extract_stem(w) for w in ws}
            exact_rates.append(sum(1 for w in ws if w in pharma_word_set) / len(ws))
            stem_rates.append(sum(1 for w in ws if extract_stem(w) in pharma_stem_set) / len(ws))
            jaccards.append(len(sset & pharma_stem_set) / len(sset | pharma_stem_set))
        return {
            "n_folios": len(fol_list),
            "mean_pharma_exact_token_cov_pct": round(100.0 * sum(exact_rates) / len(exact_rates), 2),
            "mean_pharma_stem_token_cov_pct": round(100.0 * sum(stem_rates) / len(stem_rates), 2),
            "mean_pharma_stem_jaccard": round(sum(jaccards) / len(jaccards), 4),
        }

    late_herbal_stats = pharma_overlap_stats(late_herbal_folios)
    early_herbal_stats = pharma_overlap_stats(early_herbal_folios)

    # Specifically compare Currier A Late Herbal (12 folios) vs Currier A Early Herbal (80 folios)
    late_herbal_A = [f for f in late_herbal_folios if fmeta.get(f, {}).get("currier_lang") == "A"]
    early_herbal_A = [f for f in early_herbal_folios if fmeta.get(f, {}).get("currier_lang") == "A"]
    late_A_stats = pharma_overlap_stats(late_herbal_A)
    early_A_stats = pharma_overlap_stats(early_herbal_A)

    late_herbal_table = []
    for f in late_herbal_folios:
        ws = folios[f]["words"]
        m = fmeta.get(f, {})
        late_herbal_table.append({
            "folio": f,
            "currier_lang": m.get("currier_lang", "?"),
            "hand": m.get("hand", "?"),
            "n_paragraphs": len(folios[f]["paragraphs"]),
            "opening_words": [p["words"][0] for p in folios[f]["paragraphs"]],
            "pharma_exact_token_cov_pct": round(100.0 * sum(1 for w in ws if w in pharma_word_set) / len(ws), 2) if ws else 0.0,
            "pharma_stem_token_cov_pct": round(100.0 * sum(1 for w in ws if extract_stem(w) in pharma_stem_set) / len(ws), 2) if ws else 0.0,
            "profile": morph_profile(ws),
        })

    # f87r detailed analysis
    f87r_paras = []
    for idx, p in enumerate(folios["f87r"]["paragraphs"], 1):
        f87r_paras.append({
            "para_index": idx,
            "start_line": p["start_line"],
            "end_line": p["end_line"],
            "n_lines": len(p["lines"]),
            "opening_two_words": ".".join(p["words"][:2]),
            "closing_two_words": ".".join(p["words"][-2:]),
            "profile": morph_profile(p["words"]),
            "text_preview": " ".join(p["words"][:15]),
        })
    p1_stems = {extract_stem(w) for w in folios["f87r"]["paragraphs"][0]["words"]}
    p2_stems = {extract_stem(w) for w in folios["f87r"]["paragraphs"][1]["words"]}
    f87r_shared_stems = sorted(p1_stems & p2_stems)
    f87r_shared_exact = sorted(set(folios["f87r"]["paragraphs"][0]["words"]) & set(folios["f87r"]["paragraphs"][1]["words"]))

    # 2. Quire 20 Starred Recipes Length Stratification & f111v Long-Recipe Multi-Clause Architecture
    q20_folios = [
        "f103r", "f103v", "f104r", "f104v", "f105r", "f105v", "f106r", "f106v",
        "f107r", "f107v", "f108r", "f108v", "f111r", "f111v", "f112r", "f112v",
        "f113r", "f113v", "f114r", "f114v", "f115r", "f115v", "f116r"
    ]
    all_q20_recipes = []
    q20_page_means = []
    for f in q20_folios:
        ps = folios[f]["paragraphs"]
        words_per_rec = [len(p["words"]) for p in ps]
        q20_page_means.append({
            "folio": f,
            "n_recipes": len(ps),
            "total_words": sum(words_per_rec),
            "mean_words_per_recipe": round(sum(words_per_rec) / len(ps), 2) if ps else 0.0,
            "max_recipe_words": max(words_per_rec) if words_per_rec else 0,
        })
        for idx, p in enumerate(ps, 1):
            ws = p["words"]
            # Count internal gallows starts (excluding word 0)
            internal_gallows_init = sum(1 for w in ws[1:] if w.startswith(("k", "t", "p", "f", "ok", "ot", "op", "of")))
            internal_top_gallows = sum(1 for w in ws[1:] if w.startswith(("p", "f", "op", "of")))
            internal_am_dy_stops = sum(1 for w in ws[:-1] if w.endswith(("am", "om", "aim", "dy")) and not w.endswith("edy"))
            participle_to_qo_chains = sum(
                1 for i in range(len(ws) - 1)
                if ws[i].startswith(("ch", "sh")) and ws[i].endswith(("edy", "eey", "ey")) and ws[i + 1].startswith("qo")
            )
            all_q20_recipes.append({
                "folio": f,
                "recipe_idx": idx,
                "n_words": len(ws),
                "n_lines": len(p["lines"]),
                "opening_word": ws[0],
                "closing_word": ws[-1],
                "internal_gallows_init": internal_gallows_init,
                "internal_top_gallows": internal_top_gallows,
                "internal_am_dy_stops": internal_am_dy_stops,
                "participle_to_qo_chains": participle_to_qo_chains,
                "profile": morph_profile(ws),
            })

    short_recs = [r for r in all_q20_recipes if r["n_words"] <= 25]
    med_recs = [r for r in all_q20_recipes if 26 <= r["n_words"] <= 59]
    long_recs = [r for r in all_q20_recipes if r["n_words"] >= 60]

    def tier_summary(recs, label):
        n = len(recs)
        return {
            "tier": label,
            "n_recipes": n,
            "mean_words": round(sum(r["n_words"] for r in recs) / n, 2),
            "mean_lines": round(sum(r["n_lines"] for r in recs) / n, 2),
            "mean_internal_gallows_init": round(sum(r["internal_gallows_init"] for r in recs) / n, 2),
            "mean_internal_top_gallows_pf": round(sum(r["internal_top_gallows"] for r in recs) / n, 2),
            "mean_internal_am_dy_subclause_stops": round(sum(r["internal_am_dy_stops"] for r in recs) / n, 2),
            "mean_participle_to_qo_chains": round(sum(r["participle_to_qo_chains"] for r in recs) / n, 2),
            "mean_qo_pct": round(sum(r["profile"]["qo_pct"] for r in recs) / n, 2),
            "mean_edy_pct": round(sum(r["profile"]["edy_pct"] for r in recs) / n, 2),
        }

    # Count star comments in ZL3b-n across Quire 20: Paragraph-Start (<%>) vs Intra-Paragraph (+P0 without <%>)
    raw_lines = ZL_PATH.read_text(encoding="utf-8", errors="ignore").splitlines()
    loc_re = re.compile(r"^<(f1[01][0-9][rv])\.([0-9]+),([^>]+)>\s+(.*)$")
    pending_star = False
    para_start_stars = []
    intra_para_stars = []
    for line in raw_lines:
        if line.startswith("#") and "star" in line.lower() and "text only" not in line.lower():
            pending_star = True
            continue
        m = loc_re.match(line)
        if m:
            fol = m.group(1)
            lnum = int(m.group(2))
            body = m.group(4)
            clean_b = re.sub(r"<![^>]*>", "", body).replace("<%>", "").replace("<$>", "")
            toks = [clean_word(t) for t in re.split(r"[.,\s]+", clean_b) if clean_word(t)]
            fw = toks[0] if toks else ""
            if pending_star:
                if "<%>" in body or lnum == 1:
                    para_start_stars.append({"folio": fol, "line": lnum, "first_word": fw})
                else:
                    intra_para_stars.append({"folio": fol, "line": lnum, "first_word": fw})
                pending_star = False

    para_star_gallows = sum(1 for x in para_start_stars if x["first_word"].startswith(("p", "f", "k", "t", "op", "of", "ok", "ot")))
    intra_star_gallows = sum(1 for x in intra_para_stars if x["first_word"].startswith(("p", "f", "k", "t", "op", "of", "ok", "ot")))
    intra_star_sd_init = sum(1 for x in intra_para_stars if x["first_word"].startswith(("s", "d", "q", "o", "y", "l")))

    f111v_recipes = [r for r in all_q20_recipes if r["folio"] == "f111v"]

    out = {
        "attack": 191,
        "discovery": 208,
        "title": "Post-Rosettes Late Herbal Monographs in Quires 15-17 (f87r-f96v), the f87r Parallel 'pchor' Paragraph Pair, and the f111v Dual-Level Star & Long-Recipe Multi-Clause Architecture",
        "summary": {
            "late_herbal_folios_count": len(late_herbal_folios),
            "early_herbal_folios_count": len(early_herbal_folios),
            "late_herbal_pharma_overlap": late_herbal_stats,
            "early_herbal_pharma_overlap": early_herbal_stats,
            "late_herbal_A_pharma_overlap": late_A_stats,
            "early_herbal_A_pharma_overlap": early_A_stats,
            "late_vs_early_A_pharma_jaccard_lift": round(late_A_stats["mean_pharma_stem_jaccard"] / early_A_stats["mean_pharma_stem_jaccard"], 2),
            "f87r_shared_exact_words": f87r_shared_exact,
            "f87r_shared_stems": f87r_shared_stems,
            "quire20_short_recipes_tier": tier_summary(short_recs, "Short (<=25 words)"),
            "quire20_medium_recipes_tier": tier_summary(med_recs, "Medium (26-59 words)"),
            "quire20_long_recipes_tier": tier_summary(long_recs, "Long (>=60 words)"),
            "quire20_para_start_stars_count": len(para_start_stars),
            "quire20_para_start_stars_gallows_pct": round(100.0 * para_star_gallows / len(para_start_stars), 2) if para_start_stars else 0.0,
            "quire20_intra_para_stars_count": len(intra_para_stars),
            "quire20_intra_para_stars_gallows_pct": round(100.0 * intra_star_gallows / len(intra_para_stars), 2) if intra_para_stars else 0.0,
            "quire20_intra_para_stars_sd_particle_pct": round(100.0 * intra_star_sd_init / len(intra_para_stars), 2) if intra_para_stars else 0.0,
            "intra_para_stars_examples": intra_para_stars,
            "f111v_p_gallows_bottom_7_recipes": [r["opening_word"] for r in f111v_recipes[1:]],
        },
        "f87r_paragraphs": f87r_paras,
        "late_herbal_table": late_herbal_table,
        "f111v_recipes": f111v_recipes,
        "quire20_page_means_sorted": sorted(q20_page_means, key=lambda x: x["mean_words_per_recipe"], reverse=True),
    }

    OUT_PATH.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"Wrote {OUT_PATH}")
    print(json.dumps(out["summary"], indent=2))
    print("\nTop 5 Longest-Recipe Folios in Quire 20:")
    for pm in out["quire20_page_means_sorted"][:5]:
        print(" ", pm)
    print("\nf111v Recipes:")
    for r in f111v_recipes:
        print(f"  Recipe #{r['recipe_idx']}: {r['n_words']} words ({r['n_lines']} lines), {r['opening_word']} ... {r['closing_word']}, subclauses={r['internal_am_dy_stops']}, chsh->qo={r['participle_to_qo_chains']}")


if __name__ == "__main__":
    main()
