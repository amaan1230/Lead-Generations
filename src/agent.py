import google.generativeai as genai
import streamlit as st
from src.database import Lead, LeadStatus, get_session

def generate_personalized_email(lead_name, clinic_name, website_description=None):
    """Generate personalized email opening using Gemini AI with fallback"""
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = f"""
        You are a professional outreach assistant. 
        Write a short, non-spammy, and helpful opening line for a cold email to a clinic.
        
        Clinic Name: {clinic_name}
        Contact Name: {lead_name if lead_name else "there"}
        Website Context: {website_description if website_description else "Professional clinic"}
        
        The goal is to sound human and genuinely interested in their clinic. 
        Return ONLY the opening line.
        """
        
        response = model.generate_content(prompt)
        generated_text = response.text.strip()
        print(f"✅ Gemini AI generated: {generated_text[:50]}...")
        return generated_text
        
    except Exception as e:
        error_msg = str(e)
        print(f"⚠️ Gemini API Error: {error_msg}")
        
        # Fallback to template-based personalization
        fallback = f"Hi {lead_name if lead_name else 'there'}, I came across {clinic_name} and was impressed by your work."
        print(f"📝 Using fallback: {fallback}")
        return fallback

def get_email_body(lead, custom_opening):
    """Generate complete email body"""
    return f"""
    {custom_opening}

    I'm reaching out because we help clinics like {lead.clinic_name} streamline their patient onboarding process. 
    I noticed your website and thought our solution could be a great fit.

    Would you be open to a 5-minute chat next week?

    Best regards,
    [Your Name]
    """
