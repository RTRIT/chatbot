# === Import Libraries ===
import logging
import re
import ast
import streamlit as st
from sqlalchemy.exc import OperationalError
from agent import handle_chat
from vulnChatbot import handleChatVuln



# === UI Settings: Logo and Title ===
logo_url = "/Users/pro/Documents/Documents - pro's MacBook Pro - 1/Học Viện/Năm 4-HKII/Kỹ thuật theo dõi giám sát an toàn mạng/chatbot_sql/logo.png"
st.markdown(
    f"""
    <div style="display: flex; justify-content: space-between; align-items: center;">
        <h1>Chinook Tunes</h1>
        <img src="{logo_url}" style="height: 50px;">
    </div>
    """,
    unsafe_allow_html=True,
)


# === Initialize Session State ===
if "history" not in st.session_state:
    st.session_state["history"] = []

options = ["SQLi Chatbot", "Agent Chatbot"]
queryVulnChatbot = [
    "Find album titled <Name of the Album>",
    "What tracks are in the album <Name of the Album>?",
    "Show me albums by <Name of the Artist>",
    "List all songs by <Name of The Artist>",
    "Find track called <Name of the Song>",

]


# Main chatbot selection dropdown
chatbot_type = st.selectbox("Choose a chatbot:", options, key="dropdown_selection")
selected = ""

# Conditional second dropdown
if chatbot_type == "SQLi Chatbot":
    selected = st.selectbox("Choose a query:", queryVulnChatbot, key="dropdown_selection2")
    
else:
    st.write("Agent Chatbot selected. No predefined queries.")


# Add a flag to signal when to clear input
if "clear_input" not in st.session_state:
    st.session_state["clear_input"] = False


# === Message Sending Function ===
def send_message():
    user_message = st.session_state.user_input
    print("Send message to agent chatbot")
    # user_message = st.session_state.dropdown_selection
    if user_message:
        try:
            response = handle_chat(user_message)
            st.session_state["history"].append(("You", user_message))
            st.session_state["history"].append(("CT", response['output']))
        except OperationalError as e:
            logging.error(f"Database error: {e}")
            st.session_state["history"].append(("You", user_message))
            st.session_state["history"].append(("CT", "⚠️ A database error occurred. Please try again later."))
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            st.session_state["history"].append(("You", user_message))
            st.session_state["history"].append(("CT", "⚠️ An unexpected error occurred."))
        finally:
            st.session_state["clear_input"] = True


def send_message_vulChatbot(index, query):
    response = handleChatVuln(index, query)
    print("semd_message_handleChatVuln: "+str(index))

    # print(response)
    user_message = st.session_state.user_input
    # user_message = st.session_state.dropdown_selection
    if user_message:
        try:
            response = handleChatVuln(index, query)
            st.session_state["history"].append(("You", re.sub(r"<.*?>", query, queryVulnChatbot[index])))
            st.session_state["history"].append(("CT", response['output']))
            return response
        except OperationalError as e:
            logging.error(f"Database error: {e}")
            st.session_state["history"].append(("You", re.sub(r"<.*?>", query, queryVulnChatbot[index])))
            st.session_state["history"].append(("CT", "⚠️ A database error occurred. Please try again later."))
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            st.session_state["history"].append(("You", re.sub(r"<.*?>", query, queryVulnChatbot[index])))
            st.session_state["history"].append(("CT", "⚠️ An unexpected error occurred."))
        finally:
            st.session_state["clear_input"] = True




import streamlit as st

def send_message_wrapper():
    user_input = st.session_state.get("user_input", "").strip()
    if user_input and chatbot_type != "SQLi Chatbot":
        send_message()

if st.session_state["clear_input"]:
    st.session_state["user_input"] = ""
    st.session_state["clear_input"] = False 

# Text input with on_change handler
st.text_input(
    "Enter your message:",
    key="user_input",
    on_change=send_message_wrapper
)



#Get user input
user_input = st.session_state.get("user_input", "").strip()

if user_input:
    if chatbot_type == "SQLi Chatbot":
        print("selected: " + selected)
        selected_index = queryVulnChatbot.index(selected)

        if selected_index == 0:
            # Find album by title
            send_message_vulChatbot(1, user_input)

        elif selected_index == 1:
    # Get tracks from album
            result = send_message_vulChatbot(3, user_input)
            tuple_str = result["output"].splitlines()[0]
            tuple_val = ast.literal_eval(tuple_str)  # Convert '(2,)' → (2,)
            album_id = tuple_val[0]
            # print("this is index: "+str(index))
            try:
                send_message_vulChatbot(4, album_id)
            except Exception as e:
                print("Failed to parse AlbumId:", e)

            #             print("Failed to parse AlbumId:", e)
            # send_message_vulChatbot(4, str(index))
            # if album_result and "output" in album_result:
            #     lines = album_result["output"].splitlines()
            #     if lines:
            #         # Evaluate the string as a tuple safely
            #         try:
            #             album_tuple = eval(lines[0])  # ⚠️ only safe here because you control the DB
            #             album_id = str(album_tuple[0])
            #             print("Parsed AlbumId:", album_id)

            #             # Now use AlbumId to get tracks
            #             send_message_vulChatbot(4, album_id)
            #         except Exception as e:
            #             print("Failed to parse AlbumId:", e)
            #     else:
            #         print("No AlbumId found.")
    else:
        send_message()







# === Chat History Display ===
for user, message in reversed(st.session_state["history"]):
    alignment = "right" if user == "You" else "left"
    st.markdown(f"<div style='text-align: {alignment};'><b>{user}:</b> {message}</div>", unsafe_allow_html=True)


# === Footer Separator ===
st.markdown("---")
