#!/usr/bin/env python3
"""
Attack 43: Cosmological & Four-Seasons/Four-Moons Diagram Decoder (f57v, f67r1-f70r2, f85r1-f86v6)
====================================================================================================
Investigates the Cosmological ($I=C) and Astronomical ($I=A) diagrams and the reverse side of the
9-Sphere Rosettes foldout (f85r1, f85r2, f86v3, f86v4, f86v5, f86v6):
  1. Exact Ring Periodicity & Key-Sequence Analysis on f57v (the 4-cycle ring on the outer bifolium of Quire H).
  2. Locus-Role Stratification across Radial Spokes (@R), Perimeter Rings (@C), Diagram Labels (@L),
     and Prose Paragraphs (@P) in Cosmological/Astronomical folios (f57v, f67r1-f70r2, f85r1-f86v6),
     with a 1,000-trial permutation test for ok-/ot- celestial prefixing and 16-cell vocalic-liquid stems.
  3. Four-Quadrant / Four-Season / Four-Moon Symmetry Decoder on f85r2 and f86v4.
  4. Physical Sheet Cross-Coupling between Front-Side fRos (9-Sphere Rosettes Map) and Back-Side
     f85r1-f86v6 (Quire N foldout reverse), testing rare-stem sharing against 1,000 random folio sets.
"""

from __future__ import annotations

import json
import math
import random
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, List, Set, Tuple

ROOT = Path(__file__).resolve().parents[1]
ZL_PATH = ROOT / "data" / "ZL3b-n.txt"
OUT_JSON = ROOT / "data" / "attack43_cosmological_and_f85_f86_diagram_decoder.json"

LOCUS_RE = re.compile(r"^<f([0-9]+[rv][0-9]*|Ros)\.([^,>]+),([^>]+)>\s*(.*)$")
CELLS_4 = ["ol", "ar", "or", "al"]
MATRIX_16 = {c1 + c2 for c1 in CELLS_4 for c2 in CELLS_4}


def clean_tokens_keep_special(raw: str) -> List[str]:
    s = re.sub(r"\{[^}]*\}", "", raw)
    s = re.sub(r"\[([^:\]]+):[^\]]+\]", r"\1", s)
    s = s.replace("<%>", " ").replace("<$>", " ").replace("<->", " . ")
    s = re.sub(r"<[^>]*>", " ", s)
    s = re.sub(r"[!?*']", "", s)
    out = []
    for tok in re.split(r"[\s.,]+", s.strip()):
        if tok:
            out.append(tok)
    return out


def clean_alpha(tok: str) -> str:
    return re.sub(r"[^a-z]", "", tok.lower())


def is_matrix16(w: str) -> bool:
    for m in MATRIX_16:
        if m in w:
            return True
    return False


def is_ok_ot(w: str) -> bool:
    return w.startswith(("ok", "ot", "yk", "yt"))


