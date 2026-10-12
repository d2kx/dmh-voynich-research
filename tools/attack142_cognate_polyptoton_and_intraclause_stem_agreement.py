#!/usr/bin/env python3
"""
Attack 142 (Phase 153 / Discovery 159):
The Cognate Polyptoton (Figura Etymologica) & Intra-Clause Stem-Agreement Law
Across All 4,424 Multi-Word Clauses.

Tests:
  1. Intra-Clause Cognate Polyptoton Enrichment:
     Do open-class canonical stems recur within the same clause line in DISTINCT surface
     inflections (w_i != w_j, stem(w_i) == stem(w_j), e.g., qokedy/okedy, qokeey/okeey,
     chedy/chol, shedy/shey) significantly more often than under a 300-trial Within-(Section $I, Language $L)
     Line-Assignment Permutation Null?
  2. Left-to-Right Topic-to-Comment / Nominal-to-Operator-and-Closure Directional Law (w_i -> w_j, i < j):
     When two distinct inflections of the same stem occur in the same clause, the Left slot (w_i)
     preferentially carries Deictic/Nominal/Liquid Topic Marking (d-/s-, o-, -ol/-or/-al/-ar), while
     the Right slot (w_j) preferentially carries Active/Applicative/Processual Operator Prefixing
     (qo-, l-/ol-, ch-/sh-) and Terminal Nasal Closure (-am/-m, 2.75x surge).
     Tested against a 1,000-trial Within-Pair Order-Flip Permutation Null.
"""

import json
import math
import random
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INDEX_PATH = ROOT / "data" / "folio_index.json"
EVA_PATH = ROOT / "data" / "ZL3b-n.txt"
OUT_JSON = ROOT / "data" / "attack142_cognate_polyptoton_and_intraclause_stem_agreement.json"

ONSET_RE = re.compile(r"^(qok|qot|qo|olk|olt|ol|alk|al|ch|sh|ok|ot|op|of|lk|lt|yk|yt|da|sa|o|d|s|l|r|y|q)")
CODA_RE = re.compile(r"(aiin|oiin|eiin|iin|ain|eedy|edy|ody|dy|eey|ey|ol|or|al|ar|am|om|an|in|y|l|r|m|n|s|g)$")

CLOSED_PARTICLES = {"aiin", "ain", "iin", "dy", "ey", "ol", "or", "al", "ar", "am", "an", "in", "y", "l", "r", "m", "n", "s", "d", "o", "k", "p", "ai"}


def normalize_token(tok: str) -> str:
    t = re.sub(r"\[([^:\]]+):[^\]]+\]", r"\1", tok)
    t = re.sub(r"\{[^}]*\}", "", t)
    t = re.sub(r"<[^>]*>", "", t)
    t = re.sub(r"[^a-zA-Z]", "", t).lower()
    t = t.replace("f", "p").replace("t", "k")
    t = re.sub(r"i{3,}", "ii", t)
    t = re.sub(r"e{3,}", "ee", t)
    return t


def extract_root_core(raw_w: str, norm_w: str) -> str:
    """
    Extract the shared lexical root core so cognate inflections (e.g., qokedy/okedy/kedy -> ked,
    qokeey/okeey/cheey -> kee, chol/chedy/cheol -> ch/cheo) map to the same canonical stem while
    keeping distinct stems separate.
    """
    w = norm_w
    # Strip outer proclitic/prefix (qo, ol, al, o, d, s, l, y) if >= 3 chars remain
    m_pre = re.match(r"^(qo|ol|al|da|sa|o|d|s|l|y)", w)
    if m_pre and len(w) - len(m_pre.group(1)) >= 3:
        w = w[len(m_pre.group(1)):]
    # Strip inflectional suffix (aiin, iin, ain, dy, y, ol, or, al, ar, am, m, s) if >= 2 chars remain
    m_suf = re.search(r"(aiin|iin|ain|dy|y|ol|or|al|ar|am|om|m|n|s)$", w)
    if m_suf and len(w) - len(m_suf.group(1)) >= 2:
        w = w[: -len(m_suf.group(1))]
    return w


def morph_features(w: str) -> dict:
    is_qo = 1 if w.startswith(("qo", "qok", "qot")) else 0
    is_l = 1 if (w.startswith(("l", "ol", "al")) and len(w) >= 4) else 0
    is_chsh = 1 if w.startswith(("ch", "sh")) else 0
    is_o = 1 if (w.startswith("o") and not w.startswith("ol")) else 0
    is_ds = 1 if w.startswith(("d", "s")) else 0
    is_edy = 1 if w.endswith(("edy", "eedy")) else 0
    is_aiin = 1 if w.endswith(("aiin", "ain", "iin")) else 0
    is_liq = 1 if w.endswith(("ol", "or", "al", "ar")) else 0
    is_am = 1 if (w.endswith(("am", "m")) and len(w) >= 3) else 0
    # Topic-to-Comment Progression Score for slot w:
    # Positive if Verbal Operator / Terminal Closure (qo, l_appl, chsh, am),
    # Negative if Deictic / Nominal / Liquid Topic (ds_deic, o_nom, liq)
    progression_score = (is_qo + is_l + is_chsh + 2 * is_am) - (is_ds + is_o + is_liq)
    return {
        "qo": is_qo,
        "l_appl": is_l,
        "chsh": is_chsh,
        "o_nom": is_o,
        "ds_deic": is_ds,
        "edy": is_edy,
        "aiin": is_aiin,
        "liq": is_liq,
        "am": is_am,
        "progression_score": progression_score,
    }


