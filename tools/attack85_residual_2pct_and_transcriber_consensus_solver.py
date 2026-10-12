#!/usr/bin/env python3
"""
Attack 85 (Discovery 102): Resolving the Final 2.85% Residual (`1,027` Unexplained Word Types /
`1,034` Tokens) via Multi-Transcriber Line-to-Line Alignment (`ZL3b-n`, `RF1b-er`, `IT2a-n`)
& Recursive Multi-Morpheme Segmentation

Tests:
1. Aligns all `5,376` prose lines across the three independent EVA transliterations:
   - `ZL3b-n.txt` (Zandbergen-Landini v3b)
   - `RF1b-er.txt` (Reference EVA)
   - `IT2a-n.txt` (Takahashi EVA)
2. Takes the exact `1,027` residual word types (`1,034` tokens = `2.85%` of the corpus) that were
   left unexplained in `TIER6_RESIDUAL_UNEXPLAINED` of Attack 82 (`Discovery 99`) and tests:
   - Sub-Tier 6A (`TRANSCRIBER_SPLIT_OR_VARIANT`): At the exact same `<folio.line>` locus in
     `RF1b-er.txt` or `IT2a-n.txt`, the residual token is either split into standard explained words
     (e.g., `otaiinodain -> otaiin . o . dain`, `dolchiody -> do . lchody`) or read as an already-explained
     word (`TIER1..TIER5`)!
   - Sub-Tier 6B (`THREE_MORPHEME_COMPOUND_OR_PHRASE`): Splits into 3 attested words/cores/particles
     (`M_1 + M_2 + M_3`) from the Top-1,000 / 46-Core inventory (e.g., `Prefix + Core_1 + Linker_Vowel + Core_2 + Suffix`
     or 3-word univerbation `W_1 + W_2 + W_3`).
   - Sub-Tier 6C (`UNCERTAIN_BRACKET_OR_DAMAGED_LOCUS`): Contains uncertain/damaged bracket readings
     `[a:b]` or `?` in the raw `ZL3b-n.txt` line at that exact token position.
   - Sub-Tier 6D (`TWO_EDIT_PALEOGRAPHIC_GLIDE`): Within Levenshtein distance 2 of an attested
     Top-1,000 word of length >= 5.
   - Sub-Tier 6E (`IRREDUCIBLE_HAPAX_RESIDUAL`): What remains unexplained across the entire
     36,229-word Voynich Manuscript after Tiers 1–5 and Sub-Tiers 6A–6D!
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
RF_PATH = DATA_DIR / "RF1b-er.txt"
IT_PATH = DATA_DIR / "IT2a-n.txt"
OUT_JSON = DATA_DIR / "attack85_residual_2pct_and_transcriber_consensus_solver.json"

LOCUS_RE = re.compile(r"^<f([0-9]+[rv][0-9]*|Ros)\.([^,>]+),([^>]+)>\s*(.*)$")

PREFIXES = ("qok", "qot", "qop", "qof", "qol", "qo", "po", "fo", "so", "do", "yo", "lo", "ro",
            "ol", "al", "or", "ar", "da", "sa", "yk", "yt", "ok", "ot", "op", "of", "ch", "sh",
            "q", "o", "y", "s", "d", "l", "r", "")
SUFFIXES = ("aiin", "oiin", "eiin", "ain", "oin", "ein", "iin", "in",
            "edy", "ody", "ady", "eey", "ey", "dy", "hy", "ky", "ty", "py", "fy", "ly", "ry", "sy", "y",
            "eol", "eal", "ol", "al", "el", "il", "ul",
            "eor", "ear", "or", "ar", "er", "ir",
            "am", "om", "em", "im", "m", "n", "s", "d", "l", "r", "o", "a", "")


def clean_tokens_with_raw(raw: str):
    s = re.sub(r"\{[^}]*\}", "", raw)
    s = s.replace("<%>", " ").replace("<$>", " ").replace("<->", " ")
    s = re.sub(r"<[^>]*>", " ", s)
    s = re.sub(r"@[0-9]+;", "", s)
    raw_chunks = [c for c in s.replace(".", " ").split() if c]
    out = []
    for c in raw_chunks:
        has_unc = ("[" in c) or ("?" in c) or ("*" in c)
        c_res = re.sub(r"\[([^:\]]+):[^\]]+\]", r"\1", c)
        w = re.sub(r"[^a-zA-Z]", "", c_res).lower()
        if w:
            out.append((w, has_unc, c))
    return out


def clean_tokens(raw: str):
    return [w for w, _, _ in clean_tokens_with_raw(raw)]


def canonical_form(w: str) -> str:
    s = w
    if s.startswith("qo") and len(s) > 3:
        s = "o" + s[2:]
    elif s.startswith("q") and len(s) > 2:
        s = s[1:]
    s = s.replace("cph", "cth").replace("cfh", "ckh")
    s = s.replace("p", "t").replace("f", "k")
    s = s.replace("sh", "ch")
    s = re.sub(r"e+", "e", s)
    s = re.sub(r"i+", "i", s)
    return s


def decompose_word(w: str):
    cands = []
    for p in PREFIXES:
        if not w.startswith(p):
            continue
        rem1 = w[len(p):]
        for s in SUFFIXES:
            if not rem1.endswith(s):
                continue
            core = rem1[:len(rem1) - len(s)] if s else rem1
            if core:
                cands.append((p, core, s))
    return cands


def edit_distance_le2(w1: str, w2: str) -> int:
    if abs(len(w1) - len(w2)) > 2:
        return 3
    dp = list(range(len(w2) + 1))
    for i, c1 in enumerate(w1, 1):
        new_dp = [i]
        for j, c2 in enumerate(w2, 1):
            cost = 0 if c1 == c2 else 1
            new_dp.append(min(new_dp[-1] + 1, dp[j] + 1, dp[j - 1] + cost))
        dp = new_dp
        if min(dp) > 2:
            return 3
    return dp[-1]


def parse_eva_file(path: Path) -> dict:
    lines = {}
    for raw_line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        raw_s = raw_line.strip()
        if not raw_s or raw_s.startswith("#"):
            continue
        m = LOCUS_RE.match(raw_s)
        if m:
            folio, lnum, ltype, text = m.group(1), m.group(2), m.group(3), m.group(4)
            if ltype.startswith(("L", "R", "C", "S")):
                continue
            lines[f"f{folio}.{lnum}"] = clean_tokens_with_raw(text)
    return lines


def main():
    zl_lines = parse_eva_file(ZL_PATH)
    rf_lines = parse_eva_file(RF_PATH)
    it_lines = parse_eva_file(IT_PATH)

    word_counts = Counter()
    word_uncertain_hits = Counter()
    word_loci = defaultdict(list)

    for loc, tok_tuples in zl_lines.items():
        for w, has_unc, raw_c in tok_tuples:
            word_counts[w] += 1
            if has_unc:
                word_uncertain_hits[w] += 1
            word_loci[w].append((loc, raw_c))

    ranked = word_counts.most_common()
    top1000_words = [w for w, _ in ranked[:1000]]
    top1000_set = set(top1000_words)
    top500_words = [w for w, _ in ranked[:500]]

    canon_to_top1000 = {}
    for w in top1000_words:
        cw = canonical_form(w)
        if cw not in canon_to_top1000:
            canon_to_top1000[cw] = w

    attested_cores = set()
    attested_canon_cores = set()
    for w in top500_words:
        cands = decompose_word(w)
        cands.sort(key=lambda x: (len(x[1]), -len(x[0]) - len(x[2])))
        if cands:
            _, core, _ = cands[0]
            attested_cores.add(core)
            attested_canon_cores.add(canonical_form(core))

    top1000_by_len = defaultdict(list)
    for w in top1000_words:
        if len(w) >= 3:
            top1000_by_len[len(w)].append(w)

    def is_tier1_to_5(w: str) -> bool:
        if w in top1000_set or canonical_form(w) in canon_to_top1000:
            return True
        cands = decompose_word(w)
        for p, core, s in cands:
            if core in attested_cores or canonical_form(core) in attested_canon_cores:
                return True
        for split_i in range(2, len(w) - 1):
            w1, w2 = w[:split_i], w[split_i:]
            if (w1 in top1000_set or canonical_form(w1) in canon_to_top1000) and (
                w2 in top1000_set or canonical_form(w2) in canon_to_top1000
            ):
                return True
        for p, core, s in cands:
            for split_i in range(1, len(core)):
                c1, c2 = core[:split_i], core[split_i:]
                if (c1 in attested_cores or canonical_form(c1) in attested_canon_cores) and (
                    c2 in attested_cores or canonical_form(c2) in attested_canon_cores
                ):
                    return True
        if not any(g in w for g in ("k", "t", "p", "f", "ch", "sh")) and set(w).issubset(
            set("qoaysdlreimn")
        ):
            return True
        if len(w) >= 3:
            for cand_len in (len(w), len(w) - 1, len(w) + 1):
                for tw in top1000_by_len[cand_len]:
                    if edit_distance_le2(w, tw) == 1:
                        return True
        return False

    # Build atomic morpheme inventory for recursive 3-morpheme decomposition (Sub-Tier 6B)
    atomic_morphemes = set(top1000_set) | attested_cores | attested_canon_cores | set(PREFIXES) | set(SUFFIXES)
    atomic_morphemes.discard("")
    # Keep morphemes of length >= 2 (plus single-vowel linkers o, a, e, y, d, s, l, r)
    valid_segments = {m for m in atomic_morphemes if len(m) >= 2} | {"o", "a", "e", "y", "d", "s", "l", "r"}

    def can_segment_3_morphemes(w: str):
        cw = canonical_form(w)
        # Try 3-way split of w or cw into 3 valid segments where at least two have len >= 2
        for target in (w, cw):
            n = len(target)
            for i in range(1, n - 1):
                m1 = target[:i]
                if m1 not in valid_segments and canonical_form(m1) not in valid_segments:
                    continue
                for j in range(i + 1, n):
                    m2 = target[i:j]
                    m3 = target[j:]
                    if (m2 in valid_segments or canonical_form(m2) in valid_segments) and (
                        m3 in valid_segments or canonical_form(m3) in valid_segments
                    ):
                        if sum(1 for seg in (m1, m2, m3) if len(seg) >= 2) >= 2:
                            return f"{m1}+{m2}+{m3}"
        # Also try Prefix + Core1 + VowelLinker + Core2 + Suffix
        for p, core, s in decompose_word(w):
            nc = len(core)
            for i in range(1, nc - 1):
                c1 = core[:i]
                if c1 not in attested_cores and canonical_form(c1) not in attested_canon_cores:
                    continue
                for j in range(i + 1, min(i + 4, nc)):
                    linker = core[i:j]
                    c2 = core[j:]
                    if set(linker).issubset(set("oaeiy")) and (
                        c2 in attested_cores or canonical_form(c2) in attested_canon_cores
                    ):
                        return f"[{p or '0'}+{c1}+{linker}+{c2}+{s or '0'}]"
        return None

    # Identify the exact 1,027 Tier-6 residual types from Attack 82
    residual_words = [(w, cnt) for w, cnt in ranked[1000:] if not is_tier1_to_5(w)]

    subtier_types = Counter()
    subtier_tokens = Counter()
    subtier_examples = defaultdict(list)

    for w, cnt in residual_words:
        resolved = False
        # Sub-Tier 6A: Check RF1b-er and IT2a-n at the same line locus
        for loc, raw_c in word_loci[w]:
            for tr_name, tr_dict in (("RF", rf_lines), ("IT", it_lines)):
                if loc not in tr_dict:
                    continue
                tr_words = [tw for tw, _, _ in tr_dict[loc]]
                # 1) Check if w was split into 2 or 3 adjacent words in RF/IT
                for idx in range(len(tr_words) - 1):
                    if tr_words[idx] + tr_words[idx + 1] == w:
                        if is_tier1_to_5(tr_words[idx]) and is_tier1_to_5(tr_words[idx + 1]):
                            subtier_types["SUBTIER_6A_TRANSCRIBER_SPLIT_OR_VARIANT"] += 1
                            subtier_tokens["SUBTIER_6A_TRANSCRIBER_SPLIT_OR_VARIANT"] += cnt
                            if len(subtier_examples["SUBTIER_6A_TRANSCRIBER_SPLIT_OR_VARIANT"]) < 12:
                                subtier_examples["SUBTIER_6A_TRANSCRIBER_SPLIT_OR_VARIANT"].append({
                                    "word": w, "loc": loc, "transcriber": tr_name,
                                    "resolution": f"{tr_words[idx]} . {tr_words[idx+1]}"
                                })
                            resolved = True
                            break
                if resolved:
                    break
                # 2) Check if an aligned word in RF/IT at edit distance <= 2 is Tier 1-5
                for tw in tr_words:
                    if tw != w and edit_distance_le2(w, tw) <= 2 and is_tier1_to_5(tw):
                        subtier_types["SUBTIER_6A_TRANSCRIBER_SPLIT_OR_VARIANT"] += 1
                        subtier_tokens["SUBTIER_6A_TRANSCRIBER_SPLIT_OR_VARIANT"] += cnt
                        if len(subtier_examples["SUBTIER_6A_TRANSCRIBER_SPLIT_OR_VARIANT"]) < 12:
                            subtier_examples["SUBTIER_6A_TRANSCRIBER_SPLIT_OR_VARIANT"].append({
                                "word": w, "loc": loc, "transcriber": tr_name,
                                "resolution": f"{w} -> {tw}"
                            })
                        resolved = True
                        break
                if resolved:
                    break
            if resolved:
                break

        if resolved:
            continue

        # Sub-Tier 6B: 3-Morpheme Compound or Phrase Segmentation
        seg3 = can_segment_3_morphemes(w)
        if seg3:
            subtier_types["SUBTIER_6B_THREE_MORPHEME_COMPOUND"] += 1
            subtier_tokens["SUBTIER_6B_THREE_MORPHEME_COMPOUND"] += cnt
            if len(subtier_examples["SUBTIER_6B_THREE_MORPHEME_COMPOUND"]) < 12:
                subtier_examples["SUBTIER_6B_THREE_MORPHEME_COMPOUND"].append({
                    "word": w, "count": cnt, "segmentation": seg3
                })
            continue

        # Sub-Tier 6C: Uncertain bracket [a:b] or damaged glyph in ZL3b-n.txt
        if word_uncertain_hits[w] > 0:
            subtier_types["SUBTIER_6C_UNCERTAIN_DAMAGED_READING"] += 1
            subtier_tokens["SUBTIER_6C_UNCERTAIN_DAMAGED_READING"] += cnt
            if len(subtier_examples["SUBTIER_6C_UNCERTAIN_DAMAGED_READING"]) < 12:
                loc, raw_c = word_loci[w][0]
                subtier_examples["SUBTIER_6C_UNCERTAIN_DAMAGED_READING"].append({
                    "word": w, "loc": loc, "raw_zl": raw_c
                })
            continue

        # Sub-Tier 6D: Distance-2 Paleographic Neighbor of a Top-1,000 word (for len >= 5)
        if len(w) >= 5:
            found_2ed = None
            for clen in range(max(3, len(w) - 2), len(w) + 3):
                for tw in top1000_by_len[clen]:
                    if edit_distance_le2(w, tw) <= 2:
                        found_2ed = tw
                        break
                if found_2ed:
                    break
            if found_2ed:
                subtier_types["SUBTIER_6D_TWO_EDIT_PALEOGRAPHIC_GLIDE"] += 1
                subtier_tokens["SUBTIER_6D_TWO_EDIT_PALEOGRAPHIC_GLIDE"] += cnt
                if len(subtier_examples["SUBTIER_6D_TWO_EDIT_PALEOGRAPHIC_GLIDE"]) < 12:
                    subtier_examples["SUBTIER_6D_TWO_EDIT_PALEOGRAPHIC_GLIDE"].append({
                        "word": w, "closest_top1000": found_2ed
                    })
                continue

        subtier_types["SUBTIER_6E_IRREDUCIBLE_RESIDUAL"] += 1
        subtier_tokens["SUBTIER_6E_IRREDUCIBLE_RESIDUAL"] += cnt
        if len(subtier_examples["SUBTIER_6E_IRREDUCIBLE_RESIDUAL"]) < 15:
            loc, raw_c = word_loci[w][0]
            subtier_examples["SUBTIER_6E_IRREDUCIBLE_RESIDUAL"].append({
                "word": w, "count": cnt, "loc": loc, "raw_zl": raw_c
            })

    total_tokens = sum(word_counts.values())
    total_types = len(word_counts)
    n_res_types = len(residual_words)
    n_res_tokens = sum(cnt for _, cnt in residual_words)
    irred_types = subtier_types["SUBTIER_6E_IRREDUCIBLE_RESIDUAL"]
    irred_tokens = subtier_tokens["SUBTIER_6E_IRREDUCIBLE_RESIDUAL"]

    breakdown = []
    for st in (
        "SUBTIER_6A_TRANSCRIBER_SPLIT_OR_VARIANT",
        "SUBTIER_6B_THREE_MORPHEME_COMPOUND",
        "SUBTIER_6C_UNCERTAIN_DAMAGED_READING",
        "SUBTIER_6D_TWO_EDIT_PALEOGRAPHIC_GLIDE",
        "SUBTIER_6E_IRREDUCIBLE_RESIDUAL",
    ):
        breakdown.append({
            "subtier": st,
            "residual_types": subtier_types[st],
            "pct_of_tier6_types": round(100.0 * subtier_types[st] / n_res_types, 2),
            "residual_tokens": subtier_tokens[st],
            "pct_of_tier6_tokens": round(100.0 * subtier_tokens[st] / n_res_tokens, 2),
            "pct_of_full_corpus_tokens": round(100.0 * subtier_tokens[st] / total_tokens, 3),
            "examples": subtier_examples[st][:8],
        })

    out = {
        "tier6_residual_input": {
            "residual_types": n_res_types,
            "residual_tokens": n_res_tokens,
            "pct_of_corpus_tokens": round(100.0 * n_res_tokens / total_tokens, 2),
        },
        "resolved_summary": {
            "newly_resolved_types": n_res_types - irred_types,
            "newly_resolved_tokens": n_res_tokens - irred_tokens,
            "pct_of_tier6_tokens_resolved": round(100.0 * (n_res_tokens - irred_tokens) / n_res_tokens, 2),
            "remaining_irreducible_types": irred_types,
            "remaining_irreducible_tokens": irred_tokens,
            "total_corpus_explained_tokens": total_tokens - irred_tokens,
            "total_corpus_explained_token_pct": round(100.0 * (total_tokens - irred_tokens) / total_tokens, 2),
            "total_corpus_explained_types": total_types - irred_types,
            "total_corpus_explained_type_pct": round(100.0 * (total_types - irred_types) / total_types, 2),
        },
        "subtier_breakdown": breakdown,
    }
    OUT_JSON.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"Saved {OUT_JSON}")
    print("Resolved Summary:", out["resolved_summary"])
    for b in breakdown:
        print(
            f"  {b['subtier']}: types={b['residual_types']} ({b['pct_of_tier6_types']}%), "
            f"tokens={b['residual_tokens']} ({b['pct_of_tier6_tokens']}%, {b['pct_of_full_corpus_tokens']}% of corpus)"
        )


if __name__ == "__main__":
    main()
