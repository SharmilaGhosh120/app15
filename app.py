# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import os
from datetime import datetime
import requests
import re
import base64

# --- Streamlit frontend ---

# Ensure queries.csv exists with the correct columns
CSV_FILE = "queries.csv"
if not os.path.exists(CSV_FILE):
    pd.DataFrame(columns=["student_id", "Query", "Timestamp", "response"]).to_csv(CSV_FILE, index=False)

# Set page configuration with Ky’ra favicon/icon
# Use a bold, beautiful SVG icon for Ky’ra (embedded as base64)
KYRA_SVG = """
<svg width="48" height="48" viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
<circle cx="24" cy="24" r="22" fill="#4fb8ac" stroke="#222" stroke-width="3"/>
<text x="50%" y="56%" text-anchor="middle" fill="#fff" font-size="22" font-family="Segoe UI, Arial, sans-serif" font-weight="bold" dy=".3em">K</text>
</svg>
"""
def svg_to_base64(svg):
    return base64.b64encode(svg.encode("utf-8")).decode("utf-8")

kyra_svg_base64 = svg_to_base64(KYRA_SVG)
kyra_icon_dataurl = f"data:image/svg+xml;base64,{kyra_svg_base64}"

st.set_page_config(
    page_title="Ask Ky’ra",
    page_icon=kyra_icon_dataurl,
    layout="centered"
)

