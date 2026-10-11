# Four-Tier Radical & Clause-Frame Structural Translation Edition (`Phase 27 / Attack 16`)
## 1. Corpus-Wide Structural Parse Coverage
- **Total Prose Tokens Parsed**: `32,590` tokens across all 226 folios.
- **Tokens with Grounded Radical Gloss (`Attack 12/14` Lexicon)**: **`31,184 / 32,590` (`95.69%`)**.
- **Tokens Containing a Top-59 Elementary Radical (`Attack 14`)**: **`31,049 / 32,590` (`95.27%`)**.
- **Prose Tokens Sharing an Exact Core Root with a Diagram Figure Label (`@Lf/@Lc/@Lz/@L0/@Lt/@Ln`)**: **`23,695 / 32,590` (`72.71%`)**.

### Guide to the Four Interlinear Tiers
1. **Tier 1 (`EVA Surface`)**: Exact transliteration from [data/ZL3b-n.txt](../data/ZL3b-n.txt) with paragraph start (`<%>`), paragraph end (`<$>`), drawing intrusion (`<->`), and marginal star class (`[★D]`, `[★L.]`, `[★L]`).
2. **Tier 2 (`Radical Segmentation`)**: Stage-3 canonical form segmented into `Prefix-[R_1+R_2]-Suffix` via our FST ([tools/attack7_positional_envelope_fst.py](../tools/attack7_positional_envelope_fst.py)) and Minimum Description Length Radical Decomposition ([tools/attack12_core_root_radical_decomposition.py](../tools/attack12_core_root_radical_decomposition.py)).
3. **Tier 3 (`Morphosyntactic & Radical Role Gloss`)**: Functional slot parse combining proclitic/prefix operators (`CONJ(q-)+`, `NOM(o-)+`, `ABL(d-)+`, `LIQ(l-)+`), empirically grounded radical domains (`ACT:mix/proc`, `ACT:heat/steep`, `BOTAN/ROOT(ar)`, `JAR/HERB(or)`, `FLUID/TUBE(ol)`), and case/verbal suffixes (`-VERB(do/ed)`, `-ACC/GEN(unit)`, `-LOC(fluid)`, `-FIN(complete!)`).
4. **Tier 4 (`Diagram Crib & Structural Anchor Notes`)**: Direct 1-word and 2-word crib equations linking prose tokens to illustrated plants (`@Lf`), apothecary jars (`@Lc`), zodiac degrees (`@Lz`), cosmological hubs (`@L0`), or biological tubes/nymphs (`@Lt/@Ln`).

---

## 1. The Three-Way Botanical Phrase Crib Paradigm (`f88v.4` Label <-> `f105r.1-8` Chained Recipes <-> `f114v.36-38` Recipe)
Demonstrates the 2-word botanical label `<f88v.4,@Lf> otar . arody` (`18.47` rarity bits) recurring across three distinct syntactic environments with predictable positional allography: (a) standalone plant label `otar . arody` (`o-` nominal + `t` gallows), (b) paragraph-initial recipe header `<f105r.6,@P0> <%>par . arody` (top-line `p` gallows, chained to `<f105r.1-5>` via shared `L.` star), and (c) interior line-final clause closer `<f114v.37,+P0> ... chey . tar . arody <$>` (unprefixed `t` gallows).

### f88v Botanical Labels (Lines 1-6)
- **`<f88v.1,@Lc>`** 
  - **T1 (EVA)**: `okalyd`
  - **T2 (Radicals)**: `[kal+y]--d`
  - **T3 (Gloss)**: `NOM+HUMORAL_ROOT(kal)+STATE(y)--d`
  - **T4 (Cribs)**: `okalyd` = exact label `okalyd` [f88v.1(@Lc)]
- **`<f88v.2,@Lf>`** 
  - **T1 (EVA)**: `cheocthy`
  - **T2 (Radicals)**: `[cheo+cth]--y`
  - **T3 (Gloss)**: `(cheo)+HERB_LEAF_OP(cth)--y`
  - **T4 (Cribs)**: `cheocthy` = exact label `cheocthy` [f88v.2(@Lf)]
- **`<f88v.3,@Lf>`** 
  - **T1 (EVA)**: `cpheor`
  - **T2 (Radicals)**: `[cthe]--or`
  - **T3 (Gloss)**: `ROOT(cthe)--or`
  - **T4 (Cribs)**: `cpheor` = exact label `ctheor` [f88v.3(@Lf)]
- **`<f88v.4,@Lf>`** 
  - **T1 (EVA)**: `otar . arody`
  - **T2 (Radicals)**: `[t]--ar . [ar]--ody`
  - **T3 (Gloss)**: `NOM+TUBE/DUCT(t)--ar | BOTAN/ROOT(ar)--ody`
  - **T4 (Cribs)**: `otar . arody` == Diagram Label `otar . arody` (f88v.4(2W-LABEL)); `otar` = exact label `otar` [f70v2.4(&Lz), f70v2.22(@Lz)]; `arody` = exact label `arody` [f88v.4(@Lf)]
- **`<f88v.5,@Lf>`** 
  - **T1 (EVA)**: `otokol`
  - **T2 (Radicals)**: `[to+k]--ol`
  - **T3 (Gloss)**: `NOM+SPOKE/RAY(to)+VESSEL/BODY(k)--ol`
  - **T4 (Cribs)**: `otokol` = exact label `otokol` [f88v.5(@Lf)]
- **`<f88v.6,@P0>`** 
  - **T1 (EVA)**: `<%> teodal . lkeo,cheor . roshckhy . sorshy . aiin . cheokal . saldaiin`
  - **T2 (Radicals)**: `[teo+d]--al . [l+keo+che]--or . [ro+sh+ckh]--y . [so+rsh]--y . [ain] . [cheo+k]--al . [sa+ld]--ain`
  - **T3 (Gloss)**: `ZOD_CONTAIN(teo)+BASE/HUB(d)--al | LIQUID_PREF(l)+PHARMA_BOIL(keo)+ACT:infuse--or | ROOT(ro)+ACT:heat/steep+BALNEO_OP(ckh)--y | HERB_SAP(so)+ROOT(rsh)--y | ESSENCE/UNIT(ain) | (cheo)+VESSEL/BODY(k)--al | ROOT(sa)+ROOT(ld)--ain`
  - **T4 (Cribs)**: `aiin` = exact label `ain` [f99r.7(+Lf)]

### f105r Same-Star Chained Recipes P1->P2 (Lines 1-10)
- **`<f105r.1,@P0>`** [★L.] 
  - **T1 (EVA)**: `<%> @199;aiin,dar . chcphy . qokeey . qopaiin . ypcheeey . saraisl . aiin . cheedy . aiin . arody`
  - **T2 (Radicals)**: `[@1+9+9+;+ain+d]--ar . [ch+cth]--y . q--[k]--ey . q--[t]--ain . y--[tch]--ey . [sar+ai+s]--l . [ain] . [ch]--edy . [ain] . [ar]--ody`
  - **T3 (Gloss)**: `ROOT(@1)+ROOT(9)+ROOT(9)+ROOT(;)+ESSENCE/UNIT(ain)+BASE/HUB(d)--ar | ACT:mix/proc+HERB_LEAF_OP(cth)--y | CONJ+NOM+VESSEL/BODY(k)--ey | CONJ+NOM+TUBE/DUCT(t)--ain | INIT_NOM+PROC_OP(tch)--ey | ROOT(sar)+(ai)+SEED/PART(s)--l | ESSENCE/UNIT(ain) | ACT:mix/proc--edy | ESSENCE/UNIT(ain) | BOTAN/ROOT(ar)--ody`
  - **T4 (Cribs)**: `qokeey` = exact label `okey` [f69r.8(&L0), f72r1.16(&Lz)]; `qopaiin` = exact label `otain` [f71v.7(&Lz), f72r1.9(&Lz)]; `aiin` = exact label `ain` [f99r.7(+Lf)]; `aiin` = exact label `ain` [f99r.7(+Lf)]; `arody` = exact label `arody` [f88v.4(@Lf)]
- **`<f105r.2,+P0>`** 
  - **T1 (EVA)**: `dshees . yey . cheey . raiin . otchdy . qodor . ches . or . cheey . okees . odar . cheody,qody`
  - **T2 (Radicals)**: `[d+she]--s . y--[ey] . [ch]--ey . [r]--ain . [tch]--dy . q--[d]--or . [che]--s . [or] . [ch]--ey . [ke]--s . [d]--ar . [cheo+dy+q]--ody`
  - **T3 (Gloss)**: `BASE/HUB(d)+ACT:decoct--s | INIT_NOM+(ey) | ACT:mix/proc--ey | STREAM/PART(r)--ain | NOM+PROC_OP(tch)--dy | CONJ+NOM+BASE/HUB(d)--or | ACT:infuse--s | NOM+JAR/HERB(or) | ACT:mix/proc--ey | NOM+EXTRACT/COOK(ke)--s | NOM+BASE/HUB(d)--ar | (cheo)+DONE(dy)+ROOT(q)--ody`
  - **T4 (Cribs)**: `yey` = exact label `ey` [fRos.42(@L0)]; `otchdy` = exact label `otchdy` [f67v2.1(@La), f68r1.23(@Ls)]; `qodor` = exact label `odor` [f101v.17(@Lf)]; `or` = exact label `or` [f66r.3(+L0), f84r.2(@Ln)]; `okees` = exact label `okes` [f70v2.20(&Lz)]
