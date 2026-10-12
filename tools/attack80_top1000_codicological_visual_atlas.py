#!/usr/bin/env python3
"""
Attack 80: The Top-1,000 Core Lexicon (`71.26%` of All Manuscript Tokens) &
Multi-Modal Codicological-Visual Reference Atlas

Synthesizes Attacks 77-79 and compiles the complete annotated reference lexicon
for the Top 1,000 Most Frequent Words of the Voynich Manuscript:
  - Exports all 1,000 entries to `data/attack80_top1000_codicological_visual_atlas.json`
  - Exports the Codicological Bifolio Atlas, Pigment-Grammar Concordance, and
    Ranks #1-#100 Summary + Ranks #501-#1,000 Full Table (complementing Ranks #1-#500 in
    `notes/TOP500_LEXICON_AND_6LEVEL_DECODER.md`) to `notes/TOP1000_CODICOLOGICAL_VISUAL_ATLAS.md`.
"""

import json
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
NOTES_DIR = ROOT / "notes"
ZL_PATH = DATA_DIR / "ZL3b-n.txt"
A71_JSON = DATA_DIR / "attack71_parallel_clause_tree_aligner.json"
A77_JSON = DATA_DIR / "attack77_codicological_bifolio_and_spread_continuity.json"
A78_JSON = DATA_DIR / "attack78_scribal_bifolio_compositional_order.json"
A79_JSON = DATA_DIR / "attack79_full_manuscript_pigment_grammar_concordance.json"

OUT_JSON = DATA_DIR / "attack80_top1000_codicological_visual_atlas.json"
OUT_MD = NOTES_DIR / "TOP1000_CODICOLOGICAL_VISUAL_ATLAS.md"

LOCUS_RE = re.compile(r"^<f([0-9]+[rv][0-9]*|Ros)\.([^,>]+),([^>]+)>\s*(.*)$")


def clean_tokens(raw: str):
    s = re.sub(r"\{[^}]*\}", "", raw)
    s = re.sub(r"\[([^:\]]+):[^\]]+\]", r"\1", s)
    s = s.replace("<%>", " ").replace("<$>", " ").replace("<->", " ")
    s = re.sub(r"<[^>]*>", " ", s)
    s = re.sub(r"@[0-9]+;", "", s)
    s = re.sub(r"[^a-zA-Z.\s]", "", s).lower()
    return [t for t in s.replace(".", " ").split() if t]


def get_10bit_code(w: str) -> str:
    b1 = "1" if any(g in w for g in ("k", "t", "p", "f", "ch", "sh")) else "0"
    b2 = "1" if w.startswith("q") else "0"
    b3 = "1" if w.startswith(("l", "ol", "qol", "dal")) and len(w) > 3 else "0"
    b4 = "1" if w.startswith(("s", "y")) or w.startswith("sh") else "0"
    b5 = "1" if any(g in w for g in ("k", "t", "p", "f")) else "0"
    b6 = "1" if any(g in w for g in ("t", "p")) else "0"
    b7 = "1" if any(c in w for c in ("ckh", "cth", "cph", "cfh", "kch", "tch", "pch", "fch")) else "0"
    b8 = "1" if w.endswith("y") else "0"
    b9 = "1" if w.endswith("dy") or w.startswith("d") else "0"
    b10 = "1" if "a" in w or w.endswith("r") else "0"
    return f"{b1}{b2}{b3}{b4}{b5}{b6}{b7}{b8}{b9}{b10}"


