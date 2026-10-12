#!/usr/bin/env python3
"""
Attack 76: Complete Discourse-Anaphoric & Multi-Step Procedural Recipe Interpreter
(Synthesizing Attacks 73-75 into a Full Paragraph-Level Topic-Tracking,
Moraic-Harmony, and Drawing-Bridge Interpreter)

Outputs:
- data/attack76_discourse_procedural_interpreter.json
- notes/DISCOURSE_PROCEDURAL_INTERPRETER.md
"""

import json
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
NOTES_DIR = ROOT / "notes"
ZL_PATH = DATA_DIR / "ZL3b-n.txt"
A73_JSON = DATA_DIR / "attack73_paragraph_anaphora_and_topic_persistence.json"
A74_JSON = DATA_DIR / "attack74_minim_and_loop_quantifier_solver.json"
A75_JSON = DATA_DIR / "attack75_visual_layout_and_intrusion_grammar.json"

OUT_JSON = DATA_DIR / "attack76_discourse_procedural_interpreter.json"
OUT_MD = NOTES_DIR / "DISCOURSE_PROCEDURAL_INTERPRETER.md"

LOCUS_RE = re.compile(r"^<f([0-9]+[rv][0-9]*|Ros)\.([^,>]+),([^>]+)>\s*(.*)$")


def clean_segment(seg: str):
    s = re.sub(r"\{[^}]*\}", "", seg)
    s = re.sub(r"\[([^:\]]+):[^\]]+\]", r"\1", s)
    s = s.replace("<%>", " ").replace("<$>", " ")
    s = re.sub(r"<[^>]*>", " ", s)
    s = re.sub(r"@[0-9]+;", "", s)
    s = re.sub(r"[^a-zA-Z.\s]", "", s).lower()
    return [t for t in s.replace(".", " ").split() if t]


def extract_prefix_and_stem(w: str):
    if not any(g in w for g in ("k", "t", "p", "f", "ch", "sh")):
        return None
    pfx = "PFX_ZERO"
    rem = w
    if rem.startswith(("qol", "ol", "dal", "al")) and len(rem) > 4:
        for p in ("qol", "dal", "ol", "al"):
            if rem.startswith(p) and any(g in rem[len(p):] for g in ("k", "t", "p", "f", "ch", "sh")):
                pfx = "PFX_L_APPL"
                rem = rem[len(p):]
                break
    elif rem.startswith("l") and len(rem) > 3 and any(g in rem[1:] for g in ("k", "t", "p", "f", "ch", "sh")):
        pfx = "PFX_L_APPL"
        rem = rem[1:]
    elif rem.startswith("qo") and len(rem) > 3:
        pfx = "PFX_QO_ACT"
        rem = rem[2:]
    elif rem.startswith("q") and len(rem) > 2:
        pfx = "PFX_QO_ACT"
        rem = rem[1:]
    elif rem.startswith(("po", "fo", "p", "f", "cph", "cfh")):
        pfx = "PFX_TOP_PF"
    elif rem.startswith("o") and len(rem) > 2 and any(g in rem[1:] for g in ("k", "t", "p", "f", "ch", "sh")):
        pfx = "PFX_O_NOM"
        rem = rem[1:]
    elif rem.startswith(("y", "s", "d")) and len(rem) > 2 and any(g in rem[1:] for g in ("k", "t", "p", "f", "ch", "sh")):
        pfx = f"PFX_{rem[0].upper()}_CONT"
        rem = rem[1:]
        if rem.startswith("o") and len(rem) > 2 and any(g in rem[1:] for g in ("k", "t", "p", "f", "ch", "sh")):
            rem = rem[1:]

    s_norm = rem.replace("cph", "cth").replace("cfh", "ckh").replace("p", "t").replace("f", "k")
    s_norm = re.sub(r"e+", "e", s_norm)
    s_norm = re.sub(r"i+", "i", s_norm)
    for end in ("aiin", "oiin", "ain", "oin", "edy", "ody", "dy", "ey", "oy", "y", "ol", "or", "al", "ar", "am", "om"):
        if s_norm.endswith(end) and len(s_norm) - len(end) >= 2:
            s_norm = s_norm[:-len(end)]
            break
    return pfx, s_norm


