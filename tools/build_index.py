import json
import re
import pymupdf
from pathlib import Path

SECTION_NAMES = {
    'T': 'Text-only',
    'H': 'Herbal (Botanical)',
    'A': 'Astronomical',
    'Z': 'Zodiac (Astrological)',
    'B': 'Biological (Balneological)',
    'C': 'Cosmological',
    'P': 'Pharmaceutical',
    'S': 'Starred Recipes',
}

def normalize_pdf_label(raw_label: str) -> list[str]:
    """Map PDF page text label like '1r' or '85v and 86r (foldout)' to canonical folio IDs."""
    folios = [f"f{f}" for f in re.findall(r'\b(\d+[rv]\d*)\b', raw_label)]
    if '85v' in raw_label and '86r' in raw_label:
        folios.append('fRos')
    return folios

def parse_zl_metadata(zl_path: Path):
    folio_data = {}
    current_folio = None
    with open(zl_path, 'r', encoding='utf-8', errors='replace') as f:
        for line in f:
            line = line.rstrip('\r\n')
            m_header = re.match(r'^<(f[A-Za-z0-9]+)>\s+<!\s*(.*?)>', line)
            if m_header:
                current_folio = m_header.group(1)
                meta_str = m_header.group(2)
                kv = dict(re.findall(r'\$([A-Z])=([^\s>]+)', meta_str))
                folio_data[current_folio] = {
                    'folio': current_folio,
                    'quire': kv.get('Q', ''),
                    'section_code': kv.get('I', ''),
                    'section': SECTION_NAMES.get(kv.get('I', ''), kv.get('I', 'Unknown')),
                    'currier_lang': kv.get('L', ''),
                    'hand': kv.get('H', ''),
                    'comments': [],
                    'lines': 0,
                    'words': 0,
                    'labels': [],
                    'right_justified_titles': [],
                    'drawing_intrusions': 0,
                }
                continue

            if current_folio and line.startswith('# '):
                comment = line[2:].strip()
                if comment and not comment.startswith('page '):
                    folio_data[current_folio]['comments'].append(comment)
                continue

            m_locus = re.match(r'^<(f[A-Za-z0-9]+)\.([^,>]+),([^>]+)>\s+(.*)$', line)
            if m_locus:
                f_id, loc_num, loc_type, text = m_locus.groups()
                if f_id not in folio_data:
                    continue
                entry = folio_data[f_id]
                entry['lines'] += 1
                entry['drawing_intrusions'] += text.count('<->')
                # Clean text of IVTFF tags
                clean = re.sub(r'<![^>]*>', '', text)
                clean = re.sub(r'<[^>]*>', '.', clean)
                clean = re.sub(r'\[([^:\]]+):[^\]]+\]', r'\1', clean)
                clean = re.sub(r'\{([^}]+)\}', r'\1', clean)
                words = [w for w in re.split(r'[.,\s]+', clean) if w and not w.startswith('@')]
                entry['words'] += len(words)
                if 'L' in loc_type:
                    entry['labels'].append({'locus': f"{f_id}.{loc_num}", 'type': loc_type, 'words': words})
                if loc_type == '=Pt':
                    entry['right_justified_titles'].append({'locus': f"{f_id}.{loc_num}", 'words': words})

    return folio_data

def main():
    doc1 = pymupdf.open('2002046.pdf')
    doc2 = pymupdf.open('voynich-manuscript.pdf')
    toc2 = {entry[2]: entry[1] for entry in doc2.get_toc() if entry[0] == 2}

    pdf_pages = []
    folio_to_pdf = {}

    for i, page in enumerate(doc1):
        pno = i + 1
        txt = [line.strip() for line in page.get_text().splitlines() if line.strip()]
        label1 = txt[0] if txt else f'page_{pno}'
        img_id = txt[-1] if len(txt) >= 3 and 'Image ID' in txt[-2] else ''
        imgs1 = page.get_images()
        w1, h1 = (imgs1[0][2], imgs1[0][3]) if imgs1 else (0, 0)

        # Match with voynich-manuscript.pdf
        pno2 = pno if pno <= 209 else (210 if label1 == '[Back cover]' else None)
        label2 = toc2.get(pno2, '') if pno2 else ''
        w2, h2 = (0, 0)
        if pno2:
            info2 = doc2[pno2 - 1].get_image_info()
            if info2:
                w2, h2 = info2[0]['width'], info2[0]['height']

        folios = normalize_pdf_label(label1)
        rec = {
            'pdf1_page': pno,
            'pdf1_label': label1,
            'beinecke_image_id': img_id,
            'pdf1_size': [w1, h1],
            'pdf2_page': pno2,
            'pdf2_label': label2,
            'pdf2_size': [w2, h2],
            'folios': folios,
        }
        pdf_pages.append(rec)
        for f in folios:
            folio_to_pdf.setdefault(f, []).append(rec)

    zl_data = parse_zl_metadata(Path('data/ZL3b-n.txt'))

    # Attach PDF info to zl_data
    for f_id, f_info in zl_data.items():
        m_b = re.match(r'^(f\d+[rv])', f_id)
        base_f = m_b.group(1) if m_b else f_id
        f_info['pdf_pages'] = folio_to_pdf.get(f_id, folio_to_pdf.get(base_f, []))

    out = {
        'summary': {
            'pdf1_file': '2002046.pdf',
            'pdf1_pages': len(doc1),
            'pdf2_file': 'voynich-manuscript.pdf',
            'pdf2_pages': len(doc2),
            'transcribed_folios': len(zl_data),
            'total_words': sum(v['words'] for v in zl_data.values()),
            'total_labels': sum(len(v['labels']) for v in zl_data.values()),
            'total_drawing_intrusions': sum(v['drawing_intrusions'] for v in zl_data.values()),
        },
        'pdf_pages': pdf_pages,
        'folios': zl_data,
    }

    with open('data/folio_index.json', 'w', encoding='utf-8') as f:
        json.dump(out, f, indent=2)

    print("Saved data/folio_index.json:")
    print(json.dumps(out['summary'], indent=2))

if __name__ == '__main__':
    main()
