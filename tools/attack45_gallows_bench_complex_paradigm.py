#!/usr/bin/env python3
"""
Attack 45: The Gallows-Bench Complex Paradigm (`[p/f/k/t]ch` vs `c[p/f/k/t]h`)
==============================================================================
Tests whether the two EVA notations for combined Gallows + Bench glyphs:
  - Sequential Gallows+Bench (`pch`, `fch`, `kch`, `tch`, `psh`, `fsh`, `ksh`, `tsh`)
  - Split Pedestal Bench+Gallows (`cph`, `cfh`, `ckh`, `cth`)
are complementary positional allographs of a single underlying consonant series:
  1. Positional Complementary Distribution inside the word:
     - Is `[p/f/k/t]ch` predominantly word-initial (or immediately after `o-/qo-/y-` onsets),
       whereas `c[p/f/k/t]h` is predominantly word-medial (between vowel/bench and suffix `-y/-edy/-ol/-or/-aiin`)?
     - Tested against 1,000 random position-preserving shuffles.
  2. Top-Line / Paragraph-Initial Allography (`pch/fch/cph/cfh` vs `kch/tch/ckh/cth`):
     - Do complex gallows-bench clusters obey the exact same Line-1 labial (`p/f`) vs interior coronal (`k/t`)
       allographic law as simplex gallows (`p/f` vs `k/t`), tested across 1,000 within-paragraph line shuffles?
  3. Lexical Twin Unification (`[p/f/k/t]ch <-> c[p/f/k/t]h` and `k/t/p/f` neutralization):
     - How many distinct word types collapse into identical canonical stems when `[p/f/k/t]ch` and `c[p/f/k/t]h`
       are unified, and how high is their distributional context cosine similarity?
"""

from __future__ import annotations

import json
import math
import random
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, List, Tuple

ROOT = Path(__file__).resolve().parents[1]
ZL_PATH = ROOT / "data" / "ZL3b-n.txt"
OUT_JSON = ROOT / "data" / "attack45_gallows_bench_complex_paradigm.json"

LOCUS_RE = re.compile(r"^<f([0-9]+[rv][0-9]*|Ros)\.([^,>]+),([^>]+)>\s*(.*)$")

SEQ_CLUSTERS = ("pch", "fch", "kch", "tch", "psh", "fsh", "ksh", "tsh")
PED_CLUSTERS = ("cph", "cfh", "ckh", "cth")


def clean_tokens(raw: str) -> List[str]:
    s = re.sub(r"\{[^}]*\}", "", raw)
    s = re.sub(r"\[([^:\]]+):[^\]]+\]", r"\1", s)
    s = s.replace("<%>", " ").replace("<$>", " ").replace("<->", " ")
    s = re.sub(r"<[^>]*>", " ", s)
    s = re.sub(r"@[0-9]+;", "", s)
    s = re.sub(r"[^a-zA-Z.\s]", "", s).lower()
    return [t for t in s.replace(".", " ").split() if t]


def unify_gallows_bench(w: str) -> str:
    """Normalize both [p/f/k/t][c/s]h and c[p/f/k/t]h to a unified KCH token `K`."""
    s = w
    for cl in ("pch", "fch", "kch", "tch", "psh", "fsh", "ksh", "tsh", "cph", "cfh", "ckh", "cth"):
        s = s.replace(cl, "K")
    return s


