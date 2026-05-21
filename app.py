import streamlit as st
import time

# ==========================================
# Real AI Brain: Google Gemini Integration
# ==========================================
def generate_ats_report(jd_text, pdf_file):
    import PyPDF2
    from google import genai
    import json
    
    # 1. Extract text from the uploaded PDF
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    resume_text = ""
    for page in pdf_reader.pages:
        page_text = page.extract_text()
        if page_text:
            resume_text += page_text + "\n"

    # 2. Connect to Google Gemini using Streamlit Secrets
    try:
        client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
    except Exception as e:
        st.error("⚠️ System Alert: API Key missing. Please add GEMINI_API_KEY to your Streamlit Cloud Secrets.")
        st.stop()

    # 3. Give Gemini explicit instructions to return structured JSON data
    prompt = f"""
    You are an expert ATS optimization scanner and senior technical recruiter.
    Analyze this Resume against this Job Description.
    
    Resume Text:
    {resume_text}
    
    Job Description:
    {jd_text}
    
    Return ONLY a raw JSON object (no markdown formatting, no ```json blocks) with this exact structure:
    {{
        "ats_score": [A number between 0 and 100 representing the match],
        "critical_keywords": [
            {{"keyword": "[Missing or required skill]", "required_level": "[High/Medium/Low]"}},
            {{"keyword": "[Missing or required skill]", "required_level": "[High/Medium/Low]"}}
        ],
        "gaps_and_strategy": [
            {{"category": "[Area of improvement]", "strategy": "[Specific advice to fix it]", "criticality": "[Critical/Moderate/Low]"}}
        ]
    }}
    """
    
    # 4. Generate the response
    try:
        response = client.models.generate_content(
            model='gemini-1.5-flash',
            contents=prompt
        )
        
        # 5. Clean up the response and convert it to a Python dictionary
        clean_json = response.text.replace('```json', '').replace('```', '').strip()
        report_data = json.loads(clean_json)
        
        # Ensure fallback defaults if AI misses a key
        if "ats_score" not in report_data: report_data["ats_score"] = "N/A"
        if "critical_keywords" not in report_data: report_data["critical_keywords"] = []
        if "gaps_and_strategy" not in report_data: report_data["gaps_and_strategy"] = []
        
        return report_data
        
    except Exception as e:
        # Fallback if the AI fails or returns invalid JSON
        return {
            "ats_score": 0,
            "critical_keywords": [{"keyword": "System Error", "required_level": "High"}],
            "gaps_and_strategy": [{"category": "Error", "strategy": f"Failed to parse response: {str(e)}", "criticality": "Critical"}]
        }


