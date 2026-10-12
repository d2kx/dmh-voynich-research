"""
Attack 61: The 6-Way Internal Stem Nucleus Solver (`-0-`, `-e-`, `-ee-`, `-o-`, `-eo-`, `-a-`).

In Attack 60 (Discovery 77), assigning each word to its Dual-Matrix Cell (`[Prefix x Core x Coda]`,
419 attested cells covering 99.73% of the manuscript) explained 68.09% (7.3334 bits) of total
unigram word entropy H(Word) = 10.7699 bits, leaving H(Word | Cell) = 3.4365 bits.

What accounts for the variation INSIDE a single Dual-Matrix cell?
For example, inside cell `OPEN:QO:K_F:EDY` we find:
  - `qokdy`   (nucleus = ZERO_V `-0-`)
  - `qokedy`  (nucleus = E1 `-e-`)
  - `qokeedy` (nucleus = E2 `-ee-`)
  - `qokody`  (nucleus = O_VOW `-o-`)
  - `qokeody` (nucleus = EO_DIPH `-eo-`)
And inside `OPEN:ZERO:CH:EDY` we find:
  - `chdy`    (ZERO_V)
  - `chedy`   (E1)
  - `cheedy`  (E2)
  - `chody`   (O_VOW)
  - `cheody`  (EO_DIPH)

This script tests three core hypotheses across all 27,529 Open-Class tokens:
1. Core-Length / Weight Compensation (`E1` vs `E2` vs `ZERO_V`):
   Why do Simplex Gallows (`qok-`, `ok-`) strongly prefer geminate `E2` (`qokeedy = 303`, `qokeey = 310`,
   `okeey = 175`), whereas Simplex Bench (`ch-`, `sh-`) prefers single `E1` (`chedy = 501` vs `cheedy = 55`,
   `shedy = 428` vs `sheedy = 74`), and Complex Pedestal/Sequential (`ckh-`, `cth-`, `kch-`, `tch-`)
   prefers `ZERO_V` or `E1` (`cthy = 98`, `ckhy = 67`, `chdy = 145`)?
2. Scribe-Hand (`$H=1..5`) & Currier Language (`$L=A` vs `$L=B`) Dialect Conditioning of `-o-/-eo-` vs `-e-/-ee-`:
   Does `-o- / -eo-` (`chody, cheody, okody, qokeody, oteody`) surge in `$H=1, 3, 4` and `$L=A / $I=H,P,Z`,
   while `E2` (`qokeedy, qokeey, sheedy`) surges in Scribe Hand `$H=2` (Balneological `$I=B`) vs `E1` (`qokedy, shedy`)?
3. Information Gain: How much of the remaining `3.4365 bits` of H(Word | Cell) is captured by adding the
   Internal Stem Nucleus slot `V_nuc` (`H(Cell, V_nuc)`)?
"""

import json
import math
import random
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ZL_PATH = ROOT / "data" / "ZL3b-n.txt"
OUT_JSON = ROOT / "data" / "attack61_internal_stem_nucleus_solver.json"

LOCUS_RE = re.compile(r"^<f([0-9]+[rv][0-9]*|Ros)\.([^,>]+),([^>]+)>\s*(.*)$")
KCH_COMPLEX = ("kch", "fch", "ksh", "fsh", "ckh", "cfh")
TCH_COMPLEX = ("tch", "pch", "tsh", "psh", "cth", "cph")


def mean(xs):
    return sum(xs) / len(xs) if xs else 0.0


def std(xs):
    if len(xs) < 2:
        return 0.0
    m = mean(xs)
    return math.sqrt(sum((x - m) ** 2 for x in xs) / len(xs))


def shannon_entropy(counts: Counter) -> float:
    tot = sum(counts.values())
    if tot == 0:
        return 0.0
    return -sum((c / tot) * math.log2(c / tot) for c in counts.values() if c > 0)


