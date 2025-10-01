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
    
def fetch_client_and_project_data(client_id: str) -> dict:
    """
    Fetch key client and project context for the LLM agent.
    Returns minimal structured data.
    """

    if not client_id:
        raise ValueError("client_id is required")

    # ---- Fetch client ----
    client_result = supabase.table("clients") \
        .select("id, name, industry, contact_name, contact_email, priority_level, client_notes") \
        .eq("id", client_id) \
        .limit(1) \
        .execute()

    if not client_result.data or len(client_result.data) == 0:
        return {}

    client = client_result.data[0]

    # ---- Fetch related projects ----
    project_result = supabase.table("projects") \
        .select("id, name, description, billing_type, start_date, end_date, budget, status, client_goal, success_metric") \
        .eq("client_id", client_id) \
        .execute()

    projects = project_result.data if project_result.data else []

    # ---- Prepare compact response ----
    return {
        "client": {
            "id": client.get("id"),
            "name": client.get("name"),
            "industry": client.get("industry"),
            "contact_name": client.get("contact_name"),
            "contact_email": client.get("contact_email"),
            "priority_level": client.get("priority_level"),
            "notes": client.get("client_notes"),
        },
        "projects": [
            {
                "id": p.get("id"),
                "name": p.get("name"),
                "description": p.get("description"),                
                "goal": p.get("client_goal"),
                "success_metric": p.get("success_metric"),
            }
            for p in projects
        ]
    }

# if __name__ == "__main__":
    
#     data=fetch_client_and_project_data(client_id="1ad1e31e-11ca-4342-84bb-eec461585c05")
#     print(data) 
    
    # settings=fetch_personality_settings(user_id="0b669362-6720-47df-a788-d4094e1cfade")
    # print(f"📥 Personality settings from Supabase: {settings}")
    
    # client_emails = fetch_client_emails()
    # print("📥 Client emails from Supabase:")
    # for email in client_emails:
    #     print(" -", email)
