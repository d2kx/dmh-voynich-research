#!/usr/bin/env python3
"""
Attack 174: The Multi-Row Pharmaceutical Shelf-to-Paragraph Alignment Law (f88r-f102v2),
the Act-I Paragraph-Opening Ingredient Citation Law (Mean Line Pos = 0.285),
and Apothecary Vessel (@Lc) vs. Root (@Lf) Morphology.
"""

import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ZL_PATH = ROOT / "data" / "ZL3b-n.txt"
OUT_JSON = ROOT / "data" / "attack174_multirow_pharma_shelf_to_paragraph_alignment.json"


def clean_tok(t: str) -> str:
    t = re.sub(r"\{[^}]*\}", "", t)
    t = re.sub(r"\[([^]:]+):[^\]]+\]", r"\1", t)
    t = re.sub(r"[^a-zA-Z0-9]", "", t)
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


def parse_pharma_folios():
    folios = {}
    cur_folio = None
    cur_sec = None

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
                cur_sec = meta.get("I", "?")
                if cur_sec == "P":
                    folios[cur_folio] = {
                        "folio": cur_folio,
                        "containers": [],
                        "plant_rows": defaultdict(list),
                        "paragraphs": [],
                        "items": [],
                    }
                continue

            if not cur_folio or cur_sec != "P" or line.startswith("#"):
                continue

            m_l = re.match(r"^<(f\d+[rv]\d*)\.(\d+),([^>]+)>\s*(.*)$", line)
            if not m_l:
                continue
            fol, lno, ltype, body = m_l.group(1), int(m_l.group(2)), m_l.group(3), m_l.group(4)
            has_p_start = "<%>" in body
            has_p_end = "<$>" in body
            body_clean = re.sub(r"<![^>]*>", "", body)
            body_clean = re.sub(r"<[^>]*>", " ", body_clean)
            toks = [clean_tok(t) for t in re.split(r"[.\s,]+", body_clean)]
            toks = [t for t in toks if t]
            if not toks:
                continue

            folios[cur_folio]["items"].append({
                "lno": lno,
                "ltype": ltype,
                "has_p_start": has_p_start,
                "has_p_end": has_p_end,
                "tokens": toks,
            })

    for fol, fd in folios.items():
        cur_row_idx = 0
        last_was_lf = False
        cur_para = None

        for it in fd["items"]:
            lt = it["ltype"]
            toks = it["tokens"]
            if "Lc" in lt:
                for t in toks:
                    fd["containers"].append({"lno": it["lno"], "word": t, "stem": canonical_stem(t)})
                last_was_lf = False
            elif "Lf" in lt or "L0" in lt or "Ln" in lt:
                if not last_was_lf:
                    cur_row_idx += 1
                for t in toks:
                    fd["plant_rows"][cur_row_idx].append({
                        "lno": it["lno"],
                        "col": len(fd["plant_rows"][cur_row_idx]) + 1,
                        "word": t,
                        "stem": canonical_stem(t),
                    })
                last_was_lf = True
            elif any(p in lt for p in ("P", "Pt", "Pc")):
                last_was_lf = False
                if it["has_p_start"] or cur_para is None:
                    cur_para = {
                        "para_idx": len(fd["paragraphs"]) + 1,
                        "preceding_row_idx": cur_row_idx,
                        "lines": [],
                        "words": [],
                        "stems": set(),
                    }
                    fd["paragraphs"].append(cur_para)
                cur_para["lines"].append({"lno": it["lno"], "tokens": toks})
                cur_para["words"].extend(toks)
                for t in toks:
                    cur_para["stems"].add(canonical_stem(t))

    return folios


