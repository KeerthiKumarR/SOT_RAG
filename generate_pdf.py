"""
Script to generate the exact 16-page Mirai_SoT_Policy_Handbook_2026.pdf
matching the official student policy handbook document.
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
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
            self.draw_header_footer(num_pages)
            super(NumberedCanvas, self).showPage()
        super(NumberedCanvas, self).save()

    def draw_header_footer(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 9)
        self.setFillColor(colors.HexColor("#333333"))
        
        # Header (pages 1 to 16)
        self.setFont("Helvetica-Bold", 14)
        self.setFillColor(colors.HexColor("#0f172a"))
        self.drawString(54, 750, "Mirai")
        self.setFont("Helvetica-Bold", 6)
        self.drawString(88, 745, "SCHOOL OF TECHNOLOGY")
        
        self.setFont("Helvetica-Bold", 9)
        self.drawRightString(558, 755, "studenthelpdesk@msot.org")
        self.drawRightString(558, 742, "www.msot.org")
        
        # Header line
        self.setStrokeColor(colors.HexColor("#0284c7"))
        self.setLineWidth(2)
        self.line(54, 732, 558, 732)
        
        # Footer
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748b"))
        footer_text = f"www.msot.org | Page {self._pageNumber} of {page_count}"
        self.drawCentredString(306, 36, footer_text)
        
        self.restoreState()


def build_handbook_pdf(output_filename="Mirai_SoT_Policy_Handbook_2026.pdf"):
    doc = SimpleDocTemplate(
        output_filename,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=80,
        bottomMargin=54
    )
    
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        alignment=1, # Center
        textColor=colors.HexColor('#0f172a'),
        spaceAfter=15
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=17,
        alignment=1,
        textColor=colors.HexColor('#0284c7'),
        spaceAfter=25
    )
    
    h1_style = ParagraphStyle(
        'Heading1_Custom',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=15,
        leading=19,
        alignment=1,
        textColor=colors.HexColor('#0f172a'),
        spaceAfter=15,
        spaceBefore=10
    )
    
    h2_style = ParagraphStyle(
        'Heading2_Custom',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=15,
        textColor=colors.HexColor('#0284c7'),
        spaceBefore=10,
        spaceAfter=6
    )
    
    body_style = ParagraphStyle(
        'Body_Custom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#1e293b'),
        spaceAfter=6
    )
    
    bullet_style = ParagraphStyle(
        'Bullet_Custom',
        parent=body_style,
        leftIndent=15,
        firstLineIndent=-10,
        spaceAfter=4
    )
    
    story = []

    # ================= PAGE 1: COVER =================
    story.append(Spacer(1, 150))
    story.append(Paragraph("<b>Mirai</b> <font size='8'>SCHOOL OF TECHNOLOGY</font>", title_style))
    story.append(Spacer(1, 30))
    story.append(Paragraph("MIRAI SCHOOL OF TECHNOLOGY", title_style))
    story.append(Paragraph("Student Policy Handbook 2026", subtitle_style))
    story.append(PageBreak())

    # ================= PAGE 2: CONTENTS =================
    story.append(Paragraph("CONTENTS", h1_style))
    story.append(Spacer(1, 10))
    story.append(Paragraph("<b>Policies Included</b>", h2_style))
    story.append(Paragraph("● &nbsp; Academic Evaluation Policy", bullet_style))
    story.append(Paragraph("● &nbsp; Attendance Policy", bullet_style))
    story.append(Paragraph("● &nbsp; Examination and Malpractice Policy", bullet_style))
    story.append(Paragraph("● &nbsp; No dues & Admit card policy", bullet_style))
    story.append(Paragraph("● &nbsp; Code of Conduct Policy", bullet_style))
    story.append(Paragraph("● &nbsp; Clubs and Events Policy", bullet_style))
    story.append(Paragraph("● &nbsp; Grievance Redressal Policy", bullet_style))
    story.append(Paragraph("● &nbsp; Medical Leave, Duty Leave & Attendance Deviation Policy", bullet_style))
    story.append(Spacer(1, 120))
    story.append(Paragraph("<b>Mirai School of Technology</b><br/>Administration", ParagraphStyle('AdminCenter', parent=body_style, alignment=1, fontName='Helvetica-Bold')))
    story.append(PageBreak())

    # ================= PAGE 3: ACADEMIC EVALUATION POLICY (Part 1) =================
    story.append(Paragraph("ACADEMIC EVALUATION POLICY", h1_style))
    story.append(Paragraph("Purpose", h2_style))
    story.append(Paragraph("Mirai School of Technology defines the evaluation framework, grading system, and academic progression rules for all programs offered at the institution through this policy.", body_style))
    
    story.append(Paragraph("Intent and Scope", h2_style))
    story.append(Paragraph("This policy establishes a rigorous, continuous, and practical assessment framework designed specifically for our B.Tech students. It ensures that foundational and advanced engineering modules—such as Design and Analysis of Algorithms (DAA) and Advance Web Development—are evaluated with a strong emphasis on hands-on coding, consistent practice, and project building. The standards outlined in this document are effective immediately and apply to the current academic year.", body_style))
    
    story.append(Paragraph("Evaluation Components & Weightage", h2_style))
    story.append(Paragraph("Based on the institutional standards, courses are divided into continuous evaluation, attendance, and final examinations. The specific weightages and criteria differ slightly based on the practical requirements of the subject.<br/>*The evaluation scheme is specified for each course as per the respective course faculty's instruction.", body_style))
    
    story.append(Paragraph("Standard Attendance Evaluation", h2_style))
    story.append(Paragraph("Attendance carries a 10% weightage across all courses. Marks are awarded based on the following tier system:", body_style))
    
    table_data_3 = [
        [Paragraph("<b>Attendance Percentage</b>", body_style), Paragraph("<b>Marks Awarded</b>", body_style)],
        ["90% and above", "10 marks"],
        ["80% – 89.99%", "8 marks"],
        ["75% – 79.99%", "6 marks"],
        ["60% – 74.99%", "4 marks"],
        ["Below 60%", "0 marks (Debarred from the Final Exam for that subject)"]
    ]
    t3 = Table(table_data_3, colWidths=[200, 300])
    t3.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0f2942')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('PADDING', (0, 0), (-1, -1), 5),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ]))
    story.append(t3)
    story.append(Spacer(1, 8))
    story.append(Paragraph("Grading & CGPA Calculation", h2_style))
    story.append(Paragraph("● &nbsp; Final grades for each subject are calculated by aggregating the weighted marks from continuous evaluation, attendance, biweekly tests/projects, and final exams into a cumulative score out of 100.", bullet_style))
    story.append(PageBreak())

    # ================= PAGE 4: ACADEMIC EVALUATION POLICY (Part 2) =================
    story.append(Paragraph("● &nbsp; The total composite percentage directly correlates to the student's final grade point and subsequent CGPA for the academic term.", bullet_style))
    story.append(Paragraph("● &nbsp; Students must secure a minimum aggregate score as defined by the academic council to pass the course.", bullet_style))
    story.append(Spacer(1, 10))
    story.append(Paragraph("Promotion / Backlog Rules", h2_style))
    story.append(Paragraph("Academic progression at Mirai School of Technology requires strict adherence to attendance and continuous evaluation standards.", body_style))
    story.append(Paragraph("● &nbsp; <b>Debarment Policy:</b> Students falling below the 75% attendance threshold in any subject will receive 0 marks for the attendance component and will be strictly debarred from appearing in the Final Exam for that subject.", bullet_style))
    story.append(Paragraph("● &nbsp; <b>Medical Exemptions:</b> A valid, verified medical certificate only provides a maximum of 15% weightage buffer in attendance criteria from debarment. It does not entirely waive the attendance requirement.", bullet_style))
    story.append(Paragraph("● &nbsp; <b>Continuous Evaluation Deficits:</b> Failure to complete mandatory course-specific continuous evaluation criteria — such as coding-practice targets or capstone/project submissions defined in the relevant course syllabus — will result in a total loss of the respective component's weightage, severely impacting the student's ability to clear the subject and potentially resulting in an academic backlog.", bullet_style))
    story.append(PageBreak())

    # ================= PAGE 5: ATTENDANCE POLICY =================
    story.append(Paragraph("ATTENDANCE POLICY", h1_style))
    story.append(Paragraph("Purpose", h2_style))
    story.append(Paragraph("This policy establishes the minimum attendance requirements for students and the conditions under which attendance relaxation will be granted.", body_style))
    story.append(Paragraph("Minimum Attendance Requirement", h2_style))
    story.append(Paragraph("● &nbsp; Every student shall maintain a minimum of <b>75% attendance in both Mirai Track & University Track</b> during the semester.", bullet_style))
    story.append(Paragraph("● &nbsp; Students with attendance below the prescribed limit will be debarred from appearing in examinations, unless attendance is condoned by the competent authority on valid grounds. Attendance shall be recorded for every scheduled lecture, laboratory, tutorial, and other mandatory academic activity.", bullet_style))
    story.append(Paragraph("● &nbsp; Students are solely responsible for monitoring and maintaining their attendance.", bullet_style))
    
    story.append(Paragraph("Attendance Regularisation", h2_style))
    story.append(Paragraph("Attendance regularisation will be considered only in the following cases:", body_style))
    story.append(Paragraph("● &nbsp; Approved Medical Leave supported by valid medical documents.", bullet_style))
    story.append(Paragraph("● &nbsp; Approved Leave for representing Mirai School of Technology (MSOT) in competitions or internships which require physical presence in industry or other academic institutes.", bullet_style))
    story.append(Paragraph("Attendance relaxation is not automatic and shall be granted solely at the discretion of the authority.", body_style))
    
    story.append(Paragraph("Process", h2_style))
    story.append(Paragraph("Students representing Mirai School of Technology in approved hackathons, competitions, conferences, workshops, research activities, industry visits, internships, or official events may receive attendance benefits subject to:", body_style))
    story.append(Paragraph("● &nbsp; Prior written approval along with NOC certificate is mandatory from the concerned faculties. (Please note that post facto approval will not be granted)", bullet_style))
    story.append(Paragraph("● &nbsp; Submission of supporting documents with faculties approval should be mailed to:<br/>&nbsp;&nbsp;&nbsp;&nbsp;<b>Experience ID:</b> experience@msot.org<br/>&nbsp;&nbsp;&nbsp;&nbsp;<b>Campus manager ID:</b> sundaram.mishra@msot.org", bullet_style))
    
    story.append(Paragraph("Unauthorized Absence", h2_style))
    story.append(Paragraph("● &nbsp; Absence without prior approval or valid justification shall be treated as unauthorized and marked absent.", bullet_style))
    story.append(Paragraph("● &nbsp; Proxy attendance, attendance fraud, or tampering with attendance records is strictly prohibited and may result in disciplinary action.", bullet_style))
    story.append(PageBreak())

    # ================= PAGE 6: EXAMINATION AND MALPRACTICE POLICY (Part 1) =================
    story.append(Paragraph("EXAMINATION AND MALPRACTICE POLICY", h1_style))
    story.append(Paragraph("Purpose", h2_style))
    story.append(Paragraph("This policy ensures fairness, transparency, and integrity in the conduct of all examinations - across internal assessments, biweekly tests, lab practicals, and end-semester finals- whether the exam happens on campus, or online.", body_style))
    
    story.append(Paragraph("Conduct of Examinations", h2_style))
    story.append(Paragraph("• &nbsp; Students must carry a valid Mirai School of Technology ID card (or admit card, where issued) to every examination and produce it on request.", bullet_style))
    story.append(Paragraph("• &nbsp; Students must be seated at least 10 minutes before the scheduled start time; entry is not permitted after 20 minutes from the start of the examination, and no student may leave the examination hall in the first 30 minutes or the final 10 minutes of the session.", bullet_style))
    story.append(Paragraph("• &nbsp; Only items explicitly permitted for that examination (e.g., approved calculators, blank rough sheets stamped by the invigilator) may be kept at the desk. All bags, notes, and electronic devices- including smartwatches and phones- must be deposited at the front of the room before the exam begins.", bullet_style))
    story.append(Paragraph("• &nbsp; Invigilators are authorized to inspect any item at a student's desk, reseat students, and record observations relevant to the conduct of the examination.", bullet_style))
    
    story.append(Paragraph("Unfair Means & Penalties", h2_style))
    story.append(Paragraph('"Unfair Means" (UFM) covers a range of behaviour, including — but not limited to:', body_style))
    story.append(Paragraph("• &nbsp; Possessing or consulting unauthorized material (written, printed, or electronic) during an examination.", bullet_style))
    story.append(Paragraph("• &nbsp; Unethical and unauthorised use of AI tools during the examination.", bullet_style))
    story.append(Paragraph("• &nbsp; Copying from, or allowing another student to copy from, one's own work.", bullet_style))
    story.append(Paragraph("• &nbsp; Impersonation, or facilitating impersonation, of a candidate.", bullet_style))
    story.append(Paragraph("• &nbsp; Communicating with another candidate or outside party during the examination through any means.", bullet_style))
    story.append(Paragraph("• &nbsp; Submitting work substantially produced by another person or by an unauthorized AI tool where such use is not permitted for that assessment.", bullet_style))
    story.append(Paragraph("• &nbsp; Tampering with answer scripts, attendance sheets, or examination records.", bullet_style))
    story.append(Paragraph("• &nbsp; Any other conduct that compromises the fairness or integrity of the examination process.", bullet_style))
    story.append(Paragraph("Cases of suspected unfair means will be reported by the invigilator on a standard incident form, countersigned by the student where possible, and referred to the Examination Committee. Penalties are assessed by severity and are proportionate:", body_style))
    story.append(PageBreak())

    # ================= PAGE 7: EXAMINATION POLICY (Part 2) =================
    story.append(Paragraph("<b>Strict Actions will be taken :</b>", h2_style))
    table_data_7 = [
        [Paragraph("Cancellation of that paper's result; the student may be required to reappear, subject to Examination Committee review.", body_style)],
        [Paragraph("Cancellation of results for the examination cycle, suspension from the institution for a defined period, and referral to the partner institution / Disciplinary Committee.", body_style)],
        [Paragraph("Withdrawal of the scholarship awarded to the student.", body_style)]
    ]
    t7 = Table(table_data_7, colWidths=[500])
    t7.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('PADDING', (0, 0), (-1, -1), 6),
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8fafc'))
    ]))
    story.append(t7)
    story.append(Spacer(1, 6))
    story.append(Paragraph("• &nbsp; Repeat offences are treated as an aggravating factor and may attract escalated penalties, including expulsion in extreme or repeat cases.", bullet_style))
    
    story.append(Paragraph("Revaluation:", h2_style))
    story.append(Paragraph("• &nbsp; Students may apply for revaluation or re-checking of an answer script within the first seven (7) working days of result declaration.", bullet_style))
    story.append(Paragraph("• &nbsp; Revaluation covers checking for totalling errors, unevaluated answers, and adherence to the marking scheme; it does not permit a general re-argument of awarded marks for a fully evaluated answer.", bullet_style))
    story.append(Paragraph("• &nbsp; Revaluation results will ordinarily be communicated within fifteen (15) working days of application.", bullet_style))
    story.append(PageBreak())

    # ================= PAGE 8: NO DUES & ADMIT CARD POLICY =================
    story.append(Paragraph("NO DUES & ADMIT CARD POLICY", h1_style))
    story.append(Paragraph("Purpose", h2_style))
    story.append(Paragraph("This policy establishes the requirement for students to clear all outstanding dues and obtain a No Dues Certificate before the issuance of the examination admit card.", body_style))
    
    story.append(Paragraph("Late Fee Policy", h2_style))
    story.append(Paragraph("A late fee of <b>₹100 per day</b> will be applicable to students who fail to clear their outstanding dues within the stipulated fee payment timeline. The late fee will be calculated on a per-day basis until all outstanding dues, including the applicable late fee, are cleared. Students are advised to complete their fee payment within the stipulated timeline to avoid additional charges", body_style))
    
    story.append(Paragraph("Eligibility for Admit Card", h2_style))
    story.append(Paragraph("Every student must clear all academic, administrative, library, transport, and any other outstanding dues before the scheduled examination.", body_style))
    story.append(Paragraph("The examination admit card shall be issued only after the student has obtained a <b>No Dues Certificate</b> from the institute.", body_style))
    
    story.append(Paragraph("No Dues Certificate", h2_style))
    story.append(Paragraph("The No Dues Certificate confirms that the student has fulfilled all financial and administrative obligations to the institution.", body_style))
    
    story.append(Paragraph("Process", h2_style))
    story.append(Paragraph("Students shall initiate the No Dues process within the timeline communicated by the institution before the commencement of examinations.. The examination admit card will be issued upon successful completion of all outstanding dues and verification of the No Dues Certificate.", body_style))
    
    story.append(Paragraph("Exceptional Cases", h2_style))
    story.append(Paragraph("Any request for relaxation due to exceptional circumstances shall be considered only upon written application and shall be subject to the approval of the competent authority. Grant of relaxation, if any, shall be purely at the discretion of the institution and shall not constitute a precedent for future cases.", body_style))
    story.append(PageBreak())

    # ================= PAGE 9: CODE OF CONDUCT POLICY =================
    story.append(Paragraph("CODE OF CONDUCT POLICY", h1_style))
    story.append(Paragraph("Purpose", h2_style))
    story.append(Paragraph("This policy defines the standards of behavior expected of every Mirai School of Technology student and staff member. It applies in addition to the rules of the partner universities where students are enrolled; where both apply, the stricter standard prevails.", body_style))
    
    story.append(Paragraph("General Code of Conduct", h2_style))
    story.append(Paragraph("1. Conduct yourself with honesty, respect, and professionalism in classrooms, hostels, online platforms, and at all Mirai activities including hackathons, industry visits, and internships.", bullet_style))
    story.append(Paragraph("2. Students represent Mirai in every interaction and are expected to uphold its reputation, including on social media and official communication channels.", bullet_style))
    story.append(Paragraph("3. Carry your ID on campus and comply with reasonable instructions of faculty, administration, and partner-campus authorities.", bullet_style))
    story.append(Paragraph("4. The standard day-to-day dress code is <b>Smart Casual</b>.", bullet_style))
    story.append(Paragraph("5. Clothing should be decent, presentable, and suitable for a professional office environment.", bullet_style))
    story.append(Paragraph("6. Ripped or distressed clothing, excessively revealing attire, flip-flops, gym wear, and clothing with offensive slogans or graphics are not permitted.", bullet_style))
    story.append(Paragraph("7. Students attending <b>hackathons, external competitions, interviews and other student events are required to wear strictly formal attire (Indian or Western formals)</b>.", bullet_style))
    story.append(Paragraph("8. Personal grooming and hygiene are expected to be maintained at all times.", bullet_style))
    
    story.append(Paragraph("Prohibited Activities", h2_style))
    story.append(Paragraph("1. <b>Possession or consumption of alcohol, tobacco, or prohibited substances</b> on campus or at any Mirai activity.", bullet_style))
    story.append(Paragraph("2. Impersonation, forgery, or misuse of the Mirai name, logo, or student identity.", bullet_style))
    story.append(Paragraph("3. Unauthorized commercial activity, gambling, or any unlawful act on campus or at Mirai events.", bullet_style))
    story.append(Paragraph("4. Any conduct, online or offline, that brings disrepute to Mirai or its partner institutions.", bullet_style))
    
    story.append(Paragraph("Disciplinary Committee & Process", h2_style))
    story.append(Paragraph("1. A Disciplinary Committee constituted by Mirai administration shall examine reported violations, giving the concerned individual a fair opportunity to be heard.", bullet_style))
    story.append(Paragraph("2. Actions will include warning, suspension from Mirai activities, withholding of certifications, or referral to the partner institution in proportion to the misconduct.", bullet_style))
    story.append(PageBreak())

    # ================= PAGE 10: CLUBS AND EVENTS POLICY (Part 1) =================
    story.append(Paragraph("CLUBS AND EVENTS POLICY", h1_style))
    story.append(Paragraph("Purpose", h2_style))
    story.append(Paragraph("Mirai School of Technology encourages students to form clubs and organize events, hackathons, and competitions that build practical skills and represent the institution. As a new-age school of technology, our goal is to foster a dynamic campus ecosystem that champions innovation, leadership, and holistic student development. This policy outlines the official framework for the formation, operation, and governance of all student-led organizations. It establishes a clear operational bridge between students, faculty, and management, ensuring that all club activities, events, and budgetary requests are executed with professionalism, accountability, and alignment with the institution's core values.", body_style))
    
    story.append(Paragraph("Club Formation & Recognition", h2_style))
    story.append(Paragraph("<b>1. Existing Recognized Clubs:</b> Mirai School of Technology currently recognizes and supports four foundational student clubs:", body_style))
    story.append(Paragraph("● &nbsp; <b>Coding & Tech Club:</b> Focused on software development, algorithmic programming, and hackathons. To accommodate specialized technical domains, this club may establish distinct subsidiary societies under its umbrella, such as a <b>Cybersecurity Society</b>, or a <b>Machine Learning and Artificial Intelligence (ML & AI) Society</b>.", bullet_style))
    story.append(Paragraph("● &nbsp; <b>Entrepreneurship Club:</b> Dedicated to startups, innovation, and business acumen.", bullet_style))
    story.append(Paragraph("● &nbsp; <b>Sports Club:</b> Responsible for athletic events, intramurals, and inter-college sports competitions.", bullet_style))
    story.append(Paragraph("● &nbsp; <b>Cultural Club:</b> Centered on the arts, music, dance, and cultural festivals.", bullet_style))
    
    story.append(Paragraph("<b>2. Proposing New Clubs</b>", body_style))
    story.append(Paragraph("● &nbsp; <b>Student Support Requirement:</b> Students interested in establishing a new student organization must demonstrate significant interest from the student body. A new club can be officially proposed if <b>at least 40% of the total batch students are in favor of its creation</b>.", bullet_style))
    story.append(Paragraph("● &nbsp; <b>Submission Process:</b> A formal proposal detailing the club's mission, proposed activities, structural plan, and a verifiable list of supporting student signatures (meeting the 40% threshold) <b>must be submitted to the designated Faculty Coordinator for initial review before being passed to Management for final recognition</b>.", bullet_style))
    
    story.append(Paragraph("<b>3. Membership and Induction:</b> Selection Process: Student members will be inducted and appointed directly by the respective club's leadership based on a transparent process of skill evaluations, assignments, and interviews.", body_style))
    story.append(Paragraph("<b>4. Leadership and Elections:</b> Core Office Bearers: Each club will be led by three primary office bearers: <b>President, Vice President, and Treasurer</b>. Contested and filled through annual club elections.", body_style))
    story.append(PageBreak())

    # ================= PAGE 11: CLUBS AND EVENTS POLICY (Part 2) =================
    story.append(Paragraph("Event Approval Workflow", h1_style))
    story.append(Paragraph("To ensure quality and feasibility, all events, competitions, and hackathons must follow a structured four-step approval workflow:", body_style))
    story.append(Paragraph("1. <b>Proposal & Budget Creation:</b> The club's office bearers (led by the President and Treasurer) must draft a comprehensive event proposal and a detailed, itemized budget.", bullet_style))
    story.append(Paragraph("2. <b>Submission to Faculty Coordinator:</b> The finalized draft is officially submitted to the designated Faculty Coordinator for the respective club.", bullet_style))
    story.append(Paragraph("3. <b>Revision & Faculty Review:</b> The Faculty Coordinator reviews the proposal for institutional alignment, feasibility, and safety. The coordinator will work with the students to revise and refine the plan and budget as necessary.", bullet_style))
    story.append(Paragraph("4. <b>Management Sanction:</b> Once the Faculty Coordinator is satisfied and grants preliminary approval, the Faculty Coordinator (not the students) will forward the final proposal and budget to the Management for ultimate approval and fund disbursement.", bullet_style))
    
    story.append(Paragraph("Budget & Conduct Guidelines", h2_style))
    story.append(Paragraph("<b>1. Faculty as the Point of Contact (POC):</b> The Faculty Coordinator serves as the official liaison between the student body and the college Management. <b>Students are not to bypass the faculty to approach Management directly regarding club operations or finances.</b>", body_style))
    story.append(Paragraph("<b>2. Financial Protocols:</b>", body_style))
    story.append(Paragraph("● &nbsp; <b>Faculty-First Approval:</b> Any budget proposed by the students must be strictly reviewed and approved by the Faculty Coordinator first.", bullet_style))
    story.append(Paragraph("● &nbsp; <b>Management Conveyance:</b> Only the Faculty Coordinator is authorized to convey the approved budget to Management for final financial clearance.", bullet_style))
    story.append(Paragraph("● &nbsp; <b>Accountability:</b> The club Treasurer is responsible for maintaining transparent records of all expenditures, which are subject to audit by the Faculty Coordinator post-event.", bullet_style))
    story.append(Paragraph("<b>3. General Conduct:</b> All club activities must reflect the innovative and professional spirit of Mirai School of Technology in an inclusive, safe and respectful environment.", body_style))
    story.append(PageBreak())

    # ================= PAGE 12: GRIEVANCE REDRESSAL POLICY =================
    story.append(Paragraph("GRIEVANCE REDRESSAL POLICY", h1_style))
    story.append(Paragraph("Purpose", h2_style))
    story.append(Paragraph("This policy provides a fair, transparent, confidential, and timely mechanism for students and staff to raise and resolve grievances related to academic, administrative, workplace, or campus matters. Mirai School of Technology is committed to addressing all grievances impartially and without retaliation.", body_style))
    
    story.append(Paragraph("Grievance Redressal Committee", h2_style))
    story.append(Paragraph("A Grievance Redressal Committee (GRC) shall be constituted by the administration to receive, review, and resolve grievances.", body_style))
    story.append(Paragraph("● &nbsp; Ensure fair and unbiased review of all complaints.<br/>● &nbsp; Maintain confidentiality throughout the process.<br/>● &nbsp; Recommend appropriate corrective or disciplinary action, where required.<br/>● &nbsp; Ensure compliance with institutional policies.", bullet_style))
    
    story.append(Paragraph("Filing & Escalation Process", h2_style))
    story.append(Paragraph("● &nbsp; Grievances may be submitted through the student help desk : <b>studenthelpdesk@msot.org</b>, keeping campus manager's email address in cc.", bullet_style))
    story.append(Paragraph("● &nbsp; An acknowledgment will be shared within <b>7 working days</b>.", bullet_style))
    story.append(Paragraph("● &nbsp; The Committee shall review the grievance and communicate its decision after due examination.", bullet_style))
    story.append(Paragraph("● &nbsp; If the complainant is dissatisfied, the matter may be escalated to the <b>Head of Institution</b> for final review.", bullet_style))
    
    story.append(Paragraph("Resolution Timelines & Records", h2_style))
    story.append(Paragraph("● &nbsp; Every effort shall be made to resolve grievances within <b>15 working days</b>.", bullet_style))
    story.append(Paragraph("● &nbsp; All grievances, actions taken, and decisions shall be documented and maintained confidentially by the administration.", bullet_style))
    story.append(Paragraph("● &nbsp; The institution may periodically review grievance records to improve policies and processes.", bullet_style))
    story.append(PageBreak())

    # ================= PAGE 13: MEDICAL LEAVE, DUTY LEAVE POLICY (Part 1) =================
    story.append(Paragraph("MIRAI SCHOOL OF TECHNOLOGY", title_style))
    story.append(Paragraph("MEDICAL LEAVE, DUTY LEAVE & ATTENDANCE DEVIATION POLICY", subtitle_style))
    story.append(Paragraph("<i>Applicable to all students across HI-Tech, Ratnam and JUJ campuses</i>", body_style))
    story.append(Spacer(1, 4))
    story.append(Paragraph("1. Purpose", h2_style))
    story.append(Paragraph("● &nbsp; This policy sets out the process by which students may request Medical Leave (for illness, injury or treatment) or Duty Leave for participation in events, competitions and other official activities. It also defines the process for rectifying any deviation in attendance records that is not covered by a Medical or Duty Leave request.<br/>● &nbsp; It defines the documents required, the timelines within which requests and rectifications must be raised, the levels of escalation available to students, and the consequences of non-compliance.", bullet_style))
    
    story.append(Paragraph("2. Definitions", h2_style))
    story.append(Paragraph("● &nbsp; <b>Medical Leave</b> — an absence from classes due to illness, injury or medical treatment, supported by valid medical documents.<br/>● &nbsp; <b>Duty Leave (DL)</b> — an absence from classes for the purpose of participating in an event, competition, workshop or other official activity on behalf of the college.<br/>● &nbsp; <b>Sessions Missed</b> — the total number of scheduled classes, labs and tutorials missed during the leave period, computed as per the timetable.<br/>● &nbsp; <b>Attendance Deviation</b> — any discrepancy between what a student believes their attendance should be and what is recorded on the system.", bullet_style))
    
    story.append(Paragraph("3. Documents Required (for Medical / DL requests)", h2_style))
    table_data_13 = [
        [Paragraph("<b>Type of Leave</b>", body_style), Paragraph("<b>Documents Required</b>", body_style)],
        [Paragraph("<b>Medical Leave</b>", body_style), Paragraph("● Medical certificate issued by a registered medical practitioner<br/>● Doctor's prescription related to the illness / injury<br/>● Discharge summary, in case of hospitalisation<br/>● Any other supporting document (test reports, referral notes, etc.)", body_style)],
        [Paragraph("<b>Duty Leave (DL) for Event / Competition</b>", body_style), Paragraph("● Official invitation / registration letter for the event<br/>● Event schedule or agenda, mentioning your dates of participation<br/>● Participation certificate (to be submitted after the event)<br/>● Any other supporting document confirming your attendance", body_style)]
    ]
    t13 = Table(table_data_13, colWidths=[150, 350])
    t13.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0f2942')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('PADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(t13)
    story.append(PageBreak())

    # ================= PAGE 14: MEDICAL LEAVE, DUTY LEAVE POLICY (Part 2) =================
    story.append(Paragraph("4. 7-Day Submission Rule (for Medical / DL requests)", h2_style))
    story.append(Paragraph("● &nbsp; <b>All supporting documents — for both Medical Leave and Duty Leave — must be submitted within 7 days of the event or medical situation. Requests submitted after 7 days will not be accepted.</b>", bullet_style))
    story.append(Paragraph("● &nbsp; <b>For Medical Leave:</b> the 7-day period is counted from the last day of the illness / treatment, or from the date of consultation for short-term issues.", bullet_style))
    story.append(Paragraph("● &nbsp; <b>For Duty Leave:</b> the 7-day period is counted from the last day of the event / competition.", bullet_style))
    story.append(Paragraph("● &nbsp; Requests submitted after 7 days will be treated as regular absence — no relaxation will be granted, even if the medical or event was genuine.", bullet_style))
    story.append(Paragraph("● &nbsp; Advance intimation (before the leave) is strongly encouraged, but does not replace the requirement to submit documents within 7 days after the event / illness.", bullet_style))
    
    story.append(Paragraph("5. Consequences of Non-Compliance", h2_style))
    story.append(Paragraph("● &nbsp; If documents are not submitted within the 7-day window, the absence will be marked as a regular absence and will count against your attendance for the respective subjects.<br/>● &nbsp; Students falling below the required 75% attendance in any subject will be dealt with as per the standard attendance and debarment policy.<br/>● &nbsp; The medical leverage cap of up to 15% (where applicable per campus policy) is applied only to verified medical cases where documents have been submitted within the 7-day window.", bullet_style))
    
    story.append(Paragraph("6. How to Submit", h2_style))
    story.append(Paragraph("● &nbsp; Submit the documents through mail to your respective <b>Campus Manager</b> (details in Section 8 below).<br/>● &nbsp; Ensure documents are signed and dated by the issuing authority (doctor, event organiser, etc.).<br/>● &nbsp; Retain a copy of the submitted documents and a note of the date of submission for your own records.<br/>● &nbsp; Where a digital submission channel is enabled at your campus, follow the instructions shared by your Campus Manager.", bullet_style))
    
    story.append(Paragraph("7. Verification & Approval", h2_style))
    story.append(Paragraph("● &nbsp; The Campus Manager will verify the documents against the dates of your absence. Once verified, your request will be entered into the Medical & DL records for your campus, and the approval will be communicated to you.", bullet_style))
    story.append(Paragraph("● &nbsp; If the documents are found to be incomplete, incorrect or forged, the request will be rejected and, in case of forgery, further disciplinary action may follow.", bullet_style))
    
    story.append(Paragraph("8. Point of Contact & Escalation (Medical / DL)", h2_style))
    story.append(Paragraph("● &nbsp; For any query, clarification or to submit your documents for Medical or Duty Leave, please connect with the Campus Manager for your campus:", bullet_style))
    story.append(PageBreak())

    # ================= PAGE 15: MEDICAL LEAVE, DUTY LEAVE POLICY (Part 3) =================
    table_data_15_campuses = [
        [Paragraph("<b>Campus</b>", body_style), Paragraph("<b>Campus Manager (Primary Contact)</b>", body_style), Paragraph("<b>How to Reach</b>", body_style)],
        ["HI-Tech", "Sundaram Sir", "In person at the CM office / campus email"],
        ["Ratnam", "Yashaswini Ma’am", "In person at the CM office / campus email"],
        ["JUJ (Jagannath University)", "Dolly Ma’am", "In person at the CM office / campus email"]
    ]
    t15_c = Table(table_data_15_campuses, colWidths=[140, 180, 180])
    t15_c.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0f2942')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('PADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(t15_c)
    story.append(Spacer(1, 10))
    
    story.append(Paragraph("Escalation ladder for Medical / DL matters", h2_style))
    story.append(Paragraph("● &nbsp; If your Medical or DL request is not resolved at the CM level, or if you have any concern regarding the decision taken, you may escalate as per the following ladder. Please attempt each level in order and allow reasonable time before moving to the next.", body_style))
    
    table_data_15_ladder = [
        [Paragraph("<b>Level</b>", body_style), Paragraph("<b>Whom to Approach</b>", body_style), Paragraph("<b>When to Escalate</b>", body_style)],
        ["L1", "Campus Manager (CM) — Sundaram Sir (HI-Tech) / Yashaswini Ma’am (Ratnam) / Dolly Ma’am (JUJ)", "First point of contact for all Medical / DL requests, questions or clarifications."],
        ["L2", "Dr. Abhilash Karakoti (abhilash.karakoti@msot.org)", "If the matter is not resolved at the CM level, or if the concern is regarding the CM’s decision."],
        ["L3", "Mr. Arpit Sarda (arpit@msot.org)", "For final escalation, if the matter remains unresolved even after L2."]
    ]
    t15_l = Table(table_data_15_ladder, colWidths=[50, 220, 230])
    t15_l.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0f2942')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('PADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(t15_l)
    story.append(Spacer(1, 10))
    
    story.append(Paragraph("9. Attendance Deviation (Other than Medical / DL)", h2_style))
    story.append(Paragraph("● &nbsp; For any deviation in attendance which is not covered by a Medical or Duty Leave request — for example, a class you actually attended but which has been marked absent, or any other mistake in the recorded attendance — the following process applies:", body_style))
    story.append(Paragraph("● &nbsp; The student must raise the discrepancy and get it rectified within <b>7 days</b> of the date on which the deviation was noticed / recorded. Requests raised after 7 days will not be entertained.", bullet_style))
    story.append(Paragraph("● &nbsp; The student should first approach the respective subject faculty of the class in question and request a correction of the record.", bullet_style))
    story.append(Paragraph("● &nbsp; If the subject faculty is unable to rectify the discrepancy, the student should escalate the matter as per the escalation ladder below. Kindly do not raise the same matter with multiple people simultaneously — please follow the ladder in order.", bullet_style))
    story.append(PageBreak())

    # ================= PAGE 16: ATTENDANCE DEVIATION LADDER & GUIDELINES =================
    story.append(Paragraph("Escalation ladder for Attendance Deviation", h2_style))
    table_data_16_ladder = [
        [Paragraph("<b>Level</b>", body_style), Paragraph("<b>Whom to Approach</b>", body_style), Paragraph("<b>When to Escalate</b>", body_style)],
        ["L1", "Respective Subject Faculty", "First step — raise the attendance discrepancy directly with the faculty of the concerned subject."],
        ["L2", "Campus Manager (CM)", "If the subject faculty is unable to rectify the discrepancy, escalate to your Campus Manager."],
        ["L3", "Dr. Abhilash Karakoti — Senior Program Manager", "If the CM is unable to resolve the discrepancy within the 7-day window."],
        ["L4", "Mr. Arpit Sarda", "For final escalation, if the matter remains unresolved even after L3."]
    ]
    t16_l = Table(table_data_16_ladder, colWidths=[50, 220, 230])
    t16_l.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0f2942')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('PADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(t16_l)
    story.append(Spacer(1, 10))
    
    story.append(Paragraph("10. General Guidelines for Students", h2_style))
    story.append(Paragraph("● &nbsp; Wherever possible, inform your Campus Manager in advance about a planned event, or as soon as possible in case of an unplanned medical situation.", bullet_style))
    story.append(Paragraph("● &nbsp; For extended medical situations, share periodic updates with your Campus Manager — do not wait till the end to inform.", bullet_style))
    story.append(Paragraph("● &nbsp; Do not miss consecutive classes without any communication to your Campus Manager or the concerned faculty.", bullet_style))
    story.append(Paragraph("● &nbsp; Understand that the 7-day rule is meant to keep the process fair for everyone — late submissions and late rectification requests cannot be accepted, however genuine the reason, once the window has closed.", bullet_style))
    story.append(Paragraph("● &nbsp; When raising a concern or an escalation, please do so through a single, well-articulated communication. Sending the same email multiple times in a short span does not accelerate the response.", bullet_style))
    
    story.append(Paragraph("11. Effective Date", h2_style))
    story.append(Paragraph("● &nbsp; This policy is effective immediately upon publication and supersedes all previous informal practices with respect to Medical Leave, Duty Leave and attendance rectification for students. It applies uniformly to all students across all Mirai campuses.", bullet_style))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Successfully generated {output_filename}")

if __name__ == "__main__":
    build_handbook_pdf()