def clean_tokens(raw: str):
    s = re.sub(r"\{[^}]*\}", "", raw)
    s = re.sub(r"\[([^:\]]+):[^\]]+\]", r"\1", s)
    s = s.replace("<%>", " ").replace("<$>", " ").replace("<->", " ")
    s = re.sub(r"<[^>]*>", " ", s)
    s = re.sub(r"@[0-9]+;", "", s)
    s = re.sub(r"[^a-zA-Z.\s]", "", s).lower()
    return [t for t in s.replace(".", " ").split() if t]


def classify_pre(pre: str) -> str:
    if pre == "":
        return "ZERO"
    if pre.startswith("qo"):
        return "QO"
    if pre.startswith("ol") or pre.startswith("qol") or pre.startswith("l") or pre.startswith("al"):
        return "L_APPL"
    if pre.startswith("o"):
        return "O_VOW"
    if pre.startswith("y"):
        return "Y"
    if pre.startswith("d"):
        return "D"
    if pre.startswith("s"):
        return "S"
    return "R_OTHER"


def parse_post_into_nucleus_and_coda(post: str):
    """
    Given the substring `post` after the Core (`ch, sh, k/f, t/p, kch/ckh, tch/cth`),
    split `post` into `(V_nuc, Coda)` where:
      Coda in `['DY', 'Y', 'AIIN', 'OL', 'OR', 'AL', 'AR', 'AM_OTHER']`
      V_nuc in `['ZERO_V', 'E1', 'E2', 'O_VOW', 'EO_DIPH', 'A_VOW', 'OTHER_V']`
    """
    # Identify Coda strip
    coda = "AM_OTHER"
    nuc_str = post
    for suf_pat, c_label in [
        ("dy", "DY"),
        ("aiin", "AIIN"), ("iiin", "AIIN"), ("iin", "AIIN"), ("ain", "AIIN"), ("in", "AIIN"),
        ("y", "Y"),
        ("ol", "OL"), ("or", "OR"), ("al", "AL"), ("ar", "AR"),
        ("am", "AM_OTHER"), ("om", "AM_OTHER"), ("m", "AM_OTHER"),
    ]:
        if post.endswith(suf_pat):
            coda = c_label
            nuc_str = post[:-len(suf_pat)]
            # Wait: for -aiin/-ain, 'a' is part of the vowel before iin/in, or for -ol/-or/-al/-ar, 'o'/'a' is the vowel!
            if suf_pat in ("aiin", "ain"):
                nuc_str = post[:-len(suf_pat)] + "a"
            elif suf_pat in ("ol", "or"):
                nuc_str = post[:-2] + "o"
            elif suf_pat in ("al", "ar"):
                nuc_str = post[:-2] + "a"
            elif suf_pat in ("am", "om"):
                nuc_str = post[:-1]
            break

    # Classify nuc_str into 6 canonical Internal Stem Nuclei
    if nuc_str == "":
        v_nuc = "ZERO_V"
    elif nuc_str in ("ee", "eee"):
        v_nuc = "E2"
    elif nuc_str == "e":
        v_nuc = "E1"
    elif nuc_str in ("eo", "eeo"):
        v_nuc = "EO_DIPH"
    elif nuc_str in ("o", "oo"):
        v_nuc = "O_VOW"
    elif nuc_str in ("a", "ea", "oa"):
        v_nuc = "A_VOW"
    else:
        v_nuc = "OTHER_V"

    return v_nuc, coda, nuc_str


def parse_open_token(w: str):
    for pat in KCH_COMPLEX:
        idx = w.find(pat)
        if idx != -1:
            v_nuc, coda, nstr = parse_post_into_nucleus_and_coda(w[idx + len(pat):])
            return classify_pre(w[:idx]), "KCH_CKH", v_nuc, coda
    for pat in TCH_COMPLEX:
        idx = w.find(pat)
        if idx != -1:
            v_nuc, coda, nstr = parse_post_into_nucleus_and_coda(w[idx + len(pat):])
            return classify_pre(w[:idx]), "TCH_CTH", v_nuc, coda
    for pat, cname in (("ch", "CH"), ("sh", "SH")):
        idx = w.find(pat)
        if idx != -1:
            v_nuc, coda, nstr = parse_post_into_nucleus_and_coda(w[idx + 2:])
            return classify_pre(w[:idx]), cname, v_nuc, coda
    for i, ch in enumerate(w):
        if ch in ("k", "f"):
            v_nuc, coda, nstr = parse_post_into_nucleus_and_coda(w[i + 1:])
            return classify_pre(w[:i]), "K_F", v_nuc, coda
        if ch in ("t", "p"):
            v_nuc, coda, nstr = parse_post_into_nucleus_and_coda(w[i + 1:])
            return classify_pre(w[:i]), "T_P", v_nuc, coda
    return None


