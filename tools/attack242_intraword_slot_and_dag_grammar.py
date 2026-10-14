"""Attack 242: Intra-Word Slot Automaton, DAG Unidirectionality, Directionality
Asymmetry, and Currier A/B Stem-Shift Analysis.

Five empirical tests on clean running-text words (unit == 'P', excluding titles
unit_sub == 't' where specified, imported via tools/voynich_corpus.py):

  T1  Intra-Word Precedence DAG & Feedback Arc Set (FAS) Unidirectionality Test:
      - Three alphabets: (a) raw eva_chars, (b) collapsed multi-char EVA ligature
        units (cth, ckh, cph, cfh, ch, sh, iiin, iin, in, eee, ee), (c) Glen
        Claston v101 (data/GC2a-n.txt).
      - Both adjacent bigrams (u, v) with u != v and any-distance intra-word
        precedence pairs u < v with u != v.
      - Pairwise directionality index D(u,v) = |C(u<v) - C(v<u)| / (C(u<v) + C(v<u))
        and weighted mean directionality.
      - Optimal topological linear ordering minimizing Feedback Arc Set (FAS)
        violation weight fraction (via multi-start simulated annealing + exact
        insert/swap local search to fixed point).
      - Evaluated across: token-weighted (ALL, line_interior, lang_A, lang_B),
        type-weighted (ALL_types, lang_A_types, lang_B_types), within-word
        character-shuffle null, random alphabet-order null, and natural-language
        controls (Latin De Bello Gallico, English Culpeper Herbal).
      - Boundary-ambivalent glyph diagnosis and positional allograph splitting
        (splitting word-initial vs non-initial / word-final vs non-final for top
        ambivalent glyphs o, d, y, e, a, s, r, l).

  T2  Left-to-Right vs. Right-to-Left Positional Entropy Profile:
      - Fixed word lengths L in {4, 5, 6, 7} (in eva_chars and eva_units) and
        all-length start-aligned (+1..+6) vs end-aligned (-1..-6).
      - Unconditional slot entropy H(g_k), Markov-1 conditional entropy forward
        H(g_k | g_{k-1}) vs backward H(g_k | g_{k+1}), and full chain-rule
        conditional entropy H(g_k | g_1..g_{k-1}) vs H(g_k | g_{k+1}..g_L) with
        Miller-Madow bias correction and subsample parity.
      - Token-weighted and type-weighted comparisons against Latin and English.

  T3  Word-Length Binomiality & Variance Test:
      - Mean mu, variance sigma^2, Fano dispersion D = sigma^2 / mu, skewness,
        excess kurtosis across ALL, lang_A, lang_B, hands 1..5, line positions
        (line_start, line_mid, line_end, labels), and Latin/English controls.
      - Best-fit Binomial(n, p), Shifted Binomial 1 + Bin(n-1, p), and Poisson(lambda)
        goodness-of-fit (TVD and KL divergence).
      - 3-Slot Morphological Decomposition (Prefix + Core + Suffix): variance and
        covariance decomposition showing core root concentration at 1-2 units.

  T4  Currier Language A vs. Language B Cognate / Paradigm Shift Matrix:
      - Global Lang A vs Lang B and the within-Scribe 3 natural experiment:
        Scribe 3 writes Lang A on f58r-f58v ($H=3, $L=A, $I=S; 747 clean words)
        and Lang B in Quire 20 f103r-f116r ($H=3, $L=B, $I=S; 10,361 clean words)
        plus Herbal B f94r-f95v2 ($H=3, $L=B, $I=H; 532 clean words).
      - Subsample-controlled slot distributions (Prefix, Core/Gallows, Medial
        Vowel-Grade, Terminal Suffix), JSD matrix across (H1_A, H3_A_f58, H3_B_Q20,
        H3_B_Herb, H2_B_Herb, H2_B_Balneo), and explicit cognate stem-shift table.

  T5  Visual Plots & High-Res Scan Verification:
      - pages/w242_dag_matrix.png
      - pages/w242_entropy_and_length.png
      - pages/w242_f58r_scribe3_langA_crop.png
      - pages/w242_f103r_scribe3_langB_crop.png
      - pages/w242_scribe3_langA_vs_langB_vellum.png

Usage:  python tools/attack242_intraword_slot_and_dag_grammar.py
Output: data/attack242_intraword_slot_and_dag_grammar.json,
        notes/INTRA_WORD_SLOT_GRAMMAR.md,
        pages/w242_*.png
"""
from __future__ import annotations

import json
import math
import os
import random
import re
import statistics
import subprocess
import sys
import tempfile
import urllib.request
from collections import Counter, defaultdict
from typing import Dict, List, Optional, Sequence, Tuple

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from voynich_corpus import DATA, ROOT, load_lines, paragraphs  # noqa: E402

SEED = 242
EVA_UNITS_ORDER = (
    'cth', 'ckh', 'cph', 'cfh', 'ch', 'sh',
    'iiin', 'iin', 'in', 'eee', 'ee',
)

PREFIX_UNITS = ('qo', 'q', 'yo', 'y', 'do', 'd', 'so', 's', 'o')
SUFFIX_UNITS = (
    'aiin', 'iiin', 'iin', 'in',
    'edy', 'dy', 'ey', 'y',
    'ol', 'al', 'or', 'ar',
    'am', 'om', 'an', 'm', 'n', 's', 'r', 'l',
)

CONTROL_URLS = {
    'culpeper_herbal_en': 'https://www.gutenberg.org/cache/epub/49513/pg49513.txt',
    'caesar_bg_la': 'https://www.gutenberg.org/cache/epub/18837/pg18837.txt',
}


def r4(x):
    if isinstance(x, float):
        if math.isnan(x) or math.isinf(x):
            return None
        return round(x, 4)
    return x


def mean(xs):
    xs = list(xs)
    return sum(xs) / len(xs) if xs else float('nan')


def sd(xs):
    xs = list(xs)
    return statistics.pstdev(xs) if len(xs) > 1 else 0.0


# ---------------------------------------------------------------------------
# Tokenization & Control Corpora
# ---------------------------------------------------------------------------
def tokenize_word(w: str, mode: str) -> List[str]:
    """Tokenize word into atomic units according to alphabet mode."""
    if mode == 'eva_chars':
        return list(w)
    if mode == 'eva_units':
        out = []
        i = 0
        n = len(w)
        while i < n:
            matched = False
            for u in EVA_UNITS_ORDER:
                if w.startswith(u, i):
                    out.append(u)
                    i += len(u)
                    matched = True
                    break
            if not matched:
                out.append(w[i])
                i += 1
        return out
    if mode == 'gc_v101':
        return [c for c in w if c.isalnum()]
    return list(w)


def collapse_repeats(seq: Sequence[str]) -> List[str]:
    """Collapse consecutive identical symbols (e.g. a, a -> a)."""
    out = []
    for g in seq:
        if not out or out[-1] != g:
            out.append(g)
    return out


def fetch_control_words(name: str, max_tokens: int = 35000) -> List[str]:
    d = os.path.join(tempfile.gettempdir(), 'voynich_attack240')
    os.makedirs(d, exist_ok=True)
    p = os.path.join(d, name + '.txt')
    if not os.path.exists(p):
        try:
            urllib.request.urlretrieve(CONTROL_URLS[name], p)
        except Exception as e:
            print('Control download failed:', name, e)
            return []
    with open(p, encoding='utf-8', errors='replace') as fh:
        t = fh.read()
    a = t.find('*** START')
    b = t.find('*** END')
    if a >= 0:
        t = t[t.find('\n', a) + 1:b if b > a else None]
    t = t.replace('\r', '')
    if name == 'culpeper_herbal_en':
        idx = t.find('AMARA DULCIS.')
        if idx >= 0:
            t = t[idx:]
    else:
        t = re.sub(r'\[[^\]]*\]', ' ', t)
    words = re.findall(r"[a-z]+", t.lower())
    return words[:max_tokens]


# ---------------------------------------------------------------------------
# T1: Intra-Word Precedence DAG & Feedback Arc Set (FAS) Unidirectionality
# ---------------------------------------------------------------------------
def build_precedence_matrices(
    word_seqs: Sequence[Sequence[str]],
    weights: Optional[Sequence[int]] = None,
) -> Tuple[Counter, Counter, Counter]:
    """Return (adj_pairs, any_pairs, glyph_counts) excluding identical u == v.
    For adjacent bigrams, consecutive identical runs are collapsed first so
    u -> v represents transitions between distinct adjacent symbols.
    For any-distance precedence, every distinct pair (g_i, g_j) with i < j and
    g_i != g_j in the word is counted. Also returns unique-pair-per-word any_pairs.
    """
    adj = Counter()
    any_dist = Counter()
    glyph_freq = Counter()
    if weights is None:
        weights = [1] * len(word_seqs)
    for seq, w in zip(word_seqs, weights):
        for g in seq:
            glyph_freq[g] += w
        cseq = collapse_repeats(seq)
        for i in range(len(cseq) - 1):
            u, v = cseq[i], cseq[i + 1]
            if u != v:
                adj[(u, v)] += w
        m = len(seq)
        for i in range(m):
            ui = seq[i]
            for j in range(i + 1, m):
                vj = seq[j]
                if ui != vj:
                    any_dist[(ui, vj)] += w
    return adj, any_dist, glyph_freq