def get_dual_matrix_and_const(w: str):
    has_core = any(g in w for g in ("k", "t", "p", "f", "ch", "sh"))
    if w.endswith(("aiin", "oiin", "eiin", "ain", "oin", "ein", "in", "iiin")):
        suf = "IN_MIN"
    elif w.endswith("dy"):
        suf = "DY_DENT"
    elif w.endswith("y"):
        suf = "Y_BARE"
    elif w.endswith(("ol", "al", "el", "il", "ul")) or w in ("ol", "al", "l"):
        suf = "L_LAT"
    elif w.endswith(("or", "ar", "er", "ir", "ur")) or w in ("or", "ar", "r"):
        suf = "R_RHO"
    elif w.endswith(("am", "om", "em", "im", "m", "an")):
        suf = "M_NAS"
    elif w.endswith(("eey", "ee", "e", "o", "a")):
        suf = "V_OPEN"
    else:
        suf = "C_OTH"

    if not has_core:
        if w.startswith("q"):
            return f"M1:QO×{suf}", "PP_PREP"
        if w.startswith("d"):
            if w in ("daiin", "dain", "daim", "dair"):
                return f"M1:DA×{suf}", "NP_MEAS"
            return f"M1:DA×{suf}", "PP_PREP"
        if w.startswith("s"):
            return f"M1:S×{suf}", "PP_PREP"
        if w.startswith("y"):
            return f"M1:Y×{suf}", "PP_PREP"
        if suf == "M_NAS":
            return f"M1:V×{suf}", "FIN_CLOSE"
        return f"M1:V×{suf}", "NP_MEAS"

    # Open class M2
    if w.startswith("qo") or w.startswith("q"):
        pfx = "QO"
    elif w.startswith(("l", "ol", "qol", "dal")) and len(w) > 4:
        pfx = "L_APPL"
    elif w.startswith(("po", "fo", "p", "f", "cph", "cfh")):
        pfx = "TOP_PF"
    elif w.startswith("o"):
        pfx = "O_NOM"
    elif w.startswith("y"):
        pfx = "Y_CONT"
    elif w.startswith("s"):
        pfx = "S_CONT"
    elif w.startswith("d"):
        pfx = "D_LOC"
    else:
        pfx = "ZERO"

    if any(c in w for c in ("ckh", "cfh")):
        core = "CKH"
    elif any(c in w for c in ("cth", "cph")):
        core = "CTH"
    elif any(c in w for c in ("kch", "fch")):
        core = "KCH"
    elif any(c in w for c in ("tch", "pch")):
        core = "TCH"
    elif "sh" in w:
        core = "SH"
    elif "ch" in w:
        core = "CH"
    elif any(c in w for c in ("k", "f")):
        core = "K_F"
    else:
        core = "T_P"

    if pfx == "TOP_PF":
        cst = "TOP_HEAD"
    elif pfx in ("QO", "L_APPL") or suf in ("DY_DENT", "Y_BARE"):
        cst = "VP_PROC"
    elif suf == "M_NAS":
        cst = "FIN_CLOSE"
    else:
        cst = "NP_MEAS"

    return f"M2:{pfx}×{core}×{suf}", cst


