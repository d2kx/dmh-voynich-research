#!/usr/bin/env python3
"""
Attack 173: The 20-Quire Gathering Architecture, Quire Signatures (1..20),
100% Page-Boundary Paragraph Closure Law, and Same-Leaf / Same-Quire Lexical Cohesion.
"""

import json
import math
import random
import re
from collections import Counter, defaultdict
from pathlib import Path

random.seed(42)

ROOT = Path(__file__).resolve().parent.parent
ZL_PATH = ROOT / "data" / "ZL3b-n.txt"
OUT_JSON = ROOT / "data" / "attack173_quire_signatures_and_bifolio_continuity.json"


def clean_tok(t: str) -> str:
    t = re.sub(r"\{[^}]*\}", "", t)
    t = re.sub(r"\[([^]:]+):[^\]]+\]", r"\1", t)
    t = re.sub(r"[^a-zA-Z0-9@;]", "", t)
    return t.strip()


def canonical_stem(w: str) -> str:
    s = w
    for p in ("qo", "ch", "sh", "cth", "ckh", "cph", "cfh", "ok", "ot", "op", "of", "yk", "yt", "da", "sa", "so", "ol", "or", "al", "ar", "o", "y", "d", "s"):
        if s.startswith(p) and len(s) - len(p) >= 2:
            s = s[len(p):]
            break
    for suf in ("aiin", "oiin", "eiin", "chedy", "shedy", "edy", "eey", "ody", "oldy", "aldy", "am", "om", "aim", "ol", "or", "al", "ar", "dy", "ey", "hy", "ky", "ly", "ry", "y", "m", "n", "l", "r"):
        if s.endswith(suf) and len(s) - len(suf) >= 2:
            s = s[:-len(suf)]
            break
    return s if len(s) >= 2 else w


def parse_zl_quires():
    folios = {}
    quire_Order = []
    cur_folio = None

    with open(ZL_PATH, "r", encoding="utf-8", errors="ignore") as f:
        for raw in f:
            line = raw.strip()
            if not line:
                continue
            m_f = re.match(r"^<(f\d+[rv]\d*)>\s*(?:<!\s*(.*?)\s*>)?", line)
            if m_f and "." not in line.split(">")[0]:
                cur_folio = m_f.group(1)
                meta_str = m_f.group(2) or ""
                meta = dict(re.findall(r"\$([A-Z])=([A-Za-z0-9]+)", meta_str))
                folios[cur_folio] = {
                    "folio": cur_folio,
                    "quire": meta.get("Q", "?"),
                    "pos_in_quire": meta.get("P", "?"),
                    "folio_in_quire": meta.get("F", "?"),
                    "bifol_num": meta.get("B", "?"),
                    "section": meta.get("I", "?"),
                    "lang": meta.get("L", "?"),
                    "hand": meta.get("H", "?"),
                    "quire_mark_comments": [],
                    "other_comments": [],
                    "prose_lines": [],
                    "all_words": [],
                    "stems": set(),
                }
                continue

            if not cur_folio:
                continue

            if line.startswith("#"):
                if "Quire mark" in line or "quire" in line.lower() or "missing" in line.lower() or "numbered" in line.lower():
                    folios[cur_folio]["quire_mark_comments"].append(line)
                else:
                    folios[cur_folio]["other_comments"].append(line)
                continue

            m_l = re.match(r"^<(f\d+[rv]\d*)\.(\d+),([^>]+)>\s*(.*)$", line)
            if m_l:
                fol, lno, ltype, body = m_l.group(1), int(m_l.group(2)), m_l.group(3), m_l.group(4)
                has_p_start = "<%>" in body
                has_p_end = "<$>" in body
                body_clean = re.sub(r"<![^>]*>", "", body)
                body_clean = re.sub(r"<[^>]*>", " ", body_clean)
                raw_toks = [clean_tok(t) for t in re.split(r"[.\s,]+", body_clean)]
                toks = [t for t in raw_toks if t and not t.startswith("@")]
                if toks:
                    folios[cur_folio]["all_words"].extend(toks)
                    for t in toks:
                        folios[cur_folio]["stems"].add(canonical_stem(t))
                if any(p in ltype for p in ("P", "Pt", "Pc")):
                    folios[cur_folio]["prose_lines"].append({
                        "lno": lno,
                        "ltype": ltype,
                        "has_p_start": has_p_start,
                        "has_p_end": has_p_end,
                        "tokens": toks,
                    })
    return folios


