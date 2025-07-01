import os
import streamlit as st
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex
from llama_index.llms.openai import OpenAI
from llama_index.core.settings import Settings

# --- Configuration ---
# Load your OpenAI API key (set this as a secret in Streamlit Cloud)
os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]

# Set OpenAI as LLM
Settings.llm = OpenAI()

# Rebuild the index from documents in /docs
documents = SimpleDirectoryReader("docs", recursive=True).load_data()
index = VectorStoreIndex.from_documents(documents)
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
