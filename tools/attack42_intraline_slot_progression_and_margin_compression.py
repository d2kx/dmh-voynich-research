#!/usr/bin/env python3
"""
Attack 42 (Phase 53): Intra-Line Quintile Progression, Right-Margin & Drawing-Intrusion
Compression, and Vertical Paragraph-Depth Discourse Trajectory (`Line 1 -> Interior -> Line m`).

Tests three macro-structural laws across all multi-word prose lines and paragraphs:
1. Horizontal Intra-Line Quintile Trajectory (`Q1 [0.0-0.2] .. Q5 [0.8-1.0]`):
   - Tracks functional word classes (`G_TOPIC`, `Q_ACT`, `CH_VERB`, `AIIN_QUANT`, `LIQ_INGR`,
     `PREP_CONN`, `DAIIN_DELIM`, `AM_CLOSER`) and mean word length across the 5 horizontal
     quintiles of a physical line (`lines with len >= 5`).
2. Right-Margin & Pre-Intrusion (`<->`) Word-Length Compression Law:
   - Tests whether words immediately preceding the right margin (`w_n`) and words immediately
     preceding a mid-line drawing intrusion (`w_{<-> - 1}`) undergo statistically significant
     character-length compression compared to interior words (`1,000` within-line permutations).
3. Vertical Paragraph-Depth Discourse Trajectory (`Line 1 [<%>] -> Early Interior -> Late Interior -> Final Line m [<$>]`):
   - Tests the 3-stage recipe discourse hypothesis across all multi-line paragraphs (`m >= 4` lines):
     Stage I  (`Line 1 [<%>]`)      : Enriches `G_TOPIC` headers and `LIQ_INGR` botanical ingredients;
     Stage II (`Interior 2..m-1`)   : Enriches `Q_ACT` (`qok-/qot-`) and `CH_VERB` (`chedy/shedy`) processing loops;
     Stage III(`Final Line m [<$>]`): Enriches `AM_CLOSER` (`-am/-om` finished product) and `DAIIN_DELIM` closers.
"""

from __future__ import annotations

import json
import math
import random
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, List

ROOT = Path(__file__).resolve().parents[1]
ZL_PATH = ROOT / "data" / "ZL3b-n.txt"
OUT_JSON = ROOT / "data" / "attack42_intraline_slot_progression_and_margin_compression.json"

PREP_WORDS = {
    "ol", "or", "ar", "al", "dar", "dal", "dol", "sol", "sal", "dair", "air", "oraiin", "olaiin"
}
DAIIN_WORDS = {"daiin", "dain", "daiiin"}


def clean_tok(t: str) -> str:
    t = re.sub(r"<!.*?>", "", t)
    t = re.sub(r"<[^>]+>", "", t)
    t = re.sub(r"\[([^:\]]+):[^\]]+\]", r"\1", t)
    t = t.replace("[", "").replace("]", "").replace("?", "").replace("!", "").replace("*", "")
    t = t.replace(",", "").replace("'", "").strip()
    return t


def classify_token(w: str) -> str:
    if w in DAIIN_WORDS:
        return "DAIIN_DELIM"
    if w in PREP_WORDS:
        return "PREP_CONN"
    if w.endswith(("am", "om", "aim", "oim", "an")):
        return "AM_CLOSER"
    if w.startswith(("qo", "qok", "qot")):
        return "Q_ACT"
    if w.endswith(("edy", "dy")) or w.startswith(("ch", "sh")):
        if w.endswith(("ol", "or", "ar", "al")) and not w.endswith(("edy", "dy")):
            return "LIQ_INGR"
        if re.search(r"i+n$", w):
            return "AIIN_QUANT"
        return "CH_VERB"
    if re.search(r"i+n$", w):
        return "AIIN_QUANT"
    if w.endswith(("ol", "or", "ar", "al", "eor", "eol", "eal", "ear")):
        return "LIQ_INGR"
    if w.startswith(("p", "f", "k", "t", "cp", "cf", "ck", "ct", "op", "of", "ok", "ot")):
        return "G_TOPIC"
    if w.startswith("y"):
        return "AM_CLOSER"
    return "OTHER"


