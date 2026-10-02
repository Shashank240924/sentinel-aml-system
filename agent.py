import google.generativeai as genai
import os

# --- CONFIGURATION ---
# 🔑 PASTE YOUR API KEY HERE (Keep the quotes!)
GEMINI_API_KEY = "AIzaSyDVY2LkvKht3ACAnaza5EsDteTM8HDYtE0" 
genai.configure(api_key=GEMINI_API_KEY)

def get_available_model():
    """
    Automatically finds a working model to prevent '404 Not Found' errors.
    """
    try:
        # Ask Google which models are available to you
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        
        # Priority: Flash (Fastest) -> Pro (Smarter) -> Standard
        preferences = [
            'models/gemini-1.5-flash',      
            'models/gemini-1.5-flash-001',
            'models/gemini-1.5-pro',
            'models/gemini-pro'
        ]
        
        for pref in preferences:
            if pref in models:
                print(f"[INFO] Using AI Model: {pref}")
                return genai.GenerativeModel(pref)
        
        # Fallback to whatever is available
        if models:
            return genai.GenerativeModel(models[0])
            
    except Exception as e:
        print(f"[ERROR] Connection failed: {e}")
    
    # Last resort (blind guess)
    return genai.GenerativeModel('gemini-1.5-flash')

# Initialize model once
model = get_available_model()

def generate_investigation_report(txn_data, risk_factors):
    """
    Generates a simple, clear narrative using Google Gemini.
    """
    # --- UPDATED PROMPT FOR SIMPLE LANGUAGE ---
    prompt = f"""
    You are an AI assistant helping a bank manager. Write a short explanation for a suspicious transaction.
    
    Transaction Details:
    - ID: {txn_data['txn_id']}
    - Amount: ${txn_data['amount']:,.2f}
    - Risk Score: {txn_data['total_risk']:.2f}
    
    Why it was flagged:
    {risk_factors}
    
    Instructions:
    1. Start with "INVESTIGATION SUMMARY:".
    2. Write one clear paragraph (3-4 sentences).
    3. Use simple, easy-to-understand language. Avoid complex legal jargon.
    4. Clearly state what looks wrong (e.g., "The money is moving in a circle" or "This amount is unusually high").
    5. End with a simple recommendation like "We should freeze this account."
    """
    
    try:
        # Generate response
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"AI Agent is offline. Please review manually. (Error: {str(e)})"

if __name__ == "__main__":
    print("Agent online. Ready to generate simple reports.")