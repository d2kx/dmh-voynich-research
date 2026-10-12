#!/usr/bin/env python3
"""
Adversarial Verification Suite for Wave 48 (Attacks 201–204 / Discoveries 218–221)
Executed by Challenger M2 to independently verify Worker M2 deliverables.
"""

import json
import math
import random
import re
import subprocess
import time
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ZL_PATH = ROOT / "data" / "ZL3b-n.txt"
INDEX_PATH = ROOT / "data" / "folio_index.json"

A201_JSON = ROOT / "data" / "attack201_sagittarius_centaur_archer_and_ecliptic_drift.json"
A202_JSON = ROOT / "data" / "attack202_pharmaceutical_albarelli_registers_and_recipe_bridge.json"
A203_JSON = ROOT / "data" / "attack203_quire20_star_point_morphology_and_formulary_clusters.json"
A204_JSON = ROOT / "data" / "attack204_wave48_master_compendium.json"
MD_PATH = ROOT / "notes" / "WAVE48_MASTER_COMPENDIUM.md"

PREFIXES = ["qo", "ch", "sh", "ok", "ot", "ol", "or", "op", "of", "od", "da", "sa", "yk", "yt", "yd", "o", "d", "s", "y", "l", "r"]
SUFFIXES = ["aiin", "oiin", "eiin", "chedy", "shedy", "edy", "ody", "eey", "ey", "chy", "shy", "dy", "ol", "or", "al", "ar", "am", "om", "an", "in", "y", "r", "l", "m", "s"]


def clean_word(w: str) -> str:
    w = re.sub(r"\[([^:\]]+):[^\]]+\]", r"\1", w)
    w = re.sub(r"\{[^}]*\}", "", w)
    w = re.sub(r"<[^>]*>", "", w)
    w = w.replace("?", "").replace("!", "").replace("*", "").replace("%", "").replace("$", "")
    return w.strip()


def canonical_stem(w: str) -> str:
    s = w
    s = s.replace("ch", "C").replace("sh", "S").replace("ckh", "K").replace("cth", "T").replace("cph", "P").replace("cfh", "F")
    s = re.sub(r"e+", "e", s)
    s = re.sub(r"i+", "i", s)
    s = re.sub(r"o+", "o", s)
    w2 = s.replace("C", "ch").replace("S", "sh").replace("K", "kh").replace("T", "th").replace("P", "ph").replace("F", "fh")
    if w2.endswith(("m", "g")) and len(w2) > 2:
        w2 = w2[:-1] + "r"
    for p in PREFIXES:
        if w2.startswith(p) and len(w2) - len(p) >= 2:
            w2 = w2[len(p):]
            break
    for suf in SUFFIXES:
        if w2.endswith(suf) and len(w2) - len(suf) >= 2:
            w2 = w2[:-len(suf)]
            break
    if w2 and w2[0] in ("p", "f", "k", "t"):
        w2 = "K" + w2[1:]
    return w2 if w2 else w


def verify_scripts_execution():
    print("=== 1. Verifying Scripts Re-Execution and Runtime Performance ===")
    scripts = [
        "tools/attack201_sagittarius_centaur_archer_and_ecliptic_drift.py",
        "tools/attack202_pharmaceutical_albarelli_registers_and_recipe_bridge.py",
        "tools/attack203_quire20_star_point_morphology_and_formulary_clusters.py",
        "tools/attack204_wave48_master_compendium.py",
    ]
    total_time = 0.0
    for s in scripts:
        t0 = time.time()
        res = subprocess.run(["python", s], capture_output=True, text=True, cwd=str(ROOT))
        dt = time.time() - t0
        total_time += dt
        assert res.returncode == 0, f"{s} failed with exit code {res.returncode}: {res.stderr}"
        assert dt < 5.0, f"{s} exceeded runtime budget (took {dt:.2f}s)"
        print(f"  PASS: {s} (exit 0, {dt:.3f}s)")
    print(f"All 4 scripts executed in {total_time:.3f}s total (budget < 20s).\n")


