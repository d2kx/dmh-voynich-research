#!/usr/bin/env python3
"""
Attack 34 (Phase 45): Late Interleaved Herbal Bridge (f87r-v, f90r1-f96v)
& The Quire G/H Marginal/Circular Key Sequences (f49v, f57v, f66r).

Tests two major structural systems bridging the Herbal, Cosmological, and Pharmaceutical sections:
1. Part A — Codicological Sandwich & Lexical Bridge (Late Herbals f87r-v, f90r1-f96v -> Pharma f88-f89, f99-f102):
   - Late Herbal folios in Quire O (f87r-v) and Quire Q (f90r1-f96v) are physically interleaved
     with the two Pharmaceutical Jar/Root Formularies: Quire P (f88r-f89v2) and Quire T (f99r-f102v2).
   - Tests whether Late Herbal folios share a significantly higher fraction of rare herbal stems
     (1 <= herbal_df <= 3) and @Lf/@Lc specimen labels with the Pharmaceutical Formularies than
     Early Monographic Herbals (f1r-f57r) do (1,000-trial language-stratified permutation test).
2. Part B — The Three Marginal/Circular Single-Glyph Key Sequences (f49v, f57v, f66r) & Quire H Outer Bifolium:
   - Analyzes the only three loci in the Voynich Manuscript containing structured single-glyph
     key/index sequences:
     (a) f49v (Quire G, Hand 1): 26 vertical left-margin glyphs aligned 1-to-1 with 26 prose lines,
         exhibiting a 3x periodic 6-glyph cycle: [f/p] - o - [r/@192;] - y - e - @140;
     (b) f57v (Quire H outer bifolium, Hand 1): 4x repeating 17-glyph circular ring (@Cc.3):
         o - l - d - r - v - x - k - m - [f/p] - @169;v - t - r - @170; - @171; - y - [I/c] - @172;
     (c) f66r (Quire H outer bifolium conjugate leaf to f57, Hand 5): 15 left-margin index words (@L0.1-15)
         + 34 vertical single-glyph key symbols (@L0.16-49) sharing the rare glyph inventory
         {@169;, @172;, x, f, p, c, l, r, t, o, d, y} with its conjugate leaf f57v, plus same-folio
         stem recurrence between the 15 marginal words and the 5 prose paragraphs of f66r.
"""

from __future__ import annotations

import json
import math
import random
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, List, Set

ROOT = Path(__file__).resolve().parents[1]
ZL_PATH = ROOT / "data" / "ZL3b-n.txt"
INDEX_PATH = ROOT / "data" / "folio_index.json"
OUT_JSON = ROOT / "data" / "attack34_small_plant_quire_p_q_bridge_analysis.json"


def clean_tok(t: str) -> str:
    t = re.sub(r"<!.*?>", "", t)
    t = re.sub(r"<[^>]+>", "", t)
    t = re.sub(r"\[([^:\]]+):[^\]]+\]", r"\1", t)
    t = t.replace("[", "").replace("]", "").replace("?", "").replace("!", "").replace("*", "")
    t = t.replace(",", "").replace("'", "").strip()
    return t


def canonical_stem(w: str) -> str:
    s = w
    if s.startswith("qo") and len(s) > 3:
        s = s[2:]
    elif s.startswith(("ch", "sh")) and len(s) > 4:
        pass
    elif s.startswith(("o", "d", "s", "y")) and len(s) > 4:
        s = s[1:]
    s = re.sub(r"i{2,}n$", "in", s)
    s = re.sub(r"e{2,}", "e", s)
    if s.startswith("cth"):
        s = "kh" + s[3:]
    elif s.startswith("cph"):
        s = "ph" + s[3:]
    elif s.startswith("ckh"):
        s = "kh" + s[3:]
    elif s.startswith("cfh"):
        s = "fh" + s[3:]
    return s


def strip_gallows(w: str) -> str:
    for g in ("kch", "tch", "pch", "fch", "cth", "ckh", "cph", "cfh", "k", "t", "p", "f"):
        if w.startswith(g) and len(w) - len(g) >= 2:
            return w[len(g):]
    if w.startswith(("ok", "ot", "op", "of", "yk", "yt", "yp", "yf")) and len(w) >= 4:
        return "o" + w[2:]
    return w


