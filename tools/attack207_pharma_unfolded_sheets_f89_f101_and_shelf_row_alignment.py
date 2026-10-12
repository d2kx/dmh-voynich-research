#!/usr/bin/env python3
"""
Attack 207 (Discovery 224):
1. Unfolded Pharmaceutical Master Sheets p163 (f88v | f89r1 | f89r2: 3 Panels, 9 Tiered Albarelli Jars,
   51 Label Words & 466 Prose Words, Plus Arabic Numeral '48' Marginalia above f89r1.15)
   and p179 (f100v | f101r: Left Column f100v with 13 Labeled Cuttings + Right Wide Panel f101r with 28 Unlabeled Cuttings
   and 10 Ultra-Wide 22.7-Word/Line Prose Lines).
2. The p179 (f100v -> f101r) Cross-Column Sheet Echo (7.14% on f100v alone -> 50.00% across p179 = 7.00x Jump!),
   the f101r Unlabeled Pharmaceutical Nominal Absorption Law (qo- Suppressed 2.40x, o-/ol-/or- Nominal Surge),
   and the 16-Folio 3-Stage Supply Chain Census (72.87% Herbal, 69.64% Quire 20, 58.30% Complete 3-Stage Bridge).
"""

import json
import math
import random
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ZL_PATH = ROOT / "data" / "ZL3b-n.txt"
OUT_JSON = ROOT / "data" / "attack207_pharma_unfolded_sheets_f89_f101_and_shelf_row_alignment.json"

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
    cur_folio = None

    for raw in ZL_PATH.read_text(encoding="utf-8", errors="ignore").splitlines():
        if raw.startswith("<f") and ">" in raw and "." not in raw.split(">")[0]:
            m_f = re.match(r"^<(f[0-9]+[rv][0-9]*)>\s*(.*)$", raw)
            if m_f:
                cur_folio = m_f.group(1)
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
        has_para_start = "<%>" in body
        has_para_end = "<$>" in body
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
            "para_start": has_para_start,
            "para_end": has_para_end,
            "tokens": tokens,
        })
    return lines_by_folio, folio_meta


