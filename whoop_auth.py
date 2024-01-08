'''
Responsible for handling OAuth 2.0 authentication with the Whoop API. It initializes an OAuth2 session, generates authorization URLs, \
and manages the exchange of authorization codes for access tokens.
'''
from requests_oauthlib import OAuth2Session
import requests
import urllib.parse

class WhoopAPI:
    def __init__(self, client_id, client_secret, redirect_uri, all_scopes):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.all_scopes = all_scopes
        self.oauth = self._initialize_oauth()
        self.access_token = None # newly initializing the attribute for RestAPI

    def _initialize_oauth(self):
        oauth = OAuth2Session(
            self.client_id,
            scope=self.all_scopes,
            redirect_uri=self.redirect_uri
        )
        return oauth

    def get_authorization_url(self):
        authorization_url, state = self.oauth.authorization_url('https://api.prod.whoop.com/oauth/oauth2/auth')
        return authorization_url

    # only function not necessary for RestAPI auth process but useful for manual auth process?
    def get_access_token(self, authorization_response):
        parsed_url = urllib.parse.urlparse(authorization_response)
        returned_state = urllib.parse.parse_qs(parsed_url.query)['state'][0]
        returned_code = urllib.parse.parse_qs(parsed_url.query)['code'][0]
        token_url = 'https://api.prod.whoop.com/oauth/oauth2/token'
        payload = {
            'grant_type': 'authorization_code',
            'code': returned_code,
            'redirect_uri': self.redirect_uri,
            'client_id': self.client_id,
            'client_secret': self.client_secret
        }
        response = requests.post(token_url, data=payload)
        token_info = response.json()
        self.access_token = token_info['access_token']

    def get_access_token_from_code(self, code):
        token_url = 'https://api.prod.whoop.com/oauth/oauth2/token'
        payload = {
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': self.redirect_uri,
            'client_id': self.client_id,
            'client_secret': self.client_secret
        }
        try:
            response = requests.post(token_url, data=payload)
            print(f"Response Status: {response.status_code}")  # Debugging statement

            token_info = response.json()
            print(f"Response Content: {token_info}")  # Debugging statement

            # Validate that 'access_token' is present in the response
            if 'access_token' in token_info:
                self.access_token = token_info['access_token']
                print(f"Assigned Access Token: {self.access_token}")  # Debugging statement
            else:
                print("Error: 'access_token' not found in API response")  # Debugging statement
                return None

        except Exception as e:
            print(f"An exception occurred: {e}")  # Debugging statement
            raise e

