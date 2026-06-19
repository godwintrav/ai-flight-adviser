import os
import json
from dotenv import load_dotenv
from openai import OpenAI
import gradio as gr
from prompts import system_prompt
from tool_definition import tools
from tools import set_user_preferences, get_flight_prices, search_airports

load_dotenv(override=True)

openai_api_key = os.getenv('OPENAI_API_KEY')
if openai_api_key:
    print(f"OpenAI API Key exists and begins {openai_api_key[:8]}")
else:
    print("OpenAI API Key not set")
    
MODEL = "gpt-4.1-mini"
openai = OpenAI()

FUNCTIONS = {
    "set_user_preferences": set_user_preferences,
    "get_flight_prices": get_flight_prices,
    "search_airports": search_airports,
}

def handle_tool_calls(message):
    responses = []
    for tool_call in message.tool_calls:
        if tool_call.function.name in FUNCTIONS:
            arguments = json.loads(tool_call.function.arguments)
            tool_response = FUNCTIONS[tool_call.function.name](**arguments)
            print("TOOL RESPONSE", tool_response)
            responses.append({
                "role": "tool",
                "content": json.dumps(tool_response),
                "tool_call_id": tool_call.id
            })   
    return responses

def chat(history):
    history = [{"role": h["role"], "content":h["content"]} for h in history]
    messages = [{"role": "system", "content": system_prompt}] + history
    response = openai.chat.completions.create(model=MODEL, messages=messages, tools=tools)

    while response.choices[0].finish_reason == "tool_calls":
        message = response.choices[0].message
        print("AI TOOL MESSAGE", message)
        responses = handle_tool_calls(message)
        messages.append(message)
        messages.extend(responses)
        response = openai.chat.completions.create(model=MODEL, messages=messages, tools=tools)
    
    reply = response.choices[0].message.content
    history += [{"role": "assistant", "content": reply}]
    return history

def put_message_in_chatbot(message, history):
        return "", history + [{"role":"user", "content":message}]

# UI definition

with gr.Blocks() as ui:
    with gr.Row():
        chatbot = gr.Chatbot(height=500)
    with gr.Row():
        message = gr.Textbox(label="Chat with our AI Flight Assistant:")

# Hooking up events to callbacks

    message.submit(put_message_in_chatbot, inputs=[message, chatbot], outputs=[message, chatbot]).then(
        chat, inputs=chatbot, outputs=[chatbot]
    )

ui.launch( 
    server_name="0.0.0.0",
    server_port=int(os.getenv("PORT", 7860)),
    )