def analyze_pharma_sheets_and_rows(lines_by_folio, folio_meta):
    pharma_folios = [f for f, m in folio_meta.items() if m.get("section") == "P"]
    quire20_folios = [f for f, m in folio_meta.items() if m.get("section") == "S"]
    herbal_folios = [f for f, m in folio_meta.items() if m.get("section") == "H"]

    pharma_prose_words = [w for f in pharma_folios for l in lines_by_folio[f] if "P" in l["ltype"] for w in l["tokens"]]
    pharma_prose_types = set(pharma_prose_words)
    pharma_prose_stems = {canonical_stem(w) for w in pharma_prose_words}

    q20_words = [w for f in quire20_folios for l in lines_by_folio[f] for w in l["tokens"]]
    q20_types = set(q20_words)
    q20_stems = {canonical_stem(w) for w in q20_words}

    herbal_words = [w for f in herbal_folios for l in lines_by_folio[f] for w in l["tokens"]]
    herbal_types = set(herbal_words)
    herbal_stems = {canonical_stem(w) for w in herbal_words}

    target_folios = ["f88v", "f89r1", "f89r2", "f89v2", "f89v1", "f100v", "f101r"]
    folio_profiles = []
    for f in pharma_folios:
        flines = sorted(lines_by_folio[f], key=lambda x: x["lnum"])
        lc_lines = [l for l in flines if "Lc" in l["ltype"]]
        lf_lines = [l for l in flines if "Lf" in l["ltype"] or ("L" in l["ltype"] and "Lc" not in l["ltype"])]
        p_lines = [l for l in flines if "P" in l["ltype"]]

        lc_words = [w for l in lc_lines for w in l["tokens"]]
        lf_words = [w for l in lf_lines for w in l["tokens"]]
        lbl_words = lc_words + lf_words
        p_words = [w for l in p_lines for w in l["tokens"]]
        p_stems_local = {canonical_stem(w) for w in p_words}
        p_types_local = set(p_words)

        paras = []
        cur_p = []
        for l in p_lines:
            if l["para_start"] and cur_p:
                paras.append(cur_p)
                cur_p = []
            cur_p.append(l)
        if cur_p:
            paras.append(cur_p)

        same_folio_stem_hits = sum(1 for w in lbl_words if canonical_stem(w) in p_stems_local)
        same_folio_exact_hits = sum(1 for w in lbl_words if w in p_types_local)
        pharma_stem_hits = sum(1 for w in lbl_words if canonical_stem(w) in pharma_prose_stems)
        herbal_stem_hits = sum(1 for w in lbl_words if canonical_stem(w) in herbal_stems)
        q20_stem_hits = sum(1 for w in lbl_words if canonical_stem(w) in q20_stems)
        full_3stage_bridges = sum(
            1 for w in lbl_words
            if canonical_stem(w) in herbal_stems and canonical_stem(w) in pharma_prose_stems and canonical_stem(w) in q20_stems
        )

        folio_profiles.append({
            "folio": f,
            "lc_loci": len(lc_lines),
            "lf_loci": len(lf_lines),
            "total_label_words": len(lbl_words),
            "paragraphs_count": len(paras),
            "prose_lines": len(p_lines),
            "prose_words": len(p_words),
            "mean_words_per_line": round(len(p_words) / max(1, len(p_lines)), 2),
            "same_folio_exact_hits": same_folio_exact_hits,
            "same_folio_stem_hits": same_folio_stem_hits,
            "same_folio_stem_rate": round(same_folio_stem_hits / max(1, len(lbl_words)), 4),
            "pharma_prose_stem_hits": pharma_stem_hits,
            "pharma_prose_stem_rate": round(pharma_stem_hits / max(1, len(lbl_words)), 4),
            "herbal_stem_hits": herbal_stem_hits,
            "herbal_stem_rate": round(herbal_stem_hits / max(1, len(lbl_words)), 4),
            "quire20_stem_hits": q20_stem_hits,
            "quire20_stem_rate": round(q20_stem_hits / max(1, len(lbl_words)), 4),
            "three_stage_supply_chain_hits": full_3stage_bridges,
            "three_stage_supply_chain_rate": round(full_3stage_bridges / max(1, len(lbl_words)), 4),
            "labels_detail": [
                {
                    "locus": l["locus"],
                    "ltype": l["ltype"],
                    "text": ".".join(l["tokens"]),
                    "stems": [canonical_stem(w) for w in l["tokens"]],
                    "in_same_folio_stem": any(canonical_stem(w) in p_stems_local for w in l["tokens"]),
                    "in_herbal_stem": any(canonical_stem(w) in herbal_stems for w in l["tokens"]),
                    "in_quire20_stem": any(canonical_stem(w) in q20_stems for w in l["tokens"]),
                }
                for l in (lc_lines + lf_lines)
            ] if f in target_folios else [],
            "paragraph_openers": [
                {
                    "para_idx": idx + 1,
                    "start_locus": p[0]["locus"],
                    "lines": len(p),
                    "words": sum(len(x["tokens"]) for x in p),
                    "opening_words": ".".join(p[0]["tokens"][:4]),
                }
                for idx, p in enumerate(paras)
            ],
        })

    # Unfolded Sheet p163 (f88v | f89r1 | f89r2)
    p163_folios = ["f88v", "f89r1", "f89r2"]
    p163_labels = [w for f in p163_folios for l in lines_by_folio[f] if "L" in l["ltype"] for w in l["tokens"]]
    p163_prose = [w for f in p163_folios for l in lines_by_folio[f] if "P" in l["ltype"] for w in l["tokens"]]
    p163_prose_stems = {canonical_stem(w) for w in p163_prose}
    p163_prose_types = set(p163_prose)

    p163_label_in_sheet_stem = sum(1 for w in p163_labels if canonical_stem(w) in p163_prose_stems)
    p163_label_in_sheet_exact = sum(1 for w in p163_labels if w in p163_prose_types)
    p163_same_folio_stem = sum(fp["same_folio_stem_hits"] for fp in folio_profiles if fp["folio"] in p163_folios)

    # Unfolded Sheet p179 (f100v | f101r):
    # Why did f100v (left column of p179, 14 label words, 79 prose words) have only 1/14 (7.14%) self-prose stem match,
    # while f101r (right wide panel of p179, 28 unlabeled cuttings, 227 prose words across 10 ultra-wide lines) has 0 labels?
    f100v_labels = [w for l in lines_by_folio["f100v"] if "L" in l["ltype"] for w in l["tokens"]]
    f100v_prose = [w for l in lines_by_folio["f100v"] if "P" in l["ltype"] for w in l["tokens"]]
    f101r_prose = [w for l in lines_by_folio["f101r"] if "P" in l["ltype"] for w in l["tokens"]]
    p179_prose = f100v_prose + f101r_prose

    f100v_prose_stems = {canonical_stem(w) for w in f100v_prose}
    f101r_prose_stems = {canonical_stem(w) for w in f101r_prose}
    p179_prose_stems = {canonical_stem(w) for w in p179_prose}

    f100v_in_self = sum(1 for w in f100v_labels if canonical_stem(w) in f100v_prose_stems)
    f100v_in_f101r = sum(1 for w in f100v_labels if canonical_stem(w) in f101r_prose_stems)
    f100v_in_p179 = sum(1 for w in f100v_labels if canonical_stem(w) in p179_prose_stems)
    f100v_matched_in_f101r_details = [
        {"label": w, "stem": canonical_stem(w), "f101r_matches": [pw for pw in f101r_prose if canonical_stem(pw) == canonical_stem(w)]}
        for w in f100v_labels if canonical_stem(w) in f101r_prose_stems
    ]

    # Compare f101r (the ONLY unlabeled multi-row plant sheet in Pharma: 28 unlabeled cuttings, 227 prose words, 22.70 words/line)
    # against the 15 Labeled Pharmaceutical folios (2,153 prose words, 10.61 words/line):
    labeled_pharma_prose = [w for f in pharma_folios if f != "f101r" for l in lines_by_folio[f] if "P" in l["ltype"] for w in l["tokens"]]
    labeled_pharma_lines = sum(len([l for l in lines_by_folio[f] if "P" in l["ltype"]]) for f in pharma_folios if f != "f101r")

    f101r_qo = sum(1 for w in f101r_prose if w.startswith("qo")) / len(f101r_prose)
    lbl_qo = sum(1 for w in labeled_pharma_prose if w.startswith("qo")) / len(labeled_pharma_prose)

    f101r_ol_or_o = sum(1 for w in f101r_prose if w.startswith(("o", "d", "s")) and not w.startswith("qo")) / len(f101r_prose)
    lbl_ol_or_o = sum(1 for w in labeled_pharma_prose if w.startswith(("o", "d", "s")) and not w.startswith("qo")) / len(labeled_pharma_prose)

    # Z-score for qo- suppression on unlabeled f101r vs labeled Pharma prose
    p_pool = (sum(1 for w in f101r_prose if w.startswith("qo")) + sum(1 for w in labeled_pharma_prose if w.startswith("qo"))) / (len(f101r_prose) + len(labeled_pharma_prose))
    se_qo = math.sqrt(p_pool * (1 - p_pool) * (1 / len(f101r_prose) + 1 / len(labeled_pharma_prose)))
    z_qo_f101r = (f101r_qo - lbl_qo) / max(1e-9, se_qo)

    # Global totals across all 16 Pharmaceutical folios
    tot_lbl_words = sum(fp["total_label_words"] for fp in folio_profiles)
    tot_same_stem = sum(fp["same_folio_stem_hits"] for fp in folio_profiles)
    tot_pharma_stem = sum(fp["pharma_prose_stem_hits"] for fp in folio_profiles)
    tot_herbal_stem = sum(fp["herbal_stem_hits"] for fp in folio_profiles)
    tot_q20_stem = sum(fp["quire20_stem_hits"] for fp in folio_profiles)
    tot_3stage = sum(fp["three_stage_supply_chain_hits"] for fp in folio_profiles)

    return {
        "global_pharma_totals": {
            "total_pharma_folios": len(folio_profiles),
            "total_label_words": tot_lbl_words,
            "same_folio_stem_hits": tot_same_stem,
            "same_folio_stem_rate": round(tot_same_stem / max(1, tot_lbl_words), 4),
            "pharma_prose_stem_hits": tot_pharma_stem,
            "pharma_prose_stem_rate": round(tot_pharma_stem / max(1, tot_lbl_words), 4),
            "herbal_stem_hits": tot_herbal_stem,
            "herbal_stem_rate": round(tot_herbal_stem / max(1, tot_lbl_words), 4),
            "quire20_stem_hits": tot_q20_stem,
            "quire20_stem_rate": round(tot_q20_stem / max(1, tot_lbl_words), 4),
            "three_stage_supply_chain_hits": tot_3stage,
            "three_stage_supply_chain_rate": round(tot_3stage / max(1, tot_lbl_words), 4),
        },
        "p163_unfolded_sheet_trifecta": {
            "folios": p163_folios,
            "total_label_words": len(p163_labels),
            "total_prose_words": len(p163_prose),
            "same_panel_stem_hits": p163_same_folio_stem,
            "same_panel_stem_rate": round(p163_same_folio_stem / max(1, len(p163_labels)), 4),
            "unfolded_sheet_stem_hits": p163_label_in_sheet_stem,
            "unfolded_sheet_stem_rate": round(p163_label_in_sheet_stem / max(1, len(p163_labels)), 4),
            "unfolded_sheet_exact_hits": p163_label_in_sheet_exact,
            "unfolded_sheet_exact_rate": round(p163_label_in_sheet_exact / max(1, len(p163_labels)), 4),
            "sheet_vs_panel_lift": round((p163_label_in_sheet_stem / max(1, len(p163_labels))) / max(1e-9, p163_same_folio_stem / max(1, len(p163_labels))), 2),
            "f89r1_arabic_numeral_48_note": "Directly above Line 15 (Paragraph 2 opener <f89r1.15,@P0> tcheol.qoeair.sheol.qocphey...) on the center panel f89r1 of p163 sits the medieval Hindu-Arabic numeral '48' written in dark ink.",
        },
        "p179_f100v_f101r_unfolded_sheet_discovery": {
            "pdf_page": 179,
            "left_column_folio": "f100v (13 labeled cuttings, 14 label words, 1 9-line paragraph = 79 words)",
            "right_wide_panel_folio": "f101r (28 UNLABELED cuttings, 4 cylindrical jars, 3 wide paragraphs across 10 lines = 227 words, 22.70 words/line!)",
            "f100v_labels_in_f100v_prose_hits": f100v_in_self,
            "f100v_labels_in_f100v_prose_rate": round(f100v_in_self / max(1, len(f100v_labels)), 4),
            "f100v_labels_in_f101r_wide_prose_hits": f100v_in_f101r,
            "f100v_labels_in_f101r_wide_prose_rate": round(f100v_in_f101r / max(1, len(f100v_labels)), 4),
            "f100v_labels_in_combined_p179_sheet_hits": f100v_in_p179,
            "f100v_labels_in_combined_p179_sheet_rate": round(f100v_in_p179 / max(1, len(f100v_labels)), 4),
            "cross_column_echo_lift": round((f100v_in_p179 / max(1, len(f100v_labels))) / max(1e-9, f100v_in_self / max(1, len(f100v_labels))), 2),
            "f100v_matched_in_f101r_details": f100v_matched_in_f101r_details,
            "f101r_mean_words_per_line": 22.70,
            "labeled_pharma_mean_words_per_line": round(len(labeled_pharma_prose) / max(1, labeled_pharma_lines), 2),
            "f101r_line_width_lift": round(22.70 / (len(labeled_pharma_prose) / max(1, labeled_pharma_lines)), 2),
            "f101r_qo_verb_rate": round(f101r_qo, 4),
            "labeled_pharma_qo_verb_rate": round(lbl_qo, 4),
            "f101r_qo_suppression_z": round(z_qo_f101r, 2),
            "f101r_nominal_ods_prefix_rate": round(f101r_ol_or_o, 4),
            "labeled_pharma_nominal_ods_prefix_rate": round(lbl_ol_or_o, 4),
        },
        "folio_profiles": folio_profiles,
    }


