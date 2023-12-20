import json
import os
from datetime import datetime

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
import base64
from bs4 import BeautifulSoup

# Gmail APIのスコープを設定
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']


def gmail_authenticate():
    flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
    creds = flow.run_local_server(port=0)
    return build('gmail', 'v1', credentials=creds)


def search_messages(service, q):
    result = service.users().messages().list(userId='me',q=q).execute()
    messages = []
    if 'messages' in result:
        messages.extend(result['messages'])
    while 'nextPageToken' in result:
        page_token = result['nextPageToken']
        result = service.users().messages().list(userId='me',q=q, pageToken=page_token).execute()
        if 'messages' in result:
            messages.extend(result['messages'])
    return messages


def read_message(service, message, out_path):
    msg = service.users().messages().get(userId='me', id=message['id'], format='full').execute()
    with open(os.path.join(out_path, f"{message['id']}.json"), "w") as fp:
        fp.write(json.dumps(msg, indent=2, ensure_ascii=False))


def main():
    now = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = f"out/download/{now}"
    os.makedirs(out_path, exist_ok=True)

    service = gmail_authenticate()
    q = os.environ["GMAIL_SEARCH_QUERY"]
    messages = search_messages(service, q)
    for msg in messages:
        print(f"read: {msg['id']}")
        read_message(service, msg, out_path)

    print(f"done: {out_path}")


if __name__ == '__main__':
    main()