# ==========================================
# Page Configuration & Custom CSS
# ==========================================
st.set_page_config(
    page_title="BK.ai | Intelligent Resume Strategist",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    /* Global style: Dark base with Neon glowing orbs */
    [data-testid="stAppViewContainer"] {
        background-color: #05050a;
        background-image: 
            radial-gradient(circle at 15% 50%, rgba(110, 40, 217, 0.15), transparent 40%),
            radial-gradient(circle at 85% 20%, rgba(217, 70, 239, 0.1), transparent 40%);
        background-attachment: fixed;
        color: #e0e0e0;
        font-family: 'SF Pro Display', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
    }
    
    /* Sidebar Glassmorphism Styling */
    [data-testid="stSidebar"] {
        background-color: rgba(10, 10, 15, 0.4) !important;
        backdrop-filter: blur(20px) !important;
        -webkit-backdrop-filter: blur(20px) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.05) !important;
    }
    .sidebar-title {
        background: linear-gradient(to right, #ffffff, #a881ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        font-size: 2.5rem;
        margin-bottom: 0px;
    }
    
    /* Header layout */
    .app-title-container {
        display: flex;
        align-items: center;
        margin-bottom: 3rem;
    }
    
    /* Typography Overhauls */
    .gradient-text {
        background: linear-gradient(to right, #ffffff, #a881ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        font-size: 4rem;
        line-height: 1.1;
        margin-bottom: 1rem;
    }
    .main-title {
        color: #f8f9fa;
        font-size: 2rem;
        font-weight: 700;
        margin: 0;
    }
    .sub-title {
        color: #a1a1aa;
        font-size: 1.3rem;
        font-weight: 400;
        margin-top: 1rem;
        margin-bottom: 4rem;
        line-height: 1.5;
        max-width: 800px;
        margin-left: auto;
        margin-right: auto;
    }
    
    /* Hero layout */
    .landing-page-hero-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        text-align: center;
        margin-bottom: 6rem;
        padding-top: 2rem;
    }
    .styled-card-row {
        margin-bottom: 5rem;
    }
    
    /* Glassmorphism Cards */
    .styled-card {
        background: rgba(20, 20, 25, 0.5);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 20px;
        padding: 2.5rem;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
        transition: transform 0.3s ease, border-color 0.3s ease;
    }
    .styled-card:hover {
        border-color: rgba(168, 129, 255, 0.3);
        transform: translateY(-5px);
    }
    .styled-card.input-panel {
        background: rgba(15, 15, 20, 0.7);
        padding: 4rem;
        display: flex;
        flex-direction: column;
        align-items: center;
    }
    
    /* Section Headers */
    h2.section-header {
        font-size: 2rem;
        font-weight: 700;
        color: #ffffff;
        margin-bottom: 2rem;
        border-bottom: 2px solid rgba(168, 129, 255, 0.3);
        display: inline-block;
        padding-bottom: 0.5rem;
    }
    h3.card-title {
        font-size: 1.5rem;
        font-weight: 600;
        color: #ffffff;
        margin-bottom: 1rem;
    }
    .card-description {
        font-size: 1rem;
        color: #a1a1aa;
        margin-bottom: 2rem;
        line-height: 1.6;
    }
    
    /* Input Elements Overhaul */
    .stTextArea textarea, .stFileUploader > div > div > div > button {
        background: rgba(10, 10, 15, 0.6) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
        color: #f8f9fa !important;
        padding: 1.2rem !important;
        font-size: 1rem !important;
    }
    .stTextArea textarea:focus {
        border-color: #a881ff !important;
        box-shadow: 0 0 10px rgba(168, 129, 255, 0.2) !important;
    }
    
    /* Gradient Primary Button */
    .stButton > button {
        background: linear-gradient(135deg, #7c3aed 0%, #d946ef 100%) !important;
        border: none !important;
        color: #ffffff !important;
        font-size: 1.1rem !important;
        font-weight: 600 !important;
        padding: 1rem 3rem !important;
        border-radius: 12px !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(124, 58, 237, 0.3) !important;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(217, 70, 239, 0.4) !important;
    }
    
    /* Data Points styling inside cards */
    .mock-panel-group {
        display: flex;
        flex-direction: column;
        gap: 1rem;
    }
    .data-point {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 1rem;
        background: rgba(0, 0, 0, 0.3);
        border-radius: 10px;
        border: 1px solid rgba(255, 255, 255, 0.05);
    }
    .data-label {
        font-weight: 500;
        color: #e0e0e0;
        font-size: 0.95rem;
    }
    .data-value {
        font-weight: 600;
        color: #ffffff;
    }
    
    /* Score visuals */
    .score-circle {
        display: inline-flex;
        justify-content: center;
        align-items: center;
        width: 100px;
        height: 100px;
        border-radius: 50%;
        border: 4px solid #a881ff;
        font-size: 2.2rem;
        font-weight: 800;
        color: #ffffff;
        box-shadow: 0 0 20px rgba(168, 129, 255, 0.2);
    }
    
    /* Criticality Tags */
    .criticality-tag {
        display: inline-block;
        padding: 0.4rem 1rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .critical { background: rgba(244, 63, 94, 0.2); color: #fb7185; border: 1px solid rgba(244, 63, 94, 0.3); }
    .moderate { background: rgba(251, 191, 36, 0.2); color: #fcd34d; border: 1px solid rgba(251, 191, 36, 0.3); }
</style>
""", unsafe_allow_html=True)

# Helper function to render data points
def render_data_point(label, value, extra_class=""):
    st.markdown(f'<div class="data-point"><span class="data-label">{label}</span><span class="data-value {extra_class}">{value}</span></div>', unsafe_allow_html=True)


# ==========================================
# Sidebar Support Configuration
# ==========================================
with st.sidebar:
    st.markdown('<div class="sidebar-title">BK.ai</div>', unsafe_allow_html=True)
    st.caption("v2.0.0 | Enterprise ATS Intelligence")
    
    st.divider()
    
    st.markdown("### 🤝 Support & Contact")
    st.markdown("""
    *Engineered by Kalpana*
    
    **Need assistance or want to collaborate?**
    * 📧 [Email Me](mailto:kalpanakb1822@gmail.com)
    * 💻 [GitHub Profile](https://github.com/kalpana1822)
    """)
    
    st.divider()
    st.info("💡 **Pro Tip:** Ensure your PDF text is selectable. Image-based PDFs will not scan properly.")

# ==========================================
# Main Application Interface
# ==========================================
def main():
    # Header
    st.markdown("""
    <div class="app-title-container">
        <h1 class="main-title">BK.ai</h1>
    </div>
    """, unsafe_allow_html=True)

    # Hero Section
    st.markdown("""
    <div class="landing-page-hero-container">
        <div class="gradient-text">Unleashing the Power of<br>Artificial Intelligence</div>
        <p class="sub-title">Embracing the Age of Artificial Intelligence. Discover the Boundless Potential and Impact of AI in Every Sphere of Life and elevate your career trajectory.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Interactive Get Started Button
    _, center_btn, _ = st.columns([1, 1, 1])
    with center_btn:
        if st.button("Get Started", key="hero_btn"):
            st.toast("Welcome to BK.ai! Scroll down to optimize your resume.", icon="✨")

    # Scanning Section (Input)
    st.markdown('<h2 class="section-header" style="text-align: center; display: block; margin-top: 4rem;">Optimize Your Strategy</h2>', unsafe_allow_html=True)
    st.markdown('<div class="styled-card-row">', unsafe_allow_html=True)
    
    with st.container():
        input_container, _ = st.columns([1.5, 0.5])
        with input_container:
            st.markdown('<div class="styled-card input-panel">', unsafe_allow_html=True)
            st.markdown('<h3 class="card-title">Analyze Your Application</h3>', unsafe_allow_html=True)
            st.markdown('<p class="card-description">Submit your target job description and your resume for a zero-shot AI evaluation.</p>', unsafe_allow_html=True)
            
            jd_input = st.text_area(
                "TARGET JOB DESCRIPTION",
                placeholder="Paste the Job Description here...",
                height=200,
                key="jd_text_area",
                label_visibility="collapsed",
            )
            
            col_file, _ = st.columns([2, 1])
            with col_file:
                st.markdown('<br><span class="data-label" style="margin-bottom: 10px; display:block;">UPLOAD RESUME (PDF)</span>', unsafe_allow_html=True)
                uploaded_pdf = st.file_uploader(
                    "",
                    type=["pdf"],
                    key="resume_uploader",
                    label_visibility="collapsed",
                )
            
            st.markdown('<div style="margin-top: 3rem;">', unsafe_allow_html=True)
            analyze_button = st.button("🚀 Generate Report", key="ats_analyze_button")
            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Output Section
    report_container = st.empty()
    
    if analyze_button and jd_input and uploaded_pdf:
        with st.status("🔮 Intelligent Strategist analyzing details...", expanded=True) as status:
            st.write("📄 Extracting resume data...")
            st.write("🧠 Engaging Gemini AI models...")
            
            # Fetch real data from the AI
            report_data = generate_ats_report(jd_input, uploaded_pdf)
            status.update(label="Analysis finalized!", state="complete", expanded=False)
        
        with report_container.container():
            st.markdown('<h2 class="section-header">AI Evaluation Report</h2>', unsafe_allow_html=True)
            st.markdown('<div class="styled-card-row">', unsafe_allow_html=True)
            
            # Card 1: Score & Critical Keywords
            st.markdown('<div class="styled-card">', unsafe_allow_html=True)
            col_score, col_keywords = st.columns([1, 1])
            
            with col_score:
                st.markdown(f'<h3 class="card-title">ATS Match Score</h3><div class="card-description">Overall performance heuristic.</div><div class="score-circle">{report_data.get("ats_score", 0)}%</div>', unsafe_allow_html=True)
            
            with col_keywords:
                st.markdown('<h3 class="card-title">Critical Keywords</h3><div class="card-description">Top skills priority analysis.</div>', unsafe_allow_html=True)
                st.markdown('<div class="mock-panel-group">', unsafe_allow_html=True)
                for kw_data in report_data.get("critical_keywords", []):
                    req_level = kw_data.get('required_level', 'Unknown')
                    render_data_point(kw_data.get("keyword", "N/A"), f"Req: {req_level.upper()}")
                st.markdown('</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True) 
            
            # Card 2: Strategy
            st.markdown('<div class="styled-card">', unsafe_allow_html=True)
            st.markdown('<h3 class="card-title">Actionable Strategy</h3><div class="card-description">Recommendations to improve your match.</div>', unsafe_allow_html=True)
            
            for gap in report_data.get("gaps_and_strategy", []):
                category = gap.get("category", "Detail").upper()
                criticality = gap.get("criticality", "Moderate")
                strategy = gap.get("strategy", "")
                
                st.markdown(f'<div class="data-point" style="flex-direction: column; align-items: flex-start; gap: 10px; margin-bottom: 10px;">', unsafe_allow_html=True)
                st.markdown(f'<div style="display: flex; justify-content: space-between; width: 100%;"><span class="data-label">{category}</span><span class="criticality-tag {criticality.lower()}">{criticality}</span></div>', unsafe_allow_html=True)
                st.markdown(f'<span style="color: #a1a1aa; font-size: 0.95rem;">{strategy}</span>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True) 

    # Pricing Section
    st.markdown('<div style="text-align: center; margin-top: 6rem;"><h2 class="section-header">Discover our pricing plans</h2><p class="card-description">Pick a plan to grow your brand and business</p></div>', unsafe_allow_html=True)
    st.markdown('<div class="styled-card-row">', unsafe_allow_html=True)
    
    col_p1, col_p2, col_p3 = st.columns([1,1,1])
    
    with col_p1:
        st.markdown('<div class="styled-card">', unsafe_allow_html=True)
        st.markdown('<h3 class="card-title">Basic</h3><div class="card-description">Free starter performance tools.</div>', unsafe_allow_html=True)
        st.markdown('<div style="font-size: 2.5rem; font-weight: 800; color: #ffffff; margin-bottom: 2rem;">$0<span style="font-size: 1rem; color: #a1a1aa; font-weight: 500;">/mo</span></div>', unsafe_allow_html=True)
        st.markdown('<div class="mock-panel-group" style="margin-bottom: 2rem;">', unsafe_allow_html=True)
        render_data_point("Basic Formatting Checks", "Included")
        render_data_point("Monthly ATS Scans", "5 Scans")
        render_data_point("Community Support", "Included")
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Interactive Button
        if st.button("Current Plan", key="btn_basic"):
            st.info("You are currently using the Free Basic tier.")
            
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col_p2:
        st.markdown('<div class="styled-card" style="border-color: rgba(217, 70, 239, 0.4); box-shadow: 0 0 30px rgba(217, 70, 239, 0.1);">', unsafe_allow_html=True)
        st.markdown('<h3 class="card-title">Premium</h3><div class="card-description">Detailed performance analysis.</div>', unsafe_allow_html=True)
        st.markdown('<div style="font-size: 2.5rem; font-weight: 800; color: #ffffff; margin-bottom: 2rem;">$9.99<span style="font-size: 1rem; color: #a1a1aa; font-weight: 500;">/mo</span></div>', unsafe_allow_html=True)
        st.markdown('<div class="mock-panel-group" style="margin-bottom: 2rem;">', unsafe_allow_html=True)
        render_data_point("Advanced NLP Analysis", "Included")
        render_data_point("Monthly ATS Scans", "Unlimited")
        render_data_point("Keyword Prioritization", "Included")
        render_data_point("Priority Email Support", "Included")
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Interactive Button
        if st.button("Upgrade to Premium", key="btn_prem"):
            st.success("Redirecting to secure checkout... 💳")
            st.balloons()
            
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col_p3:
        st.markdown('<div class="styled-card">', unsafe_allow_html=True)
        st.markdown('<h3 class="card-title">Enterprise</h3><div class="card-description">Full structural strategizing.</div>', unsafe_allow_html=True)
        st.markdown('<div style="font-size: 2.5rem; font-weight: 800; color: #ffffff; margin-bottom: 2rem;">$99.0<span style="font-size: 1rem; color: #a1a1aa; font-weight: 500;">/mo</span></div>', unsafe_allow_html=True)
        st.markdown('<div class="mock-panel-group" style="margin-bottom: 2rem;">', unsafe_allow_html=True)
        render_data_point("Custom ATS Rulesets", "Included")
        render_data_point("API Integration Access", "Included")
        render_data_point("Dedicated Account Manager", "Included")
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Interactive Button
        if st.button("Contact Sales", key="btn_ent"):
            st.toast("Thank you! Our enterprise team will email you shortly.", icon="📩")
            
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

    # Footer
    st.markdown('<div style="text-align: center; color: #71717a; padding: 2rem; border-top: 1px solid rgba(255,255,255,0.05); margin-top: 4rem;">© 2026 BK.ai. Engineered by Kalpana. Empowering the future of human capital.</div>', unsafe_allow_html=True)

if __name__ == '__main__':
    main()
