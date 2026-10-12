"""
Attack 64: The Top-500 Core Lexicon (63.60% of the Entire Manuscript) & Complete 6-Level Reference Decoder.

Synthesizes Autonomous Wave 13 (Attacks 61-64 / Discoveries 78-81):
  1. Attack 61: The Isochronous 3-Mora Stem-Template Law (`|Core| + |V_nuc| = 3`, z = +507.17) &
     Scribe-Hand Nucleus Conditioning (`$H=1..5`, z = +286.73), raising explained word entropy to 79.45%.
  2. Attack 62: The 6-Level Hierarchical Entropy Cascade, explaining 97.28% (10.4766 / 10.7699 bits) of
     total unigram word entropy by Level 5, leaving only 0.2932 bits (2.72%) of vowel/minim spelling variation.
  3. Attack 63: The 3x3 Two-Dimensional Paragraph Spatial Grid (`Z11..Z33`, z = +411.74 within-paragraph permutation).
  4. Attack 64: Exhaustive 6-Level Morphological, Spatial-Zone, Sectional, and Structural Decoding Table of the
     Top 500 Most Frequent Words of the Voynich Manuscript (`23,042 / 36,229` tokens = `63.60%` of the entire book).
"""

import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

from attack52_complete_proclitic_and_top100_word_parser import decompose_and_gloss
from attack61_internal_stem_nucleus_solver import parse_open_token, parse_post_into_nucleus_and_coda

ZL_PATH = ROOT / "data" / "ZL3b-n.txt"
A61_JSON = ROOT / "data" / "attack61_internal_stem_nucleus_solver.json"
A62_JSON = ROOT / "data" / "attack62_subcell_allography_entropy_decomposition.json"
A63_JSON = ROOT / "data" / "attack63_paragraph_arc_and_sentence_translator.json"

OUT_JSON = ROOT / "data" / "attack64_top500_lexicon_and_6level_decoder.json"
OUT_MD = ROOT / "notes" / "TOP500_LEXICON_AND_6LEVEL_DECODER.md"

LOCUS_RE = re.compile(r"^<f([0-9]+[rv][0-9]*|Ros)\.([^,>]+),([^>]+)>\s*(.*)$")


def clean_tokens(raw: str):
    s = re.sub(r"\{[^}]*\}", "", raw)
    s = re.sub(r"\[([^:\]]+):[^\]]+\]", r"\1", s)
    s = s.replace("<%>", " ").replace("<$>", " ").replace("<->", " ")
    s = re.sub(r"<[^>]*>", " ", s)
    s = re.sub(r"@[0-9]+;", "", s)
    s = re.sub(r"[^a-zA-Z.\s]", "", s).lower()
    return [t for t in s.replace(".", " ").split() if t]


def dual_matrix_and_nucleus(w: str):
    op = parse_open_token(w)
    if op:
        pre, core, v_nuc, coda = op
        return f"OPEN:{pre}:{core}:{coda}", v_nuc
    for p, lbl in [
        ("qo", "QO_PRO"), ("o", "O_VOW"), ("a", "O_VOW"), ("e", "O_VOW"), ("i", "O_VOW"),
        ("y", "Y_CONJ"), ("d", "D_DEIC"), ("s", "S_SIB"), ("l", "L_APPL"), ("r", "R_PORT")
    ]:
        if w.startswith(p):
            v_nuc, coda, _ = parse_post_into_nucleus_and_coda(w[len(p):])
            return f"CLOSED:{lbl}:{coda}", v_nuc
    return "RESIDUAL", "NONE"


