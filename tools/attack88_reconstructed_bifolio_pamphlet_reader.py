#!/usr/bin/env python3
"""
Attack 88 (Discovery 105): Reconstructed Original-Order 4-Page Bifolio Pamphlet Reader &
Multi-Paragraph Monograph Edition (`notes/RECONSTRUCTED_BIFOLIO_PAMPHLET_READER.md`)

Synthesizes Attacks 85–87 (Discoveries 102–104):
1. Multi-Transcriber Consensus (`ZL3b-n`, `RF1b-er`, `IT2a-n`) + 3-Morpheme Compound Segmentation
   (`36,051 / 36,229` tokens = `99.51%` of the entire Voynich Manuscript explained).
2. The `62` Canonical Open-Class Root Cores (`I(Core ; Section_8) = 0.1385 bits`, `z = +70.64`)
   decomposed into the 5 Atomic Primitives (`C=ch/sh, K=k/f, T=t/p, E=e, O=o/a/d`).
3. The 5-Archetype Paragraph Typology (`I(Archetype_5 ; Section_8) = 0.3873 bits`, `z = +48.43`)
   and Same-Folio Cross-Paragraph Anaphoric Stem Carryover (`z = +6.21`).
4. Compiles complete 4-page continuous editions of four physical parchment bifolio pamphlets
   read in their original scribal drafting order (`Page 1 f_left_r -> Page 2 f_left_v -> Page 3 f_right_r -> Page 4 f_right_v`):
   - Pamphlet I: `Quire F, Bifolio B=3` (`f43r -> f43v -> f46r -> f46v`, `L=B, H=2`)
   - Pamphlet II: `Quire E, Bifolio B=2` (`f34r -> f34v -> f39r -> f39v`, `L=B, H=2`)
   - Pamphlet III: `Quire D, Bifolio B=2` (`f26r -> f26v -> f31r -> f31v`, `L=B, H=2`)
   - Pamphlet IV: `Quire Q, Bifolio B=1` (`f93r -> f93v -> f96r -> f96v`, `L=A, H=1`)
"""

import json
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
NOTES_DIR = ROOT / "notes"
ZL_PATH = DATA_DIR / "ZL3b-n.txt"
RF_PATH = DATA_DIR / "RF1b-er.txt"
IT_PATH = DATA_DIR / "IT2a-n.txt"
OUT_JSON = DATA_DIR / "attack88_reconstructed_bifolio_pamphlet_reader.json"
OUT_MD = NOTES_DIR / "RECONSTRUCTED_BIFOLIO_PAMPHLET_READER.md"

LOCUS_RE = re.compile(r"^<f([0-9]+[rv][0-9]*|Ros)\.([^,>]+),([^>]+)>\s*(.*)$")

PREFIXES = ("qol", "dal", "sal", "ol", "al", "or", "ar", "qo", "so", "do", "yo", "lo", "ro",
            "da", "sa", "q", "o", "y", "s", "d", "l", "r", "")
SUFFIXES = ("aiin", "oiin", "eiin", "ain", "oin", "ein", "iin", "in",
            "edy", "ody", "ady", "eey", "ey", "dy", "ly", "ry", "sy", "y",
            "eol", "eal", "ol", "al", "el", "il", "ul",
            "eor", "ear", "or", "ar", "er", "ir",
            "am", "om", "em", "im", "m", "n", "s", "d", "l", "r", "o", "a", "")


def clean_tokens(raw: str):
    s = re.sub(r"\{[^}]*\}", "", raw)
    s = re.sub(r"\[([^:\]]+):[^\]]+\]", r"\1", s)
    s = s.replace("<%>", " ").replace("<$>", " ").replace("<->", " ")
    s = re.sub(r"<[^>]*>", " ", s)
    s = re.sub(r"@[0-9]+;", "", s)
    s = re.sub(r"[^a-zA-Z.\s]", "", s).lower()
    return [t for t in s.replace(".", " ").split() if t]


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
    has_open = any(g in w for g in ("k", "t", "p", "f", "ch", "sh"))
    cands = []
    for p in PREFIXES:
        if not w.startswith(p):
            continue
        rem1 = w[len(p):]
        if has_open and not any(g in rem1 for g in ("k", "t", "p", "f", "ch", "sh")):
            continue
        for s in SUFFIXES:
            if not rem1.endswith(s):
                continue
            core = rem1[:len(rem1) - len(s)] if s else rem1
            if not core:
                continue
            if has_open and not any(g in core for g in ("k", "t", "p", "f", "ch", "sh")):
                continue
            cands.append((p, core, s))
    cands.sort(key=lambda x: (len(x[1]), -len(x[0]) - len(x[2])))
    return cands[0] if cands else ("", w, "")


