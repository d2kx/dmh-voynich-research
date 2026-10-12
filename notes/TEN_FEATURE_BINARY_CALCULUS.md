# The 10-Feature Orthogonal Binary Calculus of Voynich Morphology (`{0, 1}^{10}`)

## 1. Executive Synthesis (`Attack 68 / Discovery 85`)

Every word token in the Voynich Manuscript (`36,229` tokens) maps into a **10-bit binary feature vector $\mathbf{f}(w) \in \{0, 1\}^{10}$** built from the 10 grammatical and phonological oppositions solved in Attacks 53–67:

- **Theoretical Hypercube Size**: $2^{10} = 1,024$ states
- **Attested Hypercube States**: **`231 / 1,024` (`22.6%`)** (with the Top 25 bitstrings covering **`57.27%`** of the entire manuscript!)
- **Sum of 10 Marginal Feature Entropies $\sum_{i=1}^{10} H(F_i)$**: `8.0506 bits`
- **Joint 10-Bit Vector Entropy $H(F_1, \dots, F_{10})$**: **`6.3587 bits`**
- **Internal Grammatical Constraint (Multi-Information / Redundancy)**: **`1.6918 bits`** (`21.0%` compression due to phonotactic selection laws!)

---

## 2. The 10 Binary Features of Voynich Morphology

| Bit | Feature Name | `+1` Rate (%) | Marginal $H(F_i)$ (bits) | Structural Definition & Empirical Justification |
| :---: | :--- | :---: | :---: | :--- |
| `F1` | **`F1_OPEN_CLASS`** | `75.99%` | `0.7953` | Open-Class Gallows/Bench stem (`1`) vs. Closed-Class Functional word (`0`) [`Attack 55 & 57`] |
| `F2` | **`F2_ACTIVE_Q`** | `14.75%` | `0.6035` | Active Operator proclitic `qo-/q-` (`1`) vs. Stative/Nominal/Zero (`0`) [`Attack 35 & 57`, $z = +1357.35$] |
| `F3` | **`F3_APPLICATIVE_L`** | `13.23%` | `0.5638` | Liquid-Applicative `l-/ol-/qol-` prefix or `-l-` denominal infix (`1`) vs. absent (`0`) [`Attack 51 & 67`, $z = +23.26$] |
| `F4` | **`F4_CONT_S_Y_PLUME`** | `20.55%` | `0.7328` | Sibilant/Conjunction Left-Margin Continuation `s-/sh-/y-` (`1`) vs. Interior `d-/ch-/o-` (`0`) [`Attack 53 & 58`, $z = +10.45$] |
| `F5` | **`F5_GALLOWS_HIGH`** | `53.40%` | `0.9967` | Tall Gallows Core `k/t/p/f` (`1`) vs. Horizontal Bench/Zero Core (`0`) [`Attack 45 & 57`] |
| `F6` | **`F6_DOUBLE_LOOP_T`** | `23.14%` | `0.7804` | Double-Loop `T_CLASS` `t/p/cth/tch` (`1`, Astrological/Labels) vs. Single-Loop `K_CLASS` (`0`, Bio/Pharma) [`Attack 59`, $z = +322.37$] |
| `F7` | **`F7_COMPOUND_EXT`** | `19.92%` | `0.7203` | Complex Gallows-Bench (`ckh/cth/kch/tch`) or Double-Core/Infix compound (`1`) vs. Simplex (`0`) [`Attack 45 & 67`] |
| `F8` | **`F8_VERBAL_Y`** | `42.03%` | `0.9816` | Verbal/Participial `-y / -dy` coda (`1`) vs. Nominal/Quantitative `-aiin/-ol/-or/-al/-ar/-am` (`0`) [`Attack 57`, $z = +318.29$] |
| `F9` | **`F9_DENTAL_D`** | `34.66%` | `0.9310` | Dental `-d-` morpheme (`-dy` finite/participial, `-d-` infix, or `d-` deictic, `1`) vs. absent (`0`) [`Attack 49 & 65`, $z = +23.84$] |
| `F10` | **`F10_OPEN_A_RHOTIC`** | `36.31%` | `0.9453` | Open `a`-grade / Rhotic `-r` coda (`-aiin, -ar, -al, -am, -or`, `1`) vs. Back `o/e`-grade / `-l` (`0`) [`Attack 50 & 66`, $z = +17.50$] |

