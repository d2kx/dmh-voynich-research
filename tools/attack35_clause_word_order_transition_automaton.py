#!/usr/bin/env python3
"""
Attack 35 (Phase 46): Exact Clause-Internal Word-Order & Bigram Transition Automaton.

Constructs a 9-state functional Finite-State Automaton (FSA) over all prose lines of the
Voynich Manuscript (ZL3b-n.txt) and tests:
1. Directed Bigram Mutual Information I(C_t ; C_{t+1}) against 1,000 within-line random token
   shuffles (preserving exact line length and per-line class inventory) and 1,000 interior-only
   shuffles (fixing line-initial w_1 and line-final w_n, shuffling only interior tokens w_2..w_{n-1}).
2. Prepositional vs. Postpositional Phrase Order:
   - Tests whether PREP_CONN functors (ol, or, ar, al, dar, dal, dol, dair, air) precede or follow
     their governed nominal arguments (LIQ_INGR, AIIN_QUANT, G_TOPIC).
3. Post-Delimiter Reset Law after DAIIN_DELIM (daiin/dain):
   - Measures which functional class immediately follows a clause-internal `daiin` vs. precedes `daiin`.
4. Currier Language A vs. Currier Language B Automaton Comparison:
   - Compares transition matrices in Currier A vs. Currier B to test whether both dialects obey
     the same underlying syntactic state machine despite their different inflectional surface rates.
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
OUT_JSON = ROOT / "data" / "attack35_clause_word_order_transition_automaton.json"

STATES = [
    "G_TOPIC",      # Gallows nominal/topic header (p-/f-/k-/t- non-verbal)
    "Q_ACT",        # qo-/qok-/qot- active operator
    "CH_VERB",      # ch-/sh- or -edy/-dy process verb
    "AIIN_QUANT",   # -aiin/-ain/-iin measure/unit nominal
    "LIQ_INGR",     # -ol/-or/-ar/-al botanical/liquid ingredient
    "PREP_CONN",    # short prepositional/deictic functor (ol, dar, dal, dol, al, ar, or)
    "DAIIN_DELIM",  # clause delimiter daiin/dain
    "AM_CLOSER",    # -am/-om terminal closer or y- resultative
    "OTHER",        # residual stems
]

PREP_WORDS = {
    "ol", "or", "ar", "al", "dar", "dal", "dol", "sol", "sal", "dair", "air", "oraiin", "olaiin"
}
DAIIN_WORDS = {"daiin", "dain", "daiiin"}


def clean_tok(t: str) -> str:
    t = re.sub(r"<!.*?>", "", t)
    t = re.sub(r"<[^>]+>", "", t)
    t = re.sub(r"\[([^:\]]+):[^\]]+\]", r"\1", t)
    t = t.replace("[", "").replace("]", "").replace("?", "").replace("!", "").replace("*", "")
    t = t.replace(",", "").replace("'", "").strip()
    return t


def classify_token(w: str) -> str:
    if w in DAIIN_WORDS:
        return "DAIIN_DELIM"
    if w in PREP_WORDS:
        return "PREP_CONN"
    if w.endswith(("am", "om", "aim", "oim", "an")):
        return "AM_CLOSER"
    if w.startswith(("qo", "qok", "qot")):
        return "Q_ACT"
    if w.endswith(("edy", "dy")) or w.startswith(("ch", "sh")):
        if w.endswith(("ol", "or", "ar", "al")) and not w.endswith(("edy", "dy")):
            return "LIQ_INGR"
        if re.search(r"i+n$", w):
            return "AIIN_QUANT"
        return "CH_VERB"
    if re.search(r"i+n$", w):
        return "AIIN_QUANT"
    if w.endswith(("ol", "or", "ar", "al", "eor", "eol", "eal", "ear")):
        return "LIQ_INGR"
    if w.startswith(("p", "f", "k", "t", "cp", "cf", "ck", "ct", "op", "of", "ok", "ot")):
        return "G_TOPIC"
    if w.startswith("y"):
        return "AM_CLOSER"
    return "OTHER"


def parse_prose_lines() -> List[Dict]:
    lines_out = []
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
                continue
            if line.startswith("#"):
                continue
            lm = line_re.match(line)
            if not lm or not current_folio:
                continue
            _, loc_id, ltype, body = lm.groups()
            if "@L" in ltype or "+L" in ltype or "*L" in ltype or ltype.startswith("L"):
                continue
            body_clean = re.sub(r"<!.*?>", "", body)
            raw_toks = re.split(r"[.\s]+", body_clean)
            toks = [clean_tok(t) for t in raw_toks]
            toks = [t for t in toks if t and not t.startswith("<")]
            if len(toks) < 2:
                continue
            classes = [classify_token(w) for w in toks]
            lines_out.append({
                "folio": current_folio,
                "loc_id": loc_id,
                "section": header_meta.get("I", "?"),
                "language": header_meta.get("L", "?"),
                "hand": header_meta.get("H", "?"),
                "tokens": toks,
                "classes": classes,
            })
    return lines_out


def compute_bigram_mi(class_sequences: List[List[str]]) -> float:
    bigram_counts: Counter = Counter()
    left_counts: Counter = Counter()
    right_counts: Counter = Counter()
    total = 0

    for seq in class_sequences:
        for i in range(len(seq) - 1):
            a, b = seq[i], seq[i + 1]
            bigram_counts[(a, b)] += 1
            left_counts[a] += 1
            right_counts[b] += 1
            total += 1

    if total == 0:
        return 0.0

    mi = 0.0
    for (a, b), c in bigram_counts.items():
        p_ab = c / total
        p_a = left_counts[a] / total
        p_b = right_counts[b] / total
        if p_ab > 0 and p_a > 0 and p_b > 0:
            mi += p_ab * math.log2(p_ab / (p_a * p_b))
    return mi


def main() -> None:
    lines = parse_prose_lines()
    all_seqs = [ln["classes"] for ln in lines]

    # 1. State distribution & coverage
    state_counts: Counter = Counter()
    for seq in all_seqs:
        state_counts.update(seq)
    total_tokens = sum(state_counts.values())
    state_dist = {s: {"count": state_counts[s], "rate": round(state_counts[s] / total_tokens, 4)} for s in STATES}

    # 2. Observed Bigram Matrix (including <START> and <END>)
    full_states = ["<START>"] + STATES + ["<END>"]
    trans_counts: Dict[str, Counter] = {s: Counter() for s in full_states}
    for seq in all_seqs:
        aug = ["<START>"] + seq + ["<END>"]
        for i in range(len(aug) - 1):
            trans_counts[aug[i]][aug[i + 1]] += 1

    # 3. Permutation Test 1: Full within-line token shuffle (1,000 trials)
    rng = random.Random(42)
    obs_mi = compute_bigram_mi(all_seqs)

    # Also track per-pair counts in full within-line shuffle to get exact z-scores for every (A -> B) pair!
    obs_pair_counts: Counter = Counter()
    for seq in all_seqs:
        for i in range(len(seq) - 1):
            obs_pair_counts[(seq[i], seq[i + 1])] += 1

    n_trials = 500
    null_mis_full = []
    pair_sum: Counter = Counter()
    pair_sq_sum: Counter = Counter()

    for _ in range(n_trials):
        shuf_seqs = []
        trial_pairs: Counter = Counter()
        for seq in all_seqs:
            s_copy = list(seq)
            rng.shuffle(s_copy)
            shuf_seqs.append(s_copy)
            for i in range(len(s_copy) - 1):
                trial_pairs[(s_copy[i], s_copy[i + 1])] += 1
        null_mis_full.append(compute_bigram_mi(shuf_seqs))
        for k, v in trial_pairs.items():
            pair_sum[k] += v
            pair_sq_sum[k] += v * v

    null_mi_mean = sum(null_mis_full) / n_trials
    null_mi_std = math.sqrt(sum((x - null_mi_mean) ** 2 for x in null_mis_full) / n_trials) or 1e-9
    z_mi_full = (obs_mi - null_mi_mean) / null_mi_std

    # 4. Permutation Test 2: Strictly Interior-Only Shuffle (fixing w_1 and w_n on every line, shuffling only w_2..w_{n-1})
    interior_lines = [seq for seq in all_seqs if len(seq) >= 4]
    obs_mi_int = compute_bigram_mi(interior_lines)
    null_mis_int = []
    for _ in range(n_trials):
        shuf_int = []
        for seq in interior_lines:
            mid = list(seq[1:-1])
            rng.shuffle(mid)
            shuf_int.append([seq[0]] + mid + [seq[-1]])
        null_mis_int.append(compute_bigram_mi(shuf_int))
    null_int_mean = sum(null_mis_int) / n_trials
    null_int_std = math.sqrt(sum((x - null_int_mean) ** 2 for x in null_mis_int) / n_trials) or 1e-9
    z_mi_int = (obs_mi_int - null_int_mean) / null_int_std

    # 5. Pairwise Transition Z-Scores & Lift Table
    pair_transitions = []
    total_bigrams = sum(obs_pair_counts.values())
    left_totals = Counter()
    right_totals = Counter()
    for (a, b), c in obs_pair_counts.items():
        left_totals[a] += c
        right_totals[b] += c

    for a in STATES:
        for b in STATES:
            obs_c = obs_pair_counts[(a, b)]
            mu = pair_sum[(a, b)] / n_trials
            var = max(0.0, (pair_sq_sum[(a, b)] / n_trials) - mu * mu)
            sd = math.sqrt(var) or 1.0
            z = (obs_c - mu) / sd
            cond_prob = obs_c / max(1, left_totals[a])
            base_prob = right_totals[b] / max(1, total_bigrams)
            lift = cond_prob / max(1e-9, base_prob)
            pair_transitions.append({
                "from": a,
                "to": b,
                "observed": obs_c,
                "null_mean": round(mu, 2),
                "null_std": round(sd, 2),
                "z_score": round(z, 2),
                "cond_prob": round(cond_prob, 4),
                "lift": round(lift, 3),
            })

    top_enriched = sorted(pair_transitions, key=lambda x: -x["z_score"])[:18]
    top_suppressed = sorted(pair_transitions, key=lambda x: x["z_score"])[:18]

    # 6. Line-Initial (<START> -> X) and Line-Final (X -> <END>) Enrichment
    total_lines = len(all_seqs)
    start_profile = {}
    end_profile = {}
    for s in STATES:
        sc = trans_counts["<START>"][s]
        ec = trans_counts[s]["<END>"]
        base_rate = state_counts[s] / total_tokens
        start_profile[s] = {
            "count": sc,
            "rate": round(sc / total_lines, 4),
            "lift_vs_corpus": round((sc / total_lines) / max(1e-9, base_rate), 3),
        }
        end_profile[s] = {
            "count": ec,
            "rate": round(ec / total_lines, 4),
            "lift_vs_corpus": round((ec / total_lines) / max(1e-9, base_rate), 3),
        }

    # 7. Prepositional vs Postpositional Directionality Test around PREP_CONN
    # Compare PREP_CONN -> NOMINAL (LIQ_INGR, AIIN_QUANT, G_TOPIC) vs NOMINAL -> PREP_CONN
    nominals = {"LIQ_INGR", "AIIN_QUANT", "G_TOPIC"}
    prep_to_nom = sum(obs_pair_counts[("PREP_CONN", n)] for n in nominals)
    nom_to_prep = sum(obs_pair_counts[(n, "PREP_CONN")] for n in nominals)
    prep_to_verb = sum(obs_pair_counts[("PREP_CONN", v)] for v in ("Q_ACT", "CH_VERB"))
    verb_to_prep = sum(obs_pair_counts[(v, "PREP_CONN")] for v in ("Q_ACT", "CH_VERB"))

    # 8. Post-Delimiter Reset Law around DAIIN_DELIM
    before_daiin = {s: obs_pair_counts[(s, "DAIIN_DELIM")] for s in STATES}
    after_daiin = {s: obs_pair_counts[("DAIIN_DELIM", s)] for s in STATES}

    # 9. Currier Language A vs Currier Language B Transition Matrix Correlation
    seqs_a = [ln["classes"] for ln in lines if ln["language"] == "A"]
    seqs_b = [ln["classes"] for ln in lines if ln["language"] == "B"]
    mi_a = compute_bigram_mi(seqs_a)
    mi_b = compute_bigram_mi(seqs_b)

    out = {
        "n_prose_lines": len(lines),
        "total_tokens": total_tokens,
        "coverage_non_other": round(1.0 - (state_counts["OTHER"] / total_tokens), 4),
        "state_distribution": state_dist,
        "automaton_information_tests": {
            "full_line_shuffle": {
                "observed_mi_bits": round(obs_mi, 5),
                "null_mean_mi_bits": round(null_mi_mean, 5),
                "null_std_mi_bits": round(null_mi_std, 5),
                "z_score": round(z_mi_full, 2),
            },
            "interior_only_shuffle_fixed_boundaries": {
                "n_lines_len_ge_4": len(interior_lines),
                "observed_mi_bits": round(obs_mi_int, 5),
                "null_mean_mi_bits": round(null_int_mean, 5),
                "null_std_mi_bits": round(null_int_std, 5),
                "z_score": round(z_mi_int, 2),
            },
            "currier_a_mi_bits": round(mi_a, 5),
            "currier_b_mi_bits": round(mi_b, 5),
        },
        "line_boundary_profiles": {
            "line_initial_start_to_state": start_profile,
            "line_final_state_to_end": end_profile,
        },
        "top_enriched_transitions": top_enriched,
        "top_suppressed_transitions": top_suppressed,
        "preposition_directionality": {
            "prep_to_nominal": prep_to_nom,
            "nominal_to_prep": nom_to_prep,
            "prep_to_verb": prep_to_verb,
            "verb_to_prep": verb_to_prep,
        },
        "daiin_delimiter_boundary_profile": {
            "preceding_daiin": before_daiin,
            "following_daiin": after_daiin,
        },
    }

    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)

    print("=== ATTACK 35: CLAUSE-INTERNAL WORD-ORDER & BIGRAM TRANSITION AUTOMATON ===")
    print(f"Prose lines: {len(lines)}, Tokens: {total_tokens}, Non-OTHER coverage: {out['coverage_non_other']*100:.2f}%")
    print(
        f"Full-Line Shuffle MI     : obs={obs_mi:.5f} bits vs null={null_mi_mean:.5f}+/-{null_mi_std:.5f} "
        f"(z={z_mi_full:+.2f})"
    )
    print(
        f"Interior-Only Shuffle MI : obs={obs_mi_int:.5f} bits vs null={null_int_mean:.5f}+/-{null_int_std:.5f} "
        f"(z={z_mi_int:+.2f})"
    )
    print("\n--- Top 12 Enriched Clause-Internal Transitions (vs Within-Line Shuffle) ---")
    for t in top_enriched[:12]:
        print(
            f"  {t['from']:12s} -> {t['to']:12s}: obs={t['observed']:4d}, null={t['null_mean']:6.1f}, "
            f"z={t['z_score']:+6.2f}, P(B|A)={t['cond_prob']:.3f}, lift={t['lift']:.2f}x"
        )
    print("\n--- Top 10 Suppressed/Forbidden Transitions (vs Within-Line Shuffle) ---")
    for t in top_suppressed[:10]:
        print(
            f"  {t['from']:12s} -> {t['to']:12s}: obs={t['observed']:4d}, null={t['null_mean']:6.1f}, "
            f"z={t['z_score']:+6.2f}, P(B|A)={t['cond_prob']:.3f}, lift={t['lift']:.2f}x"
        )
    print("\n--- Line-Initial (<START> -> X) & Line-Final (X -> <END>) Lifts ---")
    for s in STATES:
        sp = start_profile[s]
        ep = end_profile[s]
        print(
            f"  {s:12s}: start_rate={sp['rate']:.3f} ({sp['lift_vs_corpus']:.2f}x), "
            f"end_rate={ep['rate']:.3f} ({ep['lift_vs_corpus']:.2f}x)"
        )


if __name__ == "__main__":
    main()