def parse_manuscript() -> Dict[str, Dict]:
    with open(INDEX_PATH, "r", encoding="utf-8") as f:
        idx = json.load(f)
    folio_meta = idx.get("folios", {})

    folios: Dict[str, Dict] = {}
    current_folio = None
    header_meta: Dict[str, str] = {}

    line_re = re.compile(r"^<([^.>]+)\.([^,>]+),([^>]+)>\s*(.*)$")
    page_re = re.compile(r"^<f[0-9]+[rv][0-9]*>\s*<!\s*(.*?)>")

    with open(ZL_PATH, "r", encoding="utf-8") as f:
        for raw in f:
            line = raw.strip()
            if not line:
                continue
            pm = page_re.match(line)
            if pm:
                f_m = re.match(r"^<(f[0-9]+[rv][0-9]*)>", line)
                if f_m:
                    current_folio = f_m.group(1)
                    meta_str = pm.group(1)
                    header_meta = dict(re.findall(r"\$([A-Z])=([A-Za-z0-9]+)", meta_str))
                    f_info = folio_meta.get(current_folio, {})
                    folios[current_folio] = {
                        "folio": current_folio,
                        "section": header_meta.get("I", f_info.get("section", "?")),
                        "language": header_meta.get("L", f_info.get("currier_language", "?")),
                        "hand": header_meta.get("H", f_info.get("hand", "?")),
                        "quire": header_meta.get("Q", f_info.get("quire", "?")),
                        "prose_tokens": [],
                        "label_tokens": [],
                        "lines": [],
                        "paragraphs": 0,
                        "intrusions": 0,
                    }
                continue

            if line.startswith("#"):
                continue

            lm = line_re.match(line)
            if not lm or not current_folio or current_folio not in folios:
                continue

            _, loc_id, ltype, body = lm.groups()
            if "<%>" in body:
                folios[current_folio]["paragraphs"] += 1
            if "<->" in body:
                folios[current_folio]["intrusions"] += 1

            body_clean = re.sub(r"<!.*?>", "", body)
            raw_toks = re.split(r"[.\s]+", body_clean)
            toks = [clean_tok(t) for t in raw_toks]
            toks = [t for t in toks if t and not t.startswith("<")]
            if not toks:
                continue

            folios[current_folio]["lines"].append({
                "loc_id": loc_id,
                "ltype": ltype,
                "tokens": toks,
                "has_para_start": "<%>" in body,
                "has_intrusion": "<->" in body,
            })

            if "@L" in ltype or "+L" in ltype or "*L" in ltype or ltype.startswith("L"):
                folios[current_folio]["label_tokens"].extend(toks)
            else:
                folios[current_folio]["prose_tokens"].extend(toks)

    return folios


def classify_folio_stratum(folio: str, fdata: Dict) -> str:
    m = re.match(r"^f([0-9]+)([rv])([0-9]*)$", folio)
    if not m:
        return "OTHER"
    fnum = int(m.group(1))
    sec = fdata["section"]
    lang = fdata["language"]

    if folio in ("f65r", "f65v", "f66r", "f66v"):
        return "QUIRE_H_HYBRID_65_66"
    if fnum <= 57 and sec == "H":
        return f"EARLY_HERBAL_{lang}"
    if (fnum == 87 or (90 <= fnum <= 96)) and sec == "H":
        return f"LATE_HERBAL_{lang}"
    if sec == "P" or fnum in (88, 89, 99, 100, 101, 102):
        return "PHARMA_FORMULARY"
    if fnum >= 103 and sec in ("S", "T"):
        return "STARRED_RECIPES_Q20"
    if sec == "B":
        return "BALNEOLOGICAL"
    return f"OTHER_{sec}"


