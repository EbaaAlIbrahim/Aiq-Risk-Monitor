import time
import json
import random
import fakeredis

redis_client = fakeredis.FakeRedis(decode_responses=True)

PIPELINE_ID = "PL-042-MAIN"

print("Pipeline Sensor Simulator Started (Using FakeRedis). Press Ctrl+C to stop.")

try:
    while True:
        # Generate baseline metrics with minor random fluctuations
        pressure = round(random.uniform(75.0, 85.0), 2)     # PSI
        temperature = round(random.uniform(140.0, 150.0), 2) # Fahrenheit
        flow_rate = round(random.uniform(980.0, 1020.0), 2)  # Barrels per hour
        
        if random.random() > 0.95:
            pressure = round(random.uniform(110.0, 130.0), 2)
            print(" Simulated abnormal pressure spike generated!")

        telemetry_payload = {
            "pipeline_id": PIPELINE_ID,
            "timestamp": time.time(),
            "metrics": {
                "pressure_psi": pressure,
                "temperature_f": temperature,
                "flow_rate_bph": flow_rate
            }
        }
        
        redis_client.set(f"telemetry:latest:{PIPELINE_ID}", json.dumps(telemetry_payload))
        
        print(f" Sent Telemetry -> Press: {pressure} PSI | Temp: {temperature}°F")
        time.sleep(1) 

except KeyboardInterrupt:
    print("\n Simulator stopped.")
