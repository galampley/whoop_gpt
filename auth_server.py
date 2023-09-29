'''
This FastAPI application manages the OAuth 2.0 flow for Whoop API authentication. It provides endpoints for generating an authorization URL and exchanging an authorization code for an access token.\
It also has an endpoint (/some_endpoint) that expects an access token and fetches data from the Whoop API.
'''
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2AuthorizationCodeBearer
from wrapped_auth import WhoopAPI
from pydantic import BaseModel
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
import logging
import requests
from dotenv import load_dotenv
import os

logging.basicConfig(level=logging.INFO)

env_path = "/Users/galampley/Documents/secrets.env"
load_dotenv(dotenv_path=env_path)

app = FastAPI()

# fastapi CORS
app.add_middleware(
    CORSMiddleware,
    # allow_origins=["http://localhost:8501"],  # Update this to the domain where your Streamlit app will run
    allow_origins=["https://whoop-gpt-45ade1b84fc3.herokuapp.com/"],  # Update this to the domain where your Streamlit app will run
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type"],
)

whoop_client_id=os.getenv('WHOOP_CLIENT_ID')
whoop_client_secret=os.getenv('WHOOP_CLIENT_SECRET')

logging.info(f"WHOOP_CLIENT_ID: {whoop_client_id}")
logging.info(f"WHOOP_CLIENT_SECRET: {whoop_client_secret}")

# Initialize your WhoopAPI class
whoop_api = WhoopAPI(
    client_id=whoop_client_id,
    client_secret=whoop_client_secret,
    # redirect_uri='http://localhost:8000/token',  # Callback URL
    redirect_uri='https://whoop-gpt-45ade1b84fc3.herokuapp.com/token',  # Callback URL
    all_scopes=["read:profile", "read:recovery", "read:workout", "read:sleep", "read:body_measurement", "read:cycles"]
)

oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl=whoop_api.get_authorization_url(),
    tokenUrl="not_used_here",  # Token exchange is done in the get_token function
)

class Token(BaseModel):
    access_token: str
    token_type: str

# dynamic authorization url
@app.get("/auth_url")
def get_auth_url():
    return {"auth_url": whoop_api.get_authorization_url()}

@app.get("/token", response_model=Token)
async def get_token(code: str, state: str = None):
    logging.info(f"Received code: {code}")
    logging.info(f"Received state: {state}")
    try:
        whoop_api.get_access_token_from_code(code)
        logging.info(f"Access Token: {whoop_api.access_token}")
        access_token = whoop_api.access_token
        headers = {'Authorization': f'Bearer {access_token}'}
        response = requests.get('https://api.prod.whoop.com/developer/v1/activity/sleep', headers=headers)
        logging.info(f"Whoop API response: {response.json()}")
    except Exception as e:
        logging.error(f"Error occurred: {e}")
        raise HTTPException(status_code=400, detail=str(e))

    # streamlit_url = f"http://localhost:8501/?token={access_token}"
    streamlit_url = f"https://whoop-gpt-45ade1b84fc3.herokuapp.com/?token={access_token}"
    return RedirectResponse(url=streamlit_url)


'''
How You're Authorizing Now:
Manual Steps: You generate an authorization URL and manually open it in a web browser.
User Input: The user logs in on the authorization page and is redirected to a callback URL.
Copy-Paste: The user needs to copy this URL and paste it back into your application.
Token Fetch: You then use this URL to fetch an access token for making authorized API calls.

What We're Doing with FastAPI:
User Clicks Authorization Link: Within your Streamlit app, the user initiates the authorization process by clicking a link.
Automatic Redirection: The user is automatically redirected to the Whoop API's authorization page, where they log in and grant permission.
Automatic Capture: After granting permission, the Whoop API redirects the user back to your FastAPI server. FastAPI automatically captures the authorization code from the URL.
Token Exchange: FastAPI uses the captured authorization code to perform a token exchange with the Whoop API, obtaining an access token.
Seamless Integration: The access token is seamlessly integrated into your Streamlit app without requiring manual copying. This token enables your app to make authorized API calls to the Whoop service, providing the user with the desired functionality.
'''
