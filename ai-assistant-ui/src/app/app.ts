import { Component, ChangeDetectionStrategy } from '@angular/core';
import { ChatContainerComponent } from './components/chat-container/chat-container.component';

@Component({
  selector: 'app-root',
  imports: [ChatContainerComponent],
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `<app-chat-container />`,
  styles: [`
    :host {
      display: block;
      width: 100%;
      height: 100vh;
    }
  `]
})
export class App {}
