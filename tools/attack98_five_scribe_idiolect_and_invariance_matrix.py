#!/usr/bin/env python3
"""
Attack 98 (Discovery 115): The 5-Scribe (`$H=1..5`) Paleographic & Orthographic Idiolect
Transfer Matrix — Isolating Scribe-Specific Spelling Habits from Underlying Grammatical Invariance

Tests:
1. Parses all `226` folios and `36,229` tokens by Lisa Fagin Davis Scribe Hand (`$H=1, 2, 3, 4, 5`)
   from the `<f...> <! ... $H=...>` headers in `data/ZL3b-n.txt`.
2. Computes the **4-Level Pairwise Scribe Divergence Collapse** across all `10` pairs of Scribes `(H_i, H_j)`:
   - Level 1 (`SURFACE_WORD_JSD`): Raw surface word probability distribution $P(w | H)$.
   - Level 2 (`CANONICAL_STEM_JSD`): 4-Rule Canonical + `-edy/-ody -> -dy` unified stem distribution.
   - Level 3 (`RADICAL_CORE62_JSD`): Underlying `62`-Core + Particle slot distribution.
   - Level 4 (`CONSTITUENT_5ROLE_BIGRAM_JSD`): `5 x 5` Clause Constituent Transition Matrix $P(R_t, R_{t+1} | H)$.
3. Profiles the **Exact Scribe-Specific Orthographic Idiolect Matrix** across `$H=1..5`, holding
   shared canonical cores fixed (`ch, k, t, ke, te, che, kch, tch, ol, or, ar, al`):
   - `-edy` vs. `-ody` vs. bare `-dy` dental inflection choice,
   - Geminate `ee+` vs. single `e` rate,
   - `ii+` vs. single `i` in `-aiin / -ain / -in`,
   - `sh` vs. `ch` plume rate,
   - `p/f` vs. `t/k` gallows rate,
   - Soft-comma `,` word-gap density in `ZL3b-n.txt`.
"""

import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
ZL_PATH = DATA_DIR / "ZL3b-n.txt"
OUT_JSON = DATA_DIR / "attack98_five_scribe_idiolect_and_invariance_matrix.json"

FOLIO_META_RE = re.compile(r"^<f([0-9]+[rv][0-9]*|Ros)>\s*<!\s*(.*?)>")
LOCUS_RE = re.compile(r"^<f([0-9]+[rv][0-9]*|Ros)\.([^,>]+),([^>]+)>\s*(.*)$")

PREFIXES = ("qok", "qot", "qop", "qof", "qol", "qo", "po", "fo", "to", "ko", "so", "do", "yo", "lo", "ro",
            "ol", "al", "or", "ar", "da", "sa", "yk", "yt", "ok", "ot", "op", "of",
            "q", "o", "y", "s", "d", "l", "r", "")
SUFFIXES = ("aiin", "oiin", "eiin", "ain", "oin", "ein", "iin", "in",
            "edy", "ody", "ady", "eey", "ey", "dy", "hy", "ky", "ty", "py", "fy", "ly", "ry", "sy", "y",
            "eol", "eal", "ol", "al", "el", "il", "ul",
            "eor", "ear", "or", "ar", "er", "ir",
            "am", "om", "em", "im", "m", "n", "s", "d", "l", "r", "o", "a", "")


def clean_tokens_with_comma(raw: str):
    s = re.sub(r"\{[^}]*\}", "", raw)
    s = s.replace("<%>", " ").replace("<$>", " ").replace("<->", " ")
    s = re.sub(r"<[^>]*>", " ", s)
    s = re.sub(r"@[0-9]+;", "", s)
    s = re.sub(r"\[([^:\]]+):[^\]]+\]", r"\1", s)
    out = []
    for c in s.replace(".", " ").split():
        has_comma = "," in c
        w = re.sub(r"[^a-zA-Z]", "", c).lower()
        if w:
            out.append((w, has_comma))
    return out


