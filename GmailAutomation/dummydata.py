# raw = {
#     'Message_ID': '1999fb8c1e11f668',
#     'From': 'nandaniramoliya@gmail.com',
#     'Subject': 'Getting Error',
#     'Body': 'Hello I am facing issue in database connection.',
#     'is_important': True,
#     'Date': '2025-10-01 17:51:35.000000',
#     'attachment_data': [{'filename': 'image.png', 'mimeType': 'image/png', 'path': 'attachments/image.png'}]
#     }

raw={
    "Message_ID": "1999fb8c1e11f668", 
    "query": "Hello I am facing issue in database connection.", 
    "escalate": True, 
    "priority": "high",
    "escalation_reason": "User is experiencing a database connection issue.", 
    "response": "A database connection error may arise from several reasons. You might try to check your database credentials and ensure the database server is running. If this does not resolve the issue, please let me know, and I will escalate it to our technical team.",
    "subject": "Re: Getting Error", "to_email": "nandaniramoliya@gmail.com", "reply_to": True}

# raw={
#     'Message_ID': '1999fb8c1e11f668',
#     "query": "This database issue is still not solved",
#     "response": "We have fix this issue currently server is geting restart try after some time you will get results.",
#     "subject": "Re: Database issue",
#     "esclation_reason": "Database is critical part in production at time of retrival",
#     "esclate": False,
#     "to_email": "nandaniramoliya@gmail.com",
#     "reply_to": False,
#     "message_id": "1999a074854f32b0",
# }
