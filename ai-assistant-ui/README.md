# MSI AI Assistant - Angular UI

A modern, feature-rich Angular UI for the MSI AI Assistant powered by LangChain. This application provides a complete chat interface with support for RAG (Retrieval-Augmented Generation), MCP tool integration, streaming responses, and markdown rendering.

## Features

### 🎨 Modern UI Components
- **Responsive Chat Interface**: Clean, intuitive design optimized for conversations
- **Sidebar Navigation**: Conversation history with quick switching
- **Message List**: Auto-scrolling message display with user/assistant differentiation
- **Smart Input**: Textarea with Enter-to-send and Shift+Enter for new lines

### 🚀 LangChain Integration
- **RAG Context Display**: Visualize retrieved documents from vector store
- **MCP Tool Calls**: See math, weather, and other tool executions in real-time
- **Streaming Responses**: Token-by-token message streaming with typing indicators
- **Conversation Management**: Create, load, and delete conversations

### 💎 Rich Content Rendering
- **Markdown Support**: Full markdown rendering with the `marked` library
- **Code Syntax Highlighting**: Beautiful code blocks using `highlight.js`
- **Tool Call Visualization**: Expandable tool execution details
- **RAG Context Cards**: Collapsible document chunks with similarity scores

### ♿ Accessibility & Performance
- **WCAG AA Compliant**: Focus management, ARIA attributes, color contrast
- **OnPush Change Detection**: Optimized performance with Angular signals
- **Standalone Components**: Modern Angular architecture (v21+)
- **Type-Safe**: Full TypeScript support with strict typing

## Architecture

### Component Structure

```
src/app/
├── components/
│   ├── chat-container/          # Main orchestrator component
│   ├── sidebar/                 # Conversation history sidebar
│   ├── message-list/            # Scrollable message display
│   ├── message-input/           # User input with keyboard shortcuts
│   ├── message-item/            # Individual message renderer
│   ├── markdown/                # Markdown renderer with syntax highlighting
│   ├── tool-calls/              # MCP tool execution display
│   └── rag-context/             # RAG document context display
├── services/
│   └── langchain-api.service.ts # LangChain backend communication
├── models/
│   └── message.model.ts         # TypeScript interfaces for messages
└── app.ts                       # Root component
```

### State Management

Uses **Angular Signals** for reactive state management:
- `currentConversation`: Active conversation
- `conversations`: List of all conversations
- `isLoading`: Loading state indicator
- `error`: Error message display

### LangChain Backend Integration

The UI is designed to work with your existing LangChain backend that includes:
- **RAG System**: Chroma vector store with OpenAI embeddings
- **MCP Tools**: Math server (stdio) and Weather server (HTTP)
- **Streaming**: Token-by-token response streaming
- **Dynamic Prompts**: Context injection middleware

## Installation & Setup

### Prerequisites

- Node.js 18+ and npm
- Angular CLI 21+

### Install Dependencies

```bash
cd ai-assistant-ui
npm install
```

### Development Server

```bash
npm start
```

Navigate to `http://localhost:4200/`

### Production Build

```bash
npm run build
```

Build artifacts will be in `dist/ai-assistant-ui/`

## Configuration

### Backend API Endpoint

Update the API URL in [langchain-api.service.ts](src/app/services/langchain-api.service.ts):

```typescript
private readonly apiUrl = 'http://localhost:8080/api';
```

### Connecting to Your LangChain Backend

The service currently uses **mock data** for demonstration. To connect to your real backend:

1. **Create a streaming endpoint** in your Python backend:
   ```python
   # Example FastAPI endpoint for streaming
   @app.post("/api/chat/stream")
   async def stream_chat(request: ChatRequest):
       async for chunk in agent.astream(...):
           yield {"type": "content", "data": chunk}
   ```

2. **Update the `streamResponse` method** in [langchain-api.service.ts](src/app/services/langchain-api.service.ts):
   ```typescript
   private async streamResponse(conversation: Conversation, message: Message): Promise<void> {
     const response = await fetch(`${this.apiUrl}/chat/stream`, {
       method: 'POST',
       headers: { 'Content-Type': 'application/json' },
       body: JSON.stringify({
         messages: conversation.messages.map(m => ({ role: m.role, content: m.content }))
       })
     });

     const reader = response.body?.getReader();
     // Process streaming chunks...
   }
   ```

