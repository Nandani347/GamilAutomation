import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Dict
from mcp.server.fastmcp import Context



def create_message(sender: str, to: str, subject: str, body: str) -> Dict:
    """Create a MIME message for email sending.
    
    Args:
        sender: The email address of the sender
        to: The email address of the recipient
        subject: The subject line of the email
        message_text: The body text of the email
        
    Returns:
        Dict: A dictionary containing the raw message in base64url encoded format
    """
    print(f"Creating email message from {sender} to {to} with subject: {subject}")
    try:
        msg = MIMEMultipart()
        msg['to'] = to
        msg['from'] = sender
        msg['subject'] = subject
        msg.attach(MIMEText(body))
        raw_message = base64.urlsafe_b64encode(msg.as_bytes()).decode()
        print("Email message created successfully")
        return {'raw': raw_message}
    except Exception as e:
        print(f"Error creating email message: {e}", exc_info=True)
        raise
    
def send_email(to: str, subject: str, body: str, ctx: Context = None) -> Dict:
    """Send an email message.
    
    Args:
        to: Recipient's email address
        subject: Email subject line
        message_text: Body text of the email
        ctx: FastMCP context object containing Gmail service
        
    Returns:
        Dict: Dictionary containing:
            - messageId: ID of the sent message
            - threadId: ID of the message thread
            - status: Status message
            
    Example:
        >>> send_email(to='user@example.com', 
        ...             subject='Test', 
        ...             message_text='Hello')
        {'messageId': '...', 'threadId': '...', 'status': 'Email sent successfully'}
    """
    print(f"Sending email to: {to}, subject: {subject}")
    service = ctx.request_context.lifespan_context.gmail_service
    user = ctx.request_context.lifespan_context.user_id

    try:
        msg = create_message(user, to, subject, body)
        sent = service.users().messages().send(userId=user, body=msg).execute()
        
        print(f"Email sent successfully to {to}, message ID: {sent['id']}")
        return {
            'messageId': sent['id'],
            'threadId': sent['threadId'],
            'status': 'Email sent successfully'
        }
    except Exception as e:
        print(f"Failed to send email to {to}: {e}", exc_info=True)
        return {
            'messageId': None,
            'threadId': None,
            'status': f'Failed to send email: {str(e)}'
        }
        
        
def reply_email(message_id: str, reply_body: str, ctx: Context = None) -> Dict:
    
    """Reply to an existing email message.
    
    Args:
        message_id: ID of the message to reply to
        reply_text: Text content of the reply
        ctx: FastMCP context object containing Gmail service
        
    Returns:
        Dict: Dictionary containing:
            - messageId: ID of the reply message
            - threadId: ID of the message thread
            - status: Status message
            - inReplyTo: ID of the original message
            
    Example:
        >>> reply_to_message(message_id='123', reply_text='Thank you')
        {'messageId': '...', 'threadId': '...', 'status': 'Reply sent', 'inReplyTo': '123'}
    """
    print(f"Replying to email with ID: {message_id}")
    service = ctx.request_context.lifespan_context.gmail_service
    user = ctx.request_context.lifespan_context.user_id

    try:
        original = service.users().messages().get(userId=user, id=message_id, format='full').execute()
        headers = original['payload']['headers']
        subject = next((h['value'] for h in headers if h['name'].lower() == 'subject'), '')
        sender = next((h['value'] for h in headers if h['name'].lower() == 'from'), '')
        
        print(f"Original email - From: {sender}, Subject: {subject}")

        reply_subject = subject if subject.startswith("Re:") else f"Re: {subject}"
        reply_msg = create_message(user, sender, reply_subject, reply_body)

        sent = service.users().messages().send(userId=user, body=reply_msg).execute()
        
        print(f"Reply sent successfully to {sender}, message ID: {sent['id']}")
        return {
            'messageId': sent['id'],
            'threadId': sent['threadId'],
            'status': 'Reply sent',
            'inReplyTo': message_id
        }
    except Exception as e:
        print(f"Failed to reply to email {message_id}: {e}", exc_info=True)
        return {
            'messageId': None,
            'threadId': None,
            'status': f'Failed to send reply: {str(e)}',
            'inReplyTo': message_id
        }
        

def main():
    # Example usage
    data={
    'query': 'This database issue is still not solved',
    'response': 'We have fix this issue currently server is geting restart try after some time you will get results.',
    'subject': 'Re: Database issue',
    'esclation_reason': 'Database is critical part in production at time of retrival',
    'esclate': True,
    'to_email': 'vishva355.rejoice@gmail.com'
    }
    send_email(
        to=data['to_email'],
        subject=data['subject'],
        body=data['response']
        )
    print("📤 Email sent successfully!")
    
if __name__ == "__main__":
    main()        
   