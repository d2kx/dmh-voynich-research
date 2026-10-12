#!/usr/bin/env python3
"""
Attack 162 (Phase 173 / Discovery 179):
The 5-Scribe Paleographic Hand ($H=1..5) & Currier Dialect (A vs. B) Invariance
and Specialization Proof.

Tests across all 5 Lisa Fagin Davis Scribe Hands ($H=1..5) and both Currier
Languages ($L=A/B):
  1. Do all 5 scribes obey the exact same Positional Line & Paragraph Envelope Law
     (Top-Line Gallows `p/f` surge, Line-Start `y-` surge, Line-End `-m` stop surge,
     and Diagram Label `o-` nominal surge vs. Prose `qo-` active verb surge)?
  2. How many Canonical Root Stems are shared across all 5 / 5 Scribe Hands
     (Universal Codex Vocabulary coverage)?
  3. How do Currier A (Hand 1) and Currier B (Hands 2 & 3) systematically inflect
     the SAME shared root stems (e.g., `chol/chor` in Currier A <-> `chedy/cheey`
     in Currier B; `daiin` in Currier A <-> `dain/qokain` in Currier B)?
"""

import json
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ZL_PATH = ROOT / "data" / "ZL3b-n.txt"
OUT_JSON = ROOT / "data" / "attack162_five_scribe_hands_and_dialect_bridge.json"

HAND_DESCRIPTIONS = {
    "1": "Scribe 1 (Currier A: 96 Herbal A Monographs & Pharmaceutical Jars)",
    "2": "Scribe 2 (Currier B: 20 Balneological Baths, Quire 14 Rosettes & Herbal B)",
    "3": "Scribe 3 (Currier B: 26 Starred Master Recipe Folios f103r-f116r & Herbal B)",
    "4": "Scribe 4 (Astronomical Star Wheels f67r1-f70r2 & 12 Zodiac Month Wheels f70v2-f73v)",
    "5": "Scribe 5 (Specialized Quire G/H Folios: f41v, f48r/v, f57v Key Ring, f66r Margin Table)",
}

PREFIXES = ("pold", "qo", "ol", "ot", "ok", "op", "od", "da", "sa", "yk", "yd", "o", "d", "s", "y", "l")
SUFFIXES = ("eedy", "edy", "aiin", "ain", "iin", "oldy", "aldy", "ary", "ory", "ody", "am", "om", "ol", "or", "al", "ar", "dy", "y")


def clean_eva_token(tok: str) -> str:
    t = re.sub(r"\{[^}]*\}", "", tok)
    t = re.sub(r"\[([^]:]+):[^\]]+\]", r"\1", t)
    t = re.sub(r"[^a-zA-Z]", "", t).lower()
    return t


def extract_canonical_stem(w: str) -> str:
    s = w.lower()
    s = s.replace("p", "t").replace("f", "k")
    s = re.sub(r"e+", "e", s)
    s = re.sub(r"i+", "i", s)
    for p in PREFIXES:
        if s.startswith(p) and len(s) > len(p) + 1:
            s = s[len(p):]
            break
    for suf in SUFFIXES:
        if s.endswith(suf) and len(s) > len(suf) + 1:
            s = s[:-len(suf)]
            break
    return s


