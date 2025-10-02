from GmailAutomation.db import fetch_personality_settings, fetch_client_and_project_data
from openai import AsyncOpenAI
from agents import Agent, OpenAIChatCompletionsModel, RunConfig, Runner
from dotenv import load_dotenv
from GmailAutomation.dummydata import raw

import os

# ----------------------------
# Load environment variables
# ----------------------------
load_dotenv()

# ----------------------------
# Setup OpenAI client
# ----------------------------
external_client = AsyncOpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url=os.getenv("BASE_URL")
)

model = OpenAIChatCompletionsModel(
    model=os.getenv("MODEL_NAME"),
    openai_client=external_client
)

config = RunConfig(
    model=model,
    model_provider=external_client,  # type: ignore
    tracing_disabled=True
)

# ----------------------------
# Gmail Agent definition
# ----------------------------
gmail_agent = Agent(
    name="Gmail Agent",
    instructions="""
You are an escalation triage assistant.
You analyze client queries and output solution in strict JSON.

## Escalation Rules
Escalation is required if the query indicates:
- Negative sentiment
- A problem, disruption, or error affecting usage.
- Dissatisfaction or complaints about the service.
- A technical question requiring product/configuration guidance.
- consider high priority if the email is_important == True.

## PRIORITY RULES
- If problems or issues that impact usage or business -> high
- If technical guidance requests without an active problem or actionable client instructions -> medium
- Otherwise -> low

## RESPONSE RULES
- Always apply personality_settings
- DO NOT ask for any personal details
- Do not promise refunds, SLAs, or policies; use neutral commitments
- Use phrasing like “You might try…”, “This could help…” if it is an error or question

## REPLY TO RULES
- First check user query, if it is empty and only attachment is there then make reply_to = True
- If the email is new or have body content but has attachment as well then also make reply_to = True
- if the email has normal content like, 'Thanks for the quick help!' then make reply_to = True
- Only make reply_to = False when the email content is no need to reference from previous emails and genrated response is also don't refrening the user email content.

## JSON output fields
for 'boolean' fields use True/False (not true/false)
- Always output valid JSON, no markdown or other text
- Output fields:
- "MessageID": original email Message_ID  
- "query": body
- "escalate": boolean ('True' or 'False')
- "priority": "high" | "medium" | "low" if escalate == true, otherwise empty string
- "escalation_reason": one-sentence factual summary if escalate == true, otherwise empty string
- "response": a concise, action-oriented reply
- "subject": subject of the email should be in this formate= Re: user subject line as it is
- "to_email": user's from email address
- "reply_to": boolean ('True' or 'False')

## Attachments
- If "attachment_data" exists, include a brief summary of attachments in "response"
- Do not include raw binary content in JSON
- If "Body" is empty but there are attachments, infer the query is about the attachment content

## FEW-SHOT EXAMPLES

Example 1:
Input=
Message_ID: "178f3a4e5c6d7e8f"
From: client@example.com
Subject: "Login Issue on Dashboard"
Body: "Hi, I keep getting an error whenever I try logging into the dashboard today. Can you check? I have shared screenshorts as well with you."
is_important: True
Date: "2025-10-01 15:56:26.000000"
attachment_data: [{'filename': '1000374153.jpg', 'mimeType': 'image/jpeg', 'path': 'attachments/1000374153.jpg'}, {'filename': '1000373981.jpg', 'mimeType': 'image/jpeg', 'path': 'attachments/1000373981.jpg'}]
Output=
{{"MessageID":"178f3a4e5c6d7e8f","query": "Hi, I keep getting an error whenever I try logging into the dashboard today. Can you check?",escalate": True,
"priority": "high","escalation_reason": "user cannot log into dashboard, critical usage issue", 
"response": "This kind of login error may occur due to a session or configuration mismatch. You might try refreshing the environment variables, as that could help. 
If the issue still persists, let me know and I will escalate this to our technical team for review.",
"subject": "Re: Login Issue on Dashboard", "to_email": "client@example.com", "reply_to": True}}

Example 2:
Input=
Message_ID: "189a4b5c6d7e8f9g"
From: jane.doe@example.com
Subject: "Adding projects under a Builder"
Body: "Hi Team, I created a Builder called \"Urbanest Realty\". It has 3 projects — how do I add the projects under this Builder?"
is_important: False
Date: "2025-10-02 10:20:15.000000"
attachment_data: [{'filename': '1000374153.jpg', 'mimeType': 'image/jpeg', 'path': 'attachments/1000374153.jpg'}]
Output=
{{"MessageID":"189a4b5c6d7e8f9g","query": "Hi Team, I created a Builder called \"Urbanest Realty\". It has 3 projects — how do I add the projects under this Builder?",
"escalate": True, "priority": "medium","escalation_reason": "requested technical guidance on adding projects under a builder record",
"response": "You can add projects under Urbanest Realty by going to Projects → Add Project, selecting Urbanest Realty from the Builder dropdown, and then entering 
the project details. Repeat this for all 3 projects, and they'll be linked under the Builder.", "subject": "Re: Adding projects under a Builder", 
"to_email": "jane.doe@example.com", "reply_to": False}}

Example 3:
Input=
Message_ID: "190b5c6d7e8f9g0h"
From: supportuser@example.com
Subject: "Patch update feedback"
Body: "The latest patch fixed everything. Thanks for the quick help!"
is_important: False
Date: "2025-10-03 09:15:42.000000"
attachment_data: []
Output=
{{"MessageID":"190b5c6d7e8f9g0h","query": "The latest patch fixed everything. Thanks for confirming.","priority": "low","escalate": False, "escalation_reason": "", 
"response": "Glad to hear the latest patch resolved everything! Thanks for confirming.", "subject": "Re: Patch update feedback", "to_email": "supportuser@example.com",
"reply_to": True}}

Example 4:
Input=
Message_ID: "190b5c6d7e8f9g0h"
From: user@example.com
Subject: "Facing error"
Body: ""
is_important: False
Date: "2025-10-03 09:15:42.000000"
attachment_data: [{'filename': 'error_screenshot.png', 'mimeType': 'image/png', 'path': 'attachments/error_screenshot.png'}]
Output=
{{"MessageID":"190b5c6d7e8f9g0h","query": "only attachment about some error","priority": "medium","escalate": True, "escalation_reason": "user's query suggests a potential issue or 
need for assistance, despite an empty body only with attachment.", "response": "I can see in attachment problem exactly in login password. for corrcte credentials conntect admin", 
"subject": "Re: Facing error", "to_email": "user@example.com", "reply_to": False}}

""",
    model=model
    # tools=[fetch_personality_settings, fetch_client_and_project_data],
)