def optimize_linear_order(
    pair_counts: Counter,
    alphabet: Sequence[str],
    rng: random.Random,
    n_restarts: int = 25,
) -> Tuple[List[str], int, int]:
    """Find linear ordering of `alphabet` maximizing forward weight (minimizing FAS).
    Uses multi-start heuristic initializations + exhaustive single-node re-insertion
    (insert-opt) and adjacent/non-adjacent swap local search + simulated annealing.
    Returns (best_order, forward_weight, backward_weight).
    """
    nodes = list(alphabet)
    k = len(nodes)
    if k <= 1:
        return nodes, 0, 0

    idx_map = {g: i for i, g in enumerate(nodes)}
    # W[i][j] = weight of i -> j
    W = [[0] * k for _ in range(k)]
    total_w = 0
    for (u, v), c in pair_counts.items():
        if u in idx_map and v in idx_map and u != v:
            ui, vi = idx_map[u], idx_map[v]
            W[ui][vi] += c
            total_w += c

    if total_w == 0:
        return nodes, 0, 0

    # Net flow score for initial sorting: out_w / (out_w + in_w)
    scores = []
    for i in range(k):
        out_w = sum(W[i][j] for j in range(k))
        in_w = sum(W[j][i] for j in range(k))
        ratio = (out_w - in_w) / (out_w + in_w) if (out_w + in_w) > 0 else 0.0
        scores.append((ratio, out_w - in_w, i))

    def eval_order(order: List[int]) -> int:
        fw = 0
        for p in range(k):
            up = order[p]
            row = W[up]
            for q in range(p + 1, k):
                fw += row[order[q]]
        return fw

    def local_search(order: List[int]) -> Tuple[List[int], int]:
        """Exhaustive single-item insertion + pairwise swap until local optimum."""
        cur = order[:]
        cur_fw = eval_order(cur)
        improved = True
        while improved:
            improved = False
            # Single-element re-insertion (O(k^2) delta evaluation)
            for i in range(k):
                elem = cur[i]
                # Delta if we move elem from position i to position j
                # Moving right (j > i): elem passes cur[i+1..j], so for each x passed,
                # we lose W[elem][x] and gain W[x][elem]
                best_delta = 0
                best_j = i
                delta = 0
                for j in range(i + 1, k):
                    x = cur[j]
                    delta += W[x][elem] - W[elem][x]
                    if delta > best_delta:
                        best_delta = delta
                        best_j = j
                delta = 0
                for j in range(i - 1, -1, -1):
                    x = cur[j]
                    delta += W[elem][x] - W[x][elem]
                    if delta > best_delta:
                        best_delta = delta
                        best_j = j
                if best_delta > 0:
                    cur.pop(i)
                    cur.insert(best_j, elem)
                    cur_fw += best_delta
                    improved = True
                    break
            if improved:
                continue
            # Pairwise swap of non-adjacent elements
            for i in range(k):
                for j in range(i + 2, k):
                    u, v = cur[i], cur[j]
                    # Delta of swapping cur[i] and cur[j]
                    delta = W[v][u] - W[u][v]
                    for m in range(i + 1, j):
                        x = cur[m]
                        delta += (W[v][x] - W[x][v]) + (W[x][u] - W[u][x])
                    if delta > 0:
                        cur[i], cur[j] = cur[j], cur[i]
                        cur_fw += delta
                        improved = True
                        break
                if improved:
                    break
        return cur, cur_fw

    # Candidate initial orders
    init_orders = [
        [i for _, _, i in sorted(scores, reverse=True)],
        [i for _, _, i in sorted(scores, key=lambda t: (t[1], t[0]), reverse=True)],
    ]
    for _ in range(n_restarts):
        perm = list(range(k))
        rng.shuffle(perm)
        init_orders.append(perm)

    best_ord = None
    best_fw = -1
    for init in init_orders:
        cand, fw = local_search(init)
        if fw > best_fw:
            best_fw = fw
            best_ord = cand[:]
        # Perturb best and re-optimize (Iterated Local Search)
        if k >= 4:
            pert = cand[:]
            a, b = rng.sample(range(k), 2)
            pert[a], pert[b] = pert[b], pert[a]
            cand2, fw2 = local_search(pert)
            if fw2 > best_fw:
                best_fw = fw2
                best_ord = cand2[:]

    best_glyphs = [nodes[i] for i in best_ord]
    bw = total_w - best_fw
    return best_glyphs, best_fw, bw


def analyze_dag(
    word_seqs: Sequence[Sequence[str]],
    rng: random.Random,
    weights: Optional[Sequence[int]] = None,
    coverage_target: float = 0.995,
    compute_nulls: bool = False,
    n_null: int = 50,
) -> Dict:
    """Full DAG & FAS analysis for a given sequence collection."""
    if weights is None:
        weights = [1] * len(word_seqs)
    adj, any_dist, gfreq = build_precedence_matrices(word_seqs, weights)
    tot_glyphs = sum(gfreq.values())
    # Select frequent glyphs covering >= coverage_target (and at least top 25 if present)
    sorted_g = [g for g, _ in gfreq.most_common()]
    active_g = []
    cum = 0
    for g in sorted_g:
        active_g.append(g)
        cum += gfreq[g]
        if cum / tot_glyphs >= coverage_target and len(active_g) >= min(22, len(sorted_g)):
            break
    if len(sorted_g) <= 30:
        active_g = sorted_g

    res = {
        'n_words': sum(weights),
        'n_unique_seqs': len(word_seqs),
        'n_alphabet_total': len(sorted_g),
        'n_alphabet_active': len(active_g),
        'active_coverage': r4(sum(gfreq[g] for g in active_g) / tot_glyphs) if tot_glyphs else 0.0,
    }

    for mode_name, pairs in (('adjacent', adj), ('any_distance', any_dist)):
        # Filter to active_g
        aset = set(active_g)
        fpairs = Counter({(u, v): c for (u, v), c in pairs.items() if u in aset and v in aset and u != v})
        tot_pairs = sum(fpairs.values())
        # Weighted mean pairwise directionality D(u,v) = |C(u,v)-C(v,u)| / (C(u,v)+C(v,u))
        unordered = set()
        for u, v in fpairs:
            unordered.add((min(u, v), max(u, v)))
        num_dir = 0
        den_dir = 0
        pair_dirs = []
        for u, v in unordered:
            c1 = fpairs[(u, v)]
            c2 = fpairs[(v, u)]
            s = c1 + c2
            d = abs(c1 - c2)
            num_dir += d
            den_dir += s
            if s >= 20:
                pair_dirs.append(d / s)
        w_dir = num_dir / den_dir if den_dir else 0.0
        u_dir = mean(pair_dirs) if pair_dirs else 0.0

        order, fw, bw = optimize_linear_order(fpairs, active_g, rng)
        fas_rate = bw / (fw + bw) if (fw + bw) > 0 else 0.0

        # Identify top feedback arcs (violating transitions u -> v where pos(u) > pos(v))
        pos = {g: i for i, g in enumerate(order)}
        viol_arcs = []
        glyph_viol_involvement = Counter()
        for (u, v), c in fpairs.items():
            if pos[u] > pos[v]:
                viol_arcs.append((u, v, c, fpairs[(v, u)]))
                glyph_viol_involvement[u] += c
                glyph_viol_involvement[v] += c
        viol_arcs.sort(key=lambda x: -x[2])

        # Cumulative share of feedback weight attributable to top ambivalent glyphs
        # (measured by greedy removal or involvement)
        rem_bw = bw
        removed = set()
        greedy_curve = []
        # Rank glyphs by backward weight where glyph is the *target* or *source* of a feedback arc
        for step in range(min(8, len(active_g))):
            best_g = None
            best_drop = -1
            for g in active_g:
                if g in removed:
                    continue
                drop = sum(
                    c for (u, v), c in fpairs.items()
                    if pos[u] > pos[v] and u not in removed and v not in removed and (u == g or v == g)
                )
                if drop > best_drop:
                    best_drop = drop
                    best_g = g
            if best_g is None or best_drop <= 0:
                break
            removed.add(best_g)
            rem_bw -= best_drop
            greedy_curve.append({
                'step': step + 1,
                'glyph': best_g,
                'feedback_dropped_pct_of_fas': r4(100.0 * (bw - rem_bw) / bw) if bw else 100.0,
                'residual_fas_rate': r4(rem_bw / (fw + bw)) if (fw + bw) else 0.0,
            })

        block = {
            'total_transitions': tot_pairs,
            'weighted_directionality_D': r4(w_dir),
            'unweighted_directionality_D_min20': r4(u_dir),
            'optimal_order': order,
            'forward_weight': fw,
            'feedback_weight': bw,
            'forward_pct': r4(100.0 * (1.0 - fas_rate)),
            'fas_rate': r4(fas_rate),
            'fas_pct': r4(100.0 * fas_rate),
            'top_feedback_arcs': [
                {
                    'arc': f'{u}->{v}',
                    'backward_count': c,
                    'forward_reverse_count': rev,
                    'share_of_all_feedback_pct': r4(100.0 * c / bw) if bw else 0.0,
                }
                for u, v, c, rev in viol_arcs[:15]
            ],
            'greedy_ambivalent_glyph_attribution': greedy_curve,
        }

        if compute_nulls:
            # Null 1: Random permutation of alphabet order on observed matrix
            rand_fas = []
            for _ in range(200):
                p_ord = active_g[:]
                rng.shuffle(p_ord)
                p_pos = {g: i for i, g in enumerate(p_ord)}
                rbw = sum(c for (u, v), c in fpairs.items() if p_pos[u] > p_pos[v])
                rand_fas.append(rbw / tot_pairs if tot_pairs else 0.5)
            # Null 2: Within-word character shuffle (preserving exact word lengths & multisets),
            # then re-optimizing the linear order on the shuffled corpus!
            shuf_fas = []
            shuf_dir = []
            for _ in range(n_null):
                shuf_seqs = []
                for seq in word_seqs:
                    s2 = list(seq)
                    rng.shuffle(s2)
                    shuf_seqs.append(s2)
                s_adj, s_any, _ = build_precedence_matrices(shuf_seqs, weights)
                spairs = s_adj if mode_name == 'adjacent' else s_any
                sfpairs = Counter({(u, v): c for (u, v), c in spairs.items() if u in aset and v in aset and u != v})
                stot = sum(sfpairs.values())
                _, sfw, sbw = optimize_linear_order(sfpairs, active_g, rng, n_restarts=5)
                shuf_fas.append(sbw / (sfw + sbw) if (sfw + sbw) else 0.5)
                s_num = sum(abs(sfpairs[(u, v)] - sfpairs[(v, u)]) for u, v in unordered)
                s_den = sum(sfpairs[(u, v)] + sfpairs[(v, u)] for u, v in unordered)
                shuf_dir.append(s_num / s_den if s_den else 0.0)
            block['null_random_order_fas_mean'] = r4(mean(rand_fas))
            block['null_random_order_fas_sd'] = r4(sd(rand_fas))
            block['null_within_word_shuffle_optimized_fas_mean'] = r4(mean(shuf_fas))
            block['null_within_word_shuffle_optimized_fas_sd'] = r4(sd(shuf_fas))
            block['null_within_word_shuffle_D_mean'] = r4(mean(shuf_dir))
            block['z_vs_within_word_shuffle'] = r4((fas_rate - mean(shuf_fas)) / sd(shuf_fas)) if sd(shuf_fas) > 0 else None

        res[mode_name] = block
    return res


def positional_allograph_split_experiment(
    words_tokens: Sequence[Sequence[str]],
    rng: random.Random,
) -> List[Dict]:
    """Test how much FAS drops when boundary-ambivalent glyphs are split into
    positional allographs:
      - `g_pre`: onset / pre-core position (word-initial i == 0, or i == 1 before
        any core gallows/bench glyph, e.g. `o` in `qo-`, `so-`, `do-`, `yo-`)
      - `g_end`: coda / word-final position (i == len-1, or penultimate `d` before
        final `y` in `-dy`)
      - `g_post`: post-core medial position
    """
    core_set = {'ch', 'sh', 'k', 't', 'p', 'f', 'cth', 'ckh', 'cph', 'cfh'}
    split_stages = [
        ('0_unsplit_baseline', set()),
        ('1_split_o_pos', {'o'}),
        ('2_split_o_d_pos', {'o', 'd'}),
        ('3_split_o_d_y_pos', {'o', 'd', 'y'}),
        ('4_split_o_d_y_s_pos', {'o', 'd', 'y', 's'}),
        ('5_split_o_d_y_s_r_l_pos', {'o', 'd', 'y', 's', 'r', 'l'}),
        ('6_split_o_d_y_s_r_l_a_e_pos', {'o', 'd', 'y', 's', 'r', 'l', 'a', 'e'}),
    ]
    out = []
    for label, split_set in split_stages:
        transformed = []
        for seq in words_tokens:
            if len(seq) <= 1:
                transformed.append(list(seq))
                continue
            seen_core = False
            new_seq = []
            for idx, g in enumerate(seq):
                if g in core_set:
                    seen_core = True
                if g in split_set:
                    if not seen_core and idx <= 1:
                        tag = 'pre'
                    elif idx == len(seq) - 1 or (g == 'd' and idx == len(seq) - 2 and seq[-1] == 'y'):
                        tag = 'end'
                    else:
                        tag = 'post'
                    new_seq.append(f'{g}_{tag}')
                else:
                    new_seq.append(g)
            transformed.append(new_seq)
        adj, anyd, gf = build_precedence_matrices(transformed)
        act = [g for g, cnt in gf.most_common() if cnt >= 20]
        aset = set(act)
        fadj = Counter({(u, v): c for (u, v), c in adj.items() if u in aset and v in aset and u != v})
        fany = Counter({(u, v): c for (u, v), c in anyd.items() if u in aset and v in aset and u != v})
        _, fw_adj, bw_adj = optimize_linear_order(fadj, act, rng, n_restarts=15)
        _, fw_any, bw_any = optimize_linear_order(fany, act, rng, n_restarts=15)
        fas_adj = bw_adj / (fw_adj + bw_adj) if (fw_adj + bw_adj) else 0.0
        fas_any = bw_any / (fw_any + bw_any) if (fw_any + bw_any) else 0.0

        # Weighted directionality D
        u_adj = {(min(u, v), max(u, v)) for u, v in fadj}
        d_adj = (sum(abs(fadj[(u, v)] - fadj[(v, u)]) for u, v in u_adj)
                 / sum(fadj[(u, v)] + fadj[(v, u)] for u, v in u_adj))
        u_any = {(min(u, v), max(u, v)) for u, v in fany}
        d_any = (sum(abs(fany[(u, v)] - fany[(v, u)]) for u, v in u_any)
                 / sum(fany[(u, v)] + fany[(v, u)] for u, v in u_any))

        out.append({
            'stage': label,
            'split_glyphs': sorted(split_set),
            'n_active_glyphs': len(act),
            'adjacent_fas_pct': r4(100.0 * fas_adj),
            'adjacent_forward_pct': r4(100.0 * (1.0 - fas_adj)),
            'adjacent_D': r4(d_adj),
            'any_distance_fas_pct': r4(100.0 * fas_any),
            'any_distance_forward_pct': r4(100.0 * (1.0 - fas_any)),
            'any_distance_D': r4(d_any),
        })
    return out


