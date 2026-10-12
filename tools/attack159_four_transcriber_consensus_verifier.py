#!/usr/bin/env python3
"""
tools/attack159_four_transcriber_consensus_verifier.py

Attack 159 (Phase 170 / Discovery 176):
Four-Transcriber Paleographic Consensus Audit (`ZL3b-n`, `RF1b-er`, `IT2a-n`, `GC2a-n`).

Tests whether our core grammatical rules (`Prefix + Root Stem + Suffix`) and
flagship visual/bilingual cribs (`oror`, `doaro`, `darary`, `okar`, `olkol`,
`okoldy`, `qokeedy`, `shedy`, `poldchody`, `fachys`, `daiin`, `chol`, `otar`,
`otam`) are invariant across all 4 independent human transcription traditions:
  1. `ZL3b-n.txt`: Zandbergen-Landini (EVA v3b)
  2. `RF1b-er.txt`: First Study Group / Friedman Reference (EVA)
  3. `IT2a-n.txt`: Takeshi Takahashi complete transcription (EVA)
  4. `GC2a-n.txt`: Glen Claston `v101` transcription (mapped to canonical EVA)
"""

import json
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
OUT_JSON = DATA_DIR / "attack159_four_transcriber_consensus_verifier.json"

CORE_CRIBS_AND_STEMS = [
    "fachys", "poldchody", "oror", "doaro", "darary", "olkol", "okoldy",
    "qokeedy", "qokedy", "shedy", "chedy", "daiin", "chol", "shol",
    "otar", "okar", "okal", "otol", "okol", "otam", "okam", "daram",
    "opchor", "pchor", "otaly", "okaly"
]


def v101_to_eva(tok: str) -> str:
    """Maps Glen Claston v101 characters to standard EVA equivalents."""
    t = re.sub(r"@\d+;", "", tok)
    t = re.sub(r"\{[^}]*\}", "", t)
    # Ordered multi-char / single-char replacements
    mapping = [
        ("1", "ch"), ("2", "sh"), ("3", "sh"), ("5", "sh"),
        ("4", "q"), ("8", "d"), ("7", "d"), ("9", "y"),
        ("C", "ee"), ("c", "e"), ("h", "k"), ("k", "t"),
        ("g", "p"), ("K", "cth"), ("H", "ckh"), ("J", "cph"),
        ("G", "cph"), ("F", "cfh"), ("e", "l"), ("y", "r"),
        ("M", "iiin"), ("m", "iin"), ("N", "iin"), ("n", "in"),
        ("A", "a"), ("I", "ii"), ("Z", "iiir"),
    ]
    out = []
    for idx, ch in enumerate(t):
        if ch == "g" and idx == len(t) - 1:
            out.append("m")
            continue
        rep = ch
        for k, v in mapping:
            if ch == k:
                rep = v
                break
        out.append(rep)
    res = "".join(out)
    return re.sub(r"[^a-zA-Z]", "", res).lower()


def clean_eva(tok: str) -> str:
    t = re.sub(r"\{[^}]*\}", "", tok)
    t = re.sub(r"\[([^\]:]+):[^\]]+\]", r"\1", t)
    t = re.sub(r"[^a-zA-Z]", "", t)
    return t.lower()


def parse_ivtff(path: Path, is_v101: bool = False):
    locus_map = {}
    word_counts = Counter()
    locus_re = re.compile(r"^<(f[0-9A-Za-z]+\.[^,;>]+),([^>]+)>\s*(.*)$")

    for raw in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        m = locus_re.match(line)
        if not m:
            continue
        loc_key, loc_type, text = m.groups()
        text = re.sub(r"<[^>]+>", " ", text)
        raw_toks = re.split(r"[.\s,]+", text)
        if is_v101:
            words = [v101_to_eva(w) for w in raw_toks]
        else:
            words = [clean_eva(w) for w in raw_toks]
        words = [w for w in words if len(w) >= 2]
        if words:
            locus_map[loc_key] = words
            word_counts.update(words)
    return locus_map, word_counts


def canonical_skeleton(w: str) -> str:
    """Reduces a word to its canonical prefix+stem+suffix skeleton for cross-transcriber comparison."""
    s = w.lower()
    s = re.sub(r"ee+", "e", s)
    s = re.sub(r"ii+", "i", s)
    s = s.replace("cth", "ch").replace("ckh", "ch").replace("cph", "cp")
    return s


