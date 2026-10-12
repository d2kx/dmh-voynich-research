#!/usr/bin/env python3
r"""
Attack 118 (Discovery 135): Complete 19-Folio Balneological (`Quire M`, `f75r–f84v`, `$I=B`)
3-Zone Hydraulic Translator & `Ln` (Nymph Label) vs. `Lt` (Tube/Pipe/Tank Apparatus Label) Contrast Solver

Tests & Builds:
1. Parses all `19` transcribed Balneological folios (`f75r–f84v`, `$I=B, $Q=M, $H=2`) into:
   - **`Ln` (`@Ln, =Ln, +Ln, ~Ln, *Ln`)**: Bather / Nymph Figure Labels (`63` loci),
   - **`Lt` (`@Lt, =Lt, +Lt, ~Lt, *Lt`)**: Tube / Pipe / Tank / Conduit Apparatus Labels (`47` loci),
   - **`L0` (`*L0, =L0, ~L0, +L0`)**: General Marginal/Diagram Labels (`15` loci),
   - **`P` (`P0, P1, Pb, Pr`)**: Hydraulic Prose Paragraphs (`TOP_INFLOW_ZONE`, `MID_CONDUIT_ZONE`, `BOTTOM_POOL_ZONE`).
2. Quantitative Contrast Between `Ln` (Nymph Labels) and `Lt` (Tube/Pipe/Tank Apparatus Labels):
   - Compares word length, Gallows density (`k/t/p/f`), Nominal `o-`, Aqueous Applicative `l-/ol-/qol-`,
     Plumed `sh` spray, State `-y/-dy`, Container/Spout `-ol/-or/-al/-ar`, and cross-section attestation (`B`, `H`, `P`, `S`).
3. Traces all Balneological Labels (`Ln + Lt + L0`) across Same-Folio, Same-Bifolio (`$B`), Quire M (`$I=B`),
   and Herbal Monographs (`$I=H`), plus 2-to-3-stem compound decomposition.
4. Quantifies the 3-Zone Vertical Hydraulic Gradient (`TOP_INFLOW_ZONE -> MID_CONDUIT_ZONE -> BOTTOM_POOL_ZONE`,
   plus `@Pb / +Pb` Bottom Basin Prose) and builds the Complete 19-Folio Balneological Translation Atlas.
"""

import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ZL_PATH = ROOT / "data" / "ZL3b-n.txt"
OUT_PATH = ROOT / "data" / "attack118_balneological_19folio_hydraulic_and_nymph_translator.json"


def normalize_token(w: str) -> str:
    w = re.sub(r"\[([^:\]]+):[^\]]+\]", r"\1", w)
    w = re.sub(r"\{[^}]*\}", "", w)
    w = re.sub(r"<[^>]*>", "", w)
    w = w.replace("?", "").replace("!", "").replace("*", "").replace("%", "").strip()
    return w


def canonical_stem(w: str, is_top_line: bool = False) -> str:
    s = w
    if is_top_line:
        s = s.replace("p", "t").replace("f", "k")
    if s.startswith("qo") and len(s) > 2:
        s = s[1:]
    elif s.startswith("q") and len(s) > 2:
        s = s[1:]
    s = re.sub(r"i{2,}", "ii", s)
    s = re.sub(r"e{2,}", "ee", s)
    if len(s) >= 4 and s.endswith("dy"):
        s = s[:-2] + "y"
    return s


def folded_stem(w: str) -> str:
    s = w.replace("p", "t").replace("f", "k")
    if s.endswith("g"):
        s = s[:-1] + "m"
    return canonical_stem(s, is_top_line=True)


def strip_o_prefix(cs: str) -> str:
    if cs.startswith("o") and not cs.startswith(("ol", "or")) and len(cs) >= 4:
        return canonical_stem(cs[1:], is_top_line=True)
    return cs


