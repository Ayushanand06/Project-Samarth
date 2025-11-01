import streamlit as st
import config
from agent import create_agent_executor

st.set_page_config(page_title="AgriClimate Q&A India", page_icon="🌾", layout="wide")
st.title("🌾 AgriClimate Q&A India")
st.caption(f"An intelligent assistant for India's agricultural & climate data (Powered by {config.GROQ_MODEL_NAME})")

if not config.GROQ_API_KEY:
    st.error("Groq API key is missing. Please check your .env file.")
    st.stop()

if "agent_executor" not in st.session_state:
    st.session_state.agent_executor = create_agent_executor()
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Compare rainfall and top crops in states like Punjab and Bihar from 2010 to 2012..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        with st.spinner("Analyzing local datasets and generating response..."):
            try:
                response = st.session_state.agent_executor.invoke({
                    "input": prompt,
                    "chat_history": st.session_state.messages
                })
                output = response["output"]
                st.markdown(output)
                st.session_state.messages.append({"role": "assistant", "content": output})
            except Exception as e:
                st.error(f"An error occurred: {e}")
                st.session_state.messages.append({"role": "assistant", "content": str(e)})