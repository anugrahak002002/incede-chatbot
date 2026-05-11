PROMPTS = {
    "name":        "Hello! 👋 What is your name?",
    "phone":       "Great! Please enter your phone number.",
    "email":       "Thanks! Please enter your email address.",
    "description": "Almost done! Please enter a description, or type 'skip'.",
}


def ask_node(obj):
    field = obj["current_field"]
    obj["bot_message"] = PROMPTS.get(field, "Please continue.")
    return obj