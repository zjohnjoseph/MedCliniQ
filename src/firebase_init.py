import os
import firebase_admin
from firebase_admin import credentials

_CREDENTIALS_PATH = os.path.join(
    os.path.dirname(__file__),
    "chatbot-auth-76288-firebase-adminsdk-fbsvc-5902a47b41.json"
)


def init_firebase():
    if not firebase_admin._apps:
        cred = credentials.Certificate(_CREDENTIALS_PATH)
        firebase_admin.initialize_app(cred, {"projectId": "chatbot-auth-76288"})