BALNEO_GLOSS = {
    "qokedy": "FLOW/INFUSE-ACTIVE [stream]",
    "qokeedy": "SURGE/BOIL-STREAM [active]",
    "qokeey": "POUR/INFUSE-STEADY",
    "qokaiin": "DRAW-ONE-MEASURE [inflow]",
    "qokain": "DRAW-MEASURE [inflow]",
    "qokol": "HEAT-BATH-VESSEL",
    "qol": "INTO-THE-POOL [aqueous]",
    "ol": "THE-POOL/WATER",
    "al": "TO-THE-BASIN",
    "or": "STREAM-PORTION",
    "ar": "AT-THE-CONDUIT",
    "dar": "INTO-THE-PIPE/BASIN",
    "dal": "FROM-THE-BASIN",
    "daiin": "FROM-THIS-STREAM [1-measure]",
    "dain": "FROM-THIS-STREAM [measure]",
    "aiin": "ONE-VOLUME [measure]",
    "shedy": "SPRAY/SHOWER-FLOW [plumed]",
    "sheedy": "HEAVY-SHOWER-FLOW [plumed]",
    "chedy": "CHANNEL-MIX [bench]",
    "cheedy": "STEADY-CHANNEL-MIX",
    "shol": "SHOWER-FLUID",
    "sheol": "INFUSED-BATH-WATER",
    "chol": "HERB-BATH-EXTRACT",
    "cheol": "STEEPED-BATH-LIQUID",
    "lchedy": "POOL-MIX-APPLICATIVE",
    "lshedy": "POOL-SHOWER-APPLICATIVE",
    "lkedy": "POOL-HEAT-APPLICATIVE",
    "lkeedy": "POOL-BOIL-APPLICATIVE",
    "olchedy": "IN-WATER-MIX",
    "olshedy": "IN-WATER-SHOWER",
}


def gloss_balneo_word(w: str, is_top: bool = False) -> str:
    if w in BALNEO_GLOSS:
        return BALNEO_GLOSS[w]
    cs = canonical_stem(w, is_top)
    if cs in BALNEO_GLOSS:
        return BALNEO_GLOSS[cs]

    parts = []
    s = w
    if s.startswith("qol"):
        parts.append("INTO-POOL")
        s = s[3:]
    elif s.startswith("qo"):
        parts.append("FLOW/HEAT")
        s = s[2:]
    elif s.startswith(("ol", "l")) and len(s) >= 4:
        parts.append("IN-BATH")
        s = s[2:] if s.startswith("ol") else s[1:]
    elif s.startswith("o") and not s.startswith(("ol", "or")) and len(s) >= 4:
        parts.append("NOM-STATION")
        s = s[1:]
    elif s.startswith(("d", "da")) and len(s) >= 4:
        parts.append("PIPE/FROM")
        s = s[2:] if s.startswith("da") else s[1:]
    elif s.startswith(("s", "sa")) and len(s) >= 4:
        parts.append("NEXT-STREAM")
        s = s[2:] if s.startswith("sa") else s[1:]

    if "sh" in s:
        parts.append("VAPOR/SPRAY")
    elif "ch" in s:
        parts.append("CONDUIT/MIX")
    elif any(r in s for r in ("k", "t", "p", "f")):
        parts.append("VALVE/SOURCE")
    else:
        parts.append("WATER")

    if w.endswith(("edy", "eedy")):
        parts.append("[FLOWING]")
    elif w.endswith(("aiin", "oiin", "iin", "ain")):
        parts.append("[VOLUME]")
    elif w.endswith(("ol", "al")):
        parts.append("[POOL]")
    elif w.endswith(("or", "ar")):
        parts.append("[SPOUT]")
    elif w.endswith(("am", "om", "m")):
        parts.append("[DRAIN-END]")
    elif w.endswith(("dy", "y")):
        parts.append("[BATHED]")

    return "-".join(parts) + f" ({cs})"


