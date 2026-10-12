# The Astro-Botanical Calendar, Quire 14 Cosmological Companion & Quire 20 Stoichiometric Procedural Handbook (`Attacks 101–104` / `Discoveries 118–121`)

> **Repository-Relative Asset Links**:
> - **Scripts**: [`tools/attack101_zodiac_10sign_nymph_and_herbal_astro_calendar.py`](../tools/attack101_zodiac_10sign_nymph_and_herbal_astro_calendar.py), [`tools/attack102_quire14_f85_f86_and_rosettes_bridge.py`](../tools/attack102_quire14_f85_f86_and_rosettes_bridge.py), [`tools/attack103_quire20_recipe_step_and_dosing_parser.py`](../tools/attack103_quire20_recipe_step_and_dosing_parser.py), [`tools/attack104_astro_botanical_and_306recipe_handbook.py`](../tools/attack104_astro_botanical_and_306recipe_handbook.py)
> - **Structured Datasets**: [`data/attack101_zodiac_10sign_nymph_and_herbal_astro_calendar.json`](../data/attack101_zodiac_10sign_nymph_and_herbal_astro_calendar.json), [`data/attack102_quire14_f85_f86_and_rosettes_bridge.json`](../data/attack102_quire14_f85_f86_and_rosettes_bridge.json), [`data/attack103_quire20_recipe_step_and_dosing_parser.json`](../data/attack103_quire20_recipe_step_and_dosing_parser.json), [`data/attack104_astro_botanical_and_306recipe_handbook.json`](../data/attack104_astro_botanical_and_306recipe_handbook.json)

---

## Part I: The 12-Medallion Zodiac (`f70v2–f73v`) Astro-Botanical Calendar (`Attack 101` / `Discovery 118`)

- **Astro-Botanical Herbal Correspondence ($z = +3.34$)**: Across the `12` Zodiac medallions (`f70v2` Pisces through `f73v` Sagittarius), the mean Top-1 IDF-weighted open-class stem overlap with Herbal Monographs (`$I=H`) is **`15.496` vs. `13.323 ± 0.65` under 300-trial vocabulary-preserving permutation ($z = +3.34$)**.
- **`3.39×` Herbal-B Selectivity (`10 / 12 = 83.33%`)**: Although Herbal-B comprises only `31 / 126` (`24.60%`) of Herbal folios, **`10 / 12` (`83.33%`) of Zodiac medallions match a Herbal-B folio as their `#1` botanical partner (`3.39×` enrichment)**, led by `f43v` (`Quire F, B=3`), `f34r` (`Quire E, B=2`, matching `f73r` Scorpio at `IDF = 23.42` with `8` shared open stems), `f40r`, and `f48r`!
- **Taurus Split-Sign Coherence (`+61.8%`) & Distinct Medallion Inventories ($z = -0.59$)**: Facing halves of Taurus (`f71v` Taurus-Light and `f72r1` Taurus-Dark) share **`0.1304` stem Jaccard (`+61.8%` above non-adjacent medallion pairs `0.0806`)**, while across different signs each medallion maintains a distinct 30-degree lexical inventory (`adjacent_mean = 0.0771`, $z = -0.59$). In the split Aries/Taurus medallions, **Dark-Star halves (`f70v1, f72r1`) enrich `-aiin` quantifiers by `1.70×` (`13.48%` vs. `7.95%` Light)**, while across the annual wheel `y-` onset rises **`15.6×` from Spring (`1.14%` on `f71r/f71v`) to Autumn/Winter (`11.83%` on `f72v1` Libra, `17.78%` on `f73v` Sagittarius)**.

