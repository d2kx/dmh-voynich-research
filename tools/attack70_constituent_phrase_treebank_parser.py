"""
Attack 70: Complete Constituent Phrase Grammar (`TOP_HEAD`, `VP_PROC`, `NP_MEAS`, `PP_PREP`, `FIN_CLOSE`)
& Full-Corpus Clause Treebank Parser.

Building on Attack 69 (which proved that 2-word sequences like `or . aiin`, `chol . daiin`, and
`ol . chedy` are syntactic constituents equivalent to fused single-word compounds `oraiin`, `chodaiin`,
`olchedy` at z = +16.16 and context cosine z = +7.40), this script chunks all 5,262 lines (36,229 tokens)
of the Voynich Manuscript into 5 canonical phrase constituent types:

  1. `TOP_HEAD`  : Line-1 / Paragraph-initial topic header (`<%>p/f... [+ nominal]`) or line-initial `s-/y-` opener
  2. `VP_PROC`   : Procedural Verb Phrase (`[ol/dal]? + [ch/sh verb] + [qo- active operator]*` or standalone `[qo- + verb]`)
  3. `NP_MEAS`   : Nominal / Partitive Measure Phrase (`[Gallows/Bench/Liquid nominal] + [daiin/aiin/raiin/ol/or/al/ar]`)
  4. `PP_PREP`   : Deictic / Prepositional Case Phrase (`[dar/dal/dol/dor/daiin/saiin] + [complement]`)
  5. `FIN_CLOSE` : Right-margin line/clause closer (`-am/-om/-m` or line-final bare `-y/-dy`)

Computes:
  - Total constituents, mean words per constituent, and mean constituents per line.
  - Constituent-to-Constituent transition matrix and within-line permutation z-score.
  - Top 30 multi-word `[VP_PROC]`, `[NP_MEAS]`, and `[PP_PREP]` constituents across the manuscript.
  - Exports `data/attack70_constituent_phrase_treebank_parser.json`.
"""

import json
import math
import random
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ZL_PATH = ROOT / "data" / "ZL3b-n.txt"
OUT_JSON = ROOT / "data" / "attack70_constituent_phrase_treebank_parser.json"

LOCUS_RE = re.compile(r"^<f([0-9]+[rv][0-9]*|Ros)\.([^,>]+),([^>]+)>\s*(.*)$")


def mean(xs):
    return sum(xs) / len(xs) if xs else 0.0


def std(xs):
    if len(xs) < 2:
        return 0.0
    m = mean(xs)
    return math.sqrt(sum((x - m) ** 2 for x in xs) / len(xs))


def clean_tokens(raw: str):
    s = re.sub(r"\{[^}]*\}", "", raw)
    s = re.sub(r"\[([^:\]]+):[^\]]+\]", r"\1", s)
    s = s.replace("<%>", " ").replace("<$>", " ").replace("<->", " ")
    s = re.sub(r"<[^>]*>", " ", s)
    s = re.sub(r"@[0-9]+;", "", s)
    s = re.sub(r"[^a-zA-Z.\s]", "", s).lower()
    return [t for t in s.replace(".", " ").split() if t]


def word_tag(w: str, idx: int, n: int, is_para: bool) -> str:
    if idx == 0 and (is_para or any(c in w for c in ("p", "f"))):
        return "W_TOP"
    if idx == n - 1 and (w.endswith(("am", "om", "m")) or w in ("dy", "ky", "ty", "ry", "ly")):
        return "W_CLOSE"
    if w.startswith("qo") or (w.startswith(("l", "ol", "qol")) and w.endswith(("edy", "eedy", "ey", "eey", "dy"))):
        return "W_QACT"
    if w.startswith(("ch", "sh")) and w.endswith(("edy", "eedy", "dy", "ey", "eey", "y")):
        return "W_CHV"
    if w in ("ol", "dal", "qol", "al") and idx < n - 1:
        return "W_APPL"
    if w in ("daiin", "dain", "aiin", "ain", "raiin", "rain", "iiin"):
        return "W_MEAS"
    if w.startswith(("d", "s", "y")) and len(w) <= 5 and not w.endswith(("edy", "eedy")):
        return "W_PREP"
    return "W_NOM"