def main():
    folio_meta = {}
    cur_folio = None
    loc_re = re.compile(r"^<f([0-9]+[rv][0-9]*|Ros)\.([^>]+)>\s+(.*)$")
    meta_h_re = re.compile(r"\$H=([0-9A-Za-z@]+)")
    meta_l_re = re.compile(r"\$L=([AB])")
    meta_i_re = re.compile(r"\$I=([A-Z])")

    hand_stats = defaultdict(lambda: {
        "folios": set(),
        "total_tokens": 0,
        "par_start_tokens": 0,
        "par_start_gallows": 0,
        "line_start_tokens": 0,
        "line_start_y": 0,
        "line_mid_tokens": 0,
        "line_mid_y": 0,
        "line_mid_m": 0,
        "line_end_tokens": 0,
        "line_end_m": 0,
        "label_tokens": 0,
        "label_o": 0,
        "prose_tokens": 0,
        "prose_qo": 0,
        "prose_edy": 0,
        "prose_aiin": 0,
        "words": Counter(),
        "stems": Counter(),
    })

    lang_stem_forms = {"A": defaultdict(Counter), "B": defaultdict(Counter)}

    for raw_line in ZL_PATH.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("<f") and ">" in line and "." not in line.split(">")[0]:
            cur_folio = line.split(">")[0][1:]
            mh = meta_h_re.search(line)
            ml = meta_l_re.search(line)
            mi = meta_i_re.search(line)
            h = mh.group(1) if mh else "U"
            l = ml.group(1) if ml else ("A" if h == "1" else ("B" if h in ("2", "3") else "U"))
            sec = mi.group(1) if mi else "U"
            folio_meta[cur_folio] = {"hand": h, "lang": l, "sec": sec}
            continue

        m = loc_re.match(line)
        if not m:
            continue
        folio = "f" + m.group(1)
        loc_tag = m.group(2)
        body = m.group(3)
        meta = folio_meta.get(folio, {"hand": "2" if folio == "fRos" else "U", "lang": "B" if folio == "fRos" else "U", "sec": "C"})
        h = meta["hand"]
        l = meta["lang"]
        if h not in ("1", "2", "3", "4", "5"):
            continue

        is_par_start = "<%>" in body
        is_label = any(tag in loc_tag for tag in ("@L", "&L", "@Ro", "&Ro", "@R", "&R"))
        raw_toks = [clean_eva_token(t) for t in re.split(r"[.\s,]+", body)]
        toks = [t for t in raw_toks if len(t) >= 2]
        if not toks:
            continue

        hs = hand_stats[h]
        hs["folios"].add(folio)
        for idx, t in enumerate(toks):
            hs["total_tokens"] += 1
            hs["words"][t] += 1
            stem = extract_canonical_stem(t)
            hs["stems"][stem] += 1
            if l in ("A", "B"):
                lang_stem_forms[l][stem][t] += 1

            if is_label:
                hs["label_tokens"] += 1
                if t.startswith("o"):
                    hs["label_o"] += 1
            else:
                hs["prose_tokens"] += 1
                if t.startswith("qo"):
                    hs["prose_qo"] += 1
                if t.endswith(("edy", "dy")):
                    hs["prose_edy"] += 1
                if t.endswith(("aiin", "ain", "iin")):
                    hs["prose_aiin"] += 1

                if idx == 0 and is_par_start:
                    hs["par_start_tokens"] += 1
                    if any(g in t[:3] for g in ("p", "f", "k", "t")):
                        hs["par_start_gallows"] += 1
                elif idx == 0:
                    hs["line_start_tokens"] += 1
                    if t.startswith("y"):
                        hs["line_start_y"] += 1
                elif idx == len(toks) - 1 and len(toks) >= 3:
                    hs["line_end_tokens"] += 1
                    if t.endswith("m"):
                        hs["line_end_m"] += 1
                else:
                    hs["line_mid_tokens"] += 1
                    if t.startswith("y"):
                        hs["line_mid_y"] += 1
                    if t.endswith("m"):
                        hs["line_mid_m"] += 1

    hands_table = []
    all_hand_sets = []
    for h in ("1", "2", "3", "4", "5"):
        hs = hand_stats[h]
        all_hand_sets.append(set(hs["stems"].keys()))
        ps_n = max(hs["par_start_tokens"], 1)
        ls_n = max(hs["line_start_tokens"], 1)
        lm_n = max(hs["line_mid_tokens"], 1)
        le_n = max(hs["line_end_tokens"], 1)
        lb_n = max(hs["label_tokens"], 1)
        pr_n = max(hs["prose_tokens"], 1)

        hands_table.append({
            "hand": f"Hand {h}",
            "description": HAND_DESCRIPTIONS[h],
            "folio_count": len(hs["folios"]),
            "total_tokens": hs["total_tokens"],
            "par_start_gallows_rate": round(hs["par_start_gallows"] / ps_n, 4),
            "line_start_y_rate": round(hs["line_start_y"] / ls_n, 4),
            "line_mid_y_rate": round(hs["line_mid_y"] / lm_n, 4),
            "line_end_m_rate": round(hs["line_end_m"] / le_n, 4),
            "line_mid_m_rate": round(hs["line_mid_m"] / lm_n, 4),
            "label_o_rate": round(hs["label_o"] / lb_n, 4) if hs["label_tokens"] else None,
            "prose_qo_rate": round(hs["prose_qo"] / pr_n, 4),
            "prose_edy_rate": round(hs["prose_edy"] / pr_n, 4),
            "prose_aiin_rate": round(hs["prose_aiin"] / pr_n, 4),
            "top_words": [w for w, _ in hs["words"].most_common(8)],
        })

    universal_5hand_stems = set.intersection(*all_hand_sets) if all_hand_sets else set()
    total_corpus_tokens = sum(hand_stats[h]["total_tokens"] for h in ("1", "2", "3", "4", "5"))
    universal_stem_tokens = sum(
        sum(hand_stats[h]["stems"][st] for h in ("1", "2", "3", "4", "5"))
        for st in universal_5hand_stems
    )

    # Top shared stems showing Currier A <-> Currier B inflectional shift
    dialect_bridge_table = []
    shared_ab = set(lang_stem_forms["A"].keys()) & set(lang_stem_forms["B"].keys())
    scored_stems = sorted(
        shared_ab,
        key=lambda st: -(sum(lang_stem_forms["A"][st].values()) + sum(lang_stem_forms["B"][st].values())),
    )
    for st in scored_stems[:15]:
        a_cnt = sum(lang_stem_forms["A"][st].values())
        b_cnt = sum(lang_stem_forms["B"][st].values())
        dialect_bridge_table.append({
            "canonical_stem": st,
            "currier_a_hits": a_cnt,
            "currier_b_hits": b_cnt,
            "currier_a_top_forms": [w for w, _ in lang_stem_forms["A"][st].most_common(4)],
            "currier_b_top_forms": [w for w, _ in lang_stem_forms["B"][st].most_common(4)],
        })

    out = {
        "attack": 162,
        "phase": 173,
        "discovery": 179,
        "title": "5-Scribe Paleographic Hand ($H=1..5) Invariance & Currier A/B Inflectional Bridge",
        "summary": {
            "total_tokens_across_5_hands": total_corpus_tokens,
            "universal_5hand_stems_count": len(universal_5hand_stems),
            "universal_5hand_token_coverage": round(universal_stem_tokens / max(total_corpus_tokens, 1), 4),
            "shared_currier_ab_stems_count": len(shared_ab),
            "all_5_hands_obey_gallows_opener_law": all(r["par_start_gallows_rate"] >= 0.75 for r in hands_table),
            "all_5_hands_obey_line_end_m_law": all(r["line_end_m_rate"] > r["line_mid_m_rate"] * 5 for r in hands_table),
        },
        "hands_table": hands_table,
        "dialect_bridge_table": dialect_bridge_table,
    }

    OUT_JSON.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    print(
        f"[Attack 162] 5-Hand tokens={total_corpus_tokens}, universal 5/5 stems={len(universal_5hand_stems)} "
        f"covering {universal_stem_tokens/total_corpus_tokens*100:.1f}% of corpus! "
        f"All 5 hands obey Gallows Opener (>=75%) & Line-End -m (>5x): "
        f"{out['summary']['all_5_hands_obey_gallows_opener_law']} / {out['summary']['all_5_hands_obey_line_end_m_law']}"
    )


if __name__ == "__main__":
    main()
