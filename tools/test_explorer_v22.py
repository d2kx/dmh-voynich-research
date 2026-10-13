#!/usr/bin/env python3
"""
tools/test_explorer_v22.py

Verification suite for Interactive Explorer v22.0.
Verifies that:
- tools/build_interactive_explorer.py generates valid explorer/index.html
- Exactly 24 interactive tabs (including Tab 23 and Tab 24)
- Exactly 98 page walkthroughs in WALKTHROUGH_FOLIOS and DATA
- Exactly 115 botanical/astrological specimens (SPEC-01..115)
- All required Wave 55 and Wave 56 dataset keys and tables are populated
- All header badges, version markers, and titles are correctly synchronized
"""

import json
import re
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
HTML_PATH = ROOT / "explorer" / "index.html"


def test_explorer_v22():
    print("Testing Interactive Explorer v22.0...")
    assert HTML_PATH.exists(), f"File {HTML_PATH} does not exist"
    content = HTML_PATH.read_text(encoding="utf-8")
    assert len(content) > 100_000, f"HTML content too small: {len(content)} bytes"

    # 1. Tab buttons
    tab_btn_pattern = re.compile(r'<button class="tab-btn[^"]*" onclick="switchTab\(\'([^\']+)\'')
    tab_buttons = tab_btn_pattern.findall(content)
    print(f"  [PASS] Tab buttons found: {len(tab_buttons)}")
    assert len(tab_buttons) == 24, f"Expected 24 tab buttons, found {len(tab_buttons)}"
    assert tab_buttons[-2] == "wave55", f"Expected Tab 23 to be wave55, got {tab_buttons[-2]}"
    assert tab_buttons[-1] == "wave56", f"Expected Tab 24 to be wave56, got {tab_buttons[-1]}"

    # 2. Tab panels
    tab_panel_pattern = re.compile(r'<section id="tab-([^"]+)" class="tab-panel')
    tab_panels = tab_panel_pattern.findall(content)
    print(f"  [PASS] Tab panels found: {len(tab_panels)}")
    assert len(tab_panels) == 24, f"Expected 24 tab panels, found {len(tab_panels)}"
    assert tab_panels[-2] == "wave55", f"Expected Tab 23 panel to be tab-wave55, got {tab_panels[-2]}"
    assert tab_panels[-1] == "wave56", f"Expected Tab 24 panel to be tab-wave56, got {tab_panels[-1]}"
    assert set(tab_buttons) == set(tab_panels), f"Buttons and panels mismatch: {set(tab_buttons) ^ set(tab_panels)}"

    # 3. Embedded JSON DATA parsing
    data_match = re.search(r"const DATA = ({.*?});\s*const PREFIX_RULES", content, re.DOTALL)
    assert data_match, "Could not find const DATA embedded JSON in index.html"
    data = json.loads(data_match.group(1))

    # 4. Walkthrough count
    folios = data.get("folios", [])
    print(f"  [PASS] Walkthrough folios: {len(folios)}")
    assert len(folios) == 98, f"Expected 98 walkthrough folios, found {len(folios)}"
    wave55_56_folios = ["f35r", "f36v", "f44r", "f45r", "f53r", "f56v", "p210", "p212"]
    for f_id in wave55_56_folios:
        assert any(w["folio"] == f_id for w in folios), f"Missing walkthrough folio: {f_id}"

    # 5. Specimen count
    specimens = data.get("specimens", [])
    print(f"  [PASS] Visual specimens: {len(specimens)}")
    assert len(specimens) == 115, f"Expected 115 specimens, found {len(specimens)}"
    assert specimens[0]["id"] == "SPEC-01", f"First specimen ID was {specimens[0]['id']}"
    assert specimens[-1]["id"] == "SPEC-115", f"Last specimen ID was {specimens[-1]['id']}"

    # 6. Wave 55 & 56 embedded dataset keys
    expected_keys = [
        ("wave55_q5_bifolia", 4),
        ("wave55_q6_folios", 16),
        ("wave55_q7_bifolia", 4),
        ("wave55_quire_map", 18),
        ("wave56_binding_atlas", 20),
        ("wave56_registration_pairs", 7),
        ("wave56_defects", 15),
        ("wave56_stitches", 6),
        ("wave56_twenty_quires", 20),
        ("wave56_scribes", 6),
    ]
    for key_name, min_items in expected_keys:
        assert key_name in data, f"Missing key in DATA: {key_name}"
        assert len(data[key_name]) >= min_items, f"Key {key_name} has {len(data[key_name])} items (expected >= {min_items})"
        print(f"  [PASS] Dataset '{key_name}': {len(data[key_name])} items")

    # 7. Header badges and titles
    required_phrases = [
        "v22.0 Grand Release",
        "24 Interactive Tabs",
        "98 Walkthroughs",
        "115 Visual Specimens",
        "227/227 = 100.0% Visual Coverage",
        "Milestone 250th Discovery",
        "1. Page-by-Page Reader (98)",
        "2. Visual Cribs &amp; Species (115)",
        "23. Wave 55: Historic 227/227 = 100.0% Codex Coverage &amp; Middle Herbal Bifolia (v21.0)",
        "24. Wave 56: Milestone 250th Discovery — Physical Binding, Forensics &amp; 20-Quire Synthesis (v22.0)",
        "115 Flagship Botanical, Astronomical, Balneological, Cosmological, Margin-Key &amp; Visual-Twin Identifications (SPEC-01..115)",
        "wave55Quire5Table",
        "wave55Quire6Table",
        "wave55Quire7Table",
        "wave55QuireMapTable",
        "wave56BindingAtlasTable",
        "wave56DefectAtlasTable",
        "wave56TwentyQuiresTable",
        "wave56ScribeTriadTable",
        "renderWave55Tab()",
        "renderWave56Tab()",
    ]
    for phrase in required_phrases:
        assert phrase in content, f"Missing required phrase in index.html: {phrase}"
        print(f"  [PASS] Verified content phrase: {phrase[:50]}...")

    print("\nAll 7 test suites passed successfully (v22.0 verified)!")
    return 0


if __name__ == "__main__":
    sys.exit(test_explorer_v22())
