"""Analyze f57v 4-fold ring sequence, Astronomical/Cosmological wheels (f67r1-f70r2), and Herbal A/B structure."""
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ZL_FILE = ROOT / "data" / "ZL3b-n.txt"
OUT_FILE = ROOT / "data" / "astro_and_herbal_analysis.json"


def clean_word(w: str) -> str:
    w = re.sub(r"\[([^:\]]+):[^\]]+\]", r"\1", w)
    w = re.sub(r"\{[^}]*\}", "", w)
    w = re.sub(r"<[^>]*>", "", w)
    w = w.replace("?", "").replace("!", "").replace("*", "").replace("%", "")
    w = w.replace("'", "").replace('"', "").replace("(", "").replace(")", "")
    return w.strip()


def canonical_word(w: str, is_line_end: bool = False) -> str:
    if len(w) <= 1:
        return w
    s = w
    if s.startswith("qo") and len(s) > 2:
        s = s[1:]
    elif s.startswith("y") and len(s) > 2 and s[1] in "otkpfchsd":
        s = s[1:]
    s = s.replace("p", "t").replace("f", "k")
    s = re.sub(r"e+", "e", s)
    s = re.sub(r"i+", "i", s)
    s = re.sub(r"o+", "o", s)
    s = re.sub(r"a+", "a", s)
    if (is_line_end or len(s) >= 3) and s.endswith("m") and len(s) >= 3 and s[-2] in "aoei":
        s = s[:-1] + "r"
    return s


def parse_zl():
    text = ZL_FILE.read_text(encoding="utf-8", errors="ignore")
    folio_re = re.compile(r"^<(f[\w]+)>")
    loc_re = re.compile(r"^<(f[\w]+)\.([^,>]+),([^>]+)>\s*(.*)$")

    folios = {}
    cur = None

    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        fm = folio_re.match(line)
        if fm and "." not in line.split(">")[0]:
            cur = fm.group(1)
            meta = dict(re.findall(r"\$([A-Z])=([A-Za-z0-9]+)", line))
            folios[cur] = {"folio": cur, "meta": meta, "lines": []}
            continue
        lm = loc_re.match(line)
        if lm and cur:
            f_id, loc_id, ltype, body = lm.groups()
            body_clean = re.sub(r"<![^>]*>", "", body)
            raw_tokens = [t for t in re.split(r"[.,\s]+", body_clean) if t and t != "-"]
            words = [clean_word(t) for t in raw_tokens]
            words = [w for w in words if w and re.search(r"[a-z]", w)]
            folios[cur]["lines"].append({
                "loc": f"{f_id}.{loc_id}",
                "ltype": ltype,
                "raw_body": body_clean.strip(),
                "words": words,
            })
    return folios