def annotate_paragraph(p: dict):
    """
    Annotates every line in paragraph `p` with:
    - Anaphoric Stem Links (`@M1[stem]` on first mention vs `@ANAPH<-L{k}[stem: pfx_shift]` on re-mentions)
    - Moraic Harmony Links (`~EE_HARM`, `~II_HARM`)
    - Drawing Intrusion Bridges (`<->`)
    """
    first_seen = {}
    multi_line_stems = defaultdict(set)
    for l_idx, ln in enumerate(p["lines"]):
        for w in ln["words"]:
            res = extract_prefix_and_stem(w)
            if res:
                multi_line_stems[res[1]].add(l_idx)

    shared_stems = {st for st, lset in multi_line_stems.items() if len(lset) >= 2}

    annotated_lines = []
    anaphora_hits = 0
    harmony_hits = 0
    intrusion_hits = 0

    for l_idx, ln in enumerate(p["lines"]):
        seg_strs = []
        prev_e = 0
        prev_i = 0
        for s_idx, sg in enumerate(ln["seg_words"]):
            if s_idx > 0:
                seg_strs.append("**`<-> [DRAWING]`**")
                intrusion_hits += 1
            for w in sg:
                tags = []
                res = extract_prefix_and_stem(w)
                if res and res[1] in shared_stems:
                    pfx, st = res
                    if st not in first_seen:
                        first_seen[st] = (l_idx + 1, w, pfx)
                        tags.append(f"TOPIC:{st}")
                    else:
                        orig_l, orig_w, orig_pfx = first_seen[st]
                        if orig_l < l_idx + 1:
                            anaphora_hits += 1
                            if pfx != orig_pfx:
                                tags.append(f"ANAPH<-L{orig_l}:{orig_w}[{orig_pfx}->{pfx}]")
                            else:
                                tags.append(f"ANAPH<-L{orig_l}:{orig_w}[={st}]")

                e_runs = [len(m.group(0)) for m in re.finditer(r"e+", w)]
                i_runs = [len(m.group(0)) for m in re.finditer(r"i+", w)]
                cur_e = max(e_runs) if e_runs else 0
                cur_i = max(i_runs) if i_runs else 0
                if cur_e >= 2 and prev_e >= 2:
                    tags.append("EE_HARM")
                    harmony_hits += 1
                if cur_i >= 2 and prev_i >= 2:
                    tags.append("II_HARM")
                    harmony_hits += 1
                prev_e = cur_e
                prev_i = cur_i

                if tags:
                    seg_strs.append(f"`{w}`({','.join(tags)})")
                else:
                    seg_strs.append(f"`{w}`")

        annotated_lines.append({
            "lnum": ln["lnum"],
            "raw_str": " <-> ".join(" . ".join(sg) for sg in ln["seg_words"]),
            "annot_str": " ".join(seg_strs),
        })

    return {
        "shared_stems": sorted(shared_stems),
        "anaphora_hits": anaphora_hits,
        "harmony_hits": harmony_hits,
        "intrusion_hits": intrusion_hits,
        "annotated_lines": annotated_lines,
    }


