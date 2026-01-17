from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle
import os

SCOPES = ["https://www.googleapis.com/auth/blogger"]

def main():
    creds = None

    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                r"C:\Users\Ossama-Hashim\Documents\blogger_credentials\client_secret_560836748568-vgmep42hvshne8a4pusl2852nvjllcmd.apps.googleusercontent.com.json",
                SCOPES
            )
            creds = flow.run_local_server(port=0)

        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)

    print("Token created successfully.")

if __name__ == "__main__":
    main()