---

## 3. Top 25 Attested 10-Bit Hypercube States (`67.98%` of All Manuscript Tokens)

| Rank | 10-Bit Vector | Tokens | Share % | Cum % | Active Binary Features | Top Exemplar Words |
| :---: | :---: | :---: | :---: | :---: | :--- | :--- |
| 1 | `0000000011` | `2,008` | `5.54%` | `5.54%` | `DENTAL_D+OPEN_A_RHOTIC` | `daiin` (790), `dar` (277), `dain` (195), `dal` (188) |
| 2 | `0000000001` | `1,459` | `4.03%` | `9.57%` | `OPEN_A_RHOTIC` | `aiin` (321), `or` (280), `ar` (274), `ain` (71) |
| 3 | `1000100001` | `1,213` | `3.35%` | `12.92%` | `OPEN_CLASS+GALLOWS_HIGH+OPEN_A_RHOTIC` | `okaiin` (212), `okain` (138), `okal` (135), `okar` (126) |
| 4 | `1000110001` | `1,102` | `3.04%` | `15.96%` | `OPEN_CLASS+GALLOWS_HIGH+DOUBLE_LOOP_T+OPEN_A_RHOTIC` | `otaiin` (151), `otar` (129), `otal` (119), `otain` (95) |
| 5 | `1000000110` | `1,095` | `3.02%` | `18.98%` | `OPEN_CLASS+VERBAL_Y+DENTAL_D` | `chedy` (450), `chdy` (133), `chody` (90), `cheody` (87) |
| 6 | `1100100001` | `1,055` | `2.91%` | `21.89%` | `OPEN_CLASS+ACTIVE_Q+GALLOWS_HIGH+OPEN_A_RHOTIC` | `qokain` (278), `qokaiin` (263), `qokal` (188), `qokar` (148) |
| 7 | `1000000000` | `977` | `2.70%` | `24.59%` | `OPEN_CLASS` | `chol` (336), `cheol` (147), `cho` (55), `cheo` (39) |
| 8 | `1001000110` | `867` | `2.39%` | `26.98%` | `OPEN_CLASS+CONT_S_Y_PLUME+VERBAL_Y+DENTAL_D` | `shedy` (381), `sheedy` (75), `shody` (53), `sheody` (47) |
| 9 | `1000111100` | `857` | `2.37%` | `29.35%` | `OPEN_CLASS+GALLOWS_HIGH+DOUBLE_LOOP_T+COMPOUND_EXT+VERBAL_Y` | `cthy` (99), `chcthy` (78), `cthey` (47), `otchy` (44) |
| 10 | `1000101100` | `836` | `2.31%` | `31.66%` | `OPEN_CLASS+GALLOWS_HIGH+COMPOUND_EXT+VERBAL_Y` | `chckhy` (133), `cheky` (63), `checkhy` (47), `choky` (39) |
| 11 | `1000000100` | `748` | `2.06%` | `33.72%` | `OPEN_CLASS+VERBAL_Y` | `chey` (297), `cheey` (156), `chy` (154), `choy` (15) |
| 12 | `1001000000` | `715` | `1.97%` | `35.70%` | `OPEN_CLASS+CONT_S_Y_PLUME` | `shol` (173), `sho` (104), `sheol` (102), `sheo` (32) |
| 13 | `1000000001` | `705` | `1.95%` | `37.64%` | `OPEN_CLASS+OPEN_A_RHOTIC` | `chor` (196), `cheor` (84), `char` (69), `chear` (44) |
| 14 | `1100100110` | `684` | `1.89%` | `39.53%` | `OPEN_CLASS+ACTIVE_Q+GALLOWS_HIGH+VERBAL_Y+DENTAL_D` | `qokeedy` (304), `qokedy` (272), `qokeody` (33), `qokeeody` (16) |
| 15 | `1001000100` | `678` | `1.87%` | `41.40%` | `OPEN_CLASS+CONT_S_Y_PLUME+VERBAL_Y` | `shey` (238), `sheey` (129), `shy` (86), `ycheey` (24) |
| 16 | `0010000000` | `664` | `1.83%` | `43.23%` | `APPLICATIVE_L` | `ol` (392), `l` (58), `lol` (32), `ols` (20) |
| 17 | `0000000000` | `651` | `1.80%` | `45.03%` | `ZERO_BARE` | `o` (89), `r` (88), `aiiin` (36), `oiin` (31) |
| 18 | `1000100100` | `618` | `1.71%` | `46.74%` | `OPEN_CLASS+GALLOWS_HIGH+VERBAL_Y` | `okeey` (178), `oky` (100), `okey` (62), `keey` (35) |
| 19 | `1100100100` | `612` | `1.69%` | `48.43%` | `OPEN_CLASS+ACTIVE_Q+GALLOWS_HIGH+VERBAL_Y` | `qokeey` (302), `qoky` (136), `qokey` (102), `qokeeey` (27) |
| 20 | `1000100110` | `571` | `1.58%` | `50.00%` | `OPEN_CLASS+GALLOWS_HIGH+VERBAL_Y+DENTAL_D` | `okedy` (119), `okeedy` (106), `okeody` (38), `keedy` (35) |
| 21 | `0010000001` | `570` | `1.57%` | `51.57%` | `APPLICATIVE_L+OPEN_A_RHOTIC` | `al` (167), `oraiin` (61), `olaiin` (56), `lor` (36) |
| 22 | `1000110110` | `564` | `1.56%` | `53.13%` | `OPEN_CLASS+GALLOWS_HIGH+DOUBLE_LOOP_T+VERBAL_Y+DENTAL_D` | `otedy` (158), `oteedy` (105), `oteody` (40), `tedy` (33) |
| 23 | `1000110100` | `509` | `1.40%` | `54.54%` | `OPEN_CLASS+GALLOWS_HIGH+DOUBLE_LOOP_T+VERBAL_Y` | `oteey` (139), `oty` (111), `otey` (56), `teey` (15) |
| 24 | `1000100000` | `507` | `1.40%` | `55.94%` | `OPEN_CLASS+GALLOWS_HIGH` | `okol` (70), `okeol` (64), `kol` (22), `keol` (17) |
| 25 | `0000000010` | `484` | `1.34%` | `57.27%` | `DENTAL_D` | `dol` (91), `d` (38), `daiiin` (19), `daiir` (19) |

