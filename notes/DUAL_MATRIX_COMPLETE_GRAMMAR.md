# Complete Dual-Matrix Generative Grammar of the Voynich Manuscript (`99.56%` Coverage)

## 1. Executive Synthesis (`Attacks 55–60 / Discoveries 72–77`)

Across `36,229` canonical tokens (`8,510` unique word types) in [`data/ZL3b-n.txt`](../data/ZL3b-n.txt), the entire vocabulary of the Voynich Manuscript partitions into two orthogonal, complementary morphological matrices covering **`36,069 / 36,229` tokens (`99.56%`)**:

| Matrix Component | Structural Dimensions | Attested / Theoretical Cells | Token Count | Share of Corpus | Within-Class Coverage |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **Matrix I: Closed-Class Functional/Case Matrix** ([`Attack 55`](../tools/attack55_seven_series_closed_class_matrix.py)) | `7 Onsets × 8 Suffixes` | `55 / 56` (`98.2%`) | `8,601` | `23.74%` | `98.16%` (`8,540 / 8,700`) |
| **Matrix II: Open-Class Gallows/Bench Tensor** ([`Attack 57`](../tools/attack57_open_class_gallows_bench_matrix.py)) | `8 Prefixes × 6 Cores × 8 Suffixes` | `363 / 384` (`94.5%`) | `27,529` | `75.99%` | `100.00%` (`27,529 / 27,529`) |
| **Combined Dual-Matrix Grammar** ([`Attack 60`](../tools/attack60_dual_matrix_complete_generative_grammar.py)) | **`440` Total Cells (`56 + 384`)** | **`419 / 440` (`95.2%`)** | **`36,130`** | **`99.73%`** | **`99.56%` of entire book** |
| *Residual Unparsed Tokens* (single glyphs / damaged loci) | — | — | `99` | `0.27%` | — |

---

## 2. Information-Theoretic Decomposition ($H(\text{Word}) = 9.9516\text{ bits}$)

- **Total Unigram Word Entropy $H(\text{Word})$**: `10.7699 bits`
- **Entropy Explained by Dual-Matrix Cell Assignment $H(\text{Cell})$**: `7.3334 bits` (**`68.09%` of total word entropy!**)
- **Residual Surface Allography Entropy $H(\text{Word} \mid \text{Cell})$**: `3.4365 bits` (capturing moraic `-e-/-ee-` grading, `i/ii/iii` minim count, and top-line `p/f` allography).

---

## 3. Resolution of the Two Internal Core Contrasts (`Attacks 58 & 59`)

### 3.1 The Simplex Bench Contrast: `ch-` (Unplumed) vs. `sh-` (`s`-Plumed) ([`Attack 58`](../tools/attack58_ch_vs_sh_plume_contrast_solver.py))
1. **Strict Monotonic Vocalic `-e-/-ee-` Grading ($z = +9.69$)**:
   - **`0_NO_E` stems** (`chol, chor, char, chal, chdy, chaiin, chy`, $n = 3,754$): `SH_share = 29.65%` (`CH = 2,641`, `SH = 1,113`)
   - **`1_E` stems** (`chedy, chey, cheol, cheor, cheo, cheody`, $n = 3,561$): `SH_share = 38.73%` (`CH = 2,182`, `SH = 1,379`)
   - **`2_EE` stems** (`cheey, cheedy, cheeor, cheeol`, $n = 850$): `SH_share = 45.18%` (`CH = 466`, `SH = 384`, with `sheedy [74] > cheedy [55]`)
2. **Sibilant-Plume Line-Initial Homology ($z = +5.21$)**:
   - Morphographically, EVA `sh` is `ch` surmounted by an `s`-plume. Just as simplex `s-` (`saiin, sar, sal`) is the Continuation Line-Initial Series (`42.73%` line-initial vs. `17.62%` for `d-`, $z = +10.45$), `sh-` is **`3.45×` more line-initial** than `ch-` on bare `0_NO_E` stems (`11.50%` vs. `3.33%`) and **`2.03×` more line-initial** across all 15 matched pairs (`4.59%` vs. `2.26%`, suffix-stratified permutation $z = +5.21$).

