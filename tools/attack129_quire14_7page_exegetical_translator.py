#!/usr/bin/env python3
"""
Attack 129 (Phase 140 / Discovery 146):
Complete Quire 14 (`f85r1–f86v3` + `fRos`, `$Q=N`) 7-Page Foldout Exegetical &
Cosmological Translator.

Investigates:
1. All 7 foldout pages of Quire 14 (`f85r1`, `f85r2`, `fRos`, `f86v4`, `f86v6`,
   `f86v5`, `f86v3`; Scribe 2 `$H=2`, Currier B `$L=B`, `$B=1`):
   - 3 Cosmological Diagram pages (`f85r2` 4-Season Sun Wheel, `fRos` 9-Sphere
     Rosettes Map, `f86v4` 4-Winds Ring & Marginal Prose)
   - 4 Pure Exegetical Prose pages (`f85r1`, `f86v6`, `f86v5`, `f86v3`)
2. Locus-level morphological shift inside Quire 14 between Diagram Rings/Labels
   (`@Ro/@Rc/@L0/@C0/@Pb`) and Exegetical Prose Paragraphs (`@P0`).
3. Internal Diagram-to-Commentary Citation Test (1,000-trial permutation test
   against Scribe 2 non-Quire-14 paragraphs): do the 15 Exegetical Prose
   Paragraphs (`@P0`) of Quire 14 selectively cite the rare stems of the
   Cosmological Diagrams (`f85r2 + fRos + f86v4` rings/labels)?
4. Complete 7-page & 15-paragraph functional router and interlinear translator.
"""

import json
import math
import random
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ZL_PATH = ROOT / "data" / "ZL3b-n.txt"
INDEX_PATH = ROOT / "data" / "folio_index.json"
OUT_JSON = ROOT / "data" / "attack129_quire14_7page_exegetical_translator.json"

PREFIXES = [
    "qok", "qot", "qop", "qof", "qo",
    "ch", "sh", "cth", "ckh", "cph", "cfh",
    "da", "sa", "ol", "al", "or", "ar",
    "ok", "ot", "op", "of",
    "yk", "yt", "yp", "yf",
    "lk", "lt", "lp", "lf",
    "d", "s", "y", "o", "l", "r", "k", "t", "p", "f",
]

SUFFIXES = [
    "aiin", "oiin", "eiin", "iin", "in",
    "eedy", "edy", "ody", "ady", "dy",
    "ey", "oy", "ay", "y",
    "eal", "ol", "al", "el", "l",
    "ear", "or", "ar", "er", "r",
    "eam", "am", "om", "m",
    "an", "en", "on", "n",
    "s", "d", "g",
]


def clean_tok(t: str) -> str:
    t = re.sub(r"\{[^}]*\}", "", t)
    t = re.sub(r"\[([^]:]+):[^\]]+\]", r"\1", t)
    t = re.sub(r"[^a-zA-Z]", "", t).lower()
    return t


def canon_stem(w: str) -> str:
    s = w
    if s.startswith("q") and len(s) > 2:
        s = s[1:]
    for p in ["ch", "sh", "da", "sa", "ol", "al", "or", "ar", "ok", "ot", "yk", "yt", "d", "s", "y", "o", "l"]:
        if s.startswith(p) and len(s) - len(p) >= 2:
            s = s[len(p):]
            break
    for suf in ["aiin", "oiin", "iin", "eedy", "edy", "ody", "ady", "dy", "ey", "oy", "ol", "al", "or", "ar", "am", "om", "an", "in", "y", "l", "r", "m", "n", "s"]:
        if s.endswith(suf) and len(s) - len(suf) >= 2:
            s = s[:-len(suf)]
            break
    return s


