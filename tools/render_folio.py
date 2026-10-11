import argparse
import io
import json
import pymupdf
from pathlib import Path
from PIL import Image, ImageOps, ImageEnhance

def extract_embedded_image(doc, pno: int) -> Image.Image:
    page = doc[pno - 1]
    info = page.get_image_info(xrefs=True)
    if info and info[0].get("xref"):
        xref = info[0]["xref"]
        base_img = doc.extract_image(xref)
        return Image.open(io.BytesIO(base_img["image"])).convert("RGB")
    imgs = page.get_images(full=True)
    if len(imgs) == 1:
        base_img = doc.extract_image(imgs[0][0])
        return Image.open(io.BytesIO(base_img["image"])).convert("RGB")
    pix = page.get_pixmap(dpi=200)
    return Image.open(io.BytesIO(pix.tobytes("png"))).convert("RGB")

def enhance_faded_ink(img: Image.Image) -> Image.Image:
    """Enhance faded iron-gall / marginalia ink using blue-channel contrast & autocontrast."""
    r, g, b = img.split()
    # Faded brown/iron-gall ink absorbs strongly in blue/UV relative to red parchment background
    b_ac = ImageOps.autocontrast(b, cutoff=2)
    r_ac = ImageOps.autocontrast(r, cutoff=2)
    g_ac = ImageOps.autocontrast(g, cutoff=2)
    merged = Image.merge("RGB", (r_ac, g_ac, b_ac))
    merged = ImageEnhance.Contrast(merged).enhance(1.6)
    merged = ImageEnhance.Sharpness(merged).enhance(1.5)
    return merged

def main():
    parser = argparse.ArgumentParser(description="Extract and optionally crop/enhance Voynich folio scans.")
    parser.add_argument("folio", help="Folio ID (e.g. f1r, 116v) or PDF page number (e.g. p4)")
    parser.add_argument("--pdf", default="2002046.pdf", help="PDF filename (default: 2002046.pdf)")
    parser.add_argument("--crop", type=float, nargs=4, metavar=("X0", "Y0", "X1", "Y1"),
                        help="Normalized crop coordinates [0..1]: x0 y0 x1 y1")
    parser.add_argument("--enhance", action="store_true", help="Apply contrast/channel enhancement for faded ink")
    parser.add_argument("--compare", action="store_true", help="Create side-by-side comparison of both PDFs")
    parser.add_argument("--out", default=None, help="Output file path")
    args = parser.parse_args()

    with open("data/folio_index.json", "r", encoding="utf-8") as f:
        idx = json.load(f)

    pno1, pno2 = None, None
    key = args.folio.lower()
    if key.startswith("p") and key[1:].isdigit():
        pno1 = int(key[1:])
        pno2 = pno1 if pno1 <= 209 else None
    else:
        if not key.startswith("f"):
            key = "f" + key
        if key in idx["folios"] and idx["folios"][key]["pdf_pages"]:
            rec = idx["folios"][key]["pdf_pages"][0]
            pno1 = rec["pdf1_page"]
            pno2 = rec["pdf2_page"]
        else:
            for rec in idx["pdf_pages"]:
                if args.folio.lower() in rec["pdf1_label"].lower():
                    pno1 = rec["pdf1_page"]
                    pno2 = rec["pdf2_page"]
                    break

    if not pno1:
        raise ValueError(f"Could not resolve folio/page: {args.folio}")

    doc1 = pymupdf.open(args.pdf)
    img1 = extract_embedded_image(doc1, pno1)

    if args.crop:
        x0, y0, x1, y1 = args.crop
        w, h = img1.size
        img1 = img1.crop((int(x0 * w), int(y0 * h), int(x1 * w), int(y1 * h)))

    if args.compare and pno2:
        doc2 = pymupdf.open("voynich-manuscript.pdf")
        img2 = extract_embedded_image(doc2, pno2)
        if args.crop:
            x0, y0, x1, y1 = args.crop
            w2, h2 = img2.size
            img2 = img2.crop((int(x0 * w2), int(y0 * h2), int(x1 * w2), int(y1 * h2)))
        img2_resized = img2.resize(img1.size, Image.Resampling.LANCZOS)
        if args.enhance:
            img1 = enhance_faded_ink(img1)
            img2_resized = enhance_faded_ink(img2_resized)
        combined = Image.new("RGB", (img1.width * 2 + 10, img1.height), (30, 30, 30))
        combined.paste(img1, (0, 0))
        combined.paste(img2_resized, (img1.width + 10, 0))
        out_img = combined
    else:
        out_img = enhance_faded_ink(img1) if args.enhance else img1

    out_path = Path(args.out) if args.out else Path("pages") / f"{args.folio.replace(' ', '_')}{'_enh' if args.enhance else ''}{'_cmp' if args.compare else ''}.png"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_img.save(out_path)
    print(f"Saved {out_path} ({out_img.width}x{out_img.height}) from page {pno1}")

if __name__ == "__main__":
    main()