- **`<f105r.3,+P0>`** 
  - **T1 (EVA)**: `olshey . qoden . odeey . kcheody . cheeo . ar . yteey . ytchy . otedy . qokeedy . qokeey . rol`
  - **T2 (Radicals)**: `[ol+sh]--ey . q--[de+n] . [d]--ey . [k+che]--ody . [cheo] . [ar] . y--[t]--ey . y--[tch]--y . [t]--edy . q--[k]--edy . q--[k]--ey . [r]--ol`
  - **T3 (Gloss)**: `NOM+FLUID/TUBE(ol)+ACT:heat/steep--ey | CONJ+NOM+ROOT(de)+ROOT(n) | NOM+BASE/HUB(d)--ey | VESSEL/BODY(k)+ACT:infuse--ody | (cheo) | BOTAN/ROOT(ar) | INIT_NOM+TUBE/DUCT(t)--ey | INIT_NOM+PROC_OP(tch)--y | NOM+TUBE/DUCT(t)--edy | CONJ+NOM+VESSEL/BODY(k)--edy | CONJ+NOM+VESSEL/BODY(k)--ey | STREAM/PART(r)--ol`
  - **T4 (Cribs)**: `odeey` = exact label `odey` [fRos.54(@L0)]; `ar` = exact label `ar` [f69r.6(&L0), f69r.14(&L0)]; `yteey` = exact label `ytey` [f69r.13(&L0), f69r.14(&L0)]; `otedy` = exact label `otedy` [f73r.3(&Lz), f73v.3(&Lz)]; `qokeedy` = exact label `okedy` [f72v1.28(&Lz), f73r.11(&Lz)]; `qokeey` = exact label `okey` [f69r.8(&L0), f72r1.16(&Lz)]
- **`<f105r.4,+P0>`** 
  - **T1 (EVA)**: `ykaiin . olkeedy . odaiin . okar . eeeodaiin . yteey . ochedy . qokeeey . oy . teedy . qotam`
  - **T2 (Radicals)**: `y--[k]--ain . [olk]--edy . [d]--ain . [k]--ar . [eod]--ain . y--[t]--ey . [ch]--edy . q--[k]--ey . [o]--y . [t]--edy . q--[t]--ar`
  - **T3 (Gloss)**: `INIT_NOM+VESSEL/BODY(k)--ain | NOM+(olk)--edy | NOM+BASE/HUB(d)--ain | NOM+VESSEL/BODY(k)--ar | ROOT(eod)--ain | INIT_NOM+TUBE/DUCT(t)--ey | NOM+ACT:mix/proc--edy | CONJ+NOM+VESSEL/BODY(k)--ey | NOM+ENTITY_CORE(o)--y | TUBE/DUCT(t)--edy | CONJ+NOM+TUBE/DUCT(t)--ar`
  - **T4 (Cribs)**: `ykaiin` = exact label `ykain` [f67r2.47(+L0)]; `olkeedy` = exact label `olkedy` [f82v.39(@Ln)]; `odaiin` = exact label `odain` [f68r2.9(@Ls)]; `okar` = exact label `okar` [f67r2.3(&L0), f67r2.10(&L0)]; `yteey` = exact label `ytey` [f69r.13(&L0), f69r.14(&L0)]; `qokeeey` = exact label `okey` [f69r.8(&L0), f72r1.16(&Lz)]
- **`<f105r.5,+P0>`** 
  - **T1 (EVA)**: `daiin . yteedy . yteeeody . yl . cheod . or . aiiroekey . otchdy . otey <$>`
  - **T2 (Radicals)**: `[d]--ain . y--[t]--edy . y--[te]--ody . [y]--l . [cheo]--d . [or] . [air+oe+k]--ey . [tch]--dy . [t]--ey`
  - **T3 (Gloss)**: `BASE/HUB(d)--ain | INIT_NOM+TUBE/DUCT(t)--edy | INIT_NOM+DRAW/CONDUIT(te)--ody | STATE(y)--l | (cheo)--d | NOM+JAR/HERB(or) | AETHER/STAR(air)+ROOT(oe)+VESSEL/BODY(k)--ey | NOM+PROC_OP(tch)--dy | NOM+TUBE/DUCT(t)--ey`
  - **T4 (Cribs)**: `daiin` = exact label `dain` [f67r2.56(&Ls)]; `yteedy` = exact label `ytedy` [f72v2.30(&Lz)]; `yteeeody` = exact label `yteody` [f72v2.14(&Lz), f73r.4(&Lz)]; `or` = exact label `or` [f66r.3(+L0), f84r.2(@Ln)]; `otchdy` = exact label `otchdy` [f67v2.1(@La), f68r1.23(@Ls)]; `otey` = exact label `otey` [f72v3.14(&Lz), f73r.21(&Lz)]
- **`<f105r.6,+P0>`** [★L.] 
  - **T1 (EVA)**: `<%> par . arody . shedeeey . qopchedy . qody . qoteody . aiin . yteody . qokor . olpshedy`
  - **T2 (Radicals)**: `[t]--ar . [ar]--ody . [she+d]--ey . q--[tch]--edy . q--[dy] . q--[te]--ody . [ain] . y--[te]--ody . q--[k]--or . [ol+tsh]--edy`
  - **T3 (Gloss)**: `TUBE/DUCT(t)--ar | BOTAN/ROOT(ar)--ody | ACT:decoct+BASE/HUB(d)--ey | CONJ+NOM+PROC_OP(tch)--edy | CONJ+NOM+DONE(dy) | CONJ+NOM+DRAW/CONDUIT(te)--ody | ESSENCE/UNIT(ain) | INIT_NOM+DRAW/CONDUIT(te)--ody | CONJ+NOM+VESSEL/BODY(k)--or | NOM+FLUID/TUBE(ol)+(tsh)--edy`
  - **T4 (Cribs)**: `par` = exact label `tar` [f70v1.2(@Lz)]; `arody` = exact label `arody` [f88v.4(@Lf)]; `qody` = exact label `ody` [f70v2.6(&Lz)]; `qoteody` = exact label `oteody` [f73v.2(&Lz), f73v.13(&Lz)]; `aiin` = exact label `ain` [f99r.7(+Lf)]; `yteody` = exact label `yteody` [f72v2.14(&Lz), f73r.4(&Lz)]
- **`<f105r.7,+P0>`** 
  - **T1 (EVA)**: `ysheeody . ykeeos . or . aiiin . shey . qodaiiin . qokeed . qokeey . saiin . aiirody`
  - **T2 (Radicals)**: `y--[she]--ody . y--[keo]--s . [or] . [ain] . [sh]--ey . q--[d]--ain . q--[ke]--d . q--[k]--ey . [s]--ain . [air]--ody`
  - **T3 (Gloss)**: `INIT_NOM+ACT:decoct--ody | INIT_NOM+PHARMA_BOIL(keo)--s | NOM+JAR/HERB(or) | ESSENCE/UNIT(ain) | ACT:heat/steep--ey | CONJ+NOM+BASE/HUB(d)--ain | CONJ+NOM+EXTRACT/COOK(ke)--d | CONJ+NOM+VESSEL/BODY(k)--ey | SEED/PART(s)--ain | AETHER/STAR(air)--ody`
  - **T4 (Cribs)**: `or` = exact label `or` [f66r.3(+L0), f84r.2(@Ln)]; `aiiin` = exact label `ain` [f99r.7(+Lf)]; `shey` = exact label `shey` [f68r2.29(@Ls), f116v.1(@Lx)]; `qodaiiin` = exact label `odain` [f68r2.9(@Ls)]; `qokeey` = exact label `okey` [f69r.8(&L0), f72r1.16(&Lz)]; `saiin` = exact label `sain` [f66r.12(+L0)]
- **`<f105r.8,+P0>`** 
  - **T1 (EVA)**: `sheey . oleeey . or,air . qokaiin . chey . qokeedy . qokedy . oteedy . lchedy . oesal`
  - **T2 (Radicals)**: `[sh]--ey . [ol]--ey . [or+ai]--r . q--[k]--ain . [ch]--ey . q--[k]--edy . q--[k]--edy . [t]--edy . [lch]--edy . [es]--al`
  - **T3 (Gloss)**: `ACT:heat/steep--ey | NOM+FLUID/TUBE(ol)--ey | NOM+JAR/HERB(or)+(ai)--r | CONJ+NOM+VESSEL/BODY(k)--ain | ACT:mix/proc--ey | CONJ+NOM+VESSEL/BODY(k)--edy | CONJ+NOM+VESSEL/BODY(k)--edy | NOM+TUBE/DUCT(t)--edy | LIQ_MIX(lch)--edy | NOM+ROOT(es)--al`
  - **T4 (Cribs)**: `sheey` = exact label `shey` [f68r2.29(@Ls), f116v.1(@Lx)]; `qokaiin` = exact label `okain` [f67r2.28(+L0), f72r3.12(&Lz)]; `qokeedy` = exact label `okedy` [f72v1.28(&Lz), f73r.11(&Lz)]; `qokedy` = exact label `okedy` [f72v1.28(&Lz), f73r.11(&Lz)]; `oteedy` = exact label `otedy` [f73r.3(&Lz), f73v.3(&Lz)]