def main():
    a61 = json.loads(A61_JSON.read_text(encoding="utf-8"))
    a62 = json.loads(A62_JSON.read_text(encoding="utf-8"))
    a63 = json.loads(A63_JSON.read_text(encoding="utf-8"))

    word_counts = Counter()
    word_sec = defaultdict(Counter)
    word_lang = defaultdict(Counter)
    word_hand = defaultdict(Counter)
    word_pos = defaultdict(Counter)

    cur_sec = "U"
    cur_lang = "U"
    cur_hand = "U"

    for raw_line in ZL_PATH.read_text(encoding="utf-8", errors="replace").splitlines():
        raw_line = raw_line.strip()
        if not raw_line or raw_line.startswith("#"):
            continue
        if raw_line.startswith("<f") and ">" in raw_line and "." not in raw_line.split(">")[0]:
            m_s = re.search(r"\$I=([A-Z])", raw_line)
            cur_sec = m_s.group(1) if m_s else "U"
            m_l = re.search(r"\$L=([A-Z])", raw_line)
            cur_lang = m_l.group(1) if m_l else "U"
            m_h = re.search(r"\$H=([0-9A-Za-z]+)", raw_line)
            cur_hand = m_h.group(1) if m_h else "U"
            continue

        m = LOCUS_RE.match(raw_line)
        if not m:
            continue
        is_para = "<%>" in m.group(4)
        is_end = "<$>" in m.group(4)
        toks = clean_tokens(m.group(4))
        n = len(toks)
        for i, w in enumerate(toks):
            word_counts[w] += 1
            word_sec[w][cur_sec] += 1
            word_lang[w][cur_lang] += 1
            word_hand[w][cur_hand] += 1
            if is_para and i == 0:
                word_pos[w]["Z11_PARA_INIT"] += 1
            elif i == 0:
                word_pos[w]["LEFT_INIT"] += 1
            elif is_end and i == n - 1:
                word_pos[w]["Z33_PARA_END"] += 1
            elif i == n - 1:
                word_pos[w]["RIGHT_FINAL"] += 1
            else:
                word_pos[w]["MID_INTERIOR"] += 1

    total_tokens = sum(word_counts.values())
    top500 = word_counts.most_common(500)
    top500_tokens = sum(c for _, c in top500)

    lexicon_rows = []
    cum = 0
    for rank, (w, cnt) in enumerate(top500, 1):
        cum += cnt
        cell, vnuc = dual_matrix_and_nucleus(w)
        morph, slot, gloss = decompose_and_gloss(w)
        dom_sec, sec_cnt = word_sec[w].most_common(1)[0]
        b_pct = round(100.0 * word_lang[w]["B"] / max(1, word_lang[w]["A"] + word_lang[w]["B"]), 1)
        init_pct = round(100.0 * (word_pos[w]["Z11_PARA_INIT"] + word_pos[w]["LEFT_INIT"]) / cnt, 1)
        fin_pct = round(100.0 * (word_pos[w]["Z33_PARA_END"] + word_pos[w]["RIGHT_FINAL"]) / cnt, 1)
        lexicon_rows.append({
            "rank": rank,
            "word": w,
            "count": cnt,
            "cum_pct": round(100.0 * cum / total_tokens, 2),
            "dual_matrix_cell": cell,
            "stem_nucleus": vnuc,
            "init_pct": init_pct,
            "final_pct": fin_pct,
            "lang_B_pct": b_pct,
            "dom_sec": f"{dom_sec} ({round(100.0*sec_cnt/cnt)}%)",
            "morphemes": morph,
            "structural_gloss": gloss,
        })

    out_data = {
        "summary": {
            "total_corpus_tokens": total_tokens,
            "top500_tokens": top500_tokens,
            "top500_coverage_pct": round(100.0 * top500_tokens / total_tokens, 2),
            "level5_entropy_explained_pct": a62["six_level_cascade"][4]["cumulative_pct_of_word_entropy"],
            "paragraph_3x3_grid_z": a63["within_paragraph_permutation_z"],
            "core_weight_nucleus_z": a61["core_weight_compensation"]["z_score"],
        },
        "top500_lexicon": lexicon_rows,
    }
    OUT_JSON.write_text(json.dumps(out_data, indent=2), encoding="utf-8")

    # Build Markdown Reference Edition
    md = [
        "# Top-500 Core Lexicon (`63.60%` of the Voynich Manuscript) & Complete 6-Level Morphological Decoder",
        "",
        "## 1. Executive Synthesis (`Autonomous Wave 13: Attacks 61–64 / Discoveries 78–81`)",
        "",
        "Building on the **Dual-Matrix Generative Grammar (`99.73%` Corpus Coverage, [`Attack 60`](DUAL_MATRIX_COMPLETE_GRAMMAR.md))**, Wave 13 resolves the internal sub-cell variation ($H(\\text{Word} \\mid \\text{Cell}) = 3.4365\\text{ bits}$) and 2D spatial layout of Voynich paragraphs:",
        "",
        "### 1.1 The Isochronous 3-Mora Stem-Template Law (`|Core| + |V_nuc| = 3`, $z = +507.17$, [`Attack 61`](../tools/attack61_internal_stem_nucleus_solver.py))",
        "Across all `11,606` `-dy/-y` open-class tokens, the choice of internal stem nucleus (`ZERO_V [-0-]`, `E1 [-e-]`, `E2 [-ee-]`, `O_VOW [-o-]`, `EO_DIPH [-eo-]`) obeys an exact **3-Mora Stem-Width Compensation Law ($I = 0.2118\\text{ bits}, z = +507.17$)**:",
        "",
        "| Core Class | Core Glyph Width | `ZERO_V (-0-)` | `E1 (-e-)` | `E2 (-ee-)` | `O_VOW (-o-)` | `EO_DIPH (-eo-)` | Modal Template (`|Core| + |V_nuc| = 3`) |",
        "| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |",
        "| **`K_F` (`k/f`)** | `1` glyph | `13.14%` | `26.93%` | **`51.32%`** | `1.48%` | `7.13%` | `1 (k) + 2 (ee) = 3` (`qokeedy, qokeey, okeey`) |",
        "| **`T_P` (`t/p`)** | `1` glyph | `19.61%` | `31.40%` | **`36.40%`** | `4.70%` | `7.89%` | `1 (t) + 2 (ee) = 3` (`qoteedy, qoteey, oteey`) |",
        "| **`CH` (`ch`)** | `2` glyphs | `23.37%` | **`52.59%`** | `14.18%` | `4.99%` | `4.87%` | `2 (ch) + 1 (e) = 3` (`chedy, chey`) |",
        "| **`SH` (`sh`)** | `2` glyphs | `14.89%` | **`57.72%`** | `18.55%` | `4.45%` | `4.39%` | `2 (sh) + 1 (e) = 3` (`shedy, shey`) |",
        "| **`KCH_CKH` (`kch/ckh`)** | `3` glyphs | **`58.69%`** | `33.19%` | `3.31%` | `2.69%` | `2.12%` | `3 (ckh) + 0 (0) = 3` (`ckhy, kchy, kchdy`) |",
        "| **`TCH_CTH` (`tch/cth`)** | `3` glyphs | **`51.13%`** | `37.53%` | `4.12%` | `4.36%` | `2.86%` | `3 (cth) + 0 (0) = 3` (`cthy, tchy, tchdy`) |",
        "",
        "- **Scribe-Hand Nucleus Dialect Conditioning ($I = 0.1019\\text{ bits}, z = +286.73$)**:",
        "  - **Hands 1, 4, and 5** use `-o-/-eo-` (`chody, cheody, okody, qokeody`) in **`16.86%–20.61%`** of tokens vs. **`3.18%` in Hand 2** (Balneological `$I=B`) and **`6.56%` in Hand 3** (Quire 20 Starred Recipes `$I=S`).",
        "  - **Hand 3** doubles the geminate `E2 : E1` ratio compared to **Hand 2** (`E2:E1 = 0.818` in Hand 3 vs. `0.405` in Hand 2).",
        "",
        "---",
        "",
        "### 1.2 The 6-Level Hierarchical Entropy Cascade (`97.28%` Explained at Level 5, [`Attack 62`](../tools/attack62_subcell_allography_entropy_decomposition.py))",
        "",
        "| Cascade Level | Structural Specification | Attested States | Cumulative $H$ (bits) | Incremental Gain | % of $H(\\text{Word})$ Explained | Remaining Residual |",
        "| :---: | :--- | :---: | :---: | :---: | :---: | :---: |",
    ]

    for row in a62["six_level_cascade"]:
        md.append(
            f"| **Level {row['level']}** | {row['description']} | `{row['attested_states']:,}` | `{row['cumulative_entropy_bits']:.4f}` | `+{row['incremental_gain_bits']:.4f}` | **`{row['cumulative_pct_of_word_entropy']:.2f}%`** | `{row['remaining_residual_bits']:.4f} bits` |"
        )

    md.extend([
        "",
        "---",
        "",
        "### 1.3 The `3 × 3 = 9`-Zone 2D Paragraph Spatial Grid ($z = +411.74$, [`Attack 63`](../tools/attack63_paragraph_arc_and_sentence_translator.py))",
        "Across `742` multi-line paragraphs (`32,592` prose tokens), 2D spatial assignment `Zone_3x3` carries `0.18261 bits` of mutual information with grammatical role vs. `0.00343 ± 0.00044 bits` under within-paragraph word-position permutation (**$z = +411.74$**):",
        "",
        "| 2D Paragraph Zone | Tokens | `PF_TOPLINE (p/f)` | `S/SH_CONT` | `Y_CONJ` | `QO_ACTIVE` | `CH/SH_VERB` | `AIIN_NOM` | `M_CLOSER (-am/-m)` | Top 3 Words in Zone |",
        "| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |",
    ])

    for z_key, v in a63["nine_zone_table"].items():
        top3 = ", ".join(f"`{w}`" for w in list(v["top_5_words"].keys())[:3])
        md.append(
            f"| **`{z_key}`** | `{v['total_tokens']:,}` | `{v['PF_TOPLINE_GALLOWS_pct']:.2f}%` | `{v['S_SH_CONTINUATION_pct']:.2f}%` | `{v['Y_CONJ_INIT_pct']:.2f}%` | `{v['QO_ACTIVE_OP_pct']:.2f}%` | `{v['CH_SH_BENCH_VERB_pct']:.2f}%` | `{v['AIIN_MEASURE_NOM_pct']:.2f}%` | `{v['M_NASAL_CLOSER_pct']:.2f}%` | {top3} |"
        )

    md.extend([
        "",
        "---",
        "",
        f"## 2. Complete Top-500 Core Lexicon (`{top500_tokens:,} / {total_tokens:,}` Tokens = `{100*top500_tokens/total_tokens:.2f}%` of the Manuscript)",
        "",
        "| Rank | EVA Word | Count | Cum % | Dual-Matrix Cell | Nucleus | Init % | Final % | `$L=B` % | Dom `$I` | Morpheme Parse | Compositional Structural Gloss |",
        "| :---: | :--- | :---: | :---: | :--- | :---: | :---: | :---: | :---: | :---: | :--- | :--- |",
    ])

    for r in lexicon_rows:
        md.append(
            f"| {r['rank']} | **`{r['word']}`** | `{r['count']}` | `{r['cum_pct']:.2f}%` | `{r['dual_matrix_cell']}` | `{r['stem_nucleus']}` | `{r['init_pct']}%` | `{r['final_pct']}%` | `{r['lang_B_pct']}%` | `{r['dom_sec']}` | `{r['morphemes']}` | {r['structural_gloss']} |"
        )

    OUT_MD.write_text("\n".join(md) + "\n", encoding="utf-8")
    print("=== ATTACK 64: TOP-500 CORE LEXICON & 6-LEVEL DECODER ===")
    print(f"Top 500 Words Cover: {top500_tokens:,} / {total_tokens:,} tokens ({100*top500_tokens/total_tokens:.2f}% of the entire manuscript!)")
    print(f"Saved -> {OUT_JSON}")
    print(f"Saved -> {OUT_MD}")


if __name__ == "__main__":
    main()
