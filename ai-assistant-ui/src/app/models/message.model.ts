/**
 * Message models for LangChain-based chat interface
 */

export type MessageRole = 'user' | 'assistant' | 'system' | 'tool';

export interface ToolCall {
  id: string;
  name: string;
  args: Record<string, unknown>;
  result?: unknown;
}

export interface RAGContext {
  documents: string[];
  similarity_scores?: number[];
}

export interface Message {
  id: string;
  role: MessageRole;
  content: string;
  timestamp: Date;
  toolCalls?: ToolCall[];
  ragContext?: RAGContext;
  isStreaming?: boolean;
}

export interface Conversation {
  id: string;
  title: string;
  messages: Message[];
  createdAt: Date;
  updatedAt: Date;
}

export interface ChatState {
  currentConversation: Conversation | null;
  conversations: Conversation[];
  isLoading: boolean;
  error: string | null;
}