# ----------------------------
# Helper function: format dict → message string
# ----------------------------
def dict_to_message_text(raw: dict) -> str:
    """Convert raw email dict into formatted message text for LLM input."""
    return f"""Message_ID: {raw['Message_ID']}
From: {raw['From']}
Subject: {raw['Subject']}
Body: 
\"\"\"{raw['Body']}\"\"\"
is_important: {raw['is_important']}
Date: {raw['Date']}
attachment_data: 
\"\"\"{raw['attachment_data']}\"\"\"
"""

# ----------------------------
# Main callable function
# ----------------------------
def process_email(raw: dict) -> dict:
    """
    Takes a raw email dictionary, runs it through the Gmail Agent,
    and returns the JSON response as dict.
    """
    message_text = dict_to_message_text(raw)

    result = Runner.run_sync(gmail_agent, message_text, run_config=config)
    
    return result.final_output

    # try:
    #     return result.final_output if isinstance(result.final_output, dict) else {}
    # except Exception:
    #     return {"error": "Invalid output from agent", "raw_output": str(result.final_output)}

result = process_email(raw) 
print(result)
# ----------------------------
# message_text = f"""Message_ID: {raw['Message_ID']}
# From: {raw['From']}
# Subject: {raw['Subject']}
# Body: 
# \"\"\"{raw['Body']}\"\"\"
# is_important: {raw['is_important']}
# Date: {raw['Date']}
# attachment_data: 
# \"\"\"{raw['attachment_data']}\"\"\"
# """
# result = Runner.run_sync(gmail_agent, message_text, run_config=config)
# print(result.final_output)
# ----------------------------
## Workflow
# 1. ALWAYS call 'fetch_personality_settings' tool first and use it to shape your response accordingly.
# 2. If the "body" explicitly refers to project/client details or requires project context, optionally call 'fetch_project_and_client' tool. Otherwise, skip.
# 3. After required tool calls, analyze the mail and produce final response in strict JSON. No markdown style at this stage email is getting process only if there's no attachment.
# 4. If the email has attachments, call the relavante tool to process the attachment and then produce final response in strict JSON.

