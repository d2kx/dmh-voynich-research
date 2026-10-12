"""
Attack 63: The 3x3 Two-Dimensional Paragraph Spatial Grid & Discourse Progression Automaton.

Combines the vertical paragraph axis (`TOP_LINE_1 [<%>]`, `MID_LINES_2..M-1`, `BOT_LINE_M [<$>]`)
with the horizontal line axis (`LEFT_W1`, `MID_W2..N-1`, `RIGHT_WN`) to define the 9 spatial zones
of a Voynich Manuscript paragraph (`3 x 3 = 9` 2D Paragraph Zones):

  - Z11 (`TOP_LEFT`: Line 1, Word 1 `<%>w_1`)     | Z12 (`TOP_MID`: Line 1, Words 2..n-1)     | Z13 (`TOP_RIGHT`: Line 1, Word n)
  - Z21 (`MID_LEFT`: Lines 2..m-1, Word 1)        | Z22 (`MID_MID`: Lines 2..m-1, Words 2..n-1)| Z23 (`MID_RIGHT`: Lines 2..m-1, Word n)
  - Z31 (`BOT_LEFT`: Final Line m, Word 1)        | Z32 (`BOT_MID`: Final Line m, Words 2..n-1)| Z33 (`BOT_RIGHT`: Final Line m, Word n `<$>`)

Across all multi-line prose paragraphs in `ZL3b-n.txt`, this script:
1. Computes the exact Dual-Matrix feature profile of each of the 9 spatial zones (`Z11..Z33`):
   - Top-line Labial Gallows (`p/f, pch/fch, cph/cfh`)
   - Sibilant & Conjunction Continuation Onsets (`s-, sh-, y-`)
   - Active Operator Proclitics (`qo-` + `k/t` + `-edy/-eedy/-eey`)
   - Simplex Bench Verbs (`chedy/shedy/chey/shey`)
   - Partitive/Measure Nominals (`daiin, aiin, raiin`)
   - Right-Margin Nasal Closers (`-am, -om, -m`, `dam, ram, lam, otam`)
2. Runs a 500-trial within-paragraph word-position permutation test on the 2D Spatial Mutual Information
   I(Zone_3x3 ; GrammaticalFeatureClass).
3. Exports `data/attack63_paragraph_arc_and_sentence_translator.json`.
"""

import json
import math
import random
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ZL_PATH = ROOT / "data" / "ZL3b-n.txt"
OUT_JSON = ROOT / "data" / "attack63_paragraph_arc_and_sentence_translator.json"

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


def functional_role(w: str) -> str:
    if any(g in w for g in ("p", "f")):
        return "PF_TOPLINE_GALLOWS"
    if w.endswith(("am", "om", "m")) and len(w) >= 2:
        return "M_NASAL_CLOSER"
    if w.startswith("qo"):
        return "QO_ACTIVE_OP"
    if w.startswith(("l", "ol", "qol")) and any(c in w for c in ("k", "t", "ch", "sh")):
        return "L_APPLICATIVE_OP"
    if w.startswith(("s", "sh")) and not w.endswith(("edy", "eedy")):
        return "S_SH_CONTINUATION"
    if w.startswith("y"):
        return "Y_CONJ_INIT"
    if w.startswith(("ch", "sh")) and w.endswith(("edy", "eedy", "dy", "ey", "eey")):
        return "CH_SH_BENCH_VERB"
    if w.endswith(("aiin", "ain", "iin", "in")):
        return "AIIN_MEASURE_NOM"
    if w.startswith(("ok", "ot", "k", "t", "ckh", "cth")):
        return "KT_GALLOWS_STEM"
    if w.startswith("d"):
        return "D_DEICTIC_PREP"
    return "O_LIQUID_OTHER"


def load_paragraphs():
    paragraphs = []
    cur_para = []
    cur_sec = "U"
    cur_lang = "U"
    cur_folio = ""

    for raw_line in ZL_PATH.read_text(encoding="utf-8", errors="replace").splitlines():
        raw_line = raw_line.strip()
        if not raw_line or raw_line.startswith("#"):
            continue
        if raw_line.startswith("<f") and ">" in raw_line and "." not in raw_line.split(">")[0]:
            m_s = re.search(r"\$I=([A-Z])", raw_line)
            cur_sec = m_s.group(1) if m_s else "U"
            m_l = re.search(r"\$L=([A-Z])", raw_line)
            cur_lang = m_l.group(1) if m_l else "U"
            continue

        m = LOCUS_RE.match(raw_line)
        if not m:
            continue
        folio = "f" + m.group(1)
        loc_tag = m.group(3)
        body = m.group(4)
        if "P" not in loc_tag:
            continue

        is_start = "<%>" in body or folio != cur_folio
        is_end = "<$>" in body
        toks = clean_tokens(body)
        if not toks:
            continue

        if is_start and cur_para:
            paragraphs.append(cur_para)
            cur_para = []

        cur_folio = folio
        cur_para.append({
            "folio": folio,
            "sec": cur_sec,
            "lang": cur_lang,
            "loc": f"<{folio}.{m.group(2)},{loc_tag}>",
            "words": toks,
        })

        if is_end and cur_para:
            paragraphs.append(cur_para)
            cur_para = []

    if cur_para:
        paragraphs.append(cur_para)

    return [p for p in paragraphs if len(p) >= 2]