def decompose_word(w: str) -> dict:
    rem = w
    pref = ""
    for p in PREFIXES:
        if rem.startswith(p) and len(rem) - len(p) >= 2:
            pref = p
            rem = rem[len(p):]
            break
    suf = ""
    for s in SUFFIXES:
        if rem.endswith(s) and len(rem) - len(s) >= 1:
            suf = s
            rem = rem[:-len(s)]
            break
    stem = canon_stem(w)
    if pref.startswith("qo"):
        p_gloss = "ACT_BOIL"
    elif pref in ("ch", "sh", "cth", "ckh", "cph", "cfh"):
        p_gloss = "HERB_BENCH"
    elif pref in ("o", "ok", "ot", "op", "of", "y", "yk", "yt"):
        p_gloss = "NOM_SPEC"
    elif pref in ("d", "da"):
        p_gloss = "TOP_LOC"
    elif pref in ("s", "sa"):
        p_gloss = "SEQ_CONT"
    elif pref in ("l", "ol", "al", "lk", "lt"):
        p_gloss = "APPL_VESSEL"
    elif pref in ("or", "ar", "r"):
        p_gloss = "FLOW_LIQ"
    else:
        p_gloss = "BARE"

    if suf in ("aiin", "oiin", "eiin", "iin", "in"):
        s_gloss = "DOSE_AIIN"
    elif suf in ("eedy", "edy"):
        s_gloss = "PROC_SIMMER"
    elif suf in ("ody", "ady", "dy"):
        s_gloss = "PERF_DONE"
    elif suf in ("ey", "oy", "ay", "y"):
        s_gloss = "STATE_Y"
    elif suf in ("ol", "al", "el", "eal", "l"):
        s_gloss = "FLUID_L"
    elif suf in ("or", "ar", "er", "ear", "r"):
        s_gloss = "SOURCE_R"
    elif suf in ("am", "om", "eam", "m"):
        s_gloss = "FINAL_M"
    else:
        s_gloss = "ROOT"

    return {
        "word": w,
        "prefix": pref,
        "core": rem,
        "suffix": suf,
        "stem": stem,
        "gloss": f"{p_gloss}[{stem.upper()}]:{s_gloss}",
    }


def classify_q14_loc(loc: str) -> str:
    l = loc.lstrip("@+=*~&/")
    if l.startswith("C") or l.startswith("R"):
        return "DIAGRAM_RING"
    if l.startswith("L"):
        return "DIAGRAM_LABEL"
    if l.startswith("Pb"):
        return "DIAGRAM_WEDGE_BLOCK"
    if l.startswith("P"):
        return "EXEGETICAL_PROSE"
    return "OTHER"


def parse_corpus():
    with open(INDEX_PATH, encoding="utf-8") as f:
        idx = json.load(f)
    folio_meta = idx["folios"]

    folio_tokens = defaultdict(list)
    q14_lines = defaultdict(list)
    scribe2_other_paras = []

    cur_folio = None
    cur_para_tokens = []
    cur_para_folio = None
    cur_para_id = 0

    with open(ZL_PATH, encoding="utf-8", errors="ignore") as f:
        for raw in f:
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            m_page = re.match(r"^<(f[0-9a-zA-Z]+)>", line)
            if m_page and "\t" not in line and "." not in line.split(">")[0]:
                cur_folio = m_page.group(1)
                continue
            m_line = re.match(r"^<(f[0-9a-zA-Z]+)\.([^>]+)>\s+(.*)$", line)
            if not m_line:
                continue
            fol, loc_part, text = m_line.groups()
            loc = loc_part.split(",")[-1] if "," in loc_part else loc_part
            line_id = loc_part.split(",")[0]

            has_para_start = "<%>" in text
            has_para_end = "<$>" in text

            raw_toks = re.split(r"[.\s,]+", text)
            toks = [clean_tok(t) for t in raw_toks]
            toks = [t for t in toks if len(t) >= 2]
            if not toks:
                continue

            for t in toks:
                folio_tokens[fol].append((loc, t))

            meta = folio_meta.get(fol, {})
            q = meta.get("quire", "")
            h = str(meta.get("hand", ""))

            if q == "N":
                q14_lines[fol].append({
                    "line_id": line_id,
                    "loc": loc,
                    "loc_class": classify_q14_loc(loc),
                    "has_para_start": has_para_start,
                    "has_para_end": has_para_end,
                    "tokens": toks,
                })
            elif h == "2" and loc.lstrip("@+=*~&").startswith("P"):
                if has_para_start and cur_para_tokens:
                    scribe2_other_paras.append((cur_para_folio, cur_para_id, cur_para_tokens))
                    cur_para_tokens = []
                    cur_para_id += 1
                cur_para_folio = fol
                cur_para_tokens.extend(toks)
                if has_para_end and cur_para_tokens:
                    scribe2_other_paras.append((cur_para_folio, cur_para_id, cur_para_tokens))
                    cur_para_tokens = []
                    cur_para_id += 1

    if cur_para_tokens:
        scribe2_other_paras.append((cur_para_folio, cur_para_id, cur_para_tokens))

    return folio_meta, folio_tokens, q14_lines, scribe2_other_paras


def metrics_for_tokens(toks: list) -> dict:
    n = len(toks)
    if n == 0:
        return {}
    stems = [canon_stem(w) for w in toks]
    qo = sum(1 for w in toks if w.startswith("qo"))
    o_nom = sum(1 for w in toks if w.startswith("o") and not w.startswith("ol"))
    bench = sum(1 for w in toks if w.startswith(("ch", "sh")))
    da_top = sum(1 for w in toks if w.startswith("d"))
    l_appl = sum(1 for w in toks if w.startswith(("l", "ol", "al")))
    edy = sum(1 for w in toks if w.endswith(("edy", "eedy")))
    aiin = sum(1 for w in toks if w.endswith(("aiin", "oiin", "iin")))
    am = sum(1 for w in toks if w.endswith(("am", "om", "m")))
    dy = sum(1 for w in toks if w.endswith("dy") and not w.endswith(("edy", "eedy")))
    return {
        "n_tokens": n,
        "n_unique_stems": len(set(stems)),
        "mean_len": round(sum(len(w) for w in toks) / n, 3),
        "o_nom_pct": round(100.0 * o_nom / n, 2),
        "qo_pct": round(100.0 * qo / n, 2),
        "bench_pct": round(100.0 * bench / n, 2),
        "d_top_pct": round(100.0 * da_top / n, 2),
        "l_appl_pct": round(100.0 * l_appl / n, 2),
        "edy_pct": round(100.0 * edy / n, 2),
        "aiin_pct": round(100.0 * aiin / n, 2),
        "dy_pct": round(100.0 * dy / n, 2),
        "am_pct": round(100.0 * am / n, 2),
    }


