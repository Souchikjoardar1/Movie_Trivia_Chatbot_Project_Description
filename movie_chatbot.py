
from __future__ import annotations
import os
import uuid
from pathlib import Path
from typing import Dict

from dotenv import load_dotenv
load_dotenv()


import gradio as gr

# ---- LangChain core + community imports ----
from langchain_community.document_loaders.pdf import PyPDFLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_community.llms import Ollama  # local Ollama LLM

# --------------------- Config ---------------------
APP_GREETING = (
    "Hello, I am MovieBot, your movie trivia expert. Ask me anything about films!"
)
DEFAULT_PDF_PATH = os.getenv("PDF_PATH", str(Path("./movies_trivia.pdf").resolve()))
COLLECTION_NAME = "movie_trivia"
CHROMA_DIR = str(Path(".chroma") / COLLECTION_NAME)

# Pinned to local Ollama model; change via env if desired
LLM_MODEL = os.getenv("LLM_MODEL", "mistral").strip()  # e.g., llama3 or mistral

# LangSmith / LangChain tracing support
if os.getenv("LANGSMITH_API_KEY") and not os.getenv("LANGCHAIN_API_KEY"):
    os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGSMITH_API_KEY")
if os.getenv("LANGSMITH_PROJECT") and not os.getenv("LANGCHAIN_PROJECT"):
    os.environ["LANGCHAIN_PROJECT"] = os.getenv("LANGSMITH_PROJECT")
if os.getenv("LANGCHAIN_TRACING_V2") is None and (
    os.getenv("LANGCHAIN_API_KEY") or os.getenv("LANGSMITH_API_KEY")
):
    os.environ["LANGCHAIN_TRACING_V2"] = "true"

# --------------------- RAG Building Blocks ---------------------

def load_and_split_pdf(pdf_path: str):
    if not Path(pdf_path).exists():
        raise FileNotFoundError(
            f"PDF not found at '{pdf_path}'. Set PDF_PATH env var or place movies_trivia.pdf in project root."
        )
    loader = PyPDFLoader(pdf_path)
    docs = loader.load()
    splitter = CharacterTextSplitter(chunk_size=150, chunk_overlap=20)
    chunks = splitter.split_documents(docs)
    return chunks


def build_vectorstore(chunks):
    embeddings = OllamaEmbeddings(model="granite-embedding:latest")
    vs = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        collection_name=COLLECTION_NAME,
        persist_directory=CHROMA_DIR,
    )
    return vs


def get_llm():
    # Local Ollama text model
    return Ollama(model=LLM_MODEL)


def build_prompt() -> PromptTemplate:
    template = (
        "You are MovieBot, a precise movie trivia expert.\n"
        "Answer ONLY using the provided context. If the answer isn't in the context, say you don't know.\n\n"
        "Context:\n{context}\n\n"
        "Question: {question}\n\n"
        "Answer concisely and cite movie names, years, roles, and awards when relevant."
    )
    return PromptTemplate(template=template, input_variables=["context", "question"])


def build_qa_chain(vectorstore):
    retriever = vectorstore.as_retriever(search_kwargs={"k": 4})
    llm = get_llm()
    prompt = build_prompt()

    qa = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        chain_type_kwargs={"prompt": prompt},
        return_source_documents=True,
    )
    return qa

# --------------------- Chat + History ---------------------
_sessions: Dict[str, InMemoryChatMessageHistory] = {}

def get_session(session_id: str) -> InMemoryChatMessageHistory:
    if session_id not in _sessions:
        _sessions[session_id] = InMemoryChatMessageHistory()
    return _sessions[session_id]


def format_history_for_prompt(history: InMemoryChatMessageHistory, max_turns: int = 6) -> str:
    messages = history.messages[-(2 * max_turns) :]
    lines = []
    for m in messages:
        role = getattr(m, "type", None) or getattr(m, "role", "user")
        content = getattr(m, "content", "")
        lines.append(f"{role.title()}: {content}")
    return "\n".join(lines)


def answer_query(qa: RetrievalQA, user_text: str, session_id: str):
    history = get_session(session_id)
    chat_history_text = format_history_for_prompt(history)    
    combined_q = (
        f"Conversation history (may be empty):\n{chat_history_text}\n\n"
        f"User question: {user_text}"
    ).strip()
    inputs = {"query": combined_q, "question": combined_q}
    result = qa.invoke(inputs)

    answer = result.get("result", "")
    history.add_user_message(user_text)
    history.add_ai_message(answer)

    # REMOVE sources collection and return only answer
    return answer



def clear_session(session_id: str):
    if session_id in _sessions:
        del _sessions[session_id]

# --------------------- App Bootstrap ---------------------

def prepare_vectorstore(pdf_path: str):
    chunks = load_and_split_pdf(pdf_path)
    vs = build_vectorstore(chunks)
    return vs


def main():
    pdf_path = DEFAULT_PDF_PATH
    vectorstore = prepare_vectorstore(pdf_path)
    qa_chain = build_qa_chain(vectorstore)

    with gr.Blocks(title="MovieBot - Movie Trivia RAG") as demo:
        gr.Markdown(f"### {APP_GREETING}")
        chatbot = gr.Chatbot(label="MovieBot", height=400)
        txt = gr.Textbox(label="Ask about movies", placeholder="Who directed The Dark Knight?", lines=2)
        submit = gr.Button("Submit", variant="primary")
        clear = gr.Button("Clear History")
        session_state = gr.State(str(uuid.uuid4()))

        def respond(user_input, chat_history, session_id):
            if not user_input or not user_input.strip():
                return chat_history, ""
            answer = answer_query(qa_chain, user_input.strip(), session_id)

            chat_history.append({"role": "user", "content": user_input})
            chat_history.append({"role": "assistant", "content": answer})

            return chat_history, ""




        def clear_all(session_id):
            clear_session(session_id)
            return [], str(uuid.uuid4())

        submit.click(respond, inputs=[txt, chatbot, session_state], outputs=[chatbot, txt])
        clear.click(clear_all, inputs=[session_state], outputs=[chatbot, session_state])

    demo.queue().launch()



if __name__ == "__main__":
    main()
