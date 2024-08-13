# Handles the Oauth 2.0 authentication flow, including obtaining, refreshing, and storing tokens securely.
import os
import time
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from module5.utils import logger

# Path to 'clients_secret.json' file
CREDENTIALS_FILE = 'config/client_secret.json'

# Path to file where access and refresh tokens are stored
TOKEN_FILE = 'config/token.json'

#Scopes required by the application
SCOPES = [
    'https://www.googleapis.com/auth/drive', 
    'https://www.googleapis.com/auth/documents'
]

def load_credentials():
    #Load credentials from file if they exist
    credentials = None
    if os.path.exists(TOKEN_FILE):
        credentials = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
        logger.debug("# Credentials loaded successfully.")
    return credentials

def save_credentials(credentials):
    """ Save the credentials for the next run """
    try:
        with open(TOKEN_FILE, 'w') as token:
            token.write(credentials.to_json())
        logger.debug("# Credentials saved successfully.")
    except IOError as e:
        logger.error(f"Credentials were not saved successfully. Error: {e}")
    
def authenticate():
    """
    Authenticates the user with Google OAuth 2.0.

    This function tries to load existing credentials from a file. If the credentials
    are not found, expired, or invalid, it initiates an authentication flow to obtain
    new credentials. Valid credentials are then saved for future use.

    Returns:
        google.oauth2.credentials.Credentials: The OAuth2 credentials for accessing Google APIs.
    """
    credentials = load_credentials()

    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            # Refresh the access token if expired
            for attempt in range(5):
                try:
                    credentials.refresh(Request())
                    logger.debug("# Access token refreshed successfully.")
                    break
                except HttpError as error:
                    logger.error(f"Attempt {attempt + 1}: Failed to refresh access token. Error: {error}")
                    if error.status_code in [429, 500, 502, 503, 504]: # Retryable errors
                        time.sleep(2 ** attempt) # Exponential backoff
                    else:
                        raise
                except Exception as e:
                    logger.error(f"Failed to refresh access token. Error: {e}")
                    raise
                raise Exception("Failed to refresh access token after multiple attempts.")
        else:
            try:
                # Initialize the OAuth 2.0 flow using client secrets from the JSON file, specifying the required scopes
                flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE,SCOPES)
            except FileNotFoundError:
                logger.error(f"File not found: {CREDENTIALS_FILE}")
                return None
            except Exception as e:
                logger.error(f"Unexpected error during OAuth flow initialization: {e}")
                return None
            else:
                # Send users to Google's auth 2.0 server
                credentials = flow.run_local_server(
                    host='localhost',
                    port=8080, 
                    authorization_prompt_message='Please visit this URL: {url}', 
                    success_message='The auth flow is complete; you may close this window.',
                    open_browser=True
                )
                if credentials is None:
                    logger.error("Failed to obtain credentials.")
                    return None
        save_credentials(credentials)
    logger.debug("Oauth authentication successful.")    
    return credentials
