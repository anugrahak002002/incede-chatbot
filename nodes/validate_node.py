from llm import run_agent


def validate_node(obj):
    """
    Calls LLM agent to validate current field.
    Only sets valid/value/bot_message — field advancement
    is handled by the update_field node in graph.py.
    """

    field      = obj["current_field"]
    user_input = obj["user_input"]

    result = run_agent(field, user_input)

    obj["valid"]       = result["valid"]
    obj["bot_message"] = result["message"]

    # save the validated value into state
    if result["valid"]:
        obj[field] = result["value"]

    return obj