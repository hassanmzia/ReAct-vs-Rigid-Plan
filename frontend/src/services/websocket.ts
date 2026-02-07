const WS_URL = process.env.REACT_APP_WS_URL || 'ws://172.168.1.95:8042';

export class AgentWebSocket {
  private ws: WebSocket | null = null;
  private sessionId: string;
  private onMessage: (data: any) => void;
  private onError?: (error: Event) => void;
  private reconnectAttempts = 0;
  private maxReconnects = 3;

  constructor(
    sessionId: string,
    onMessage: (data: any) => void,
    onError?: (error: Event) => void
  ) {
    this.sessionId = sessionId;
    this.onMessage = onMessage;
    this.onError = onError;
  }

  connect(): void {
    const url = `${WS_URL}/ws/agent/${this.sessionId}/`;
    this.ws = new WebSocket(url);

    this.ws.onopen = () => {
      this.reconnectAttempts = 0;
    };

    this.ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        this.onMessage(data);
      } catch (e) {
        console.error('WebSocket message parse error:', e);
      }
    };

    this.ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      this.onError?.(error);
    };

    this.ws.onclose = () => {
      if (this.reconnectAttempts < this.maxReconnects) {
        this.reconnectAttempts++;
        setTimeout(() => this.connect(), 2000 * this.reconnectAttempts);
      }
    };
  }

  disconnect(): void {
    this.maxReconnects = 0;
    this.ws?.close();
    this.ws = null;
  }

  send(data: any): void {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data));
    }
  }
}
