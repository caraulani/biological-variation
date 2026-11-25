"""Lay out text that runs bottom-to-top (tables printed sideways) as normal left-to-right rows.
Usage: rotated_table.py paper.pdf page_number(1-based) [page ...] > out.txt"""
import sys
import pymupdf

PUA = {0xF130 + d: str(d) for d in range(10)}

def rotated_rows(page, tol=2.5):
    spans = []
    for b in page.get_text("dict", flags=pymupdf.TEXT_CID_FOR_UNKNOWN_UNICODE)["blocks"]:
        for l in b.get("lines", []):
            if abs(l["dir"][1] + 1) > 0.01:
                continue
            for s in l["spans"]:
                x0, y0, x1, y1 = s["bbox"]
                spans.append(((x0 + x1) / 2, page.rect.height - y1, page.rect.height - y0, s["text"].translate(PUA)))
    spans.sort()
    rows, cur, lastx = [], [], None
    for x, pos, end, t in spans:
        if lastx is not None and x - lastx > tol:
            rows.append(cur); cur = []
        cur.append((pos, end, t)); lastx = x
    if cur:
        rows.append(cur)
    out = []
    for r in rows:
        r.sort()
        # join spans: no space when a span starts where the previous one ended
        line, prev_end = "", None
        for pos, end, t in r:
            if prev_end is not None and pos - prev_end < 1.0:
                line += t
            else:
                col = int(pos / 3.2)
                line = (line.ljust(col) if len(line) < col else line + " ") + t
            prev_end = end
        out.append(line.rstrip())
    return out

if __name__ == "__main__":
    doc = pymupdf.open(sys.argv[1])
    for pn in sys.argv[2:]:
        print(f"=== PAGE {pn} (rotated) ===")
        print("\n".join(rotated_rows(doc[int(pn) - 1])))
