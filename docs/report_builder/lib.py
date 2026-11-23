"""Helpers that add content to a copy of the reference report using its own styles.

Everything is written with the styles that already exist in the reference file
(Heading1-3, Figure, Caption, TableCaption, ListParagraph, TableText, Code ...), so the
new report keeps the same look. Text is always black.
"""

import copy
import math
import re
from xml.sax.saxutils import escape

from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls, qn
from docx.shared import Emu, Inches

W_NS = nsdecls("w")


def esc(text):
    return escape(text, {'"': "&quot;"})


def runs_xml(text, size=None, base_bold=False, mono=False):
    """Turn 'plain **bold** plain' into run XML."""
    parts = re.split(r"(\*\*.+?\*\*)", text)
    out = []
    for part in parts:
        if not part:
            continue
        bold = base_bold
        if part.startswith("**") and part.endswith("**"):
            part = part[2:-2]
            bold = True
        props = ""
        if mono:
            props += '<w:rFonts w:ascii="Courier New" w:hAnsi="Courier New" w:cs="Courier New"/>'
        if bold:
            props += "<w:b/><w:bCs/>"
        if size:
            props += f'<w:sz w:val="{size}"/><w:szCs w:val="{size}"/>'
        rpr = f"<w:rPr>{props}</w:rPr>" if props else ""
        out.append(f'<w:r>{rpr}<w:t xml:space="preserve">{esc(part)}</w:t></w:r>')
    return "".join(out)


