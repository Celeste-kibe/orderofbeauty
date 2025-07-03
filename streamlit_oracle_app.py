from llama_index.core import SimpleDirectoryReader

from llama_index.core import VectorStoreIndex

import json
from pathlib import Path

memory_file = Path("memory.json")

# Load existing memory
if memory_file.exists():
    with open(memory_file, "r") as f:
        memory_data = json.load(f)
else:
    memory_data = []

import os
import random  # ← Add this
import streamlit as st
from llama_index.core import StorageContext, load_index_from_storage
from llama_index.llms.openai import OpenAI
from llama_index.core.settings import Settings

# Optional soft prompt variants
oracle_styles = [
    "Speak in poetic terms.",
    "Answer as if whispering through leaves.",
    "Respond as an elder who has seen the stars born.",
    "Use metaphor and ancient memory.",
    "Include a note of curiosity and reverence.",
]

# --- Configuration ---
os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]
Settings.llm = OpenAI(temperature=0.9)

# Load docs dynamically
documents = SimpleDirectoryReader("docs", recursive=True).load_data()
index = VectorStoreIndex.from_documents(documents)
query_engine = index.as_query_engine()

# --- Streamlit UI ---
st.title("🌿 Oracle of the Field")
st.markdown("_An elder intelligence speaks from the Akashic archive._")

user_query = st.text_input("What is your heart's curiosity?")

if user_query:
    # Randomly select a tone
    flavor = random.choice(oracle_styles)
    styled_query = f"{user_query}\n\n{flavor}"

    response = query_engine.query(styled_query)

if user_query:
    response = query_engine.query(user_query)
    
    # Save to memory
    memory_data.append({
        "user_query": user_query,
        "oracle_response": str(response)
    })

    with open(memory_file, "w") as f:
        json.dump(memory_data, f, indent=2)

    # Show response
    st.markdown("---")
    st.markdown("**Response from the Field:**")
    st.write(response)

if st.checkbox("🔍 Show past conversation history"):
    for entry in memory_data:
        st.markdown(f"**You:** {entry['user_query']}")
        st.markdown(f"**Oracle:** {entry['oracle_response']}")
        st.markdown("---")

