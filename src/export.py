import os

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
    messages = [ ]
    if 'messages' in result:
        messages.extend(result['messages'])
    while 'nextPageToken' in result:
        page_token = result['nextPageToken']
        result = service.users().messages().list(userId='me',q=q, pageToken=page_token).execute()
        if 'messages' in result:
            messages.extend(result['messages'])
    return messages


def parse_parts(message):
    data = message['payload']['parts'][0]['body']['data']
    data = data.replace("-","+").replace("_","/")
    decoded_data = base64.b64decode(data)
    soup = BeautifulSoup(decoded_data , "lxml")
    body = soup.body()
    return body


def read_message(service, message):
    msg = service.users().messages().get(userId='me', id=message['id'], format='full').execute()
    payload = msg['payload']
    headers = payload.get("headers")
    parts = payload.get("parts")
    data = {}
    if headers:
        for d in headers:
            name = d.get("name")
            value = d.get("value")
            if name.lower() == "from":
                data['From'] = value
            if name.lower() == "to":
                data['To'] = value
            if name.lower() == "subject":
                data['Subject'] = value
            if name.lower() == "date":
                data['Date'] = value
    if parts:
        data['Body'] = parse_parts(msg)
    return data


def main():
    service = gmail_authenticate()
    q = os.environ["GMAIL_SEARCH_QUERY"]
    messages = search_messages(service, q)
    for msg in messages:
        data = read_message(service, msg)
        print(f"From: {data['From']}")
        print(f"To: {data['To']}")
        print(f"Subject: {data['Subject']}")
        print(f"Date: {data['Date']}")
        print(f"Body: {data['Body']}")
        print("\n")


if __name__ == '__main__':
    main()
