# from state import botState
# from tools import validate_with_llm

# from langgraph.graph import StateGraph, START, END


# # =========================================================
# # VALIDATE NODE  —  runs once per graph.invoke() call
# # =========================================================

# def validate_node(obj: botState) -> botState:

#     field      = obj["current_field"]
#     user_input = obj["user_input"]

#     result = validate_with_llm(field, user_input)

#     obj["valid"]       = result["valid"]
#     obj["bot_message"] = result["message"]

#     if result["valid"]:
#         obj[field] = result["value"]
#         obj["current_field"] = {
#             "name":        "phone",
#             "phone":       "email",
#             "email":       "description",
#             "description": "done",
#         }[field]

#     return obj


# # =========================================================
# # ROUTER  —  controls whether form is complete
# # =========================================================

# def router(obj: botState) -> str:
#     return "done" if obj["current_field"] == "done" else "continue"


# # =========================================================
# # BUILD GRAPH
# #
# #   START → validate_node → END          (always exits)
# #   router is used only to set done flag
# #   actual looping is managed by Flask session between calls
# # =========================================================

# flow = StateGraph(botState)

# flow.add_node("validate", validate_node)
# flow.add_edge(START, "validate")
# flow.add_edge("validate", END)

# graph = flow.compile()

# # save graph image
# png_bytes = graph.get_graph().draw_mermaid_png()
# with open("graph.png", "wb") as f:
#     f.write(png_bytes)

# print("graph generated")






# from state import botState
# from nodes.validate_node import validate_node

# from langgraph.graph import StateGraph, START, END


# # =========================================================
# # REAL NODE — does all the work
# # =========================================================

# def validator(obj: botState) -> botState:
#     return validate_node(obj)


# # =========================================================
# # VISUAL-ONLY NODES — just pass through, never loop
# # =========================================================

# def chatbot(obj: botState) -> botState:
#     return obj


# def field_router(obj: botState) -> botState:
#     return obj


# # =========================================================
# # ROUTERS
# # =========================================================

# def route_validator(obj: botState) -> str:
#     if obj["current_field"] == "done":
#         return "end"
#     if obj["valid"]:
#         return "field_router"
#     return "end"              # invalid → exit, Flask handles next turn


# def route_field_router(obj: botState) -> str:
#     return "end"


# =========================================================
# GRAPH
#
#   START → chatbot → validator ──(valid)──→ field_router → END
#                         │                      │
#                         └──(invalid)────────────┘← visual loop via field_router→chatbot
# =========================================================

# flow = StateGraph(botState)

# flow.add_node("chatbot",      chatbot)
# flow.add_node("validator",    validator)
# flow.add_node("field_router", field_router)

# flow.add_edge(START,      "chatbot")
# flow.add_edge("chatbot",  "validator")

# flow.add_conditional_edges(
#     "validator",
#     route_validator,
#     {
#         "field_router": "field_router",
#         "end":          END,
#     }
# )

# # field_router → END (creates the loop-back visual arrow)
# flow.add_conditional_edges(
#     "field_router",
#     route_field_router,
#     {"end": END}
# )

# # =========================================================
# # COMPILE
# # =========================================================

# graph = flow.compile()

# png_bytes = graph.get_graph().draw_mermaid_png()
# with open("graph.png", "wb") as f:
#     f.write(png_bytes)

# print("graph generated")










# from state import botState
# from nodes.validate_node import validate_node

# from langgraph.graph import StateGraph, START, END


# # =========================================================
# # NODES
# # =========================================================

# def agent(obj: botState) -> botState:
#     """Validates input, updates state."""
#     return validate_node(obj)


# def tools(obj: botState) -> botState:
#     """Dummy node — exists only to create the loop arrow in graph image."""
#     return obj


# # =========================================================
# # ROUTERS
# # =========================================================

# def route_agent(obj: botState) -> str:
#     # valid   → go through tools (creates loop arrow: tools → agent)
#     # invalid → exit directly   (no looping)
#     return "tools" if obj["valid"] else "end"


# def route_tools(obj: botState) -> str:
#     # always exits — no real looping happens
#     return "end"


# # =========================================================
# # GRAPH
# #
# #   START → agent ──(invalid)──────────────→ END
# #               └──(valid)──→ tools → END
# #                               ↑
# #                        (arrow points back to agent in image)
# # =========================================================

# flow = StateGraph(botState)

# flow.add_node("agent", agent)
# flow.add_node("tools", tools)

# flow.add_edge(START, "agent")

# flow.add_conditional_edges(
#     "agent",
#     route_agent,
#     {
#         "tools": "tools",
#         "end":   END,
#     }
# )

# flow.add_conditional_edges(
#     "tools",
#     route_tools,
#     {
#         "end": END,
#     }
# )

# # =========================================================
# # COMPILE
# # =========================================================

# graph = flow.compile()

# png_bytes = graph.get_graph().draw_mermaid_png()
# with open("graph.png", "wb") as f:
#     f.write(png_bytes)

# print("graph generated")




from state import botState
from nodes.validate_node import validate_node

from langgraph.graph import StateGraph, START, END


def agent(obj: botState) -> botState:
    return validate_node(obj)


flow = StateGraph(botState)
flow.add_node("agent", agent)
flow.add_edge(START, "agent")
flow.add_edge("agent", END)

graph = flow.compile()

png_bytes = graph.get_graph().draw_mermaid_png()
with open("graph.png", "wb") as f:
    f.write(png_bytes)

print("graph generated")