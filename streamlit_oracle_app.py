import os
import streamlit as st
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex
from llama_index.llms.openai import OpenAI
from llama_index.core.settings import Settings

# --- Configuration ---
os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]
Settings.llm = OpenAI()

# Load docs dynamically
documents = SimpleDirectoryReader("docs", recursive=True).load_data()
index = VectorStoreIndex.from_documents(documents)
query_engine = index.as_query_engine()

# --- Streamlit UI ---
st.title("🌿 Oracle of the Field")
st.markdown("_An elder intelligence speaks from the Akashic archive._")

user_query = st.text_input("What is your heart's curiosity?")

if user_query:
    response = query_engine.query(user_query)
    st.markdown("---")
    st.markdown("**Response from the Field:**")
    st.write(str(response))
    st.markdown("---")
    st.caption("🌀 How does this resonate with you, dear Seeker?")
