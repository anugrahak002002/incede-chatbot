from groq import Groq

from tools import (
    validate_name,
    validate_email,
    validate_phone,
    validate_description
)

import os


client = Groq(

    api_key=os.getenv("GROQ_API_KEY")
)


# ---------------- LLM CHAT RESPONSE ---------------- #

def general_chat(user_input, current_field):

    prompt = f"""

    The user is currently filling a form.

    Current required field: {current_field}

    User message: {user_input}

    Respond naturally to the user's message in a friendly conversational way.

    Then politely guide them back to providing their {current_field}.

    Keep response short.
    """


    response = client.chat.completions.create(

        model = "lllama-3.1-8b-instant",

        messages=[

            {
                "role": "system",
                "content": "You are a friendly AI assistant."
            },

            {
                "role": "user",
                "content": prompt
            }
        ]
    )


    return response.choices[0].message.content



# ---------------- MAIN PROCESS ---------------- #

def process_input(current_field, user_input):


    # -------- NAME -------- #

    if current_field == "name":

        result = validate_name(user_input)

        if result["valid"]:

            return {

                "valid": True,

                "value": result["value"],

                "message": "Nice to meet you. Please enter your email."
            }

        else:

            ai_reply = general_chat(user_input, "name")

            return {

                "valid": False,

                "value": "",

                "message": ai_reply
            }



    # -------- EMAIL -------- #

    elif current_field == "email":

        result = validate_email(user_input)

        if result["valid"]:

            return {

                "valid": True,

                "value": result["value"],

                "message": "Please enter your phone number."
            }

        else:

            ai_reply = general_chat(user_input, "email")

            return {

                "valid": False,

                "value": "",

                "message": ai_reply
            }



    # -------- PHONE -------- #

    elif current_field == "phone":

        result = validate_phone(user_input)

        if result["valid"]:

            return {

                "valid": True,

                "value": result["value"],

                "message": "Please enter description or type 'skip'."
            }

        else:

            ai_reply = general_chat(user_input, "phone number")

            return {

                "valid": False,

                "value": "",

                "message": ai_reply
            }



    # -------- DESCRIPTION -------- #

    elif current_field == "description":

        result = validate_description(user_input)

        if result["valid"]:

            return {

                "valid": True,

                "value": result["value"],

                "message": "Thank you. Data collected successfully."
            }

        else:

            ai_reply = general_chat(user_input, "description")

            return {

                "valid": False,

                "value": "",

                "message": ai_reply
            }