import streamlit as st
import time
from supabase import create_client, Client
import json
import plotly.graph_objects as go 

# ... [Keep your existing CSS/Style block at the top] ...

# ==========================================
# Real AI Brain: Google Gemini Integration
# ==========================================
def generate_ats_report(jd_text, pdf_file):
    import PyPDF2
    from google import genai
    
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    resume_text = ""
    for page in pdf_reader.pages:
        if page.extract_text(): resume_text += page.extract_text() + "\n"

    client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

    prompt = f"""
    Analyze this Resume vs JD. Return ONLY valid JSON:
    {{
        "ats_score": 85,
        "skill_scores": {{"Python": 90, "DBMS": 75, "Communication": 80, "Problem Solving": 85, "MS Office": 60}},
        "critical_keywords": [{{"keyword": "Python", "required_level": "High"}}],
        "gaps_and_strategy": [{{"category": "Gap", "strategy": "Improve metrics", "criticality": "High"}}]
    }}
    Resume: {resume_text}
    JD: {jd_text}
    """
    
    response = client.models.generate_content(model='gemini-2.0-flash', contents=prompt)
    return json.loads(response.text.replace('```json', '').replace('```', '').strip())

# ==========================================
# Flex Visualization
# ==========================================
def render_radar_chart(skill_scores):
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=list(skill_scores.values()),
        theta=list(skill_scores.keys()),
        fill='toself', line_color='#d946ef'
    ))
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        paper_bgcolor='rgba(0,0,0,0)',
        font_color="white"
    )
    st.plotly_chart(fig, use_container_width=True)

# ... [Keep your init_supabase and Sidebar code exactly as you had it] ...

# ==========================================
# Main Interface
# ==========================================
def main():
    st.markdown('<h1 class="main-title">BK.ai</h1>', unsafe_allow_html=True)
    
    if st.session_state.user is None:
        st.warning("🔒 Sign in to access the strategist.")
        return

    jd_input = st.text_area("TARGET JOB DESCRIPTION", height=150)
    uploaded_pdf = st.file_uploader("UPLOAD RESUME (PDF)", type=["pdf"])
    
    if st.button("🚀 Generate Report"):
        with st.status("Analyzing..."):
            report = generate_ats_report(jd_input, uploaded_pdf)
            
        st.markdown('<h2 class="section-header">AI Evaluation Report</h2>', unsafe_allow_html=True)
        
        # Grid layout for the report
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown('<div class="styled-card">', unsafe_allow_html=True)
            st.markdown('### Skill Proficiency Mapping')
            render_radar_chart(report.get("skill_scores", {}))
            st.markdown('</div>', unsafe_allow_html=True)
            
        with col2:
            st.markdown(f'''
            <div class="styled-card">
                <h3>ATS Match Score</h3>
                <div class="score-circle">{report.get("ats_score", 0)}%</div>
            </div>
            ''', unsafe_allow_html=True)

        # Strategy Section
        st.markdown('<h3 class="card-title">Actionable Strategy</h3>', unsafe_allow_html=True)
        for gap in report.get("gaps_and_strategy", []):
            st.markdown(f'''
            <div class="styled-card">
                <span class="criticality-tag {gap.get("criticality", "Moderate").lower()}">{gap.get("criticality")}</span>
                <p>{gap.get("strategy")}</p>
            </div>
            ''', unsafe_allow_html=True)

    # ... [Keep your Pricing Plans section at the bottom] ...
