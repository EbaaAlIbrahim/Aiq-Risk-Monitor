import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, interval } from 'rxjs';
import { switchMap, shareReplay } from 'rxjs/operators';

@Injectable({
  providedIn: 'root'
})
export class TelemetryService {
  // Use a relative path so it automatically works on local and Vercel production
  private baseUrl = '/api'; 

  constructor(private http: HttpClient) {}

  /**
   * Replaces your old WebSocket listener stream.
   * Emits new telemetry statistics automatically every 1 second.
   */
  getTelemetryStream(): Observable<any> {
    return interval(1000).pipe(
      switchMap(() => this.http.get(`${this.baseUrl}/telemetry`)),
      shareReplay(1) // Share the subscription across multiple dashboard charts
    );
  }

  /**
   * Replaces your WebSocket send data logic for control triggers
   */
  setSystemMode(mode: string): Observable<any> {
    return this.http.post(`${this.baseUrl}/command`, { set_mode: mode });
  }

  setValveStatus(status: 'OPEN' | 'CLOSED'): Observable<any> {
    return this.http.post(`${this.baseUrl}/command`, { set_valve: status });
  }
}
