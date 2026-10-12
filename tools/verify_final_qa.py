#!/usr/bin/env python3
"""
Comprehensive Final Verification Suite for Milestone 200 & Explorer v14.0
Executed by Worker M4.
"""

import json
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

ATTACK_SCRIPTS = [
    "tools/attack197_gemini_cancer_decans_and_p131_sheet.py",
    "tools/attack198_f67v_cardinal_treatises_and_velar_stop_network.py",
    "tools/attack199_f75r_waterfall_basin_and_hydraulic_master_hub.py",
    "tools/attack200_milestone200_master_compendium.py",
    "tools/attack201_sagittarius_centaur_archer_and_ecliptic_drift.py",
    "tools/attack202_pharmaceutical_albarelli_registers_and_recipe_bridge.py",
    "tools/attack203_quire20_star_point_morphology_and_formulary_clusters.py",
    "tools/attack204_wave48_master_compendium.py",
]

ATTACK_JSONS = [
    "data/attack197_gemini_cancer_decans_and_p131_sheet.json",
    "data/attack198_f67v_cardinal_treatises_and_velar_stop_network.json",
    "data/attack199_f75r_waterfall_basin_and_hydraulic_master_hub.json",
    "data/attack200_milestone200_master_compendium.json",
    "data/attack201_sagittarius_centaur_archer_and_ecliptic_drift.json",
    "data/attack202_pharmaceutical_albarelli_registers_and_recipe_bridge.json",
    "data/attack203_quire20_star_point_morphology_and_formulary_clusters.json",
    "data/attack204_wave48_master_compendium.json",
]

CROPS_12 = [
    "pages/f72r2_gemini_medallion_enh.png",
    "pages/f72r3_cancer_medallion_enh.png",
    "pages/f67v1_smiling_sun_wheel_enh.png",
    "pages/f67v2_four_corner_cosmology_enh.png",
    "pages/f75v_gastric_stream_conduits_enh.png",
    "pages/f75v_gutter_acrostic_sllors_enh.png",
    "pages/f73v_sagittarius_medallion_enh.png",
    "pages/f88v_three_register_pharma_enh.png",
    "pages/f48v_gentian_bifurcated_twin_enh.png",
    "pages/f105r_dotted_star_dyads_enh.png",
    "pages/f116r_penultimate_recipes_enh.png",
    "pages/f99v_three_row_jars_and_roots_enh.png",
]

DOC_FILES = [
    "README.md",
    "NOTES.md",
    "notes/PLAIN_ENGLISH_VISUAL_READERS_GUIDE.md",
    "notes/VISUAL_BOTANICAL_AND_ASTRO_IDENTIFICATIONS.md",
    "notes/DECODING_ATTACKS_SYNTHESIS.md",
    "notes/MILESTONE_200_ATTACKS_DECANS_QUADRANTS_AND_BALNEO_HUB.md",
    "notes/WAVE48_MASTER_COMPENDIUM.md",
]


def test_1_reexecute_attacks():
    print("=== Step 1: Re-executing and Verifying 8 Attack Scripts ===")
    for script_rel, json_rel in zip(ATTACK_SCRIPTS, ATTACK_JSONS):
        script_path = ROOT / script_rel
        json_path = ROOT / json_rel
        assert script_path.exists(), f"Script {script_rel} missing"
        
        res = subprocess.run([sys.executable, str(script_path)], capture_output=True, text=True, cwd=str(ROOT))
        assert res.returncode == 0, f"Script {script_rel} failed with code {res.returncode}:\n{res.stderr}"
        
        assert json_path.exists(), f"Output JSON {json_rel} does not exist"
        assert json_path.stat().st_size > 500, f"Output JSON {json_rel} suspiciously small ({json_path.stat().st_size} bytes)"
        
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert isinstance(data, dict) and len(data) > 0, f"JSON {json_rel} empty or invalid dict"
        print(f"  [PASS] {script_rel} -> {json_rel} ({json_path.stat().st_size:,} bytes, {len(data)} top-level keys)")
    print("Step 1 PASSED: All 8 attack scripts execute cleanly with valid JSON output.\n")