def zone_morph_profile(tokens):
    n = len(tokens)
    if n == 0:
        return {}
    mean_chars = sum(len(w) for w, _, _ in tokens) / n
    gallows_cnt = sum(1 for w, _, _ in tokens if any(g in w for g in ("k", "t", "p", "f")))
    qo_cnt = sum(1 for w, _, _ in tokens if w.startswith("qo"))
    o_cnt = sum(1 for w, _, _ in tokens if w.startswith("o") and not w.startswith(("ol", "or", "qo")))
    l_app = sum(1 for w, _, _ in tokens if w.startswith(("l", "ol", "qol")) and len(w) >= 3)
    d_cnt = sum(1 for w, _, _ in tokens if w.startswith(("d", "da")))
    s_cnt = sum(1 for w, _, _ in tokens if w.startswith(("s", "sa")))
    sh_cnt = sum(1 for w, _, _ in tokens if "sh" in w)
    edy_cnt = sum(1 for w, _, _ in tokens if w.endswith(("edy", "eedy")))
    dy_y_cnt = sum(1 for w, _, _ in tokens if w.endswith("y") and not w.endswith(("edy", "eedy")))
    ol_or_cnt = sum(1 for w, _, _ in tokens if w.endswith(("ol", "or", "al", "ar")))
    aiin_cnt = sum(1 for w, _, _ in tokens if w.endswith(("aiin", "oiin", "iin", "ain")))
    am_cnt = sum(1 for w, _, _ in tokens if w.endswith(("am", "om", "m")))
    return {
        "n_tokens": n,
        "mean_word_length_chars": round(mean_chars, 2),
        "gallows_ktpf_pct": round(100.0 * gallows_cnt / n, 2),
        "qo_active_flow_pct": round(100.0 * qo_cnt / n, 2),
        "o_nominal_pct": round(100.0 * o_cnt / n, 2),
        "l_ol_qol_aqueous_applicative_pct": round(100.0 * l_app / n, 2),
        "d_da_pipe_deictic_pct": round(100.0 * d_cnt / n, 2),
        "s_sa_continuation_pct": round(100.0 * s_cnt / n, 2),
        "sh_plumed_spray_pct": round(100.0 * sh_cnt / n, 2),
        "edy_processual_flow_pct": round(100.0 * edy_cnt / n, 2),
        "dy_y_bathed_state_pct": round(100.0 * dy_y_cnt / n, 2),
        "ol_or_al_ar_vessel_spout_pct": round(100.0 * ol_or_cnt / n, 2),
        "aiin_pool_volume_pct": round(100.0 * aiin_cnt / n, 2),
        "am_m_drain_closure_pct": round(100.0 * am_cnt / n, 2),
    }


