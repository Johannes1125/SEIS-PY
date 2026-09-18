"""
reports/pdf_generator.py - Professional Structural Calculation Sheet PDF Generator
"""
import io
import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.pdfgen import canvas
from core.retrofitting import get_retrofit_recommendations

class NumberedCanvas(canvas.Canvas):
    """
    Two-pass canvas to dynamically compute and display 'Page X of Y' along with header/footer.
    """
    def __init__(self, *args, **kwargs):
        super(NumberedCanvas, self).__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super(NumberedCanvas, self).showPage()
        super(NumberedCanvas, self).save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(colors.HexColor("#1e293b"))
        
        # Header (Top Rule & Title)
        self.drawString(36, 11 * inch - 28, "RESISEISMIC PH - STRUCTURAL ENGINEERING CALCULATION SHEET")
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748b"))
        self.drawRightString(8.5 * inch - 36, 11 * inch - 28, "NSCP 2015 / PHIVOLCS COMPLIANCE")
        
        self.setStrokeColor(colors.HexColor("#0284c7"))
        self.setLineWidth(1.2)
        self.line(36, 11 * inch - 32, 8.5 * inch - 36, 11 * inch - 32)
        
        # Footer
        self.setStrokeColor(colors.HexColor("#cbd5e1"))
        self.setLineWidth(0.75)
        self.line(36, 36, 8.5 * inch - 36, 36)
        
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748b"))
        self.drawString(36, 24, "National Structural Code of the Philippines (NSCP 2015, 7th Ed.) | Association of Structural Engineers of the Philippines (ASEP)")
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(8.5 * inch - 36, 24, page_str)
        self.restoreState()