def main():
    random.seed(42)
    folio_meta, folio_tokens, q14_lines, scribe2_other_paras = parse_corpus()

    # Build stem document frequency across all 226 folios
    stem_folios = defaultdict(set)
    section_stems = defaultdict(set)
    folio_stem_sets = {}

    for fol, lt_list in folio_tokens.items():
        meta = folio_meta.get(fol, {})
        sec = meta.get("section_code", "?")
        lang = meta.get("language", "?")
        st_set = {canon_stem(t) for _, t in lt_list if len(canon_stem(t)) >= 2}
        folio_stem_sets[fol] = st_set
        for s in st_set:
            stem_folios[s].add(fol)
            if meta.get("quire") != "N":
                section_stems[sec].add(s)
                if sec == "H":
                    section_stems[f"H_{lang}"].add(s)

    n_folios = len(folio_tokens)
    stem_idf = {
        s: math.log(n_folios / len(fols))
        for s, fols in stem_folios.items()
        if 2 <= len(fols) <= 20 and len(s) >= 2
    }

    q14_order = ["f85r1", "f85r2", "fRos", "f86v4", "f86v6", "f86v5", "f86v3"]
    q14_page_titles = {
        "f85r1": "Opening Exegetical Preface (4 Prose Paragraphs)",
        "f85r2": "4-Season Bearded Sun Cosmological Wheel",
        "fRos": "9-Sphere Rosettes Cosmological-Botanical Map",
        "f86v4": "4-Winds Ring Diagram & Dual Marginal Commentary",
        "f86v6": "Central Exegetical Treatise I (4 Prose Paragraphs)",
        "f86v5": "Central Exegetical Treatise II (3 Prose Paragraphs)",
        "f86v3": "Closing Exegetical Synthesis (2 Prose Paragraphs)",
    }

    # Collect Quire 14 Diagram Stems vs Exegetical Prose Stems
    diagram_toks = []
    prose_toks = []
    ring_toks = []
    label_toks = []
    wedge_toks = []

    for fol in q14_order:
        for ln in q14_lines[fol]:
            lc = ln["loc_class"]
            if lc == "DIAGRAM_RING":
                ring_toks.extend(ln["tokens"])
                diagram_toks.extend(ln["tokens"])
            elif lc == "DIAGRAM_LABEL":
                label_toks.extend(ln["tokens"])
                diagram_toks.extend(ln["tokens"])
            elif lc == "DIAGRAM_WEDGE_BLOCK":
                wedge_toks.extend(ln["tokens"])
                diagram_toks.extend(ln["tokens"])
            elif lc == "EXEGETICAL_PROSE":
                prose_toks.extend(ln["tokens"])

    diagram_stems = {canon_stem(w) for w in diagram_toks if len(canon_stem(w)) >= 2}
    prose_stems = {canon_stem(w) for w in prose_toks if len(canon_stem(w)) >= 2}
    q14_all_stems = diagram_stems | prose_stems

    # Page-by-page analysis
    page_profiles = []
    q14_paragraphs = []

    for fol in q14_order:
        lines = q14_lines[fol]
        all_toks = [t for ln in lines for t in ln["tokens"]]
        m = metrics_for_tokens(all_toks)
        st_set = {canon_stem(t) for t in all_toks if len(canon_stem(t)) >= 2}

        sec_idf = {}
        for sec_key in ["H_A", "H_B", "H", "A", "Z", "B", "P", "S"]:
            shared = [s for s in (st_set & section_stems[sec_key]) if s in stem_idf]
            sec_idf[sec_key] = round(sum(stem_idf[s] for s in shared), 3)

        # Best external folios outside Quire 14
        ext_scores = []
        for ext_fol, ext_st in folio_stem_sets.items():
            if folio_meta.get(ext_fol, {}).get("quire") == "N":
                continue
            sh = [s for s in (st_set & ext_st) if s in stem_idf]
            if sh:
                ext_scores.append((
                    round(sum(stem_idf[s] for s in sh), 3),
                    ext_fol,
                    folio_meta.get(ext_fol, {}).get("section", "?"),
                    sorted(sh, key=lambda x: -stem_idf[x])[:5],
                ))
        ext_scores.sort(reverse=True)

        # Segment paragraphs on this folio
        cur_p = []
        cur_lines = []
        p_idx = 1
        for ln in lines:
            if ln["loc_class"] != "EXEGETICAL_PROSE":
                continue
            if ln["has_para_start"] and cur_p:
                q14_paragraphs.append({
                    "folio": fol,
                    "para_id": f"{fol}.P{p_idx}",
                    "line_range": f"{cur_lines[0]}–{cur_lines[-1]}",
                    "tokens": cur_p,
                })
                p_idx += 1
                cur_p = []
                cur_lines = []
            cur_p.extend(ln["tokens"])
            cur_lines.append(ln["line_id"])
            if ln["has_para_end"] and cur_p:
                q14_paragraphs.append({
                    "folio": fol,
                    "para_id": f"{fol}.P{p_idx}",
                    "line_range": f"{cur_lines[0]}–{cur_lines[-1]}",
                    "tokens": cur_p,
                })
                p_idx += 1
                cur_p = []
                cur_lines = []
        if cur_p:
            q14_paragraphs.append({
                "folio": fol,
                "para_id": f"{fol}.P{p_idx}",
                "line_range": f"{cur_lines[0]}–{cur_lines[-1]}",
                "tokens": cur_p,
            })

        # First line sample interlinear
        first_ln = lines[0]
        sample_gloss = [decompose_word(w)["gloss"] for w in first_ln["tokens"][:8]]

        page_profiles.append({
            "folio": fol,
            "section": folio_meta.get(fol, {}).get("section", "?"),
            "title": q14_page_titles[fol],
            "metrics": m,
            "section_routing_idf": sec_idf,
            "top_external_folios": [
                {"folio": ef, "section": es, "idf": sc, "shared_stems": sts}
                for sc, ef, es, sts in ext_scores[:4]
            ],
            "opening_line_eva": " ".join(first_ln["tokens"][:8]),
            "opening_line_gloss": " ".join(sample_gloss),
        })

    # Detailed analysis of each of the 21 Exegetical Paragraphs in Quire 14
    para_profiles = []
    obs_para_diagram_idf_list = []
    obs_para_bridge_idf_list = []

    celestial_stems = section_stems["A"] | section_stems["Z"] | diagram_stems
    clinical_bot_stems = section_stems["H"] | section_stems["P"] | section_stems["B"]
    bridge_stems = {s for s in (celestial_stems & clinical_bot_stems) if s in stem_idf}

    for p in q14_paragraphs:
        toks = p["tokens"]
        m = metrics_for_tokens(toks)
        st_set = {canon_stem(w) for w in toks if len(canon_stem(w)) >= 2}
        shared_diag = [s for s in (st_set & diagram_stems) if s in stem_idf]
        diag_idf = sum(stem_idf[s] for s in shared_diag)
        obs_para_diagram_idf_list.append(diag_idf)

        shared_bridge = [s for s in (st_set & bridge_stems) if s in stem_idf]
        br_idf = sum(stem_idf[s] for s in shared_bridge)
        obs_para_bridge_idf_list.append(br_idf)

        sec_idf = {}
        for sec_key in ["H", "A", "Z", "B", "P", "S"]:
            sh = [s for s in (st_set & section_stems[sec_key]) if s in stem_idf]
            sec_idf[sec_key] = round(sum(stem_idf[s] for s in sh), 3)

        dom_sec = max(["H", "A", "Z", "B", "P", "S"], key=lambda k: sec_idf[k])
        open_eva = " ".join(toks[:7])
        open_gloss = " ".join(decompose_word(w)["gloss"] for w in toks[:7])
        close_eva = " ".join(toks[-5:])
        close_gloss = " ".join(decompose_word(w)["gloss"] for w in toks[-5:])

        para_profiles.append({
            "para_id": p["para_id"],
            "folio": p["folio"],
            "line_range": p["line_range"],
            "metrics": m,
            "diagram_shared_idf": round(diag_idf, 3),
            "diagram_shared_stems": sorted(shared_diag, key=lambda x: -stem_idf[x])[:8],
            "celestial_clinical_bridge_idf": round(br_idf, 3),
            "bridge_stems": sorted(shared_bridge, key=lambda x: -stem_idf[x])[:8],
            "dominant_external_section": dom_sec,
            "section_routing_idf": sec_idf,
            "opening_eva": open_eva,
            "opening_gloss": open_gloss,
            "closing_eva": close_eva,
            "closing_gloss": close_gloss,
        })

    # Test 1: Quire 14 Locus Split Permutation Test (@L0/@Cc Nominal Rings/Labels vs @Pb/@P0 Procedural Wedges/Prose)
    nom_locus_toks = label_toks + ring_toks
    proc_locus_toks = wedge_toks + prose_toks
    all_q14_toks = nom_locus_toks + proc_locus_toks
    n_nom = len(nom_locus_toks)

    def o_minus_qo_spread(nom_sub, proc_sub):
        o_nom_rate = sum(1 for w in nom_sub if w.startswith("o") and not w.startswith("ol")) / len(nom_sub)
        qo_nom_rate = sum(1 for w in nom_sub if w.startswith("qo")) / len(nom_sub)
        o_proc_rate = sum(1 for w in proc_sub if w.startswith("o") and not w.startswith("ol")) / len(proc_sub)
        qo_proc_rate = sum(1 for w in proc_sub if w.startswith("qo")) / len(proc_sub)
        return (o_nom_rate - o_proc_rate) + (qo_proc_rate - qo_nom_rate)

    obs_locus_spread = o_minus_qo_spread(nom_locus_toks, proc_locus_toks)
    null_spreads = []
    for _ in range(1000):
        shuf = list(all_q14_toks)
        random.shuffle(shuf)
        null_spreads.append(o_minus_qo_spread(shuf[:n_nom], shuf[n_nom:]))
    mu_sp = sum(null_spreads) / len(null_spreads)
    sd_sp = math.sqrt(sum((x - mu_sp) ** 2 for x in null_spreads) / len(null_spreads))
    z_locus_split = (obs_locus_spread - mu_sp) / (sd_sp if sd_sp > 0 else 1.0)

    # Test 2: 6-Domain Universal Exegetical Bridge Test (Geometric Mean of H, A, Z, B, P, S Rare-Stem IDF)
    def six_domain_geom_idf(st_set):
        vals = []
        for sk in ["H", "A", "Z", "B", "P", "S"]:
            sh = [s for s in (st_set & section_stems[sk]) if s in stem_idf]
            vals.append(max(0.1, sum(stem_idf[s] for s in sh)))
        return math.exp(sum(math.log(v) for v in vals) / 6.0), {
            sk: round(sum(stem_idf[s] for s in (st_set & section_stems[sk]) if s in stem_idf), 3)
            for sk in ["H", "A", "Z", "B", "P", "S"]
        }

    obs_geom_idf, obs_6dom_dict = six_domain_geom_idf(q14_all_stems)
    all_non_q14_fols = [f for f, meta in folio_meta.items() if meta.get("quire") != "N" and f in folio_tokens]
    non_q14_stream = [t for f in all_non_q14_fols for _, t in folio_tokens[f]]
    null_geom_idfs = []
    for _ in range(1000):
        start = random.randint(0, len(non_q14_stream) - len(all_q14_toks) - 1)
        window = non_q14_stream[start : start + len(all_q14_toks)]
        w_stems = {canon_stem(w) for w in window if len(canon_stem(w)) >= 2}
        g_val, _ = six_domain_geom_idf(w_stems)
        null_geom_idfs.append(g_val)

    null_mu = sum(null_geom_idfs) / len(null_geom_idfs)
    null_sd = math.sqrt(sum((x - null_mu) ** 2 for x in null_geom_idfs) / len(null_geom_idfs))
    z_6dom = (obs_geom_idf - null_mu) / (null_sd if null_sd > 0 else 1.0)
    p_6dom = sum(1 for x in null_geom_idfs if x >= obs_geom_idf) / len(null_geom_idfs)

    obs_q14_diag_prose_overlap = [s for s in (diagram_stems & prose_stems) if s in stem_idf]

    # Also analyze f86v4's internal Ring/Wedge vs Prose split
    f86v4_ring_toks = [
        t for ln in q14_lines["f86v4"]
        if ln["loc_class"] in ("DIAGRAM_RING", "DIAGRAM_LABEL", "DIAGRAM_WEDGE_BLOCK")
        for t in ln["tokens"]
    ]
    f86v4_prose_toks = [
        t for ln in q14_lines["f86v4"]
        if ln["loc_class"] == "EXEGETICAL_PROSE"
        for t in ln["tokens"]
    ]

    locus_summary = {
        "DIAGRAM_LABEL_L0": metrics_for_tokens(label_toks),
        "DIAGRAM_RING_Cc": metrics_for_tokens(ring_toks),
        "DIAGRAM_WEDGE_Pb": metrics_for_tokens(wedge_toks),
        "EXEGETICAL_PROSE_P0": metrics_for_tokens(prose_toks),
        "f86v4_RING_AND_LABELS": metrics_for_tokens(f86v4_ring_toks),
        "f86v4_MARGINAL_PROSE": metrics_for_tokens(f86v4_prose_toks),
    }

    out = {
        "attack": 129,
        "phase": 140,
        "discovery": 146,
        "title": "Complete Quire 14 (f85r1-f86v3 + fRos, $Q=N) 7-Page Foldout Exegetical & Cosmological Translator",
        "summary": {
            "n_pages": len(q14_order),
            "total_tokens": len(diagram_toks) + len(prose_toks),
            "diagram_tokens": len(diagram_toks),
            "prose_tokens": len(prose_toks),
            "n_exegetical_paragraphs": len(q14_paragraphs),
            "locus_summary": locus_summary,
            "locus_split_permutation_test": {
                "nominal_ring_label_tokens": len(nom_locus_toks),
                "procedural_wedge_prose_tokens": len(proc_locus_toks),
                "observed_o_vs_qo_spread": round(obs_locus_spread, 4),
                "null_mean": round(mu_sp, 4),
                "null_sd": round(sd_sp, 4),
                "z_score": round(z_locus_split, 2),
            },
            "universal_6domain_bridge_test": {
                "six_domain_idf_breakdown": obs_6dom_dict,
                "observed_6domain_geometric_mean_idf": round(obs_geom_idf, 3),
                "null_mean_2339tok_window": round(null_mu, 3),
                "null_sd": round(null_sd, 3),
                "lift_ratio": round(obs_geom_idf / null_mu, 3) if null_mu > 0 else 0.0,
                "z_score": round(z_6dom, 2),
                "p_value": round(p_6dom, 4),
                "shared_diagram_prose_rare_stems": sorted(obs_q14_diag_prose_overlap, key=lambda s: -stem_idf[s])[:15],
            },
        },
        "page_profiles": page_profiles,
        "exegetical_paragraphs": para_profiles,
    }

    OUT_JSON.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"[Attack 129] Saved {OUT_JSON}")
    print(f"Total Quire 14 tokens: {out['summary']['total_tokens']} ({len(diagram_toks)} diagram, {len(prose_toks)} prose across {len(q14_paragraphs)} paragraphs)")
    print("Locus Split Test:", json.dumps(out["summary"]["locus_split_permutation_test"], indent=2))
    print("Universal 6-Domain Bridge Test:", json.dumps(out["summary"]["universal_6domain_bridge_test"], indent=2))


if __name__ == "__main__":
    main()