def chunk_line_into_constituents(words, is_para: bool):
    """
    Deterministic bottom-up constituent chunker combining adjacent compatible word tags into
    phrase constituents (`TOP_HEAD`, `VP_PROC`, `NP_MEAS`, `PP_PREP`, `FIN_CLOSE`).
    """
    n = len(words)
    tags = [word_tag(w, i, n, is_para) for i, w in enumerate(words)]
    constituents = []
    i = 0
    while i < n:
        t = tags[i]
        w = words[i]

        # 1. TOP_HEAD: W_TOP (+ optional W_NOM or W_MEAS)
        if t == "W_TOP":
            if i + 1 < n and tags[i + 1] in ("W_NOM", "W_MEAS"):
                constituents.append(("TOP_HEAD", [w, words[i + 1]]))
                i += 2
            else:
                constituents.append(("TOP_HEAD", [w]))
                i += 1
            continue

        # 2. FIN_CLOSE at end of line
        if t == "W_CLOSE":
            constituents.append(("FIN_CLOSE", [w]))
            i += 1
            continue

        # 3. VP_PROC: [W_APPL]? + [W_CHV] + [W_QACT]? OR [W_QACT] + [W_CHV/W_QACT]?
        if t == "W_APPL" and i + 1 < n and tags[i + 1] in ("W_CHV", "W_QACT"):
            span = [w, words[i + 1]]
            i += 2
            if i < n and tags[i] == "W_QACT":
                span.append(words[i])
                i += 1
            constituents.append(("VP_PROC", span))
            continue

        if t == "W_CHV":
            span = [w]
            i += 1
            if i < n and tags[i] == "W_QACT":
                span.append(words[i])
                i += 1
            constituents.append(("VP_PROC", span))
            continue

        if t == "W_QACT":
            span = [w]
            i += 1
            if i < n and tags[i] in ("W_CHV", "W_QACT"):
                span.append(words[i])
                i += 1
            elif i < n and tags[i] == "W_MEAS":
                span.append(words[i])
                i += 1
            constituents.append(("VP_PROC", span))
            continue

        # 4. PP_PREP: W_PREP + [W_NOM / W_MEAS / W_APPL]?
        if t == "W_PREP":
            if i + 1 < n and tags[i + 1] in ("W_NOM", "W_MEAS", "W_APPL"):
                constituents.append(("PP_PREP", [w, words[i + 1]]))
                i += 2
            else:
                constituents.append(("PP_PREP", [w]))
                i += 1
            continue

        # 5. NP_MEAS: W_NOM + [W_MEAS / W_NOM]? OR W_MEAS (+ W_NOM)?
        if t in ("W_NOM", "W_MEAS", "W_APPL"):
            if i + 1 < n and tags[i + 1] in ("W_MEAS", "W_APPL"):
                constituents.append(("NP_MEAS", [w, words[i + 1]]))
                i += 2
            elif t == "W_MEAS" and i + 1 < n and tags[i + 1] == "W_NOM":
                constituents.append(("NP_MEAS", [w, words[i + 1]]))
                i += 2
            else:
                constituents.append(("NP_MEAS", [w]))
                i += 1
            continue

        constituents.append(("NP_MEAS", [w]))
        i += 1

    return constituents


