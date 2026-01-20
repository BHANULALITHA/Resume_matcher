import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from src.utils import extract_text_from_pdf, create_pdf
from src.llm_engine import LLMEngine

# --- Page Config ---
st.set_page_config(
    page_title="CV Genius Pro",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom CSS ---
st.markdown("""
    <style>
    .stButton>button {
        width: 100%;
        background-color: #4CAF50;
        color: white;
        border-radius: 5px;
        padding: 0.5rem 1rem;
        font-weight: 600;
    }
    .stButton>button:hover {
        background-color: #45a049;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

# --- Session State Management ---
if 'resume_data' not in st.session_state:
    st.session_state.resume_data = None
if 'processed' not in st.session_state:
    st.session_state.processed = False
if 'original_text' not in st.session_state:
    st.session_state.original_text = ""

# --- Sidebar Configuration ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3135/3135768.png", width=80)
    st.title("CV Genius Pro")
    st.markdown("---")
    
    # Model selection with better descriptions
    model_choice = st.selectbox(
        "Select AI Model", 
        [
            "orca-mini:latest",     # ⭐ RECOMMENDED
            "tinyllama:latest",     # ⚡ Fastest
            "phi3:latest",          # 🎯 Good balance
            "mistral:latest",       # Medium quality
            "neural-chat:latest",   # Best quality
        ], 
        index=0,
        help="orca-mini is recommended for best balance of speed and quality on CPU"
    )
    
    st.caption("⭐ **Recommended:** orca-mini")
    st.caption("📥 Install: `ollama pull orca-mini`")
    
    st.markdown("---")
    st.info("💡 **Tip:** Paste the complete job description for better keyword matching.")

# --- Main Interface ---
st.title("🚀 AI Resume Optimizer")
st.markdown("Transform your resume into an **ATS-optimized version** tailored to specific job postings.")

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📤 Upload & Input")
    uploaded_file = st.file_uploader("Upload Your Resume (PDF)", type=["pdf"], help="Upload your current resume in PDF format")
    job_desc = st.text_area(
        "Paste Job Description", 
        height=300, 
        placeholder="Paste the full job description here...\n\nInclude:\n• Required skills\n• Responsibilities\n• Qualifications\n• Preferred experience",
        help="The more detailed the job description, the better the optimization"
    )

    if st.button("🔍 Analyze & Generate Optimized Resume", type="primary"):
        if uploaded_file and job_desc:
            if len(job_desc.strip()) < 50:
                st.warning("⚠️ Job description seems too short. Please paste a more detailed job description for better results.")
            else:
                # Progress tracking
                progress_container = st.container()
                
                with progress_container:
                    status_text = st.empty()
                    progress_bar = st.progress(0)
                    
                    try:
                        # Step 1: Extract PDF
                        status_text.info("📄 Step 1/3: Extracting text from PDF...")
                        raw_text = extract_text_from_pdf(uploaded_file)
                        
                        if "Error reading PDF" in raw_text or len(raw_text.strip()) < 50:
                            st.error("❌ Failed to extract text from PDF. Please ensure the PDF is not scanned or password-protected.")
                            progress_bar.progress(0)
                        else:
                            st.session_state.original_text = raw_text
                            progress_bar.progress(33)
                            
                            # Step 2: Analyze with AI
                            status_text.info(f"🤖 Step 2/3: Analyzing with {model_choice}... (this may take 30-60 seconds on CPU)")
                            
                            engine = LLMEngine(model_name=model_choice)
                            result = engine.analyze(raw_text, job_desc)
                            progress_bar.progress(66)
                            
                            # Step 3: Finalize
                            status_text.info("✨ Step 3/3: Generating optimized resume...")
                            st.session_state.resume_data = result
                            st.session_state.processed = True
                            
                            progress_bar.progress(100)
                            status_text.success("✅ Analysis complete! Scroll down to see results.")
                            
                            # Auto-scroll hint
                            st.balloons()
                            
                    except Exception as e:
                        st.error(f"❌ Processing Error: {str(e)}")
                        st.error("🔍 Troubleshooting tips:")
                        st.markdown("""
                        1. Ensure Ollama is running: `ollama serve`
                        2. Verify model is installed: `ollama list`
                        3. Install the model: `ollama pull orca-mini`
                        4. Check if Ollama is accessible at http://localhost:11434
                        """)
                        progress_bar.progress(0)
        else:
            st.warning("⚠️ Please provide both a resume PDF and job description.")

# --- Results Dashboard ---
if st.session_state.processed and st.session_state.resume_data:
    data = st.session_state.resume_data
    
    with col2:
        st.subheader("📊 Match Analysis")
        
        # Gauge Chart for Match Score
        score = data.get('match_score', 0)
        score = int(score) if isinstance(score, (str, float)) and str(score).replace('.','').isdigit() else 0
        
        fig = go.Figure(go.Indicator(
            mode = "gauge+number+delta",
            value = score,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "ATS Match Score", 'font': {'size': 16}},
            delta = {'reference': 70, 'increasing': {'color': "green"}},
            gauge = {
                'axis': {'range': [None, 100], 'tickwidth': 1},
                'bar': {'color': "#4CAF50" if score >= 70 else "#FF9800" if score >= 50 else "#FF5722"},
                'bgcolor': "white",
                'borderwidth': 2,
                'bordercolor': "gray",
                'steps': [
                    {'range': [0, 50], 'color': '#ffebee'},
                    {'range': [50, 70], 'color': '#fff3e0'},
                    {'range': [70, 100], 'color': '#e8f5e9'}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 70
                }
            }
        ))
        fig.update_layout(height=280, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig, use_container_width=True)

        # Score interpretation
        if score >= 80:
            st.success("🎉 Excellent match! Your resume aligns very well with the job requirements.")
        elif score >= 60:
            st.info("👍 Good match! Consider adding the missing keywords below to improve further.")
        elif score >= 40:
            st.warning("⚠️ Moderate match. Several key skills should be added to your resume.")
        else:
            st.error("❌ Low match. Consider highlighting more relevant experience and skills.")

        # Missing Keywords
        missing_keywords = data.get('missing_keywords', [])
        if missing_keywords and isinstance(missing_keywords, list) and len(missing_keywords) > 0:
            # Filter out empty or placeholder keywords
            valid_keywords = [str(k).strip() for k in missing_keywords if k and str(k).strip() and 'skill' not in str(k).lower()]
            if valid_keywords:
                st.error(f"⚠️ **Missing Keywords:** {', '.join(valid_keywords[:5])}")
        else:
            st.success("✅ Great keyword coverage!")

    # --- Tabs for Content ---
    st.markdown("---")
    tab1, tab2, tab3, tab4 = st.tabs([
        "📝 Optimized Resume", 
        "✉️ Cover Letter", 
        "🎯 Optimization Tips", 
        "🔍 Raw Data"
    ])
    
    with tab1:
        st.subheader("📄 Your Tailored Resume")
        
        # Contact Info
        contact_info = data.get('personal_info', {})
        name = contact_info.get('name', 'Your Name')
        email = contact_info.get('email', '')
        phone = contact_info.get('phone', '')
        
        st.markdown(f"### {name}")
        
        contact_parts = []
        if email:
            contact_parts.append(f"📧 {email}")
        if phone:
            contact_parts.append(f"📱 {phone}")
        
        if contact_parts:
            st.markdown(" | ".join(contact_parts))
        
        st.markdown("---")
        
        # Professional Summary
        st.markdown("#### 💼 Professional Summary")
        summary = data.get('summary', 'Professional with relevant experience')
        st.markdown(f"*{summary}*")
        
        st.markdown("---")
        
        # Skills Section
        st.markdown("#### 🔧 Key Skills")
        skills = data.get('skills', [])
        if skills and isinstance(skills, list):
            # Display in columns for better visual
            cols = st.columns(3)
            for i, skill in enumerate(skills):
                if skill and str(skill).strip():
                    with cols[i % 3]:
                        st.markdown(f"✓ {skill}")
        
        st.markdown("---")
        
        # Experience Section
        st.markdown("#### 🏢 Professional Experience")
        experience = data.get('experience', [])
        if experience and isinstance(experience, list):
            for idx, exp in enumerate(experience):
                if isinstance(exp, dict):
                    role = exp.get('role', 'N/A')
                    company = exp.get('company', 'N/A')
                    duration = exp.get('duration', '')
                    
                    st.markdown(f"**{role}**")
                    st.markdown(f"*{company}*")
                    if duration:
                        st.caption(f"📅 {duration}")
                    
                    details = exp.get('details', [])
                    if isinstance(details, list):
                        for detail in details:
                            if detail and str(detail).strip():
                                st.markdown(f"• {detail}")
                    
                    if idx < len(experience) - 1:
                        st.markdown("")  # Spacing between experiences
        else:
            st.info("Experience details will be extracted from your resume")
        
        st.markdown("---")
        
        # Education Section
        st.markdown("#### 🎓 Education")
        education = data.get('education', [])
        if education and isinstance(education, list):
            for edu in education:
                if isinstance(edu, dict):
                    degree = edu.get('degree', 'Degree')
                    institution = edu.get('institution', 'Institution')
                    year = edu.get('year', '')
                    
                    st.markdown(f"**{degree}**")
                    st.markdown(f"*{institution}*")
                    if year:
                        st.caption(f"🗓️ {year}")
        else:
            st.info("Education details will be extracted from your resume")
        
        # Download Button
        st.markdown("---")
        st.markdown("### 📥 Download Your Optimized Resume")
        
        try:
            pdf_file = create_pdf(data)
            if pdf_file:
                with open(pdf_file, "rb") as f:
                    st.download_button(
                        label="📄 Download as PDF",
                        data=f,
                        file_name=pdf_file,
                        mime="application/pdf",
                        type="primary"
                    )
                st.success("✅ Resume PDF generated successfully!")
            else:
                st.error("❌ Failed to generate PDF. Please check the console for errors.")
        except Exception as e:
            st.error(f"❌ Error generating PDF: {str(e)}")
            import traceback
            st.code(traceback.format_exc())

    with tab2:
        st.subheader("💌 Personalized Cover Letter")
        st.markdown("*Edit and customize before using*")
        
        cover_letter = data.get('cover_letter', 'Your personalized cover letter will appear here')
        
        edited_cover = st.text_area(
            "Cover Letter", 
            value=cover_letter, 
            height=400,
            help="Edit the cover letter to add personal touches"
        )
        
        # Copy to clipboard helper
        st.markdown("---")
        col_a, col_b = st.columns(2)
        with col_a:
            st.download_button(
                "📄 Download as Text",
                data=edited_cover,
                file_name="cover_letter.txt",
                mime="text/plain"
            )
        with col_b:
            if st.button("📋 Copy to Clipboard"):
                st.code(edited_cover)
                st.info("👆 Select and copy the text above")
    
    with tab3:
        st.subheader("🎯 ATS Optimization Guide")
        
        # Score-based recommendations
        score = int(data.get('match_score', 0))
        
        if score >= 80:
            st.success("### ✅ Excellent Match!")
            st.markdown("Your resume is well-optimized. Minor refinements:")
        elif score >= 60:
            st.info("### ⚠️ Good Match - Room for Improvement")
            st.markdown("Focus on these areas to boost your score:")
        else:
            st.warning("### ❌ Needs Significant Work")
            st.markdown("Priority improvements needed:")
        
        st.markdown("---")
        
        # Missing Keywords Section
        st.markdown("#### 🔑 Keywords to Add")
        missing = data.get('missing_keywords', [])
        if missing and isinstance(missing, list):
            valid_missing = [k for k in missing if k and str(k).strip()]
            if valid_missing:
                for keyword in valid_missing:
                    st.markdown(f"• **{keyword}** - Incorporate this into your experience or skills section")
            else:
                st.success("✅ Your resume covers all major keywords from the job description!")
        else:
            st.success("✅ Excellent keyword coverage!")
        
        st.markdown("---")
        
        # Best Practices
        st.markdown("#### 📋 ATS Best Practices")
        
        with st.expander("📐 Formatting Guidelines", expanded=True):
            st.markdown("""
            - **Use standard fonts**: Arial, Calibri, or Times New Roman
            - **Avoid graphics and images**: ATS can't read them
            - **No headers/footers**: Important info might be missed
            - **Use standard section names**: Summary, Experience, Education, Skills
            - **Save as PDF or DOCX**: Avoid scanned images
            """)
        
        with st.expander("🎯 Content Optimization"):
            st.markdown("""
            - **Mirror job description keywords**: Use exact terminology from the posting
            - **Quantify achievements**: Include numbers, percentages, dollar amounts
            - **Use action verbs**: Led, Developed, Implemented, Increased, etc.
            - **Tailor for each job**: Customize your resume for every application
            - **Keep it concise**: 1-2 pages maximum
            """)
        
        with st.expander("🔍 Keyword Strategy"):
            st.markdown("""
            - **Front-load important keywords**: Place them in summary and top of experience
            - **Use both acronyms and full terms**: e.g., "AI (Artificial Intelligence)"
            - **Include skill variations**: e.g., "JavaScript" and "JS"
            - **Add industry-specific terms**: Use jargon that's common in your field
            """)
        
        with st.expander("✅ Final Checklist"):
            st.markdown("""
            - [ ] Contact information is clear and correct
            - [ ] No spelling or grammar errors
            - [ ] All dates are consistent (MM/YYYY format)
            - [ ] Job titles match industry standards
            - [ ] File name is professional (FirstName_LastName_Resume.pdf)
            - [ ] Tested on ATS scanner tools
            """)
    
    with tab4:
        st.subheader("🔍 Raw Analysis Data")
        st.markdown("*Developer view - JSON structure of the analysis*")
        
        st.json(data)
        
        st.markdown("---")
        st.markdown("#### Original Resume Text")
        with st.expander("View extracted text from your original resume"):
            st.text_area("Original Text", st.session_state.original_text, height=300)

else:
    # Show instructions when no analysis has been done
    with col2:
        st.subheader("👋 How It Works")
        st.markdown("""
        1. **Upload** your current resume (PDF format)
        2. **Paste** the job description you're targeting
        3. **Click** "Analyze & Generate"
        4. **Review** the optimized resume and match score
        5. **Download** your tailored resume as PDF
        
        ---
        
        ### ✨ Features
        - 🤖 AI-powered analysis using local Ollama models
        - 📊 ATS compatibility scoring
        - 🔑 Keyword gap identification
        - ✍️ Automatic cover letter generation
        - 📄 Professional PDF export
        
        ### 💻 Requirements
        - Ollama installed and running
        - Model downloaded (e.g., `ollama pull orca-mini`)
        """)

# Footer
st.markdown("---")
st.caption("🔒 Privacy: All processing happens locally on your machine. No data is sent to external servers.")
st.caption("Made with ❤️ using Streamlit and Ollama | CPU-Optimized for Local AI")