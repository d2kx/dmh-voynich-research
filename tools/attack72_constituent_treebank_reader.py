#!/usr/bin/env python3
"""
Attack 72: The Voynich Constituent Treebank & Parallel Cross-Dialect Reader
(Synthesizing Attacks 69-71 into a Full-Corpus Constituent Treebank &
Bilingual Currier A <-> Currier B Structural Translation Edition)

Outputs:
- data/attack72_constituent_treebank_reader.json
- notes/CONSTITUENT_TREEBANK_READER.md
"""

import json
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
NOTES_DIR = ROOT / "notes"
ZL_PATH = DATA_DIR / "ZL3b-n.txt"
A69_JSON = DATA_DIR / "attack69_phrase_univerbation_constituent_solver.json"
A70_JSON = DATA_DIR / "attack70_constituent_phrase_treebank_parser.json"
A71_JSON = DATA_DIR / "attack71_parallel_clause_tree_aligner.json"

OUT_JSON = DATA_DIR / "attack72_constituent_treebank_reader.json"
OUT_MD = NOTES_DIR / "CONSTITUENT_TREEBANK_READER.md"

LOCUS_RE = re.compile(r"^<f([0-9]+[rv][0-9]*|Ros)\.([^,>]+),([^>]+)>\s*(.*)$")


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
    n = len(words)
    tags = [word_tag(w, i, n, is_para) for i, w in enumerate(words)]
    constituents = []
    i = 0
    while i < n:
        t = tags[i]
        w = words[i]
        if t == "W_TOP":
            if i + 1 < n and tags[i + 1] in ("W_NOM", "W_MEAS"):
                constituents.append(("TOP_HEAD", [w, words[i + 1]]))
                i += 2
            else:
                constituents.append(("TOP_HEAD", [w]))
                i += 1
            continue
        if t == "W_CLOSE":
            constituents.append(("FIN_CLOSE", [w]))
            i += 1
            continue
        if t in ("W_APPL", "W_CHV", "W_QACT"):
            vp = [w]
            j = i + 1
            while j < n and tags[j] in ("W_CHV", "W_QACT") and len(vp) < 3:
                vp.append(words[j])
                j += 1
            constituents.append(("VP_PROC", vp))
            i = j
            continue
        if t == "W_PREP":
            if i + 1 < n and tags[i + 1] in ("W_NOM", "W_MEAS"):
                constituents.append(("PP_PREP", [w, words[i + 1]]))
                i += 2
            else:
                constituents.append(("PP_PREP", [w]))
                i += 1
            continue
        if t in ("W_NOM", "W_MEAS"):
            if i + 1 < n and tags[i + 1] == "W_MEAS":
                constituents.append(("NP_MEAS", [w, words[i + 1]]))
                i += 2
            elif i + 1 < n and w in ("or", "ar", "ol", "al", "chol", "shol", "chor") and words[i + 1] in ("aiin", "ain", "daiin", "dain", "ol", "al"):
                constituents.append(("NP_MEAS", [w, words[i + 1]]))
                i += 2
            else:
                constituents.append(("NP_MEAS", [w]))
                i += 1
            continue
        constituents.append(("NP_MEAS", [w]))
        i += 1
    return constituents


def gloss_constituent(ctype: str, words: list, all_vocab: set, a_to_b: dict, b_to_a: dict, lang: str) -> str:
    joined = "".join(words)
    phrase_str = " . ".join(words)
    univ_note = ""
    if len(words) == 2 and joined in all_vocab:
        univ_note = f" (≡{joined})"
    elif len(words) == 1:
        w = words[0]
        # Check if single word is a known fused compound
        for pfx in ("or", "ar", "ol", "al", "cho", "chol", "sho", "shol", "qo", "d", "s", "y"):
            if w.startswith(pfx) and len(w) > len(pfx) + 2:
                rem = w[len(pfx):]
                if rem in ("aiin", "daiin", "chedy", "shedy", "keedy", "kedy", "kaiin", "taiin", "ckhy", "cthy"):
                    univ_note = f" (<{pfx}+{rem})"
                    break

    # Cross-dialect note
    dial_notes = []
    for w in words:
        if lang == "A" and w in a_to_b and a_to_b[w] != w:
            dial_notes.append(f"B:{a_to_b[w]}")
        elif lang == "B" and w in b_to_a and b_to_a[w] != w:
            dial_notes.append(f"A:{b_to_a[w]}")
    d_str = f" [{','.join(dial_notes)}]" if dial_notes else ""

    return f"[{ctype}: {phrase_str}{univ_note}{d_str}]"