def verify_attack201():
    print("=== 2. Adversarially Verifying Attack 201 (Discovery 218) ===")
    assert A201_JSON.exists(), "attack201 JSON missing"
    a201 = json.loads(A201_JSON.read_text(encoding="utf-8"))

    raw_lines = ZL_PATH.read_text(encoding="utf-8", errors="ignore").splitlines()
    f73r_lines = [l for l in raw_lines if l.startswith("<f73r.")]
    f73v_lines = [l for l in raw_lines if l.startswith("<f73v.")]

    assert len(f73r_lines) == 33, f"Expected 33 lines on f73r, got {len(f73r_lines)}"
    assert len(f73v_lines) == 33, f"Expected 33 lines on f73v, got {len(f73v_lines)}"

    # Parse degree loci directly
    for fol, flines in [("f73r", f73r_lines), ("f73v", f73v_lines)]:
        top_overflow = [l for l in flines if re.match(r"^<f73[rv]\.[1-4],[@&]Lz>", l)]
        mid_ring = [l for l in flines if any(re.match(rf"^<f73[rv]\.{i},[@&]Lz>", l) for i in range(6, 22))]
        inn_ring = [l for l in flines if any(re.match(rf"^<f73[rv]\.{i},[@&]Lz>", l) for i in range(23, 33))]
        cc_outer = [l for l in flines if re.match(r"^<f73[rv]\.5,[@&]Cc>", l)]
        cc_middle = [l for l in flines if re.match(r"^<f73[rv]\.22,[@&]Cc>", l)]
        cc_inner = [l for l in flines if re.match(r"^<f73[rv]\.33,[@&]Cc>", l)]

        assert len(top_overflow) == 4, f"{fol}: Expected 4 top overflow loci, got {len(top_overflow)}"
        assert len(mid_ring) == 16, f"{fol}: Expected 16 middle ring loci, got {len(mid_ring)}"
        assert len(inn_ring) == 10, f"{fol}: Expected 10 inner ring loci, got {len(inn_ring)}"
        assert len(cc_outer) == 1, f"{fol}: Expected 1 outer Cc ring, got {len(cc_outer)}"
        assert len(cc_middle) == 1, f"{fol}: Expected 1 middle Cc ring, got {len(cc_middle)}"
        assert len(cc_inner) == 1, f"{fol}: Expected 1 inner Cc ring, got {len(cc_inner)}"
        assert len(top_overflow) + len(mid_ring) + len(inn_ring) == 30, f"{fol}: Total degree loci != 30"

    # Specific labels
    f73r_top_words = [clean_word(l.split(">", 1)[1].split("<!")[0].strip()) or clean_word(re.sub(r"<!.*?>", "", l.split(">", 1)[1])) for l in f73r_lines[:4]]
    f73v_top_words = [clean_word(re.sub(r"<!.*?>", "", l.split(">", 1)[1])) for l in f73v_lines[:4]]
    assert f73r_top_words == ["otaly", "chockhy", "otedy", "yteeody"], f"f73r top words mismatch: {f73r_top_words}"
    assert f73v_top_words == ["okol", "oteody", "oteedy", "eeeody"], f"f73v top words mismatch: {f73v_top_words}"

    # Ecliptic Seasonal Drift
    zodiac_folios = [
        {"folio": "f70v2", "sign": "Pisces", "season": "Spring"},
        {"folio": "f70v1", "sign": "Aries I", "season": "Spring"},
        {"folio": "f71r", "sign": "Aries II", "season": "Spring"},
        {"folio": "f71v", "sign": "Taurus I", "season": "Spring"},
        {"folio": "f72r1", "sign": "Taurus II", "season": "Spring"},
        {"folio": "f72r2", "sign": "Gemini", "season": "Summer"},
        {"folio": "f72r3", "sign": "Cancer", "season": "Summer"},
        {"folio": "f72v3", "sign": "Leo", "season": "Summer"},
        {"folio": "f72v2", "sign": "Virgo", "season": "Autumn"},
        {"folio": "f72v1", "sign": "Libra", "season": "Autumn"},
        {"folio": "f73r", "sign": "Scorpio", "season": "Autumn"},
        {"folio": "f73v", "sign": "Sagittarius", "season": "Autumn"},
    ]
    words_by_season = defaultdict(list)
    words_by_folio = {}
    for item in zodiac_folios:
        fol = item["folio"]
        f_words = []
        for l in raw_lines:
            if l.startswith(f"<{fol}."):
                body = l.split(">", 1)[1]
                body_clean = re.sub(r"<!.*?>", "", body)
                toks = [clean_word(t) for t in re.split(r"[.,\s]+", body_clean) if clean_word(t)]
                f_words.extend(toks)
        words_by_folio[fol] = f_words
        words_by_season[item["season"]].extend(f_words)

    # Word counts per season
    sp_words = words_by_season["Spring"]
    su_words = words_by_season["Summer"]
    au_words = words_by_season["Autumn"]

    assert len(sp_words) == 512, f"Spring words: {len(sp_words)} != 512"
    assert len(su_words) == 395, f"Summer words: {len(su_words)} != 395 (Discrepancy note: compendium draft text cites 399)"
    assert len(au_words) == 407, f"Autumn words: {len(au_words)} != 407 (Discrepancy note: compendium draft text cites 413)"

    sp_ot = sum(1 for w in sp_words if w.startswith(("ot", "op")))
    sp_ok = sum(1 for w in sp_words if w.startswith(("ok", "of")))
    su_ot = sum(1 for w in su_words if w.startswith(("ot", "op")))
    su_ok = sum(1 for w in su_words if w.startswith(("ok", "of")))
    au_ot = sum(1 for w in au_words if w.startswith(("ot", "op")))
    au_ok = sum(1 for w in au_words if w.startswith(("ok", "of")))

    assert sp_ot == 154 and sp_ok == 67, f"Spring ot/ok: {sp_ot}, {sp_ok}"
    assert su_ot == 75 and su_ok == 75, f"Summer ot/ok: {su_ot}, {su_ok}"
    assert au_ot == 89 and au_ok == 60, f"Autumn ot/ok: {au_ot}, {au_ok}"

    # Percentages
    assert round(sp_ot / 512 * 100, 2) == 30.08
    assert round(sp_ok / 512 * 100, 2) == 13.09
    assert round(sp_ot / sp_ok, 3) == 2.299

    assert round(su_ot / 395 * 100, 2) == 18.99
    assert round(su_ok / 395 * 100, 2) == 18.99
    assert round(su_ot / su_ok, 3) == 1.000

    assert round(au_ot / 407 * 100, 2) == 21.87
    assert round(au_ok / 407 * 100, 2) == 14.74
    assert round(au_ot / au_ok, 3) == 1.483

    # Chi2
    obs = [[sp_ot, sp_ok], [su_ot, su_ok]]
    r_sums = [sp_ot + sp_ok, su_ot + su_ok]
    c_sums = [sp_ot + su_ot, sp_ok + su_ok]
    tot = sum(r_sums)
    chi2 = sum(((obs[r][c] - (r_sums[r] * c_sums[c]) / tot) ** 2) / ((r_sums[r] * c_sums[c]) / tot) for r in range(2) for c in range(2))
    assert abs(chi2 - 14.6530) < 1e-3, f"Chi2 mismatch: {chi2}"

    print(f"  PASS: Attack 201 layout (10+16+4=30° on f73r/f73v), seasonal prefix counts (Spring 2.30, Summer 1.00, Autumn 1.48), Chi2=14.653.\n")


