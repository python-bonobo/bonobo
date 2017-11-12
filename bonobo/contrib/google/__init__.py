import os

import httplib2
from apiclient import discovery
from oauth2client import client, tools
from oauth2client.file import Storage
from oauth2client.tools import argparser

HOME_DIR = os.path.expanduser('~')
GOOGLE_SCOPES = ('https://www.googleapis.com/auth/spreadsheets', )
GOOGLE_SECRETS = os.path.join(HOME_DIR, '.cache/secrets/client_secrets.json')


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    credential_dir = os.path.join(HOME_DIR, '.cache', __package__, 'credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir, 'googleapis.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(GOOGLE_SECRETS, GOOGLE_SCOPES)
        flow.user_agent = 'Bonobo ETL (https://www.bonobo-project.org/)'
        flags = argparser.parse_args(['--noauth_local_webserver'])
        credentials = tools.run_flow(flow, store, flags)
        print('Storing credentials to ' + credential_path)
    return credentials


def get_google_spreadsheets_api_client():
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    discoveryUrl = 'https://sheets.googleapis.com/$discovery/rest?version=v4'
    return discovery.build('sheets', 'v4', http=http, discoveryServiceUrl=discoveryUrl, cache_discovery=False)
