import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any, Dict
from googleapiclient.discovery import Resource
from GmailAutomation.auth import get_gmail_service
from logger import logger

DEFAULT_USER_ID = "me"
EMAIL_PREVIEW_LENGTH = 500  # Number of characters to show in preview

# Initialize Gmail service
service: Resource = get_gmail_service()

def create_mime_message(sender: str, to: str, subject: str, body: str) -> Dict[str, Any]:
    """Create a MIME message for sending via Gmail API"""
    msg = MIMEMultipart()
    msg["to"] = to
    msg["from"] = sender
    msg["subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    raw_message = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    return {"raw": raw_message}

def create_reply_message(service: Resource, user_id: str, message_id: str, body: str) -> Dict[str, Any]:
    """Create a reply to an existing email"""
    original = service.users().messages().get(userId=user_id, id=message_id, format="full").execute()
    thread_id = original["threadId"]

    headers = original["payload"]["headers"]
    subject = next((h["value"] for h in headers if h["name"].lower() == "subject"), "")
    sender_email = next((h["value"] for h in headers if h["name"].lower() == "from"), "")
    msg_id_header = next((h["value"] for h in headers if h["name"].lower() == "message-id"), None)

    reply_subject = subject if subject.lower().startswith("re:") else f"Re: {subject}"

    message = MIMEText(body, "plain")
    message["to"] = sender_email
    message["from"] = service.users().getProfile(userId=user_id).execute().get("emailAddress")
    message["subject"] = reply_subject
    if msg_id_header:
        message["In-Reply-To"] = msg_id_header
        message["References"] = msg_id_header

    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
    return {"raw": raw_message, "threadId": thread_id}

def send_email(to: str, subject: str, body: str) -> str:
    """Send a direct email"""
    sender = service.users().getProfile(userId=DEFAULT_USER_ID).execute().get("emailAddress")
    message = create_mime_message(sender, to, subject, body)
    sent = service.users().messages().send(userId=DEFAULT_USER_ID, body=message).execute()

    return f"""
Message ID: {sent.get("id")}
To: {to}
Subject: {subject}
Body: {body[:EMAIL_PREVIEW_LENGTH]}{"..." if len(body) > EMAIL_PREVIEW_LENGTH else ""}
"""

def send_reply(message_id: str, body: str) -> str:
    """Send a reply to an existing message"""
    reply_msg = create_reply_message(service, DEFAULT_USER_ID, message_id, body)
    sent = service.users().messages().send(userId=DEFAULT_USER_ID, body=reply_msg).execute()

    return f"""
Message ID: {message_id}
Thread ID: {sent.get("id")}
Body: {body[:EMAIL_PREVIEW_LENGTH]}{"..." if len(body) > EMAIL_PREVIEW_LENGTH else ""}
"""

def handle_escalation(subject: str, reason: str) -> str:
    """Generate escalation email body"""
    escalation_body = f"""
Escalation Draft:
Subject: {subject}
Reason: {reason}
Please address this issue as soon as possible.
Automated Email System
"""
    return escalation_body

def mark_message_as_read(service, user_id: str, message_id: str):
    """
    Remove the UNREAD label from a message.
    """
    try:
        service.users().messages().modify(
            userId=user_id,
            id=message_id,
            body={'removeLabelIds': ['UNREAD']}
        ).execute()
    except Exception as e:
        logger.error(f"Failed to mark message as read: {e}")
        
        
# raw={'Message_ID': '199a899d4f0f2e00', 'query': '"Hello"', 'escalate': False, 'priority': '', 'escalation_reason': '', 'response': 'Hello, Thanks you!', 'subject': 'Re: Test', 'to_email': 'xyz@gmail.com', 'reply_to': False}        
# result=send_email(to=raw["to_email"], subject=raw["subject"], body=raw["response"])
# print(result)
