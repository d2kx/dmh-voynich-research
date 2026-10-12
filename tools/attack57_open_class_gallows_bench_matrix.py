#!/usr/bin/env python3
"""
Attack 57: The 8x6x8 Open-Class Gallows & Bench Paradigm Tensor (`75.99%` of the Voynich Manuscript)
====================================================================================================
Complements the 7x8 Closed-Class Function-Word Matrix (`Attack 55`, covering `98.16%` of the `8,700`
non-gallows, non-bench tokens) by factoring all `27,529` Gallows/Bench tokens (`75.99%` of the
entire manuscript) into a 3D Orthogonal Paradigm Tensor `[8 Prefixes] x [6 Core Classes] x [8 Suffixes]`:
  - Dimension 1 (8 Onset Prefixes):
      1. `ZERO` (`ø-` direct core onset: `chedy, shedy, kedy, tedy, cthy, pchedy`)
      2. `QO` (`qo-, q-`: `qokeedy, qokedy, qokaiin, qotedy, qokchy`)
      3. `O_VOW` (`o-, a-, e-, i-`: `okeey, okedy, okaiin, otedy, otaiin, opchedy`)
      4. `Y` (`y-`: `ykedy, ykeey, ytaiin, ychedy`)
      5. `D` (`d-, da-, do-`: `dchedy, dshedy, dkedy, dchor`)
      6. `S` (`s-, sa-, so-`: `schedy, sshedy, skedy, schor`)
      7. `L_APPL` (`l-, ol-, qol-`: `lchedy, lshedy, lkedy, olchedy, qolchey`)
      8. `R_OTHER` (`r-, ar-, or-, al-` or compound onset)
  - Dimension 2 (6 Core Consonant Classes):
      1. `CH` (Unplumed simplex bench `ch`)
      2. `SH` (Plumed simplex bench `sh`)
      3. `K_F` (Single-loop simplex gallows `k / f`)
      4. `T_P` (Double-loop / crossbar simplex gallows `t / p`)
      5. `KCH_CKH` (Single-loop gallows+bench complex `kch, fch, ksh, fsh, ckh, cfh`)
      6. `TCH_CTH` (Double-loop gallows+bench complex `tch, pch, tsh, psh, cth, cph`)
  - Dimension 3 (8 Inflectional Suffixes):
      1. `EDY` (`-eedy, -edy, -ody, -dy`)
      2. `EY_Y` (`-eey, -ey, -y`)
      3. `AIIN` (`-aiin, -ain, -iin, -in`)
      4. `OL` (`-ol`)
      5. `OR` (`-or`)
      6. `AL` (`-al`)
      7. `AR` (`-ar`)
      8. `AM_OTHER` (`-am, -om, -m` or bare/other coda)
"""

from __future__ import annotations

import json
import math
import random
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, List, Optional, Tuple

ROOT = Path(__file__).resolve().parents[1]
ZL_PATH = ROOT / "data" / "ZL3b-n.txt"
OUT_JSON = ROOT / "data" / "attack57_open_class_gallows_bench_matrix.json"

LOCUS_RE = re.compile(r"^<f([0-9]+[rv][0-9]*|Ros)\.([^,>]+),([^>]+)>\s*(.*)$")

PREFIXES_8 = ["ZERO", "QO", "O_VOW", "Y", "D", "S", "L_APPL", "R_OTHER"]
CORES_6 = ["CH", "SH", "K_F", "T_P", "KCH_CKH", "TCH_CTH"]
SUFFIXES_8 = ["EDY", "EY_Y", "AIIN", "OL", "OR", "AL", "AR", "AM_OTHER"]

KCH_COMPLEX = ("kch", "fch", "ksh", "fsh", "ckh", "cfh")
TCH_COMPLEX = ("tch", "pch", "tsh", "psh", "cth", "cph")


def clean_tokens(raw: str) -> List[str]:
    s = re.sub(r"\{[^}]*\}", "", raw)
    s = re.sub(r"\[([^:\]]+):[^\]]+\]", r"\1", s)
    s = s.replace("<%>", " ").replace("<$>", " ").replace("<->", " ")
    s = re.sub(r"<[^>]*>", " ", s)
    s = re.sub(r"@[0-9]+;", "", s)
    s = re.sub(r"[^a-zA-Z.\s]", "", s).lower()
    return [t for t in s.replace(".", " ").split() if t]


