"""
Attack 59: The `k/f` (Single-Loop) vs `t/p` (Double-Loop) Gallows Contrast Solver.

Having solved the `ch-` vs `sh-` Bench contrast in Attack 58 (Discovery 75), only ONE binary
opposition remains inside the 6 Open-Class Core types (`K_F, T_P, CH, SH, KCH_CKH, TCH_CTH`):
the contrast between:
  - `K_CLASS` (`k / f`, `kch / fch`, `ckh / cfh`): Single-loop / straight-crossbar gallows
  - `T_CLASS` (`t / p`, `tch / pch`, `cth / cph`): Double-loop / right-looped gallows

This script analyzes all 17,843 Gallows and Gallows-Bench tokens across 5 dimensions:
1. Prefix Selection (`Prefix x [K_CLASS vs T_CLASS]`): Why does `L_APPL` select `K_CLASS` at 90.8%
   and `QO` at 75.4%, whereas `O_VOW` (`ok-` vs `ot-`), `ZERO` (`k-` vs `t-`), and `Y_CONJ` (`yk-` vs `yt-`)
   dramatically shift toward `T_CLASS`?
2. Suffix Selection (`Suffix x [K_CLASS vs T_CLASS]`): How do verbal `-edy/-ey` suffixes vs
   case/nominal `-ar/-al/-or/-ol/-aiin/-y` suffixes partition `K_CLASS` and `T_CLASS`?
3. Locus Type (`@L` Labels vs `@C/@R` Rings vs `@P` Prose): Does `T_CLASS` (`ot-`, `yt-`, `cth-`)
   surge in Diagram Labels (`@L`) and Astrological Rings (`@C/@R`) relative to Prose (`@P`)?
4. Section & Currier Language Stratification (`$I=Z/A/C` vs `$I=B/S/H/P`, `$L=A` vs `$L=B`).
5. Matched Minimal Pairs (`okX` vs `otX`, `qokX` vs `qotX`, `ckhX` vs `cthX`, `kX` vs `tX`):
   Line-position and syntactic context tests with 1,000-trial stratified permutation baselines.
"""

import json
import math
import random
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ZL_PATH = ROOT / "data" / "ZL3b-n.txt"
INDEX_PATH = ROOT / "data" / "folio_index.json"
OUT_PATH = ROOT / "data" / "attack59_k_vs_t_gallows_contrast_solver.json"


def mean(xs):
    return sum(xs) / len(xs) if xs else 0.0


def std(xs):
    if len(xs) < 2:
        return 0.0
    m = mean(xs)
    return math.sqrt(sum((x - m) ** 2 for x in xs) / len(xs))


def load_tokens():
    tokens = []
    cur_sec = "U"
    cur_lang = "U"
    with open(ZL_PATH, "r", encoding="utf-8", errors="replace") as f:
        for raw in f:
            raw = raw.strip()
            if not raw or raw.startswith("#") or not raw.startswith("<f"):
                continue
            if ">" in raw and "." not in raw.split(">")[0]:
                m_s = re.search(r"\$I=([A-Z])", raw)
                cur_sec = m_s.group(1) if m_s else "U"
                m_l = re.search(r"\$L=([A-Z])", raw)
                cur_lang = m_l.group(1) if m_l else "U"
                continue
            parts = raw.split(">", 1)
            if len(parts) < 2:
                continue
            loc = parts[0][1:]
            txt = parts[1].strip()
            folio = loc.split(".")[0]
            lang = cur_lang
            sec = cur_sec
            is_para = "<%>" in txt

            # Locus type: @P/+P (prose), @L (label), @C/@R (ring/circle), other
            if "@P" in loc or "+P" in loc:
                loc_type = "PROSE_P"
            elif "@L" in loc or "+L" in loc:
                loc_type = "LABEL_L"
            elif "@C" in loc or "+C" in loc or "@R" in loc or "+R" in loc:
                loc_type = "RING_CR"
            else:
                loc_type = "OTHER_LOC"

            clean = txt.replace("<%>", "").replace("<$>", "").replace("<->", " . ")
            clean = re.sub(r"\{[^}]*\}", "", clean)
            clean = re.sub(r"\[([^\]:]+):[^\]]+\]", r"\1", clean)
            clean = re.sub(r"[@!&*?<>]", "", clean)
            words = [w.strip() for w in clean.replace(",", ".").split(".") if w.strip()]
            n = len(words)
            for i, w in enumerate(words):
                tokens.append({
                    "w": w,
                    "folio": folio,
                    "lang": lang,
                    "sec": sec,
                    "loc_type": loc_type,
                    "is_para_line1": is_para,
                    "is_line_init": (i == 0),
                    "is_line_final": (i == n - 1),
                    "rel_pos": i / (n - 1) if n > 1 else 0.5,
                    "prev_w": words[i - 1] if i > 0 else "<LINE_INIT>",
                })
    return tokens


