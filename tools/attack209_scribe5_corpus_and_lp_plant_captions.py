#!/usr/bin/env python3
"""
Attack 209 (Discovery 226): Scribe 5 ($H=5) Complete Corpus Forensics (f41v Labeled
Crossed-Root Umbel & All Scribe 5 Folios) and @Lp Plant Caption / Ultra-Minimal
Herbal Folios (f65r 3-Word Alliterative -m Triad & Global @Lp Census).
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
OUT_PATH = ROOT / "data" / "attack209_scribe5_corpus_and_lp_plant_captions.json"


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
    folios = defaultdict(lambda: {"body": [], "labels": [], "lp": [], "intrusions": 0, "lines": []})
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
        if "Lp" in loc:
            folios[folio]["lp"].extend(toks)
            folios[folio]["labels"].extend(toks)
        elif "@L" in loc or "+L" in loc:
            folios[folio]["labels"].extend(toks)
        else:
            folios[folio]["body"].extend(toks)
    return folios


def main():
    random.seed(209)
    idx = json.loads(INDEX_PATH.read_text(encoding="utf-8"))["folios"]
    zl = parse_zl()

    # 1. Scribe 5 ($H=5) Complete Corpus Census & Comparison across Scribes 1..5
    scribe_folios = defaultdict(list)
    for f, meta in idx.items():
        h = str(meta.get("hand", "?"))
        scribe_folios[h].append(f)

    scribe_stats = {}
    for h in sorted(scribe_folios.keys()):
        flist = sorted(scribe_folios[h])
        all_words = []
        intrusions = 0
        labels_count = 0
        for f in flist:
            w = zl[f]["body"] + zl[f]["labels"]
            all_words.extend(w)
            intrusions += zl[f]["intrusions"]
            labels_count += len(zl[f]["labels"])
        total = len(all_words)
        if total == 0:
            continue
        edy_eey = sum(1 for w in all_words if w.endswith(("edy", "eey")))
        q_init = sum(1 for w in all_words if w.startswith("q"))
        aiin_end = sum(1 for w in all_words if w.endswith(("aiin", "ain", "oiin")))
        m_end = sum(1 for w in all_words if w.endswith("m"))
        scribe_stats[h] = {
            "folio_count": len(flist),
            "folios": flist,
            "total_words": total,
            "mean_words_per_folio": round(total / len(flist), 2),
            "edy_eey_pct": round(100.0 * edy_eey / total, 2),
            "q_initial_pct": round(100.0 * q_init / total, 2),
            "aiin_pct": round(100.0 * aiin_end / total, 2),
            "m_terminal_pct": round(100.0 * m_end / total, 2),
            "total_intrusions": intrusions,
            "total_label_words": labels_count,
        }

    # Detailed breakdown of all Scribe 5 folios
    h5_details = []
    for f in sorted(scribe_folios.get("5", [])):
        meta = idx[f]
        words = zl[f]["body"] + zl[f]["labels"]
        total = len(words)
        edy = sum(1 for w in words if w.endswith(("edy", "eey")))
        q_cnt = sum(1 for w in words if w.startswith("q"))
        stems = [canonical_stem(w) for w in zl[f]["body"] if canonical_stem(w)]
        h5_details.append({
            "folio": f,
            "section": meta.get("section_code"),
            "language": meta.get("currier_lang"),
            "quire": meta.get("quire"),
            "word_count": total,
            "body_words": len(zl[f]["body"]),
            "label_words": len(zl[f]["labels"]),
            "lp_words": zl[f]["lp"],
            "intrusions": zl[f]["intrusions"],
            "edy_eey_pct": round(100.0 * edy / max(1, total), 2),
            "q_initial_pct": round(100.0 * q_cnt / max(1, total), 2),
            "top_stems": Counter(stems).most_common(6),
        })

    # Specific forensic analysis of f41v ($H=5)
    f41v_lines = zl["f41v"]["lines"]
    f41v_lp = zl["f41v"]["lp"]
    f41v_lp_stem = canonical_stem(f41v_lp[0]) if f41v_lp else ""
    f41v_body_stems = [canonical_stem(w) for w in zl["f41v"]["body"] if canonical_stem(w)]
    f41v_left_right = []
    for ln in f41v_lines:
        if "<->" in ln["raw"]:
            parts = ln["raw"].split("<->")
            left_toks = [clean_word(t) for t in re.split(r"[.,\s<>\-$%]+", parts[0]) if clean_word(t)]
            right_toks = [clean_word(t) for t in re.split(r"[.,\s<>\-$%]+", parts[1]) if clean_word(t)]
            f41v_left_right.append({
                "lnum": ln["lnum"],
                "left_tokens": left_toks,
                "right_tokens": right_toks,
                "pre_gap_token": left_toks[-1] if left_toks else "",
                "post_gap_token": right_toks[0] if right_toks else "",
            })

    # 2. Complete Census of @Lp (Plant Label / Header) Loci across the Manuscript
    lp_folios = []
    for f, data in sorted(zl.items()):
        if data["lp"]:
            body_stems = set(canonical_stem(w) for w in data["body"] if canonical_stem(w))
            lp_stems = [canonical_stem(w) for w in data["lp"] if canonical_stem(w)]
            echo_in_own_body = sum(1 for s in lp_stems if s in body_stems)
            lp_folios.append({
                "folio": f,
                "section": idx.get(f, {}).get("section_code", "?"),
                "language": idx.get(f, {}).get("currier_lang", "?"),
                "hand": idx.get(f, {}).get("hand", "?"),
                "lp_tokens": data["lp"],
                "lp_stems": lp_stems,
                "body_word_count": len(data["body"]),
                "echo_in_own_body": echo_in_own_body,
            })

    # 3. Ultra-Minimal Herbal Folios & f65r ("otaim.dam.alam") Alliterative -m Triad Proof
    herbal_folios = [f for f, m in idx.items() if m.get("section_code") == "H"]
    herbal_by_length = sorted(
        [
            {
                "folio": f,
                "language": idx[f].get("currier_lang"),
                "hand": idx[f].get("hand"),
                "total_words": len(zl[f]["body"]) + len(zl[f]["labels"]),
                "body_words": len(zl[f]["body"]),
                "label_words": len(zl[f]["labels"]),
                "first_line": zl[f]["lines"][0]["tokens"] if zl[f]["lines"] else [],
            }
            for f in herbal_folios
        ],
        key=lambda x: x["total_words"],
    )[:10]

    # Permutation test on f65r's 3-word caption ("otaim", "dam", "alam"):
    # All 3 tokens end in -m (-aim / -am / -am)!
    all_herbal_tokens = []
    for f in herbal_folios:
        all_herbal_tokens.extend(zl[f]["body"] + zl[f]["labels"])
    m_rate_herbal = sum(1 for w in all_herbal_tokens if w.endswith("m")) / len(all_herbal_tokens)
    exact_prob_3_of_3_m = m_rate_herbal ** 3

    trials = 10000
    hits_3m = 0
    for _ in range(trials):
        sample = random.sample(all_herbal_tokens, 3)
        if all(w.endswith("m") for w in sample):
            hits_3m += 1

    # Check where "otaim", "dam", "alam" and their stems occur across the manuscript
    f65r_tokens = ["otaim", "dam", "alam"]
    f65r_token_occurrences = {}
    for tok in f65r_tokens:
        st = canonical_stem(tok)
        exact_folios = []
        stem_folios = []
        for f in idx:
            wlist = zl[f]["body"] + zl[f]["labels"]
            if tok in wlist:
                exact_folios.append(f)
            if any(canonical_stem(w) == st for w in wlist):
                stem_folios.append(f)
        f65r_token_occurrences[tok] = {
            "canonical_stem": st,
            "exact_folio_count": len(exact_folios),
            "exact_folios": exact_folios[:15],
            "stem_folio_count": len(stem_folios),
        }

    # Check f65r <-> f65v same-leaf relationship
    f65v_words = zl["f65v"]["body"] + zl["f65v"]["labels"]
    f65v_stems = set(canonical_stem(w) for w in f65v_words if canonical_stem(w))
    f65r_stems = [canonical_stem(w) for w in f65r_tokens]
    f65r_in_f65v = [s for s in f65r_stems if s in f65v_stems]

    out = {
        "attack": 209,
        "discovery": 226,
        "title": "Scribe 5 ($H=5) Complete Corpus Forensics (f41v Labeled Crossed-Root Umbel) and @Lp Plant Caption / f65r 3-Word Alliterative -m Triad",
        "scribe_comparison": scribe_stats,
        "scribe5_folio_breakdown": h5_details,
        "f41v_forensics": {
            "lp_header": f41v_lp,
            "lp_canonical_stem": f41v_lp_stem,
            "body_word_count": len(zl["f41v"]["body"]),
            "intrusions": zl["f41v"]["intrusions"],
            "crossed_root_split_lines": f41v_left_right,
        },
        "global_lp_plant_captions": {
            "total_lp_folios": len(lp_folios),
            "folios": lp_folios,
        },
        "shortest_herbal_folios": herbal_by_length,
        "f65r_alliterative_m_triad": {
            "tokens": f65r_tokens,
            "m_ending_count": 3,
            "m_ending_pct": 100.0,
            "herbal_baseline_m_ending_pct": round(100.0 * m_rate_herbal, 3),
            "analytical_p_value_3_of_3_m": round(exact_prob_3_of_3_m, 8),
            "monte_carlo_hits_in_10000": hits_3m,
            "token_and_stem_distribution": f65r_token_occurrences,
            "f65r_stems_echoed_on_verso_f65v": f65r_in_f65v,
            "f65v_word_count": len(f65v_words),
        },
    }

    OUT_PATH.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"Wrote {OUT_PATH}")
    print("Scribe 5 summary:", scribe_stats.get("5"))
    print("Global @Lp folios:", [(x["folio"], x["lp_tokens"], x["body_word_count"]) for x in lp_folios])
    print("f65r -m triad test: herbal -m rate =", round(100 * m_rate_herbal, 3), "%, exact p =", exact_prob_3_of_3_m)
    print("f65r stems echoed on f65v:", f65r_in_f65v)


if __name__ == "__main__":
    main()
