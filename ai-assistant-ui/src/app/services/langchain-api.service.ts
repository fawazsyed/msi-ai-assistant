import { Injectable, signal } from '@angular/core';
import { Message, Conversation } from '../models/message.model';

/**
 * Service for communicating with LangChain backend
 * Supports streaming responses via Server-Sent Events (SSE)
 */
@Injectable({
  providedIn: 'root'
})
export class LangchainApiService {
  private readonly apiUrl = 'http://localhost:8080/api';

  // State signals
  currentConversation = signal<Conversation | null>(null);
  conversations = signal<Conversation[]>([]);
  isLoading = signal(false);
  error = signal<string | null>(null);

  /**
   * Send a message and stream the response from the backend
   */
  async sendMessage(content: string, conversationId?: string): Promise<void> {
    this.isLoading.set(true);
    this.error.set(null);

    try {
      // Create or get conversation
      let conversation = conversationId
        ? this.conversations().find(c => c.id === conversationId)
        : this.currentConversation();

      if (!conversation) {
        conversation = this.createNewConversation();
      }

      // Add user message
      const userMessage: Message = {
        id: this.generateId(),
        role: 'user',
        content,
        timestamp: new Date()
      };

      conversation.messages.push(userMessage);
      this.updateConversation(conversation);

      // Create assistant message placeholder for streaming
      const assistantMessage: Message = {
        id: this.generateId(),
        role: 'assistant',
        content: '',
        timestamp: new Date(),
        isStreaming: true
      };

      conversation.messages.push(assistantMessage);
      this.updateConversation(conversation);

      // Stream response from backend
      await this.streamResponse(conversation, assistantMessage);

      assistantMessage.isStreaming = false;
      this.updateConversation(conversation);

    } catch (err) {
      this.error.set(err instanceof Error ? err.message : 'Unknown error');
      console.error('Error sending message:', err);
    } finally {
      this.isLoading.set(false);
    }
  }

  /**
   * Stream response from LangChain backend using Server-Sent Events
   */
  private async streamResponse(conversation: Conversation, message: Message): Promise<void> {
    try {
      // Prepare messages for the API
      const messages = conversation.messages
        .filter(m => !m.isStreaming) // Exclude the placeholder
        .map(m => ({ role: m.role, content: m.content }));

      // Make SSE request to streaming endpoint
      const response = await fetch(`${this.apiUrl}/chat/stream`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ messages })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      // Process the stream
      const reader = response.body?.getReader();
      const decoder = new TextDecoder();

      if (!reader) {
        throw new Error('No response body');
      }

      let buffer = '';
      let isDone = false;

      while (true && !isDone) {
        const { done, value } = await reader.read();

        if (done) {
          break;
        }

        // Decode chunk and add to buffer
        buffer += decoder.decode(value, { stream: true });

        // Process complete SSE messages (separated by \n\n)
        const lines = buffer.split('\n\n');
        buffer = lines.pop() || ''; // Keep incomplete message in buffer

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.substring(6); // Remove 'data: ' prefix

            try {
              const chunk = JSON.parse(data);
              console.log('[LangChain] Received chunk:', chunk);

              // Handle different chunk types
              if (chunk.type === 'rag_context' && chunk.ragContext) {
                console.log('[LangChain] RAG context received');
                message.ragContext = chunk.ragContext;
              } else if (chunk.type === 'tool_call' && chunk.toolCall) {
                console.log('[LangChain] Tool call:', chunk.toolCall.name);
                if (!message.toolCalls) {
                  message.toolCalls = [];
                }
                message.toolCalls.push(chunk.toolCall);
              } else if (chunk.type === 'content') {
                console.log('[LangChain] Content update, length:', chunk.content?.length || 0);
                // Create a new message object to trigger change detection
                const updatedMessage = { ...message, content: chunk.content || '' };
                const messageIndex = conversation.messages.findIndex(m => m.id === message.id);
                if (messageIndex !== -1) {
                  conversation.messages[messageIndex] = updatedMessage;
                  // Update the reference for subsequent chunks
                  Object.assign(message, updatedMessage);
                }
              } else if (chunk.type === 'error') {
                console.error('[LangChain] Error:', chunk.error);
                this.error.set(chunk.error || 'Unknown error');
              } else if (chunk.type === 'done') {
                console.log('[LangChain] Stream completed');
                // Stream completed - set flag to exit outer while loop
                isDone = true;
                break;
              }

              // Update UI after each chunk
              this.updateConversation(conversation);

            } catch (parseError) {
              console.error('Error parsing SSE data:', parseError, data);
            }
          }
        }
      }

    } catch (err) {
      console.error('Streaming error:', err);
      message.content = 'Sorry, I encountered an error while processing your request.';
      this.error.set(err instanceof Error ? err.message : 'Streaming failed');
      this.updateConversation(conversation);
    }
  }

  /**
   * Create a new conversation
   */
  createNewConversation(): Conversation {
    const conversation: Conversation = {
      id: this.generateId(),
      title: 'New Conversation',
      messages: [],
      createdAt: new Date(),
      updatedAt: new Date()
    };

    const conversations = [...this.conversations(), conversation];
    this.conversations.set(conversations);
    this.currentConversation.set(conversation);

    return conversation;
  }

  /**
   * Load a conversation by ID
   */
  loadConversation(id: string): void {
    const conversation = this.conversations().find(c => c.id === id);
    if (conversation) {
      this.currentConversation.set(conversation);
    }
  }

  /**
   * Delete a conversation
   */
  deleteConversation(id: string): void {
    const conversations = this.conversations().filter(c => c.id !== id);
    this.conversations.set(conversations);

    if (this.currentConversation()?.id === id) {
      this.currentConversation.set(null);
    }
  }

  /**
   * Update conversation in the list
   */
  private updateConversation(conversation: Conversation): void {
    conversation.updatedAt = new Date();

    // Update title based on first user message
    if (conversation.messages.length > 0 && conversation.title === 'New Conversation') {
      const firstUserMsg = conversation.messages.find(m => m.role === 'user');
      if (firstUserMsg) {
        conversation.title = firstUserMsg.content.substring(0, 50) +
          (firstUserMsg.content.length > 50 ? '...' : '');
      }
    }

    const conversations = this.conversations().map(c =>
      c.id === conversation.id ? conversation : c
    );
    this.conversations.set(conversations);
    this.currentConversation.set(conversation);
  }

  /**
   * Generate unique ID
   */
  private generateId(): string {
    return `${Date.now()}-${Math.random().toString(36).substring(2, 9)}`;
  }
}
