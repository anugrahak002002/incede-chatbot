import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel, Field
from tools import TOOLS, FIELD_TOOL_MAP

load_dotenv()


# =========================================================
# PYDANTIC STRUCTURED OUTPUT SCHEMA
# =========================================================

class AgentResponse(BaseModel):
    valid:   bool = Field(description="Whether the user input was valid for the current field")
    value:   str  = Field(description="The cleaned/extracted value if valid, empty string if not")
    message: str  = Field(description="Friendly conversational reply to show the user")


# =========================================================
# LLM WITH TOOLS BOUND
# =========================================================

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0.5,
)

# bind all validation tools to the LLM
llm_with_tools = llm.bind_tools(TOOLS)

# structured output LLM for final response
llm_structured = llm.with_structured_output(AgentResponse)


# =========================================================
# MAIN AGENT FUNCTION
# =========================================================

def run_agent(field: str, user_input: str) -> dict:
    """
    Uses LangChain tool-calling:
    1. LLM decides which tool to call based on current field
    2. Tool executes and returns validation result
    3. LLM generates structured conversational response
    """

    next_field_hint = {
        "name":        "phone number",
        "phone":       "email address",
        "email":       "description (or skip)",
        "description": "nothing - form is complete",
    }

    system = SystemMessage(content=f"""You are a friendly conversational form assistant.
You are currently collecting the user's {field}.
Use the appropriate validation tool to validate the input.
After validation, respond naturally and conversationally.
If the user asks a question or chats, answer it helpfully then guide back to {field}.
Next field after {field} will be: {next_field_hint[field]}""")

    human = HumanMessage(content=f"Current field: {field}\nUser said: {user_input}")

    # Step 1 — LLM decides which tool to call
    ai_response = llm_with_tools.invoke([system, human])

    # Step 2 — Execute tool calls if any
    tool_result = None
    if ai_response.tool_calls:
        tool_call = ai_response.tool_calls[0]
        tool_name = tool_call["name"]
        tool_args = tool_call["args"]

        # find and run the matching tool
        for t in TOOLS:
            if t.name == tool_name:
                tool_result = t.invoke(tool_args)
                break

    # Step 3 — If tool ran successfully, use its result
    if tool_result and isinstance(tool_result, dict):
        return {
            "valid":   tool_result.get("valid", False),
            "value":   tool_result.get("value", ""),
            "message": tool_result.get("message", "Please try again.")
        }

    # Step 4 — No tool call (user was chatting) — use structured output
    structured = llm_structured.invoke([
        system,
        human,
        HumanMessage(content=f"The user seems to be chatting. Answer their message naturally, then ask for their {field} again. Set valid=false.")
    ])

    return {
        "valid":   structured.valid,
        "value":   structured.value,
        "message": structured.message
    }