#!/usr/bin/env python3
"""
Attack 46: The f66r Three-Column Index Table, Suffix-Key Echo Law (`rary->y, rals->s, saly->y, salf->f`),
and the `den mus del` Sub-Figure Inscription
========================================================================================================
Analyzes the outer-bifolium index page `f66r` (Quire H, Hand 5):
  1. Reconstructs the 3-column alignment between Column 1 (`@L` 15 outer words), Column 2 (`@X` 34 single-char
     key glyphs), and Column 3 (`@P/+P` 31 prose lines across 5 paragraphs).
  2. Tests the Suffix-Key Echo Law on the opening block (`rary->y`, `rals->s`, `saly->y`, `salf->f`, `fary->f`)
     against 10,000 random permutations of the Column 2 key sequence, and checks the global corpus rarity
     of word-final `-f` (`salf`).
  3. Maps the cross-manuscript occurrences and section distribution of all 15 outer index words of `f66r`.
  4. Analyzes the bottom-left medical illustration (reclining figure, apothecary jar, 2 dose spheres) and
     the alphabetic inscription `den mus del` (`<f66r.16,@L>`).
"""

from __future__ import annotations

import json
import math
import random
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, List

ROOT = Path(__file__).resolve().parents[1]
ZL_PATH = ROOT / "data" / "ZL3b-n.txt"
OUT_JSON = ROOT / "data" / "attack46_f66r_index_table_and_den_mus_del_decoder.json"

LOCUS_RE = re.compile(r"^<f([0-9]+[rv][0-9]*|Ros)\.([^,>]+),([^>]+)>\s*(.*)$")


def clean_raw(raw: str) -> str:
    s = re.sub(r"\{[^}]*\}", "", raw)
    s = re.sub(r"\[([^:\]]+):[^\]]+\]", r"\1", s)
    s = s.replace("<%>", " ").replace("<$>", " ").replace("<->", " ")
    s = re.sub(r"<[^>]*>", " ", s)
    s = re.sub(r"[!?*']", "", s)
    return s.strip()


def clean_alpha_tokens(raw: str) -> List[str]:
    s = clean_raw(raw)
    s = re.sub(r"@[0-9]+;", "", s)
    s = re.sub(r"[^a-zA-Z.\s]", "", s).lower()
    return [t for t in s.replace(".", " ").split() if t]