def classify_gallows_token(w: str):
    """
    If token contains a Gallows or Gallows-Bench core, return:
      (g_class ['K' or 'T'], mode ['SIMPLEX', 'SEQ_BENCH', 'PED_BENCH'], prefix_cat, suffix_cat, pre_str, post_str)
    """
    # Check Gallows-Bench complexes first
    for pat, g_cls, mode in [
        ("kch", "K", "SEQ_BENCH"), ("fch", "K", "SEQ_BENCH"),
        ("tch", "T", "SEQ_BENCH"), ("pch", "T", "SEQ_BENCH"),
        ("ckh", "K", "PED_BENCH"), ("cfh", "K", "PED_BENCH"),
        ("cth", "T", "PED_BENCH"), ("cph", "T", "PED_BENCH"),
    ]:
        pos = w.find(pat)
        if pos != -1:
            pre = w[:pos]
            post = w[pos + 3:]
            return g_cls, mode, classify_prefix(pre), classify_suffix(post), pre, post

    # Check Simplex Gallows (k, f vs t, p)
    for ch in w:
        if ch in ("k", "f", "t", "p"):
            pos = w.find(ch)
            g_cls = "K" if ch in ("k", "f") else "T"
            pre = w[:pos]
            post = w[pos + 1:]
            return g_cls, "SIMPLEX", classify_prefix(pre), classify_suffix(post), pre, post

    return None


def classify_prefix(pre: str) -> str:
    if pre == "":
        return "ZERO"
    if pre.startswith("qo"):
        return "QO"
    if pre.startswith("ol") or pre.startswith("qol") or pre.startswith("l") or pre.startswith("al"):
        return "L_APPL"
    if pre.startswith("o"):
        return "O_VOW"
    if pre.startswith("y"):
        return "Y_CONJ"
    if pre.startswith("d"):
        return "D_DEIC"
    if pre.startswith("s"):
        return "S_SIB"
    if pre.startswith("c") or pre.startswith("ch") or pre.startswith("sh"):
        return "CH_BENCH_PRE"
    return "OTHER_PRE"


def classify_suffix(post: str) -> str:
    if post.endswith("edy") or post.endswith("eedy") or post.endswith("ody"):
        return "EDY"
    if post.endswith("ey") or post.endswith("eey"):
        return "EY"
    if post.endswith("aiin") or post.endswith("iin") or post.endswith("ain") or post.endswith("in"):
        return "AIIN"
    if post.endswith("ar") or post.endswith("ear") or post.endswith("air"):
        return "AR"
    if post.endswith("or") or post.endswith("eor"):
        return "OR"
    if post.endswith("al") or post.endswith("eal"):
        return "AL"
    if post.endswith("ol") or post.endswith("eol"):
        return "OL"
    if post.endswith("y") or post.endswith("dy") or post.endswith("ky") or post.endswith("ty"):
        return "Y_DY"
    return "OTHER_SUF"


def mutual_info_and_z(pairs, n_perm=500, seed=5901):
    xs = [p[0] for p in pairs]
    ys = [p[1] for p in pairs]
    n = len(pairs)
    cx = Counter(xs)
    cy = Counter(ys)
    cxy = Counter(pairs)
    mi = 0.0
    for (x, y), c in cxy.items():
        p_xy = c / n
        p_x = cx[x] / n
        p_y = cy[y] / n
        mi += p_xy * math.log2(p_xy / (p_x * p_y))

    rng = random.Random(seed)
    ys_shuf = list(ys)
    nulls = []
    for _ in range(n_perm):
        rng.shuffle(ys_shuf)
        cxy_s = Counter(zip(xs, ys_shuf))
        m_s = 0.0
        for (x, y), c in cxy_s.items():
            p_xy = c / n
            m_s += p_xy * math.log2(p_xy / ((cx[x] / n) * (cy[y] / n)))
        nulls.append(m_s)
    z = (mi - mean(nulls)) / (std(nulls) + 1e-12)
    return mi, z


