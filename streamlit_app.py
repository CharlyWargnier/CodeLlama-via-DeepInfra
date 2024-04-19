import streamlit as st
import openai
import requests

st.set_page_config(page_title="CodeLlama Playground - via DeepInfra", page_icon='🦙')

MODEL_IMAGES = {
    "meta-llama/Meta-Llama-3-8B-Instruct": "https://em-content.zobj.net/source/twitter/376/llama_1f999.png",  # Add the emoji for the Meta-Llama model
    "codellama/CodeLlama-34b-Instruct-hf": "https://em-content.zobj.net/source/twitter/376/llama_1f999.png",
    "mistralai/Mistral-7B-Instruct-v0.1": "https://em-content.zobj.net/source/twitter/376/tornado_1f32a-fe0f.png",
    "mistralai/Mixtral-8x7B-Instruct-v0.1": "https://em-content.zobj.net/source/twitter/376/tornado_1f32a-fe0f.png",
}

# Create a mapping from formatted model names to their original identifiers
def format_model_name(model_key):
    parts = model_key.split('/')
    model_name = parts[-1]  # Get the last part after '/'
    name_parts = model_name.split('-')

    # Custom formatting for specific models
    if "Meta-Llama-3-8B-Instruct" in model_key:
        return "Llama 3 8B-Instruct"
    else:
        # General formatting for other models
        formatted_name = ' '.join(name_parts[:-2]).title()  # Join them into a single string with title case
        return formatted_name

formatted_names_to_identifiers = {
    format_model_name(key): key for key in MODEL_IMAGES.keys()
}

# Debug to ensure names are formatted correctly
#st.write("Formatted Model Names to Identifiers:", formatted_names_to_identifiers)

selected_formatted_name = st.sidebar.radio(
    "Select LLM Model",
    list(formatted_names_to_identifiers.keys())
)

selected_model = formatted_names_to_identifiers[selected_formatted_name]

if MODEL_IMAGES[selected_model].startswith("http"):
    st.image(MODEL_IMAGES[selected_model], width=90)
else:
    st.write(f"Model Icon: {MODEL_IMAGES[selected_model]}", unsafe_allow_html=True)

# Display the selected model using the formatted name
model_display_name = selected_formatted_name  # Already formatted
# st.write(f"Model being used: `{model_display_name}`")

st.sidebar.markdown('---')

API_KEY = st.secrets["api_key"]

openai.api_base = "https://api.deepinfra.com/v1/openai"
MODEL_CODELLAMA = selected_model

def get_response(api_key, model, user_input, max_tokens, top_p):
    openai.api_key = api_key
    try:
        if "meta-llama/Meta-Llama-3-8B-Instruct" in model:
            # Assume different API setup for Meta-Llama
            chat_completion = requests.post(
                "https://api.deepinfra.com/v1/openai/chat/completions",
                headers={"Authorization": f"Bearer {api_key}"},
                json={
                    "model": model,
                    "messages": [{"role": "user", "content": user_input}],
                    "max_tokens": max_tokens,
                    "top_p": top_p
                }
            ).json()
            return chat_completion['choices'][0]['message']['content'], None
        else:
            # Existing setup for other models
            chat_completion = openai.ChatCompletion.create(
                model=model,
                messages=[{"role": "user", "content": user_input}],
                max_tokens=max_tokens,
                top_p=top_p
            )
            return chat_completion.choices[0].message.content, None
    except Exception as e:
        return None, str(e)



# Adjust the title based on the selected model
st.header(f"`{model_display_name}` Model")

with st.expander("About this app"):
    st.write(f"""
    This Chatbot app allows users to interact with various models including the new LLM models hosted on DeepInfra's OpenAI compatible API.
    For more info, you can refer to [DeepInfra's documentation](https://deepinfra.com/docs/advanced/openai_api).

    💡 For decent answers, you'd want to increase the `Max Tokens` value from `100` to `500`. 
    """)

if "api_key" not in st.session_state:
    st.session_state.api_key = ""

with st.sidebar:
    max_tokens = st.slider('Max Tokens', 10, 500, 100)
    top_p = st.slider('Top P', 0.0, 1.0, 0.5, 0.05)

if max_tokens > 100:
    user_provided_api_key = st.text_input("👇 Your DeepInfra API Key", value=st.session_state.api_key, type='password')
    if user_provided_api_key:
        st.session_state.api_key = user_provided_api_key
    if not st.session_state.api_key:
        st.warning("❄️ If you want to try this app with more than `100` tokens, you must provide your own DeepInfra API key. Get yours here → https://deepinfra.com/dash/api_keys")

if max_tokens <= 100 or st.session_state.api_key:
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": "How may I assist you today?"}]
        
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])
    
    if prompt := st.chat_input():
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response, error = get_response(st.session_state.api_key, MODEL_CODELLAMA, prompt, max_tokens, top_p)
                if error:
                    st.error(f"Error: {error}") 
                else:
                    placeholder = st.empty()
                    placeholder.markdown(response)
                    message = {"role": "assistant", "content": response}
                    st.session_state.messages.append(message)

# Clear chat history function and button
def clear_chat_history():
    st.session_state.messages = [{"role": "assistant", "content": "How may I assist you today?"}]
st.sidebar.button('Clear Chat History', on_click=clear_chat_history)
