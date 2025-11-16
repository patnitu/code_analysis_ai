# app/services/code_processor.py

from pathlib import Path

def read_code_files(code_dir):
    """
    Read all code files from the directory and return as a list of dictionaries.
    Only include .py, .java, .js, .sql files.
    """
    code_files = []
    for path in Path(code_dir).rglob("*.*"):
        if path.suffix in [".py", ".java", ".js", ".sql"]:
            try:
                with open(path, "r", encoding="utf-8", errors="ignore") as f:
                    code_files.append({"path": str(path), "content": f.read()})
            except Exception as e:
                print(f"Error reading {path}: {e}")
    return code_files


def chunk_code(content, chunk_size=500):
    """
    Split a large code string into smaller chunks to avoid token limit issues.
    Each chunk is roughly `chunk_size` lines.
    """
    lines = content.split("\n")
    chunks = []
    for i in range(0, len(lines), chunk_size):
        chunk = "\n".join(lines[i:i+chunk_size])
        chunks.append(chunk)
    return chunks