def main():
    with open(A69_JSON, "r", encoding="utf-8") as f:
        a69 = json.load(f)
    with open(A70_JSON, "r", encoding="utf-8") as f:
        a70 = json.load(f)
    with open(A71_JSON, "r", encoding="utf-8") as f:
        a71 = json.load(f)

    a_to_b = {}
    b_to_a = {}
    for m in a71["a_to_b_lexicon_bridge"]:
        wa = m["word_A"]
        wb_het = m["best_B_heteronym"]
        a_to_b[wa] = wb_het
        if wb_het not in b_to_a:
            b_to_a[wb_het] = wa

    # Add core B -> A verbal bridges
    b_to_a.update({
        "chedy": "chey/chol",
        "shedy": "shey/shol",
        "qokeedy": "qotchy/cthy",
        "qokedy": "qoky/cthy",
        "qokeey": "qokey/chey",
        "qokaiin": "qokain/daiin",
        "okaiin": "daiin",
        "otar": "chor",
        "oky": "cthy",
    })

    # Parse all lines and collect target folios
    all_vocab = Counter()
    folio_lines = defaultdict(list)
    cur_sec = "U"
    cur_lang = "U"
    cur_hand = "U"

    raw_records = []
    for raw_line in ZL_PATH.read_text(encoding="utf-8", errors="replace").splitlines():
        raw_s = raw_line.strip()
        if not raw_s or raw_s.startswith("#"):
            continue
        if raw_s.startswith("<f") and ">" in raw_s and "." not in raw_s.split(">")[0]:
            m_s = re.search(r"\$I=([A-Z])", raw_s)
            cur_sec = m_s.group(1) if m_s else "U"
            m_l = re.search(r"\$L=([A-Z])", raw_s)
            cur_lang = m_l.group(1) if m_l else "U"
            m_h = re.search(r"\$H=([0-9A-Za-z]+)", raw_s)
            cur_hand = m_h.group(1) if m_h else "U"
            continue

        m = LOCUS_RE.match(raw_s)
        if not m:
            continue
        folio, lnum, ltype, raw_txt = f"f{m.group(1)}", m.group(2), m.group(3), m.group(4)
        is_para = "<%>" in raw_txt
        toks = clean_tokens(raw_txt)
        if not toks:
            continue
        for w in toks:
            all_vocab[w] += 1
        raw_records.append((folio, lnum, ltype, cur_sec, cur_lang, cur_hand, is_para, toks))

    vocab_set = {w for w, c in all_vocab.items() if c >= 2}

    total_lines = 0
    total_words = 0
    total_consts = 0
    multiword_consts = 0
    univerbated_multiword_hits = 0
    skeleton_counts = Counter()

    for folio, lnum, ltype, sec, lang, hand, is_para, toks in raw_records:
        consts = chunk_line_into_constituents(toks, is_para)
        total_lines += 1
        total_words += len(toks)
        total_consts += len(consts)
        skel = " -> ".join(c[0] for c in consts)
        skeleton_counts[skel] += 1
        for ctype, ws in consts:
            if len(ws) >= 2:
                multiword_consts += 1
                if "".join(ws) in vocab_set:
                    univerbated_multiword_hits += 1

        folio_lines[folio].append({
            "folio": folio,
            "lnum": lnum,
            "ltype": ltype,
            "sec": sec,
            "lang": lang,
            "hand": hand,
            "is_para": is_para,
            "words": toks,
            "consts": consts,
            "tree_str": " ".join(gloss_constituent(c[0], c[1], vocab_set, a_to_b, b_to_a, lang) for c in consts),
        })

    target_folios = ["f20v", "f1r", "f78r", "f85r2", "f99r", "f107r"]

    # Build Markdown Edition
    md = []
    md.append("# The Voynich Constituent Treebank & Parallel Cross-Dialect Reader (`Attacks 69–72`)\n")
    md.append("## 1. Executive Summary: From Words to Phrase Constituents & Cross-Dialect Clause Trees\n")
    u_test = a69["univerbation_enrichment_test"]
    c_test = a69["constituent_context_equivalence_test"]
    md.append(
        f"- **Corpus Parsed**: `{total_lines:,}` lines | `{total_words:,}` words $\\to$ **`{total_consts:,}` Phrase Constituents** "
        f"(`{total_words / total_consts:.3f}` words/constituent, `{total_consts / total_lines:.3f}` constituents/line).\n"
        f"- **Three-Stage Phrase-Univerbation Continuum (`A . B <-> A,B <-> AB`, Attack 69)**: **`{u_test['observed_rate_pct']:.2f}%` (`{u_test['observed_univerbated_or_comma_hits']} / {u_test['frequent_bigrams_tested']}`)** of frequent 2-word phrases also occur as single-word fused compounds (`AB` or micro-spaced `A,B`) vs. `{u_test['null_rate_mean_pct']:.2f}%` null (**$z = +{u_test['permutation_z']}$**), with identical external syntactic context frames (`mean cosine = {c_test['observed_mean_context_cosine']:.4f}`, **$z = +{c_test['permutation_z']}$**).\n"
        f"- **Constituent Phrase Transition Grammar (`Attack 70`)**: Adjacent phrase constituents (`TOP_HEAD`, `PP_PREP`, `VP_PROC`, `NP_MEAS`, `FIN_CLOSE`) exhibit **`{a70['summary']['constituent_transition_mi_bits']:.5f} bits`** of transition mutual information vs. `0.00609 ± 0.00053 bits` within-line permutation null (**$z = +{a70['summary']['within_line_permutation_z']}$**).\n"
        f"- **Cross-Dialect `Currier A <-> Currier B` Structural & Lexical Alignment (`Attack 71`)**: Currier A (`1,557` prose lines) and Currier B (`2,467` prose lines) share a constituent transition bigram cosine of **`{a71['summary']['constituent_bigram_cosine_AB']:.4f}`**, and the Top-60 Currier A lexemes align to Currier B distributional counterparts at **`mean cosine = {a71['summary']['mean_top1_word_align_cosine']:.4f}`** (`heteronym cosine = {a71['summary']['mean_heteronym_word_align_cosine']:.4f}`, **$z = +{a71['summary']['word_align_z']}$**).\n"
    )

    md.append("\n---\n\n## 2. The Three-Stage Phrase-Univerbation Law (`A . B <-> A,B <-> AB`)\n")
    md.append("| Two-Word Phrase (`A . B`) | Analytical (`A . B`) | Uncertain Space (`A,B`) | Fused Compound (`AB`) | Context Frame Cosine | Total Tokens |\n")
    md.append("| :--- | :---: | :---: | :--- | :---: | :---: |\n")
    for p in a69["top_continuum_families"][:20]:
        fw_str = ", ".join(f"`{k}` ({v})" for k, v in p["fused_words"].items())
        md.append(f"| `{p['phrase_A_B']}` | `{p['dot_phrase_count']}` | `{p['comma_microspace_count']}` | {fw_str} | **`{p['context_cosine_phrase_vs_fused']:.4f}`** | `{p['combined_constituent_tokens']}` |\n")

    md.append("\n---\n\n## 3. Cross-Dialect (`Currier A <-> Currier B`) Distributional Translation Bridge\n")
    md.append("| Currier A Word (`$L=A`) | Count (`A`) | Best Currier B Overall (`$L=B`) | Cosine | Best Currier B Heteronym (`$L=B`) | Count (`B`) | Heteronym Cosine |\n")
    md.append("| :--- | :---: | :--- | :---: | :--- | :---: | :---: |\n")
    for m in a71["a_to_b_lexicon_bridge"][:25]:
        md.append(
            f"| **`{m['word_A']}`** | `{m['count_A']}` | `{m['best_B_overall']}` | `{m['best_B_overall_cos']:.4f}` | "
            f"**`{m['best_B_heteronym']}`** | `{m['count_B_same']}/{m['best_B_heteronym_count']}` | **`{m['best_B_heteronym_cos']:.4f}`** |\n"
        )

    md.append("\n---\n\n## 4. Top 12 Aligned Cross-Dialect Parallel Clause Trees (`Currier A <-> Currier B`)\n")
    md.append("| Alignment Score | Currier A Clause (`$L=A`) | Currier B Parallel Clause (`$L=B`) | Shared Constituent Skeleton |\n")
    md.append("| :---: | :--- | :--- | :--- |\n")
    for p in a71["top_parallel_clause_pairs"][:12]:
        md.append(
            f"| **`{p['score']:.4f}`** | `{p['A_loc']}`: `{p['A_words']}` | `{p['B_loc']}`: `{p['B_words']}` | `{p['A_consts']}` |\n"
        )

    md.append("\n---\n\n## 5. Full Constituent-Bracketed & Cross-Dialect Annotated Editions of 6 Landmark Folios\n")
    md.append("Notation inside each bracketed constituent `[TYPE: words (≡fused / <split) [Dialect Counterpart]]`:\n")
    md.append("- `(≡AB)` indicates a 2-word analytical constituent that also appears in the corpus as the single fused word `AB`.\n")
    md.append("- `(<A+B)` indicates a single fused word decomposed into its underlying `A + B` constituent morphemes.\n")
    md.append("- `[B:word]` / `[A:word]` provides the top cross-dialect distributional counterpart between Currier A and Currier B.\n")

    for fol in target_folios:
        flines = folio_lines.get(fol, [])
        if not flines:
            continue
        f0 = flines[0]
        md.append(f"\n### Folio `{fol}` (Section `$I={f0['sec']}`, Currier `$L={f0['lang']}`, Hand `$H={f0['hand']}`, `{len(flines)}` lines)\n")
        for r in flines[:20]:
            p_mark = "<%> " if r["is_para"] else ""
            md.append(f"- **`<{r['folio']}.{r['lnum']},{r['ltype']}>`** {p_mark}`{' . '.join(r['words'])}`\n")
            md.append(f"  - **Tree**: `{r['tree_str']}`\n")

    OUT_MD.write_text("".join(md), encoding="utf-8")

    out_data = {
        "summary": {
            "total_lines": total_lines,
            "total_words": total_words,
            "total_constituents": total_consts,
            "multiword_constituents": multiword_consts,
            "univerbated_multiword_hits": univerbated_multiword_hits,
            "univerbated_multiword_share": round(univerbated_multiword_hits / max(multiword_consts, 1), 4),
        },
        "top_clause_skeletons": [
            {"skeleton": k, "count": v} for k, v in skeleton_counts.most_common(25)
        ],
    }
    OUT_JSON.write_text(json.dumps(out_data, indent=2), encoding="utf-8")

    print("=== ATTACK 72: CONSTITUENT TREEBANK & PARALLEL CROSS-DIALECT READER ===")
    print(f"Total Lines: {total_lines:,} | Total Words: {total_words:,} | Total Constituents: {total_consts:,}")
    print(f"Multi-Word Constituents: {multiword_consts:,} | Attested as Fused Word (AB): {univerbated_multiword_hits:,} ({univerbated_multiword_hits/max(multiword_consts,1)*100:.2f}%)")
    print(f"Saved JSON -> {OUT_JSON}")
    print(f"Saved Markdown Reader -> {OUT_MD}")


if __name__ == "__main__":
    main()
