import { Component, input, signal, ChangeDetectionStrategy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RAGContext } from '../../models/message.model';

/**
 * Component for displaying RAG retrieved context
 * Shows documents retrieved from vector store
 */
@Component({
  selector: 'app-rag-context',
  imports: [CommonModule],
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <div class="rag-context-container">
      <button class="rag-header" (click)="toggleExpanded()">
        <span class="rag-icon">📚</span>
        <span class="rag-label">Retrieved Context ({{ ragContext().documents.length }} documents)</span>
        <span class="expand-icon">{{ isExpanded() ? '▼' : '▶' }}</span>
      </button>

      @if (isExpanded()) {
        <div class="rag-documents">
          @for (doc of ragContext().documents; track $index) {
            <div class="rag-document">
              <div class="doc-header">
                <span class="doc-number">Document {{ $index + 1 }}</span>
                @if (ragContext().similarity_scores && ragContext().similarity_scores![$index]) {
                  <span class="similarity-score">
                    Similarity: {{ (ragContext().similarity_scores![$index] * 100).toFixed(1) }}%
                  </span>
                }
              </div>
              <div class="doc-content">{{ doc }}</div>
            </div>
          }
        </div>
      }
    </div>
  `,
  styles: [`
    .rag-context-container {
      background-color: #fff3cd;
      border-left: 3px solid #ffc107;
      border-radius: 4px;
      margin: 0.75rem 0;
      overflow: hidden;
    }

    .rag-header {
      width: 100%;
      display: flex;
      align-items: center;
      gap: 0.5rem;
      padding: 0.75rem;
      background: none;
      border: none;
      cursor: pointer;
      font-weight: 600;
      color: #856404;
      font-size: 0.85rem;
      transition: background-color 0.2s;
    }

    .rag-header:hover {
      background-color: rgba(255, 193, 7, 0.1);
    }

    .rag-icon {
      font-size: 1rem;
    }

    .rag-label {
      flex: 1;
      text-align: left;
    }

    .expand-icon {
      font-size: 0.7rem;
      color: #666;
    }

    .rag-documents {
      padding: 0 0.75rem 0.75rem 0.75rem;
    }

    .rag-document {
      background-color: white;
      padding: 0.75rem;
      border-radius: 4px;
      margin-bottom: 0.5rem;
      font-size: 0.85rem;
    }

    .rag-document:last-child {
      margin-bottom: 0;
    }

    .doc-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 0.5rem;
      padding-bottom: 0.5rem;
      border-bottom: 1px solid #eee;
    }

    .doc-number {
      font-weight: 600;
      color: #333;
      font-size: 0.8rem;
    }

    .similarity-score {
      font-size: 0.75rem;
      color: #666;
      background-color: #f4f4f4;
      padding: 0.2rem 0.5rem;
      border-radius: 3px;
    }

    .doc-content {
      color: #555;
      line-height: 1.5;
      white-space: pre-wrap;
      word-wrap: break-word;
    }
  `]
})
export class RagContextComponent {
  ragContext = input.required<RAGContext>();
  isExpanded = signal(false);

  toggleExpanded(): void {
    this.isExpanded.update(value => !value);
  }
}
