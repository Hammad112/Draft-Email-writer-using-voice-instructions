import os
import base64
from email.mime.text import MIMEText
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from email.message import EmailMessage

import markdown

SCOPES = ['https://www.googleapis.com/auth/gmail.compose']

HTML_TEMPLATE = """
        <DOCTYPE html>
        <html>
        <head>
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 20px;
                background-color: #f4f4f4;
            }}
        </style>
        </head>
        <body>
            <h1>Meeting Minutes</h1>
            <p>{final_email_body}</p>
        </body>
        </html>
            """

def authenticate_gmail():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    token_path = os.path.join(current_dir, 'token.json')
    creds_path = os.path.join(current_dir, 'secrets.json')

    creds = None
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
            creds = flow.run_local_server(port=0) 

            # Save the credentials for future use
            with open(token_path, 'w') as token:
                token.write(creds.to_json())
    
    service = build('gmail', 'v1', credentials=creds)
    return service

def create_message(sender, to, subject, message_text):
    md=markdown.Markdown(extensions=['tables','fenced_code','nl2br'])
    ## Format the message text as HTML
    formatted_text = HTML_TEMPLATE.format(
        final_email_body=md.convert(message_text))

    msg = EmailMessage()
    content = formatted_text

    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = to
    msg.add_header('Content-Type', 'text/html')
    msg.set_payload(content)

    encoding=base64.urlsafe_b64encode(msg.as_bytes()).decode('utf-8')

    return {'raw': encoding}

def create_draft(service, user_id, message):
    try:
        draft = service.users().drafts().create(userId=user_id, body={'message:,message_body'}).execute()
        print(f"Draft created: {draft}")
        return draft
    except Exception as e:
        print(f"Error creating draft: {e}")
        return None
    




