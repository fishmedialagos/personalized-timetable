"""
NOUN 2026_2 Personalized E-Exam Timetable Generator
Streamlit Web App
"""

import streamlit as st
import pandas as pd
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Flowable
)
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from datetime import datetime

# ----------------------- Page Config -----------------------
st.set_page_config(
    page_title="NOUN Personalized Timetable Generator",
    page_icon="📅",
    layout="centered",
    initial_sidebar_state="expanded",
)

# ----------------------- Load Data -----------------------
@st.cache_data
def load_timetable():
    df = pd.read_csv("NOUN_2026_2_Full_Timetable.csv")
    # Normalize course codes for matching
    df["Course Code Clean"] = df["Course Code"].str.upper().str.strip()
    return df

try:
    timetable_df = load_timetable()
except Exception:
    # Fallback path when running from different directory
    timetable_df = pd.read_csv("/home/workdir/artifacts/NOUN_2026_2_Full_Timetable.csv")
    timetable_df["Course Code Clean"] = timetable_df["Course Code"].str.upper().str.strip()

ALL_CODES = sorted(timetable_df["Course Code Clean"].unique().tolist())

# Faculty → Batch mapping (official NOUN split)
BATCH_A_FACULTIES = [
    "Faculty of Arts",
    "Faculty of Computing",
    "Faculty of Education",
    "Faculty of Management Sciences",
]

BATCH_B_FACULTIES = [
    "Faculty of Agricultural Sciences",
    "Faculty of Law",
    "Faculty of Sciences",
    "Faculty of Health Sciences",
    "Faculty of Social Sciences",
]

ALL_FACULTIES = BATCH_A_FACULTIES + BATCH_B_FACULTIES

# ----------------------- PDF Generator -----------------------
class ColoredLine(Flowable):
    def __init__(self, width, thickness=1.5, color=colors.HexColor("#1e3a5f")):
        Flowable.__init__(self)
        self.width = width
        self.thickness = thickness
        self.color = color
        self.height = thickness

    def draw(self):
        self.canv.setStrokeColor(self.color)
        self.canv.setLineWidth(self.thickness)
        self.canv.line(0, 0, self.width, 0)


