#!/usr/bin/env python3
"""
Attack 210 (Discovery 227): Balneological Boundary & Single-Label Architecture:
f76r <-> f76v (Pure-Text Master Treatise Recto to Illustrated Canopy/Bladder Verso),
f81v (Two-Tier 14-Nymph Pool with Single 2-Word Callout 'otain.olkal'), and
f84v (Quire 13 Closing Folio '13m' with @P1 Showerhead Header & @Pb 10-Line Right-Margin Callout Column).
"""

import json
import math
import random
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ZL_PATH = ROOT / "data" / "ZL3b-n.txt"
INDEX_PATH = ROOT / "data" / "folio_index.json"
OUT_PATH = ROOT / "data" / "attack210_balneo_f76v_f81v_f84v_closure_and_pb_callouts.json"


def canonical_stem(word: str) -> str:
    w = re.sub(r"\[([^:\]]+):[^\]]+\]", r"\1", word)
    w = re.sub(r"\{[^}]+\}", "", w)
    w = re.sub(r"[^a-z]", "", w.lower())
    if not w:
        return ""
    if w.startswith("qo") and len(w) > 3:
        w = w[2:]
    elif w.startswith("q") and len(w) > 2:
        w = w[1:]
    w = w.replace("ee", "e").replace("ii", "i")
    for sfx in ("aiin", "oiin", "ain", "oin", "edy", "eey", "ody", "ey", "dy", "al", "ol", "or", "ar", "am", "om", "y", "l", "r", "m", "n", "s"):
        if w.endswith(sfx) and len(w) - len(sfx) >= 2:
            w = w[: -len(sfx)]
            break
    return w


def clean_word(word: str) -> str:
    w = re.sub(r"\[([^:\]]+):[^\]]+\]", r"\1", word)
    w = re.sub(r"\{[^}]+\}", "", w)
    w = re.sub(r"[^a-z]", "", w.lower())
    return w


def parse_zl():
    text = ZL_PATH.read_text(encoding="utf-8", errors="ignore")
    folios = defaultdict(lambda: {"body": [], "labels": [], "p1": [], "pb": [], "lt": [], "lines": [], "intrusions": 0})
    for raw_line in text.splitlines():
        if not raw_line.startswith("<f"):
            continue
        m = re.match(r"^<([^.]+)\.([^,>]+),([^>]+)>\s+(.*)$", raw_line)
        if not m:
            continue
        folio, lnum, loc, body = m.groups()
        body_no_comments = re.sub(r"<!.*?>", "", body)
        intrusions = body_no_comments.count("<->")
        folios[folio]["intrusions"] += intrusions
        toks = [clean_word(t) for t in re.split(r"[.,\s<>\-$%]+", body_no_comments) if clean_word(t)]
        if not toks:
            continue
        folios[folio]["lines"].append({"lnum": lnum, "loc": loc, "tokens": toks, "intrusions": intrusions, "raw": body_no_comments.strip()})
        if "P1" in loc:
            folios[folio]["p1"].extend(toks)
        elif "Pb" in loc:
            folios[folio]["pb"].extend(toks)
        elif "Lt" in loc:
            folios[folio]["lt"].extend(toks)
            folios[folio]["labels"].extend(toks)
        elif "@L" in loc or "+L" in loc:
            folios[folio]["labels"].extend(toks)
        else:
            folios[folio]["body"].extend(toks)
    return folios


