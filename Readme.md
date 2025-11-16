AI Code Analysis Tool – Project Documentation
1. Project Overview

Project Name: AI Code Analysis Tool

Purpose:
The AI Code Analysis Tool allows developers to upload code (ZIP files), analyze it using AI, and get meaningful explanations, bug detection, and suggestions. The system stores code embeddings in ChromaDB for semantic retrieval and AI analysis.

Technologies Used:

Backend: Python, FastAPI

Frontend: React, plain CSS

Vector Store / Database: ChromaDB

AI: OpenAI embeddings and LLM (via LangChain)

Other Libraries: tiktoken, dotenv, shutil, zipfile

Key Features:

Upload code ZIP files

Extract and process code files automatically

Store code embeddings in ChromaDB

Query AI for code explanations, debugging, or insights

Simple React frontend for easy interaction

2. System Architecture

Workflow:

React Frontend
    ├─ Upload file → /upload API → FastAPI → code_processor → embeddings → ChromaDB
    └─ Send query → /analyze API → FastAPI → CodeAnalysisAgent → ChromaDB → AI response


Ports:

Backend FastAPI: 127.0.0.1:8000

Frontend React: localhost:5173 (Vite default)

ChromaDB: Default port (ensure different from backend if needed)

3. Backend Documentation
3.1 API Endpoints
APIs : http://localhost:8000/docs

Endpoint	Method	Description	Request Body	Response
/upload/	POST	Upload ZIP file, extract, and store embeddings	multipart/form-data (file)	JSON with status & path
/analyze/query	POST	Analyze uploaded code using AI	multipart/form-data (file + query)	JSON with AI response
/	GET	Home / welcome message	None	JSON with message

Request Examples:

Upload ZIP File:

POST http://127.0.0.1:8000/upload/
Content-Type: multipart/form-data
Body: file=<your_zip_file.zip>


Analyze Code Query:

POST http://127.0.0.1:8000/analyze/query
Content-Type: multipart/form-data
Body: file=<your_zip_file.zip>, query="Explain the calculateTotal() method"

3.2 Services

code_processor.py – Reads code files from ZIP, prepares chunks for embedding.

embeddings.py – Stores code chunks in ChromaDB.

CodeAnalysisAgent – Handles AI queries, retrieves relevant code from ChromaDB, and generates AI responses.

3.3 CORS Handling

Backend is configured to allow all origins for development purposes.

Ensures the React frontend (port 5173) can communicate with FastAPI backend (port 8000).

4. Frontend Documentation
4.1 Components

App.jsx – Main container with:

File upload input

Prompt box for AI query

Response textarea

Analyze button

api.js – Handles communication with backend:

Upload API (/upload)

Analyze API (/analyze)

4.2 UI Features

Upload a ZIP file → stores in backend + embeddings

Prompt box → send query related to uploaded code

AI response displayed in a scrollable textarea

Simple, responsive design using plain CSS

5. Deployment Instructions (Local)
5.1 Backend Setup (FastAPI)

Clone project repository.

Create Python virtual environment:

python -m venv myenv


Activate virtual environment:

Windows: myenv\Scripts\activate

Linux/macOS: source myenv/bin/activate

Install dependencies:

pip install -r requirements.txt


Start FastAPI server:

uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

5.2 ChromaDB Setup

Ensure ChromaDB server is running on a port different from backend (default: 8001).

FastAPI connects to ChromaDB via embeddings service.

5.3 Frontend Setup (React)

Navigate to frontend folder.

Install dependencies:

npm install


Start React dev server:

npm run dev


Access frontend at: http://localhost:5173

5.4 Usage Flow

Open React frontend.

Upload ZIP file containing code.

Enter your query in the prompt box.

Click Analyze.

AI response will appear in the response textarea.

 Future Improvements

User authentication & project management

Real-time upload progress & AI analysis status

Auto-expanding response textarea

Persistent storage of previous queries

Deployment on cloud / Docker container


User Uploads a Codebase (ZIP file)

Step-by-step flow:

Frontend Upload:

User selects a ZIP file in the React frontend.

The file is sent via a POST request to the /upload/ FastAPI endpoint using multipart/form-data.

Backend Receives File:

FastAPI endpoint upload_code(file: UploadFile = File(...)) receives the file.

The file is saved temporarily in the temp/ directory.

Extract ZIP File:

The backend extracts the ZIP contents to a folder like temp/<zip_file_name>/.

Each code file (Python, Java, JS, etc.) inside the ZIP is now accessible.

Process Code Files:

code_processor.read_code_files() reads all code files recursively.

Each file’s content is split into chunks for easier embedding.

Chunking ensures large files don’t exceed the embedding or LLM context limits.

Store Embeddings:

embeddings.store_embeddings(code_files) is called.

Each chunk is converted into an embedding vector using OpenAI embeddings.

Embeddings are stored in ChromaDB, which acts as a semantic search engine for the code.

Outcome:

Code chunks from the ZIP are embedded and stored in ChromaDB.

The system is now ready to retrieve relevant chunks for any future query.

User Sends a Query

Step-by-step flow:

Frontend Query Submission:

User enters a prompt in the React frontend and clicks Analyze.

Selected file (optional) and query are sent via POST to /analyze/.

Backend Query Handling (CodeAnalysisAgent.extract_knowledge):

Step 1: Check if query is code-related (rule-based check).

Only if query is related to code, the AI processing is triggered.

Step 2: Retrieve Relevant Code Chunks

ChromaDB semantic search is used to find top K code chunks most relevant to the query.

Each chunk contains code text and metadata.

Combine and Trim Chunks to Fit LLM Context Window:

All retrieved chunks are concatenated into combined_code.

The trim_to_max_tokens() function uses tiktoken to encode tokens:

If total tokens exceed LLM context limit (e.g., 6000 for gpt-4o-mini), it trims older/extra tokens.

Ensures the prompt fits within the LLM’s context window.

Prepare LLM Prompt:

A PromptTemplate is loaded: it combines the user query and the selected code chunks.

The template ensures the LLM understands it should analyze code and provide meaningful explanations.

Call LLM:

LLM receives the trimmed code + user query as input.

It generates a response explaining the code, identifying bugs, or providing suggestions.

Return Response to Frontend:

AI response is sent back to React frontend.

The frontend displays it in the textarea.

Key Technical Considerations

Context Window Management:

LLMs can only process a limited number of tokens.

The system trims retrieved code to ensure it fits within this limit.

Semantic Search:

ChromaDB allows retrieval of relevant code chunks using embeddings.

This avoids sending entire codebases, which may be too large.

Chunking Code:

Large code files are split into smaller chunks for embedding.

This improves retrieval precision and LLM efficiency.

AI Safety:

LLM calls are wrapped in try-except blocks to prevent crashes.

4️ Visual Flow (Simplified)
[React Frontend]
   |
   |-- Upload ZIP --> /upload
   |                   - Extract ZIP
   |                   - Chunk code files
   |                   - Store embeddings in ChromaDB
   |
   |-- Send Query --> /analyze
                       - Check if code-related
                       - Retrieve relevant chunks from ChromaDB
                       - Trim tokens to fit LLM
                       - Create prompt + user query
                       - Call LLM
                       - Return response
