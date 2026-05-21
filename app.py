import streamlit as st
import time
from supabase import create_client, Client
import json

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
    
    /* Sidebar Styling */
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
    
    /* Login Form Inputs & Input Elements */
    [data-testid="stSidebar"] input, .stTextArea textarea, .stFileUploader > div > div > div > button {
        background-color: rgba(0, 0, 0, 0.5) !important;
        color: white !important;
        border: 1px solid rgba(168, 129, 255, 0.3) !important;
        border-radius: 8px !important;
    }
    
    /* Header layout */
    .app-title-container {
        display: flex;
        align-items: center;
        margin-bottom: 3rem;
    }
    
    /* Typography */
    .gradient-text {
        background: linear-gradient(to right, #ffffff, #a881ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        font-size: 4rem;
        line-height: 1.1;
        margin-bottom: 1rem;
    }
    .main-title { color: #f8f9fa; font-size: 2rem; font-weight: 700; margin: 0; }
    .sub-title { color: #a1a1aa; font-size: 1.3rem; font-weight: 400; margin-top: 1rem; margin-bottom: 4rem; line-height: 1.5; max-width: 800px; margin-left: auto; margin-right: auto; }
    
    /* Layouts */
    .landing-page-hero-container { display: flex; flex-direction: column; align-items: center; text-align: center; margin-bottom: 6rem; padding-top: 2rem; }
    .styled-card-row { margin-bottom: 5rem; }
    
    /* Glassmorphism Cards */
    .styled-card {
        background: rgba(20, 20, 25, 0.5);
        backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 20px;
        padding: 2.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
    }
    
    /* Section Headers */
    h2.section-header { font-size: 2rem; font-weight: 700; color: #ffffff; margin-bottom: 2rem; border-bottom: 2px solid rgba(168, 129, 255, 0.3); display: inline-block; padding-bottom: 0.5rem; }
    h3.card-title { font-size: 1.5rem; font-weight: 600; color: #ffffff; margin-bottom: 1rem; }
    .card-description { font-size: 1rem; color: #a1a1aa; margin-bottom: 2rem; line-height: 1.6; }
    
    /* Default Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #7c3aed 0%, #d946ef 100%) !important;
        border: none !important;
        color: #ffffff !important;
        font-size: 1.1rem !important;
        font-weight: 600 !important;
        border-radius: 12px !important;
        width: 100% !important;
    }

    /* MASSIVE DOWNLOAD BUTTON STYLING */
    [data-testid="stDownloadButton"] > button {
        background: linear-gradient(135deg, #10b981 0%, #047857 100%) !important;
        font-size: 1.8rem !important; /* Huge Font */
        padding: 1.5rem 2rem !important; /* Thick padding */
        font-weight: 900 !important;
        border-radius: 16px !important;
        text-transform: uppercase !important;
        letter-spacing: 2px !important;
        box-shadow: 0 10px 30px rgba(16, 185, 129, 0.4) !important;
        border: 2px solid #34d399 !important;
        transition: transform 0.2s ease, box-shadow 0.2s ease !important;
    }
    [data-testid="stDownloadButton"] > button:hover {
        transform: translateY(-4px) !important;
        box-shadow: 0 15px 40px rgba(16, 185, 129, 0.6) !important;
    }
    
    /* Data Points */
    .mock-panel-group { display: flex; flex-direction: column; gap: 1rem; }
    .data-point { display: flex; justify-content: space-between; align-items: center; padding: 1rem; background: rgba(0, 0, 0, 0.3); border-radius: 10px; border: 1px solid rgba(255, 255, 255, 0.05); }
    .data-label { font-weight: 500; color: #e0e0e0; font-size: 0.95rem; }
    .data-value { font-weight: 600; color: #ffffff; }
    .score-circle { display: inline-flex; justify-content: center; align-items: center; width: 100px; height: 100px; border-radius: 50%; border: 4px solid #a881ff; font-size: 2.2rem; font-weight: 800; color: #ffffff; box-shadow: 0 0 20px rgba(168, 129, 255, 0.2); margin: 0 auto; }
    .criticality-tag { display: inline-block; padding: 0.4rem 1rem; border-radius: 20px; font-size: 0.8rem; font-weight: 700; text-transform: uppercase; }
    .critical { background: rgba(244, 63, 94, 0.2); color: #fb7185; border: 1px solid rgba(244, 63, 94, 0.3); }
    .moderate { background: rgba(251, 191, 36, 0.2); color: #fcd34d; border: 1px solid rgba(251, 191, 36, 0.3); }
</style>
""", unsafe_allow_html=True)

# ==========================================
# Real AI Brain: Google Gemini Integration
# ==========================================
def generate_ats_report(jd_text, pdf_file):
    import PyPDF2
    from google import genai
    
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    resume_text = ""
    for page in pdf_reader.pages:
        page_text = page.extract_text()
        if page_text:
            resume_text += page_text + "\n"

    try:
        client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
    except Exception as e:
        st.error("⚠️ API Key missing from secrets.")
        st.stop()

    prompt = f"""
    You are an expert ATS optimization scanner and senior technical recruiter.
    Analyze this Resume against this Job Description.
    
    Resume Text:
    {resume_text}
    
    Job Description:
    {jd_text}
    
    Return ONLY a raw, perfectly valid JSON object. Do not include any conversational text, do not use markdown code blocks (like ```json), and ensure there are no missing trailing commas.
    Strictly adhere to this exact structure:
    {{
        "ats_score": 85,
        "critical_keywords": [
            {{"keyword": "Example Skill", "required_level": "High"}}
        ],
        "gaps_and_strategy": [
            {{"category": "Detail", "strategy": "Add specific metrics.", "criticality": "Moderate"}}
        ]
    }}
    """
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
        )
        
        clean_json = response.text.replace('```json', '').replace('```', '').strip()
        report_data = json.loads(clean_json)
        
        if "ats_score" not in report_data: report_data["ats_score"] = "N/A"
        if "critical_keywords" not in report_data: report_data["critical_keywords"] = []
        if "gaps_and_strategy" not in report_data: report_data["gaps_and_strategy"] = []
        return report_data
    except Exception as e:
        return {
            "ats_score": 0,
            "critical_keywords": [{"keyword": "System Error", "required_level": "High"}],
            "gaps_and_strategy": [{"category": "Error", "strategy": f"Details: {str(e)}", "criticality": "Critical"}]
        }

# ==========================================
# PDF Generation Function
# ==========================================
def generate_pdf_report(report_data):
    from fpdf import FPDF
    
    def safe_text(text):
        # Prevent PDF encoding crashes for weird emojis/symbols
        return str(text).encode('latin-1', 'replace').decode('latin-1')

    pdf = FPDF()
    pdf.add_page()
    
    # Header
    pdf.set_font("Arial", 'B', 22)
    pdf.set_text_color(110, 40, 217) # Brand purple
    pdf.cell(0, 15, "BK.ai ATS Evaluation Report", ln=True, align='C')
    pdf.ln(5)
    
    # Score
    pdf.set_font("Arial", 'B', 16)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 10, f"Overall ATS Match Score: {report_data.get('ats_score', 0)}%", ln=True)
    pdf.ln(5)
    
    # Critical Keywords
    pdf.set_font("Arial", 'B', 14)
    pdf.set_text_color(217, 70, 239)
    pdf.cell(0, 10, "CRITICAL KEYWORDS", ln=True)
    
    pdf.set_font("Arial", '', 12)
    pdf.set_text_color(50, 50, 50)
    for kw in report_data.get('critical_keywords', []):
        k = safe_text(kw.get('keyword', 'N/A'))
        r = safe_text(kw.get('required_level', 'Unknown').upper())
        pdf.cell(0, 8, f"* {k} (Required: {r})", ln=True)
    pdf.ln(5)
    
    # Strategy & Gaps
    pdf.set_font("Arial", 'B', 14)
    pdf.set_text_color(217, 70, 239)
    pdf.cell(0, 10, "ACTIONABLE STRATEGY & GAPS", ln=True)
    
    for gap in report_data.get('gaps_and_strategy', []):
        cat = safe_text(gap.get('category', 'Detail').upper())
        crit = safe_text(gap.get('criticality', 'Moderate').upper())
        strat = safe_text(gap.get('strategy', ''))
        
        pdf.set_font("Arial", 'B', 12)
        if crit == 'CRITICAL':
            pdf.set_text_color(220, 50, 50) # Red
        else:
            pdf.set_text_color(200, 150, 0) # Orange/Yellow
            
        pdf.cell(0, 8, f"[{crit}] {cat}:", ln=True)
        
        pdf.set_font("Arial", '', 11)
        pdf.set_text_color(50, 50, 50)
        pdf.multi_cell(0, 6, strat)
        pdf.ln(3)

    # Output as bytes for Streamlit downloader
    try:
        return pdf.output(dest="S").encode("latin-1")
    except Exception:
        return bytes(pdf.output())

# ==========================================
# Database Setup & Session Memory
# ==========================================
@st.cache_resource
def init_supabase():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

supabase = init_supabase()

if 'user' not in st.session_state:
    st.session_state.user = None

# Store the report data in session state so it persists during downloads
if 'report_data' not in st.session_state:
    st.session_state.report_data = None

# ==========================================
# Sidebar System (The Bouncer)
# ==========================================
with st.sidebar:
    st.markdown('<div class="sidebar-title">BK.ai</div>', unsafe_allow_html=True)
    st.caption("v2.1.0 | Enterprise Edition")
    st.divider()
    
    if st.session_state.user is None:
        st.markdown("### 🔐 Access Portal")
        auth_email = st.text_input("Email Address")
        auth_password = st.text_input("Password", type="password")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Sign In"):
                try:
                    response = supabase.auth.sign_in_with_password({"email": auth_email, "password": auth_password})
                    st.session_state.user = response.user
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {str(e)}") 
        with col2:
            if st.button("Sign Up"):
                try:
                    response = supabase.auth.sign_up({"email": auth_email, "password": auth_password})
                    st.success("Account created! Please Sign In.")
                except Exception as e:
                    st.error(f"Error: {str(e)}") 
    else:
        st.markdown("### 👤 User Profile")
        st.success(f"Welcome back,\n{st.session_state.user.email}")
        if st.button("Sign Out"):
            st.session_state.user = None
            st.session_state.report_data = None
            supabase.auth.sign_out()
            st.rerun()

    st.divider()
    st.markdown("### 🤝 Support & Contact\n*Engineered by Kalpana*\n* 📧 [Email Me](mailto:kalpanakb1822@gmail.com)\n* 💻 [GitHub Profile](https://github.com/kalpana1822)")

# ==========================================
# Main Application Interface
# ==========================================
def main():
    st.markdown('<div class="app-title-container"><h1 class="main-title">BK.ai</h1></div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="landing-page-hero-container">
        <div class="gradient-text">Unleashing the Power of<br>Artificial Intelligence</div>
        <p class="sub-title">Embracing the Age of Artificial Intelligence. Discover the Boundless Potential and Impact of AI in Every Sphere of Life and elevate your career trajectory.</p>
    </div>
    """, unsafe_allow_html=True)

    if st.session_state.user is None:
        st.warning("🔒 Please Sign In or Sign Up using the sidebar menu to access the AI Strategist.")
    
    if st.session_state.user is not None:
        st.markdown('<h2 class="section-header" style="text-align: center; display: block; margin-top: 4rem;">Optimize Your Strategy</h2>', unsafe_allow_html=True)
        
        # Input Section
        with st.container():
            input_container, _ = st.columns([1.5, 0.5])
            with input_container:
                st.markdown('<div style="text-align: center; margin-bottom: 2rem;"><h3 class="card-title" style="font-size: 2rem;">Analyze Your Application</h3><p class="card-description">Submit your target job description and your resume for a zero-shot AI evaluation.</p></div>', unsafe_allow_html=True)
                
                jd_input = st.text_area("TARGET JOB DESCRIPTION", placeholder="Paste the Job Description here...", height=200, key="jd_text_area", label_visibility="collapsed")
                
                col_file, _ = st.columns([2, 1])
                with col_file:
                    st.markdown('<br><span class="data-label" style="margin-bottom: 10px; display:block;">UPLOAD RESUME (PDF)</span>', unsafe_allow_html=True)
                    uploaded_pdf = st.file_uploader("", type=["pdf"], key="resume_uploader", label_visibility="collapsed")
                
                st.markdown('<div style="margin-top: 2rem;">', unsafe_allow_html=True)
                analyze_button = st.button("🚀 Generate Report", key="ats_analyze_button")
                st.markdown('</div>', unsafe_allow_html=True)

        if analyze_button and jd_input and uploaded_pdf:
            with st.status("🔮 Intelligent Strategist analyzing details...", expanded=True) as status:
                st.write("🧠 Engaging Gemini AI models...")
                # Save the report to session state so it doesn't clear when download button is clicked
                st.session_state.report_data = generate_ats_report(jd_input, uploaded_pdf)
                status.update(label="Analysis finalized!", state="complete", expanded=False)
            
        if st.session_state.report_data:
            report_data = st.session_state.report_data
            with st.container():
                st.markdown('<h2 class="section-header" style="margin-top: 4rem;">AI Evaluation Report</h2>', unsafe_allow_html=True)
                
                col_score, col_keywords = st.columns([1, 1])
                
                # Render Score Card
                with col_score:
                    score = report_data.get("ats_score", 0)
                    st.markdown(f'''
                    <div class="styled-card" style="text-align: center;">
                        <h3 class="card-title">ATS Match Score</h3>
                        <div class="card-description">Overall performance heuristic.</div>
                        <div style="display: flex; justify-content: center;"><div class="score-circle">{score}%</div></div>
                    </div>
                    ''', unsafe_allow_html=True)
                
                # Render Keywords Card
                with col_keywords:
                    kw_html = '''
                    <div class="styled-card">
                        <h3 class="card-title">Critical Keywords</h3>
                        <div class="card-description">Top skills priority analysis.</div>
                        <div class="mock-panel-group">
                    '''
                    for kw_data in report_data.get("critical_keywords", []):
                        kw_html += f'<div class="data-point"><span class="data-label">{kw_data.get("keyword", "N/A")}</span><span class="data-value">Req: {kw_data.get("required_level", "Unknown").upper()}</span></div>'
                    kw_html += '</div></div>'
                    st.markdown(kw_html, unsafe_allow_html=True)
                
                # Render Strategy Card
                strat_html = '''
                <div class="styled-card">
                    <h3 class="card-title">Actionable Strategy</h3>
                    <div class="card-description">Recommendations to improve your match.</div>
                '''
                for gap in report_data.get("gaps_and_strategy", []):
                    cat = gap.get("category", "Detail").upper()
                    crit = gap.get("criticality", "Moderate")
                    strat = gap.get("strategy", "")
                    strat_html += f'<div class="data-point" style="flex-direction: column; align-items: flex-start; gap: 10px; margin-bottom: 10px;"><div style="display: flex; justify-content: space-between; width: 100%;"><span class="data-label">{cat}</span><span class="criticality-tag {crit.lower()}">{crit}</span></div><span style="color: #a1a1aa; font-size: 0.95rem;">{strat}</span></div>'
                strat_html += '</div>'
                st.markdown(strat_html, unsafe_allow_html=True)

                # Generate the PDF bytes dynamically
                pdf_bytes = generate_pdf_report(report_data)
                
                # Massive Download Button Container
                st.markdown('<div style="margin-top: 3rem; margin-bottom: 3rem;">', unsafe_allow_html=True)
                st.download_button(
                    label="📥 DOWNLOAD REPORT (PDF)",
                    data=pdf_bytes,
                    file_name="ATS_Evaluation_Report.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
                st.markdown('</div>', unsafe_allow_html=True)

        # ==========================================
        # The Pricing Plans
        # ==========================================
        st.markdown('<div style="text-align: center; margin-top: 6rem;"><h2 class="section-header">Discover our pricing plans</h2><p class="card-description">Pick a plan to grow your brand and business</p></div>', unsafe_allow_html=True)
        
        col_p1, col_p2, col_p3 = st.columns([1,1,1])
        
        with col_p1:
            st.markdown('''
            <div class="styled-card">
                <h3 class="card-title">Basic</h3>
                <div class="card-description">Free starter performance tools.</div>
                <div style="font-size: 2.5rem; font-weight: 800; color: #ffffff; margin-bottom: 2rem;">$0<span style="font-size: 1rem; color: #a1a1aa; font-weight: 500;">/mo</span></div>
                <div class="mock-panel-group" style="margin-bottom: 2rem;">
                    <div class="data-point"><span class="data-label">Basic Formatting Checks</span><span class="data-value">Included</span></div>
                    <div class="data-point"><span class="data-label">Monthly ATS Scans</span><span class="data-value">5 Scans</span></div>
                    <div class="data-point"><span class="data-label">Community Support</span><span class="data-value">Included</span></div>
                </div>
            </div>
            ''', unsafe_allow_html=True)
            if st.button("Current Plan", key="btn_basic"):
                st.info("You are currently using the Free Basic tier.")
            
        with col_p2:
            st.markdown('''
            <div class="styled-card" style="border-color: rgba(217, 70, 239, 0.4); box-shadow: 0 0 30px rgba(217, 70, 239, 0.1);">
                <h3 class="card-title">Premium</h3>
                <div class="card-description">Detailed performance analysis.</div>
                <div style="font-size: 2.5rem; font-weight: 800; color: #ffffff; margin-bottom: 2rem;">$9.99<span style="font-size: 1rem; color: #a1a1aa; font-weight: 500;">/mo</span></div>
                <div class="mock-panel-group" style="margin-bottom: 2rem;">
                    <div class="data-point"><span class="data-label">Advanced NLP Analysis</span><span class="data-value">Included</span></div>
                    <div class="data-point"><span class="data-label">Monthly ATS Scans</span><span class="data-value">Unlimited</span></div>
                    <div class="data-point"><span class="data-label">Keyword Prioritization</span><span class="data-value">Included</span></div>
                    <div class="data-point"><span class="data-label">Priority Email Support</span><span class="data-value">Included</span></div>
                </div>
            </div>
            ''', unsafe_allow_html=True)
            if st.button("Upgrade to Premium", key="btn_prem"):
                st.success("Redirecting to secure checkout... 💳")
                st.balloons()
            
        with col_p3:
            st.markdown('''
            <div class="styled-card">
                <h3 class="card-title">Enterprise</h3>
                <div class="card-description">Full structural strategizing.</div>
                <div style="font-size: 2.5rem; font-weight: 800; color: #ffffff; margin-bottom: 2rem;">$99.0<span style="font-size: 1rem; color: #a1a1aa; font-weight: 500;">/mo</span></div>
                <div class="mock-panel-group" style="margin-bottom: 2rem;">
                    <div class="data-point"><span class="data-label">Custom ATS Rulesets</span><span class="data-value">Included</span></div>
                    <div class="data-point"><span class="data-label">API Integration Access</span><span class="data-value">Included</span></div>
                    <div class="data-point"><span class="data-label">Dedicated Account Manager</span><span class="data-value">Included</span></div>
                </div>
            </div>
            ''', unsafe_allow_html=True)
            if st.button("Contact Sales", key="btn_ent"):
                st.toast("Thank you! Our enterprise team will email you shortly.", icon="📩")

    # Footer
    st.markdown('<div style="text-align: center; color: #71717a; padding: 2rem; border-top: 1px solid rgba(255,255,255,0.05); margin-top: 4rem;">© 2026 BK.ai. Engineered by Kalpana.</div>', unsafe_allow_html=True)

if __name__ == '__main__':
    main()
