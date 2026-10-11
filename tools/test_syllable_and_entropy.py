"""
Phase 9 (Avenue B): Information-Theoretic Slot Decomposition, Mutual Information,
and Multi-Word Syllable/Clause Grouping Analysis of the Voynich Manuscript.

Outputs:
- data/syllable_and_entropy.json
"""

import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ZL_PATH = ROOT / "data" / "ZL3b-n.txt"
INDEX_PATH = ROOT / "data" / "folio_index.json"
OUT_PATH = ROOT / "data" / "syllable_and_entropy.json"


def clean_word(raw: str) -> str:
    w = re.sub(r"\[([^:\]]+):[^\]]+\]", r"\1", raw)
    w = re.sub(r"\{[^}]*\}", "", w)
    w = re.sub(r"<[^>]*>", "", w)
    w = w.replace("?", "").replace("!", "").replace("*", "").replace("%", "")
    w = w.replace("'", "").replace(",", "").strip()
    return w


def canonicalize(w: str) -> str:
    if not w:
        return ""
    s = w
    if len(s) > 2 and s[0] in ("q", "y"):
        s = s[1:]
    s = s.replace("cth", "ckh").replace("cph", "ckh").replace("cfh", "ckh")
    s = s.replace("p", "t").replace("f", "k")
    s = re.sub(r"e+", "e", s)
    s = re.sub(r"i+", "i", s)
    s = re.sub(r"o+", "o", s)
    s = re.sub(r"a+", "a", s)
    if len(s) > 2 and s.endswith("m"):
        s = s[:-1] + "r"
    return s


# Deterministic 5-Slot Morphological Parser for Voynich Words:
# Slot 1 (Proclitic/Initial): q, y, d, s, l, r, o, a, or empty
# Slot 2 (Onset/Link vowel): o, a, e, y, or empty
# Slot 3 (Core Consonant / Gallows / Bench): cth, ckh, cph, cfh, ch, sh, k, t, p, f, d, l, r, s, n, m, or empty
# Slot 4 (Medial Vowel / Minim Grade): eee, ee, e, o, a, ii, i, eo, ea, or empty
# Slot 5 (Terminal Suffix): aiin, iin, in, edy, eey, dy, ey, ky, ty, ly, ry, sy, y, ol, al, el, or, ar, am, om, s, d, l, r, m, or empty

SLOT_REGEX = re.compile(
    r"^"
    r"(?P<s1>qo|q|y|d|s|l)?"
    r"(?P<s2>o|a|e)?"
    r"(?P<s3>cth|ckh|cph|cfh|kch|tch|pch|fch|dch|lch|rch|sch|ksh|tsh|psh|fsh|ch|sh|lk|lt|lp|lf|ld|lr|ls|k|t|p|f|d|l|r|s)?"
    r"(?P<s4>eee|ee|e|eo|ea|o|a|ii|i)?"
    r"(?P<s5>aiin|iiin|iin|ain|in|edy|eey|ody|aly|ory|ary|dy|ey|ky|ty|py|fy|ly|ry|sy|chy|shy|y|ol|al|el|or|ar|er|am|om|aim|s|d|l|r|m)?"
    r"$"
)


