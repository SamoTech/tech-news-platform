# modules/publisher/blogger_publisher.py

import os
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials


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
            scopes=["https://www.googleapis.com/auth/blogger"],
        )

        return build("blogger", "v3", credentials=creds)

    def publish(self, article: dict) -> dict:
        """
        Publish article dict to Blogger.
        Expected keys: title, content
        """

        body = {
            "kind": "blogger#post",
            "title": article["title"],
            "content": article["content"],
        }

        post = (
            self.service.posts()
            .insert(blogId=self.blog_id, body=body, isDraft=False)
            .execute()
        )

        return {
            "post_id": post.get("id"),
            "url": post.get("url"),
        }
