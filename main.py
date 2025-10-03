
import tempfile
import time
from GmailAutomation.InsertionPipeline.sendEmail import handle_escalation, mark_message_as_read, send_email, send_reply
from GmailAutomation.LLM.EmailAgent import process_email
from GmailAutomation.RetrivalPipeline.schedular import download_attachment, fetch_new_emails, get_gmail_service
from logger import logger



# ------------------------------------------------------------
# Polling Logic
# ------------------------------------------------------------
global last_history_id
no_email_counter = 0  # counts iterations with no new emails
HEARTBEAT_INTERVAL = 20  # how many cycles before logging "still running"


service = get_gmail_service()
logger.info("🚀 Starting Gmail Trigger (poll every 3s)...")

no_email_counter = 0

try:
    while True:
        new_emails = fetch_new_emails(service)
        last_history_id=None
        if new_emails:
            no_email_counter = 0
            logger.info(f"📬 {len(new_emails)} new email(s):")
            for email in new_emails:
                with tempfile.TemporaryDirectory() as tmpdir:
                    attachment_data = []

                    if email["attachments"]:
                        for att in email["attachments"]:
                            file_path = download_attachment(
                                service,
                                message_id=email["id"],
                                attachment_id=att["attachmentId"],
                                filename=att["filename"],
                                save_dir=tmpdir,
                            )
                            attachment_data.append(
                                {
                                    "filename": att["filename"],
                                    "mimeType": att["mimeType"],
                                    "path": file_path,
                                }
                            )
                            logger.info(f"📎 Saved attachment: {file_path}")

                    data = {
                        "Message_ID": email["id"],
                        "From": email["from"],
                        "Subject": email["subject"],
                        "Body": email["body"],
                        "is_important": email["is_important"],
                        "Date": email["date"],
                        "attachment_data": attachment_data,
                    }
                    
                    response = process_email(data)

                logger.info(f"Email data: {data}")
                logger.info(f"🤖 LLM Response: {response}")
                
                if response.get("escalate", False):
                    escalation_email = handle_escalation(
                        response["subject"], response.get("escalation_reason", "No reason provided")
                    )
                    logger.info(f"Escalation email sent: {escalation_email}")
                    mark_message_as_read(service, 'me', response["Message_ID"])
                    logger.info(f"✅ Message {response['Message_ID']} marked as read")
                elif response.get("reply_to", False):
                    result = send_reply(message_id=response["Message_ID"], body=response["response"])
                    logger.info(f"✅ Reply sent successfully in initial email reply !!: {result}")
                    mark_message_as_read(service, 'me', response["Message_ID"]) 
                    logger.info(f"✅ Message {response['Message_ID']} marked as read")
                else:
                    result = send_email(to=response["to_email"], subject=response["subject"], body=response["response"])
                    logger.info(f"✅ Email sent successfully direct to the inbox! : {result}")
                    mark_message_as_read(service, 'me', response["Message_ID"])
                    logger.info(f"✅ Message {response['Message_ID']} marked as read")
                    
        else:
            no_email_counter += 1
            if no_email_counter % HEARTBEAT_INTERVAL == 0:
                logger.info(f"⏱ Still running... no new emails in the last {HEARTBEAT_INTERVAL * 3} seconds")

        time.sleep(3)
except KeyboardInterrupt:
    logger.info("🛑 Gmail Trigger stopped by user")