---

## 4. Top Lag-1 Cross-Word Feature Transitions ($F_i(w_t) \to F_j(w_{t+1})$)

| Rank | Feature of $w_t$ | Feature of $w_{t+1}$ | Lag-1 $\phi$ Correlation | Syntactic Interpretation |
| :---: | :--- | :--- | :---: | :--- |
| 1 | `F8_VERBAL_Y` | `F2_ACTIVE_Q` | **`+0.2611`** | Positive syntactic licensing / register persistence |
| 2 | `F10_OPEN_A_RHOTIC` | `F2_ACTIVE_Q` | **`-0.1824`** | Cross-word syntactic alternation / dissimilation |
| 3 | `F8_VERBAL_Y` | `F5_GALLOWS_HIGH` | **`+0.1632`** | Positive syntactic licensing / register persistence |
| 4 | `F9_DENTAL_D` | `F2_ACTIVE_Q` | **`+0.1576`** | Positive syntactic licensing / register persistence |
| 5 | `F1_OPEN_CLASS` | `F2_ACTIVE_Q` | **`+0.1361`** | Positive syntactic licensing / register persistence |
| 6 | `F6_DOUBLE_LOOP_T` | `F6_DOUBLE_LOOP_T` | **`+0.1330`** | Positive syntactic licensing / register persistence |
| 7 | `F9_DENTAL_D` | `F9_DENTAL_D` | **`+0.1210`** | Positive syntactic licensing / register persistence |
| 8 | `F1_OPEN_CLASS` | `F5_GALLOWS_HIGH` | **`+0.1186`** | Positive syntactic licensing / register persistence |
| 9 | `F4_CONT_S_Y_PLUME` | `F2_ACTIVE_Q` | **`+0.1043`** | Positive syntactic licensing / register persistence |
| 10 | `F9_DENTAL_D` | `F5_GALLOWS_HIGH` | **`+0.0984`** | Positive syntactic licensing / register persistence |
| 11 | `F8_VERBAL_Y` | `F9_DENTAL_D` | **`+0.0926`** | Positive syntactic licensing / register persistence |
| 12 | `F8_VERBAL_Y` | `F8_VERBAL_Y` | **`+0.0892`** | Positive syntactic licensing / register persistence |
