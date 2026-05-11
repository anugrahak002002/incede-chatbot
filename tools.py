import os
import json
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def validate_with_llm(field: str, user_input: str) -> dict:

    rules = {
        "name": "only letters and spaces, at least 3 characters, must have a vowel",
        "phone": "exactly 10 digits, starts with 6/7/8/9 (Indian mobile)",
        "email": "valid email format like user@example.com",
        "description": "at least 10 characters, or the word skip",
    }

    next_prompt = {
        "name":        "Now ask for their phone number.",
        "phone":       "Now ask for their email address.",
        "email":       "Now ask for a short description (or they can type skip).",
        "description": "Thank them warmly, the form is complete.",
    }

    prompt = f"""You are a friendly conversational AI assistant helping collect a user's {field} through chat.

STEP 1 — Decide what the user is doing:
  A) They provided a value that matches this rule: {rules[field]}
  B) They are chatting, asking a question, or saying something unrelated to {field}
  C) They provided something that looks like a {field} but it's invalid format

STEP 2 — Respond accordingly:
  A) Valid value → set valid=true, extract clean value, confirm warmly. {next_prompt[field]}
  B) Chat/question → set valid=false, value="". FULLY answer their message naturally like a friend would. Then in one sentence, gently ask for their {field} again.
  C) Invalid format → set valid=false, value="". Briefly explain the issue. Ask again for {field}.

User said: "{user_input}"
Current field: {field}

Examples of case B: "how are you", "what is gold rate", "why do you need this", "hello", "lol", "who made you"
These must be answered naturally before redirecting.

Respond ONLY with JSON:
{{
  "valid"  : true or false,
  "value"  : "cleaned value if case A, else empty string",
  "message": "your natural friendly reply"
}}"""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": "You are a warm, conversational assistant. You answer all questions naturally. You never ignore what the user says. Always reply in valid JSON only."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            response_format={"type": "json_object"},
            temperature=0.7
        )

        data = json.loads(response.choices[0].message.content.strip())

        return {
            "valid":   bool(data.get("valid", False)),
            "value":   str(data.get("value", "")),
            "message": str(data.get("message", "Please try again."))
        }

    except Exception as e:
        print("LLM ERROR:", e)
        return {
            "valid":   False,
            "value":   "",
            "message": "Sorry, something went wrong. Please try again."
        }