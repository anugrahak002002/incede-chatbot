# INCEDE AI — Conversational Form Bot

An AI-powered conversational form assistant built with **Flask**, **LangGraph**, and **Groq (LLaMA 3.3 70B)**. The bot collects user information (name, phone, email, description) through natural conversation, validates each field using an LLM, stores sessions in SQLite, and displays logs via a web dashboard.

---

## Project Structure

```
scratch/
├── app.py                  # Flask app — routes, session management, DB integration
├── graph.py                # LangGraph graph definition — nodes, edges, routers
├── state.py                # TypedDict state schema shared across all nodes
├── tools.py                # LLM validation — single Groq API call per user message
├── db.py                   # SQLAlchemy db instance
├── models.py               # DB models — ChatSession, ChatMessage
├── requirements.txt        # Python dependencies with versions
├── .env                    # Environment variables (not committed)
├── graph.png               # Auto-generated graph image on startup
│
├── nodes/                  # LangGraph node functions
│   ├── __init__.py
│   ├── validate_node.py    # Calls tools.py, updates state field and advances form
│   └── ask_node.py         # Prompt strings for each field (visual node)
│
├── static/
│   └── script.js           # Frontend JS — send messages, typing indicator, reset
│
├── templates/
│   ├── index.html          # Main landing page with embedded chat widget
│   ├── logs.html           # Paginated session log table
│   └── session.html        # Individual session detail — collected data + conversation
│
└── instance/
    └── chatbot.db          # SQLite database (auto-created on first run)
```

---

## Conversation Flow

```
User opens chat
      │
      ▼
 Hello! What is your name?
      │
      ▼
┌─────────────────────────────────────────┐
│              LangGraph Graph            │
│                                         │
│   START                                 │
│     │                                   │
│     ▼                                   │
│  chatbot  ──────────────→  validator    │
│               (always)        │         │
│                               │ valid   │
│                               ▼         │
│                         field_router    │
│                               │         │
│                               ▼         │
│                             END         │
└─────────────────────────────────────────┘
      │
      ▼
 Flask session tracks current_field
 between graph.invoke() calls
      │
      ├── name  → phone → email → description → done
      │
      ▼
 All data saved to SQLite on completion
```

### Field Order

| Step | Field       | Validation Rule                                              |
|------|-------------|--------------------------------------------------------------|
| 1    | Name        | Min 3 chars, letters and spaces only, must contain a vowel  |
| 2    | Phone       | Exactly 10 digits, starts with 6/7/8/9 (Indian mobile)      |
| 3    | Email       | Valid format — starts with letter, contains @, proper domain |
| 4    | Description | Min 10 characters, or type `skip` to skip                   |

---

## How It Works

### Backend (Flask + LangGraph)
- Each user message hits `POST /chat`
- Flask loads the current state from the session (includes `current_field`)
- `graph.invoke(state)` runs the LangGraph graph once
- Inside the graph, `validate_node` calls `validate_with_llm()` in `tools.py`
- One Groq API call validates the input AND generates a conversational reply
- If valid, `current_field` advances to the next field
- If invalid, the bot replies with a friendly error and stays on the same field
- On completion (`current_field == "done"`), data is saved to `ChatSession` in SQLite

### Frontend (Vanilla JS + Tailwind)
- Chat widget toggled via CSS checkbox (no JS needed to open/close)
- Messages sent via `fetch()` to `/POST chat`
- Animated typing indicator shown while waiting for response
- Input disabled during API call to prevent double-sends
- On form completion, input is locked and session is reset after 2 seconds

### Database
- `ChatSession` — one row per browser session, stores collected fields + status
- `ChatMessage` — every user and bot message logged with timestamp and role
- Errors are also logged as `role="error"` so they appear in the session detail view

---

## Setup & Run

### 1. Clone and enter the project
```bash
git clone <your-repo-url>
cd scratch
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Create `.env` file
```
GROQ_API_KEY=gsk_your_key_here
```
Get your key from [console.groq.com](https://console.groq.com/keys)

### 4. Run the app
```bash
python app.py
```

### 5. Open in browser
```
http://127.0.0.1:5000
```

---

## Routes

| Route                  | Method | Description                          |
|------------------------|--------|--------------------------------------|
| `/`                    | GET    | Main page with chat widget           |
| `/chat`                | POST   | Accepts user message, returns reply  |
| `/reset`               | POST   | Clears current session               |
| `/logs`                | GET    | Paginated session log table          |
| `/session/<id>`        | GET    | Individual session detail + messages |

---

## Environment Variables

| Variable       | Description                  |
|----------------|------------------------------|
| `GROQ_API_KEY` | Groq API key for LLaMA model |

---