# ---------------------------------------------------------------------------
# T2: Left-to-Right vs. Right-to-Left Positional Entropy Profile
# ---------------------------------------------------------------------------
def cond_entropy_mm(pairs: Sequence[Tuple[object, object]]) -> Tuple[float, float]:
    """Compute plug-in (MLE) and Miller-Madow bias-corrected conditional entropy
    H(Y | X) in bits from observed (x, y) pairs.
    """
    n = len(pairs)
    if n == 0:
        return 0.0, 0.0
    cx = Counter()
    cxy = Counter()
    for x, y in pairs:
        cx[x] += 1
        cxy[(x, y)] += 1
    h_mle = 0.0
    for (x, y), c in cxy.items():
        h_mle += (c / n) * math.log2(cx[x] / c)
    # Miller-Madow correction for H(X,Y) - H(X):
    # Bias(H(X,Y)) ~ (|supp(X,Y)| - 1) / (2 N ln 2)
    # Bias(H(X))   ~ (|supp(X)| - 1) / (2 N ln 2)
    m_xy = len(cxy)
    m_x = len(cx)
    mm_corr = max(0.0, (m_xy - m_x) / (2.0 * n * math.log(2.0)))
    return h_mle, h_mle + mm_corr


def entropy_profile_fixed_length(
    seqs: Sequence[Sequence[str]],
    L: int,
) -> Dict:
    """For sequences of exact length L, compute slot-by-slot forward and backward
    conditional entropies (both Markov-1 bigram and full chain-rule history).
    """
    sub = [s for s in seqs if len(s) == L]
    n = len(sub)
    if n < 30:
        return {'L': L, 'n': n, 'skipped': True}

    uncond_mm = []
    markov1_fwd_mm = []
    markov1_bwd_mm = []
    chain_fwd_mle = []
    chain_fwd_mm = []
    chain_bwd_mle = []
    chain_bwd_mm = []

    for k in range(L):
        # Unconditional H(g_k)
        _, h_u = cond_entropy_mm([(None, s[k]) for s in sub])
        uncond_mm.append(r4(h_u))

        # Markov-1 forward H(g_k | g_{k-1})
        if k == 0:
            markov1_fwd_mm.append(r4(h_u))
        else:
            _, h_m1f = cond_entropy_mm([(s[k - 1], s[k]) for s in sub])
            markov1_fwd_mm.append(r4(h_m1f))

        # Markov-1 backward H(g_k | g_{k+1})
        if k == L - 1:
            markov1_bwd_mm.append(r4(h_u))
        else:
            _, h_m1b = cond_entropy_mm([(s[k + 1], s[k]) for s in sub])
            markov1_bwd_mm.append(r4(h_m1b))

        # Full chain forward H(g_k | g_0..g_{k-1})
        hmle_f, hmm_f = cond_entropy_mm([(tuple(s[:k]), s[k]) for s in sub])
        chain_fwd_mle.append(r4(hmle_f))
        chain_fwd_mm.append(r4(hmm_f))

        # Full chain backward H(g_k | g_{k+1}..g_{L-1})
        hmle_b, hmm_b = cond_entropy_mm([(tuple(s[k + 1:]), s[k]) for s in sub])
        chain_bwd_mle.append(r4(hmle_b))
        chain_bwd_mm.append(r4(hmm_b))

    # Compare step-by-step from word boundary (step 1 = boundary glyph, step 2 = 2nd glyph in, etc.)
    # Forward step m (m=0..L-1) is slot k=m; Backward step m from end is slot k=L-1-m.
    bwd_by_step_from_end_markov1 = list(reversed(markov1_bwd_mm))
    bwd_by_step_from_end_chain_mm = list(reversed(chain_bwd_mm))

    # Asymmetry summary: first half vs second half of word
    half = L // 2
    fwd_first_half_m1 = sum(markov1_fwd_mm[:half])
    fwd_last_half_m1 = sum(markov1_fwd_mm[L - half:])
    bwd_first_steps_m1 = sum(bwd_by_step_from_end_markov1[:half])

    return {
        'L': L,
        'n': n,
        'unconditional_slot_H_mm': uncond_mm,
        'markov1_forward_H_mm_by_slot': markov1_fwd_mm,
        'markov1_backward_H_mm_by_slot': markov1_bwd_mm,
        'markov1_backward_H_mm_by_step_from_end': bwd_by_step_from_end_markov1,
        'chain_forward_H_mle_by_slot': chain_fwd_mle,
        'chain_forward_H_mm_by_slot': chain_fwd_mm,
        'chain_backward_H_mle_by_slot': chain_bwd_mle,
        'chain_backward_H_mm_by_slot': chain_bwd_mm,
        'chain_backward_H_mm_by_step_from_end': bwd_by_step_from_end_chain_mm,
        'peak_unconditional_slot_1indexed': int(max(range(L), key=lambda i: uncond_mm[i]) + 1),
        'peak_markov1_forward_slot_1indexed': int(max(range(L), key=lambda i: markov1_fwd_mm[i]) + 1),
        'boundary_onset_H_g1': uncond_mm[0],
        'boundary_coda_H_gL': uncond_mm[-1],
        'onset_minus_coda_H_bits': r4(uncond_mm[0] - uncond_mm[-1]),
        'markov1_total_forward_bits': r4(sum(markov1_fwd_mm)),
        'markov1_first_half_forward_bits': r4(fwd_first_half_m1),
        'markov1_last_half_forward_bits': r4(fwd_last_half_m1),
        'markov1_first_half_backward_from_end_bits': r4(bwd_first_steps_m1),
    }


def aligned_boundary_entropy_profile(
    seqs: Sequence[Sequence[str]],
    max_depth: int = 6,
) -> Dict:
    """Across all words of length >= k, compute start-aligned (+1..+max_depth)
    and end-aligned (-1..-max_depth) unconditional and Markov-1 conditional entropies.
    """
    start_uncond = []
    start_m1_fwd = []
    end_uncond = []
    end_m1_bwd = []
    counts_at_depth = []

    for d in range(max_depth):
        sub = [s for s in seqs if len(s) > d]
        counts_at_depth.append(len(sub))
        if len(sub) < 50:
            break
        _, hu_s = cond_entropy_mm([(None, s[d]) for s in sub])
        start_uncond.append(r4(hu_s))
        if d == 0:
            start_m1_fwd.append(r4(hu_s))
        else:
            _, hm_s = cond_entropy_mm([(s[d - 1], s[d]) for s in sub])
            start_m1_fwd.append(r4(hm_s))

        _, hu_e = cond_entropy_mm([(None, s[-(d + 1)]) for s in sub])
        end_uncond.append(r4(hu_e))
        if d == 0:
            end_m1_bwd.append(r4(hu_e))
        else:
            _, hm_e = cond_entropy_mm([(s[-d], s[-(d + 1)]) for s in sub])
            end_m1_bwd.append(r4(hm_e))

    return {
        'depths': list(range(1, len(start_uncond) + 1)),
        'n_at_depth': counts_at_depth[:len(start_uncond)],
        'start_aligned_uncond_H_mm': start_uncond,
        'start_aligned_markov1_fwd_H_mm': start_m1_fwd,
        'end_aligned_uncond_H_mm': end_uncond,
        'end_aligned_markov1_bwd_H_mm': end_m1_bwd,
    }


# ---------------------------------------------------------------------------
# T3: Word-Length Binomiality, Variance & 3-Slot Decomposition
# ---------------------------------------------------------------------------
def length_distribution_stats(lengths: Sequence[int]) -> Dict:
    n = len(lengths)
    if n == 0:
        return {}
    mu = sum(lengths) / n
    var = sum((x - mu) ** 2 for x in lengths) / n
    sd_val = math.sqrt(var)
    fano = var / mu if mu > 0 else 0.0
    if sd_val > 0:
        skew = (sum((x - mu) ** 3 for x in lengths) / n) / (sd_val ** 3)
        kurt_excess = (sum((x - mu) ** 4 for x in lengths) / n) / (sd_val ** 4) - 3.0
    else:
        skew, kurt_excess = 0.0, 0.0

    hist = Counter(lengths)
    max_l = max(lengths)
    emp_p = {k: hist[k] / n for k in range(0, max_l + 5)}

    # Fit 1: Standard Binomial(N_bin, p) over N_bin in 1..30 minimizing TVD
    best_bin = None
    for n_b in range(max(2, int(round(mu))), 35):
        p_b = min(0.999, max(0.001, mu / n_b))
        probs = {
            k: math.comb(n_b, k) * (p_b ** k) * ((1.0 - p_b) ** (n_b - k)) if k <= n_b else 0.0
            for k in emp_p
        }
        tvd = 0.5 * sum(abs(emp_p[k] - probs[k]) for k in emp_p)
        if best_bin is None or tvd < best_bin['tvd']:
            best_bin = {'n': n_b, 'p': r4(p_b), 'tvd': r4(tvd), 'implied_var': r4(n_b * p_b * (1.0 - p_b))}

    # Fit 2: Shifted Binomial 1 + Binomial(N_bin, p) (since word length >= 1)
    best_sbin = None
    mu_s = max(0.01, mu - 1.0)
    for n_b in range(max(1, int(round(mu_s))), 35):
        p_b = min(0.999, max(0.001, mu_s / n_b))
        probs = {
            k: (math.comb(n_b, k - 1) * (p_b ** (k - 1)) * ((1.0 - p_b) ** (n_b - (k - 1)))
                if 1 <= k <= n_b + 1 else 0.0)
            for k in emp_p
        }
        tvd = 0.5 * sum(abs(emp_p[k] - probs[k]) for k in emp_p)
        if best_sbin is None or tvd < best_sbin['tvd']:
            best_sbin = {'n_trials': n_b, 'p': r4(p_b), 'tvd': r4(tvd), 'implied_var': r4(n_b * p_b * (1.0 - p_b))}

    # Fit 3: Shifted Poisson 1 + Poisson(mu - 1) and standard Poisson(mu)
    lam = max(0.01, mu)
    pois_probs = {k: math.exp(-lam) * (lam ** k) / math.factorial(k) for k in emp_p}
    pois_tvd = 0.5 * sum(abs(emp_p[k] - pois_probs[k]) for k in emp_p)

    slam = max(0.01, mu - 1.0)
    spois_probs = {k: (math.exp(-slam) * (slam ** (k - 1)) / math.factorial(k - 1) if k >= 1 else 0.0) for k in emp_p}
    spois_tvd = 0.5 * sum(abs(emp_p[k] - spois_probs[k]) for k in emp_p)

    return {
        'n': n,
        'mean': r4(mu),
        'variance': r4(var),
        'sd': r4(sd_val),
        'fano_dispersion_var_over_mean': r4(fano),
        'skewness': r4(skew),
        'excess_kurtosis': r4(kurt_excess),
        'best_binomial_fit': best_bin,
        'best_shifted_binomial_fit': best_sbin,
        'poisson_tvd': r4(pois_tvd),
        'shifted_poisson_tvd': r4(spois_tvd),
        'histogram_pct': {str(k): r4(100.0 * hist[k] / n) for k in sorted(hist) if hist[k] / n >= 0.002},
    }


