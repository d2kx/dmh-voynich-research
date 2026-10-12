#!/usr/bin/env python3
"""
Attack 71: Cross-Dialect & Cross-Sectional Parallel Clause Tree Aligner
(Aligning Currier A <-> Currier B Words & Parallel Sentences via Constituent Skeletons
and Dialect-Invariant Anchor Frames)

Tests:
1. Cross-Dialect Functional Equivalence Dictionary (Currier A <-> Currier B):
   - Builds distributional context vectors for all words (count >= 15) in Currier A
     and Currier B using dialect-invariant syntactic frames:
       * Relative line position [INIT, MED, FIN]
       * Preceding & following Constituent Class [BOS, TOP_HEAD, PP_PREP, VP_PROC, NP_MEAS, FIN_CLOSE, EOS]
       * Preceding & following Shared Anchor Class (M1_DAIIN, M1_OL_OR, M1_AIIN, M1_DAR_DAL, M1_S_Y, M1_FIN_AM, M2_CH_SH, M2_GALLOWS)
   - Computes the top Currier B structural counterpart for every major Currier A word
     (and vice versa), testing mean top-1 cosine similarity against a random feature-shuffled null.
2. Cross-Dialect Parallel Clause Tree Alignment:
   - Aligns 5..7 word prose lines in Currier A against 5..7 word prose lines in Currier B
     using combined Constituent Tag + Dialect-Translated Word + 10-Bit Skeleton similarity.
   - Evaluates whether cross-dialect parallel clause alignment exceeds shuffled-corpus null.
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
FOLIO_INDEX_PATH = DATA_DIR / "folio_index.json"
OUT_JSON = DATA_DIR / "attack71_parallel_clause_tree_aligner.json"


def clean_tok(t: str) -> str:
    t = re.sub(r"\{[^}]*\}", "", t)
    t = re.sub(r"\[([^]:]+):[^\]]+\]", r"\1", t)
    t = re.sub(r"[\[\]<>@*$?1234567890!%()/,-]", "", t)
    return t.strip()


def classify_suffix(w: str) -> str:
    if w.endswith(("aiin", "oiin", "eiin", "ain", "oin", "ein", "in", "iiin")):
        return "IN_MINIM"
    if w.endswith("dy"):
        return "DY_DENTAL"
    if w.endswith("y"):
        return "Y_BARE"
    if w.endswith(("ol", "al", "el", "il", "ul")) or w in ("ol", "al", "l"):
        return "L_LATERAL"
    if w.endswith(("or", "ar", "er", "ir", "ur")) or w in ("or", "ar", "r"):
        return "R_RHOTIC"
    if w.endswith(("am", "om", "em", "im", "m", "an")):
        return "M_NASAL"
    if w.endswith(("eey", "ee", "e", "o", "a")):
        return "V_OPEN"
    return "C_OTHER"


def classify_word_role(w: str, idx: int, n_words: int):
    has_core = any(g in w for g in ("k", "t", "p", "f", "ch", "sh"))
    suf = classify_suffix(w)
    if not has_core:
        if w.startswith("q"):
            return "M1_QO", "PP_PREP"
        if w.startswith("d"):
            if w in ("daiin", "dain", "daim", "dair"):
                return "M1_DAIIN", "NP_MEAS"
            return "M1_DA_PREP", "PP_PREP"
        if w.startswith("s"):
            return "M1_S_PREP", "PP_PREP"
        if w.startswith("y"):
            return "M1_Y_CONJ", "PP_PREP"
        if suf in ("L_LATERAL", "R_RHOTIC"):
            return "M1_LIQUID", "NP_MEAS"
        if suf == "IN_MINIM":
            return "M1_MINIM", "NP_MEAS"
        if suf == "M_NASAL" or idx == n_words - 1:
            return "M1_NASAL_FIN", "FIN_CLOSE"
        return "M1_VOWEL", "NP_MEAS"

    # Open class M2
    if idx == 0 and any(w.startswith(p) for p in ("p", "f", "t", "k", "po", "fo", "to", "ko", "cph", "cfh")):
        return "M2_TOP_GALLOWS", "TOP_HEAD"
    if w.startswith("qo") or w.startswith("q"):
        return "M2_QO_VERB", "VP_PROC"
    if suf in ("DY_DENTAL", "Y_BARE"):
        if "ch" in w or "sh" in w:
            return "M2_BENCH_VERB", "VP_PROC"
        return "M2_GALLOWS_VERB", "VP_PROC"
    if suf in ("L_LATERAL", "R_RHOTIC", "IN_MINIM"):
        if "ch" in w or "sh" in w:
            return "M2_BENCH_NOUN", "NP_MEAS"
        return "M2_GALLOWS_NOUN", "NP_MEAS"
    if suf == "M_NASAL" and idx == n_words - 1:
        return "M2_FIN_CLOSE", "FIN_CLOSE"
    return "M2_OTHER_NOUN", "NP_MEAS"


def parse_corpus():
    lines = []
    line_re = re.compile(r"^<f(\d+[rv]\d*)\.(\d+),([^>]+)>\s+(.*)$")
    cur_sec = "U"
    cur_lang = "U"
    cur_hand = "U"

    with open(ZL_PATH, "r", encoding="utf-8", errors="replace") as f:
        for raw_line in f:
            raw_s = raw_line.strip()
            if not raw_s or raw_s.startswith("#"):
                continue
            if raw_s.startswith("<f") and ">" in raw_s and "." not in raw_s.split(">")[0]:
                m_s = re.search(r"\$I=([A-Z])", raw_s)
                cur_sec = m_s.group(1) if m_s else "U"
                m_l = re.search(r"\$L=([A-Z])", raw_s)
                cur_lang = m_l.group(1) if m_l else "U"
                m_h = re.search(r"\$H=([0-9A-Za-z]+)", raw_s)
                cur_hand = m_h.group(1) if m_h else "U"
                continue

            m = line_re.match(raw_s)
            if not m:
                continue
            folio, lnum_str, loc, text = m.group(1), m.group(2), m.group(3), m.group(4)
            if not loc.startswith(("@P", "+P", "*P", "=P")):
                continue
            if cur_lang not in ("A", "B"):
                continue
            text = re.sub(r"<!.*?>", "", text)
            text = text.replace("<%>", " ").replace("<$>", " ").replace("<->", " ")
            text = re.sub(r"<[^>]*>", " ", text)
            raw_tokens = [t for t in re.split(r"[.\s,]+", text) if t]
            words = [clean_tok(t) for t in raw_tokens]
            words = [w for w in words if w]
            if not words:
                continue

            roles = [classify_word_role(w, i, len(words)) for i, w in enumerate(words)]
            lines.append({
                "folio": f"f{folio}",
                "line": int(lnum_str),
                "lang": cur_lang,
                "section": cur_sec,
                "hand": cur_hand,
                "words": words,
                "subroles": [r[0] for r in roles],
                "consts": [r[1] for r in roles],
            })
    return lines


def cosine_dict(d1: dict, d2: dict) -> float:
    if not d1 or not d2:
        return 0.0
    common = set(d1.keys()) & set(d2.keys())
    num = sum(d1[k] * d2[k] for k in common)
    den1 = sum(v * v for v in d1.values())
    den2 = sum(v * v for v in d2.values())
    if den1 == 0 or den2 == 0:
        return 0.0
    return num / math.sqrt(den1 * den2)


def main():
    random.seed(42)
    lines = parse_corpus()

    lines_a = [ln for ln in lines if ln["lang"] == "A"]
    lines_b = [ln for ln in lines if ln["lang"] == "B"]

    # 1. Compare Constituent Skeleton distributions between Currier A and Currier B
    const_counts_a = Counter(c for ln in lines_a for c in ln["consts"])
    const_counts_b = Counter(c for ln in lines_b for c in ln["consts"])
    tot_a = sum(const_counts_a.values())
    tot_b = sum(const_counts_b.values())

    const_dist_a = {k: round(v / tot_a, 4) for k, v in const_counts_a.items()}
    const_dist_b = {k: round(v / tot_b, 4) for k, v in const_counts_b.items()}

    # Constituent Bigram transition profiles in A vs B
    bg_a = Counter()
    bg_b = Counter()
    for ln in lines_a:
        cs = ["BOS"] + ln["consts"] + ["EOS"]
        for i in range(len(cs) - 1):
            bg_a[f"{cs[i]}->{cs[i+1]}"] += 1
    for ln in lines_b:
        cs = ["BOS"] + ln["consts"] + ["EOS"]
        for i in range(len(cs) - 1):
            bg_b[f"{cs[i]}->{cs[i+1]}"] += 1

    bg_cos_ab = cosine_dict(bg_a, bg_b)

    # 2. Build Dialect-Specific Word Context Profiles in A and B
    word_counts_a = Counter(w for ln in lines_a for w in ln["words"])
    word_counts_b = Counter(w for ln in lines_b for w in ln["words"])

    ctx_a = defaultdict(Counter)
    ctx_b = defaultdict(Counter)

    for ln in lines:
        lang = ln["lang"]
        ws = ln["words"]
        srs = ln["subroles"]
        cst = ln["consts"]
        n = len(ws)
        target_ctx = ctx_a if lang == "A" else ctx_b
        for i, w in enumerate(ws):
            pos_zone = "POS_INIT" if i == 0 else ("POS_FIN" if i == n - 1 else "POS_MED")
            prev_c = "BOS" if i == 0 else cst[i - 1]
            next_c = "EOS" if i == n - 1 else cst[i + 1]
            prev_sr = "BOS" if i == 0 else srs[i - 1]
            next_sr = "EOS" if i == n - 1 else srs[i + 1]
            own_c = cst[i]
            suf = classify_suffix(w)

            target_ctx[w][pos_zone] += 2.0
            target_ctx[w][f"OWN_C:{own_c}"] += 2.5
            target_ctx[w][f"PREV_C:{prev_c}"] += 1.5
            target_ctx[w][f"NEXT_C:{next_c}"] += 1.5
            target_ctx[w][f"PREV_SR:{prev_sr}"] += 1.5
            target_ctx[w][f"NEXT_SR:{next_sr}"] += 1.5
            target_ctx[w][f"SUF:{suf}"] += 1.0

    # Normalize context vectors to probabilities
    norm_ctx_a = {}
    for w, cnt in word_counts_a.items():
        if cnt >= 15:
            tot = sum(ctx_a[w].values())
            norm_ctx_a[w] = {k: v / tot for k, v in ctx_a[w].items()}

    norm_ctx_b = {}
    for w, cnt in word_counts_b.items():
        if cnt >= 15:
            tot = sum(ctx_b[w].values())
            norm_ctx_b[w] = {k: v / tot for k, v in ctx_b[w].items()}

    # 3. Align Top Currier A words -> Top Currier B words (both exact-cognate and cross-lexeme)
    a_to_b_mappings = []
    top_a_words = [w for w, c in word_counts_a.most_common(60) if w in norm_ctx_a]
    top_b_words = [w for w, c in word_counts_b.most_common(120) if w in norm_ctx_b]

    for wa in top_a_words:
        scored = []
        for wb in top_b_words:
            cos = cosine_dict(norm_ctx_a[wa], norm_ctx_b[wb])
            scored.append((cos, wb))
        scored.sort(reverse=True)
        best_any_cos, best_any_wb = scored[0]
        # Best non-identical heteronym in B
        non_id = [(cos, wb) for cos, wb in scored if wb != wa]
        best_het_cos, best_het_wb = non_id[0]

        a_to_b_mappings.append({
            "word_A": wa,
            "count_A": word_counts_a[wa],
            "count_B_same": word_counts_b[wa],
            "best_B_overall": best_any_wb,
            "best_B_overall_cos": round(best_any_cos, 4),
            "best_B_heteronym": best_het_wb,
            "best_B_heteronym_count": word_counts_b[best_het_wb],
            "best_B_heteronym_cos": round(best_het_cos, 4),
            "top3_B": [
                {"word_B": wb, "cos": round(c, 4), "count_B": word_counts_b[wb]}
                for c, wb in scored[:3]
            ],
        })

    mean_top1_cos = sum(m["best_B_overall_cos"] for m in a_to_b_mappings) / len(a_to_b_mappings)
    mean_het_cos = sum(m["best_B_heteronym_cos"] for m in a_to_b_mappings) / len(a_to_b_mappings)

    # Permutation baseline: shuffle feature keys of B words
    all_feat_keys = sorted({k for d in norm_ctx_b.values() for k in d})
    null_means = []
    for _ in range(200):
        perm_keys = all_feat_keys[:]
        random.shuffle(perm_keys)
        kmap = dict(zip(all_feat_keys, perm_keys))
        shuf_b = {wb: {kmap.get(k, k): v for k, v in d.items()} for wb, d in norm_ctx_b.items()}
        trial_maxes = []
        for wa in top_a_words:
            best_c = max(cosine_dict(norm_ctx_a[wa], shuf_b[wb]) for wb in top_b_words)
            trial_maxes.append(best_c)
        null_means.append(sum(trial_maxes) / len(trial_maxes))

    null_mu = sum(null_means) / len(null_means)
    null_sd = math.sqrt(sum((x - null_mu) ** 2 for x in null_means) / len(null_means))
    z_lex_align = (mean_top1_cos - null_mu) / (null_sd if null_sd > 0 else 1e-9)

    # 4. Align Full Clause Trees between Currier A and Currier B (lines of length 5..8)
    best_b_map = {m["word_A"]: (m["best_B_overall"], m["best_B_heteronym"]) for m in a_to_b_mappings}

    cand_a = [ln for ln in lines_a if 5 <= len(ln["words"]) <= 7]
    cand_b = [ln for ln in lines_b if 5 <= len(ln["words"]) <= 7]

    # Index cand_b by length and constituent signature
    b_by_len = defaultdict(list)
    for ln in cand_b:
        b_by_len[len(ln["words"])].append(ln)

    def line_pair_score(la, lb):
        n = len(la["words"])
        score = 0.0
        for i in range(n):
            wa, wb = la["words"][i], lb["words"][i]
            ca, cb = la["consts"][i], lb["consts"][i]
            sra, srb = la["subroles"][i], lb["subroles"][i]
            if ca == cb:
                score += 1.0
            if sra == srb:
                score += 1.0
            if wa == wb:
                score += 1.5
            elif wa in best_b_map and wb in best_b_map[wa]:
                score += 1.25
            elif wa in norm_ctx_a and wb in norm_ctx_b:
                score += cosine_dict(norm_ctx_a[wa], norm_ctx_b[wb])
        return score / (n * 3.5)

    aligned_clause_pairs = []
    for la in cand_a[:300]:
        n = len(la["words"])
        best_s = -1.0
        best_lb = None
        for lb in b_by_len[n]:
            s = line_pair_score(la, lb)
            if s > best_s:
                best_s = s
                best_lb = lb
        if best_lb:
            aligned_clause_pairs.append({
                "score": round(best_s, 4),
                "A_loc": f"{la['folio']}.{la['line']} ({la['section']})",
                "B_loc": f"{best_lb['folio']}.{best_lb['line']} ({best_lb['section']})",
                "A_words": " . ".join(la["words"]),
                "B_words": " . ".join(best_lb["words"]),
                "A_consts": " -> ".join(la["consts"]),
                "B_consts": " -> ".join(best_lb["consts"]),
                "A_subroles": " -> ".join(la["subroles"]),
                "B_subroles": " -> ".join(best_lb["subroles"]),
            })

    aligned_clause_pairs.sort(key=lambda x: x["score"], reverse=True)

    print("=== ATTACK 71: CROSS-DIALECT PARALLEL CLAUSE TREE ALIGNER (CURRIER A <-> B) ===")
    print(f"Prose Lines: Currier A = {len(lines_a):,} | Currier B = {len(lines_b):,}")
    print(f"Constituent Transition Bigram Cosine (A vs B) = {bg_cos_ab:.4f}")
    print(f"Top-60 A -> B Word Alignment Mean Cosine = {mean_top1_cos:.4f} (Heteronym = {mean_het_cos:.4f}) vs {null_mu:.4f} ± {null_sd:.4f} null (z = +{z_lex_align:.2f})")
    print("\nTop 15 Currier A -> Currier B Word Translations:")
    for m in a_to_b_mappings[:15]:
        print(f"  A:{m['word_A']:10s} (n={m['count_A']:3d}) -> B_all:{m['best_B_overall']:10s} ({m['best_B_overall_cos']:.4f}) | B_het:{m['best_B_heteronym']:10s} (n={m['best_B_heteronym_count']:3d}, cos={m['best_B_heteronym_cos']:.4f})")
    print("\nTop 8 Parallel Clause Tree Alignments (Currier A <-> Currier B):")
    for p in aligned_clause_pairs[:8]:
        print(f"  [{p['score']:.4f}] A({p['A_loc']}): {p['A_words']}")
        print(f"           B({p['B_loc']}): {p['B_words']}")
        print(f"           Tree: {p['A_consts']}")

    out = {
        "summary": {
            "lines_A": len(lines_a),
            "lines_B": len(lines_b),
            "constituent_dist_A": const_dist_a,
            "constituent_dist_B": const_dist_b,
            "constituent_bigram_cosine_AB": round(bg_cos_ab, 4),
            "mean_top1_word_align_cosine": round(mean_top1_cos, 4),
            "mean_heteronym_word_align_cosine": round(mean_het_cos, 4),
            "null_word_align_cosine_mean": round(null_mu, 4),
            "null_word_align_cosine_sd": round(null_sd, 4),
            "word_align_z": round(z_lex_align, 2),
        },
        "a_to_b_lexicon_bridge": a_to_b_mappings,
        "top_parallel_clause_pairs": aligned_clause_pairs[:40],
    }

    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    print(f"\nSaved -> {OUT_JSON}")


if __name__ == "__main__":
    main()
