import os
import sys
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_PDF = BASE_DIR / "Complete_Patent_Document.pdf"
SCREENSHOTS_DIR = BASE_DIR / "Project_Screenshots"
DIAGRAMS_DIR = BASE_DIR / "Technical_Diagrams"

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748B"))
        
        # Header (Pages 2+)
        if self._pageNumber > 1:
            self.drawString(54, 11 * 72 - 36, "Lovely Professional University — IPR Cell | PathMatch AI Complete Patent Specification")
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.5)
            self.line(54, 11 * 72 - 40, 8.5 * 72 - 54, 11 * 72 - 40)

        # Footer (All pages)
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.5)
        self.line(54, 45, 8.5 * 72 - 54, 45)
        
        page_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(8.5 * 72 - 54, 32, page_text)
        self.drawString(54, 32, "Confidential — Patent Application: To Be Assigned by the Indian Patent Office")
        self.restoreState()

def build_pdf():
    print("Initializing PDF Document Builder...")
    doc = SimpleDocTemplate(
        str(OUTPUT_PDF),
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()

    # Custom typography
    title_style = ParagraphStyle(
        "CoverTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=16,
        textColor=colors.HexColor("#0F172A"),
        alignment=1, # Center
        spaceAfter=6
    )

    h1_style = ParagraphStyle(
        "PatentH1",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=15,
        textColor=colors.HexColor("#1E3A8A"),
        spaceBefore=12,
        spaceAfter=6,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        "PatentH2",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=10,
        leading=13,
        textColor=colors.HexColor("#334155"),
        spaceBefore=8,
        spaceAfter=4,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        "PatentBody",
        parent=styles["Normal"],
        fontName="Times-Roman",
        fontSize=9.5,
        leading=13.5,
        textColor=colors.HexColor("#1E293B"),
        spaceAfter=5
    )

    caption_style = ParagraphStyle(
        "PatentCaption",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor("#475569"),
        alignment=1, # Center
        spaceBefore=4,
        spaceAfter=8
    )

    tbl_text = ParagraphStyle(
        "TblText",
        parent=styles["Normal"],
        fontName="Times-Roman",
        fontSize=8,
        leading=10.5,
        textColor=colors.HexColor("#1E293B")
    )

    tbl_hdr = ParagraphStyle(
        "TblHdr",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8.5,
        leading=11,
        textColor=colors.white,
        alignment=1
    )

    story = []

    # -------------------------------------------------------------
    # HEADER BANNER
    # -------------------------------------------------------------
    story.append(Paragraph("<b>LOVELY PROFESSIONAL UNIVERSITY</b><br/>DIVISION OF RESEARCH & INNOVATION (IPR CELL)", title_style))
    story.append(Spacer(1, 4))
    story.append(Paragraph("<b>ANNEXURE 3b — COMPLETE FILING<br/>INVENTION DISCLOSURE FORM (IDF) & FORM 2 COMPLETE SPECIFICATION</b><br/><font size=9 color='#64748B'><i>(THE PATENTS ACT, 1970 & THE PATENTS RULES, 2003)</i></font>", title_style))
    story.append(Spacer(1, 4))
    story.append(Paragraph("<font size=8.5 color='#475569'>Patent Application Number: <b>To Be Assigned by the Indian Patent Office</b> | IPC/CPC: G06Q 10/06, G06N 3/00, G06F 40/00</font>", caption_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#1E3A8A"), spaceBefore=4, spaceAfter=8))

    # =============================================================
    # PART I: INVENTION DISCLOSURE FORM (ANNEXURE 3b)
    # =============================================================
    story.append(Paragraph("PART I: INVENTION DISCLOSURE FORM (ANNEXURE 3b — COMPLETE FILING)", h1_style))
    story.append(Paragraph("<b>1. TITLE OF THE INVENTION:</b><br/>System and Method for Intelligent Pure-LLM Multi-Agent Occupational Role Recommendation, Skill-Gap Diagnostic, and Career Guidance Grounded in Standardized Occupational Taxonomy", body_style))
    story.append(Spacer(1, 4))

    story.append(Paragraph("<b>2. INTERNAL INVENTOR(S) / STUDENT(S): (All fields mandatory)</b>", h2_style))
    
    inv_matrix = [
        [Paragraph("<b>Particulars</b>", tbl_hdr), Paragraph("<b>Inventor 1 (Lead)</b>", tbl_hdr), Paragraph("<b>Inventor 2</b>", tbl_hdr), Paragraph("<b>Inventor 3</b>", tbl_hdr)],
        [Paragraph("<b>Full Name</b>", tbl_text), Paragraph("Akash Kopalli", tbl_text), Paragraph("Rohit Singh Danu", tbl_text), Paragraph("Komaldeep Kaur", tbl_text)],
        [Paragraph("<b>Mobile Number</b>", tbl_text), Paragraph("970148471", tbl_text), Paragraph("863 0487038", tbl_text), Paragraph("70153 33897", tbl_text)],
        [Paragraph("<b>Email (Personal)</b>", tbl_text), Paragraph("kopalliakash45@gmail.com", tbl_text), Paragraph("rohitsinghdanu1122@gmail.com", tbl_text), Paragraph("komaldeep0612@gmail.com", tbl_text)],
        [Paragraph("<b>UID / Reg. Number</b>", tbl_text), Paragraph("12306174", tbl_text), Paragraph("12326149", tbl_text), Paragraph("12318028", tbl_text)],
        [Paragraph("<b>Address of Affiliation</b>", tbl_text), Paragraph("Lovely Professional University, Phagwara, Punjab-144411, India", tbl_text), Paragraph("Lovely Professional University, Phagwara, Punjab-144411, India", tbl_text), Paragraph("Lovely Professional University, Phagwara, Punjab-144411, India", tbl_text)],
        [Paragraph("<b>Signature</b>", tbl_text), Paragraph("Affixed in Section 15", tbl_text), Paragraph("Affixed in Section 15", tbl_text), Paragraph("Affixed in Section 15", tbl_text)]
    ]
    t_inv = Table(inv_matrix, colWidths=[110, 130, 130, 134])
    t_inv.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1E3A8A")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F8FAFC")]),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_inv)
    story.append(Spacer(1, 6))

    story.append(Paragraph("<b>EXTERNAL INVENTOR(S):</b> Not Applicable (N/A). All named inventors are undergraduate scholars registered at Lovely Professional University, Punjab, India.", body_style))
    story.append(Spacer(1, 6))

    story.append(Paragraph("<b>3. DESCRIPTION OF THE INVENTION:</b>", h1_style))
    story.append(Paragraph("<b>A. PROBLEM ADDRESSED BY THE INVENTION:</b><br/>"
                           "The modern engineering graduate transition suffers from the 'Graduate Employability Paradox.' "
                           "Students describe competencies using high-level academic coursework names (e.g., 'Completed DBMS'), whereas employers demand "
                           "concrete toolchain evidence and architectural patterns (e.g., 'PostgreSQL index optimization'). "
                           "Traditional recruitment systems fail due to (1) keyword stuffing vulnerabilities where TF-IDF/cosine similarity penalizes alternative phrasing, "
                           "(2) uncalibrated generative AI chatbots that hallucinate 90%+ match scores on basic markup like HTML/CSS, and "
                           "(3) reliance on unverified commercial job postings filled with phantom vacancies.", body_style))

    story.append(Paragraph("<b>B. OBJECTIVES OF THE INVENTION:</b><br/>"
                           "1. To develop a pure Large Language Model (LLM) cognitive multi-agent reasoning architecture that evaluates career suitability strictly without traditional machine learning, vector distance metrics, or keyword overlap frequencies.<br/>"
                           "2. To ground all occupational evaluations into the authoritative U.S. Department of Labor O*NET 2018 SOC taxonomy comprising 72 standardized computing occupations across 10 technology domains.<br/>"
                           "3. To enforce an anti-hallucination six-dimension qualitative evaluation rubric, producing calibrated honest suitability scores (~46%-52% Foundational Fit for basic HTML/CSS declarations).<br/>"
                           "4. To automatically diagnose prerequisite skill deficits and synthesize actionable 30-60-90 day milestone learning roadmaps paired with an interactive conversational mentor.", body_style))

    story.append(Spacer(1, 6))
    story.append(Paragraph("<b>C. STATE OF THE ART / RESEARCH GAP / NOVELTY TABLE:</b>", h2_style))

    soa_matrix = [
        [Paragraph("<b>Sr.</b>", tbl_hdr), Paragraph("<b>Patent ID</b>", tbl_hdr), Paragraph("<b>Prior-Art Abstract</b>", tbl_hdr), Paragraph("<b>Identified Research Gap</b>", tbl_hdr), Paragraph("<b>Novelty of Invention</b>", tbl_hdr)],
        [Paragraph("1", tbl_text), Paragraph("<b>US20160379516A1</b><br/>(Google Patents)", tbl_text), Paragraph("Career Path Guidance Platform using statistical transition vectors to match job titles.", tbl_text), Paragraph("Lacks multi-agent qualitative reasoning and deep code project substantiation.", tbl_text), Paragraph("7-Agent pure LLM reasoning evaluating code depth across 6 calibrated dimensions.", tbl_text)],
        [Paragraph("2", tbl_text), Paragraph("<b>US20150127567A1</b><br/>(Google Patents)", tbl_text), Paragraph("Data mining text to infer competencies via heuristic NLP keyword extraction.", tbl_text), Paragraph("Vulnerable to keyword gaming; cannot evaluate architectural complexity.", tbl_text), Paragraph("Strict prompt injection guardrails; audits verified evidence vs unverified claims.", tbl_text)],
        [Paragraph("3", tbl_text), Paragraph("<b>US20090276231A1</b><br/>(Google Patents)", tbl_text), Paragraph("Job guidance and career planning system using static business rules.", tbl_text), Paragraph("Rigid heuristic rules fail on modern software engineering stacks.", tbl_text), Paragraph("Dynamic multi-turn AI career mentor with real-time O*NET SOC cross-linking.", tbl_text)],
        [Paragraph("4", tbl_text), Paragraph("<b>US8060451B2</b><br/>(Microsoft)", tbl_text), Paragraph("Skill gap analysis based on corporate metadata tag analytics.", tbl_text), Paragraph("Confined to internal enterprise tags; ignores academic-to-industry gap.", tbl_text), Paragraph("Synthesizes 30-60-90 day milestone plans specifically bridging coursework.", tbl_text)],
        [Paragraph("5", tbl_text), Paragraph("<b>US11120403B2</b><br/>(Google Patents)", tbl_text), Paragraph("Career analytics platform using predictive machine learning models.", tbl_text), Paragraph("Opaque black-box models lacking transparent explainability.", tbl_text), Paragraph("100% transparent qualitative reasoning justification for every assigned score.", tbl_text)]
    ]
    t_soa = Table(soa_matrix, colWidths=[24, 85, 130, 130, 135])
    t_soa.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1E3A8A")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F8FAFC")]),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_soa)
    story.append(Spacer(1, 6))

    story.append(Paragraph("<b>D. DETAILED TECHNICAL DESCRIPTION & RESULTS:</b><br/>"
                           "The invention operates as an intelligent multi-agent committee: Profile Understanding Agent parses and normalizes input; "
                           "Skill Intelligence Agent maps transferable competencies; Occupational Matching Agent reasons across 72 O*NET occupations using "
                           "a 6-dimension rubric; Skill-Gap Diagnostic Agent separates conceptual from tooling deficits; Strategic Learning Path Agent generates milestone plans; "
                           "and Career Guidance Assistant delivers real-time conversational mentoring.", body_style))

    story.append(Paragraph("<b>4. STATUTORY USE AND DISCLOSURE CHECKLIST:</b>", h2_style))
    ud_matrix = [
        [Paragraph("<b>Statutory Inquiry</b>", tbl_hdr), Paragraph("<b>Response</b>", tbl_hdr), Paragraph("<b>Particulars</b>", tbl_hdr)],
        [Paragraph("Described or shown invention/design to anyone or in any conference?", tbl_text), Paragraph("<b>NO [X]</b>", tbl_text), Paragraph("Internal confidential academic prototype.", tbl_text)],
        [Paragraph("Attempts to commercialize invention (approached companies)?", tbl_text), Paragraph("<b>NO [X]</b>", tbl_text), Paragraph("No commercial sales or licensing agreements executed.", tbl_text)],
        [Paragraph("Described in any printed publication or internet media?", tbl_text), Paragraph("<b>NO [X]</b>", tbl_text), Paragraph("Proprietary architecture has not been published in journals.", tbl_text)],
        [Paragraph("Collaboration with any other institute/organization?", tbl_text), Paragraph("<b>NO [X]</b>", tbl_text), Paragraph("Developed solely by LPU internal scholars.", tbl_text)],
        [Paragraph("Regulatory body or other approvals required?", tbl_text), Paragraph("<b>NO [X]</b>", tbl_text), Paragraph("Pure software cognitive system; no bio-medical approvals required.", tbl_text)]
    ]
    t_ud = Table(ud_matrix, colWidths=[200, 64, 240])
    t_ud.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1E3A8A")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F8FAFC")]),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(t_ud)
    story.append(Spacer(1, 6))

    story.append(Paragraph("<b>5. PUBLIC LINKS & DATES:</b> Project Code Repository: https://github.com/Akashkopalli/pathmatchAi (November 2026).<br/>"
                           "<b>6. MOU TERMS & CONDITIONS:</b> Conceived and developed exclusively within Lovely Professional University.<br/>"
                           "<b>7. COMMERCIALIZATION POTENTIAL:</b> High demand across university career centers, AICTE, Skill India, and EdTech platforms.<br/>"
                           "<b>8. TARGET COMPANIES:</b> LinkedIn, Handshake, Coursera, Unstop, TCS iON.<br/>"
                           "<b>9. BASIC PATENTS USED:</b> None. Built upon original prompting architectures and public domain O*NET database.<br/>"
                           "<b>10. FILING OPTIONS:</b> Complete Specification Filing (Form 2 under Indian Patents Act, 1970).<br/>"
                           "<b>11. KEYWORDS:</b> Multi-Agent Systems; Large Language Models; Occupational Recommendation; O*NET SOC; Skill-Gap Diagnostic; Pure LLM Reasoning.", body_style))

    # =============================================================
    # PART II: FORM 2 COMPLETE SPECIFICATION
    # =============================================================
    story.append(PageBreak())
    story.append(Paragraph("<b>FORM 2 — COMPLETE SPECIFICATION</b><br/><font size=9>THE PATENTS ACT, 1970 (39 OF 1970) & THE PATENTS RULES, 2003</font>", title_style))
    story.append(Spacer(1, 6))

    story.append(Paragraph("TITLE OF THE INVENTION", h1_style))
    story.append(Paragraph("<b>SYSTEM AND METHOD FOR INTELLIGENT PURE-LLM MULTI-AGENT OCCUPATIONAL ROLE RECOMMENDATION, SKILL-GAP DIAGNOSTIC, AND CAREER GUIDANCE GROUNDED IN STANDARDIZED OCCUPATIONAL TAXONOMY</b>", body_style))

    story.append(Paragraph("APPLICANTS & INVENTORS", h2_style))
    story.append(Paragraph("1. <b>Akash Kopalli</b>, Indian National, Reg. No. 12306174<br/>"
                           "2. <b>Rohit Singh Danu</b>, Indian National, Reg. No. 12326149<br/>"
                           "3. <b>Komaldeep Kaur</b>, Indian National, Reg. No. 12318028<br/>"
                           "All residing at: Lovely Professional University, Phagwara, Punjab-144411, India.<br/>"
                           "<i>Preamble: The following specification particularly describes the invention and the manner in which it is to be performed:</i>", body_style))

    story.append(Paragraph("ABSTRACT OF THE INVENTION", h1_style))
    story.append(Paragraph(
        "A system and computer-implemented method for intelligent occupational role recommendation, prerequisite skill-gap diagnostic, "
        "and structured milestone career guidance are disclosed. The system eliminates statistical vector distance metrics, TF-IDF keyword calculations, "
        "and Bag-of-Words similarity matching in favor of pure Large Language Model (LLM) cognitive semantic reasoning executed by an orchestrated "
        "multi-agent pipeline. A Profile Understanding Agent extracts and sanitizes declared skills, academic coursework, and project deliverables from "
        "natural language student input under prompt injection defense constraints. A Skill Intelligence Agent categorizes competencies into verified core, "
        "related, and transferable capabilities. An Occupational Matching Agent evaluates the candidate profile against 72 standardized occupations "
        "derived from the U.S. Department of Labor O*NET 2018 SOC taxonomy using a strict six-dimension qualitative evaluation rubric, preventing "
        "hallucination and capping entry-level markup declarations (e.g., HTML/CSS) to ~46%-52% Foundational Fit for Frontend engineering roles. "
        "A Skill-Gap Diagnostic Agent pinpoints missing prerequisite toolchains, while a Strategic Learning Path Agent synthesizes progressive "
        "30-60-90 day milestone roadmaps. An interactive conversational Career Guidance Assistant resolves follow-up queries with concise, non-hallucinated "
        "counseling directly cross-linked to official O*NET Online occupational databases.", body_style))

    story.append(Paragraph("TECHNICAL FIELD OF THE INVENTION", h1_style))
    story.append(Paragraph(
        "The present invention relates generally to artificial intelligence, natural language processing, and multi-agent cognitive systems. "
        "More particularly, the invention relates to a system, software architecture, and computer-implemented method for evaluating academic student competencies, "
        "auditing project evidence, generating calibrated occupational role recommendations grounded in standardized national labor taxonomies, "
        "and synthesizing customized career development roadmaps without reliance on legacy statistical keyword matching or unverified corporate job postings.", body_style))

    story.append(Paragraph("BACKGROUND OF THE INVENTION & PRIOR-ART LIMITATIONS", h1_style))
    story.append(Paragraph(
        "Transitioning from university degree curricula to professional technical employment represents a formidable challenge for computing "
        "and engineering scholars worldwide. Academic curricula are structured around theoretical discipline titles ('Discrete Mathematics', 'DBMS'), "
        "whereas employers seek verifiable proficiency in discrete tooling, framework paradigms, and production workflows. "
        "Conventional applicant tracking systems (ATS) exhibit three fatal deficiencies: (1) Lexical keyword matching rewards superficial keyword stuffing "
        "while penalizing students who describe identical concepts using alternative wording; (2) Unconstrained commercial LLMs suffer from sycophancy, "
        "awarding false-positive 90%+ match scores to novices who have merely declared HTML/CSS; and (3) Commercial job boards crawl volatile, "
        "unverified postings with phantom vacancies and exaggerated compensation claims.", body_style))

    story.append(Paragraph("OBJECTIVES & SUMMARY OF THE INVENTION", h1_style))
    story.append(Paragraph(
        "The present invention overcomes these barriers by providing an orchestrated 7-agent pure LLM architecture grounded in the official "
        "U.S. Department of Labor O*NET 2018 SOC taxonomy (72 technical occupations). The system enforces an anti-hallucination 6-dimension qualitative "
        "evaluation rubric (Direct Skill Overlap 35%, Foundational Knowledge 20%, Project Evidence 20%, Transferable Skills 10%, Skill Gap Feasibility 10%, "
        "Career Trajectory 5%), guarantees 0% occupational hallucination, pinpoints exact prerequisite deficits, and delivers structured 30-60-90 day milestone roadmaps.", body_style))

    # -------------------------------------------------------------
    # DRAWINGS AND DETAILED DESCRIPTION SECTION
    # -------------------------------------------------------------
    story.append(PageBreak())
    story.append(Paragraph("DETAILED DESCRIPTION OF DRAWINGS & SYSTEM ARCHITECTURE", h1_style))

    figs = [
        ("FIG. 1: Main Landing & System Gateway of Running PathMatch AI Application",
         SCREENSHOTS_DIR / "FIG_1_Homepage.png",
         "FIG. 1 illustrates the graphical user interface of the running PathMatch AI system gateway. "
         "The interface features a responsive navigation bar, instant dark/light theme toggle, and hero controls providing access to profile ingestion, "
         "recommendations, and the O*NET intelligence dashboard."),

        ("FIG. 2: Student Profile & Competency Ingestion Form with Structured & Natural Inputs",
         SCREENSHOTS_DIR / "FIG_2_Profile_Input.png",
         "FIG. 2 illustrates the student profile ingestion interface. The form captures academic credentials, coursework, verified skills, "
         "substantiated project descriptions (with architecture and technologies used), and an expansive natural language narrative area."),

        ("FIG. 3: Pure LLM Occupational Recommendation Cards with O*NET Codes & Suitability Scores",
         SCREENSHOTS_DIR / "FIG_3_Role_Recommendations.png",
         "FIG. 3 illustrates the recommendation results view generated by the Occupational Matching Agent. Each card displays the official O*NET title, "
         "8-digit SOC code, calibrated match percentage, domain badge, and direct one-click hyperlinks to the official U.S. DOL O*NET Online portal."),

        ("FIG. 4: O*NET Intelligence Dashboard & Knowledge Base Explorer with 72 Official Occupations",
         SCREENSHOTS_DIR / "FIG_4_ONET_Analytics_Dashboard.png",
         "FIG. 4 illustrates the O*NET intelligence dashboard and knowledge base explorer, displaying domain distribution metrics, "
         "required technologies, knowledge areas, and daily tasks across 72 official technical occupations in 10 computing domains."),

        ("FIG. 5: Detailed Three-Tier System Architecture & Multi-Agent Pure LLM Reasoning Engine",
         DIAGRAMS_DIR / "FIG_5_System_Architecture.png",
         "FIG. 5 is an architectural block diagram showing the three-tier framework of the invention: Tier 1 Client Presentation & Ingestion Layer, "
         "Tier 2 Multi-Agent Pure LLM Reasoning Pipeline (6 specialized reasoning agents + Defense Gate), and Tier 3 Authoritative O*NET Knowledge Base & SQLite Datastore."),

        ("FIG. 6: Sequential Multi-Agent Execution Workflow from Ingestion to Milestone Guidance",
         DIAGRAMS_DIR / "FIG_6_Multi_Agent_Workflow.png",
         "FIG. 6 is a flowchart showing the sequential execution workflow across Step 1 Ingestion & Sanitization, Step 2 Profile Extraction, "
         "Step 3 Skill Intelligence, Step 4 O*NET Retrieval, Step 5 Six-Dimension LLM Evaluation, Step 6 Deficit Diagnostic, Step 7 Roadmap Generation, and Step 8 Career Mentorship."),

        ("FIG. 7: Standardized Six-Dimension Qualitative Occupational Suitability Rubric",
         DIAGRAMS_DIR / "FIG_7_Six_Dimension_Evaluation_Rubric.png",
         "FIG. 7 illustrates the mathematical and qualitative formulation of the six-dimension rubric: Direct Skill Overlap (35%), "
         "Foundational Knowledge (20%), Project Evidence (20%), Transferable Skills (10%), Skill Gap Feasibility (10%), and Career Trajectory (5%)."),

        ("FIG. 8: O*NET 2018 SOC Taxonomy Hierarchical Knowledge Graph & Attribute Architecture",
         DIAGRAMS_DIR / "FIG_8_ONET_Taxonomy_Integration.png",
         "FIG. 8 illustrates the hierarchical knowledge structure indexing 72 official occupations across 10 technology domains, "
         "detailing core skills, tools & technologies, knowledge domains, and generalized work activities for every cataloged node.")
    ]

    for title, img_path, desc in figs:
        story.append(KeepTogether([
            Paragraph(f"<b>{title}</b>", h2_style),
            Paragraph(desc, body_style),
            Spacer(1, 2)
        ]))
        if img_path.exists():
            img = Image(str(img_path), width=500, height=270)
            story.append(KeepTogether([
                img,
                Paragraph(f"<i>{title}</i>", caption_style),
                Spacer(1, 6)
            ]))

    # -------------------------------------------------------------
    # CLAIMS SECTION
    # -------------------------------------------------------------
    story.append(PageBreak())
    story.append(Paragraph("CLAIMS", h1_style))
    story.append(Paragraph("<b>WE CLAIM:</b>", h2_style))

    claims_text = [
        "1. An intelligent computing system for automated occupational role recommendation and career guidance, comprising: "
        "a hardware processor and a non-transitory computer-readable memory storing instructions; "
        "an ingestion interface configured to receive natural language student profile data comprising academic coursework, declared technical competencies, and project narratives; "
        "an input sanitization module configured to intercept prompt injection attacks and bind student inputs within immutable delimiters; "
        "an authoritative occupational knowledge base storing standardized occupational profiles derived from the U.S. Department of Labor O*NET 2018 Standard Occupational Classification (SOC) taxonomy comprising a plurality of verified technical occupations; "
        "a multi-agent Large Language Model (LLM) cognitive reasoning engine communicatively coupled to said processor, wherein said engine is configured to execute semantic reasoning over said student profile data without reliance on statistical vector distance metrics, TF-IDF frequencies, or cosine similarity calculations, comprising: "
        "a Profile Understanding Agent configured to extract verified skills and substantiated project evidence; "
        "a Skill Intelligence Agent configured to classify skills into core proficiencies, related technologies, and transferable cognitive abilities; "
        "an Occupational Matching Agent configured to evaluate said profile against candidate occupations from said knowledge base across a calibrated six-dimension qualitative evaluation rubric to generate occupational match suitability scores; "
        "a Skill-Gap Diagnostic Agent configured to identify missing prerequisite technical competencies and estimate learning acquisition feasibility; "
        "a Strategic Learning Path Agent configured to synthesize progressive 30-60-90 day milestone learning roadmaps; and "
        "a presentation interface configured to render recommended occupational role cards with direct hyperlinks to official O*NET Online occupational records and provide an interactive conversational career mentorship assistant.",

        "2. The system as claimed in claim 1, wherein said six-dimension qualitative evaluation rubric comprises: "
        "a Direct Skill Overlap dimension weighted at approximately 35%; "
        "a Foundational Knowledge dimension evaluating academic coursework weighted at approximately 20%; "
        "a Project Evidence dimension evaluating tangible code implementation weighted at approximately 20%; "
        "a Transferable Skills dimension evaluating cognitive and algorithmic logic weighted at approximately 10%; "
        "a Skill Gap Feasibility dimension evaluating 30-to-90 day learning feasibility weighted at approximately 10%; and "
        "a Career Trajectory Alignment dimension evaluating candidate preferences weighted at approximately 5%.",

        "3. The system as claimed in claim 1, wherein said Occupational Matching Agent is constrained by prompt boundaries to prevent skill hallucination, such that an input containing only foundational markup languages (HTML and CSS) is capped to a calibrated suitability score between 46% and 52% Foundational Fit for Frontend Web Developer roles while explicitly flagging JavaScript and modern framework competencies as missing prerequisites.",

        "4. The system as claimed in claim 1, wherein said authoritative occupational knowledge base indexes exactly 72 technical occupations across 10 computing domains, and wherein every generated recommendation is strictly mapped to an official 8-digit O*NET SOC code.",

        "5. The system as claimed in claim 1, wherein said input sanitization module implements a multi-layer defense gate that intercepts instruction-overriding phrases, sanitizes special delimiter characters, and strictly prevents student input from escaping prompt context boundaries.",

        "6. The system as claimed in claim 1, wherein said Skill Intelligence Agent dynamically infers transferable competencies including structured problem decomposition, algorithmic thinking, database structuring, and technical documentation from declared programming languages.",

        "7. The system as claimed in claim 1, wherein said Skill-Gap Diagnostic Agent categorizes identified deficits into primary mandatory prerequisite technologies and secondary complementary frameworks, assigning an estimated effort rating for each deficit.",

        "8. The system as claimed in claim 1, wherein said Strategic Learning Path Agent structures milestone roadmaps into three chronological phases comprising: "
        "a 30-day Foundation Sprint focusing on core syntax and prerequisite toolchain acquisition; "
        "a 60-day Deep Dive & Implementation phase focusing on architectural framework design and integration; and "
        "a 90-day Portfolio & Production Deployment phase focusing on testing, continuous integration, and cloud deployment.",

        "9. The system as claimed in claim 1, wherein said presentation interface includes an interactive conversational Career Guidance Assistant configured to respond to natural language student inquiries with direct technical advice while remaining grounded in verified O*NET occupational standards without generating fictional salaries or unverified job vacancies.",

        "10. A computer-implemented method for automated occupational role recommendation and career guidance, comprising the steps of: "
        "receiving natural language student profile data comprising academic coursework, technical skills, and project narratives; "
        "sanitizing said student profile data via an input defense gate to intercept prompt injection attempts; "
        "extracting verified competencies and substantiated project evidence via a Profile Understanding LLM Agent; "
        "inferring skill relationships and transferable cognitive capabilities via a Skill Intelligence LLM Agent; "
        "retrieving a subset of candidate occupational profiles from an authoritative O*NET 2018 SOC database comprising 72 standardized technical occupations; "
        "evaluating said student profile data against said candidate occupational profiles via an Occupational Matching LLM Agent using a standardized six-dimension qualitative rubric to generate calibrated suitability percentages without computing statistical vector similarity; "
        "identifying prerequisite skill deficits and acquisition feasibility via a Skill-Gap Diagnostic LLM Agent; "
        "synthesizing a progressive 30-60-90 day milestone learning roadmap via a Strategic Learning Path LLM Agent; and "
        "rendering recommended role cards on a graphical user interface with direct one-click hyperlinks to official O*NET Online database records."
    ]

    for c in claims_text:
        story.append(Paragraph(c, body_style))
        story.append(Spacer(1, 3))

    # -------------------------------------------------------------
    # PHASE 7: INVENTOR DECLARATION & 3 LARGE SIGNATURE BOXES
    # -------------------------------------------------------------
    story.append(PageBreak())
    story.append(Paragraph("DECLARATION BY INVENTORS & DEDICATED SIGNATURE SECTION", h1_style))
    story.append(Paragraph(
        "We, the undersigned inventors, hereby declare that we are the true and first inventors of the invention entitled "
        "\"<b>SYSTEM AND METHOD FOR INTELLIGENT PURE-LLM MULTI-AGENT OCCUPATIONAL ROLE RECOMMENDATION, SKILL-GAP DIAGNOSTIC, "
        "AND CAREER GUIDANCE GROUNDED IN STANDARDIZED OCCUPATIONAL TAXONOMY</b>\". "
        "All signature areas below are deliberately formatted with substantial physical signing space to accommodate physical handwritten signatures.", body_style))
    story.append(Spacer(1, 8))

    sig_matrix = [
        [Paragraph("<b>INVENTOR 1 (LEAD)</b>", tbl_hdr), Paragraph("<b>INVENTOR 2</b>", tbl_hdr), Paragraph("<b>INVENTOR 3</b>", tbl_hdr)],
        [
            Paragraph("<br/><br/><br/><br/><br/><br/><br/><br/><i><font color='#94A3B8'>(Affix Handwritten Signature Here)</font></i><br/><br/>", tbl_text),
            Paragraph("<br/><br/><br/><br/><br/><br/><br/><br/><i><font color='#94A3B8'>(Affix Handwritten Signature Here)</font></i><br/><br/>", tbl_text),
            Paragraph("<br/><br/><br/><br/><br/><br/><br/><br/><i><font color='#94A3B8'>(Affix Handwritten Signature Here)</font></i><br/><br/>", tbl_text)
        ],
        [
            Paragraph("<b>Full Name:</b> Akash Kopalli<br/>"
                      "<b>UID / Reg. No.:</b> 12306174<br/>"
                      "<b>Mobile:</b> +91-970148471<br/>"
                      "<b>Email:</b> kopalliakash45@gmail.com<br/>"
                      "<b>Affiliation:</b> Lovely Professional University<br/>"
                      "<b>Date:</b> ____ / ____ / 2026<br/>"
                      "<b>Place:</b> Phagwara, Punjab, India", tbl_text),
            Paragraph("<b>Full Name:</b> Rohit Singh Danu<br/>"
                      "<b>UID / Reg. No.:</b> 12326149<br/>"
                      "<b>Mobile:</b> +91-863 0487038<br/>"
                      "<b>Email:</b> rohitsinghdanu1122@gmail.com<br/>"
                      "<b>Affiliation:</b> Lovely Professional University<br/>"
                      "<b>Date:</b> ____ / ____ / 2026<br/>"
                      "<b>Place:</b> Phagwara, Punjab, India", tbl_text),
            Paragraph("<b>Full Name:</b> Komaldeep Kaur<br/>"
                      "<b>UID / Reg. No.:</b> 12318028<br/>"
                      "<b>Mobile:</b> +91-70153 33897<br/>"
                      "<b>Email:</b> komaldeep0612@gmail.com<br/>"
                      "<b>Affiliation:</b> Lovely Professional University<br/>"
                      "<b>Date:</b> ____ / ____ / 2026<br/>"
                      "<b>Place:</b> Phagwara, Punjab, India", tbl_text)
        ]
    ]

    t_sig = Table(sig_matrix, colWidths=[168, 168, 168])
    t_sig.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1E3A8A")),
        ('GRID', (0,0), (-1,-1), 1.2, colors.HexColor("#1E3A8A")),
        ('BACKGROUND', (0,1), (-1,1), colors.white),
        ('BACKGROUND', (0,2), (-1,2), colors.HexColor("#F8FAFC")),
        ('ALIGN', (0,1), (-1,1), 'CENTER'),
        ('VALIGN', (0,1), (-1,1), 'MIDDLE'),
        ('TOPPADDING', (0,1), (-1,1), 16),
        ('BOTTOMPADDING', (0,1), (-1,1), 16),
        ('TOPPADDING', (0,2), (-1,2), 8),
        ('BOTTOMPADDING', (0,2), (-1,2), 8),
    ]))
    story.append(t_sig)
    story.append(Spacer(1, 12))

    story.append(Paragraph("RELEVANT PRIOR-ART PATENT CITATIONS (GOOGLE PATENTS)", h1_style))
    cits = [
        "1. <b>US Patent Application No. US20160379516A1</b> — 'Career Path Guidance Platform', Assignee/Inventors: CareerBuilder LLC / Google Patents Index.",
        "2. <b>US Patent Application No. US20150127567A1</b> — 'Data mining including processing natural language text to infer competencies', Google Patents Index.",
        "3. <b>US Patent Application No. US20090276231A1</b> — 'Method and System for Job and Career Guidance, Planning, Strategy and Workforce Development', Google Patents Index.",
        "4. <b>US Patent No. US8060451B2</b> — 'System and method for facilitating skill gap analysis and remediation based on tag analytics', Microsoft Technology Licensing LLC.",
        "5. <b>US Patent No. US11120403B2</b> — 'Career analytics platform', Google Patents Index."
    ]
    for cit in cits:
        story.append(Paragraph(cit, body_style))
        story.append(Spacer(1, 3))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Complete Patent Document PDF generated successfully at: {OUTPUT_PDF} ({OUTPUT_PDF.stat().st_size} bytes)")

if __name__ == "__main__":
    build_pdf()
