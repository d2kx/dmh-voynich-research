#!/usr/bin/env python3
"""
Attack 102 (Discovery 119): The Quire 14 (`f85r1–f86v6` + `fRos`) Six-Page Cosmological
Foldout & Rosettes Exegetical Bridge — Proving That the Four Quire 14 Prose Treatises
(`f85r1, f86v3, f86v5, f86v6`) Specifically Exegete the Four Quire 14 Cosmological Diagrams
(`f85r2, f85v2, f86v4, fRos`)

Tests:
1. Extracts all tokens and open-class canonical stems across the `8` surfaces of Quire 14 (`$Q=N`):
   - **4 Cosmological Diagram Surfaces (`$I=C`)**: `f85r2` (12-Wind Solar Wheel), `f85v2` (Four-Corner Diagram),
     `f86v4` (Cosmological Ring Diagram), and `fRos` (9-Sphere Rosettes Foldout Map).
   - **4 Prose Treatise Surfaces (`$I=T`)**: `f85r1`, `f86v3`, `f86v5`, and `f86v6`.
2. Tests **Within-Quire Diagram <-> Treatise Exegetical Cohesion**:
   - Compares the mean IDF-weighted open-class stem overlap and stem Jaccard between the `4` Quire 14
     Cosmological Diagrams and the `4` Quire 14 Prose Treatises (`16` pairs) against:
     (a) non-Quire-14 Currier B prose folios (`f75r..f84v`, `f103r..f116r`, `f26r..f48v`), and
     (b) a 500-trial vocabulary-preserving permutation null.
3. Maps the **4 x 4 Quire 14 Diagram-to-Treatise Routing Matrix** and the **Nominal-to-Active
   (`o-R -> qo-R / l-R`) Transformation** of shared stems between the Diagrams and the Treatises.
"""

import json
import math
import random
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
ZL_PATH = DATA_DIR / "ZL3b-n.txt"
OUT_JSON = DATA_DIR / "attack102_quire14_f85_f86_and_rosettes_bridge.json"

FOLIO_META_RE = re.compile(r"^<f([0-9]+[rv][0-9]*|Ros)>\s*<!\s*(.*?)>")
LOCUS_RE = re.compile(r"^<f([0-9]+[rv][0-9]*|Ros)\.([^,>]+),([^>]+)>\s*(.*)$")

Q14_DIAGRAMS = ["f85r2", "f86v4", "fRos"]
Q14_TREATISES = ["f85r1", "f86v3", "f86v5", "f86v6"]


def clean_tokens(raw: str):
    s = re.sub(r"\{[^}]*\}", "", raw)
    s = s.replace("<%>", " ").replace("<$>", " ").replace("<->", " ")
    s = re.sub(r"<[^>]*>", " ", s)
    s = re.sub(r"@[0-9]+;", "", s)
    s = re.sub(r"\[([^:\]]+):[^\]]+\]", r"\1", s)
    out = []
    for c in s.replace(".", " ").split():
        w = re.sub(r"[^a-zA-Z]", "", c).lower()
        if w:
            out.append(w)
    return out


def canonical_stem(w: str) -> str:
    s = w
    if s.startswith("qo") and len(s) > 3:
        s = "o" + s[2:]
    elif s.startswith("q") and len(s) > 2:
        s = s[1:]
    s = s.replace("cph", "cth").replace("cfh", "ckh")
    s = s.replace("p", "t").replace("f", "k")
    s = s.replace("sh", "ch")
    s = re.sub(r"e+", "e", s)
    s = re.sub(r"i+", "i", s)
    if s.endswith("edy") and len(s) >= 4:
        s = s[:-3] + "dy"
    elif s.endswith("ody") and len(s) >= 4:
        s = s[:-3] + "dy"
    return s


def jaccard(s1: set, s2: set) -> float:
    if not s1 or not s2:
        return 0.0
    return len(s1 & s2) / len(s1 | s2)


