"""Analyze (1) 9-Rosettes (<fRos>) to reverse-side text panels (f85r1-f86v6) matching,
(2) Biological section (f75r-f84v) label-to-paragraph & bifolium structure, and
(3) Marginal key sequences on f66r, f58r-f58v, f49v, and f76r.
"""
import json
import random
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ZL_FILE = ROOT / "data" / "ZL3b-n.txt"
OUT_FILE = ROOT / "data" / "bio_rosettes_and_keys.json"


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

    global_canon_freq = Counter()
    canon_to_locs = defaultdict(list)
    for f, fd in folios.items():
        sec = fd["meta"].get("I", "?")
        for l in fd["lines"]:
            n = len(l["words"])
            for idx, w in enumerate(l["words"]):
                c = canonical_word(w, idx == n - 1)
                global_canon_freq[c] += 1
                canon_to_locs[c].append((f, sec, l["loc"], l["ltype"], w))

    # 1. Test whether <fRos> (9-Rosettes map, Quire N) shares rare stems with the reverse panels of Quire N
    # (f85r1, f85r2, f86v3, f86v4, f86v5, f86v6)
    quire_n_panels = ["f85r1", "f85r2", "f86v3", "f86v4", "f86v5", "f86v6"]
    fros_canons = {
        canonical_word(w, True)
        for l in folios["fRos"]["lines"]
        for w in l["words"] if len(w) >= 4
    }
    fros_label_canons = {
        canonical_word(w, True)
        for l in folios["fRos"]["lines"] if "L" in l["ltype"]
        for w in l["words"] if len(w) >= 4
    }

    quire_n_matches = []
    obs_qn_rare_25 = 0
    for qf in quire_n_panels:
        if qf not in folios:
            continue
        q_canons = {
            canonical_word(w, True)
            for l in folios[qf]["lines"]
            for w in l["words"] if len(w) >= 4
        }
        shared = fros_canons & q_canons
        rare_shared = [
            {
                "canon": c,
                "global_count": global_canon_freq[c],
                "is_fros_label": c in fros_label_canons,
                "fros_words": [w for f, _, loc, lt, w in canon_to_locs[c] if f == "fRos"],
                "panel_words": [(loc, w) for f, _, loc, lt, w in canon_to_locs[c] if f == qf],
            }
            for c in shared if global_canon_freq[c] <= 25
        ]
        obs_qn_rare_25 += len(rare_shared)
        rare_shared.sort(key=lambda x: x["global_count"])
        quire_n_matches.append({
            "panel": qf,
            "total_shared": len(shared),
            "rare_shared_le_25": rare_shared,
        })

    # Permutation test against random Currier-B folios
    currier_b_folios = [
        f for f, fd in folios.items()
        if fd["meta"].get("L") == "B" and f not in quire_n_panels and f != "fRos"
    ]
    b_canon_sets = {
        f: {canonical_word(w, True) for l in folios[f]["lines"] for w in l["words"] if len(w) >= 4}
        for f in currier_b_folios
    }
    rng = random.Random(42)
    null_qn_rare = []
    for _ in range(2000):
        sample_b = rng.sample(currier_b_folios, len(quire_n_panels))
        cnt = 0
        for bf in sample_b:
            sh = fros_canons & b_canon_sets[bf]
            cnt += sum(1 for c in sh if global_canon_freq[c] <= 25)
        null_qn_rare.append(cnt)
    mean_qn = sum(null_qn_rare) / len(null_qn_rare)
    std_qn = (sum((x - mean_qn) ** 2 for x in null_qn_rare) / len(null_qn_rare)) ** 0.5

    # 2. Detailed analysis of all 20 Biological folios (f75r..f84v, Quire M)
    bio_folios = sorted([f for f, fd in folios.items() if fd["meta"].get("I") == "B"])
    bio_details = []
    for bf in bio_folios:
        fd = folios[bf]
        labels = []
        par_canons = set()
        par_word_locs = defaultdict(list)
        for l in fd["lines"]:
            n = len(l["words"])
            if "L" in l["ltype"]:
                for w in l["words"]:
                    c = canonical_word(w, True)
                    labels.append({
                        "loc": l["loc"],
                        "ltype": l["ltype"],
                        "word": w,
                        "canon": c,
                        "global_count": global_canon_freq[c],
                    })
            elif "P" in l["ltype"]:
                for idx, w in enumerate(l["words"]):
                    c = canonical_word(w, idx == n - 1)
                    par_canons.add(c)
                    par_word_locs[c].append((l["loc"], w, round(idx / max(1, n - 1), 2)))

        same_page_hits = []
        other_bio_hits = []
        for lb in labels:
            c = lb["canon"]
            if len(c) < 3:
                continue
            if c in par_canons:
                same_page_hits.append({
                    "label_loc": lb["loc"],
                    "label_type": lb["ltype"],
                    "label_word": lb["word"],
                    "canon": c,
                    "global_count": lb["global_count"],
                    "par_matches": par_word_locs[c],
                })
            # Check if rare (count <= 5) and occurs on another Bio folio
            if 2 <= lb["global_count"] <= 5:
                other_b = [
                    (f, loc, lt, w) for f, sec, loc, lt, w in canon_to_locs[c]
                    if f != bf and sec == "B"
                ]
                if other_b:
                    other_bio_hits.append({
                        "label_loc": lb["loc"],
                        "label_word": lb["word"],
                        "global_count": lb["global_count"],
                        "other_bio_locs": other_b,
                    })

        bio_details.append({
            "folio": bf,
            "total_labels": len(labels),
            "same_page_label_hits": same_page_hits,
            "rare_cross_bio_hits": other_bio_hits,
        })

    # 3. Inspect marginal key columns across the manuscript:
    # f49v, f66r, f76r, f1r, f58r-f58v
    marginal_keys = {}
    for mf in ["f1r", "f49v", "f58r", "f58v", "f66r", "f66v", "f76r"]:
        if mf not in folios:
            continue
        m_lines = []
        for l in folios[mf]["lines"]:
            if not l["ltype"].startswith(("@P", "+P")):
                m_lines.append({
                    "loc": l["loc"],
                    "ltype": l["ltype"],
                    "words": l["words"],
                })
        # Also get paragraph opening words on this folio
        par_openers = []
        for idx, l in enumerate(folios[mf]["lines"]):
            if "<%>" in l["raw_body"] or l["ltype"].startswith("@P"):
                if l["words"]:
                    par_openers.append((l["loc"], l["words"][0], l["words"][-1]))
        marginal_keys[mf] = {
            "non_prose_loci": m_lines,
            "paragraph_openers_and_closers": par_openers,
        }

    out = {
        "quire_n_rosettes_to_reverse_panels": {
            "observed_rare_25": obs_qn_rare_25,
            "null_mean": round(mean_qn, 2),
            "null_std": round(std_qn, 2),
            "z_score": round((obs_qn_rare_25 - mean_qn) / (std_qn or 1.0), 2),
            "panel_matches": quire_n_matches,
        },
        "bio_section_analysis": bio_details,
        "marginal_key_folios": marginal_keys,
    }
    OUT_FILE.write_text(json.dumps(out, indent=2), encoding="utf-8")

    print("=== 1. QUIRE N (<fRos> <-> Reverse Panels f85r1..f86v6) ===")
    print(f"  Observed rare<=25 matches: {obs_qn_rare_25} vs Null {mean_qn:.2f} +/- {std_qn:.2f} (z={(obs_qn_rare_25 - mean_qn)/(std_qn or 1):.2f})")
    for pm in quire_n_matches:
        if pm["rare_shared_le_25"]:
            print(f"  {pm['panel']} (total shared={pm['total_shared']}): {pm['rare_shared_le_25'][:6]}")

    print("\n=== 2. BIOLOGICAL SECTION (f75r..f84v) RARE SAME-PAGE & CROSS-BIO HITS ===")
    for bd in bio_details:
        rare_sp = [h for h in bd["same_page_label_hits"] if h["global_count"] <= 20]
        if rare_sp or bd["rare_cross_bio_hits"]:
            print(f"  {bd['folio']} (labels={bd['total_labels']}): same_page_rare={rare_sp} | cross_bio={bd['rare_cross_bio_hits']}")

    print("\n=== 3. MARGINAL KEY FOLIOS (f49v, f66r, f76r, f58r/v) ===")
    for mf, md in marginal_keys.items():
        print(f"  {mf}: non_prose={md['non_prose_loci']}")
        print(f"       par_openers={md['paragraph_openers_and_closers'][:8]}")


if __name__ == "__main__":
    main()
