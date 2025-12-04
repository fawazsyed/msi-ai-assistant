import { Component, input, output, ChangeDetectionStrategy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Conversation } from '../../models/message.model';

/**
 * Sidebar component for conversation history and navigation
 */
@Component({
  selector: 'app-sidebar',
  imports: [CommonModule],
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <div class="sidebar">
      <div class="sidebar-header">
        <h1 class="app-title">
          <span class="title-icon">🤖</span>
          MSI Assistant
        </h1>
        <button class="new-chat-button" (click)="newConversation.emit()">
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
            <path d="M8 1V15M1 8H15" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
          </svg>
          New Chat
        </button>
      </div>

      <div class="conversations-section">
        <h3 class="section-title">Conversations</h3>

        @if (conversations().length === 0) {
          <div class="empty-conversations">
            <p>No conversations yet</p>
            <p class="empty-hint">Start a new chat to begin</p>
          </div>
        } @else {
          <div class="conversations-list">
            @for (conversation of conversations(); track conversation.id) {
              <div
                class="conversation-item"
                [class.active]="currentConversationId() === conversation.id"
                (click)="conversationSelected.emit(conversation.id)"
              >
                <div class="conversation-content">
                  <div class="conversation-title">{{ conversation.title }}</div>
                  <div class="conversation-meta">
                    <span class="message-count">{{ conversation.messages.length }} messages</span>
                    <span class="conversation-time">{{ formatDate(conversation.updatedAt) }}</span>
                  </div>
                </div>

                <button
                  class="delete-button"
                  (click)="onDeleteConversation($event, conversation.id)"
                  title="Delete conversation"
                >
                  <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
                    <path d="M1 1L13 13M1 13L13 1" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                  </svg>
                </button>
              </div>
            }
          </div>
        }
      </div>

      <div class="sidebar-footer">
        <div class="info-section">
          <h4>Features</h4>
          <ul class="feature-list">
            <li>📚 RAG with Vector Search</li>
            <li>🔧 MCP Tool Integration</li>
            <li>💬 Streaming Responses</li>
            <li>🎨 Markdown & Code Highlighting</li>
          </ul>
        </div>

        <div class="powered-by">
          <span>Powered by</span>
          <strong>LangChain</strong>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .sidebar {
      width: 280px;
      background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
      color: white;
      display: flex;
      flex-direction: column;
      height: 100%;
      overflow: hidden;
    }

    .sidebar-header {
      padding: 1.5rem;
      border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    }

    .app-title {
      margin: 0 0 1rem 0;
      font-size: 1.5rem;
      font-weight: 700;
      display: flex;
      align-items: center;
      gap: 0.5rem;
    }

    .title-icon {
      font-size: 1.75rem;
    }

    .new-chat-button {
      width: 100%;
      padding: 0.75rem;
      background-color: rgba(255, 255, 255, 0.2);
      border: 1px solid rgba(255, 255, 255, 0.3);
      border-radius: 8px;
      color: white;
      font-weight: 600;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 0.5rem;
      transition: all 0.2s;
      font-size: 0.9rem;
    }

    .new-chat-button:hover {
      background-color: rgba(255, 255, 255, 0.3);
      transform: translateY(-1px);
    }

    .conversations-section {
      flex: 1;
      overflow-y: auto;
      padding: 1rem;
    }

    .section-title {
      margin: 0 0 1rem 0;
      font-size: 0.8rem;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      opacity: 0.8;
      font-weight: 600;
    }

    .empty-conversations {
      text-align: center;
      padding: 2rem 1rem;
      opacity: 0.7;
    }

    .empty-conversations p {
      margin: 0;
      font-size: 0.9rem;
    }

    .empty-hint {
      font-size: 0.8rem;
      opacity: 0.7;
      margin-top: 0.5rem;
    }

    .conversations-list {
      display: flex;
      flex-direction: column;
      gap: 0.5rem;
    }

    .conversation-item {
      padding: 0.75rem;
      background-color: rgba(255, 255, 255, 0.1);
      border-radius: 8px;
      cursor: pointer;
      transition: all 0.2s;
      display: flex;
      align-items: center;
      gap: 0.5rem;
      position: relative;
    }

    .conversation-item:hover {
      background-color: rgba(255, 255, 255, 0.2);
      transform: translateX(2px);
    }

    .conversation-item.active {
      background-color: rgba(255, 255, 255, 0.25);
      border-left: 3px solid white;
    }

    .conversation-content {
      flex: 1;
      min-width: 0;
    }

    .conversation-title {
      font-weight: 500;
      font-size: 0.9rem;
      margin-bottom: 0.25rem;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }

    .conversation-meta {
      display: flex;
      justify-content: space-between;
      font-size: 0.75rem;
      opacity: 0.8;
    }

    .delete-button {
      width: 24px;
      height: 24px;
      border: none;
      background: rgba(255, 255, 255, 0.2);
      border-radius: 4px;
      color: white;
      cursor: pointer;
      display: none;
      align-items: center;
      justify-content: center;
      transition: all 0.2s;
      flex-shrink: 0;
    }

    .conversation-item:hover .delete-button {
      display: flex;
    }

    .delete-button:hover {
      background: rgba(255, 0, 0, 0.5);
    }

    .sidebar-footer {
      padding: 1rem 1.5rem;
      border-top: 1px solid rgba(255, 255, 255, 0.1);
    }

    .info-section {
      margin-bottom: 1rem;
    }

    .info-section h4 {
      margin: 0 0 0.5rem 0;
      font-size: 0.8rem;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      opacity: 0.8;
    }

    .feature-list {
      list-style: none;
      padding: 0;
      margin: 0;
    }

    .feature-list li {
      font-size: 0.8rem;
      padding: 0.25rem 0;
      opacity: 0.9;
    }

    .powered-by {
      text-align: center;
      font-size: 0.75rem;
      opacity: 0.7;
      padding-top: 1rem;
      border-top: 1px solid rgba(255, 255, 255, 0.1);
    }

    .powered-by strong {
      display: block;
      font-size: 0.9rem;
      margin-top: 0.25rem;
      opacity: 1;
    }

    /* Scrollbar styling */
    .conversations-section::-webkit-scrollbar {
      width: 6px;
    }

    .conversations-section::-webkit-scrollbar-track {
      background: rgba(255, 255, 255, 0.1);
    }

    .conversations-section::-webkit-scrollbar-thumb {
      background: rgba(255, 255, 255, 0.3);
      border-radius: 3px;
    }

    .conversations-section::-webkit-scrollbar-thumb:hover {
      background: rgba(255, 255, 255, 0.4);
    }
  `]
})
export class SidebarComponent {
  conversations = input.required<Conversation[]>();
  currentConversationId = input<string | null>(null);

  newConversation = output<void>();
  conversationSelected = output<string>();
  conversationDeleted = output<string>();

  formatDate(date: Date): string {
    const now = new Date();
    const messageDate = new Date(date);
    const diff = now.getTime() - messageDate.getTime();
    const days = Math.floor(diff / (1000 * 60 * 60 * 24));

    if (days === 0) {
      return 'Today';
    } else if (days === 1) {
      return 'Yesterday';
    } else if (days < 7) {
      return `${days}d ago`;
    } else {
      return messageDate.toLocaleDateString();
    }
  }

  onDeleteConversation(event: Event, id: string): void {
    event.stopPropagation();
    this.conversationDeleted.emit(id);
  }
}
