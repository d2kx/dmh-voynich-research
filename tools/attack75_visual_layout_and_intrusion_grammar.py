#!/usr/bin/env python3
"""
Attack 75: Multi-Modal Visual Layout, Drawing-Intrusion (`<->`) Constituent Bridging,
and Vertical Plant-Zone (`P_top` Flower/Leaf vs `P_mid` Stem vs `P_bot` Root) Concordance

Tests 3 multi-modal text-to-drawing hypotheses across the Voynich Manuscript:
1. Drawing-Intrusion (`Left_Seg <-> Right_Seg`) Syntactic & Morphological Micro-Grammar:
   - Across all 754 `<->` drawing intrusions on illustrated folios, examines the exact
     word immediately preceding the drawing (`w_pre`, left of `<->`) and the exact word
     immediately following the drawing (`w_post`, right of `<->`).
   - Tests whether `<->` acts as:
     (a) A Clause/Line Boundary (enriching line-final `-am/-om/-y` at `w_pre` and line-initial
         `y-/s-/sh-` at `w_post`), OR
     (b) A Mid-Constituent / Mid-Clause Physical Split where the syntactic transition
         `Role(w_pre) -> Role(w_post)` preserves normal intra-line constituent transitions
         across the painted stem/figure!
2. Within-Folio Uninterrupted Canopy Lines (`no <->`) vs Drawing-Wrapping Lines (`has <->`):
   - Paired within-folio comparison across illustrated folios containing both line types:
     measures word length, constituent density, and 10-bit feature shifts.
3. Multi-Paragraph Herbal Vertical Plant-Zone Progression (`P1 [Top Flower/Leaf Zone]` vs
   `P2 [Mid Stem Zone]` vs `P3+ [Bottom Root Zone]`):
   - On Herbal (`$I=H`) folios with >= 2 paragraphs, tests how prefix, core-class, and
     suffix distributions shift from the top paragraph (adjacent to the flower/upper leaves)
     to the bottom paragraph (adjacent to the roots).
"""

import json
import math
import random
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
ZL_PATH = DATA_DIR / "ZL3b-n.txt"
OUT_JSON = DATA_DIR / "attack75_visual_layout_and_intrusion_grammar.json"

LOCUS_RE = re.compile(r"^<f([0-9]+[rv][0-9]*|Ros)\.([^,>]+),([^>]+)>\s*(.*)$")


def clean_word(raw: str) -> str:
    s = re.sub(r"\{[^}]*\}", "", raw)
    s = re.sub(r"\[([^:\]]+):[^\]]+\]", r"\1", s)
    s = re.sub(r"<[^>]*>", "", s)
    s = re.sub(r"@[0-9]+;", "", s)
    s = re.sub(r"[^a-zA-Z]", "", s).lower()
    return s


def clean_segment(seg: str):
    s = re.sub(r"\{[^}]*\}", "", seg)
    s = re.sub(r"\[([^:\]]+):[^\]]+\]", r"\1", s)
    s = s.replace("<%>", " ").replace("<$>", " ")
    s = re.sub(r"<[^>]*>", " ", s)
    s = re.sub(r"@[0-9]+;", "", s)
    s = re.sub(r"[^a-zA-Z.\s]", "", s).lower()
    return [t for t in s.replace(".", " ").split() if t]


def word_role(w: str) -> str:
    if w.endswith(("am", "om", "m")):
        return "FIN_M"
    if w.startswith("qo") or w.startswith("q"):
        return "ACT_QO"
    if w.startswith(("ch", "sh")) and w.endswith(("edy", "eedy", "dy", "ey", "eey", "y")):
        return "VERB_CH"
    if w in ("daiin", "dain", "aiin", "ain", "raiin", "iiin"):
        return "MEAS_IN"
    if w.startswith(("d", "s", "y")) and len(w) <= 5:
        return "PREP_DSY"
    if w.startswith(("o", "a")) and any(g in w for g in ("k", "t", "p", "f")):
        return "NOM_OK"
    if w.endswith(("ol", "or", "al", "ar")):
        return "NOM_LIQ"
    return "NOM_OTHER"


