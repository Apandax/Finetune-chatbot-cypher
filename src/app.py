import os
import openai
import pandas as pd
import streamlit as st
from streamlit_chat import message
from driver import read_query
from train_cypher import examples
from openaigpt4 import generate_cypher
from neo4j import GraphDatabase
from dotenv import load_dotenv
load_dotenv()

st.set_page_config(page_title="💬 Ask us, Weeping Wranglers ")
st.title("💬 Ask us, Weeping Wranglers ")
st.info("Ask us V0.01 - Weeping Wranglers | Powered By GPT-4",icon="ℹ️")

# Define color palette
COLOR_BLACK = "#000000"
COLOR_DARK_BLUE = "#14213D"
COLOR_ORANGE = "#FCA311"
COLOR_LIGHT_GREY = "#E5E5E5"
COLOR_WHITE = "#FFFFFF"

# ------------------ Custom CSS ------------------

def inject_custom_css():
    st.markdown(f"""
    <style>
    /* Set the background color of the entire app */
    .stApp {{
        background-color: {COLOR_DARK_BLUE};
        color: {COLOR_WHITE};
    }}

    /* Customize the sidebar */
    .css-1d391kg {{
        background-color: {COLOR_BLACK};
        color: {COLOR_WHITE};
    }}

    /* Customize headers */
    h1, h2, h3, h4, h5, h6 {{
        color: {COLOR_ORANGE};
    }}

    /* Customize Streamlit info boxes */
    .stInfo {{
        background-color: {COLOR_LIGHT_GREY};
        color: {COLOR_BLACK};
    }}

    /* Customize buttons */
    .css-1emrehy.edgvbvh3 {{
        background-color: {COLOR_ORANGE};
        color: {COLOR_WHITE};
    }}
    .css-1emrehy.edgvbvh3:hover {{
        background-color: {COLOR_WHITE};
        color: {COLOR_ORANGE};
    }}

    /* Customize chat messages */
    .streamlit-chat-message.user {{
        background-color: {COLOR_LIGHT_GREY};
        color: {COLOR_BLACK};
    }}
    .streamlit-chat-message.assistant {{
        background-color: {COLOR_ORANGE};
        color: {COLOR_WHITE};
    }}
    </style>
    """, unsafe_allow_html=True)

inject_custom_css()


openai.api_key = os.getenv("OPENAI_KEY")
host = os.getenv('HOST')
user = os.getenv('USER')
password = os.getenv('PASSWORD')
driver = GraphDatabase.driver(host, auth=(user, password))

def generate_response(prompt, cypher=True):
    usr_input = [{"role": "user", "content": prompt}]
    ai_reponse = generate_cypher(usr_input)
    query_result, query = read_query(driver, ai_reponse)
    return query_result, ai_reponse, query

with st.sidebar:
    st.markdown('📖 Learn more about-Me')
    
# Store LLM generated responses
if "messages" not in st.session_state.keys():
    st.session_state.messages = [{"role": "assistant", "content": "How may I help you?"}]

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if isinstance(message["content"], pd.DataFrame):
            response_session = st.table(message["content"],)
        else:
            response_session = st.write(message["content"],)

if user_input := st.chat_input():
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
            st.write(user_input)

if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        # Generate the response, ai_response, and query
        df_result, ai_response, query = generate_response(user_input)
        
        response = df_result
        print(response)
        # Display `ai_response` as the main response content
        message = {"role": "assistant", "content": ai_response}
        # st.write(message["content"])
        
        # If `ai_response` contains a Cypher query, display it
        if "MATCH" in ai_response:
            st.write("**AI Response (Main Content):**")
            st.write(ai_response)
        if isinstance(response, pd.DataFrame):
            response_session = st.table(response)
        else:
            response_session = st.write(response)
        # # Display `query` separately if it contains a Cypher query
        # if "MATCH" in query:
        #     st.write("**Cypher Query:**")
        #     st.code(query, language="cypher")  # Syntax-highlighted code block for the query

        # Append `ai_response` to session state
        st.session_state.messages.append(message)
        
        # Append the full `response` to session state as a separate message
        if isinstance(response, str) or not response.empty:
            st.session_state.messages.append({"role": "assistant", "content": response})
            