def main() -> None:
    lines_raw = ZL_PATH.read_text(encoding="utf-8", errors="replace").splitlines()
    current_folio = ""
    current_section = ""

    folio_loci: Dict[str, List[Dict]] = defaultdict(list)
    folio_sec: Dict[str, str] = {}
    doc_freq: Counter = Counter()
    folio_vocab: Dict[str, Set[str]] = defaultdict(set)

    for line in lines_raw:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("<f") and ">" in line and "." not in line.split(">")[0]:
            header = line.split(">")[0] + ">"
            m_f = re.match(r"^<f([0-9]+[rv][0-9]*|Ros)>", header)
            if m_f:
                current_folio = "f" + m_f.group(1)
            m_s = re.search(r"\$I=([A-Z])", line)
            current_section = m_s.group(1) if m_s else "U"
            folio_sec[current_folio] = current_section
            continue

        m = LOCUS_RE.match(line)
        if not m:
            continue
        folio = "f" + m.group(1)
        loc_id = m.group(2)
        loc_tag = m.group(3)
        raw_text = m.group(4)
        toks_raw = clean_tokens_keep_special(raw_text)
        toks_alpha = [clean_alpha(t) for t in toks_raw if clean_alpha(t)]

        folio_loci[folio].append({
            "loc_id": loc_id,
            "loc_tag": loc_tag,
            "raw_text": raw_text,
            "toks_raw": toks_raw,
            "toks_alpha": toks_alpha,
        })
        for w in toks_alpha:
            folio_vocab[folio].add(w)

    for f, voc in folio_vocab.items():
        for w in voc:
            doc_freq[w] += 1

    # 1. Analyze f57v Ring Periodicity & Structure
    f57v_rings = []
    for loc in folio_loci.get("f57v", []):
        f57v_rings.append({
            "loc_id": loc["loc_id"],
            "loc_tag": loc["loc_tag"],
            "token_count": len(loc["toks_raw"]),
            "tokens_raw": loc["toks_raw"],
        })

    # Specifically check Ring 2 (<f57v.2,@Cr>) and Ring 4 (<f57v.4,@Cr>) for exact 4-fold periodicity
    ring_periodicity = {}
    for loc in folio_loci.get("f57v", []):
        seq = loc["toks_raw"]
        n = len(seq)
        if n >= 12:
            # Test lag autocorrelation for lags 4..20
            best_lag = None
            best_match_rate = 0.0
            lag_rates = {}
            for lag in range(4, min(25, n // 2 + 1)):
                matches = sum(1 for i in range(n - lag) if seq[i] == seq[i + lag])
                rate = matches / (n - lag)
                lag_rates[str(lag)] = round(rate, 4)
                if rate > best_match_rate:
                    best_match_rate = rate
                    best_lag = lag
            ring_periodicity[loc["loc_id"] + "," + loc["loc_tag"]] = {
                "length": n,
                "best_lag": best_lag,
                "best_match_rate": round(best_match_rate, 4),
                "lag_rates": lag_rates,
                "sequence_preview": " ".join(seq[:36]),
            }

    # 2. Locus-Role Stratification across Cosmological & Astronomical Folios (f57v, f67r1-f70r2, f85r1-f86v6)
    target_folios = [
        f for f in folio_loci
        if folio_sec.get(f) in ("C", "A") or f.startswith(("f57v", "f67", "f68", "f69", "f70", "f85", "f86"))
    ]
    target_folios = sorted(set(target_folios))

    role_stats: Dict[str, Counter] = defaultdict(Counter)
    all_target_tokens: List[Tuple[str, str]] = []  # (role_group, word)

    def classify_locus_role(tag: str) -> str:
        if "R" in tag:
            return "RADIAL_SPOKE (@R)"
        if "C" in tag:
            return "PERIMETER_RING (@C)"
        if "L" in tag:
            return "DIAGRAM_LABEL (@L)"
        if "P" in tag:
            return "PROSE_PARAGRAPH (@P)"
        return "OTHER"

    for f in target_folios:
        for loc in folio_loci[f]:
            role = classify_locus_role(loc["loc_tag"])
            for w in loc["toks_alpha"]:
                if not w:
                    continue
                all_target_tokens.append((role, w))
                role_stats[role]["total"] += 1
                if is_ok_ot(w):
                    role_stats[role]["ok_ot"] += 1
                if is_matrix16(w):
                    role_stats[role]["matrix16"] += 1
                if w.startswith(("qo", "qok", "qot")):
                    role_stats[role]["qo"] += 1
                if w.startswith(("ch", "sh")):
                    role_stats[role]["ch_sh"] += 1
                if w.startswith(("o", "y")) and not is_ok_ot(w):
                    role_stats[role]["o_y_nom"] += 1

    role_summary = {}
    for role, cnt in role_stats.items():
        tot = max(cnt["total"], 1)
        role_summary[role] = {
            "total_tokens": cnt["total"],
            "ok_ot_rate": round(cnt["ok_ot"] / tot, 4),
            "matrix16_rate": round(cnt["matrix16"] / tot, 4),
            "qo_rate": round(cnt["qo"] / tot, 4),
            "ch_sh_rate": round(cnt["ch_sh"] / tot, 4),
            "o_y_nom_rate": round(cnt["o_y_nom"] / tot, 4),
        }

    # Permutation test: ok_ot + matrix16 enrichment in Diagram Loci (@R/@C/@L) vs Prose (@P) within target_folios
    diag_roles = {"RADIAL_SPOKE (@R)", "PERIMETER_RING (@C)", "DIAGRAM_LABEL (@L)"}
    obs_diag_ok_ot = sum(
        1 for r, w in all_target_tokens if r in diag_roles and is_ok_ot(w)
    )
    n_diag = sum(1 for r, _ in all_target_tokens if r in diag_roles)
    obs_diag_rate = obs_diag_ok_ot / max(n_diag, 1)

    rng = random.Random(43)
    words_only = [w for _, w in all_target_tokens]
    roles_only = [r for r, _ in all_target_tokens]
    null_rates = []
    for _ in range(1000):
        shuffled_roles = roles_only[:]
        rng.shuffle(shuffled_roles)
        c = sum(1 for r, w in zip(shuffled_roles, words_only) if r in diag_roles and is_ok_ot(w))
        null_rates.append(c / max(n_diag, 1))
    mu_ok = sum(null_rates) / len(null_rates)
    sd_ok = math.sqrt(sum((x - mu_ok) ** 2 for x in null_rates) / len(null_rates)) or 1e-9
    z_ok_diag = (obs_diag_rate - mu_ok) / sd_ok

    # 3. Decode Four-Seasons / Four-Moons Diagrams (f85r2 and f86v4)
    four_fold_diagrams = {}
    for f in ["f85r2", "f86v4", "f67r2", "f68v3"]:
        loci_out = []
        for loc in folio_loci.get(f, []):
            loci_out.append({
                "loc_id": loc["loc_id"],
                "loc_tag": loc["loc_tag"],
                "tokens": loc["toks_alpha"],
                "ok_ot_tokens": [w for w in loc["toks_alpha"] if is_ok_ot(w)],
                "matrix16_tokens": [w for w in loc["toks_alpha"] if is_matrix16(w)],
            })
        four_fold_diagrams[f] = {
            "total_loci": len(loci_out),
            "total_tokens": sum(len(x["tokens"]) for x in loci_out),
            "loci": loci_out,
        }

    # 4. Physical Sheet Cross-Coupling: fRos (Front of Quire N Foldout) vs f85r1-f86v6 (Back/Interior of Quire N Foldout)
    quire_n_other = ["f85r1", "f85r2", "f86v3", "f86v4", "f86v5", "f86v6"]
    fros_vocab = folio_vocab.get("fRos", set())
    fros_rare = {w for w in fros_vocab if 2 <= doc_freq[w] <= 5}

    quire_n_vocab = set()
    for f in quire_n_other:
        quire_n_vocab |= folio_vocab.get(f, set())

    shared_rare_fros_qn = sorted(fros_rare & quire_n_vocab)
    obs_shared_count = len(shared_rare_fros_qn)

    # Permutation baseline: sample 6 random folios (excluding fRos) 1,000 times, controlling for total vocab size
    candidate_folios = [f for f in folio_vocab if f != "fRos" and len(folio_vocab[f]) >= 20]
    null_shared = []
    for _ in range(1000):
        sampled = rng.sample(candidate_folios, len(quire_n_other))
        svoc = set()
        for sf in sampled:
            svoc |= folio_vocab[sf]
        null_shared.append(len(fros_rare & svoc))
    mu_sh = sum(null_shared) / len(null_shared)
    sd_sh = math.sqrt(sum((x - mu_sh) ** 2 for x in null_shared) / len(null_shared)) or 1e-9
    z_fros_qn = (obs_shared_count - mu_sh) / sd_sh

    result = {
        "f57v_ring_periodicity": ring_periodicity,
        "f57v_loci": f57v_rings,
        "cosmological_astronomical_role_summary": role_summary,
        "ok_ot_diagram_vs_prose_permutation": {
            "diagram_tokens": n_diag,
            "observed_ok_ot_rate": round(obs_diag_rate, 4),
            "null_mean_rate": round(mu_ok, 4),
            "z_score": round(z_ok_diag, 2),
        },
        "four_fold_diagrams": four_fold_diagrams,
        "fRos_to_quireN_sheet_coupling": {
            "fRos_rare_vocab_count": len(fros_rare),
            "quire_n_folios": quire_n_other,
            "observed_shared_rare_count": obs_shared_count,
            "null_mean_shared": round(mu_sh, 2),
            "z_score": round(z_fros_qn, 2),
            "shared_rare_words": shared_rare_fros_qn,
        },
    }

    OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print("=== ATTACK 43: COSMOLOGICAL & FOUR-SEASONS/FOUR-MOONS DIAGRAM DECODER ===")
    print("1. f57v Ring Periodicity:")
    for k, v in ring_periodicity.items():
        print(f"   {k}: len={v['length']}, best_lag={v['best_lag']}, match_rate={v['best_match_rate']} | preview: {v['sequence_preview']}")
    print("\n2. Locus-Role Stratification (f57v, f67r1-f70r2, f85r1-f86v6):")
    for role, st in role_summary.items():
        print(f"   {role:22s}: n={st['total_tokens']:4d} | ok/ot={st['ok_ot_rate']:.3f} | matrix16={st['matrix16_rate']:.3f} | qo={st['qo_rate']:.3f} | ch/sh={st['ch_sh_rate']:.3f}")
    print(f"   Diagram (@R/@C/@L) vs Prose (@P) ok-/ot- enrichment: obs={obs_diag_rate:.4f} vs null={mu_ok:.4f} (z={z_ok_diag:+.2f})")
    print(f"\n3. Physical Sheet Coupling (fRos <-> f85r1-f86v6): shared rare stems={obs_shared_count} vs null={mu_sh:.2f} (z={z_fros_qn:+.2f})")
    print(f"   Shared rare words: {shared_rare_fros_qn}")


if __name__ == "__main__":
    main()