def main():
    with open(A73_JSON, "r", encoding="utf-8") as f:
        a73 = json.load(f)
    with open(A74_JSON, "r", encoding="utf-8") as f:
        a74 = json.load(f)
    with open(A75_JSON, "r", encoding="utf-8") as f:
        a75 = json.load(f)

    paragraphs = []
    cur_para = None
    cur_sec = "U"
    cur_lang = "U"
    cur_hand = "U"
    folio_para_counter = Counter()

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
            cur_para = None
            continue

        m = LOCUS_RE.match(raw_s)
        if not m:
            continue
        folio, lnum, ltype, raw_txt = f"f{m.group(1)}", m.group(2), m.group(3), m.group(4)
        if not ltype.startswith(("@P", "+P", "*P")):
            continue
        is_start = "<%>" in raw_txt or cur_para is None
        is_end = "<$>" in raw_txt
        raw_segments = raw_txt.split("<->")
        seg_words = [clean_segment(sg) for sg in raw_segments]
        seg_words = [sg for sg in seg_words if sg]
        all_words = [w for sg in seg_words for w in sg]
        if not all_words:
            continue

        if is_start:
            folio_para_counter[folio] += 1
            cur_para = {
                "folio": folio,
                "para_num": folio_para_counter[folio],
                "sec": cur_sec,
                "lang": cur_lang,
                "hand": cur_hand,
                "lines": [],
            }
            paragraphs.append(cur_para)

        cur_para["lines"].append({
            "lnum": lnum,
            "words": all_words,
            "seg_words": seg_words,
        })
        if is_end:
            cur_para = None

    multi_paras = [p for p in paragraphs if len(p["lines"]) >= 2]
    paras_with_anaphora = 0
    total_anaphora_links = 0
    total_harmony_links = 0

    annotated_by_key = {}
    for p in multi_paras:
        ann = annotate_paragraph(p)
        if ann["anaphora_hits"] > 0:
            paras_with_anaphora += 1
        total_anaphora_links += ann["anaphora_hits"]
        total_harmony_links += ann["harmony_hits"]
        annotated_by_key[(p["folio"], p["para_num"])] = (p, ann)

    anaphora_para_pct = round(paras_with_anaphora / len(multi_paras) * 100, 2)

    target_walkthroughs = [
        ("f2r", 1, "Herbal Monograph (`f2r` P1) — Mid-Constituent `<->` Stem Bridges (`s <-> shor`, `y <-> chor`)"),
        ("f20v", 1, "Herbal Monograph (`f20v` P1) — Topic Persistence & Phrase Univerbation (`chodaiin` vs `shol . daiin`)"),
        ("f20v", 2, "Herbal Monograph (`f20v` P2) — Root-Zone Paragraph & `shocthy . sho . cthy` Juxtaposition"),
        ("f34r", 1, "Herbal Monograph (`f34r` P1) — Double-Core Compounds & Multi-Line Anaphoric Chains"),
        ("f78r", 1, "Balneological Folio (`f78r` P1) — `qokedy/qokeedy` Moraic Harmony & `PFX_L_APPL` Re-Mentions"),
        ("f75r", 1, "Balneological Folio (`f75r` P1) — Dense `qo-` Active Operator & Applicative `l-` Chains"),
        ("f88r", 2, "Pharmaceutical Recipe (`f88r` P2) — Sub-Row `okol -> qoekol -> qockhol` Anaphoric Progression"),
        ("f99r", 1, "Pharmaceutical Recipe (`f99r` P1) — Jar-to-Recipe Topic Tracking"),
        ("f107r", 4, "Starred Recipe (`f107r` P4) — Pisces `otaram -> otaral -> otalar` Sequential Progression"),
        ("f113r", 1, "Starred Recipe (`f113r` P1) — Water-Trigon Double `.13` Zodiac Crib Recipe"),
    ]

    md = []
    md.append("# The Voynich Discourse-Anaphoric & Multi-Step Procedural Interpreter (`Attacks 73–76`)\n\n")
    md.append("## 1. Executive Summary: Paragraph-Level Topic Persistence, Moraic Harmony & Visual Layout Grammar\n")
    md.append(
        f"- **Intra-Paragraph Topic & Word Persistence (`Attack 73`)**: Across `{len(multi_paras):,}` multi-line paragraphs (`{a73['summary']['intra_paragraph_line_pairs']:,}` intra-paragraph line pairs), **`{anaphora_para_pct:.2f}%` (`{paras_with_anaphora} / {len(multi_paras)}`)** of all multi-line paragraphs track at least one recurring open-class topic stem across multiple lines (`{total_anaphora_links:,}` cross-line anaphoric re-mentions). Lines in the same paragraph share open-class stems at **`{a73['summary']['stem_overlap_rate_pct']:.2f}%`** vs. `{a73['summary']['null_stem_overlap_mean_pct']:.2f}%` section+language-stratified null (**$z = +{a73['summary']['stem_persistence_z']}$**), and share exact open-class words at **`{a73['summary']['exact_open_word_overlap_rate_pct']:.2f}%`** vs. `{a73['summary']['null_word_overlap_mean_pct']:.2f}%` null (**$z = +{a73['summary']['exact_word_persistence_z']}$**).\n"
        f"- **The Anaphoric Prefix-Shift Trajectory (`First Mention M_1 -> Re-Mention M_2+`, `Attack 73`)**: First mentions (`M_1`) concentrate Top-Gallows `PFX_TOP_PF` (`2.14%` vs. `0.66%` in `M_2+`, `3.24×` `M_1` enrichment), `PFX_S_CONT` (`2.54%` vs. `1.64%`), and nominal `PFX_O_NOM` (`18.87%` vs. `17.42%`), whereas subsequent re-mentions (`M_2+`) surge in **Applicative/Resultative `PFX_L_APPL` (`l-/ol-/qol-`: `7.37%` $\\to$ `10.29%`, `+39.7%` lift)** and **Active `PFX_QO_ACT` (`qo-`: `20.83%` $\\to$ `22.83%`, `+9.6%` lift)**.\n"
        f"- **Cross-Word Moraic Harmony & Line-Final Loop Compression (`Attack 74`)**: Holding the exact consonantal skeleton (`w_skel`) strictly fixed, adjacent words exhibit significant **Cross-Word Moraic Harmony** in both `i`-minims (`-aiin` after `-aiin` = **`68.30%`** vs. **`50.46%`** after `-ain`, `+17.84%`, skeleton-stratified **$z = +4.39$**) and `e`-loops (`-ee-` after `-ee-` = **`51.78%`** vs. **`39.65%`** after `-e-`, `+12.13%`, **$z = +5.30$**), while geminate `-ee-` compresses monotonically across the line (`W_INIT = 52.42%` $\\to$ `W_INTERIOR = 39.77%` $\\to$ `W_FINAL = 26.69%`, **$z = -3.98$**).\n"
        f"- **Drawing-Intrusion (`<->`) Constituent Bridging & Herbal Vertical Zones (`Attack 75`)**: Across `732` `<->` drawing intrusions, **`15.57%` (`114 / 732`)** split a single 2-word constituent right across the painted plant stem (`Role-Transition Cosine = 0.7583`, e.g., `s <-> shor` and `y <-> chor` on `f2r`), while on `87` multi-paragraph Herbal folios, `T_CLASS` (`qoty, otol`) and `shy/cheey` enrich in **`P_top` (Flower/Leaf Zone)** whereas `K_CLASS` (`okal, kchy, okedy, qokchy`) and `-ol/-al` liquids (`25.88%` $\\to$ `30.02%`) enrich in **`P_bot` (Root Zone)**.\n"
    )

    md.append("\n---\n\n## 2. Anaphoric Prefix-Shift Trajectory (`First Mention M_1` vs. `Subsequent Re-Mention M_2+`)\n")
    md.append("| Prefix Class | First Mention (`M_1`) | Subsequent Re-Mention (`M_2+`) | `M_2+ / M_1` Ratio | Discourse Function |\n")
    md.append("| :--- | :---: | :---: | :---: | :--- |\n")
    role_desc = {
        "PFX_TOP_PF": "Paragraph/Topic-Initial Gallows (`p-/f-`)",
        "PFX_S_CONT": "Sectional/Sibilant Opener (`s-`)",
        "PFX_O_NOM": "Nominal / Ingredient Citation (`o-`)",
        "PFX_Y_CONT": "Clausal Conjunction / Continuation (`y-`)",
        "PFX_ZERO": "Unprefixed Core Stem (`ch-/sh-/k-/t-`)",
        "PFX_D_CONT": "Deictic / Ablative Prefix (`d-`)",
        "PFX_QO_ACT": "Active Procedural Operator (`qo-`)",
        "PFX_L_APPL": "Anaphoric Resultative / Applicative (`l-/ol-/qol-`)",
    }
    for k, v in a73["anaphoric_prefix_shift"].items():
        md.append(
            f"| **`{k}`** | `{v['first_mention_pct']:.2f}%` (`{v['first_mention_count']}`) | "
            f"`{v['remention_pct']:.2f}%` (`{v['remention_count']}`) | **`{v['remention_to_first_ratio']:.3f}×`** | {role_desc.get(k, '')} |\n"
        )

    md.append("\n---\n\n## 3. Skeleton-Stratified Moraic Harmony & Horizontal Loop Compression (`Attack 74`)\n")
    md.append("| System | Polymorphic Tokens (`Skeletons`) | `W_INIT` Multi% | `W_INTERIOR` Multi% | `W_FINAL` Multi% (`z`) | After Single (`1`) | After Multi (`2+`) | Cross-Word Harmony Lift (`z`) |\n")
    md.append("| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |\n")
    for st in (a74["minim_i_system"], a74["loop_e_system"]):
        wz = st["word_zone_multi_pct"]
        ch = st["cross_word_harmony"]
        md.append(
            f"| **`{st['system']}`** | `{st['polymorphic_tokens']:,}` (`{st['polymorphic_skeletons']}`) | "
            f"`{wz['W_INIT']:.2f}%` | `{wz['W_INTERIOR']:.2f}%` | **`{wz['W_FINAL']:.2f}%` ($z = {st['w_final_permutation_z']:+.2f}$)** | "
            f"`{ch['after_single_pct']:.2f}%` | **`{ch['after_multi_pct']:.2f}%`** | **`{ch['diff_pct']:+.2f}%` ($z = {ch['harmony_permutation_z']:+.2f}$)** |\n"
        )

    md.append("\n---\n\n## 4. Drawing-Intrusion (`<->`) Boundary Profiles vs. True Line Margins (`Attack 75`)\n")
    md.append("| Locus Position | Tokens | Mean Length | `-am/-om/-m` Closer% | `-y/-dy` Verbal% | `y-/s-` Opener% | `o-` Nominal% | `qo-` Active% |\n")
    md.append("| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |\n")
    for label, key in [
        ("True Line-Initial (`w_1`)", "true_line_initial"),
        ("Post-Drawing (`w_post` after `<->`)", "post_drawing_w_post"),
        ("True Clause-Interior (`w_2..n-1`)", "true_interior"),
        ("Pre-Drawing (`w_pre` before `<->`)", "pre_drawing_w_pre"),
        ("True Line-Final (`w_n`)", "true_line_final"),
    ]:
        pr = a75["position_profiles"][key]
        md.append(
            f"| **{label}** | `{pr['count']:,}` | `{pr['mean_len']:.3f}` | `{pr['fin_m_pct']:.2f}%` | "
            f"`{pr['fin_y_dy_pct']:.2f}%` | `{pr['init_y_s_pct']:.2f}%` | `{pr['init_o_pct']:.2f}%` | `{pr['init_qo_pct']:.2f}%` |\n"
        )

    md.append("\n---\n\n## 5. Ten Complete Step-by-Step Discourse-Anaphoric & Procedural Paragraph Walkthroughs\n")
    md.append("Annotation tags attached to words:\n")
    md.append("- `(TOPIC:stem)`: First introduction (`M_1`) of a multi-line recurring open-class stem in the paragraph.\n")
    md.append("- `(ANAPH<-Lk:word[PFX1->PFX2])`: Subsequent re-mention (`M_2+`) on a later line referring back to the antecedent introduced on Line `k`, showing the exact prefix shift (e.g., `[PFX_O_NOM->PFX_QO_ACT]` or `[PFX_ZERO->PFX_L_APPL]`).\n")
    md.append("- `(EE_HARM)` / `(II_HARM)`: Cross-word moraic harmony (`-ee-` after `-ee-`, or `-aiin` after `-aiin`).\n")
    md.append("- **`<-> [DRAWING]`**: Physical drawing intrusion bridged across the painted plant stem or figure.\n")

    for fol, pnum, title in target_walkthroughs:
        entry = annotated_by_key.get((fol, pnum))
        if not entry:
            continue
        p, ann = entry
        md.append(f"\n### {title}\n")
        md.append(
            f"- **Metadata**: Folio `{p['folio']}` Paragraph `{p['para_num']}` | Section `$I={p['sec']}` | Currier `$L={p['lang']}` | Hand `$H={p['hand']}` | "
            f"**Recurring Topic Stems**: `{', '.join(ann['shared_stems'])}` (`{ann['anaphora_hits']}` cross-line anaphoric links, `{ann['harmony_hits']}` moraic harmony links, `{ann['intrusion_hits']}` drawing bridges)\n"
        )
        for idx, aln in enumerate(ann["annotated_lines"]):
            md.append(f"  - **Step/Line {idx+1} (`<{p['folio']}.{aln['lnum']}>`)**: {aln['annot_str']}\n")

    OUT_MD.write_text("".join(md), encoding="utf-8")

    out_data = {
        "summary": {
            "multi_line_paragraphs_parsed": len(multi_paras),
            "paragraphs_with_cross_line_anaphora": paras_with_anaphora,
            "paragraphs_with_anaphora_pct": anaphora_para_pct,
            "total_cross_line_anaphoric_links": total_anaphora_links,
            "total_adjacent_moraic_harmony_links": total_harmony_links,
        }
    }
    OUT_JSON.write_text(json.dumps(out_data, indent=2), encoding="utf-8")

    print("=== ATTACK 76: DISCOURSE-ANAPHORIC & PROCEDURAL INTERPRETER ===")
    print(f"Multi-Line Paragraphs Parsed: {len(multi_paras):,} | With Cross-Line Anaphora: {paras_with_anaphora:,} ({anaphora_para_pct:.2f}%)")
    print(f"Total Cross-Line Anaphoric Links: {total_anaphora_links:,} | Total Moraic Harmony Links: {total_harmony_links:,}")
    print(f"Saved JSON -> {OUT_JSON}")
    print(f"Saved Markdown Edition -> {OUT_MD}")


if __name__ == "__main__":
    main()