def segment_three_slots(w: str) -> Tuple[List[str], List[str], List[str]]:
    """Decompose an EVA word into (Prefix_units, Core_units, Suffix_units)
    using atomic eva_units. At most 1 prefix segment and 1 suffix segment are stripped,
    leaving at least 1 core unit whenever len(w) >= 1.
    """
    prefs = ('qo', 'q', 'yo', 'y', 'do', 'd', 'so', 's', 'po', 'fo', 'o', 'l', 'r')
    suffs = (
        'eedy', 'edy', 'ody', 'dy', 'eed', 'ed', 'od',
        'eey', 'ey', 'oy', 'ay',
        'aiin', 'oiin', 'iiin', 'iin', 'in', 'ain', 'aiir', 'air',
        'al', 'ol', 'ar', 'or', 'am', 'om', 'an',
        'y', 'd', 'm', 'n', 's', 'r', 'l',
    )
    p_str = ''
    rem = w
    for pr in prefs:
        if rem.startswith(pr) and len(rem) > len(pr):
            p_str = pr
            rem = rem[len(pr):]
            break
    s_str = ''
    for sf in suffs:
        if rem.endswith(sf) and len(rem) > len(sf):
            s_str = sf
            rem = rem[:-len(sf)]
            break
    return (
        tokenize_word(p_str, 'eva_units') if p_str else [],
        tokenize_word(rem, 'eva_units') if rem else [],
        tokenize_word(s_str, 'eva_units') if s_str else [],
    )


def analyze_slot_decomposition(words: Sequence[str]) -> Dict:
    lp, lc, ls, ltot = [], [], [], []
    cp_chars, cc_chars, cs_chars = [], [], []
    core_len_hist = Counter()
    for w in words:
        p, c, s = segment_three_slots(w)
        lp.append(len(p))
        lc.append(len(c))
        ls.append(len(s))
        ltot.append(len(p) + len(c) + len(s))
        core_len_hist[len(c)] += 1
        cp_chars.append(sum(len(u) for u in p))
        cc_chars.append(sum(len(u) for u in c))
        cs_chars.append(sum(len(u) for u in s))

    n = len(words)
    mp, mc, ms = mean(lp), mean(lc), mean(ls)
    vp = sum((x - mp) ** 2 for x in lp) / n
    vc = sum((x - mc) ** 2 for x in lc) / n
    vs = sum((x - ms) ** 2 for x in ls) / n
    vtot = sum((x - (mp + mc + ms)) ** 2 for x in ltot) / n
    cov_pc = sum((a - mp) * (b - mc) for a, b in zip(lp, lc)) / n
    cov_ps = sum((a - mp) * (b - ms) for a, b in zip(lp, ls)) / n
    cov_cs = sum((a - mc) * (b - ms) for a, b in zip(lc, ls)) / n

    return {
        'n_words': n,
        'units': {
            'prefix_mean': r4(mp), 'prefix_var': r4(vp),
            'core_mean': r4(mc), 'core_var': r4(vc),
            'suffix_mean': r4(ms), 'suffix_var': r4(vs),
            'sum_of_slot_variances': r4(vp + vc + vs),
            'total_word_unit_var': r4(vtot),
            'cov_pref_core': r4(cov_pc),
            'cov_pref_suff': r4(cov_ps),
            'cov_core_suff': r4(cov_cs),
            'core_length_1_or_2_units_pct': r4(100.0 * (core_len_hist[1] + core_len_hist[2]) / n),
            'core_length_hist_pct': {str(k): r4(100.0 * core_len_hist[k] / n) for k in sorted(core_len_hist) if core_len_hist[k] / n >= 0.002},
        },
        'chars': {
            'prefix_char_mean': r4(mean(cp_chars)),
            'core_char_mean': r4(mean(cc_chars)),
            'core_char_var': r4(sum((x - mean(cc_chars)) ** 2 for x in cc_chars) / n),
            'suffix_char_mean': r4(mean(cs_chars)),
        }
    }


# ---------------------------------------------------------------------------
# T4: Currier Language A vs. Language B & Within-Scribe 3 Paradigm Shift
# ---------------------------------------------------------------------------
CANON_CORES_15 = {'ch', 'sh', 'k', 't', 'd', 'l', 'r', 'p', 'f', 'cth', 'ckh', 'cph', 'cfh', 'a'}


def parse_four_slot_paradigm(w: str) -> Tuple[str, str, str, str]:
    """Parse word into 4 orthogonal morphological slots for A/B shift analysis:
      (Prefix, Onset_Core, Medial_Vowel_Grade, Terminal_Coda)
    """
    orig = w
    # 1. Prefix
    pref = '0'
    for p in ('qo', 'q', 'yo', 'y', 'do', 'so', 'o', 'd', 's'):
        if p == 's' and w.startswith('sh'):
            continue
        if w.startswith(p) and len(w) > len(p) + 1:
            if p in ('d', 's') and w[len(p):] in ('aiin', 'iiin', 'iin', 'in', 'y', 'al', 'ar', 'ol', 'or', 'am', 'ain'):
                continue
            pref = p
            w = w[len(p):]
            break

    # 2. Terminal Coda
    suff = '0'
    for s in ('iiin', 'iin', 'in', 'dy', 'd', 'y', 'l', 'r', 'm', 'n', 's', 'g'):
        if w.endswith(s) and len(w) > len(s):
            suff = s
            w = w[:-len(s)]
            break

    # 3. Medial Vowel-Grade
    vowel = '0'
    for v in ('eee', 'ee', 'e', 'eo', 'oe', 'o', 'a'):
        if w.endswith(v) and len(w) > len(v):
            vowel = v
            w = w[:-len(v)]
            break

    core = w if w else orig
    return pref, core, vowel, suff


def js_divergence(c1: Counter, c2: Counter) -> float:
    """Jensen-Shannon divergence (in bits, [0, 1]) between two frequency Counters."""
    n1, n2 = sum(c1.values()), sum(c2.values())
    if n1 == 0 or n2 == 0:
        return 1.0
    keys = set(c1) | set(c2)
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