def main():
    folios = parse_zl()

    # Global canonical frequency
    global_canon_freq = Counter()
    canon_to_occurrences = defaultdict(list)
    for f, fdata in folios.items():
        sec = fdata["meta"].get("I", "?")
        for l in fdata["lines"]:
            n = len(l["words"])
            for idx, w in enumerate(l["words"]):
                c = canonical_word(w, is_line_end=(idx == n - 1))
                global_canon_freq[c] += 1
                canon_to_occurrences[c].append({
                    "folio": f,
                    "sec": sec,
                    "loc": l["loc"],
                    "ltype": l["ltype"],
                    "word": w,
                })

    # 1. Inspect f57v (the 4-fold repeating sequence wheel at end of Herbal/Cosmo)
    f57v_data = folios.get("f57v", {})
    f57v_lines = []
    for l in f57v_data.get("lines", []):
        f57v_lines.append({
            "loc": l["loc"],
            "ltype": l["ltype"],
            "words": l["words"],
            "joined": ".".join(l["words"]),
        })

    # Let's check the 4-fold repetition in f57v rings
    # Specifically look at lines with single characters or repeating sequences
    f57v_rings = {}
    for l in f57v_lines:
        seq = l["words"]
        # Check if seq consists of 4 nearly identical quarters
        n = len(seq)
        f57v_rings[l["loc"]] = {
            "ltype": l["ltype"],
            "len": n,
            "seq": " ".join(seq),
        }

    # 2. Analyze Astronomical / Cosmological folios (f67r1..f70r2, f85r2, f86v4)
    astro_folios = [
        f for f, fd in folios.items()
        if fd["meta"].get("I") in ("A", "C") and f not in ("f57v", "fRos")
    ]
    astro_summary = []
    astro_rare_links = []

    for f in sorted(astro_folios):
        fd = folios[f]
        all_words = [w for l in fd["lines"] for w in l["words"]]
        label_words = [w for l in fd["lines"] if "L" in l["ltype"] for w in l["words"]]
        prefixes = Counter()
        for w in label_words:
            if w.startswith(("ot", "op")):
                prefixes["ot/op"] += 1
            elif w.startswith(("ok", "of")):
                prefixes["ok/of"] += 1
            elif w.startswith(("ol", "or")):
                prefixes["ol/or"] += 1
            elif w.startswith("o"):
                prefixes["o_other"] += 1
            elif w.startswith("d"):
                prefixes["d-"] += 1
            elif w.startswith("s"):
                prefixes["s-"] += 1
            else:
                prefixes["other"] += 1

        astro_summary.append({
            "folio": f,
            "sec": fd["meta"].get("I"),
            "hand": fd["meta"].get("H"),
            "total_words": len(all_words),
            "label_count": len(label_words),
            "label_prefixes": dict(prefixes),
        })

        # Check rare labels on this astro folio (count 2..5) that appear in other sections
        for l in fd["lines"]:
            if "L" in l["ltype"]:
                for w in l["words"]:
                    if len(w) < 4:
                        continue
                    c = canonical_word(w, True)
                    cnt = global_canon_freq[c]
                    if 2 <= cnt <= 5:
                        others = [
                            o for o in canon_to_occurrences[c]
                            if o["folio"] != f
                        ]
                        if others:
                            astro_rare_links.append({
                                "astro_folio": f,
                                "loc": l["loc"],
                                "ltype": l["ltype"],
                                "word": w,
                                "canon": c,
                                "global_count": cnt,
                                "other_occurrences": others,
                            })

    # 3. Analyze Herbal -> Pharma visual twin pairs (from ZL comments)
    herbal_pharma_pairs = [
        ("f1v", "f102r1"),
        ("f2r", "f99v"),
        ("f5r", "f99v"),
        ("f9v", "f99r"),
        ("f16r", "f99v"),
        ("f17r", "f99r"),
        ("f19r", "f101v"),
        ("f21r", "f100r"),
        ("f22r", "f88r"),
        ("f22v", "f89v1"),
        ("f25r", "f99v"),
        ("f32v", "f99r"),
        ("f37v", "f102r1"),
        ("f38r", "f101v"),
        ("f45v", "f102r2"),
        ("f47v", "f99r"),
        ("f51v", "f100r"),
        ("f53v", "f102v2"),
        ("f56r", "f102v2"),
    ]
    herbal_pharma_pairs = [(hf, pf) for hf, pf in herbal_pharma_pairs if hf in folios and pf in folios]
    pair_shared_rare = []
    obs_rare_15_matches = 0
    obs_label_to_herbal_matches = 0

    for hf, pf in herbal_pharma_pairs:
        h_canons = {canonical_word(w, True) for l in folios[hf]["lines"] for w in l["words"] if len(w) >= 4}
        p_canons = {canonical_word(w, True) for l in folios[pf]["lines"] for w in l["words"] if len(w) >= 4}
        p_label_canons = {
            canonical_word(w, True)
            for l in folios[pf]["lines"] if "L" in l["ltype"]
            for w in l["words"] if len(w) >= 4
        }
        shared = h_canons & p_canons
        rare_shared = [
            {
                "canon": c,
                "global_count": global_canon_freq[c],
                "is_pharma_label": c in p_label_canons,
            }
            for c in shared if global_canon_freq[c] <= 25
        ]
        obs_rare_15_matches += sum(1 for c in shared if global_canon_freq[c] <= 15)
        obs_label_to_herbal_matches += sum(1 for c in (h_canons & p_label_canons) if global_canon_freq[c] <= 15)
        rare_shared.sort(key=lambda x: x["global_count"])
        pair_shared_rare.append({
            "herbal_folio": hf,
            "pharma_folio": pf,
            "herbal_first_word": folios[hf]["lines"][0]["words"][0] if folios[hf]["lines"] and folios[hf]["lines"][0]["words"] else "",
            "shared_count": len(shared),
            "rare_shared": rare_shared,
        })

    # Permutation test: randomly pair 19 Currier-A Herbal folios with the same Pharma folios (5000 trials)
    import random
    rng = random.Random(42)
    all_herbal_a = [
        f for f, fd in folios.items()
        if fd["meta"].get("I") == "H" and fd["meta"].get("L") == "A"
    ]
    herbal_canon_sets = {
        f: {canonical_word(w, True) for l in folios[f]["lines"] for w in l["words"] if len(w) >= 4}
        for f in all_herbal_a
    }
    pharma_canon_sets = {
        pf: {canonical_word(w, True) for l in folios[pf]["lines"] for w in l["words"] if len(w) >= 4}
        for _, pf in herbal_pharma_pairs
    }
    pharma_label_sets = {
        pf: {
            canonical_word(w, True)
            for l in folios[pf]["lines"] if "L" in l["ltype"]
            for w in l["words"] if len(w) >= 4
        }
        for _, pf in herbal_pharma_pairs
    }

    # Also test matching specifically to Paragraph-Opening Lines (<%>) on the paired Herbal folio
    herbal_par_start_sets = {
        f: {
            canonical_word(w, True)
            for idx_l, l in enumerate(folios[f]["lines"])
            if idx_l == 0 or l["ltype"].startswith("@P") or "<%>" in l["raw_body"]
            for w in l["words"] if len(w) >= 4
        }
        for f in all_herbal_a
    }
    obs_label_to_herbal_par_start = sum(
        1 for hf, pf in herbal_pharma_pairs
        for c in (herbal_par_start_sets.get(hf, set()) & pharma_label_sets[pf])
        if global_canon_freq[c] <= 15
    )

    null_rare_15 = []
    null_label_matches = []
    null_label_par_start = []
    for _ in range(5000):
        r15 = 0
        lm = 0
        lps = 0
        for _, pf in herbal_pharma_pairs:
            rh = rng.choice(all_herbal_a)
            sh = herbal_canon_sets[rh] & pharma_canon_sets[pf]
            r15 += sum(1 for c in sh if global_canon_freq[c] <= 15)
            sh_lbl = herbal_canon_sets[rh] & pharma_label_sets[pf]
            lm += sum(1 for c in sh_lbl if global_canon_freq[c] <= 15)
            sh_ps = herbal_par_start_sets[rh] & pharma_label_sets[pf]
            lps += sum(1 for c in sh_ps if global_canon_freq[c] <= 15)
        null_rare_15.append(r15)
        null_label_matches.append(lm)
        null_label_par_start.append(lps)

    mean_r15 = sum(null_rare_15) / len(null_rare_15)
    std_r15 = (sum((x - mean_r15) ** 2 for x in null_rare_15) / len(null_rare_15)) ** 0.5
    p_r15 = sum(1 for x in null_rare_15 if x >= obs_rare_15_matches) / len(null_rare_15)

    mean_lm = sum(null_label_matches) / len(null_label_matches)
    std_lm = (sum((x - mean_lm) ** 2 for x in null_label_matches) / len(null_label_matches)) ** 0.5
    p_lm = sum(1 for x in null_label_matches if x >= obs_label_to_herbal_matches) / len(null_label_matches)

    mean_lps = sum(null_label_par_start) / len(null_label_par_start)
    std_lps = (sum((x - mean_lps) ** 2 for x in null_label_par_start) / len(null_label_par_start)) ** 0.5
    p_lps = sum(1 for x in null_label_par_start if x >= obs_label_to_herbal_par_start) / len(null_label_par_start)

    perm_stats = {
        "rare_15_shared": {
            "observed": obs_rare_15_matches,
            "null_mean": round(mean_r15, 3),
            "null_std": round(std_r15, 3),
            "z_score": round((obs_rare_15_matches - mean_r15) / (std_r15 or 1.0), 2),
            "p_value": round(p_r15, 4),
        },
        "pharma_label_to_herbal_rare_15": {
            "observed": obs_label_to_herbal_matches,
            "null_mean": round(mean_lm, 3),
            "null_std": round(std_lm, 3),
            "z_score": round((obs_label_to_herbal_matches - mean_lm) / (std_lm or 1.0), 2),
            "p_value": round(p_lm, 4),
        },
        "pharma_label_to_herbal_par_start_rare_15": {
            "observed": obs_label_to_herbal_par_start,
            "null_mean": round(mean_lps, 3),
            "null_std": round(std_lps, 3),
            "z_score": round((obs_label_to_herbal_par_start - mean_lps) / (std_lps or 1.0), 2),
            "p_value": round(p_lps, 4),
        },
    }

    out = {
        "f57v_rings": f57v_rings,
        "astro_summary": astro_summary,
        "astro_rare_links": astro_rare_links[:40],
        "herbal_pharma_pairs": pair_shared_rare,
        "herbal_pharma_permutation_test": perm_stats,
    }
    OUT_FILE.write_text(json.dumps(out, indent=2), encoding="utf-8")

    print("=== f57v RINGS ===")
    for k, v in f57v_rings.items():
        print(f"  {k} ({v['ltype']}, n={v['len']}): {v['seq'][:100]}")

    print(f"\n=== ASTRO RARE LINKS (count 2..5): {len(astro_rare_links)} ===")
    for r in astro_rare_links[:20]:
        others_str = ", ".join(f"{o['loc']}({o['sec']}:{o['word']})" for o in r["other_occurrences"])
        print(f"  {r['loc']} ({r['ltype']}) '{r['word']}' (cnt={r['global_count']}) -> {others_str}")

    print("\n=== HERBAL <-> PHARMA VISUAL TWIN PAIRS RARE SHARED STEMS ===")
    for p in pair_shared_rare:
        if p["rare_shared"]:
            print(f"  {p['herbal_folio']} <-> {p['pharma_folio']} (first={p['herbal_first_word']}): {p['rare_shared']}")
    print("\n=== HERBAL <-> PHARMA PERMUTATION TEST (5,000 trials, Currier A stratified) ===")
    print(" ", perm_stats)


if __name__ == "__main__":
    main()
