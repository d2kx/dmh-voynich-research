#!/usr/bin/env python3
"""
Attack 222 (Discovery 239):
Completing 100.0% (16/16) Visual Coverage of Opening Quire 1 ($Q=A, f1r-f8v: f2v, f3v, f4r, f5v, f6v, f7r, f7v),
the 4-Bifolium Architecture (f1<->f8, f2<->f7, f3<->f6, f4<->f5),
f7v.7 4-Fold daiin Epizeuxis, and Quire 1 Lexical Seeding of Currier A Herbal.
"""

import json
import os
import re
import glob
from collections import Counter

def normalize_token(w: str) -> str:
    w = re.sub(r"\[([^:\]]+):[^\]]+\]", r"\1", w)
    w = re.sub(r"[^a-zA-Z]", "", w).lower()
    return w

def canonical_stem(w: str) -> str:
    w = normalize_token(w)
    if not w:
        return ""
    w = re.sub(r"^qo", "o", w)
    w = w.replace("eee", "e").replace("ee", "e").replace("ii", "i")
    w = w.replace("f", "p").replace("k", "t")
    for p in ["o", "d", "y", "s"]:
        if len(w) > 3 and w.startswith(p):
            w = w[len(p):]
            break
    for s in ["aiin", "ain", "edy", "eey", "ody", "ady", "al", "ar", "or", "ol", "am", "an", "dy", "ey", "y"]:
        if len(w) > len(s) + 1 and w.endswith(s):
            w = w[:-len(s)]
            break
    return w

def parse_zl_words(path: str):
    folio_words = {}
    folio_lines = {}
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("#") or not line.strip():
                continue
            m = re.match(r"^<([^.>]+)\.([^,>]+),([^>]+)>\s+(.*)$", line)
            if not m:
                continue
            folio, lno, ltype, rest = m.groups()
            rest_clean = re.sub(r"<!.*?>", "", rest)
            rest_clean = re.sub(r"<[@$%~].*?>", "", rest_clean)
            rest_clean = rest_clean.replace("<->", ".")
            raw_tokens = re.split(r"[.,\s]+", rest_clean)
            words = [normalize_token(t) for t in raw_tokens if normalize_token(t)]
            folio_words.setdefault(folio, []).extend(words)
            folio_lines.setdefault(folio, []).append((lno, ltype, words, rest.strip()))
    return folio_words, folio_lines

def jaccard(s1, s2):
    u = s1 | s2
    return len(s1 & s2) / len(u) if u else 0.0

