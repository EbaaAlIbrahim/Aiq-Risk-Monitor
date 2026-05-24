import { Injectable } from '@angular/core';
import { Observable, Subject } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class TelemetryService {
  private socket!: WebSocket;
  private telemetrySubject = new Subject<any>();

  constructor() {
    this.connect();
  }

  private connect(): void {
    this.socket = new WebSocket('ws://localhost:8765');

    this.socket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      this.telemetrySubject.next(data);
    };

    this.socket.onclose = () => {
      setTimeout(() => this.connect(), 3000);
    };
  }

  getLiveStream(): Observable<any> {
    return this.telemetrySubject.asObservable();
  }

  // NEW METHOD: Sends user override actions back to Python
  sendCommand(payload: any): void {
    if (this.socket && this.socket.readyState === WebSocket.OPEN) {
      this.socket.send(JSON.stringify(payload));
    }
  }
}
