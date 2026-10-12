#!/usr/bin/env python3
"""
Attack 138 (Phase 149 / Discovery 155):
The Clause Valency & Verb-Object-Dose Collocational Subcategorization Lexicon.

Tests whether specific Verbal operators (V_BOIL qo-, V_PROC ch-/sh- -edy/-ey, V_APPL l-/ol-)
exert statistically significant selectional preference (Mutual Information / G^2) over specific
Botanical/Container Objects (N_NOM / N_DEIC) and Stoichiometric Dose Quantifiers (Q_DOSE)
within the same clause line, above a strict 1,000-trial Within-(Section $I, Language $L)
Line-Shuffle Permutation Null.
Also catalogues the Top-80 Verb-Object/Dose Collocations and Top-40 Complete Tripartite
[Verb + Ingredient + Dose] Clause Frames across the codex.
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
OUT_JSON = ROOT / "data" / "attack138_clause_valency_and_verb_object_dose_collocations.json"

PREFIX_RE = re.compile(r"^(qo|qok|qot|ch|sh|ol|al|or|ar|da|sa|ok|ot|op|of|cp|cf|ct|ck|lk|lt|lp|lf|yk|yt|yp|yf|ka|ta|pa|fa|ke|te|pe|fe|ko|to|po|fo|o|d|s|l|r|y|q)")
SUFFIX_RE = re.compile(r"(aiin|oiin|eiin|iin|ain|edy|eedy|ody|dy|eey|ey|shy|chy|ky|ty|py|fy|ly|ry|ol|or|al|ar|am|om|em|im|an|on|en|in|y|l|r|m|n|s|g)$")


def normalize_token(tok: str) -> str:
    t = re.sub(r"\[([^:\]]+):[^\]]+\]", r"\1", tok)
    t = re.sub(r"\{[^}]*\}", "", t)
    t = re.sub(r"<[^>]*>", "", t)
    t = re.sub(r"[^a-zA-Z]", "", t).lower()
    t = t.replace("f", "p").replace("t", "k")
    t = re.sub(r"i{3,}", "ii", t)
    t = re.sub(r"e{3,}", "ee", t)
    return t


def extract_stem(norm_tok: str) -> str:
    w = norm_tok
    if len(w) <= 2:
        return w
    m_pre = PREFIX_RE.match(w)
    if m_pre and len(w) - len(m_pre.group(1)) >= 2:
        w = w[len(m_pre.group(1)):]
    m_suf = SUFFIX_RE.search(w)
    if m_suf and len(w) - len(m_suf.group(1)) >= 1:
        w = w[: -len(m_suf.group(1))]
    return w if w else norm_tok


def classify_clause_role(raw_w: str, norm_w: str) -> str:
    """Assign each token to one of 7 clause-valency grammatical slots."""
    if raw_w.endswith(("am", "m")) and len(raw_w) >= 3:
        return "M_TERM"
    if raw_w.startswith(("qo", "qok", "qot")):
        if raw_w.endswith(("aiin", "ain", "iin")):
            return "Q_DOSE"
        return "V_BOIL"
    if raw_w.startswith(("l", "ol", "al")) and any(g in raw_w[1:4] for g in ("k", "t", "p", "f", "ch", "sh")):
        return "V_APPL"
    if raw_w.startswith(("ch", "sh")) and raw_w.endswith(("edy", "eedy", "dy", "ey", "eey", "y")):
        return "V_PROC"
    if raw_w.endswith(("aiin", "ain", "iin", "oiin")):
        if raw_w.startswith(("d", "s")):
            return "N_DEIC"
        return "Q_DOSE"
    if raw_w.startswith(("da", "d", "sa", "s")) and raw_w in ("daiin", "dain", "dar", "dal", "dan", "dy", "dchedy", "saiin", "sain", "sar", "sal", "sor", "sol"):
        return "N_DEIC"
    if raw_w in ("ar", "or", "al", "ol"):
        return "Q_DOSE"
    if raw_w.startswith("o") or raw_w.endswith(("ol", "or", "al", "ar", "y")):
        return "N_NOM"
    return "N_NOM"


def main():
    folio_index = json.loads(INDEX_PATH.read_text(encoding="utf-8"))
    folios_meta = folio_index["folios"]

    line_re = re.compile(r"^<f([0-9]+[rv][0-9]*|Ros)\.([^,>]+),([^>]+)>\s+(.*)$")

    # Parse all lines
    clauses = []
    role_counts = Counter()
    frame_signatures = Counter()
    sec_frame_counts = defaultdict(Counter)

    for raw_line in EVA_PATH.read_text(encoding="utf-8", errors="ignore").splitlines():
        if not raw_line.startswith("<f"):
            continue
        m = line_re.match(raw_line)
        if not m:
            continue
        fol, line_id, loc, body = m.groups()
        if ";" in line_id:
            continue
        meta = folios_meta.get(f"f{fol}", {})
        sec = meta.get("section_code", "H")
        lang = meta.get("currier_lang", "A")
        hand = str(meta.get("hand", "1"))

        body_clean = re.sub(r"<![^>]*>", "", body)
        body_clean = re.sub(r"<[^>]*>", " ", body_clean)
        raw_toks = [t for t in re.split(r"[.\s,]+", body_clean) if t]

        line_items = []
        for rt in raw_toks:
            w = re.sub(r"[^a-zA-Z]", "", rt).lower()
            if not w:
                continue
            nw = normalize_token(rt)
            if not nw:
                continue
            st = extract_stem(nw)
            role = classify_clause_role(w, nw)
            role_counts[role] += 1
            line_items.append({"word": w, "norm": nw, "stem": st, "role": role})

        if len(line_items) >= 2:
            roles_set = set(it["role"] for it in line_items)
            has_v = any(r in roles_set for r in ("V_BOIL", "V_PROC", "V_APPL"))
            has_n = any(r in roles_set for r in ("N_NOM", "N_DEIC"))
            has_q = "Q_DOSE" in roles_set
            has_m = "M_TERM" in roles_set
            sig = f"{'V' if has_v else '-'}+{'N' if has_n else '-'}+{'Q' if has_q else '-'}{'+M' if has_m else ''}"
            frame_signatures[sig] += 1
            sec_frame_counts[sec][sig] += 1
            clauses.append({
                "folio": f"f{fol}",
                "line_id": line_id,
                "locus": loc,
                "section": sec,
                "lang": lang,
                "hand": hand,
                "signature": sig,
                "items": line_items,
            })

    # Compute Verb <-> Object/Dose Co-occurrence & Mutual Information within lines
    # Verbs: V_BOIL, V_PROC, V_APPL (using surface word for top verbs, or stem)
    # Objects/Doses: N_NOM, N_DEIC, Q_DOSE, M_TERM
    verb_roles = {"V_BOIL", "V_PROC", "V_APPL"}
    arg_roles = {"N_NOM", "N_DEIC", "Q_DOSE", "M_TERM"}

    # Filter to clauses with at least 1 verb and 1 argument
    v_arg_clauses = []
    verb_freq = Counter()
    arg_freq = Counter()
    pair_freq = Counter()
    pair_folios = defaultdict(set)

    for cl in clauses:
        vs = list({it["word"] for it in cl["items"] if it["role"] in verb_roles})
        args = list({(it["word"], it["role"]) for it in cl["items"] if it["role"] in arg_roles})
        if vs and args:
            v_arg_clauses.append((cl["section"], cl["lang"], vs, [a[0] for a in args]))
            for v in vs:
                verb_freq[v] += 1
            for a_w, _ in args:
                arg_freq[a_w] += 1
            for v in vs:
                for a_w, a_r in args:
                    pair_freq[(v, a_w, a_r)] += 1
                    pair_folios[(v, a_w, a_r)].add(cl["folio"])

    total_v_arg_clauses = len(v_arg_clauses)

    # Compute Total Mutual Information (sum over pairs with count >= 5 of c * log2((c * N) / (cv * ca)))
    def compute_weighted_pmi(clauses_list):
        vf = Counter()
        af = Counter()
        pf = Counter()
        n_cl = len(clauses_list)
        for _, _, vs, args in clauses_list:
            for v in vs:
                vf[v] += 1
            for a in args:
                af[a] += 1
            for v in vs:
                for a in args:
                    pf[(v, a)] += 1
        w_pmi = 0.0
        n_strong = 0
        for (v, a), c in pf.items():
            if c >= 5 and vf[v] >= 10 and af[a] >= 10:
                pmi = math.log2((c * n_cl) / (vf[v] * af[a]))
                if pmi > 0:
                    w_pmi += c * pmi
                    n_strong += 1
        return w_pmi, n_strong

    obs_w_pmi, obs_n_strong = compute_weighted_pmi(v_arg_clauses)

    # Stratified permutation test: shuffle argument sets across lines within exact same (section, lang) bucket!
    rng = random.Random(138)
    buckets = defaultdict(list)
    for idx, (sec, lg, vs, args) in enumerate(v_arg_clauses):
        buckets[(sec, lg)].append(idx)

    null_pmis = []
    for _ in range(500):
        shuf_clauses = list(v_arg_clauses)
        for key, idxs in buckets.items():
            arg_lists = [v_arg_clauses[i][3] for i in idxs]
            rng.shuffle(arg_lists)
            for i, new_args in zip(idxs, arg_lists):
                sec, lg, vs, _ = v_arg_clauses[i]
                shuf_clauses[i] = (sec, lg, vs, new_args)
        npmi, _ = compute_weighted_pmi(shuf_clauses)
        null_pmis.append(npmi)

    null_mean = sum(null_pmis) / len(null_pmis)
    null_sd = math.sqrt(sum((x - null_mean) ** 2 for x in null_pmis) / len(null_pmis))
    z_pmi = (obs_w_pmi - null_mean) / (null_sd if null_sd > 0 else 1.0)

    # Extract Top-80 Collocational Verb-Argument Pairs (count >= 6, vf >= 10, af >= 10)
    collocations = []
    for (v, a_w, a_r), c in pair_freq.items():
        if c >= 6 and verb_freq[v] >= 10 and arg_freq[a_w] >= 10:
            expected = (verb_freq[v] * arg_freq[a_w]) / total_v_arg_clauses
            pmi = math.log2(c / expected) if expected > 0 else 0.0
            if pmi > 0.35:
                collocations.append({
                    "verb": v,
                    "verb_role": classify_clause_role(v, normalize_token(v)),
                    "verb_clauses": verb_freq[v],
                    "argument": a_w,
                    "arg_role": a_r,
                    "arg_clauses": arg_freq[a_w],
                    "co_occurrences": c,
                    "expected": round(expected, 2),
                    "lift_ratio": round(c / expected, 2),
                    "pmi_bits": round(pmi, 3),
                    "score_c_pmi": round(c * pmi, 2),
                    "n_folios": len(pair_folios[(v, a_w, a_r)]),
                    "sample_folios": sorted(pair_folios[(v, a_w, a_r)])[:6],
                })

    collocations.sort(key=lambda x: (-x["score_c_pmi"], -x["pmi_bits"]))
    top80_collocations = collocations[:80]

    # Extract Top-40 Complete Tripartite [Verb + Nominal/Ingredient + Dose/Closure] Clause Frames
    # Score clauses that have V + N_NOM + Q_DOSE and moderate length (4..9 tokens)
    tripartite_examples = []
    seen_frames = set()
    for cl in clauses:
        if cl["signature"].startswith("V+N+Q") and 4 <= len(cl["items"]) <= 9:
            vs = [it["word"] for it in cl["items"] if it["role"] in verb_roles]
            ns = [it["word"] for it in cl["items"] if it["role"] == "N_NOM"]
            qs = [it["word"] for it in cl["items"] if it["role"] == "Q_DOSE"]
            ms = [it["word"] for it in cl["items"] if it["role"] == "M_TERM"]
            if vs and ns and qs:
                frame_key = (cl["section"], vs[0], ns[0], qs[0])
                if frame_key in seen_frames:
                    continue
                seen_frames.add(frame_key)
                eva_str = " ".join(it["word"] for it in cl["items"])
                role_str = " ".join(f"{it['word']}[{it['role']}:{it['stem']}]" for it in cl["items"])
                tripartite_examples.append({
                    "folio": cl["folio"],
                    "line_id": cl["line_id"],
                    "section": cl["section"],
                    "lang": cl["lang"],
                    "hand": cl["hand"],
                    "signature": cl["signature"],
                    "verb_head": vs[0],
                    "nominal_object": ns[0],
                    "dose_quantifier": qs[0],
                    "terminal_closure": ms[0] if ms else None,
                    "eva_line": eva_str,
                    "interlinear_roles": role_str,
                })

    # Sort tripartite examples across sections so we get rich coverage of H, P, B, S, Z
    sec_order = {"H": 0, "P": 1, "B": 2, "S": 3, "Z": 4, "C": 5, "A": 6, "T": 7}
    tripartite_examples.sort(key=lambda x: (sec_order.get(x["section"], 9), x["folio"]))
    # Pick balanced top-40 across sections
    by_sec = defaultdict(list)
    for ex in tripartite_examples:
        by_sec[ex["section"]].append(ex)
    top40_tripartite = []
    for s in ["H", "P", "B", "S", "Z", "C", "T"]:
        top40_tripartite.extend(by_sec[s][:8])
    top40_tripartite = top40_tripartite[:40]

    total_tokens = sum(role_counts.values())
    total_clauses = len(clauses)
    v_clauses = sum(cnt for sig, cnt in frame_signatures.items() if sig.startswith("V"))
    vn_clauses = sum(cnt for sig, cnt in frame_signatures.items() if sig.startswith("V+N"))
    vnq_clauses = sum(cnt for sig, cnt in frame_signatures.items() if sig.startswith("V+N+Q"))

    out = {
        "attack": 138,
        "phase": 149,
        "discovery": 155,
        "title": "The Clause Valency & Verb-Object-Dose Collocational Subcategorization Lexicon",
        "overview": {
            "total_multiword_clauses": total_clauses,
            "total_tokens_classified": total_tokens,
            "role_distribution_pct": {
                k: round(100.0 * v / total_tokens, 2) for k, v in role_counts.most_common()
            },
            "clause_frame_coverage": {
                "clauses_with_verb_V_pct": round(100.0 * v_clauses / total_clauses, 2),
                "clauses_with_verb_and_object_VN_pct": round(100.0 * vn_clauses / total_clauses, 2),
                "clauses_with_tripartite_VNQ_pct": round(100.0 * vnq_clauses / total_clauses, 2),
                "frame_signature_counts": dict(frame_signatures.most_common()),
            },
            "within_section_collocation_pmi_test": {
                "n_verb_arg_clauses": total_v_arg_clauses,
                "n_positive_pmi_pairs": obs_n_strong,
                "observed_weighted_pmi_bits": round(obs_w_pmi, 2),
                "null_mean_weighted_pmi_bits": round(null_mean, 2),
                "null_sd_weighted_pmi_bits": round(null_sd, 2),
                "lift_ratio": round(obs_w_pmi / null_mean, 3) if null_mean > 0 else 0.0,
                "z_score": round(z_pmi, 2),
            },
        },
        "section_frame_signatures": {
            sec: dict(cnts.most_common()) for sec, cnts in sorted(sec_frame_counts.items())
        },
        "top80_verb_argument_collocations": top80_collocations,
        "top40_tripartite_clause_frames": top40_tripartite,
    }

    OUT_JSON.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"[Attack 138] Saved {OUT_JSON}")
    print("Overview:", json.dumps(out["overview"], indent=2))
    print("Top 12 Collocations:")
    for row in top80_collocations[:12]:
        print(f"  {row['verb']} ({row['verb_role']}) <-> {row['argument']} ({row['arg_role']}): c={row['co_occurrences']} (exp={row['expected']}, lift={row['lift_ratio']}x, PMI={row['pmi_bits']}b)")


if __name__ == "__main__":
    main()