def verify_attack202():
    print("=== 3. Adversarially Verifying Attack 202 (Discovery 219) ===")
    assert A202_JSON.exists(), "attack202 JSON missing"
    a202 = json.loads(A202_JSON.read_text(encoding="utf-8"))

    index_data = json.loads(INDEX_PATH.read_text(encoding="utf-8"))
    folio_meta = index_data.get("folios", {})

    raw_lines = ZL_PATH.read_text(encoding="utf-8", errors="ignore").splitlines()
    lc_words = []
    lf_words = []
    for raw in raw_lines:
        if not raw.startswith("<f"): continue
        m = re.match(r"^<(f[0-9]+[rv][0-9]*)\.([^,>]+),([^>]+)>\s*(.*)$", raw)
        if not m: continue
        fol, lnum, ltype, body = m.groups()
        sec = folio_meta.get(fol, {}).get("section_code", "?")
        toks = [clean_word(t) for t in re.split(r"[.,\s]+", body) if clean_word(t)]
        if not toks: continue
        if sec == "P" and ("@Lc" in ltype or "@Lf" in ltype):
            if "@Lc" in ltype:
                lc_words.extend(toks)
            else:
                lf_words.extend(toks)

    assert len(lc_words) == 37, f"Expected 37 @Lc words, got {len(lc_words)}"
    assert len(lf_words) == 208, f"Expected 208 @Lf words, got {len(lf_words)}"

    lc_lens = [len(w) for w in lc_words]
    lf_lens = [len(w) for w in lf_words]
    m_lc = sum(lc_lens) / len(lc_lens)
    m_lf = sum(lf_lens) / len(lf_lens)
    v_lc = sum((x - m_lc)**2 for x in lc_lens) / (len(lc_lens) - 1)
    v_lf = sum((x - m_lf)**2 for x in lf_lens) / (len(lf_lens) - 1)
    se = math.sqrt(v_lc / len(lc_lens) + v_lf / len(lf_lens))
    t_stat = (m_lc - m_lf) / se

    assert abs(m_lc - 7.108) < 1e-3, f"LC mean length mismatch: {m_lc}"
    assert abs(m_lf - 5.769) < 1e-3, f"LF mean length mismatch: {m_lf}"
    assert abs((m_lc - m_lf) - 1.339) < 1e-3, f"Diff mismatch: {m_lc - m_lf}"
    assert abs(t_stat - 4.356) < 1e-3, f"t-statistic mismatch: {t_stat}"

    # Long compounds >= 7
    lc_long = sum(1 for w in lc_words if len(w) >= 7)
    lf_long = sum(1 for w in lf_words if len(w) >= 7)
    assert lc_long == 24 and round(lc_long / 37 * 100, 2) == 64.86, f"LC long: {lc_long}"
    assert lf_long == 60 and round(lf_long / 208 * 100, 2) == 28.85, f"LF long: {lf_long}"

    # Formulation bridge
    fb = a202["formulation_bridge"]["groups"]
    assert fb["all_pharma"]["stem_matches_pct"] == 64.49, f"All pharma stem matches: {fb['all_pharma']['stem_matches_pct']}"
    assert fb["all_pharma"]["stem_in_recipe_openers_pct"] == 47.35, f"All pharma opener stem: {fb['all_pharma']['stem_in_recipe_openers_pct']}"
    assert fb["f99v"]["stem_matches_pct"] == 57.69, f"f99v stem matches: {fb['f99v']['stem_matches_pct']}"
    assert fb["f88v"]["stem_matches_pct"] == 64.29, f"f88v stem matches: {fb['f88v']['stem_matches_pct']}"

    print(f"  PASS: Attack 202 @Lc (37 words, mean 7.11) vs @Lf (208 words, mean 5.77), t=+4.356, formulation bridge 64.49% stem match.\n")