### 3.2 The Gallows Contrast: `k/f` (Single-Loop) vs. `t/p` (Double-Loop) ([`Attack 59`](../tools/attack59_k_vs_t_gallows_contrast_solver.py))
1. **Monotonic Prefix Hierarchy ($I = 0.0509\text{ bits}, z = +322.37$)**:
   - **`L_APPL` (`l-/ol-/qol-`)**: `87.08% K` vs. `12.92% T` (`K:T = 6.74 : 1`, e.g. `lkaiin, lkedy, lkar`)
   - **`QO` (`qo-`)**: `71.04% K` vs. `28.96% T` (`K:T = 2.45 : 1`, e.g. `qokedy, qokaiin, qokar`)
   - **`S_SIB` (`s-`)**: `68.37% K` vs. `31.63% T` (`K:T = 2.16 : 1`)
   - **`D_DEIC` (`d-`)**: `62.50% K` vs. `37.50% T` (`K:T = 1.67 : 1`)
   - **`CH_BENCH_PRE` (`ckh-` vs. `cth-`)**: `60.21% K` vs. `39.79% T` (`K:T = 1.51 : 1`)
   - **`Y_CONJ` (`yk-` vs. `yt-`)**: `52.57% K` vs. `47.43% T` (`K:T = 1.11 : 1`)
   - **`O_VOW` (`ok-` vs. `ot-`)**: `47.91% K` vs. **`52.09% T`** (`K:T = 0.92 : 1` — flips to `T_CLASS` majority!)
   - **`ZERO` (`k/f-` vs. `t/p-`)**: `42.85% K` vs. **`57.15% T`** (`K:T = 0.75 : 1` — strong `T_CLASS` majority!)
2. **Diagram/Astrological Locus Shift ($z = +8.16$)**:
   - In continuous prose (`@P`), `K_CLASS` dominates (`58.09% K` vs. `41.91% T`, peaking in `$I=P` Pharmaceutical at `68.82% K` and `$I=B` Biological at `65.69% K`).
   - In Astrological Rings (`@C/@R`, `51.73% T`) and Diagram Labels (`@L`, `52.68% T`), `T_CLASS` flips to the majority (peaking in `$I=Z` Zodiac at **`57.72% T`** and `$I=C` Cosmological at **`51.39% T`**).

---

## 4. Top Cross-Matrix Syntactic Transitions ($z = +11.83$ Within-Line Permutation)

Across all `30,853` within-line adjacent word pairs, macro-state transitions between Matrix I (`7` Closed-Class series) and Matrix II (`6` Open-Class cores) carry `0.06377 bits` of mutual information vs. `0.02470 ± 0.00124 bits` under within-line word-order shuffling (**$z = +31.40$**):

| Rank | From Macro-State ($w_t$) | To Macro-State ($w_{t+1}$) | Observed Count | Expected Count | Syntactic Lift |
| :---: | :--- | :--- | :---: | :---: | :---: |
| 1 | `CLOSED_S_SIB` | `CLOSED_O_VOW` | `221` | `82.0` | **`2.70×`** |
| 2 | `CLOSED_R_PORT` | `CLOSED_O_VOW` | `64` | `24.3` | **`2.64×`** |
| 3 | `CLOSED_O_VOW` | `CLOSED_O_VOW` | `631` | `287.9` | **`2.19×`** |
| 4 | `OPEN_SH` | `CLOSED_QO_PRO` | `95` | `48.3` | **`1.97×`** |
| 5 | `OPEN_TCH_CTH` | `OPEN_TCH_CTH` | `399` | `208.7` | **`1.91×`** |
| 6 | `OPEN_T_P` | `OPEN_T_P` | `739` | `426.9` | **`1.73×`** |
| 7 | `OPEN_KCH_CKH` | `CLOSED_S_SIB` | `70` | `44.3` | **`1.58×`** |
| 8 | `CLOSED_D_DEIC` | `CLOSED_D_DEIC` | `218` | `144.2` | **`1.51×`** |
| 9 | `OPEN_KCH_CKH` | `OPEN_KCH_CKH` | `212` | `142.5` | **`1.49×`** |
| 10 | `CLOSED_S_SIB` | `OPEN_SH` | `110` | `75.0` | **`1.47×`** |
| 11 | `OPEN_CH` | `CLOSED_R_PORT` | `91` | `62.5` | **`1.46×`** |
| 12 | `CLOSED_L_APPL` | `OPEN_CH` | `62` | `43.9` | **`1.41×`** |
| 13 | `OPEN_CH` | `CLOSED_QO_PRO` | `126` | `90.2` | **`1.40×`** |
| 14 | `CLOSED_QO_PRO` | `OPEN_CH` | `132` | `94.7` | **`1.40×`** |
| 15 | `OPEN_TCH_CTH` | `OPEN_KCH_CKH` | `249` | `179.4` | **`1.39×`** |
