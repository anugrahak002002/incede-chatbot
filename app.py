import uuid
import traceback
import math

from flask import Flask, render_template, request, jsonify, session
from graph import graph
from db import db
from models import ChatSession, ChatMessage

app = Flask(__name__)
app.secret_key = "incede-secret-key"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///chatbot.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

with app.app_context():
    db.create_all()

PER_PAGE = 10


# ── helpers ──────────────────────────────────────────────── #

def fresh_state():
    return {
        "current_field": "name",
        "name":          "",
        "email":         "",
        "phone":         "",
        "description":   "",
        "user_input":    "",
        "bot_message":   "Hello 👋 What is your name?",
        "valid":         False,
    }


def save_message(session_id, role, message):
    db.session.add(ChatMessage(
        session_id=session_id,
        role=role,
        message=message
    ))
    db.session.commit()


# ── routes ───────────────────────────────────────────────── #

@app.route("/")
def home():
    session.clear()

    sess_uuid = str(uuid.uuid4())
    chat_sess = ChatSession(session_uuid=sess_uuid)
    db.session.add(chat_sess)
    db.session.commit()

    session["state"]      = fresh_state()
    session["session_id"] = chat_sess.id

    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    try:
        data       = request.get_json()
        user_input = data.get("message", "").strip()

        if not user_input:
            return jsonify({"reply": "Please type something.", "done": False})

        state = session.get("state", fresh_state())

        if state["current_field"] == "done":
            return jsonify({"reply": "Form already completed. Thank you!", "done": True})

        state["user_input"] = user_input
        updated = graph.invoke(state)
        session["state"] = dict(updated)

        session_id = session.get("session_id")

        if session_id:
            save_message(session_id, "user", user_input)
            save_message(session_id, "bot",  updated["bot_message"])

        done = updated["current_field"] == "done"

        if done and session_id:
            chat_sess = ChatSession.query.get(session_id)
            if chat_sess:
                chat_sess.name        = updated.get("name", "")
                chat_sess.phone       = updated.get("phone", "")
                chat_sess.email       = updated.get("email", "")
                chat_sess.description = updated.get("description", "")
                chat_sess.status      = "completed"
                db.session.commit()

        return jsonify({
            "reply": updated["bot_message"],
            "done":  done
        })

    except Exception as e:
        err_msg = str(e)
        print("ERROR:", err_msg)
        traceback.print_exc()

        session_id = session.get("session_id")
        if session_id:
            save_message(session_id, "error", f"Internal error: {err_msg}")

        return jsonify({
            "reply": "Something went wrong. Please try again.",
            "done":  False
        })


@app.route("/reset", methods=["POST"])
def reset():
    session.clear()
    return jsonify({"status": "reset"})


@app.route("/logs")
def logs():
    page        = request.args.get("page", 1, type=int)
    total       = ChatSession.query.count()
    total_pages = max(1, math.ceil(total / PER_PAGE))
    page        = max(1, min(page, total_pages))

    sessions = (
        ChatSession.query
        .order_by(ChatSession.started_at.desc())
        .offset((page - 1) * PER_PAGE)
        .limit(PER_PAGE)
        .all()
    )

    return render_template(
        "logs.html",
        sessions=sessions,
        page=page,
        total=total,
        total_pages=total_pages
    )


@app.route("/session/<int:session_id>")
def session_detail(session_id):
    chat_sess = ChatSession.query.get_or_404(session_id)
    messages  = (
        ChatMessage.query
        .filter_by(session_id=session_id)
        .order_by(ChatMessage.created_at)
        .all()
    )
    return render_template("session.html", session=chat_sess, messages=messages)


if __name__ == "__main__":
    app.run(debug=True)