- **`<f105r.9,+P0>`** 
  - **T1 (EVA)**: `oeeolchy . okeeydy . okeey . okchey`
  - **T2 (Radicals)**: `[eol+ch]--y . [k+ey]--dy . [k]--ey . [kch]--ey`
  - **T3 (Gloss)**: `NOM+ROOT(eol)+ACT:mix/proc--y | NOM+VESSEL/BODY(k)+(ey)--dy | NOM+VESSEL/BODY(k)--ey | NOM+STAR_OP(kch)--ey`
  - **T4 (Cribs)**: `okeey` = exact label `okey` [f69r.8(&L0), f72r1.16(&Lz)]
- **`<f105r.10,+Pr>`** 
  - **T1 (EVA)**: `sairy . ore . daiindy . ytam <$>`
  - **T2 (Radicals)**: `[sai]--ry . [or+e] . [d+ain]--dy . y--[t]--ar`
  - **T3 (Gloss)**: `ROOT(sai)--ry | NOM+JAR/HERB(or)+ESSENCE(e) | BASE/HUB(d)+ESSENCE/UNIT(ain)--dy | INIT_NOM+TUBE/DUCT(t)--ar`
  - **T4 (Cribs)**: `daiindy` = exact label `daindy` [f100r.5(@Lf)]

### f114v Starred Recipe P10 (Lines 36-38)
- **`<f114v.36,+P0>`** [★L.] 
  - **T1 (EVA)**: `<%> tshey . oidal . op . shoko . otchey . qopchol . qopaiin . qotar . al,kal . ram`
  - **T2 (Radicals)**: `[tsh]--ey . [i+d]--al . [ot] . [sho+ko] . [tch]--ey . q--[tch]--ol . q--[t]--ain . q--[t]--ar . [al+k]--al . [r]--ar`
  - **T3 (Gloss)**: `(tsh)--ey | NOM+ROOT(i)+BASE/HUB(d)--al | NOM+DUCT_NOM(ot) | (sho)+STAR_NODE(ko) | NOM+PROC_OP(tch)--ey | CONJ+NOM+PROC_OP(tch)--ol | CONJ+NOM+TUBE/DUCT(t)--ain | CONJ+NOM+TUBE/DUCT(t)--ar | SUBST/STAR(al)+VESSEL/BODY(k)--al | STREAM/PART(r)--ar`
  - **T4 (Cribs)**: `otchey` = exact label `otchey` [f70v1.3(&Lz)]; `qopaiin` = exact label `otain` [f71v.7(&Lz), f72r1.9(&Lz)]; `qotar` = exact label `otar` [f70v2.4(&Lz), f70v2.22(@Lz)]
- **`<f114v.37,+P0>`** 
  - **T1 (EVA)**: `dcheey . ol . cheodaiiin . qokar . otaiin . otal . o,kaiin . chey . tar . arody`
  - **T2 (Radicals)**: `[dch]--ey . [ol] . [cheo+d]--ain . q--[k]--ar . [t]--ain . [t]--al . [k]--ain . [ch]--ey . [t]--ar . [ar]--ody`
  - **T3 (Gloss)**: `(dch)--ey | NOM+FLUID/TUBE(ol) | (cheo)+BASE/HUB(d)--ain | CONJ+NOM+VESSEL/BODY(k)--ar | NOM+TUBE/DUCT(t)--ain | NOM+TUBE/DUCT(t)--al | NOM+VESSEL/BODY(k)--ain | ACT:mix/proc--ey | TUBE/DUCT(t)--ar | BOTAN/ROOT(ar)--ody`
  - **T4 (Cribs)**: `qokar` = exact label `okar` [f67r2.3(&L0), f67r2.10(&L0)]; `otaiin` = exact label `otain` [f71v.7(&Lz), f72r1.9(&Lz)]; `otal` = exact label `otal` [f70v2.16(&Lz), f70v1.11(&Lz)]; `o,kaiin` = exact label `okain` [f67r2.28(+L0), f72r3.12(&Lz)]; `tar` = exact label `tar` [f70v1.2(@Lz)]; `arody` = exact label `arody` [f88v.4(@Lf)]
- **`<f114v.38,+P0>`** 
  - **T1 (EVA)**: `oteey . okedaiin . otaiin . qotchey . qoteeody . otaiin . okal . dals`
  - **T2 (Radicals)**: `[t]--ey . [ke+d]--ain . [t]--ain . q--[tch]--ey . q--[te]--ody . [t]--ain . [k]--al . [d+al]--s`
  - **T3 (Gloss)**: `NOM+TUBE/DUCT(t)--ey | NOM+EXTRACT/COOK(ke)+BASE/HUB(d)--ain | NOM+TUBE/DUCT(t)--ain | CONJ+NOM+PROC_OP(tch)--ey | CONJ+NOM+DRAW/CONDUIT(te)--ody | NOM+TUBE/DUCT(t)--ain | NOM+VESSEL/BODY(k)--al | BASE/HUB(d)+SUBST/STAR(al)--s`
  - **T4 (Cribs)**: `oteey` = exact label `otey` [f72v3.14(&Lz), f73r.21(&Lz)]; `otaiin` = exact label `otain` [f71v.7(&Lz), f72r1.9(&Lz)]; `qotchey` = exact label `otchey` [f70v1.3(&Lz)]; `qoteeody` = exact label `oteody` [f73v.2(&Lz), f73v.13(&Lz)]; `otaiin` = exact label `otain` [f71v.7(&Lz), f72r1.9(&Lz)]; `okal` = exact label `okal` [f66r.13(+L0), f67r2.22(+L0)]

---

## 2. Same-Star Chained Recipe Pairs: Parallel Template Cloning (`f115r:P5->P6`) & Tail-to-Head Catenation (`f111r:P3->P4`)
Demonstrates why the rubricator repeated the same marginal star (`L. -> L.`) on 10 pairs in Quire 20: on `f115r:P5->P6`, the two recipes clone the exact 4-slot opening sequence (`tch -> qokch -> qotch -> l-pch/polch`); on `f111r:P3->P4`, the closing words of P3 (`lkeedy . lkedar . okeedy`) catenate directly into the opening clause of P4 (`<%>pchedar . oteeol . lkeedain . okeam`).

### f115r:P5->P6 Parallel Template Pair (Lines 17-23)
- **`<f115r.17,+P0>`** 
  - **T1 (EVA)**: `qol . cheey . qotchy . daiin . daiin . cheocthy . dolkeedy . qotaiin . chol . oteeedchey . okeedain`
  - **T2 (Radicals)**: `q--[ol] . [ch]--ey . q--[tch]--y . [d]--ain . [d]--ain . [cheo+cth]--y . [d+olk]--edy . q--[t]--ain . [ch]--ol . [ted+ch]--ey . [ke+d]--ain`
  - **T3 (Gloss)**: `CONJ+NOM+FLUID/TUBE(ol) | ACT:mix/proc--ey | CONJ+NOM+PROC_OP(tch)--y | BASE/HUB(d)--ain | BASE/HUB(d)--ain | (cheo)+HERB_LEAF_OP(cth)--y | BASE/HUB(d)+(olk)--edy | CONJ+NOM+TUBE/DUCT(t)--ain | ACT:mix/proc--ol | NOM+ROOT(ted)+ACT:mix/proc--ey | NOM+EXTRACT/COOK(ke)+BASE/HUB(d)--ain`
  - **T4 (Cribs)**: `qotchy` = exact label `otchy` [f102v2.13(@Lf)]; `daiin` = exact label `dain` [f67r2.56(&Ls)]; `daiin` = exact label `dain` [f67r2.56(&Ls)]; `cheocthy` = exact label `cheocthy` [f88v.2(@Lf)]; `qotaiin` = exact label `otain` [f71v.7(&Lz), f72r1.9(&Lz)]; `chol` = exact label `chol` [f68r2.25(@Ls)]
- **`<f115r.18,+P0>`** 
  - **T1 (EVA)**: `cheol . lcheey . okcho . keedor . ykechey . chchdy <$>`
  - **T2 (Radicals)**: `[che]--ol . [lch]--ey . [k+cho] . [ke+d]--or . y--[ke+ch]--ey . [ch+ch]--dy`
  - **T3 (Gloss)**: `ACT:infuse--ol | LIQ_MIX(lch)--ey | NOM+VESSEL/BODY(k)+(cho) | EXTRACT/COOK(ke)+BASE/HUB(d)--or | INIT_NOM+EXTRACT/COOK(ke)+ACT:mix/proc--ey | ACT:mix/proc+ACT:mix/proc--dy`
- **`<f115r.19,+P0>`** [★L.] 
  - **T1 (EVA)**: `<%> pcheodain . qokchey . qotchedy . darailchedy . polchedy . chol . pchody . qotchedy . qofchedy . ram`
  - **T2 (Radicals)**: `[tch+eod]--ain . q--[kch]--ey . q--[tch]--edy . [dar+ai+lch]--edy . [t+olch]--edy . [ch]--ol . [tch]--ody . q--[tch]--edy . q--[kch]--edy . [r]--ar`
  - **T3 (Gloss)**: `PROC_OP(tch)+ROOT(eod)--ain | CONJ+NOM+STAR_OP(kch)--ey | CONJ+NOM+PROC_OP(tch)--edy | JAR/ROOT_SRC(dar)+(ai)+LIQ_MIX(lch)--edy | TUBE/DUCT(t)+ROOT(olch)--edy | ACT:mix/proc--ol | PROC_OP(tch)--ody | CONJ+NOM+PROC_OP(tch)--edy | CONJ+NOM+STAR_OP(kch)--edy | STREAM/PART(r)--ar`
  - **T4 (Cribs)**: `chol` = exact label `chol` [f68r2.25(@Ls)]