def verify_attack203():
    print("=== 4. Adversarially Verifying Attack 203 (Discovery 220) ===")
    assert A203_JSON.exists(), "attack203 JSON missing"
    a203 = json.loads(A203_JSON.read_text(encoding="utf-8"))

    raw_lines = ZL_PATH.read_text(encoding="utf-8", errors="ignore").splitlines()

    def parse_star(desc):
        d = desc.lower()
        points = None
        m = re.search(r"([0-9]+)\s*points?", d)
        if m: points = int(m.group(1))
        elif "7/8" in d: points = 7.5
        dotted = "dotted" in d
        dark = "dark" in d
        tail = "tail" in d
        return {"points": points, "dotted": dotted, "dark": dark, "tail": tail, "raw": desc}

    star_units = []
    pending_star = None
    current_unit = None

    for raw in raw_lines:
        if raw.startswith("#") and "star" in raw.lower() and "text only" not in raw.lower() and "labeled" not in raw.lower():
            pending_star = raw.strip("# \n\r")
            continue
        if not raw.startswith("<f"): continue
        m = re.match(r"^<(f[0-9]+[rv][0-9]*)\.([^,>]+),([^>]+)>\s*(.*)$", raw)
        if not m: continue
        fol, lnum, ltype, body = m.groups()
        fnum_m = re.match(r"f([0-9]+)", fol)
        fnum = int(fnum_m.group(1)) if fnum_m else 0
        if not (103 <= fnum <= 116): continue
        tokens = [clean_word(t) for t in re.split(r"[.,\s]+", body) if clean_word(t)]
        if not tokens: continue
        if pending_star is not None:
            if current_unit: star_units.append(current_unit)
            current_unit = {"folio": fol, "locus": f"{fol}.{lnum}", "star_meta": parse_star(pending_star), "tokens": list(tokens)}
            pending_star = None
        elif current_unit:
            current_unit["tokens"].extend(tokens)

    if current_unit: star_units.append(current_unit)

    assert len(star_units) == 322, f"Expected 322 star units, got {len(star_units)}"

    # Point counts
    pts_counts = Counter(u["star_meta"]["points"] for u in star_units)
    assert pts_counts[7] == 182, f"Expected 182 7-pt stars, got {pts_counts[7]}"
    assert pts_counts[8] == 123, f"Expected 123 8-pt stars, got {pts_counts[8]}"
    assert pts_counts[9] == 6, f"Expected 6 9-pt stars, got {pts_counts[9]}"

    # Openers
    for u in star_units:
        w0 = u["tokens"][0]
        if w0.startswith(("p", "f")): u["fam"] = "PF"
        elif w0.startswith(("t", "k")): u["fam"] = "TK"
        else: u["fam"] = "Other"

    u7_pf = sum(1 for u in star_units if u["star_meta"]["points"] == 7 and u["fam"] == "PF")
    u7_tk = sum(1 for u in star_units if u["star_meta"]["points"] == 7 and u["fam"] == "TK")
    u8_pf = sum(1 for u in star_units if u["star_meta"]["points"] == 8 and u["fam"] == "PF")
    u8_tk = sum(1 for u in star_units if u["star_meta"]["points"] == 8 and u["fam"] == "TK")

    assert u7_pf == 102 and u7_tk == 40, f"7pt openers: {u7_pf} PF, {u7_tk} TK"
    assert u8_pf == 50 and u8_tk == 41, f"8pt openers: {u8_pf} PF, {u8_tk} TK"

    or_val = (u7_pf * u8_tk) / (u7_tk * u8_pf)
    assert abs(or_val - 2.091) < 1e-3, f"Odds ratio mismatch: {or_val}"

    # Star Parity Alternation
    by_fol = defaultdict(list)
    for u in star_units: by_fol[u["folio"]].append(u)

    total_transitions = 0
    total_alternations = 0
    perfect_folios = 0
    for fol, u_list in sorted(by_fol.items()):
        seq = ["D" if u["star_meta"]["dotted"] else "P" for u in u_list]
        n_trans = len(seq) - 1
        alts = sum(1 for i in range(n_trans) if seq[i] != seq[i+1])
        total_transitions += n_trans
        total_alternations += alts
        if alts == n_trans:
            perfect_folios += 1

    assert total_transitions == 299, f"Total transitions: {total_transitions}"
    assert total_alternations == 255, f"Total alternations: {total_alternations}"
    assert round(total_alternations / total_transitions * 100, 2) == 85.28
    assert perfect_folios == 17, f"Perfect folios: {perfect_folios} != 17"
    assert len(by_fol) == 23, f"Total folios: {len(by_fol)} != 23"
    assert round(perfect_folios / len(by_fol) * 100, 2) == 73.91

    # Binomial test
    exp = total_transitions * 0.5
    sd_null = math.sqrt(total_transitions * 0.25)
    z_score = (total_alternations - exp) / sd_null
    assert abs(z_score - 12.2024) < 1e-3, f"z-score mismatch: {z_score}"

    print(f"  PASS: Attack 203 star points (182 7pt vs 123 8pt, OR=2.091), parity alternation (255/299 = 85.28%, 17/23 folios 100%, z=+12.20).\n")


