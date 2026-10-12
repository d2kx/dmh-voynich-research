r"""
Attack 23: Distributional Context-Embedding & Minimal-Pair Substitution Matrix of the Top 150 Core Roots
========================================================================================================
Analyzes the syntagmatic (`[w_{i-1} _ w_{i+1}]`) and morphological (`[Prefix _ Suffix]`) distributions of the
Top 150 Core Roots across all 37,517 prose tokens in `data/ZL3b-n.txt`:
1. Computes a combined **Morpho-Syntagmatic Embedding Vector** for each of the Top 150 Core Roots:
   - Morphological envelope vector (`P(Prefix | Root)` + `P(Suffix | Root)`)
   - Syntagmatic bigram context vector (`P(Prev_Root | Root)` + `P(Next_Root | Root)` + `P(Line_Position | Root)`)
   - Section distribution vector (`P(Section | Root)`)
2. Evaluates all **Systematic Minimal Pairs** (`k/t`, `ch/sh`, `che/she`, `cth/ckh`, `kch/tch`, `lch/lsh`,
   `kol/kal`, `tol/tal`, `dar/dal`, `teo/keo`, `cheo/sheo`, `ar/or`, `al/ol`, `dch/sch`, `lk/lt`, `pch/fch`),
   measuring Morphological Cosine ($\cos_{\text{morph}}$), Syntagmatic Context Cosine ($\cos_{\text{ctx}}$),
   and Section Cosine ($\cos_{\text{sec}}$) against a 10,000-pair random baseline ($z$-score).
3. Extracts the **Top Nearest-Neighbor Substitution Clusters** and classifies the Top 150 Core Roots into
   6 Distributional Word Classes (Verbal Operators, Gallows-C Compound Operators, Vessel/Conduit Nouns,
   Botanical/Jar Substance Nouns, Celestial/Nymph Nouns, and Deictic/Boundary Particles).
"""

import json
import math
import re
import random
from pathlib import Path
from collections import Counter, defaultdict

from attack7_positional_envelope_fst import extract_core_root_and_envelope
from attack16_radical_clause_translation_edition import RADICAL_SHORT_TAG

ROOT = Path(__file__).resolve().parent.parent
ZL_PATH = ROOT / "data" / "ZL3b-n.txt"
INDEX_PATH = ROOT / "data" / "folio_index.json"
OUT_PATH = ROOT / "data" / "attack23_distributional_minimal_pair_matrix.json"


def normalize_token(w: str) -> str:
    w = re.sub(r"\[([^:\]]+):[^\]]+\]", r"\1", w)
    w = re.sub(r"[^a-zA-Z]", "", w).lower()
    if not w:
        return ""
    if w.startswith("qo") and len(w) > 2:
        w = w[1:]
    elif w.startswith("q") and len(w) > 1:
        w = w[1:]
    if w.startswith("cph"):
        w = "cth" + w[3:]
    elif w.startswith("cfh"):
        w = "ckh" + w[3:]
    elif w.startswith("p") and len(w) > 1:
        w = "t" + w[1:]
    elif w.startswith("f") and len(w) > 1:
        w = "k" + w[1:]
    w = re.sub(r"i{2,}", "i", w)
    w = re.sub(r"e{2,}", "e", w)
    if len(w) > 2 and w.endswith("am"):
        w = w[:-2] + "ar"
    elif len(w) > 2 and w.endswith("om"):
        w = w[:-2] + "or"
    elif len(w) >= 4 and w.endswith("aim"):
        w = w[:-3] + "air"
    return w


def cosine_sim(d1: dict, d2: dict) -> float:
    if not d1 or not d2:
        return 0.0
    common = set(d1.keys()) & set(d2.keys())
    num = sum(d1[k] * d2[k] for k in common)
    den1 = sum(v * v for v in d1.values()) ** 0.5
    den2 = sum(v * v for v in d2.values()) ** 0.5
    return num / (den1 * den2) if den1 > 0 and den2 > 0 else 0.0


