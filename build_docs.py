import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

def set_cell_background(cell, fill_hex):
    tcPr = cell._element.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), fill_hex)
    tcPr.append(shd)

def create_document():
    doc = Document()
    print("Building NirikshanX Complete Project Documentation.docx...")
    doc.add_heading("NirikshanX: AI-Powered Packaged Commodity Compliance System", 0)
    doc.save("NirikshanX_Complete_Project_Documentation.docx")
    print("Document built successfully.")

if __name__ == "__main__":
    create_document()