def analyze_currier_ab_and_scribe3(lines) -> Dict:
    """Analyze Currier A vs B morphological shift globally and inside Scribe 3."""
    p_lines = [l for l in lines if l.unit == 'P']
    partitions = {
        'ALL_Lang_A': [w for l in p_lines if l.lang == 'A' for w in l.clean_words],
        'ALL_Lang_B': [w for l in p_lines if l.lang == 'B' for w in l.clean_words],
        'H1_Lang_A_Herb': [w for l in p_lines if l.hand == '1' and l.lang == 'A' and l.section == 'H' for w in l.clean_words],
        'H1_Lang_A_Pharma': [w for l in p_lines if l.hand == '1' and l.lang == 'A' and l.section == 'P' for w in l.clean_words],
        'H3_Lang_A_f58': [w for l in p_lines if l.hand == '3' and l.lang == 'A' for w in l.clean_words],
        'H3_Lang_B_Q20': [w for l in p_lines if l.hand == '3' and l.lang == 'B' and l.section == 'S' for w in l.clean_words],
        'H3_Lang_B_Herb': [w for l in p_lines if l.hand == '3' and l.lang == 'B' and l.section == 'H' for w in l.clean_words],
        'H2_Lang_B_Herb': [w for l in p_lines if l.hand == '2' and l.lang == 'B' and l.section == 'H' for w in l.clean_words],
        'H2_Lang_B_Balneo': [w for l in p_lines if l.hand == '2' and l.lang == 'B' and l.section == 'B' for w in l.clean_words],
    }

    slot_counters = {}
    summary_stats = {}
    for name, ws in partitions.items():
        cp, cc, cc15, cv, cs = Counter(), Counter(), Counter(), Counter(), Counter()
        w_cnt = Counter(ws)
        for w in ws:
            p, c, v, s = parse_four_slot_paradigm(w)
            cp[p] += 1
            cc[c] += 1
            cc15[c if c in CANON_CORES_15 else 'OTHER'] += 1
            cv[v] += 1
            cs[s] += 1
        slot_counters[name] = {'pref': cp, 'core': cc, 'core15': cc15, 'vowel': cv, 'suff': cs, 'word': w_cnt}
        n = len(ws)
        summary_stats[name] = {
            'n_tokens': n,
            'n_types': len(w_cnt),
            'qo_prefix_pct': r4(100.0 * (cp['qo'] + cp['q']) / n) if n else 0.0,
            'e_grade_vowel_pct': r4(100.0 * (cv['e'] + cv['ee'] + cv['eee'] + cv['eo']) / n) if n else 0.0,
            'o_a_grade_vowel_pct': r4(100.0 * (cv['o'] + cv['a'] + cv['oe']) / n) if n else 0.0,
            'zero_grade_vowel_pct': r4(100.0 * cv['0'] / n) if n else 0.0,
            'dy_coda_pct': r4(100.0 * cs['dy'] / n) if n else 0.0,
            'y_coda_pct': r4(100.0 * cs['y'] / n) if n else 0.0,
            'l_r_coda_pct': r4(100.0 * (cs['l'] + cs['r']) / n) if n else 0.0,
            'iin_in_coda_pct': r4(100.0 * (cs['iin'] + cs['iiin'] + cs['in']) / n) if n else 0.0,
            'top_prefixes': [(k, r4(100.0 * v / n)) for k, v in cp.most_common(6)],
            'top_cores': [(k, r4(100.0 * v / n)) for k, v in cc.most_common(8)],
            'top_vowels': [(k, r4(100.0 * v / n)) for k, v in cv.most_common(6)],
            'top_codas': [(k, r4(100.0 * v / n)) for k, v in cs.most_common(8)],
        }

    jsd_table = []
    KeyPairs = [
        ('H3_Lang_A_f58', 'H3_Lang_B_Q20', 'Same Scribe (H=3), Same Section (S), Lang A vs Lang B'),
        ('H3_Lang_A_f58', 'H1_Lang_A_Herb', 'Different Scribe (H=3 vs H=1 Herb), Same Language (Lang A)'),
        ('H3_Lang_A_f58', 'H1_Lang_A_Pharma', 'Different Scribe (H=3 vs H=1 Pharma), Same Language (Lang A)'),
        ('H3_Lang_B_Q20', 'H3_Lang_B_Herb', 'Same Scribe (H=3), Same Language (Lang B), Section S vs H'),
        ('H3_Lang_B_Q20', 'H2_Lang_B_Balneo', 'Different Scribe (H=3 vs H=2 Balneo), Same Language (Lang B)'),
        ('H3_Lang_B_Herb', 'H2_Lang_B_Herb', 'Different Scribe (H=3 vs H=2), Same Language (Lang B), Same Section (H)'),
        ('ALL_Lang_A', 'ALL_Lang_B', 'Global Currier Language A vs Language B'),
    ]
    for p1, p2, desc in KeyPairs:
        s1, s2 = slot_counters[p1], slot_counters[p2]
        jsd_table.append({
            'pair': f'{p1} vs {p2}',
            'description': desc,
            'jsd_prefix_bits': r4(js_divergence(s1['pref'], s2['pref'])),
            'jsd_core15_bits': r4(js_divergence(s1['core15'], s2['core15'])),
            'jsd_core_all_bits': r4(js_divergence(s1['core'], s2['core'])),
            'jsd_vowel_grade_bits': r4(js_divergence(s1['vowel'], s2['vowel'])),
            'jsd_coda_bits': r4(js_divergence(s1['suff'], s2['suff'])),
            'jsd_full_word_bits': r4(js_divergence(s1['word'], s2['word'])),
        })

    major_cores = ['ch', 'sh', 'k', 't', 'd', 'l', 'r', 'p', 'f', 'cth', 'ckh']
    core_realizations = defaultdict(lambda: defaultdict(Counter))
    for part_key in ('ALL_Lang_A', 'ALL_Lang_B', 'H3_Lang_A_f58', 'H3_Lang_B_Q20', 'H1_Lang_A_Herb'):
        for w in partitions[part_key]:
            p, c, v, s = parse_four_slot_paradigm(w)
            core_realizations[c][part_key][w] += 1

    cognate_paradigms = []
    for c in major_cores:
        ca = core_realizations[c]['ALL_Lang_A']
        cb = core_realizations[c]['ALL_Lang_B']
        h3a = core_realizations[c]['H3_Lang_A_f58']
        h3b = core_realizations[c]['H3_Lang_B_Q20']
        na, nb = sum(ca.values()), sum(cb.values())
        if na < 20 or nb < 20:
            continue
        va, vb, sa, sb = Counter(), Counter(), Counter(), Counter()
        for w, cnt in ca.items():
            _, _, v, s = parse_four_slot_paradigm(w)
            va[v] += cnt
            sa[s] += cnt
        for w, cnt in cb.items():
            _, _, v, s = parse_four_slot_paradigm(w)
            vb[v] += cnt
            sb[s] += cnt

        cognate_paradigms.append({
            'core': c,
            'count_lang_A': na,
            'count_lang_B': nb,
            'count_H3_A_f58': sum(h3a.values()),
            'count_H3_B_Q20': sum(h3b.values()),
            'lang_A_e_grade_pct': r4(100.0 * (va['e'] + va['ee'] + va['eee'] + va['eo']) / na),
            'lang_B_e_grade_pct': r4(100.0 * (vb['e'] + vb['ee'] + vb['eee'] + vb['eo']) / nb),
            'lang_A_o_a_grade_pct': r4(100.0 * (va['o'] + va['a'] + va['oe']) / na),
            'lang_B_o_a_grade_pct': r4(100.0 * (vb['o'] + vb['a'] + vb['oe']) / nb),
            'lang_A_dy_coda_pct': r4(100.0 * sa['dy'] / na),
            'lang_B_dy_coda_pct': r4(100.0 * sb['dy'] / nb),
            'lang_A_l_r_coda_pct': r4(100.0 * (sa['l'] + sa['r']) / na),
            'lang_B_l_r_coda_pct': r4(100.0 * (sb['l'] + sb['r']) / nb),
            'lang_A_top3_words': [(w, cnt) for w, cnt in ca.most_common(3)],
            'lang_B_top3_words': [(w, cnt) for w, cnt in cb.most_common(3)],
            'H3_A_f58_top3_words': [(w, cnt) for w, cnt in h3a.most_common(3)],
            'H3_B_Q20_top3_words': [(w, cnt) for w, cnt in h3b.most_common(3)],
        })

    return {
        'partition_summaries': summary_stats,
        'jsd_comparisons': jsd_table,
        'cognate_core_shift_paradigms': cognate_paradigms,
    }


# ---------------------------------------------------------------------------
# T5: Visual Plots & High-Res Scan Crops
# ---------------------------------------------------------------------------
def plot_dag_matrix(res_t1: Dict, out_path: str):
    from PIL import Image, ImageDraw

    W, H = 1600, 920
    img = Image.new('RGB', (W, H), (252, 251, 247))
    d = ImageDraw.Draw(img)

    # Title banner
    d.rectangle([0, 0, W, 58], fill=(28, 37, 54))
    d.text((24, 12), "ATTACK 242 (T1): INTRA-WORD PRECEDENCE DAG, OPTIMAL TOPOLOGICAL ORDER & ALLOGRAPH SPLITTING", fill=(255, 255, 255))
    d.text((24, 34), "Left: Adjacent Bigram Transition Matrix in Optimal Order (ZL3b eva_units) | Right Top: FAS Violation Rate Across Corpora | Right Bottom: Allograph Split Curve", fill=(200, 215, 235))

    # Left Panel: Heatmap of pairwise adjacent transitions in optimal order for eva_units ALL
    units_blk = res_t1['eva_units']['ALL_tokens']['adjacent']
    order = units_blk['optimal_order'][:22]
    k = len(order)
    pair_map = res_t1['_raw_adj_eva_units_map']

    x0, y0 = 75, 110
    cell = 31
    grid_size = k * cell

    d.text((x0, 72), f"Optimal Glyph Order (EVA Units, Top {k} = 99.7% cov): Forward = {units_blk['forward_pct']:.2f}% (above diag), Feedback FAS = {units_blk['fas_pct']:.2f}% (below diag)", fill=(20, 20, 20))

    max_c = max([pair_map.get((u, v), 0) for u in order for v in order if u != v] + [1])
    log_max = math.log10(max_c + 1)

    for i, u in enumerate(order):
        # Row/Col labels
        d.text((x0 - 38, y0 + i * cell + 8), u, fill=(20, 20, 20))
        d.text((x0 + i * cell + 4, y0 - 18), u, fill=(20, 20, 20))
        for j, v in enumerate(order):
            cx0 = x0 + j * cell
            cy0 = y0 + i * cell
            cx1 = cx0 + cell
            cy1 = cy0 + cell
            if i == j:
                d.rectangle([cx0, cy0, cx1, cy1], fill=(220, 220, 220), outline=(190, 190, 190))
                continue
            c = pair_map.get((u, v), 0)
            intensity = math.log10(c + 1) / log_max if c > 0 else 0.0
            if i < j:
                # Forward transition (above diagonal) -> blue/teal scale
                r = int(245 - 205 * intensity)
                g = int(248 - 130 * intensity)
                b = int(252 - 35 * intensity)
            else:
                # Feedback violation (below diagonal) -> red/amber scale
                r = int(252 - 20 * intensity)
                g = int(245 - 195 * intensity)
                b = int(242 - 195 * intensity)
            d.rectangle([cx0, cy0, cx1, cy1], fill=(r, g, b), outline=(215, 215, 215))
            if c >= 100:
                txt = f"{c // 1000}k" if c >= 1000 else str(c)
                fg = (255, 255, 255) if intensity > 0.65 else (30, 30, 30)
                d.text((cx0 + 3, cy0 + 9), txt, fill=fg)

    d.rectangle([x0, y0, x0 + grid_size, y0 + grid_size], outline=(30, 30, 30), width=2)
    d.line([(x0, y0), (x0 + grid_size, y0 + grid_size)], fill=(40, 40, 40), width=2)
    d.text((x0, y0 + grid_size + 12), "Blue (Upper Triangle) = Forward DAG Transitions (u precedes v in optimal slot order)", fill=(20, 80, 160))
    d.text((x0, y0 + grid_size + 30), "Red (Lower Triangle)  = Feedback Arc Violations (dominated by boundary-ambivalent o, d, y, e, a)", fill=(180, 30, 30))

    # Right Top Panel: Bar chart comparing FAS violation rates across corpora
    rx0, ry0, rx1, ry1 = 830, 110, 1550, 440
    d.rectangle([rx0, ry0, rx1, ry1], fill=(255, 255, 255), outline=(80, 80, 80))
    d.text((rx0 + 12, ry0 - 26), "Feedback Arc Set (FAS %) Violation Rate: Voynich vs. Natural Languages & Nulls (Adjacent Bigrams)", fill=(20, 20, 20))

    bars = [
        ("Voynich Lang B (units, tok)", res_t1['eva_units']['lang_B_tokens']['adjacent']['fas_pct'], (35, 110, 185)),
        ("Voynich ALL (units, tok)", res_t1['eva_units']['ALL_tokens']['adjacent']['fas_pct'], (45, 125, 200)),
        ("Voynich Line-Interior (units)", res_t1['eva_units']['line_interior_tokens']['adjacent']['fas_pct'], (60, 140, 210)),
        ("Voynich Lang A (units, tok)", res_t1['eva_units']['lang_A_tokens']['adjacent']['fas_pct'], (75, 155, 220)),
        ("Voynich Unique Types (units)", res_t1['eva_units']['ALL_types']['adjacent']['fas_pct'], (95, 165, 225)),
        ("Voynich Raw EVA Chars (tok)", res_t1['eva_chars']['ALL_tokens']['adjacent']['fas_pct'], (70, 130, 170)),
        ("Voynich GC v101 (tok)", res_t1['gc_v101']['ALL_tokens']['adjacent']['fas_pct'], (80, 150, 140)),
        ("English Culpeper (chars, tok)", res_t1['controls']['culpeper_herbal_en_tokens']['adjacent']['fas_pct'], (215, 120, 45)),
        ("Latin Caesar BG (chars, tok)", res_t1['controls']['caesar_bg_la_tokens']['adjacent']['fas_pct'], (205, 85, 55)),
        ("Shuffled Within-Word Null", res_t1['eva_units']['ALL_tokens']['adjacent']['null_within_word_shuffle_optimized_fas_mean'] * 100.0, (140, 140, 140)),
    ]
    max_bar_val = 50.0
    bh = (ry1 - ry0 - 30) / len(bars)
    for idx, (lbl, val, col) in enumerate(bars):
        by0 = ry0 + 15 + idx * bh
        by1 = by0 + bh - 6
        bw_px = (val / max_bar_val) * (rx1 - rx0 - 250)
        d.rectangle([rx0 + 205, by0, rx0 + 205 + bw_px, by1], fill=col, outline=(40, 40, 40))
        d.text((rx0 + 10, by0 + 4), lbl, fill=(20, 20, 20))
        d.text((rx0 + 212 + bw_px, by0 + 4), f"{val:.2f}%", fill=(20, 20, 20))

    # Right Bottom Panel: Positional Allograph Splitting Curve
    bx0, by0, bx1, by1 = 830, 510, 1550, 815
    d.rectangle([bx0, by0, bx1, by1], fill=(255, 255, 255), outline=(80, 80, 80))
    d.text((bx0 + 12, by0 - 26), "Positional Allograph Splitting (Word-Initial g^ / Word-Final g$ vs. Medial g): FASCollapse", fill=(20, 20, 20))

    stages = res_t1['positional_allograph_splitting']
    n_st = len(stages)
    ymax = max(s['any_distance_fas_pct'] for s in stages) * 1.15
    px = lambda i: bx0 + 60 + i * (bx1 - bx0 - 100) / (n_st - 1)
    py = lambda v: by1 - 45 - (v / ymax) * (by1 - by0 - 75)

    # Grid lines
    for gv in (0, 2, 4, 6, 8, 10, 12, 14):
        if gv <= ymax:
            gy = py(gv)
            d.line([(bx0 + 50, gy), (bx1 - 20, gy)], fill=(230, 230, 230))
            d.text((bx0 + 15, gy - 6), f"{gv}%", fill=(80, 80, 80))

    pts_adj = [(px(i), py(s['adjacent_fas_pct'])) for i, s in enumerate(stages)]
    pts_any = [(px(i), py(s['any_distance_fas_pct'])) for i, s in enumerate(stages)]
    d.line(pts_adj, fill=(30, 100, 200), width=3)
    d.line(pts_any, fill=(200, 60, 40), width=3)

    short_labels = ["Unsplit", "+split o", "+split d", "+split y", "+split s", "+split r,l", "+split a,e"]
    for i, s in enumerate(stages):
        x, ya, yd = px(i), py(s['adjacent_fas_pct']), py(s['any_distance_fas_pct'])
        d.ellipse([x - 5, ya - 5, x + 5, ya + 5], fill=(30, 100, 200))
        d.ellipse([x - 5, yd - 5, x + 5, yd + 5], fill=(200, 60, 40))
        d.text((x - 16, ya - 18), f"{s['adjacent_fas_pct']:.1f}%", fill=(20, 70, 160))
        d.text((x - 16, yd + 8), f"{s['any_distance_fas_pct']:.1f}%", fill=(170, 40, 20))
        d.text((x - 24, by1 - 30), short_labels[i], fill=(20, 20, 20))

    d.text((bx0 + 65, by0 + 12), "Blue = Adjacent Bigram FAS %   |   Red = Any-Distance Precedence FAS %", fill=(30, 30, 30))

    img.save(out_path)
    return out_path


