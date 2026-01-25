# modules/publisher/blogger_publisher.py

import os
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

SCOPES = ["https://www.googleapis.com/auth/blogger"]


class BloggerPublisher:
    def __init__(self, blog_id: str):
        self.blog_id = blog_id
        self.service = self._authenticate()

    def _authenticate(self):
        creds = Credentials(
            token=None,
            refresh_token=os.environ["BLOGGER_REFRESH_TOKEN"],
            token_uri="https://oauth2.googleapis.com/token",
            client_id=os.environ["BLOGGER_CLIENT_ID"],
            client_secret=os.environ["BLOGGER_CLIENT_SECRET"],
            scopes=SCOPES,
        )

        return build("blogger", "v3", credentials=creds)

    def publish(self, title: str, html_content: str):
        post = {
            "kind": "blogger#post",
            "title": title,
            "content": html_content,
        }

        request = self.service.posts().insert(
            blogId=self.blog_id,
            body=post,
            isDraft=False,
        )

        return request.execute()
