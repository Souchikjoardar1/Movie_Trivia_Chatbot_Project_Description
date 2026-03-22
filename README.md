# 🎬 MovieBot - Movie Trivia RAG Chatbot

A sophisticated AI-powered chatbot that answers movie trivia questions using Retrieval Augmented Generation (RAG). MovieBot combines local language models with vector database technology to provide accurate, context-aware responses about films, directors, actors, and movie facts.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Architecture](#architecture)
- [System Requirements](#system-requirements)
- [Installation](#installation)
- [Configuration](#configuration)
- [How It Works](#how-it-works)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Technology Stack](#technology-stack)

---

## 🎯 Overview

MovieBot is a specialized conversational AI system designed for movie trivia. Unlike generic chatbots, MovieBot:

- **Operates Locally**: Runs entirely on your machine without cloud dependencies
- **Retrieval-Augmented**: Uses a knowledge base extracted from PDF documents
- **Conversational Memory**: Maintains chat history within sessions for context-aware responses
- **Precise Answers**: References specific movies, years, directors, actors, and awards from source materials

The system is built on the Retrieval Augmented Generation (RAG) paradigm, which combines the power of vector databases for semantic search with large language models for natural language understanding.

---

## ✨ Key Features

### 🔍 **Semantic Search**
- Converts documents into vector embeddings for intelligent similarity searches
- Retrieves the most relevant movie information based on user queries
- Handles complex questions by finding contextually similar passages

### 💾 **Persistent Knowledge Base**
- Loads and processes PDF documents containing movie trivia information
- Splits documents into manageable chunks for efficient retrieval
- Stores embeddings in a vector database for fast lookups

### 🧠 **Conversational Context**
- Maintains chat history per session for multi-turn conversations
- Understands follow-up questions in context
- Provides coherent, sequential responses based on previous exchanges

### 🎨 **User-Friendly Interface**
- Built with Gradio for an intuitive web-based experience
- Real-time chat interaction with clear message flow
- One-click session clearing for starting fresh conversations

### 🔐 **Privacy-First Design**
- All processing happens locally on your machine
- No data sent to external APIs
- Complete control over your data and conversations

---

## 🏗️ Architecture

### System Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    MovieBot System Flow                      │
└─────────────────────────────────────────────────────────────┘

1. INITIALIZATION PHASE
   ├── Load PDF Document (movies_trivia.pdf)
   ├── Split into Chunks (150 chars, 20-char overlap)
   ├── Generate Embeddings (Ollama granite-embedding model)
   └── Store in Vector DB (Chroma)

2. USER INTERACTION PHASE
   ├── User Enters Question
   ├── System Converts Question to Embedding
   ├── Search Vector DB for Top 4 Similar Chunks
   ├── Format Context + Chat History
   └── Send to Local LLM (Mistral/Llama3)

3. RESPONSE PHASE
   ├── LLM Generates Answer Based on Context
   ├── Store Q&A in Session History
   ├── Return Answer to User
   └── Maintain Conversation State
```

### Key Components

#### **1. Document Processing Pipeline**
```python
PDF Document → Text Extraction → Chunking → Embeddings → Vector Store
```
- **PyPDFLoader**: Extracts text from PDF files
- **CharacterTextSplitter**: Breaks documents into overlapping chunks
- **OllamaEmbeddings**: Converts text to vector representations

#### **2. Retrieval Augmented Generation (RAG) Pipeline**
```python
User Query → Embedding → Semantic Search → Context Retrieval → LLM Inference
```
- **Semantic Search**: Finds contextually relevant information using vector similarity
- **Context Injection**: Provides relevant passages to the LLM
- **Grounded Responses**: LLM generates answers based only on retrieved context

#### **3. Conversation Management**
```python
User Input → Session Lookup → Add to History → Generate Response → Update History
```
- Each user gets a unique session ID
- Chat history is maintained in memory for the session duration
- History is used to provide contextual follow-up responses

---

## 📦 System Requirements

### Hardware
- **Processor**: Multi-core CPU recommended
- **RAM**: 8GB minimum, 16GB+ recommended for smooth operation
- **Storage**: 5GB+ for models and vector database
- **Network**: Optional (for initial Ollama model download)

### Software
- **Python**: 3.10 or higher
- **Ollama**: Installed and running locally
- **Operating System**: Windows, macOS, or Linux

---

## 🚀 Installation

### Step 1: Install Ollama

Download and install Ollama from [ollama.ai](https://ollama.ai). After installation, ensure Ollama is running:

```bash
# Pull required models
ollama pull mistral           # Main language model
ollama pull granite-embedding # Embedding model
```

Verify Ollama is running (typically on `localhost:11434`):
```bash
curl http://localhost:11434/api/tags
```

### Step 2: Clone or Download Project

```bash
# Navigate to project directory
cd path/to/Movie_Trivia_Chatbot_Project_Description
```

### Step 3: Install Python Dependencies

```bash
# Create virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 4: Prepare Movie Trivia PDF

Ensure `movies_trivia.pdf` is in the project root directory. The system will automatically load it on startup.

---

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the project root (already in `.gitignore`):

```env
# PDF file path
PDF_PATH=./movies_trivia.pdf

# Local Ollama LLM model (mistral or llama3)
LLM_MODEL=mistral

# Optional: LangSmith tracing (for debugging/monitoring)
LANGSMITH_API_KEY=your_key_here
LANGSMITH_PROJECT=your_project_name
```

### Configuration Details

| Variable | Default | Description |
|----------|---------|-------------|
| `PDF_PATH` | `./movies_trivia.pdf` | Path to the movie trivia PDF document |
| `LLM_MODEL` | `mistral` | Ollama model name (`mistral` or `llama3`) |
| `LANGSMITH_API_KEY` | Optional | API key for LangSmith tracing (debugging) |
| `LANGSMITH_PROJECT` | Optional | Project name for LangSmith |

---

## 🔧 How It Works

### Phase 1: Knowledge Base Initialization

When you start the application:

1. **PDF Loading**
   - PyPDFLoader reads all pages from `movies_trivia.pdf`
   - Extracts raw text from each page
   - Returns a list of document objects with page content

2. **Text Chunking**
   - CharacterTextSplitter divides text into 150-character chunks
   - Maintains 20-character overlap between chunks for context continuity
   - Prevents loss of information at chunk boundaries
   - Creates semantically coherent pieces for embedding

   *Example chunking*:
   ```
   Original: "Christopher Nolan directed The Dark Knight in 2008. 
              It starred Christian Bale and Heath Ledger..."
   
   Chunk 1: "Christopher Nolan directed The Dark Knight in 2008. 
            It starred Christian"
   Chunk 2: "It starred Christian Bale and Heath Ledger as the..."
   ```

3. **Embedding Generation**
   - `OllamaEmbeddings` with `granite-embedding:latest` model
   - Converts each chunk into a 1024-dimensional vector representation
   - Captures semantic meaning (similar concepts cluster together)
   - Enables fast similarity-based search

4. **Vector Store Creation**
   - Chroma vector database stores all embeddings
   - Indexes them for fast retrieval
   - Persists data to `.chroma/movie_trivia` directory
   - Allows reuse without re-processing on subsequent runs

### Phase 2: Query Processing

When a user asks a question:

1. **Query Embedding**
   - User input is converted to the same vector space as documents
   - Uses the same embedding model for consistency

2. **Semantic Search**
   - Calculates similarity between query vector and all stored vectors
   - Retrieves top 4 most relevant document chunks
   - Uses cosine similarity metric for comparison
   - Scores represent relevance (higher = more relevant)

3. **Context Assembly**
   - Combines retrieved chunks with recent chat history
   - Formats as:
     ```
     Conversation History:
     User: [previous questions]
     Assistant: [previous answers]
     
     Context:
     [Retrieved document chunks]
     
     User Question: [Current query]
     ```

4. **LLM Processing**
   - Sends formatted prompt to local Ollama model
   - Model generates response based solely on provided context
   - Instructed to refuse answering if info not in context
   - Ensures accuracy and prevents confabulation

5. **Response Generation**
   - Returns answer to user interface
   - Stores Q&A pair in session history
   - History becomes part of next query's context

### Phase 3: Session Management

- **Session Isolation**: Each user gets unique session ID (UUID)
- **Memory Storage**: Chat history kept in `_sessions` dictionary
- **Context Window**: Last 6 conversation turns included in new queries
- **Session Clearing**: Users can clear history to start fresh

---

## 💬 Usage

### Starting the Application

```bash
python movie_chatbot.py
```

The system will:
1. Load and process the PDF (first run takes a few seconds)
2. Initialize the vector database
3. Start Gradio web interface
4. Display a local URL (typically `http://127.0.0.1:7860`)

### Interacting with MovieBot

**In the Gradio Interface:**

1. **Ask Questions**
   - Type natural language questions in the text box
   - Examples:
     - "Who directed The Shawshank Redemption?"
     - "What year was Inception released?"
     - "Which movie won Best Picture in 2020?"

2. **Multi-Turn Conversations**
   - Follow-up questions reference previous context
   - Maintain conversational flow naturally
   - Ask about details from previous answers

3. **Clear History**
   - Click "Clear History" button to reset session
   - Starts new conversation with fresh context
   - Maintains separate sessions for multiple users

### Example Interaction

```
User: "When was Interstellar released?"
Bot: "Interstellar was released on November 7, 2014."

User: "Who directed it?"
Bot: "Interstellar was directed by Christopher Nolan."

User: "What was the budget?"
Bot: "According to the provided context, the budget information 
     for Interstellar is not available in my knowledge base."
```

---

## 📁 Project Structure

```
Movie_Trivia_Chatbot_Project_Description/
├── movie_chatbot.py              # Main application file
├── requirements.txt              # Python dependencies
├── movies_trivia.pdf             # Movie knowledge base
├── movies_trivia.pdf             # Additional PDF resource
├── .gitignore                    # Git ignore file (includes .env)
├── README.md                     # This file
├── .chroma/                      # Vector database (auto-created)
│   └── movie_trivia/             # Chroma collection storage
└── .env                          # Environment variables (local only)
```

### File Descriptions

| File | Purpose |
|------|---------|
| `movie_chatbot.py` | Core application with RAG pipeline and UI |
| `requirements.txt` | All Python package dependencies |
| `movies_trivia.pdf` | Movie trivia knowledge base |
| `.chroma/` | Persistent vector database storage |
| `.env` | Configuration (not in version control) |

---

## 🛠️ Technology Stack

### Core Libraries

| Library | Version | Purpose |
|---------|---------|---------|
| **LangChain** | 0.3+ | Orchestration framework for RAG pipelines |
| **LangChain Community** | 0.3+ | Integrations for Ollama, PDF loading, Chroma |
| **Chroma** | 0.5+ | Vector database for embeddings |
| **Ollama** | Local | Local LLM and embedding models |
| **Gradio** | 4.0+ | Web UI for user interaction |
| **PyPDF** | 4.0+ | PDF text extraction |
| **Python-dotenv** | Latest | Environment variable management |

### Models

| Model | Purpose | Provider |
|-------|---------|----------|
| **Mistral** (default) | Text generation / QA | Ollama |
| **Llama3** (optional) | Alternative text generation | Ollama |
| **Granite-embedding** | Vector embeddings | Ollama |

### Data Flow Architecture

```
┌──────────────────┐
│  PDF Document    │
└────────┬─────────┘
         │
         └─→ PyPDFLoader → CharacterTextSplitter → OllamaEmbeddings
                                                          │
                                                          ↓
                                                   ┌──────────────┐
                                                   │ Chroma DB    │
                                                   │(Vector Store)│
                                                   └──────────────┘
                                                          ↑
                                                          │
┌──────────────────┐                             ┌──────────────┐
│ User Question    │─→ (embed) ────────→ retrieval (get top 4)
└─────────┬────────┘                             └──────────────┘
          │                                               │
          │  ┌─────────────────────────────────────────────┘
          │  │
          └─→ └─→ Format Prompt + Chat History
                            │
                            ↓
                    ┌──────────────────┐
                    │  Ollama LLM      │
                    │ (Generate Answer)│
                    └────────┬─────────┘
                             │
                             ↓
                    ┌──────────────────┐
                    │ Response to User │
                    │Store in History  │
                    └──────────────────┘
```

---

## 🎓 Understanding RAG

**Retrieval Augmented Generation** is a technique that:

1. **Retrieves** relevant information from a knowledge base (vector search)
2. **Augments** the LLM prompt with retrieved context
3. **Generates** responses based on both context and learned knowledge

### Why RAG?

- **Accuracy**: Answers grounded in specific documents
- **Freshness**: Easy to update knowledge by changing PDF
- **Transparency**: Can trace which documents informed an answer
- **Local**: No need for fine-tuning or cloud APIs

### How MovieBot Uses RAG

```
Question: "Who directed The Dark Knight?"

Step 1 - Retrieve:
  Search for chunks mentioning "Dark Knight" or "director"
  → Found: "Christopher Nolan directed The Dark Knight (2008)"

Step 2 - Augment:
  Create prompt:
  Context: "Christopher Nolan directed The Dark Knight (2008)"
  Question: "Who directed The Dark Knight?"

Step 3 - Generate:
  LLM reads context + question
  → "Christopher Nolan directed The Dark Knight."
```

---

## 🔄 Chat History Management

### How Conversation State Works

1. **Session Creation**
   - New session ID (UUID) generated when user loads interface
   - Unique session to prevent conflicts between users

2. **Message Storage**
   - Each user message stored with metadata
   - Each bot response stored with metadata
   - Stored in `_sessions[session_id]` dictionary (in-memory)

3. **Context Window**
   - Last 6 conversation turns included with new queries
   - Prevents prompt bloat with old conversations
   - Maintains relevant context for follow-ups

4. **Session Clearing**
   - User clicks "Clear History" button
   - All messages for session deleted
   - New session ID generated
   - Conversation starts fresh

### Example Session Flow

```python
Session ID: 550e8400-e29b-41d4-a716-446655440000

Initial State: []

After Q1: 
[
  {"type": "user", "content": "Who directed Inception?"},
  {"type": "ai", "content": "Christopher Nolan directed Inception."}
]

After Q2:
[
  {"type": "user", "content": "Who directed Inception?"},
  {"type": "ai", "content": "Christopher Nolan directed Inception."},
  {"type": "user", "content": "When was it released?"},
  {"type": "ai", "content": "Inception was released on July 16, 2010."}
]
```

---

## 🚨 Troubleshooting

### Ollama Not Running
**Problem**: "Connection refused" errors
```bash
# Ensure Ollama is running
ollama serve
```

### Models Not Installed
**Problem**: "Model not found" errors
```bash
ollama pull mistral
ollama pull granite-embedding:latest
```

### PDF Not Found
**Problem**: "FileNotFoundError"
- Ensure `movies_trivia.pdf` is in project root
- Or set correct path in `.env`

### Slow Response Times
**Problem**: Initial query takes too long
- First query involves initialization; subsequent queries are faster
- Ensure adequate RAM and CPU available
- Consider using lighter model if system is constrained

---

## 📝 Notes

- The application uses local models only; no data is sent externally
- Vector database is cached in `.chroma/` directory for faster subsequent startups
- Chat history is kept in memory and clears when the application stops
- The system follows a "retrieve first" approach to minimize LLM hallucinations

---

**MovieBot** - Bringing movie knowledge to your fingertips through intelligent retrieval and generation. 🎬✨
