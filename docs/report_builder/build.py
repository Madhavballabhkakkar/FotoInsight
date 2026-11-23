"""Build the FotoInsight internship report on top of the reference report's styles.

Run from the repository root:
    .venv/bin/python docs/report_builder/build.py [output.docx]
"""
import copy
import math
import re
import sys
from pathlib import Path

from docx import Document
from docx.oxml import parse_xml
from docx.oxml.ns import qn, nsdecls

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "docs" / "report_builder"))

import content_a, content_b, content_c, content_d  # noqa: E402
from lib import Report, esc  # noqa: E402

BASE = "/Users/madhavballabhkakkar/Downloads/Aman Sharma K26059 Internship Report.docx"
OUT = next((a for a in sys.argv[1:] if not a.startswith("--")), None) or str(ROOT / "docs" / "FotoInsight_Internship_Report_Jayanti_Jha.docx")
CERT = ROOT / "docs" / "report_assets" / "compressed" / "jayanti_certificate.jpg"

TITLE = "FotoInsight: Photography Studio Website and Data Analytics Dashboard"
NAME = "Jayanti Jha"
SID = "K25341"

doc = Document(BASE)
body = doc.element.body
kids = list(body)

# sanity checks on the reference layout -------------------------------------------------
def ptext(el):
    return "".join(t.text or "" for t in el.iter(qn("w:t")))

assert ptext(kids[19]) == "Certificate", ptext(kids[19])
assert ptext(kids[46]) == "Introduction", ptext(kids[46])
assert ptext(kids[40]) == "Appendix"
assert kids[-1].tag == qn("w:sectPr")


# front matter helpers --------------------------------------------------------------------
def run_xml(text, bold=False, sz=26):
    b = "<w:b/><w:bCs/>" if bold else ""
    return (
        f'<w:r {nsdecls("w")}><w:rPr>{b}<w:sz w:val="{sz}"/><w:szCs w:val="{sz}"/></w:rPr>'
        f'<w:t xml:space="preserve">{esc(text)}</w:t></w:r>'
    )


def rebuild(p, text, sz=26):
    """Replace all runs of paragraph p; **x** marks bold segments. pPr (including sectPr) is kept."""
    for r_ in p.findall(qn("w:r")):
        p.remove(r_)
    for hl in p.findall(qn("w:hyperlink")):
        p.remove(hl)
    for i, part in enumerate(re.split(r"\*\*", text)):
        if part:
            p.append(parse_xml(run_xml(part, bold=(i % 2 == 1), sz=sz)))


def set_same_format(p, new):
    """Keep the first run (and its formatting) and replace the text of the whole paragraph."""
    runs = p.findall(qn("w:r"))
    first = runs[0]
    for extra in runs[1:]:
        p.remove(extra)
    for t in first.findall(qn("w:t")):
        first.remove(t)
    t = parse_xml(f'<w:t {nsdecls("w")} xml:space="preserve">{esc(new)}</w:t>')
    first.append(t)


def replace_in_paragraphs(root, mapping):
    hits = 0
    for p in root.iter(qn("w:p")):
        txt = ptext(p).strip()
        if txt in mapping and p.findall(qn("w:r")):
            set_same_format(p, mapping[txt])
            hits += 1
    return hits


# ---- cover page table: guides and submitted-by ----------------------------------------
n = replace_in_paragraphs(
    kids[7],
    {
        "Designation": "Fotographiya Ventures Pvt. Ltd., Kota",
        "Aman Sharma": NAME,
        "(K26059)": f"({SID})",
    },
)
assert n >= 3, n

# ---- certificate image -------------------------------------------------------------------
cert_p = kids[20]
blip = cert_p.find(".//" + qn("a:blip"))
old_rid = blip.get(qn("r:embed"))
new_rid, _img = doc.part.get_or_add_image(str(CERT))
blip.set(qn("r:embed"), new_rid)
CX = 5775960
CY = int(CX * 576 / 1024)
for ext in cert_p.iter("{http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing}extent"):
    ext.set("cx", str(CX))
    ext.set("cy", str(CY))
for ext in cert_p.iter("{http://schemas.openxmlformats.org/drawingml/2006/main}ext"):
    if ext.get("cx"):
        ext.set("cx", str(CX))
        ext.set("cy", str(CY))
if old_rid != new_rid:
    del doc.part.rels[old_rid]

# ---- acknowledgement ---------------------------------------------------------------------
rebuild(
    kids[22],
    "I am grateful to **Mr. Mohit Barthunia** (Founder & CEO) **Fotographiya Ventures Pvt. Ltd.** for giving me the internship "
    "opportunity as a **Data Analyst** from 01 June 2026 to 15 July 2026. He trusted me with a real project, and I tried to do my "
    "best in every task. I also thank **Ms. Princu Kherada** (Director) for guiding me during training and providing me with genuine feedback.",
)
rebuild(
    kids[23],
    "External Guide Mr. Ajay Raj Kushwah reviewed my work during the internship and guided me whenever I got stuck while building "
    "the studio website and the analytics, so that I could find the solution by myself.",
)
rebuild(
    kids[24],
    "Internal Guide Ms. Namrata Kashyap kept a regular check on my progress and helped me present this work in a proper report format. "
    "Thanks, are also due to the faculty members and Head of Department, School of Computer Application & Technology, Career Point "
    "University, Kota. I also thank my family members and friends for their patience.",
)
set_same_format(kids[25], NAME)
set_same_format(kids[26], SID)