def jaccard(s1: set, s2: set) -> float:
    if not s1 or not s2:
        return 0.0
    u = len(s1 | s2)
    return len(s1 & s2) / u if u else 0.0


def main():
    folios = parse_zl_quires()
    folio_list = list(folios.values())

    # 1. Group by Quire ($Q=A..T)
    quires = defaultdict(list)
    for fd in folio_list:
        quires[fd["quire"]].append(fd)

    quire_summaries = []
    pure_lang_quires = 0
    pure_hand_quires = 0
    pure_sec_quires = 0

    for q_letter in sorted(quires.keys()):
        q_fols = quires[q_letter]
        q_num = ord(q_letter) - ord("A") + 1
        langs = sorted(set(f["lang"] for f in q_fols if f["lang"] != "?"))
        hands = sorted(set(f["hand"] for f in q_fols if f["hand"] != "?"))
        secs = sorted(set(f["section"] for f in q_fols if f["section"] != "?"))
        q_marks = []
        for f in q_fols:
            for c in f["quire_mark_comments"]:
                if "Quire mark" in c:
                    q_marks.append(f"{f['folio']}: {c}")

        if len(langs) <= 1:
            pure_lang_quires += 1
        if len(hands) <= 1:
            pure_hand_quires += 1
        if len(secs) <= 1:
            pure_sec_quires += 1

        quire_summaries.append({
            "quire_letter": q_letter,
            "quire_number": q_num,
            "n_transcribed_pages": len(q_fols),
            "first_folio": q_fols[0]["folio"],
            "last_folio": q_fols[-1]["folio"],
            "sections": secs,
            "languages": langs,
            "scribe_hands": hands,
            "is_single_language": len(langs) <= 1,
            "is_single_hand": len(hands) <= 1,
            "is_single_section": len(secs) <= 1,
            "quire_mark_annotations": q_marks,
            "total_words": sum(len(f["all_words"]) for f in q_fols),
        })

    # 2. Page-Boundary Paragraph Closure Law & Terminal Stop Enrichment on Page-Final Lines
    prose_folios = [f for f in folio_list if f["prose_lines"]]
    pages_ending_with_p_end = 0
    pages_starting_with_p_start = 0

    page_final_words = []
    mid_page_line_final_words = []
    all_mid_line_words = []

    for f in prose_folios:
        plines = f["prose_lines"]
        if plines[0]["has_p_start"]:
            pages_starting_with_p_start += 1
        if plines[-1]["has_p_end"]:
            pages_ending_with_p_end += 1

        for idx, pl in enumerate(plines):
            toks = pl["tokens"]
            if not toks:
                continue
            if idx == len(plines) - 1:
                page_final_words.append(toks[-1])
            else:
                mid_page_line_final_words.append(toks[-1])
            if len(toks) > 1:
                all_mid_line_words.extend(toks[:-1])

    def stop_rate(words):
        if not words:
            return 0.0
        return sum(1 for w in words if w.endswith(("am", "om", "aim", "m"))) / len(words)

    def m_or_y_stop_rate(words):
        if not words:
            return 0.0
        return sum(1 for w in words if w.endswith(("am", "om", "aim", "m", "y"))) / len(words)

    page_final_m_rate = stop_rate(page_final_words)
    mid_page_end_m_rate = stop_rate(mid_page_line_final_words)
    mid_line_m_rate = stop_rate(all_mid_line_words)

    # 3. Missing-Folio Gap Analysis (check if pages immediately before/after missing leaves are 100% self-contained)
    missing_gaps = [
        {"gap": "f12 missing (Quire B)", "before": "f11v", "after": "f13r"},
        {"gap": "f59-f64 missing (Quire H)", "before": "f58v", "after": "f65r"},
        {"gap": "f74 missing (Quire L)", "before": "f73v", "after": "f75r"},
        {"gap": "f91-f92 missing (Quire P)", "before": "f90v2", "after": "f93r"},
        {"gap": "f97-f98 missing (Quire R)", "before": "f96v", "after": "f99r"},
        {"gap": "f109-f110 missing (Quire T)", "before": "f108v", "after": "f111r"},
    ]
    gap_results = []
    for g in missing_gaps:
        fb = folios.get(g["before"])
        fa = folios.get(g["after"])
        b_closed = fb["prose_lines"][-1]["has_p_end"] if (fb and fb["prose_lines"]) else True
        a_opened = fa["prose_lines"][0]["has_p_start"] if (fa and fa["prose_lines"]) else True
        b_last_word = fb["prose_lines"][-1]["tokens"][-1] if (fb and fb["prose_lines"] and fb["prose_lines"][-1]["tokens"]) else "(label-only)"
        a_first_word = fa["prose_lines"][0]["tokens"][0] if (fa and fa["prose_lines"] and fa["prose_lines"][0]["tokens"]) else "(label-only)"
        gap_results.append({
            "gap": g["gap"],
            "before_folio": g["before"],
            "after_folio": g["after"],
            "before_ends_with_paragraph_close": b_closed,
            "after_starts_with_paragraph_open": a_opened,
            "before_last_word": b_last_word,
            "after_first_word": a_first_word,
        })

    # 4. Physical Leaf (Recto <-> Verso), Conjoined Bifolio ($B), and Same-Quire ($Q) Lexical Stem Cohesion
    # Controlled strictly within matching (Section $I, Language $L) buckets!
    valid_folios = [f for f in folio_list if len(f["stems"]) >= 15 and f["section"] != "?" and f["lang"] != "?"]

    same_leaf_jaccards = []
    same_bifolio_jaccards = []
    same_quire_jaccards = []
    diff_quire_same_sec_lang_jaccards = []

    def base_leaf(fol_name: str) -> str:
        m = re.match(r"^f(\d+)", fol_name)
        return m.group(1) if m else fol_name

    for i in range(len(valid_folios)):
        for j in range(i + 1, len(valid_folios)):
            f1, f2 = valid_folios[i], valid_folios[j]
            if f1["section"] != f2["section"] or f1["lang"] != f2["lang"]:
                continue
            jac = jaccard(f1["stems"], f2["stems"])
            if base_leaf(f1["folio"]) == base_leaf(f2["folio"]):
                same_leaf_jaccards.append(jac)
            elif f1["quire"] == f2["quire"] and f1["bifol_num"] != "?" and f1["bifol_num"] == f2["bifol_num"]:
                same_bifolio_jaccards.append(jac)
            elif f1["quire"] == f2["quire"]:
                same_quire_jaccards.append(jac)
            else:
                diff_quire_same_sec_lang_jaccards.append(jac)

    def mean_std(arr):
        if not arr:
            return 0.0, 0.0
        m = sum(arr) / len(arr)
        v = sum((x - m) ** 2 for x in arr) / max(1, len(arr) - 1)
        return m, math.sqrt(v)

    m_leaf, s_leaf = mean_std(same_leaf_jaccards)
    m_bifol, s_bifol = mean_std(same_bifolio_jaccards)
    m_quire, s_quire = mean_std(same_quire_jaccards)
    m_diff, s_diff = mean_std(diff_quire_same_sec_lang_jaccards)

    # Two-sample z-scores vs diff_quire_same_sec_lang
    z_leaf_vs_diff = (m_leaf - m_diff) / math.sqrt((s_leaf ** 2 / len(same_leaf_jaccards)) + (s_diff ** 2 / len(diff_quire_same_sec_lang_jaccards)))
    z_quire_vs_diff = (m_quire - m_diff) / math.sqrt((s_quire ** 2 / len(same_quire_jaccards)) + (s_diff ** 2 / len(diff_quire_same_sec_lang_jaccards)))

    out = {
        "attack": "Attack 173: 20-Quire Gathering Signatures, 100% Page-Boundary Closure Law & Physical Leaf/Quire Lexical Cohesion",
        "quire_architecture": {
            "total_quires": len(quire_summaries),
            "single_language_quires": pure_lang_quires,
            "single_language_quire_pct": round(100.0 * pure_lang_quires / len(quire_summaries), 2),
            "single_hand_quires": pure_hand_quires,
            "single_hand_quire_pct": round(100.0 * pure_hand_quires / len(quire_summaries), 2),
            "single_section_quires": pure_sec_quires,
            "single_section_quire_pct": round(100.0 * pure_sec_quires / len(quire_summaries), 2),
            "quires": quire_summaries,
        },
        "page_boundary_closure_law": {
            "total_prose_folios": len(prose_folios),
            "pages_starting_with_paragraph_open": pages_starting_with_p_start,
            "pages_starting_with_paragraph_open_pct": round(100.0 * pages_starting_with_p_start / len(prose_folios), 2),
            "pages_ending_with_paragraph_close": pages_ending_with_p_end,
            "pages_ending_with_paragraph_close_pct": round(100.0 * pages_ending_with_p_end / len(prose_folios), 2),
            "page_final_word_m_stop_rate_pct": round(100.0 * page_final_m_rate, 2),
            "mid_page_line_end_m_stop_rate_pct": round(100.0 * mid_page_end_m_rate, 2),
            "mid_line_m_stop_rate_pct": round(100.0 * mid_line_m_rate, 2),
            "page_final_vs_mid_line_m_stop_ratio": round(page_final_m_rate / max(1e-9, mid_line_m_rate), 2),
            "page_final_vs_mid_page_line_end_m_stop_ratio": round(page_final_m_rate / max(1e-9, mid_page_end_m_rate), 2),
            "page_final_m_or_y_stop_rate_pct": round(100.0 * m_or_y_stop_rate(page_final_words), 2),
        },
        "missing_folio_boundary_test": gap_results,
        "physical_codicology_cohesion_controlled_for_section_and_lang": {
            "n_same_leaf_pairs": len(same_leaf_jaccards),
            "mean_jaccard_same_leaf_recto_verso": round(m_leaf, 4),
            "n_same_bifolio_pairs": len(same_bifolio_jaccards),
            "mean_jaccard_same_bifolio_sheet": round(m_bifol, 4),
            "n_same_quire_pairs": len(same_quire_jaccards),
            "mean_jaccard_same_quire": round(m_quire, 4),
            "n_diff_quire_same_section_lang_pairs": len(diff_quire_same_sec_lang_jaccards),
            "mean_jaccard_diff_quire_same_section_lang": round(m_diff, 4),
            "same_leaf_vs_diff_quire_ratio": round(m_leaf / max(1e-9, m_diff), 2),
            "same_leaf_vs_diff_quire_z": round(z_leaf_vs_diff, 2),
            "same_quire_vs_diff_quire_ratio": round(m_quire / max(1e-9, m_diff), 2),
            "same_quire_vs_diff_quire_z": round(z_quire_vs_diff, 2),
        },
    }

    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)

    print("=== Attack 173 Summary ===")
    print(f"Total Quires: {len(quire_summaries)} | Single-Language Quires: {pure_lang_quires}/{len(quire_summaries)} ({out['quire_architecture']['single_language_quire_pct']}%) | Single-Hand Quires: {pure_hand_quires}/{len(quire_summaries)} ({out['quire_architecture']['single_hand_quire_pct']}%)")
    print(f"Page-Boundary Closure: {pages_starting_with_p_start}/{len(prose_folios)} ({out['page_boundary_closure_law']['pages_starting_with_paragraph_open_pct']}%) start with <%> and {pages_ending_with_p_end}/{len(prose_folios)} ({out['page_boundary_closure_law']['pages_ending_with_paragraph_close_pct']}%) end with <$>")
    print(f"Page-Final -m Stop Rate: {out['page_boundary_closure_law']['page_final_word_m_stop_rate_pct']}% vs Mid-Page Line-End {out['page_boundary_closure_law']['mid_page_line_end_m_stop_rate_pct']}% ({out['page_boundary_closure_law']['page_final_vs_mid_page_line_end_m_stop_ratio']}x) vs Mid-Line {out['page_boundary_closure_law']['mid_line_m_stop_rate_pct']}% ({out['page_boundary_closure_law']['page_final_vs_mid_line_m_stop_ratio']}x)")
    print(f"Controlled Stem Jaccard (Same Section & Lang): Same-Leaf={m_leaf:.4f} (z={z_leaf_vs_diff:+.2f}), Same-Bifolio={m_bifol:.4f}, Same-Quire={m_quire:.4f} (z={z_quire_vs_diff:+.2f}) vs Diff-Quire={m_diff:.4f}")


if __name__ == "__main__":
    main()
