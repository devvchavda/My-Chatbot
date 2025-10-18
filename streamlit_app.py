import os
os.environ["STREAMLIT_HOME"] = "/tmp/.streamlit"
import streamlit as st
from chat_langraph import system, workflow, HumanMessage, AIMessage, get_all_chat_ids, ToolMessage
import uuid
import base64
import io

st.set_page_config(layout="wide")
st.title("My Chatbot")

TEMP_DIR = "/tmp"
os.makedirs(TEMP_DIR, exist_ok=True)

def set_title(messages):
    if messages:
        title = "New Chat"
        st.session_state.chat_dict[st.session_state.current_chat_id] = title

def set_config():
    return {"configurable": {"thread_id": st.session_state.current_chat_id}}

def load_session_state():
    if "chats" not in st.session_state:
        st.session_state.chats = get_all_chat_ids()
    if "current_chat_id" not in st.session_state:
        if len(st.session_state.chats) > 0:
            st.session_state.current_chat_id = st.session_state.chats[-1]
        else:
            new_id = str(uuid.uuid4())
            st.session_state.chats.append(new_id)
            st.session_state.current_chat_id = new_id
    if "chat_dict" not in st.session_state:
        st.session_state.chat_dict = {}

def render_sidebar():
    with st.sidebar:
        st.title("Chats")
        if st.button("➕ New Chat"):
            new_id = str(uuid.uuid4())
            st.session_state.chats.append(new_id)
            st.session_state.current_chat_id = new_id
            config = {"configurable": {"thread_id": new_id}}
            workflow.update_state(config, {"messages": [system]})
            st.session_state.chat_dict[new_id] = "New Chat"
            st.rerun()

        for chat_id in st.session_state.chats:
            if st.button(st.session_state.chat_dict.get(chat_id, "New Chat"), key=chat_id):
                st.session_state.current_chat_id = chat_id
        
        st.markdown("---")

def create_download_link(file_path: str, label: str = None) -> str:
    if not os.path.exists(file_path): return ""
    try:
        with open(file_path, "rb") as f: data = f.read()
        b64 = base64.b64encode(data).decode()
        label = label or f"📥 Download {os.path.basename(file_path)}"
        href = f'<a href="data:file/octet-stream;base64,{b64}" download="{os.path.basename(file_path)}">{label}</a>'
        return href
    except Exception as e:
        return f"Error creating download link: {e}"

def loadchats():
    if "current_chat_id" not in st.session_state: return []
    config = {"configurable": {"thread_id": st.session_state.current_chat_id}}
    state = workflow.get_state(config)
    messages = state.values.get("messages", [])
    for message in messages:
        if not message.content: continue
        if isinstance(message, HumanMessage):
            with st.chat_message("human"): st.write(message.content)
        elif isinstance(message, AIMessage):
            with st.chat_message("assistant"): st.write(message.content)
        elif isinstance(message, ToolMessage):
            with st.chat_message("assistant"):
                st.info("Using Appropriate tool")
                if message.name == "plot_graph" and "Filepath" in message.content:
                    st.image(message.content.split(":")[1], "📊")
                if "Filepath" in message.content:
                    st.markdown(create_download_link(message.content.split(":")[1]), unsafe_allow_html=True)
    return messages

load_session_state()

if "current_chat_id" in st.session_state:
    loadchats()
    
    user_input = st.chat_input("Your message:")
    if user_input:
        with st.chat_message("human"):
            st.write(user_input)

        with st.chat_message("assistant"):
            with st.spinner("Assistant is thinking..."):
                response_placeholder = st.empty()
                full_response = ""
                for message, metadata in workflow.stream(
                    {"messages": [system, HumanMessage(user_input)]},
                    config={"configurable": {"thread_id": st.session_state.current_chat_id}},
                    stream_mode="messages",
                ):
                    if isinstance(message, AIMessage):
                        if isinstance(message.content, list):
                            full_response += " ".join(message.content)
                        else:
                            full_response += message.content
                    elif isinstance(message, ToolMessage):
                        st.info("Using Appropriate tool")
                    response_placeholder.markdown(full_response + " ")
                st.rerun()
