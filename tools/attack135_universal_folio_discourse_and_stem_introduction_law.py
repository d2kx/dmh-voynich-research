#!/usr/bin/env python3
"""
Attack 135 (Phase 146 / Discovery 152):
The Universal Intra-Folio Discourse Architecture Across All 226 Folios —
Folio-Top (`Line 1`) vs. Interior vs. Folio-Bottom (`Line N`) Vertical Grammar,
Same-Folio `Para 1 -> Para 2..K` Rare-Stem Topic Persistence (`z`-score
stratified by `$I, $L, $H`), and First-Mention vs. Re-Mention Inflectional Shift.

Investigates:
1. Vertical Folio-Frame Grammar across all `@P` prose folios (`FOLIO_TOP_LINE_1`,
   `FOLIO_INTERIOR_LINES`, `FOLIO_BOTTOM_LINE_N`), both corpus-wide and
   stratified by Currier Language (`A` vs. `B`).
2. Stratified Permutation Test (`1,000` trials within exact `(Section $I,
   Language $L, Hand $H)` buckets): Do continuation paragraphs (`Para 2..K`) on
   a folio share significantly higher Rare-Stem (`2 <= df <= 25`) IDF with
   `Para 1` of the SAME folio than with `Para 1` of random matched folios?
3. Paired Within-Folio `Para 1 (First Mention)` -> `Para 2..K (Re-Mention)`
   Morphological Shift on shared stems.
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
OUT_JSON = ROOT / "data" / "attack135_universal_folio_discourse_and_stem_introduction_law.json"


def clean_tok(t: str) -> str:
    t = re.sub(r"\{[^}]*\}", "", t)
    t = re.sub(r"\[([^]:]+):[^\]]+\]", r"\1", t)
    t = re.sub(r"[^a-zA-Z]", "", t).lower()
    return t


def canon_stem(w: str) -> str:
    s = w
    if s.startswith("q") and len(s) > 2:
        s = s[1:]
    for p in ["ch", "sh", "da", "sa", "ol", "al", "or", "ar", "ok", "ot", "yk", "yt", "d", "s", "y", "o", "l"]:
        if s.startswith(p) and len(s) - len(p) >= 2:
            s = s[len(p):]
            break
    for suf in ["aiin", "oiin", "iin", "eedy", "edy", "ody", "ady", "dy", "ey", "oy", "ol", "al", "or", "ar", "am", "om", "an", "in", "y", "l", "r", "m", "n", "s"]:
        if s.endswith(suf) and len(s) - len(suf) >= 2:
            s = s[:-len(suf)]
            break
    return s


def metrics_for_tokens(toks: list) -> dict:
    n = len(toks)
    if n == 0:
        return {}
    stems = [canon_stem(w) for w in toks]
    pf_gal = sum(1 for w in toks if w.startswith(("p", "f", "op", "of", "cph", "cfh", "qop", "qof")))
    o_nom = sum(1 for w in toks if w.startswith("o") and not w.startswith("ol"))
    qo = sum(1 for w in toks if w.startswith("qo"))
    bench = sum(1 for w in toks if w.startswith(("ch", "sh")))
    d_top = sum(1 for w in toks if w.startswith("d"))
    l_appl = sum(1 for w in toks if w.startswith(("l", "ol", "al")))
    edy = sum(1 for w in toks if w.endswith(("edy", "eedy")))
    aiin = sum(1 for w in toks if w.endswith(("aiin", "oiin", "iin")))
    am = sum(1 for w in toks if w.endswith(("am", "om", "m")))
    ol_or = sum(1 for w in toks if w.endswith(("ol", "or", "al", "ar")))
    return {
        "n_tokens": n,
        "n_unique_stems": len(set(stems)),
        "mean_len": round(sum(len(w) for w in toks) / n, 3),
        "pf_gallows_pct": round(100.0 * pf_gal / n, 2),
        "o_nom_pct": round(100.0 * o_nom / n, 2),
        "qo_pct": round(100.0 * qo / n, 2),
        "bench_pct": round(100.0 * bench / n, 2),
        "d_top_pct": round(100.0 * d_top / n, 2),
        "l_appl_pct": round(100.0 * l_appl / n, 2),
        "edy_pct": round(100.0 * edy / n, 2),
        "aiin_pct": round(100.0 * aiin / n, 2),
        "am_pct": round(100.0 * am / n, 2),
        "liquid_coda_pct": round(100.0 * ol_or / n, 2),
    }


def main():
    random.seed(42)
    with open(INDEX_PATH, encoding="utf-8") as f:
        idx = json.load(f)
    folio_meta = idx["folios"]

    folio_prose_lines = defaultdict(list)
    stem_folios = defaultdict(set)

    with open(ZL_PATH, encoding="utf-8", errors="ignore") as f:
        for raw in f:
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            m_line = re.match(r"^<(f[0-9a-zA-Z]+)\.([^>]+)>\s+(.*)$", line)
            if not m_line:
                continue
            fol, loc_part, text = m_line.groups()
            loc = loc_part.split(",")[-1] if "," in loc_part else loc_part
            line_id = loc_part.split(",")[0]

            has_para_start = "<%>" in text
            has_para_end = "<$>" in text

            text_no_comm = re.sub(r"<![^>]+>", "", text)
            raw_toks = re.split(r"[.\s,]+", text_no_comm)
            toks = [clean_tok(t) for t in raw_toks]
            toks = [t for t in toks if len(t) >= 2]
            if not toks:
                continue

            for t in toks:
                st = canon_stem(t)
                if len(st) >= 2:
                    stem_folios[st].add(fol)

            l_clean = loc.lstrip("@+=*~&/")
            if l_clean.startswith("P") and not l_clean.startswith(("Pb", "Pt")):
                folio_prose_lines[fol].append({
                    "line_id": line_id,
                    "loc": loc,
                    "has_para_start": has_para_start,
                    "has_para_end": has_para_end,
                    "tokens": toks,
                })

    n_folios = 226
    stem_idf = {
        s: math.log(n_folios / len(fols))
        for s, fols in stem_folios.items()
        if 2 <= len(fols) <= 25 and len(s) >= 2
    }

    # 1. Vertical Folio-Frame Grammar: Line 1 vs Interior vs Line N
    zone_toks = {
        "ALL": {"TOP_LINE_1": [], "INTERIOR_LINES": [], "BOTTOM_LINE_N": []},
        "CURRIER_A": {"TOP_LINE_1": [], "INTERIOR_LINES": [], "BOTTOM_LINE_N": []},
        "CURRIER_B": {"TOP_LINE_1": [], "INTERIOR_LINES": [], "BOTTOM_LINE_N": []},
    }

    folio_paragraphs = defaultdict(list)

    for fol, lns in folio_prose_lines.items():
        if len(lns) < 3:
            continue
        lg = folio_meta.get(fol, {}).get("currier_lang", "?")
        lg_key = "CURRIER_A" if lg == "A" else ("CURRIER_B" if lg == "B" else None)

        top_t = lns[0]["tokens"]
        bot_t = lns[-1]["tokens"]
        int_t = [t for ln in lns[1:-1] for t in ln["tokens"]]

        zone_toks["ALL"]["TOP_LINE_1"].extend(top_t)
        zone_toks["ALL"]["INTERIOR_LINES"].extend(int_t)
        zone_toks["ALL"]["BOTTOM_LINE_N"].extend(bot_t)
        if lg_key:
            zone_toks[lg_key]["TOP_LINE_1"].extend(top_t)
            zone_toks[lg_key]["INTERIOR_LINES"].extend(int_t)
            zone_toks[lg_key]["BOTTOM_LINE_N"].extend(bot_t)

        # Segment paragraphs on this folio
        cur_p = []
        for ln in lns:
            if ln["has_para_start"] and cur_p:
                folio_paragraphs[fol].append(cur_p)
                cur_p = []
            cur_p.extend(ln["tokens"])
            if ln["has_para_end"] and cur_p:
                folio_paragraphs[fol].append(cur_p)
                cur_p = []
        if cur_p:
            folio_paragraphs[fol].append(cur_p)

    vertical_folio_summary = {
        scope: {z: metrics_for_tokens(tlist) for z, tlist in zdict.items()}
        for scope, zdict in zone_toks.items()
    }

    # 2. Multi-Paragraph Folio Topic Persistence & Stem Introduction Cascade
    multi_para_fols = [f for f, plist in folio_paragraphs.items() if len(plist) >= 2 and len(plist[0]) >= 15]

    para_position_toks = {"PARA_1_OPENING": [], "PARA_2_SECOND": [], "PARA_3PLUS_LATER": []}
    para_new_rare_idf_per_100w = {"PARA_1_OPENING": [], "PARA_2_SECOND": [], "PARA_3PLUS_LATER": []}

    # Track same-folio Para 1 <-> Para 2..K rare-stem IDF
    bucket_folios = defaultdict(list)
    folio_p1_stems = {}
    folio_p2plus_stems = {}

    first_mention_p1_toks = []
    remention_p2plus_toks = []

    for fol in multi_para_fols:
        plist = folio_paragraphs[fol]
        meta = folio_meta.get(fol, {})
        b_key = (meta.get("section_code", "?"), meta.get("currier_lang", "?"), str(meta.get("hand", "?")))
        bucket_folios[b_key].append(fol)

        seen_stems_on_folio = set()
        for idx_p, p_toks in enumerate(plist):
            pos_key = "PARA_1_OPENING" if idx_p == 0 else ("PARA_2_SECOND" if idx_p == 1 else "PARA_3PLUS_LATER")
            para_position_toks[pos_key].extend(p_toks)
            p_stems = {canon_stem(w) for w in p_toks if len(canon_stem(w)) >= 2}
            new_rare = [s for s in (p_stems - seen_stems_on_folio) if s in stem_idf]
            new_idf_100 = 100.0 * sum(stem_idf[s] for s in new_rare) / max(15, len(p_toks))
            para_new_rare_idf_per_100w[pos_key].append(new_idf_100)
            seen_stems_on_folio |= p_stems

        p1_toks = plist[0]
        p2plus_toks = [t for p in plist[1:] for t in p]
        p1_st = {canon_stem(w) for w in p1_toks if len(canon_stem(w)) >= 2}
        p2_st = {canon_stem(w) for w in p2plus_toks if len(canon_stem(w)) >= 2}
        folio_p1_stems[fol] = p1_st
        folio_p2plus_stems[fol] = p2_st

        shared_st = p1_st & p2_st
        for w in p1_toks:
            if canon_stem(w) in shared_st:
                first_mention_p1_toks.append(w)
        for w in p2plus_toks:
            if canon_stem(w) in shared_st:
                remention_p2plus_toks.append(w)

    # Stratified Permutation Test: Does Para 2..K share significantly higher Rare-Stem IDF
    # with Para 1 of the SAME folio than with Para 1 of random folios in the exact same ($I, $L, $H) bucket?
    obs_same_folio_idfs = []
    for fol in multi_para_fols:
        sh = [s for s in (folio_p1_stems[fol] & folio_p2plus_stems[fol]) if s in stem_idf]
        obs_same_folio_idfs.append(sum(stem_idf[s] for s in sh))
    obs_mean_p1_p2_idf = sum(obs_same_folio_idfs) / len(obs_same_folio_idfs)

    null_means = []
    for _ in range(1000):
        sim_vals = []
        for fol in multi_para_fols:
            meta = folio_meta.get(fol, {})
            b_key = (meta.get("section_code", "?"), meta.get("currier_lang", "?"), str(meta.get("hand", "?")))
            pool = bucket_folios[b_key]
            rand_fol = random.choice(pool)
            sh = [s for s in (folio_p1_stems[rand_fol] & folio_p2plus_stems[fol]) if s in stem_idf]
            sim_vals.append(sum(stem_idf[s] for s in sh))
        null_means.append(sum(sim_vals) / len(sim_vals))

    mu_p1p2 = sum(null_means) / len(null_means)
    sd_p1p2 = math.sqrt(sum((x - mu_p1p2) ** 2 for x in null_means) / len(null_means))
    z_p1p2 = (obs_mean_p1_p2_idf - mu_p1p2) / (sd_p1p2 if sd_p1p2 > 0 else 1.0)
    p_p1p2 = sum(1 for x in null_means if x >= obs_mean_p1_p2_idf) / len(null_means)

    para_progression_summary = {}
    for pos_key in ["PARA_1_OPENING", "PARA_2_SECOND", "PARA_3PLUS_LATER"]:
        m = metrics_for_tokens(para_position_toks[pos_key])
        idf_list = para_new_rare_idf_per_100w[pos_key]
        m["mean_new_rare_stem_idf_per_100w"] = round(sum(idf_list) / len(idf_list), 3) if idf_list else 0.0
        para_progression_summary[pos_key] = m

    out = {
        "attack": 135,
        "phase": 146,
        "discovery": 152,
        "title": "Universal Intra-Folio Discourse Architecture Across All 226 Folios — Vertical Folio Frame (Line 1 vs. Interior vs. Line N) & Para 1 -> Para 2..K Topic Persistence",
        "vertical_folio_frame_summary": vertical_folio_summary,
        "paragraph_progression_summary": para_progression_summary,
        "same_folio_p1_to_p2plus_topic_persistence_test": {
            "n_multi_paragraph_folios": len(multi_para_fols),
            "observed_mean_rare_stem_idf": round(obs_mean_p1_p2_idf, 3),
            "null_mean_stratified_I_L_H": round(mu_p1p2, 3),
            "null_sd": round(sd_p1p2, 3),
            "lift_ratio": round(obs_mean_p1_p2_idf / mu_p1p2, 3) if mu_p1p2 > 0 else 0.0,
            "z_score": round(z_p1p2, 2),
            "p_value": round(p_p1p2, 4),
        },
        "shared_stem_first_mention_p1_vs_remention_p2plus": {
            "PARA1_FIRST_MENTION": metrics_for_tokens(first_mention_p1_toks),
            "PARA2PLUS_RE_MENTION": metrics_for_tokens(remention_p2plus_toks),
        },
    }

    OUT_JSON.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"[Attack 135] Saved {OUT_JSON}")
    print("Vertical Folio Frame (ALL):", json.dumps(vertical_folio_summary["ALL"], indent=2))
    print("Paragraph Progression Summary:", json.dumps(para_progression_summary, indent=2))
    print("Same-Folio Para 1 -> Para 2..K Topic Persistence Test:", json.dumps(out["same_folio_p1_to_p2plus_topic_persistence_test"], indent=2))
    print("Shared Stem First-Mention (P1) vs Re-Mention (P2+):", json.dumps(out["shared_stem_first_mention_p1_vs_remention_p2plus"], indent=2))


if __name__ == "__main__":
    main()
