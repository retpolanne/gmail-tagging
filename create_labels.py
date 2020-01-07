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
    SCOPES = ['https://www.googleapis.com/auth/gmail.modify https://www.googleapis.com/auth/gmail.settings.basic']
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


def create_filter(service, from_mail, label_id):
    filter = {
        'criteria': {
            'from': from_mail
        },
        'action': {
            'addLabelIds': [label_id]
        }
    }
    return service.users().settings().filters().create(userId='me',
                                                    body=filter).execute()


def get_label_id(service, label_list, label_name):
    try:
        for label in label_list.get('labels'):
            if label.get('name') == label_name:
                return label.get('id')
    except HttpError as e:
        if '409' not in str(e):
            print(f"Unexpected error occurred {e}") 

def main():
    service = build('gmail', 'v1', credentials=get_creds())
    f = open("domain-labels.json")
    r = json.loads(f.read())
    domain_labels_list = []
    current_labels = [cur_label for cur_label in service.users().labels().list(userId='me').execute().get('labels')]
    print(f"Found {len(current_labels)} labels already created")
    for item in r:
        label = item.get("label")
        label_split = label.split("/")
        label_id = ""
        try:
            print(f"Creating label {label_split[0]}")
            label_object = {
                "name": label_split[0] 
            }
            label = service.users().labels().create(userId='me',
                                                body=label_object).execute()
            label_id = label.get("id")
            print(label_id)
            current_labels.append({
                'name': label_split[0],
                'id': label_id
            })
        except HttpError as e:
            if '409' not in str(e):
                print(f"Unexpected error occurred {e}") 
            else:
                print(f"Label {label_split[0]} already exists")
                label_id = get_label_id(service, current_labels, label_split[0])
                print(label_id)
        if len(label_split) >= 2:
            try:
                print(f"Creating nested label {label}")
                label_object = {
                    "name": label
                }
                label = service.users().labels().create(userId='me',
                                                        body=label_object).execute()
                label_id = label.get("id")
                print(label_id)
                current_labels.append({
                    'name': label,
                    'id': label_id
                })
            except HttpError as e:
                if '409' not in str(e):
                    print(f"Unexpected error occurred {e}") 
                else:
                    print(f"Label {label} already exists")
                    label_id = get_label_id(service, current_labels, label)
                    print(label_id)
        try:
            filter_id = create_filter(service, item.get("domain"), label_id)
            print(filter_id)
        except HttpError as e:
            if '409' not in str(e):
                print(f"Unexpected error occurred {e}") 


if __name__ == '__main__':
    main()