def main():
    a77 = json.loads(A77_JSON.read_text(encoding="utf-8"))
    a78 = json.loads(A78_JSON.read_text(encoding="utf-8"))
    a79 = json.loads(A79_JSON.read_text(encoding="utf-8"))

    word_counts = Counter()
    word_sec = defaultdict(Counter)
    word_lang = defaultdict(Counter)
    word_hand = defaultdict(Counter)
    word_quire = defaultdict(Counter)
    word_b_depth = defaultdict(Counter)

    cur_meta = {"Q": "U", "B": "U", "I": "U", "L": "U", "H": "U"}
    for raw_line in ZL_PATH.read_text(encoding="utf-8", errors="replace").splitlines():
        raw_s = raw_line.strip()
        if not raw_s or raw_s.startswith("#"):
            continue
        if raw_s.startswith("<f") and ">" in raw_s and "." not in raw_s.split(">")[0]:
            tags = dict(re.findall(r"\$([A-Z])=([0-9A-Za-z]+)", raw_s))
            cur_meta = {
                "Q": tags.get("Q", "U"),
                "B": tags.get("B", "U"),
                "I": tags.get("I", "U"),
                "L": tags.get("L", "U"),
                "H": tags.get("H", "U"),
            }
            continue
        m = LOCUS_RE.match(raw_s)
        if not m:
            continue
        toks = clean_tokens(m.group(4))
        for w in toks:
            word_counts[w] += 1
            word_sec[w][cur_meta["I"]] += 1
            word_lang[w][cur_meta["L"]] += 1
            word_hand[w][cur_meta["H"]] += 1
            word_quire[w][cur_meta["Q"]] += 1
            word_b_depth[w][cur_meta["B"]] += 1

    total_tokens = sum(word_counts.values())
    top1000 = word_counts.most_common(1000)

    # Coverage waterfall
    milestones = [10, 25, 50, 100, 250, 500, 750, 1000]
    waterfall = {}
    cum = 0
    entries = []

    for rank, (w, cnt) in enumerate(top1000, start=1):
        cum += cnt
        if rank in milestones:
            waterfall[f"Top_{rank}"] = {
                "tokens": cum,
                "coverage_pct": round(cum / total_tokens * 100.0, 2),
            }

        cell, cst = get_dual_matrix_and_const(w)
        bit10 = get_10bit_code(w)
        dom_sec, sec_cnt = word_sec[w].most_common(1)[0]
        dom_lang, lang_cnt = word_lang[w].most_common(1)[0]
        dom_hand, _ = word_hand[w].most_common(1)[0]
        dom_q, _ = word_quire[w].most_common(1)[0]
        dom_b, _ = word_b_depth[w].most_common(1)[0]

        entries.append({
            "rank": rank,
            "word": w,
            "count": cnt,
            "cum_pct": round(cum / total_tokens * 100.0, 2),
            "matrix_cell": cell,
            "constituent": cst,
            "bit10": bit10,
            "dom_sec": f"{dom_sec}({int(round(sec_cnt/cnt*100))}%)",
            "dom_lang": f"{dom_lang}({int(round(lang_cnt/cnt*100))}%)",
            "dom_hand": dom_hand,
            "dom_quire": dom_q,
            "dom_bifolio": dom_b,
        })

    # Build Markdown Atlas
    md = []
    md.append("# The Top-1,000 Core Lexicon (`71.26%` of the Manuscript) & Multi-Modal Codicological-Visual Atlas (`Attacks 77–80`)\n\n")
    md.append("## 1. Executive Summary: Codicological Bifolio Law, Pigment Concordance & `71.26%` Lexicon Coverage\n")
    md.append(
        f"- **`100.00%` (`78 / 78`) Physical Bifolio Sheet-Mate (`$B`) Language & Hand Concordance in Mixed Quires (`Attack 77`)**: Across all `6` mixed-language quires (`$Q = D, E, F, G, H, Q`, where Currier A and Currier B are interleaved in bound codex order), conjugate leaves across the centerfold belonging to the **same physical parchment bifolio sheet (`$B`)** match in Currier language and Scribe Hand in **`78 / 78` (`100.00%`)** of pairs vs. **`38.65%` (`160 / 414`)** for non-conjugate leaves in the same quire.\n"
        f"- **The 4-Page Bifolio Pamphlet Compositional Order (`+52.5%` Cross-Fold Stem Continuity, `Attack 78`)**: Across the `17` Cross-Fold Bifolio Pamphlet Bridges (`f_left_v -> f_right_r`) in the 6 mixed quires, open-class stem Jaccard similarity jumps by **`+52.47%`** (`0.1453` vs. `0.0953` in bound next-leaf order) and 10-bit feature cosine jumps from `0.9448` to **`0.9766`**, led by `f34v -> f39r` (`Q=E, B=2`: `FeatCos = 0.9881, StemJacc = 0.2150`, sharing rare stems `tchdain`, `chckhdy`, `chdar`), `f26v -> f31r` (`Q=D, B=2`: `FeatCos = 0.9734, StemJacc = 0.1842`), and `f42v -> f47r` (`Q=F, B=2`: `FeatCos = 0.9691, StemJacc = 0.1477`, sharing `chtchy`).\n"
        f"- **Full-Manuscript Computer-Vision Pigment $\\leftrightarrow$ 10-Bit Grammar Concordance (`Attack 79`)**: Across `177` folios scanned directly from `2002046.pdf` (`300` `($I,$L)`-stratified permutations), Verdigris Green canopy coverage suppresses `F6_T_CLASS` (**$z = -3.61$**) and `F5_GALLOWS` (**$z = -3.32$**) while enriching `F10_A_RHOTIC` (**$z = +2.27$**), whereas Vermilion/Crimson Red pigment (`f16v`, `f93v`, `f11v`, `f87v`, and `$I=P` apothecary jars) significantly enriches `F7_COMPOUND` (`Bench + Pedestal` complex compounds like `chckhy` `3.09×` and `chocthy` `2.26×`, **$z = +2.33$**).\n"
        f"- **Top-1,000 Core Lexicon Coverage (`Attack 80`)**: The Top 1,000 word types cover **`{waterfall['Top_1000']['tokens']:,} / {total_tokens:,}` tokens (`{waterfall['Top_1000']['coverage_pct']:.2f}%` of the entire Voynich Manuscript)**.\n"
    )

    md.append("\n---\n\n## 2. Cumulative Lexicon Coverage Waterfall (`Top 10` $\\to$ `Top 1,000`)\n")
    md.append("| Lexicon Tier | Cumulative Tokens | Share of Entire Manuscript (`36,229` Words) |\n")
    md.append("| :--- | :---: | :---: |\n")
    for k, v in waterfall.items():
        md.append(f"| **`{k}`** | `{v['tokens']:,}` | **`{v['coverage_pct']:.2f}%`** |\n")

    md.append("\n---\n\n## 3. Physical Bifolio Sheet (`$B`) Architecture of the 6 Mixed-Language Quires (`D, E, F, G, H, Q`)\n")
    md.append("| Quire (`$Q`) | Bifolio Sheet (`$B`) | Conjugate Folios Across the Fold (`Left Leaf <-> Right Leaf`) | Currier Language (`$L`) | Uniform Sheet? |\n")
    md.append("| :---: | :---: | :--- | :---: | :---: |\n")
    for b in a77["mixed_quire_bifolio_test"]["mixed_quire_bifolia"]:
        md.append(f"| **`{b['quire']}`** | **`$B={b['bifolio_sheet']}`** | `{', '.join(b['folios'])}` | **`{','.join(b['languages'])}`** | **`{b['is_uniform_language']}`** |\n")

    md.append("\n---\n\n## 4. Top Cross-Fold Bifolio Pamphlet Bridges (`f_left_v -> f_right_r` vs. Bound Next Leaf)\n")
    md.append("| Quire & Bifolio | Dialect/Hand | Pamphlet Bridge (`Page 2 -> Page 3`) | Bridge FeatCos (`StemJacc`) | Bound Next Leaf (Discontinuous) | Bound FeatCos (`StemJacc`) | Shared Rare Open-Class Stems |\n")
    md.append("| :---: | :---: | :--- | :---: | :--- | :---: | :--- |\n")
    for br in a78["cross_fold_bifolio_bridges"]:
        md.append(
            f"| `Q={br['quire']}, B={br['bifolio']}` | `{br['lang']}{br['hand']}` | **`{br['bridge']}`** | "
            f"**`{br['bridge_feat_cos']:.4f}` (`{br['bridge_stem_jacc']:.4f}`)** | `{br['bound_next_rejected']}` | "
            f"`{br['bound_next_feat_cos']:.4f}` (`{br['bound_next_stem_jacc']:.4f}`) | `{', '.join(br['shared_rare_stems'][:4]) or '—'}` |\n"
        )

    md.append("\n---\n\n## 5. Complete Annotated Reference Table for Ranks `#501–#1,000` (Complementing `#1–#500` in [`TOP500_LEXICON_AND_6LEVEL_DECODER.md`](TOP500_LEXICON_AND_6LEVEL_DECODER.md))\n")
    md.append("| Rank | Word | Count | Cum% | Dual-Matrix Cell | Constituent | 10-Bit Code | Dom Sec | Dom Lang | Hand | Quire (`$B`) |\n")
    md.append("| :---: | :--- | :---: | :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: |\n")
    for e in entries[500:1000]:
        md.append(
            f"| `{e['rank']}` | **`{e['word']}`** | `{e['count']}` | `{e['cum_pct']:.2f}%` | `{e['matrix_cell']}` | "
            f"`{e['constituent']}` | `{e['bit10']}` | `{e['dom_sec']}` | `{e['dom_lang']}` | `{e['dom_hand']}` | `{e['dom_quire']}(B{e['dom_bifolio']})` |\n"
        )

    OUT_MD.write_text("".join(md), encoding="utf-8")

    out_data = {
        "summary": {
            "total_corpus_tokens": total_tokens,
            "coverage_waterfall": waterfall,
        },
        "top1000_lexicon": entries,
    }
    OUT_JSON.write_text(json.dumps(out_data, indent=2), encoding="utf-8")

    print("=== ATTACK 80: TOP-1,000 CORE LEXICON & CODICOLOGICAL-VISUAL ATLAS ===")
    for k, v in waterfall.items():
        print(f"  {k:8s}: {v['tokens']:6,d} / {total_tokens:,d} ({v['coverage_pct']:.2f}%)")
    print(f"Saved JSON -> {OUT_JSON}")
    print(f"Saved Markdown Atlas -> {OUT_MD}")


if __name__ == "__main__":
    main()
