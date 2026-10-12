#!/usr/bin/env python3
"""
Attack 77: Codicological Quire ($Q), Physical Bifolio Sheet ($B), Leaf ($F),
and Facing Open-Spread Continuity Solver

Extracts all codicological metadata ($Q, $P, $F, $B, $I, $L, $H, $C, $X) from ZL3b-n.txt
across all 226 folios and tests:

1. Physical Bifolio ($B) Language & Scribe-Hand Integrity in Mixed Herbal Quires ($Q=C,D,E,G,H):
   - In quires where Currier A ($L=A, Hand 1) and Currier B ($L=B, Hand 2) are interleaved,
     do conjugate leaves belonging to the SAME physical parchment bifolio ($Q, $B) share
     the exact same Currier language ($L) and Scribe Hand ($H)?
2. Within-Quire Lexical & Morphological Continuity Across 4 Physical Relationships
   (Strictly stratified within matching ($Q, $I, $L, $H)):
   - (A) `SAME_LEAF_RV` (`Recto <-> Verso`: same $Q, same $F)
   - (B) `FACING_SPREAD_VR` (`Verso_k <-> Recto_{k+1}`: consecutive pages $P on different $F)
   - (C) `CONJUGATE_BIFOLIO` (`Same $Q and $B, Different $F`: opposite halves of the same parchment sheet, separated across the quire centerfold)
   - (D) `UNRELATED_SAME_QUIRE` (`Same $Q, $I, $L, $H`, but different $F, not facing spread, and different $B)
3. Bifolio Sheet Depth ($B=1 Outer Sheet -> $B=2 -> $B=3 -> $B=4+ Inner Centerfold):
   - Tests how word density, word length, and suffix/prefix distributions vary from outer
     parchment sheets ($B=1) to inner centerfold sheets ($B=4+).
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
OUT_JSON = DATA_DIR / "attack77_codicological_bifolio_and_spread_continuity.json"

LOCUS_RE = re.compile(r"^<f([0-9]+[rv][0-9]*|Ros)\.([^,>]+),([^>]+)>\s*(.*)$")


def clean_tokens(raw: str):
    s = re.sub(r"\{[^}]*\}", "", raw)
    s = re.sub(r"\[([^:\]]+):[^\]]+\]", r"\1", s)
    s = s.replace("<%>", " ").replace("<$>", " ").replace("<->", " ")
    s = re.sub(r"<[^>]*>", " ", s)
    s = re.sub(r"@[0-9]+;", "", s)
    s = re.sub(r"[^a-zA-Z.\s]", "", s).lower()
    return [t for t in s.replace(".", " ").split() if t]


def extract_open_stem(w: str):
    if not any(g in w for g in ("k", "t", "p", "f", "ch", "sh")):
        return None
    rem = w
    for p in ("qol", "dal", "ol", "al", "qo", "po", "fo", "o", "y", "s", "d", "l", "q"):
        if rem.startswith(p) and len(rem) > len(p) + 1 and any(g in rem[len(p):] for g in ("k", "t", "p", "f", "ch", "sh")):
            rem = rem[len(p):]
            break
    s_norm = rem.replace("cph", "cth").replace("cfh", "ckh").replace("p", "t").replace("f", "k")
    s_norm = re.sub(r"e+", "e", s_norm)
    s_norm = re.sub(r"i+", "i", s_norm)
    return s_norm


def jaccard(s1: set, s2: set) -> float:
    if not s1 or not s2:
        return 0.0
    inter = len(s1 & s2)
    union = len(s1 | s2)
    return inter / union if union else 0.0


def cosine_counter(c1: Counter, c2: Counter) -> float:
    if not c1 or not c2:
        return 0.0
    common = set(c1.keys()) & set(c2.keys())
    num = sum(c1[k] * c2[k] for k in common)
    d1 = sum(v * v for v in c1.values())
    d2 = sum(v * v for v in c2.values())
    return num / math.sqrt(d1 * d2) if d1 and d2 else 0.0


def main():
    random.seed(42)
    folios = []
    cur_meta = None

    for raw_line in ZL_PATH.read_text(encoding="utf-8", errors="replace").splitlines():
        raw_s = raw_line.strip()
        if not raw_s or raw_s.startswith("#"):
            continue
        if raw_s.startswith("<f") and ">" in raw_s and "." not in raw_s.split(">")[0]:
            fname = raw_s.split(">")[0][1:]
            tags = dict(re.findall(r"\$([A-Z])=([0-9A-Za-z]+)", raw_s))
            cur_meta = {
                "folio": fname,
                "Q": tags.get("Q", "U"),
                "P": tags.get("P", "U"),
                "F": tags.get("F", "U"),
                "B": tags.get("B", "U"),
                "I": tags.get("I", "U"),
                "L": tags.get("L", "U"),
                "H": tags.get("H", "U"),
                "C": tags.get("C", "U"),
                "X": tags.get("X", "U"),
                "words": [],
                "first_line_words": [],
                "last_line_words": [],
            }
            folios.append(cur_meta)
            continue

        m = LOCUS_RE.match(raw_s)
        if not m or cur_meta is None:
            continue
        ltype, raw_txt = m.group(3), m.group(4)
        if not ltype.startswith(("@P", "+P", "*P", "=P")):
            continue
        toks = clean_tokens(raw_txt)
        if not toks:
            continue
        if not cur_meta["first_line_words"]:
            cur_meta["first_line_words"] = toks
        cur_meta["last_line_words"] = toks
        cur_meta["words"].extend(toks)

    # Filter to folios with >= 25 prose words
    valid_folios = [f for f in folios if len(f["words"]) >= 25]
    for f in valid_folios:
        stems = [extract_open_stem(w) for w in f["words"]]
        stems = [s for s in stems if s]
        f["stem_set"] = set(stems)
        f["stem_counts"] = Counter(stems)
        f["word_set"] = set(f["words"])
        f["word_counts"] = Counter(f["words"])
        f["p_ord"] = ord(f["P"][0]) - ord("A") if len(f["P"]) == 1 and f["P"].isalpha() else -1

    # 1. Mixed-Language Quire Bifolio ($B) Concordance Test
    # Group folios by ($Q, $B)
    quires_langs = defaultdict(set)
    for f in folios:
        if f["L"] in ("A", "B"):
            quires_langs[f["Q"]].add(f["L"])
    mixed_quires = sorted(q for q, ls in quires_langs.items() if len(ls) == 2)

    mixed_bifolia = defaultdict(list)
    for f in folios:
        if f["Q"] in mixed_quires and f["L"] in ("A", "B") and f["B"] != "U":
            mixed_bifolia[(f["Q"], f["B"])].append(f)

    same_b_pairs = 0
    same_b_same_lang = 0
    diff_b_pairs = 0
    diff_b_same_lang = 0

    for q in mixed_quires:
        q_fols = [f for f in folios if f["Q"] == q and f["L"] in ("A", "B") and f["B"] != "U"]
        for i in range(len(q_fols)):
            for j in range(i + 1, len(q_fols)):
                fi, fj = q_fols[i], q_fols[j]
                if fi["F"] == fj["F"]:
                    continue  # skip Recto-Verso of the exact same leaf; test conjugate leaves across the fold!
                is_same_lang = 1 if fi["L"] == fj["L"] else 0
                if fi["B"] == fj["B"]:
                    same_b_pairs += 1
                    same_b_same_lang += is_same_lang
                else:
                    diff_b_pairs += 1
                    diff_b_same_lang += is_same_lang

    conjugate_lang_concordance = same_b_same_lang / max(same_b_pairs, 1)
    nonconjugate_lang_concordance = diff_b_same_lang / max(diff_b_pairs, 1)

    mixed_quire_layout = []
    for (q, b), flist in sorted(mixed_bifolia.items()):
        mixed_quire_layout.append({
            "quire": q,
            "bifolio_sheet": b,
            "folios": [f"{x['folio']}(F={x['F']},L={x['L']},H={x['H']})" for x in flist],
            "languages": sorted({x["L"] for x in flist}),
            "is_uniform_language": len({x["L"] for x in flist}) == 1,
        })

    # 2. Within-Quire Lexical & Stem Continuity Across 4 Physical Relationships
    # Strictly stratified within matching ($Q, $I, $L, $H)
    rel_metrics = defaultdict(lambda: {"stem_jacc": [], "word_jacc": [], "stem_cos": [], "pairs": []})

    by_qilh = defaultdict(list)
    for f in valid_folios:
        by_qilh[(f["Q"], f["I"], f["L"], f["H"])].append(f)

    for bucket_key, b_fols in by_qilh.items():
        if len(b_fols) < 2:
            continue
        for i in range(len(b_fols)):
            for j in range(i + 1, len(b_fols)):
                fi, fj = b_fols[i], b_fols[j]
                sj = jaccard(fi["stem_set"], fj["stem_set"])
                wj = jaccard(fi["word_set"], fj["word_set"])
                sc = cosine_counter(fi["stem_counts"], fj["stem_counts"])

                if fi["F"] == fj["F"] and fi["F"] != "U":
                    rel = "1_SAME_LEAF_RV"
                elif abs(fi["p_ord"] - fj["p_ord"]) == 1 and fi["F"] != fj["F"] and fi["p_ord"] >= 0 and fj["p_ord"] >= 0:
                    rel = "2_FACING_SPREAD_VR"
                elif fi["B"] == fj["B"] and fi["B"] != "U" and fi["F"] != fj["F"]:
                    rel = "3_CONJUGATE_BIFOLIO"
                else:
                    rel = "4_UNRELATED_SAME_QUIRE"

                rel_metrics[rel]["stem_jacc"].append(sj)
                rel_metrics[rel]["word_jacc"].append(wj)
                rel_metrics[rel]["stem_cos"].append(sc)
                rel_metrics[rel]["pairs"].append((sc, f"{fi['folio']}<->{fj['folio']} (Q={fi['Q']},B={fi['B']})"))

    rel_summary = {}
    base_jacc = rel_metrics["4_UNRELATED_SAME_QUIRE"]["stem_jacc"]
    base_mu = sum(base_jacc) / len(base_jacc)
    base_sd = math.sqrt(sum((x - base_mu) ** 2 for x in base_jacc) / len(base_jacc))

    for rel in sorted(rel_metrics.keys()):
        m = rel_metrics[rel]
        sjs = m["stem_jacc"]
        wjs = m["word_jacc"]
        scs = m["stem_cos"]
        n = len(sjs)
        mu_sj = sum(sjs) / n
        mu_wj = sum(wjs) / n
        mu_sc = sum(scs) / n
        # Two-sample z vs UNRELATED_SAME_QUIRE
        se = base_sd * math.sqrt(1.0 / n + 1.0 / len(base_jacc))
        z_vs_unrel = (mu_sj - base_mu) / (se if se > 0 else 1e-9)
        top_p = sorted(m["pairs"], reverse=True)[:5]
        rel_summary[rel] = {
            "pair_count": n,
            "mean_stem_jaccard": round(mu_sj, 4),
            "mean_word_jaccard": round(mu_wj, 4),
            "mean_stem_cosine": round(mu_sc, 4),
            "z_vs_unrelated_same_quire": round(z_vs_unrel, 2),
            "top_pairs": [{"pair": p[1], "stem_cosine": round(p[0], 4)} for p in top_p],
        }

    # 3. Bifolio Sheet Depth ($B=1 Outer -> $B=4+ Inner Centerfold)
    by_b_depth = defaultdict(list)
    for f in valid_folios:
        if f["B"].isdigit():
            b_num = min(int(f["B"]), 4)
            by_b_depth[b_num].append(f)

    b_depth_summary = {}
    for b_num in sorted(by_b_depth.keys()):
        flist = by_b_depth[b_num]
        all_ws = [w for f in flist for w in f["words"]]
        b_depth_summary[f"B={b_num}"] = {
            "folios": len(flist),
            "mean_words_per_folio": round(len(all_ws) / len(flist), 1),
            "mean_word_len": round(sum(len(w) for w in all_ws) / len(all_ws), 3),
            "qo_pct": round(sum(1 for w in all_ws if w.startswith("q")) / len(all_ws) * 100, 2),
            "dy_pct": round(sum(1 for w in all_ws if w.endswith("dy")) / len(all_ws) * 100, 2),
        }

    print("=== ATTACK 77: CODICOLOGICAL QUIRE ($Q), BIFOLIO ($B) & SPREAD CONTINUITY ===")
    print(f"Mixed-Language Quires ($L=A & $L=B): {mixed_quires}")
    print(f"Conjugate Bifolio Sheet-Mate ($B) Language Concordance in Mixed Quires: {same_b_same_lang}/{same_b_pairs} = {conjugate_lang_concordance*100:.2f}% vs Non-Conjugate {diff_b_same_lang}/{diff_b_pairs} = {nonconjugate_lang_concordance*100:.2f}%")
    print("\nWithin-Quire Continuity (Strictly Stratified by $Q, $I, $L, $H):")
    for rel, st in rel_summary.items():
        print(f"  {rel:24s} (n={st['pair_count']:3d}): StemJacc={st['mean_stem_jaccard']:.4f} | WordJacc={st['mean_word_jaccard']:.4f} | StemCos={st['mean_stem_cosine']:.4f} | z = {st['z_vs_unrelated_same_quire']:+.2f}")
    print("\nBifolio Sheet Depth ($B=1 Outer -> $B=4 Inner Centerfold):")
    for k, v in b_depth_summary.items():
        print(f"  {k}: {v['folios']:2d} folios | Words/Folio={v['mean_words_per_folio']:5.1f} | Len={v['mean_word_len']:.3f} | qo%={v['qo_pct']:5.2f}% | -dy%={v['dy_pct']:5.2f}%")

    out = {
        "mixed_quire_bifolio_test": {
            "mixed_quires": mixed_quires,
            "conjugate_leaf_pairs_tested": same_b_pairs,
            "conjugate_same_language_hits": same_b_same_lang,
            "conjugate_same_language_pct": round(conjugate_lang_concordance * 100, 2),
            "nonconjugate_leaf_pairs_tested": diff_b_pairs,
            "nonconjugate_same_language_hits": diff_b_same_lang,
            "nonconjugate_same_language_pct": round(nonconjugate_lang_concordance * 100, 2),
            "mixed_quire_bifolia": mixed_quire_layout,
        },
        "within_quire_continuity": rel_summary,
        "bifolio_sheet_depth": b_depth_summary,
    }
    OUT_JSON.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"\nSaved -> {OUT_JSON}")


if __name__ == "__main__":
    main()