def verify_compendium_consistency_and_discrepancies():
    print("=== 5. Cross-Compendium Numerical Consistency & Discrepancy Auditing ===")
    assert MD_PATH.exists(), "Master compendium markdown missing"
    md_text = MD_PATH.read_text(encoding="utf-8")
    a201 = json.loads(A201_JSON.read_text(encoding="utf-8"))
    a202 = json.loads(A202_JSON.read_text(encoding="utf-8"))
    a203 = json.loads(A203_JSON.read_text(encoding="utf-8"))
    a204 = json.loads(A204_JSON.read_text(encoding="utf-8"))

    discrepancies = []

    # Discrepancy 1: Summer word count mismatch (399 vs 395)
    # Check Section 1 text and Section 4 text
    if "399 words" in md_text:
        discrepancies.append({
            "id": "DISC-01",
            "severity": "MEDIUM",
            "field": "Summer word count in WAVE48_MASTER_COMPENDIUM.md (lines 19, 178)",
            "compendium_text": "399 words",
            "actual_data": "395 words",
            "context": "Table 2 lists f72r2 (113), f72r3 (164), f72v3 (118), which sum to 395 words. The percentage 75 / 395 = 18.99% is derived from 395. The text '399 words' is an internal contradiction with Table 2 and attack201 JSON.",
        })

    # Discrepancy 2: Autumn word count mismatch (413 vs 407)
    if "413 words" in md_text:
        discrepancies.append({
            "id": "DISC-02",
            "severity": "MEDIUM",
            "field": "Autumn word count in WAVE48_MASTER_COMPENDIUM.md (lines 20, 179)",
            "compendium_text": "413 words",
            "actual_data": "407 words",
            "context": "Table 2 lists f72v2 (108), f72v1 (104), f73r (96), f73v (99), which sum to 407 words. The percentages 89 / 407 = 21.87% and 60 / 407 = 14.74% are derived from 407. The text '413 words' is an internal contradiction with Table 2 and attack201 JSON.",
        })

    # Discrepancy 3: attack203 summary string literal says "16/23 folios" instead of 17
    summary_law = a203["summary"]["key_findings"]["star_parity_alternation"]["law"]
    if "16/23 folios" in summary_law:
        discrepancies.append({
            "id": "DISC-03",
            "severity": "LOW",
            "field": "attack203 JSON summary law string literal (tools/attack203 line 345)",
            "compendium_text": "16/23 folios",
            "actual_data": "17/23 folios (73.91%)",
            "context": "attack203 summary string says '100% on 16/23 folios', while the calculated field in the same JSON is 17 (73.91%), and the compendium correctly says '17 / 23 (73.91%)'.",
        })

    # Discrepancy 4: Parenthetical t = +5.516 in docstring/text
    # Documented as unweighted census reference, but check if verified
    print(f"Total Discrepancies Found: {len(discrepancies)}")
    for d in discrepancies:
        print(f"  [{d['severity']}] {d['id']}: {d['field']}")
        print(f"         Claimed: {d['compendium_text']} | Actual: {d['actual_data']}")
        print(f"         Detail:  {d['context']}")

    # Check relative links
    links = re.findall(r"\[.*?\]\((.*?)\)", md_text)
    broken = []
    for l in links:
        if l.startswith("#") or l.startswith("http"): continue
        target = (MD_PATH.parent / l).resolve()
        if not target.exists():
            broken.append((l, str(target)))
    assert len(broken) == 0, f"Broken markdown links in compendium: {broken}"
    print(f"All {len(links)} markdown links in {MD_PATH.name} resolve successfully.\n")

    # Check images
    image_paths = [
        "pages/f73v_sagittarius_medallion_enh.png",
        "pages/f99v_three_row_jars_and_roots_enh.png",
        "pages/f88v_three_register_pharma_enh.png",
        "pages/f48v_gentian_bifurcated_twin_enh.png",
        "pages/f105r_dotted_star_dyads_enh.png",
        "pages/f116r_penultimate_recipes_enh.png",
    ]
    for ip in image_paths:
        p = ROOT / ip
        assert p.exists() and p.stat().st_size > 50000, f"Image {ip} missing or suspiciously small ({p.stat().st_size if p.exists() else 0} B)"
        print(f"  PASS: Image {ip} ({p.stat().st_size:,} bytes)")
    print()

    return discrepancies


def main():
    verify_scripts_execution()
    verify_attack201()
    verify_attack202()
    verify_attack203()
    discrepancies = verify_compendium_consistency_and_discrepancies()

    if discrepancies:
        print("=== VERIFICATION SUMMARY ===")
        print(f"Found {len(discrepancies)} internal numerical discrepancies requiring remediation.")
        return 1
    else:
        print("=== ALL VERIFICATION CHECKS PASSED WITH 0 DISCREPANCIES ===")
        return 0


if __name__ == "__main__":
    exit(main())