def plot_entropy_and_length(res_t2: Dict, res_t3: Dict, out_path: str):
    from PIL import Image, ImageDraw

    W, H = 1600, 860
    img = Image.new('RGB', (W, H), (252, 251, 247))
    d = ImageDraw.Draw(img)

    d.rectangle([0, 0, W, 58], fill=(28, 37, 54))
    d.text((24, 12), "ATTACK 242 (T2 & T3): DIRECTIONAL ENTROPY ASYMMETRY & 3-SLOT WORD-LENGTH CONCENTRATION", fill=(255, 255, 255))
    d.text((24, 34), "Left: Start-Aligned vs End-Aligned Conditional Entropy | Center: L=5 Slot Profile | Right: Word-Length Binomiality & 3-Slot Decomposition", fill=(200, 215, 235))

    # Panel 1 (Top Left): Start-aligned (+1..+6) vs End-aligned (-1..-6) Markov-1 conditional entropy
    x0, y0, x1, y1 = 65, 105, 760, 430
    d.rectangle([x0, y0, x1, y1], fill=(255, 255, 255), outline=(80, 80, 80))
    d.text((x0 + 10, y0 - 24), "T2A: Boundary-Aligned Conditional Entropy (Step k from Start vs Step k from End, EVA Chars)", fill=(20, 20, 20))

    al_v = res_t2['eva_chars']['ALL_tokens']['boundary_aligned']
    al_la = res_t2['controls']['caesar_bg_la_tokens']['boundary_aligned']
    depths = al_v['depths']
    ymax = 4.5
    px = lambda i: x0 + 55 + i * (x1 - x0 - 95) / (len(depths) - 1)
    py = lambda v: y1 - 40 - (v / ymax) * (y1 - y0 - 65)

    for gv in (1.0, 2.0, 3.0, 4.0):
        gy = py(gv)
        d.line([(x0 + 45, gy), (x1 - 20, gy)], fill=(230, 230, 230))
        d.text((x0 + 12, gy - 6), f"{gv:.1f}b", fill=(80, 80, 80))

    s_fwd = [(px(i), py(v)) for i, v in enumerate(al_v['start_aligned_markov1_fwd_H_mm'])]
    e_bwd = [(px(i), py(v)) for i, v in enumerate(al_v['end_aligned_markov1_bwd_H_mm'])]
    la_fwd = [(px(i), py(v)) for i, v in enumerate(al_la['start_aligned_markov1_fwd_H_mm'])]
    la_bwd = [(px(i), py(v)) for i, v in enumerate(al_la['end_aligned_markov1_bwd_H_mm'])]

    d.line(s_fwd, fill=(25, 105, 195), width=3)
    d.line(e_bwd, fill=(210, 50, 40), width=3)
    d.line(la_fwd, fill=(100, 165, 220), width=2)
    d.line(la_bwd, fill=(230, 140, 120), width=2)

    for i, k in enumerate(depths):
        d.ellipse([s_fwd[i][0] - 4, s_fwd[i][1] - 4, s_fwd[i][0] + 4, s_fwd[i][1] + 4], fill=(25, 105, 195))
        d.ellipse([e_bwd[i][0] - 4, e_bwd[i][1] - 4, e_bwd[i][0] + 4, e_bwd[i][1] + 4], fill=(210, 50, 40))
        d.text((px(i) - 12, y1 - 26), f"k={k}", fill=(20, 20, 20))
        d.text((s_fwd[i][0] - 14, s_fwd[i][1] - 18), f"{al_v['start_aligned_markov1_fwd_H_mm'][i]:.2f}", fill=(20, 80, 160))
        d.text((e_bwd[i][0] - 14, e_bwd[i][1] + 7), f"{al_v['end_aligned_markov1_bwd_H_mm'][i]:.2f}", fill=(180, 35, 25))

    d.text((x0 + 55, y0 + 10), "Dark Blue = Voynich Forward H(g_k | g_{k-1}) from Start (+k)", fill=(25, 105, 195))
    d.text((x0 + 55, y0 + 26), "Dark Red  = Voynich Backward H(g_{-k} | g_{-k+1}) from End (-k)", fill=(210, 50, 40))
    d.text((x0 + 55, y0 + 42), "Light Blue/Red = Latin De Bello Gallico Forward / Backward Controls", fill=(110, 110, 110))

    # Panel 2 (Bottom Left): Fixed Length L=5 and L=6 Full-Chain vs Markov-1 Entropy Profile
    bx0, by0, bx1, by1 = 65, 495, 760, 815
    d.rectangle([bx0, by0, bx1, by1], fill=(255, 255, 255), outline=(80, 80, 80))
    d.text((bx0 + 10, by0 - 24), "T2B: Fixed Length L=5 (EVA Chars, n=9,899) Internal Slot Entropy Trajectory (Slots 1..5)", fill=(20, 20, 20))

    l5 = res_t2['eva_chars']['ALL_tokens']['fixed_lengths']['5']
    px5 = lambda i: bx0 + 70 + i * (bx1 - bx0 - 130) / 4
    py5 = lambda v: by1 - 40 - (v / 3.8) * (by1 - by0 - 65)

    for gv in (1.0, 2.0, 3.0):
        gy = py5(gv)
        d.line([(bx0 + 50, gy), (bx1 - 20, gy)], fill=(230, 230, 230))
        d.text((bx0 + 12, gy - 6), f"{gv:.1f}b", fill=(80, 80, 80))

    u5 = [(px5(i), py5(v)) for i, v in enumerate(l5['unconditional_slot_H_mm'])]
    cf5 = [(px5(i), py5(v)) for i, v in enumerate(l5['chain_forward_H_mm_by_slot'])]
    cb5 = [(px5(i), py5(v)) for i, v in enumerate(l5['chain_backward_H_mm_by_slot'])]

    d.line(u5, fill=(90, 90, 90), width=2)
    d.line(cf5, fill=(25, 105, 195), width=3)
    d.line(cb5, fill=(210, 50, 40), width=3)

    for i in range(5):
        d.ellipse([cf5[i][0] - 4, cf5[i][1] - 4, cf5[i][0] + 4, cf5[i][1] + 4], fill=(25, 105, 195))
        d.ellipse([cb5[i][0] - 4, cb5[i][1] - 4, cb5[i][0] + 4, cb5[i][1] + 4], fill=(210, 50, 40))
        d.text((px5(i) - 18, by1 - 26), f"Slot {i+1}", fill=(20, 20, 20))
        d.text((cf5[i][0] - 14, cf5[i][1] - 18), f"{l5['chain_forward_H_mm_by_slot'][i]:.2f}", fill=(20, 80, 160))
        d.text((cb5[i][0] - 14, cb5[i][1] + 7), f"{l5['chain_backward_H_mm_by_slot'][i]:.2f}", fill=(180, 35, 25))

    d.text((bx0 + 60, by0 + 10), "Gray = Unconditional H(g_k) | Blue = Chain Fwd H(g_k | g_1..k-1) | Red = Chain Bwd H(g_k | g_k+1..5)", fill=(40, 40, 40))
    d.text((bx0 + 60, by0 + 28), "Note: Slot 2-3 (Core/Gallows) is the lexical information bottleneck; Slot 5 (Coda) is highly constrained", fill=(60, 60, 60))

    # Panel 3 (Top Right): Word-Length Distribution & Sub-Poissonian Fano Factor
    rx0, ry0, rx1, ry1 = 825, 105, 1550, 430
    d.rectangle([rx0, ry0, rx1, ry1], fill=(255, 255, 255), outline=(80, 80, 80))
    vt = res_t3['eva_chars']['ALL_tokens']
    lt = res_t3['controls']['caesar_bg_la_tokens']
    et = res_t3['controls']['culpeper_herbal_en_tokens']
    d.text((rx0 + 10, ry0 - 24), f"T3A: Word-Length Concentration (EVA Chars): Voynich (Fano D={vt['fano_dispersion_var_over_mean']:.2f}) vs. Latin (D={lt['fano_dispersion_var_over_mean']:.2f}) & English (D={et['fano_dispersion_var_over_mean']:.2f})", fill=(20, 20, 20))

    vh = vt['histogram_pct']
    lh = lt['histogram_pct']
    eh = et['histogram_pct']

    max_pct = 38.0
    bw = (rx1 - rx0 - 80) / 12
    for k_len in range(1, 13):
        vp = vh.get(str(k_len), 0.0)
        lp_v = lh.get(str(k_len), 0.0)
        ep_v = eh.get(str(k_len), 0.0)
        cx = rx0 + 50 + (k_len - 1) * bw
        # 3 grouped bars per length k_len
        h_v = (vp / max_pct) * (ry1 - ry0 - 65)
        h_l = (lp_v / max_pct) * (ry1 - ry0 - 65)
        h_e = (ep_v / max_pct) * (ry1 - ry0 - 65)
        d.rectangle([cx + 2, ry1 - 35 - h_v, cx + bw * 0.34, ry1 - 35], fill=(35, 110, 195))
        d.rectangle([cx + bw * 0.35, ry1 - 35 - h_l, cx + bw * 0.66, ry1 - 35], fill=(210, 80, 50))
        d.rectangle([cx + bw * 0.67, ry1 - 35 - h_e, cx + bw * 0.96, ry1 - 35], fill=(230, 165, 50))
        d.text((cx + bw * 0.25, ry1 - 26), str(k_len), fill=(20, 20, 20))

    d.text((rx0 + 55, ry0 + 12), f"Blue = Voynich Chars (mean={vt['mean']:.2f}, var={vt['variance']:.2f}, Fano D={vt['fano_dispersion_var_over_mean']:.2f}, Bin TVD={vt['best_binomial_fit']['tvd']:.3f})", fill=(35, 110, 195))
    d.text((rx0 + 55, ry0 + 30), f"Red  = Latin Caesar BG (mean={lt['mean']:.2f}, var={lt['variance']:.2f}, Fano D={lt['fano_dispersion_var_over_mean']:.2f})", fill=(210, 80, 50))
    d.text((rx0 + 55, ry0 + 48), f"Gold = English Culpeper (mean={et['mean']:.2f}, var={et['variance']:.2f}, Fano D={et['fano_dispersion_var_over_mean']:.2f})", fill=(180, 120, 20))

    # Panel 4 (Bottom Right): 3-Slot Morphological Decomposition (Prefix + Core + Suffix)
    sx0, sy0, sx1, sy1 = 825, 495, 1550, 815
    d.rectangle([sx0, sy0, sx1, sy1], fill=(255, 255, 255), outline=(80, 80, 80))
    slot_u = res_t3['slot_decomposition']['ALL_tokens']['units']
    vu = res_t3['eva_units']['ALL_tokens']
    d.text((sx0 + 10, sy0 - 24), f"T3B: Why Variance Is So Low: Stripping Prefix & Suffix Leaves a 1-2 Unit Core Root ({slot_u['core_length_1_or_2_units_pct']:.1f}% of Corpus!)", fill=(20, 20, 20))

    chist = slot_u['core_length_hist_pct']
    tot_uhist = vu['histogram_pct']

    bw2 = (sx1 - sx0 - 100) / 8
    for k_u in range(1, 9):
        tu = tot_uhist.get(str(k_u), 0.0)
        cu = chist.get(str(k_u), 0.0)
        cx = sx0 + 60 + (k_u - 1) * bw2
        h_tu = (tu / 72.0) * (sy1 - sy0 - 80)
        h_cu = (cu / 72.0) * (sy1 - sy0 - 80)
        d.rectangle([cx + 4, sy1 - 35 - h_tu, cx + bw2 * 0.46, sy1 - 35], fill=(160, 185, 225), outline=(80, 100, 140))
        d.rectangle([cx + bw2 * 0.48, sy1 - 35 - h_cu, cx + bw2 * 0.90, sy1 - 35], fill=(30, 140, 95), outline=(20, 90, 60))
        d.text((cx + bw2 * 0.30, sy1 - 26), f"{k_u}u", fill=(20, 20, 20))
        if cu >= 3.0:
            d.text((cx + bw2 * 0.48, sy1 - 50 - h_cu), f"{cu:.1f}%", fill=(20, 110, 70))

    d.text((sx0 + 60, sy0 + 12), f"Light Blue = Full Word Length in EVA Units (mean={vu['mean']:.2f}u, var={vu['variance']:.2f}, Fano D={vu['fano_dispersion_var_over_mean']:.2f})", fill=(70, 95, 145))
    d.text((sx0 + 60, sy0 + 30), f"Green      = Stripped Core Root Length in EVA Units (mean={slot_u['core_mean']}u, var={slot_u['core_var']}, 1-2u = {slot_u['core_length_1_or_2_units_pct']}%)", fill=(20, 115, 75))
    d.text((sx0 + 60, sy0 + 48), f"Slot Variances: Var(Pref)={slot_u['prefix_var']} + Var(Core)={slot_u['core_var']} + Var(Suff)={slot_u['suffix_var']}", fill=(50, 50, 50))

    img.save(out_path)
    return out_path


