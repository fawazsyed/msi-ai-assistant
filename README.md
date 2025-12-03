# MSI AI Assistant

AI-powered Assistant for Motorola Solutions using Model Context Protocol (MCP) and LangChain (RAG).

---

> **📚 UTDesign Capstone Project**  
> This project is developed as part of the UTDesign Capstone program.  
> **Sponsor:** Motorola Solutions  
> **Note:** This is a student project and not an official Motorola Solutions product.

---

## 🚀 Quick Start

**New to the project?** Follow our comprehensive setup guide: **[GETTING_STARTED.md](GETTING_STARTED.md)**

**Already set up?** Run the application:
```bash
uv run src/rag_agent.py "[Question regarding documentation]"
```

---

## 📋 Project Overview

This project implements a RAG (Retrieval-Augmented Generation) system that:
- Indexes Motorola Solutions product documentation
- Retrieves relevant context using vector similarity search
- Generates accurate answers using OpenAI's GPT-4o
- Provides observability through LangSmith tracing

**Current Status:** In development - Core RAG functionality implemented with document chunking

---

## ⚙️ Technology Stack

- **Language**: Python 3.12.10
- **Package Manager**: uv
- **LLM**: OpenAI GPT-4o
- **Embeddings**: OpenAI text-embedding-3-small
- **Vector Store**: Chroma (persistent, local)
- **Framework**: LangChain
- **Observability**: LangSmith (optional)
- **RAG Architecture**: Dynamic prompt middleware with similarity search
- **Web Crawler/Scraper**: Crawl4AI

---

## 📁 Project Structure

```
msi-ai-assistant/
├── src/                    # Source code
│   ├── main.py             # Main RAG application
│   └── utils.py            # Logging and utility functions
├── documents/              # Knowledge base documents (~90K tokens total)
│   ├── video_manager_admin_guide.txt        (~75K tokens, 357K chars)
│   └── video_manager_admin_guide_user.txt   (~15K tokens, 70K chars)
├── logs/                   # Application logs (not in git)
│   └── archive/            # Archived logs
├── tests/                  # Test outputs and validation
├── dev_resources/          # Development references
├── research/               # Research data (not in git)
├── chroma_langchain_db/    # Persistent vector store (not in git)
├── pyproject.toml          # Project dependencies
├── .env                    # API keys (not in git)
├── .env.example            # Template for .env
├── GETTING_STARTED.md      # Complete setup guide
└── README.md               # This file
```

---

## 🎯 Key Features

- ✅ **Document Chunking**: RecursiveCharacterTextSplitter (1000 chars, 200 overlap)
- ✅ **Persistent Vector Store**: Chroma with local persistence
- ✅ **LangSmith Tracing**: Full observability of RAG pipeline
- ✅ **Auto-archived Logging**: Timestamped logs with automatic archiving
- ✅ **Team Collaboration**: Shared LangSmith workspace support

---

## 📚 Requirements

- **Python 3.12.10** (NOT 3.13.x - compatibility issues)
- **OpenAI API Key** (required for LLM and embeddings)
- **LangSmith API Key** (optional but recommended for observability)

**Full setup instructions:** [GETTING_STARTED.md](GETTING_STARTED.md)

---

## 🧪 Testing

Test outputs are documented in the `tests/` folder for validation and debugging.

### Recent Tests

**Test 01: Base RAG Implementation**
- Query: "How do I add a new user?"
- Status: ✓ PASSED
- Configuration: k=2 similarity search, Chroma persistence
- Result: Generated accurate 16-step instructions

**Test 02: Document Chunking**
- Status: ✓ PASSED  
- Configuration: RecursiveCharacterTextSplitter (chunk_size=1000, chunk_overlap=200)
- Result: ~30-40 chunks from 23,400-token document
- Improvement: Eliminates rate limit errors, enables better context retrieval

See `tests/` folder for complete test outputs and evaluations.

---

## 🛠️ Development

### Running the Application
```bash
uv run src/main.py
```

### Project Commands
```bash
# Install/update dependencies
uv sync

# Set Python version
uv python pin 3.12.10

# Run with specific environment
uv run --env-file .env src/main.py
```

---

## 🤝 Contributing

This is a team project for Motorola Solutions support assistant development.

### For Team Members
1. Read [GETTING_STARTED.md](GETTING_STARTED.md) for complete setup
2. Join the LangSmith workspace (ask team lead for invitation)
3. Create your own API keys (OpenAI + LangSmith)
4. Use project name: `msi-ai-assistant` for shared traces

### Best Practices
- Use LangSmith to track your experiments
- Add descriptive metadata to traces
- Document findings in test files
- Keep `.env` file private (never commit)

---

## 🗺️ Roadmap

## 🗺️ Roadmap

### ✅ Completed
- Core RAG implementation with LangChain
- Document chunking (RecursiveCharacterTextSplitter)
- Persistent vector store (Chroma)
- LangSmith tracing integration
- Auto-archived logging (keeps 10 recent, archives older)
- Team collaboration setup


### 📋 Planned
- Interactive chat interface
- MCP (Model Context Protocol) integration
- Web scraping for docs.motorolasolutions.com
- Real-time document updates

---

## 📖 Documentation

- **[GETTING_STARTED.md](GETTING_STARTED.md)** - Complete setup guide
- **tests/** - Test outputs and validations

---

## 📄 License

[Add license information]

---

**Built with ❤️ for Capstone Sponsor: Motorola Solutions-CPS**