| Zodiac Folio | Zodiac Sign & Month | `#1` Herbal Monograph (`$L`) | Runner-Up Herbal Folios | Shared Open Stems | IDF Overlap Score | Top Shared Astro-Botanical Stems (`Zodiac <-> Herbal`) |
| :---: | :--- | :---: | :--- | :---: | :---: | :--- |
| **`f70v2`** | `01_PISCES_MAR` | **`f87r`** (`A`) | `f34r(13.5)`, `f43r(13.4)`, `f20v(13.1)` | `6` | **`13.53`** | `aldy: Z(alody) <-> H(aldy)`; `sal: Z(sal) <-> H(sal)`; `otedy: Z(oteody) <-> H(oteody)`; `cheos: Z(sheeos) <-> H(cheos)` |
| **`f70v1`** | `02A_ARIES_DARK_APR1` | **`f40r`** (`B`) | `f48r(12.6)`, `f43r(10.9)`, `f57r(10.7)` | `5` | **`14.57`** | `okolchy: Z(okolshy) <-> H(okolchy)`; `toar: Z(toar) <-> H(toar)`; `air: Z(air) <-> H(aiir)`; `olain: Z(olaiin) <-> H(olaiin)` |
| **`f71r`** | `02B_ARIES_LIGHT_APR2` | **`f43v`** (`B`) | `f43r(10.9)`, `f41v(9.3)`, `f90v1(9.3)` | `5` | **`11.12`** | `okaldy: Z(okalody) <-> H(okaldy)`; `oteos: Z(oteos*Lz) <-> H(oteos)`; `otedy: Z(oteody) <-> H(oteody)`; `okedy: Z(okeeody) <-> H(okeody)` |
| **`f71v`** | `03A_TAURUS_LIGHT_MAY1` | **`f48r`** (`B`) | `f17v(9.8)`, `f8r(9.2)`, `f42r(9.2)` | `4` | **`10.44`** | `otaldy: Z(otalody) <-> H(opaldy)`; `oteodain: Z(oteeodaiin) <-> H(oteodaiin)`; `che: Z(she) <-> H(she)`; `okam: Z(okam) <-> H(okam)` |
| **`f72r1`** | `03B_TAURUS_DARK_MAY2` | **`f43v`** (`B`) | `f31v(11.4)`, `f93v(10.2)`, `f8v(10.1)` | `6` | **`13.74`** | `chedal: Z(chedal) <-> H(chedal)`; `oteos: Z(oteos) <-> H(oteos)`; `otam: Z(otam) <-> H(otam)`; `ytey: Z(ytey) <-> H(yteey)` |
| **`f72r2`** | `04_GEMINI_JUN` | **`f43v`** (`B`) | `f48v(13.0)`, `f66v(12.7)`, `f24r(11.8)` | `7` | **`16.28`** | `okedal: Z(okedal) <-> H(qokedal)`; `okaldy: Z(okaldy) <-> H(okaldy)`; `oteos: Z(oteos) <-> H(oteos)`; `otedy: Z(qoteeody) <-> H(oteody)` |
| **`f72r3`** | `05_CANCER_JUL` | **`f43v`** (`B`) | `f50r(16.9)`, `f31r(15.5)`, `f26v(14.9)` | `9` | **`18.47`** | `oteos: Z(oteos) <-> H(oteos)`; `ytain: Z(ypaiin) <-> H(ytaiin)`; `otedy: Z(oteody) <-> H(oteody)`; `orain: Z(oraiin) <-> H(oraiin)` |
| **`f72v3`** | `06_LEO_AUG` | **`f43v`** (`B`) | `f34r(13.1)`, `f33v(12.8)`, `f87r(12.6)` | `7` | **`15.81`** | `chesy: Z(cheesy) <-> H(chesy)`; `okaldy: Z(okaldy) <-> H(okaldy)`; `oteos: Z(oteos) <-> H(oteos)`; `otedy: Z(oteody) <-> H(oteody)` |
| **`f72v2`** | `07_VIRGO_SEP` | **`f90v1`** (`A`) | `f49r(12.4)`, `f48r(12.4)`, `f43r(11.6)` | `7` | **`16.73`** | `cheokey: Z(sheokey) <-> H(cheokeey)`; `ykeor: Z(ykeeor) <-> H(ykeeor)`; `ytedy: Z(yteody) <-> H(yteody)`; `okeor: Z(okeeor) <-> H(qokeor)` |
| **`f72v1`** | `08_LIBRA_OCT` | **`f43v`** (`B`) | `f48v(11.4)`, `f39r(11.1)`, `f54v(10.2)` | `7` | **`18.8`** | `chtey: Z(shtey) <-> H(chtey)`; `oteod: Z(oteod) <-> H(oteod)`; `octhy: Z(octhy) <-> H(octhy)`; `oteos: Z(oteos) <-> H(oteos)` |
| **`f73r`** | `09_SCORPIO_NOV` | **`f34r`** (`B`) | `f46r(18.9)`, `f43v(18.1)`, `f31v(16.4)` | `8` | **`23.42`** | `oltey: Z(olteey) <-> H(oltey)`; `chesy: Z(cheesy) <-> H(chesy)`; `chetey: Z(cheteey) <-> H(chetey)`; `ochey: Z(qocheey) <-> H(ochey)` |
| **`f73v`** | `10_SAGITTARIUS_DEC` | **`f43v`** (`B`) | `f90v1(12.0)`, `f54v(11.6)`, `f41v(11.0)` | `6` | **`13.04`** | `ykedy: Z(ykeody) <-> H(ykeody)`; `ytain: Z(ypaiin) <-> H(ytaiin)`; `otedy: Z(oteody) <-> H(oteody)`; `ytdy: Z(yteedy) <-> H(yteedy)` |