def has_gallows_or_bench(w: str) -> bool:
    return any(g in w for g in ("p", "f", "k", "t", "ch", "sh"))


def classify_8x6x8(w: str) -> Optional[Tuple[str, str, str]]:
    if not has_gallows_or_bench(w):
        return None

    # 1. Core Consonant Class (check complex gallows-bench first, then simplex gallows, then simplex bench)
    if any(c in w for c in KCH_COMPLEX):
        core = "KCH_CKH"
    elif any(c in w for c in TCH_COMPLEX):
        core = "TCH_CTH"
    elif "k" in w or "f" in w:
        core = "K_F"
    elif "t" in w or "p" in w:
        core = "T_P"
    elif "sh" in w:
        core = "SH"
    elif "ch" in w:
        core = "CH"
    else:
        return None

    # 2. Onset Prefix (before the first gallows or bench character)
    m_first = re.search(r"(kch|fch|ksh|fsh|ckh|cfh|tch|pch|tsh|psh|cth|cph|ch|sh|p|f|k|t)", w)
    onset_str = w[: m_first.start()] if m_first else ""
    if onset_str == "":
        pref = "ZERO"
    elif onset_str in ("qol", "ol") or onset_str.startswith("l"):
        pref = "L_APPL"
    elif onset_str.startswith("q"):
        pref = "QO"
    elif onset_str.startswith("y"):
        pref = "Y"
    elif onset_str.startswith("d"):
        pref = "D"
    elif onset_str.startswith("s"):
        pref = "S"
    elif onset_str[0] in ("o", "a", "e", "i") and "l" not in onset_str and "r" not in onset_str:
        pref = "O_VOW"
    else:
        pref = "R_OTHER"

    # 3. Inflectional Suffix
    if w.endswith(("eedy", "edy", "ody", "dy")):
        suf = "EDY"
    elif w.endswith(("eey", "ey", "y")):
        suf = "EY_Y"
    elif w.endswith(("aiin", "ain", "iin", "in")):
        suf = "AIIN"
    elif w.endswith("ol"):
        suf = "OL"
    elif w.endswith("or"):
        suf = "OR"
    elif w.endswith("al"):
        suf = "AL"
    elif w.endswith("ar"):
        suf = "AR"
    else:
        suf = "AM_OTHER"

    return (pref, core, suf)


def calc_mi(pairs: List[Tuple[str, str]]) -> float:
    n = len(pairs)
    if n == 0:
        return 0.0
    cx = Counter(x for x, _ in pairs)
    cy = Counter(y for _, y in pairs)
    cxy = Counter(pairs)
    mi = 0.0
    for (x, y), c in cxy.items():
        pxy = c / n
        px = cx[x] / n
        py = cy[y] / n
        mi += pxy * math.log2(pxy / (px * py))
    return mi