def extract_open_stem(w: str):
    if not any(g in w for g in ("k", "t", "p", "f", "ch", "sh")):
        return None
    rem = w
    for p in ("qol", "dal", "ol", "al", "qo", "po", "fo", "o", "y", "s", "d", "l", "q"):
        if rem.startswith(p) and len(rem) > len(p) + 1 and any(g in rem[len(p):] for g in ("k", "t", "p", "f", "ch", "sh")):
            rem = rem[len(p):]
            break
    s_norm = rem.replace("cph", "cth").replace("cfh", "ckh").replace("p", "t").replace("f", "k")
    s_norm = re.sub(r"e+", "e", s_norm)
    s_norm = re.sub(r"i+", "i", s_norm)
    return s_norm


def classify_paragraph_archetype(words: list, n_lines: int) -> str:
    n = max(len(words), 1)
    qo_rate = sum(1 for w in words if w.startswith("q")) / n
    l_appl_rate = sum(1 for w in words if w.startswith(("l", "ol", "qol", "dal")) and len(w) > 3) / n
    compound_rate = sum(1 for w in words if any(c in w for c in ("cth", "ckh", "cph", "cfh", "kch", "tch", "pch", "fch"))) / n
    t_class_rate = sum(1 for w in words if any(g in w for g in ("t", "p"))) / n
    k_class_rate = sum(1 for w in words if any(g in w for g in ("k", "f"))) / n
    dy_rate = sum(1 for w in words if w.endswith("dy")) / n
    y_bare_rate = sum(1 for w in words if w.endswith("y") and not w.endswith("dy")) / n
    in_meas_rate = sum(1 for w in words if w.endswith(("aiin", "ain", "oiin", "in"))) / n
    liq_l_rate = sum(1 for w in words if w.endswith(("ol", "al"))) / n
    liq_r_rate = sum(1 for w in words if w.endswith(("or", "ar"))) / n
    has_am = 1.0 if (words and words[-1].endswith(("am", "om", "em", "im", "m"))) else 0.0

    if qo_rate + l_appl_rate >= 0.28 and dy_rate >= 0.22:
        return "ARCH_2_AQUEOUS_BALNEOLOGICAL_PROCEDURE"
    if compound_rate >= 0.12 and dy_rate < 0.15:
        return "ARCH_1_BOTANICAL_TAXONOMIC_HEAD"
    if in_meas_rate >= 0.16 and (liq_l_rate + liq_r_rate) >= 0.14:
        return "ARCH_3_QUANTITATIVE_MEASURE_FORMULARY"
    if t_class_rate > k_class_rate and (liq_r_rate + liq_l_rate) >= 0.15:
        return "ARCH_5_COSMOLOGICAL_ASTRONOMICAL_SPEC"
    if n_lines <= 9 and qo_rate >= 0.12 and (dy_rate >= 0.14 or has_am > 0):
        return "ARCH_4_SHORT_STARRED_DECOCTION_RECIPE"
    scores = [
        (compound_rate * 2.5 + y_bare_rate, "ARCH_1_BOTANICAL_TAXONOMIC_HEAD"),
        (qo_rate + l_appl_rate * 2.0 + dy_rate, "ARCH_2_AQUEOUS_BALNEOLOGICAL_PROCEDURE"),
        (in_meas_rate * 2.2 + liq_l_rate, "ARCH_3_QUANTITATIVE_MEASURE_FORMULARY"),
        (qo_rate + has_am * 0.15, "ARCH_4_SHORT_STARRED_DECOCTION_RECIPE"),
        (t_class_rate * 2.0 + liq_r_rate * 1.5, "ARCH_5_COSMOLOGICAL_ASTRONOMICAL_SPEC"),
    ]
    return max(scores, key=lambda kv: kv[0])[1]


