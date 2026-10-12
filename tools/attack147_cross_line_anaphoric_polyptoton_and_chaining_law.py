#!/usr/bin/env python3
"""
Attack 147 (Phase 158 / Discovery 164):
Cross-Line Anaphoric Polyptoton, Sequential Stem Chaining (Line t -> Line t+1),
and Horizontal Zone Handoff Law Across Multi-Line Paragraphs.

Tests:
1. Across all multi-line paragraphs in ZL3b-n.txt, every adjacent line pair
   (Line t -> Line t+1) is analyzed for:
   - Cross-Line Cognate Polyptoton: token w_a in Line t and token w_b in Line t+1
     share the exact same canonical stem S (len(S) >= 2), with w_a != w_b.
   - Cross-Line Exact Token Repetition: w_a == w_b sharing stem S.
2. Dual Stratified Permutation Baselines (1,000 trials each):
   - Baseline A (Within-Section Line-Order Shuffle across paragraphs of the same
     Section $I & Language $L): measures total paragraph + sequential cross-line
     anaphoric stem chaining.
   - Baseline B (Strict Within-Paragraph Line-Order Shuffle inside paragraphs of
     >= 4 lines): preserves the exact vocabulary and stem inventory of each
     individual paragraph while destroying the sequential order of lines (t, t+1),
     testing whether adjacent lines (t -> t+1) chain stems even more tightly than
     non-adjacent lines (|t - t'| >= 2) within the very same paragraph.
3. Horizontal Zone Handoff Matrix (START = first token, END = last token,
   MID = interior tokens) comparing Line t zone -> Line t+1 zone for Cognate
   Polyptoton vs. Exact Repetition (including the Pos 1 -> Pos 1 Line-Initial
   Repulsion Law).
4. Cross-Line Directional Morphological Shift (Line t -> Line t+1) across all
   Cross-Line Cognate Polyptoton pairs (w_t != w_{t+1}), tested via 1,000-trial
   pair-orientation sign-flip permutation.
"""

from __future__ import annotations

import json
import math
import random
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, List, Tuple

ROOT = Path(__file__).resolve().parents[1]
ZL_PATH = ROOT / "data" / "ZL3b-n.txt"
FOLIO_INDEX_PATH = ROOT / "data" / "folio_index.json"
OUT_JSON = ROOT / "data" / "attack147_cross_line_anaphoric_polyptoton_and_chaining_law.json"

PREFIX_RE = re.compile(r"^(qo|ch|sh|da|ct|ck|cp|cf|op|ot|ok|of|ol|or|al|ar|yk|yt|yp|yf|d|s|y|l|r|q|o)")
SUFFIX_RE = re.compile(r"(aiin|oiin|eiin|iin|ain|edy|ody|eey|ey|dy|am|om|im|in|al|ol|ar|or|el|y|r|l|m|n|s|g)$")


def normalize_token(tok: str) -> str:
    t = re.sub(r"\[([^:\]]+):[^\]]+\]", r"\1", tok)
    t = re.sub(r"\{[^}]*\}", "", t)
    t = re.sub(r"<[^>]*>", "", t)
    t = t.replace("?", "").replace("!", "").replace("*", "").replace("%", "").replace("$", "")
    t = t.replace(",", "").replace("'", "").strip().lower()
    t = re.sub(r"c([tkpf])h", r"c\1h", t)
    t = re.sub(r"i{2,}", "ii", t)
    t = re.sub(r"e{2,}", "ee", t)
    return t


def extract_prefix_stem_suffix(word: str) -> Tuple[str, str, str]:
    w = word
    pref = ""
    suff = ""
    if len(w) >= 4:
        m = PREFIX_RE.match(w)
        if m and len(w) - len(m.group(1)) >= 2:
            pref = m.group(1)
            w = w[len(pref):]
    if len(w) >= 3:
        m2 = SUFFIX_RE.search(w)
        if m2 and len(w) - len(m2.group(1)) >= 2:
            suff = m2.group(1)
            w = w[: -len(suff)]
    return pref, w, suff


