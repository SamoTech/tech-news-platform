from googleapiclient.discovery import build
import pickle
import os

BLOG_ID = "7570751768424346777"

def get_service():
    with open("token.pickle", "rb") as token:
        creds = pickle.load(token)

    service = build("blogger", "v3", credentials=creds)
    return service

def publish_post(title, content):
    service = get_service()

    post_body = {
        "kind": "blogger#post",
        "title": title,
        "content": content
    }

    post = service.posts().insert(
        blogId=BLOG_ID,
        body=post_body,
        isDraft=False
    ).execute()

    print("Post published:")
    print(post["url"])

if __name__ == "__main__":
    publish_post(
        title="Automated Tech News Test Post",
        content="<p>This is a test post published automatically by the system.</p>"
    )
