"""Turn every downloaded source into text for reading and for quote checks.
Writes paper.txt (normal text) and rotated.txt (pages printed sideways) next to each PDF,
and fulltext.txt next to each JATS XML."""
import pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).parent))
import pymupdf
from pdftext import pdf_to_text
from rotated_table import rotated_rows
from jats_text import jats_to_text

RAW = pathlib.Path(__file__).resolve().parent.parent.parent / "_raw" / "meaningful-change"

def main():
    for d in sorted(p for p in RAW.iterdir() if p.is_dir()):
        pdf = d / "paper.pdf"
        if pdf.exists():
            (d / "paper.txt").write_text(pdf_to_text(pdf))
            doc = pymupdf.open(pdf)
            out = []
            for i, page in enumerate(doc, 1):
                rows = rotated_rows(page)
                if sum(1 for r in rows if r.strip()) > 5:
                    out.append(f"=== PAGE {i} (rotated) ===")
                    out.extend(rows)
            (d / "rotated.txt").write_text("\n".join(out))
        xml = d / "fulltext.xml"
        if xml.exists():
            (d / "fulltext.txt").write_text(jats_to_text(xml))
        print("extracted", d.name)

if __name__ == "__main__":
    main()
