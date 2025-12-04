# Getting Started with MSI AI Assistant

Setup guide for the agentic RAG system with MCP integration.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [API Keys Setup](#api-keys-setup)
4. [LangSmith Configuration](#langsmith-configuration-optional)
5. [Running the Application](#running-the-application)
6. [Troubleshooting](#troubleshooting)
7. [Team Collaboration](#team-collaboration)

---

## Prerequisites

### Python Version Requirement
**You MUST use Python 3.12.10** - This project is NOT compatible with Python 3.13.x due to compatibility issues with LangChain and Chroma dependencies.

Check your Python version:
```bash
python --version
```

If you need to install Python 3.12.10:
- **Windows**: Download from [python.org](https://www.python.org/downloads/release/python-31210/)
- **macOS/Linux**: Use `pyenv` to install and manage Python versions

### Package Manager
This project uses [uv](https://github.com/astral-sh/uv) for fast, reliable package management.

Install uv:
```bash
# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
```

---

## Installation

### 1. Clone the Repository
```bash
git clone https://github.com/fawazsyed/msi-ai-assistant.git
cd msi-ai-assistant
```

### 2. Set Python Version
Ensure the project uses Python 3.12.10:
```bash
uv python pin 3.12.10
```

### 3. Install Dependencies
```bash
uv sync
```

This installs all required packages:
- LangChain and LangChain OpenAI
- Chroma vector store (persistent)
- OpenAI Python client
- Python-dotenv for environment variables

---

## API Keys Setup

### OpenAI API Key (Required)

1. **Create an OpenAI Account**
   - Go to [platform.openai.com](https://platform.openai.com/)
   - Sign up or log in

2. **Generate API Key**
   - Navigate to [API Keys](https://platform.openai.com/api-keys)
   - Click **"Create new secret key"**
   - Give it a name (e.g., "MSI Support Assistant")
   - Copy the key immediately (you won't see it again!)

3. **Add Billing Information**
   - Go to [Billing Settings](https://platform.openai.com/account/billing)
   - Add a payment method
   - Set usage limits to avoid unexpected charges

### Configure Environment Variables

1. **Copy the template file:**
   ```bash
   cp .env.example .env
   ```

2. **Edit `.env` and add your OpenAI key:**
   ```bash
   OPENAI_API_KEY=sk-proj-your-actual-key-here
   ```

**Security Note**: Never commit the `.env` file to version control. It's already in `.gitignore`.

---

## LangSmith Configuration (Optional)

LangSmith provides powerful observability for your RAG pipeline - highly recommended for development!

### What LangSmith Provides:
- 🔍 Trace every LLM call and retrieval step
- 💰 See token usage and costs per query
- 📊 Debug retrieval quality (which chunks matched, similarity scores)
- 🧪 Compare experiments side-by-side
- 🐛 Understand why queries succeed or fail

### Setup Steps:

1. **Create LangSmith Account**
   - Go to [smith.langchain.com](https://smith.langchain.com)
   - Sign up (free tier: 5,000 traces/month)

2. **Generate API Key**
   - Navigate to Settings → API Keys
   - Click **"Create API Key"**
   - Key Type: Select **"Personal Access Token"**
   - Description: `msi-ai-assistant-dev` (or your name)
   - Expiration: Choose **"Never"** or **"1 year"**
   - Copy the key (starts with `lsv2_pt_...`)

3. **Add to `.env`**
   ```bash
   LANGSMITH_TRACING=true
   LANGSMITH_API_KEY=lsv2_pt_your-actual-key-here
   LANGSMITH_PROJECT=msi-ai-assistant
   ```

4. **View Traces**
   - After running the app, visit [smith.langchain.com](https://smith.langchain.com)
   - Navigate to Projects → `msi-ai-assistant`
   - See detailed traces of every query

---

## Running the Application

### Basic Usage
```bash
uv run src/main.py
```

### What Happens:
1. Loads the VideoManager Admin Guide documentation
2. Creates embeddings using OpenAI's `text-embedding-3-small`
3. Indexes the document in a Chroma vector store (persists to `./chroma_langchain_db/`)
4. Runs a sample query: "How do I add a new user?"
5. Displays the AI-generated answer based on retrieved documentation

**Note**: First run takes longer (embedding documents). Subsequent runs are faster as the vector store is persistent.

### Expected Output
```
2024-12-01 10:30:15 - __main__ - INFO - Using existing vector store
2024-12-01 10:30:15 - __main__ - INFO - Question: How do I add a new user?

================================ Human Message =================================

How do I add a new user?

================================== Ai Message ==================================

To add a new user in VideoManager, follow these steps:
1. Navigate to the Admin tab.
2. Select the Users pane.
...
```

---

## Troubleshooting

### Rate Limit Error (429)
```
openai.RateLimitError: Error code: 429 - Request too large
```
**Solution:**
- Your OpenAI account has token limits (30,000 TPM for free tier)
- Wait a minute and try again
- The chunking implementation reduces this issue

### Python Version Error
```
ERROR: No solution found when resolving dependencies
```
**Solution:**
- Verify Python version: `python --version`
- Must be 3.12.x (NOT 3.13.x)
- Use `uv python pin 3.12.10` to set correct version

### Missing API Key
```
openai.OpenAIError: The api_key client option must be set
```
**Solution:**
- Check that `.env` file exists in project root
- Verify `OPENAI_API_KEY` is set correctly in `.env`
- Key should start with `sk-proj-` or `sk-`

### Import Errors
```
ModuleNotFoundError: No module named 'langchain'
```
**Solution:**
- Run `uv sync` to install all dependencies
- Ensure you're in the project directory

### LangSmith Not Working
```
No traces appearing in LangSmith dashboard
```
**Solution:**
- Verify `LANGSMITH_TRACING=true` in `.env`
- Check API key is correct (starts with `lsv2_pt_`)
- Ensure project name matches: `LANGSMITH_PROJECT=msi-ai-assistant`
- Check LangSmith status at [status.smith.langchain.com](https://status.smith.langchain.com)

---

## Team Collaboration

### For Team Leads

1. **Invite team members to LangSmith workspace:**
   - Go to [smith.langchain.com](https://smith.langchain.com) → Settings → Members
   - Send invitations via email
   - Members will share the same workspace and project

2. **Share repository access:**
   - Add team members to the GitHub repository
   - Ensure they have read/write access

### For New Team Members

1. **Accept LangSmith workspace invitation** (check your email)
2. **Follow all installation steps above**
3. **Create your own API keys:**
   - OpenAI: Your own account and key
   - LangSmith: Your own Personal Access Token
4. **Use the same project name:** `msi-ai-assistant`
5. **All team traces will appear in the shared project**

### Team Benefits
- ✅ **Shared Learning**: Everyone sees each other's traces and experiments
- ✅ **No Key Sharing**: Each person has their own API keys (more secure)
- ✅ **Easy Debugging**: "Check my trace from 10 minutes ago"
- ✅ **Cost Tracking**: See token usage per team member
- ✅ **Compare Experiments**: Side-by-side comparison of different approaches

### Best Practices
- Use descriptive run names for your experiments
- Add metadata tags to categorize traces
- Review team traces weekly to learn from each other
- Document interesting findings in the repository

---

## Next Steps

Once you're up and running:

1. **Explore the code**: Start with `src/main.py`
2. **Try different queries**: Modify the sample question
3. **Check LangSmith traces**: Understand how RAG retrieval works
4. **Read the architecture docs**: Understand the RAG pipeline
5. **Start contributing**: Check open issues and project roadmap

---

## Additional Resources

- [LangChain Documentation](https://python.langchain.com/)
- [LangSmith Observability Guide](https://docs.smith.langchain.com/)
- [OpenAI API Reference](https://platform.openai.com/docs/api-reference)
- [Chroma Vector Store Docs](https://docs.trychroma.com/)
- [uv Package Manager](https://github.com/astral-sh/uv)

---

## Need Help?

- **Issues**: Open an issue on GitHub
- **Questions**: Ask in your team's communication channel
- **LangSmith Support**: [smith.langchain.com/support](https://smith.langchain.com/support)
- **OpenAI Support**: [help.openai.com](https://help.openai.com/)