### Example Backend Response Format

The UI expects streaming chunks in this format:

```typescript
// RAG context chunk
{ type: 'rag_context', ragContext: { documents: [...], similarity_scores: [...] } }

// Tool call chunk
{ type: 'tool_call', toolCall: { id: '...', name: 'add', args: { a: 5, b: 3 } } }

// Content chunk
{ type: 'content', content: 'partial response text...' }
```

## Customization

### Theming

Update the gradient colors in [sidebar.component.ts](src/app/components/sidebar/sidebar.component.ts):

```typescript
background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
```

### Company Branding

Replace "MSI Assistant" with your company name in:
- [sidebar.component.ts](src/app/components/sidebar/sidebar.component.ts)
- [message-item.component.ts](src/app/components/message-item/message-item.component.ts)
- [chat-container.component.ts](src/app/components/chat-container/chat-container.component.ts)

### Syntax Highlighting Theme

Change the code theme in [styles.scss](src/styles.scss):

```scss
@import 'highlight.js/styles/github-dark.css'; // or any other theme
```

Available themes: https://highlightjs.org/demo

## Technologies Used

| Technology | Version | Purpose |
|------------|---------|---------|
| Angular | 21.0+ | Frontend framework |
| TypeScript | 5.7+ | Type-safe development |
| RxJS | Latest | Reactive programming |
| marked | Latest | Markdown parsing |
| marked-highlight | Latest | Code block highlighting |
| highlight.js | Latest | Syntax highlighting |
| SCSS | - | Styling |

## Project Scripts

```bash
# Development server
npm start

# Production build
npm run build

# Run tests
npm test

# Lint code
ng lint
```

## Integration with Your Python Backend

### Your Current Backend Stack

Based on your `main.py`:
- **LLM**: Claude 3.5 Sonnet (Anthropic)
- **Embeddings**: OpenAI text-embedding-3-small
- **Vector DB**: Chroma with persistent storage
- **MCP Servers**: Math (stdio), Weather (HTTP)
- **RAG**: Dynamic prompt middleware with similarity search

### Recommended Backend Setup

Create a FastAPI wrapper for your LangChain agent:

```python
# backend/api.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse

app = FastAPI()

# Enable CORS for Angular dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/chat/stream")
async def chat_stream(request: ChatRequest):
    async def event_generator():
        async for step in agent.astream({"messages": request.messages}):
            # Format for UI consumption
            if step.get("rag_context"):
                yield {"event": "rag_context", "data": step["rag_context"]}
            if step.get("tool_calls"):
                yield {"event": "tool_call", "data": step["tool_calls"]}
            if step.get("content"):
                yield {"event": "content", "data": step["content"]}

    return EventSourceResponse(event_generator())
```

Run both servers:
```bash
# Terminal 1: Angular UI
cd ai-assistant-ui && npm start

# Terminal 2: Python Backend
uvicorn backend.api:app --port 8080
```

## Features Showcase

### Message Types
- ✅ User messages with gradient avatars
- ✅ Assistant messages with markdown rendering
- ✅ System messages (if needed)
- ✅ Tool execution messages

### Interactive Elements
- ✅ Expandable RAG context cards
- ✅ Tool call details with arguments and results
- ✅ Code blocks with syntax highlighting
- ✅ Clickable conversation history
- ✅ Delete conversations with confirmation

### UX Enhancements
- ✅ Auto-scroll to latest message
- ✅ Typing indicators during streaming
- ✅ Loading states and error handling
- ✅ Keyboard shortcuts (Enter/Shift+Enter)
- ✅ Empty state with example queries

## Browser Support

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+

## Contributing

This UI is built with Angular best practices:
- Standalone components (no NgModules)
- Signal-based state management
- OnPush change detection
- Type-safe with strict TypeScript
- Accessible (WCAG AA compliant)

## License

MIT

## Support

For issues or questions about the UI, check the component documentation in the source files. Each component includes detailed JSDoc comments.

For LangChain backend integration, refer to your existing `main.py` implementation.

---

**Built with** ❤️ **using Angular and LangChain**
