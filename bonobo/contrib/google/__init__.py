import os

import httplib2
from apiclient import discovery
from oauth2client import client, tools
from oauth2client.file import Storage
from oauth2client.tools import argparser

# https://developers.google.com/api-client-library/python/guide/aaa_oauth
# pip install google-api-python-client (1.6.4)


HOME_DIR = os.path.expanduser('~')
GOOGLE_SECRETS = os.path.join(HOME_DIR, '.cache/secrets/client_secrets.json')


def get_credentials(*, scopes):
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

    # see https://developers.google.com/api-client-library/python/auth/web-app
    # kw: "incremental scopes"
    if not credentials or credentials.invalid or not credentials.has_scopes(scopes):
        flow = client.flow_from_clientsecrets(GOOGLE_SECRETS, scopes)
        flow.user_agent = 'Bonobo ETL (https://www.bonobo-project.org/)'
        flags = argparser.parse_args(['--noauth_local_webserver'])
        credentials = tools.run_flow(flow, store, flags)
        print('Storing credentials to ' + credential_path)
    return credentials


def get_google_spreadsheets_api_client(scopes=('https://www.googleapis.com/auth/spreadsheets',)):
    credentials = get_credentials(scopes=scopes)
    http = credentials.authorize(httplib2.Http())
    discoveryUrl = 'https://sheets.googleapis.com/$discovery/rest?version=v4'
    return discovery.build('sheets', 'v4', http=http, discoveryServiceUrl=discoveryUrl, cache_discovery=False)


def get_google_people_api_client(scopes=('https://www.googleapis.com/auth/contacts',)):
    credentials = get_credentials(scopes=scopes)
    http = credentials.authorize(httplib2.Http())
    discoveryUrl = 'https://people.googleapis.com/$discovery/rest?version=v1'
    return discovery.build('people', 'v1', http=http, discoveryServiceUrl=discoveryUrl, cache_discovery=False)