- **`<f115r.20,+P0>`** 
  - **T1 (EVA)**: `lcheod . lkchedy . chockhy . chedy . qokchedy . qoky . chor . al . alor . cheey . qol . keo,r,shey`
  - **T2 (Radicals)**: `[l+cheo]--d . [lk+ch]--edy . [cho+ckh]--y . [ch]--edy . q--[kch]--edy . q--[k]--y . [ch]--or . [al] . [al]--or . [ch]--ey . q--[ol] . [keo+rsh]--ey`
  - **T3 (Gloss)**: `LIQUID_PREF(l)+(cheo)--d | LIQ_VESSEL(lk)+ACT:mix/proc--edy | (cho)+BALNEO_OP(ckh)--y | ACT:mix/proc--edy | CONJ+NOM+STAR_OP(kch)--edy | CONJ+NOM+VESSEL/BODY(k)--y | ACT:mix/proc--or | SUBST/STAR(al) | SUBST/STAR(al)--or | ACT:mix/proc--ey | CONJ+NOM+FLUID/TUBE(ol) | PHARMA_BOIL(keo)+ROOT(rsh)--ey`
  - **T4 (Cribs)**: `chockhy` = exact label `chockhy` [f68r1.12(@Ls), f73r.2(&Lz)]; `qoky` = exact label `oky` [f68r3.15(@Ls), f70v2.6(&Lz)]; `chor` = exact label `chor` [f99v.28(@Lf), f102v2.4(@Lf)]; `al` = exact label `al` [f69r.10(&L0)]
- **`<f115r.21,+P0>`** 
  - **T1 (EVA)**: `yches . oaiin . or,al . chy . cheody . rodaiin . cheockhy . oeeody <$>`
  - **T2 (Radicals)**: `y--[che]--s . [ain] . [or]--al . [ch]--y . [che]--ody . [ro+d]--ain . [cheo+ckh]--y . [e]--ody`
  - **T3 (Gloss)**: `INIT_NOM+ACT:infuse--s | NOM+ESSENCE/UNIT(ain) | NOM+JAR/HERB(or)--al | ACT:mix/proc--y | ACT:infuse--ody | ROOT(ro)+BASE/HUB(d)--ain | (cheo)+BALNEO_OP(ckh)--y | NOM+ESSENCE(e)--ody`
  - **T4 (Cribs)**: `chy` = exact label `chy` [f67r2.11(&L0), f70v2.14(&Lz)]; `cheody` = exact label `cheody` [f89r2.19(@Lf)]; `oeeody` = exact label `oeody` [f72v1.31(&Lz)]
- **`<f115r.22,+P0>`** [★L] 
  - **T1 (EVA)**: `<%> psheody . chsho . tchdy . dar . chedy . okchdar . chdor . cheedy . y . cheedy . qepchey . lkam`
  - **T2 (Radicals)**: `[t+she]--ody . [ch+sho] . [tch]--dy . [d]--ar . [ch]--edy . [kch+d]--ar . [chd]--or . [ch]--edy . [y] . [ch]--edy . q--[e+tch]--ey . [lk]--ar`
  - **T3 (Gloss)**: `TUBE/DUCT(t)+ACT:decoct--ody | ACT:mix/proc+(sho) | PROC_OP(tch)--dy | BASE/HUB(d)--ar | ACT:mix/proc--edy | NOM+STAR_OP(kch)+BASE/HUB(d)--ar | (chd)--or | ACT:mix/proc--edy | STATE(y) | ACT:mix/proc--edy | CONJ+ESSENCE(e)+PROC_OP(tch)--ey | LIQ_VESSEL(lk)--ar`
  - **T4 (Cribs)**: `dar` = exact label `dar` [f67v1.4(&L0), f69r.7(&L0)]; `okchdar` = exact label `okchdar` [fRos.99(@L0)]; `y` = exact label `y` [f66r.16(@L0), f66r.20(+L0)]
- **`<f115r.23,+P0>`** 
  - **T1 (EVA)**: `dchey,keey . qokeod . chody . qokcho . s . checthy . qokeeey . keeey . lol . chedy . qokchedy . ldy`
  - **T2 (Radicals)**: `[dche+yk]--ey . q--[keo]--d . [ch]--ody . q--[k+cho] . [s] . [che+cth]--y . q--[k]--ey . [k]--ey . [l]--ol . [ch]--edy . q--[kch]--edy . [l]--dy`
  - **T3 (Gloss)**: `ROOT(dche)+ROOT(yk)--ey | CONJ+NOM+PHARMA_BOIL(keo)--d | ACT:mix/proc--ody | CONJ+NOM+VESSEL/BODY(k)+(cho) | SEED/PART(s) | ACT:infuse+HERB_LEAF_OP(cth)--y | CONJ+NOM+VESSEL/BODY(k)--ey | VESSEL/BODY(k)--ey | LIQUID_PREF(l)--ol | ACT:mix/proc--edy | CONJ+NOM+STAR_OP(kch)--edy | LIQUID_PREF(l)--dy`
  - **T4 (Cribs)**: `qokeod` = exact label `okeod` [f73v.30(&Lz)]; `chody` = exact label `chody` [f89v2.12(@Lf)]; `s` = exact label `s` [f66r.18(+L0), f66r.35(+L0)]; `qokeeey` = exact label `okey` [f69r.8(&L0), f72r1.16(&Lz)]

### f111r:P3->P4 Tail-to-Head Catenated Pair (Lines 12-21)
- **`<f111r.12,+P0>`** 
  - **T1 (EVA)**: `dsheeo . qokeedy . otchedey . lshey . lkeedy . oteey . qokeedy . oteolair . ar . shedam . cheam`
  - **T2 (Radicals)**: `[d+sheo] . q--[k]--edy . [t+ched]--ey . [lsh]--ey . [lk]--edy . [t]--ey . q--[k]--edy . [te+ol+ai]--r . [ar] . [she+d]--ar . [che]--ar`
  - **T3 (Gloss)**: `BASE/HUB(d)+(sheo) | CONJ+NOM+VESSEL/BODY(k)--edy | NOM+TUBE/DUCT(t)+ROOT(ched)--ey | ROOT(lsh)--ey | LIQ_VESSEL(lk)--edy | NOM+TUBE/DUCT(t)--ey | CONJ+NOM+VESSEL/BODY(k)--edy | NOM+DRAW/CONDUIT(te)+FLUID/TUBE(ol)+(ai)--r | BOTAN/ROOT(ar) | ACT:decoct+BASE/HUB(d)--ar | ACT:infuse--ar`
  - **T4 (Cribs)**: `qokeedy` = exact label `okedy` [f72v1.28(&Lz), f73r.11(&Lz)]; `otchedey` = exact label `otchedey` [f89v2.14(@Lf)]; `oteey` = exact label `otey` [f72v3.14(&Lz), f73r.21(&Lz)]; `qokeedy` = exact label `okedy` [f72v1.28(&Lz), f73r.11(&Lz)]; `ar` = exact label `ar` [f69r.6(&L0), f69r.14(&L0)]
- **`<f111r.13,+P0>`** 
  - **T1 (EVA)**: `qosheo . lchdy . lshedy . olkeeedy . lr . al . chr . or,dain . shey . arain . chey . teey . cheodaiin`
  - **T2 (Radicals)**: `q--[sheo] . [lch]--dy . [lsh]--edy . [olk]--edy . [l]--r . [al] . [ch]--r . [or+d]--ain . [sh]--ey . [ar]--ain . [ch]--ey . [t]--ey . [cheo+d]--ain`
  - **T3 (Gloss)**: `CONJ+NOM+(sheo) | LIQ_MIX(lch)--dy | ROOT(lsh)--edy | NOM+(olk)--edy | LIQUID_PREF(l)--r | SUBST/STAR(al) | ACT:mix/proc--r | NOM+JAR/HERB(or)+BASE/HUB(d)--ain | ACT:heat/steep--ey | BOTAN/ROOT(ar)--ain | ACT:mix/proc--ey | TUBE/DUCT(t)--ey | (cheo)+BASE/HUB(d)--ain`
  - **T4 (Cribs)**: `lchdy` = exact label `lchdy` [fRos.151(+L0)]; `olkeeedy` = exact label `olkedy` [f82v.39(@Ln)]; `al` = exact label `al` [f69r.10(&L0)]; `shey` = exact label `shey` [f68r2.29(@Ls), f116v.1(@Lx)]
- **`<f111r.14,+P0>`** 
  - **T1 (EVA)**: `dchedar . oteey . lchey . ykeeeos . aiin . shear . oteedy . tedam . oteey . pchedey . chedy . lchedy`
  - **T2 (Radicals)**: `[d+ched]--ar . [t]--ey . [lch]--ey . y--[keo]--s . [ain] . [she]--ar . [t]--edy . [te+d]--ar . [t]--ey . [t+ched]--ey . [ch]--edy . [lch]--edy`
  - **T3 (Gloss)**: `BASE/HUB(d)+ROOT(ched)--ar | NOM+TUBE/DUCT(t)--ey | LIQ_MIX(lch)--ey | INIT_NOM+PHARMA_BOIL(keo)--s | ESSENCE/UNIT(ain) | ACT:decoct--ar | NOM+TUBE/DUCT(t)--edy | DRAW/CONDUIT(te)+BASE/HUB(d)--ar | NOM+TUBE/DUCT(t)--ey | TUBE/DUCT(t)+ROOT(ched)--ey | ACT:mix/proc--edy | LIQ_MIX(lch)--edy`
  - **T4 (Cribs)**: `oteey` = exact label `otey` [f72v3.14(&Lz), f73r.21(&Lz)]; `aiin` = exact label `ain` [f99r.7(+Lf)]; `oteedy` = exact label `otedy` [f73r.3(&Lz), f73v.3(&Lz)]; `oteey` = exact label `otey` [f72v3.14(&Lz), f73r.21(&Lz)]
