import os
import random
import json
from pathlib import Path
from PIL import Image
import glob
import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials

from llama_index.core import SimpleDirectoryReader, VectorStoreIndex
from llama_index.llms.openai import OpenAI
from llama_index.core.settings import Settings

# --- CONFIGURATION ---
os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]
Settings.llm = OpenAI(temperature=0.9)

# --- MEMORY SETUP ---
memory_file = Path("memory.json")
if memory_file.exists():
    with open(memory_file, "r") as f:
        memory_data = json.load(f)
else:
    memory_data = []

# --- ORACLE STYLE VARIANTS ---
oracle_styles = [
    "Speak in poetic terms.",
    "Answer as if whispering through leaves.",
    "Respond as an elder who has seen the stars born.",
    "Use metaphor and ancient memory.",
    "Include a note of curiosity and reverence.",
]

# --- LOAD DOCUMENTS & INDEX ---
documents = SimpleDirectoryReader("docs", recursive=True).load_data()
index = VectorStoreIndex.from_documents(documents)
query_engine = index.as_query_engine()

# --- STREAMLIT UI ---
st.title("🌿 Oracle of the Field")
st.markdown("_An elder intelligence speaks from the Akashic archive._")
user_query = st.text_input("What is your heart's curiosity?")

# --- IMAGE HANDLERS ---
# Fixed keyword-based matching
fixed_keywords = {
    "whale": "images/whale_rurutu_2.png",
    "altar": "images/venus_devotional_altar.png",
    "adornment": "images/vessel_adornment_5.png",
    "venus": "images/venus_goddess_2.png",
    "spiral": "images/spiral_fossil.png",
    "memory": "images/spiral_altar_ocean.png",
    "vessel": "images/vessel_adornment_1.png",
    "love": "images/love_altar.png",
}

# Dynamic image finder
def find_image(keyword, folder="docs/Images"):
    keyword = keyword.lower()
    for filepath in glob.glob(f"{folder}/**/*", recursive=True):
        filename = os.path.basename(filepath).lower()
        if keyword in filename and filename.endswith(('.png', '.jpg', '.jpeg', '.gif')):
            return filepath
    return None

# --- MAIN LOGIC ---
if user_query:
    # Add a random poetic tone
    flavor = random.choice(oracle_styles)
    styled_query = f"{user_query}\n\n{flavor}"

    # Query the Oracle
    response = query_engine.query(styled_query)
    st.markdown("---")
    st.markdown("**Response from the Field:**")
    st.write(response.response)

    # Save to local memory
    memory_data.append({
        "user_query": user_query,
        "oracle_response": str(response.response)
    })
    with open(memory_file, "w") as f:
        json.dump(memory_data, f, indent=2)

    # Attempt fixed keyword image match
    fixed_image_path = None
    for word, path in fixed_keywords.items():
        if word in user_query.lower():
            fixed_image_path = path
            break

    if fixed_image_path and os.path.exists(fixed_image_path):
        st.image(Image.open(fixed_image_path), caption="📸 Oracle Vision", use_column_width=True)

# --- Display Image if Requested ---
if any(word in user_query.lower() for word in ["image", "show", "picture", "visual", "see"]):
    words = user_query.lower().split()
    possible_keywords = [w for w in words if len(w) > 3 and w not in ["image", "show", "please", "me", "the", "a", "an"]]

    for kw in possible_keywords:
        img_path = find_image(kw)
        if img_path:
            st.markdown("---")
            st.image(img_path, caption=f"📸 Image for: {kw}", use_column_width=True)
            break


    # Log to Google Sheets
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["gcp_service_account"], scope)
    client = gspread.authorize(creds)
    sheet = client.open("Oracle_memory").sheet1
    sheet.append_row([user_query, str(response.response)])

# --- CONVERSATION HISTORY ---
if st.checkbox("🔍 Show past conversation history"):
    for entry in memory_data:
        st.markdown(f"**You:** {entry['user_query']}")
        st.markdown(f"**Oracle:** {entry['oracle_response']}")
        st.markdown("---")