def compute_morph_profile(tokens: List[str]) -> Dict[str, float]:
    n = len(tokens)
    if n == 0:
        return {}
    qo = sum(1 for w in tokens if w.startswith(("qo", "qok", "qot")))
    ch_sh = sum(1 for w in tokens if w.startswith(("ch", "sh")) or "ch" in w or "sh" in w)
    ed_dy = sum(1 for w in tokens if w.endswith(("edy", "dy")))
    aiin = sum(1 for w in tokens if re.search(r"i+n$", w))
    ol_or_ar_al = sum(1 for w in tokens if w.endswith(("ol", "or", "ar", "al")))
    am_om = sum(1 for w in tokens if w.endswith(("am", "om", "aim", "oim")))
    daiin = sum(1 for w in tokens if w in ("daiin", "dain", "daiiin"))
    ol_dar_dal = sum(1 for w in tokens if w in ("ol", "or", "ar", "al", "dar", "dal", "dol", "chol", "shol"))

    return {
        "n_tokens": n,
        "qo_rate": round(qo / n, 4),
        "ch_sh_rate": round(ch_sh / n, 4),
        "edy_dy_rate": round(ed_dy / n, 4),
        "aiin_rate": round(aiin / n, 4),
        "liquid_suffix_rate": round(ol_or_ar_al / n, 4),
        "am_om_rate": round(am_om / n, 4),
        "daiin_rate": round(daiin / n, 4),
        "noun_functor_rate": round(ol_dar_dal / n, 4),
        "mean_word_len": round(sum(len(w) for w in tokens) / n, 3),
    }