---

## Part II: The Quire 14 (`f85r1–f86v6` + `fRos`) Cosmological Diagram $\leftrightarrow$ Prose Treatise Exegetical Bridge (`Attack 102` / `Discovery 119`)

- **`+43.20%` Within-Quire Exegetical Stem Cohesion ($z = +3.11$)**: The `4` Quire 14 Prose Treatise surfaces (`f85r1, f86v3, f86v5, f86v6`) share **`0.071` mean open-class stem Jaccard** (`95` shared open stems = `23.57%` of all Diagram open stems) with the `3` Quire 14 Cosmological Diagram surfaces (`f85r2, f86v4, fRos`), beating all other Currier B prose folios (`0.0496`) by **`+43.2%` ($z = +3.11$)**.
- **`2.08×` `o- -> qo-` Active Verb Transformation (`Diagrams -> Treatises`)**: Holding the exact `95` shared stems fixed, their occurrences on the **Quire 14 Diagrams (`n=171`)** are **`53.8%` Nominal `o-` (`5.85%` `qo-`)**, whereas in the **Quire 14 Prose Treatises (`n=255`)** Active `qo-` more than doubles to **`12.16%` (`2.08×`, e.g. `otchdaiin -> qotchdaiin`)** and Applicative `l-/ol-/qol-` rises from **`14.04% -> 17.65%`**.

| Quire 14 Diagram Surface | Quire 14 Exegetical Treatise | Shared Open Stems | Open-Stem Jaccard | IDF Overlap Score | Top Shared Cosmological Bridges (`Diagram -> Treatise`) |
| :---: | :---: | :---: | :---: | :---: | :--- |
| **`fRos`** | **`f86v6`** | `35` | `0.0794` | **`83.41`** | `oro: Diag(oro) -> Treat(oro)`; `otchdain: Diag(otchdaiin) -> Treat(qotchdaiin)`; `dairdy: Diag(dairdy) -> Treat(dairody)`; `otydain: Diag(otydaiin) -> Treat(qopydaiin)` |
| **`fRos`** | **`f85r1`** | `33` | `0.0819` | **`71.15`** | `otedam: Diag(otedam) -> Treat(otedam)`; `tched: Diag(tched) -> Treat(tsheed)`; `tchdain: Diag(tchdaiin) -> Treat(pchdaiin)`; `oto: Diag(oto) -> Treat(oto)` |
| **`fRos`** | **`f86v5`** | `27` | `0.0678` | **`59.13`** | `otches: Diag(opchees) -> Treat(otchees)`; `oal: Diag(oal) -> Treat(oal)`; `okary: Diag(okary) -> Treat(okary)`; `octhey: Diag(octhey) -> Treat(octhey)` |
| **`f86v4`** | **`f85r1`** | `22` | `0.0969` | **`44.36`** | `chdair: Diag(chdair) -> Treat(shdair)`; `chetchdy: Diag(cheepchdy) -> Treat(shetshdy)`; `chotain: Diag(chotaiin) -> Treat(chotaiin)`; `octhdy: Diag(octhedy) -> Treat(qocthdy)` |
| **`fRos`** | **`f86v3`** | `16` | `0.042` | **`36.71`** | `otodar: Diag(otodar) -> Treat(otodar)`; `okady: Diag(okady) -> Treat(qokady)`; `odey: Diag(odeey) -> Treat(odeeey)`; `olkar: Diag(olkar) -> Treat(olkar)` |
| **`f86v4`** | **`f86v6`** | `17` | `0.0625` | **`32.58`** | `ltchdy: Diag(lpchedy) -> Treat(ltchedy)`; `chotain: Diag(chotaiin) -> Treat(shotaiin)`; `olkar: Diag(olkar) -> Treat(olkar)`; `chdar: Diag(shdar) -> Treat(chdar)` |
| **`f86v4`** | **`f86v5`** | `17` | `0.0769` | **`30.9`** | `olkar: Diag(olkar) -> Treat(olkar)`; `ytedy: Diag(yteeody) -> Treat(yteody)`; `otcho: Diag(opcho) -> Treat(otcho)`; `oes: Diag(oes) -> Treat(oeees)` |
| **`f85r2`** | **`f86v3`** | `15` | `0.0857` | **`30.3`** | `otodar: Diag(otodar) -> Treat(otodar)`; `otodain: Diag(otodaiin) -> Treat(otodaiin)`; `oram: Diag(oram) -> Treat(oram)`; `olkar: Diag(olkar) -> Treat(olkar)` |
| **`f85r2`** | **`f86v6`** | `15` | `0.0591` | **`29.45`** | `otchd: Diag(qotchd) -> Treat(qopchd)`; `ardy: Diag(arody) -> Treat(arody)`; `octhey: Diag(qocthey) -> Treat(ocphey)`; `olkar: Diag(olkar) -> Treat(olkar)` |
| **`f85r2`** | **`f86v5`** | `13` | `0.0634` | **`27.59`** | `otchs: Diag(otchs) -> Treat(otshs)`; `otodain: Diag(otodaiin) -> Treat(otodaiin)`; `octhey: Diag(qocthey) -> Treat(octhey)`; `olkar: Diag(olkar) -> Treat(olkar)` |
| **`f85r2`** | **`f85r1`** | `15` | `0.0701` | **`25.31`** | `oram: Diag(oram) -> Treat(oram)`; `octhdy: Diag(octhody) -> Treat(qocthdy)`; `kchey: Diag(fcheey) -> Treat(ksheey)`; `ytchdy: Diag(ypshedy) -> Treat(ypchdy)` |
| **`f86v4`** | **`f86v3`** | `13` | `0.066` | **`25.05`** | `olkar: Diag(olkar) -> Treat(olkar)`; `ytedy: Diag(yteeody) -> Treat(yteeody)`; `chdar: Diag(shdar) -> Treat(chdar)`; `oes: Diag(oes) -> Treat(oees)` |