class Report:
    def __init__(self, doc, assets):
        self.doc = doc
        self.body = doc.element.body
        self.assets = assets
        self.toc = []  # (level, number, text, bookmark)
        self.bm_id = 5000
        self.bm_count = 0
        self.chapter = 0
        self.letter = None
        self.sec = 0
        self.fig_no = 0
        self.tab_no = 0
        self.list_no = 100
        self.numbering = doc.part.numbering_part.element
        self.est_items = []  # (kind, value) used to estimate page numbers
        self.captions = []

    # ------------------------------------------------------------------ low level
    def add(self, element):
        sect = self.body.find(qn("w:sectPr"))
        sect.addprevious(element)
        return element

    def xml(self, text):
        return parse_xml(text.replace("<w:p>", f"<w:p {W_NS}>", 1) if text.startswith("<w:p>") else text)

    def para(self, inner, ppr="", style=None):
        sty = f'<w:pStyle w:val="{style}"/>' if style else ""
        props = f"<w:pPr>{sty}{ppr}</w:pPr>" if (sty or ppr) else ""
        el = parse_xml(f"<w:p {W_NS}>{props}{inner}</w:p>")
        return self.add(el)

    # ------------------------------------------------------------------ headings
    def _bookmark(self, text, style, ppr_extra=""):
        self.bm_count += 1
        name = f"_Toc9{self.bm_count:07d}"
        self.bm_id += 1
        inner = (
            f'<w:bookmarkStart w:id="{self.bm_id}" w:name="{name}"/>'
            f'<w:r><w:t xml:space="preserve">{esc(text)}</w:t></w:r>'
            f'<w:bookmarkEnd w:id="{self.bm_id}"/>'
        )
        self.para(inner, ppr_extra, style)
        return name

    def h1(self, text):
        self.chapter += 1
        self.letter = None
        self.sec = 0
        self.fig_no = 0
        self.tab_no = 0
        bm = self._bookmark(text, "Heading1")
        self.toc.append((1, str(self.chapter), text, bm))
        self.est_items.append(("h1", None))
        return bm

    def h2(self, text):
        if self.letter:
            bm = self._bookmark(text, "Heading2", '<w:numPr><w:ilvl w:val="0"/><w:numId w:val="0"/></w:numPr>')
            self.toc.append((2, "", text, bm))
        else:
            self.sec += 1
            bm = self._bookmark(text, "Heading2")
            self.toc.append((2, f"{self.chapter}.{self.sec}", text, bm))
        self.est_items.append(("h2", None))
        return bm

    def h3(self, text):
        bm = self._bookmark(text, "Heading3")
        self.toc.append((3, "", text, bm))
        self.est_items.append(("h3", None))
        return bm

    def annex(self, letter, title):
        """Annexure X (Heading 1, no number) followed by its title (Heading 2, no number)."""
        self.letter = letter
        self.fig_no = 0
        self.tab_no = 0
        bm = self._bookmark(f"Annexure {letter}", "Heading1", '<w:numPr><w:ilvl w:val="0"/><w:numId w:val="0"/></w:numPr>')
        self.toc.append((1, "", f"Annexure {letter}", bm))
        self.est_items.append(("h1", None))
        self.h2(title)

    # ------------------------------------------------------------------ paragraphs
    def p(self, text, size=None, jc=None, keep_next=False, space_after=None):
        ppr = ""
        if keep_next:
            ppr += "<w:keepNext/>"
        if space_after is not None:
            ppr += f'<w:spacing w:after="{space_after}"/>'
        if jc:
            ppr += f'<w:jc w:val="{jc}"/>'
        self.para(runs_xml(text, size), ppr)
        self.est_items.append(("p", len(re.sub(r"\*\*", "", text))))

    def blank(self):
        self.para("")
        self.est_items.append(("p", 0))

    def page_break(self):
        self.para('<w:r><w:br w:type="page"/></w:r>')
        self.est_items.append(("pb", None))

    # ------------------------------------------------------------------ lists
    def _new_num(self, abstract_id, restart=True):
        self.list_no += 1
        num_id = self.list_no
        override = (
            '<w:lvlOverride w:ilvl="0"><w:startOverride w:val="1"/></w:lvlOverride>' if restart else ""
        )
        num = parse_xml(
            f'<w:num {W_NS} w:numId="{num_id}"><w:abstractNumId w:val="{abstract_id}"/>{override}</w:num>'
        )
        existing = self.numbering.findall(qn("w:num"))
        existing[-1].addnext(num)  # keep w:num elements before w:numIdMacAtCleanup
        return num_id

    def _list(self, items, abstract_id, restart=True, ilvl=0):
        num_id = self._new_num(abstract_id, restart)
        for item in items:
            self.list_item(item, num_id, ilvl)
        return num_id

    def list_item(self, item, num_id, ilvl=0):
        if isinstance(item, tuple):
            lead, rest = item
            text = f"**{lead}:** {rest}"
        else:
            text = item
        ppr = f'<w:numPr><w:ilvl w:val="{ilvl}"/><w:numId w:val="{num_id}"/></w:numPr>'
        self.para(runs_xml(text), ppr, "ListParagraph")
        self.est_items.append(("p", len(re.sub(r"\*\*", "", text)) + 8))

    def bullets(self, items):
        return self._list(items, 5)  # round bullet, 720 indent

    def numbered(self, items):
        return self._list(items, 15)  # 1.  2.  3.

    def lettered(self, items):
        return self._list(items, 13)  # a)  b)  c)

    def bullets_sub(self, items, num_id):
        for item in items:
            self.list_item(item, num_id, 1)

    def lead_with_body(self, lead, body, num_id):
        """Bold lead line (numbered) followed by an indented plain paragraph, as in the reference."""
        ppr = f'<w:numPr><w:ilvl w:val="0"/><w:numId w:val="{num_id}"/></w:numPr><w:rPr><w:b/><w:bCs/></w:rPr>'
        self.para(runs_xml(lead, base_bold=True), ppr, "ListParagraph")
        self.para(runs_xml(body), "", "ListParagraph")
        self.est_items.append(("p", len(lead) + 6))
        self.est_items.append(("p", len(body) + 8))

    # ------------------------------------------------------------------ figures and tables
    def _label(self, kind):
        if self.letter:
            prefix = self.letter
        else:
            prefix = str(self.chapter)
        if kind == "fig":
            self.fig_no += 1
            return f"Figure {prefix}.{self.fig_no}"
        self.tab_no += 1
        return f"Table {prefix}.{self.tab_no}"

    def picture(self, path, width_in=6.2, max_height_in=8.4, style="Figure"):
        from PIL import Image

        with Image.open(path) as im:
            w_px, h_px = im.size
        width = Inches(width_in)
        height = int(width * h_px / w_px)
        if height > Inches(max_height_in):
            height = Inches(max_height_in)
            width = int(height * w_px / h_px)
        para = self.doc.add_paragraph(style=style)
        # python-docx appends before sectPr already, but keep the order explicit.
        self.body.remove(para._p)
        self.add(para._p)
        para.add_run().add_picture(str(path), width=Emu(width), height=Emu(height))
        self.est_items.append(("img", height / 914400))
        return para

    def figure(self, path, caption, width_in=6.2, max_height_in=8.3):
        self.picture(path, width_in, max_height_in)
        label = self._label("fig")
        self.para(runs_xml(f"{label}: {caption}"), "", "Caption")
        self.captions.append(f"{label}: {caption}")
        self.est_items.append(("p", 40))
        return label

    def table_caption(self, caption):
        label = self._label("tab")
        self.para(runs_xml(f"{label}: {caption}"), "", "TableCaption")
        self.captions.append(f"{label}: {caption}")
        self.est_items.append(("p", 60))
        return label

    def table(self, headers, rows, widths, size=24, center_cols=(), header_size=None, bold_first=False):
        total = sum(widths)
        header_size = header_size or size
        grid = "".join(f'<w:gridCol w:w="{w}"/>' for w in widths)
        borders = "".join(
            f'<w:{side} w:val="single" w:sz="12" w:space="0" w:color="auto"/>'
            for side in ("top", "left", "bottom", "right", "insideH", "insideV")
        )

        def cell(text, width, style, jc=None, sz=size, bold=False):
            ppr = f'<w:pStyle w:val="{style}"/>'
            if jc:
                ppr += f'<w:jc w:val="{jc}"/>'
            ppr += f'<w:rPr><w:sz w:val="{sz}"/><w:szCs w:val="{sz}"/></w:rPr>'
            paras = []
            for line in str(text).split("\n"):
                paras.append(f"<w:p><w:pPr>{ppr}</w:pPr>{runs_xml(line, sz, base_bold=bold)}</w:p>")
            return (
                f'<w:tc><w:tcPr><w:tcW w:w="{width}" w:type="dxa"/><w:vAlign w:val="center"/></w:tcPr>'
                + "".join(paras)
                + "</w:tc>"
            )

        head = "".join(
            cell(h, w, "TableHeader", "center", header_size) for h, w in zip(headers, widths)
        )
        xml = [
            f'<w:tbl {W_NS}><w:tblPr><w:tblW w:w="{total}" w:type="dxa"/><w:tblBorders>{borders}</w:tblBorders>'
            '<w:tblLayout w:type="fixed"/><w:tblCellMar><w:top w:w="40" w:type="dxa"/><w:left w:w="85" w:type="dxa"/>'
            '<w:bottom w:w="40" w:type="dxa"/><w:right w:w="85" w:type="dxa"/></w:tblCellMar>'
            '<w:tblLook w:val="04A0" w:firstRow="1" w:lastRow="0" w:firstColumn="1" w:lastColumn="0" w:noHBand="0" w:noVBand="1"/>'
            f"</w:tblPr><w:tblGrid>{grid}</w:tblGrid>"
            f"<w:tr><w:trPr><w:cantSplit/><w:tblHeader/></w:trPr>{head}</w:tr>"
        ]
        for row in rows:
            cells = []
            for i, (value, w) in enumerate(zip(row, widths)):
                cells.append(
                    cell(value, w, "TableText", "center" if i in center_cols else None, size, bold_first and i == 0)
                )
            xml.append(f"<w:tr><w:trPr><w:cantSplit/></w:trPr>{''.join(cells)}</w:tr>")
        xml.append("</w:tbl>")
        el = parse_xml("".join(xml))
        self.add(el)
        # spacer paragraph so that following text does not touch the table
        self.para("", '<w:spacing w:after="0"/>')
        self.est_items.append(("table", (widths, rows, headers, size)))

    def code(self, path_label, language, lines, size=22):
        """Two-row table: file path and language on top, code lines below (Code style)."""
        borders = "".join(
            f'<w:{side} w:val="single" w:sz="4" w:space="0" w:color="000000"/>'
            for side in ("top", "left", "bottom", "right", "insideH", "insideV")
        )
        head = (
            f'<w:tr><w:trPr><w:cantSplit/></w:trPr><w:tc><w:tcPr><w:tcW w:w="9026" w:type="dxa"/></w:tcPr>'
            f'<w:p><w:pPr><w:pStyle w:val="TableHeader"/><w:tabs><w:tab w:val="right" w:pos="8856"/></w:tabs></w:pPr>'
            f'<w:r><w:t xml:space="preserve">{esc(path_label)}</w:t></w:r><w:r><w:tab/><w:t>{esc(language)}</w:t></w:r></w:p></w:tc></w:tr>'
        )
        body_paras = []
        for line in lines:
            indent = len(line) - len(line.lstrip(" "))
            ind = f'<w:ind w:left="{indent * 80}"/>' if indent else ""
            body_paras.append(
                f'<w:p><w:pPr><w:pStyle w:val="Code"/>{ind}<w:rPr><w:sz w:val="{size}"/><w:szCs w:val="{size}"/></w:rPr></w:pPr>'
                f'<w:r><w:rPr><w:sz w:val="{size}"/><w:szCs w:val="{size}"/></w:rPr>'
                f'<w:t xml:space="preserve">{esc(line.lstrip(" "))}</w:t></w:r></w:p>'
            )
        el = parse_xml(
            f'<w:tbl {W_NS}><w:tblPr><w:tblW w:w="9026" w:type="dxa"/><w:tblBorders>{borders}</w:tblBorders>'
            '<w:tblLayout w:type="fixed"/><w:tblCellMar><w:top w:w="40" w:type="dxa"/><w:left w:w="85" w:type="dxa"/>'
            '<w:bottom w:w="40" w:type="dxa"/><w:right w:w="85" w:type="dxa"/></w:tblCellMar>'
            '<w:tblLook w:val="04A0" w:firstRow="1" w:lastRow="0" w:firstColumn="1" w:lastColumn="0" w:noHBand="0" w:noVBand="1"/>'
            f'</w:tblPr><w:tblGrid><w:gridCol w:w="9026"/></w:tblGrid>{head}'
            f'<w:tr><w:tc><w:tcPr><w:tcW w:w="9026" w:type="dxa"/></w:tcPr>{"".join(body_paras)}</w:tc></w:tr></w:tbl>'
        )
        self.add(el)
        self.para("", '<w:spacing w:after="0"/>')
        self.est_items.append(("code", len(lines)))

    # ------------------------------------------------------------------ hyperlinks
    def link(self, url):
        rid = self.doc.part.relate_to(
            url, "http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink", is_external=True
        )
        return rid

    def p_with_links(self, pieces, size=None):
        """pieces: list of str or ('url', text). Links are black and underlined."""
        out = []
        for piece in pieces:
            if isinstance(piece, tuple):
                url, label = piece
                rid = self.link(url)
                out.append(
                    f'<w:hyperlink r:id="{rid}" w:history="1" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
                    f'<w:r><w:rPr><w:color w:val="000000"/><w:u w:val="single"/></w:rPr><w:t xml:space="preserve">{esc(label)}</w:t></w:r></w:hyperlink>'
                )
            else:
                out.append(runs_xml(piece, size))
        self.para("".join(out))
        self.est_items.append(("p", sum(len(x if isinstance(x, str) else x[1]) for x in pieces)))
