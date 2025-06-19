import streamlit as st
import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# URLs
PRIMARY_API_URL = "https://main-file-20.onrender.com/generate/"
GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"

# Streamlit UI
st.title("🔐 Custom LLM API Key Chatbot with Gemini Fallback")

# --- API Key Assignment ---
email = st.text_input("📧 Enter your email to get an API key")
if st.button("Get API Key"):
    try:
        with open("keys.json", "r") as f:
            keys = json.load(f)
    except FileNotFoundError:
        keys = {}

    if email not in keys:
        new_key = email[::-1] + "123"
        keys[email] = new_key
        with open("keys.json", "w") as f:
            json.dump(keys, f)
        st.success(f"✅ Your API Key: {new_key}")
    else:
        st.info(f"🔐 Your existing API Key: {keys[email]}")

# --- Input Section ---
api_key = st.text_input("🔑 Enter your API Key", type="password")
prompt = st.text_area("💬 Enter your prompt")

# --- Generation Logic ---
if st.button("🚀 Generate"):
    if not api_key or not prompt.strip():
        st.warning("⚠️ Please enter both an API key and a prompt.")
    else:
        result = ""
        headers = {"Authorization": f"Bearer {api_key}"}
        payload = {"prompt": prompt}

        # Try own LLM first
        try:
            response = requests.post(PRIMARY_API_URL, headers=headers, json=payload, timeout=10)
            if response.status_code == 200:
                result = response.json().get("response", "")
        except Exception:
            pass  # Continue to Gemini fallback

        # If no result, fallback to Gemini
        if not result:
            gemini_payload = {
                "contents": [{"parts": [{"text": prompt}]}]
            }
            gemini_headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {GEMINI_API_KEY}"
            }

            gemini_response = requests.post(
                GEMINI_API_URL, headers=gemini_headers, json=gemini_payload
            )

            if gemini_response.status_code == 200:
                result = gemini_response.json()["candidates"][0]["content"]["parts"][0]["text"]
            else:
                st.error(f"❌ Gemini API failed: {gemini_response.text}")

        if result:
            st.success(result)