def main() -> None:
    lines_raw = ZL_PATH.read_text(encoding="utf-8", errors="replace").splitlines()
    paragraphs: List[List[List[str]]] = []
    cur_para: List[List[str]] = []
    all_words: List[str] = []
    prose_lines: List[List[str]] = []

    for line in lines_raw:
        line = line.strip()
        if not line or line.startswith("#") or "." not in line.split(">")[0]:
            continue
        m = LOCUS_RE.match(line)
        if not m:
            continue
        loc_tag = m.group(3)
        raw_text = m.group(4)
        toks = clean_tokens(raw_text)
        if not toks:
            continue
        all_words.extend(toks)
        if "P" in loc_tag:
            prose_lines.append(toks)
            is_new = loc_tag.startswith("@P") or "<%>" in raw_text
            if is_new:
                if cur_para:
                    paragraphs.append(cur_para)
                cur_para = [toks]
            else:
                cur_para.append(toks)
    if cur_para:
        paragraphs.append(cur_para)

    # 1. Word-Internal Positional Distribution of SEQ_CLUSTERS vs PED_CLUSTERS
    pos_counts = {
        "SEQ_[p/f/k/t]ch": Counter(),
        "PED_c[p/f/k/t]h": Counter(),
    }
    suffix_counts = {
        "SEQ_[p/f/k/t]ch": Counter(),
        "PED_c[p/f/k/t]h": Counter(),
    }

    seq_words = []
    ped_words = []

    for w in all_words:
        has_seq = any(cl in w for cl in SEQ_CLUSTERS)
        has_ped = any(cl in w for cl in PED_CLUSTERS)
        if has_seq:
            seq_words.append(w)
            for cl in SEQ_CLUSTERS:
                idx = w.find(cl)
                if idx != -1:
                    if idx == 0:
                        pos_counts["SEQ_[p/f/k/t]ch"]["word_initial (idx=0)"] += 1
                    elif w[:idx] in ("o", "qo", "y", "d", "s", "ol", "qok", "qot"):
                        pos_counts["SEQ_[p/f/k/t]ch"]["post_prefix (o-/qo-/y-/d-/s-)"] += 1
                    else:
                        pos_counts["SEQ_[p/f/k/t]ch"]["medial_other"] += 1
                    rest = w[idx + len(cl):]
                    suffix_counts["SEQ_[p/f/k/t]ch"][rest or "FINAL"] += 1
                    break
        if has_ped:
            ped_words.append(w)
            for cl in PED_CLUSTERS:
                idx = w.find(cl)
                if idx != -1:
                    if idx == 0:
                        pos_counts["PED_c[p/f/k/t]h"]["word_initial (idx=0)"] += 1
                    elif w[:idx] in ("o", "qo", "y", "d", "s", "ol", "ch", "sh", "och", "qoch"):
                        pos_counts["PED_c[p/f/k/t]h"]["post_prefix (o-/qo-/ch-/sh-)"] += 1
                    else:
                        pos_counts["PED_c[p/f/k/t]h"]["medial_other"] += 1
                    rest = w[idx + len(cl):]
                    suffix_counts["PED_c[p/f/k/t]h"][rest or "FINAL"] += 1
                    break

    # Compare suffix distributions between SEQ_[p/f/k/t]ch and PED_c[p/f/k/t]h
    all_sufs = set(suffix_counts["SEQ_[p/f/k/t]ch"].keys()) | set(suffix_counts["PED_c[p/f/k/t]h"].keys())
    dot = sum(suffix_counts["SEQ_[p/f/k/t]ch"][s] * suffix_counts["PED_c[p/f/k/t]h"][s] for s in all_sufs)
    n1 = math.sqrt(sum(v * v for v in suffix_counts["SEQ_[p/f/k/t]ch"].values())) or 1e-9
    n2 = math.sqrt(sum(v * v for v in suffix_counts["PED_c[p/f/k/t]h"].values())) or 1e-9
    suffix_cosine = dot / (n1 * n2)

    # Word-initial rate comparison
    seq_tot = sum(pos_counts["SEQ_[p/f/k/t]ch"].values())
    ped_tot = sum(pos_counts["PED_c[p/f/k/t]h"].values())
    seq_init_rate = pos_counts["SEQ_[p/f/k/t]ch"]["word_initial (idx=0)"] / max(seq_tot, 1)
    ped_init_rate = pos_counts["PED_c[p/f/k/t]h"]["word_initial (idx=0)"] / max(ped_tot, 1)

    # 2. Top-Line / Paragraph-Initial Labial (`pch/fch/cph/cfh`) vs Coronal (`kch/tch/ckh/cth`) Allography
    labial_cl = ("pch", "fch", "psh", "fsh", "cph", "cfh")
    coronal_cl = ("kch", "tch", "ksh", "tsh", "ckh", "cth")

    line1_lab = 0
    line1_cor = 0
    int_lab = 0
    int_cor = 0

    for para in paragraphs:
        if len(para) < 2:
            continue
        for li, ltoks in enumerate(para):
            for w in ltoks:
                is_lab = any(c in w for c in labial_cl)
                is_cor = any(c in w for c in coronal_cl)
                if li == 0:
                    if is_lab:
                        line1_lab += 1
                    if is_cor:
                        line1_cor += 1
                else:
                    if is_lab:
                        int_lab += 1
                    if is_cor:
                        int_cor += 1

    obs_line1_lab_share = line1_lab / max(line1_lab + line1_cor, 1)
    obs_int_lab_share = int_lab / max(int_lab + int_cor, 1)
    lift_line1_lab = obs_line1_lab_share / max(obs_int_lab_share, 1e-9)

    # Permutation test: shuffle lines within each paragraph 1,000 times
    rng = random.Random(45)
    null_line1_shares = []
    multi_paras = [p for p in paragraphs if len(p) >= 2]
    for _ in range(1000):
        l1_lab = 0
        l1_cor = 0
        for p in multi_paras:
            sp = p[:]
            rng.shuffle(sp)
            for w in sp[0]:
                if any(c in w for c in labial_cl):
                    l1_lab += 1
                if any(c in w for c in coronal_cl):
                    l1_cor += 1
        null_line1_shares.append(l1_lab / max(l1_lab + l1_cor, 1))
    mu_l1 = sum(null_line1_shares) / len(null_line1_shares)
    sd_l1 = math.sqrt(sum((x - mu_l1) ** 2 for x in null_line1_shares) / len(null_line1_shares)) or 1e-9
    z_line1_lab = (obs_line1_lab_share - mu_l1) / sd_l1

    # 3. Lexical Twin Unification: words differing ONLY by `[p/f/k/t]ch` vs `c[p/f/k/t]h`
    vocab_counts = Counter(all_words)
    unified_buckets: Dict[str, List[Tuple[str, int]]] = defaultdict(list)
    for w, cnt in vocab_counts.items():
        if any(c in w for c in SEQ_CLUSTERS + PED_CLUSTERS):
            u = unify_gallows_bench(w)
            unified_buckets[u].append((w, cnt))

    mixed_families = []
    types_before = 0
    types_after = 0
    for u, members in unified_buckets.items():
        types_before += len(members)
        types_after += 1
        has_s = any(any(c in m[0] for c in SEQ_CLUSTERS) for m in members)
        has_p = any(any(c in m[0] for c in PED_CLUSTERS) for m in members)
        if has_s and has_p:
            members_sorted = sorted(members, key=lambda x: -x[1])
            tot_cnt = sum(m[1] for m in members_sorted)
            mixed_families.append({
                "unified_stem": u,
                "total_tokens": tot_cnt,
                "member_count": len(members_sorted),
                "members": [{"word": m[0], "count": m[1]} for m in members_sorted[:8]],
            })
    mixed_families.sort(key=lambda x: -x["total_tokens"])

    result = {
        "summary": {
            "seq_cluster_tokens": len(seq_words),
            "ped_cluster_tokens": len(ped_words),
            "seq_word_initial_rate": round(seq_init_rate, 4),
            "ped_word_initial_rate": round(ped_init_rate, 4),
            "suffix_distribution_cosine_similarity": round(suffix_cosine, 4),
            "line1_labial_share": round(obs_line1_lab_share, 4),
            "interior_labial_share": round(obs_int_lab_share, 4),
            "line1_labial_lift": round(lift_line1_lab, 2),
            "line1_labial_z_score": round(z_line1_lab, 2),
            "gallows_bench_types_before_unification": types_before,
            "gallows_bench_types_after_unification": types_after,
            "type_reduction_rate": round(1.0 - (types_after / max(types_before, 1)), 4),
            "mixed_seq_and_ped_families_count": len(mixed_families),
        },
        "positional_distribution": {k: dict(v) for k, v in pos_counts.items()},
        "top_suffixes_seq": dict(suffix_counts["SEQ_[p/f/k/t]ch"].most_common(12)),
        "top_suffixes_ped": dict(suffix_counts["PED_c[p/f/k/t]h"].most_common(12)),
        "top_mixed_families": mixed_families[:25],
    }

    OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print("=== ATTACK 45: GALLOWS-BENCH COMPLEX PARADIGM ([p/f/k/t]ch vs c[p/f/k/t]h) ===")
    s = result["summary"]
    print(f"1. Positional Split: SEQ tokens={s['seq_cluster_tokens']} (word-initial={s['seq_word_initial_rate']*100:.2f}%) vs PED tokens={s['ped_cluster_tokens']} (word-initial={s['ped_word_initial_rate']*100:.2f}%)")
    print(f"   Suffix distribution cosine similarity between [p/f/k/t]ch and c[p/f/k/t]h: {s['suffix_distribution_cosine_similarity']:.4f}")
    print(f"2. Top-Line Labial Allography (pch/fch/cph/cfh): Line1={s['line1_labial_share']*100:.2f}% vs Interior={s['interior_labial_share']*100:.2f}% ({s['line1_labial_lift']}x lift, z={s['line1_labial_z_score']:+.2f})")
    print(f"3. Lexical Unification: {types_before} types -> {types_after} unified stems (-{s['type_reduction_rate']*100:.2f}%), with {len(mixed_families)} mixed SEQ<->PED families:")
    for mf in mixed_families[:10]:
        m_str = ", ".join(f"{m['word']}({m['count']})" for m in mf["members"][:6])
        print(f"   {mf['unified_stem']:10s} (tot={mf['total_tokens']:4d}): {m_str}")


if __name__ == "__main__":
    main()
