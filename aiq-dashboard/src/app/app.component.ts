import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { TelemetryService } from './telemetry.service';
import { Subscription } from 'rxjs';

interface IncidentLog {
  timestamp: string;
  assetId: string;
  issueType: string;
  pressure: number;
  flow: number;
}

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent implements OnInit, OnDestroy {
  title = 'aiq-dashboard';
  currentData: any = null;
  incidentHistory: IncidentLog[] = [];
  pressureHistory: number[] = [];
  svgPathCoordinates: string = '';
  
  private streamSubscription!: Subscription;

  constructor(private telemetryService: TelemetryService) {}

  ngOnInit(): void {
    this.streamSubscription = this.telemetryService.getLiveStream().subscribe({
      next: (payload) => {
        this.processIncidentLogging(payload);
        this.currentData = payload;
        this.updateChartTimeline(payload.metrics.pressure_psi);
      }
    });
  }

  private processIncidentLogging(data: any): void {
    const currentStatus = data.status;

    // UPDATED CONDITIONAL: Handle the specific analytical alerts emitted by the ML model
    if (currentStatus === 'BLOCKAGE_CRITICAL' || currentStatus === 'FATIGUE_CRITICAL') {
      if (!this.currentData || this.currentData.status !== currentStatus) {
        const logEntry: IncidentLog = {
          timestamp: new Date().toLocaleTimeString(),
          assetId: data.pipeline_id,
          issueType: currentStatus,
          pressure: data.metrics.pressure_psi,
          flow: data.metrics.flow_rate_bph
        };
        this.incidentHistory.unshift(logEntry);
      }
    }
  }

  private updateChartTimeline(latestPressure: number): void {
    this.pressureHistory.push(latestPressure);

    if (this.pressureHistory.length > 20) {
      this.pressureHistory.shift();
    }

    const widthBetweenPoints = 500 / 19; 
    let points = this.pressureHistory.map((val, index) => {
      const x = index * widthBetweenPoints;
      // Adjusted bounds to clearly present the baseline values
      const minPress = 0;
      const maxPress = 120;
      const percentage = (val - minPress) / (maxPress - minPress);
      const y = 120 - (percentage * 100); 
      return `${x},${Math.max(10, Math.min(110, y))}`;
    });

    this.svgPathCoordinates = points.join(' ');
  }

  triggerSystemMode(modeName: string): void {
    this.telemetryService.sendCommand({ set_mode: modeName });
  }

  toggleEmergencyValve(status: string): void {
    this.telemetryService.sendCommand({ set_valve: status });
  }

  clearAuditHistory(): void {
    this.incidentHistory = [];
  }

  ngOnDestroy(): void {
    if (this.streamSubscription) {
      this.streamSubscription.unsubscribe();
    }
  }
}
