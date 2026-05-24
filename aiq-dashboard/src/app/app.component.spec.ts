import { TestBed } from '@angular/core/testing';
import { AppComponent } from './app.component';
import { TelemetryService } from './telemetry.service';
import { of } from 'rxjs';

declare var describe: any;
declare var beforeEach: any;
declare var it: any;
declare var expect: any;

describe('AppComponent', () => {
  const mockTelemetryService = {
    getLiveStream: () => of({
      pipeline_id: 'PL-042-TEST',
      status: 'NORMAL',
      system_mode: 'AUTO',
      valve_status: 'OPEN',
      metrics: { pressure_psi: 8.5, temperature_f: 22.4, flow_rate_bph: 99.1 }
    }),
    sendCommand: () => {}
  };

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [AppComponent],
      // Inject our safe fake service data provider into the isolated testing window environment
      providers: [
        { provide: TelemetryService, useValue: mockTelemetryService }
      ]
    }).compileComponents();
  });

  it('should create the app', () => {
    const fixture = TestBed.createComponent(AppComponent);
    const app = fixture.componentInstance;
    expect(app).toBeTruthy();
  });

  it(`should have the 'aiq-dashboard' title`, () => {
    const fixture = TestBed.createComponent(AppComponent);
    const app = fixture.componentInstance;
    expect(app.title).toEqual('aiq-dashboard');
  });

  it('should render the refinery dashboard main header', () => {
    const fixture = TestBed.createComponent(AppComponent);
    fixture.detectChanges(); 
    const compiled = fixture.nativeElement as HTMLElement;
    
    expect(compiled.querySelector('h2')?.textContent).toContain('AIQ Risk Monitor v1.0');
  });
});
