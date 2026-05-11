import re
from langchain_core.tools import tool
from pydantic import BaseModel, Field



class ValidationResult(BaseModel):
    valid:   bool  = Field(description="Whether the input is valid")
    value:   str   = Field(description="Cleaned value if valid, empty string if not")
    message: str   = Field(description="Friendly conversational reply to the user")




@tool
def validate_name(user_input: str) -> dict:
    """
    Validate a user's name.
    A valid name has at least 3 characters, contains only letters and spaces,
    and has at least one vowel. Random strings like 'xyz' are invalid.
    Returns a ValidationResult as a dict.
    """
    name = user_input.strip()

    if (
        len(name) < 3
        or not re.match(r"^[A-Za-z\s]+$", name)
        or not any(v in name.lower() for v in "aeiou")
    ):
        return {
            "valid":   False,
            "value":   "",
            "message": f"'{name}' doesn't look like a valid name. Please enter your full name (letters only, at least one vowel)."
        }

    return {
        "valid":   True,
        "value":   name.title(),
        "message": f"Nice to meet you, {name.title()}! Could you please share your phone number?"
    }


@tool
def validate_phone(user_input: str) -> dict:
    """
    Validate an Indian mobile phone number.
    A valid number has exactly 10 digits and starts with 6, 7, 8, or 9.
    Returns a ValidationResult as a dict.
    """
    phone = re.sub(r"\D", "", user_input.strip())

    if len(phone) != 10 or phone[0] not in "6789":
        return {
            "valid":   False,
            "value":   "",
            "message": "That doesn't look like a valid Indian mobile number. Please enter a 10-digit number starting with 6, 7, 8, or 9."
        }

    return {
        "valid":   True,
        "value":   phone,
        "message": f"Got it! Phone number {phone} saved. What's your email address?"
    }


@tool
def validate_email(user_input: str) -> dict:
    """
    Validate an email address.
    A valid email starts with a letter, contains @, and has a proper domain.
    Returns a ValidationResult as a dict.
    """
    email = user_input.strip()
    pattern = r"^[a-zA-Z][a-zA-Z0-9._%+-]*@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

    if not re.match(pattern, email):
        return {
            "valid":   False,
            "value":   "",
            "message": "That doesn't look like a valid email. Please enter something like user@example.com."
        }

    return {
        "valid":   True,
        "value":   email.lower(),
        "message": f"Email {email.lower()} saved! Could you give a short description? (or type 'skip')"
    }


@tool
def validate_description(user_input: str) -> dict:
    """
    Validate a description field.
    Valid if at least 10 characters long, or if user types skip/no/none/na/nothing.
    Returns a ValidationResult as a dict.
    """
    text = user_input.strip()
    skip_words = ["skip", "no", "none", "na", "nothing"]

    if text.lower() in skip_words:
        return {
            "valid":   True,
            "value":   "Skipped",
            "message": "No problem! All your details have been collected successfully. ✅"
        }

    if len(text) < 10:
        return {
            "valid":   False,
            "value":   "",
            "message": "Description is a bit short. Please write at least 10 characters, or type 'skip'."
        }

    return {
        "valid":   True,
        "value":   text,
        "message": "Thank you! All your details have been collected successfully. ✅"
    }


# =========================================================
# TOOL REGISTRY
# =========================================================

TOOLS = [validate_name, validate_phone, validate_email, validate_description]

FIELD_TOOL_MAP = {
    "name":        validate_name,
    "phone":       validate_phone,
    "email":       validate_email,
    "description": validate_description,
}