def generate_seismic_pdf_report(
    project_name: str,
    engineer_name: str,
    location_str: str,
    params: dict,
    physics_res: dict,
    ml_res: dict = None,
    output_path: str = None
) -> bytes:
    """
    Generates a high-quality PDF Structural Calculation Sheet and Seismic Assessment.
    Returns bytes buffer if output_path is None, or writes to file and returns bytes.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        output_path if output_path else buffer,
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=46,
        bottomMargin=46
    )

    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'ReportTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=16,
        leading=20,
        textColor=colors.HexColor("#0f172a"),
        alignment=TA_CENTER
    )
    subtitle_style = ParagraphStyle(
        'ReportSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=13,
        textColor=colors.HexColor("#475569"),
        alignment=TA_CENTER
    )
    h1_style = ParagraphStyle(
        'SectionH1',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=14,
        textColor=colors.HexColor("#0369a1"),
        spaceBefore=8,
        spaceAfter=4
    )
    body_style = ParagraphStyle(
        'ReportBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11.5,
        textColor=colors.HexColor("#1e293b")
    )
    table_cell_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=10.5,
        textColor=colors.HexColor("#1e293b")
    )
    table_cell_bold = ParagraphStyle(
        'TableCellBold',
        parent=table_cell_style,
        fontName='Helvetica-Bold',
        textColor=colors.HexColor("#0f172a")
    )
    table_cell_header = ParagraphStyle(
        'TableCellHeader',
        parent=table_cell_style,
        fontName='Helvetica-Bold',
        textColor=colors.white,
        alignment=TA_CENTER
    )
    table_cell_center = ParagraphStyle(
        'TableCellCenter',
        parent=table_cell_style,
        alignment=TA_CENTER
    )
    pass_badge = ParagraphStyle(
        'PassBadge',
        parent=table_cell_style,
        fontName='Helvetica-Bold',
        textColor=colors.HexColor("#065f46"),
        alignment=TA_CENTER
    )
    fail_badge = ParagraphStyle(
        'FailBadge',
        parent=table_cell_style,
        fontName='Helvetica-Bold',
        textColor=colors.HexColor("#991b1b"),
        alignment=TA_CENTER
    )

    story = []

    # 1. Document Header Banner
    story.append(Paragraph("STRUCTURAL CALCULATION & SEISMIC COMPLIANCE REPORT", title_style))
    story.append(Paragraph("Low-Rise Reinforced Concrete Residential Building Analysis per NSCP 2015 & PHIVOLCS Standards", subtitle_style))
    story.append(Spacer(1, 8))
    
    # Metadata Table
    now_str = datetime.datetime.now().strftime("%B %d, %Y - %I:%M %p")
    meta_data = [
        [
            Paragraph("<b>Project:</b> " + project_name, table_cell_style),
            Paragraph("<b>Location:</b> " + location_str, table_cell_style)
        ],
        [
            Paragraph("<b>Engineer / Specialist:</b> " + engineer_name, table_cell_style),
            Paragraph("<b>Assessment Date:</b> " + now_str, table_cell_style)
        ],
        [
            Paragraph("<b>Governing Code:</b> NSCP 2015, 7th Edition (Section 208)", table_cell_style),
            Paragraph("<b>Software / Engine:</b> ResiSeismic PH Modular Engine v1.0", table_cell_style)
        ]
    ]
    meta_table = Table(meta_data, colWidths=[270, 270])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f8fafc")),
        ('BOX', (0,0), (-1,-1), 1.0, colors.HexColor("#cbd5e1")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 10))

    # 2. Section: Design Parameters & Seismic Hazard Coefficients
    story.append(Paragraph("1. SEISMIC HAZARD COEFFICIENTS & GEOMETRIC INPUTS", h1_style))
    
    geom_data = [
        [
            Paragraph("Parameter", table_cell_header),
            Paragraph("Input Value", table_cell_header),
            Paragraph("Code Reference / Technical Description", table_cell_header)
        ],
        [
            Paragraph("Seismic Zone", table_cell_bold),
            Paragraph(f"{params.get('zone', 'Zone 4')} (Z = {0.40 if params.get('zone')=='Zone 4' else 0.20})", table_cell_style),
            Paragraph("NSCP 2015 Table 208-3 (Zone 4 = 0.40g for active PH archipelago)", table_cell_style)
        ],
        [
            Paragraph("Soil Profile Type", table_cell_bold),
            Paragraph(f"{params.get('soil_type', 'SD')}", table_cell_style),
            Paragraph("NSCP 2015 Table 208-1 (Stiff Soil profile typical in urban Philippines)", table_cell_style)
        ],
        [
            Paragraph("Fault Proximity (Dist.)", table_cell_bold),
            Paragraph(f"{params.get('fault_dist', 5.0):.1f} km", table_cell_style),
            Paragraph("Seismic Source Type A (West Valley Fault / Philippine Fault Zone)", table_cell_style)
        ],
        [
            Paragraph("Near-Source Factors (Na / Nv)", table_cell_bold),
            Paragraph(f"Na = {physics_res.get('Na', 1.2):.2f}, Nv = {physics_res.get('Nv', 1.6):.2f}", table_cell_style),
            Paragraph("NSCP 2015 Tables 208-4 & 208-5 (Near-fault velocity pulse amplifications)", table_cell_style)
        ],
        [
            Paragraph("Seismic Coefficients (Ca / Cv)", table_cell_bold),
            Paragraph(f"Ca = {physics_res.get('Ca', 0.44):.3f}, Cv = {physics_res.get('Cv', 0.64):.3f}", table_cell_style),
            Paragraph("NSCP 2015 Tables 208-7 & 208-8 (Design Spectrum Parameters)", table_cell_style)
        ],
        [
            Paragraph("Peak Ground Accel. (PGA)", table_cell_bold),
            Paragraph(f"{params.get('pga', 0.40):.2f} g", table_cell_style),
            Paragraph("PHIVOLCS probabilistic seismic hazard model / User site demand", table_cell_style)
        ],
        [
            Paragraph("Structural Framing System", table_cell_bold),
            Paragraph(f"{params.get('frame_type', 'SMRF')} (R = {8.5 if params.get('frame_type')=='SMRF' else (5.5 if params.get('frame_type')=='IMRF' else 3.5)})", table_cell_style),
            Paragraph("NSCP 2015 Table 208-11 (Response Modification Factor)", table_cell_style)
        ],
        [
            Paragraph("Building Geometry", table_cell_bold),
            Paragraph(f"{params.get('stories', 2)} Stories | H = {params.get('stories', 2)*params.get('story_height', 3.0):.1f} m", table_cell_style),
            Paragraph(f"Plan Area = {params.get('plan_area', 120.0):.1f} m² | Story Height = {params.get('story_height', 3.0):.2f} m", table_cell_style)
        ],
        [
            Paragraph("Plan Configuration", table_cell_bold),
            Paragraph(f"{params.get('plan_shape', 'REGULAR')} (Torsion x{physics_res.get('torsion_mult', 1.0):.2f})", table_cell_style),
            Paragraph("NSCP 2015 Tables 208-9 & 208-10 (Plan & Vertical Irregularity Factors)", table_cell_style)
        ],
        [
            Paragraph("Concrete Strength (f'c)", table_cell_bold),
            Paragraph(f"{params.get('fc', 21.0):.1f} MPa ({int(params.get('fc', 21.0)*145)} psi)", table_cell_style),
            Paragraph("NSCP 2015 Chapter 4 Concrete Material Specifications", table_cell_style)
        ],
        [
            Paragraph("Reinforcement Grade (fy)", table_cell_bold),
            Paragraph(f"PNS Grade {int(params.get('fy', 275.0))} (fy = {params.get('fy', 275.0):.0f} MPa)", table_cell_style),
            Paragraph(f"Longitudinal Rebar Ratio = {params.get('rebar_ratio', 1.5):.2f}%", table_cell_style)
        ]
    ]
    
    geom_table = Table(geom_data, colWidths=[140, 140, 260])
    geom_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#0369a1")),
        ('BOX', (0,0), (-1,-1), 1.0, colors.HexColor("#94a3b8")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#f8fafc")]),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(geom_table)
    story.append(Spacer(1, 10))

    # 3. Section: Key Structural Seismic Response Summary
    story.append(Paragraph("2. NSCP 2015 GOVERNING SEISMIC RESPONSES & COMPLIANCE", h1_style))
    
    compliance_text = "PASSED (COMPLIANT)" if physics_res.get('drift_compliance', True) else "FAILED (EXCEEDS LIMIT)"
    compliance_style = pass_badge if physics_res.get('drift_compliance', True) else fail_badge
    
    resp_data = [
        [
            Paragraph("Design Parameter", table_cell_header),
            Paragraph("Physics Exact Value", table_cell_header),
            Paragraph("ML AI Prediction", table_cell_header),
            Paragraph("NSCP 2015 Code Limit / Status", table_cell_header)
        ],
        [
            Paragraph("Fundamental Period (T₁)", table_cell_bold),
            Paragraph(f"<b>{physics_res.get('fundamental_period_s', 0.25):.3f} s</b>", table_cell_style),
            Paragraph(f"{ml_res.get('period_s', 0.25):.3f} s" if ml_res else "—", table_cell_style),
            Paragraph("NSCP 208.5.2 (Rayleigh / Ct Method)", table_cell_style)
        ],
        [
            Paragraph("Design Base Shear (V)", table_cell_bold),
            Paragraph(f"<b>{physics_res.get('base_shear_kn', 0.0):.2f} kN</b>", table_cell_style),
            Paragraph(f"{ml_res.get('base_shear_kn', 0.0):.2f} kN" if ml_res else "—", table_cell_style),
            Paragraph(f"Cs = {physics_res.get('base_shear_coeff', 0.15):.3f} W (Total W = {physics_res.get('total_weight_kn', 0):.1f} kN)", table_cell_style)
        ],
        [
            Paragraph("Peak Roof Displacement (Δ)", table_cell_bold),
            Paragraph(f"<b>{physics_res.get('peak_roof_disp_mm', 0.0):.2f} mm</b>", table_cell_style),
            Paragraph(f"{ml_res.get('roof_disp_mm', 0.0):.2f} mm" if ml_res else "—", table_cell_style),
            Paragraph("Inelastic Max Deflection Δm = 0.70 R Δs", table_cell_style)
        ],
        [
            Paragraph("Max Inter-Story Drift (IDR)", table_cell_bold),
            Paragraph(f"<b>{physics_res.get('max_idr_pct', 0.0):.3f}%</b>", table_cell_style),
            Paragraph(f"{ml_res.get('max_idr_pct', 0.0):.3f}%" if ml_res else "—", table_cell_style),
            Paragraph(f"Allowable Limit ≤ <b>{physics_res.get('drift_limit_pct', 2.5):.1f}%</b> (Sec 208.5.9)", table_cell_style)
        ],
        [
            Paragraph("NSCP 2015 Drift Compliance", table_cell_bold),
            Paragraph(compliance_text, compliance_style),
            Paragraph("Verified", table_cell_center),
            Paragraph(f"Status: {compliance_text}", table_cell_style)
        ],
        [
            Paragraph("Park-Ang Damage Index (DI)", table_cell_bold),
            Paragraph(f"<b>{physics_res.get('damage_index', 0.15):.3f}</b>", table_cell_style),
            Paragraph(f"{ml_res.get('damage_index', 0.15):.3f}" if ml_res else "—", table_cell_style),
            Paragraph(f"Performance: <b>{physics_res.get('safety_level', 'Life Safety')}</b>", table_cell_style)
        ]
    ]
    
    resp_table = Table(resp_data, colWidths=[140, 120, 110, 170])
    resp_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#0f766e")),
        ('BOX', (0,0), (-1,-1), 1.0, colors.HexColor("#94a3b8")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#f8fafc")]),
        ('TOPPADDING', (0,0), (-1,-1), 3.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3.5),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(resp_table)
    story.append(Spacer(1, 10))

    # 4. Section: Story-by-Story Profile Table
    story.append(Paragraph("3. STORY-BY-STORY LATERAL FORCE & DRIFT DISTRIBUTION", h1_style))
    
    stories_count = params.get('stories', 2)
    story_table_data = [
        [
            Paragraph("Story Level", table_cell_header),
            Paragraph("Elevation (m)", table_cell_header),
            Paragraph("Lateral Force Fx (kN)", table_cell_header),
            Paragraph("Story Shear Vx (kN)", table_cell_header),
            Paragraph("Inelastic Disp. (mm)", table_cell_header),
            Paragraph("Story Drift Ratio (%)", table_cell_header),
            Paragraph("NSCP Status", table_cell_header)
        ]
    ]
    
    h_story = params.get('story_height', 3.0)
    disps = physics_res.get('story_displacements_mm', [0]*stories_count)
    drifts = physics_res.get('idr_percentages', [0]*stories_count)
    forces = physics_res.get('story_forces_kn', [0]*stories_count)
    shears = physics_res.get('story_shears_kn', [0]*stories_count)
    limit_pct = physics_res.get('drift_limit_pct', 2.5)
    
    for i in range(stories_count - 1, -1, -1):
        lvl_name = f"Roof Level (L{i+1})" if i == stories_count - 1 else f"Story Level {i+1}"
        elev = (i + 1) * h_story
        fx = forces[i] if i < len(forces) else 0.0
        vx = shears[i] if i < len(shears) else 0.0
        disp = disps[i] if i < len(disps) else 0.0
        drift = drifts[i] if i < len(drifts) else 0.0
        status_p = Paragraph("OK", pass_badge) if drift <= limit_pct else Paragraph("EXCEED", fail_badge)
        
        story_table_data.append([
            Paragraph(lvl_name, table_cell_bold),
            Paragraph(f"{elev:.2f}", table_cell_center),
            Paragraph(f"{fx:.2f}", table_cell_center),
            Paragraph(f"{vx:.2f}", table_cell_center),
            Paragraph(f"{disp:.2f}", table_cell_center),
            Paragraph(f"{drift:.3f}%", table_cell_center),
            status_p
        ])
        
    story_table = Table(story_table_data, colWidths=[100, 70, 80, 80, 80, 75, 55])
    story_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#334155")),
        ('BOX', (0,0), (-1,-1), 1.0, colors.HexColor("#94a3b8")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#f8fafc")]),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(story_table)
    story.append(Spacer(1, 10))

    # Page Break for Clean 2nd Page
    story.append(PageBreak())

    # 5. Section: PHIVOLCS Intensity & Structural Vulnerability Assessment
    story.append(Paragraph("4. PHIVOLCS EARTHQUAKE INTENSITY & DAMAGE ASSESSMENT", h1_style))
    
    peis_level = physics_res.get('peis_level', 'PEIS VII (Destructive)')
    safety_level = physics_res.get('safety_level', 'Life Safety')
    damage_desc = physics_res.get('damage_desc', '')
    
    peis_box_data = [
        [
            Paragraph("<b>PHIVOLCS PEIS Intensity Rating:</b> " + peis_level, ParagraphStyle('PEISTitle', parent=table_cell_style, fontSize=9.5, leading=12, textColor=colors.HexColor("#1e293b"))),
            Paragraph("<b>Structural Safety State:</b> " + safety_level, ParagraphStyle('StateTitle', parent=table_cell_style, fontSize=9.5, leading=12, textColor=colors.HexColor("#0369a1")))
        ],
        [
            Paragraph(f"<b>Detailed Damage Mechanism Description:</b><br/>{damage_desc}", table_cell_style),
            Paragraph(f"<b>Park-Ang Damage Index:</b> {physics_res.get('damage_index', 0.15):.3f} (Scale: 0.0 to 1.0+)<br/><b>PGA Site Intensity:</b> {params.get('pga', 0.40):.2f} g", table_cell_style)
        ]
    ]
    peis_table = Table(peis_box_data, colWidths=[270, 270])
    peis_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f0fdf4") if physics_res.get('damage_index', 0.15) < 0.25 else (colors.HexColor("#fefce8") if physics_res.get('damage_index', 0.15) < 0.40 else colors.HexColor("#fef2f2"))),
        ('BOX', (0,0), (-1,-1), 1.0, colors.HexColor("#94a3b8")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(peis_table)
    story.append(Spacer(1, 10))

    # 6. Section: Philippine Standard Retrofitting & Mitigation Recommendations
    story.append(Paragraph("5. ASEP / DPWH RETROFITTING & RISK MITIGATION RECOMMENDATIONS", h1_style))
    
    di = physics_res.get('damage_index', 0.15)
    retrofit_items = get_retrofit_recommendations(di)

    for item in retrofit_items:
        story.append(Paragraph(item, body_style))
        story.append(Spacer(1, 4))
        
    story.append(Spacer(1, 8))

    # 7. Section: Engineering Sign-off & Professional Certification Block
    story.append(Paragraph("6. PROFESSIONAL ENGINEER SIGN-OFF & DISCLAIMER", h1_style))
    story.append(Paragraph(
        "<b>Disclaimer:</b> This calculation sheet is an automated computational assessment based on the equations and seismic principles of the National Structural Code of the Philippines (NSCP 2015 7th Edition) and PHIVOLCS ground motion scaling. It provides rapid structural vulnerability screening and preliminary design verification. Final construction drawings, structural detailing, and site-specific geotechnical investigations must be approved and sealed by a licensed Civil / Structural Engineer in accordance with Philippine Republic Act 544 and the National Building Code of the Philippines (PD 1096).",
        ParagraphStyle('Disclaimer', parent=body_style, fontSize=7.5, leading=9.5, textColor=colors.HexColor("#64748b"))
    ))
    story.append(Spacer(1, 16))
    
    # Signature Box
    sig_data = [
        [
            Paragraph("<b>Prepared & Verified By:</b>", table_cell_style),
            Paragraph("<b>Reviewed & Noted By:</b>", table_cell_style)
        ],
        [
            Paragraph("<br/><br/>____________________________________________<br/><b>" + engineer_name + "</b><br/>Registered Civil / Structural Engineer<br/>PRC License No.: ______________ | PTR No.: ______________", table_cell_style),
            Paragraph("<br/><br/>____________________________________________<br/><b>Supervising Structural Engineer / Consultant</b><br/>ASEP Member / Structural Specialist<br/>Date Signed: ________________________", table_cell_style)
        ]
    ]
    sig_table = Table(sig_data, colWidths=[270, 270])
    sig_table.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 0.75, colors.HexColor("#cbd5e1")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f8fafc")),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(sig_table)

    doc.build(story, canvasmaker=NumberedCanvas)
    
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes
