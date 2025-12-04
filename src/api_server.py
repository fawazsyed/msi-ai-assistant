"""
FastAPI server to connect the Angular UI to the LangChain backend.

This server provides a REST API that the Angular frontend can call,
bridging the gap between the web UI and your LangChain agent.
"""

import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from pathlib import Path
import json
from dotenv import load_dotenv

# LangChain imports
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain.agents import create_agent
from langchain.agents.middleware import ToolCallLimitMiddleware
from langchain.chat_models import init_chat_model
from langchain_core.tools import tool
from langchain_core.rate_limiters import InMemoryRateLimiter
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_mcp_adapters.client import MultiServerMCPClient
from utils import setup_logging

# Get project root (parent of src/)
PROJECT_ROOT = Path(__file__).parent.parent

# Setup logging
logger = setup_logging(PROJECT_ROOT, keep_recent=10)

# Load environment variables from .env file
load_dotenv()

app = FastAPI(title="MSI AI Assistant API")

# Enable CORS for Angular dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],  # Angular dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables for agent and vector store (initialized on startup)
agent = None
vector_store = None
mcp_client = None


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: list[ChatMessage]


async def initialize_agent():
    """Initialize the LangChain agent, vector store, and MCP tools"""
    global agent, vector_store, mcp_client

    logger.info("Initializing LangChain agent...")

    # RATE LIMITING: Protect against API overspending
    rate_limiter = InMemoryRateLimiter(
        requests_per_second=2,  # 2 requests/second = 120 requests/minute
        check_every_n_seconds=0.1,  # Check every 100ms
        max_bucket_size=10,  # Allow bursts of up to 10 requests
    )
    logger.info("Rate limiter configured: 2 requests/second (120 RPM)")

    # Initialize LLM - Using OpenAI GPT-4o-mini (cheaper, faster)
    # GPT-4o-mini is cost-effective: $0.15 per 1M input tokens
    model = init_chat_model(
        "gpt-4o-mini",
        model_provider="openai",
        rate_limiter=rate_limiter  # Add rate limiting
    )

    # Alternative models (if you want to switch):
    # model = init_chat_model("gpt-4o", model_provider="openai", rate_limiter=rate_limiter)
    # model = init_chat_model("claude-3-5-sonnet-20241022", model_provider="anthropic", rate_limiter=rate_limiter)
    # model = init_chat_model("gemini-2.0-flash-exp", model_provider="google-genai", rate_limiter=rate_limiter)

    # Initialize embeddings
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

    # Initialize vector store
    doc_path = PROJECT_ROOT / "documents" / "video_manager_admin_guide.txt"
    try:
        with open(doc_path, "r", encoding="utf-8") as f:
            doc_content = f.read()
    except FileNotFoundError:
        logger.error(f"Document not found: {doc_path}")
        raise

    persist_dir = str(PROJECT_ROOT / "chroma_langchain_db")
    vector_store = Chroma(
        collection_name="msi_support_docs",
        embedding_function=embeddings,
        persist_directory=persist_dir,
    )

    # Add documents if needed
    if vector_store._collection.count() == 0:
        logger.info("Indexing documents...")
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1500,
            chunk_overlap=300,
            separators=["\n\n", "\n", ". ", " ", ""],
        )
        chunks = text_splitter.split_text(doc_content)
        vector_store.add_texts(texts=chunks)
        logger.info(f"Indexed {len(chunks)} document chunks")
    else:
        logger.info("Using existing vector store")

    # Create RAG tool for documentation search
    @tool
    def search_msi_documentation(query: str) -> str:
        """Search Motorola Solutions product documentation for information.

        Use this tool when the user asks questions about:
        - How to use MSI products (Video Manager, etc.)
        - Product features and capabilities
        - Configuration and setup instructions
        - Troubleshooting and support
        - User management and administration

        Args:
            query: The search query to find relevant documentation

        Returns:
            Relevant documentation excerpts that answer the query
        """
        retrieved_docs = vector_store.similarity_search(query, k=2)

        if not retrieved_docs:
            return "No relevant documentation found for this query."

        docs_content = "\n\n---\n\n".join(
            f"Document excerpt {i+1}:\n{doc.page_content}"
            for i, doc in enumerate(retrieved_docs)
        )

        return docs_content

    # Load MCP tools
    try:
        mcp_client = MultiServerMCPClient(
            {
                "math": {
                    "command": "python",
                    "args": [str(PROJECT_ROOT / "src" / "mcp_server.py")],
                    "transport": "stdio",
                },
                "weather": {
                    "url": "http://localhost:8000/mcp",
                    "transport": "streamable_http",
                }
            }
        )

        mcp_tools = await mcp_client.get_tools()
        logger.info(f"Loaded {len(mcp_tools)} MCP tools: {[t.name for t in mcp_tools]}")
    except Exception as e:
        logger.warning(f"Could not load all MCP tools: {e}")
        mcp_tools = []

    # Create agent with MCP tools and RAG tool
    all_tools = mcp_tools + [search_msi_documentation]

    # TOOL CALL LIMITS: Prevent runaway loops and excessive API usage
    tool_call_limit = ToolCallLimitMiddleware(
        run_limit=15,  # Max 15 tool calls per single user query
        exit_behavior="continue"  # Continue and return response when limit hit
    )
    logger.info("Tool call limit configured: 15 calls per query")

    agent = create_agent(
        model,
        tools=all_tools,
        middleware=[tool_call_limit],  # Prevent excessive API calls
        system_prompt=(
            "You are an MSI Support Assistant powered by Motorola Solutions. "
            "You have access to product documentation via the search_msi_documentation tool. "
            "When users ask about MSI products, features, or how-to questions, "
            "use the search tool to find relevant information before answering. "
            "Always provide accurate information based on the documentation."
        )
    )

    logger.info("Agent initialization complete!")


@app.on_event("startup")
async def startup_event():
    """Initialize agent when the server starts"""
    await initialize_agent()


@app.get("/")
async def root():
    """Health check endpoint"""
    return {"status": "ok", "message": "MSI AI Assistant API is running"}


@app.post("/api/chat")
async def chat(request: ChatRequest):
    """
    Simple non-streaming chat endpoint.
    Returns the complete response from the LangChain agent.
    """
    if agent is None:
        return {"error": "Agent not initialized", "content": "Server is starting up, please try again."}

    try:
        # Run the agent (it will decide whether to use the RAG tool)
        result = await agent.ainvoke({
            "messages": [{"role": m.role, "content": m.content} for m in request.messages]
        })

        # Extract the assistant's response
        assistant_message = result["messages"][-1].content if result.get("messages") else ""

        # Extract tool calls if any (for debugging/visibility)
        tool_calls = []
        for msg in result.get("messages", []):
            if hasattr(msg, "tool_calls") and msg.tool_calls:
                tool_calls.extend([
                    {"name": tc.get("name", ""), "args": tc.get("args", {})}
                    for tc in msg.tool_calls
                ])

        return {
            "content": assistant_message,
            "toolCalls": tool_calls
        }

    except Exception as e:
        logger.error(f"Chat error: {e}", exc_info=True)
        return {"error": str(e), "content": "Sorry, I encountered an error processing your request."}


@app.post("/api/chat/stream")
async def chat_stream(request: ChatRequest):
    """
    Streaming chat endpoint.
    Sends server-sent events (SSE) to the Angular frontend as the agent processes the query.
    """
    if agent is None:
        async def error_stream():
            yield f"data: {json.dumps({'type': 'error', 'error': 'Agent not initialized'})}\n\n"
        return StreamingResponse(error_stream(), media_type="text/event-stream")

    async def event_stream():
        try:
            # Get the last message
            last_message = request.messages[-1].content
            logger.info(f"Processing query: {last_message}")

            # Stream agent response (agent will call RAG tool if needed)
            full_content = ""
            event_count = 0

            # Use stream_mode="values" to get complete state updates
            async for chunk in agent.astream(
                {"messages": [{"role": m.role, "content": m.content} for m in request.messages]},
                stream_mode="values"
            ):
                event_count += 1

                # Get all messages from the chunk
                messages = chunk.get("messages", [])
                if not messages:
                    logger.debug(f"Event {event_count}: No messages in chunk")
                    continue

                # Get the last message (most recent)
                last_msg = messages[-1]
                msg_class_name = type(last_msg).__name__
                msg_type = getattr(last_msg, 'type', 'unknown')  # LangChain uses 'type' not 'role'
                msg_content = getattr(last_msg, 'content', '')
                msg_has_tool_calls = hasattr(last_msg, 'tool_calls') and last_msg.tool_calls

                logger.info(f"Event {event_count}: class={msg_class_name}, type={msg_type}, content_len={len(str(msg_content)) if msg_content else 0}, has_tools={msg_has_tool_calls}")

                # Skip human and system messages (only process AI messages)
                if msg_type != 'ai':
                    continue

                # Check for tool calls
                if hasattr(last_msg, "tool_calls") and last_msg.tool_calls:
                    for tool_call in last_msg.tool_calls:
                        tool_data = {
                            "type": "tool_call",
                            "toolCall": {
                                "id": tool_call.get("id", ""),
                                "name": tool_call.get("name", ""),
                                "args": tool_call.get("args", {})
                            }
                        }
                        event_json = json.dumps(tool_data)
                        logger.info(f"Event {event_count}: Sending tool_call: {tool_call.get('name')}")
                        yield f"data: {event_json}\n\n"

                # Send content updates
                if hasattr(last_msg, "content") and last_msg.content:
                    current_content = str(last_msg.content)

                    # Only send if content changed
                    if current_content != full_content:
                        full_content = current_content
                        content_data = {
                            "type": "content",
                            "content": full_content
                        }
                        logger.info(f"Event {event_count}: Sending content update (length: {len(full_content)})")
                        yield f"data: {json.dumps(content_data)}\n\n"

            # Always send final content (even if empty)
            final_content_data = {
                "type": "content",
                "content": full_content if full_content else "I processed your request."
            }
            logger.info(f"Sending final content (length: {len(full_content)}, events: {event_count})")
            yield f"data: {json.dumps(final_content_data)}\n\n"

            # Signal completion
            done_event = json.dumps({'type': 'done'})
            logger.info(f"Query completed. Total events: {event_count}, Final content length: {len(full_content)}")
            yield f"data: {done_event}\n\n"

        except Exception as e:
            logger.error(f"Streaming error: {e}", exc_info=True)
            error_data = {
                "type": "error",
                "error": str(e)
            }
            yield f"data: {json.dumps(error_data)}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable nginx buffering
        }
    )


if __name__ == "__main__":
    import uvicorn
    print("Starting MSI AI Assistant API Server...")
    print("API: http://localhost:8080")
    print("Connect to Angular UI at http://localhost:4200")
    uvicorn.run(app, host="0.0.0.0", port=8080, log_level="info")