def main() -> None:
    folios = parse_manuscript()

    strata_folios: Dict[str, List[str]] = defaultdict(list)
    for f, fd in folios.items():
        st = classify_folio_stratum(f, fd)
        fd["stratum"] = st
        strata_folios[st].append(f)

    # 1. Compute morphological profiles per stratum
    strata_profiles = {}
    for st in sorted(strata_folios.keys()):
        toks = []
        lbls = []
        n_para = 0
        n_intr = 0
        for f in strata_folios[st]:
            toks.extend(folios[f]["prose_tokens"])
            lbls.extend(folios[f]["label_tokens"])
            n_para += folios[f]["paragraphs"]
            n_intr += folios[f]["intrusions"]
        prof = compute_morph_profile(toks)
        prof["n_folios"] = len(strata_folios[st])
        prof["n_labels"] = len(lbls)
        prof["n_paragraphs"] = n_para
        prof["n_intrusions"] = n_intr
        prof["intrusions_per_folio"] = round(n_intr / max(1, len(strata_folios[st])), 2)
        strata_profiles[st] = prof

    # 2. Part A: Lexical & Rare-Stem Bridge between Late Herbals (f87, f90-f96) and Pharma Formularies (f88-f89, f99-f102)
    pharma_folios = strata_folios["PHARMA_FORMULARY"]
    pharma_prose_stems: Counter = Counter()
    pharma_label_stems: Counter = Counter()
    pharma_folio_by_stem: Dict[str, Set[str]] = defaultdict(set)
    pharma_label_folio_by_stem: Dict[str, Set[str]] = defaultdict(set)

    for f in pharma_folios:
        for w in folios[f]["prose_tokens"]:
            cs = canonical_stem(w)
            if len(cs) >= 3:
                pharma_prose_stems[cs] += 1
                pharma_folio_by_stem[cs].add(f)
        for w in folios[f]["label_tokens"]:
            cs = canonical_stem(w)
            if len(cs) >= 3:
                pharma_label_stems[cs] += 1
                pharma_label_folio_by_stem[cs].add(f)

    global_df: Counter = Counter()
    herbal_df: Counter = Counter()
    all_herbal_folios = (
        strata_folios["EARLY_HERBAL_A"]
        + strata_folios["EARLY_HERBAL_B"]
        + strata_folios["LATE_HERBAL_A"]
        + strata_folios["LATE_HERBAL_B"]
    )
    for f, fd in folios.items():
        stems = {canonical_stem(w) for w in fd["prose_tokens"] + fd["label_tokens"] if len(canonical_stem(w)) >= 3}
        for s in stems:
            global_df[s] += 1
            if f in all_herbal_folios:
                herbal_df[s] += 1

    def folio_pharma_bridge_metrics(f: str) -> Dict:
        toks = folios[f]["prose_tokens"]
        stems = [canonical_stem(w) for w in toks if len(canonical_stem(w)) >= 3]
        unique_stems = set(stems)
        rare_herbal_stems = {s for s in unique_stems if 1 <= herbal_df[s] <= 3}
        rare_shared_pharma_prose = {s for s in rare_herbal_stems if s in pharma_prose_stems}
        shared_pharma_labels = {s for s in unique_stems if s in pharma_label_stems and global_df[s] <= 12}
        headword = ""
        head_base = ""
        for ln in folios[f]["lines"]:
            if ln["tokens"] and "@L" not in ln["ltype"] and "*L" not in ln["ltype"]:
                headword = ln["tokens"][0]
                head_base = canonical_stem(strip_gallows(headword))
                break
        head_in_pharma = head_base in pharma_prose_stems or head_base in pharma_label_stems
        return {
            "folio": f,
            "stratum": folios[f]["stratum"],
            "language": folios[f]["language"],
            "hand": folios[f]["hand"],
            "quire": folios[f]["quire"],
            "n_tokens": len(toks),
            "n_unique_stems": len(unique_stems),
            "n_rare_herbal_stems": len(rare_herbal_stems),
            "n_rare_shared_pharma_prose": len(rare_shared_pharma_prose),
            "rare_shared_rate": round(len(rare_shared_pharma_prose) / max(1, len(rare_herbal_stems)), 4),
            "n_shared_pharma_labels": len(shared_pharma_labels),
            "shared_pharma_label_rate_per_100": round(100.0 * len(shared_pharma_labels) / max(1, len(toks)), 3),
            "rare_shared_stems": sorted(
                [
                    {
                        "stem": s,
                        "herbal_df": herbal_df[s],
                        "pharma_folios": sorted(pharma_folio_by_stem[s]),
                        "pharma_label_folios": sorted(pharma_label_folio_by_stem[s]),
                    }
                    for s in (rare_shared_pharma_prose | shared_pharma_labels)
                ],
                key=lambda x: (x["herbal_df"], x["stem"]),
            ),
            "headword": headword,
            "head_base": head_base,
            "head_in_pharma": head_in_pharma,
        }

    herbal_bridge_details = {f: folio_pharma_bridge_metrics(f) for f in all_herbal_folios}

    group_summaries = {}
    for st in ("EARLY_HERBAL_A", "LATE_HERBAL_A", "EARLY_HERBAL_B", "LATE_HERBAL_B"):
        fs = strata_folios[st]
        metrics = [herbal_bridge_details[f] for f in fs]
        tot_rare = sum(m["n_rare_herbal_stems"] for m in metrics)
        tot_shared = sum(m["n_rare_shared_pharma_prose"] for m in metrics)
        tot_lbl_shared = sum(m["n_shared_pharma_labels"] for m in metrics)
        tot_toks = sum(m["n_tokens"] for m in metrics)
        group_summaries[st] = {
            "n_folios": len(fs),
            "total_tokens": tot_toks,
            "mean_tokens_per_folio": round(tot_toks / max(1, len(fs)), 2),
            "total_rare_herbal_stems": tot_rare,
            "total_rare_shared_pharma": tot_shared,
            "rare_shared_fraction": round(tot_shared / max(1, tot_rare), 4),
            "mean_folio_rare_shared_rate": round(
                sum(m["rare_shared_rate"] for m in metrics) / max(1, len(metrics)), 4
            ),
            "shared_pharma_labels_per_100_toks": round(100.0 * tot_lbl_shared / max(1, tot_toks), 3),
        }

    rng = random.Random(42)
    a_folios = strata_folios["EARLY_HERBAL_A"] + strata_folios["LATE_HERBAL_A"]
    b_folios = strata_folios["EARLY_HERBAL_B"] + strata_folios["LATE_HERBAL_B"]
    n_late_a = len(strata_folios["LATE_HERBAL_A"])
    n_late_b = len(strata_folios["LATE_HERBAL_B"])

    obs_late_folios = strata_folios["LATE_HERBAL_A"] + strata_folios["LATE_HERBAL_B"]
    obs_early_folios = strata_folios["EARLY_HERBAL_A"] + strata_folios["EARLY_HERBAL_B"]

    def mean_rare_rate(fs: List[str]) -> float:
        return sum(herbal_bridge_details[f]["rare_shared_rate"] for f in fs) / max(1, len(fs))

    obs_diff = mean_rare_rate(obs_late_folios) - mean_rare_rate(obs_early_folios)
    null_diffs = []
    for _ in range(1000):
        perm_late_a = set(rng.sample(a_folios, n_late_a))
        perm_late_b = set(rng.sample(b_folios, n_late_b))
        perm_late = list(perm_late_a | perm_late_b)
        perm_early = [f for f in (a_folios + b_folios) if f not in (perm_late_a | perm_late_b)]
        null_diffs.append(mean_rare_rate(perm_late) - mean_rare_rate(perm_early))

    null_mean = sum(null_diffs) / len(null_diffs)
    null_std = math.sqrt(sum((x - null_mean) ** 2 for x in null_diffs) / len(null_diffs)) or 1e-9
    z_bridge = (obs_diff - null_mean) / null_std
    p_bridge = sum(1 for x in null_diffs if x >= obs_diff) / len(null_diffs)

    late_herbal_folio_reports = [herbal_bridge_details[f] for f in sorted(obs_late_folios)]

    # 3. Part B: The Three Single-Glyph Marginal/Circular Key Sequences (f49v, f57v, f66r)
    f49v_margin_seq = folios["f49v"]["label_tokens"] if "f49v" in folios else []
    f57v_ring3_seq = []
    if "f57v" in folios:
        for ln in folios["f57v"]["lines"]:
            if ln["loc_id"] == "3":
                f57v_ring3_seq = ln["tokens"]
                break

    f66r_word_labels = folios["f66r"]["label_tokens"][:15] if "f66r" in folios else []
    f66r_glyph_seq = folios["f66r"]["label_tokens"][15:49] if "f66r" in folios else []
    f66r_bottom_labels = folios["f66r"]["label_tokens"][49:] if "f66r" in folios else []

    # Shared single-glyph inventory between f57v Ring 3 and f66r vertical glyph sequence (conjugate bifolium leaves of Quire H!)
    set_57v = {g.replace("v", "") if g.startswith("@169;") else g for g in f57v_ring3_seq}
    set_66r = set(f66r_glyph_seq)
    shared_57v_66r = sorted(set_57v & set_66r)

    # Test same-folio stem recurrence between f66r's 15 marginal words (@L0.1-15) and f66r's prose tokens (266 words)
    f66r_prose_stems = {canonical_stem(w) for w in folios["f66r"]["prose_tokens"]}
    f66r_word_matches = []
    for w in f66r_word_labels:
        cs = canonical_stem(w)
        stripped = canonical_stem(strip_gallows(w))
        matched_prose_words = [
            pw for pw in folios["f66r"]["prose_tokens"]
            if canonical_stem(pw) == cs or canonical_stem(strip_gallows(pw)) == stripped
        ]
        f66r_word_matches.append({
            "margin_word": w,
            "canonical_stem": cs,
            "stripped_stem": stripped,
            "matches_in_f66r_prose": sorted(set(matched_prose_words)),
            "match_count": len(matched_prose_words),
        })

    obs_f66r_matches = sum(1 for m in f66r_word_matches if m["match_count"] > 0)
    # Null test: draw 1,000 random Currier B folios of comparable length or random 15-word label sets from Currier B labels
    all_b_folios = [f for f, fd in folios.items() if fd["language"] == "B" and len(fd["prose_tokens"]) >= 100 and f != "f66r"]
    null_f66r_counts = []
    for f_other in all_b_folios:
        other_toks = folios[f_other]["prose_tokens"]
        c = 0
        for w in f66r_word_labels:
            cs = canonical_stem(w)
            stripped = canonical_stem(strip_gallows(w))
            if any(canonical_stem(pw) == cs or canonical_stem(strip_gallows(pw)) == stripped for pw in other_toks):
                c += 1
        null_f66r_counts.append(c)
    f66r_null_mean = sum(null_f66r_counts) / max(1, len(null_f66r_counts))
    f66r_null_std = math.sqrt(sum((x - f66r_null_mean) ** 2 for x in null_f66r_counts) / max(1, len(null_f66r_counts))) or 1e-9
    z_f66r_margin = (obs_f66r_matches - f66r_null_mean) / f66r_null_std

    key_sequence_analysis = {
        "f49v_vertical_margin_key": {
            "folio": "f49v",
            "quire": "G",
            "hand": "1",
            "n_glyphs": len(f49v_margin_seq),
            "sequence": f49v_margin_seq,
            "repeating_6glyph_cycles": [
                {"lines": "1..11 (odd)", "glyphs": f49v_margin_seq[0:6]},
                {"lines": "13..15 (odd, bridge)", "glyphs": f49v_margin_seq[6:8]},
                {"lines": "17..27 (odd)", "glyphs": f49v_margin_seq[8:14]},
                {"lines": "29..41 (odd)", "glyphs": f49v_margin_seq[14:21]},
                {"lines": "43..51 (odd, coda)", "glyphs": f49v_margin_seq[21:26]},
            ],
        },
        "f57v_circular_ring3_key": {
            "folio": "f57v",
            "quire": "H (outer bifolium with f66)",
            "hand": "1",
            "n_glyphs": len(f57v_ring3_seq),
            "four_17glyph_quadrants": [
                f57v_ring3_seq[0:17],
                f57v_ring3_seq[17:34],
                f57v_ring3_seq[34:51],
                f57v_ring3_seq[51:68],
            ],
            "top_label_dairal_in_f66r_prose": "dairal" in folios["f66r"]["prose_tokens"],
        },
        "f66r_dual_margin_key_and_index": {
            "folio": "f66r",
            "quire": "H (outer bifolium conjugate leaf with f57)",
            "hand": "5",
            "word_index_column_15": f66r_word_matches,
            "word_index_same_folio_matches": obs_f66r_matches,
            "word_index_null_mean_across_B_folios": round(f66r_null_mean, 3),
            "word_index_z_score": round(z_f66r_margin, 2),
            "single_glyph_column_34": f66r_glyph_seq,
            "bottom_corner_labels_3": f66r_bottom_labels,
            "shared_glyphs_with_f57v_ring3": shared_57v_66r,
            "shared_glyph_count": len(shared_57v_66r),
        },
    }

    out = {
        "strata_profiles": strata_profiles,
        "herbal_to_pharma_bridge_summary": {
            "group_summaries": group_summaries,
            "observed_late_mean_rare_shared_rate": round(mean_rare_rate(obs_late_folios), 4),
            "observed_early_mean_rare_shared_rate": round(mean_rare_rate(obs_early_folios), 4),
            "observed_diff": round(obs_diff, 4),
            "null_mean_diff": round(null_mean, 4),
            "null_std_diff": round(null_std, 4),
            "z_score": round(z_bridge, 2),
            "p_value": round(p_bridge, 4),
        },
        "late_herbal_folio_reports": late_herbal_folio_reports,
        "key_sequence_analysis": key_sequence_analysis,
    }

    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)

    print("=== ATTACK 34: LATE HERBAL BRIDGE & QUIRE G/H MARGINAL KEY SEQUENCES ===")
    print(
        f"Part A — Late vs Early Herbal Rare Pharma Stem Bridge: "
        f"obs_late={mean_rare_rate(obs_late_folios):.4f} vs obs_early={mean_rare_rate(obs_early_folios):.4f} "
        f"(z={z_bridge:+.2f}, p={p_bridge:.4f})"
    )
    print("Part B — Key Sequences (f49v, f57v, f66r):")
    print(f"  f49v 26-glyph vertical key: {' '.join(f49v_margin_seq)}")
    print(f"  f57v 4x17-glyph ring Q1   : {' '.join(f57v_ring3_seq[:17])}")
    print(f"  f66r 34-glyph vertical key: {' '.join(f66r_glyph_seq)}")
    print(f"  Shared glyphs (f57v <-> f66r outer bifolium): {shared_57v_66r} (n={len(shared_57v_66r)})")
    print(
        f"  f66r 15-word margin index same-folio matches: {obs_f66r_matches}/15 "
        f"(vs {f66r_null_mean:.2f} null across B folios, z={z_f66r_margin:+.2f})"
    )
    print(f"  f57v top label 'dairal' exact recurrence in f66r prose: {'dairal' in folios['f66r']['prose_tokens']}")


if __name__ == "__main__":
    main()