def main():
    folio_meta_re = re.compile(r"^<f([0-9]+[rv][0-9]*)>\s*<!\s*(.*?)\s*>$")
    line_re = re.compile(r"^<f([0-9]+[rv][0-9]*)\.([0-9]+),([^>]+)>\s+(.*)$")

    folios_meta = {}
    canon_counts = Counter()
    folio_canon_set = defaultdict(set)

    herbal_folios = defaultdict(set)
    pharm_folios = defaultdict(set)
    starred_folios = defaultdict(set)
    balneo_prose_by_folio = defaultdict(set)

    balneo_folios = defaultdict(lambda: {
        "paragraphs": [],   # list of dicts
        "ln_labels": [],    # Nymph labels: (loc, lnum, w, cs, fcs, ncs)
        "lt_labels": [],    # Tube/Pipe/Tank labels: (loc, lnum, w, cs, fcs, ncs)
        "l0_labels": [],    # General labels: (loc, lnum, w, cs, fcs, ncs)
        "all_labels": [],   # (ltype_sub, loc, lnum, w, cs, fcs, ncs)
    })

    current_b_para = {}
    in_para_top = defaultdict(lambda: True)

    with open(ZL_PATH, "r", encoding="utf-8", errors="replace") as f:
        for raw_line in f:
            sline = raw_line.strip()
            mf = folio_meta_re.match(sline)
            if mf:
                fol = "f" + mf.group(1)
                meta_str = mf.group(2)
                m_dict = {}
                for kv in meta_str.split():
                    if "=" in kv:
                        k, v = kv.lstrip("$").split("=", 1)
                        m_dict[k] = v
                folios_meta[fol] = {
                    "section": m_dict.get("I", ""),
                    "language": m_dict.get("L", ""),
                    "hand": m_dict.get("H", ""),
                    "quire": m_dict.get("Q", ""),
                    "bifolio": m_dict.get("B", ""),
                }
                continue

            m = line_re.match(sline)
            if not m:
                continue
            fol = "f" + m.group(1)
            lnum = int(m.group(2))
            loc = m.group(3)
            text = m.group(4)

            sec = folios_meta.get(fol, {}).get("section", "")
            has_para_start = "<%>" in text or loc.startswith(("@P", "*P", "=P"))
            has_para_end = "<$>" in text

            clean_line = re.sub(r"<[^>]*>", " ", text)
            raw_tokens = [t for t in re.split(r"[.\s,]+", clean_line) if t]
            words = [normalize_token(t) for t in raw_tokens]
            words = [w for w in words if w and re.search(r"[a-z]", w)]
            if not words:
                if has_para_end:
                    in_para_top[fol] = True
                continue

            loc_clean = loc.lstrip("@+=*~")
            is_label = loc_clean.startswith("L")
            is_top = (not is_label) and (has_para_start or lnum == 1 or in_para_top[fol])

            stems = []
            for w in words:
                cs = canonical_stem(w, is_top)
                fcs = folded_stem(w)
                ncs = strip_o_prefix(fcs)
                canon_counts[cs] += 1
                folio_canon_set[fol].add(cs)
                stems.append((w, cs, fcs, ncs, is_top))

            if sec == "H" and fol not in ("f58r", "f58v"):
                for _, cs, fcs, ncs, _ in stems:
                    herbal_folios[fol].update((cs, fcs, ncs))
            elif sec == "P":
                for _, cs, fcs, ncs, _ in stems:
                    pharm_folios[fol].update((cs, fcs, ncs))
            elif sec == "S" or fol in ("f58r", "f58v"):
                for _, cs, fcs, ncs, _ in stems:
                    starred_folios[fol].update((cs, fcs, ncs))
            elif sec == "B":
                if is_label:
                    lsub = loc_clean[:2]  # Ln, Lt, L0
                    for w, cs, fcs, ncs, _ in stems:
                        item = (f"{fol}.{lnum},{loc}", lnum, w, cs, fcs, ncs)
                        balneo_folios[fol]["all_labels"].append((lsub, f"{fol}.{lnum},{loc}", lnum, w, cs, fcs, ncs))
                        if lsub == "Ln":
                            balneo_folios[fol]["ln_labels"].append(item)
                        elif lsub == "Lt":
                            balneo_folios[fol]["lt_labels"].append(item)
                        else:
                            balneo_folios[fol]["l0_labels"].append(item)
                else:
                    for _, cs, fcs, ncs, _ in stems:
                        balneo_prose_by_folio[fol].update((cs, fcs, ncs))
                    if has_para_start or fol not in current_b_para:
                        pnum = len(balneo_folios[fol]["paragraphs"]) + 1
                        pobj = {
                            "para_id": f"{fol}.P{pnum}",
                            "para_num": pnum,
                            "loc_type": loc_clean,
                            "start_line": lnum,
                            "end_line": lnum,
                            "tokens": [],  # (w, cs, is_top)
                            "lines": [],   # (lnum, [(w, cs, is_top)])
                        }
                        balneo_folios[fol]["paragraphs"].append(pobj)
                        current_b_para[fol] = pobj
                    pobj = current_b_para[fol]
                    pobj["end_line"] = lnum
                    ltoks = [(w, cs, itop) for w, cs, _, _, itop in stems]
                    pobj["tokens"].extend(ltoks)
                    pobj["lines"].append((lnum, ltoks))

            if not is_label:
                in_para_top[fol] = False
            if has_para_end:
                in_para_top[fol] = True

    # Open-class filter
    top45_cs = {w for w, _ in canon_counts.most_common(45)}
    stem_df = Counter()
    for fol, sset in folio_canon_set.items():
        for cs in sset:
            stem_df[cs] += 1
    N_folios = len(folio_canon_set)
    open_stems = {cs for cs, df in stem_df.items() if cs not in top45_cs and len(cs) >= 3 and 2 <= df <= 95}
    stem_idf = {cs: math.log(N_folios / (1.0 + stem_df[cs])) for cs in open_stems}
    attested_vocab = {cs for cs, cnt in canon_counts.items() if cnt >= 2 and len(cs) >= 2}

    all_b_prose_stems = set().union(*balneo_prose_by_folio.values())
    all_h_stems = set().union(*herbal_folios.values())
    all_p_stems = set().union(*pharm_folios.values())
    all_s_stems = set().union(*starred_folios.values())

    # 1. Compare Ln (Nymph Labels) vs Lt (Tube/Pipe/Tank Apparatus Labels) vs L0 (General Labels)
    all_ln_toks = [(w, cs, False) for fol in balneo_folios for _, _, w, cs, _, _ in balneo_folios[fol]["ln_labels"]]
    all_lt_toks = [(w, cs, False) for fol in balneo_folios for _, _, w, cs, _, _ in balneo_folios[fol]["lt_labels"]]
    all_l0_toks = [(w, cs, False) for fol in balneo_folios for _, _, w, cs, _, _ in balneo_folios[fol]["l0_labels"]]

    # 2. Trace all Balneological Labels (Ln, Lt, L0)
    nymph_traces = []
    trace_breakdown = Counter()
    sub_stats = defaultdict(lambda: Counter())

    for fol in sorted(balneo_folios.keys()):
        b_id = folios_meta[fol]["bifolio"]
        same_bifol_stems = set()
        for f2, m2 in folios_meta.items():
            if m2.get("section") == "B" and m2.get("bifolio") == b_id:
                same_bifol_stems |= balneo_prose_by_folio[f2]

        for lsub, loc, lnum, w, cs, fcs, ncs in balneo_folios[fol]["all_labels"]:
            cands = {cs, fcs, ncs}
            same_fol = bool(cands & balneo_prose_by_folio[fol])
            same_bif = bool(cands & same_bifol_stems)
            in_qm = bool(cands & all_b_prose_stems)
            in_h = bool(cands & all_h_stems)
            in_p = bool(cands & all_p_stems)
            in_s = bool(cands & all_s_stems)

            ttype = "UNRESOLVED"
            parts = [fcs]
            if same_fol or same_bif or in_qm or in_h or in_p or in_s:
                ttype = "DIRECT_OR_O_STRIPPED"
            else:
                s = w.replace("p", "t").replace("f", "k")
                for cand in (s, s[1:] if s.startswith("o") and len(s) >= 5 else ""):
                    if not cand:
                        continue
                    for i in range(2, len(cand) - 1):
                        p1, p2 = canonical_stem(cand[:i], True), canonical_stem(cand[i:], True)
                        if p1 in attested_vocab and p2 in attested_vocab:
                            ttype = "TWO_STEM_COMPOUND"
                            parts = [p1, p2]
                            if p1 in all_b_prose_stems or p2 in all_b_prose_stems:
                                in_qm = True
                            if p1 in all_h_stems or p2 in all_h_stems:
                                in_h = True
                            break
                    if ttype != "UNRESOLVED":
                        break
                    for i in range(2, len(cand) - 2):
                        p1, p2 = canonical_stem(cand[:i], True), canonical_stem(cand[i:-1], True)
                        if p1 in attested_vocab and len(p2) >= 2 and p2 in attested_vocab:
                            ttype = "TWO_STEM_PLUS_CODA"
                            parts = [p1, p2]
                            if p1 in all_b_prose_stems or p2 in all_b_prose_stems:
                                in_qm = True
                            if p1 in all_h_stems or p2 in all_h_stems:
                                in_h = True
                            break
                    if ttype != "UNRESOLVED":
                        break

            trace_breakdown[ttype] += 1
            sub_stats[lsub]["n"] += 1
            if ttype != "UNRESOLVED":
                sub_stats[lsub]["resolved"] += 1
            if same_fol:
                sub_stats[lsub]["same_fol"] += 1
            if same_bif:
                sub_stats[lsub]["same_bif"] += 1
            if in_qm:
                sub_stats[lsub]["in_qm"] += 1
            if in_h:
                sub_stats[lsub]["in_h"] += 1

            nymph_traces.append({
                "folio": fol,
                "label_subtype": lsub,
                "loc": loc,
                "surface": w,
                "folded_cs": fcs,
                "o_stripped_cs": ncs,
                "trace_type": ttype,
                "constituent_stems": parts,
                "in_same_folio_prose": same_fol,
                "in_same_bifolio_prose": same_bif,
                "in_quire_m_prose": in_qm,
                "in_herbal_monographs": in_h,
                "nymph_gloss": gloss_balneo_word(w, False),
            })

    # 3. Classify all Balneological Paragraphs into 3 Vertical Hydraulic Zones (plus Pb Bottom Basin blocks)
    zone_tokens = {
        "ZONE_1_TOP_INFLOW": [],
        "ZONE_2_MID_CONDUIT": [],
        "ZONE_3_BOTTOM_POOL": [],
        "LOCUS_PB_BASIN_BLOCKS": [],
    }

    folio_records = []
    h_open_map = {h: s & open_stems for h, s in herbal_folios.items()}
    p_open_map = {p: s & open_stems for p, s in pharm_folios.items()}

    for fol in sorted(balneo_folios.keys()):
        bdata = balneo_folios[fol]
        paras = bdata["paragraphs"]
        n_p = len(paras)
        fol_open = balneo_prose_by_folio[fol] & open_stems

        h_scores = []
        for hfol, hset in h_open_map.items():
            shared = fol_open & hset
            if shared:
                h_scores.append({
                    "herbal_folio": hfol,
                    "language": folios_meta.get(hfol, {}).get("language", ""),
                    "idf_score": round(sum(stem_idf[c] for c in shared), 3),
                    "n_shared": len(shared),
                    "shared_stems": sorted(shared)[:10],
                })
        h_scores.sort(key=lambda x: (-x["idf_score"], -x["n_shared"]))

        p_scores = []
        for pfol, pset in p_open_map.items():
            shared = fol_open & pset
            if shared:
                p_scores.append({
                    "pharm_folio": pfol,
                    "idf_score": round(sum(stem_idf[c] for c in shared), 3),
                    "n_shared": len(shared),
                    "shared_stems": sorted(shared)[:8],
                })
        p_scores.sort(key=lambda x: (-x["idf_score"], -x["n_shared"]))

        para_records = []
        for idx, pobj in enumerate(paras):
            if idx == 0:
                zname = "ZONE_1_TOP_INFLOW"
            elif idx == n_p - 1 and n_p >= 2:
                zname = "ZONE_3_BOTTOM_POOL"
            else:
                zname = "ZONE_2_MID_CONDUIT"

            zone_tokens[zname].extend(pobj["tokens"])
            if pobj["loc_type"] == "Pb":
                zone_tokens["LOCUS_PB_BASIN_BLOCKS"].extend(pobj["tokens"])

            first_lnum, first_toks = pobj["lines"][0]
            last_lnum, last_toks = pobj["lines"][-1]
            para_records.append({
                "para_id": pobj["para_id"],
                "loc_type": pobj["loc_type"],
                "hydraulic_zone": zname,
                "line_span": f"L{pobj['start_line']}-L{pobj['end_line']}",
                "n_tokens": len(pobj["tokens"]),
                "morph_profile": zone_morph_profile(pobj["tokens"]),
                "opening_line_eva": " . ".join(w for w, _, _ in first_toks),
                "opening_line_translation": " | ".join(f"{w} [{gloss_balneo_word(w, itop)}]" for w, _, itop in first_toks),
                "closing_line_eva": " . ".join(w for w, _, _ in last_toks),
                "closing_line_translation": " | ".join(f"{w} [{gloss_balneo_word(w, itop)}]" for w, _, itop in last_toks),
            })

        folio_records.append({
            "folio": fol,
            "bifolio": folios_meta[fol]["bifolio"],
            "n_paragraphs": n_p,
            "n_ln_nymph_labels": len(bdata["ln_labels"]),
            "n_lt_tube_labels": len(bdata["lt_labels"]),
            "n_l0_general_labels": len(bdata["l0_labels"]),
            "labels": [
                {"subtype": tr["label_subtype"], "loc": tr["loc"], "w": tr["surface"], "gloss": tr["nymph_gloss"], "same_bifolio": tr["in_same_bifolio_prose"], "in_herbal": tr["in_herbal_monographs"]}
                for tr in nymph_traces if tr["folio"] == fol
            ],
            "top_herbal_infusion_partners": h_scores[:3],
            "top_pharm_formulary_partners": p_scores[:2],
            "paragraphs": para_records,
        })

    n_lbl_total = len(nymph_traces)
    tot_same_fol = sum(sub_stats[k]["same_fol"] for k in sub_stats)
    tot_same_bif = sum(sub_stats[k]["same_bif"] for k in sub_stats)
    tot_in_qm = sum(sub_stats[k]["in_qm"] for k in sub_stats)
    tot_in_h = sum(sub_stats[k]["in_h"] for k in sub_stats)

    summary = {
        "attack_id": 118,
        "discovery_id": 135,
        "title": "Complete 19-Folio Balneological (Quire M, f75r-f84v) 3-Zone Hydraulic Translator & Ln vs Lt Contrast Solver",
        "n_balneological_folios": len(folio_records),
        "n_total_paragraphs": sum(len(f["paragraphs"]) for f in folio_records),
        "label_subtype_comparison": {
            "Ln_nymph_labels": {
                "morph_profile": zone_morph_profile(all_ln_toks),
                "in_same_bifolio_pct": round(100.0 * sub_stats["Ln"]["same_bif"] / max(1, sub_stats["Ln"]["n"]), 2),
                "in_quire_m_prose_pct": round(100.0 * sub_stats["Ln"]["in_qm"] / max(1, sub_stats["Ln"]["n"]), 2),
                "in_herbal_monographs_pct": round(100.0 * sub_stats["Ln"]["in_h"] / max(1, sub_stats["Ln"]["n"]), 2),
            },
            "Lt_tube_pipe_tank_labels": {
                "morph_profile": zone_morph_profile(all_lt_toks),
                "in_same_bifolio_pct": round(100.0 * sub_stats["Lt"]["same_bif"] / max(1, sub_stats["Lt"]["n"]), 2),
                "in_quire_m_prose_pct": round(100.0 * sub_stats["Lt"]["in_qm"] / max(1, sub_stats["Lt"]["n"]), 2),
                "in_herbal_monographs_pct": round(100.0 * sub_stats["Lt"]["in_h"] / max(1, sub_stats["Lt"]["n"]), 2),
            },
            "L0_general_labels": {
                "morph_profile": zone_morph_profile(all_l0_toks),
                "in_same_bifolio_pct": round(100.0 * sub_stats["L0"]["same_bif"] / max(1, sub_stats["L0"]["n"]), 2),
                "in_quire_m_prose_pct": round(100.0 * sub_stats["L0"]["in_qm"] / max(1, sub_stats["L0"]["n"]), 2),
                "in_herbal_monographs_pct": round(100.0 * sub_stats["L0"]["in_h"] / max(1, sub_stats["L0"]["n"]), 2),
            },
        },
        "nymph_and_apparatus_label_audit": {
            "total_labels": n_lbl_total,
            "trace_type_breakdown": dict(trace_breakdown),
            "resolved_total_count": n_lbl_total - trace_breakdown["UNRESOLVED"],
            "resolved_total_pct": round(100.0 * (n_lbl_total - trace_breakdown["UNRESOLVED"]) / max(1, n_lbl_total), 2),
            "in_same_folio_prose_pct": round(100.0 * tot_same_fol / max(1, n_lbl_total), 2),
            "in_same_bifolio_prose_pct": round(100.0 * tot_same_bif / max(1, n_lbl_total), 2),
            "in_quire_m_prose_pct": round(100.0 * tot_in_qm / max(1, n_lbl_total), 2),
            "in_herbal_monographs_pct": round(100.0 * tot_in_h / max(1, n_lbl_total), 2),
        },
        "three_zone_hydraulic_gradient": {
            z: zone_morph_profile(toks) for z, toks in zone_tokens.items()
        },
        "folios": folio_records,
    }

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    print("=== ATTACK 118: 19-FOLIO BALNEOLOGICAL 3-ZONE HYDRAULIC & Ln vs Lt SOLVER ===")
    na = summary["nymph_and_apparatus_label_audit"]
    print(f"Balneo Folios: {summary['n_balneological_folios']} | Total Paragraphs: {summary['n_total_paragraphs']} | Total L-Labels: {na['total_labels']}")
    print(f"Total Label Resolution: {na['resolved_total_count']}/{na['total_labels']} ({na['resolved_total_pct']}%) | Same-Bifolio: {na['in_same_bifolio_prose_pct']}% | Quire M: {na['in_quire_m_prose_pct']}% | Herbal $I=H: {na['in_herbal_monographs_pct']}%")
    print("Label Subtype Comparison (Ln Nymph vs Lt Tube/Pipe/Tank vs L0 General):")
    for k, v in summary["label_subtype_comparison"].items():
        print(f"  {k:26s}: {v}")
    print("3-Zone Vertical Hydraulic Gradient:")
    for z, mp in summary["three_zone_hydraulic_gradient"].items():
        print(f"  {z:24s}: {mp}")


if __name__ == "__main__":
    main()
