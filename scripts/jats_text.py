"""Flatten a JATS XML full text (Europe PMC) to plain text; table rows become ' | '-joined lines."""
import sys
import xml.etree.ElementTree as ET

def text_of(el):
    return " ".join("".join(el.itertext()).split())

def jats_to_text(path):
    root = ET.parse(path).getroot()
    out = []
    for el in root.iter():
        tag = el.tag
        if tag in ("article-title", "title", "p", "label") and el.text is not None or tag in ("p", "title"):
            pass
    # body paragraphs
    for sec in root.iter():
        if sec.tag in ("title", "p"):
            out.append(text_of(sec))
        elif sec.tag == "table-wrap":
            lab = sec.find("label"); cap = sec.find("caption")
            out.append("TABLE " + (text_of(lab) if lab is not None else "") + " " + (text_of(cap) if cap is not None else ""))
            for tr in sec.iter("tr"):
                out.append(" | ".join(text_of(c) for c in tr if c.tag in ("td", "th")))
            for fn in sec.iter("table-wrap-foot"):
                out.append("FOOT " + text_of(fn))
        elif sec.tag == "disp-formula":
            out.append("FORMULA " + text_of(sec))
    return "\n".join(out)

if __name__ == "__main__":
    open(sys.argv[2], "w").write(jats_to_text(sys.argv[1]))
