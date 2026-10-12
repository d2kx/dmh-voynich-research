#!/usr/bin/env python3
"""
Attack 195 (Discovery 212): The f108v 365-Word Megaparagraph (10 Star-Marked
Sub-Clauses across 38 Lines), the Pre-Star Line-End Cadence Law across all 54
Intra-Paragraph Step Stars in Quire 20 (f103r-f116r), and the f94r Maidenhair
Fern / Spleenwort (Asplenium / Adiantum) Late Herbal Bridge.
"""

import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ZL_PATH = ROOT / "data" / "ZL3b-n.txt"
INDEX_PATH = ROOT / "data" / "folio_index.json"
OUT_JSON = ROOT / "data" / "attack195_f108v_megaparagraph_compiler_and_f94r_fern.json"

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


def main():
    index_data = json.loads(INDEX_PATH.read_text(encoding="utf-8"))
    folio_meta = index_data.get("folios", {})

    q20_lines = []
    f94r_lines = []
    sec_words = defaultdict(list)
    pending_star = None

    for raw in ZL_PATH.read_text(encoding="utf-8", errors="ignore").splitlines():
        if raw.startswith("#"):
            if "star" in raw.lower() and "text only" not in raw.lower():
                pending_star = raw.lstrip("#").strip()
            continue
        if not raw.startswith("<f"):
            continue
        m = re.match(r"^<(f[0-9]+[rv][0-9]*)\.([^,>]+),([^>]+)>\s+(.*)$", raw)
        if not m:
            continue
        folio, lnum, ltype, body = m.groups()
        sec = folio_meta.get(folio, {}).get("section", "?")
        has_p_start = "<%>" in body or ltype.startswith("@P")
        has_p_end = "<$>" in body
        star_code = pending_star
        pending_star = None
        body_clean = re.sub(r"<!.*?>", "", body)
        tokens = [clean_word(t) for t in re.split(r"[.,\s]+", body_clean) if clean_word(t)]
        if not tokens:
            continue
        sec_words[sec].extend(tokens)

        fnum = int(re.match(r"f([0-9]+)", folio).group(1))
        if 103 <= fnum <= 116 and "P" in ltype:
            q20_lines.append({
                "folio": folio,
                "lnum": int(re.sub(r"[^0-9]", "", lnum) or 0),
                "locus": f"{folio}.{lnum}",
                "ltype": ltype,
                "has_p_start": has_p_start,
                "has_p_end": has_p_end,
                "star_code": star_code,
                "words": tokens,
            })
        if folio == "f94r":
            f94r_lines.append({
                "locus": f"{folio}.{lnum}",
                "ltype": ltype,
                "has_p_start": has_p_start,
                "has_p_end": has_p_end,
                "words": tokens,
            })

    # 1. Test Pre-Star Line-End Cadence across Quire 20:
    # Compare line L-1 when line L is:
    #   (A) Primary <%> Recipe-Start Star (where L-1 has <$> paragraph end)
    #   (B) Secondary Intra-Paragraph +P0 Step Star (where L-1 is inside the same paragraph!)
    #   (C) Ordinary +P0 continuation line (no star on L, no <$> on L-1)
    pre_primary_end_words = []
    pre_step_star_end_words = []
    pre_ordinary_end_words = []

    for i in range(1, len(q20_lines)):
        curr = q20_lines[i]
        prev = q20_lines[i - 1]
        if curr["folio"] != prev["folio"]:
            continue
        last_w = prev["words"][-1]
        if curr["has_p_start"]:
            pre_primary_end_words.append(last_w)
        elif curr["star_code"] is not None and not curr["has_p_start"]:
            pre_step_star_end_words.append(last_w)
        else:
            pre_ordinary_end_words.append(last_w)

    def end_profile(words):
        n = len(words)
        if n == 0:
            return {}
        return {
            "n_lines": n,
            "m_stop_rate": round(sum(1 for w in words if w.endswith("m")) / n, 4),
            "dy_ey_y_rate": round(sum(1 for w in words if w.endswith(("dy", "ey", "y"))) / n, 4),
            "al_ar_ol_or_rate": round(sum(1 for w in words if w.endswith(("al", "ar", "ol", "or"))) / n, 4),
            "aiin_rate": round(sum(1 for w in words if w.endswith(("aiin", "oiin", "iin"))) / n, 4),
            "am_dy_y_al_ar_cadence_rate": round(
                sum(1 for w in words if w.endswith(("m", "dy", "y", "al", "ar", "ol", "or", "aiin"))) / n, 4
            ),
        }

    # 2. Compile f108v paragraphs and find the longest megaparagraph on f108v
    f108v_lines = [ln for ln in q20_lines if ln["folio"] == "f108v"]
    f108v_paragraphs = []
    curr_p = []
    for ln in f108v_lines:
        if ln["has_p_start"] and curr_p:
            f108v_paragraphs.append(curr_p)
            curr_p = [ln]
        else:
            curr_p.append(ln)
    if curr_p:
        f108v_paragraphs.append(curr_p)

    f108v_para_summaries = []
    for idx, p_lines in enumerate(f108v_paragraphs, 1):
        words = [w for ln in p_lines for w in ln["words"]]
        step_stars = [ln["locus"] for ln in p_lines[1:] if ln["star_code"] is not None]
        f108v_para_summaries.append({
            "para_num": idx,
            "start_locus": p_lines[0]["locus"],
            "end_locus": p_lines[-1]["locus"],
            "n_lines": len(p_lines),
            "n_words": len(words),
            "first_word": words[0],
            "last_word": words[-1],
            "n_step_stars": len(step_stars),
            "step_star_loci": step_stars,
        })

    # Compile star-marked sub-clauses of the longest megaparagraph on f108v (and also across all f108v)
    mega_lines = max(f108v_paragraphs, key=lambda p: sum(len(ln["words"]) for ln in p))
    subclauses = []
    curr_sc = []
    for idx, ln in enumerate(mega_lines):
        if idx > 0 and ln["star_code"] is not None and curr_sc:
            subclauses.append(curr_sc)
            curr_sc = [ln]
        else:
            curr_sc.append(ln)
    if curr_sc:
        subclauses.append(curr_sc)

    subclause_rows = []
    for idx, sc_lines in enumerate(subclauses, 1):
        words = [w for ln in sc_lines for w in ln["words"]]
        stems = {canonical_stem(w) for w in words}
        prev_words = {w for ln in subclauses[idx - 2] for w in ln["words"]} if idx > 1 else set()
        prev_stems = {canonical_stem(w) for w in prev_words} if idx > 1 else set()
        subclause_rows.append({
            "subclause_num": idx,
            "tier": "Primary <%> Start" if idx == 1 else "Intra-Paragraph +P0 Step Star",
            "start_locus": sc_lines[0]["locus"],
            "end_locus": sc_lines[-1]["locus"],
            "star_code": sc_lines[0]["star_code"],
            "n_lines": len(sc_lines),
            "n_words": len(words),
            "first_word": words[0],
            "last_word": words[-1],
            "qo_count": sum(1 for w in words if w.startswith("qo")),
            "edy_count": sum(1 for w in words if w.endswith(("edy", "ody"))),
            "shared_exact_with_prev": sorted(set(words) & prev_words),
            "shared_stems_with_prev": sorted(stems & prev_stems),
            "n_shared_exact_with_prev": len(set(words) & prev_words),
            "n_shared_stems_with_prev": len(stems & prev_stems),
        })

    # Also compile ALL megaparagraphs across Quire 20 and count their step stars
    q20_paragraphs = []
    cp = []
    for ln in q20_lines:
        if ln["has_p_start"] and cp:
            q20_paragraphs.append(cp)
            cp = [ln]
        else:
            cp.append(ln)
    if cp:
        q20_paragraphs.append(cp)

    megaparagraph_table = []
    for p_lines in q20_paragraphs:
        words = [w for ln in p_lines for w in ln["words"]]
        step_stars = [ln for ln in p_lines[1:] if ln["star_code"] is not None]
        if len(words) >= 80 or len(step_stars) >= 1:
            megaparagraph_table.append({
                "folio": p_lines[0]["folio"],
                "start_locus": p_lines[0]["locus"],
                "end_locus": p_lines[-1]["locus"],
                "n_lines": len(p_lines),
                "n_words": len(words),
                "n_step_stars": len(step_stars),
                "total_subclauses": 1 + len(step_stars),
                "mean_words_per_subclause": round(len(words) / (1 + len(step_stars)), 1),
                "first_word": words[0],
                "last_word": words[-1],
            })
    megaparagraph_table.sort(key=lambda x: -x["n_words"])

    all_star_clauses_words = []
    for p_lines in q20_paragraphs:
        sc = []
        for idx, ln in enumerate(p_lines):
            if idx > 0 and ln["star_code"] is not None and sc:
                all_star_clauses_words.append(sum(len(x["words"]) for x in sc))
                sc = [ln]
            else:
                sc.append(ln)
        if sc:
            all_star_clauses_words.append(sum(len(x["words"]) for x in sc))

    # 3. Analyze f94r Maidenhair Fern / Spleenwort (Asplenium / Adiantum)
    f94r_words = [w for ln in f94r_lines for w in ln["words"]]
    f94r_stems = {canonical_stem(w) for w in f94r_words}
    pharma_words = set(sec_words.get("Pharmaceutical", []))
    pharma_stems = {canonical_stem(w) for w in pharma_words}
    recipe_words = {ln_w for ln in q20_lines for ln_w in ln["words"]}
    recipe_stems = {canonical_stem(w) for w in recipe_words}
    f108v_word_set = {w for ln in f108v_lines for w in ln["words"]}
    f108v_stem_set = {canonical_stem(w) for w in f108v_word_set}

    f94r_profile = {
        "folio": "f94r",
        "botanical_id": "Maidenhair Fern / Spleenwort (Adiantum capillus-veneris / Asplenium trichomanes)",
        "n_lines": len(f94r_lines),
        "n_words": len(f94r_words),
        "first_line": ".".join(f94r_lines[0]["words"]),
        "last_line": ".".join(f94r_lines[-1]["words"]),
        "exact_in_pharma_count": sum(1 for w in f94r_words if w in pharma_words),
        "exact_in_pharma_rate": round(sum(1 for w in f94r_words if w in pharma_words) / len(f94r_words), 4),
        "stem_in_pharma_count": sum(1 for w in f94r_words if canonical_stem(w) in pharma_stems),
        "stem_in_pharma_rate": round(sum(1 for w in f94r_words if canonical_stem(w) in pharma_stems) / len(f94r_words), 4),
        "exact_in_recipes_count": sum(1 for w in f94r_words if w in recipe_words),
        "exact_in_recipes_rate": round(sum(1 for w in f94r_words if w in recipe_words) / len(f94r_words), 4),
        "stem_in_recipes_count": sum(1 for w in f94r_words if canonical_stem(w) in recipe_stems),
        "stem_in_recipes_rate": round(sum(1 for w in f94r_words if canonical_stem(w) in recipe_stems) / len(f94r_words), 4),
        "shared_exact_with_f108v": sorted(set(f94r_words) & f108v_word_set),
        "shared_stems_with_f108v": sorted(f94r_stems & f108v_stem_set),
    }

    longest_f108v_para = max(f108v_para_summaries, key=lambda x: x["n_words"])
    para_lengths = [sum(len(ln["words"]) for ln in p) for p in q20_paragraphs]
    mu_before = sum(para_lengths) / len(para_lengths)
    sd_before = math.sqrt(sum((x - mu_before) ** 2 for x in para_lengths) / len(para_lengths))
    mu_after = sum(all_star_clauses_words) / len(all_star_clauses_words)
    sd_after = math.sqrt(sum((x - mu_after) ** 2 for x in all_star_clauses_words) / len(all_star_clauses_words))

    out = {
        "summary": {
            "total_q20_paragraphs": len(q20_paragraphs),
            "total_q20_star_subclauses": len(all_star_clauses_words),
            "mean_words_per_paragraph": round(mu_before, 2),
            "sd_words_before_step_star_split": round(sd_before, 2),
            "cv_before_step_star_split": round(sd_before / mu_before, 3),
            "mean_words_per_star_unit": round(mu_after, 2),
            "sd_words_after_step_star_split": round(sd_after, 2),
            "cv_after_step_star_split": round(sd_after / mu_after, 3),
            "sd_reduction_factor": round(sd_before / sd_after, 2),
            "max_words_before_step_star_split": max(para_lengths),
            "max_words_after_step_star_split": max(all_star_clauses_words),
            "f108v_total_words": sum(p["n_words"] for p in f108v_para_summaries),
            "f108v_total_paragraphs": len(f108v_para_summaries),
            "f108v_total_step_stars": sum(p["n_step_stars"] for p in f108v_para_summaries),
            "f108v_megaparagraph_words": longest_f108v_para["n_words"],
            "f108v_megaparagraph_subclauses": len(subclause_rows),
            "f108v_mean_words_per_subclause": round(longest_f108v_para["n_words"] / len(subclause_rows), 2),
            "f94r_pharma_exact_echo_rate": f94r_profile["exact_in_pharma_rate"],
            "f94r_pharma_stem_echo_rate": f94r_profile["stem_in_pharma_rate"],
            "f94r_recipes_exact_echo_rate": f94r_profile["exact_in_recipes_rate"],
            "f94r_recipes_stem_echo_rate": f94r_profile["stem_in_recipes_rate"],
        },
        "pre_star_line_end_profiles": {
            "before_primary_recipe_start": end_profile(pre_primary_end_words),
            "before_intra_paragraph_step_star": end_profile(pre_step_star_end_words),
            "before_ordinary_continuation_line": end_profile(pre_ordinary_end_words),
        },
        "f108v_paragraphs": f108v_para_summaries,
        "f108v_megaparagraph_10_subclauses": subclause_rows,
        "quire20_step_star_megaparagraphs": megaparagraph_table,
        "f94r_profile": f94r_profile,
    }

    OUT_JSON.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"Wrote {OUT_JSON}")
    print(json.dumps(out["summary"], indent=2))
    print("Pre-star line-end profiles:", json.dumps(out["pre_star_line_end_profiles"], indent=2))
    print("Top megaparagraphs split by step stars:", json.dumps(megaparagraph_table[:8], indent=2))


if __name__ == "__main__":
    main()