# ---- declaration -------------------------------------------------------------------------
rebuild(
    kids[30],
    f"I hereby declare that this Project Report titled {TITLE}, submitted by me to the School of Computer Application and Technology "
    "(SOCA), Career Point University, Kota, with the approval of my project guides, is a bona fide work undertaken by me. It has not "
    "been submitted to any other University or Institution for the award of any degree or diploma, and it has not been published before.",
)
n = replace_in_paragraphs(
    kids[31],
    {
        "Fotographiya: Full-Stack MERN Blog CMS": TITLE,
        "Aman Sharma (K26059)": f"{NAME} ({SID})",
    },
)
assert n == 2, n

# ---- company overview table ----------------------------------------------------------------
replace_in_paragraphs(kids[35], {"Mr. Princu Kherada": "Ms. Princu Kherada"})

# ---- last paragraph of the front matter (carries the section break) ---------------------------
rebuild(
    kids[38],
    "For a photography business, a website that shows services and prices clearly, a simple way to receive enquiries, and a trustworthy "
    "view of bookings, payments and customers are all required. During my 45-day internship as a **Data Analyst** from 01st June 2026 "
    "to 15th July 2026, I worked on providing this for the startup by building FotoInsight, a studio website with a staff dashboard and "
    "Pandas and NumPy analytics. My External Guide was **Mr. Ajay Raj Kushwah**.",
)

# keep the TOC sdt, drop everything after the appendix list -------------------------------------
sdt = kids[39]
assert sdt.tag == qn("w:sdt")
for el in kids[46:-1]:
    body.remove(el)

# ------------------------------------------------------------------------------------------------
# body content
# ------------------------------------------------------------------------------------------------
assets = ROOT / "docs" / "report_assets"
r = Report(doc, assets)
import os

os.chdir(ROOT)
A = {}
content_a.build(r, A)
content_b.build(r, A)
content_c.build(r, A)
content_d.build_d(r, A)
content_d.build_e(r, A)


# ------------------------------------------------------------------------------------------------
# page-number estimate for the table of contents (Word refreshes it on open)
# ------------------------------------------------------------------------------------------------
PAGE_H = 9.5
LINE_IN = 0.29


def est_pages(items, first_page):
    page, y = first_page, 0.0
    marks = []  # page for every heading in order

    def put(h):
        nonlocal page, y
        if y + h > PAGE_H:
            page += 1
            y = 0.0
        y += h

    for kind, val in items:
        if kind == "h1":
            if y > 0:
                page += 1
            y = 0.0
            marks.append(page)
            y += 0.55
        elif kind == "h2":
            put(0.5)
            marks.append(page)
        elif kind == "h3":
            put(0.4)
            marks.append(page)
        elif kind == "p":
            lines = max(1, math.ceil((val or 1) / 88))
            put(lines * LINE_IN + 0.09)
        elif kind == "img":
            put(val + 0.2)
        elif kind == "code":
            put(val * 0.2 + 0.5)
        elif kind == "pb":
            if y > 0:
                page += 1
                y = 0.0
        elif kind == "table":
            widths, rows, headers, size = val
            cpi = 13.5 * 22 / size

            def row_h(cells):
                m = 1
                for c, w in zip(cells, widths):
                    cpl = max(4, int(((w - 170) / 1440) * cpi))
                    lines = sum(max(1, math.ceil(len(x) / cpl)) for x in str(c).split("\n"))
                    m = max(m, lines)
                return m * (size / 2 * 1.2 / 72) + 0.1

            put(row_h(headers))
            for row in rows:
                put(row_h(row))
    return marks, page


toc = r.toc
toc_pages = max(1, math.ceil((len(toc) + 2) / 38))
first_page = 6 + toc_pages + 1
marks, last_page = est_pages(r.est_items, first_page)
assert len(marks) == len(toc), (len(marks), len(toc))

import json

Path(ROOT / "docs" / "report_builder" / "toc.json").write_text(
    json.dumps([[l, n, t] for (l, n, t, _b) in toc], ensure_ascii=False), encoding="utf-8"
)
pages_file = ROOT / "docs" / "report_builder" / "pages.json"
if pages_file.exists() and "--estimate" not in sys.argv:
    real = json.loads(pages_file.read_text())
    if len(real) == len(toc):
        marks = real
        print("using measured page numbers from pages.json")

# ---- rebuild the TOC -------------------------------------------------------------------------------
content = sdt.find(qn("w:sdtContent"))
paras = content.findall(qn("w:p"))
for extra in paras[1:]:
    content.remove(extra)

