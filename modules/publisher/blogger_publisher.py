# modules/publisher/blogger_publisher.py

from typing import Dict
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from pathlib import Path
import json
import os


SCOPES = ["https://www.googleapis.com/auth/blogger"]


class BloggerPublisher:
    def __init__(self, blog_id: str):
        self.blog_id = blog_id
        self.service = self._authenticate()

    def _authenticate(self):
        creds = None

        token_path = Path("token.json")
        creds_path = Path("credentials.json")

        if token_path.exists():
            creds = Credentials.from_authorized_user_file(
                token_path, SCOPES
            )

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    creds_path, SCOPES
                )
                creds = flow.run_local_server(port=0)

            token_path.write_text(creds.to_json(), encoding="utf-8")

        return build("blogger", "v3", credentials=creds)

    def publish(self, article: Dict) -> Dict:
        """
        Publish article to Blogger.
        Expects: title, content, meta_description, angle
        """

        post_body = {
            "kind": "blogger#post",
            "title": article["title"],
            "content": article["content"],
            "labels": [
                "AI",
                "Technology",
                article.get("angle", "analysis"),
            ],
        }

        request = (
            self.service.posts()
            .insert(blogId=self.blog_id, body=post_body, isDraft=False)
        )

        response = request.execute()

        return {
            "id": response.get("id"),
            "url": response.get("url"),
        }