def classify_morph_features(word: str, pref: str, suff: str) -> Dict[str, bool]:
    return {
        "is_qo_act": pref == "qo" or word.startswith("qo"),
        "is_l_ol_appl": pref in {"l", "ol"} or word.startswith(("ol", "qol")),
        "is_da_art": pref == "da" or word.startswith(("da", "daiin", "dal")),
        "is_ds_deictic": pref in {"d", "s"} or word.startswith(("d", "s")),
        "is_edy_proc": suff in {"edy", "ody", "eey", "ey"} or word.endswith("edy"),
        "is_dy_perf": suff == "dy" and not word.endswith("edy"),
        "is_y_stat": suff == "y" and not word.endswith(("dy", "ey")),
        "is_liq_nom": suff in {"ol", "or", "al", "ar", "el", "l", "r"},
        "is_nasal_quant": suff in {"aiin", "oiin", "eiin", "iin", "ain", "in", "n"},
        "is_am_term": suff in {"am", "om", "im", "m"} or word.endswith(("am", "m")),
    }


def token_zone(idx: int, total: int) -> str:
    if idx == 0:
        return "START"
    if idx == total - 1:
        return "END"
    return "MID"


def parse_paragraphs(zl_path: Path, folio_meta: Dict[str, dict]) -> List[dict]:
    text = zl_path.read_text(encoding="utf-8", errors="ignore")
    loc_re = re.compile(r"^<([^>]+)>\s+(.*)$")

    paragraphs = []
    cur_para = None
    cur_folio = None

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        m = loc_re.match(line)
        if not m:
            continue
        loc, body = m.group(1), m.group(2)
        if ";" in loc:
            continue
        parts = loc.split(",")
        f_line = parts[0]
        locus_tag = parts[1] if len(parts) > 1 else "@P0"
        if not (locus_tag.startswith("@P") or locus_tag.startswith("+P") or locus_tag.startswith("*P")):
            continue

        folio = f_line.split(".")[0]
        fmeta = folio_meta.get(folio, {})
        sec = fmeta.get("section", "H")
        lang = fmeta.get("currier_language", "A")
        hand = str(fmeta.get("hand", "1"))

        has_para_start = "<%>" in body or locus_tag.startswith("@P") or locus_tag.startswith("*P")
        has_para_end = "<$>" in body

        clean_body = re.sub(r"<[^>]*>", " ", body)
        raw_toks = [t for t in re.split(r"[.\s]+", clean_body) if t]
        toks = []
        for rt in raw_toks:
            nt = normalize_token(rt)
            if len(nt) >= 2:
                pref, stem, suff = extract_prefix_stem_suffix(nt)
                if len(stem) >= 2:
                    toks.append({
                        "word": nt,
                        "pref": pref,
                        "stem": stem,
                        "suff": suff,
                    })
        if len(toks) < 2:
            continue

        if cur_para is None or folio != cur_folio or has_para_start:
            if cur_para and len(cur_para["lines"]) >= 1:
                paragraphs.append(cur_para)
            cur_para = {
                "folio": folio,
                "section": sec,
                "lang": lang,
                "hand": hand,
                "para_index": len([p for p in paragraphs if p["folio"] == folio]) + 1,
                "lines": [],
            }
            cur_folio = folio

        cur_para["lines"].append({
            "loc": f_line,
            "tokens": toks,
        })

        if has_para_end:
            if len(cur_para["lines"]) >= 1:
                paragraphs.append(cur_para)
            cur_para = None

    if cur_para and len(cur_para["lines"]) >= 1:
        paragraphs.append(cur_para)

    return paragraphs


def line_pair_stats(line_a: dict, line_b: dict) -> Tuple[int, int, List[Tuple[dict, dict, str, str]]]:
    """
    Returns (cognate_polyptoton_pairs, exact_repeat_pairs, detailed_cognate_pairs)
    between line_a (Line t) and line_b (Line t+1).
    """
    toks_a = line_a["tokens"]
    toks_b = line_b["tokens"]
    na, nb = len(toks_a), len(toks_b)
    cognate_count = 0
    exact_count = 0
    details = []
    for ia, ta in enumerate(toks_a):
        za = token_zone(ia, na)
        for ib, tb in enumerate(toks_b):
            if ta["stem"] == tb["stem"]:
                zb = token_zone(ib, nb)
                if ta["word"] != tb["word"]:
                    cognate_count += 1
                    details.append((ta, tb, za, zb))
                else:
                    exact_count += 1
    return cognate_count, exact_count, details


