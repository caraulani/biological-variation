"""Extract text from a PDF page by page. De Gruyter PDFs set digits in a font that maps
them to private-use code points U+F130..U+F139; these are mapped back to 0..9."""
import sys
import pymupdf

PUA = {0xF130 + d: str(d) for d in range(10)}

def pdf_to_text(path):
    doc = pymupdf.open(path)
    out = []
    for i, page in enumerate(doc, 1):
        t = page.get_text("text", sort=True, flags=pymupdf.TEXT_CID_FOR_UNKNOWN_UNICODE | pymupdf.TEXT_PRESERVE_WHITESPACE)
        out.append(f"\n=== PAGE {i} ===\n" + t.translate(PUA))
    return "".join(out)

if __name__ == "__main__":
    open(sys.argv[2], "w").write(pdf_to_text(sys.argv[1]))
