import base64
import os
import re
import time

from logger import logger
from datetime import datetime
from googleapiclient.errors import HttpError
from GmailAutomation.db import fetch_client_emails

# ------------------------------------------------------------
# Polling Logic
# ------------------------------------------------------------
last_history_id = None

"""
Symbol Handling Helper if needed in future:
SYMBOL -> Result
& -> &amp;
" -> &quot;
' -> &#39;
\ -> \\
> -> &gt;
< -> &lt;
"""
# ======================
"""
Body Formater:
Feched irrelevant -> replace with
\n>>> -> \n
\n\r -> \n
'   ' -> ' ' (single space)
"""

def fetch_new_emails(service):
    global last_history_id
    try:
        profile = service.users().getProfile(userId="me").execute()
        new_email = profile["emailAddress"]

        if last_history_id is None:
            last_history_id = profile["historyId"]
            logger.info(f"✅ Gmail Trigger initialized for {new_email}, historyId={last_history_id}")
            return []

        history = (
            service.users()
            .history()
            .list(userId="me", startHistoryId=last_history_id, historyTypes=["messageAdded"])
            .execute()
        )

        messages = []
        if "history" in history:
            for record in history["history"]:
                if "messagesAdded" in record:
                    for msg in record["messagesAdded"]:
                        msg_id = msg["message"]["id"]
                        
                        # Fetch client emails once
                        client_emails = fetch_client_emails()
                        
                        full_msg = (
                            service.users()
                            .messages()
                            .get(
                                userId="me",
                                id=msg_id,
                                format="full",
                                metadataHeaders=["Subject", "From", "LabelIds", "Date"],
                            )
                            .execute()
                        )

                        def extract_parts(parts, body="", attachments=None):
                            if attachments is None:
                                attachments = []

                            for part in parts:
                                mime_type = part.get("mimeType", "")
                                part_body = part.get("body", {})

                                # If this part has sub-parts (multipart/*), go deeper
                                if "parts" in part:
                                    body, attachments = extract_parts(part["parts"], body, attachments)
                                else:
                                    # Extract text content
                                    if mime_type == "text/plain" and "data" in part_body:
                                        decoded = base64.urlsafe_b64decode(part_body["data"]).decode(
                                            "utf-8", errors="ignore"
                                        )
                                        decoded = decoded.replace("\r\n", "\n").replace("\r", "\n")
                                        body += decoded

                                    # Collect attachments
                                    if part.get("filename") and "attachmentId" in part_body:
                                        attachments.append(
                                            {
                                                "filename": part["filename"],
                                                "mimeType": mime_type,
                                                "attachmentId": part_body["attachmentId"],
                                            }
                                        )

                            return body, attachments

                        def get_body_from_message(msg):
                            payload = msg["payload"]
                            body = ""
                            attachments = []

                            if "parts" in payload:
                                body, attachments = extract_parts(payload["parts"])

                            else:
                                # Single-part message
                                body = payload["body"].get("data")
                                if body:
                                    body = base64.urlsafe_b64decode(body).decode("utf-8")

                            return body, attachments

                        def clean_body(text):
                            """
                            Cleans Gmail email body:
                            - Normalize newlines (\r\n -> \n)
                            - Remove broken HTML tags
                            - Collapse multiple newlines
                            - Keep replies, but remove repeated quoted headers
                            - Strip spaces
                            """

                            # Normalize newlines
                            text = text.replace("\r\n", "\n").replace("\r", "\n")

                            # Remove broken HTML tags like <\n> or <>
                            text = re.sub(r"<\s*[^>]*>", "", text)

                            lines = text.split("\n")
                            cleaned_lines = []
                            skip_block = False

                            # Patterns that indicate start of previous messages
                            quote_headers = [
                                r"^On .* wrote:$",
                                r"^From: .*",
                                r"^Sent: .*",
                                r"^To: .*",
                                r"^Subject: .*",
                                r"^---+",  # for "---Original Message---"
                            ]

                            for line in lines:
                                line = line.strip()
                                # Check for previous thread headers
                                if any(re.match(p, line) for p in quote_headers):
                                    skip_block = True  # start skipping repeated thread
                                    continue
                                # Skip only lines fully quoted with >
                                if skip_block and re.match(r"^>+", line):
                                    continue
                                # Reset skip if it's normal text after quotes
                                if skip_block and line and not line.startswith(">"):
                                    skip_block = False

                                cleaned_lines.append(line)

                            # Collapse multiple newlines into max 2
                            cleaned_text = "\n".join(cleaned_lines)
                            cleaned_text = re.sub(r"\n{3,}", "\n\n", cleaned_text)
                            cleaned_text = cleaned_text.strip()

                            return cleaned_text

                        subject, sender, date = "", "", ""
                        for header in full_msg["payload"].get("headers", []):
                            if header["name"] == "Subject":
                                subject = header["value"]
                            if header["name"] == "From":
                                sender = re.search(r"<(.*?)>", header["value"])  # Extract the email address
                                if sender:
                                    sender = sender.group(1)  # Get the email from the regex match
                                else:
                                    sender = header["value"]  # Fallback to full value if no angle brackets
                            if header["name"] == "Date":
                                date = header["value"]

                        # Convert the date to the required format (YYYY-MM-DD HH:MM:SS.ssssss)
                        if date:
                            try:
                                # Parse the Gmail date string into a datetime object
                                parsed_date = datetime.strptime(date, "%a, %d %b %Y %H:%M:%S %z")

                                # Convert to the format required by Supabase (YYYY-MM-DD HH:MM:SS.ssssss)
                                formatted_date = (
                                    parsed_date.strftime("%Y-%m-%d %H:%M:%S")
                                    + "."
                                    + str(parsed_date.microsecond).zfill(6)
                                )
                            except ValueError as e:
                                logger.error(f"⚠️ Date parsing error for date '{date}': {e}")
                                formatted_date = None
                        else:
                            formatted_date = None

                        # Check if the email has the "IMPORTANT" label
                        is_important = "IMPORTANT" in full_msg.get("labelIds", [])

                        # Only continue if sender is in client emails
                        if sender not in client_emails:
                            continue  # Skip this email and move to the next one

                        full_msg.get("snippet", "")
                        body, attachments = get_body_from_message(full_msg)
                        messages.append(
                            {
                                "id": msg_id,
                                "from": sender,
                                "subject": subject,
                                "body": clean_body(body),
                                "emailAddress": new_email,
                                "is_important": is_important,
                                "date": formatted_date,
                                "attachments": attachments,
                            }
                        )

        if "historyId" in history:
            last_history_id = history["historyId"]

        return messages

    except HttpError as error:
        logger.error(f"⚠️ Gmail API error: {error}")
        # If rate limit error, wait longer before retrying
        if error.resp.status in [429, 503]:
            logger.warning("⏳ Rate limit hit, waiting 10 seconds...")
            time.sleep(10)
        return []


def download_attachment(service, message_id, attachment_id, filename, save_dir):
    """
    Download attachment from Gmail using attachment ID.
    Returns raw file bytes.
    """
    os.makedirs(save_dir, exist_ok=True)

    attachment = (
        service.users()
        .messages()
        .attachments()
        .get(userId="me", messageId=message_id, id=attachment_id)
        .execute()
    )

    file_data = base64.urlsafe_b64decode(attachment["data"])
    file_path = os.path.join(save_dir, filename)

    # Optionally save
    with open(file_path, "wb") as f:
        f.write(file_data)

    return file_path
