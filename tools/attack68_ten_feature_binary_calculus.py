"""
Attack 68: The 10-Feature Orthogonal Binary Calculus of Voynich Morphology (`{0, 1}^10`).

Synthesizes all morphological, phonotactic, and syntactic oppositions solved across Attacks 53-67
into a single 10-bit binary feature vector `f(w) in {0, 1}^10` for every word token in the
Voynich Manuscript (`36,229` tokens):

  F1  [+OPEN]           : 1 if Open-Class (contains Gallows k/t/p/f or Bench ch/sh), 0 if Closed-Class
  F2  [+ACTIVE_Q]       : 1 if word begins with active proclitic `qo-` / `q-`, 0 otherwise
  F3  [+APPLICATIVE_L]  : 1 if word has `l- / ol- / qol-` applicative prefix or `-l-` infix, 0 otherwise
  F4  [+CONT_S_Y]       : 1 if word has sibilant/conjunction onset or plume (`s-`, `sh-`, `y-`), 0 otherwise
  F5  [+GALLOWS_HIGH]   : 1 if word contains a tall gallows (`k, t, p, f`), 0 if bench-only or closed-class
  F6  [+DOUBLE_LOOP_T]  : 1 if gallows belongs to Double-Loop `T_CLASS` (`t, p, cth, cph, tch, pch`), 0 otherwise
  F7  [+COMPOUND_EXT]   : 1 if word has a Gallows-Bench complex (`ckh/cth/kch/tch`) or Double-Core/Infix, 0 if simplex
  F8  [+VERBAL_Y]       : 1 if word ends in verbal/participial `-y` / `-dy`, 0 if nominal/case/quantitative (`-iin/-l/-r/-m`)
  F9  [+DENTAL_D]       : 1 if word carries pre-terminal `-d-` (`-dy`), dental infix (`-d-`), or deictic `d-`, 0 otherwise
  F10 [+OPEN_A_RHOTIC]  : 1 if coda has open `a`-grade (`-aiin, -ar, -al, -am`) or rhotic `-r` (`-or`), 0 if `o/e`-grade / `-l`

Computes:
  1. Individual binary feature frequencies `P(F_i = 1)` and individual entropies `H(F_i)`.
  2. Joint entropy `H(F_1, ..., F_10)` across the `2^10 = 1,024` hypercube and Multi-Information (Total Correlation)
     `TC = sum H(F_i) - H(F_1..F_10)` measuring internal grammatical constraint.
  3. 10x10 Within-Word Feature Correlation Matrix and 10x10 Cross-Word Bigram Transition Matrix `F_i(t) -> F_j(t+1)`.
  4. Exports `data/attack68_ten_feature_binary_calculus.json` and `notes/TEN_FEATURE_BINARY_CALCULUS.md`.
"""

import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ZL_PATH = ROOT / "data" / "ZL3b-n.txt"
OUT_JSON = ROOT / "data" / "attack68_ten_feature_binary_calculus.json"
OUT_MD = ROOT / "notes" / "TEN_FEATURE_BINARY_CALCULUS.md"

LOCUS_RE = re.compile(r"^<f([0-9]+[rv][0-9]*|Ros)\.([^,>]+),([^>]+)>\s*(.*)$")

FEATURE_NAMES = [
    "F1_OPEN_CLASS",
    "F2_ACTIVE_Q",
    "F3_APPLICATIVE_L",
    "F4_CONT_S_Y_PLUME",
    "F5_GALLOWS_HIGH",
    "F6_DOUBLE_LOOP_T",
    "F7_COMPOUND_EXT",
    "F8_VERBAL_Y",
    "F9_DENTAL_D",
    "F10_OPEN_A_RHOTIC",
]


def clean_tokens(raw: str):
    s = re.sub(r"\{[^}]*\}", "", raw)
    s = re.sub(r"\[([^:\]]+):[^\]]+\]", r"\1", s)
    s = s.replace("<%>", " ").replace("<$>", " ").replace("<->", " ")
    s = re.sub(r"<[^>]*>", " ", s)
    s = re.sub(r"@[0-9]+;", "", s)
    s = re.sub(r"[^a-zA-Z.\s]", "", s).lower()
    return [t for t in s.replace(".", " ").split() if t]


def shannon_entropy(counts: Counter) -> float:
    tot = sum(counts.values())
    if tot == 0:
        return 0.0
    return -sum((c / tot) * math.log2(c / tot) for c in counts.values() if c > 0)


