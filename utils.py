import pdfplumber
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import re
from typing import Dict, Any

def extract_text_from_pdf(file) -> str:
    """
    Robust PDF text extraction with comprehensive error handling.
    
    Args:
        file: Uploaded PDF file object
        
    Returns:
        Extracted text or error message
    """
    try:
        text = ""
        with pdfplumber.open(file) as pdf:
            if len(pdf.pages) == 0:
                return "Error: PDF has no pages"
            
            for page_num, page in enumerate(pdf.pages):
                try:
                    extracted = page.extract_text()
                    if extracted:
                        text += extracted + "\n"
                except Exception as e:
                    print(f"Warning: Could not extract text from page {page_num + 1}: {str(e)}")
                    continue
        
        if not text.strip():
            return "Error: No text could be extracted from PDF. The file might be scanned or image-based."
        
        return text.strip()
        
    except Exception as e:
        return f"Error reading PDF: {str(e)}. Please ensure the file is a valid PDF and not password-protected."

def create_pdf(data: Dict[str, Any]) -> str:
    """
    Generate an ATS-optimized resume PDF with professional formatting.
    
    This creates a clean, scannable resume that works well with Applicant Tracking Systems.
    
    Args:
        data: Dictionary containing resume data
        
    Returns:
        Filename of generated PDF or None if error
    """
    try:
        # Extract and validate personal info
        personal_info = data.get('personal_info', {})
        name = personal_info.get('name', '').strip()
        
        if not name or name == '':
            # Fallback to data.get('name') if personal_info.name is empty
            name = data.get('name', 'Resume').strip()
        
        if not name or name == '':
            name = 'Optimized_Resume'
        
        # Sanitize filename
        safe_name = re.sub(r'[^\w\s-]', '', name)
        safe_name = re.sub(r'[-\s]+', '_', safe_name)
        filename = f"{safe_name}_Resume.pdf"
        
        # Create PDF document with proper margins
        doc = SimpleDocTemplate(
            filename, 
            pagesize=letter,
            topMargin=0.5*inch, 
            bottomMargin=0.5*inch,
            leftMargin=0.75*inch,
            rightMargin=0.75*inch
        )
        
        elements = []
        styles = getSampleStyleSheet()
        
        # ===== CUSTOM STYLES =====
        
        # Name/Title style
        name_style = ParagraphStyle(
            'CandidateName',
            parent=styles['Heading1'],
            fontSize=22,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=4,
            spaceBefore=0,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        # Contact info style
        contact_style = ParagraphStyle(
            'Contact',
            parent=styles['Normal'],
            fontSize=10,
            alignment=TA_CENTER,
            spaceAfter=16,
            textColor=colors.HexColor('#333333')
        )
        
        # Section header style (Professional, clean look)
        section_header_style = ParagraphStyle(
            'SectionHeader',
            parent=styles['Heading2'],
            fontSize=12,
            textColor=colors.HexColor('#1f4788'),
            spaceAfter=6,
            spaceBefore=12,
            fontName='Helvetica-Bold',
            borderWidth=0,
            borderColor=colors.HexColor('#1f4788'),
            borderPadding=0,
            leftIndent=0
        )
        
        # Body text style
        body_style = ParagraphStyle(
            'BodyText',
            parent=styles['Normal'],
            fontSize=10,
            leading=14,
            textColor=colors.HexColor('#1a1a1a'),
            alignment=TA_LEFT
        )
        
        # Bullet point style
        bullet_style = ParagraphStyle(
            'BulletPoint',
            parent=styles['Normal'],
            fontSize=10,
            leading=13,
            leftIndent=20,
            textColor=colors.HexColor('#1a1a1a')
        )
        
        # Job title style
        job_title_style = ParagraphStyle(
            'JobTitle',
            parent=styles['Normal'],
            fontSize=11,
            fontName='Helvetica-Bold',
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=2
        )
        
        # Company/Institution style
        company_style = ParagraphStyle(
            'Company',
            parent=styles['Normal'],
            fontSize=10,
            fontName='Helvetica-Oblique',
            textColor=colors.HexColor('#333333'),
            spaceAfter=2
        )
        
        # Date style
        date_style = ParagraphStyle(
            'DateRange',
            parent=styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor('#666666'),
            spaceAfter=4
        )
        
        # ===== DOCUMENT CONTENT =====
        
        # 1. CANDIDATE NAME
        elements.append(Paragraph(name, name_style))
        
        # 2. CONTACT INFORMATION
        email = personal_info.get('email', '').strip()
        phone = personal_info.get('phone', '').strip()
        
        contact_parts = []
        if email:
            contact_parts.append(email)
        if phone:
            contact_parts.append(phone)
        
        if contact_parts:
            contact_text = " • ".join(contact_parts)
            elements.append(Paragraph(contact_text, contact_style))
        else:
            elements.append(Spacer(1, 0.15*inch))
        
        # 3. PROFESSIONAL SUMMARY
        summary = data.get('summary', '').strip()
        if summary:
            elements.append(Paragraph("PROFESSIONAL SUMMARY", section_header_style))
            elements.append(Paragraph(summary, body_style))
            elements.append(Spacer(1, 0.1*inch))
        
        # 4. KEY SKILLS
        skills = data.get('skills', [])
        if skills and isinstance(skills, list):
            skills_list = [str(s).strip() for s in skills if s and str(s).strip()]
            
            if skills_list:
                elements.append(Paragraph("KEY SKILLS", section_header_style))
                
                # Format skills as comma-separated list for ATS
                skills_text = ", ".join(skills_list)
                elements.append(Paragraph(skills_text, body_style))
                elements.append(Spacer(1, 0.1*inch))
        
        # 5. PROFESSIONAL EXPERIENCE
        experience = data.get('experience', [])
        if experience and isinstance(experience, list):
            elements.append(Paragraph("PROFESSIONAL EXPERIENCE", section_header_style))
            
            for idx, exp in enumerate(experience):
                if isinstance(exp, dict):
                    role = exp.get('role', '').strip()
                    company = exp.get('company', '').strip()
                    duration = exp.get('duration', '').strip()
                    
                    # Job Title
                    if role:
                        elements.append(Paragraph(role, job_title_style))
                    
                    # Company Name
                    if company:
                        elements.append(Paragraph(company, company_style))
                    
                    # Duration
                    if duration:
                        elements.append(Paragraph(duration, date_style))
                    
                    # Responsibilities/Achievements
                    details = exp.get('details', [])
                    if isinstance(details, list):
                        for detail in details:
                            if detail and str(detail).strip():
                                bullet_text = f"• {str(detail).strip()}"
                                elements.append(Paragraph(bullet_text, bullet_style))
                    
                    # Add spacing between jobs
                    if idx < len(experience) - 1:
                        elements.append(Spacer(1, 0.08*inch))
            
            elements.append(Spacer(1, 0.1*inch))
        
        # 6. EDUCATION
        education = data.get('education', [])
        if education and isinstance(education, list):
            elements.append(Paragraph("EDUCATION", section_header_style))
            
            for edu in education:
                if isinstance(edu, dict):
                    degree = edu.get('degree', '').strip()
                    institution = edu.get('institution', '').strip()
                    year = edu.get('year', '').strip()
                    
                    # Degree
                    if degree:
                        elements.append(Paragraph(degree, job_title_style))
                    
                    # Institution
                    if institution:
                        elements.append(Paragraph(institution, company_style))
                    
                    # Year
                    if year:
                        elements.append(Paragraph(year, date_style))
                    
                    elements.append(Spacer(1, 0.05*inch))
        
        # Build the PDF
        doc.build(elements)
        
        print(f"✅ PDF generated successfully: {filename}")
        return filename
        
    except Exception as e:
        print(f"❌ Error creating PDF: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def validate_resume_data(data: Dict[str, Any]) -> bool:
    """
    Validate that resume data has required fields.
    
    Args:
        data: Resume data dictionary
        
    Returns:
        True if valid, False otherwise
    """
    required_fields = ['personal_info', 'summary', 'skills']
    
    for field in required_fields:
        if field not in data:
            print(f"Warning: Missing required field: {field}")
            return False
    
    # Check personal_info has at least name
    if not data.get('personal_info', {}).get('name'):
        print("Warning: Personal info missing name")
        return False
    
    return True