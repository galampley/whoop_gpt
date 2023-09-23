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
