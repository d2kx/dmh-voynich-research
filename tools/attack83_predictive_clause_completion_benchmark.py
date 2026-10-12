#!/usr/bin/env python3
"""
Attack 83 (Discovery 100): End-to-End Predictive Word & Clause Completion Benchmark —
Measuring Information-Theoretic Perplexity Reduction and Masked-Slot Prediction Accuracy
of the Unified Voynich Grammar on Held-Out Lines

Evaluates on a strict 80% Train / 20% Held-Out Test split (every 5th line across all 226 folios,
n_test_tokens = 6,866):
1. Progressive 7-Stage Held-Out Cross-Entropy (bits/word) & Perplexity Cascade:
   - M0: Uniform Vocabulary Baseline (`log2 |V|`)
   - M1: Global Unigram Zipf Distribution (`P(w)`)
   - M2: + Section (`$I`) & Currier Dialect (`$L`) Conditioning (`P(w | I, L)`)
   - M3: + `3x3` Spatial Paragraph Grid (`L_zone x W_zone`) Conditioning
   - M4: + Constituent Automaton & Cross-Word Moraic/Coda Harmony Bigram Conditioning
   - M5: + Intra-Paragraph Anaphoric Topic Cache (`P_para(w)` active words/stems in paragraph)
   - M6: + Factored Dual-Matrix Morpheme Grammar (`P(Prefix | ctx) * P(Core | I, L, ParaCache) * P(Suffix | ctx, Core)`)
2. Context-Only Masked Slot Prediction Accuracy (predicting attributes of masked word `w_t`
   using ONLY `(I, L, L_zone, W_zone, prev_word, next_word, para_topic_cache)` without seeing `w_t`):
   - Task A: 10-Bit Binary Feature Vector (`F1..F10` mean bitwise accuracy vs. majority baseline)
   - Task B: 5-Way Constituent Role (`TOP_HEAD, PP_PREP, VP_PROC, NP_MEAS, FIN_CLOSE` Top-1 & Top-2 accuracy)
   - Task C: Prefix Slot Class (`8` classes: Top-1 & Top-2 accuracy)
   - Task D: Suffix Inflection Class (`7` classes: Top-1 & Top-2 accuracy)
   - Task E: Open-Class Stem Retrieval from Bayesian-Weighted Intra-Paragraph Anaphoric Cache + `(I,L)` Prior
     (Top-1, Top-5, Top-10, Top-25 recall vs. unconditioned global baseline).
"""

import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
ZL_PATH = DATA_DIR / "ZL3b-n.txt"
OUT_JSON = DATA_DIR / "attack83_predictive_clause_completion_benchmark.json"

LOCUS_RE = re.compile(r"^<f([0-9]+[rv][0-9]*|Ros)\.([^,>]+),([^>]+)>\s*(.*)$")


def clean_tokens(raw: str):
    s = re.sub(r"\{[^}]*\}", "", raw)
    s = re.sub(r"\[([^:\]]+):[^\]]+\]", r"\1", s)
    s = s.replace("<%>", " ").replace("<$>", " ").replace("<->", " ")
    s = re.sub(r"<[^>]*>", " ", s)
    s = re.sub(r"@[0-9]+;", "", s)
    s = re.sub(r"[^a-zA-Z.\s]", "", s).lower()
    return [t for t in s.replace(".", " ").split() if t]


def get_prefix_class(w: str) -> str:
    if any(g in w[:2] for g in ("p", "f")) or w.startswith(("po", "fo", "cph", "cfh")):
        return "PFX_TOP_PF"
    if w.startswith(("qol", "ol", "al", "dal")) and len(w) > 3:
        return "PFX_L_APPL"
    if w.startswith("q"):
        return "PFX_QO_ACT"
    if w.startswith("o"):
        return "PFX_O_NOM"
    if w.startswith(("ch", "sh")):
        return "PFX_CH_SH"
    if w.startswith("y"):
        return "PFX_Y_CONJ"
    if w.startswith(("d", "s")):
        return "PFX_D_S"
    return "PFX_BARE"


