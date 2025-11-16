import streamlit as st
import os
from app.services.code_analysis_agent import CodeAnalysisAgent
from app.services import code_processor, embeddings
from zipfile import ZipFile
import shutil

# Initialize the AI agent
agent = CodeAnalysisAgent()

# Temporary folder to save uploads
UPLOAD_DIR = "temp"
os.makedirs(UPLOAD_DIR, exist_ok=True)

st.title("AI Code Analysis Tool (Streamlit)")

# ------------------------------
# File upload
# ------------------------------
uploaded_file = st.file_uploader("Upload your code ZIP file", type="zip")

if uploaded_file:
    # Save uploaded zip
    file_path = os.path.join(UPLOAD_DIR, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    st.success(f"Uploaded file: {uploaded_file.name}")

    # Extract ZIP
    extract_folder = os.path.join(UPLOAD_DIR, uploaded_file.name.replace(".zip", ""))
    with ZipFile(file_path, 'r') as zip_ref:
        zip_ref.extractall(extract_folder)

    st.info(f"Code extracted to: {extract_folder}")

    # Process code and store embeddings
    code_files = code_processor.read_code_files(extract_folder)
    embeddings.store_embeddings(code_files)
    st.success("Code processed and embeddings stored successfully!")

# ------------------------------
# Query input
# ------------------------------
query = st.text_area("Enter your query about the code")

if st.button("Analyze"):

    if not query.strip():
        st.warning("Please enter a query before analyzing.")
    else:
        with st.spinner("Analyzing..."):
            response = agent.extract_knowledge(query)
            st.subheader("AI Response:")
            st.text_area("", value=response["response"], height=300)