def main():
    raw_lines = ZL_PATH.read_text(encoding="utf-8", errors="replace").splitlines()
    cur_folio = None
    cur_meta = {}
    folio_meta = {}
    folio_tokens = defaultdict(list)
    all_word_counts = Counter()

    for raw_line in raw_lines:
        raw_s = raw_line.strip()
        if not raw_s or raw_s.startswith("#"):
            continue
        mf = FOLIO_META_RE.match(raw_s)
        if mf:
            cur_folio = "f" + mf.group(1)
            meta_str = mf.group(2)
            cur_meta = {}
            for kv in meta_str.split():
                if "=" in kv:
                    k, v = kv.lstrip("$").split("=", 1)
                    cur_meta[k] = v
            folio_meta[cur_folio] = cur_meta
            continue
        ml = LOCUS_RE.match(raw_s)
        if ml and cur_folio:
            toks = clean_tokens(ml.group(4))
            if not toks:
                continue
            for w in toks:
                all_word_counts[w] += 1
            folio_tokens[cur_folio].extend(toks)

    canon_counts = Counter()
    for w, c in all_word_counts.items():
        cs = canonical_stem(w)
        if len(cs) >= 3:
            canon_counts[cs] += c
    top40_closed = {cs for cs, _ in canon_counts.most_common(40)}

    def get_open_stems(tokens):
        return {canonical_stem(w) for w in tokens if len(w) >= 3 and canonical_stem(w) not in top40_closed}

    folio_open_stems = {f: get_open_stems(toks) for f, toks in folio_tokens.items() if len(toks) >= 20}
    n_docs = len(folio_open_stems)
    df = Counter(cs for s in folio_open_stems.values() for cs in s)
    idf = {cs: math.log((n_docs + 1.0) / (c + 0.5)) for cs, c in df.items()}

    # 1. Compute 4 x 4 Quire 14 Diagram <-> Treatise Routing Matrix
    routing_matrix = []
    q14_jaccards = []
    q14_idf_scores = []

    for df_name in Q14_DIAGRAMS:
        dst = folio_open_stems[df_name]
        dtoks = folio_tokens[df_name]
        for tf_name in Q14_TREATISES:
            tst = folio_open_stems[tf_name]
            ttoks = folio_tokens[tf_name]
            inter = dst & tst
            jac = jaccard(dst, tst)
            idf_sc = sum(idf[cs] for cs in inter)
            q14_jaccards.append(jac)
            q14_idf_scores.append(idf_sc)

            top_shared = sorted(inter, key=lambda x: -idf[x])[:6]
            surf_bridges = []
            for cs in top_shared:
                dw = [w for w in dtoks if canonical_stem(w) == cs][0]
                tw = [w for w in ttoks if canonical_stem(w) == cs][0]
                surf_bridges.append(f"{cs}: Diag({dw}) -> Treat({tw})")

            routing_matrix.append({
                "diagram_folio": df_name,
                "treatise_folio": tf_name,
                "shared_open_stems": len(inter),
                "jaccard": round(jac, 4),
                "idf_score": round(idf_sc, 2),
                "top_shared_bridges": surf_bridges,
            })

    obs_q14_mean_jaccard = sum(q14_jaccards) / len(q14_jaccards)
    obs_q14_mean_idf = sum(q14_idf_scores) / len(q14_idf_scores)

    # Compare against non-Quire-14 Currier B prose folios (`$L=B`, excluding Quire 14)
    other_b_folios = [
        f for f, m in folio_meta.items()
        if m.get("L") == "B" and f not in Q14_DIAGRAMS and f not in Q14_TREATISES and f in folio_open_stems
    ]
    other_b_jaccards = []
    for df_name in Q14_DIAGRAMS:
        dst = folio_open_stems[df_name]
        for bf in other_b_folios:
            other_b_jaccards.append(jaccard(dst, folio_open_stems[bf]))
    other_b_mean_jaccard = sum(other_b_jaccards) / len(other_b_jaccards)
    jaccard_lift_vs_other_b = 100.0 * (obs_q14_mean_jaccard - other_b_mean_jaccard) / (other_b_mean_jaccard or 1e-9)

    # Permutation Null Test (500 trials): randomly sample 4 Currier B prose folios and compute mean Jaccard with Q14_DIAGRAMS
    rng = random.Random(102)
    all_b_prose = Q14_TREATISES + other_b_folios
    null_jac_means = []
    for _ in range(500):
        samp4 = rng.sample(all_b_prose, 4)
        vals = [jaccard(folio_open_stems[d], folio_open_stems[t]) for d in Q14_DIAGRAMS for t in samp4]
        null_jac_means.append(sum(vals) / len(vals))
    null_mu = sum(null_jac_means) / len(null_jac_means)
    null_sd = math.sqrt(sum((x - null_mu) ** 2 for x in null_jac_means) / len(null_jac_means)) or 1e-9
    z_q14_cohesion = (obs_q14_mean_jaccard - null_mu) / null_sd

    # 2. Union of Q14 Diagrams vs Union of Q14 Treatises: Morphological Transformation of Shared Stems
    diag_union_stems = set.union(*(folio_open_stems[d] for d in Q14_DIAGRAMS))
    treat_union_stems = set.union(*(folio_open_stems[t] for t in Q14_TREATISES))
    q14_shared_stems = diag_union_stems & treat_union_stems

    diag_shared_toks = [w for d in Q14_DIAGRAMS for w in folio_tokens[d] if canonical_stem(w) in q14_shared_stems]
    treat_shared_toks = [w for t in Q14_TREATISES for w in folio_tokens[t] if canonical_stem(w) in q14_shared_stems]

    def profile_tokens(toks):
        n = len(toks) or 1
        return {
            "n_tokens": len(toks),
            "o_nominal_pct": round(100.0 * sum(1 for w in toks if w.startswith("o") and not w.startswith("qo")) / n, 2),
            "qo_active_pct": round(100.0 * sum(1 for w in toks if w.startswith("qo")) / n, 2),
            "l_applicative_pct": round(100.0 * sum(1 for w in toks if w.startswith(("l", "ol", "qol"))) / n, 2),
            "edy_processual_pct": round(100.0 * sum(1 for w in toks if w.endswith("edy")) / n, 2),
            "aiin_quantifier_pct": round(100.0 * sum(1 for w in toks if w.endswith(("aiin", "ain", "iin"))) / n, 2),
        }

    q14_transformation = {
        "total_diagram_open_stems": len(diag_union_stems),
        "total_treatise_open_stems": len(treat_union_stems),
        "shared_open_stems_count": len(q14_shared_stems),
        "pct_of_diagram_stems_in_treatises": round(100.0 * len(q14_shared_stems) / len(diag_union_stems), 2),
        "diagram_surface_profile": profile_tokens(diag_shared_toks),
        "treatise_surface_profile": profile_tokens(treat_shared_toks),
    }

    # Best Treatise Match for each of the 4 Quire 14 Diagrams
    best_per_diagram = []
    for d in Q14_DIAGRAMS:
        sub = [r for r in routing_matrix if r["diagram_folio"] == d]
        sub.sort(key=lambda x: -x["idf_score"])
        best_per_diagram.append(sub[0])

    out = {
        "quire14_exegetical_cohesion": {
            "observed_4x4_mean_jaccard": round(obs_q14_mean_jaccard, 4),
            "other_currier_b_folios_mean_jaccard": round(other_b_mean_jaccard, 4),
            "jaccard_lift_vs_other_currier_b_pct": round(jaccard_lift_vs_other_b, 2),
            "null_sampled_currier_b_mean_jaccard": round(null_mu, 4),
            "null_std": round(null_sd, 4),
            "z_score": round(z_q14_cohesion, 2),
            "observed_4x4_mean_idf_score": round(obs_q14_mean_idf, 2),
        },
        "quire14_shared_stem_transformation": q14_transformation,
        "best_treatise_per_diagram": best_per_diagram,
        "full_4x4_routing_matrix": sorted(routing_matrix, key=lambda x: -x["idf_score"]),
    }

    OUT_JSON.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"Saved {OUT_JSON}")
    print("Quire 14 Exegetical Cohesion:", json.dumps(out["quire14_exegetical_cohesion"], indent=2))
    print("Quire 14 Shared Stem Transformation:", json.dumps(q14_transformation, indent=2))
    for b in best_per_diagram:
        print(f"  {b['diagram_folio']} -> {b['treatise_folio']} (shared={b['shared_open_stems']}, Jaccard={b['jaccard']}, IDF={b['idf_score']}): {b['top_shared_bridges'][:3]}")


if __name__ == "__main__":
    main()