- **`<f111r.15,+P0>`** 
  - **T1 (EVA)**: `sheeodar . aiin . sheey . shey . oteody . oteedy . chey . daiin . oteol . otedar . tar . pchdam`
  - **T2 (Radicals)**: `[sheo+d]--ar . [ain] . [sh]--ey . [sh]--ey . [te]--ody . [t]--edy . [ch]--ey . [d]--ain . [te]--ol . [te+d]--ar . [t]--ar . [tch+d]--ar`
  - **T3 (Gloss)**: `(sheo)+BASE/HUB(d)--ar | ESSENCE/UNIT(ain) | ACT:heat/steep--ey | ACT:heat/steep--ey | NOM+DRAW/CONDUIT(te)--ody | NOM+TUBE/DUCT(t)--edy | ACT:mix/proc--ey | BASE/HUB(d)--ain | NOM+DRAW/CONDUIT(te)--ol | NOM+DRAW/CONDUIT(te)+BASE/HUB(d)--ar | TUBE/DUCT(t)--ar | PROC_OP(tch)+BASE/HUB(d)--ar`
  - **T4 (Cribs)**: `aiin` = exact label `ain` [f99r.7(+Lf)]; `sheey` = exact label `shey` [f68r2.29(@Ls), f116v.1(@Lx)]; `shey` = exact label `shey` [f68r2.29(@Ls), f116v.1(@Lx)]; `oteody` = exact label `oteody` [f73v.2(&Lz), f73v.13(&Lz)]; `oteedy` = exact label `otedy` [f73r.3(&Lz), f73v.3(&Lz)]; `daiin` = exact label `dain` [f67r2.56(&Ls)]
- **`<f111r.16,+P0>`** 
  - **T1 (EVA)**: `dchedshey . qokeedy . okeodain . shet . sheota . oteal,tey . lkeey . sheedy . shtar . keedy`
  - **T2 (Radicals)**: `[dche+dsh]--ey . q--[k]--edy . [keo+d]--ain . [she+t] . [sheo+ta] . [te+al+t]--ey . [lk]--ey . [sh]--edy . [sht]--ar . [k]--edy`
  - **T3 (Gloss)**: `ROOT(dche)+ROOT(dsh)--ey | CONJ+NOM+VESSEL/BODY(k)--edy | NOM+PHARMA_BOIL(keo)+BASE/HUB(d)--ain | ACT:decoct+TUBE/DUCT(t) | (sheo)+ROOT(ta) | NOM+DRAW/CONDUIT(te)+SUBST/STAR(al)+TUBE/DUCT(t)--ey | LIQ_VESSEL(lk)--ey | ACT:heat/steep--edy | ROOT(sht)--ar | VESSEL/BODY(k)--edy`
  - **T4 (Cribs)**: `qokeedy` = exact label `okedy` [f72v1.28(&Lz), f73r.11(&Lz)]; `shet` = exact label `shet` [fRos.158(@L0)]
- **`<f111r.17,+P0>`** 
  - **T1 (EVA)**: `otes . lchey . lshedy . qoteedy . olcheody . qokeey . chey . kal . chekeedy . oteed . keedy . otam`
  - **T2 (Radicals)**: `[te]--s . [lch]--ey . [lsh]--edy . q--[t]--edy . [ol+che]--ody . q--[k]--ey . [ch]--ey . [k]--al . [che+k]--edy . [te]--d . [k]--edy . [t]--ar`
  - **T3 (Gloss)**: `NOM+DRAW/CONDUIT(te)--s | LIQ_MIX(lch)--ey | ROOT(lsh)--edy | CONJ+NOM+TUBE/DUCT(t)--edy | NOM+FLUID/TUBE(ol)+ACT:infuse--ody | CONJ+NOM+VESSEL/BODY(k)--ey | ACT:mix/proc--ey | VESSEL/BODY(k)--al | ACT:infuse+VESSEL/BODY(k)--edy | NOM+DRAW/CONDUIT(te)--d | VESSEL/BODY(k)--edy | NOM+TUBE/DUCT(t)--ar`
  - **T4 (Cribs)**: `qoteedy` = exact label `otedy` [f73r.3(&Lz), f73v.3(&Lz)]; `qokeey` = exact label `okey` [f69r.8(&L0), f72r1.16(&Lz)]; `oteed` = exact label `oted` [f75v.33(+Ln)]; `otam` = exact label `otar` [f70v2.4(&Lz), f70v2.22(@Lz)]
- **`<f111r.18,+P0>`** 
  - **T1 (EVA)**: `daiin . shecthey . oteody . qochey . qokeey . chey . teey . qokeedy . qokeedy . cheol . lokeedy . lched`
  - **T2 (Radicals)**: `[d]--ain . [she+cth]--ey . [te]--ody . q--[ch]--ey . q--[k]--ey . [ch]--ey . [t]--ey . q--[k]--edy . q--[k]--edy . [che]--ol . [lo+k]--edy . [l+che]--d`
  - **T3 (Gloss)**: `BASE/HUB(d)--ain | ACT:decoct+HERB_LEAF_OP(cth)--ey | NOM+DRAW/CONDUIT(te)--ody | CONJ+NOM+ACT:mix/proc--ey | CONJ+NOM+VESSEL/BODY(k)--ey | ACT:mix/proc--ey | TUBE/DUCT(t)--ey | CONJ+NOM+VESSEL/BODY(k)--edy | CONJ+NOM+VESSEL/BODY(k)--edy | ACT:infuse--ol | ROOT(lo)+VESSEL/BODY(k)--edy | LIQUID_PREF(l)+ACT:infuse--d`
  - **T4 (Cribs)**: `daiin` = exact label `dain` [f67r2.56(&Ls)]; `oteody` = exact label `oteody` [f73v.2(&Lz), f73v.13(&Lz)]; `qokeey` = exact label `okey` [f69r.8(&L0), f72r1.16(&Lz)]; `qokeedy` = exact label `okedy` [f72v1.28(&Lz), f73r.11(&Lz)]; `qokeedy` = exact label `okedy` [f72v1.28(&Lz), f73r.11(&Lz)]
- **`<f111r.19,+P0>`** 
  - **T1 (EVA)**: `saiin . okeeol . qokeedy . lchey . lcheoekam . oaiin . cheky . qokeeodar . checthdy . qoted,l . loty`
  - **T2 (Radicals)**: `[s]--ain . [ke]--ol . q--[k]--edy . [lch]--ey . [l+cheo+ek]--ar . [ain] . [che+k]--y . q--[keo+d]--ar . [che+cth]--dy . q--[te+d]--l . [lo+t]--y`
  - **T3 (Gloss)**: `SEED/PART(s)--ain | NOM+EXTRACT/COOK(ke)--ol | CONJ+NOM+VESSEL/BODY(k)--edy | LIQ_MIX(lch)--ey | LIQUID_PREF(l)+(cheo)+DISTILL(ek)--ar | NOM+ESSENCE/UNIT(ain) | ACT:infuse+VESSEL/BODY(k)--y | CONJ+NOM+PHARMA_BOIL(keo)+BASE/HUB(d)--ar | ACT:infuse+HERB_LEAF_OP(cth)--dy | CONJ+NOM+DRAW/CONDUIT(te)+BASE/HUB(d)--l | ROOT(lo)+TUBE/DUCT(t)--y`
  - **T4 (Cribs)**: `saiin` = exact label `sain` [f66r.12(+L0)]; `okeeol` = exact label `okeol` [f72v3.16(&Lz), f72v1.32(&Lz)]; `qokeedy` = exact label `okedy` [f72v1.28(&Lz), f73r.11(&Lz)]; `cheky` = exact label `cheky` [f73r.27(&Lz), fRos.160(+L0)]
- **`<f111r.20,+P0>`** 
  - **T1 (EVA)**: `qokeey . qokeey . lchedy . checthy . chedey . cheol . teedy . okeedy . qokeedy . okeey . cho,ol . l,kai@175;`
  - **T2 (Radicals)**: `q--[k]--ey . q--[k]--ey . [lch]--edy . [che+cth]--y . [che+d]--ey . [che]--ol . [t]--edy . [k]--edy . q--[k]--edy . [k]--ey . [ch]--ol . [lk+ai+@1+7+5+;]`
  - **T3 (Gloss)**: `CONJ+NOM+VESSEL/BODY(k)--ey | CONJ+NOM+VESSEL/BODY(k)--ey | LIQ_MIX(lch)--edy | ACT:infuse+HERB_LEAF_OP(cth)--y | ACT:infuse+BASE/HUB(d)--ey | ACT:infuse--ol | TUBE/DUCT(t)--edy | NOM+VESSEL/BODY(k)--edy | CONJ+NOM+VESSEL/BODY(k)--edy | NOM+VESSEL/BODY(k)--ey | ACT:mix/proc--ol | LIQ_VESSEL(lk)+(ai)+ROOT(@1)+ROOT(7)+ROOT(5)+ROOT(;)`
  - **T4 (Cribs)**: `qokeey` = exact label `okey` [f69r.8(&L0), f72r1.16(&Lz)]; `qokeey` = exact label `okey` [f69r.8(&L0), f72r1.16(&Lz)]; `okeedy` = exact label `okedy` [f72v1.28(&Lz), f73r.11(&Lz)]; `qokeedy` = exact label `okedy` [f72v1.28(&Lz), f73r.11(&Lz)]; `okeey` = exact label `okey` [f69r.8(&L0), f72r1.16(&Lz)]; `cho,ol` = exact label `chol` [f68r2.25(@Ls)]
