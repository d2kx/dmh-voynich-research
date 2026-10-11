"""
Phase 11 (Avenue D): Functional Role Parser & Full-Page Interlinear Structural Gloss Generator.

Generates word-by-word and line-by-line structural interlinear glosses for representative
folios across Herbal (f5r, f17r), Biological (f82v, f84r), Pharmaceutical (f99v),
and Starred Recipes (f106v), as well as global functional-role coverage statistics.

Outputs:
- data/interlinear_glosses.json
- notes/INTERLINEAR_GLOSSES.md
"""

import json
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ZL_PATH = ROOT / "data" / "ZL3b-n.txt"
INDEX_PATH = ROOT / "data" / "folio_index.json"
JSON_OUT = ROOT / "data" / "interlinear_glosses.json"
MD_OUT = ROOT / "notes" / "INTERLINEAR_GLOSSES.md"


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


LABEL_TYPE_NAMES = {
    "Lf": "PLANT",
    "Lr": "ROOT",
    "Lc": "JAR",
    "Ln": "NYMPH",
    "Lt": "TUBE",
    "Ls": "STAR",
    "Lz": "ZODIAC",
    "La": "ASTRO",
    "L0": "MAP/DIAG",
    "Lx": "CORNER",
}


def classify_functional_role(
    w: str,
    cw: str,
    idx_in_line: int,
    line_len: int,
    is_par_start_line: bool,
    is_after_break: bool,
    label_index: dict,
    global_canon_counts: Counter,
    same_folio: str,
) -> dict:
    pos_flags = []
    if is_par_start_line and idx_in_line == 0:
        pos_flags.append("PAR_START")
    elif idx_in_line == 0:
        pos_flags.append("LINE_START")
    if is_after_break:
        pos_flags.append("POST_DRAWING_RESET")
    if idx_in_line == line_len - 1 and line_len > 1:
        pos_flags.append("LINE_END")

    ortho_notes = []
    if is_par_start_line and ("p" in w or "f" in w):
        ortho_notes.append("TOP_LINE_GALLOWS(p/f->t/k)")
    if (idx_in_line == 0 or is_after_break) and w.startswith("y") and len(w) > 1:
        ortho_notes.append("INITIAL_Y_PROCLITIC")
    if idx_in_line == line_len - 1 and len(w) > 2 and w.endswith("m"):
        ortho_notes.append("RIGHT_MARGIN_M_CLOSER(-m->-r)")
    if w.startswith("qo") and len(w) > 2:
        ortho_notes.append(f"Q_PROCLITIC(q+{w[1:]})")

    # Primary syntactic/functional category
    if w in ("daiin", "dain", "aiin", "ain", "saiin"):
        role = "DET/CLOSER"
    elif w in ("ol", "al", "or", "ar", "dar", "dal", "dol", "sol", "sal", "sar", "chol", "shol"):
        role = "LINK/PREP" if len(w) <= 3 else "FRAME_MOD"
    elif w.startswith(("ch", "sh", "lch", "lsh", "dch", "dsh")):
        if w.endswith(("dy", "edy", "ey", "eey", "y")):
            role = "VERB/STATE_MOD(-dy/-y)"
        else:
            role = "BENCH_STEM"
    elif w.startswith("qo"):
        role = "Q_NOMINAL(q+oX)"
    elif w.startswith(("ok", "ot", "op", "of", "ol", "or", "od")):
        role = "BARE_NOMINAL(oX)"
    elif w.startswith(("k", "t", "p", "f", "yk", "yt", "yp", "yf", "cth", "ckh", "cph", "cfh")):
        role = "GALLOWS_HEAD"
    elif len(w) > 2 and w.endswith("m"):
        role = "CLAUSE_CLOSER(-m)"
    else:
        role = "STEM"

    # Check if canonical stem matches any @L figure label (same-folio or rare cross-folio)
    label_hits = label_index.get(cw, [])
    same_folio_labels = [h for h in label_hits if h["folio"] == same_folio]
    rare_cross_labels = [h for h in label_hits if h["folio"] != same_folio and global_canon_counts[cw] <= 15]

    crib_tag = None
    if same_folio_labels:
        h = same_folio_labels[0]
        ltype = LABEL_TYPE_NAMES.get(h["cat"], "LABEL")
        crib_tag = f"SAME-PAGE {ltype} [{h['loc']} '{h['word']}', MS_cnt={global_canon_counts[cw]}]"
    elif rare_cross_labels:
        h = rare_cross_labels[0]
        ltype = LABEL_TYPE_NAMES.get(h["cat"], "LABEL")
        crib_tag = f"XREF {ltype} [{h['loc']} '{h['word']}', MS_cnt={global_canon_counts[cw]}]"

    return {
        "word": w,
        "canon": cw,
        "global_count": global_canon_counts[cw],
        "role": role,
        "pos_flags": pos_flags,
        "ortho_notes": ortho_notes,
        "crib_tag": crib_tag,
    }


