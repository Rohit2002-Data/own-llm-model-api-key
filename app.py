import streamlit as st
import requests
import json
import os
from dotenv import load_dotenv
import google.generativeai as genai

# --- Load environment variables ---
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
HF_API_TOKEN = os.getenv("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")  # Add this to your .env file

# --- Configure Gemini SDK ---
genai.configure(api_key=GEMINI_API_KEY)

# --- Hugging Face API ---
HF_MODEL = "google/gemma-2b"
HF_API_URL = f"https://api-inference.huggingface.co/models/{HF_MODEL}"

# --- Streamlit UI ---
st.title("🤖 Chatbot with Gemma-2B & Gemini fallback")

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
        headers = {
            "Authorization": f"Bearer {HF_API_TOKEN}",
            "Content-Type": "application/json"
        }
        payload = {
            "inputs": prompt,
            "parameters": {"max_new_tokens": 200}
        }

        # Try Hugging Face Gemma-2B
        try:
            response = requests.post(HF_API_URL, headers=headers, json=payload, timeout=20)
            if response.status_code == 200:
                hf_result = response.json()
                if isinstance(hf_result, list) and "generated_text" in hf_result[0]:
                    result = hf_result[0]["generated_text"].strip()
                elif isinstance(hf_result, dict) and "generated_text" in hf_result:
                    result = hf_result["generated_text"].strip()
            else:
                st.error(f"HF API error {response.status_code}: {response.text}")
        except Exception as e:
            st.error(f"Hugging Face API error: {str(e)}")

        # Fallback to Gemini SDK if needed
        if not result:
            try:
                model = genai.GenerativeModel("gemini-2.0-flash")
                gemini_response = model.generate_content(prompt)
                result = gemini_response.text
            except Exception as e:
                st.error(f"Gemini error: {str(e)}")

        # Final Result
        if result:
            st.success(result)
        else:
            st.error("❌ No response from either Gemma-2B or Gemini.")