- **`<f111r.21,+P0>`** 
  - **T1 (EVA)**: `daiin . okar . ain . teey . oteey . ox,o,r,shey . chey,ky,deedy . cheo . dain . sheet . ar . al,l . cheotydy`
  - **T2 (Radicals)**: `[d]--ain . [k]--ar . [ain] . [t]--ey . [t]--ey . [x+or+sh]--ey . [che+yk+yd]--edy . [cheo] . [d]--ain . [she+t] . [ar] . [al]--l . [cheo+ty]--dy`
  - **T3 (Gloss)**: `BASE/HUB(d)--ain | NOM+VESSEL/BODY(k)--ar | ESSENCE/UNIT(ain) | TUBE/DUCT(t)--ey | NOM+TUBE/DUCT(t)--ey | NOM+ROOT(x)+JAR/HERB(or)+ACT:heat/steep--ey | ACT:infuse+ROOT(yk)+ROOT(yd)--edy | (cheo) | BASE/HUB(d)--ain | ACT:decoct+TUBE/DUCT(t) | BOTAN/ROOT(ar) | SUBST/STAR(al)--l | (cheo)+ROOT(ty)--dy`
  - **T4 (Cribs)**: `daiin` = exact label `dain` [f67r2.56(&Ls)]; `okar` = exact label `okar` [f67r2.3(&L0), f67r2.10(&L0)]; `ain` = exact label `ain` [f99r.7(+Lf)]; `oteey` = exact label `otey` [f72v3.14(&Lz), f73r.21(&Lz)]; `dain` = exact label `dain` [f67r2.56(&Ls)]; `sheet` = exact label `shet` [fRos.158(@L0)]

---

## 3. The Rosettes-Anchored Herbal Treatise (`f48v`, Lines 7-11)
Paragraph 2 of Herbal folio `f48v` (`Hand 1, Language A`), where line `<f48v.9,+P0>` splits across the central flower stalk (`<->`) and cites the exact 2-word Cosmological Rosettes label `<fRos.45,+L0> otchdy . otoldy` (`19.53` rarity bits) followed two words later by `otedy` (`<fRos.72> otedain . otedy`).

### f48v Paragraph 2 (Lines 7-11)
- **`<f48v.7,+P0>`** 
  - **T1 (EVA)**: `<%> pchedar . chey . ypchedy . otedy . shef,eeedy . al . shedy . otedy . fcheodal . cpheeg`
  - **T2 (Radicals)**: `[t+ched]--ar . [ch]--ey . y--[tch]--edy . [t]--edy . [she+k]--edy . [al] . [sh]--edy . [t]--edy . [kch+eod]--al . [cth+eg]`
  - **T3 (Gloss)**: `TUBE/DUCT(t)+ROOT(ched)--ar | ACT:mix/proc--ey | INIT_NOM+PROC_OP(tch)--edy | NOM+TUBE/DUCT(t)--edy | ACT:decoct+VESSEL/BODY(k)--edy | SUBST/STAR(al) | ACT:heat/steep--edy | NOM+TUBE/DUCT(t)--edy | STAR_OP(kch)+ROOT(eod)--al | HERB_LEAF_OP(cth)+ROOT(eg)`
  - **T4 (Cribs)**: `otedy` = exact label `otedy` [f73r.3(&Lz), f73v.3(&Lz)]; `al` = exact label `al` [f69r.10(&L0)]; `otedy` = exact label `otedy` [f73r.3(&Lz), f73v.3(&Lz)]
- **`<f48v.8,+P0>`** 
  - **T1 (EVA)**: `oteody . chkey . okedy . chckhedy . ykedy . oldy . otoly . chey . kaly . tokar . otam`
  - **T2 (Radicals)**: `[te]--ody . [chk]--ey . [k]--edy . [ch+ckh]--edy . y--[k]--edy . [ol]--dy . [t]--oly . [ch]--ey . [k]--aly . [to+k]--ar . [t]--ar`
  - **T3 (Gloss)**: `NOM+DRAW/CONDUIT(te)--ody | (chk)--ey | NOM+VESSEL/BODY(k)--edy | ACT:mix/proc+BALNEO_OP(ckh)--edy | INIT_NOM+VESSEL/BODY(k)--edy | NOM+FLUID/TUBE(ol)--dy | NOM+TUBE/DUCT(t)--oly | ACT:mix/proc--ey | VESSEL/BODY(k)--aly | SPOKE/RAY(to)+VESSEL/BODY(k)--ar | NOM+TUBE/DUCT(t)--ar`
  - **T4 (Cribs)**: `oteody` = exact label `oteody` [f73v.2(&Lz), f73v.13(&Lz)]; `okedy` = exact label `okedy` [f72v1.28(&Lz), f73r.11(&Lz)]; `ykedy` = exact label `ykedy` [f72v1.21(&Lz), f73r.9(&Lz)]; `oldy` = exact label `oldy` [f99v.4(@Lf)]; `otoly` = exact label `otoly` [f72v3.10(&Lz), f75v.37(+Ln)]; `otam` = exact label `otar` [f70v2.4(&Lz), f70v2.22(@Lz)]
- **`<f48v.9,+P0>`** 
  - **T1 (EVA)**: `tor . shody . okal . otchedy . cheky . oly . loldy . lol . otchdy . otoldy . ytam . otedy`
  - **T2 (Radicals)**: `[t]--or . [sh]--ody . [k]--al . [tch]--edy . [che+k]--y . [ol+y] . [l+ol]--dy . [l]--ol . [tch]--dy . [t+ol]--dy . y--[t]--ar . [t]--edy`
  - **T3 (Gloss)**: `TUBE/DUCT(t)--or | ACT:heat/steep--ody | NOM+VESSEL/BODY(k)--al | NOM+PROC_OP(tch)--edy | ACT:infuse+VESSEL/BODY(k)--y | NOM+FLUID/TUBE(ol)+STATE(y) | LIQUID_PREF(l)+FLUID/TUBE(ol)--dy | LIQUID_PREF(l)--ol | NOM+PROC_OP(tch)--dy | NOM+TUBE/DUCT(t)+FLUID/TUBE(ol)--dy | INIT_NOM+TUBE/DUCT(t)--ar | NOM+TUBE/DUCT(t)--edy`
  - **T4 (Cribs)**: `otchdy . otoldy` == Diagram Label `otchdy . otoldy` (fRos.45(2W-LABEL)); `okal` = exact label `okal` [f66r.13(+L0), f67r2.22(+L0)]; `cheky` = exact label `cheky` [f73r.27(&Lz), fRos.160(+L0)]; `oly` = exact label `oly` [f69r.16(&L0)]; `otchdy` = exact label `otchdy` [f67v2.1(@La), f68r1.23(@Ls)]; `otoldy` = exact label `otoldy` [fRos.45(@L0), f89r1.4(@Lf)]
- **`<f48v.10,+P0>`** 
  - **T1 (EVA)**: `tol . chedy . ytedy . ykeol . chdy . chdor . chtol . chdy . ytchedal . cthey . okar,ar . ary`
  - **T2 (Radicals)**: `[t]--ol . [ch]--edy . y--[t]--edy . y--[ke]--ol . [ch]--dy . [chd]--or . [cht]--ol . [ch]--dy . y--[t+ched]--al . [cth]--ey . [k+ar]--ar . [ar+y]`
  - **T3 (Gloss)**: `TUBE/DUCT(t)--ol | ACT:mix/proc--edy | INIT_NOM+TUBE/DUCT(t)--edy | INIT_NOM+EXTRACT/COOK(ke)--ol | ACT:mix/proc--dy | (chd)--or | ROOT(cht)--ol | ACT:mix/proc--dy | INIT_NOM+TUBE/DUCT(t)+ROOT(ched)--al | HERB_LEAF_OP(cth)--ey | NOM+VESSEL/BODY(k)+BOTAN/ROOT(ar)--ar | BOTAN/ROOT(ar)+STATE(y)`
  - **T4 (Cribs)**: `tol` = exact label `tol` [f67r2.56(&Ls)]; `ytedy` = exact label `ytedy` [f72v2.30(&Lz)]; `ykeol` = exact label `ykeol` [f66r.5(+L0)]; `chdy` = exact label `chdy` [f69r.14(&L0), f73r.17(&Lz)]; `chdy` = exact label `chdy` [f69r.14(&L0), f73r.17(&Lz)]; `cthey` = exact label `cthey` [f67r2.66(&L0)]