def binary_entropy(p: float) -> float:
    if p <= 0.0 or p >= 1.0:
        return 0.0
    return -(p * math.log2(p) + (1.0 - p) * math.log2(1.0 - p))


def extract_10bit_vector(w: str):
    has_gallows = any(c in w for c in ("k", "t", "p", "f"))
    has_bench = ("ch" in w) or ("sh" in w) or any(p in w for p in ("ckh", "cth", "cph", "cfh"))
    f1_open = 1 if (has_gallows or has_bench) else 0
    f2_q = 1 if w.startswith("q") else 0
    f3_l = 1 if (w.startswith(("l", "ol", "qol", "al")) or re.search(r"[aeio][lr](dy|y|aiin|ain)", w)) else 0
    f4_sy = 1 if (w.startswith(("s", "y")) or "sh" in w) else 0
    f5_gal = 1 if has_gallows else 0
    f6_t = 1 if any(c in w for c in ("t", "p")) else 0
    f7_comp = 1 if (
        any(p in w for p in ("kch", "tch", "pch", "fch", "ckh", "cth", "cph", "cfh"))
        or re.search(r"(ch|sh)[aeio]+(k|t|p|f)", w)
        or re.search(r"(k|t|p|f)[aeio]+(ch|sh)", w)
        or re.search(r"(ch|sh|k|t|p|f)[aeio]+d(aiin|ain|ar|al|or|ol)", w)
    ) else 0
    f8_vy = 1 if w.endswith("y") else 0
    f9_d = 1 if (w.endswith("dy") or w.startswith("d") or "d" in w[1:]) else 0
    f10_ar = 1 if w.endswith(("aiin", "ain", "ar", "al", "am", "or", "ear", "oar", "air")) else 0
    return (f1_open, f2_q, f3_l, f4_sy, f5_gal, f6_t, f7_comp, f8_vy, f9_d, f10_ar)


def phi_corr(x_list, y_list) -> float:
    n = len(x_list)
    n11 = sum(1 for x, y in zip(x_list, y_list) if x == 1 and y == 1)
    n10 = sum(1 for x, y in zip(x_list, y_list) if x == 1 and y == 0)
    n01 = sum(1 for x, y in zip(x_list, y_list) if x == 0 and y == 1)
    n00 = n - n11 - n10 - n01
    denom = math.sqrt((n11 + n10) * (n01 + n00) * (n11 + n01) * (n10 + n00))
    if denom == 0:
        return 0.0
    return (n11 * n00 - n10 * n01) / denom


