import google.generativeai as genai

# Configure Gemini API
api_key = "AIzaSyChGsei10lH9hnMw1eAdOGmrHtctyS5Ox0"
genai.configure(api_key=api_key)

print("Testing Gemini API...")
print(f"API Key: {api_key[:20]}...")

try:
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    prompt = """
    You are a professional outreach assistant. 
    Write a short, non-spammy, and helpful opening line for a cold email to a clinic.
    
    Clinic Name: New York Dental Clinic
    Contact Name: Dr. Smith
    Website Context: Professional dental clinic
    
    The goal is to sound human and genuinely interested in their clinic. 
    Return ONLY the opening line.
    """
    
    print("\nSending request to Gemini...")
    response = model.generate_content(prompt)
    
    print("\n✅ SUCCESS! Gemini API is working")
    print(f"\nGenerated content:\n{response.text}")
    
except Exception as e:
    print(f"\n❌ ERROR: {type(e).__name__}")
    print(f"Message: {str(e)}")
    import traceback
    traceback.print_exc()