def main() -> None:
    lines_raw = ZL_PATH.read_text(encoding="utf-8", errors="replace").splitlines()
    total_tokens = 0
    gb_tokens = 0
    mapped_tokens = 0

    pref_counts = Counter()
    core_counts = Counter()
    suf_counts = Counter()
    pref_core_grid: Dict[str, Counter] = {p: Counter() for p in PREFIXES_8}
    core_suf_grid: Dict[str, Counter] = {c: Counter() for c in CORES_6}

    pc_pairs: List[Tuple[str, str]] = []
    cs_pairs: List[Tuple[str, str]] = []
    ps_pairs: List[Tuple[str, str]] = []

    for line in lines_raw:
        line = line.strip()
        if not line or line.startswith("#") or "." not in line.split(">")[0]:
            continue
        m = LOCUS_RE.match(line)
        if not m:
            continue
        toks = clean_tokens(m.group(4))
        for w in toks:
            total_tokens += 1
            if has_gallows_or_bench(w):
                gb_tokens += 1
                pcs = classify_8x6x8(w)
                if pcs:
                    mapped_tokens += 1
                    p, c, s = pcs
                    pref_counts[p] += 1
                    core_counts[c] += 1
                    suf_counts[s] += 1
                    pref_core_grid[p][c] += 1
                    core_suf_grid[c][s] += 1
                    pc_pairs.append((p, c))
                    cs_pairs.append((c, s))
                    ps_pairs.append((p, s))

    mi_pc = calc_mi(pc_pairs)
    mi_cs = calc_mi(cs_pairs)
    mi_ps = calc_mi(ps_pairs)

    rng = random.Random(57)
    p_list = [p for p, _ in pc_pairs]
    c_list = [c for _, c in pc_pairs]
    s_list = [s for _, s in cs_pairs]
    null_pc = []
    null_cs = []
    for _ in range(300):
        sc = c_list[:]
        ss = s_list[:]
        rng.shuffle(sc)
        rng.shuffle(ss)
        null_pc.append(calc_mi(list(zip(p_list, sc))))
        null_cs.append(calc_mi(list(zip(c_list, ss))))

    def z_val(obs: float, arr: List[float]) -> float:
        mu = sum(arr) / len(arr)
        sd = math.sqrt(sum((x - mu) ** 2 for x in arr) / len(arr)) or 1e-9
        return round((obs - mu) / sd, 2)

    z_pc = z_val(mi_pc, null_pc)
    z_cs = z_val(mi_cs, null_cs)

    result = {
        "summary": {
            "total_corpus_tokens": total_tokens,
            "gallows_bench_tokens": gb_tokens,
            "gb_corpus_share": round(gb_tokens / max(total_tokens, 1), 4),
            "mapped_8x6x8_tokens": mapped_tokens,
            "mapped_share_of_gb": round(mapped_tokens / max(gb_tokens, 1), 4),
            "mi_prefix_core_bits": round(mi_pc, 5),
            "z_prefix_core": z_pc,
            "mi_core_suffix_bits": round(mi_cs, 5),
            "z_core_suffix": z_cs,
            "mi_prefix_suffix_bits": round(mi_ps, 5),
        },
        "prefix_counts": dict(pref_counts),
        "core_counts": dict(core_counts),
        "suffix_counts": dict(suf_counts),
        "prefix_by_core_grid": {p: dict(pref_core_grid[p]) for p in PREFIXES_8},
        "core_by_suffix_grid": {c: dict(core_suf_grid[c]) for c in CORES_6},
    }

    OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print("=== ATTACK 57: THE 8x6x8 OPEN-CLASS GALLOWS & BENCH PARADIGM TENSOR ===")
    s = result["summary"]
    print(f"Gallows/Bench tokens: {s['gallows_bench_tokens']:,} / {s['total_corpus_tokens']:,} ({s['gb_corpus_share']*100:.2f}% of corpus)")
    print(f"Mapped into 8x6x8 tensor: {s['mapped_8x6x8_tokens']:,} / {s['gallows_bench_tokens']:,} ({s['mapped_share_of_gb']*100:.2f}% coverage!)")
    print(f"Mutual Information: I(Prefix;Core)={s['mi_prefix_core_bits']:.5f} bits (z={s['z_prefix_core']:+.2f}) | I(Core;Suffix)={s['mi_core_suffix_bits']:.5f} bits (z={s['z_core_suffix']:+.2f}) | I(Prefix;Suffix)={s['mi_prefix_suffix_bits']:.5f} bits")
    print("\nPrefix x Core Grid:")
    header = "Prefix   | " + " | ".join(f"{c:7s}" for c in CORES_6) + " | Total"
    print("  " + header)
    for p in PREFIXES_8:
        row_s = " | ".join(f"{pref_core_grid[p][c]:7d}" for c in CORES_6)
        print(f"  {p:8s} | {row_s} | {pref_counts[p]:5d}")
    print("\nCore x Suffix Grid:")
    header2 = "Core     | " + " | ".join(f"{sf:8s}" for sf in SUFFIXES_8) + " | Total"
    print("  " + header2)
    for c in CORES_6:
        row_s = " | ".join(f"{core_suf_grid[c][sf]:8d}" for sf in SUFFIXES_8)
        print(f"  {c:8s} | {row_s} | {core_counts[c]:5d}")


if __name__ == "__main__":
    main()
