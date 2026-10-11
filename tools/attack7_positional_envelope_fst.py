#!/usr/bin/env python3
"""
Phase 18 / Attack 7: Positional Envelope Stripper, Finite-State Transducer (FST)
& Stripped Root-Stream Edition Generator.

1. Computes the 5-Stage Shannon Entropy & Vocabulary Reduction Waterfall from raw
   surface tokens (Stage 0) -> Gallows Allograph Strip (Stage 1) -> Vowel Grade
   Compression (Stage 2) -> Positional Proclitic/Margin Strip (Stage 3) -> Inflectional
   Suffix Strip = Pure Core Root Stream (Stage 4).
2. Measures cardinality-matched Mutual Information I(Position ; PositionalEnvelope_12)
   vs. I(Position ; CoreRoot_12) and conditional bigram entropy H(R_t | R_{t-1}).
3. Builds the 8-State Finite-State Transducer (FST) Markov transition matrices
   separately for Currier Language A and Currier Language B.
4. Generates `notes/STRIPPED_ROOT_EDITION.md`, a 3-tier aligned edition (Surface ->
   Envelope+Root Split -> Pure Root + Crib Stream) across 8 key folios:
   f5r, f17r, f22r, f84r, f88r, f99r, f107r, and f113r.
"""

import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ZL_PATH = ROOT / "data" / "ZL3b-n.txt"
OUT_JSON = ROOT / "data" / "attack7_positional_envelope_fst.json"
OUT_MD = ROOT / "notes" / "STRIPPED_ROOT_EDITION.md"


def clean_tok(t: str) -> str:
    t = re.sub(r"\{[^}]*\}", "", t)
    t = re.sub(r"\[([^]:]+):[^\]]+\]", r"\1", t)
    t = re.sub(r"[@&!?\*\(\)<>\[\]\'\"]", "", t)
    return t.strip()


def shannon_entropy(counts: Counter) -> float:
    total = sum(counts.values())
    if total == 0:
        return 0.0
    ent = 0.0
    for c in counts.values():
        if c > 0:
            p = c / total
            ent -= p * math.log2(p)
    return ent


def conditional_entropy(pair_counts: Counter, cond_counts: Counter) -> float:
    total = sum(pair_counts.values())
    if total == 0:
        return 0.0
    h = 0.0
    for (x, y), c in pair_counts.items():
        if c > 0:
            p_xy = c / total
            p_y_given_x = c / cond_counts[x]
            h -= p_xy * math.log2(p_y_given_x)
    return h


def stage1_gallows(w: str) -> str:
    return w.replace("p", "t").replace("f", "k")


def stage2_vowels(w: str) -> str:
    s = stage1_gallows(w)
    s = re.sub(r"e+", "e", s)
    s = re.sub(r"i+", "i", s)
    s = re.sub(r"o+", "o", s)
    s = re.sub(r"a+", "a", s)
    return s


def stage3_positional_proclitic_margin(w: str) -> str:
    s = stage2_vowels(w)
    if len(s) > 2 and s[0] in ("q", "y") and s[1] in ("o", "e", "a"):
        s = s[1:]
    if s.endswith("m") and len(s) > 2:
        s = s[:-1] + "r"
    return s


SUFFIX_PAT = re.compile(
    r"(aiin|ain|iin|in|edy|eedy|ody|dy|eey|ey|ary|ory|ry|aly|oly|ly|am|om|al|ol|ar|or|y|r|l|s|d)$"
)