def render_scribe3_vellum_crops():
    """Render high-res crops of f58r (Scribe 3, Currier A) and f103r (Scribe 3, Currier B)
    and build a side-by-side annotated forensic panel.
    """
    from PIL import Image, ImageDraw

    f58r_crop = os.path.join(ROOT, 'pages', 'w242_f58r_scribe3_langA_crop.png')
    f103r_crop = os.path.join(ROOT, 'pages', 'w242_f103r_scribe3_langB_crop.png')
    panel_out = os.path.join(ROOT, 'pages', 'w242_scribe3_langA_vs_langB_vellum.png')

    subprocess.run([
        sys.executable, os.path.join(ROOT, 'tools', 'render_folio.py'),
        'f58r', '--crop', '0.05', '0.06', '0.88', '0.42', '--enhance', '--out', f58r_crop
    ], check=True)
    subprocess.run([
        sys.executable, os.path.join(ROOT, 'tools', 'render_folio.py'),
        'f103r', '--crop', '0.05', '0.06', '0.88', '0.42', '--enhance', '--out', f103r_crop
    ], check=True)

    im_a = Image.open(f58r_crop).convert('RGB')
    im_b = Image.open(f103r_crop).convert('RGB')

    target_w = 760
    ha = int(im_a.height * (target_w / im_a.width))
    hb = int(im_b.height * (target_w / im_b.width))
    im_a = im_a.resize((target_w, ha), Image.Resampling.LANCZOS)
    im_b = im_b.resize((target_w, hb), Image.Resampling.LANCZOS)

    H = max(ha, hb) + 175
    W = target_w * 2 + 60
    canvas = Image.new('RGB', (W, H), (248, 246, 240))
    d = ImageDraw.Draw(canvas)

    d.rectangle([0, 0, W, 62], fill=(28, 37, 54))
    d.text((20, 12), "ATTACK 242 (T4 & T5): WITHIN-SCRIBE 3 ($H=3, $I=S) MORPHOLOGICAL SHIFT ON HIGH-RES VELLUM", fill=(255, 255, 255))
    d.text((20, 35), "Same Scribe Hand ($H=3) & Same Starred Layout ($I=S), Opposite Currier Languages: f58r ($L=A) vs. f103r ($L=B)", fill=(200, 215, 235))

    # Paste left (f58r) and right (f103r)
    canvas.paste(im_a, (20, 95))
    canvas.paste(im_b, (target_w + 40, 95))
    d.rectangle([20, 95, 20 + target_w, 95 + ha], outline=(40, 90, 170), width=3)
    d.rectangle([target_w + 40, 95, target_w + 40 + target_w, 95 + hb], outline=(190, 50, 40), width=3)

    d.text((24, 72), "LEFT: f58r (Quire 8, $H=3, $L=A, $I=S) -- Zero-Grade / -ol,-or,-aiin Paradigm", fill=(25, 70, 150))
    d.text((target_w + 44, 72), "RIGHT: f103r (Quire 20, $H=3, $L=B, $I=S) -- e-Grade / qo- + -edy,-dy Paradigm", fill=(170, 35, 25))

    by = max(ha, hb) + 108
    d.text((24, by), "f58r.1-3 ($L=A): kor.shol.shor.qokor.okeol.chor.oky.daiin / dchor.chol.shol.cthol.shtol", fill=(25, 70, 150))
    d.text((24, by + 20), "H=3 Lang A Stats: e-grade vowel = 14.3%, -edy/-dy/-ey = 7.4%, -ol/-or/-al/-ar = 32.1%, qo- = 12.6%", fill=(40, 40, 40))

    d.text((target_w + 44, by), "f103r.1-3 ($L=B): pchedy.shedy.qokeey.qokeedy.qokedy / ychedy.qokain.chedy.qokeedy", fill=(170, 35, 25))
    d.text((target_w + 44, by + 20), "H=3 Lang B Stats: e-grade vowel = 48.9%, -edy/-dy/-ey = 43.1%, -ol/-or/-al/-ar = 15.8%, qo- = 22.9%", fill=(40, 40, 40))

    canvas.save(panel_out)
    return [f58r_crop, f103r_crop, panel_out]


