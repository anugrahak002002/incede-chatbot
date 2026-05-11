from tools import validate_with_llm


def validate_node(obj):

    field      = obj["current_field"]
    user_input = obj["user_input"]

    result = validate_with_llm(field, user_input)

    obj["valid"]       = result["valid"]
    obj["bot_message"] = result["message"]

    if result["valid"]:
        obj[field] = result["value"]
        obj["current_field"] = {
            "name":        "phone",
            "phone":       "email",
            "email":       "description",
            "description": "done",
        }[field]

    return obj