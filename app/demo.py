import streamlit as st
from dotenv import load_dotenv
import os, json
from openpipe import OpenAI
load_dotenv()

def get_current_weather(location, unit="fahrenheit"):
    """Get the current weather in a given location"""
    if "tokyo" in location.lower():
        return json.dumps({"location": "Tokyo", "temperature": "10", "unit": unit})
    elif "san francisco" in location.lower():
        return json.dumps({"location": "San Francisco", "temperature": "72", "unit": unit})
    elif "paris" in location.lower():
        return json.dumps({"location": "Paris", "temperature": "22", "unit": unit})
    else:
        return json.dumps({"location": location, "temperature": "unknown"})

def main():
    st.title("Tool Call App")

    # Configuration Page
    if "config" not in st.session_state:
        st.session_state.config = {
            "get_current_weather": {"enabled": True, "unit": "fahrenheit", "fields": ["location", "temperature", "unit"]},
            "browse_company_items": {"enabled": True, "fields": ["keyword"]},
            "contact_support": {"enabled": True, "fields": ["message"]},
            "draft_email": {"enabled": True, "fields": ["to", "from", "subject", "body"]},
            "analyze_sql_database": {"enabled": True, "fields": ["database", "query"]},
            "search_jira_cards": {"enabled": True, "fields": ["query"]},
        }

    if not st.session_state.get("model"):
        st.session_state.model = "gpt-4o"

    with st.sidebar:
        st.header("Configuration")
        for tool, settings in st.session_state.config.items():
            with st.expander(tool):
                settings["enabled"] = st.checkbox("Enabled", value=settings["enabled"], key=f"{tool}_enabled")
                if tool == "get_current_weather":
                    settings["unit"] = st.selectbox("Unit", ["fahrenheit", "celsius"], index=0 if settings["unit"] == "fahrenheit" else 1, key=f"{tool}_unit")
                if "fields" not in settings:
                    settings["fields"] = []
                settings["fields"] = st.multiselect("Fields to return", options=[field for field in settings["fields"]], default=settings["fields"], key=f"{tool}_fields")
                st.session_state.config[tool] = settings

        st.header("Model")
        st.session_state.model = st.selectbox("Choose a Model", ["gpt-4o", "gpt-4o-mini", "gpt-4", "gpt-3.5-turbo", "anthropic:claude-3-5-sonnet-20240620", "anthropic:claude-3-opus-20240229", "openpipe:llama3-1-8b"])

    # Testing Page
    st.header("Tool Call Tests")
    st.write("Try asking questions that will make the GPT call the tools. For example, 'What is the weather in Tokyo?' or 'Browse for shoes.'")
    st.divider()

    OPENAI_API_KEY = os.getenv("OPENPIPE_API_KEY")

    client = OpenAI(
        api_key=os.environ.get("OPENAI_API_KEY"),
        openpipe={
            "api_key": os.getenv("OPENPIPE_API_KEY"),
        }
    )

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("What is up?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            tools = []
            if st.session_state.config["get_current_weather"]["enabled"]:
                tools.append({
                    "type": "function",
                    "function": {
                        "name": "get_current_weather",
                        "description": "Get the current weather in a given location",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "location": {
                                    "type": "string",
                                    "description": "The city and state, e.g. San Francisco, CA",
                                },
                                "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]},
                            },
                            "required": ["location"],
                        },
                        "fields": st.session_state.config["get_current_weather"]["fields"]
                    },
                })
            if st.session_state.config["browse_company_items"]["enabled"]:
                tools.append({
                    "type": "function",
                    "function": {
                        "name": "browse_company_items",
                        "description": "Browse Company Items",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "keyword": {
                                    "type": "string",
                                    "description": "The Search Keyword",
                                },
                            },
                            "required": ["keyword"],
                        },
                        "fields": st.session_state.config["browse_company_items"]["fields"]
                    },
                })
            if st.session_state.config["contact_support"]["enabled"]:
                tools.append({
                    "type": "function",
                    "function": {
                        "name": "contact_support",
                        "description": "Contact Company Support",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "message": {
                                    "type": "string",
                                    "description": "Message to send to support",
                                },
                            },
                            "required": ["message"],
                        },
                        "fields": st.session_state.config["contact_support"]["fields"]
                    },
                })
            if st.session_state.config["draft_email"]["enabled"]:
                tools.append({
                    "type": "function",
                    "function": {
                        "name": "draft_email",
                        "description": "Draft an email",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "to": {
                                    "type": "string",
                                    "description": "The recipient of the email (default to 'User')",
                                },
                                "from": {
                                    "type": "string",
                                    "description": "The sender of the email (default to 'Assistant')",
                                },
                                "subject": {
                                    "type": "string",
                                    "description": "The subject of the email",
                                },
                                "body": {
                                    "type": "string",
                                    "description": "The body of the email",
                                },
                            },
                            "required": ["to", "from", "subject", "body"],
                        },
                        "fields": st.session_state.config["draft_email"]["fields"]
                    },
                })
            if st.session_state.config["analyze_sql_database"]["enabled"]:
                tools.append({
                    "type": "function",
                    "function": {
                        "name": "analyze_sql_database",
                        "description": "Analyze a SQL database",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "database": {
                                    "type": "string",
                                    "description": "The name of the database",
                                },
                                "query": {
                                    "type": "string",
                                    "description": "The SQL query to run",
                                },
                            },
                            "required": ["database", "query"],
                        },
                        "fields": st.session_state.config["analyze_sql_database"]["fields"]
                    },
                })
            if st.session_state.config["search_jira_cards"]["enabled"]:
                tools.append({
                    "type": "function",
                    "function": {
                        "name": "search_jira_cards",
                        "description": "Search through Jira cards",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "query": {
                                    "type": "string",
                                    "description": "The keyword query to run",
                                },
                            },
                            "required": ["query"],
                        },
                        "fields": st.session_state.config["search_jira_cards"]["fields"]
                    },
                })

            stream = client.chat.completions.create(
                model=st.session_state.model,
                messages=[
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ],
                stream=False,
                tools=tools if tools else None,
            )
            if stream.choices[0].message.tool_calls:
                output = json.loads(stream.choices[0].message.tool_calls[0].function.arguments)
                st.write("Tool Call: ", stream.choices[0].message.tool_calls[0].function)
                content = "Called on function " + stream.choices[0].message.tool_calls[0].function.name 
            else:
                content = stream.choices[0].message.content
                st.write(content)

            st.session_state.messages.append({"role": "assistant", "content": content})

if __name__ == "__main__":
    main()