def main() -> None:
    line_re = re.compile(r"^<([^.>]+)\.([^,>]+),([^>]+)>\s*(.*)$")
    page_re = re.compile(r"^<(f[0-9]+[rv][0-9]*|fRos)>\s*<!\s*(.*?)>")

    current_folio = None
    header_meta: Dict[str, str] = {}
    paragraphs: List[List[Dict]] = []
    curr_para: List[Dict] = []
    all_lines: List[Dict] = []

    with open(ZL_PATH, "r", encoding="utf-8") as f:
        for raw in f:
            line = raw.strip()
            if not line:
                continue
            pm = page_re.match(line)
            if pm:
                if curr_para:
                    paragraphs.append(curr_para)
                    curr_para = []
                current_folio = pm.group(1)
                meta_str = pm.group(2)
                header_meta = dict(re.findall(r"\$([A-Z])=([A-Za-z0-9]+)", meta_str))
                continue
            if line.startswith("#"):
                continue
            lm = line_re.match(line)
            if not lm or not current_folio:
                continue
            _, loc_id, ltype, body = lm.groups()
            if "@L" in ltype or "+L" in ltype or "*L" in ltype or ltype.startswith("L") or "Cc" in ltype or "Ro" in ltype:
                continue

            body_clean = re.sub(r"<!.*?>", "", body)
            # Track `<->` intrusion positions before splitting
            segments = body_clean.split("<->")
            seg_tokens = []
            for seg in segments:
                rt = re.split(r"[.\s]+", seg)
                ct = [clean_tok(t) for t in rt]
                ct = [t for t in ct if t and not t.startswith("<")]
                if ct:
                    seg_tokens.append(ct)

            toks = [w for seg in seg_tokens for w in seg]
            if not toks:
                continue

            is_new_para = ("<%>" in body) or ltype.startswith("@P") or ("=Pt" in ltype)
            if is_new_para and curr_para:
                paragraphs.append(curr_para)
                curr_para = []

            rec = {
                "folio": current_folio,
                "loc_id": loc_id,
                "section": header_meta.get("I", "?"),
                "language": header_meta.get("L", "?"),
                "tokens": toks,
                "classes": [classify_token(w) for w in toks],
                "seg_tokens": seg_tokens,
                "has_intrusion": len(seg_tokens) > 1,
                "has_para_start": is_new_para,
                "has_para_end": "<$>" in body,
            }
            all_lines.append(rec)
            curr_para.append(rec)

            if "<$>" in body and curr_para:
                paragraphs.append(curr_para)
                curr_para = []

    if curr_para:
        paragraphs.append(curr_para)

    # 1. Horizontal Intra-Line Quintile Progression (for lines with >= 5 tokens)
    quintile_classes: Dict[str, Counter] = {f"Q{k}": Counter() for k in range(1, 6)}
    quintile_lengths: Dict[str, List[int]] = {f"Q{k}": [] for k in range(1, 6)}

    long_lines = [ln for ln in all_lines if len(ln["tokens"]) >= 5]
    for ln in long_lines:
        n = len(ln["tokens"])
        for i, (w, c) in enumerate(zip(ln["tokens"], ln["classes"])):
            rel = i / (n - 1)
            q_idx = min(5, int(rel * 5) + 1)
            qk = f"Q{q_idx}"
            quintile_classes[qk][c] += 1
            quintile_lengths[qk].append(len(w))

    quintile_profiles = {}
    for k in range(1, 6):
        qk = f"Q{k}"
        tot = sum(quintile_classes[qk].values()) or 1
        lens = quintile_lengths[qk]
        quintile_profiles[qk] = {
            "n_tokens": tot,
            "mean_word_len": round(sum(lens) / max(1, len(lens)), 3),
            "class_rates": {
                c: round(quintile_classes[qk][c] / tot, 4)
                for c in ("G_TOPIC", "Q_ACT", "CH_VERB", "AIIN_QUANT", "LIQ_INGR", "PREP_CONN", "DAIIN_DELIM", "AM_CLOSER")
            },
        }

    # 2. Right-Margin (`w_n` vs `w_2..w_{n-1}`) & Pre-Intrusion (`w_{<-> - 1}`) Word-Length Compression Test
    # Exclude w_1 (since w_1 has top-line/line-initial gallows prefixes) and compare w_n against interior w_2..w_{n-1}!
    interior_lens = []
    line_end_lens = []
    for ln in long_lines:
        toks = ln["tokens"]
        for w in toks[1:-1]:
            interior_lens.append(len(w))
        line_end_lens.append(len(toks[-1]))

    mean_int_len = sum(interior_lens) / max(1, len(interior_lens))
    mean_end_len = sum(line_end_lens) / max(1, len(line_end_lens))

    # Permutation test for line-end word length vs interior (w_2..w_n shuffled within each line):
    rng = random.Random(42)
    null_end_lens = []
    for _ in range(500):
        s_end = 0
        for ln in long_lines:
            sub = ln["tokens"][1:]
            s_end += len(rng.choice(sub))
        null_end_lens.append(s_end / len(long_lines))
    mu_end = sum(null_end_lens) / 500
    sd_end = math.sqrt(sum((x - mu_end) ** 2 for x in null_end_lens) / 500) or 1e-9
    z_end_len = (mean_end_len - mu_end) / sd_end

    # Pre-intrusion word length (`seg[:-1][-1]`) vs post-intrusion word length (`seg[1:][0]`)
    pre_intr_lens = []
    post_intr_lens = []
    for ln in all_lines:
        if ln["has_intrusion"]:
            segs = ln["seg_tokens"]
            for s_i in range(len(segs) - 1):
                pre_intr_lens.append(len(segs[s_i][-1]))
                post_intr_lens.append(len(segs[s_i + 1][0]))

    # 3. Vertical Paragraph-Depth Trajectory (`STAGE_1_LINE1`, `STAGE_2_INTERIOR`, `STAGE_3_FINAL_LINE`)
    multi_paras = [p for p in paragraphs if len(p) >= 4]
    stage_counts = {
        "STAGE_1_LINE1": Counter(),
        "STAGE_2_EARLY_INT": Counter(),
        "STAGE_3_LATE_INT": Counter(),
        "STAGE_4_FINAL_LINE": Counter(),
    }
    for p in multi_paras:
        m = len(p)
        stage_counts["STAGE_1_LINE1"].update(p[0]["classes"])
        stage_counts["STAGE_4_FINAL_LINE"].update(p[-1]["classes"])
        mid = p[1:-1]
        half = max(1, len(mid) // 2)
        for ln in mid[:half]:
            stage_counts["STAGE_2_EARLY_INT"].update(ln["classes"])
        for ln in mid[half:]:
            stage_counts["STAGE_3_LATE_INT"].update(ln["classes"])

    stage_profiles = {}
    for st_name, cnts in stage_counts.items():
        tot = sum(cnts.values()) or 1
        stage_profiles[st_name] = {
            "n_tokens": tot,
            "class_rates": {
                c: round(cnts[c] / tot, 4)
                for c in ("G_TOPIC", "Q_ACT", "CH_VERB", "AIIN_QUANT", "LIQ_INGR", "PREP_CONN", "DAIIN_DELIM", "AM_CLOSER")
            },
        }

    # Permutation test for Paragraph-Depth Progression (shuffling lines within each multi-line paragraph, 500 trials):
    # Test (a) LIQ_INGR enrichment in Line 1, (b) Q_ACT + CH_VERB enrichment in Interior, (c) AM_CLOSER enrichment in Final Line
    obs_l1_liq = stage_profiles["STAGE_1_LINE1"]["class_rates"]["LIQ_INGR"]
    obs_int_proc = (
        (stage_counts["STAGE_2_EARLY_INT"]["Q_ACT"] + stage_counts["STAGE_2_EARLY_INT"]["CH_VERB"]
         + stage_counts["STAGE_3_LATE_INT"]["Q_ACT"] + stage_counts["STAGE_3_LATE_INT"]["CH_VERB"])
        / max(1, sum(stage_counts["STAGE_2_EARLY_INT"].values()) + sum(stage_counts["STAGE_3_LATE_INT"].values()))
    )
    obs_fin_am = stage_profiles["STAGE_4_FINAL_LINE"]["class_rates"]["AM_CLOSER"]

    null_l1_liq = []
    null_int_proc = []
    null_fin_am = []
    for _ in range(500):
        c_l1 = Counter()
        c_int = Counter()
        c_fin = Counter()
        for p in multi_paras:
            p_shuf = list(p)
            rng.shuffle(p_shuf)
            c_l1.update(p_shuf[0]["classes"])
            c_fin.update(p_shuf[-1]["classes"])
            for ln in p_shuf[1:-1]:
                c_int.update(ln["classes"])
        null_l1_liq.append(c_l1["LIQ_INGR"] / max(1, sum(c_l1.values())))
        null_int_proc.append((c_int["Q_ACT"] + c_int["CH_VERB"]) / max(1, sum(c_int.values())))
        null_fin_am.append(c_fin["AM_CLOSER"] / max(1, sum(c_fin.values())))

    def z_of(obs: float, arr: List[float]) -> float:
        mu = sum(arr) / len(arr)
        sd = math.sqrt(sum((x - mu) ** 2 for x in arr) / len(arr)) or 1e-9
        return round((obs - mu) / sd, 2)

    z_l1_liq = z_of(obs_l1_liq, null_l1_liq)
    z_int_proc = z_of(obs_int_proc, null_int_proc)
    z_fin_am = z_of(obs_fin_am, null_fin_am)

    out = {
        "horizontal_quintile_profiles": quintile_profiles,
        "margin_and_intrusion_compression": {
            "n_lines_len_ge_5": len(long_lines),
            "mean_interior_word_len_w2_to_wn_minus_1": round(mean_int_len, 4),
            "mean_line_end_word_len_wn": round(mean_end_len, 4),
            "line_end_vs_interior_diff_chars": round(mean_end_len - mean_int_len, 4),
            "line_end_len_z_score": round(z_end_len, 2),
            "n_intrusion_breaks": len(pre_intr_lens),
            "mean_pre_intrusion_word_len": round(sum(pre_intr_lens) / max(1, len(pre_intr_lens)), 4),
            "mean_post_intrusion_word_len": round(sum(post_intr_lens) / max(1, len(post_intr_lens)), 4),
        },
        "vertical_paragraph_depth_profiles": {
            "n_paragraphs_len_ge_4": len(multi_paras),
            "stages": stage_profiles,
            "hypothesis_tests": {
                "line1_liq_ingr_rate": round(obs_l1_liq, 4),
                "line1_liq_ingr_z_score": z_l1_liq,
                "interior_q_act_plus_ch_verb_rate": round(obs_int_proc, 4),
                "interior_procedural_z_score": z_int_proc,
                "final_line_am_closer_rate": round(obs_fin_am, 4),
                "final_line_am_closer_z_score": z_fin_am,
            },
        },
    }

    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)

    print("=== ATTACK 42: INTRA-LINE QUINTILE PROGRESSION & PARAGRAPH-DEPTH TRAJECTORY ===")
    print("1. Horizontal Quintiles (Q1 [Left] -> Q5 [Right]):")
    for qk, qp in quintile_profiles.items():
        cr = qp["class_rates"]
        print(
            f"   {qk}: len={qp['mean_word_len']:.3f} | G={cr['G_TOPIC']:.3f}, Q={cr['Q_ACT']:.3f}, "
            f"V={cr['CH_VERB']:.3f}, AIIN={cr['AIIN_QUANT']:.3f}, LIQ={cr['LIQ_INGR']:.3f}, "
            f"DAIIN={cr['DAIIN_DELIM']:.3f}, AM={cr['AM_CLOSER']:.3f}"
        )
    mc = out["margin_and_intrusion_compression"]
    print(
        f"\n2. Right-Margin Word-Length Compression: interior={mc['mean_interior_word_len_w2_to_wn_minus_1']:.3f} chars "
        f"vs line-end w_n={mc['mean_line_end_word_len_wn']:.3f} chars (z={mc['line_end_len_z_score']:+.2f})"
    )
    print(
        f"   Drawing Intrusion (<->): pre-intrusion={mc['mean_pre_intrusion_word_len']:.3f} chars "
        f"vs post-intrusion={mc['mean_post_intrusion_word_len']:.3f} chars (n={mc['n_intrusion_breaks']})"
    )
    print("\n3. Vertical Paragraph-Depth Discourse Trajectory (m >= 4 lines, n=355 paragraphs):")
    for st_name, sp in stage_profiles.items():
        cr = sp["class_rates"]
        print(
            f"   {st_name:19s}: G={cr['G_TOPIC']:.3f}, LIQ={cr['LIQ_INGR']:.3f}, "
            f"Q+V={cr['Q_ACT']+cr['CH_VERB']:.3f} (Q={cr['Q_ACT']:.3f}, V={cr['CH_VERB']:.3f}), "
            f"AIIN={cr['AIIN_QUANT']:.3f}, AM={cr['AM_CLOSER']:.3f}"
        )
    ht = out["vertical_paragraph_depth_profiles"]["hypothesis_tests"]
    print(
        f"   Z-scores vs Within-Paragraph Line Shuffle: "
        f"Line1_LIQ z={ht['line1_liq_ingr_z_score']:+.2f}, "
        f"Interior_Q+V z={ht['interior_procedural_z_score']:+.2f}, "
        f"FinalLine_AM z={ht['final_line_am_closer_z_score']:+.2f}"
    )


if __name__ == "__main__":
    main()