def parse_5slots(w: str):
    # Ensure `qo` splits into s1='q', s2='o'
    if w.startswith("qo") and len(w) > 2:
        m = SLOT_REGEX.match(w[2:])
        if m and not m.group("s1") and not m.group("s2"):
            return (
                "q",
                "o",
                m.group("s3") or "∅",
                m.group("s4") or "∅",
                m.group("s5") or "∅",
                True,
            )
    m = SLOT_REGEX.match(w)
    if m:
        s1 = m.group("s1") or "∅"
        s2 = m.group("s2") or "∅"
        if s1 == "qo":
            s1, s2 = "q", "o"
        return (
            s1,
            s2,
            m.group("s3") or "∅",
            m.group("s4") or "∅",
            m.group("s5") or "∅",
            True,
        )
    # Fallback heuristic decomposition for double-core or multi-syllable compounds
    s1 = "∅"
    rem = w
    if rem.startswith("qo") and len(rem) > 2:
        s1, s2 = "q", "o"
        rem = rem[2:]
    else:
        if len(rem) > 1 and rem[0] in ("q", "y", "d", "s", "l") and not rem.startswith("sh"):
            s1 = rem[0]
            rem = rem[1:]
        s2 = "∅"
        if rem and rem[0] in ("o", "a", "e"):
            s2 = rem[0]
            rem = rem[1:]
    s5 = "∅"
    for suf in (
        "aiin", "iiin", "iin", "ain", "in", "edy", "eey", "ody", "aly", "ory", "ary",
        "chy", "shy", "dy", "ey", "ky", "ty", "py", "fy", "ly", "ry", "sy", "y",
        "ol", "al", "el", "or", "ar", "er", "am", "om", "aim", "s", "d", "l", "r", "m"
    ):
        if rem.endswith(suf) and len(rem) >= len(suf):
            s5 = suf
            rem = rem[: len(rem) - len(suf)]
            break
    s3 = "∅"
    for core in (
        "cth", "ckh", "cph", "cfh", "kch", "tch", "pch", "fch", "dch", "lch", "rch", "sch",
        "ksh", "tsh", "psh", "fsh", "ch", "sh", "lk", "lt", "lp", "lf", "ld", "lr", "ls",
        "k", "t", "p", "f", "d", "l", "r", "s"
    ):
        if rem.startswith(core):
            s3 = core
            rem = rem[len(core):]
            break
    # Keep S4 strictly vocalic grade if possible; if extra consonants remain, append to S3
    m_v = re.match(r"^([^aeoi]*)(eee|ee|e|eo|ea|o|a|ii|i)?$", rem)
    if m_v and (m_v.group(1) or m_v.group(2)):
        if m_v.group(1):
            s3 = (s3 if s3 != "∅" else "") + m_v.group(1)
        s4 = m_v.group(2) or "∅"
    else:
        s4 = rem if rem else "∅"
    return (s1, s2, s3, s4, s5, False)


def shannon_entropy(counter: Counter) -> float:
    total = sum(counter.values())
    if total == 0:
        return 0.0
    h = 0.0
    for c in counter.values():
        if c > 0:
            p = c / total
            h -= p * math.log2(p)
    return h


def mutual_information(pairs: list[tuple[str, str]]) -> float:
    n = len(pairs)
    if n == 0:
        return 0.0
    cx = Counter(x for x, _ in pairs)
    cy = Counter(y for _, y in pairs)
    cxy = Counter(pairs)
    return shannon_entropy(cx) + shannon_entropy(cy) - shannon_entropy(cxy)


