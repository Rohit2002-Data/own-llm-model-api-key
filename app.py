import streamlit as st
import requests
import json
import os
from dotenv import load_dotenv
import google.generativeai as genai

# --- Load environment variables ---
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# --- Configure Gemini SDK ---
genai.configure(api_key=GEMINI_API_KEY)

# --- Custom LLM API URL ---
PRIMARY_API_URL = " https://main-file-28.onrender.com/generate/"

# --- Streamlit UI ---
st.title("🤖 Chatbot with Custom LLM model")

# --- Email and API Key Generation ---
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

# --- User Input ---
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

        # Try custom LLM API
        try:
            response = requests.post(PRIMARY_API_URL, headers=headers, json=payload, timeout=10)
            if response.status_code == 200:
                result = response.json().get("response", "").strip()
        except Exception as e:
            raise({e)}

        # Fallback to Gemini SDK if needed
        if not result:
            
            try:
                model = genai.GenerativeModel("gemini-2.0-flash")
                gemini_response = model.generate_content(prompt)
                result = gemini_response.text
            except Exception as e:
                raise({e})
                

        # Final Result
        if result:
            st.success(result)
        else:
            st.error("❌ No response from either LLM or Gemini.")