def get_suffix_class(w: str) -> str:
    if w.endswith("dy"):
        return "SFX_DY"
    if w.endswith("y"):
        return "SFX_Y_BARE"
    if w.endswith(("aiin", "oiin", "eiin", "ain", "oin", "ein", "iin", "in")):
        return "SFX_IN"
    if w.endswith(("ol", "al", "el", "il")):
        return "SFX_LIQ_L"
    if w.endswith(("or", "ar", "er", "ir")):
        return "SFX_LIQ_R"
    if w.endswith(("am", "om", "em", "im", "m")):
        return "SFX_M_CLOSE"
    return "SFX_OTHER"


def get_constituent_role(w: str, w_zone: str) -> str:
    if w.endswith(("am", "om", "em", "im", "m")) or (
        w_zone == "W_FINAL" and w in ("dy", "ry", "ly", "am", "dam", "ram", "olam")
    ):
        return "FIN_CLOSE"
    if any(g in w[:2] for g in ("p", "f")) or w.startswith(("po", "fo")):
        return "TOP_HEAD"
    if not any(g in w for g in ("k", "t", "p", "f", "ch", "sh")):
        if w.endswith(("aiin", "ain", "oiin", "in")):
            return "NP_MEAS"
        return "PP_PREP"
    if w.endswith(("aiin", "ain", "oiin", "in")):
        return "NP_MEAS"
    return "VP_PROC"


def get_10bit_features(w: str) -> tuple:
    is_open = 1 if any(g in w for g in ("k", "t", "p", "f", "ch", "sh")) else 0
    has_q = 1 if w.startswith("q") else 0
    has_l_appl = 1 if (w.startswith(("l", "ol", "qol", "dal")) and len(w) > 3) else 0
    has_sy = 1 if w.startswith(("s", "y")) else 0
    has_gal = 1 if any(g in w for g in ("k", "t", "p", "f")) else 0
    has_t = 1 if any(g in w for g in ("t", "p")) else 0
    has_cmp = 1 if any(c in w for c in ("cth", "ckh", "cph", "cfh")) else 0
    has_ee_ii = 1 if ("ee" in w or "ii" in w) else 0
    has_dy = 1 if w.endswith("dy") else 0
    has_r_a = 1 if (w.endswith(("or", "ar", "am")) or "a" in w) else 0
    return (is_open, has_q, has_l_appl, has_sy, has_gal, has_t, has_cmp, has_ee_ii, has_dy, has_r_a)


def extract_core_class(w: str) -> str:
    if not any(g in w for g in ("k", "t", "p", "f", "ch", "sh")):
        return "CORE_CLOSED_" + (w[:2] if len(w) >= 2 else w)
    for c in ("cth", "ckh", "cph", "cfh"):
        if c in w:
            return "CORE_" + c.replace("p", "t").replace("f", "k")
    for g in ("k", "t", "p", "f"):
        if g in w:
            base = "t" if g in ("t", "p") else "k"
            if "ch" in w or "sh" in w:
                return f"CORE_{base}ch"
            if "eo" in w or "od" in w:
                return f"CORE_{base}eo"
            if "ee" in w:
                return f"CORE_{base}ee"
            if "e" in w:
                return f"CORE_{base}e"
            return f"CORE_{base}o"
    if "sh" in w:
        return "CORE_sh" + ("ee" if "ee" in w else ("e" if "e" in w else "o"))
    return "CORE_ch" + ("ee" if "ee" in w else ("e" if "e" in w else "o"))


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


