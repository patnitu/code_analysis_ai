# app/services/code_analysis_agent.py

import os
from typing import List, Dict, Any
from dotenv import load_dotenv

from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document

from app.services import code_processor

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


class CodeAnalysisAgent:
    def __init__(
        self,
        collection_name: str = "codebase_embeddings",
        persist_directory: str = "./chroma_db",
        model_name: str = "gpt-4o-mini",
        embedding_model: str = "text-embedding-3-small",
        temperature: float = 0.2,
    ):
        self.api_key = OPENAI_API_KEY

        # Embeddings
        self.embeddings = OpenAIEmbeddings(
            model=embedding_model,
            api_key=self.api_key
        )

        # LLM
        self.llm = ChatOpenAI(
            model=model_name,
            temperature=temperature,
            api_key=self.api_key
        )

        # Vector DB
        self.vectordb = Chroma(
            persist_directory=persist_directory,
            embedding_function=self.embeddings,
            collection_name=collection_name,
        )

    # ----------------------------------------------------------------
    # Intent Detection (NO LLM CALL)
    # ----------------------------------------------------------------
    def is_code_related(self, query: str) -> bool:
        code_keywords = [
            "code", "bug", "error", "fix", "function", "class", "method",
            "java", "python", "js", "javascript", "typescript",
            "spring", "react", "node", "api",
            "explain this", "what does this do", "debug", "stacktrace",
            "compile", "runtime", "exception"
        ]
        q = query.lower()
        return any(kw in q for kw in code_keywords)

    # ----------------------------------------------------------------
    # RAG Query
    # ----------------------------------------------------------------
    def extract_knowledge(self, query: str, top_k: int = 5) -> Dict[str, Any]:
        print("User Query:", query)

        # 1️⃣ Skip LLM if NOT code related
        if not self.is_code_related(query):
            return {
                "response":
                    "Your question doesn't seem related to code analysis. "
                    "Please ask about code, errors, architecture, functions, or bugs.",
                "retrieved_docs": []
            }

        import tiktoken

        # Helper: trim tokens
        def trim_to_max_tokens(text: str, max_tokens: int = 6000, model: str = "gpt-4o-mini"):
            try:
                enc = tiktoken.encoding_for_model(model)
            except Exception:
                enc = tiktoken.get_encoding("cl100k_base")

            tokens = enc.encode(text)
            if len(tokens) <= max_tokens:
                return text

            trimmed = enc.decode(tokens[:max_tokens])
            print(f"[WARN] Code trimmed from {len(tokens)} tokens -> {max_tokens}")
            return trimmed

        # 2️⃣ Retrieve relevant code
        retriever = self.vectordb.as_retriever(
            search_type="similarity",
            search_kwargs={"k": top_k},
        )

        docs = retriever.invoke(query)

        if not docs:
            return {
                "response": "No relevant code found for your query.",
                "retrieved_docs": []
            }

        # 3️⃣ Combine + trim
        combined_code = "\n\n".join([d.page_content for d in docs])
        combined_code = trim_to_max_tokens(combined_code)

        # 4️⃣ Load prompt template
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)
        prompt_path = os.path.join(project_root, "prompts", "code_analysis_prompt.txt")

        with open(prompt_path, "r", encoding="utf-8") as f:
            prompt_template_str = f.read()

        prompt = PromptTemplate(
            input_variables=["user_query", "code"],
            template=prompt_template_str,
        )

        chain = prompt | self.llm

        # 5️⃣ LLM Execution
        try:
            resp = chain.invoke({"user_query": query, "code": combined_code})
            result_text = resp.content
        except Exception as e:
            result_text = f"Error generating analysis: {str(e)}"

        return {
            "response": result_text,
            "retrieved_docs": [d.metadata for d in docs],
        }

    # ----------------------------------------------------------------
    # Index Codebase into Chroma
    # ----------------------------------------------------------------
    def analyze_codebase(self, code_files: List[Dict[str, str]]):
        for file in code_files:
            chunks = code_processor.chunk_code(file["content"])

            for idx, chunk in enumerate(chunks):
                doc = Document(
                    page_content=chunk,
                    metadata={"file": file["path"], "chunk_id": idx}
                )
                self.vectordb.add_documents([doc])