- **`<f48v.11,+P0>`** 
  - **T1 (EVA)**: `ykeedal . chckhy . ykal . y,tam . or . cheedls . sary <$>`
  - **T2 (Radicals)**: `y--[ke+d]--al . [ch+ckh]--y . y--[k]--al . y--[t]--ar . [or] . [ched+l]--s . [s]--ary`
  - **T3 (Gloss)**: `INIT_NOM+EXTRACT/COOK(ke)+BASE/HUB(d)--al | ACT:mix/proc+BALNEO_OP(ckh)--y | INIT_NOM+VESSEL/BODY(k)--al | INIT_NOM+TUBE/DUCT(t)--ar | NOM+JAR/HERB(or) | ROOT(ched)+LIQUID_PREF(l)--s | SEED/PART(s)--ary`
  - **T4 (Cribs)**: `ykal` = exact label `ykal` [f77v.1(@Lt)]; `or` = exact label `or` [f66r.3(+L0), f84r.2(@Ln)]; `sary` = exact label `sary` [f67v2.20(+La), f99v.17(@Lf)]

---

## 4. The First Crimson-Star Triad (`D -> L_1 -> L_2`) on `f103r` (Paragraphs 1-3, Lines 1-11)
Illustrates the 3-part functional division of the Crimson-Star (`D -> L -> L`) triads on `f103r`: Slot 1 (`★D`, Master Recipe) introduces the core preparation; Slot 2 (`★L`, First Follower) expands nominal/ingredient quantities (`-aiin`); Slot 3 (`★L`, Second Follower) executes high-density verbal actions (`-edy/-dy`).

### f103r Triad 1: P1 (★D), P2 (★L), P3 (★L) (Lines 1-11)
- **`<f103r.1,@P0>`** [★D] 
  - **T1 (EVA)**: `<%> pchedal . shdy . ytechypchy . otey . lshey . qoteey . qotal . shedy . yshdal . dain . okal . daldy`
  - **T2 (Radicals)**: `[t+ched]--al . [sh]--dy . y--[te+chy+tch]--y . [t]--ey . [lsh]--ey . q--[t]--ey . q--[t]--al . [sh]--edy . y--[shd]--al . [d]--ain . [k]--al . [d+al]--dy`
  - **T3 (Gloss)**: `TUBE/DUCT(t)+ROOT(ched)--al | ACT:heat/steep--dy | INIT_NOM+DRAW/CONDUIT(te)+ROOT(chy)+PROC_OP(tch)--y | NOM+TUBE/DUCT(t)--ey | ROOT(lsh)--ey | CONJ+NOM+TUBE/DUCT(t)--ey | CONJ+NOM+TUBE/DUCT(t)--al | ACT:heat/steep--edy | INIT_NOM+ROOT(shd)--al | BASE/HUB(d)--ain | NOM+VESSEL/BODY(k)--al | BASE/HUB(d)+SUBST/STAR(al)--dy`
  - **T4 (Cribs)**: `shdy` = exact label `shdy` [fRos.66(@L0)]; `otey` = exact label `otey` [f72v3.14(&Lz), f73r.21(&Lz)]; `qoteey` = exact label `otey` [f72v3.14(&Lz), f73r.21(&Lz)]; `qotal` = exact label `otal` [f70v2.16(&Lz), f70v1.11(&Lz)]; `dain` = exact label `dain` [f67r2.56(&Ls)]; `okal` = exact label `okal` [f66r.13(+L0), f67r2.22(+L0)]
- **`<f103r.2,+P0>`** 
  - **T1 (EVA)**: `dain . shek . chdy . daloky . opchedy . peshol . chep . ar . otchy . sal . lkeey . sar . ain . ok . chedy`
  - **T2 (Radicals)**: `[d]--ain . [she+k] . [ch]--dy . [dal+ok]--y . [tch]--edy . [te+sh]--ol . [che+t] . [ar] . [tch]--y . [s]--al . [lk]--ey . [s]--ar . [ain] . [ok] . [ch]--edy`
  - **T3 (Gloss)**: `BASE/HUB(d)--ain | ACT:decoct+VESSEL/BODY(k) | ACT:mix/proc--dy | BASIN/PORTION(dal)+VESSEL_NOM(ok)--y | NOM+PROC_OP(tch)--edy | DRAW/CONDUIT(te)+ACT:heat/steep--ol | ACT:infuse+TUBE/DUCT(t) | BOTAN/ROOT(ar) | NOM+PROC_OP(tch)--y | SEED/PART(s)--al | LIQ_VESSEL(lk)--ey | SEED/PART(s)--ar | ESSENCE/UNIT(ain) | NOM+VESSEL_NOM(ok) | ACT:mix/proc--edy`
  - **T4 (Cribs)**: `dain` = exact label `dain` [f67r2.56(&Ls)]; `chdy` = exact label `chdy` [f69r.14(&L0), f73r.17(&Lz)]; `ar` = exact label `ar` [f69r.6(&L0), f69r.14(&L0)]; `otchy` = exact label `otchy` [f102v2.13(@Lf)]; `sal` = exact label `sal` [f70v1.3(&Lz)]; `ain` = exact label `ain` [f99r.7(+Lf)]
- **`<f103r.3,+P0>`** 
  - **T1 (EVA)**: `yshdain . sheek . cheoty . eeokal . chedy . chckhy . or . orol . okaiin . eeal . ot . kar . otar . chal`
  - **T2 (Radicals)**: `y--[shd]--ain . [she+k] . [cheo+t]--y . [eok]--al . [ch]--edy . [ch+ckh]--y . [or] . [or]--ol . [k]--ain . [e]--al . [ot] . [k]--ar . [t]--ar . [ch]--al`
  - **T3 (Gloss)**: `INIT_NOM+ROOT(shd)--ain | ACT:decoct+VESSEL/BODY(k) | (cheo)+TUBE/DUCT(t)--y | ROOT(eok)--al | ACT:mix/proc--edy | ACT:mix/proc+BALNEO_OP(ckh)--y | NOM+JAR/HERB(or) | NOM+JAR/HERB(or)--ol | NOM+VESSEL/BODY(k)--ain | ESSENCE(e)--al | NOM+DUCT_NOM(ot) | VESSEL/BODY(k)--ar | NOM+TUBE/DUCT(t)--ar | ACT:mix/proc--al`
  - **T4 (Cribs)**: `or` = exact label `or` [f66r.3(+L0), f84r.2(@Ln)]; `orol` = exact label `orol` [f100r.18(@Lf)]; `okaiin` = exact label `okain` [f67r2.28(+L0), f72r3.12(&Lz)]; `kar` = exact label `kar` [f73r.31(&Lz)]; `otar` = exact label `otar` [f70v2.4(&Lz), f70v2.22(@Lz)]
- **`<f103r.4,+P0>`** 
  - **T1 (EVA)**: `ychedy . qokedy . okedy . qokeey . okey . chdar,ol . loty . chedaraly <$>`
  - **T2 (Radicals)**: `y--[ch]--edy . q--[k]--edy . [k]--edy . q--[k]--ey . [k]--ey . [ch+dar]--ol . [lo+t]--y . [ched+ar]--aly`
  - **T3 (Gloss)**: `INIT_NOM+ACT:mix/proc--edy | CONJ+NOM+VESSEL/BODY(k)--edy | NOM+VESSEL/BODY(k)--edy | CONJ+NOM+VESSEL/BODY(k)--ey | NOM+VESSEL/BODY(k)--ey | ACT:mix/proc+JAR/ROOT_SRC(dar)--ol | ROOT(lo)+TUBE/DUCT(t)--y | ROOT(ched)+BOTAN/ROOT(ar)--aly`
  - **T4 (Cribs)**: `qokedy` = exact label `okedy` [f72v1.28(&Lz), f73r.11(&Lz)]; `okedy` = exact label `okedy` [f72v1.28(&Lz), f73r.11(&Lz)]; `qokeey` = exact label `okey` [f69r.8(&L0), f72r1.16(&Lz)]; `okey` = exact label `okey` [f69r.8(&L0), f72r1.16(&Lz)]
- **`<f103r.5,+P0>`** [★L] 
  - **T1 (EVA)**: `<%> pocharal . okedar . shedy . oteey . qokey . lkar . sheeky . okalor . shedy . yt . rkar . ota . okdy`
  - **T2 (Radicals)**: `[to+ch+ar]--al . [ke+d]--ar . [sh]--edy . [t]--ey . q--[k]--ey . [lk]--ar . [she+k]--y . [k+al]--or . [sh]--edy . [yt] . [r+k]--ar . [ta] . [k]--dy`
  - **T3 (Gloss)**: `SPOKE/RAY(to)+ACT:mix/proc+BOTAN/ROOT(ar)--al | NOM+EXTRACT/COOK(ke)+BASE/HUB(d)--ar | ACT:heat/steep--edy | NOM+TUBE/DUCT(t)--ey | CONJ+NOM+VESSEL/BODY(k)--ey | LIQ_VESSEL(lk)--ar | ACT:decoct+VESSEL/BODY(k)--y | NOM+VESSEL/BODY(k)+SUBST/STAR(al)--or | ACT:heat/steep--edy | ROOT(yt) | STREAM/PART(r)+VESSEL/BODY(k)--ar | NOM+ROOT(ta) | NOM+VESSEL/BODY(k)--dy`
  - **T4 (Cribs)**: `oteey` = exact label `otey` [f72v3.14(&Lz), f73r.21(&Lz)]; `qokey` = exact label `okey` [f69r.8(&L0), f72r1.16(&Lz)]; `yt` = exact label `yt` [f69r.12(&L0)]