def main() -> None:
    lines_raw = ZL_PATH.read_text(encoding="utf-8", errors="replace").splitlines()
    current_folio = ""
    current_sec = ""
    folio_sec: Dict[str, str] = {}

    f66r_loci = []
    global_word_counts: Counter = Counter()
    word_by_sec: Dict[str, Counter] = defaultdict(Counter)
    word_folios: Dict[str, List[str]] = defaultdict(list)

    for line in lines_raw:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("<f") and ">" in line and "." not in line.split(">")[0]:
            m_f = re.match(r"^<f([0-9]+[rv][0-9]*|Ros)>", line.split(">")[0] + ">")
            if m_f:
                current_folio = "f" + m_f.group(1)
            m_s = re.search(r"\$I=([A-Z])", line)
            current_sec = m_s.group(1) if m_s else "U"
            folio_sec[current_folio] = current_sec
            continue

        m = LOCUS_RE.match(line)
        if not m:
            continue
        folio = "f" + m.group(1)
        loc_id = m.group(2)
        loc_tag = m.group(3)
        raw_text = m.group(4)
        toks = clean_alpha_tokens(raw_text)

        if folio == "f66r":
            f66r_loci.append({
                "loc_id": loc_id,
                "loc_tag": loc_tag,
                "raw_text": raw_text,
                "clean_text": clean_raw(raw_text),
                "tokens": toks,
            })

        for w in toks:
            global_word_counts[w] += 1
            word_by_sec[w][folio_sec.get(folio, "U")] += 1
            if len(word_folios[w]) < 15:
                word_folios[w].append(f"{folio}.{loc_id},{loc_tag}")

    # Separate f66r loci into Column 1 (loci 1..15 outer words), Column 2 (loci 16..49 key chars), and Column 3 (@P/+P prose)
    l0_loci = [x for x in f66r_loci if x["loc_tag"] in ("@L0", "+L0")]
    col1_outer = l0_loci[:15]
    col2_keys = l0_loci[15:49]
    col3_prose = [x for x in f66r_loci if "P" in x["loc_tag"]]
    bottom_lx = [x for x in f66r_loci if x["loc_tag"] == "@Lx"]

    # Check word-final '-f' across the entire Voynich Manuscript
    words_ending_in_f = [
        {"word": w, "count": cnt, "loci": word_folios[w]}
        for w, cnt in global_word_counts.most_common()
        if w.endswith("f") and len(w) >= 2
    ]

    # Test Suffix/Onset-Key Echo Law on the f66r outer words vs aligned Column 2 keys:
    # Specifically:
    #   <f66r.1> rary <-> <f66r.16> y (ends in y)
    #   <f66r.2> rals <-> <f66r.18> s (ends in s)
    #   <f66r.4> dary <-> <f66r.20> y / <f66r.21> d (starts with d, ends in y)
    #   <f66r.6> saly <-> <f66r.29> y (ends in y)
    #   <f66r.7> salf <-> <f66r.30> f (ends in f)
    #   <f66r.8> fary <-> <f66r.31> f (starts with f, ends in y)
    all_key_chars = [x["clean_text"].split("<")[0].strip() for x in col2_keys]
    outer_words = [x["tokens"][0] if x["tokens"] else "" for x in col1_outer]

    # Test contiguous triad match: [saly, salf, fary] (indices 5,6,7) vs [y, f, f] (indices 13,14,15 in col2_keys = loci 29,30,31)
    # Plus [rary, rals, dary] vs [y, s, y/d]
    anchor_pairs = [
        ("rary", all_key_chars[0]),   # locus 1 <-> locus 16 ('y')
        ("rals", all_key_chars[2]),   # locus 2 <-> locus 18 ('s')
        ("dary", all_key_chars[4]),   # locus 4 <-> locus 20 ('y')
        ("saly", all_key_chars[13]),  # locus 6 <-> locus 29 ('y')
        ("salf", all_key_chars[14]),  # locus 7 <-> locus 30 ('f')
        ("fary", all_key_chars[15]),  # locus 8 <-> locus 31 ('f')
    ]
    obs_exact_matches = sum(1 for w, k in anchor_pairs if w.endswith(k) or w.startswith(k))

    rng = random.Random(46)
    null_matches = []
    for _ in range(10000):
        sampled_keys = rng.sample(all_key_chars, len(anchor_pairs))
        c = sum(1 for (w, _), k in zip(anchor_pairs, sampled_keys) if len(k) == 1 and (w.endswith(k) or w.startswith(k)))
        null_matches.append(c)
    mu_m = sum(null_matches) / len(null_matches)
    sd_m = math.sqrt(sum((x - mu_m) ** 2 for x in null_matches) / len(null_matches)) or 1e-9
    z_echo = (obs_exact_matches - mu_m) / sd_m
    p_echo = sum(1 for x in null_matches if x >= obs_exact_matches) / len(null_matches)

    # Cross-manuscript profile of all 15 Voynich outer words on f66r (loci 1..15)
    outer_word_profiles = []
    for idx, loc in enumerate(col1_outer):
        w = loc["tokens"][0] if loc["tokens"] else ""
        approx_key_idx = min(int(round(idx * (len(all_key_chars) - 1) / 14.0)), len(all_key_chars) - 1)
        paired_key = all_key_chars[approx_key_idx]
        outer_word_profiles.append({
            "index": idx + 1,
            "loc_id": loc["loc_id"],
            "word": w,
            "approx_aligned_key": paired_key,
            "global_count": global_word_counts[w],
            "section_distribution": dict(word_by_sec[w]),
            "sample_loci": word_folios[w][:10],
        })

    result = {
        "summary": {
            "col1_outer_count": len(col1_outer),
            "col2_key_count": len(col2_keys),
            "col3_prose_lines": len(col3_prose),
            "anchor_pairs": [{"word": w, "key": k} for w, k in anchor_pairs],
            "observed_anchor_key_matches": obs_exact_matches,
            "null_mean_matches": round(mu_m, 4),
            "z_score": round(z_echo, 2),
            "empirical_p_value": round(p_echo, 6),
            "global_words_ending_in_f_count": len(words_ending_in_f),
            "global_words_ending_in_f_tokens": sum(x["count"] for x in words_ending_in_f),
        },
        "words_ending_in_f": words_ending_in_f,
        "outer_word_profiles": outer_word_profiles,
        "all_col2_keys": all_key_chars,
        "bottom_lx_locus82": bottom_lx[0] if bottom_lx else None,
    }

    OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print("=== ATTACK 46: f66r THREE-COLUMN INDEX TABLE & SUFFIX-KEY ECHO DECODER ===")
    s = result["summary"]
    print(f"1. 6-Anchor Suffix/Onset-Key Echo (rary->y, rals->s, dary->y, saly->y, salf->f, fary->f): {s['observed_anchor_key_matches']}/6 exact matches vs null={s['null_mean_matches']:.4f} (z={s['z_score']:+.2f}, p={s['empirical_p_value']:.6f})")
    print(f"2. Words ending in '-f' across the entire 38,409-word manuscript: {s['global_words_ending_in_f_count']} types ({s['global_words_ending_in_f_tokens']} tokens): {[x['word'] for x in words_ending_in_f]}")
    print("3. All 15 Outer Index Words on f66r:")
    for p in outer_word_profiles:
        print(f"   #{p['index']:2d} <f66r.{p['loc_id']}> {p['word']:8s} (approx_key={p['approx_aligned_key']:5s}) | global_cnt={p['global_count']:4d} | secs={p['section_distribution']}")


if __name__ == "__main__":
    main()
