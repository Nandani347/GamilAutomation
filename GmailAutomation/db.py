from supabase import Client, create_client
from dotenv import load_dotenv
import os

load_dotenv()  # take environment variables from .env.

# ---------------------------
# Config
# ---------------------------
SUPABASE_URL = os.getenv("SUPABASE_URL")  # "https://iqeczjgesbyskcyrpyob.supabase.co"
SUPABASE_KEY = os.getenv("SUPABASE_KEY")  # "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImlxZWN6amdlc2J5c2tjeXJweW9iIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MzQyOTk3OSwiZXhwIjoyMDY5MDA1OTc5fQ.J8-SzxPV748ZzmXAdlzHMsfif2lCxtMx5mfLGHkqVRQ"

if not SUPABASE_URL or not SUPABASE_KEY:
    raise Exception("⚠️ Please set SUPABASE_URL and SUPABASE_KEY environment variables")

# ---------------------------
# Supabase Setup
# ---------------------------
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


def fetch_client_emails():
    """Fetch client emails from Supabase table 'clients'."""
    data = supabase.table("clients").select("contact_email").execute()
    emails = [row["contact_email"] for row in data.data]
    return emails

# ----------------------------
# Tool function
# ----------------------------
def fetch_personality_settings(user_id: str = None, client_id: str = None) -> dict:
    """
    Fetch essential personality settings for LLM agent use.

    Returns only the key fields needed to guide responses.
    """
    if not user_id and not client_id:
        raise ValueError("At least one of user_id or client_id must be provided")

    query = supabase.table("ai_personality_settings").select("*")

    if user_id:
        query = query.eq("user_id", user_id)
    if client_id:
        query = query.eq("client_id", client_id)

    result = query.limit(1).execute()

    if result.data and len(result.data) > 0:
        data = result.data[0]
        # Only the most important fields for LLM response shaping
        personality_settings = {
            "assistant_name": data.get("assistant_name"),
            "communication_tone": data.get("communication_tone"),
            "default_greeting": data.get("default_greeting"),
            "followup_message": data.get("followup_message"),
            "sentiment_analysis": data.get("sentiment_analysis"),
            "automatic_escalation": data.get("automatic_escalation"),
            "formality_level": data.get("formality_level"),
            "language_style": data.get("language_style"),
        }
        return personality_settings
    else:
        return {}  # No data found

# if __name__ == "__main__":
    
    
    # settings=fetch_personality_settings(user_id="0b669362-6720-47df-a788-d4094e1cfade")
    # print(f"📥 Personality settings from Supabase: {settings}")
    
    # client_emails = fetch_client_emails()
    # print("📥 Client emails from Supabase:")
    # for email in client_emails:
    #     print(" -", email)
