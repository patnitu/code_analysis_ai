# app/routes/upload.py

from fastapi import APIRouter, UploadFile, File
import os
import shutil
import zipfile
from app.services import code_processor, embeddings

router = APIRouter()

UPLOAD_DIR = "temp"

# Make sure temp directory exists
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

def extract_zip(zip_path, extract_to):
    """Extracts the zip file to the specified directory."""
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)

@router.post("/")
async def upload_code(file: UploadFile = File(...)):
    """
    Endpoint to upload a zip file, extract it, process code,
    and save embeddings to ChromaDB.
    """
    # Save uploaded zip
    print("File is uploading")
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Extract zip contents
    extract_folder = os.path.join(UPLOAD_DIR, file.filename.replace(".zip", ""))
    extract_zip(file_path, extract_folder)

    # Step 1: Read all code files
    code_files = code_processor.read_code_files(extract_folder)

    # Step 2: Store code chunks in ChromaDB
    embeddings.store_embeddings(code_files)

    return {
        "message": "Code uploaded, processed, and saved to ChromaDB successfully",
        "extract_path": extract_folder
    }
