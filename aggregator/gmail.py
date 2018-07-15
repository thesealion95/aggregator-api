"""
Shows basic usage of the Gmail API.

Lists the user's Gmail labels.
"""
from __future__ import print_function
from apiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
from aggregator.db import retrieve_objects_from_db, save_to_db


def get_facebook():
    # Setup the Gmail API
    SCOPES = 'https://www.googleapis.com/auth/gmail.readonly'
    store = file.Storage('credentials.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('client_secret.json', SCOPES)
        creds = tools.run_flow(flow, store)
    service = build('gmail', 'v1', http=creds.authorize(Http()))

    # Call the Gmail API
    results = service.users().messages().list(userId='me',
                                              q="from:notification+zrdevrpidrgz@facebookmail.com is:unread").execute()
    messages = []

    if 'messages' in results:
        messages.extend(results['messages'])

    while 'nextPageToken' in results:
        page_token = results['nextPageToken']
        results = service.users().messages().list(userId='me',
                                                  q="from:notification+zrdevrpidrgz@facebookmail.com is:unread", pageToken=page_token).execute()
        messages.extend(results['messages'])

    for count in messages:
        return_obj = {}
        results = service.users().messages().get(
            userId='me', id=count['id'], format='full').execute()
        for item in results['payload']['headers']:
            if item['name'] == 'Subject':
                return_obj['msg'] = item['value']
            if item['name'] == 'Date':
                return_obj['time_received'] = item['value']
            return_obj['from_program'] = 'facebook'
            return_obj['url'] = 'https://www.facebook.com/profile'
            return_obj['read'] = False
            return_obj['email_id'] = item['id']

            query = {'email_id': item['id']}
            result = retrieve_objects_from_db(
                query, 'email_db', 'email_collection', True)
            if not result:
                save_to_db(return_obj)