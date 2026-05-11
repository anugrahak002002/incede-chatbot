from db import db
from datetime import datetime


class ChatSession(db.Model):
    id           = db.Column(db.Integer, primary_key=True)
    session_uuid = db.Column(db.String(100), unique=True, nullable=False)
    started_at   = db.Column(db.DateTime, default=datetime.utcnow)
    status       = db.Column(db.String(20), default="active")
    # collected fields
    name         = db.Column(db.String(100), default="")
    phone        = db.Column(db.String(20),  default="")
    email        = db.Column(db.String(150), default="")
    description  = db.Column(db.Text,        default="")


class ChatMessage(db.Model):
    id         = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey("chat_session.id"))
    role       = db.Column(db.String(10))   # user / bot
    message    = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)