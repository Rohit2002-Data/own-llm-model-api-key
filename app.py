import streamlit as st
import requests
import json

API_URL = "https://main-file-5.onrender.com/generate/"  # Update when deployed

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

api_key = st.text_input("🔑 Enter your API Key", type="password")
prompt = st.text_area("💬 Enter your prompt")

if st.button("🚀 Generate"):
    if not api_key or not prompt.strip():
        st.warning("Please enter both an API key and a prompt.")
    else:
        headers = {"Authorization": f"Bearer {api_key}"}
        payload = {"prompt": prompt}
        try:
            response = requests.post(API_URL, headers=headers, json=payload)
            if response.status_code == 200:
                result = response.json()["response"]
                st.success(result)
            else:
                st.error(f"Error {response.status_code}: {response.json().get('detail', 'Unknown error')}")
        except Exception as e:
            st.error(f"Connection failed: {e}")