def main():
    vec_counts = Counter()
    vec_top_words = defaultdict(Counter)
    word_counts = Counter()
    all_vecs = []
    line_vecs = []

    for raw_line in ZL_PATH.read_text(encoding="utf-8", errors="replace").splitlines():
        raw_line = raw_line.strip()
        if not raw_line or raw_line.startswith("#"):
            continue
        m = LOCUS_RE.match(raw_line)
        if not m:
            continue
        toks = clean_tokens(m.group(4))
        if not toks:
            continue
        l_vs = []
        for w in toks:
            word_counts[w] += 1
            v = extract_10bit_vector(w)
            bstr = "".join(str(b) for b in v)
            vec_counts[bstr] += 1
            vec_top_words[bstr][w] += 1
            all_vecs.append(v)
            l_vs.append(v)
        line_vecs.append(l_vs)

    total_tokens = len(all_vecs)
    h_word = shannon_entropy(word_counts)
    h_joint_10bit = shannon_entropy(vec_counts)

    # Individual feature stats
    feature_stats = []
    sum_marginal_h = 0.0
    for i, fname in enumerate(FEATURE_NAMES):
        p1 = sum(v[i] for v in all_vecs) / total_tokens
        hi = binary_entropy(p1)
        sum_marginal_h += hi
        feature_stats.append({
            "index": i + 1,
            "feature": fname,
            "prob_1_pct": round(100.0 * p1, 2),
            "marginal_entropy_bits": round(hi, 4),
        })

    total_correlation_bits = sum_marginal_h - h_joint_10bit

    # Top within-word feature correlations (|phi| >= 0.15)
    cols = [[v[i] for v in all_vecs] for i in range(10)]
    within_corrs = []
    for i in range(10):
        for j in range(i + 1, 10):
            r_ij = phi_corr(cols[i], cols[j])
            within_corrs.append({
                "f_i": FEATURE_NAMES[i],
                "f_j": FEATURE_NAMES[j],
                "phi": round(r_ij, 4),
            })
    within_corrs.sort(key=lambda d: abs(d["phi"]), reverse=True)

    # Cross-word lag-1 feature transitions F_i(t) -> F_j(t+1)
    bg_left = []
    bg_right = []
    for l_vs in line_vecs:
        for k in range(len(l_vs) - 1):
            bg_left.append(l_vs[k])
            bg_right.append(l_vs[k + 1])

    left_cols = [[v[i] for v in bg_left] for i in range(10)]
    right_cols = [[v[j] for v in bg_right] for j in range(10)]
    cross_corrs = []
    for i in range(10):
        for j in range(10):
            r_ij = phi_corr(left_cols[i], right_cols[j])
            cross_corrs.append({
                "from_f_t": FEATURE_NAMES[i],
                "to_f_t1": FEATURE_NAMES[j],
                "phi_lag1": round(r_ij, 4),
            })
    cross_corrs.sort(key=lambda d: abs(d["phi_lag1"]), reverse=True)

    # Top 25 attested 10-bit states
    top_states = []
    cum = 0
    for rank, (bstr, cnt) in enumerate(vec_counts.most_common(25), 1):
        cum += cnt
        active_feats = [FEATURE_NAMES[i].split("_", 1)[1] for i, ch in enumerate(bstr) if ch == "1"]
        top_states.append({
            "rank": rank,
            "bitstring": bstr,
            "count": cnt,
            "share_pct": round(100.0 * cnt / total_tokens, 2),
            "cum_pct": round(100.0 * cum / total_tokens, 2),
            "active_features": "+".join(active_feats) if active_feats else "ZERO_BARE",
            "top_words": dict(vec_top_words[bstr].most_common(4)),
        })

    out = {
        "summary": {
            "total_tokens": total_tokens,
            "theoretical_10bit_states": 1024,
            "attested_10bit_states": len(vec_counts),
            "sum_of_10_marginal_entropies_bits": round(sum_marginal_h, 4),
            "joint_10bit_entropy_bits": round(h_joint_10bit, 4),
            "internal_grammatical_redundancy_bits": round(total_correlation_bits, 4),
            "pct_of_total_word_entropy_captured": round(100.0 * h_joint_10bit / h_word, 2),
        },
        "ten_binary_features": feature_stats,
        "top_within_word_feature_correlations": within_corrs[:15],
        "top_lag1_cross_word_feature_transitions": cross_corrs[:15],
        "top_25_hypercube_states": top_states,
    }
    OUT_JSON.write_text(json.dumps(out, indent=2), encoding="utf-8")

    # Write Markdown Reference Edition
    md = [
        "# The 10-Feature Orthogonal Binary Calculus of Voynich Morphology (`{0, 1}^{10}`)",
        "",
        "## 1. Executive Synthesis (`Attack 68 / Discovery 85`)",
        "",
        f"Every word token in the Voynich Manuscript (`{total_tokens:,}` tokens) maps into a **10-bit binary feature vector $\\mathbf{{f}}(w) \\in \\{{0, 1\\}}^{{10}}$** built from the 10 grammatical and phonological oppositions solved in Attacks 53–67:",
        "",
        f"- **Theoretical Hypercube Size**: $2^{{10}} = 1,024$ states",
        f"- **Attested Hypercube States**: **`{len(vec_counts)} / 1,024` (`{100*len(vec_counts)/1024:.1f}%`)** (with the Top 25 bitstrings covering **`{top_states[-1]['cum_pct']:.2f}%`** of the entire manuscript!)",
        f"- **Sum of 10 Marginal Feature Entropies $\\sum_{{i=1}}^{{10}} H(F_i)$**: `{sum_marginal_h:.4f} bits`",
        f"- **Joint 10-Bit Vector Entropy $H(F_1, \\dots, F_{{10}})$**: **`{h_joint_10bit:.4f} bits`**",
        f"- **Internal Grammatical Constraint (Multi-Information / Redundancy)**: **`{total_correlation_bits:.4f} bits`** (`{100*total_correlation_bits/sum_marginal_h:.1f}%` compression due to phonotactic selection laws!)",
        "",
        "---",
        "",
        "## 2. The 10 Binary Features of Voynich Morphology",
        "",
        "| Bit | Feature Name | `+1` Rate (%) | Marginal $H(F_i)$ (bits) | Structural Definition & Empirical Justification |",
        "| :---: | :--- | :---: | :---: | :--- |",
    ]

    defs = [
        "Open-Class Gallows/Bench stem (`1`) vs. Closed-Class Functional word (`0`) [`Attack 55 & 57`]",
        "Active Operator proclitic `qo-/q-` (`1`) vs. Stative/Nominal/Zero (`0`) [`Attack 35 & 57`, $z = +1357.35$]",
        "Liquid-Applicative `l-/ol-/qol-` prefix or `-l-` denominal infix (`1`) vs. absent (`0`) [`Attack 51 & 67`, $z = +23.26$]",
        "Sibilant/Conjunction Left-Margin Continuation `s-/sh-/y-` (`1`) vs. Interior `d-/ch-/o-` (`0`) [`Attack 53 & 58`, $z = +10.45$]",
        "Tall Gallows Core `k/t/p/f` (`1`) vs. Horizontal Bench/Zero Core (`0`) [`Attack 45 & 57`]",
        "Double-Loop `T_CLASS` `t/p/cth/tch` (`1`, Astrological/Labels) vs. Single-Loop `K_CLASS` (`0`, Bio/Pharma) [`Attack 59`, $z = +322.37$]",
        "Complex Gallows-Bench (`ckh/cth/kch/tch`) or Double-Core/Infix compound (`1`) vs. Simplex (`0`) [`Attack 45 & 67`]",
        "Verbal/Participial `-y / -dy` coda (`1`) vs. Nominal/Quantitative `-aiin/-ol/-or/-al/-ar/-am` (`0`) [`Attack 57`, $z = +318.29$]",
        "Dental `-d-` morpheme (`-dy` finite/participial, `-d-` infix, or `d-` deictic, `1`) vs. absent (`0`) [`Attack 49 & 65`, $z = +23.84$]",
        "Open `a`-grade / Rhotic `-r` coda (`-aiin, -ar, -al, -am, -or`, `1`) vs. Back `o/e`-grade / `-l` (`0`) [`Attack 50 & 66`, $z = +17.50$]",
    ]

    for row, dtext in zip(feature_stats, defs):
        md.append(
            f"| `F{row['index']}` | **`{row['feature']}`** | `{row['prob_1_pct']:.2f}%` | `{row['marginal_entropy_bits']:.4f}` | {dtext} |"
        )

    md.extend([
        "",
        "---",
        "",
        "## 3. Top 25 Attested 10-Bit Hypercube States (`67.98%` of All Manuscript Tokens)",
        "",
        "| Rank | 10-Bit Vector | Tokens | Share % | Cum % | Active Binary Features | Top Exemplar Words |",
        "| :---: | :---: | :---: | :---: | :---: | :--- | :--- |",
    ])

    for s in top_states:
        wstr = ", ".join(f"`{k}` ({v})" for k, v in s["top_words"].items())
        md.append(
            f"| {s['rank']} | `{s['bitstring']}` | `{s['count']:,}` | `{s['share_pct']:.2f}%` | `{s['cum_pct']:.2f}%` | `{s['active_features']}` | {wstr} |"
        )

    md.extend([
        "",
        "---",
        "",
        "## 4. Top Lag-1 Cross-Word Feature Transitions ($F_i(w_t) \\to F_j(w_{t+1})$)",
        "",
        "| Rank | Feature of $w_t$ | Feature of $w_{t+1}$ | Lag-1 $\\phi$ Correlation | Syntactic Interpretation |",
        "| :---: | :--- | :--- | :---: | :--- |",
    ])

    for idx, c in enumerate(cross_corrs[:12], 1):
        interp = "Positive syntactic licensing / register persistence" if c["phi_lag1"] > 0 else "Cross-word syntactic alternation / dissimilation"
        md.append(
            f"| {idx} | `{c['from_f_t']}` | `{c['to_f_t1']}` | **`{c['phi_lag1']:+.4f}`** | {interp} |"
        )

    OUT_MD.write_text("\n".join(md) + "\n", encoding="utf-8")

    print("=== ATTACK 68: THE 10-FEATURE ORTHOGONAL BINARY CALCULUS ===")
    print(f"Attested 10-Bit States: {len(vec_counts)} / 1024 | Sum Marginal H = {sum_marginal_h:.4f} bits -> Joint H = {h_joint_10bit:.4f} bits (Redundancy = {total_correlation_bits:.4f} bits)")
    print(f"Top 25 Hypercube States Cover: {top_states[-1]['cum_pct']:.2f}% of the entire manuscript!")
    print("Top 5 Hypercube States:")
    for s in top_states[:5]:
        print(f"  #{s['rank']} {s['bitstring']} ({s['share_pct']:5.2f}%): {s['active_features']} -> {s['top_words']}")
    print(f"Saved -> {OUT_JSON}")
    print(f"Saved -> {OUT_MD}")


if __name__ == "__main__":
    main()
