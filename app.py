import streamlit as st
import time
from supabase import create_client, Client
import json
import plotly.graph_objects as go # New import for the Flex

# ... [Keep your CSS style block exactly the same as before] ...
# (I am omitting the style block here to save space, but DO NOT delete it from your file!)

def generate_ats_report(jd_text, pdf_file):
    import PyPDF2
    from google import genai
    
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    resume_text = ""
    for page in pdf_reader.pages:
        page_text = page.extract_text()
        if page_text:
            resume_text += page_text + "\n"

    client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

    # We added 'skill_scores' to the JSON structure for the chart!
    prompt = f"""
    You are an expert ATS analyst. Analyze the Resume against the Job Description.
    Resume: {resume_text}
    Job Description: {jd_text}
    
    Return ONLY a raw, valid JSON object with this exact structure:
    {{
        "ats_score": 85,
        "skill_scores": {{"Python": 90, "DBMS": 75, "Communication": 80, "Problem Solving": 85, "MS Office": 60}},
        "critical_keywords": [{{"keyword": "Python", "required_level": "High"}}],
        "gaps_and_strategy": [{{"category": "Gap", "strategy": "Improve project metrics", "criticality": "High"}}]
    }}
    """
    
    try:
        response = client.models.generate_content(model='gemini-2.5-flash', contents=prompt)
        return json.loads(response.text.replace('```json', '').replace('```', '').strip())
    except:
        return {"ats_score": 0, "skill_scores": {}, "critical_keywords": [], "gaps_and_strategy": []}

# ... [Keep your init_supabase and Sidebar/Bouncer code exactly the same] ...

# ==========================================
# The "Flex" Visualization Engine
# ==========================================
def render_radar_chart(skill_scores):
    categories = list(skill_scores.keys())
    values = list(skill_scores.values())
    
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(r=values, theta=categories, fill='toself', line_color='#d946ef'))
    
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        showlegend=False,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color="white"
    )
    st.plotly_chart(fig, use_container_width=True)

# ... [In your main() function, update the Evaluation Report section] ...
        if analyze_button and jd_input and uploaded_pdf:
            # ... (keep the status spinner code) ...
            
            with report_container.container():
                st.markdown('<h2 class="section-header">AI Evaluation Report</h2>', unsafe_allow_html=True)
                
                # Flex: Show the Radar Chart!
                st.markdown('<h3 class="card-title">Skill Proficiency Mapping</h3>', unsafe_allow_html=True)
                render_radar_chart(report_data.get("skill_scores", {}))
                
                # ... (keep your existing ATS Score and Keywords columns below this) ...
