from firebase_admin import firestore
from datetime import datetime, timezone

def get_db():
    return firestore.client()


def create_conversation(user_id: str, title: str = "New Chat") -> str:
    db = get_db()
    now = datetime.now(timezone.utc)
    try:
        ref = (
            db.collection("users")
            .document(user_id)
            .collection("conversations")
            .document()
        )
        ref.set({"title": title, "created_at": now, "updated_at": now})
        return ref.id
    except Exception:
        return f"local-{int(now.timestamp() * 1000)}"


def get_conversations(user_id: str) -> list[dict]:
    db = get_db()
    try:
        docs = (
            db.collection("users")
            .document(user_id)
            .collection("conversations")
            .order_by("updated_at", direction=firestore.Query.DESCENDING)
            .stream()
        )
        return [{"id": d.id, **d.to_dict()} for d in docs]
    except Exception:
        return []


def get_messages(user_id: str, conversation_id: str) -> list[dict]:
    db = get_db()
    try:
        docs = (
            db.collection("users")
            .document(user_id)
            .collection("conversations")
            .document(conversation_id)
            .collection("messages")
            .order_by("timestamp")
            .stream()
        )
        return [d.to_dict() for d in docs]
    except Exception:
        return []


def save_message(user_id: str, conversation_id: str, role: str, content: str):
    db = get_db()
    now = datetime.now(timezone.utc)
    try:
        conv_ref = (
            db.collection("users")
            .document(user_id)
            .collection("conversations")
            .document(conversation_id)
        )
        conv_ref.collection("messages").document().set({
            "role": role,
            "content": content,
            "timestamp": now,
        })
        conv_ref.update({"updated_at": now})
    except Exception:
        pass


def update_conversation_title(user_id: str, conversation_id: str, title: str):
    db = get_db()
    try:
        (
            db.collection("users")
            .document(user_id)
            .collection("conversations")
            .document(conversation_id)
            .update({"title": title})
        )
    except Exception:
        pass


def delete_conversation(user_id: str, conversation_id: str):
    db = get_db()
    try:
        conv_ref = (
            db.collection("users")
            .document(user_id)
            .collection("conversations")
            .document(conversation_id)
        )
        for msg in conv_ref.collection("messages").stream():
            msg.reference.delete()
        conv_ref.delete()
    except Exception:
        pass