def exact_stem_matches_para(lbl_word: str, lbl_stem: str, para: dict) -> tuple[bool, list]:
    matched_lines = []
    for line_idx, ln in enumerate(para["lines"]):
        for w in ln["tokens"]:
            ws = canonical_stem(w)
            if w == lbl_word or ws == lbl_stem:
                matched_lines.append({
                    "line_idx_in_para": line_idx + 1,
                    "norm_line_pos": (line_idx) / max(1, len(para["lines"]) - 1) if len(para["lines"]) > 1 else 0.5,
                    "matched_word": w,
                    "matched_stem": ws,
                })
    return (len(matched_lines) > 0), matched_lines


def main():
    folios = parse_pharma_folios()

    paired_matches = 0
    paired_total = 0
    unpaired_same_page_matches = 0
    unpaired_same_page_total = 0
    off_folio_matches = 0
    off_folio_total = 0
    whole_folio_matches = 0

    all_first_hit_line_positions = []
    early_col_line_pos = []
    late_col_line_pos = []
    first_two_lines_hits = 0
    total_multi_line_hits = 0

    folio_breakdowns = []

    all_pharma_paras = [(fol, p) for fol, fd in folios.items() for p in fd["paragraphs"]]

    for fol, fd in sorted(folios.items()):
        if not fd["plant_rows"] or not fd["paragraphs"]:
            continue

        f_paired_hit = 0
        f_paired_tot = 0
        f_unpaired_hit = 0
        f_unpaired_tot = 0
        row_details = []

        for r_idx, plants in sorted(fd["plant_rows"].items()):
            paired_paras = [p for p in fd["paragraphs"] if p["preceding_row_idx"] == r_idx]
            if not paired_paras and r_idx <= len(fd["paragraphs"]):
                paired_paras = [fd["paragraphs"][r_idx - 1]]
            if not paired_paras and fd["paragraphs"]:
                paired_paras = [fd["paragraphs"][-1]]

            paired_ids = set(p["para_idx"] for p in paired_paras)
            off_paras = [p for p in fd["paragraphs"] if p["para_idx"] not in paired_ids]

            n_cols = len(plants)
            plant_echoes = []

            for pl in plants:
                hit_paired = False
                hit_lines_all = []
                for pp in paired_paras:
                    ok, mlines = exact_stem_matches_para(pl["word"], pl["stem"], pp)
                    if ok:
                        hit_paired = True
                        hit_lines_all.extend(mlines)

                paired_total += 1
                f_paired_tot += 1
                if hit_paired:
                    paired_matches += 1
                    f_paired_hit += 1

                # Check any paragraph on same folio
                hit_any_same_folio = hit_paired
                for op in off_paras:
                    ok_off, mlines_off = exact_stem_matches_para(pl["word"], pl["stem"], op)
                    unpaired_same_page_total += 1
                    f_unpaired_tot += 1
                    if ok_off:
                        unpaired_same_page_matches += 1
                        f_unpaired_hit += 1
                        hit_any_same_folio = True
                        if not hit_lines_all:
                            hit_lines_all.extend(mlines_off)

                if hit_any_same_folio:
                    whole_folio_matches += 1
                    norm_col = (pl["col"] - 1) / max(1, n_cols - 1) if n_cols > 1 else 0.5
                    first_line_pos = hit_lines_all[0]["norm_line_pos"]
                    all_first_hit_line_positions.append(first_line_pos)
                    total_multi_line_hits += 1
                    if hit_lines_all[0]["line_idx_in_para"] <= 2:
                        first_two_lines_hits += 1
                    if norm_col <= 0.5:
                        early_col_line_pos.append(first_line_pos)
                    else:
                        late_col_line_pos.append(first_line_pos)

                # Test against off-folio Pharmaceutical paragraphs
                for other_fol, other_p in all_pharma_paras:
                    if other_fol == fol:
                        continue
                    ok_other, _ = exact_stem_matches_para(pl["word"], pl["stem"], other_p)
                    off_folio_total += 1
                    if ok_other:
                        off_folio_matches += 1

                plant_echoes.append({
                    "col": pl["col"],
                    "word": pl["word"],
                    "stem": pl["stem"],
                    "hit_paired_para": hit_paired,
                    "hit_same_folio": hit_any_same_folio,
                    "sample_matches": [m["matched_word"] for m in hit_lines_all[:3]],
                })

            row_details.append({
                "row_idx": r_idx,
                "n_plants": len(plants),
                "paired_para_indices": sorted(paired_ids),
                "plants": plant_echoes,
            })

        folio_breakdowns.append({
            "folio": fol,
            "n_containers": len(fd["containers"]),
            "containers": [c["word"] for c in fd["containers"]],
            "n_rows": len(fd["plant_rows"]),
            "n_paragraphs": len(fd["paragraphs"]),
            "paired_hit_rate_pct": round(100.0 * f_paired_hit / max(1, f_paired_tot), 2),
            "off_row_hit_rate_pct": round(100.0 * f_unpaired_hit / max(1, f_unpaired_tot), 2) if f_unpaired_tot else None,
            "rows": row_details,
        })

    paired_rate = paired_matches / max(1, paired_total)
    unpaired_rate = unpaired_same_page_matches / max(1, unpaired_same_page_total)
    off_folio_rate = off_folio_matches / max(1, off_folio_total)
    whole_folio_rate = whole_folio_matches / max(1, paired_total)

    # Z-score of Paired Shelf->Paragraph vs Off-Folio Pharmaceutical Paragraph
    p_pool_off = (paired_matches + off_folio_matches) / max(1, paired_total + off_folio_total)
    se_off = math.sqrt(p_pool_off * (1.0 - p_pool_off) * (1.0 / max(1, paired_total) + 1.0 / max(1, off_folio_total)))
    z_paired_vs_off_folio = (paired_rate - off_folio_rate) / se_off if se_off > 0 else 0.0

    # Z-score of Paired Shelf->Paragraph vs Unpaired Same-Page Paragraph
    p_pool_sp = (paired_matches + unpaired_same_page_matches) / max(1, paired_total + unpaired_same_page_total)
    se_sp = math.sqrt(p_pool_sp * (1.0 - p_pool_sp) * (1.0 / max(1, paired_total) + 1.0 / max(1, unpaired_same_page_total)))
    z_paired_vs_same_page = (paired_rate - unpaired_rate) / se_sp if se_sp > 0 else 0.0

    # Act-I Paragraph-Opening Citation Law (mean_first_hit_line_pos vs 0.500 uniform null)
    mean_line_pos = sum(all_first_hit_line_positions) / max(1, len(all_first_hit_line_positions))
    sd_line_pos = math.sqrt(sum((x - mean_line_pos) ** 2 for x in all_first_hit_line_positions) / max(1, len(all_first_hit_line_positions) - 1))
    z_act1_opening = (mean_line_pos - 0.5) / (sd_line_pos / math.sqrt(max(1, len(all_first_hit_line_positions))))

    all_containers = [c["word"] for fd in folios.values() for c in fd["containers"]]
    all_plants = [p["word"] for fd in folios.values() for r in fd["plant_rows"].values() for p in r]

    def morph_profile(words):
        n = max(1, len(words))
        return {
            "count": len(words),
            "mean_len": round(sum(len(w) for w in words) / n, 2),
            "o_initial_pct": round(100.0 * sum(1 for w in words if w.startswith("o")) / n, 2),
            "ok_ot_initial_pct": round(100.0 * sum(1 for w in words if w.startswith(("ok", "ot", "op", "of"))) / n, 2),
            "d_or_s_initial_pct": round(100.0 * sum(1 for w in words if w.startswith(("d", "s", "r"))) / n, 2),
            "ends_l_or_r_or_d_pct": round(100.0 * sum(1 for w in words if w.endswith(("l", "r", "d", "n"))) / n, 2),
            "ends_y_pct": round(100.0 * sum(1 for w in words if w.endswith("y")) / n, 2),
            "sample_tokens": words[:16],
        }

    lc_prof = morph_profile(all_containers)
    lf_prof = morph_profile(all_plants)

    out = {
        "attack": "Attack 174: Multi-Row Pharmaceutical Shelf-to-Paragraph Gradient, Act-I Opening Citation Law & Vessel (@Lc) vs Root (@Lf) Morphology",
        "shelf_to_paragraph_gradient": {
            "whole_folio_hit_rate_pct": round(100.0 * whole_folio_rate, 2),
            "paired_shelf_para_matches": paired_matches,
            "paired_shelf_para_total": paired_total,
            "paired_shelf_para_hit_rate_pct": round(100.0 * paired_rate, 2),
            "off_shelf_same_page_matches": unpaired_same_page_matches,
            "off_shelf_same_page_total": unpaired_same_page_total,
            "off_shelf_same_page_hit_rate_pct": round(100.0 * unpaired_rate, 2),
            "off_folio_pharma_para_matches": off_folio_matches,
            "off_folio_pharma_para_total": off_folio_total,
            "off_folio_pharma_para_hit_rate_pct": round(100.0 * off_folio_rate, 2),
            "paired_vs_same_page_off_shelf_ratio": round(paired_rate / max(1e-9, unpaired_rate), 2),
            "paired_vs_same_page_off_shelf_z": round(z_paired_vs_same_page, 2),
            "paired_vs_off_folio_ratio": round(paired_rate / max(1e-9, off_folio_rate), 2),
            "paired_vs_off_folio_z": round(z_paired_vs_off_folio, 2),
        },
        "act1_paragraph_opening_citation_law": {
            "n_echoed_plants": len(all_first_hit_line_positions),
            "mean_first_hit_normalized_line_pos": round(mean_line_pos, 3),
            "uniform_null_line_pos": 0.500,
            "z_score_vs_uniform": round(z_act1_opening, 2),
            "first_two_lines_hit_count": first_two_lines_hits,
            "first_two_lines_hit_pct": round(100.0 * first_two_lines_hits / max(1, total_multi_line_hits), 2),
            "left_half_shelf_mean_line_pos": round(sum(early_col_line_pos) / max(1, len(early_col_line_pos)), 3),
            "right_half_shelf_mean_line_pos": round(sum(late_col_line_pos) / max(1, len(late_col_line_pos)), 3),
        },
        "container_Lc_vs_plant_Lf_morphology": {
            "apothecary_vessels_Lc": lc_prof,
            "plant_ingredients_Lf": lf_prof,
        },
        "folio_breakdowns": folio_breakdowns,
    }

    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)

    print("=== Attack 174 Summary ===")
    print(f"Exact Canonical Stem Gradient: Whole-Folio={out['shelf_to_paragraph_gradient']['whole_folio_hit_rate_pct']}% | Paired Shelf->Para={out['shelf_to_paragraph_gradient']['paired_shelf_para_hit_rate_pct']}% ({paired_matches}/{paired_total}) vs Off-Shelf Same-Page={out['shelf_to_paragraph_gradient']['off_shelf_same_page_hit_rate_pct']}% (Ratio={out['shelf_to_paragraph_gradient']['paired_vs_same_page_off_shelf_ratio']}x, z={z_paired_vs_same_page:+.2f}) vs Off-Folio Pharma Para={out['shelf_to_paragraph_gradient']['off_folio_pharma_para_hit_rate_pct']}% (Ratio={out['shelf_to_paragraph_gradient']['paired_vs_off_folio_ratio']}x, z={z_paired_vs_off_folio:+.2f})")
    print(f"Act-I Opening Citation Law: Mean First-Hit Line Pos={mean_line_pos:.3f} vs 0.500 null (z={z_act1_opening:+.2f}); {first_two_lines_hits}/{total_multi_line_hits} ({out['act1_paragraph_opening_citation_law']['first_two_lines_hit_pct']}%) hit in Lines 1-2 of the paragraph!")


if __name__ == "__main__":
    main()