def main():
    paras = load_paragraphs()
    zones_order = [
        "Z11_TOP_LEFT", "Z12_TOP_MID", "Z13_TOP_RIGHT",
        "Z21_MID_LEFT", "Z22_MID_MID", "Z23_MID_RIGHT",
        "Z31_BOT_LEFT", "Z32_BOT_MID", "Z33_BOT_RIGHT",
    ]

    para_zone_role_records = []
    zone_counts = defaultdict(Counter)
    zone_top_words = defaultdict(Counter)

    for p in paras:
        m_lines = len(p)
        p_recs = []
        for l_idx, ln in enumerate(p):
            if l_idx == 0:
                v_zone = "Z1_TOP"
            elif l_idx == m_lines - 1:
                v_zone = "Z3_BOT"
            else:
                v_zone = "Z2_MID"

            words = ln["words"]
            n_w = len(words)
            for w_idx, w in enumerate(words):
                if w_idx == 0:
                    h_zone = "LEFT"
                elif w_idx == n_w - 1:
                    h_zone = "RIGHT"
                else:
                    h_zone = "MID"

                z_label = f"{v_zone[:2]}{1 if h_zone=='LEFT' else (2 if h_zone=='MID' else 3)}_{v_zone[3:]}_{h_zone}"
                role = functional_role(w)
                zone_counts[z_label][role] += 1
                zone_top_words[z_label][w] += 1
                p_recs.append((z_label, role))
        para_zone_role_records.append(p_recs)

    # Compute observed MI(Zone_3x3 ; Role)
    all_pairs = [pair for p_recs in para_zone_role_records for pair in p_recs]
    n_tot = len(all_pairs)
    cz = Counter(z for z, _ in all_pairs)
    cr = Counter(r for _, r in all_pairs)
    czr = Counter(all_pairs)
    obs_mi = sum(
        (c / n_tot) * math.log2((c / n_tot) / ((cz[z] / n_tot) * (cr[r] / n_tot)))
        for (z, r), c in czr.items()
    )

    # 500-trial within-paragraph permutation test (preserving exact vocabulary of every paragraph!)
    rng = random.Random(6301)
    null_mis = []
    for _ in range(500):
        sim_czr = Counter()
        for p_recs in para_zone_role_records:
            zs = [z for z, _ in p_recs]
            rs = [r for _, r in p_recs]
            rng.shuffle(rs)
            for z, r in zip(zs, rs):
                sim_czr[(z, r)] += 1
        m_val = sum(
            (c / n_tot) * math.log2((c / n_tot) / ((cz[z] / n_tot) * (cr[r] / n_tot)))
            for (z, r), c in sim_czr.items()
        )
        null_mis.append(m_val)

    z_score = (obs_mi - mean(null_mis)) / (std(null_mis) + 1e-12)

    # Build 9-zone summary table
    zone_summary = {}
    for z in zones_order:
        cnt = zone_counts[z]
        tot = sum(cnt.values())
        if tot == 0:
            continue
        zone_summary[z] = {
            "total_tokens": tot,
            "PF_TOPLINE_GALLOWS_pct": round(100.0 * cnt["PF_TOPLINE_GALLOWS"] / tot, 2),
            "S_SH_CONTINUATION_pct": round(100.0 * cnt["S_SH_CONTINUATION"] / tot, 2),
            "Y_CONJ_INIT_pct": round(100.0 * cnt["Y_CONJ_INIT"] / tot, 2),
            "QO_ACTIVE_OP_pct": round(100.0 * cnt["QO_ACTIVE_OP"] / tot, 2),
            "CH_SH_BENCH_VERB_pct": round(100.0 * cnt["CH_SH_BENCH_VERB"] / tot, 2),
            "AIIN_MEASURE_NOM_pct": round(100.0 * cnt["AIIN_MEASURE_NOM"] / tot, 2),
            "M_NASAL_CLOSER_pct": round(100.0 * cnt["M_NASAL_CLOSER"] / tot, 2),
            "top_5_words": dict(zone_top_words[z].most_common(5)),
        }

    print("=== ATTACK 63: THE 3x3 TWO-DIMENSIONAL PARAGRAPH SPATIAL GRID ===")
    print(f"Analyzed {len(paras)} multi-line paragraphs ({n_tot:,} prose tokens)")
    print(f"2D Spatial Grid MI(Zone_3x3 ; Role) = {obs_mi:.5f} bits vs {mean(null_mis):.5f} ± {std(null_mis):.5f} within-paragraph null (z = {z_score:+.2f})\n")
    for z in zones_order:
        v = zone_summary[z]
        print(
            f"  {z:13s} (n={v['total_tokens']:5d}): PF={v['PF_TOPLINE_GALLOWS_pct']:5.2f}%, "
            f"S/SH={v['S_SH_CONTINUATION_pct']:5.2f}%, Y={v['Y_CONJ_INIT_pct']:5.2f}%, "
            f"QO={v['QO_ACTIVE_OP_pct']:5.2f}%, CH_V={v['CH_SH_BENCH_VERB_pct']:5.2f}%, "
            f"AIIN={v['AIIN_MEASURE_NOM_pct']:5.2f}%, M_CLOSE={v['M_NASAL_CLOSER_pct']:5.2f}% | Top: {list(v['top_5_words'].keys())[:3]}"
        )

    out = {
        "paragraphs_analyzed": len(paras),
        "total_prose_tokens": n_tot,
        "spatial_grid_mi_bits": round(obs_mi, 5),
        "within_paragraph_null_mean_bits": round(mean(null_mis), 5),
        "within_paragraph_null_std_bits": round(std(null_mis), 5),
        "within_paragraph_permutation_z": round(z_score, 2),
        "nine_zone_table": zone_summary,
    }
    OUT_JSON.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"\nSaved -> {OUT_JSON}")


if __name__ == "__main__":
    main()