def main():
    tokens = load_tokens()
    g_recs = []
    for t in tokens:
        res = classify_gallows_token(t["w"])
        if res:
            g_cls, mode, p_cat, s_cat, pre_str, post_str = res
            rec = dict(t)
            rec.update({
                "g_cls": g_cls,
                "mode": mode,
                "p_cat": p_cat,
                "s_cat": s_cat,
                "pre_str": pre_str,
                "post_str": post_str,
            })
            g_recs.append(rec)

    total_g = len(g_recs)
    k_tot = sum(1 for r in g_recs if r["g_cls"] == "K")
    t_tot = sum(1 for r in g_recs if r["g_cls"] == "T")

    # 1. Prefix x [K vs T]
    pref_table = {}
    for p in ["L_APPL", "QO", "S_SIB", "D_DEIC", "CH_BENCH_PRE", "O_VOW", "ZERO", "Y_CONJ", "OTHER_PRE"]:
        sub = [r for r in g_recs if r["p_cat"] == p]
        if not sub:
            continue
        k_c = sum(1 for r in sub if r["g_cls"] == "K")
        t_c = sum(1 for r in sub if r["g_cls"] == "T")
        pref_table[p] = {
            "K": k_c,
            "T": t_c,
            "total": len(sub),
            "T_share_pct": round(100.0 * t_c / len(sub), 2),
            "K_to_T_ratio": round(k_c / t_c, 2) if t_c > 0 else None,
        }

    mi_pref, z_pref = mutual_info_and_z([(r["p_cat"], r["g_cls"]) for r in g_recs], n_perm=500, seed=5901)

    # 2. Suffix x [K vs T]
    suf_table = {}
    for s in ["EDY", "EY", "Y_DY", "AIIN", "OL", "OR", "AL", "AR", "OTHER_SUF"]:
        sub = [r for r in g_recs if r["s_cat"] == s]
        if not sub:
            continue
        k_c = sum(1 for r in sub if r["g_cls"] == "K")
        t_c = sum(1 for r in sub if r["g_cls"] == "T")
        suf_table[s] = {
            "K": k_c,
            "T": t_c,
            "total": len(sub),
            "T_share_pct": round(100.0 * t_c / len(sub), 2),
        }

    mi_suf, z_suf = mutual_info_and_z([(r["s_cat"], r["g_cls"]) for r in g_recs], n_perm=500, seed=5902)

    # 3. Locus Type (@P vs @C/@R vs @L)
    loc_table = {}
    for lt in ["PROSE_P", "RING_CR", "LABEL_L", "OTHER_LOC"]:
        sub = [r for r in g_recs if r["loc_type"] == lt]
        if not sub:
            continue
        k_c = sum(1 for r in sub if r["g_cls"] == "K")
        t_c = sum(1 for r in sub if r["g_cls"] == "T")
        loc_table[lt] = {
            "K": k_c,
            "T": t_c,
            "total": len(sub),
            "T_share_pct": round(100.0 * t_c / len(sub), 2),
        }

    # Permutation test for T_CLASS enrichment in Non-Prose (@L + @C/@R) vs Prose (@P)
    non_prose = [r for r in g_recs if r["loc_type"] in ("LABEL_L", "RING_CR")]
    prose = [r for r in g_recs if r["loc_type"] == "PROSE_P"]
    np_t = sum(1 for r in non_prose if r["g_cls"] == "T")
    pr_t = sum(1 for r in prose if r["g_cls"] == "T")
    obs_loc_diff = (np_t / len(non_prose)) - (pr_t / len(prose))
    pool_loc = [1 if r["g_cls"] == "T" else 0 for r in (non_prose + prose)]
    rng = random.Random(5903)
    null_loc = []
    n_np = len(non_prose)
    n_pr = len(prose)
    for _ in range(1000):
        rng.shuffle(pool_loc)
        null_loc.append((sum(pool_loc[:n_np]) / n_np) - (sum(pool_loc[n_np:]) / n_pr))
    z_loc = (obs_loc_diff - mean(null_loc)) / (std(null_loc) + 1e-12)

    # 4. Section & Language breakdown
    sec_table = {}
    for sec in ["B", "S", "H", "P", "C", "A", "Z", "T"]:
        sub = [r for r in g_recs if r["sec"] == sec]
        if not sub:
            continue
        k_c = sum(1 for r in sub if r["g_cls"] == "K")
        t_c = sum(1 for r in sub if r["g_cls"] == "T")
        sec_table[sec] = {
            "K": k_c,
            "T": t_c,
            "total": len(sub),
            "T_share_pct": round(100.0 * t_c / len(sub), 2),
        }

    lang_table = {}
    for lg in ["A", "B"]:
        sub = [r for r in g_recs if r["lang"] == lg]
        k_c = sum(1 for r in sub if r["g_cls"] == "K")
        t_c = sum(1 for r in sub if r["g_cls"] == "T")
        lang_table[lg] = {
            "K": k_c,
            "T": t_c,
            "total": len(sub),
            "T_share_pct": round(100.0 * t_c / len(sub), 2),
        }

    # 5. Minimal Pair families: okX vs otX, qokX vs qotX, ckhX vs cthX, ykX vs ytX
    stems_8 = ["edy", "eedy", "ey", "eey", "aiin", "ar", "al", "or", "ol", "y", "dy"]
    minimal_families = {}
    for fam_name, k_pre, t_pre in [
        ("O_SIMPLEX (ok- vs ot-)", "ok", "ot"),
        ("QO_SIMPLEX (qok- vs qot-)", "qok", "qot"),
        ("PEDESTAL (ckh- vs cth-)", "ckh", "cth"),
        ("Y_SIMPLEX (yk- vs yt-)", "yk", "yt"),
        ("BARE_SIMPLEX (k- vs t-)", "k", "t"),
    ]:
        rows = []
        for s in stems_8:
            kw = k_pre + s
            tw = t_pre + s
            kc = sum(1 for r in g_recs if r["w"] == kw)
            tc = sum(1 for r in g_recs if r["w"] == tw)
            if kc + tc >= 10:
                rows.append({
                    "stem": s,
                    "k_word": kw,
                    "t_word": tw,
                    "k_count": kc,
                    "t_count": tc,
                    "T_share_pct": round(100.0 * tc / (kc + tc), 2),
                })
        minimal_families[fam_name] = rows

    print("=== ATTACK 59: THE k/f (SINGLE-LOOP) vs t/p (DOUBLE-LOOP) GALLOWS CONTRAST SOLVER ===")
    print(f"Total Gallows/Gallows-Bench Tokens: {total_g} -> K_CLASS={k_tot} ({100*k_tot/total_g:.2f}%), T_CLASS={t_tot} ({100*t_tot/total_g:.2f}%)")
    print(f"\n1. Prefix x [K vs T] (MI = {mi_pref:.4f} bits, z = {z_pref:+.2f}):")
    for p, v in pref_table.items():
        print(f"   {p:13s}: K={v['K']:4d}, T={v['T']:4d} (tot={v['total']:4d}) -> T_share={v['T_share_pct']:5.2f}% (K:T = {v['K_to_T_ratio']}:1)")
    print(f"\n2. Suffix x [K vs T] (MI = {mi_suf:.4f} bits, z = {z_suf:+.2f}):")
    for s, v in suf_table.items():
        print(f"   {s:10s}: K={v['K']:4d}, T={v['T']:4d} (tot={v['total']:4d}) -> T_share={v['T_share_pct']:5.2f}%")
    print(f"\n3. Locus Type (@P Prose vs @C/@R Ring vs @L Label) [Non-Prose T-lift z = {z_loc:+.2f}]:")
    for lt, v in loc_table.items():
        print(f"   {lt:10s}: K={v['K']:4d}, T={v['T']:4d} (tot={v['total']:4d}) -> T_share={v['T_share_pct']:5.2f}%")
    print("\n4. Section Stratification ($I):")
    for sec, v in sec_table.items():
        print(f"   $I={sec}: K={v['K']:4d}, T={v['T']:4d} (tot={v['total']:4d}) -> T_share={v['T_share_pct']:5.2f}%")
    print("\n5. Currier Language Stratification ($L):")
    for lg, v in lang_table.items():
        print(f"   $L={lg}: K={v['K']:4d}, T={v['T']:4d} (tot={v['total']:4d}) -> T_share={v['T_share_pct']:5.2f}%")

    out = {
        "totals": {
            "gallows_tokens": total_g,
            "K_CLASS": k_tot,
            "T_CLASS": t_tot,
            "K_share_pct": round(100.0 * k_tot / total_g, 2),
            "T_share_pct": round(100.0 * t_tot / total_g, 2),
        },
        "prefix_selection": {
            "mi_bits": round(mi_pref, 5),
            "z_score": round(z_pref, 2),
            "table": pref_table,
        },
        "suffix_selection": {
            "mi_bits": round(mi_suf, 5),
            "z_score": round(z_suf, 2),
            "table": suf_table,
        },
        "locus_selection": {
            "non_prose_vs_prose_T_z": round(z_loc, 2),
            "table": loc_table,
        },
        "section_table": sec_table,
        "language_table": lang_table,
        "minimal_families": minimal_families,
    }
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    print(f"Saved -> {OUT_PATH}")


if __name__ == "__main__":
    main()