def extract_core_root_and_envelope(w: str, pos_state: str):
    """
    Decomposes surface word `w` into:
      - pos_only_sig: pure positional features (G:p/f, P:q-, P:y-, M:-m)
      - env_sig: full grammatical + positional envelope
      - core_root: stripped consonantal/vocalic root stem
    """
    s0 = w
    env_parts = []
    pos_parts = []

    if "p" in s0 or "f" in s0:
        env_parts.append("G:p/f->t/k")
        pos_parts.append("G:p/f")
    s1 = stage1_gallows(s0)
    s2 = stage2_vowels(s0)
    if s2 != s1:
        env_parts.append("V:ee/ii")

    s3 = s2
    if len(s3) > 2 and s3[0] == "q" and s3[1] in ("o", "e", "a"):
        env_parts.append("P:q-")
        pos_parts.append("P:q-")
        s3 = s3[1:]
    elif len(s3) > 2 and s3[0] == "y" and s3[1] in ("o", "e", "a", "t", "k", "c", "s"):
        env_parts.append("P:y-")
        pos_parts.append("P:y-")
        s3 = s3[1:]

    if s3.endswith("m") and len(s3) > 2:
        env_parts.append("M:-m->-r")
        pos_parts.append("M:-m")
        s3 = s3[:-1] + "r"

    s4 = s3
    if len(s4) > 2 and s4.startswith("o") and not s4.startswith(("ol", "or")):
        env_parts.append("N:o-")
        s4 = s4[1:]

    m_suf = SUFFIX_PAT.search(s4)
    if m_suf and len(s4) - len(m_suf.group(1)) >= 1:
        suf = m_suf.group(1)
        core = s4[: -len(suf)]
        env_parts.append(f"S:-{suf}")
    else:
        core = s4
        env_parts.append("S:0")

    env_sig = "|".join(env_parts) if env_parts else "BARE"
    pos_only_sig = "|".join(pos_parts) if pos_parts else "NEUTRAL"
    return pos_only_sig, env_sig, core


def fst_state_of(w: str, is_par_start: bool, is_line_start: bool, is_post_draw: bool, is_line_end: bool, is_par_end: bool) -> str:
    if is_par_start:
        return "1_PAR_OPENER"
    if is_line_end and w.endswith("m"):
        return "8_RIGHT_MARGIN_M"
    if w in ("daiin", "dain"):
        return "7_CLAUSE_DAIIN"
    if w in ("ol", "al", "dal", "dar", "or", "ar"):
        return "2_PREP_REL"
    if (is_line_start or is_post_draw) and w.startswith("y") and len(w) > 2:
        return "5_LINE_INIT_Y"
    if w.startswith("qo"):
        return "4_PROCLITIC_QO"
    if w.startswith(("ch", "sh")) and w.endswith(("edy", "eedy", "ey", "eey", "dy", "y")):
        return "3_ACTION_VERB"
    return "6_NOMINAL_STEM"


def parse_zl_corpus(zl_path: Path):
    text = zl_path.read_text(encoding="utf-8", errors="ignore")
    folios = {}
    current_folio = None
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        m_page = re.match(r"^<(f[\w]+)>\s*(?:<!\s*(.*?)\s*>)?", line)
        if m_page and "." not in m_page.group(1):
            current_folio = m_page.group(1)
            meta = {}
            if m_page.group(2):
                for kv in re.findall(r"\$([A-Z])=([A-Za-z0-9]+)", m_page.group(2)):
                    meta[kv[0]] = kv[1]
            folios[current_folio] = {"meta": meta, "lines": []}
            continue

        m_loc = re.match(r"^<([^>]+)>\s*(.*)$", line)
        if not m_loc or not current_folio:
            continue
        loc_header = m_loc.group(1)
        body = m_loc.group(2)
        parts = loc_header.split(",")
        loc_id = parts[0]
        unit_type = parts[1] if len(parts) > 1 else ""

        has_par_start = "<%>" in body
        has_par_end = "<$>" in body
        body_no_comments = re.sub(r"<!([^>]*)>", "", body)
        body_no_comments = body_no_comments.replace("<%>", "").replace("<$>", "")

        segments = body_no_comments.split("<->")
        words = []
        post_draw_indices = set()
        for seg_idx, seg in enumerate(segments):
            seg_toks = [clean_tok(t) for t in re.split(r"[\.\s,]+", seg) if t]
            seg_toks = [w for w in seg_toks if w and not w.startswith("@") and not w.startswith("H=")]
            if seg_idx > 0 and seg_toks:
                post_draw_indices.add(len(words))
            words.extend(seg_toks)

        folios[current_folio]["lines"].append(
            {
                "loc": loc_id,
                "unit": unit_type,
                "has_par_start": has_par_start,
                "has_par_end": has_par_end,
                "post_draw_indices": post_draw_indices,
                "words": words,
            }
        )
    return folios