def main():
    paragraphs = []
    cur_meta = None
    cur_para = []

    for raw_line in ZL_PATH.read_text(encoding="utf-8", errors="replace").splitlines():
        raw_s = raw_line.strip()
        if not raw_s or raw_s.startswith("#"):
            continue
        if raw_s.startswith("<f") and ">" in raw_s and "." not in raw_s.split(">")[0]:
            if cur_para:
                paragraphs.append(cur_para)
                cur_para = []
            fname = raw_s.split(">")[0][1:]
            tags = dict(re.findall(r"\$([A-Z])=([0-9A-Za-z]+)", raw_s))
            cur_meta = {
                "folio": fname,
                "I": tags.get("I", "U"),
                "L": tags.get("L", "U"),
                "H": tags.get("H", "U"),
            }
            continue
        m = LOCUS_RE.match(raw_s)
        if m and cur_meta is not None:
            ltype = m.group(3)
            raw_text = m.group(4)
            if ltype.startswith(("L", "R", "C", "S")):
                continue
            if "<%>" in raw_text and cur_para:
                paragraphs.append(cur_para)
                cur_para = []
            toks = clean_tokens(raw_text)
            if toks:
                cur_para.append({
                    "folio": cur_meta["folio"],
                    "I": cur_meta["I"],
                    "L": cur_meta["L"],
                    "H": cur_meta["H"],
                    "words": toks,
                })
            if "<$>" in raw_text and cur_para:
                paragraphs.append(cur_para)
                cur_para = []
    if cur_para:
        paragraphs.append(cur_para)

    all_lines = []
    for p_lines in paragraphs:
        n_lines = len(p_lines)
        seen_words = Counter()
        seen_stems = Counter()
        seen_cores = Counter()
        for l_idx, line in enumerate(p_lines):
            if l_idx == 0:
                l_zone = "L_TOP"
            elif l_idx == n_lines - 1:
                l_zone = "L_BOT"
            else:
                l_zone = "L_INT"
            line["l_zone"] = l_zone
            line["prior_para_words"] = Counter(seen_words)
            line["prior_para_stems"] = Counter(seen_stems)
            line["prior_para_cores"] = Counter(seen_cores)
            all_lines.append(line)
            for w in line["words"]:
                seen_words[w] += 1
                seen_cores[extract_core_class(w)] += 1
                st = extract_open_stem(w)
                if st:
                    seen_stems[st] += 1

    train_lines = [l for i, l in enumerate(all_lines) if i % 5 != 4]
    test_lines = [l for i, l in enumerate(all_lines) if i % 5 == 4]

    vocab = set()
    unigram_counts = Counter()
    il_counts = defaultdict(Counter)
    grid_counts = defaultdict(Counter)
    role_sfx_counts = defaultdict(Counter)

    # Factored Morpheme Tables: w -> (pfx, core, sfx)
    slot_word_counts = defaultdict(Counter)
    pfx_ctx_counts = defaultdict(Counter)
    core_il_counts = defaultdict(Counter)
    sfx_ctx_counts = defaultdict(Counter)

    # Bidirectional Masked Slot Tables
    role_bictx = defaultdict(Counter)
    role_uni_ctx = defaultdict(Counter)
    pfx_bictx = defaultdict(Counter)
    pfx_uni_ctx = defaultdict(Counter)
    sfx_bictx = defaultdict(Counter)
    sfx_uni_ctx = defaultdict(Counter)
    bit_bictx = [defaultdict(Counter) for _ in range(10)]
    bit_uni_ctx = [defaultdict(Counter) for _ in range(10)]
    bit_global = [Counter() for _ in range(10)]

    stem_by_il = defaultdict(Counter)
    stem_global = Counter()

    for line in train_lines:
        il = (line["I"], line["L"])
        lz = line["l_zone"]
        words = line["words"]
        nw = len(words)
        for idx, w in enumerate(words):
            vocab.add(w)
            wz = "W_INIT" if idx == 0 else ("W_FINAL" if idx == nw - 1 else "W_INT")
            prev_w = words[idx - 1] if idx > 0 else "<BOS>"
            next_w = words[idx + 1] if idx + 1 < nw else "<EOS>"
            prev_role = get_constituent_role(prev_w, "W_INIT" if idx == 1 else "W_INT") if idx > 0 else "<BOS>"
            next_role = get_constituent_role(next_w, "W_FINAL" if idx + 2 == nw else "W_INT") if idx + 1 < nw else "<EOS>"
            prev_sfx = get_suffix_class(prev_w) if idx > 0 else "<BOS>"
            next_pfx = get_prefix_class(next_w) if idx + 1 < nw else "<EOS>"

            unigram_counts[w] += 1
            il_counts[il][w] += 1
            grid_counts[(lz, wz)][w] += 1
            role_sfx_counts[(prev_role, prev_sfx)][w] += 1

            pfx = get_prefix_class(w)
            core = extract_core_class(w)
            sfx = get_suffix_class(w)
            role = get_constituent_role(w, wz)
            bits = get_10bit_features(w)

            slot_word_counts[(pfx, core, sfx)][w] += 1
            pfx_ctx_counts[(il, lz, wz, prev_role)][pfx] += 1
            core_il_counts[(il, pfx)][core] += 1
            sfx_ctx_counts[(il, wz, core, prev_sfx)][sfx] += 1

            bictx = (il, lz, wz, prev_role, prev_sfx, next_role, next_pfx)
            unictx = (il, lz, wz, prev_role, prev_sfx)
            role_bictx[bictx][role] += 1
            role_uni_ctx[unictx][role] += 1
            pfx_bictx[bictx][pfx] += 1
            pfx_uni_ctx[unictx][pfx] += 1
            sfx_bictx[bictx][sfx] += 1
            sfx_uni_ctx[unictx][sfx] += 1

            for b_i, b_val in enumerate(bits):
                bit_bictx[b_i][bictx][b_val] += 1
                bit_uni_ctx[b_i][unictx][b_val] += 1
                bit_global[b_i][b_val] += 1

            st = extract_open_stem(w)
            if st:
                stem_by_il[il][st] += 1
                stem_global[st] += 1

    for line in test_lines:
        for w in line["words"]:
            vocab.add(w)

    V = len(vocab)
    total_train = sum(unigram_counts.values())
    il_totals = {k: sum(c.values()) for k, c in il_counts.items()}
    grid_totals = {k: sum(c.values()) for k, c in grid_counts.items()}
    rs_totals = {k: sum(c.values()) for k, c in role_sfx_counts.items()}

    # Precompute normalized distributions over V for Factored Morpheme Model M6
    slot_totals = {k: sum(c.values()) for k, c in slot_word_counts.items()}
    pfx_ctx_totals = {k: sum(c.values()) for k, c in pfx_ctx_counts.items()}
    core_il_totals = {k: sum(c.values()) for k, c in core_il_counts.items()}
    sfx_ctx_totals = {k: sum(c.values()) for k, c in sfx_ctx_counts.items()}

    # Count how many words in V fall into each (pfx, core, sfx) slot
    slot_vocab_sizes = Counter()
    for w in vocab:
        slot_vocab_sizes[(get_prefix_class(w), extract_core_class(w), get_suffix_class(w))] += 1

    ALL_PFXS = sorted({get_prefix_class(w) for w in vocab})
    ALL_CORES = sorted({extract_core_class(w) for w in vocab})
    ALL_SFXS = sorted({get_suffix_class(w) for w in vocab})

    n_test = 0
    h_m0 = h_m1 = h_m2 = h_m3 = h_m4 = h_m5 = h_m6 = 0.0

    role_top1 = role_top2 = 0
    pfx_top1 = pfx_top2 = 0
    sfx_top1 = sfx_top2 = 0
    bit_correct = [0] * 10
    bit_maj_correct = [0] * 10

    n_open_test = 0
    stem_base_top1 = stem_base_top5 = stem_base_top10 = stem_base_top25 = 0
    stem_ctx_top1 = stem_ctx_top5 = stem_ctx_top10 = stem_ctx_top25 = 0

    global_top_stems = [s for s, _ in stem_global.most_common(50)]
    total_global_stems = sum(stem_global.values())
    il_stem_totals = {il: sum(c.values()) for il, c in stem_by_il.items()}

    for line in test_lines:
        il = (line["I"], line["L"])
        lz = line["l_zone"]
        words = line["words"]
        nw = len(words)
        para_words = line["prior_para_words"]
        para_stems = line["prior_para_stems"]
        para_cores = line["prior_para_cores"]
        para_word_total = sum(para_words.values())
        para_stem_total = sum(para_stems.values())
        para_core_total = sum(para_cores.values())

        for idx, w in enumerate(words):
            n_test += 1
            wz = "W_INIT" if idx == 0 else ("W_FINAL" if idx == nw - 1 else "W_INT")
            prev_w = words[idx - 1] if idx > 0 else "<BOS>"
            next_w = words[idx + 1] if idx + 1 < nw else "<EOS>"
            prev_role = get_constituent_role(prev_w, "W_INIT" if idx == 1 else "W_INT") if idx > 0 else "<BOS>"
            next_role = get_constituent_role(next_w, "W_FINAL" if idx + 2 == nw else "W_INT") if idx + 1 < nw else "<EOS>"
            prev_sfx = get_suffix_class(prev_w) if idx > 0 else "<BOS>"
            next_pfx = get_prefix_class(next_w) if idx + 1 < nw else "<EOS>"

            # M0: Uniform over V
            p_u = 1.0 / V
            # M1: Global Unigram (Witten-Bell / Dirichlet smoothed over V)
            p_uni = (unigram_counts[w] + 0.15) / (total_train + 0.15 * V)
            p_m1 = p_uni

            # M2: + Section & Currier Dialect (I, L)
            n_il = il_totals.get(il, 0)
            p_il = (il_counts[il][w] + 0.05) / (n_il + 0.05 * V) if n_il > 0 else p_m1
            p_m2 = 0.65 * p_il + 0.35 * p_m1

            # M3: + 3x3 Spatial Paragraph Grid (L_zone, W_zone)
            n_gr = grid_totals.get((lz, wz), 0)
            p_gr = (grid_counts[(lz, wz)][w] + 0.05) / (n_gr + 0.05 * V) if n_gr > 0 else p_m2
            p_m3 = 0.78 * p_m2 + 0.22 * p_gr

            # M4: + Constituent Automaton & Moraic/Coda Harmony (prev_role, prev_sfx)
            n_rs = rs_totals.get((prev_role, prev_sfx), 0)
            p_rs = (role_sfx_counts[(prev_role, prev_sfx)][w] + 0.05) / (n_rs + 0.05 * V) if n_rs > 0 else p_m3
            p_m4 = 0.82 * p_m3 + 0.18 * p_rs

            # M5: + Intra-Paragraph Anaphoric Word Cache (adaptive Dirichlet weight)
            if para_word_total > 0:
                p_wcache = (para_words[w] + 0.05 * V * p_m4) / (para_word_total + 0.05 * V)
                p_m5 = 0.85 * p_m4 + 0.15 * p_wcache
            else:
                p_m5 = p_m4

            # M6: + Factored Dual-Matrix Morpheme Grammar:
            # P_fact(w | ctx) = P(pfx | ctx) * P(core | il, pfx, para_cores) * P(sfx | il, wz, core, prev_sfx) * P(w | pfx, core, sfx)
            pfx = get_prefix_class(w)
            core = extract_core_class(w)
            sfx = get_suffix_class(w)

            p_ctx_k = (il, lz, wz, prev_role)
            p_pfx = (pfx_ctx_counts[p_ctx_k][pfx] + 0.5) / (
                pfx_ctx_totals.get(p_ctx_k, 0) + 0.5 * len(ALL_PFXS)
            )
            c_ctx_k = (il, pfx)
            p_core_il = (core_il_counts[c_ctx_k][core] + 0.5) / (
                core_il_totals.get(c_ctx_k, 0) + 0.5 * len(ALL_CORES)
            )
            if para_core_total > 0:
                p_core = 0.85 * p_core_il + 0.15 * (para_cores[core] / para_core_total)
            else:
                p_core = p_core_il

            s_ctx_k = (il, wz, core, prev_sfx)
            p_sfx = (sfx_ctx_counts[s_ctx_k][sfx] + 0.5) / (
                sfx_ctx_totals.get(s_ctx_k, 0) + 0.5 * len(ALL_SFXS)
            )
            slot_k = (pfx, core, sfx)
            v_slot = max(slot_vocab_sizes[slot_k], 1)
            p_w_given_slot = (slot_word_counts[slot_k][w] + 0.15) / (
                slot_totals.get(slot_k, 0) + 0.15 * v_slot
            )
            p_factored = p_pfx * p_core * p_sfx * p_w_given_slot
            p_m6 = 0.88 * p_m5 + 0.12 * p_factored

            h_m0 += -math.log2(p_u)
            h_m1 += -math.log2(max(p_m1, 1e-12))
            h_m2 += -math.log2(max(p_m2, 1e-12))
            h_m3 += -math.log2(max(p_m3, 1e-12))
            h_m4 += -math.log2(max(p_m4, 1e-12))
            h_m5 += -math.log2(max(p_m5, 1e-12))
            h_m6 += -math.log2(max(p_m6, 1e-12))

            # Bidirectional Masked Slot Prediction
            bictx = (il, lz, wz, prev_role, prev_sfx, next_role, next_pfx)
            unictx = (il, lz, wz, prev_role, prev_sfx)

            rc = role_bictx[bictx] if sum(role_bictx[bictx].values()) >= 3 else role_uni_ctx[unictx]
            top_roles = [r for r, _ in rc.most_common(2)]
            if top_roles and top_roles[0] == role:
                role_top1 += 1
            if role in top_roles:
                role_top2 += 1

            pc = pfx_bictx[bictx] if sum(pfx_bictx[bictx].values()) >= 3 else pfx_uni_ctx[unictx]
            top_pfxs = [p for p, _ in pc.most_common(2)]
            if top_pfxs and top_pfxs[0] == pfx:
                pfx_top1 += 1
            if pfx in top_pfxs:
                pfx_top2 += 1

            sc = sfx_bictx[bictx] if sum(sfx_bictx[bictx].values()) >= 3 else sfx_uni_ctx[unictx]
            top_sfxs = [s for s, _ in sc.most_common(2)]
            if top_sfxs and top_sfxs[0] == sfx:
                sfx_top1 += 1
            if sfx in top_sfxs:
                sfx_top2 += 1

            true_bits = get_10bit_features(w)
            for b_i, b_val in enumerate(true_bits):
                maj = bit_global[b_i].most_common(1)[0][0]
                if maj == b_val:
                    bit_maj_correct[b_i] += 1
                bc = bit_bictx[b_i][bictx] if sum(bit_bictx[b_i][bictx].values()) >= 3 else bit_uni_ctx[b_i][unictx]
                pred_b = bc.most_common(1)[0][0] if bc else maj
                if pred_b == b_val:
                    bit_correct[b_i] += 1

            st = extract_open_stem(w)
            if st:
                n_open_test += 1
                if st == global_top_stems[0]:
                    stem_base_top1 += 1
                if st in global_top_stems[:5]:
                    stem_base_top5 += 1
                if st in global_top_stems[:10]:
                    stem_base_top10 += 1
                if st in global_top_stems[:25]:
                    stem_base_top25 += 1

                # Bayesian-weighted score combining Paragraph Topic Cache + Section/Dialect Prior + Global Prior
                cand_stems = set(global_top_stems) | set(para_stems.keys())
                for s_il, _ in stem_by_il[il].most_common(40):
                    cand_stems.add(s_il)
                scored = []
                n_il_st = max(il_stem_totals.get(il, 0), 1)
                for cs in cand_stems:
                    p_g = stem_global[cs] / total_global_stems
                    p_sec = stem_by_il[il][cs] / n_il_st
                    p_par = (para_stems[cs] / para_stem_total) if para_stem_total > 0 else 0.0
                    score = 0.55 * p_sec + 0.25 * p_g + 0.20 * p_par
                    scored.append((score, cs))
                scored.sort(reverse=True)
                ranked_ctx_stems = [cs for _, cs in scored[:25]]

                if ranked_ctx_stems and st == ranked_ctx_stems[0]:
                    stem_ctx_top1 += 1
                if st in ranked_ctx_stems[:5]:
                    stem_ctx_top5 += 1
                if st in ranked_ctx_stems[:10]:
                    stem_ctx_top10 += 1
                if st in ranked_ctx_stems[:25]:
                    stem_ctx_top25 += 1

    def ent_row(name, total_bits):
        b = total_bits / n_test
        return {
            "model": name,
            "bits_per_word": round(b, 4),
            "perplexity": round(2.0 ** b, 2),
        }

    cascade = [
        ent_row("M0_UNIFORM_VOCABULARY", h_m0),
        ent_row("M1_GLOBAL_UNIGRAM_ZIPF", h_m1),
        ent_row("M2_SECTION_AND_CURRIER_DIALECT", h_m2),
        ent_row("M3_3X3_SPATIAL_PARAGRAPH_GRID", h_m3),
        ent_row("M4_CONSTITUENT_AUTOMATON_AND_HARMONY", h_m4),
        ent_row("M5_ANAPHORIC_PARAGRAPH_TOPIC_CACHE", h_m5),
        ent_row("M6_FACTORED_DUAL_MATRIX_MORPHEME_GRAMMAR", h_m6),
    ]

    out = {
        "split_summary": {
            "train_lines": len(train_lines),
            "test_lines": len(test_lines),
            "train_tokens": total_train,
            "test_tokens": n_test,
            "vocab_size": V,
        },
        "held_out_perplexity_cascade": cascade,
        "total_perplexity_reduction_factor": round(
            cascade[0]["perplexity"] / cascade[-1]["perplexity"], 2
        ),
        "unigram_to_m6_perplexity_reduction_pct": round(
            100.0 * (cascade[1]["perplexity"] - cascade[-1]["perplexity"]) / cascade[1]["perplexity"], 2
        ),
        "masked_slot_prediction_accuracy": {
            "constituent_role_5way_top1_pct": round(100.0 * role_top1 / n_test, 2),
            "constituent_role_5way_top2_pct": round(100.0 * role_top2 / n_test, 2),
            "prefix_slot_8way_top1_pct": round(100.0 * pfx_top1 / n_test, 2),
            "prefix_slot_8way_top2_pct": round(100.0 * pfx_top2 / n_test, 2),
            "suffix_slot_7way_top1_pct": round(100.0 * sfx_top1 / n_test, 2),
            "suffix_slot_7way_top2_pct": round(100.0 * sfx_top2 / n_test, 2),
            "10bit_feature_mean_ctx_acc_pct": round(100.0 * sum(bit_correct) / (10 * n_test), 2),
            "10bit_feature_mean_maj_acc_pct": round(100.0 * sum(bit_maj_correct) / (10 * n_test), 2),
        },
        "open_class_stem_retrieval": {
            "n_open_test_tokens": n_open_test,
            "baseline_global_top1_pct": round(100.0 * stem_base_top1 / n_open_test, 2),
            "anaphoric_ctx_top1_pct": round(100.0 * stem_ctx_top1 / n_open_test, 2),
            "baseline_global_top5_pct": round(100.0 * stem_base_top5 / n_open_test, 2),
            "anaphoric_ctx_top5_pct": round(100.0 * stem_ctx_top5 / n_open_test, 2),
            "baseline_global_top10_pct": round(100.0 * stem_base_top10 / n_open_test, 2),
            "anaphoric_ctx_top10_pct": round(100.0 * stem_ctx_top10 / n_open_test, 2),
            "baseline_global_top25_pct": round(100.0 * stem_base_top25 / n_open_test, 2),
            "anaphoric_ctx_top25_pct": round(100.0 * stem_ctx_top25 / n_open_test, 2),
        },
    }
    OUT_JSON.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"Saved {OUT_JSON}")
    print("Perplexity Cascade:")
    for r in cascade:
        print(" ", r)
    print("Total Perplexity Reduction Factor:", out["total_perplexity_reduction_factor"])
    print("Unigram -> M6 Perplexity Reduction %:", out["unigram_to_m6_perplexity_reduction_pct"])
    print("Masked Slot Prediction:", out["masked_slot_prediction_accuracy"])
    print("Open Stem Retrieval:", out["open_class_stem_retrieval"])


if __name__ == "__main__":
    main()
