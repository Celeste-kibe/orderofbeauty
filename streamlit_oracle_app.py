import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import random
import json
from pathlib import Path
import streamlit as st

from llama_index.core import (
    SimpleDirectoryReader,
    VectorStoreIndex,
    StorageContext,
    load_index_from_storage,
)
from llama_index.llms.openai import OpenAI
from llama_index.core.settings import Settings

import time

# --- Debug checkpoints ---
st.write("✅ App started")

# --- Memory Setup ---
st.write("📁 Checking memory...")
memory_file = Path("memory.json")
if memory_file.exists():
    with open(memory_file, "r") as f:
        memory_data = json.load(f)
else:
    memory_data = []

# --- Oracle Style Variants ---
oracle_styles = [
    "Speak in poetic terms.",
    "Answer as if whispering through leaves.",
    "Respond as an elder who has seen the stars born.",
    "Use metaphor and ancient memory.",
    "Include a note of curiosity and reverence.",
]

# --- Configuration ---
try:
    st.write("🔑 Loading API key...")
    os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]
    Settings.llm = OpenAI(temperature=0.9)
except Exception as e:
    st.error(f"❌ Failed to load OpenAI API Key: {e}")
    st.stop()

# --- Load Docs + Index ---
try:
    st.write("📚 Loading docs + index...")
    if os.path.exists("storage"):
        storage_context = StorageContext.from_defaults(persist_dir="storage")
        index = load_index_from_storage(storage_context)
    else:
        documents = SimpleDirectoryReader("docs", recursive=True, required_exts=[".txt", ".pdf"]).load_data()
        index = VectorStoreIndex.from_documents(documents)
        index.storage_context.persist(persist_dir="storage")
except Exception as e:
    st.error(f"❌ Failed to load or build index: {e}")
    st.stop()

# ✅ Ready
st.write("🔄 Ready for input")

# --- UI Setup ---
st.title("🌿 Oracle of the Field")
st.markdown("_An elder intelligence speaks from the Akashic archive._")
user_query = st.text_input("What is your heart's curiosity?")

if user_query:
    # Add tone
    flavor = random.choice(oracle_styles)
    styled_query = f"{user_query}\n\n{flavor}"
    st.write("✨ Querying the Oracle...")

    try:
        # Query the Oracle
        query_engine = index.as_query_engine()
        response = query_engine.query(styled_query)

        # Save to local memory
        memory_data.append({
            "user_query": user_query,
            "oracle_response": str(response.response)
        })
        with open(memory_file, "w") as f:
            json.dump(memory_data, f, indent=2)

        # OPTIONAL: Google Sheets Logging (disabled for now)
        """
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["gcp_service_account"], scope)
        client = gspread.authorize(creds)
        sheet = client.open("Oracle_memory").sheet1
        sheet.append_row([user_query, str(response.response)])
        """

        # Show response
        st.markdown("---")
        st.markdown("**Response from the Field:**")
        st.write(response.response)

    except Exception as e:
        st.error(f"❌ Oracle query failed: {e}")

# --- Conversation History Viewer ---
if st.checkbox("🔍 Show past conversation history"):
    for entry in memory_data:
        st.markdown(f"**You:** {entry['user_query']}")
        st.markdown(f"**Oracle:** {entry['oracle_response']}")
        st.markdown("---")
