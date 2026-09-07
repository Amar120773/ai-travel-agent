import os
import json
from openai import OpenAI
from dotenv import load_dotenv

import tools
import memory
from logger import logger

load_dotenv()

# Initialize OpenAI client (configured for Google Gemini)
def get_openai_client():
    api_key = os.environ.get("GEMINI_API_KEY")
    
    # Check Streamlit secrets if environment variable is missing
    if not api_key:
        try:
            import streamlit as st
            api_key = st.secrets.get("GEMINI_API_KEY")
        except Exception:
            pass
            
    # Use a dummy key if none is found so the app still boots up (it will error gracefully when chatting)
    return OpenAI(
        api_key=api_key or "missing_api_key",
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
    )

client = get_openai_client()

# Use Google's incredibly fast and stable Gemini 1.5 Flash model
MODEL_NAME = "gemini-1.5-flash"

def get_available_tools():
    """Define the JSON schema for tools the LLM can call."""
    return [
        {
            "type": "function",
            "function": {
                "name": "save_preference",
                "description": "Save a user's travel preference (e.g., dietary restriction, seating preference, budget).",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_id": {"type": "string", "description": "The ID of the user (e.g., 'default_user')"},
                        "preference_key": {"type": "string", "description": "The category of the preference (e.g., 'diet', 'seat', 'airline')"},
                        "preference_value": {"type": "string", "description": "The value of the preference (e.g., 'vegan', 'aisle', 'Delta')"}
                    },
                    "required": ["user_id", "preference_key", "preference_value"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "search_destinations",
                "description": "Search for travel destinations based on climate and budget.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "climate": {"type": "string", "description": "Desired climate (e.g., 'tropical', 'cold', 'temperate')"},
                        "budget": {"type": "string", "description": "Budget level (e.g., 'low', 'medium', 'high')"}
                    }
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_flight_estimate",
                "description": "Get estimated flight cost and duration.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "origin": {"type": "string"},
                        "destination": {"type": "string"}
                    },
                    "required": ["origin", "destination"]
                }
            }
        }
    ]

def execute_tool_call(tool_call):
    """Execute the local python function corresponding to the LLM tool call."""
    function_name = tool_call.function.name
    try:
        arguments = json.loads(tool_call.function.arguments)
    except json.JSONDecodeError:
        logger.error(f"Failed to decode JSON arguments from LLM: {tool_call.function.arguments}")
        return "Error: Invalid arguments provided by LLM."
    
    logger.info(f"Agent routed to tool: {function_name}")
    logger.debug(f"Tool arguments: {arguments}")
    
    try:
        if function_name == "save_preference":
            return memory.save_preference(**arguments)
        elif function_name == "search_destinations":
            return tools.search_destinations(**arguments)
        elif function_name == "get_flight_estimate":
            return tools.get_flight_estimate(**arguments)
        else:
            logger.error(f"LLM attempted to call unknown function: {function_name}")
            return f"Error: Unknown function '{function_name}'"
    except TypeError as e:
        logger.error(f"Type error during tool execution (likely missing arguments): {e}")
        return f"Error: Incorrect arguments for tool {function_name}."
    except Exception as e:
        logger.exception(f"Unexpected error executing tool {function_name}: {e}")
        return f"Error: An unexpected error occurred while executing {function_name}."

def run_agent_loop(messages, user_id="default_user"):
    """
    The deterministic Observe-Think-Act loop.
    We pass the conversation history, and loop if the agent wants to call tools.
    """
    logger.info("Starting Observe-Think-Act loop.")
    
    # System prompt injecting memory
    system_message = {
        "role": "system",
        "content": (
            "You are a helpful, self-learning Travel Assistant. "
            "Always check if the user is stating a preference and save it using the 'save_preference' tool. "
            "When suggesting travel destinations or flights, always check the user's preferences first. "
            f"Here are the user's known preferences: {memory.get_user_preferences(user_id)}\n"
            "Use these preferences to tailor your travel recommendations."
        )
    }
    
    current_messages = [system_message] + messages
    iteration_count = 0
    MAX_ITERATIONS = 5  # Prevent infinite loops if LLM goes crazy
    
    while iteration_count < MAX_ITERATIONS:
        iteration_count += 1
        logger.debug(f"Loop iteration {iteration_count}")
        
        try:
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=current_messages,
                tools=get_available_tools(),
                tool_choice="auto"
            )
        except Exception as e:
            logger.exception(f"LLM API Call failed: {e}")
            return f"**API Error Details:**\n```\n{str(e)}\n```\n\nPlease copy this error and share it so I can fix it!"
            
        response_message = response.choices[0].message
        current_messages.append(response_message)
        
        if response_message.tool_calls:
            logger.info(f"Agent decided to use {len(response_message.tool_calls)} tool(s).")
            for tool_call in response_message.tool_calls:
                tool_result = execute_tool_call(tool_call)
                current_messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": tool_call.function.name,
                    "content": str(tool_result)
                })
        else:
            logger.info("Agent provided a final response without calling tools.")
            return response_message.content
            
    logger.warning("Agent reached max iterations without providing a final response.")
    return "I'm sorry, I had to stop thinking because it was taking too long. Please try asking your question differently."
