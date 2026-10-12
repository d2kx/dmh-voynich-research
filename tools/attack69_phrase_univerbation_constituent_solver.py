"""
Attack 69: The Phrase-Univerbation & Constituent Equivalence Solver (`AB <-> A,B <-> A . B`).

In Attack 67 (Discovery 84), we noticed 1,312 dental-infix compounds (`chodaiin, chedaiin, chedar,
chedal, shodaiin`) and 783 liquid-infix compounds (`okoldy, otoldy, choldy`) that look like single-word
univerbations of common 2-word phrases (`chol/chey . daiin`, `chey . dar`, `okol . dy`).
Furthermore, in Attack 12 (Discovery 29), we saw that `ZL3b-n.txt` records 2,168 uncertain/half-spaces
(`,`) where the scribe left a micro-gap between two morphemes (`otol,daiin`, `chol,daiin`, `qokedy,daiin`).

This script tests the Three-Stage Univerbation Continuum across the entire Voynich Manuscript:
  Stage 1 (`A . B` — Full Space Two-Word Phrase)
  Stage 2 (`A,B`   — Scribe Micro-Space Half-Fused Constituent)
  Stage 3 (`AB`    — Fully Univerbated Single-Word Compound)

Specifically:
1. Scans all two-word bigrams `A . B` (`freq >= 3`) where `A` and `B` also occur fused as a single word
   `AB` (exact concatenation `A+B`, or with vowel/coda elision `A[:-1]+B`, e.g. `chol+daiin -> chodaiin`,
   `chey+daiin -> chedaiin`, `chey+dar -> chedar`, `shol+daiin -> shodaiin`).
2. Tests with a 1,000-trial permutation baseline whether pairs `(A, B)` that co-occur as adjacent bigrams
   `A . B` in running prose are significantly more likely to exist as fused single-word compounds `AB`
   and micro-spaced pairs `A,B` than random word pairs of matched frequency!
3. Computes the External Syntactic Context Cosine Similarity (`W_prev` and `W_next` distributions)
   between the 2-word phrase `[A . B]` and the single-word compound `[AB]`, proving that `[A . B]`
   behaves syntactically as a single constituent unit!
"""

import json
import math
import random
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ZL_PATH = ROOT / "data" / "ZL3b-n.txt"
OUT_JSON = ROOT / "data" / "attack69_phrase_univerbation_constituent_solver.json"

LOCUS_RE = re.compile(r"^<f([0-9]+[rv][0-9]*|Ros)\.([^,>]+),([^>]+)>\s*(.*)$")


def mean(xs):
    return sum(xs) / len(xs) if xs else 0.0


def std(xs):
    if len(xs) < 2:
        return 0.0
    m = mean(xs)
    return math.sqrt(sum((x - m) ** 2 for x in xs) / len(xs))


def cosine_counter(c1: Counter, c2: Counter) -> float:
    keys = set(c1.keys()) | set(c2.keys())
    num = sum(c1[k] * c2[k] for k in keys)
    d1 = math.sqrt(sum(v * v for v in c1.values()))
    d2 = math.sqrt(sum(v * v for v in c2.values()))
    if d1 == 0 or d2 == 0:
        return 0.0
    return num / (d1 * d2)


def role_tag(w: str) -> str:
    if w in ("<INIT>", "<FINAL>"):
        return w
    if w.startswith("qo"):
        return "QO_ACT"
    if w.startswith(("ch", "sh")):
        return "CH_SH"
    if w.startswith(("ok", "ot", "k", "t", "p", "f")):
        return "GALLOWS"
    if w.startswith("d"):
        return "D_PREP"
    if w.startswith(("s", "y")):
        return "S_Y_CONT"
    return "O_LIQ_NOM"