# Custom styling
st.markdown(
    """
    <style>
    .main {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 10px;
        font-family: 'Roboto', sans-serif;
    }
    .stTextInput > div > input {
        border: 1px solid #ccc;
        border-radius: 5px;
        font-family: 'Roboto', sans-serif;
    }
    .stTextArea > div > textarea {
        border: 1px solid #ccc;
        border-radius: 5px;
        font-family: 'Roboto', sans-serif;
    }
    .submit-button {
        display: flex;
        justify-content: center;
    }
    .submit-button .stButton > button {
        background-color: #4fb8ac;
        color: white;
        font-size: 18px;
        padding: 10px 20px;
        border-radius: 8px;
        width: 200px;
        font-family: 'Roboto', sans-serif;
    }
    .logo-img {
        display: block;
        margin-left: auto;
        margin-right: auto;
        width: 100px;
    }
    .favicon-img {
        display: block;
        margin-left: auto;
        margin-right: auto;
        width: 64px;
        margin-bottom: 10px;
        border-radius: 50%;
        box-shadow: 0 2px 12px #4fb8ac55, 0 0 0 4px #fff;
        border: 3px solid #4fb8ac;
    }
    .history-entry {
        padding: 15px;
        border: 1px solid #e0e0e0;
        border-radius: 12px;
        background-color: #ffffff;
        margin-bottom: 10px;
        box-shadow: 1px 1px 3px #ccc;
        font-family: 'Roboto', sans-serif;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- Ky’ra favicon/icon at the top ---
st.markdown(
    f"<img src='{kyra_icon_dataurl}' class='favicon-img' alt='Ky’ra Icon'/>",
    unsafe_allow_html=True
)

# Header with logo
st.markdown(
    "<img src='https://via.placeholder.com/100?text=Ky%27ra+Logo' class='logo-img'/>",
    unsafe_allow_html=True
)

# Initialize session state for chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Input fields
st.subheader("Your Details")
email_input = st.text_input("Student Email", placeholder="student123@college.edu", help="Enter your college email address.")

# Personalized and role-based greeting
if email_input:
    name = email_input.split('@')[0].capitalize() if '@' in email_input else "User"
    if "college" in email_input.lower():
        st.markdown(f"<h1 style='text-align: center; color: #4fb8ac; font-family: \"Roboto\", sans-serif;'>🎓 Welcome College Admin, {name}!</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; font-family: \"Roboto\", sans-serif;'>Ask Ky’ra about student mapping, projects, and reports.</p>", unsafe_allow_html=True)
    else:
        st.markdown(f"<h1 style='text-align: center; color: #4fb8ac; font-family: \"Roboto\", sans-serif;'>👋 Hi {name}, ready to explore your internship path?</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; font-family: \"Roboto\", sans-serif;'>Ask Ky’ra anything about resumes, interviews, or project help - I’ll guide you step-by-step!</p>", unsafe_allow_html=True)
else:
    st.markdown("<h1 style='text-align: center; color: #4fb8ac; font-family: \"Roboto\", sans-serif;'>👋 Ask Ky’ra – Your Internship Assistant</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-family: \"Roboto\", sans-serif;'>Hi! I’m Ky’ra, your internship buddy. Enter your email to get started!</p>", unsafe_allow_html=True)

# Sample questions for selectbox
sample_questions = [
    "How do I write my internship resume?",
    "What are the best final-year projects in AI?",
    "How can I prepare for my upcoming interview?",
    "What skills should I learn for a career in cybersecurity?"
]
selected_question = st.selectbox("Choose a sample question or type your own:", sample_questions + ["Custom question..."])
query_text = st.text_area("Your Question", value=selected_question if selected_question != "Custom question..." else "", height=150, placeholder="E.g., How can I prepare for my internship interview?")

# Function to validate email
def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(pattern, email) is not None

# Function to call Ky’ra's backend API
def kyra_response(email, query):
    api_url = "http://kyra.kyras.in:8000/student-query"
    payload = {"student_id": email.strip(), "query": query.strip()}
    try:
        response = requests.post(api_url, params=payload)
        if response.status_code == 200:
            return response.json().get("response", "No response from Ky’ra.")
        else:
            return f"Error: {response.status_code} - {response.text}"
    except Exception as e:
        return f"API call failed: {str(e)}"

# Function to save queries to CSV (now includes response)
def save_query(email, query, timestamp, response):
    new_row = pd.DataFrame([[email, query, timestamp, response]], columns=["student_id", "Query", "Timestamp", "response"])
    if os.path.exists(CSV_FILE):
        df = pd.read_csv(CSV_FILE)
        df = pd.concat([df, new_row], ignore_index=True)
    else:
        df = new_row
    df.to_csv(CSV_FILE, index=False)

# Submit button logic
st.markdown('<div class="submit-button">', unsafe_allow_html=True)
if st.button("Submit", type="primary"):
    if not email_input or not query_text:
        st.error("Please enter both a valid email and a query.")
    elif not is_valid_email(email_input):
        st.error("Please enter a valid email address (e.g., student@college.edu).")
    else:
        try:
            timestamp = datetime.now().strftime("%d-%m-%Y %H:%M")
            response = kyra_response(email_input, query_text)
            save_query(email_input, query_text, timestamp, response)
            st.session_state.chat_history.append({
                "student_id": email_input,
                "query": query_text,
                "response": response,
                "timestamp": timestamp
            })
            st.success("Thank you! Ky’ra has received your question and is preparing your guidance.")
            with st.expander("🧠 Ky’ra’s Response", expanded=True):
                st.markdown(
                    f"""
                    <div style='background-color:#f0f8ff; padding:15px; border-radius:12px; box-shadow:1px 1px 3px #ccc; font-family: \"Roboto\", sans-serif;'>
                        <strong>Ky’ra’s Response:</strong><br>{response}
                    </div>
                    """,
                    unsafe_allow_html=True
                )
        except Exception as e:
            st.error(f"Failed to process query: {str(e)}")
st.markdown('</div>', unsafe_allow_html=True)

# Display chat history (filtered by user)
if email_input and os.path.exists(CSV_FILE):
    st.markdown("**🧾 Your Chat History:**")
    df = pd.read_csv(CSV_FILE)
    user_df = df[df['student_id'] == email_input]
    if not user_df.empty:
        for idx, row in user_df.iterrows():
            response_text = row['response'] if 'response' in row and pd.notna(row['response']) else "No response available."
            st.markdown(
                f"""
                <div class='history-entry'>
                    <strong>You asked:</strong> {row['Query']} <i>(submitted at {row['Timestamp']})</i><br>
                    <strong>Ky’ra replied:</strong> {response_text}
                </div>
                """,
                unsafe_allow_html=True
            )
            st.markdown("---")
    else:
        st.markdown("<p style='font-family: \"Roboto\", sans-serif;'>No chat history yet. Ask Ky’ra a question to get started!</p>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

# Storage notice
st.markdown("Your chat history is securely stored to help Ky’ra guide you better next time.", unsafe_allow_html=True)