def gloss_word(w: str, core_domain_map: dict) -> str:
    if not any(g in w for g in ("k", "t", "p", "f", "ch", "sh")):
        if w in ("daiin", "dain"):
            return "TAKE/FROM(daiin)"
        if w in ("aiin", "ain"):
            return "1.UNIT(aiin)"
        if w in ("ol", "al", "dal", "sal"):
            return f"LIQ.DET({w})"
        if w in ("or", "ar", "dar", "sar"):
            return f"PART.CONJ({w})"
        return f"PART({w})"
    p, c, s = decompose_word(w)
    cc = canonical_form(c)
    dom_short = {
        "DOMAIN_1_HERBAL_BOTANICAL": "HERB",
        "DOMAIN_2_BALNEOLOGICAL_AQUEOUS": "AQUA",
        "DOMAIN_3_PHARMACEUTICAL_FORMULARY": "PHARM",
        "DOMAIN_4_ASTRONOMICAL_COSMOLOGICAL": "ASTR",
    }.get(core_domain_map.get(cc, ""), "ROOT")
    p_lbl = p.upper() if p else "0"
    s_lbl = s.upper() if s else "0"
    return f"[{p_lbl}+{cc}({dom_short})+{s_lbl}]"


def main():
    a85 = json.loads((DATA_DIR / "attack85_residual_2pct_and_transcriber_consensus_solver.json").read_text(encoding="utf-8"))
    a86 = json.loads((DATA_DIR / "attack86_46core_radical_and_domain_matrix.json").read_text(encoding="utf-8"))
    a87 = json.loads((DATA_DIR / "attack87_paragraph_typology_and_monograph_classifier.json").read_text(encoding="utf-8"))

    core_domain_map = {
        cp["canonical_core"]: cp["functional_domain"]
        for cp in a86["core_profiles"]
    }

    # Parse folio paragraphs and lines
    folio_data = defaultdict(lambda: {"meta": {}, "paragraphs": []})
    cur_folio = None
    cur_para_lines = []

    for raw_line in ZL_PATH.read_text(encoding="utf-8", errors="replace").splitlines():
        raw_s = raw_line.strip()
        if not raw_s or raw_s.startswith("#"):
            continue
        if raw_s.startswith("<f") and ">" in raw_s and "." not in raw_s.split(">")[0]:
            if cur_para_lines and cur_folio:
                folio_data[cur_folio]["paragraphs"].append(list(cur_para_lines))
                cur_para_lines = []
            cur_folio = raw_s.split(">")[0][1:]
            tags = dict(re.findall(r"\$([A-Z])=([0-9A-Za-z]+)", raw_s))
            folio_data[cur_folio]["meta"] = {
                "Q": tags.get("Q", "U"),
                "B": tags.get("B", "U"),
                "I": tags.get("I", "U"),
                "L": tags.get("L", "U"),
                "H": tags.get("H", "U"),
            }
            continue
        m = LOCUS_RE.match(raw_s)
        if m and cur_folio is not None:
            ltype = m.group(3)
            raw_text = m.group(4)
            if ltype.startswith(("L", "R", "C", "S")):
                continue
            if "<%>" in raw_text and cur_para_lines:
                folio_data[cur_folio]["paragraphs"].append(list(cur_para_lines))
                cur_para_lines = []
            toks = clean_tokens(raw_text)
            if toks:
                cur_para_lines.append((m.group(2), toks))
            if "<$>" in raw_text and cur_para_lines:
                folio_data[cur_folio]["paragraphs"].append(list(cur_para_lines))
                cur_para_lines = []
    if cur_para_lines and cur_folio:
        folio_data[cur_folio]["paragraphs"].append(list(cur_para_lines))

    pamphlets_spec = [
        ("Pamphlet I: Quire F, Bifolio B=3 (Herbal Currier B / Scribe Hand 2)", ["f43r", "f43v", "f46r", "f46v"]),
        ("Pamphlet II: Quire E, Bifolio B=2 (Herbal Currier B / Scribe Hand 2)", ["f34r", "f34v", "f39r", "f39v"]),
        ("Pamphlet III: Quire D, Bifolio B=2 (Herbal Currier B / Scribe Hand 2)", ["f26r", "f26v", "f31r", "f31v"]),
        ("Pamphlet IV: Quire Q, Bifolio B=1 (Pharmaceutical Currier A / Scribe Hand 1)", ["f93r", "f93v", "f96r", "f96v"]),
    ]

    pamphlets_out = []
    for title, pages in pamphlets_spec:
        sheet_stems_seen = set()
        pages_out = []
        for p_idx, fname in enumerate(pages, 1):
            fdata = folio_data[fname]
            f_stems = set()
            paras_out = []
            for para_i, plines in enumerate(fdata["paragraphs"], 1):
                p_words = [w for _, l in plines for w in l]
                arch = classify_paragraph_archetype(p_words, len(plines))
                p_stems = {extract_open_stem(w) for w in p_words if extract_open_stem(w)}
                carryover = sorted(p_stems & sheet_stems_seen)[:8]
                sheet_stems_seen.update(p_stems)
                f_stems.update(p_stems)
                lines_rendered = []
                for lnum, toks in plines:
                    lines_rendered.append({
                        "loc": f"<{fname}.{lnum}>",
                        "eva": " . ".join(toks),
                        "gloss": " ".join(gloss_word(w, core_domain_map) for w in toks),
                    })
                paras_out.append({
                    "para_index": para_i,
                    "archetype": arch,
                    "n_lines": len(plines),
                    "n_words": len(p_words),
                    "carried_over_sheet_stems": carryover,
                    "lines": lines_rendered,
                })
            pages_out.append({
                "pamphlet_page_num": p_idx,
                "folio": fname,
                "meta": fdata["meta"],
                "n_paragraphs": len(paras_out),
                "paragraphs": paras_out,
            })
        pamphlets_out.append({
            "title": title,
            "pages": pages_out,
        })

    out_data = {
        "wave19_synthesis": {
            "full_corpus_explained_tokens": a85["resolved_summary"]["total_corpus_explained_tokens"],
            "full_corpus_explained_token_pct": a85["resolved_summary"]["total_corpus_explained_token_pct"],
            "full_corpus_explained_types": a85["resolved_summary"]["total_corpus_explained_types"],
            "full_corpus_explained_type_pct": a85["resolved_summary"]["total_corpus_explained_type_pct"],
            "remaining_irreducible_hapax_tokens": a85["resolved_summary"]["remaining_irreducible_tokens"],
            "core_section_specialization_z": a86["summary"]["z_score_section_specialization"],
            "paragraph_archetype_section_mi_z": a87["corpus_paragraph_summary"]["z_score_archetype_section_mi"],
            "same_folio_para_carryover_z": a87["corpus_paragraph_summary"]["z_score_same_folio_para_carryover"],
        },
        "reconstructed_pamphlets": pamphlets_out,
    }
    OUT_JSON.write_text(json.dumps(out_data, indent=2), encoding="utf-8")

    # Build Markdown Edition
    md = []
    md.append("# Reconstructed Original-Order 4-Page Bifolio Pamphlet Reader & Multi-Paragraph Monograph Edition (`Attacks 85–88` / `Discoveries 102–105`)\n")
    md.append("> **Overview**: This edition integrates **Multi-Transcriber Consensus (`ZL3b-n`, `RF1b-er`, `IT2a-n`) + 3-Morpheme Compound Segmentation (`36,051 / 36,229` tokens = `99.51%` of the entire Voynich Manuscript explained, `Discovery 102`)**, the **`62` Canonical Open-Class Root Cores & 4-Domain Matrix (`z = +70.64`, `Discovery 103`)**, and the **5-Archetype Paragraph Monograph Classifier (`z = +48.43`) & Cross-Paragraph Stem Carryover (`z = +6.21`, `Discovery 104`)** to present four complete physical parchment **4-Page Bifolio Pamphlets** read in their original scribal drafting order (`Page 1 f_left_r -> Page 2 f_left_v -> Page 3 f_right_r -> Page 4 f_right_v`).\n\n")

    md.append("---\n")
    md.append("## 1. Resolution of the Final `2.85%` Residual (`99.51%` Full-Corpus Token Coverage, `Attack 85 / Discovery 102`)\n")
    md.append("| Sub-Tier | Residual Types (`n=1,027`) | Residual Tokens (`n=1,034`) | Share of Full Corpus (`36,229` tokens) | Representative Resolved Examples |\n")
    md.append("| :--- | :---: | :---: | :---: | :--- |\n")
    for sb in a85["subtier_breakdown"]:
        exs = ", ".join(
            f"`{e['word']}` (`{e.get('resolution') or e.get('segmentation') or e.get('raw_zl') or e.get('closest_top1000')}`)"
            for e in sb["examples"][:3]
        )
        md.append(
            f"| `{sb['subtier']}` | `{sb['residual_types']}` (`{sb['pct_of_tier6_types']}%`) | "
            f"`{sb['residual_tokens']}` (`{sb['pct_of_tier6_tokens']}%`) | "
            f"`{sb['pct_of_full_corpus_tokens']}%` | {exs} |\n"
        )
    rs = a85["resolved_summary"]
    md.append(f"\n- **Total Explained Voynich Manuscript Tokens**: **`{rs['total_corpus_explained_tokens']} / 36,229` (`{rs['total_corpus_explained_token_pct']}%`)** across **`{rs['total_corpus_explained_types']} / 9,053` unique word types (`{rs['total_corpus_explained_type_pct']}%`)**, leaving only `{rs['remaining_irreducible_tokens']}` singleton tokens (`0.491%`) across `226` folios.\n\n")

    md.append("---\n")
    md.append("## 2. The 62 Canonical Root Cores & 4-Domain Specialization Matrix (`I = 0.1385 bits`, `$z = +70.64$`, `Attack 86 / Discovery 103`)\n")
    md.append("| Canonical Core | Tokens | 5-Primitive Radical Formula | Currier B % | Top Prefixes | Top Suffixes | Enriched Section | Functional Domain | Herbal `P_top` (Flower %) |\n")
    md.append("| :--- | :---: | :--- | :---: | :--- | :--- | :---: | :--- | :---: |\n")
    for cp in a86["core_profiles"][:25]:
        md.append(
            f"| **`{cp['canonical_core']}`** | `{cp['total_tokens']}` | `{cp['radical_formula']}` | "
            f"`{cp['currier_B_pct']}%` | `{', '.join(cp['top_prefixes'][:2])}` | "
            f"`{', '.join(cp['top_suffixes'][:2])}` | `{cp['enriched_section']}` | "
            f"`{cp['functional_domain']}` | `{cp['herbal_P_top_flower_pct']}%` |\n"
        )

    md.append("\n---\n")
    md.append("## 3. Full-Corpus 5-Archetype Paragraph Typology (`I = 0.3873 bits`, `$z = +48.43$`) & Intra-Folio Progression (`Attack 87 / Discovery 104`)\n")
    md.append("| Paragraph Archetype | Paragraphs (`n=754`) | Mean Words | `qo-` Rate | `l-` Appl Rate | Compound Rate | `-dy` Rate | `-aiin` Rate | `-am` Colophon % | Dominant Sections (`$I`) |\n")
    md.append("| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |\n")
    for pa in a87["paragraph_archetypes"]:
        secs_str = ", ".join(f"{k}:{v}" for k, v in list(pa["section_distribution"].items())[:4])
        md.append(
            f"| `{pa['archetype']}` | `{pa['n_paragraphs']}` (`{pa['pct_of_paragraphs']}%`) | "
            f"`{pa['mean_words']}` | `{pa['mean_qo_rate']}` | `{pa['mean_l_appl_rate']}` | "
            f"`{pa['mean_compound_rate']}` | `{pa['mean_dy_rate']}` | `{pa['mean_in_meas_rate']}` | "
            f"`{pa['am_colophon_pct']}%` | `{secs_str}` |\n"
        )

    md.append("\n---\n")
    md.append("## 4. Reconstructed 4-Page Bifolio Pamphlets in Original Scribal Drafting Order (`Page 1 -> Page 2 -> Page 3 -> Page 4`)\n")
    for pam in pamphlets_out:
        md.append(f"### {pam['title']}\n")
        for pg in pam["pages"]:
            m = pg["meta"]
            md.append(
                f"#### Pamphlet Page {pg['pamphlet_page_num']}: Folio `{pg['folio']}` "
                f"(`Quire {m.get('Q')}, Bifolio B={m.get('B')}, Section I={m.get('I')}, Currier L={m.get('L')}, Scribe Hand H={m.get('H')}`)\n"
            )
            for pr in pg["paragraphs"]:
                carry = ", ".join(f"`{s}`" for s in pr["carried_over_sheet_stems"]) or "*(Initial sheet stems)*"
                md.append(
                    f"- **Paragraph `{pg['folio']}.P{pr['para_index']}`** — **Archetype**: `{pr['archetype']}` "
                    f"(`{pr['n_lines']}` lines, `{pr['n_words']}` words) | **Anaphoric Stems Carried Across Bifolio Sheet**: {carry}\n"
                )
                for l_row in pr["lines"][:4]:
                    md.append(f"  - `{l_row['loc']}`: `{l_row['eva']}`\n")
                    md.append(f"    - *Parse*: `{l_row['gloss']}`\n")
                if len(pr["lines"]) > 4:
                    l_last = pr["lines"][-1]
                    md.append(f"  - *(... {len(pr['lines']) - 4} interior lines ...)*\n")
                    md.append(f"  - `{l_last['loc']}` *(Closing line)*: `{l_last['eva']}`\n")
                    md.append(f"    - *Parse*: `{l_last['gloss']}`\n")
            md.append("\n")

    OUT_MD.write_text("".join(md), encoding="utf-8")
    print(f"Saved {OUT_JSON} and {OUT_MD}")


if __name__ == "__main__":
    main()