def main():
    line_constituents = []
    const_type_counts = Counter()
    multiword_phrases = defaultdict(Counter)
    total_words = 0
    total_constituents = 0

    for raw_line in ZL_PATH.read_text(encoding="utf-8", errors="replace").splitlines():
        raw_line = raw_line.strip()
        if not raw_line or raw_line.startswith("#"):
            continue
        m = LOCUS_RE.match(raw_line)
        if not m:
            continue
        body = m.group(4)
        is_para = "<%>" in body
        toks = clean_tokens(body)
        if not toks:
            continue
        chunks = chunk_line_into_constituents(toks, is_para)
        total_words += len(toks)
        total_constituents += len(chunks)
        line_constituents.append([c[0] for c in chunks])
        for ctype, span in chunks:
            const_type_counts[ctype] += 1
            if len(span) >= 2:
                multiword_phrases[ctype][" . ".join(span)] += 1

    # Constituent-level transition MI across lines with >= 2 constituents
    bgs = []
    for cseq in line_constituents:
        for i in range(len(cseq) - 1):
            bgs.append((cseq[i], cseq[i + 1]))

    n_bg = len(bgs)
    cx = Counter(x for x, _ in bgs)
    cy = Counter(y for _, y in bgs)
    cxy = Counter(bgs)
    obs_mi = sum(
        (c / n_bg) * math.log2((c / n_bg) / ((cx[x] / n_bg) * (cy[y] / n_bg)))
        for (x, y), c in cxy.items()
    )

    rng = random.Random(7001)
    null_mis = []
    for _ in range(500):
        sim_bgs = []
        for cseq in line_constituents:
            if len(cseq) > 1:
                shuf = list(cseq)
                rng.shuffle(shuf)
                for i in range(len(shuf) - 1):
                    sim_bgs.append((shuf[i], shuf[i + 1]))
        sx = Counter(x for x, _ in sim_bgs)
        sy = Counter(y for _, y in sim_bgs)
        sxy = Counter(sim_bgs)
        m_val = sum(
            (c / n_bg) * math.log2((c / n_bg) / ((sx[x] / n_bg) * (sy[y] / n_bg)))
            for (x, y), c in sxy.items()
        )
        null_mis.append(m_val)

    z_const_mi = (obs_mi - mean(null_mis)) / (std(null_mis) + 1e-12)

    # Transition table
    transitions = []
    for (x, y), c in cxy.most_common():
        exp = (cx[x] * cy[y]) / n_bg
        transitions.append({
            "from": x,
            "to": y,
            "count": c,
            "expected": round(exp, 1),
            "lift": round(c / exp, 3) if exp > 0 else 0,
        })
    transitions.sort(key=lambda d: d["lift"], reverse=True)

    print("=== ATTACK 70: COMPLETE CONSTITUENT PHRASE GRAMMAR & TREEBANK PARSER ===")
    print(f"Total Lines: {len(line_constituents):,} | Words: {total_words:,} -> Phrase Constituents: {total_constituents:,}")
    print(f"Mean Words per Constituent: {total_words/total_constituents:.3f} | Mean Constituents per Line: {total_constituents/len(line_constituents):.3f}")
    print(f"Constituent-Level Bigram MI = {obs_mi:.5f} bits vs {mean(null_mis):.5f} ± {std(null_mis):.5f} null (z = {z_const_mi:+.2f})\n")
    print("Constituent Inventory:")
    for ct, c in const_type_counts.most_common():
        print(f"  {ct:10s}: {c:6,d} ({100*c/total_constituents:5.2f}%) | Top Multi-Word: {dict(multiword_phrases[ct].most_common(4))}")

    out = {
        "summary": {
            "total_lines": len(line_constituents),
            "total_words": total_words,
            "total_constituents": total_constituents,
            "mean_words_per_constituent": round(total_words / total_constituents, 3),
            "mean_constituents_per_line": round(total_constituents / len(line_constituents), 3),
            "constituent_transition_mi_bits": round(obs_mi, 5),
            "within_line_permutation_z": round(z_const_mi, 2),
        },
        "constituent_counts": dict(const_type_counts),
        "top_multiword_constituents": {
            ct: dict(multiword_phrases[ct].most_common(15))
            for ct in ["VP_PROC", "NP_MEAS", "PP_PREP", "TOP_HEAD"]
        },
        "constituent_transitions": transitions,
    }
    OUT_JSON.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"\nSaved -> {OUT_JSON}")


if __name__ == "__main__":
    main()
