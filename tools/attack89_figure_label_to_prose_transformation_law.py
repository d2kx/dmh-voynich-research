#!/usr/bin/env python3
"""
Attack 89 (Phase 100 / Discovery 106): The Complete Figure-Label (`@L`, `n = 1,000+` Tokens) vs.
Running-Prose (`@P`, `n = 33,000+` Tokens) Morphological & Radical Transformation Law

Tests:
1. Extracts every token across all Locus Types in `ZL3b-n.txt`:
   - `@P` (Running Prose Paragraphs)
   - `@L` (Standalone Figure & Diagram Labels, stratified into:
     * `@Lf`: Pharmaceutical Jar & Root Labels (`f88r–f102v`)
     * `@Ln / @Lb`: Balneological Nymph & Pipe Labels (`f75r–f84v`)
     * `@Lz / @Ls / @La`: Zodiac & Astronomical Star/Emblem Labels (`f67r–f73v`)
     * `@Lc / @Ro`: Cosmological & Rosettes Diagram Labels (`f57v, f65v–f66v, f85–f86`)
     * `@Lp / @L0`: Herbal Plant & Marginal Labels)
   - `@C / @R` (Circular Ring & Radial Diagram Text)
2. Computes the exact **Label-to-Prose Morphological Transformation Matrix**:
   - How does an open-class stem `S` appear when written as a **Standalone Nominal Label (`@L`)**
     vs. when that **exact same stem `S` is inflected inside Running Prose (`@P`)**?
   - Quantifies the enrichment/suppression of every Prefix Class (`PFX_O_NOM`, `PFX_QO_ACT`,
     `PFX_L_APPL`, `PFX_Y_CONJ`, `PFX_D_S`, `PFX_BARE`) and Suffix Class (`-y`, `-dy`, `-or/-ar`,
     `-ol/-al`, `-aiin/-in`, `-am/-m`) in `@L` vs. `@P` (`z`-scores across 500 section-stratified
     permutations).
3. Tests **Object-Specific Label Morphology across the 5 `@L` Subtypes (`Jar/Root @Lf` vs.
   `Nymph @Ln` vs. `Star/Zodiac @Lz/@Ls` vs. `Cosmological @Lc`)**:
   - Does the morphological shape of a label change systematically depending on whether the
     depicted object is a **Pharmaceutical Jar/Root (`@Lf`)**, a **Balneological Nymph (`@Ln`)**,
     or a **Zodiac/Astronomical Star (`@Lz/@Ls`)** (`I(Label_Subtype ; Affix_Profile)` `z`-score)?
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
OUT_JSON = DATA_DIR / "attack89_figure_label_to_prose_transformation_law.json"

LOCUS_RE = re.compile(r"^<f([0-9]+[rv][0-9]*|Ros)\.([^,>]+),([^>]+)>\s*(.*)$")


def clean_tokens(raw: str):
    s = re.sub(r"\{[^}]*\}", "", raw)
    s = re.sub(r"\[([^:\]]+):[^\]]+\]", r"\1", s)
    s = s.replace("<%>", " ").replace("<$>", " ").replace("<->", " ")
    s = re.sub(r"<[^>]*>", " ", s)
    s = re.sub(r"@[0-9]+;", "", s)
    s = re.sub(r"[^a-zA-Z.\s]", "", s).lower()
    return [t for t in s.replace(".", " ").split() if t]


def get_prefix_class(w: str) -> str:
    if w.startswith(("qol", "ol", "al", "dal")) and len(w) > 3:
        return "PFX_L_APPL"
    if w.startswith("q"):
        return "PFX_QO_ACT"
    if w.startswith("o"):
        return "PFX_O_NOM"
    if w.startswith("y"):
        return "PFX_Y_INIT"
    if w.startswith(("d", "s")):
        return "PFX_D_S"
    return "PFX_BARE"


def get_suffix_class(w: str) -> str:
    if w.endswith("dy"):
        return "SFX_DY"
    if w.endswith("y"):
        return "SFX_Y_BARE"
    if w.endswith(("aiin", "oiin", "eiin", "ain", "oin", "ein", "iin", "in")):
        return "SFX_IN"
    if w.endswith(("ol", "al", "el", "il")):
        return "SFX_LIQ_L"
    if w.endswith(("or", "ar", "er", "ir")):
        return "SFX_LIQ_R"
    if w.endswith(("am", "om", "em", "im", "m")):
        return "SFX_M_CLOSE"
    return "SFX_CONSONANT_OTHER"


def extract_open_stem(w: str):
    if not any(g in w for g in ("k", "t", "p", "f", "ch", "sh")):
        return None
    rem = w
    for p in ("qol", "dal", "ol", "al", "qo", "po", "fo", "o", "y", "s", "d", "l", "q"):
        if rem.startswith(p) and len(rem) > len(p) + 1 and any(g in rem[len(p):] for g in ("k", "t", "p", "f", "ch", "sh")):
            rem = rem[len(p):]
            break
    s_norm = rem.replace("cph", "cth").replace("cfh", "ckh").replace("p", "t").replace("f", "k")
    s_norm = re.sub(r"e+", "e", s_norm)
    s_norm = re.sub(r"i+", "i", s_norm)
    return s_norm


def extract_bare_radical(w: str) -> str:
    """Strips prefix and suffix to isolate the bare consonantal-vocalic stem for Stem-Matched Label<->Prose comparison."""
    s = w
    for p in ("qol", "dal", "ol", "al", "qo", "po", "fo", "so", "do", "yo", "o", "y", "s", "d", "l", "q"):
        if s.startswith(p) and len(s) > len(p) + 2:
            s = s[len(p):]
            break
    for sfx in ("aiin", "oiin", "ain", "oin", "edy", "ody", "eey", "ey", "dy", "ol", "al", "or", "ar", "am", "om", "in", "y", "m", "s", "l", "r"):
        if s.endswith(sfx) and len(s) > len(sfx) + 1:
            s = s[:-len(sfx)]
            break
    s = s.replace("cph", "cth").replace("cfh", "ckh").replace("p", "t").replace("f", "k").replace("sh", "ch")
    s = re.sub(r"e+", "e", s)
    s = re.sub(r"i+", "i", s)
    return s


def classify_label_subtype(ltype: str, sec: str) -> str:
    lt = ltype.lstrip("@+*=")
    if lt.startswith("Lf") or sec == "P":
        return "LBL_PHARM_JAR_ROOT"
    if lt.startswith(("Ln", "Lb")) or sec == "B":
        return "LBL_BALNEO_NYMPH"
    if lt.startswith(("Lz", "Ls", "La")) or sec in ("Z", "A", "T"):
        return "LBL_ASTRO_ZODIAC_STAR"
    if lt.startswith(("Lc", "Ro")) or sec == "C":
        return "LBL_COSMO_DIAGRAM"
    return "LBL_HERBAL_MARGINAL"


def mutual_info(joint: Counter) -> float:
    total = sum(joint.values())
    if total == 0:
        return 0.0
    rx = Counter()
    cy = Counter()
    for (x, y), c in joint.items():
        rx[x] += c
        cy[y] += c
    mi = 0.0
    for (x, y), c in joint.items():
        if c > 0:
            mi += (c / total) * math.log2((c / total) / ((rx[x] / total) * (cy[y] / total)))
    return mi


def main():
    cur_meta = None
    tokens_by_macro_locus = defaultdict(list)
    label_tokens_by_subtype = defaultdict(list)
    all_token_records = []

    rad_in_labels = defaultdict(list)
    rad_in_prose = defaultdict(list)

    for raw_line in ZL_PATH.read_text(encoding="utf-8", errors="replace").splitlines():
        raw_s = raw_line.strip()
        if not raw_s or raw_s.startswith("#"):
            continue
        if raw_s.startswith("<f") and ">" in raw_s and "." not in raw_s.split(">")[0]:
            fname = raw_s.split(">")[0][1:]
            tags = dict(re.findall(r"\$([A-Z])=([0-9A-Za-z]+)", raw_s))
            cur_meta = {
                "folio": fname,
                "I": tags.get("I", "U"),
                "L": tags.get("L", "U"),
                "H": tags.get("H", "U"),
            }
            continue
        m = LOCUS_RE.match(raw_s)
        if m and cur_meta is not None:
            ltype_raw = m.group(3)
            lt = ltype_raw.lstrip("@+*=")
            toks = clean_tokens(m.group(4))
            if not toks:
                continue
            if lt.startswith("L"):
                macro = "LOC_LABEL_L"
                sub = classify_label_subtype(ltype_raw, cur_meta["I"])
                for w in toks:
                    label_tokens_by_subtype[sub].append(w)
                    rad_in_labels[extract_bare_radical(w)].append(w)
            elif lt.startswith(("C", "R")):
                macro = "LOC_RING_RADIAL_CR"
            else:
                macro = "LOC_PROSE_P"
                for w in toks:
                    rad_in_prose[extract_bare_radical(w)].append(w)

            for w in toks:
                tokens_by_macro_locus[macro].append(w)
                all_token_records.append((cur_meta["I"], macro, w))

    def profile_word_list(wlist: list) -> dict:
        n = max(len(wlist), 1)
        pfxs = Counter(get_prefix_class(w) for w in wlist)
        sfxs = Counter(get_suffix_class(w) for w in wlist)
        return {
            "n_tokens": len(wlist),
            "n_types": len(set(wlist)),
            "mean_len": round(sum(len(w) for w in wlist) / n, 3),
            "open_class_pct": round(100.0 * sum(1 for w in wlist if any(g in w for g in ("k", "t", "p", "f", "ch", "sh"))) / n, 2),
            "t_class_share_of_gallows_pct": round(
                100.0 * sum(1 for w in wlist if any(g in w for g in ("t", "p")))
                / max(sum(1 for w in wlist if any(g in w for g in ("k", "t", "p", "f"))), 1),
                2,
            ),
            "prefix_pct": {k: round(100.0 * pfxs[k] / n, 2) for k in sorted(pfxs.keys())},
            "suffix_pct": {k: round(100.0 * sfxs[k] / n, 2) for k in sorted(sfxs.keys())},
            "top_words": [f"{w}({c})" for w, c in Counter(wlist).most_common(8)],
        }

    macro_profiles = {
        m: profile_word_list(wlist) for m, wlist in tokens_by_macro_locus.items()
    }
    subtype_profiles = {
        s: profile_word_list(wlist) for s, wlist in sorted(label_tokens_by_subtype.items())
    }

    # Section-Stratified Permutation Test for Label (@L) vs Prose (@P):
    # Specifically test:
    # (1) Nominal `PFX_O_NOM` enrichment in `@L` vs `@P`
    # (2) Active `PFX_QO_ACT` suppression in `@L` vs `@P`
    # (3) Rhotic `-or/-ar` (`SFX_LIQ_R`) enrichment in `@L` vs `@P`
    lbl_words = tokens_by_macro_locus["LOC_LABEL_L"]
    prs_words = tokens_by_macro_locus["LOC_PROSE_P"]

    obs_o_diff = (
        sum(1 for w in lbl_words if get_prefix_class(w) == "PFX_O_NOM") / len(lbl_words)
        - sum(1 for w in prs_words if get_prefix_class(w) == "PFX_O_NOM") / len(prs_words)
    )
    obs_qo_diff = (
        sum(1 for w in lbl_words if get_prefix_class(w) == "PFX_QO_ACT") / len(lbl_words)
        - sum(1 for w in prs_words if get_prefix_class(w) == "PFX_QO_ACT") / len(prs_words)
    )
    obs_r_diff = (
        sum(1 for w in lbl_words if get_suffix_class(w) == "SFX_LIQ_R") / len(lbl_words)
        - sum(1 for w in prs_words if get_suffix_class(w) == "SFX_LIQ_R") / len(prs_words)
    )

    by_sec = defaultdict(list)
    for sec, macro, w in all_token_records:
        if macro in ("LOC_LABEL_L", "LOC_PROSE_P"):
            by_sec[sec].append((macro, get_prefix_class(w), get_suffix_class(w)))

    rng = random.Random(89)
    null_o, null_qo, null_r = [], [], []
    for _ in range(300):
        lo = lqo = lr = ln = 0
        po = pqo = pr = pn = 0
        for sec, items in by_sec.items():
            macros = [m for m, _, _ in items]
            rng.shuffle(macros)
            for m_sh, (_, pfx, sfx) in zip(macros, items):
                if m_sh == "LOC_LABEL_L":
                    ln += 1
                    if pfx == "PFX_O_NOM":
                        lo += 1
                    if pfx == "PFX_QO_ACT":
                        lqo += 1
                    if sfx == "SFX_LIQ_R":
                        lr += 1
                else:
                    pn += 1
                    if pfx == "PFX_O_NOM":
                        po += 1
                    if pfx == "PFX_QO_ACT":
                        pqo += 1
                    if sfx == "SFX_LIQ_R":
                        pr += 1
        null_o.append(lo / ln - po / pn)
        null_qo.append(lqo / ln - pqo / pn)
        null_r.append(lr / ln - pr / pn)

    def calc_z(obs, nulls):
        m = sum(nulls) / len(nulls)
        sd = math.sqrt(sum((x - m) ** 2 for x in nulls) / len(nulls)) or 1e-9
        return round((obs - m) / sd, 2)

    z_o_nom = calc_z(obs_o_diff, null_o)
    z_qo_act = calc_z(obs_qo_diff, null_qo)
    z_sfx_r = calc_z(obs_r_diff, null_r)

    # Stem-Matched Transformation Pairs: For shared bare radicals attested >= 5 times in @L and >= 20 times in @P,
    # compare how the EXACT SAME RADICAL is inflected in a Figure Label (@L) vs Running Prose (@P)!
    shared_radical_transformations = []
    for rad, l_toks in sorted(rad_in_labels.items(), key=lambda kv: -len(kv[1])):
        p_toks = rad_in_prose.get(rad, [])
        if len(l_toks) < 6 or len(p_toks) < 20 or len(rad) < 2:
            continue
        l_o_pct = round(100.0 * sum(1 for w in l_toks if w.startswith("o")) / len(l_toks), 1)
        p_o_pct = round(100.0 * sum(1 for w in p_toks if w.startswith("o")) / len(p_toks), 1)
        l_qo_pct = round(100.0 * sum(1 for w in l_toks if w.startswith("q")) / len(l_toks), 1)
        p_qo_pct = round(100.0 * sum(1 for w in p_toks if w.startswith("q")) / len(p_toks), 1)
        shared_radical_transformations.append({
            "radical": rad,
            "n_label_tokens": len(l_toks),
            "n_prose_tokens": len(p_toks),
            "label_o_nom_pct": l_o_pct,
            "prose_o_nom_pct": p_o_pct,
            "label_qo_act_pct": l_qo_pct,
            "prose_qo_act_pct": p_qo_pct,
            "top_label_forms": [f"{w}({c})" for w, c in Counter(l_toks).most_common(4)],
            "top_prose_forms": [f"{w}({c})" for w, c in Counter(p_toks).most_common(4)],
        })

    # Mutual Information between Label Subtype (`@Lf, @Ln, @Lz, @Lc, @Lp`) and (Prefix, Suffix)
    joint_sub_affix = Counter()
    sub_affix_list = []
    for sub, wlist in label_tokens_by_subtype.items():
        for w in wlist:
            af = (get_prefix_class(w), get_suffix_class(w))
            joint_sub_affix[(sub, af)] += 1
            sub_affix_list.append((sub, af))

    obs_sub_mi = mutual_info(joint_sub_affix)
    null_sub_mis = []
    subs_only = [s for s, _ in sub_affix_list]
    afs_only = [a for _, a in sub_affix_list]
    for _ in range(300):
        sh_s = list(subs_only)
        rng.shuffle(sh_s)
        null_sub_mis.append(mutual_info(Counter(zip(sh_s, afs_only))))
    z_sub_mi = calc_z(obs_sub_mi, null_sub_mis)

    out = {
        "macro_locus_profiles": macro_profiles,
        "label_vs_prose_permutation_tests": {
            "obs_o_nom_delta_pct": round(100.0 * obs_o_diff, 2),
            "z_score_o_nom_enrichment_in_labels": z_o_nom,
            "obs_qo_act_delta_pct": round(100.0 * obs_qo_diff, 2),
            "z_score_qo_act_suppression_in_labels": z_qo_act,
            "obs_sfx_r_delta_pct": round(100.0 * obs_r_diff, 2),
            "z_score_sfx_r_enrichment_in_labels": z_sfx_r,
            "label_subtype_affix_mi_bits": round(obs_sub_mi, 4),
            "z_score_label_subtype_affix_mi": z_sub_mi,
        },
        "label_subtype_profiles": subtype_profiles,
        "shared_radical_label_to_prose_transformations": shared_radical_transformations[:25],
    }
    OUT_JSON.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"Saved {OUT_JSON}")
    print("Label vs Prose Permutation Tests:", out["label_vs_prose_permutation_tests"])
    print("Macro Profiles:")
    for m, p in macro_profiles.items():
        print(f"  {m}: n={p['n_tokens']}, T%={p['t_class_share_of_gallows_pct']}%, pfx={p['prefix_pct']}, sfx={p['suffix_pct']}")
    print("Label Subtype Profiles:")
    for s, p in subtype_profiles.items():
        print(f"  {s:24s}: n={p['n_tokens']:3d}, T%={p['t_class_share_of_gallows_pct']:5.1f}%, top={p['top_words'][:4]}")
    print("Top Shared Radical Transformations (Label -> Prose):")
    for sr in shared_radical_transformations[:8]:
        print(
            f"  rad={sr['radical']:6s} (L={sr['n_label_tokens']:2d}, P={sr['n_prose_tokens']:4d}): "
            f"o%={sr['label_o_nom_pct']}->{sr['prose_o_nom_pct']}%, "
            f"qo%={sr['label_qo_act_pct']}->{sr['prose_qo_act_pct']}% | "
            f"L={sr['top_label_forms'][:3]} vs P={sr['top_prose_forms'][:3]}"
        )


if __name__ == "__main__":
    main()