def main():
    folio_index = json.loads(INDEX_PATH.read_text(encoding="utf-8"))["folios"]
    folio_lang = {f: info.get("currier_lang", "?") for f, info in folio_index.items()}
    folio_sec = {f: info.get("section", "?") for f, info in folio_index.items()}

    all_words = []
    prose_lines = []
    currier_words = {"A": [], "B": []}

    cur_folio = None
    for raw_line in ZL_PATH.read_text(encoding="utf-8", errors="ignore").splitlines():
        if raw_line.startswith("#") or not raw_line.strip():
            continue
        m_f = re.match(r"^<(f[0-9]+[rv][0-9]*|fRos)>", raw_line)
        if m_f:
            cur_folio = m_f.group(1)
            continue
        m_l = re.match(r"^<([^>]+)>\s+(.*)$", raw_line)
        if not m_l:
            continue
        header, body = m_l.group(1), m_l.group(2)
        loc_part = header.split(",")[0] if "," in header else header
        loc_type = header.split(",")[1] if "," in header else ""
        folio = loc_part.split(".")[0]

        is_par_start = "<%>" in body
        has_drawing_break = "<->" in body
        chunks = body.split("<->")
        line_tokens = []
        after_break_indices = set()
        for ci, ch in enumerate(chunks):
            toks = [clean_word(t) for t in re.split(r"[.,\s]+", ch) if clean_word(t)]
            if ci > 0 and toks:
                after_break_indices.add(len(line_tokens))
            line_tokens.extend(toks)

        if not line_tokens:
            continue

        all_words.extend(line_tokens)
        lang = folio_lang.get(folio, "?")
        if lang in ("A", "B"):
            currier_words[lang].extend(line_tokens)

        if "P" in loc_type or loc_type == "":
            prose_lines.append({
                "folio": folio,
                "loc": loc_part,
                "lang": lang,
                "section": folio_sec.get(folio, "?"),
                "is_par_start": is_par_start,
                "has_drawing_break": has_drawing_break,
                "after_break_indices": sorted(after_break_indices),
                "words": line_tokens,
            })

    # 1. Word-level, Character-level, Canonical-level, and 5-Slot Entropies
    raw_counter = Counter(all_words)
    canon_counter = Counter(canonicalize(w) for w in all_words)
    char_counter = Counter(ch for w in all_words for ch in w)

    h_raw_word = shannon_entropy(raw_counter)
    h_canon_word = shannon_entropy(canon_counter)
    h_char = shannon_entropy(char_counter)
    avg_len = sum(len(w) for w in all_words) / len(all_words)

    # Conditional character entropy H(c_i | c_{i-1}) within words
    char_bigrams = []
    for w in all_words:
        padded = "^" + w + "$"
        for i in range(len(padded) - 1):
            char_bigrams.append((padded[i], padded[i + 1]))
    c_prev = Counter(x for x, _ in char_bigrams)
    c_pair = Counter(char_bigrams)
    h_char_cond = shannon_entropy(c_pair) - shannon_entropy(c_prev)

    # 2. 5-Slot Decomposition
    s1_c, s2_c, s3_c, s4_c, s5_c = Counter(), Counter(), Counter(), Counter(), Counter()
    tuple_c = Counter()
    exact_regex_matches = 0
    parsed_words = []
    for w in all_words:
        s1, s2, s3, s4, s5, exact = parse_5slots(w)
        if exact:
            exact_regex_matches += 1
        s1_c[s1] += 1
        s2_c[s2] += 1
        s3_c[s3] += 1
        s4_c[s4] += 1
        s5_c[s5] += 1
        tuple_c[(s1, s2, s3, s4, s5)] += 1
        parsed_words.append((s1, s2, s3, s4, s5))

    h_s1 = shannon_entropy(s1_c)
    h_s2 = shannon_entropy(s2_c)
    h_s3 = shannon_entropy(s3_c)
    h_s4 = shannon_entropy(s4_c)
    h_s5 = shannon_entropy(s5_c)
    h_sum_slots = h_s1 + h_s2 + h_s3 + h_s4 + h_s5
    h_joint_slots = shannon_entropy(tuple_c)
    within_word_slot_redundancy = h_sum_slots - h_joint_slots

    # Pairwise mutual information I(S_i ; S_j) within the same word
    slot_names = ["S1_Proclitic", "S2_Onset", "S3_Core", "S4_Grade", "S5_Suffix"]
    within_word_mi = {}
    for i in range(5):
        for j in range(i + 1, 5):
            mi = mutual_information([(p[i], p[j]) for p in parsed_words])
            within_word_mi[f"{slot_names[i]}__x__{slot_names[j]}"] = round(mi, 4)

    # 3. Adjacent-Word Information & Slot-to-Slot Transition Mutual Information
    adj_word_pairs = []
    adj_canon_pairs = []
    adj_slot_pairs = []
    for pl in prose_lines:
        ws = pl["words"]
        for i in range(len(ws) - 1):
            w1, w2 = ws[i], ws[i + 1]
            adj_word_pairs.append((w1, w2))
            adj_canon_pairs.append((canonicalize(w1), canonicalize(w2)))
            adj_slot_pairs.append((parse_5slots(w1)[:5], parse_5slots(w2)[:5]))

    mi_adj_raw = mutual_information(adj_word_pairs)
    mi_adj_canon = mutual_information(adj_canon_pairs)
    h_w2_given_w1 = shannon_entropy(Counter(adj_word_pairs)) - shannon_entropy(Counter(x for x, _ in adj_word_pairs))

    # Cross-word slot mutual information I(W1.S_i ; W2.S_j)
    cross_word_slot_mi = {}
    for i in range(5):
        for j in range(5):
            mi = mutual_information([(p1[i], p2[j]) for p1, p2 in adj_slot_pairs])
            cross_word_slot_mi[f"W1_{slot_names[i]}__to__W2_{slot_names[j]}"] = round(mi, 4)

    # 4. Testing the "1 Voynich Word = 1 Syllable / 2-Letter Code Group" & Multi-Word Phrase Grouping Hypothesis
    # Notice:
    # - A single Voynich word has H(W) = 9.96 bits (or H(Canon) = 9.35 bits), and conditional entropy inside a line
    #   or given core slots is only ~4.5-6.5 bits — which matches a SINGLE SYLLABLE in natural languages (English/Latin
    #   syllables have 1st-order entropy ~6.0-7.5 bits, whereas full European words have 10.5-12.5 bits and high conditional freedom).
    # - Let's segment each line into "Syntactic Phrases / Multi-Syllable Word Groups" using two empirical segmentation rules:
    #   Rule A (Clause/Phrase Chunking by Structural Boundaries):
    #     - A new phrase begins at: line_start, after `<->` drawing intrusion, at any Gallows-initial word (k/t/p/f/ch/sh),
    #       or after a terminal closer (`daiin`, `am/om/aim`, `dal`, `ol`).
    #   Rule B (Proclitic-Head Pairing):
    #     - Combine `[Modifier: chedy/shedy/chol/shol/daiin/ol]` + `[q-Proclitic Word: qo...]` into a single compound unit,
    #       and combine `[q-X / X]` canonical twins.

    phrases_rule_a = []
    phrase_lengths_a = []
    for pl in prose_lines:
        ws = pl["words"]
        breaks = set(pl["after_break_indices"])
        cur = []
        for idx, w in enumerate(ws):
            is_new = False
            if idx == 0 or idx in breaks:
                is_new = True
            elif w.startswith(("k", "t", "p", "f", "yk", "yt", "yp", "yf", "op", "of", "ot", "ok")):
                if len(cur) >= 2:
                    is_new = True
            if is_new and cur:
                phrases_rule_a.append(" ".join(cur))
                phrase_lengths_a.append(len(cur))
                cur = [w]
            else:
                cur.append(w)
            # Check if `w` is a hard closer (`daiin`, `-m`, `dal`)
            if w in ("daiin", "dain", "dal", "dar", "am", "dam", "oldam", "daram") or (len(w) > 2 and w.endswith("m")):
                phrases_rule_a.append(" ".join(cur))
                phrase_lengths_a.append(len(cur))
                cur = []
        if cur:
            phrases_rule_a.append(" ".join(cur))
            phrase_lengths_a.append(len(cur))

    phrase_counter_a = Counter(phrases_rule_a)
    h_phrase_a = shannon_entropy(phrase_counter_a)
    avg_phrase_len_a = sum(phrase_lengths_a) / len(phrase_lengths_a)

    # 5. Currier A vs Currier B Slot & Entropy Comparison
    currier_comparison = {}
    for lang in ("A", "B"):
        ws = currier_words[lang]
        rc = Counter(ws)
        cc = Counter(canonicalize(w) for w in ws)
        ps = [parse_5slots(w) for w in ws]
        currier_comparison[lang] = {
            "total_tokens": len(ws),
            "unique_raw_types": len(rc),
            "unique_canon_types": len(cc),
            "H_raw_word_bits": round(shannon_entropy(rc), 4),
            "H_canon_word_bits": round(shannon_entropy(cc), 4),
            "H_S1_Proclitic": round(shannon_entropy(Counter(p[0] for p in ps)), 4),
            "H_S2_Onset": round(shannon_entropy(Counter(p[1] for p in ps)), 4),
            "H_S3_Core": round(shannon_entropy(Counter(p[2] for p in ps)), 4),
            "H_S4_Grade": round(shannon_entropy(Counter(p[3] for p in ps)), 4),
            "H_S5_Suffix": round(shannon_entropy(Counter(p[4] for p in ps)), 4),
            "top_S1": Counter(p[0] for p in ps).most_common(6),
            "top_S3": Counter(p[2] for p in ps).most_common(8),
            "top_S5": Counter(p[4] for p in ps).most_common(8),
        }

    # 6. Core Stem Root Inventory (S2 + Normalized S3 + Normalized S4)
    # When we strip Slot 1 (Proclitic) and Slot 5 (Inflectional Suffix) and normalize p->t, f->k, e+->e,
    # how many distinct CORE ROOTS exist across the entire 38,949-word Voynich Manuscript?
    core_roots = Counter()
    core_root_examples = defaultdict(Counter)
    for w in all_words:
        s1, s2, s3, s4, s5, _ = parse_5slots(w)
        ns3 = s3.replace("p", "t").replace("f", "k").replace("cth", "ckh").replace("cph", "ckh").replace("cfh", "ckh")
        ns4 = re.sub(r"e+", "e", s4)
        ns4 = re.sub(r"i+", "i", ns4)
        root = f"{s2}-{ns3}-{ns4}"
        core_roots[root] += 1
        core_root_examples[root][w] += 1

    # Cumulative coverage of top N core roots
    total_toks = len(all_words)
    top_roots_list = []
    cum = 0
    for idx, (rt, cnt) in enumerate(core_roots.most_common(35), 1):
        cum += cnt
        top_roots_list.append({
            "rank": idx,
            "root": rt,
            "count": cnt,
            "pct": round(100.0 * cnt / total_toks, 2),
            "cum_pct": round(100.0 * cum / total_toks, 2),
            "top_surface_forms": [f"{w} ({c})" for w, c in core_root_examples[rt].most_common(5)],
        })

    results = {
        "summary_metrics": {
            "total_words": total_toks,
            "unique_raw_words": len(raw_counter),
            "unique_canonical_words": len(canon_counter),
            "avg_word_length_chars": round(avg_len, 3),
            "H_char_unigram_bits": round(h_char, 4),
            "H_char_conditional_bits": round(h_char_cond, 4),
            "H_raw_word_bits": round(h_raw_word, 4),
            "H_canonical_word_bits": round(h_canon_word, 4),
            "H_word_conditional_adj_bits": round(h_w2_given_w1, 4),
            "MI_adjacent_raw_words_bits": round(mi_adj_raw, 4),
            "MI_adjacent_canonical_words_bits": round(mi_adj_canon, 4),
            "exact_5slot_regex_coverage_pct": round(100.0 * exact_regex_matches / total_toks, 2),
        },
        "slot_entropies_bits": {
            "S1_Proclitic_Initial": round(h_s1, 4),
            "S2_Onset_Vowel": round(h_s2, 4),
            "S3_Core_Consonant": round(h_s3, 4),
            "S4_Medial_Grade": round(h_s4, 4),
            "S5_Terminal_Suffix": round(h_s5, 4),
            "sum_of_5_slot_entropies": round(h_sum_slots, 4),
            "joint_5_slot_entropy": round(h_joint_slots, 4),
            "within_word_slot_redundancy_MI": round(within_word_slot_redundancy, 4),
        },
        "within_word_slot_MI": within_word_mi,
        "cross_word_slot_MI": cross_word_slot_mi,
        "currier_A_vs_B": currier_comparison,
        "core_root_inventory": {
            "total_unique_core_roots_S2_S3_S4": len(core_roots),
            "H_core_root_bits": round(shannon_entropy(core_roots), 4),
            "top_35_core_roots": top_roots_list,
        },
        "multi_word_clause_phrases": {
            "total_clauses": len(phrases_rule_a),
            "avg_words_per_clause": round(avg_phrase_len_a, 3),
            "H_clause_bits": round(h_phrase_a, 4),
            "top_25_recurring_clauses": phrase_counter_a.most_common(25),
        },
    }

    OUT_PATH.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")

    print("=== 1. INFORMATION-THEORETIC SUMMARY ===")
    for k, v in results["summary_metrics"].items():
        print(f"  {k:34s}: {v}")

    print("\n=== 2. 5-SLOT SHANNON ENTROPY DECOMPOSITION (BITS) ===")
    for k, v in results["slot_entropies_bits"].items():
        print(f"  {k:34s}: {v}")

    print("\n=== 3. TOP WITHIN-WORD SLOT MUTUAL INFORMATION I(S_i ; S_j) ===")
    for k, v in sorted(within_word_mi.items(), key=lambda x: -x[1]):
        print(f"  {k:34s}: {v} bits")

    print("\n=== 4. TOP CROSS-WORD SLOT MUTUAL INFORMATION I(W1.S_i ; W2.S_j) ===")
    for k, v in sorted(cross_word_slot_mi.items(), key=lambda x: -x[1])[:8]:
        print(f"  {k:40s}: {v} bits")

    print(f"\n=== 5. CORE ROOT INVENTORY (S2+S3+S4): {len(core_roots)} TOTAL ROOTS (H = {results['core_root_inventory']['H_core_root_bits']} bits) ===")
    for r in top_roots_list[:15]:
        print(f"  #{r['rank']:02d} {r['root']:12s} : {r['count']:5d} ({r['pct']:5.2f}%, cum {r['cum_pct']:5.2f}%) -> {', '.join(r['top_surface_forms'][:4])}")


if __name__ == "__main__":
    main()
