import streamlit as st
import time
from supabase import create_client, Client

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
    
    /* Login Form Inputs */
    [data-testid="stSidebar"] input {
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
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
    }
    .styled-card.input-panel { background: rgba(15, 15, 20, 0.7); padding: 4rem; display: flex; flex-direction: column; align-items: center; }
    
    /* Section Headers */
    h2.section-header { font-size: 2rem; font-weight: 700; color: #ffffff; margin-bottom: 2rem; border-bottom: 2px solid rgba(168, 129, 255, 0.3); display: inline-block; padding-bottom: 0.5rem; }
    h3.card-title { font-size: 1.5rem; font-weight: 600; color: #ffffff; margin-bottom: 1rem; }
    .card-description { font-size: 1rem; color: #a1a1aa; margin-bottom: 2rem; line-height: 1.6; }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #7c3aed 0%, #d946ef 100%) !important;
        border: none !important;
        color: #ffffff !important;
        font-size: 1.1rem !important;
        font-weight: 600 !important;
        border-radius: 12px !important;
    }
    
    /* Data Points */
    .mock-panel-group { display: flex; flex-direction: column; gap: 1rem; }
    .data-point { display: flex; justify-content: space-between; align-items: center; padding: 1rem; background: rgba(0, 0, 0, 0.3); border-radius: 10px; border: 1px solid rgba(255, 255, 255, 0.05); }
    .data-label { font-weight: 500; color: #e0e0e0; font-size: 0.95rem; }
    .data-value { font-weight: 600; color: #ffffff; }
    .score-circle { display: inline-flex; justify-content: center; align-items: center; width: 100px; height: 100px; border-radius: 50%; border: 4px solid #a881ff; font-size: 2.2rem; font-weight: 800; color: #ffffff; box-shadow: 0 0 20px rgba(168, 129, 255, 0.2); }
    .criticality-tag { display: inline-block; padding: 0.4rem 1rem; border-radius: 20px; font-size: 0.8rem; font-weight: 700; text-transform: uppercase; }
    .critical { background: rgba(244, 63, 94, 0.2); color: #fb7185; border: 1px solid rgba(244, 63, 94, 0.3); }
    .moderate { background: rgba(251, 191, 36, 0.2); color: #fcd34d; border: 1px solid rgba(251, 191, 36, 0.3); }
</style>
""", unsafe_allow_html=True)

# Helper function
def render_data_point(label, value, extra_class=""):
    st.markdown(f'<div class="data-point"><span class="data-label">{label}</span><span class="data-value {extra_class}">{value}</span></div>', unsafe_allow_html=True)

# ==========================================
# Real AI Brain: Google Gemini Integration
# ==========================================
def generate_ats_report(jd_text, pdf_file):
    import PyPDF2
    from google import genai
    import json
    
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    resume_text = ""
    for page in pdf_reader.pages:
        page_text = page.extract_text()
        if page_text:
            resume_text += page_text + "\n"

    try:
        client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
    except Exception as e:
        st.error("⚠️ API Key missing.")
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
            "gaps_and_strategy": [{"category": "Error", "strategy": "Please try scanning again.", "criticality": "Critical"}]
        }

# ==========================================
# Database Setup & Session Memory
# ==========================================
# 1. Connect to Supabase
@st.cache_resource
def init_supabase():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

supabase = init_supabase()

# 2. Setup the App's "Memory" for the User
if 'user' not in st.session_state:
    st.session_state.user = None

# ==========================================
# Sidebar System (The Bouncer)
# ==========================================
with st.sidebar:
    st.markdown('<div class="sidebar-title">BK.ai</div>', unsafe_allow_html=True)
    st.caption("v2.1.0 | Enterprise Edition")
    st.divider()
    
    # If the user is NOT logged in, show the login form
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
                    st.rerun() # Refresh the page immediately
                except Exception as e:
                    st.error("Invalid credentials.")
        with col2:
            if st.button("Sign Up"):
                try:
                    response = supabase.auth.sign_up({"email": auth_email, "password": auth_password})
                    st.success("Account created! Please Sign In.")
                except Exception as e:
                    st.error("Error creating account.")
                    
    # If the user IS logged in, show their profile and logout button
    else:
        st.markdown("### 👤 User Profile")
        st.success(f"Welcome back,\n{st.session_state.user.email}")
        if st.button("Sign Out"):
            st.session_state.user = None
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

    # Protect the app: Only show the scanner if the user is logged in
    if st.session_state.user is None:
        st.warning("🔒 Please Sign In or Sign Up using the sidebar menu to access the AI Strategist.")
    
    # If logged in, show the full app!
    if st.session_state.user is not None:
        st.markdown('<h2 class="section-header" style="text-align: center; display: block; margin-top: 4rem;">Optimize Your Strategy</h2>', unsafe_allow_html=True)
        st.markdown('<div class="styled-card-row">', unsafe_allow_html=True)
        
        with st.container():
            input_container, _ = st.columns([1.5, 0.5])
            with input_container:
                st.markdown('<div class="styled-card input-panel">', unsafe_allow_html=True)
                jd_input = st.text_area("TARGET JOB DESCRIPTION", placeholder="Paste the Job Description here...", height=200, key="jd_text_area", label_visibility="collapsed")
                
                col_file, _ = st.columns([2, 1])
                with col_file:
                    st.markdown('<br><span class="data-label" style="margin-bottom: 10px; display:block;">UPLOAD RESUME (PDF)</span>', unsafe_allow_html=True)
                    uploaded_pdf = st.file_uploader("", type=["pdf"], key="resume_uploader", label_visibility="collapsed")
                
                st.markdown('<div style="margin-top: 3rem;">', unsafe_allow_html=True)
                analyze_button = st.button("🚀 Generate Report", key="ats_analyze_button")
                st.markdown('</div></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # Output Section
        report_container = st.empty()
        if analyze_button and jd_input and uploaded_pdf:
            with st.status("🔮 Intelligent Strategist analyzing details...", expanded=True) as status:
                st.write("🧠 Engaging Gemini AI models...")
                report_data = generate_ats_report(jd_input, uploaded_pdf)
                status.update(label="Analysis finalized!", state="complete", expanded=False)
            
            with report_container.container():
                st.markdown('<h2 class="section-header">AI Evaluation Report</h2>', unsafe_allow_html=True)
                st.markdown('<div class="styled-card-row">', unsafe_allow_html=True)
                
                st.markdown('<div class="styled-card">', unsafe_allow_html=True)
                col_score, col_keywords = st.columns([1, 1])
                
                with col_score:
                    st.markdown(f'<h3 class="card-title">ATS Match Score</h3><div class="card-description">Overall performance heuristic.</div><div class="score-circle">{report_data.get("ats_score", 0)}%</div>', unsafe_allow_html=True)
                
                with col_keywords:
                    st.markdown('<h3 class="card-title">Critical Keywords</h3><div class="card-description">Top skills priority analysis.</div><div class="mock-panel-group">', unsafe_allow_html=True)
                    for kw_data in report_data.get("critical_keywords", []):
                        render_data_point(kw_data.get("keyword", "N/A"), f"Req: {kw_data.get('required_level', 'Unknown').upper()}")
                    st.markdown('</div></div>', unsafe_allow_html=True)
                
                st.markdown('<div class="styled-card">', unsafe_allow_html=True)
                st.markdown('<h3 class="card-title">Actionable Strategy</h3><div class="card-description">Recommendations to improve your match.</div>', unsafe_allow_html=True)
                
                for gap in report_data.get("gaps_and_strategy", []):
                    st.markdown(f'<div class="data-point" style="flex-direction: column; align-items: flex-start; gap: 10px; margin-bottom: 10px;"><div style="display: flex; justify-content: space-between; width: 100%;"><span class="data-label">{gap.get("category", "Detail").upper()}</span><span class="criticality-tag {gap.get("criticality", "Moderate").lower()}">{gap.get("criticality", "Moderate")}</span></div><span style="color: #a1a1aa; font-size: 0.95rem;">{gap.get("strategy", "")}</span></div>', unsafe_allow_html=True)
                st.markdown('</div></div>', unsafe_allow_html=True) 

    # Footer
    st.markdown('<div style="text-align: center; color: #71717a; padding: 2rem; border-top: 1px solid rgba(255,255,255,0.05); margin-top: 4rem;">© 2026 BK.ai. Engineered by Kalpana.</div>', unsafe_allow_html=True)

if __name__ == '__main__':
    main()
