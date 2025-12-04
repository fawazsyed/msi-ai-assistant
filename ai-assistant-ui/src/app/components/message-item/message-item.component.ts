import { Component, input, ChangeDetectionStrategy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Message } from '../../models/message.model';
import { MarkdownComponent } from '../markdown/markdown.component';
import { ToolCallsComponent } from '../tool-calls/tool-calls.component';
import { RagContextComponent } from '../rag-context/rag-context.component';

/**
 * Component for displaying a single chat message
 * Supports markdown, tool calls, and RAG context
 */
@Component({
  selector: 'app-message-item',
  imports: [CommonModule, MarkdownComponent, ToolCallsComponent, RagContextComponent],
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <div class="message-container" [class.user-message]="message().role === 'user'"
         [class.assistant-message]="message().role === 'assistant'">

      <div class="message-avatar">
        @if (message().role === 'user') {
          <div class="avatar user-avatar">U</div>
        } @else {
          <div class="avatar assistant-avatar">AI</div>
        }
      </div>

      <div class="message-content-wrapper">
        <div class="message-header">
          <span class="message-role">{{ message().role === 'user' ? 'You' : 'MSI Assistant' }}</span>
          <span class="message-time">{{ formatTime(message().timestamp) }}</span>
        </div>

        @if (message().ragContext) {
          <app-rag-context [ragContext]="message().ragContext!" />
        }

        @if (message().toolCalls && message().toolCalls!.length > 0) {
          <app-tool-calls [toolCalls]="message().toolCalls!" />
        }

        <div class="message-content">
          @if (message().role === 'assistant') {
            <app-markdown [content]="message().content" />
          } @else {
            <p>{{ message().content }}</p>
          }

          @if (message().isStreaming) {
            <span class="streaming-cursor"></span>
          }
        </div>
      </div>
    </div>
  `,
  styles: [`
    .message-container {
      display: flex;
      gap: 1rem;
      margin-bottom: 1.5rem;
      padding: 1rem;
      border-radius: 8px;
      transition: background-color 0.2s;
    }

    .message-container:hover {
      background-color: rgba(0, 0, 0, 0.02);
    }

    .user-message {
      background-color: rgba(0, 123, 255, 0.05);
    }

    .message-avatar {
      flex-shrink: 0;
    }

    .avatar {
      width: 40px;
      height: 40px;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: 600;
      color: white;
    }

    .user-avatar {
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }

    .assistant-avatar {
      background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    }

    .message-content-wrapper {
      flex: 1;
      min-width: 0;
    }

    .message-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 0.5rem;
    }

    .message-role {
      font-weight: 600;
      color: #333;
      font-size: 0.9rem;
    }

    .message-time {
      font-size: 0.75rem;
      color: #999;
    }

    .message-content {
      color: #333;
      line-height: 1.6;
      word-wrap: break-word;
      position: relative;
    }

    .message-content p {
      margin: 0;
    }

    .streaming-cursor {
      display: inline-block;
      width: 8px;
      height: 16px;
      background-color: #667eea;
      margin-left: 2px;
      animation: blink 1s infinite;
    }

    @keyframes blink {
      0%, 50% { opacity: 1; }
      51%, 100% { opacity: 0; }
    }
  `]
})
export class MessageItemComponent {
  message = input.required<Message>();

  formatTime(date: Date): string {
    return new Date(date).toLocaleTimeString('en-US', {
      hour: 'numeric',
      minute: '2-digit'
    });
  }
}
