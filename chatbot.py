import gradio as gr
import streamlit as st
from agent import handle_chat



# Add a logo and title
logo_url = "/Users/pro/Documents/Documents - pro’s MacBook Pro - 1/Học Viện/Năm 4-HKII/Kỹ thuật theo dõi giám sát an toàn mạng/chatbot_sql/logo.avif"  # Replace with the actual URL of your logo
st.markdown(
    f"""
    <div style="display: flex; justify-content: space-between; align-items: center;">
        <h1>Chinook Tunes</h1>
        <img src="{logo_url}" style="height: 50px;">
    </div>
    """,
    unsafe_allow_html=True,
)



# Initialize chat history
if "history" not in st.session_state:
    st.session_state["history"] = []



# Function to handle message sending
def send_message():
    if st.session_state.user_input:
        user_message = st.session_state.user_input
        response = handle_chat(user_message)
        st.session_state["history"].append(("You", user_message))
        st.session_state["history"].append(("CT", response['output']))
        st.session_state.user_input = ""
        # st.experimental_rerun()
# User input field
user_input = st.text_input(
    "Enter your message:", key="user_input", on_change=send_message
)
# Send button
send_button = st.button("Send")

if send_button and st.session_state.user_input:
    send_message()




# Display chat history
for idx, (user, message) in enumerate(reversed(st.session_state["history"])):
    if user == "You":
        st.markdown(f"<div style='text-align: right;'><b>You:</b> {message}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div style='text-align: left;'><b>CT:</b> {message}</div>", unsafe_allow_html=True)


# Horizontal line for separation
st.markdown("---")


