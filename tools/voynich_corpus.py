"""Shared IVTFF transliteration parser for the Voynich research toolkit.

Every earlier ``tools/attack*.py`` script carried its own ad-hoc parser, so token
definitions drifted between experiments. New experiments should import this
module instead so that results are comparable.

Usage::

    from voynich_corpus import load_lines, load_folio_meta
    lines = load_lines()                    # ZL3b-n.txt, all loci
    para = [l for l in lines if l.unit == 'P']

Token conventions (documented so results can be reproduced):

* Words are split on ``.`` (certain space) and ``,`` (uncertain space). Each word
  records whether the boundary *before* it was uncertain (``,``).
* ``[a:b]`` alternative readings -> first alternative ``a`` (ZL's preferred one).
* ``{...}`` ligature/odd-glyph braces are removed, keeping the inner glyphs
  (``{c'y}`` -> ``c'y``). ``@nnn;`` rare-glyph codes become ``?``.
* ``<!...>`` inline comments are dropped. ``<%>`` / ``<$>`` set paragraph
  start/end flags. ``<->`` (drawing intrusion) acts as a word boundary and its
  position is recorded in ``intrusion_after`` (index of the word preceding it).
* Words containing ``?`` or ``'`` are kept but flagged ``uncertain``; use
  ``clean_words`` to get only fully-legible words.
"""
from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, 'data')

_LOCUS = re.compile(r'^<(f\w+)\.(\d+)([a-z]?),([^\w\s])(\w)(\w*)>\s*(.*)$')
_FOLIO_HDR = re.compile(r'^<(f\w+)>\s*<!(.*)>')
_META = re.compile(r'\$(\w)=(\w+)')


@dataclass
class Line:
    folio: str
    line_no: int
    locus: str            # e.g. 'f28v.7'
    pos_code: str         # '@' first in unit, '+' continuation, '*' new para after gap, '=' title, '&', '~', '/'
    unit: str             # 'P' paragraph text, 'L' label, 'C' circular, 'R' radial
    unit_sub: str         # e.g. '0', 't' (right-justified title), 'c', 'p'
    para_start: bool
    para_end: bool
    words: List[str]
    uncertain_before: List[bool]   # True if the boundary before word i was ',' (uncertain space)
    intrusion_after: List[int]     # word indices i such that a <-> follows word i
    meta: Dict[str, str] = field(default_factory=dict)  # folio-level $Q,$P,$I,$L,$H ...

    @property
    def lang(self) -> str:
        return self.meta.get('L', '?')

    @property
    def hand(self) -> str:
        return self.meta.get('H', '?')

    @property
    def section(self) -> str:
        return self.meta.get('I', '?')

    @property
    def quire(self) -> str:
        return self.meta.get('Q', '?')

    @property
    def clean_words(self) -> List[str]:
        return [w for w in self.words if w and not _is_uncertain(w)]


def _is_uncertain(w: str) -> bool:
    return '?' in w or "'" in w or '*' in w


def _normalise_text(t: str) -> str:
    t = re.sub(r'<![^>]*>', '', t)                          # inline comments
    t = re.sub(r'\[([^:\]]*):[^\]]*\]', r'\1', t)          # [a:b] -> a
    t = re.sub(r'@\d+;', '?', t)                            # rare glyph codes
    t = t.replace('{', '').replace('}', '')
    return t


def parse_text(raw: str):
    """Return (words, uncertain_before, intrusion_after, para_start, para_end)."""
    para_start = '<%>' in raw
    para_end = '<$>' in raw
    t = raw.replace('<%>', '').replace('<$>', '')
    t = _normalise_text(t)
    t = t.replace('<~>', '.')
    words: List[str] = []
    unc: List[bool] = []
    intr: List[int] = []
    # tokenise into words and separators, treating <-> as a separator
    for tok in re.split(r'(<->|[.,])', t):
        if tok == '<->':
            if words:
                intr.append(len(words) - 1)
            continue
        if tok in ('.', ','):
            continue
        w = tok.strip()
        w = re.sub(r'<[^>]*>', '', w)
        if not w:
            continue
        words.append(w)
    # second pass for uncertain-space flags (needs separators in order)
    seps = []
    for tok in re.split(r'([^.,<>-]+)', re.sub(r'<->', '.', t)):
        if tok and set(tok) <= set('.,'):
            seps.append(',' in tok)
    unc = [False] + seps[: max(0, len(words) - 1)]
    unc += [False] * (len(words) - len(unc))
    return words, unc[: len(words)], intr, para_start, para_end


def load_lines(path: Optional[str] = None) -> List[Line]:
    path = path or os.path.join(DATA, 'ZL3b-n.txt')
    out: List[Line] = []
    meta: Dict[str, Dict[str, str]] = {}
    with open(path, encoding='utf-8', errors='replace') as fh:
        for raw in fh:
            raw = raw.rstrip('\n')
            h = _FOLIO_HDR.match(raw)
            if h:
                meta[h.group(1)] = dict(_META.findall(h.group(2)))
                continue
            m = _LOCUS.match(raw)
            if not m:
                continue
            folio, ln, _sfx, pos, unit, sub, text = m.groups()
            words, unc, intr, ps, pe = parse_text(text)
            out.append(Line(folio=folio, line_no=int(ln), locus=f'{folio}.{ln}',
                            pos_code=pos, unit=unit, unit_sub=sub,
                            para_start=ps, para_end=pe, words=words,
                            uncertain_before=unc, intrusion_after=intr,
                            meta=meta.get(folio, {})))
    return out


def load_folio_meta(path: Optional[str] = None) -> Dict[str, Dict[str, str]]:
    path = path or os.path.join(DATA, 'ZL3b-n.txt')
    meta: Dict[str, Dict[str, str]] = {}
    with open(path, encoding='utf-8', errors='replace') as fh:
        for raw in fh:
            h = _FOLIO_HDR.match(raw.rstrip('\n'))
            if h:
                meta[h.group(1)] = dict(_META.findall(h.group(2)))
    return meta


def paragraphs(lines: List[Line]) -> List[List[Line]]:
    """Group running-text ('P') lines into paragraphs using <%>/<$> markers."""
    paras: List[List[Line]] = []
    cur: List[Line] = []
    for l in lines:
        if l.unit != 'P':
            continue
        if l.para_start and cur:
            paras.append(cur)
            cur = []
        cur.append(l)
        if l.para_end:
            paras.append(cur)
            cur = []
    if cur:
        paras.append(cur)
    return paras


if __name__ == '__main__':
    ls = load_lines()
    p = [l for l in ls if l.unit == 'P']
    nw = sum(len(l.words) for l in ls)
    print(f'{len(ls)} loci, {len(p)} paragraph lines, {nw} words, '
          f'{len(paragraphs(ls))} paragraphs, '
          f'{sum(len(l.intrusion_after) for l in ls)} intrusions, '
          f'{sum(sum(l.uncertain_before) for l in ls)} uncertain spaces')
    ex = next(l for l in ls if l.locus == 'f28v.7')
    print(ex.locus, ex.lang, ex.hand, ex.section, ex.words, ex.intrusion_after, ex.uncertain_before)