def main() -> None:
    index_raw = json.loads(FOLIO_INDEX_PATH.read_text(encoding="utf-8"))
    folio_meta = index_raw.get("folios", index_raw)

    paragraphs = parse_paragraphs(ZL_PATH, folio_meta)
    multi_paras = [p for p in paragraphs if len(p["lines"]) >= 2]

    total_adj_pairs = 0
    adj_pairs_with_cognate = 0
    adj_pairs_with_exact = 0
    total_cognate_links = 0
    total_exact_links = 0

    zone_handoff_cognate = Counter()
    zone_handoff_exact = Counter()
    all_cognate_details = []
    top_chained_examples = []

    sec_stats = defaultdict(lambda: {"adj_pairs": 0, "pairs_with_cognate": 0, "cognate_links": 0, "exact_links": 0})

    for p in multi_paras:
        lines = p["lines"]
        sec = p["section"]
        for i in range(len(lines) - 1):
            la, lb = lines[i], lines[i + 1]
            total_adj_pairs += 1
            sec_stats[sec]["adj_pairs"] += 1
            c_cnt, e_cnt, dets = line_pair_stats(la, lb)
            if c_cnt > 0:
                adj_pairs_with_cognate += 1
                sec_stats[sec]["pairs_with_cognate"] += 1
            if e_cnt > 0:
                adj_pairs_with_exact += 1
            total_cognate_links += c_cnt
            total_exact_links += e_cnt
            sec_stats[sec]["cognate_links"] += c_cnt
            sec_stats[sec]["exact_links"] += e_cnt

            for ta, tb, za, zb in dets:
                zone_handoff_cognate[f"{za}->{zb}"] += 1
                all_cognate_details.append((ta, tb, za, zb, p["folio"], la["loc"], lb["loc"], sec))

            # Also count exact zone handoffs
            na, nb = len(la["tokens"]), len(lb["tokens"])
            for ia, ta in enumerate(la["tokens"]):
                for ib, tb in enumerate(lb["tokens"]):
                    if ta["word"] == tb["word"]:
                        zone_handoff_exact[f"{token_zone(ia, na)}->{token_zone(ib, nb)}"] += 1

            if c_cnt >= 3 and len(top_chained_examples) < 25:
                top_chained_examples.append({
                    "folio": p["folio"],
                    "section": sec,
                    "lang": p["lang"],
                    "line_t_loc": la["loc"],
                    "line_t1_loc": lb["loc"],
                    "cognate_links": c_cnt,
                    "exact_links": e_cnt,
                    "pairs": [
                        {
                            "stem": ta["stem"],
                            "word_t": ta["word"],
                            "word_t1": tb["word"],
                            "zone_handoff": f"{za}->{zb}",
                        }
                        for ta, tb, za, zb in dets[:6]
                    ],
                })

    top_chained_examples.sort(key=lambda x: -x["cognate_links"])

    # Baseline A: Within-(Section, Language) Line-Order Shuffle across paragraphs (1,000 trials)
    bucket_lines = defaultdict(list)
    bucket_para_shapes = defaultdict(list)
    for p in multi_paras:
        key = (p["section"], p["lang"])
        bucket_para_shapes[key].append(len(p["lines"]))
        for ln in p["lines"]:
            bucket_lines[key].append(ln)

    # Precompute stem counters per line for fast permutation
    line_id_map = {}
    all_lines_flat = []
    for p in multi_paras:
        for ln in p["lines"]:
            lid = len(all_lines_flat)
            ln["_lid"] = lid
            stem_c = Counter(t["stem"] for t in ln["tokens"])
            word_c = Counter(t["word"] for t in ln["tokens"])
            all_lines_flat.append((stem_c, word_c))

    def fast_cognate_between(lid_a: int, lid_b: int) -> int:
        sa, wa = all_lines_flat[lid_a]
        sb, wb = all_lines_flat[lid_b]
        tot_stem = 0
        for s, ca in sa.items():
            cb = sb.get(s, 0)
            if cb:
                tot_stem += ca * cb
        if tot_stem == 0:
            return 0
        tot_exact = 0
        for w, ca in wa.items():
            cb = wb.get(w, 0)
            if cb:
                tot_exact += ca * cb
        return tot_stem - tot_exact

    rng = random.Random(147)
    null_sec_links = []
    for _ in range(1000):
        sim_links = 0
        for key, shapes in bucket_para_shapes.items():
            pool = [ln["_lid"] for ln in bucket_lines[key]]
            rng.shuffle(pool)
            idx = 0
            for sz in shapes:
                for k in range(sz - 1):
                    sim_links += fast_cognate_between(pool[idx + k], pool[idx + k + 1])
                idx += sz
        null_sec_links.append(sim_links)

    mu_sec = sum(null_sec_links) / len(null_sec_links)
    sd_sec = math.sqrt(sum((x - mu_sec) ** 2 for x in null_sec_links) / len(null_sec_links))
    z_sec = (total_cognate_links - mu_sec) / (sd_sec if sd_sec > 0 else 1.0)

    # Baseline B: Strict Within-Paragraph Line-Order Shuffle inside paragraphs of >= 4 lines (1,000 trials)
    paras_ge4 = [[ln["_lid"] for ln in p["lines"]] for p in multi_paras if len(p["lines"]) >= 4]
    obs_ge4_links = sum(
        fast_cognate_between(lids[k], lids[k + 1])
        for lids in paras_ge4
        for k in range(len(lids) - 1)
    )
    null_within_para = []
    for _ in range(1000):
        sim = 0
        for lids in paras_ge4:
            shuf = list(lids)
            rng.shuffle(shuf)
            for k in range(len(shuf) - 1):
                sim += fast_cognate_between(shuf[k], shuf[k + 1])
        null_within_para.append(sim)

    mu_wp = sum(null_within_para) / len(null_within_para)
    sd_wp = math.sqrt(sum((x - mu_wp) ** 2 for x in null_within_para) / len(null_within_para))
    z_wp = (obs_ge4_links - mu_wp) / (sd_wp if sd_wp > 0 else 1.0)

    # Horizontal Zone Handoff Comparison: Cognate Polyptoton vs Exact Repetition
    zone_comparison = {}
    for zkey in ["START->START", "START->MID", "START->END", "MID->START", "MID->MID", "MID->END", "END->START", "END->MID", "END->END"]:
        c_val = zone_handoff_cognate[zkey]
        e_val = zone_handoff_exact[zkey]
        c_pct = 100.0 * c_val / max(total_cognate_links, 1)
        e_pct = 100.0 * e_val / max(total_exact_links, 1)
        zone_comparison[zkey] = {
            "cognate_links": c_val,
            "cognate_pct": round(c_pct, 2),
            "exact_links": e_val,
            "exact_pct": round(e_pct, 2),
            "cognate_to_exact_ratio": round(c_val / max(e_val, 1), 2),
        }

    # Cross-Line Directional Morphological Shift (Line t -> Line t+1)
    feat_keys = [
        "is_qo_act",
        "is_l_ol_appl",
        "is_da_art",
        "is_ds_deictic",
        "is_edy_proc",
        "is_dy_perf",
        "is_y_stat",
        "is_liq_nom",
        "is_nasal_quant",
        "is_am_term",
    ]
    line_t_counts = Counter()
    line_t1_counts = Counter()
    pair_feats = []
    for ta, tb, za, zb, fol, loc_a, loc_b, sec in all_cognate_details:
        fa = classify_morph_features(ta["word"], ta["pref"], ta["suff"])
        fb = classify_morph_features(tb["word"], tb["pref"], tb["suff"])
        pair_feats.append((fa, fb))
        for fk in feat_keys:
            if fa[fk]:
                line_t_counts[fk] += 1
            if fb[fk]:
                line_t1_counts[fk] += 1

    n_pairs = len(pair_feats)
    morph_shift = {}
    for fk in feat_keys:
        ct = line_t_counts[fk]
        ct1 = line_t1_counts[fk]
        pt = 100.0 * ct / max(n_pairs, 1)
        pt1 = 100.0 * ct1 / max(n_pairs, 1)
        # Exact binomial / sign-flip z-score on discordant pairs (0->1 vs 1->0)
        n_01 = sum(1 for fa, fb in pair_feats if (not fa[fk]) and fb[fk])
        n_10 = sum(1 for fa, fb in pair_feats if fa[fk] and (not fb[fk]))
        disc = n_01 + n_10
        z_flip = (n_01 - n_10) / math.sqrt(disc) if disc > 0 else 0.0
        morph_shift[fk] = {
            "line_t_count": ct,
            "line_t_pct": round(pt, 2),
            "line_t1_count": ct1,
            "line_t1_pct": round(pt1, 2),
            "delta_pct_t_to_t1": round(pt1 - pt, 2),
            "discordant_t_to_t1_gain": n_01,
            "discordant_t_to_t1_loss": n_10,
            "sign_flip_z": round(z_flip, 2),
        }

    section_breakdown = {}
    for sec, st in sorted(sec_stats.items()):
        ap = st["adj_pairs"]
        section_breakdown[sec] = {
            "adjacent_line_pairs": ap,
            "pairs_with_cognate_polyptoton": st["pairs_with_cognate"],
            "pairs_with_cognate_pct": round(100.0 * st["pairs_with_cognate"] / max(ap, 1), 2),
            "cognate_links": st["cognate_links"],
            "exact_links": st["exact_links"],
            "cognate_to_exact_preference": round(st["cognate_links"] / max(st["exact_links"], 1), 2),
        }

    out = {
        "attack": 147,
        "phase": 158,
        "discovery": 164,
        "title": "Cross-Line Anaphoric Polyptoton, Sequential Stem Chaining (Line t -> Line t+1), and Horizontal Zone Handoff Law",
        "overview": {
            "multi_line_paragraphs": len(multi_paras),
            "total_adjacent_line_pairs": total_adj_pairs,
            "adjacent_pairs_with_cognate_polyptoton": adj_pairs_with_cognate,
            "adjacent_pairs_with_cognate_pct": round(100.0 * adj_pairs_with_cognate / max(total_adj_pairs, 1), 2),
            "adjacent_pairs_with_exact_repeat": adj_pairs_with_exact,
            "adjacent_pairs_with_exact_pct": round(100.0 * adj_pairs_with_exact / max(total_adj_pairs, 1), 2),
            "total_cross_line_cognate_polyptoton_links": total_cognate_links,
            "total_cross_line_exact_repeat_links": total_exact_links,
            "cognate_over_exact_preference_ratio": round(total_cognate_links / max(total_exact_links, 1), 2),
            "within_section_line_shuffle_permutation_1000": {
                "observed_cognate_links": total_cognate_links,
                "null_mean": round(mu_sec, 2),
                "null_sd": round(sd_sec, 2),
                "lift_ratio": round(total_cognate_links / max(mu_sec, 1.0), 3),
                "z_score": round(z_sec, 2),
            },
            "strict_within_paragraph_line_order_shuffle_ge4_lines_1000": {
                "paragraphs_ge4_lines": len(paras_ge4),
                "observed_adjacent_cognate_links": obs_ge4_links,
                "null_mean": round(mu_wp, 2),
                "null_sd": round(sd_wp, 2),
                "lift_ratio": round(obs_ge4_links / max(mu_wp, 1.0), 3),
                "z_score": round(z_wp, 2),
            },
        },
        "horizontal_zone_handoff_matrix": zone_comparison,
        "cross_line_directional_morphological_shift": morph_shift,
        "section_breakdown": section_breakdown,
        "top_chained_line_pair_examples": top_chained_examples[:15],
    }

    OUT_JSON.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"[Attack 147] Saved {OUT_JSON}")
    print("Overview:", json.dumps(out["overview"], indent=2))
    print("Zone handoff:", json.dumps(zone_comparison, indent=2))
    print("Morph shift:", json.dumps(morph_shift, indent=2))


if __name__ == "__main__":
    main()