def main():
    folio_index = json.loads(INDEX_PATH.read_text(encoding="utf-8"))
    folios_meta = folio_index["folios"]

    line_re = re.compile(r"^<f([0-9]+[rv][0-9]*|Ros)\.([^,>]+),([^>]+)>\s+(.*)$")

    clauses = []
    for raw_line in EVA_PATH.read_text(encoding="utf-8", errors="ignore").splitlines():
        if not raw_line.startswith("<f"):
            continue
        m = line_re.match(raw_line)
        if not m:
            continue
        fol, line_id, loc, body = m.groups()
        if ";" in line_id:
            continue
        f_key = f"f{fol}"
        meta = folios_meta.get(f_key, {})
        sec = meta.get("section_code", "H")
        lang = meta.get("currier_lang", "A")
        hand = str(meta.get("hand", "1"))

        body_clean = re.sub(r"<![^>]*>", "", body)
        body_clean = re.sub(r"<[^>]*>", " ", body_clean)
        raw_toks = [t for t in re.split(r"[.\s,]+", body_clean) if t]

        toks = []
        for rt in raw_toks:
            w = re.sub(r"[^a-zA-Z]", "", rt).lower()
            if not w:
                continue
            nw = normalize_token(rt)
            if not nw:
                continue
            st = extract_root_core(w, nw)
            toks.append((w, nw, st))

        if len(toks) >= 2:
            clauses.append({
                "folio": f_key,
                "line_id": line_id,
                "section": sec,
                "lang": lang,
                "hand": hand,
                "toks": toks,
            })

    polyptoton_pairs = []
    exact_repeat_pairs = []
    pair_counter = Counter()
    sec_poly_counts = Counter()
    sec_clause_counts = Counter()

    for cl in clauses:
        sec = cl["section"]
        sec_clause_counts[sec] += 1
        toks = cl["toks"]
        has_poly = False
        for i in range(len(toks)):
            wi, nwi, sti = toks[i]
            if sti in CLOSED_PARTICLES or len(sti) < 2:
                continue
            for j in range(i + 1, len(toks)):
                wj, nwj, stj = toks[j]
                if sti == stj:
                    if wi != wj:
                        has_poly = True
                        polyptoton_pairs.append((cl["folio"], cl["line_id"], sec, cl["lang"], sti, wi, wj, j - i))
                        pair_counter[(sti, wi, wj)] += 1
                    else:
                        exact_repeat_pairs.append((cl["folio"], cl["line_id"], sec, sti, wi))
        if has_poly:
            sec_poly_counts[sec] += 1

    obs_n_poly = len(polyptoton_pairs)
    obs_n_exact = len(exact_repeat_pairs)

    # Test 1: Within-(Section $I, Language $L) Line-Assignment Shuffle Permutation (300 trials)
    buckets = defaultdict(list)
    for idx, cl in enumerate(clauses):
        buckets[(cl["section"], cl["lang"])].append(idx)

    def count_poly_in_bucket(cl_indices, pool_toks):
        cnt = 0
        pos = 0
        for idx in cl_indices:
            k = len(clauses[idx]["toks"])
            sub = pool_toks[pos: pos + k]
            pos += k
            for i in range(k):
                wi, sti = sub[i]
                if sti in CLOSED_PARTICLES or len(sti) < 2:
                    continue
                for j in range(i + 1, k):
                    wj, stj = sub[j]
                    if sti == stj and wi != wj:
                        cnt += 1
        return cnt

    rng = random.Random(142)
    bucket_pools = {}
    for key, idxs in buckets.items():
        pool = []
        for idx in idxs:
            for w, nw, st in clauses[idx]["toks"]:
                pool.append((w, st))
        bucket_pools[key] = (idxs, pool)

    null_poly_counts = []
    for _ in range(300):
        tot_null = 0
        for key, (idxs, pool) in bucket_pools.items():
            shuf_pool = list(pool)
            rng.shuffle(shuf_pool)
            tot_null += count_poly_in_bucket(idxs, shuf_pool)
        null_poly_counts.append(tot_null)

    mu_poly = sum(null_poly_counts) / len(null_poly_counts)
    sd_poly = math.sqrt(sum((x - mu_poly) ** 2 for x in null_poly_counts) / len(null_poly_counts))
    z_poly = (obs_n_poly - mu_poly) / (sd_poly if sd_poly > 0 else 1.0)

    # Test 2: Left-to-Right Topic-to-Comment Progression across all polyptoton_pairs (w_i -> w_j, i < j)
    left_feats = Counter()
    right_feats = Counter()
    pair_prog_deltas = []

    for _, _, _, _, st, wi, wj, dist in polyptoton_pairs:
        fi = morph_features(wi)
        fj = morph_features(wj)
        for k, v in fi.items():
            left_feats[k] += v
        for k, v in fj.items():
            right_feats[k] += v
        pair_prog_deltas.append(fj["progression_score"] - fi["progression_score"])

    n_pairs = len(polyptoton_pairs)
    obs_mean_prog_delta = sum(pair_prog_deltas) / n_pairs if n_pairs > 0 else 0.0

    null_deltas = []
    for _ in range(1000):
        s = sum(d if rng.random() < 0.5 else -d for d in pair_prog_deltas)
        null_deltas.append(s / n_pairs)
    mu_d = sum(null_deltas) / len(null_deltas)
    sd_d = math.sqrt(sum((x - mu_d) ** 2 for x in null_deltas) / len(null_deltas))
    z_dir = (obs_mean_prog_delta - mu_d) / (sd_d if sd_d > 0 else 1.0)

    top50_ordered = []
    for (st, wi, wj), c in pair_counter.most_common(50):
        rev_c = pair_counter[(st, wj, wi)]
        asym_pct = round(100.0 * c / (c + rev_c), 1) if (c + rev_c) > 0 else 50.0
        top50_ordered.append({
            "root_core": st,
            "left_word_wi": wi,
            "right_word_wj": wj,
            "ordered_count": c,
            "reverse_count": rev_c,
            "forward_asymmetry_pct": asym_pct,
        })

    out = {
        "attack": 142,
        "phase": 153,
        "discovery": 159,
        "title": "The Cognate Polyptoton (Figura Etymologica) & Intra-Clause Stem-Agreement Law",
        "overview": {
            "total_multiword_clauses": len(clauses),
            "clauses_with_cognate_polyptoton": sum(sec_poly_counts.values()),
            "clauses_with_cognate_polyptoton_pct": round(100.0 * sum(sec_poly_counts.values()) / len(clauses), 2),
            "observed_cognate_polyptoton_pairs": obs_n_poly,
            "observed_exact_reduplication_pairs": obs_n_exact,
            "polyptoton_to_exact_repeat_ratio": round(obs_n_poly / obs_n_exact, 2) if obs_n_exact > 0 else 0.0,
            "within_section_line_shuffle_permutation_test": {
                "observed_pairs": obs_n_poly,
                "null_mean_pairs": round(mu_poly, 2),
                "null_sd_pairs": round(sd_poly, 2),
                "lift_ratio": round(obs_n_poly / mu_poly, 3) if mu_poly > 0 else 0.0,
                "z_score": round(z_poly, 2),
            },
            "left_to_right_topic_to_comment_progression_test": {
                "n_pairs": n_pairs,
                "left_wi_profile_pct": {
                    k: round(100.0 * left_feats[k] / n_pairs, 2)
                    for k in ["ds_deic", "o_nom", "liq", "qo", "l_appl", "chsh", "edy", "aiin", "am"]
                },
                "right_wj_profile_pct": {
                    k: round(100.0 * right_feats[k] / n_pairs, 2)
                    for k in ["ds_deic", "o_nom", "liq", "qo", "l_appl", "chsh", "edy", "aiin", "am"]
                },
                "observed_progression_delta": round(obs_mean_prog_delta, 4),
                "null_mean_delta": round(mu_d, 4),
                "null_sd_delta": round(sd_d, 4),
                "z_score": round(z_dir, 2),
            },
        },
        "section_polyptoton_rates": {
            sec: {
                "clauses": sec_clause_counts[sec],
                "polyptoton_clauses": sec_poly_counts[sec],
                "rate_pct": round(100.0 * sec_poly_counts[sec] / sec_clause_counts[sec], 2),
            }
            for sec in sorted(sec_clause_counts)
        },
        "top50_ordered_cognate_polyptoton_pairs": top50_ordered,
    }

    OUT_JSON.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"[Attack 142] Saved {OUT_JSON}")
    print("Overview:", json.dumps(out["overview"], indent=2))
    print("Top 14 Ordered Cognate Polyptoton Pairs:")
    for r in top50_ordered[:14]:
        print(f"  *{r['root_core']}*: {r['left_word_wi']} -> {r['right_word_wj']} (c={r['ordered_count']} vs rev={r['reverse_count']}, {r['forward_asymmetry_pct']}%)")


if __name__ == "__main__":
    main()