def main():
    random.seed(42)
    cur_sec = "U"
    cur_lang = "U"
    cur_hand = "U"

    intrusion_pairs = []
    normal_adjacent_pairs = Counter()
    intrusion_role_pairs = Counter()

    pre_words = []
    post_words = []
    true_line_final_words = []
    true_line_init_words = []
    true_interior_words = []

    folio_lines = defaultdict(list)
    herbal_paras = defaultdict(list)
    cur_para = None

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
        has_intrusion = "<->" in raw_txt

        raw_segments = raw_txt.split("<->")
        seg_words = [clean_segment(sg) for sg in raw_segments]
        seg_words = [sg for sg in seg_words if sg]
        all_words = [w for sg in seg_words for w in sg]
        if not all_words:
            continue

        if is_start:
            cur_para = {
                "folio": folio,
                "sec": cur_sec,
                "lang": cur_lang,
                "hand": cur_hand,
                "lines": [],
            }
            if cur_sec == "H":
                herbal_paras[folio].append(cur_para)

        cur_para["lines"].append({
            "lnum": lnum,
            "has_intrusion": len(seg_words) > 1,
            "words": all_words,
            "seg_words": seg_words,
        })
        folio_lines[folio].append({
            "sec": cur_sec,
            "lang": cur_lang,
            "lnum": lnum,
            "has_intrusion": len(seg_words) > 1,
            "words": all_words,
        })

        # Collect true line-initial, line-final, and interior words
        true_line_init_words.append(all_words[0])
        true_line_final_words.append(all_words[-1])
        for w in all_words[1:-1]:
            true_interior_words.append(w)

        # Collect normal intra-segment adjacent pairs
        for sg in seg_words:
            for i in range(len(sg) - 1):
                normal_adjacent_pairs[(word_role(sg[i]), word_role(sg[i + 1]))] += 1

        # Collect `<->` boundary pairs (w_pre <-> w_post)
        if len(seg_words) > 1:
            for k in range(len(seg_words) - 1):
                w_pre = seg_words[k][-1]
                w_post = seg_words[k + 1][0]
                pre_words.append(w_pre)
                post_words.append(w_post)
                r_pre = word_role(w_pre)
                r_post = word_role(w_post)
                intrusion_role_pairs[(r_pre, r_post)] += 1
                intrusion_pairs.append({
                    "folio": folio,
                    "lnum": lnum,
                    "sec": cur_sec,
                    "lang": cur_lang,
                    "w_pre": w_pre,
                    "w_post": w_post,
                    "role_pre": r_pre,
                    "role_post": r_post,
                })

        if is_end:
            cur_para = None

    # 1. Compare w_pre and w_post profiles against True Line-Final, True Line-Initial, and True Interior
    def profile_words(ws):
        n = max(len(ws), 1)
        return {
            "count": len(ws),
            "mean_len": round(sum(len(w) for w in ws) / n, 3),
            "fin_m_pct": round(sum(1 for w in ws if w.endswith(("am", "om", "m"))) / n * 100, 2),
            "fin_y_dy_pct": round(sum(1 for w in ws if w.endswith("y")) / n * 100, 2),
            "fin_in_pct": round(sum(1 for w in ws if w.endswith(("aiin", "ain", "oiin", "in"))) / n * 100, 2),
            "fin_liq_pct": round(sum(1 for w in ws if w.endswith(("ol", "or", "al", "ar"))) / n * 100, 2),
            "init_y_s_pct": round(sum(1 for w in ws if w.startswith(("y", "s"))) / n * 100, 2),
            "init_o_pct": round(sum(1 for w in ws if w.startswith("o")) / n * 100, 2),
            "init_qo_pct": round(sum(1 for w in ws if w.startswith("q")) / n * 100, 2),
            "init_ch_sh_pct": round(sum(1 for w in ws if w.startswith(("ch", "sh"))) / n * 100, 2),
            "init_pf_pct": round(sum(1 for w in ws if w.startswith(("p", "f", "cph", "cfh"))) / n * 100, 2),
        }

    prof_pre = profile_words(pre_words)
    prof_post = profile_words(post_words)
    prof_true_fin = profile_words(true_line_final_words)
    prof_true_init = profile_words(true_line_init_words)
    prof_interior = profile_words(true_interior_words)

    # Cosine similarity between `<->` role transitions and normal intra-line role transitions
    all_r_keys = sorted(set(normal_adjacent_pairs.keys()) | set(intrusion_role_pairs.keys()))
    num = sum(normal_adjacent_pairs[k] * intrusion_role_pairs[k] for k in all_r_keys)
    den1 = sum(v * v for v in normal_adjacent_pairs.values())
    den2 = sum(v * v for v in intrusion_role_pairs.values())
    role_transition_cos = num / math.sqrt(den1 * den2) if den1 and den2 else 0.0

    # Check how often `w_pre <-> w_post` forms a single multi-word constituent (e.g. Verb -> Noun or Prep -> Noun or Noun -> daiin)
    multiword_const_bridges = []
    for p in intrusion_pairs:
        wp, wn = p["w_pre"], p["w_post"]
        if wn in ("daiin", "dain", "aiin", "ain") or (wp in ("ol", "dal", "qol", "s", "d", "y", "or", "ar", "chol", "shol")) or (p["role_pre"] == "VERB_CH" and p["role_post"] == "ACT_QO"):
            multiword_const_bridges.append(p)

    # 2. Within-Folio Canopy (`no <->`) vs Split (`has <->`) Comparison
    canopy_word_lens = []
    split_word_lens = []
    paired_folios = 0
    for fol, flns in folio_lines.items():
        c_lns = [ln for ln in flns if not ln["has_intrusion"]]
        s_lns = [ln for ln in flns if ln["has_intrusion"]]
        if c_lns and s_lns:
            paired_folios += 1
            for ln in c_lns:
                canopy_word_lens.extend(len(w) for w in ln["words"])
            for ln in s_lns:
                split_word_lens.extend(len(w) for w in ln["words"])

    # 3. Multi-Paragraph Herbal Vertical Plant-Zone Progression (P1 Top Flower/Leaf vs P_last Bottom Root)
    p_top_words = []
    p_mid_words = []
    p_bot_words = []
    multi_para_herbal_folios = 0

    for fol, plist in herbal_paras.items():
        if len(plist) < 2:
            continue
        multi_para_herbal_folios += 1
        for ln in plist[0]["lines"]:
            p_top_words.extend(ln["words"])
        for ln in plist[-1]["lines"]:
            p_bot_words.extend(ln["words"])
        for mp in plist[1:-1]:
            for ln in mp["lines"]:
                p_mid_words.extend(ln["words"])

    prof_herbal_top = profile_words(p_top_words)
    prof_herbal_mid = profile_words(p_mid_words) if p_mid_words else {}
    prof_herbal_bot = profile_words(p_bot_words)

    # Top distinctive words enriched in Herbal P_top (Flower/Leaf) vs P_bot (Root)
    c_top = Counter(p_top_words)
    c_bot = Counter(p_bot_words)
    tot_top = len(p_top_words)
    tot_bot = len(p_bot_words)
    herbal_zone_words = []
    for w in set(c_top.keys()) | set(c_bot.keys()):
        if c_top[w] + c_bot[w] >= 12:
            rt = (c_top[w] + 0.5) / (tot_top + 1.0)
            rb = (c_bot[w] + 0.5) / (tot_bot + 1.0)
            herbal_zone_words.append({
                "word": w,
                "top_count": c_top[w],
                "bot_count": c_bot[w],
                "top_to_bot_ratio": round(rt / rb, 3),
            })
    herbal_zone_words.sort(key=lambda x: x["top_to_bot_ratio"], reverse=True)

    print("=== ATTACK 75: VISUAL LAYOUT, DRAWING INTRUSIONS (`<->`) & PLANT-ZONE GRAMMAR ===")
    print(f"Total `<->` Drawing Boundary Pairs: {len(intrusion_pairs):,} | Paired Folios: {paired_folios}")
    print(f"Role-Transition Cosine (`w_pre <-> w_post` vs Normal Intra-Line `w_i . w_{{i+1}}`) = {role_transition_cos:.4f}")
    print(f"Direct Multi-Word Constituent Bridges Across `<->`: {len(multiword_const_bridges)} ({len(multiword_const_bridges)/len(intrusion_pairs)*100:.2f}%)")
    print("\nPositional & Morphological Profile Comparison:")
    print(f"  True Interior  (n={prof_interior['count']:5d}): len={prof_interior['mean_len']:.3f} | -m={prof_interior['fin_m_pct']:4.2f}% | -y={prof_interior['fin_y_dy_pct']:5.2f}% | y/s-={prof_interior['init_y_s_pct']:5.2f}% | o-={prof_interior['init_o_pct']:5.2f}% | qo-={prof_interior['init_qo_pct']:5.2f}%")
    print(f"  Pre-Drawing    (n={prof_pre['count']:5d}): len={prof_pre['mean_len']:.3f} | -m={prof_pre['fin_m_pct']:4.2f}% | -y={prof_pre['fin_y_dy_pct']:5.2f}% | y/s-={prof_pre['init_y_s_pct']:5.2f}% | o-={prof_pre['init_o_pct']:5.2f}% | qo-={prof_pre['init_qo_pct']:5.2f}%")
    print(f"  True Line-Fin  (n={prof_true_fin['count']:5d}): len={prof_true_fin['mean_len']:.3f} | -m={prof_true_fin['fin_m_pct']:4.2f}% | -y={prof_true_fin['fin_y_dy_pct']:5.2f}% | y/s-={prof_true_fin['init_y_s_pct']:5.2f}% | o-={prof_true_fin['init_o_pct']:5.2f}% | qo-={prof_true_fin['init_qo_pct']:5.2f}%")
    print(f"  Post-Drawing   (n={prof_post['count']:5d}): len={prof_post['mean_len']:.3f} | -m={prof_post['fin_m_pct']:4.2f}% | -y={prof_post['fin_y_dy_pct']:5.2f}% | y/s-={prof_post['init_y_s_pct']:5.2f}% | o-={prof_post['init_o_pct']:5.2f}% | qo-={prof_post['init_qo_pct']:5.2f}%")
    print(f"  True Line-Init (n={prof_true_init['count']:5d}): len={prof_true_init['mean_len']:.3f} | -m={prof_true_init['fin_m_pct']:4.2f}% | -y={prof_true_init['fin_y_dy_pct']:5.2f}% | y/s-={prof_true_init['init_y_s_pct']:5.2f}% | o-={prof_true_init['init_o_pct']:5.2f}% | qo-={prof_true_init['init_qo_pct']:5.2f}%")

    print(f"\nMulti-Paragraph Herbal Vertical Zones ({multi_para_herbal_folios} Folios):")
    print(f"  P_top (Flower/Leaf Zone, n={prof_herbal_top['count']:4d}): o-={prof_herbal_top['init_o_pct']:.2f}%, qo-={prof_herbal_top['init_qo_pct']:.2f}%, ch/sh-={prof_herbal_top['init_ch_sh_pct']:.2f}%, -in={prof_herbal_top['fin_in_pct']:.2f}%, -liq={prof_herbal_top['fin_liq_pct']:.2f}%")
    print(f"  P_bot (Root Zone,        n={prof_herbal_bot['count']:4d}): o-={prof_herbal_bot['init_o_pct']:.2f}%, qo-={prof_herbal_bot['init_qo_pct']:.2f}%, ch/sh-={prof_herbal_bot['init_ch_sh_pct']:.2f}%, -in={prof_herbal_bot['fin_in_pct']:.2f}%, -liq={prof_herbal_bot['fin_liq_pct']:.2f}%")
    print("  Top 6 P_top (Flower/Leaf) Enriched Words:", herbal_zone_words[:6])
    print("  Top 6 P_bot (Root) Enriched Words       :", herbal_zone_words[-6:][::-1])

    out = {
        "summary": {
            "total_drawing_intrusions": len(intrusion_pairs),
            "paired_folios_with_canopy_and_split": paired_folios,
            "role_transition_cosine_intrusion_vs_normal": round(role_transition_cos, 4),
            "multiword_constituent_bridges_across_drawing": len(multiword_const_bridges),
            "multiword_constituent_bridge_pct": round(len(multiword_const_bridges) / len(intrusion_pairs) * 100, 2),
            "canopy_mean_word_len": round(sum(canopy_word_lens) / len(canopy_word_lens), 3),
            "split_line_mean_word_len": round(sum(split_word_lens) / len(split_word_lens), 3),
            "multi_para_herbal_folios": multi_para_herbal_folios,
        },
        "position_profiles": {
            "true_interior": prof_interior,
            "pre_drawing_w_pre": prof_pre,
            "true_line_final": prof_true_fin,
            "post_drawing_w_post": prof_post,
            "true_line_initial": prof_true_init,
        },
        "herbal_vertical_plant_zones": {
            "p_top_flower_leaf": prof_herbal_top,
            "p_mid_stem": prof_herbal_mid,
            "p_bot_root": prof_herbal_bot,
            "top_enriched_words": herbal_zone_words[:15],
            "bot_enriched_words": herbal_zone_words[-15:][::-1],
        },
        "sample_constituent_bridges_across_drawing": multiword_const_bridges[:30],
    }
    OUT_JSON.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"\nSaved -> {OUT_JSON}")


if __name__ == "__main__":
    main()
