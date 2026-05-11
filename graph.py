from state import botState
from nodes.validate_node import validate_node
from langgraph.graph import StateGraph, START, END



def chatbot(obj: botState) -> botState:
    """Runs LLM tool-calling to validate current field."""
    return validate_node(obj)


def update_field(obj: botState) -> botState:
    """Advances current_field to the next step after valid input."""
    next_field = {
        "name":        "phone",
        "phone":       "email",
        "email":       "description",
        "description": "done",
    }
    current = obj["current_field"]
    if current in next_field:
        obj["current_field"] = next_field[current]
    return obj


def handle_invalid(obj: botState) -> botState:
    """Keeps current_field unchanged — user must retry."""
    return obj


# =========================================================
# ROUTERS
# =========================================================

def route_after_chatbot(obj: botState) -> str:
    """Route based on whether validation passed."""
    if obj["valid"]:
        return "valid"
    return "invalid"


def route_after_update(obj: botState) -> str:
    """Route based on whether form is complete."""
    if obj["current_field"] == "done":
        return "done"
    return "continue"



flow = StateGraph(botState)


flow.add_node("chatbot",       chatbot)
flow.add_node("update_field",  update_field)
flow.add_node("handle_invalid", handle_invalid)

flow.add_edge(START, "chatbot")


flow.add_conditional_edges(
    "chatbot",
    route_after_chatbot,
    {
        "valid":   "update_field",
        "invalid": "handle_invalid",
    }
)

flow.add_conditional_edges(
    "update_field",
    route_after_update,
    {
        "done":     END,
        "continue": END,   # exits Flask session drives next turn
    }
)
flow.add_edge("handle_invalid", END)




graph = flow.compile()

png_bytes = graph.get_graph().draw_mermaid_png()
with open("graph.png", "wb") as f:
    f.write(png_bytes)

print("graph generated")