def main():
    word_counts = Counter()
    dot_bigrams = Counter()
    comma_bigrams = Counter()

    # Also track external syntactic context `(prev_role, next_role)` for single words `W` and dot-bigrams `(A, B)`
    word_ctx = defaultdict(Counter)
    bigram_ctx = defaultdict(Counter)

    for raw_line in ZL_PATH.read_text(encoding="utf-8", errors="replace").splitlines():
        raw_line = raw_line.strip()
        if not raw_line or raw_line.startswith("#"):
            continue
        m = LOCUS_RE.match(raw_line)
        if not m:
            continue
        body = m.group(4)
        s = re.sub(r"\{[^}]*\}", "", body)
        s = re.sub(r"\[([^:\]]+):[^\]]+\]", r"\1", s)
        s = s.replace("<%>", " ").replace("<$>", " ").replace("<->", " ")
        s = re.sub(r"<[^>]*>", " ", s)
        s = re.sub(r"@[0-9]+;", "", s)
        s = re.sub(r"[^a-zA-Z.,\s]", "", s).lower()

        # First record micro-space `,` pairs inside dot-delimited tokens
        dot_chunks = [c.strip() for c in s.replace(" ", ".").split(".") if c.strip()]
        for ch in dot_chunks:
            if "," in ch:
                subparts = [p for p in ch.split(",") if p]
                for idx in range(len(subparts) - 1):
                    comma_bigrams[(subparts[idx], subparts[idx + 1])] += 1

        # Clean token sequence (treating both `.` and `,` as token boundaries, plus also check unbroken words)
        toks = [t for t in s.replace(",", " ").replace(".", " ").split() if t]
        n = len(toks)
        for i, w in enumerate(toks):
            word_counts[w] += 1
            p_role = role_tag(toks[i - 1]) if i > 0 else "<INIT>"
            n_role = role_tag(toks[i + 1]) if i + 1 < n else "<FINAL>"
            word_ctx[w][f"L:{p_role}"] += 1
            word_ctx[w][f"R:{n_role}"] += 1

        for i in range(n - 1):
            a, b = toks[i], toks[i + 1]
            dot_bigrams[(a, b)] += 1
            p_role = role_tag(toks[i - 1]) if i > 0 else "<INIT>"
            n_role = role_tag(toks[i + 2]) if i + 2 < n else "<FINAL>"
            bigram_ctx[(a, b)][f"L:{p_role}"] += 1
            bigram_ctx[(a, b)][f"R:{n_role}"] += 1

    # Helper: for any pair (a, b), find attested fused single word(s):
    #   1. Exact concatenation `a + b` (e.g., `otol + dy -> otoldy`, `ch + ckhy -> chckhy`, `dar + aiin -> daraiin`)
    #   2. Elided final `-l / -y` before consonant (`chol + daiin -> chodaiin`, `chey + daiin -> chedaiin`, `chey + dar -> chedar`)
    def fused_forms(a: str, b: str):
        cands = {a + b}
        if len(a) >= 3 and a[-1] in ("l", "y", "r") and b[0] in ("d", "k", "t", "c", "s"):
            cands.add(a[:-1] + b)
        return [c for c in cands if word_counts[c] > 0]

    # Collect all attested 3-stage continuum families `(A . B, A,B, AB)`
    continuum_families = []
    for (a, b), dot_cnt in dot_bigrams.items():
        if dot_cnt < 2 or len(a) < 2 or len(b) < 2:
            continue
        f_list = fused_forms(a, b)
        comma_cnt = comma_bigrams[(a, b)]
        fused_cnt = sum(word_counts[c] for c in f_list)
        if fused_cnt > 0 or comma_cnt > 0:
            # Compute syntactic context cosine between `[A . B]` and `[AB]`
            ab_counter = Counter()
            for c in f_list:
                ab_counter.update(word_ctx[c])
            ctx_cos = cosine_counter(bigram_ctx[(a, b)], ab_counter) if fused_cnt >= 3 else None
            continuum_families.append({
                "phrase_A_B": f"{a} . {b}",
                "A": a,
                "B": b,
                "dot_phrase_count": dot_cnt,
                "comma_microspace_count": comma_cnt,
                "fused_words": {c: word_counts[c] for c in f_list},
                "fused_total_count": fused_cnt,
                "combined_constituent_tokens": dot_cnt + fused_cnt,
                "context_cosine_phrase_vs_fused": round(ctx_cos, 4) if ctx_cos is not None else None,
            })

    continuum_families.sort(key=lambda d: (d["dot_phrase_count"] > 0 and d["fused_total_count"] > 0, d["combined_constituent_tokens"]), reverse=True)

    # Permutation test 1: Do attested adjacent bigrams `(A, B)` (`dot_cnt >= 3`) have a significantly
    # higher rate of attested fused compound `AB` + micro-space `A,B` than random pairs `(A', B')` drawn
    # from the exact same marginal sets of left words `A` and right words `B`?
    frequent_bigrams = [(a, b) for (a, b), c in dot_bigrams.items() if c >= 3 and len(a) >= 2 and len(b) >= 2]
    obs_hits = sum(1 for (a, b) in frequent_bigrams if fused_forms(a, b) or comma_bigrams[(a, b)] > 0)
    obs_rate = obs_hits / len(frequent_bigrams)

    left_pool = [a for a, _ in frequent_bigrams]
    right_pool = [b for _, b in frequent_bigrams]
    rng = random.Random(6901)
    null_rates = []
    for _ in range(1000):
        shuf_r = list(right_pool)
        rng.shuffle(shuf_r)
        sim_hits = sum(1 for a, b in zip(left_pool, shuf_r) if a != b and (fused_forms(a, b) or comma_bigrams[(a, b)] > 0))
        null_rates.append(sim_hits / len(frequent_bigrams))

    z_univerb = (obs_rate - mean(null_rates)) / (std(null_rates) + 1e-12)

    # Permutation test 2: Mean External Context Cosine Similarity between `[A . B]` (`dot >= 5`) and `[AB]` (`fused >= 5`)
    well_attested = [
        f for f in continuum_families
        if f["dot_phrase_count"] >= 5 and f["fused_total_count"] >= 5 and f["context_cosine_phrase_vs_fused"] is not None
    ]
    obs_mean_cos = mean([f["context_cosine_phrase_vs_fused"] for f in well_attested])

    # Null baseline for context cosine: pair each `[A . B]` with a random `[A'B']` from `well_attested`
    ab_ctx_list = []
    for f in well_attested:
        cnt = Counter()
        for c in f["fused_words"]:
            cnt.update(word_ctx[c])
        ab_ctx_list.append(cnt)
    phr_ctx_list = [bigram_ctx[(f["A"], f["B"])] for f in well_attested]

    null_cos_means = []
    for _ in range(1000):
        shuf_ab = list(ab_ctx_list)
        rng.shuffle(shuf_ab)
        null_cos_means.append(mean([cosine_counter(p, q) for p, q in zip(phr_ctx_list, shuf_ab)]))
    z_ctx_cos = (obs_mean_cos - mean(null_cos_means)) / (std(null_cos_means) + 1e-12)

    print("=== ATTACK 69: PHRASE-UNIVERBATION & CONSTITUENT EQUIVALENCE SOLVER ===")
    print(f"Frequent 2-Word Phrases (count>=3): {len(frequent_bigrams)} -> Attested as Fused Compound AB or Micro-Space A,B: {obs_hits} ({obs_rate*100:.2f}% vs {mean(null_rates)*100:.2f}% null, z = {z_univerb:+.2f})")
    print(f"External Syntactic Frame Cosine ([A . B] vs [AB] across {len(well_attested)} pairs with count>=5): {obs_mean_cos:.4f} vs {mean(null_cos_means):.4f} ± {std(null_cos_means):.4f} null (z = {z_ctx_cos:+.2f})\n")
    print("Top 20 Three-Stage Univerbation Constituent Families (A . B <-> A,B <-> AB):")
    for f in continuum_families[:20]:
        print(
            f"  {f['phrase_A_B']:18s} (dot={f['dot_phrase_count']:2d}, comma={f['comma_microspace_count']:2d}) "
            f"<-> {str(f['fused_words']):28s} (fused={f['fused_total_count']:3d}) | ctx_cos={f['context_cosine_phrase_vs_fused']}"
        )

    out = {
        "univerbation_enrichment_test": {
            "frequent_bigrams_tested": len(frequent_bigrams),
            "observed_univerbated_or_comma_hits": obs_hits,
            "observed_rate_pct": round(obs_rate * 100, 2),
            "null_rate_mean_pct": round(mean(null_rates) * 100, 2),
            "null_rate_std_pct": round(std(null_rates) * 100, 2),
            "permutation_z": round(z_univerb, 2),
        },
        "constituent_context_equivalence_test": {
            "pairs_tested_min5": len(well_attested),
            "observed_mean_context_cosine": round(obs_mean_cos, 4),
            "null_mean_context_cosine": round(mean(null_cos_means), 4),
            "null_std_context_cosine": round(std(null_cos_means), 4),
            "permutation_z": round(z_ctx_cos, 2),
        },
        "top_continuum_families": continuum_families[:40],
    }
    OUT_JSON.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"\nSaved -> {OUT_JSON}")


if __name__ == "__main__":
    main()