def generate_pdf(student_info: dict, exams: list) -> bytes:
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=14 * mm,
        leftMargin=14 * mm,
        topMargin=14 * mm,
        bottomMargin=18 * mm,
    )
    usable_width = A4[0] - 28 * mm

    # Styles
    uni_name = ParagraphStyle("UniName", fontName="Helvetica-Bold", fontSize=13,
                              textColor=colors.HexColor("#1e3a5f"), alignment=TA_CENTER, spaceAfter=1*mm)
    doc_title = ParagraphStyle("DocTitle", fontName="Helvetica-Bold", fontSize=11,
                               textColor=colors.HexColor("#2c5282"), alignment=TA_CENTER, spaceAfter=0.5*mm)
    personal_label = ParagraphStyle("PersonalLabel", fontName="Helvetica", fontSize=8,
                                    textColor=colors.HexColor("#4a5568"), alignment=TA_CENTER, spaceAfter=3*mm)
    section_title = ParagraphStyle("SectionTitle", fontName="Helvetica-Bold", fontSize=9,
                                   textColor=colors.white, alignment=TA_CENTER)
    label_style = ParagraphStyle("Label", fontName="Helvetica-Bold", fontSize=8, textColor=colors.HexColor("#1e3a5f"))
    value_style = ParagraphStyle("Value", fontName="Helvetica", fontSize=8, textColor=colors.HexColor("#2d3748"))
    th_style = ParagraphStyle("TH", fontName="Helvetica-Bold", fontSize=7.5, textColor=colors.white, alignment=TA_CENTER)
    cell_style = ParagraphStyle("Cell", fontName="Helvetica", fontSize=7.5, textColor=colors.HexColor("#1a202c"), leading=9.5)
    code_style = ParagraphStyle("Code", fontName="Helvetica-Bold", fontSize=7.5, textColor=colors.HexColor("#1e3a5f"), alignment=TA_CENTER)
    time_style = ParagraphStyle("Time", fontName="Helvetica-Bold", fontSize=7.5, textColor=colors.HexColor("#c53030"), alignment=TA_CENTER)
    sn_style = ParagraphStyle("SN", fontName="Helvetica", fontSize=7.5, alignment=TA_CENTER)
    note_header = ParagraphStyle("NoteHeader", fontName="Helvetica-Bold", fontSize=8, textColor=colors.HexColor("#744210"))
    note_item = ParagraphStyle("NoteItem", fontName="Helvetica", fontSize=7.5, textColor=colors.HexColor("#744210"), leading=10, leftIndent=2*mm)
    support_title = ParagraphStyle("SupportTitle", fontName="Helvetica-Bold", fontSize=9, textColor=colors.HexColor("#276749"), alignment=TA_CENTER)
    support_wish = ParagraphStyle("SupportWish", fontName="Helvetica-Bold", fontSize=10, textColor=colors.HexColor("#22543d"), alignment=TA_CENTER, spaceBefore=1*mm, spaceAfter=1.5*mm)
    support_body = ParagraphStyle("SupportBody", fontName="Helvetica", fontSize=8, textColor=colors.HexColor("#2d3748"), alignment=TA_CENTER, leading=11)
    support_contact = ParagraphStyle("SupportContact", fontName="Helvetica-Bold", fontSize=9, textColor=colors.HexColor("#c53030"), alignment=TA_CENTER, spaceBefore=1.5*mm)
    support_addr = ParagraphStyle("SupportAddr", fontName="Helvetica", fontSize=7.5, textColor=colors.HexColor("#4a5568"), alignment=TA_CENTER)
    disclaimer = ParagraphStyle("Disclaimer", fontName="Helvetica", fontSize=7, textColor=colors.HexColor("#718096"), alignment=TA_CENTER, leading=9, spaceBefore=2*mm)

    story = []

    # Header
    story.append(Paragraph("NATIONAL OPEN UNIVERSITY OF NIGERIA (NOUN)", uni_name))
    story.append(Paragraph("2026_2 E-EXAMINATION FINAL TIMETABLE", doc_title))
    story.append(Paragraph("PERSONALIZED STUDENT EXAMINATION SCHEDULE", personal_label))
    story.append(ColoredLine(usable_width, thickness=1.8))
    story.append(Spacer(1, 3.5 * mm))

    # Student Info
    info_header = Table([[Paragraph("STUDENT INFORMATION", section_title)]], colWidths=[usable_width])
    info_header.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#1e3a5f")),
        ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(info_header)

    info_data = [
        [Paragraph("Student Name", label_style), Paragraph(student_info["name"], value_style),
         Paragraph("Matriculation Number", label_style), Paragraph(student_info["matric"], value_style)],
        [Paragraph("Programme", label_style), Paragraph(student_info["programme"], value_style),
         Paragraph("Level", label_style), Paragraph(student_info["level"], value_style)],
        [Paragraph("Semester / Session", label_style),
         Paragraph(f"{student_info['semester']}  ·  {student_info['session']}", value_style),
         Paragraph("Study Centre", label_style), Paragraph(student_info["centre"], value_style)],
        [Paragraph("Faculty", label_style), Paragraph(student_info.get("faculty", ""), value_style),
         Paragraph("Batch", label_style), Paragraph(student_info.get("batch", ""), value_style)],
    ]
    info_table = Table(info_data, colWidths=[38*mm, 50*mm, 42*mm, 42*mm])
    info_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f0f4f8")),
        ("BOX", (0, 0), (-1, -1), 0.8, colors.HexColor("#1e3a5f")),
        ("INNERGRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#cbd5e0")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4), ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 3.5), ("BOTTOMPADDING", (0, 0), (-1, -1), 3.5),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 4.5 * mm))

    # Schedule
    sched_header = Table([[Paragraph("EXAMINATION SCHEDULE", section_title)]], colWidths=[usable_width])
    sched_header.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#1e3a5f")),
        ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(sched_header)
    story.append(Spacer(1, 1.5 * mm))

    col_w = [11*mm, 52*mm, 22*mm, 22*mm, 65*mm]
    header_row = [Paragraph(h, th_style) for h in ["S/N", "DATE", "TIME", "CODE", "COURSE TITLE"]]
    data = [header_row]
    for i, exam in enumerate(exams, 1):
        data.append([
            Paragraph(str(i), sn_style),
            Paragraph(exam["Date"], cell_style),
            Paragraph(exam["Time"], time_style),
            Paragraph(exam["Course Code"], code_style),
            Paragraph(exam["Course Title"], cell_style),
        ])

    exam_table = Table(data, colWidths=col_w, repeatRows=1)
    exam_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2c5282")),
        ("TOPPADDING", (0, 0), (-1, 0), 5), ("BOTTOMPADDING", (0, 0), (-1, 0), 5),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f7fafc")]),
        ("BOX", (0, 0), (-1, -1), 0.9, colors.HexColor("#1e3a5f")),
        ("INNERGRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#a0aec0")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 3), ("RIGHTPADDING", (0, 0), (-1, -1), 3),
        ("TOPPADDING", (0, 1), (-1, -1), 4), ("BOTTOMPADDING", (0, 1), (-1, -1), 4),
        ("BACKGROUND", (2, 1), (2, -1), colors.HexColor("#fff5f5")),
    ]))
    story.append(exam_table)
    story.append(Spacer(1, 4 * mm))

    # Notes
    notes = [
        Paragraph("IMPORTANT NOTES", note_header),
        Paragraph("• Arrive at the examination centre at least <b>30 minutes</b> before the scheduled time.", note_item),
        Paragraph("• Carry your NOUN Student ID Card, Examination Slip and a valid photo identification.", note_item),
        Paragraph("• Electronic devices (mobile phones, smart watches, etc.) are strictly prohibited in the hall.", note_item),
        Paragraph("• This is an E-Examination. Follow all instructions issued by the invigilators.", note_item),
        Paragraph("• Always verify your course codes on the official NOUN student portal before the exam day.", note_item),
    ]
    notes_inner = Table([[n] for n in notes], colWidths=[usable_width - 6*mm])
    notes_box = Table([[notes_inner]], colWidths=[usable_width])
    notes_box.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#fffff0")),
        ("BOX", (0, 0), (-1, -1), 0.9, colors.HexColor("#d69e2e")),
        ("LEFTPADDING", (0, 0), (-1, -1), 4), ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    story.append(notes_box)
    story.append(Spacer(1, 5 * mm))

    # Support
    story.append(ColoredLine(usable_width, thickness=1.2, color=colors.HexColor("#276749")))
    story.append(Spacer(1, 2 * mm))
    story.append(Paragraph("ACADEMIC SUPPORT SERVICES", support_title))
    story.append(Paragraph("WE WISH YOU THE BEST OF LUCK", support_wish))
    story.append(Paragraph("<b>MR FISH</b><br/>ACADEMIC SUPPORT PARTNER<br/>YOUR SUCCESS OUR PRIORITY", support_body))
    story.append(Paragraph("CALL / WHATSAPP: 08109213232", support_contact))
    story.append(Paragraph("Visit our office beside NOUN V.I Study Centre, Nigeria Air Force Base Camp.", support_addr))
    story.append(Spacer(1, 2.5 * mm))
    story.append(ColoredLine(usable_width, thickness=1.2, color=colors.HexColor("#276749")))
    story.append(Spacer(1, 2.5 * mm))

    story.append(Paragraph(
        "Generated from the Official 2026_2 E-Exam Final Timetable of the National Open University of Nigeria.<br/>"
        "This personalized schedule is provided for convenience only. Always confirm details on the official NOUN portal.",
        disclaimer,
    ))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()


