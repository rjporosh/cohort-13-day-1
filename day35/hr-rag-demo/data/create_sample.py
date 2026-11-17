from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from xml.sax.saxutils import escape

out='/mnt/data/hr-rag-demo/data/URI_HR_Recruitment_Procedure_Demo_Excerpt.pdf'
doc=SimpleDocTemplate(out,pagesize=A4,rightMargin=20*mm,leftMargin=20*mm,topMargin=18*mm,bottomMargin=18*mm)
styles=getSampleStyleSheet()
styles.add(ParagraphStyle(name='Small',parent=styles['BodyText'],fontSize=8,leading=11,textColor=colors.HexColor('#555555')))
styles.add(ParagraphStyle(name='Section',parent=styles['Heading2'],spaceBefore=10,spaceAfter=5,textColor=colors.HexColor('#17365D')))
story=[]
def p(t,style='BodyText'): story.append(Paragraph(t,styles[style] if style in styles else styles['BodyText']))
def bullet(t): p('&bull; '+t)
p('HR RAG DEMO — SOURCE DOCUMENT EXCERPT','Title')
p('University of Rhode Island — Procedures for Policy on Employee Recruitment, Selection and Hiring','Heading2')
p('<b>Policy #:</b> 02.001.1 &nbsp;&nbsp; <b>Effective date:</b> July 1, 2024')
p('<b>Important:</b> This is a compact, source-derived demo excerpt prepared for RAG experimentation. It is NOT the complete official 54-page policy and must not be treated as legal or operational advice. Consult the official source for authoritative/current wording.','Small')
p('Official source: <link href="https://web.uri.edu/policies/wp-content/uploads/sites/928/Procedures-for-Policy-on-Employee-RSH-20240627.pdf" color="blue">URI Procedures for Policy on Employee Recruitment, Selection and Hiring (PDF)</link>','Small')
story.append(Spacer(1,10))
p('1. Purpose and ownership','Section')
p('The University of Rhode Island hires employees for a wide range of services. The procedures describe pre-recruitment planning, sourcing, evaluating and selecting applicants to interview, hiring, and onboarding. The procedures are maintained by the Office of Human Resource Administration (HR), which leads talent acquisition activities. HR periodically reviews the policy and supporting procedures. (Official document, printed page 5)')
p('2. Forms related to the procedure','Section')
p('<b>Employee Recruitment Strategy Form:</b> Provides HR with information needed to post a vacancy and document compliance. It must be submitted with a request to initiate a posting for faculty and non-classified staff searches. (Printed page 5)')
p('<b>Applicant Evaluation Rubric:</b> Supports consistent and fair applicant evaluation. It must be submitted to HR with a request to interview applicants for faculty and non-classified staff postings. (Printed page 5)')
p('3. Seven stages of recruitment and hiring','Section')
for x in ['Stage I — Pre-Recruitment Planning: obtain approval to fill a position, write the position description, and form a search committee.','Stage II — Sourcing: consider advertising and outreach, develop a formal recruitment strategy, submit the Employee Recruitment Strategy Form, post the vacancy, implement paid advertising, and conduct outreach.','Stage III — Evaluating Applicants: prepare to review applications, assess applicants against required qualifications, select semi-finalists, and submit the Applicant Evaluation Rubric with the interview request.','Stage IV — Interviewing and Selecting Preferred Candidates: conduct interviews and determine which applicants best meet the required qualifications and department needs.','Stage V — Hiring: select the most qualified candidate, make an employment offer and negotiate the contract, prepare the appointment letter, and complete the search process.','Stage VI — Onboarding: welcome the new employee, introduce the University structure, vision, mission, values and policies, and help the employee succeed in the role.','Stage VII — Post-Recruitment Evaluation: conduct a post-search survey.']:
    bullet(x)
p('These seven stages are described for faculty and non-classified staff processes. Their implementation may vary. (Printed pages 6–7)')
p('4. Pay equity and confidentiality','Section')
p('Under the Rhode Island Pay Equity Act provisions summarized in the procedure, hiring managers, search chairs and search committee members must not seek or rely on an applicant’s wage history when considering the applicant or determining pay. If an applicant requests the position’s wage range, it must be provided; the procedure also says the range should be provided before compensation is discussed. (Printed page 8)')
p('Applicant names must not be shared outside the search committee except with the hiring manager. Search committee members must protect personally identifiable information. Finalist information may sometimes be made public for presentations, in which case applicants should be informed and agree to disclosure. (Printed page 8)')
p('5. Faculty position approval and role requirements','Section')
p('For faculty searches, the department contacts the Dean with a request to fill a vacant position. The Dean seeks approval through the annual budget allocation process for new positions or directly from the Provost to refill a newly vacant position. The procedure describes additional forms and financial planning steps for certain positions. (Printed page 10)')
p('Faculty position descriptions must distinguish required qualifications from preferred qualifications. Required qualifications are minimum measurable skills, education, training, certifications, licenses or other specified requirements related to the essential duties. Applicants must meet all required qualifications to be considered for interview. Lack of a preferred qualification does not disqualify an applicant from interview. (Printed pages 11–12)')
p('Faculty position descriptions must be approved by the Dean. After approval, the Search Chair forwards the description to HR for entry into the applicant tracking system. HR reviews the posting and requirements for clarity and alignment with essential duties. (Printed page 12)')
p('6. Search committee requirements for faculty searches','Section')
p('Faculty searches generally require a search committee unless an applicable exception or HR waiver applies. Members must have completed the University recruitment, selection and hiring training within the two years before participating. Unless a collective bargaining agreement says otherwise, faculty search committees must have at least three members. HR approval of committee composition is required. (Printed page 13)')
p('7. Vacancy posting and external advertising','Section')
p('All vacancies must be posted on the University employment website for at least ten business days. Faculty positions must also be advertised externally unless HR waives the requirement in writing. (Printed page 14)')
p('8. Scope and limitations of this demo file','Section')
p('This excerpt covers selected general procedures and faculty-search details. It does not contain every rule for non-classified staff, classified staff, part-time faculty, postdoctoral fellows, graduate assistants, casual employees, or all onboarding and system-navigation steps. If a question requires information not present here, a grounded RAG assistant should say the excerpt does not provide enough information rather than inventing an answer.')
p('Source note','Section')
p('All policy-specific statements in this demo excerpt are paraphrased from the official University of Rhode Island procedure document, effective July 1, 2024. Original printed page references are included inline. This derivative learning sample is provided to demonstrate document retrieval, not to replace the official document.','Small')

def footer(canvas, doc):
    canvas.saveState(); canvas.setFont('Helvetica',8); canvas.setFillColor(colors.grey)
    canvas.drawString(20*mm,10*mm,'HR RAG Demo — source-derived excerpt; see official URI PDF for full policy')
    canvas.drawRightString(A4[0]-20*mm,10*mm,f'Demo PDF page {doc.page}')
    canvas.restoreState()
doc.build(story,onFirstPage=footer,onLaterPages=footer)
print(out)
