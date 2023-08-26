import streamlit as st
import openai

st.set_page_config(page_title="CodeLlama Playground - via DeepInfra", page_icon='🦙')

st.image('https://images.emojiterra.com/twitter/v14.0/1024px/1f999.png', width = 90)

API_KEY = st.secrets["api_key"]

openai.api_base = "https://api.deepinfra.com/v1/openai"
MODEL_CODELLAMA = "codellama/CodeLlama-34b-Instruct-hf"

def get_response(api_key, model, user_input, max_tokens, top_p):
    try:
        openai.api_key = API_KEY
        chat_completion = openai.ChatCompletion.create(
            model=model,
            messages=[{"role": "user", "content": user_input}],
            max_tokens=max_tokens,
            top_p=top_p
        )
        return chat_completion.choices[0].message.content, None
    except Exception as e:
        return None, str(e)

st.header("Meta's `CodeLlama` via [DeepInfra](https://deepinfra.com/)")

with st.expander("About this app"):
    st.write("""
    This Chatbot app allows users to interact with the new [CodeLlama model](https://about.fb.com/news/2023/08/code-llama-ai-for-coding/) from Meta hosted on DeepInfra's OpenAI compatible API.
    For more info, you can refer to [DeepInfra's documentation](https://deepinfra.com/docs/advanced/openai_api) -- You must set the model to `"codellama/CodeLlama-34b-Instruct-hf"`.

    💡 For decent answers, you'd want to increase the `Max Tokens` value from `100` to `500`. 


    """)

if "api_key" not in st.session_state:
    st.session_state.api_key = ""

with st.sidebar:
    max_tokens = st.slider('Max Tokens', 10, 500, 100,)
    top_p = st.slider('Top P', 0.0, 1.0, 0.5, 0.05)

if max_tokens > 100:
    user_provided_api_key = st.text_input("👇 Your DeepInfra API Key", value=st.session_state.api_key, type = 'password')
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
