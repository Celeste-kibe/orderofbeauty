import os
import streamlit as st
from llama_index.core import StorageContext, load_index_from_storage
from llama_index.llms.openai import OpenAI
from llama_index.core.settings import Settings

# --- Configuration ---
# Load your OpenAI API key (set this as a secret in Streamlit Cloud)
os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]

# Set OpenAI as LLM
Settings.llm = OpenAI()

# Define index storage path (must match the folder saved to your Google Drive)
persist_dir = "OrderAI_index"

# Load index from storage
storage_context = StorageContext.from_defaults(persist_dir=persist_dir)
index = load_index_from_storage(storage_context)
query_engine = index.as_query_engine()

# --- Streamlit UI ---
st.title("🌿 Oracle of the Field")
st.markdown("_An elder intelligence speaks from the Akashic archive._")

user_query = st.text_input("What would you like to ask the oracle?")

if user_query:
    response = query_engine.query(user_query)
    st.markdown("---")
    st.markdown("**Response from the Field:**")
    st.write(response)
    st.markdown("---")
    st.caption("🌀 What question is waiting to be asked next?")