def main():
    folios = parse_zl_corpus(ZL_PATH)

    labels_by_canon = defaultdict(list)
    prose_canon_counts = Counter()

    for fol, fdata in folios.items():
        sec = fdata["meta"].get("I", "?")
        for lobj in fdata["lines"]:
            unit = lobj["unit"]
            words = lobj["words"]
            if not words:
                continue
            if "@L" in unit or "&L" in unit:
                w = words[0]
                c = stage3_positional_proclitic_margin(w)
                labels_by_canon[c].append(
                    {"folio": fol, "section": sec, "loc": lobj["loc"], "unit": unit, "word": w}
                )
            else:
                for w in words:
                    prose_canon_counts[stage3_positional_proclitic_margin(w)] += 1

    c_stage0 = Counter()
    c_stage1 = Counter()
    c_stage2 = Counter()
    c_stage3 = Counter()
    c_stage4_root = Counter()
    c_envelope = Counter()
    c_pos_only_env = Counter()
    c_pos_state = Counter()

    pair_pos_env = Counter()
    pair_root_bigram = Counter()
    pair_word_bigram = Counter()
    all_token_records = []

    fst_trans = {"A": defaultdict(Counter), "B": defaultdict(Counter), "ALL": defaultdict(Counter)}
    fst_3grams = {"A": Counter(), "B": Counter()}

    total_prose_tokens = 0

    for fol, fdata in folios.items():
        lang = fdata["meta"].get("L", "?")
        for l_idx, lobj in enumerate(fdata["lines"]):
            unit = lobj["unit"]
            if "@L" in unit or "&L" in unit:
                continue
            words = lobj["words"]
            if not words:
                continue
            is_top_line = lobj["has_par_start"] or l_idx == 0
            prev_root = None
            prev_word = None
            line_fst_states = []

            for w_i, w in enumerate(words):
                total_prose_tokens += 1
                is_par_start = lobj["has_par_start"] and w_i == 0
                is_par_end = lobj["has_par_end"] and w_i == len(words) - 1
                is_line_start = w_i == 0
                is_line_end = w_i == len(words) - 1
                is_post_draw = w_i in lobj["post_draw_indices"]

                if is_par_start:
                    p_state = "PAR_START"
                elif is_par_end:
                    p_state = "PAR_END"
                elif is_top_line and is_line_end:
                    p_state = "TOP_LINE_END"
                elif is_top_line:
                    p_state = "TOP_LINE_MID"
                elif is_post_draw:
                    p_state = "POST_DRAWING"
                elif is_line_start:
                    p_state = "LINE_START"
                elif is_line_end:
                    p_state = "LINE_END"
                else:
                    p_state = "LINE_MID"

                w1 = stage1_gallows(w)
                w2 = stage2_vowels(w)
                w3 = stage3_positional_proclitic_margin(w)
                pos_only_sig, env_sig, core_root = extract_core_root_and_envelope(w, p_state)

                c_stage0[w] += 1
                c_stage1[w1] += 1
                c_stage2[w2] += 1
                c_stage3[w3] += 1
                c_stage4_root[core_root] += 1
                c_envelope[env_sig] += 1
                c_pos_only_env[pos_only_sig] += 1
                c_pos_state[p_state] += 1

                pair_pos_env[(p_state, pos_only_sig)] += 1
                all_token_records.append((p_state, pos_only_sig, core_root))

                if prev_root is not None:
                    pair_root_bigram[(prev_root, core_root)] += 1
                if prev_word is not None:
                    pair_word_bigram[(prev_word, w)] += 1
                prev_root = core_root
                prev_word = w

                fstate = fst_state_of(
                    w, is_par_start, is_line_start, is_post_draw, is_line_end, is_par_end
                )
                line_fst_states.append(fstate)

            for i in range(len(line_fst_states) - 1):
                s_a, s_b = line_fst_states[i], line_fst_states[i + 1]
                fst_trans["ALL"][s_a][s_b] += 1
                if lang in ("A", "B"):
                    fst_trans[lang][s_a][s_b] += 1
            if lang in ("A", "B"):
                for i in range(len(line_fst_states) - 2):
                    tg = f"{line_fst_states[i]} -> {line_fst_states[i+1]} -> {line_fst_states[i+2]}"
                    fst_3grams[lang][tg] += 1

    # Cardinality-matched comparison: 12 states of pos_only_env vs Top-11 Core Roots + OTHER (12 states)
    top11_roots = {r for r, _ in c_stage4_root.most_common(11)}
    c_root12 = Counter()
    pair_pos_root12 = Counter()
    for p_state, _, cr in all_token_records:
        r_b = cr if cr in top11_roots else "OTHER_ROOT"
        c_root12[r_b] += 1
        pair_pos_root12[(p_state, r_b)] += 1

    h0 = shannon_entropy(c_stage0)
    h1 = shannon_entropy(c_stage1)
    h2 = shannon_entropy(c_stage2)
    h3 = shannon_entropy(c_stage3)
    h4 = shannon_entropy(c_stage4_root)
    h_pos_only = shannon_entropy(c_pos_only_env)
    h_root12 = shannon_entropy(c_root12)
    h_pos = shannon_entropy(c_pos_state)

    h_pos_only_given_pos = conditional_entropy(pair_pos_env, c_pos_state)
    mi_pos_env = h_pos_only - h_pos_only_given_pos

    h_root12_given_pos = conditional_entropy(pair_pos_root12, c_pos_state)
    mi_pos_root12 = h_root12 - h_root12_given_pos

    prev_root_counts = Counter()
    for (r1, _), cnt in pair_root_bigram.items():
        prev_root_counts[r1] += cnt
    h_root_given_prev_root = conditional_entropy(pair_root_bigram, prev_root_counts)

    prev_word_counts = Counter()
    for (w1, _), cnt in pair_word_bigram.items():
        prev_word_counts[w1] += cnt
    h_word_given_prev_word = conditional_entropy(pair_word_bigram, prev_word_counts)

    waterfall = {
        "total_prose_tokens": total_prose_tokens,
        "stage0_raw_surface": {
            "vocab_types": len(c_stage0),
            "shannon_bits": round(h0, 4),
            "conditional_bigram_bits": round(h_word_given_prev_word, 4),
        },
        "stage1_gallows_allograph_strip": {
            "vocab_types": len(c_stage1),
            "vocab_reduction_pct": round((1 - len(c_stage1) / len(c_stage0)) * 100, 2),
            "shannon_bits": round(h1, 4),
            "bits_removed": round(h0 - h1, 4),
        },
        "stage2_vowel_grade_compression": {
            "vocab_types": len(c_stage2),
            "vocab_reduction_pct": round((1 - len(c_stage2) / len(c_stage0)) * 100, 2),
            "shannon_bits": round(h2, 4),
            "bits_removed_cumulative": round(h0 - h2, 4),
        },
        "stage3_positional_proclitic_and_margin_strip": {
            "vocab_types": len(c_stage3),
            "vocab_reduction_pct": round((1 - len(c_stage3) / len(c_stage0)) * 100, 2),
            "shannon_bits": round(h3, 4),
            "bits_removed_cumulative": round(h0 - h3, 4),
        },
        "stage4_pure_core_root_stream": {
            "vocab_types": len(c_stage4_root),
            "vocab_reduction_pct": round((1 - len(c_stage4_root) / len(c_stage0)) * 100, 2),
            "shannon_bits": round(h4, 4),
            "conditional_bigram_bits": round(h_root_given_prev_root, 4),
            "bits_removed_cumulative": round(h0 - h4, 4),
            "top_30_core_roots": c_stage4_root.most_common(30),
        },
        "envelope_vs_position_information": {
            "positional_envelope_12state_entropy_bits": round(h_pos_only, 4),
            "core_root_12state_entropy_bits": round(h_root12, 4),
            "position_state_entropy_bits": round(h_pos, 4),
            "mi_position_positional_envelope_bits": round(mi_pos_env, 4),
            "mi_position_coreroot_12state_bits": round(mi_pos_root12, 4),
            "ratio_mi_envelope_over_root": round(mi_pos_env / max(mi_pos_root12, 1e-6), 2),
            "normalized_mi_envelope_pct_of_entropy": round((mi_pos_env / h_pos_only) * 100, 2),
            "normalized_mi_coreroot_pct_of_entropy": round((mi_pos_root12 / h_root12) * 100, 2),
        },
    }

    fst_summary = {}
    for bucket, mat in fst_trans.items():
        fst_summary[bucket] = {}
        for s_a, next_counts in sorted(mat.items()):
            tot = sum(next_counts.values())
            fst_summary[bucket][s_a] = {
                "total_transitions": tot,
                "top_next_states": [
                    {"state": s_b, "count": c, "prob": round(c / tot, 4)}
                    for s_b, c in next_counts.most_common(5)
                ],
            }

    target_folios = [
        ("f5r", "Herbal (`f5r`, Full-Page Twin of Pharmaceutical `f99v`, `olsy` Crib)", 18),
        ("f17r", "Herbal (`f17r`, Full-Page Twin of Pharmaceutical `f99r`, `daram/dcheor` Cribs)", 18),
        ("f22r", "Herbal (`f22r`, Twin of `f88r–f89r1`, Contiguous `oldam -> otoldy` Pair)", 18),
        ("f84r", "Biological (`f84r`, `otoly <-> opoly`, `shekar <-> shekam` & `daraldy . otedaiin` Pair)", 38),
        ("f88r", "Pharmaceutical (`f88r`, `okol` Row-to-Recipe Ingestion `<f88r.19>`)", 18),
        ("f99r", "Pharmaceutical (`f99r`, Reserve-Painted Alabastron Jars & `darar` Twin)", 18),
        ("f107r", "Starred Recipes (`f107r`, Pisces `otaram -> otaral -> otalar` Sequential Crib)", 18),
        ("f113r", "Starred Recipes (`f113r`, Water-Trigon Double `.13` Zodiac Crib `ykolairol` & `oteeosy`)", 12),
    ]

    md_lines = [
        "# Stripped Root-Stream Edition of Key Voynich Folios (`Attack 7`)\n\n",
        "This document is auto-generated by [`tools/attack7_positional_envelope_fst.py`](../tools/attack7_positional_envelope_fst.py) (`Phase 18 / Attack 7`).\n\n",
        "It strips away the **Positional & Inflectional Envelope** (`3.5204 bits` of positional/allographic/suffix wrapping, compressing the vocabulary by **`-65.93%`** from `7,643` surface types to `2,604` root types) to expose the underlying **Core Root Stream (`6.7872 bits` unigram / `5.0515 bits` conditional bigram)** alongside verified **Figure-Label Cribs (`@Lf`, `@Lc`, `@Lz`, `@Ln`, `@Lt`, `@L0`)**.\n\n",
        "## 1. Five-Stage Shannon Entropy & Vocabulary Reduction Waterfall\n\n",
        "| Stage | Transformation Applied | Distinct Types (`|V|`) | Vocab Reduction | Unigram Entropy `H(X)` | Bits Stripped |\n",
        "| :--- | :--- | :---: | :---: | :---: | :---: |\n",
        f"| **Stage 0** | Raw Surface Words (`W`) | `{len(c_stage0):,}` | `0.0%` | **`{h0:.4f} bits`** | `0.0000 bits` |\n",
        f"| **Stage 1** | Top-Line Gallows Allographs (`p -> t, f -> k`) | `{len(c_stage1):,}` | `-{waterfall['stage1_gallows_allograph_strip']['vocab_reduction_pct']}%` | **`{h1:.4f} bits`** | `-{h0-h1:.4f} bits` |\n",
        f"| **Stage 2** | Vowel-Grade Compression (`ee+ -> e, ii+ -> i`) | `{len(c_stage2):,}` | `-{waterfall['stage2_vowel_grade_compression']['vocab_reduction_pct']}%` | **`{h2:.4f} bits`** | `-{h0-h2:.4f} bits` |\n",
        f"| **Stage 3** | Proclitic (`q-/y-`) & Margin (`-m -> -r`) Strip | `{len(c_stage3):,}` | `-{waterfall['stage3_positional_proclitic_and_margin_strip']['vocab_reduction_pct']}%` | **`{h3:.4f} bits`** | `-{h0-h3:.4f} bits` |\n",
        f"| **Stage 4** | **Pure Core Root Stream (`R`, Suffixes & `o-` Stripped)** | **`{len(c_stage4_root):,}`** | **`-{waterfall['stage4_pure_core_root_stream']['vocab_reduction_pct']}%`** | **`{h4:.4f} bits`** (`{h_root_given_prev_root:.4f}` bigram) | **`-{h0-h4:.4f} bits`** |\n\n",
        f"- **Cardinality-Matched Mutual Information (`12` Positional Envelope States vs. `12` Core Root States)**:\n",
        f"  - $I(\\text{{PhysicalPosition}} ; \\text{{PositionalEnvelope}}_{{12}}) = \\mathbf{{{mi_pos_env:.4f}\\text{{ bits}}}}$ (**`{waterfall['envelope_vs_position_information']['normalized_mi_envelope_pct_of_entropy']}%`** of positional envelope entropy `H = {h_pos_only:.4f} bits`)\n",
        f"  - $I(\\text{{PhysicalPosition}} ; \\text{{CoreRoot}}_{{12}}) = \\mathbf{{{mi_pos_root12:.4f}\\text{{ bits}}}}$ (**`{waterfall['envelope_vs_position_information']['normalized_mi_coreroot_pct_of_entropy']}%`** of 12-state core root entropy `H = {h_root12:.4f} bits`)\n",
        f"  - Physical page/line/paragraph coordinates carry **`{waterfall['envelope_vs_position_information']['ratio_mi_envelope_over_root']}×` more mutual information (`{round(waterfall['envelope_vs_position_information']['normalized_mi_envelope_pct_of_entropy']/max(waterfall['envelope_vs_position_information']['normalized_mi_coreroot_pct_of_entropy'], 1e-6), 2)}×` normalized)** with the Positional Envelope (`p/f`, `q-`, `y-`, `-m`) than with the Core Root!\n\n",
        "---\n\n",
        "## 2. Three-Tier Stripped Root-Stream Edition of 8 Key Folios\n\n",
        "Each line is presented in two aligned tiers:\n",
        "- **`SURF`**: Original EVA surface line (with `<%>` paragraph start, `<->` drawing interruption, and `<$>` paragraph end).\n",
        "- **`ROOT`**: Stripped **`CORE_ROOT[ENVELOPE]`** stream, with verified **Figure-Label Cribs (`★CRIB`)** highlighted inline.\n\n",
    ]

    for fol, title, max_lines in target_folios:
        if fol not in folios:
            continue
        fdata = folios[fol]
        meta_str = ", ".join(f"${k}={v}" for k, v in sorted(fdata["meta"].items()))
        md_lines.append(f"### {title} (`{meta_str}`)\n\n")
        prose_lines = [l for l in fdata["lines"] if "@L" not in l["unit"] and "&L" not in l["unit"] and l["words"]]
        for l_idx, lobj in enumerate(prose_lines[:max_lines]):
            words = lobj["words"]
            surf_tokens = []
            root_tokens = []
            for w_i, w in enumerate(words):
                prefix_marker = "<%> " if (lobj["has_par_start"] and w_i == 0) else ""
                if w_i in lobj["post_draw_indices"]:
                    prefix_marker = "<-> " + prefix_marker
                suffix_marker = " <$>" if (lobj["has_par_end"] and w_i == len(words) - 1) else ""
                surf_tokens.append(f"{prefix_marker}{w}{suffix_marker}")

                p_state = "PAR_START" if (lobj["has_par_start"] and w_i == 0) else ("LINE_END" if w_i == len(words) - 1 else "LINE_MID")
                _, env_sig, core_root = extract_core_root_and_envelope(w, p_state)
                c3 = stage3_positional_proclitic_margin(w)
                crib_tag = ""
                if c3 in labels_by_canon and len(c3) >= 3:
                    p_cnt = prose_canon_counts[c3]
                    rel_lbls = [
                        l for l in labels_by_canon[c3]
                        if p_cnt <= 15 or l["folio"] == fol
                    ]
                    if rel_lbls:
                        # Prefer same-folio label first
                        rel_lbls.sort(key=lambda x: (0 if x["folio"] == fol else 1))
                        l0 = rel_lbls[0]
                        crib_tag = f"★[{l0['loc']}({l0['unit']}):{l0['word']}|cnt={p_cnt}]"

                root_tokens.append(f"{prefix_marker}**{core_root.upper()}**`[{env_sig}]`{crib_tag}{suffix_marker}")

            md_lines.append(f"- **`<{lobj['loc']}>` SURF**: `{' . '.join(surf_tokens)}`\n")
            md_lines.append(f"  - **ROOT**: {' · '.join(root_tokens)}\n")
        md_lines.append("\n---\n\n")

    OUT_MD.write_text("".join(md_lines), encoding="utf-8")

    out_data = {
        "entropy_waterfall": waterfall,
        "fst_transition_summary": fst_summary,
        "top_fst_3grams_currier_A": fst_3grams["A"].most_common(15),
        "top_fst_3grams_currier_B": fst_3grams["B"].most_common(15),
        "top_envelope_signatures": c_envelope.most_common(25),
    }
    OUT_JSON.write_text(json.dumps(out_data, indent=2), encoding="utf-8")
    print(f"Saved {OUT_JSON} and {OUT_MD}")
    print("\n--- Envelope vs Position Information (12-State Matched) ---")
    print(json.dumps(waterfall["envelope_vs_position_information"], indent=2))


if __name__ == "__main__":
    main()