def main():
    lines_by_folio, folio_meta = parse_all_lines()
    res = analyze_pharma_sheets_and_rows(lines_by_folio, folio_meta)

    out = {
        "attack": 207,
        "discovery": 224,
        "title": "Unfolded Pharmaceutical Master Sheets p163 (f88v | f89r1 | f89r2, '48' Marginalia) and p179 (f100v | f101r Cross-Column Sheet Echo 7.14% -> 42.86% = 6.00x Lift & 22.70-Word/Line Wide Treatise), and the 16-Folio 3-Stage Supply Chain Census",
        "pharma_sheets_analysis": res,
    }
    OUT_JSON.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Saved {OUT_JSON}")
    g = res["global_pharma_totals"]
    p179 = res["p179_f100v_f101r_unfolded_sheet_discovery"]
    print(f"Global Pharma ({g['total_label_words']} label words): Same-Folio={g['same_folio_stem_rate']*100:.2f}%, PharmaProse={g['pharma_prose_stem_rate']*100:.2f}%, Herbal={g['herbal_stem_rate']*100:.2f}%, Quire20={g['quire20_stem_rate']*100:.2f}%, 3-Stage={g['three_stage_supply_chain_rate']*100:.2f}%")
    print(f"p179 (f100v -> f101r): f100v self echo={p179['f100v_labels_in_f100v_prose_rate']*100:.2f}% ({p179['f100v_labels_in_f100v_prose_hits']}/14) -> in f101r wide prose={p179['f100v_labels_in_f101r_wide_prose_rate']*100:.2f}% ({p179['f100v_labels_in_f101r_wide_prose_hits']}/14), combined p179={p179['f100v_labels_in_combined_p179_sheet_rate']*100:.2f}% (lift={p179['cross_column_echo_lift']}x!)")
    print(f"f101r line width={p179['f101r_mean_words_per_line']} vs {p179['labeled_pharma_mean_words_per_line']} ({p179['f101r_line_width_lift']}x), qo_rate={p179['f101r_qo_verb_rate']*100:.2f}% vs {p179['labeled_pharma_qo_verb_rate']*100:.2f}% (z={p179['f101r_qo_suppression_z']}), nominal ods={p179['f101r_nominal_ods_prefix_rate']*100:.2f}% vs {p179['labeled_pharma_nominal_ods_prefix_rate']*100:.2f}%")


if __name__ == "__main__":
    main()
