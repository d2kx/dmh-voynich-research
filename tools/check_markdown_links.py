import re
import urllib.parse
from pathlib import Path

repo_root = Path('.').resolve()
target_files = [
    'README.md',
    'NOTES.md',
    'notes/PLAIN_ENGLISH_VISUAL_READERS_GUIDE.md',
    'notes/VISUAL_BOTANICAL_AND_ASTRO_IDENTIFICATIONS.md',
    'notes/DECODING_ATTACKS_SYNTHESIS.md',
    'notes/WAVE55_MASTER_COMPENDIUM.md',
    'notes/WAVE56_MASTER_COMPENDIUM.md',
    'notes/AUDIT_WAVES_54_56.md',
    'notes/LINE_BREAK_BEHAVIOUR.md',
    'notes/SELF_CITATION_AUTOCOPY_TEST.md',
    'notes/VOCABULARY_DYNAMICS.md',
]

link_pattern = re.compile(r'!?\[([^\]]*)\]\(([^)]+)\)')

def get_anchors(file_path):
    if not file_path.exists():
        return set()
    content = file_path.read_text(encoding='utf-8', errors='replace')
    anchors = set()
    for line in content.splitlines():
        m = re.match(r'^(#+)\s+(.+)$', line.strip())
        if m:
            heading = m.group(2).strip()
            # GitHub slugification
            slug = heading.lower()
            slug = re.sub(r'[^\w\s-]', '', slug)
            slug = re.sub(r'[\s_]+', '-', slug)
            anchors.add(slug)
            anchors.add(heading.lower())
    return anchors

file_anchors = {}

broken_files = []
broken_anchors = []
total_links = 0
external_links = 0
internal_links = 0

for rel_path in target_files:
    fpath = repo_root / rel_path
    if not fpath.exists():
        print(f"ERROR: File {rel_path} does not exist!")
        continue
    content = fpath.read_text(encoding='utf-8', errors='replace')
    doc_dir = fpath.parent

    matches = link_pattern.findall(content)
    for text, target in matches:
        total_links += 1
        target = target.strip()
        if target.startswith('<') and target.endswith('>'):
            target = target[1:-1]

        if ' "' in target:
            target = target.split(' "')[0]
        elif " '" in target:
            target = target.split(" '")[0]

        target = urllib.parse.unquote(target)

        if target.startswith(('http://', 'https://', 'mailto:')):
            external_links += 1
            continue

        internal_links += 1

        parts = target.split('#')
        target_path_part = parts[0]
        anchor = parts[1] if len(parts) > 1 else None

        if not target_path_part:
            # Anchor in same file
            target_file = fpath
        else:
            p1 = (doc_dir / target_path_part).resolve()
            p2 = (repo_root / target_path_part).resolve()
            if p1.exists():
                target_file = p1
            elif p2.exists():
                target_file = p2
            else:
                broken_files.append({
                    'source': rel_path,
                    'link_text': text,
                    'target': target,
                })
                continue

        if anchor and target_file.suffix in ('.md', '.markdown'):
            if str(target_file) not in file_anchors:
                file_anchors[str(target_file)] = get_anchors(target_file)
            anchors = file_anchors[str(target_file)]
            clean_anchor = anchor.lower().strip()
            if clean_anchor not in anchors:
                # also check if anchor is prefix or loosely matched
                matched = any(clean_anchor in a or a in clean_anchor for a in anchors)
                if not matched:
                    broken_anchors.append({
                        'source': rel_path,
                        'link_text': text,
                        'target': target,
                        'anchor': anchor,
                        'target_file': str(target_file.relative_to(repo_root)),
                    })

print(f"Checked {len(target_files)} markdown files.")
print(f"Total links: {total_links}")
print(f"External links: {external_links}")
print(f"Internal links: {internal_links}")
print(f"Broken file targets: {len(broken_files)}")
print(f"Broken/unmatched anchor targets: {len(broken_anchors)}")

if broken_files:
    print("\nBroken files detail:")
    for b in broken_files:
        print(f"  In {b['source']}: [{b['link_text']}]({b['target']})")

if broken_anchors:
    print(f"\nUnmatched anchors detail ({len(broken_anchors)}):")
    for b in broken_anchors[:10]:
        print(f"  In {b['source']}: [{b['link_text']}]({b['target']}) -> anchor '{b['anchor']}' in {b['target_file']}")
