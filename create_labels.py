from __future__ import print_function
import pickle
import os
import json
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.errors import HttpError


def get_creds():
    # If modifying these scopes, delete the file token.pickle.
    SCOPES = ['https://www.googleapis.com/auth/gmail.modify']
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"), SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    return creds


def main():
    service = build('gmail', 'v1', credentials=get_creds())
    f = open("domain-labels.json")
    r = json.loads(f.read())
    domain_labels_list = []
    for item in r:
        label = item.get("label")
        label_split = label.split("/")
        try:
            print(f"Creating label {label_split[0]}")
            label_object = {
                "name": label_split[0] 
            }
#            label = service.users().labels().create(userId='me',
#                                                body=label_object).execute()
#            print(label['id'])
        except HttpError as e:
            if '409' not in str(e):
                print(f"Unexpected error occurred {e}") 
            else:
                print(f"Label {label_split[0]} already exists")
        if len(label_split) >= 2:
            try:
                print(f"Creating nested label {label}")
                label_object = {
                    "name": label
                }
#                label = service.users().labels().create(userId='me',
#                                                        body=label_object).execute()
#                print(label['id'])
            except HttpError as e:
                if '409' not in str(e):
                    print(f"Unexpected error occurred {e}") 
                else:
                    print(f"Label {label} already exists")


if __name__ == '__main__':
    main()
