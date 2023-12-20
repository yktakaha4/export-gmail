import glob
import json
import os
from datetime import datetime
from sys import argv

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
import base64
from bs4 import BeautifulSoup

# Gmail APIのスコープを設定
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']


def parse_parts(message, parse_html=False):
    parts = []
    for part in message['payload']['parts']:
        if part['mimeType'] == 'text/html':
            decoded_data = base64.urlsafe_b64decode(part['body']['data'])
            if parse_html:
                soup = BeautifulSoup(decoded_data , "lxml")
                body = soup.body()
            else:
                body = decoded_data.decode()
            parts.append({
                'MimeType': part['mimeType'],
                'Body': body,
            })

    return parts


def parse_message(fpath):
    with open(fpath, "r") as fp:
        msg = json.load(fp)

    payload = msg['payload']
    headers = payload.get("headers")
    parts = payload.get("parts")
    data = {'Id': msg['id']}
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
    fpaths = glob.glob(f'{argv[1]}/*')

    now = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = f"out/parse/{now}"
    os.makedirs(out_path, exist_ok=True)

    for fpath in fpaths:
        msg = parse_message(fpath)
        for i, part in enumerate(msg['Body']):
            print(f"Parse: {msg['Id']}")
            with open(f'{out_path}/{msg["Id"]}_{i}.html', 'w') as fp:
                fp.write(part['Body'])

    print(f"done: {out_path}")


if __name__ == '__main__':
    main()