def canonical_stem(w: str) -> str:
    s = w
    if s.startswith("qo") and len(s) > 3:
        s = "o" + s[2:]
    elif s.startswith("q") and len(s) > 2:
        s = s[1:]
    s = s.replace("cph", "cth").replace("cfh", "ckh")
    s = s.replace("p", "t").replace("f", "k")
    s = s.replace("sh", "ch")
    s = re.sub(r"e+", "e", s)
    s = re.sub(r"i+", "i", s)
    if s.endswith("edy") and len(s) >= 4:
        s = s[:-3] + "dy"
    elif s.endswith("ody") and len(s) >= 4:
        s = s[:-3] + "dy"
    return s


def extract_core(w: str) -> str:
    cw = canonical_stem(w)
    cands = []
    for p in PREFIXES:
        if not cw.startswith(p):
            continue
        rem = cw[len(p):]
        for s in SUFFIXES:
            if not rem.endswith(s):
                continue
            core = rem[:len(rem) - len(s)] if s else rem
            if core:
                cands.append((len(core), -len(p) - len(s), core))
    if cands:
        cands.sort()
        return cands[0][2]
    return cw[:3]


def constituent_role(w: str) -> str:
    if w in ("daiin", "dain", "dar", "dal", "dair", "dan", "dam", "dol", "dor", "chol", "chor", "or", "ol", "ar", "al", "sal", "sar", "sol", "sor") or w.startswith(("da", "sa")):
        return "R1_LINKER_DEICTIC"
    if w.startswith(("qo", "qok", "qot", "qop", "qof", "l", "ol", "qol")) or w.endswith(("edy", "ody", "dy")):
        return "R2_ACTIVE_VERB"
    if w.startswith(("ch", "sh")):
        return "R3_BENCH_QUALIFIER"
    if w.endswith(("aiin", "ain", "iin", "in", "ol", "or", "al", "ar")) or w.startswith(("ok", "ot", "op", "of", "o")):
        return "R4_NOMINAL_MEASURED"
    return "R5_CLAUSE_PARTICLE_CLOSER"


def js_divergence(c1: Counter, c2: Counter) -> float:
    n1 = sum(c1.values())
    n2 = sum(c2.values())
    if n1 == 0 or n2 == 0:
        return 0.0
    keys = set(c1.keys()) | set(c2.keys())
    jsd = 0.0
    for k in keys:
        p = c1[k] / n1
        q = c2[k] / n2
        m = 0.5 * (p + q)
        if p > 0:
            jsd += 0.5 * p * math.log2(p / m)
        if q > 0:
            jsd += 0.5 * q * math.log2(q / m)
    return jsd


