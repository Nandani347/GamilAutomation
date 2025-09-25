import os
import base64

from GmailAutomation.auth import get_gmail_service, Credentials
from googleapiclient.discovery import build,Resource
from typing import Any, Dict
from email.mime.text import MIMEText
from GmailAutomation.InsertionPipeline.dummydata import raw


# Initialize the Gmail service
service = get_gmail_service()

# Type alias for the Gmail service
GmailService = Resource

DEFAULT_USER_ID = "me"
EMAIL_PREVIEW_LENGTH = 200  # Number of characters to show in the preview

# ------------------------------------------------------------
# Gmail API Setup
# ------------------------------------------------------------
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

def get_gmail_service():
    if not os.path.exists("token.json"):
        raise Exception("⚠️ Missing token.json. Run Gmail OAuth flow first.")
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    return build("gmail", "v1", credentials=creds)

def gmail_send_email(
    service: GmailService,
    sender: str,
    to: str,
    subject: str,
    body: str,
    user_id: str = DEFAULT_USER_ID,
) -> Dict[str, Any]:
    """
    Compose and send an email.

    Args:
        service: Gmail API service instance
        sender: Email sender
        to: Email recipient
        subject: Email subject
        body: Email body text
        user_id: Gmail user ID (default: 'me')
    
    Returns:
        Sent message object
    """
    message = MIMEText(body)
    message["to"] = to
    message["from"] = sender
    message["subject"] = subject
    
    # Encode to base64url
    encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
    create_message = {"raw": encoded_message}
    
    return service.users().messages().send(userId=user_id, body=create_message).execute()

def send_email(
    to: str, subject: str, body: str
) -> str:
    """
    Compose and send an email.

    Args:
        to: Recipient email address
        subject: Email subject
        body: Email body content
        
    Returns:
        Content of the sent email
    """
    sender = service.users().getProfile(userId=DEFAULT_USER_ID).execute().get("emailAddress")
    message = gmail_send_email(
        service, sender=sender, to=to, subject=subject, body=body, user_id=DEFAULT_USER_ID
    )

    message_id = message.get("id")
    return f"""
            Email sent successfully with ID: {message_id}
            To: {to}
            Subject: {subject}
            Body: {body[:EMAIL_PREVIEW_LENGTH]}{"..." if len(body) > EMAIL_PREVIEW_LENGTH else ""}
            """

def main():
    # Example usage
    data=raw
    if data['esclate']==False: 
         
        result=send_email(
            to=data['to_email'],
            subject=data['subject'],
            body=data['response']
            )
        print("📤 Email sent successfully!")
        print(result)
    else:
        escalation_body=f"""
        Hello Team,

        The following email requires your immediate attention:

        Subject: {data['subject']}
        Reason for Escalation: {data['esclation_reason']}
        
        Please address this issue as soon as possible.

        Best regards,
        Automated Email System
        """
        print("⚠️ Escalation required. Sending to support team.")
        print(escalation_body)
    
if __name__ == "__main__":
    main()