---

## Part III: The Quire 20 (`f103r–f116r`, `292` Starred Recipes) Three-Phase Procedural Trajectory & `1:1` Stoichiometric Dosing Law (`Attack 103` / `Discovery 120`)

- **Three-Phase Internal Recipe Trajectory (`239` Multi-Line Starred Recipes)**: Moving from `PHASE_1_OPENING_LINE` (`2,358` tokens) through `PHASE_2_MIDDLE_PROCESSING_LINES` (`6,046` tokens) to `PHASE_3_FINAL_CLOSING_LINE` (`1,469` tokens):
  1. **Gallows/Header Onsets (`p-/f-/t-/k-/po-/fo-/to-/ko-`)** drop **`5.67×` from `16.62% -> 4.27% -> 2.93%` ($z = +15.21$)**.
  2. **Imperative Action Verbs (`qo-` and `-edy`)** peak on the **Opening Line (`20.02% qo-`, `17.43% -edy`)** and step down monotonically (`20.02% -> 17.93% -> 13.55% qo-`; `17.43% -> 13.51% -> 12.53% -edy`).
  3. **Liquid Applicatives (`l-/ol-/qol-`)** rise monotonically by **`+41.4%` (`8.57% -> 11.18% -> 12.12%`)**.
  4. **Measured Dose Quantifiers (`-aiin / -ain / -iin`)** surge monotonically by **`+60.6%` (`1.61×`, from `14.84% -> 20.91% -> 23.83%`)** into the final dosing/administration line!
- **The `0.964` (`~1:1`) Stoichiometric Verb-to-Dose Scaling Law ($r = +0.7476$)**: Across all `292` Starred Recipes (`mean = 36.92` tokens, `3.99` lines, `4.27` procedural steps), each recipe pairs a mean of **`16.03` measured doses/containers** with **`12.28` active verbs**, maintaining a **mean per-recipe `Verb : Dose` ratio of `0.964` (`~1:1`, Pearson $r = +0.7476$)**.

| Internal Recipe Phase | Tokens | Gallows Header `%` | `qo-` Active Verb `%` | `-edy` Processual `%` | `l-/ol-` Applicative `%` | `-aiin` Measured Dose `%` | `-ol/-or` Container `%` |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `PHASE_1_OPENING_LINE` | `2358` | **`16.62%`** | **`20.02%`** | **`17.43%`** | **`8.57%`** | **`14.84%`** | `24.34%` |
| `PHASE_2_MIDDLE_PROCESSING_LINES` | `6046` | **`4.27%`** | **`17.93%`** | **`13.51%`** | **`11.18%`** | **`20.91%`** | `24.2%` |
| `PHASE_3_FINAL_CLOSING_LINE` | `1469` | **`2.93%`** | **`13.55%`** | **`12.53%`** | **`12.12%`** | **`23.83%`** | `21.58%` |

