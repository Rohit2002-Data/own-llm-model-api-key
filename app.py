import streamlit as st
import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Gemini (free) URL using gemini-pro
GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={GEMINI_API_KEY}"

# Your own LLM API
PRIMARY_API_URL = "https://main-file-20.onrender.com/generate/"

# --- Streamlit UI ---
st.title("🤖 Chatbot with Custom LLM + Gemini Fallback")

# --- Get Email and Generate API Key ---
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

# --- Prompt Inputs ---
api_key = st.text_input("🔑 Enter your API Key", type="password")
prompt = st.text_area("💬 Enter your prompt")

# --- Generate Button ---
if st.button("🚀 Generate"):
    if not api_key or not prompt.strip():
        st.warning("⚠️ Please enter both an API key and a prompt.")
    else:
        result = ""
        headers = {"Authorization": f"Bearer {api_key}"}
        payload = {"prompt": prompt}

        # Try your own LLM
        try:
            response = requests.post(PRIMARY_API_URL, headers=headers, json=payload, timeout=10)
            if response.status_code == 200:
                result = response.json().get("response", "").strip()
        except Exception as e:
            st.warning(f"⚠️ Custom LLM error: {e}")

        # Fallback to Gemini if own LLM fails or returns empty
        if not result:
            st.info("🧠 Falling back to Gemini (free tier)...")
            gemini_payload = {
                "contents": [{"parts": [{"text": prompt}]}]
            }
            gemini_headers = {
                "Content-Type": "application/json"
            }

            try:
                gemini_response = requests.post(
                    GEMINI_API_URL, headers=gemini_headers, json=gemini_payload, timeout=10
                )
                if gemini_response.status_code == 200:
                    result = gemini_response.json()["candidates"][0]["content"]["parts"][0]["text"]
                else:
                    st.error(f"❌ Gemini API Error: {gemini_response.status_code}")
                    st.json(gemini_response.json())
            except Exception as e:
                st.error(f"❌ Gemini fallback failed: {e}")

        # Show Result
        if result:
            st.success(result)
        else:
            st.error("❌ No response from either LLM or Gemini.")