def main():
    zl_loc, zl_counts = parse_ivtff(DATA_DIR / "ZL3b-n.txt", is_v101=False)
    rf_loc, rf_counts = parse_ivtff(DATA_DIR / "RF1b-er.txt", is_v101=False)
    it_loc, it_counts = parse_ivtff(DATA_DIR / "IT2a-n.txt", is_v101=False)
    gc_loc, gc_counts = parse_ivtff(DATA_DIR / "GC2a-n.txt", is_v101=True)

    shared_loci = sorted(set(zl_loc) & set(rf_loc) & set(it_loc) & set(gc_loc))

    exact_3eva_token_matches = 0
    canon_4way_token_matches = 0
    total_aligned_tokens = 0
    line_length_exact_3eva = 0

    for loc in shared_loci:
        w_zl = zl_loc[loc]
        w_rf = rf_loc[loc]
        w_it = it_loc[loc]
        w_gc = gc_loc[loc]

        if len(w_zl) == len(w_rf) == len(w_it):
            line_length_exact_3eva += 1

        min_len = min(len(w_zl), len(w_rf), len(w_it), len(w_gc))
        for i in range(min_len):
            total_aligned_tokens += 1
            a, b, c, d = w_zl[i], w_rf[i], w_it[i], w_gc[i]
            if a == b == c:
                exact_3eva_token_matches += 1
            sk_set = {canonical_skeleton(a), canonical_skeleton(b), canonical_skeleton(c), canonical_skeleton(d)}
            if len(sk_set) <= 2:
                canon_4way_token_matches += 1

    # Check each of the 26 Core Cribs & Stems across all 4 transliterations
    crib_verification = []
    for crib in CORE_CRIBS_AND_STEMS:
        c_zl = zl_counts[crib]
        c_rf = rf_counts[crib]
        c_it = it_counts[crib]
        c_gc = gc_counts[crib]
        att_count = sum(1 for c in (c_zl, c_rf, c_it, c_gc) if c > 0)
        crib_verification.append({
            "word": crib,
            "ZL3b_hits": c_zl,
            "RF1b_hits": c_rf,
            "IT2a_hits": c_it,
            "GC2a_v101_mapped_hits": c_gc,
            "transcribers_attesting": att_count,
        })

    attested_in_all_3_eva = sum(1 for r in crib_verification if r["ZL3b_hits"] > 0 and r["RF1b_hits"] > 0 and r["IT2a_hits"] > 0)
    attested_in_all_4 = sum(1 for r in crib_verification if r["transcribers_attesting"] == 4)

    payload = {
        "attack": 159,
        "phase": 170,
        "discovery": 176,
        "title": "Four-Transcriber Paleographic Consensus Audit (ZL3b-n, RF1b-er, IT2a-n, GC2a-n)",
        "summary": {
            "shared_aligned_loci": len(shared_loci),
            "total_aligned_tokens": total_aligned_tokens,
            "line_word_count_exact_3eva_rate": round(line_length_exact_3eva / max(1, len(shared_loci)), 4),
            "exact_3eva_word_identity_rate": round(exact_3eva_token_matches / max(1, total_aligned_tokens), 4),
            "canonical_4way_consensus_rate": round(canon_4way_token_matches / max(1, total_aligned_tokens), 4),
            "core_cribs_tested": len(CORE_CRIBS_AND_STEMS),
            "core_cribs_attested_in_all_3_eva": attested_in_all_3_eva,
            "core_cribs_attested_in_all_4_editions": attested_in_all_4,
        },
        "crib_verification_table": crib_verification,
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(
        f"[Attack 159] Shared Loci = {len(shared_loci)} ({total_aligned_tokens} aligned tokens); "
        f"3-EVA Exact Word Identity = {payload['summary']['exact_3eva_word_identity_rate']*100:.1f}%, "
        f"4-Transcriber Canonical Consensus = {payload['summary']['canonical_4way_consensus_rate']*100:.1f}%; "
        f"Core Cribs Attested across All 3 EVA Editions = {attested_in_all_3_eva}/{len(CORE_CRIBS_AND_STEMS)}, "
        f"All 4 Editions (incl. v101) = {attested_in_all_4}/{len(CORE_CRIBS_AND_STEMS)}"
    )


if __name__ == "__main__":
    main()