NP = "<w:rPr><w:noProof/></w:rPr>"


def toc_entry(i, level, number, text, bm, page, first, last):
    runs = ""
    if first:
        runs += '<w:r><w:fldChar w:fldCharType="begin"/></w:r><w:r><w:instrText xml:space="preserve"> TOC \\o "1-3" \\h \\z \\u </w:instrText></w:r><w:r><w:fldChar w:fldCharType="separate"/></w:r>'
    if number:
        label = f"<w:r>{NP}<w:t>{esc(number)}</w:t></w:r><w:r>{NP}<w:tab/><w:t>{esc(text)}</w:t></w:r>"
    else:
        label = f"<w:r>{NP}<w:t>{esc(text)}</w:t></w:r>"
    link = (
        f'<w:hyperlink w:anchor="{bm}" w:history="1">{label}<w:r>{NP}<w:tab/></w:r>'
        f'<w:r>{NP}<w:fldChar w:fldCharType="begin"/></w:r>'
        f'<w:r>{NP}<w:instrText xml:space="preserve"> PAGEREF {bm} \\h </w:instrText></w:r>'
        f'<w:r>{NP}<w:fldChar w:fldCharType="separate"/></w:r>'
        f"<w:r>{NP}<w:t>{page}</w:t></w:r>"
        f'<w:r>{NP}<w:fldChar w:fldCharType="end"/></w:r></w:hyperlink>'
    )
    end = '<w:r><w:fldChar w:fldCharType="end"/></w:r>' if last else ""
    return parse_xml(
        f'<w:p {nsdecls("w")}><w:pPr><w:pStyle w:val="TOC{level}"/>{NP}</w:pPr>{runs}{link}{end}</w:p>'
    )


for i, ((level, number, text, bm), page) in enumerate(zip(toc, marks)):
    content.append(toc_entry(i, level, number, text, bm, page, i == 0, i == len(toc) - 1))

# ---- footer / header -----------------------------------------------------------------------------
footer = doc.sections[-1].footer
for p in footer._element.iter(qn("w:p")):
    for t in p.iter(qn("w:t")):
        if (t.text or "").startswith("Project Title"):
            t.text = f"Project Title: {TITLE}"
            break

# ---- settings: let Word refresh the TOC when the file is opened ---------------------------------
settings = doc.settings.element
if settings.find(qn("w:updateFields")) is None:
    uf = parse_xml(f'<w:updateFields {nsdecls("w")} w:val="true"/>')
    anchor = None
    for tag in ("w:hdrShapeDefaults", "w:footnotePr", "w:endnotePr", "w:compat"):
        anchor = settings.find(qn(tag))
        if anchor is not None:
            break
    anchor.addprevious(uf)

# ---- core properties ------------------------------------------------------------------------------
cp = doc.core_properties
cp.author = NAME
cp.last_modified_by = NAME
cp.title = f"Internship Report - {TITLE}"
cp.subject = "BCA Colloquium-II (CAC771), Career Point University, Kota"
cp.comments = ""
cp.keywords = ""

# ---- drop relationships that nothing refers to any more (old images and links) ----------------------
from lxml import etree

doc_xml = etree.tostring(doc.element).decode()
used = set(re.findall(r'r:(?:id|embed|link)="(rId\d+)"', doc_xml))
used.update(
    rel.rId
    for rel in doc.part.rels.values()
    if rel.reltype.endswith(("/styles", "/numbering", "/settings", "/footnotes", "/endnotes", "/fontTable", "/theme", "/webSettings", "/customXml", "/header", "/footer"))
)
for rid, rel in list(doc.part.rels.items()):
    if rid not in used and rel.reltype.endswith(("/image", "/hyperlink")):
        del doc.part.rels[rid]

# ---- colour clean-up: all text black --------------------------------------------------------------
W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"


def strip_colours(root):
    changed = 0
    for el in root.iter(W + "color"):
        for attr in ("themeColor", "themeTint", "themeShade"):
            if el.get(W + attr) is not None:
                del el.attrib[W + attr]
                changed += 1
        if el.get(W + "val") not in ("000000", "auto"):
            el.set(W + "val", "000000")
            changed += 1
    for el in root.iter():
        for attr in ("themeColor", "themeTint", "themeShade", "themeFill", "themeFillTint", "themeFillShade"):
            if el.get(W + attr) is not None:
                del el.attrib[W + attr]
                changed += 1
    return changed


total = strip_colours(doc.element)
total += strip_colours(doc.styles.element)
total += strip_colours(doc.part.numbering_part.element)
last = doc.sections[-1]
total += strip_colours(last.header._element)
total += strip_colours(last.footer._element)
print("colour attributes normalised:", total)

doc.save(OUT)
print("saved", OUT)
print("estimated chapter-1 page", first_page, "last page", last_page, "toc entries", len(toc))
Path(ROOT / "docs" / "report_builder" / "captions.txt").write_text("\n".join(r.captions), encoding="utf-8")
