import streamlit as st
import requests
import json

API_URL = "http://localhost:7860/generate/"  # Update when deployed

st.title("🔐 Custom LLM API Key Chatbot")

# Simulated key assignment
email = st.text_input("Enter your email to get an API key")
if st.button("Get API Key"):
    with open("keys.json", "r") as f:
        keys = json.load(f)
    if email not in keys:
        new_key = email[::-1] + "123"  # Simulate a key
        keys[email] = new_key
        with open("keys.json", "w") as f:
            json.dump(keys, f)
        st.success(f"Your API Key: {new_key}")
    else:
        st.info(f"Your API Key: {keys[email]}")

# Prompt interface
st.subheader("💬 Talk to the LLM")
api_key = st.text_input("Enter your API key")
prompt = st.text_area("Enter your prompt")

if st.button("Generate"):
    headers = {"Authorization": f"Bearer {api_key}"}
    payload = {"prompt": prompt}
    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        st.write("**Response:**")
        st.success(response.json()["response"])
    except Exception as e:
        st.error(f"Error: {e}")