- **`<f103r.6,+P0>`** 
  - **T1 (EVA)**: `ocheey . dain . shek . okeedy . okey . shedy . qokealdy . shcthy . qotedy . qoto . ota . san,am`
  - **T2 (Radicals)**: `[ch]--ey . [d]--ain . [she+k] . [k]--edy . [k]--ey . [sh]--edy . q--[ke+al]--dy . [sh+cth]--y . q--[t]--edy . q--[to] . [ta] . [s+an]--ar`
  - **T3 (Gloss)**: `NOM+ACT:mix/proc--ey | BASE/HUB(d)--ain | ACT:decoct+VESSEL/BODY(k) | NOM+VESSEL/BODY(k)--edy | NOM+VESSEL/BODY(k)--ey | ACT:heat/steep--edy | CONJ+NOM+EXTRACT/COOK(ke)+SUBST/STAR(al)--dy | ACT:heat/steep+HERB_LEAF_OP(cth)--y | CONJ+NOM+TUBE/DUCT(t)--edy | CONJ+NOM+SPOKE/RAY(to) | NOM+ROOT(ta) | SEED/PART(s)+ROOT(an)--ar`
  - **T4 (Cribs)**: `dain` = exact label `dain` [f67r2.56(&Ls)]; `okeedy` = exact label `okedy` [f72v1.28(&Lz), f73r.11(&Lz)]; `okey` = exact label `okey` [f69r.8(&L0), f72r1.16(&Lz)]; `qotedy` = exact label `otedy` [f73r.3(&Lz), f73v.3(&Lz)]; `qoto` = exact label `oto` [f69r.7(&L0)]
- **`<f103r.7,+P0>`** 
  - **T1 (EVA)**: `saiin . chey . shs . olshedy . qokeey . okeeody . qoedy . ol,shedy <$>`
  - **T2 (Radicals)**: `[s]--ain . [ch]--ey . [sh]--s . [ol+sh]--edy . q--[k]--ey . [ke]--ody . q--[e+dy] . [ol+sh]--edy`
  - **T3 (Gloss)**: `SEED/PART(s)--ain | ACT:mix/proc--ey | ACT:heat/steep--s | NOM+FLUID/TUBE(ol)+ACT:heat/steep--edy | CONJ+NOM+VESSEL/BODY(k)--ey | NOM+EXTRACT/COOK(ke)--ody | CONJ+NOM+ESSENCE(e)+DONE(dy) | NOM+FLUID/TUBE(ol)+ACT:heat/steep--edy`
  - **T4 (Cribs)**: `saiin` = exact label `sain` [f66r.12(+L0)]; `shs` = exact label `shs` [f67r2.3(&L0)]; `qokeey` = exact label `okey` [f69r.8(&L0), f72r1.16(&Lz)]; `okeeody` = exact label `okeody` [f68r2.18(@Ls), f72v2.15(&Lz)]; `qoedy` = exact label `oedy` [f72v3.25(&Lz), f72v2.23(&Lz)]
- **`<f103r.8,+P0>`** [★L] 
  - **T1 (EVA)**: `<%> daroal . okey . chedy . okey . rain . okechy . qoisal . qotar,adchey . ofeeo . ltdy . olkechdy,lo`
  - **T2 (Radicals)**: `[dar+o]--al . [k]--ey . [ch]--edy . [k]--ey . [r]--ain . [ke+ch]--y . q--[i+s]--al . q--[tar+a+dch]--ey . [keo] . [lt]--dy . [ol+kech+dy+lo]`
  - **T3 (Gloss)**: `JAR/ROOT_SRC(dar)+ENTITY_CORE(o)--al | NOM+VESSEL/BODY(k)--ey | ACT:mix/proc--edy | NOM+VESSEL/BODY(k)--ey | STREAM/PART(r)--ain | NOM+EXTRACT/COOK(ke)+ACT:mix/proc--y | CONJ+NOM+ROOT(i)+SEED/PART(s)--al | CONJ+NOM+ROOT_EARTH(tar)+HUB_AXIS(a)+(dch)--ey | NOM+PHARMA_BOIL(keo) | ROOT(lt)--dy | NOM+FLUID/TUBE(ol)+ROOT(kech)+DONE(dy)+ROOT(lo)`
  - **T4 (Cribs)**: `okey` = exact label `okey` [f69r.8(&L0), f72r1.16(&Lz)]; `okey` = exact label `okey` [f69r.8(&L0), f72r1.16(&Lz)]; `okechy` = exact label `okechy` [f99v.26(@Lf)]
- **`<f103r.9,+P0>`** 
  - **T1 (EVA)**: `oteeos . ar . cheal . okeey . shey . lkaiin . shey . lkeor . otaiin . shedy . otey . l . dy . okeedaram`
  - **T2 (Radicals)**: `[teo]--s . [ar] . [che]--al . [k]--ey . [sh]--ey . [lk]--ain . [sh]--ey . [l+ke]--or . [t]--ain . [sh]--edy . [t]--ey . [l] . [dy] . [ked+ar]--ar`
  - **T3 (Gloss)**: `NOM+ZOD_CONTAIN(teo)--s | BOTAN/ROOT(ar) | ACT:infuse--al | NOM+VESSEL/BODY(k)--ey | ACT:heat/steep--ey | LIQ_VESSEL(lk)--ain | ACT:heat/steep--ey | LIQUID_PREF(l)+EXTRACT/COOK(ke)--or | NOM+TUBE/DUCT(t)--ain | ACT:heat/steep--edy | NOM+TUBE/DUCT(t)--ey | LIQUID_PREF(l) | DONE(dy) | NOM+ROOT(ked)+BOTAN/ROOT(ar)--ar`
  - **T4 (Cribs)**: `oteeos` = exact label `oteos` [f69r.5(@L0), f71r.2(@Lz)]; `ar` = exact label `ar` [f69r.6(&L0), f69r.14(&L0)]; `okeey` = exact label `okey` [f69r.8(&L0), f72r1.16(&Lz)]; `shey` = exact label `shey` [f68r2.29(@Ls), f116v.1(@Lx)]; `shey` = exact label `shey` [f68r2.29(@Ls), f116v.1(@Lx)]; `otaiin` = exact label `otain` [f71v.7(&Lz), f72r1.9(&Lz)]
- **`<f103r.10,+P0>`** 
  - **T1 (EVA)**: `daiin . ol . oain . okeol . chol . okam . chety . shedy . otaiin . shedy . teolshy . oteedy . sor,ain`
  - **T2 (Radicals)**: `[d]--ain . [ol] . [ain] . [ke]--ol . [ch]--ol . [k]--ar . [che+t]--y . [sh]--edy . [t]--ain . [sh]--edy . [te+olsh]--y . [t]--edy . [s+or]--ain`
  - **T3 (Gloss)**: `BASE/HUB(d)--ain | NOM+FLUID/TUBE(ol) | NOM+ESSENCE/UNIT(ain) | NOM+EXTRACT/COOK(ke)--ol | ACT:mix/proc--ol | NOM+VESSEL/BODY(k)--ar | ACT:infuse+TUBE/DUCT(t)--y | ACT:heat/steep--edy | NOM+TUBE/DUCT(t)--ain | ACT:heat/steep--edy | DRAW/CONDUIT(te)+ROOT(olsh)--y | NOM+TUBE/DUCT(t)--edy | SEED/PART(s)+JAR/HERB(or)--ain`
  - **T4 (Cribs)**: `daiin` = exact label `dain` [f67r2.56(&Ls)]; `okeol` = exact label `okeol` [f72v3.16(&Lz), f72v1.32(&Lz)]; `chol` = exact label `chol` [f68r2.25(@Ls)]; `okam` = exact label `okar` [f67r2.3(&L0), f67r2.10(&L0)]; `otaiin` = exact label `otain` [f71v.7(&Lz), f72r1.9(&Lz)]; `oteedy` = exact label `otedy` [f73r.3(&Lz), f73v.3(&Lz)]
- **`<f103r.11,+P0>`** 
  - **T1 (EVA)**: `dar . oteey . otain . lolshedy . okain . chey . qorain . shey . otoy . qokeol . key . dayky`
  - **T2 (Radicals)**: `[d]--ar . [t]--ey . [t]--ain . [l+olsh]--edy . [k]--ain . [ch]--ey . q--[or]--ain . [sh]--ey . [to]--y . q--[ke]--ol . [k]--ey . [da+yk]--y`
  - **T3 (Gloss)**: `BASE/HUB(d)--ar | NOM+TUBE/DUCT(t)--ey | NOM+TUBE/DUCT(t)--ain | LIQUID_PREF(l)+ROOT(olsh)--edy | NOM+VESSEL/BODY(k)--ain | ACT:mix/proc--ey | CONJ+NOM+JAR/HERB(or)--ain | ACT:heat/steep--ey | NOM+SPOKE/RAY(to)--y | CONJ+NOM+EXTRACT/COOK(ke)--ol | VESSEL/BODY(k)--ey | ROOT(da)+ROOT(yk)--y`
  - **T4 (Cribs)**: `dar` = exact label `dar` [f67v1.4(&L0), f69r.7(&L0)]; `oteey` = exact label `otey` [f72v3.14(&Lz), f73r.21(&Lz)]; `otain` = exact label `otain` [f71v.7(&Lz), f72r1.9(&Lz)]; `okain` = exact label `okain` [f67r2.28(+L0), f72r3.12(&Lz)]; `qorain` = exact label `orain` [f89r2.30(+Lc)]; `shey` = exact label `shey` [f68r2.29(@Ls), f116v.1(@Lx)]
