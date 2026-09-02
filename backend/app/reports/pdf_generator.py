import os
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def generate_scan_pdf_report(scan_data: dict) -> bytes:
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    story = []
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#1E293B'),
        spaceAfter=12
    )

    story.append(Paragraph("<b>NirikshanX Legal Metrology Verification Report</b>", title_style))
    story.append(Spacer(1, 10))

    scan_id = scan_data.get("id", "N/A")
    status = scan_data.get("status", "UNKNOWN")
    is_valid = scan_data.get("is_valid", False)

    meta_text = f"""
    <b>Scan ID:</b> #{scan_id}<br/>
    <b>Status:</b> {'PASSED' if is_valid else 'NON-COMPLIANT / REJECTED'}<br/>
    <b>Processing Time:</b> {scan_data.get('processing_time_seconds', 0.0)}s<br/>
    """
    story.append(Paragraph(meta_text, styles['Normal']))
    story.append(Spacer(1, 15))

    # Violations table
    violations = scan_data.get("compliance_result", {}).get("violations", [])
    table_data = [["Rule ID", "Field", "Severity", "Description"]]

    if violations:
        for v in violations:
            table_data.append([
                v.get("rule_id", ""),
                v.get("field_name", ""),
                v.get("severity", ""),
                v.get("description", "")
            ])
    else:
        table_data.append(["N/A", "N/A", "NONE", "All required Legal Metrology declarations detected & compliant."])

    t = Table(table_data, colWidths=[80, 80, 70, 250])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0F172A')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F8FAFC')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
    ]))
    story.append(t)

    doc.build(story)
    pdf = buffer.getvalue()
    buffer.close()
    return pdf
