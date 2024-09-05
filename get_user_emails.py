from __future__ import print_function
import pickle
import os
import json
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request


def get_creds():
    # If modifying these scopes, delete the file token.pickle.
    SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
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


def get_unlabeled_messages(service):
    try:
        print('Getting first page of unlabeled messages')
        response = service.users().messages().list(userId='me',
                q='has:nouserlabels').execute()
        messages = []
        if 'messages' in response:
            messages.extend(response['messages'])

        while 'nextPageToken' in response:
            page_token = response['nextPageToken']
            print(f'Getting page of unlabeled messages: {page_token}')
            response = service.users().messages().list(userId='me',
                  q='has:nouserlabels',
                  pageToken=page_token).execute()
            messages.extend(response['messages'])

        return messages
    except Exception as error:
        print (f'An error occurred: {error}')


def get_from_domain(service, message_id):
    try:
        print(f'Getting message id {message_id}')
        message = service.users().messages().get(userId='me',
                id=message_id).execute()
        for header in message.get('payload').get('headers'):
            if header.get('name') == "From":
                from_header = header.get('value')
                return from_header[from_header.find("<") + 1:from_header.find(">")].split("@")[1]
    except Exception as error:
        print (f'An error occurred: {error}')


def main():
    service = build('gmail', 'v1', credentials=get_creds())

    messages = get_unlabeled_messages(service)
    res_dict = {}
    try:
        for i, message in enumerate(messages):
            print(f'Message {i} of {len(messages)}')
            msg_id = message.get('id')
            from_domain = get_from_domain(service, msg_id)
            if from_domain not in res_dict:
                res_dict[from_domain] = {
                    "message_ids": []
                }
                msg_ids = res_dict[from_domain].get('message_ids')
            if msg_id not in msg_ids:
                res_dict[from_domain]['message_ids'].append(msg_id)
    except KeyboardInterrupt:
        print("Interrupt")
    f = open("res.json", "w")
    f.write(json.dumps(res_dict))


if __name__ == '__main__':
    main()