def test_2_builders_and_counts():
    print("=== Step 2: Builders Execution and Deliverable Counts ===")
    # 2a. build_visual_botanical_astro_identifications.py
    builder_id = ROOT / "tools/build_visual_botanical_astro_identifications.py"
    res_id = subprocess.run([sys.executable, str(builder_id)], capture_output=True, text=True, cwd=str(ROOT))
    assert res_id.returncode == 0, f"build_visual_botanical_astro_identifications failed:\n{res_id.stderr}"
    
    spec_json = ROOT / "data/visual_botanical_astro_identifications.json"
    with open(spec_json, "r", encoding="utf-8") as f:
        spec_dict = json.load(f)
    specs = spec_dict.get("specimens", [])
    print(f"  [PASS] visual_botanical_astro_identifications.json contains {len(specs)} specimens (specimen_count = {spec_dict.get('specimen_count')})")
    assert len(specs) == 75, f"Expected 75 specimens, got {len(specs)}"
    
    # 2b. build_interactive_explorer.py
    builder_exp = ROOT / "tools/build_interactive_explorer.py"
    res_exp = subprocess.run([sys.executable, str(builder_exp)], capture_output=True, text=True, cwd=str(ROOT))
    assert res_exp.returncode == 0, f"build_interactive_explorer failed:\n{res_exp.stderr}"
    
    exp_html = ROOT / "explorer/index.html"
    assert exp_html.exists() and exp_html.stat().st_size > 100000, "explorer/index.html missing or too small"
    html_content = exp_html.read_text(encoding="utf-8")
    
    # Check tabs
    # Count unique switchTab('...', this) navigation buttons
    tabs_found = re.findall(r"switchTab\('([^']+)'", html_content)
    unique_tabs = list(dict.fromkeys(tabs_found))
    print(f"  [PASS] explorer/index.html contains {len(unique_tabs)} tabs: {unique_tabs}")
    assert len(unique_tabs) == 16, f"Expected 16 interactive tabs, got {len(unique_tabs)}"
    
    # Check DATA object in HTML
    m_data = re.search(r'const DATA = (\{.*?\});\n', html_content, re.DOTALL)
    assert m_data, "Could not find const DATA in explorer/index.html"
    embedded_data = json.loads(m_data.group(1))
    
    n_folios = len(embedded_data.get("folios", []))
    print(f"  [PASS] explorer/index.html DATA.folios contains {n_folios} walkthroughs")
    assert n_folios == 66, f"Expected 66 walkthroughs in HTML DATA, got {n_folios}"
    
    n_specs_html = len(embedded_data.get("specimens", []))
    print(f"  [PASS] explorer/index.html DATA.specimens contains {n_specs_html} specimens")
    assert n_specs_html == 75, f"Expected 75 specimens in HTML DATA, got {n_specs_html}"
    
    # Also verify build_interactive_explorer defines 66 walkthroughs
    import tools.build_interactive_explorer as bie
    assert len(bie.WALKTHROUGH_FOLIOS) == 66, f"Expected 66 walkthroughs in builder, got {len(bie.WALKTHROUGH_FOLIOS)}"
    
    print("Step 2 PASSED: Builders verified with exactly 16 tabs, 66 walkthroughs, 75 specimens.\n")


def test_3_validate_relative_links():
    print("=== Step 3: Validating Relative Markdown Links in 7 Documentation Files ===")
    total_links = 0
    broken_links = []
    
    link_regex = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')
    
    for doc_rel in DOC_FILES:
        doc_path = ROOT / doc_rel
        assert doc_path.exists(), f"Doc file {doc_rel} missing"
        text = doc_path.read_text(encoding="utf-8")
        
        doc_dir = doc_path.parent
        matches = link_regex.findall(text)
        doc_checked = 0
        
        for anchor, href in matches:
            # Strip anchors within target file or pure hash
            href_clean = href.strip()
            if href_clean.startswith("#") or href_clean.startswith("http://") or href_clean.startswith("https://") or href_clean.startswith("mailto:"):
                continue
            
            # Remove in-page fragment if present
            target_path_part = href_clean.split("#")[0]
            if not target_path_part:
                continue
            
            # Resolve target
            # Some links might be repo-relative (starting without ./) or file-relative
            # In repo markdown, if it starts with an existing repo folder or file from ROOT or doc_dir:
            target1 = (doc_dir / target_path_part).resolve()
            target2 = (ROOT / target_path_part).resolve()
            
            doc_checked += 1
            total_links += 1
            
            if not target1.exists() and not target2.exists():
                broken_links.append({
                    "file": doc_rel,
                    "anchor": anchor,
                    "href": href,
                    "resolved_doc_dir": str(target1),
                    "resolved_root": str(target2)
                })
        
        print(f"  [PASS] {doc_rel}: {doc_checked} relative links checked, 0 broken")
        
    if broken_links:
        print("\nBroken links found:")
        for b in broken_links:
            print(f"  In {b['file']}: [{b['anchor']}]({b['href']}) -> not found at {b['resolved_doc_dir']} or {b['resolved_root']}")
        assert len(broken_links) == 0, f"Found {len(broken_links)} broken relative links"
    
    print(f"Step 3 PASSED: All {total_links} relative markdown links resolved successfully (0 broken).\n")


def test_4_verify_crops():
    print("=== Step 4: Verifying 12 Rendered Crops in pages/*.png ===")
    for crop_rel in CROPS_12:
        crop_path = ROOT / crop_rel
        assert crop_path.exists(), f"Rendered crop {crop_rel} does not exist"
        sz = crop_path.stat().st_size
        assert sz > 50000, f"Rendered crop {crop_rel} is suspiciously small ({sz} bytes)"
        
        # Verify valid PNG header
        with open(crop_path, "rb") as f:
            header = f.read(8)
            assert header == b"\x89PNG\r\n\x1a\n", f"File {crop_rel} is not a valid PNG image (header: {header})"
        
        print(f"  [PASS] {crop_rel} exists, valid PNG ({sz:,} bytes)")
    
    print("Step 4 PASSED: All 12 rendered crops exist, are valid PNGs, and exceed minimum size thresholds.\n")


def main():
    test_1_reexecute_attacks()
    test_2_builders_and_counts()
    test_3_validate_relative_links()
    test_4_verify_crops()
    print("======================================================================")
    print("ALL VERIFICATION CHECKS (STEPS 1-4) PASSED FLAWLESSLY WITH 100% SUCCESS")
    print("======================================================================")


if __name__ == "__main__":
    main()