def mutual_info_and_z(pairs, n_perm=500, seed=6101):
    xs = [p[0] for p in pairs]
    ys = [p[1] for p in pairs]
    n = len(pairs)
    cx = Counter(xs)
    cy = Counter(ys)
    cxy = Counter(pairs)
    mi = sum(
        (c / n) * math.log2((c / n) / ((cx[x] / n) * (cy[y] / n)))
        for (x, y), c in cxy.items()
    )
    rng = random.Random(seed)
    ys_shuf = list(ys)
    nulls = []
    for _ in range(n_perm):
        rng.shuffle(ys_shuf)
        sxy = Counter(zip(xs, ys_shuf))
        m_s = sum(
            (c / n) * math.log2((c / n) / ((cx[x] / n) * (cy[y] / n)))
            for (x, y), c in sxy.items()
        )
        nulls.append(m_s)
    z = (mi - mean(nulls)) / (std(nulls) + 1e-12)
    return mi, z


def main():
    cur_sec = "U"
    cur_lang = "U"
    cur_hand = "U"

    open_records = []
    all_word_counts = Counter()
    cell_440_counts = Counter()
    cell_plus_nuc_counts = Counter()
    cell_plus_nuc_words = defaultdict(Counter)

    for raw_line in ZL_PATH.read_text(encoding="utf-8", errors="replace").splitlines():
        raw_line = raw_line.strip()
        if not raw_line or raw_line.startswith("#"):
            continue
        if raw_line.startswith("<f") and ">" in raw_line and "." not in raw_line.split(">")[0]:
            m_s = re.search(r"\$I=([A-Z])", raw_line)
            cur_sec = m_s.group(1) if m_s else "U"
            m_l = re.search(r"\$L=([A-Z])", raw_line)
            cur_lang = m_l.group(1) if m_l else "U"
            m_h = re.search(r"\$H=([0-9A-Za-z]+)", raw_line)
            cur_hand = m_h.group(1) if m_h else "U"
            continue

        m = LOCUS_RE.match(raw_line)
        if not m:
            continue
        toks = clean_tokens(m.group(4))
        for i, w in enumerate(toks):
            all_word_counts[w] += 1
            op = parse_open_token(w)
            if op:
                pre, core, v_nuc, coda = op
                c440 = f"OPEN:{pre}:{core}:{coda}"
                cnuc = f"OPEN:{pre}:{core}:{v_nuc}:{coda}"
                open_records.append({
                    "w": w,
                    "pre": pre,
                    "core": core,
                    "v_nuc": v_nuc,
                    "coda": coda,
                    "sec": cur_sec,
                    "lang": cur_lang,
                    "hand": cur_hand,
                    "is_init": (i == 0),
                })
            else:
                # Closed class with internal vowel grade
                onset = "OTHER"
                for p, lbl in [
                    ("qo", "QO_PRO"), ("o", "O_VOW"), ("a", "O_VOW"), ("e", "O_VOW"), ("i", "O_VOW"),
                    ("y", "Y_CONJ"), ("d", "D_DEIC"), ("s", "S_SIB"), ("l", "L_APPL"), ("r", "R_PORT")
                ]:
                    if w.startswith(p):
                        onset = lbl
                        v_nuc, coda, _ = parse_post_into_nucleus_and_coda(w[len(p):])
                        c440 = f"CLOSED:{onset}:{coda}"
                        cnuc = f"CLOSED:{onset}:{v_nuc}:{coda}"
                        break
                else:
                    c440 = "RESIDUAL"
                    cnuc = "RESIDUAL"

            cell_440_counts[c440] += 1
            cell_plus_nuc_counts[cnuc] += 1
            cell_plus_nuc_words[cnuc][w] += 1

    total_tokens = sum(all_word_counts.values())
    h_word = shannon_entropy(all_word_counts)
    h_c440 = shannon_entropy(cell_440_counts)
    h_cnuc = shannon_entropy(cell_plus_nuc_counts)
    h_word_given_cnuc = sum(
        (sum(wc.values()) / total_tokens) * shannon_entropy(wc)
        for wc in cell_plus_nuc_words.values()
    )

    # Test 1: Core Weight Compensation on `-dy` and `-y` stems (`DY` + `Y` codas)
    dy_y_recs = [r for r in open_records if r["coda"] in ("DY", "Y") and r["v_nuc"] in ("ZERO_V", "E1", "E2", "O_VOW", "EO_DIPH")]
    core_x_nuc = {}
    for core in ["K_F", "T_P", "CH", "SH", "KCH_CKH", "TCH_CTH"]:
        sub = [r for r in dy_y_recs if r["core"] == core]
        cnt = Counter(r["v_nuc"] for r in sub)
        tot = len(sub)
        core_x_nuc[core] = {
            "total": tot,
            "ZERO_V_pct": round(100.0 * cnt["ZERO_V"] / tot, 2) if tot else 0,
            "E1_pct": round(100.0 * cnt["E1"] / tot, 2) if tot else 0,
            "E2_pct": round(100.0 * cnt["E2"] / tot, 2) if tot else 0,
            "O_VOW_pct": round(100.0 * cnt["O_VOW"] / tot, 2) if tot else 0,
            "EO_DIPH_pct": round(100.0 * cnt["EO_DIPH"] / tot, 2) if tot else 0,
            "counts": dict(cnt),
        }

    mi_core_nuc, z_core_nuc = mutual_info_and_z([(r["core"], r["v_nuc"]) for r in dy_y_recs], n_perm=500, seed=6101)

    # Test 2: Scribe Hand ($H=1..5) and Currier Language ($L=A/B) conditioning of V_nuc on DY/Y stems
    hand_x_nuc = {}
    for h in ["1", "2", "3", "4", "5"]:
        sub = [r for r in dy_y_recs if r["hand"] == h]
        if not sub:
            continue
        cnt = Counter(r["v_nuc"] for r in sub)
        tot = len(sub)
        hand_x_nuc[f"Hand_{h}"] = {
            "total": tot,
            "ZERO_V_pct": round(100.0 * cnt["ZERO_V"] / tot, 2),
            "E1_pct": round(100.0 * cnt["E1"] / tot, 2),
            "E2_pct": round(100.0 * cnt["E2"] / tot, 2),
            "O_plus_EO_pct": round(100.0 * (cnt["O_VOW"] + cnt["EO_DIPH"]) / tot, 2),
            "E2_to_E1_ratio": round(cnt["E2"] / cnt["E1"], 3) if cnt["E1"] > 0 else None,
        }

    mi_hand_nuc, z_hand_nuc = mutual_info_and_z(
        [(r["hand"], r["v_nuc"]) for r in dy_y_recs if r["hand"] in ("1", "2", "3", "4", "5")],
        n_perm=500,
        seed=6102,
    )

    # Test 3: Constant-Cell Minimal Quintuplets (`[Prefix, Core, DY]`) across the 5 nuclei
    quintuplets = []
    for pre, core, label in [
        ("ZERO", "CH", "ch- + -dy (chdy / chedy / cheedy / chody / cheody)"),
        ("ZERO", "SH", "sh- + -dy (shdy / shedy / sheedy / shody / sheody)"),
        ("QO", "K_F", "qok- + -dy (qokdy / qokedy / qokeedy / qokody / qokeody)"),
        ("QO", "T_P", "qot- + -dy (qotdy / qotedy / qoteedy / qotody / qoteody)"),
        ("O_VOW", "K_F", "ok- + -dy (okdy / okedy / okeedy / okody / okeody)"),
        ("O_VOW", "T_P", "ot- + -dy (otdy / otedy / oteedy / otody / oteody)"),
    ]:
        sub = [r for r in dy_y_recs if r["pre"] == pre and r["core"] == core and r["coda"] == "DY"]
        cnt = Counter(r["v_nuc"] for r in sub)
        quintuplets.append({
            "paradigm": label,
            "total": len(sub),
            "ZERO_V": cnt["ZERO_V"],
            "E1": cnt["E1"],
            "E2": cnt["E2"],
            "O_VOW": cnt["O_VOW"],
            "EO_DIPH": cnt["EO_DIPH"],
        })

    print("=== ATTACK 61: THE 6-WAY INTERNAL STEM NUCLEUS SOLVER ===")
    print(f"Entropy H(Word) = {h_word:.4f} bits")
    print(f"  -> H(440-Cell) = {h_c440:.4f} bits ({100*h_c440/h_word:.2f}%)")
    print(f"  -> H(Cell + V_nuc) = {h_cnuc:.4f} bits ({100*h_cnuc/h_word:.2f}% of total word entropy explained!)")
    print(f"  -> Residual H(Word | Cell, V_nuc) = {h_word_given_cnuc:.4f} bits")
    print(f"\n1. Core-Weight Compensation across DY/Y Stems (MI = {mi_core_nuc:.4f} bits, z = {z_core_nuc:+.2f}):")
    for c, v in core_x_nuc.items():
        print(
            f"   {c:8s} (n={v['total']:4d}): ZERO_V={v['ZERO_V_pct']:5.2f}%, E1={v['E1_pct']:5.2f}%, "
            f"E2={v['E2_pct']:5.2f}%, O={v['O_VOW_pct']:5.2f}%, EO={v['EO_DIPH_pct']:5.2f}%"
        )
    print(f"\n2. Scribe-Hand Conditioning of V_nuc across DY/Y Stems (MI = {mi_hand_nuc:.4f} bits, z = {z_hand_nuc:+.2f}):")
    for h, v in hand_x_nuc.items():
        print(
            f"   {h:8s} (n={v['total']:4d}): ZERO_V={v['ZERO_V_pct']:5.2f}%, E1={v['E1_pct']:5.2f}%, "
            f"E2={v['E2_pct']:5.2f}%, O+EO={v['O_plus_EO_pct']:5.2f}% (E2:E1 = {v['E2_to_E1_ratio']})"
        )
    print("\n3. Constant-Cell Minimal Quintuplets (-dy):")
    for q in quintuplets:
        print(f"   {q['paradigm']:55s}: 0={q['ZERO_V']:3d}, e={q['E1']:3d}, ee={q['E2']:3d}, o={q['O_VOW']:3d}, eo={q['EO_DIPH']:3d}")

    out = {
        "entropy_gain": {
            "H_word_bits": round(h_word, 4),
            "H_440_cell_bits": round(h_c440, 4),
            "H_cell_plus_nucleus_bits": round(h_cnuc, 4),
            "pct_entropy_explained_by_cell_plus_nucleus": round(100.0 * h_cnuc / h_word, 2),
            "H_residual_given_cell_plus_nucleus_bits": round(h_word_given_cnuc, 4),
            "attested_cell_plus_nucleus_states": len(cell_plus_nuc_counts),
        },
        "core_weight_compensation": {
            "mi_bits": round(mi_core_nuc, 5),
            "z_score": round(z_core_nuc, 2),
            "table": core_x_nuc,
        },
        "scribe_hand_conditioning": {
            "mi_bits": round(mi_hand_nuc, 5),
            "z_score": round(z_hand_nuc, 2),
            "table": hand_x_nuc,
        },
        "constant_cell_quintuplets": quintuplets,
    }
    OUT_JSON.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"Saved -> {OUT_JSON}")


if __name__ == "__main__":
    main()