def main():
    with open(os.path.join("data", "folio_index.json"), "r", encoding="utf-8") as f:
        idx_data = json.load(f)["folios"]
    folio_words, folio_lines = parse_zl_words(os.path.join("data", "ZL3b-n.txt"))
    pngs = [os.path.basename(p) for p in glob.glob(os.path.join("pages", "*.png"))]

    q1_folios = [f"f{i}{s}" for i in range(1, 9) for s in ("r", "v")]
    q1_rendered = [f for f in q1_folios if any(re.search(rf"\b{f}(_|\.|$)", p) for p in pngs)]

    # 1. Per-page profile of Quire 1 (f1r-f8v)
    q1_profiles = []
    for f in q1_folios:
        ws = folio_words.get(f, [])
        n = len(ws)
        chol_shol = sum(1 for w in ws if w in ("chol", "shol", "chor", "shor"))
        daiin_cnt = sum(1 for w in ws if w in ("daiin", "dain"))
        o_init = sum(1 for w in ws if w.startswith("o"))
        q_init = sum(1 for w in ws if w.startswith("q"))
        edy = sum(1 for w in ws if w.endswith(("edy", "eey")))
        q1_profiles.append({
            "folio": f,
            "words": n,
            "unique_stems": len(set(canonical_stem(w) for w in ws)),
            "chol_shol_chor_shor_pct": round(100.0 * chol_shol / n, 2) if n else 0.0,
            "daiin_pct": round(100.0 * daiin_cnt / n, 2) if n else 0.0,
            "o_initial_pct": round(100.0 * o_init / n, 2) if n else 0.0,
            "q_initial_pct": round(100.0 * q_init / n, 2) if n else 0.0,
            "edy_eey_pct": round(100.0 * edy / n, 2) if n else 0.0
        })

    # 2. 4-Bifolium Architecture of Quire 1 (f1<->f8, f2<->f7, f3<->f6, f4<->f5) & Same-Leaf Coupling
    bifolia_pairs = [("f1", "f8"), ("f2", "f7"), ("f3", "f6"), ("f4", "f5")]
    bifolia_stats = []
    for l1, l2 in bifolia_pairs:
        w1 = folio_words.get(l1 + "r", []) + folio_words.get(l1 + "v", [])
        w2 = folio_words.get(l2 + "r", []) + folio_words.get(l2 + "v", [])
        s1 = set(canonical_stem(w) for w in w1)
        s2 = set(canonical_stem(w) for w in w2)
        cov12 = sum(1 for w in w2 if canonical_stem(w) in s1) / len(w2) if w2 else 0.0
        cov21 = sum(1 for w in w1 if canonical_stem(w) in s2) / len(w1) if w1 else 0.0
        bifolia_stats.append({
            "bifolium": f"{l1} <-> {l2}",
            "leaf1_words": len(w1),
            "leaf2_words": len(w2),
            "stem_jaccard": round(jaccard(s1, s2), 4),
            "leaf1_covers_leaf2_token_pct": round(100.0 * cov12, 2),
            "leaf2_covers_leaf1_token_pct": round(100.0 * cov21, 2)
        })

    same_leaf_stats = []
    for i in range(1, 9):
        fr, fv = f"f{i}r", f"f{i}v"
        wr, wv = folio_words.get(fr, []), folio_words.get(fv, [])
        sr, sv = set(canonical_stem(w) for w in wr), set(canonical_stem(w) for w in wv)
        cov_rv = sum(1 for w in wv if canonical_stem(w) in sr) / len(wv) if wv else 0.0
        same_leaf_stats.append({
            "leaf": f"f{i} ({fr} <-> {fv})",
            "recto_words": len(wr),
            "verso_words": len(wv),
            "stem_jaccard": round(jaccard(sr, sv), 4),
            "recto_covers_verso_token_pct": round(100.0 * cov_rv, 2)
        })

    # 3. Lexical seeding of the entire 94-folio Currier A Herbal corpus from Quire 1 (f1r-f8v)
    herbal_a_folios = [f for f, v in idx_data.items() if v.get("section_code") == "H" and v.get("currier_lang") == "A"]
    herbal_a_words = [w for f in herbal_a_folios for w in folio_words.get(f, [])]
    q1_all_words = [w for f in q1_folios for w in folio_words.get(f, [])]
    q1_stem_set = set(canonical_stem(w) for w in q1_all_words)
    q1_word_set = set(q1_all_words)

    herbal_a_raw_seeded = sum(1 for w in herbal_a_words if w in q1_word_set)
    herbal_a_stem_seeded = sum(1 for w in herbal_a_words if canonical_stem(w) in q1_stem_set)

    # Also check f7v.7 4-fold daiin epizeuxis line
    f7v_line7 = [ln for ln in folio_lines.get("f7v", []) if ln[0] == "7"]

    out = {
        "attack": 222,
        "discovery": 239,
        "title": "Completing 100% (16/16) Visual Coverage of Opening Quire 1 (f1r-f8v), 4-Bifolium Architecture, f7v.7 4-Fold daiin Epizeuxis, and Quire 1 Seeding of Currier A Herbal",
        "quire1_completion": {
            "total_folios": len(q1_folios),
            "rendered_folios": len(q1_rendered),
            "completion_pct": round(100.0 * len(q1_rendered) / len(q1_folios), 2),
            "total_words": len(q1_all_words),
            "unique_canonical_stems": len(q1_stem_set)
        },
        "quire1_seeds_herbal_a": {
            "herbal_a_folios": len(herbal_a_folios),
            "herbal_a_total_words": len(herbal_a_words),
            "raw_word_coverage_pct": round(100.0 * herbal_a_raw_seeded / len(herbal_a_words), 2),
            "canonical_stem_coverage_pct": round(100.0 * herbal_a_stem_seeded / len(herbal_a_words), 2)
        },
        "f7v_line7_daiin_epizeuxis": {
            "line_id": "<f7v.7,+P0>",
            "words": f7v_line7[0][2] if f7v_line7 else [],
            "daiin_count_in_line": sum(1 for w in (f7v_line7[0][2] if f7v_line7 else []) if w == "daiin")
        },
        "bifolia_coupling": bifolia_stats,
        "same_leaf_coupling": same_leaf_stats,
        "folio_profiles": q1_profiles
    }

    out_path = os.path.join("data", "attack222_quire1_100pct_completion_and_opening_bifolia_f1_f8.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    print(f"Wrote {out_path}")
    print(json.dumps({
        "quire1_completion": out["quire1_completion"],
        "quire1_seeds_herbal_a": out["quire1_seeds_herbal_a"],
        "f7v_line7": out["f7v_line7_daiin_epizeuxis"],
        "bifolia_coupling": out["bifolia_coupling"]
    }, indent=2))

if __name__ == "__main__":
    main()