def main():
    folio_meta = json.loads(INDEX_PATH.read_text(encoding="utf-8"))["folios"]

    parsed_lines = []
    for raw_line in ZL_PATH.read_text(encoding="utf-8", errors="ignore").splitlines():
        if raw_line.startswith("#") or not raw_line.strip():
            continue
        if re.match(r"^<(f[0-9]+[rv][0-9]*|fRos)>\s*<!", raw_line):
            continue
        m_l = re.match(r"^<([^>]+)>\s+(.*)$", raw_line)
        if not m_l:
            continue
        header, body = m_l.group(1), m_l.group(2)
        loc_part = header.split(",")[0] if "," in header else header
        loc_type = header.split(",")[1] if "," in header else ""
        folio = loc_part.split(".")[0]

        is_par_start = "<%>" in body
        is_par_end = "<$>" in body
        # Replace inline <! ...> or <top word> comments before splitting on <->
        body_no_comments = re.sub(r"<![^>]*>", " ", body)
        body_no_comments = re.sub(r"<(?!%|/|\$|->)[^>]*>", " ", body_no_comments)
        chunks = body_no_comments.split("<->")
        words = []
        after_break_indices = set()
        for ci, ch in enumerate(chunks):
            ch_clean = re.sub(r"<[^>]*>", " ", ch)
            toks = [clean_word(t) for t in re.split(r"[.,\s]+", ch_clean) if clean_word(t)]
            if ci > 0 and toks:
                after_break_indices.add(len(words))
            words.extend(toks)
        if not words:
            continue
        parsed_lines.append({
            "folio": folio,
            "loc": loc_part,
            "loc_type": loc_type,
            "is_par_start": is_par_start,
            "is_par_end": is_par_end,
            "after_break_indices": sorted(after_break_indices),
            "words": words,
            "canon_words": [canonicalize(w) for w in words],
        })

    global_canon_counts = Counter()
    label_index = defaultdict(list)
    for l in parsed_lines:
        lt = l["loc_type"]
        cat = re.sub(r"^[@+*&/~]", "", lt) if "L" in lt else ""
        for w, cw in zip(l["words"], l["canon_words"]):
            if cw:
                global_canon_counts[cw] += 1
                if cat and len(cw) >= 3:
                    label_index[cw].append({
                        "folio": l["folio"],
                        "loc": l["loc"],
                        "cat": cat,
                        "word": w,
                    })

    # Global role & label-stem coverage across all prose tokens
    global_role_counts = Counter()
    prose_tokens_total = 0
    prose_tokens_matching_any_label_stem = 0
    prose_tokens_with_ortho_rule = 0

    for l in parsed_lines:
        if "L" in l["loc_type"]:
            continue
        breaks = set(l["after_break_indices"])
        n = len(l["words"])
        for idx, (w, cw) in enumerate(zip(l["words"], l["canon_words"])):
            prose_tokens_total += 1
            info = classify_functional_role(
                w, cw, idx, n, l["is_par_start"], idx in breaks, label_index, global_canon_counts, l["folio"]
            )
            global_role_counts[info["role"]] += 1
            if cw in label_index:
                prose_tokens_matching_any_label_stem += 1
            if info["ortho_notes"] or info["pos_flags"]:
                prose_tokens_with_ortho_rule += 1

    # Generate full interlinear glosses for target sample folios
    target_folios = ["f5r", "f17r", "f82v", "f84r", "f99v", "f106v"]
    folio_glosses = {}
    for tf in target_folios:
        flines = [l for l in parsed_lines if l["folio"] == tf]
        glossed_lines = []
        for l in flines:
            is_label = "L" in l["loc_type"]
            breaks = set(l["after_break_indices"])
            n = len(l["words"])
            tokens_info = []
            for idx, (w, cw) in enumerate(zip(l["words"], l["canon_words"])):
                tinfo = classify_functional_role(
                    w, cw, idx, n, l["is_par_start"], idx in breaks, label_index, global_canon_counts, tf
                )
                tokens_info.append(tinfo)
            glossed_lines.append({
                "loc": l["loc"],
                "loc_type": l["loc_type"],
                "is_label": is_label,
                "is_par_start": l["is_par_start"],
                "is_par_end": l["is_par_end"],
                "after_break_indices": l["after_break_indices"],
                "tokens": tokens_info,
            })
        meta = folio_meta.get(tf, {})
        folio_glosses[tf] = {
            "folio": tf,
            "section": meta.get("section", "?"),
            "currier_lang": meta.get("currier_lang", "?"),
            "hand": meta.get("hand", "?"),
            "pdf_page": meta.get("pdf_page", "?"),
            "lines": glossed_lines,
        }

    output_data = {
        "global_coverage": {
            "total_prose_tokens": prose_tokens_total,
            "tokens_matching_attested_label_stem": prose_tokens_matching_any_label_stem,
            "pct_matching_attested_label_stem": round(100.0 * prose_tokens_matching_any_label_stem / prose_tokens_total, 2),
            "tokens_with_positional_or_orthographic_rule": prose_tokens_with_ortho_rule,
            "pct_with_positional_or_orthographic_rule": round(100.0 * prose_tokens_with_ortho_rule / prose_tokens_total, 2),
            "functional_role_distribution": {
                k: {"count": v, "pct": round(100.0 * v / prose_tokens_total, 2)}
                for k, v in global_role_counts.most_common()
            },
        },
        "sample_folio_glosses": folio_glosses,
    }

    JSON_OUT.write_text(json.dumps(output_data, indent=2, ensure_ascii=False), encoding="utf-8")

    # Build human-readable Markdown Interlinear Gloss document (`notes/INTERLINEAR_GLOSSES.md`)
    MD_OUT.parent.mkdir(parents=True, exist_ok=True)
    md = []
    md.append("# Full-Page Structural Interlinear Glosses of Representative Voynich Folios\n")
    md.append(
        "Generated automatically by [`tools/generate_interlinear_gloss.py`](../tools/generate_interlinear_gloss.py) "
        "(`Phase 11 / Avenue D`). Every token is decomposed using our 4-Rule Canonical Normalization, "
        "positional/drawing-break state machine, and cross-referenced against all `1,033` figure labels (`@L`) across the manuscript.\n"
    )
    md.append("## 1. Global Corpus Functional Role & Label-Stem Coverage (`37,800` Prose Tokens)\n")
    md.append(
        f"- **Prose tokens whose canonical stem is directly attested as an isolated Figure Label (`@L`)**: "
        f"**`{prose_tokens_matching_any_label_stem:,} / {prose_tokens_total:,}` (`{output_data['global_coverage']['pct_matching_attested_label_stem']}%`)**\n"
    )
    md.append(
        f"- **Prose tokens governed by an active Positional / Allographic / Proclitic Rule**: "
        f"**`{prose_tokens_with_ortho_rule:,} / {prose_tokens_total:,}` (`{output_data['global_coverage']['pct_with_positional_or_orthographic_rule']}%`)**\n\n"
    )
    md.append("| Functional Role Tag | Token Count | Share of Prose (`%`) | Structural Definition |\n")
    md.append("| :--- | :---: | :---: | :--- |\n")
    role_defs = {
        "VERB/STATE_MOD(-dy/-y)": "Bench (`ch-/sh-`) stem inflected with `-dy`/`-y` verbal/participial suffix",
        "BARE_NOMINAL(oX)": "Bare `o-` nominal stem (`ok-`, `ot-`, `ol-`, `or-`)—the citation form used in `@L` labels",
        "Q_NOMINAL(q+oX)": "Prose-only `q-` proclitic attached to an `oX` nominal stem (`qoX = q + oX`)",
        "LINK/PREP": "Short liquid/vowel relator (`ol`, `al`, `or`, `ar`, `dar`, `dal`, `dol`, `sol`)",
        "GALLOWS_HEAD": "Gallows-initial (`k/t/p/f`, `cth/ckh`, `yk/yt`) clause/topic opener",
        "STEM": "Other vocalic or `d-/s-/r-/l-` lexical stem",
        "BENCH_STEM": "Bench (`ch-/sh-`) stem with liquid/nasal suffix (`cheol`, `chor`, `cheor`, `shedal`)",
        "DET/CLOSER": "High-frequency demonstrative / clause-final particle (`daiin`, `aiin`, `dain`, `saiin`)",
        "FRAME_MOD": "Uninflected bench modifier (`chol`, `shol`), frequently paired with `daiin` or `qoX`",
        "CLAUSE_CLOSER(-m)": "Right-margin `-m` line/clause terminator (`-am`, `-om`, `-aim`)",
    }
    for k, v in output_data["global_coverage"]["functional_role_distribution"].items():
        md.append(f"| **`{k}`** | `{v['count']:,}` | `{v['pct']}%` | {role_defs.get(k, '')} |\n")

    md.append("\n---\n")
    for tf in target_folios:
        fg = folio_glosses[tf]
        md.append(
            f"\n## Folio `{tf}` (Section `$I={fg['section']}`, Currier `$L={fg['currier_lang']}`, "
            f"Scribe `$H={fg['hand']}`, PDF `p{fg['pdf_page']}`)\n"
        )
        # First summarize any figure labels on this folio
        label_lines = [l for l in fg["lines"] if l["is_label"]]
        prose_lines = [l for l in fg["lines"] if not l["is_label"]]
        if label_lines:
            md.append(f"### Figure Labels on `{tf}` (`{len(label_lines)}` label loci)\n")
            label_strs = []
            for ll in label_lines:
                for t in ll["tokens"]:
                    tag = f" $\\to$ **{t['crib_tag']}**" if t["crib_tag"] else ""
                    label_strs.append(f"`<{ll['loc']},{ll['loc_type']}>` **{t['word']}** (`canon={t['canon']}`, cnt={t['global_count']}){tag}")
            md.append("- " + "\n- ".join(label_strs) + "\n\n")

        md.append(f"### Running Text Interlinear Gloss (`{tf}`, `{len(prose_lines)}` lines)\n")
        for pl in prose_lines:
            hdr_flags = []
            if pl["is_par_start"]:
                hdr_flags.append("`<%> PAR_OPEN`")
            if pl["after_break_indices"]:
                hdr_flags.append(f"`<-> DRAWING_INTRUSION at word {pl['after_break_indices']}`")
            if pl["is_par_end"]:
                hdr_flags.append("`<$> PAR_END`")
            flag_str = " (" + ", ".join(hdr_flags) + ")" if hdr_flags else ""
            md.append(f"#### Line `<{pl['loc']}>`{flag_str}\n")
            raw_line_str = " . ".join(
                (f"<-> **{t['word']}**" if idx in pl["after_break_indices"] else f"**{t['word']}**")
                for idx, t in enumerate(pl["tokens"])
            )
            gloss_parts = []
            for idx, t in enumerate(pl["tokens"]):
                brk = "`<->` " if idx in pl["after_break_indices"] else ""
                ortho = f" *[{', '.join(t['ortho_notes'])}]*" if t["ortho_notes"] else ""
                crib = f" **<{t['crib_tag']}>**" if t["crib_tag"] else ""
                gloss_parts.append(f"{brk}`[{t['role']}:{t['canon']}]`{ortho}{crib}")
            md.append(f"- **Voynich**: {raw_line_str}\n")
            md.append(f"- **Gloss**: {' · '.join(gloss_parts)}\n\n")

    MD_OUT.write_text("".join(md), encoding="utf-8")

    print("=== GLOBAL PROSE COVERAGE SUMMARY ===")
    for k, v in output_data["global_coverage"].items():
        if k != "functional_role_distribution":
            print(f"  {k:44s}: {v}")
    print("\n=== FUNCTIONAL ROLE DISTRIBUTION ===")
    for k, v in output_data["global_coverage"]["functional_role_distribution"].items():
        print(f"  {k:26s}: {v['count']:6d} ({v['pct']:5.2f}%)")
    print(f"\nWrote {JSON_OUT} and {MD_OUT}")


if __name__ == "__main__":
    main()