# ----------------------- Matching Helper -----------------------
def resolve_course(code: str, preferred_batch: str, df: pd.DataFrame):
    """
    Resolve a course code to the correct row(s), respecting Batch A / Batch B
    for general courses (GST, NOU, NOUN-GST, etc.).
    """
    code = code.upper().strip()

    # Exact match first
    hits = df[df["Course Code Clean"] == code]
    if not hits.empty:
        return hits

    # If user typed base code (e.g. GST201), look for Batch variants
    batch_suffix = f"-{preferred_batch}"
    preferred = df[df["Course Code Clean"] == f"{code}{batch_suffix}"]
    if not preferred.empty:
        return preferred

    # Fallback: any code that starts with the given code
    hits = df[df["Course Code Clean"].str.startswith(code)]
    if not hits.empty:
        # Prefer the correct batch if both exist
        batch_hits = hits[hits["Course Code Clean"].str.endswith(batch_suffix)]
        if not batch_hits.empty:
            return batch_hits
        return hits

    return pd.DataFrame()  # empty


# ----------------------- UI -----------------------
st.markdown("""
<style>
    .main-header {font-size: 1.6rem; font-weight: 700; color: #1e3a5f; text-align: center;}
    .sub-header {font-size: 0.95rem; color: #4a5568; text-align: center; margin-bottom: 1.5rem;}
    .stDownloadButton button {background-color: #276749 !important; color: white !important;}
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="main-header">NOUN 2026_2 Personalized Timetable Generator</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Enter student details and registered courses to generate a clean exam schedule PDF</p>', unsafe_allow_html=True)

with st.form("student_form"):
    st.subheader("Student Details")
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("Full Name *", placeholder="e.g. PAUL Charity Alkali")
        matric = st.text_input("Matriculation Number *", placeholder="e.g. NOU251203395")
        programme = st.text_input("Programme *", placeholder="e.g. BA(Ed) English")
    with col2:
        level = st.selectbox("Level *", ["100 Level", "200 Level", "300 Level", "400 Level", "Postgraduate"])
        centre = st.text_input("Study Centre *", placeholder="e.g. Lagos Study Centre")
        semester = st.selectbox("Semester", ["First Semester", "Second Semester"], index=0)

    faculty = st.selectbox(
        "Faculty *",
        options=ALL_FACULTIES,
        help="This determines whether general courses (GST, NOU, etc.) use Batch A or Batch B"
    )

    # Show which batch will be used
    if faculty in BATCH_A_FACULTIES:
        preferred_batch = "A"
        st.info("**Batch A** will be used for general courses (GST / NOU)")
    else:
        preferred_batch = "B"
        st.info("**Batch B** will be used for general courses (GST / NOU)")

    st.subheader("Registered Courses")
    st.caption("Select all course codes the student registered for this exam (you can type to search)")
    selected_codes = st.multiselect(
        "Course Codes *",
        options=ALL_CODES,
        help="Start typing a course code to filter the list",
    )

    # Manual entry fallback
    manual_codes = st.text_input(
        "Or type course codes manually (comma separated)",
        placeholder="e.g. EDU231, ENG221, GST201",
        help="Useful if a code is missing from the list. You can type GST201 (without -A/-B) — the correct batch will be chosen automatically.",
    )

    submitted = st.form_submit_button("Generate Personalized Timetable", type="primary", use_container_width=True)

if submitted:
    if not name or not matric or not programme or not centre or not faculty:
        st.error("Please fill in all required student details (marked with *).")
    else:
        # Combine selected + manual
        codes = set(selected_codes)
        if manual_codes:
            for c in manual_codes.replace(" ", "").split(","):
                if c:
                    codes.add(c.upper().strip())

        if not codes:
            st.error("Please select or type at least one course code.")
        else:
            # Lookup exams using the correct batch
            matched = []
            not_found = []
            for code in codes:
                hits = resolve_course(code, preferred_batch, timetable_df)
                if hits.empty:
                    not_found.append(code)
                else:
                    for _, row in hits.iterrows():
                        matched.append({
                            "Date": row["Date"],
                            "Time": row["Time"],
                            "Course Code": row["Course Code"],
                            "Course Title": row["Course Title"],
                        })

            if not matched:
                st.error("None of the entered course codes were found in the official timetable.")
            else:
                # Sort by date roughly
                matched = sorted(matched, key=lambda x: (x["Date"], x["Time"]))

                student_info = {
                    "name": name.strip().upper(),
                    "matric": matric.strip().upper(),
                    "programme": programme.strip(),
                    "level": level,
                    "centre": centre.strip(),
                    "semester": semester,
                    "session": "2026_2",
                    "faculty": faculty,
                    "batch": f"Batch {preferred_batch}",
                }

                pdf_bytes = generate_pdf(student_info, matched)

                st.success(f"Found {len(matched)} exam slot(s) for {len(codes)} course code(s) using **Batch {preferred_batch}**.")
                if not_found:
                    st.warning(f"These codes were not found: {', '.join(not_found)}")

                # Preview table
                st.dataframe(
                    pd.DataFrame(matched)[["Date", "Time", "Course Code", "Course Title"]],
                    use_container_width=True,
                    hide_index=True,
                )

                filename = f"NOUN_Timetable_{matric.replace('/', '_')}.pdf"
                st.download_button(
                    label="⬇️ Download Personalized PDF Timetable",
                    data=pdf_bytes,
                    file_name=filename,
                    mime="application/pdf",
                    use_container_width=True,
                )

st.markdown("---")
st.caption("Data sourced from the Official 2026_2 E-Exam Final Timetable • National Open University of Nigeria")
st.caption("Academic Support: MR FISH • Call/WhatsApp 08109213232")