# ---------------------------------------------------------------------------
# Main Runner
# ---------------------------------------------------------------------------
def main():
    rng = random.Random(SEED)
    print("=== Attack 242: Intra-Word Slot Automaton & DAG Grammar ===")

    lines_zl = load_lines()
    p_lines_zl = [l for l in lines_zl if l.unit == 'P']
    l_lines_zl = [l for l in lines_zl if l.unit == 'L']

    lines_gc = load_lines(os.path.join(DATA, 'GC2a-n.txt'))
    p_lines_gc = [l for l in lines_gc if l.unit == 'P']

    # Build token lists stratified by language, line position, hand
    all_words_zl = [w for l in p_lines_zl for w in l.clean_words]
    interior_words_zl = [
        w for l in p_lines_zl if l.unit_sub != 't' and len(l.clean_words) >= 3
        for w in l.clean_words[1:-1]
    ]
    langA_words_zl = [w for l in p_lines_zl if l.lang == 'A' for w in l.clean_words]
    langB_words_zl = [w for l in p_lines_zl if l.lang == 'B' for w in l.clean_words]
    langA_int_zl = [
        w for l in p_lines_zl if l.lang == 'A' and l.unit_sub != 't' and len(l.clean_words) >= 3
        for w in l.clean_words[1:-1]
    ]
    langB_int_zl = [
        w for l in p_lines_zl if l.lang == 'B' and l.unit_sub != 't' and len(l.clean_words) >= 3
        for w in l.clean_words[1:-1]
    ]
    all_words_gc = [
        w for l in p_lines_gc for w in l.clean_words
        if all(c.isalnum() for c in w) and len(w) >= 1
    ]

    ctrl_la = fetch_control_words('caesar_bg_la', max_tokens=35000)
    ctrl_en = fetch_control_words('culpeper_herbal_en', max_tokens=35000)
    print(f"Loaded ZL3b P-words={len(all_words_zl)}, GC2a={len(all_words_gc)}, Latin={len(ctrl_la)}, English={len(ctrl_en)}")

    # -----------------------------------------------------------------------
    # T1: Intra-Word Precedence DAG & FAS Unidirectionality
    # -----------------------------------------------------------------------
    print("Running T1: Intra-Word Precedence DAG & FAS Optimization...")

    def run_dag_bucket(words_list: Sequence[str], mode: str, compute_nulls: bool = False) -> Tuple[Dict, Dict]:
        tok_counter = Counter(words_list)
        unique_words = list(tok_counter.keys())
        tok_weights = [tok_counter[w] for w in unique_words]
        seqs = [tokenize_word(w, mode) for w in unique_words]
        tok_res = analyze_dag(seqs, rng, weights=tok_weights, compute_nulls=compute_nulls, n_null=30)
        typ_res = analyze_dag(seqs, rng, weights=[1] * len(seqs), compute_nulls=False)
        return tok_res, typ_res

    t1_chars_all_tok, t1_chars_all_typ = run_dag_bucket(all_words_zl, 'eva_chars', compute_nulls=True)
    t1_chars_int_tok, _ = run_dag_bucket(interior_words_zl, 'eva_chars')
    t1_chars_A_tok, t1_chars_A_typ = run_dag_bucket(langA_words_zl, 'eva_chars')
    t1_chars_B_tok, t1_chars_B_typ = run_dag_bucket(langB_words_zl, 'eva_chars')

    t1_units_all_tok, t1_units_all_typ = run_dag_bucket(all_words_zl, 'eva_units', compute_nulls=True)
    t1_units_int_tok, _ = run_dag_bucket(interior_words_zl, 'eva_units')
    t1_units_A_tok, t1_units_A_typ = run_dag_bucket(langA_words_zl, 'eva_units')
    t1_units_B_tok, t1_units_B_typ = run_dag_bucket(langB_words_zl, 'eva_units')
    t1_units_A_int, _ = run_dag_bucket(langA_int_zl, 'eva_units')
    t1_units_B_int, _ = run_dag_bucket(langB_int_zl, 'eva_units')

    t1_gc_all_tok, t1_gc_all_typ = run_dag_bucket(all_words_gc, 'gc_v101', compute_nulls=True)
    t1_la_tok, t1_la_typ = run_dag_bucket(ctrl_la, 'eva_chars', compute_nulls=True)
    t1_en_tok, t1_en_typ = run_dag_bucket(ctrl_en, 'eva_chars', compute_nulls=True)

    # Positional allograph splitting on eva_units
    all_unit_seqs = [tokenize_word(w, 'eva_units') for w in all_words_zl]
    allograph_split_res = positional_allograph_split_experiment(all_unit_seqs, rng)

    # Raw adjacent pair map for heatmap plotting
    adj_u_map, _, _ = build_precedence_matrices(all_unit_seqs)

    res_t1 = {
        'eva_chars': {
            'ALL_tokens': t1_chars_all_tok,
            'ALL_types': t1_chars_all_typ,
            'line_interior_tokens': t1_chars_int_tok,
            'lang_A_tokens': t1_chars_A_tok,
            'lang_A_types': t1_chars_A_typ,
            'lang_B_tokens': t1_chars_B_tok,
            'lang_B_types': t1_chars_B_typ,
        },
        'eva_units': {
            'ALL_tokens': t1_units_all_tok,
            'ALL_types': t1_units_all_typ,
            'line_interior_tokens': t1_units_int_tok,
            'lang_A_tokens': t1_units_A_tok,
            'lang_A_types': t1_units_A_typ,
            'lang_B_tokens': t1_units_B_tok,
            'lang_B_types': t1_units_B_typ,
            'lang_A_interior_tokens': t1_units_A_int,
            'lang_B_interior_tokens': t1_units_B_int,
        },
        'gc_v101': {
            'ALL_tokens': t1_gc_all_tok,
            'ALL_types': t1_gc_all_typ,
        },
        'controls': {
            'caesar_bg_la_tokens': t1_la_tok,
            'caesar_bg_la_types': t1_la_typ,
            'culpeper_herbal_en_tokens': t1_en_tok,
            'culpeper_herbal_en_types': t1_en_typ,
        },
        'positional_allograph_splitting': allograph_split_res,
        '_raw_adj_eva_units_map': adj_u_map,
    }

    print(
        f"  T1 Summary (Adjacent FAS %): EVA Units ALL={t1_units_all_tok['adjacent']['fas_pct']}%, "
        f"LangA={t1_units_A_tok['adjacent']['fas_pct']}%, LangB={t1_units_B_tok['adjacent']['fas_pct']}%, "
        f"Types={t1_units_all_typ['adjacent']['fas_pct']}%, EVA Chars={t1_chars_all_tok['adjacent']['fas_pct']}%, "
        f"GC v101={t1_gc_all_tok['adjacent']['fas_pct']}%, Latin={t1_la_tok['adjacent']['fas_pct']}%, "
        f"English={t1_en_tok['adjacent']['fas_pct']}%"
    )

    # -----------------------------------------------------------------------
    # T2: Left-to-Right vs. Right-to-Left Positional Entropy Profile
    # -----------------------------------------------------------------------
    print("Running T2: Left-to-Right vs. Right-to-Left Positional Entropy Profile...")

    def build_entropy_suite(words_list: Sequence[str], mode: str) -> Dict:
        seqs = [tokenize_word(w, mode) for w in words_list]
        fixed = {str(L): entropy_profile_fixed_length(seqs, L) for L in (4, 5, 6, 7)}
        aligned = aligned_boundary_entropy_profile(seqs, max_depth=6)
        return {'fixed_lengths': fixed, 'boundary_aligned': aligned}

    unique_words_zl = sorted(set(all_words_zl))
    res_t2 = {
        'eva_chars': {
            'ALL_tokens': build_entropy_suite(all_words_zl, 'eva_chars'),
            'ALL_types': build_entropy_suite(unique_words_zl, 'eva_chars'),
            'lang_A_tokens': build_entropy_suite(langA_words_zl, 'eva_chars'),
            'lang_B_tokens': build_entropy_suite(langB_words_zl, 'eva_chars'),
        },
        'eva_units': {
            'ALL_tokens': build_entropy_suite(all_words_zl, 'eva_units'),
            'ALL_types': build_entropy_suite(unique_words_zl, 'eva_units'),
            'lang_A_tokens': build_entropy_suite(langA_words_zl, 'eva_units'),
            'lang_B_tokens': build_entropy_suite(langB_words_zl, 'eva_units'),
        },
        'controls': {
            'caesar_bg_la_tokens': build_entropy_suite(ctrl_la, 'eva_chars'),
            'caesar_bg_la_types': build_entropy_suite(sorted(set(ctrl_la)), 'eva_chars'),
            'culpeper_herbal_en_tokens': build_entropy_suite(ctrl_en, 'eva_chars'),
            'culpeper_herbal_en_types': build_entropy_suite(sorted(set(ctrl_en)), 'eva_chars'),
        },
    }

    # -----------------------------------------------------------------------
    # T3: Word-Length Binomiality, Variance & 3-Slot Decomposition
    # -----------------------------------------------------------------------
    print("Running T3: Word-Length Binomiality & 3-Slot Decomposition...")

    line_start_words = [l.clean_words[0] for l in p_lines_zl if l.unit_sub != 't' and len(l.clean_words) >= 2]
    line_end_words = [l.clean_words[-1] for l in p_lines_zl if l.unit_sub != 't' and len(l.clean_words) >= 2]
    label_words = [w for l in l_lines_zl for w in l.clean_words]

    res_t3 = {
        'eva_chars': {
            'ALL_tokens': length_distribution_stats([len(w) for w in all_words_zl]),
            'ALL_types': length_distribution_stats([len(w) for w in unique_words_zl]),
            'lang_A_tokens': length_distribution_stats([len(w) for w in langA_words_zl]),
            'lang_B_tokens': length_distribution_stats([len(w) for w in langB_words_zl]),
            'line_start_tokens': length_distribution_stats([len(w) for w in line_start_words]),
            'line_mid_tokens': length_distribution_stats([len(w) for w in interior_words_zl]),
            'line_end_tokens': length_distribution_stats([len(w) for w in line_end_words]),
            'figure_labels_tokens': length_distribution_stats([len(w) for w in label_words]),
            'by_hand': {
                f'H={h}': length_distribution_stats([len(w) for l in p_lines_zl if l.hand == h for w in l.clean_words])
                for h in ('1', '2', '3', '4', '5')
            },
        },
        'eva_units': {
            'ALL_tokens': length_distribution_stats([len(tokenize_word(w, 'eva_units')) for w in all_words_zl]),
            'ALL_types': length_distribution_stats([len(tokenize_word(w, 'eva_units')) for w in unique_words_zl]),
            'lang_A_tokens': length_distribution_stats([len(tokenize_word(w, 'eva_units')) for w in langA_words_zl]),
            'lang_B_tokens': length_distribution_stats([len(tokenize_word(w, 'eva_units')) for w in langB_words_zl]),
            'line_start_tokens': length_distribution_stats([len(tokenize_word(w, 'eva_units')) for w in line_start_words]),
            'line_mid_tokens': length_distribution_stats([len(tokenize_word(w, 'eva_units')) for w in interior_words_zl]),
            'line_end_tokens': length_distribution_stats([len(tokenize_word(w, 'eva_units')) for w in line_end_words]),
            'figure_labels_tokens': length_distribution_stats([len(tokenize_word(w, 'eva_units')) for w in label_words]),
        },
        'controls': {
            'caesar_bg_la_tokens': length_distribution_stats([len(w) for w in ctrl_la]),
            'caesar_bg_la_types': length_distribution_stats([len(w) for w in set(ctrl_la)]),
            'culpeper_herbal_en_tokens': length_distribution_stats([len(w) for w in ctrl_en]),
            'culpeper_herbal_en_types': length_distribution_stats([len(w) for w in set(ctrl_en)]),
        },
        'slot_decomposition': {
            'ALL_tokens': analyze_slot_decomposition(all_words_zl),
            'ALL_types': analyze_slot_decomposition(unique_words_zl),
            'lang_A_tokens': analyze_slot_decomposition(langA_words_zl),
            'lang_B_tokens': analyze_slot_decomposition(langB_words_zl),
        },
    }

    # -----------------------------------------------------------------------
    # T4: Currier A vs. B & Within-Scribe 3 Paradigm Shift
    # -----------------------------------------------------------------------
    print("Running T4: Currier A vs. B & Within-Scribe 3 Paradigm Shift...")
    res_t4 = analyze_currier_ab_and_scribe3(lines_zl)

    # -----------------------------------------------------------------------
    # T5: Visual Plots & High-Res Scan Crops
    # -----------------------------------------------------------------------
    print("Running T5: Rendering Diagnostic Plots & High-Res Scan Crops...")
    os.makedirs(os.path.join(ROOT, 'pages'), exist_ok=True)
    p_dag = plot_dag_matrix(res_t1, os.path.join(ROOT, 'pages', 'w242_dag_matrix.png'))
    p_ent = plot_entropy_and_length(res_t2, res_t3, os.path.join(ROOT, 'pages', 'w242_entropy_and_length.png'))
    vellum_paths = render_scribe3_vellum_crops()

    # Remove transient map before JSON serialization
    res_t1.pop('_raw_adj_eva_units_map', None)

    out_json = {
        'attack': 242,
        'title': 'Intra-Word Slot Automaton, DAG Unidirectionality, Directionality Asymmetry, and Currier A/B Stem-Shift Analysis',
        'seed': SEED,
        'T1_intraword_dag_and_fas': res_t1,
        'T2_directional_entropy_profile': res_t2,
        'T3_word_length_binomiality_and_slots': res_t3,
        'T4_currier_ab_and_scribe3_shift': res_t4,
        'T5_visual_artifacts': [
            'pages/w242_dag_matrix.png',
            'pages/w242_entropy_and_length.png',
            'pages/w242_f58r_scribe3_langA_crop.png',
            'pages/w242_f103r_scribe3_langB_crop.png',
            'pages/w242_scribe3_langA_vs_langB_vellum.png',
        ],
    }

    out_path = os.path.join(DATA, 'attack242_intraword_slot_and_dag_grammar.json')
    with open(out_path, 'w', encoding='utf-8') as fh:
        json.dump(out_json, fh, indent=2, ensure_ascii=False)
    print(f"Saved {out_path}")


if __name__ == '__main__':
    main()