def main():
    raw_lines = ZL_PATH.read_text(encoding="utf-8", errors="replace").splitlines()
    cur_folio = None
    cur_scribe = "U"
    cur_lang = "U"
    cur_sec = "U"

    scribe_folios = defaultdict(set)
    scribe_sections = defaultdict(Counter)
    scribe_langs = defaultdict(Counter)
    scribe_words = defaultdict(Counter)
    scribe_stems = defaultdict(Counter)
    scribe_cores = defaultdict(Counter)
    scribe_role_bigrams = defaultdict(Counter)
    scribe_token_list = defaultdict(list)
    scribe_comma_hits = Counter()

    for raw_line in raw_lines:
        raw_s = raw_line.strip()
        if not raw_s or raw_s.startswith("#"):
            continue
        mf = FOLIO_META_RE.match(raw_s)
        if mf:
            cur_folio = "f" + mf.group(1)
            meta_str = mf.group(2)
            meta = {}
            for kv in meta_str.split():
                if "=" in kv:
                    k, v = kv.lstrip("$").split("=", 1)
                    meta[k] = v
            h_raw = meta.get("H", "U")
            # Normalize e.g. '1'..'5'
            cur_scribe = f"H{h_raw[0]}" if h_raw and h_raw[0] in "12345" else "H_OTHER"
            cur_lang = meta.get("L", "U")
            cur_sec = meta.get("I", "U")
            scribe_folios[cur_scribe].add(cur_folio)
            continue
        ml = LOCUS_RE.match(raw_s)
        if ml and cur_folio:
            tok_tuples = clean_tokens_with_comma(ml.group(4))
            if not tok_tuples:
                continue
            words = [w for w, _ in tok_tuples]
            for w, has_c in tok_tuples:
                scribe_words[cur_scribe][w] += 1
                scribe_stems[cur_scribe][canonical_stem(w)] += 1
                scribe_cores[cur_scribe][extract_core(w)] += 1
                scribe_token_list[cur_scribe].append(w)
                scribe_sections[cur_scribe][cur_sec] += 1
                scribe_langs[cur_scribe][cur_lang] += 1
                if has_c:
                    scribe_comma_hits[cur_scribe] += 1
            roles = [constituent_role(w) for w in words]
            for i in range(len(roles) - 1):
                scribe_role_bigrams[cur_scribe][f"{roles[i]}->{roles[i+1]}"] += 1

    scribes = ["H1", "H2", "H3", "H4", "H5"]

    # 1. Compute 4-Level Pairwise JSD across all 10 Scribe Pairs
    pairwise_jsd = []
    for i in range(len(scribes)):
        for j in range(i + 1, len(scribes)):
            s1, s2 = scribes[i], scribes[j]
            jsd_w = js_divergence(scribe_words[s1], scribe_words[s2])
            jsd_st = js_divergence(scribe_stems[s1], scribe_stems[s2])
            jsd_c = js_divergence(scribe_cores[s1], scribe_cores[s2])
            jsd_rb = js_divergence(scribe_role_bigrams[s1], scribe_role_bigrams[s2])
            collapse_pct = 100.0 * (1.0 - jsd_rb / (jsd_w or 1e-9))
            pairwise_jsd.append({
                "pair": f"{s1}<->{s2}",
                "surface_word_jsd": round(jsd_w, 4),
                "canonical_stem_jsd": round(jsd_st, 4),
                "radical_core_jsd": round(jsd_c, 4),
                "constituent_5role_bigram_jsd": round(jsd_rb, 4),
                "syntax_vs_surface_collapse_pct": round(collapse_pct, 2),
            })

    mean_surface_jsd = sum(p["surface_word_jsd"] for p in pairwise_jsd) / len(pairwise_jsd)
    mean_stem_jsd = sum(p["canonical_stem_jsd"] for p in pairwise_jsd) / len(pairwise_jsd)
    mean_core_jsd = sum(p["radical_core_jsd"] for p in pairwise_jsd) / len(pairwise_jsd)
    mean_role_jsd = sum(p["constituent_5role_bigram_jsd"] for p in pairwise_jsd) / len(pairwise_jsd)
    overall_collapse_pct = 100.0 * (1.0 - mean_role_jsd / (mean_surface_jsd or 1e-9))

    # 2. Profile Exact Orthographic Idiolect Signatures across H1..H5
    idiolect_profiles = {}
    for s in scribes:
        toks = scribe_token_list[s]
        n = len(toks)
        if n == 0:
            continue
        dy_all = [w for w in toks if w.endswith("dy")]
        n_dy = len(dy_all) or 1
        edy_c = sum(1 for w in dy_all if w.endswith("edy"))
        ody_c = sum(1 for w in dy_all if w.endswith("ody"))
        bare_dy_c = n_dy - edy_c - ody_c

        e_words = [w for w in toks if "e" in w]
        ee_gem_c = sum(1 for w in e_words if "ee" in w)

        in_words = [w for w in toks if w.endswith(("aiin", "oiin", "eiin", "ain", "oin", "ein", "iin", "in"))]
        ii_gem_c = sum(1 for w in in_words if w.endswith(("aiin", "oiin", "eiin", "iin")))

        bench_words = [w for w in toks if ("ch" in w or "sh" in w)]
        sh_c = sum(1 for w in bench_words if "sh" in w)

        gallows_words = [w for w in toks if any(g in w for g in ("k", "t", "p", "f"))]
        pf_c = sum(1 for w in gallows_words if ("p" in w or "f" in w))

        qo_c = sum(1 for w in toks if w.startswith("qo"))
        o_nom_c = sum(1 for w in toks if w.startswith(("ok", "ot", "op", "of", "ol", "or", "o")) and not w.startswith("qo"))

        idiolect_profiles[s] = {
            "n_folios": len(scribe_folios[s]),
            "n_tokens": n,
            "dominant_currier_lang": scribe_langs[s].most_common(2),
            "dominant_sections": scribe_sections[s].most_common(3),
            "edy_share_of_dy_pct": round(100.0 * edy_c / n_dy, 2),
            "ody_share_of_dy_pct": round(100.0 * ody_c / n_dy, 2),
            "bare_dy_share_of_dy_pct": round(100.0 * bare_dy_c / n_dy, 2),
            "ee_geminate_share_of_e_words_pct": round(100.0 * ee_gem_c / (len(e_words) or 1), 2),
            "ii_double_minim_share_of_in_coda_pct": round(100.0 * ii_gem_c / (len(in_words) or 1), 2),
            "sh_plume_share_of_bench_pct": round(100.0 * sh_c / (len(bench_words) or 1), 2),
            "pf_looped_share_of_gallows_pct": round(100.0 * pf_c / (len(gallows_words) or 1), 2),
            "qo_active_token_pct": round(100.0 * qo_c / n, 2),
            "o_nominal_token_pct": round(100.0 * o_nom_c / n, 2),
            "soft_comma_gap_pct": round(100.0 * scribe_comma_hits[s] / n, 2),
        }

    # 3. Hold Canonical Stem Fixed: How each Scribe (`H1..H5`) spells the Top 8 Canonical Stems!
    shared_stems_to_track = ["chdy", "kdy", "tdy", "okdy", "otdy", "ol", "daiin", "chol"]
    fixed_stem_spellings = {}
    for cs in shared_stems_to_track:
        fixed_stem_spellings[cs] = {}
        for s in scribes:
            c = Counter(w for w in scribe_token_list[s] if canonical_stem(w) == cs)
            tot = sum(c.values())
            top3 = [f"{w} ({round(100.0*cnt/tot, 1)}%)" for w, cnt in c.most_common(3)] if tot else []
            fixed_stem_spellings[cs][s] = {"total": tot, "top_surface_forms": top3}

    out = {
        "four_level_divergence_collapse": {
            "mean_surface_word_jsd": round(mean_surface_jsd, 4),
            "mean_canonical_stem_jsd": round(mean_stem_jsd, 4),
            "mean_radical_core_jsd": round(mean_core_jsd, 4),
            "mean_constituent_5role_bigram_jsd": round(mean_role_jsd, 4),
            "overall_syntax_vs_surface_collapse_pct": round(overall_collapse_pct, 2),
            "pairwise_scribe_table": pairwise_jsd,
        },
        "scribe_idiolect_profiles": idiolect_profiles,
        "fixed_canonical_stem_surface_spellings": fixed_stem_spellings,
    }

    OUT_JSON.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"Saved {OUT_JSON}")
    print("4-Level Divergence Collapse:", json.dumps({k: v for k, v in out["four_level_divergence_collapse"].items() if k != "pairwise_scribe_table"}, indent=2))
    for s in scribes:
        p = idiolect_profiles[s]
        print(f"  {s} (folios={p['n_folios']}, n={p['n_tokens']}): -edy={p['edy_share_of_dy_pct']}% / -ody={p['ody_share_of_dy_pct']}% / -dy={p['bare_dy_share_of_dy_pct']}%, ee={p['ee_geminate_share_of_e_words_pct']}%, ii={p['ii_double_minim_share_of_in_coda_pct']}%, qo-={p['qo_active_token_pct']}%")


if __name__ == "__main__":
    main()