def edit_distance_1(s1: str, s2: str) -> bool:
    if s1 == s2:
        return False
    if abs(len(s1) - len(s2)) > 1:
        return False
    if len(s1) == len(s2):
        diffs = sum(1 for a, b in zip(s1, s2) if a != b)
        return diffs == 1
    longer, shorter = (s1, s2) if len(s1) > len(s2) else (s2, s1)
    for i in range(len(longer)):
        if longer[:i] + longer[i+1:] == shorter:
            return True
    return False


def main():
    folio_index = json.loads(INDEX_PATH.read_text(encoding="utf-8"))["folios"]
    rad_dict = dict(RADICAL_SHORT_TAG)

    prose_lines = []
    root_counts = Counter()

    for raw_line in ZL_PATH.read_text(encoding="utf-8", errors="ignore").splitlines():
        if not raw_line.startswith("<f"):
            continue
        m = re.match(r"^<([^.]+)\.([^,>]+),([^>]+)>\s*(.*)$", raw_line)
        if not m:
            continue
        folio, lnum_str, tag, body = m.group(1), m.group(2), m.group(3), m.group(4)
        if "P" not in tag:
            continue
        f_base = re.sub(r"\d+$", "", folio) if folio not in folio_index else folio
        f_meta = folio_index.get(folio, folio_index.get(f_base, {}))
        sec = f_meta.get("section", "Unknown")
        lang = f_meta.get("currier_lang", "Unknown")

        clean_body = re.sub(r"<[^>]*>", " ", body)
        raw_words = [w.strip() for w in re.split(r"[.\s,]+", clean_body) if w.strip()]
        if not raw_words:
            continue

        parsed_words = []
        n_w = len(raw_words)
        for idx_w, rw in enumerate(raw_words):
            clean_rw = re.sub(r"\[([^:\]]+):[^\]]+\]", r"\1", rw)
            clean_rw = re.sub(r"[^a-zA-Z]", "", clean_rw).lower()
            cn = normalize_token(rw)
            if not cn:
                continue
            pos = "INITIAL" if idx_w == 0 else ("FINAL" if idx_w == n_w - 1 else "MEDIAL")
            pref, suff, rt = extract_core_root_and_envelope(clean_rw, pos)
            rt = rt or cn
            clean_pref = pref.rstrip("-") or "NONE"
            clean_suff = suff.lstrip("-") or "NONE"
            # Fold medial -e-/-ee- into root/suffix cleanly so k+edy -> root k, suff edy
            if rt.endswith("ed") and clean_suff == "y" and len(rt) > 2:
                rt = rt[:-2]
                clean_suff = "edy"
            elif rt.endswith("e") and clean_suff in ("y", "dy", "ol", "or") and len(rt) > 1 and rt not in ("che", "she", "te", "ke"):
                rt = rt[:-1]
                clean_suff = "e" + clean_suff

            if clean_rw.startswith("qo") and not rt.startswith("qo"):
                env_pref = "qo-"
            elif clean_pref != "NONE":
                env_pref = clean_pref + "-"
            else:
                env_pref = "NONE"

            root_counts[rt] += 1
            parsed_words.append({
                "raw": rw,
                "clean_raw": clean_rw,
                "canon": cn,
                "env_pref": env_pref,
                "pref": clean_pref,
                "root": rt,
                "suff": clean_suff,
                "pos": pos,
                "sec": sec,
                "lang": lang
            })
        if parsed_words:
            prose_lines.append(parsed_words)

    top_150_roots = [rt for rt, _ in root_counts.most_common(150)]
    top_150_set = set(top_150_roots)
    top_60_context_roots = set(rt for rt, _ in root_counts.most_common(60))

    # Build normalized probability vectors for each of the Top 150 Core Roots
    morph_vecs = defaultdict(Counter)
    ctx_vecs = defaultdict(Counter)
    sec_vecs = defaultdict(Counter)

    for ln in prose_lines:
        n_w = len(ln)
        for i, w in enumerate(ln):
            rt = w["root"]
            if rt not in top_150_set:
                continue
            morph_vecs[rt][f"PREF:{w['env_pref']}"] += 1
            morph_vecs[rt][f"SUFF:{w['suff']}"] += 1
            ctx_vecs[rt][f"POS:{w['pos']}"] += 1
            if i > 0:
                prev_w = ln[i - 1]
                prev_rt = prev_w["root"] if prev_w["root"] in top_60_context_roots else "OTHER"
                ctx_vecs[rt][f"PREV_RT:{prev_rt}"] += 1
                ctx_vecs[rt][f"PREV_SUFF:{prev_w['suff']}"] += 1
            else:
                ctx_vecs[rt]["PREV_RT:LINE_START"] += 1
            if i < n_w - 1:
                next_w = ln[i + 1]
                next_rt = next_w["root"] if next_w["root"] in top_60_context_roots else "OTHER"
                ctx_vecs[rt][f"NEXT_RT:{next_rt}"] += 1
                ctx_vecs[rt][f"NEXT_PREF:{next_w['env_pref']}"] += 1
            else:
                ctx_vecs[rt]["NEXT_RT:LINE_END"] += 1
            sec_vecs[rt][w["sec"]] += 1

    # Normalize vectors to relative frequencies
    morph_norm = {}
    ctx_norm = {}
    sec_norm = {}
    combined_norm = {}

    for rt in top_150_roots:
        mt = max(1, sum(morph_vecs[rt].values()))
        ct = max(1, sum(ctx_vecs[rt].values()))
        st = max(1, sum(sec_vecs[rt].values()))
        morph_norm[rt] = {k: v / mt for k, v in morph_vecs[rt].items()}
        ctx_norm[rt] = {k: v / ct for k, v in ctx_vecs[rt].items()}
        sec_norm[rt] = {k: v / st for k, v in sec_vecs[rt].items()}
        comb = {}
        for k, v in morph_norm[rt].items():
            comb[f"M_{k}"] = v
        for k, v in ctx_norm[rt].items():
            comb[f"C_{k}"] = v
        combined_norm[rt] = comb

    # 1. Compute pairwise similarities across all pairs of Top 150 Core Roots
    all_pair_sims = []
    ed1_pair_sims = []
    pair_lookup = {}

    for i in range(len(top_150_roots)):
        r1 = top_150_roots[i]
        for j in range(i + 1, len(top_150_roots)):
            r2 = top_150_roots[j]
            cm = cosine_sim(morph_norm[r1], morph_norm[r2])
            cc = cosine_sim(ctx_norm[r1], ctx_norm[r2])
            cs = cosine_sim(sec_norm[r1], sec_norm[r2])
            c_comb = 0.5 * cm + 0.5 * cc
            is_ed1 = edit_distance_1(r1, r2)
            rec = {
                "root_1": r1,
                "root_2": r2,
                "count_1": root_counts[r1],
                "count_2": root_counts[r2],
                "morph_cosine": round(cm, 4),
                "context_cosine": round(cc, 4),
                "section_cosine": round(cs, 4),
                "combined_cosine": round(c_comb, 4),
                "is_edit_distance_1": is_ed1
            }
            all_pair_sims.append(rec)
            pair_lookup[(r1, r2)] = rec
            pair_lookup[(r2, r1)] = rec
            if is_ed1:
                ed1_pair_sims.append(rec)

    # Test Edit-Distance-1 Minimal-Pair Similarity vs Non-ED1 Random Pairs
    non_ed1 = [p["combined_cosine"] for p in all_pair_sims if not p["is_edit_distance_1"]]
    ed1_vals = [p["combined_cosine"] for p in ed1_pair_sims]
    mean_ed1 = sum(ed1_vals) / max(1, len(ed1_vals))
    mean_non_ed1 = sum(non_ed1) / max(1, len(non_ed1))
    std_non_ed1 = (sum((x - mean_non_ed1) ** 2 for x in non_ed1) / max(1, len(non_ed1))) ** 0.5
    # Z-score of sample mean of `len(ed1_vals)` pairs vs random pair distribution
    se_ed1 = std_non_ed1 / (max(1, len(ed1_vals)) ** 0.5)
    z_ed1 = (mean_ed1 - mean_non_ed1) / (se_ed1 if se_ed1 > 0 else 1.0)

    # 2. Evaluate Flagship Architectural Minimal Pairs
    flagship_pairs = [
        ("k", "t", "Gallows Vessel/Body (k) vs Tube/Duct (t)"),
        ("ch", "sh", "Primary Verbal Operators: Mix/Process (ch) vs Heat/Steep (sh)"),
        ("che", "she", "Extended Verbal Operators: Infuse (che) vs Decoct (she)"),
        ("cth", "ckh", "Gallows-C Operators: Leaf/Crown (cth) vs Concoct/Root (ckh)"),
        ("kch", "tch", "Pre-Gallows Operators: kch vs tch"),
        ("lch", "lsh", "Liquid-Prefixed Operators: lch vs lsh"),
        ("pch", "fch", "Top-Gallows Operators: pch vs fch"),
        ("kol", "kal", "Botanical/Vessel Stems: kol vs kal"),
        ("tol", "tal", "Conduit/Barreled-Nymph Stems: tol vs tal"),
        ("dar", "dal", "Source/Jar (dar) vs Basin/Pool (dal)"),
        ("teo", "keo", "Astrological/Pharmaceutical Pair: teo vs keo"),
        ("cheo", "sheo", "Labialized Operators: cheo vs sheo"),
        ("dch", "sch", "Dental/Sibilant Operators: dch vs sch"),
        ("lk", "lt", "Liquid-Gallows Stems: lk vs lt"),
        ("ok", "ot", "o-Gallows Nominal Stems: ok vs ot"),
        ("ar", "or", "Liquid-R Stems: ar vs or")
    ]
    flagship_results = []
    for r1, r2, desc in flagship_pairs:
        if (r1, r2) in pair_lookup:
            rec = dict(pair_lookup[(r1, r2)])
            rec["pair_description"] = desc
            flagship_results.append(rec)

    # 3. Top Nearest Neighbors for each of the Top 40 Core Roots
    nearest_neighbors = []
    for rt in top_150_roots[:40]:
        cands = []
        for other in top_150_roots:
            if other == rt:
                continue
            p = pair_lookup[(rt, other)]
            cands.append((p["combined_cosine"], other, p["morph_cosine"], p["context_cosine"], p["section_cosine"]))
        cands.sort(reverse=True)
        # Compute verbal suffix rate (`-edy/-dy`) and `q-` initial rate for `rt`
        edy_r = morph_norm[rt].get("SUFF:edy", 0.0) + morph_norm[rt].get("SUFF:dy", 0.0)
        q_r = morph_norm[rt].get("PREF:qo-", 0.0)
        o_r = morph_norm[rt].get("PREF:o-", 0.0)
        nearest_neighbors.append({
            "root": rt,
            "gloss": rad_dict.get(rt, rt),
            "count": root_counts[rt],
            "verbal_edy_dy_rate": round(edy_r, 4),
            "qo_initial_rate": round(q_r, 4),
            "o_initial_rate": round(o_r, 4),
            "top_4_distributional_synonyms": [
                {
                    "neighbor_root": nb,
                    "neighbor_gloss": rad_dict.get(nb, nb),
                    "combined_cosine": round(sc, 4),
                    "morph_cosine": round(mc, 4),
                    "context_cosine": round(cc, 4),
                    "section_cosine": round(sec_c, 4)
                }
                for sc, nb, mc, cc, sec_c in cands[:4]
            ]
        })

    # 4. Classify Top 150 Core Roots into 6 Distributional Word Classes
    word_classes = defaultdict(list)
    for rt in top_150_roots:
        edy_r = morph_norm[rt].get("SUFF:edy", 0.0) + morph_norm[rt].get("SUFF:dy", 0.0)
        q_r = morph_norm[rt].get("PREF:qo-", 0.0)
        o_r = morph_norm[rt].get("PREF:o-", 0.0)
        line_start_r = ctx_norm[rt].get("POS:INITIAL", 0.0)
        line_end_r = ctx_norm[rt].get("POS:FINAL", 0.0)

        if rt in ("ch", "sh", "che", "she", "cth", "ckh", "cheo", "sheo") or (edy_r >= 0.30 and rt.startswith(("ch", "sh", "ct", "ck"))):
            cls = "Class_I_Primary_C_Verbal_Operators"
        elif any(g in rt for g in ("kch", "tch", "pch", "fch", "lch", "lsh", "dch", "sch")) or edy_r >= 0.32:
            cls = "Class_II_Compound_Gallows_Verbal_Operators"
        elif rt in ("k", "t", "lk", "lt", "ok", "ot", "yk", "yt", "ke", "te", "keo", "teo") or q_r >= 0.22:
            cls = "Class_III_Gallows_Vessel_Conduit_Stems"
        elif rt in ("ol", "al", "or", "ar", "kol", "kal", "kar", "tol", "tal", "tar", "dar", "dal", "sol", "sal", "sar", "sor"):
            cls = "Class_IV_Liquid_Botanical_Substance_Nouns"
        elif line_start_r + line_end_r >= 0.35 or rt in ("d", "s", "r", "l", "y", "o", "a", "ain", "aiin", "air", "am", "dy"):
            cls = "Class_V_Deictic_Clause_Boundary_Particles"
        else:
            cls = "Class_VI_Specialized_Domain_Nouns"

        word_classes[cls].append({
            "root": rt,
            "gloss": rad_dict.get(rt, rt),
            "count": root_counts[rt],
            "edy_dy_rate": round(edy_r, 3),
            "qo_rate": round(q_r, 3),
            "o_rate": round(o_r, 3)
        })

    ed1_pair_sims.sort(key=lambda x: -x["combined_cosine"])

    out = {
        "summary": {
            "top_roots_analyzed": len(top_150_roots),
            "total_pairs_evaluated": len(all_pair_sims),
            "edit_distance_1_minimal_pairs_count": len(ed1_pair_sims),
            "mean_ed1_combined_cosine": round(mean_ed1, 4),
            "mean_non_ed1_combined_cosine": round(mean_non_ed1, 4),
            "std_non_ed1_combined_cosine": round(std_non_ed1, 4),
            "ed1_vs_random_z_score": round(z_ed1, 2),
            "word_class_counts": {k: len(v) for k, v in word_classes.items()}
        },
        "flagship_minimal_pairs": flagship_results,
        "top_edit_distance_1_allomorph_pairs": ed1_pair_sims[:35],
        "top_40_roots_nearest_neighbors": nearest_neighbors,
        "distributional_word_classes": dict(word_classes)
    }

    OUT_PATH.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"Saved Attack 23 results to {OUT_PATH}")
    print(f"Edit-Distance-1 Minimal Pairs (n={len(ed1_pair_sims)}): mean_cosine={mean_ed1:.4f} vs non-ED1 {mean_non_ed1:.4f} ± {std_non_ed1:.4f} (z = {z_ed1:+.2f})")
    print("\n--- Flagship Architectural Minimal Pairs ---")
    for fp in flagship_results:
        print(f"  {fp['root_1']:5s} <-> {fp['root_2']:5s} (n={fp['count_1']:4d},{fp['count_2']:4d}): comb={fp['combined_cosine']:.4f} (morph={fp['morph_cosine']:.4f}, ctx={fp['context_cosine']:.4f}, sec={fp['section_cosine']:.4f}) | {fp['pair_description']}")
    print("\n--- Top 12 Nearest-Neighbor Substitution Pairs ---")
    for nb in nearest_neighbors[:12]:
        top_syns = [(s["neighbor_root"], s["combined_cosine"]) for s in nb["top_4_distributional_synonyms"]]
        print(f"  {nb['root']:5s} ({nb['gloss']:22s}, n={nb['count']:4d}, edy={nb['verbal_edy_dy_rate']:.2f}, qo={nb['qo_initial_rate']:.2f}) -> {top_syns}")


if __name__ == "__main__":
    main()
