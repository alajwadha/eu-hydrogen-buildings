"""Author the Word style template for the V8 build (the agreed Oxford / academic look).

Starts from pandoc's default reference.docx (which already carries every style name pandoc
maps content onto) and retunes the styles natively: a refined serif body (Cambria), justified
text with academic line spacing, a clear bold heading hierarchy, a centred title block, italic
captions, A4 with 2.5 cm margins, and a centred page number in the footer.

Run: python make_ref_docx.py            (rewrites _ref_v8.docx in place)
"""
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

REF = "_ref_v8.docx"
BODY = "Cambria"
INK = RGBColor(0x1A, 0x1A, 0x1A)
d = Document(REF)


def style(name):
    try:
        return d.styles[name]
    except KeyError:
        return None


def setf(name, size=None, bold=None, italic=None, color=None, font=BODY):
    s = style(name)
    if s is None:
        return
    f = s.font
    f.name = font
    if size is not None:
        f.size = Pt(size)
    if bold is not None:
        f.bold = bold
    if italic is not None:
        f.italic = italic
    if color is not None:
        f.color.rgb = color


def setp(name, align=None, line=None, before=None, after=None):
    s = style(name)
    if s is None:
        return
    pf = s.paragraph_format
    if align is not None:
        pf.alignment = align
    if line is not None:
        pf.line_spacing = line
    if before is not None:
        pf.space_before = Pt(before)
    if after is not None:
        pf.space_after = Pt(after)


# body
setf("Normal", 11.5, color=INK)
setp("Normal", WD_ALIGN_PARAGRAPH.JUSTIFY, 1.4, 0, 6)
for s in ("Body Text", "First Paragraph", "Compact", "Footnote Text", "Block Text"):
    setf(s, 11.5)
    setp(s, WD_ALIGN_PARAGRAPH.JUSTIFY, 1.4, 0, 6)
# title block
setf("Title", 20, bold=True, color=INK)
setp("Title", WD_ALIGN_PARAGRAPH.CENTER, 1.1, 0, 6)
setf("Author", 12)
setp("Author", WD_ALIGN_PARAGRAPH.CENTER, 1.1, 0, 4)
setf("Date", 10.5)
setp("Date", WD_ALIGN_PARAGRAPH.CENTER, 1.1, 0, 12)
# headings
setf("Heading 1", 15, bold=True, color=INK)
setp("Heading 1", line=1.1, before=16, after=6)
setf("Heading 2", 13, bold=True, color=INK)
setp("Heading 2", line=1.1, before=10, after=4)
setf("Heading 3", 11.5, bold=True, italic=True, color=INK)
setp("Heading 3", line=1.1, before=8, after=2)
# captions
for s in ("Image Caption", "Caption", "Table Caption"):
    setf(s, 10, italic=True)
    setp(s, WD_ALIGN_PARAGRAPH.CENTER, 1.15, 2, 8)
# abstract
setf("Abstract", 11)
setp("Abstract", WD_ALIGN_PARAGRAPH.JUSTIFY, 1.3, 0, 6)

# hyperlinks: black text (parity with the PDF's hidelinks). The Hyperlink character style is
# what pandoc tags link runs with; colour it black so URLs/DOIs in the reference list and body
# are not blue. fix_docx_tables.py also forces black per-run as a belt-and-braces measure.
hl = style("Hyperlink")
if hl is not None:
    hl.font.color.rgb = INK

# page: A4, 2.5 cm margins
sec = d.sections[0]
sec.page_width, sec.page_height = Cm(21.0), Cm(29.7)
sec.left_margin = sec.right_margin = Cm(2.5)
sec.top_margin = sec.bottom_margin = Cm(2.5)

# centred page number in the footer
p = sec.footer.paragraphs[0]
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
fld = OxmlElement("w:fldSimple"); fld.set(qn("w:instr"), " PAGE ")
r = OxmlElement("w:r"); t = OxmlElement("w:t"); t.text = "1"; r.append(t); fld.append(r)
p._p.append(fld)

d.save(REF)
print(f"retuned {REF}: Cambria body, justified, numbered headings, A4, footer page number")