def main():
    random.seed(210)
    idx = json.loads(INDEX_PATH.read_text(encoding="utf-8"))["folios"]
    zl = parse_zl()

    balneo_folios = sorted([f for f, m in idx.items() if m.get("section_code") == "B"])

    # Part A: f76r <-> f76v Pure-Text Master Treatise Recto to Illustrated Verso Coupling
    f76r_words = zl["f76r"]["body"]
    f76v_words = zl["f76v"]["body"]
    f76r_stems = set(canonical_stem(w) for w in f76r_words if canonical_stem(w))
    f76v_stems = set(canonical_stem(w) for w in f76v_words if canonical_stem(w))
    shared_f76 = f76r_stems & f76v_stems
    jaccard_f76 = len(shared_f76) / len(f76r_stems | f76v_stems)
    f76v_covered_by_f76r = sum(1 for w in f76v_words if canonical_stem(w) in f76r_stems) / len(f76v_words)

    # Compare f76r <-> f76v token coverage against f76v covered by other Balneo folios
    other_balneo_coverages = []
    for bf in balneo_folios:
        if bf in ("f76r", "f76v"):
            continue
        bstems = set(canonical_stem(w) for w in (zl[bf]["body"] + zl[bf]["p1"] + zl[bf]["pb"]) if canonical_stem(w))
        cov = sum(1 for w in f76v_words if canonical_stem(w) in bstems) / len(f76v_words)
        other_balneo_coverages.append((bf, round(100.0 * cov, 2)))

    # Inspect f76v's 6 <-> intrusion lines (Lines 1..6 where the top-right barrel sprayer sits)
    f76v_intrusion_lines = []
    for ln in zl["f76v"]["lines"]:
        if "<->" in ln["raw"]:
            parts = ln["raw"].split("<->")
            left_t = [clean_word(t) for t in re.split(r"[.,\s<>\-$%]+", parts[0]) if clean_word(t)]
            right_t = [clean_word(t) for t in re.split(r"[.,\s<>\-$%]+", parts[1]) if clean_word(t)]
            f76v_intrusion_lines.append({
                "lnum": ln["lnum"],
                "left_count": len(left_t),
                "right_count": len(right_t),
                "pre_gap_token": left_t[-1] if left_t else "",
                "right_coda_tokens": right_t,
            })

    # Part B: f81v Two-Tier 14-Nymph Pool & Single Callout Locus (<f81v.28,@Lt> otain.olkal)
    f81v_lt = zl["f81v"]["lt"]
    f81v_body = zl["f81v"]["body"]
    f81v_body_stems = [canonical_stem(w) for w in f81v_body if canonical_stem(w)]
    f81v_body_stem_counts = Counter(f81v_body_stems)
    f81v_lt_analysis = []
    for tok in f81v_lt:
        st = canonical_stem(tok)
        exact_lines = [ln["lnum"] for ln in zl["f81v"]["lines"] if ln["loc"] != "@Lt" and tok in ln["tokens"]]
        stem_matches = [w for w in f81v_body if canonical_stem(w) == st]
        f81v_lt_analysis.append({
            "label_token": tok,
            "canonical_stem": st,
            "exact_matches_in_f81v_body": len(exact_lines),
            "exact_match_lines": exact_lines,
            "stem_matches_in_f81v_body": len(stem_matches),
            "stem_match_examples": sorted(set(stem_matches)),
        })

    # Part C: f84v Quire 13 Closing Folio ('13m'), @P1 Top-Pool Header & @Pb 10-Line Right-Margin Callout Column
    f84v_p1 = zl["f84v"]["p1"]
    f84v_pb = zl["f84v"]["pb"]
    f84v_callouts = f84v_p1 + f84v_pb
    f84v_body = zl["f84v"]["body"]
    f84v_body_set = set(f84v_body)
    f84v_body_stems = set(canonical_stem(w) for w in f84v_body if canonical_stem(w))

    all_balneo_body_stems = set()
    for bf in balneo_folios:
        for w in zl[bf]["body"]:
            s = canonical_stem(w)
            if s:
                all_balneo_body_stems.add(s)

    f84v_callout_details = []
    local_stem_hits = 0
    local_exact_hits = 0
    balneo_stem_hits = 0
    for tok in f84v_callouts:
        st = canonical_stem(tok)
        in_local_exact = tok in f84v_body_set
        in_local_stem = st in f84v_body_stems
        in_balneo_stem = st in all_balneo_body_stems
        if in_local_exact:
            local_exact_hits += 1
        if in_local_stem:
            local_stem_hits += 1
        if in_balneo_stem:
            balneo_stem_hits += 1
        matching_body_words = sorted(set(w for w in f84v_body if canonical_stem(w) == st))
        f84v_callout_details.append({
            "token": tok,
            "zone": "@P1_top_pool_header" if tok in f84v_p1 else "@Pb_right_margin_pool_callout",
            "canonical_stem": st,
            "exact_in_f84v_body": in_local_exact,
            "stem_in_f84v_body": in_local_stem,
            "stem_in_balneo_section": in_balneo_stem,
            "f84v_body_cognates": matching_body_words,
        })

    # Permutation baseline: sample 20 random non-Balneo label tokens (e.g., from Astro/Cosmo/Pharma) and test stem echo in f84v_body
    non_balneo_labels = []
    for f, m in idx.items():
        if m.get("section_code") != "B":
            non_balneo_labels.extend(zl[f]["labels"])

    trials = 1000
    null_hits = []
    for _ in range(trials):
        samp = random.sample(non_balneo_labels, len(f84v_callouts))
        hits = sum(1 for w in samp if canonical_stem(w) in f84v_body_stems)
        null_hits.append(hits)
    mean_null = sum(null_hits) / trials
    sd_null = math.sqrt(sum((x - mean_null) ** 2 for x in null_hits) / trials) or 1e-9
    z_f84v = (local_stem_hits - mean_null) / sd_null
    p_f84v = sum(1 for x in null_hits if x >= local_stem_hits) / trials

    # Updated Global Balneological Callout Law including f81v (@Lt) and f84v (@P1 + @Pb)
    balneo_label_summary = []
    total_b_callouts = 0
    total_b_local_echo = 0
    total_b_section_echo = 0
    for bf in balneo_folios:
        c_toks = zl[bf]["labels"] + zl[bf]["p1"] + zl[bf]["pb"]
        if not c_toks:
            continue
        b_stems = set(canonical_stem(w) for w in zl[bf]["body"] if canonical_stem(w))
        loc_echo = sum(1 for w in c_toks if canonical_stem(w) in b_stems)
        sec_echo = sum(1 for w in c_toks if canonical_stem(w) in all_balneo_body_stems)
        total_b_callouts += len(c_toks)
        total_b_local_echo += loc_echo
        total_b_section_echo += sec_echo
        balneo_label_summary.append({
            "folio": bf,
            "callout_count": len(c_toks),
            "local_body_echo_count": loc_echo,
            "local_body_echo_pct": round(100.0 * loc_echo / len(c_toks), 2),
            "balneo_section_echo_count": sec_echo,
            "balneo_section_echo_pct": round(100.0 * sec_echo / len(c_toks), 2),
        })

    out = {
        "attack": 210,
        "discovery": 227,
        "title": "Balneological Boundary & Single-Label Architecture: f76r<->f76v Leaf Coupling, f81v Single Callout, and f84v Quire 13 Closing @P1/@Pb Callout Column",
        "f76r_f76v_leaf_coupling": {
            "f76r_body_words": len(f76r_words),
            "f76v_body_words": len(f76v_words),
            "f76r_unique_stems": len(f76r_stems),
            "f76v_unique_stems": len(f76v_stems),
            "shared_stems_count": len(shared_f76),
            "stem_jaccard_pct": round(100.0 * jaccard_f76, 2),
            "f76v_tokens_covered_by_f76r_stems_pct": round(100.0 * f76v_covered_by_f76r, 2),
            "other_balneo_folio_coverages_of_f76v": sorted(other_balneo_coverages, key=lambda x: -x[1])[:8],
            "f76v_top_right_sprayer_intrusion_lines": f76v_intrusion_lines,
        },
        "f81v_single_locus_callout": {
            "body_word_count": len(f81v_body),
            "nymph_count_visual": 14,
            "lt_label_tokens": f81v_lt,
            "lt_token_analysis": f81v_lt_analysis,
        },
        "f84v_closing_folio_callouts": {
            "quire_signature_visual": "13m (bottom-right corner beside lower blue pool drain pipe)",
            "p1_top_pool_header_tokens": f84v_p1,
            "pb_right_margin_callout_tokens": f84v_pb,
            "total_callout_tokens": len(f84v_callouts),
            "exact_matches_in_f84v_body": local_exact_hits,
            "exact_match_pct": round(100.0 * local_exact_hits / len(f84v_callouts), 2),
            "local_stem_matches_in_f84v_body": local_stem_hits,
            "local_stem_match_pct": round(100.0 * local_stem_hits / len(f84v_callouts), 2),
            "balneo_section_stem_matches": balneo_stem_hits,
            "balneo_section_stem_match_pct": round(100.0 * balneo_stem_hits / len(f84v_callouts), 2),
            "null_mean_local_matches": round(mean_null, 2),
            "z_score_vs_non_balneo_labels": round(z_f84v, 2),
            "p_value": round(p_f84v, 4),
            "callout_details": f84v_callout_details,
        },
        "expanded_balneo_callout_census": {
            "folios_with_callouts": len(balneo_label_summary),
            "total_callout_tokens": total_b_callouts,
            "total_local_echo": total_b_local_echo,
            "total_local_echo_pct": round(100.0 * total_b_local_echo / total_b_callouts, 2),
            "total_section_echo": total_b_section_echo,
            "total_section_echo_pct": round(100.0 * total_b_section_echo / total_b_callouts, 2),
            "per_folio": balneo_label_summary,
        },
    }

    OUT_PATH.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"Wrote {OUT_PATH}")
    print("f76v tokens covered by f76r stems:", round(100.0 * f76v_covered_by_f76r, 2), "%")
    print("f81v @Lt analysis:", f81v_lt_analysis)
    print(f"f84v @P1+@Pb callouts: {local_stem_hits}/{len(f84v_callouts)} ({100*local_stem_hits/len(f84v_callouts):.2f}%) local stem echo, {balneo_stem_hits}/{len(f84v_callouts)} ({100*balneo_stem_hits/len(f84v_callouts):.2f}%) Balneo echo (z={z_f84v:.2f}, p={p_f84v:.4f})")
    print(f"Expanded Balneo Callout Law (13 folios, {total_b_callouts} tokens): {total_b_local_echo}/{total_b_callouts} ({100*total_b_local_echo/total_b_callouts:.2f}%) local, {total_b_section_echo}/{total_b_callouts} ({100*total_b_section_echo/total_b_callouts:.2f}%) section")


if __name__ == "__main__":
    main()
