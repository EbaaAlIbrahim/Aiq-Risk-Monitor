import asyncio
import json
import random
import time
import websockets
import fakeredis
import numpy as np
import pandas as pd  
import os  
from xgboost import XGBClassifier

redis_client = fakeredis.FakeRedis(decode_responses=True)
PIPELINE_ID = "PL-042-MAIN"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "pipeline_risk_model.json")

print(" Initializing production pipeline risk model...")
ai_model = XGBClassifier()
try:
    ai_model.load_model(MODEL_PATH)
    print("Weights loaded successfully into the execution layer.")
except Exception as e:
    print(f" Initialization failed. Ensure 'pipeline_risk_model.json' is placed inside: {BASE_DIR}")
    raise e

# AUTOMATED MITIGATION CONTROL STATE STRINGS
SYSTEM_MODE = "AUTO"  # Options: "AUTO", "FORCE_LEAK", "BLOCKAGE_MITIGATION", "LEAK_MITIGATION"
VALVE_STATUS = "OPEN" # Options: "OPEN", "CLOSED"
MITIGATION_STEP = "NONE" # which physical step is happening
SUB_TICK = 0

PRESSURE_QUEUE = []
FLOW_QUEUE = []

def ai_predict_risk(pressure, flow_rate, temperature, valve_raw, pump_state, pump_speed, compressor_state, energy, acoustic, vibration):
    global PRESSURE_QUEUE, FLOW_QUEUE
    if VALVE_STATUS == "CLOSED":
        return "SYSTEM_SHUTDOWN_SAFE"
        
    PRESSURE_QUEUE.append(pressure)
    FLOW_QUEUE.append(flow_rate)
    if len(PRESSURE_QUEUE) > 10:
        PRESSURE_QUEUE.pop(0)
        FLOW_QUEUE.pop(0)

    if len(PRESSURE_QUEUE) >= 3:
        flow_grad = np.gradient(FLOW_QUEUE)[-1]
        press_grad = np.gradient(PRESSURE_QUEUE)[-1]
        
        # Rule 1: Fast dropping flow paired with stable pressure indicates a leak
        if flow_grad < -1.5 and press_grad >= -0.2:
            return "FATIGUE_CRITICAL"
        
        # Rule 2: Sustained high pressure averages catch obstructions instantly
        if np.mean(PRESSURE_QUEUE) > 90.0:
            return "BLOCKAGE_CRITICAL"
        
    feature_dict = {
        "segment_id": [42],
        "pressure": [pressure],
        "flow_rate": [flow_rate],
        "temperature": [temperature],
        "valve_status": [valve_raw],
        "pump_state": [pump_state],
        "pump_speed": [pump_speed],
        "compressor_state": [compressor_state],
        "energy_consumption": [energy],
        "alarm_triggered": [1 if pressure > 95.0 else 0]
    }
    feature_df = pd.DataFrame(feature_dict)
    
    # GET LIVE AI PREDICTION FROM THE WEIGHT FILE
    prediction = int(ai_model.predict(feature_df))
    if prediction == 1:
        return "BLOCKAGE_CRITICAL" if pressure > 90.0 else "FATIGUE_CRITICAL"
    return "NORMAL"

async def pipeline_sensor_simulator():
    global SYSTEM_MODE, VALVE_STATUS, MITIGATION_STEP, SUB_TICK
    print(" Sensor Simulator running in Automated Reactive Mode...")
    tick = 0
    
    while True:
        tick += 1
        valve_raw = 1 if VALVE_STATUS == "OPEN" else 0
        pump_state = 1 if VALVE_STATUS == "OPEN" else 0
        pump_speed = round(random.uniform(1320.0, 1390.0), 2) if pump_state == 1 else 0.0
        compressor_state = random.choice([0, 1]) if pump_state == 1 else 0
        temperature = round(random.uniform(31.5, 34.5), 2)
        base_energy = 33.0 if pump_state == 1 else 11.0
        if compressor_state == 1: base_energy += random.uniform(4.0, 12.0)
        energy_consumption = round(base_energy + random.uniform(-1.5, 1.5), 2)

        # Base nominal signatures for sound waves and shaking parameters
        acoustic_khz = round(random.uniform(10.0, 20.0), 2) if VALVE_STATUS == "OPEN" else 0.0
        vibration_g = round(random.uniform(0.1, 0.4), 2) if VALVE_STATUS == "OPEN" else 0.0

        # BRANCH 1: RUNNING RECOVERIES FOR ACTIVE BLOCKAGES
        if SYSTEM_MODE == "BLOCKAGE_MITIGATION":
            SUB_TICK += 1
            if SUB_TICK <= 3:
                MITIGATION_STEP = "STEP 1: Activating Emergency Bypass Loops & Rerouting Crude Flow"
                pressure, flow_rate = round(random.uniform(88.0, 91.0), 2), round(random.uniform(2.5, 3.2), 2)
            elif SUB_TICK <= 6:
                MITIGATION_STEP = "STEP 2: Automated Pressure Venting to Refinery Flare Stacks"
                pressure, flow_rate = round(random.uniform(76.0, 80.0), 2), round(random.uniform(4.0, 4.3), 2)
            elif SUB_TICK <= 10:
                MITIGATION_STEP = "STEP 3: Injecting Mechanical Scraper Pig into Launcher"
                pressure, flow_rate = round(random.uniform(74.0, 77.0), 2), round(random.uniform(4.3, 4.5), 2)
            else:
                SYSTEM_MODE, MITIGATION_STEP, SUB_TICK = "AUTO", "NONE", 0
                continue

        # BRANCH 2: RUNNING RECOVERIES FOR CRITICAL FATIGUE/LEAKS
        elif SYSTEM_MODE == "LEAK_MITIGATION":
            SUB_TICK += 1
            if SUB_TICK <= 3:
                MITIGATION_STEP = "STEP 1: Slamming Emergency Shutdown (ESD) Segment Isolation Valves"
                VALVE_STATUS = "CLOSED"
                pressure, flow_rate, pump_speed, energy_consumption = round(random.uniform(20.0, 30.0), 2), 0.0, 0.0, 0.0
            elif SUB_TICK <= 6:
                MITIGATION_STEP = "STEP 2: Deploying Fluid Vacuum Extraction & Product Recovery Trucks"
                pressure, flow_rate, pump_speed, energy_consumption = 0.0, 0.0, 0.0, 0.0
            elif SUB_TICK <= 10:
                MITIGATION_STEP = "STEP 3: Commencing High-Pressure Inert Nitrogen Line Purge"
                pressure, flow_rate, pump_speed, energy_consumption = 5.0, 0.0, 0.0, 0.0
            else:
                VALVE_STATUS, SYSTEM_MODE, MITIGATION_STEP, SUB_TICK = "OPEN", "AUTO", "NONE", 0
                continue

        # BRANCH 3: NORMAL BASELINE & OVERRIDE DEVIATIONS
        else:
            if VALVE_STATUS == "CLOSED":
                pressure, flow_rate, energy_consumption, pump_speed = 0.0, 0.0, 0.0, 0.0
            elif SYSTEM_MODE == "FORCE_LEAK":
                pressure = round(random.uniform(74.0, 76.5), 2)   
                flow_rate = round(random.uniform(1.1, 1.4), 2) 
                acoustic_khz = round(random.uniform(45.0, 55.0), 2) 
            else:
                pressure = round(random.uniform(73.0, 78.0), 2)
                flow_rate = round(random.uniform(4.3, 4.7), 2)
                
                # Automated structural anomaly window (Ticks 26 through 35)
                if 25 < (tick % 60) <= 35:
                    pressure = round(random.uniform(95.5, 98.9), 2) 
                    flow_rate = round(random.uniform(1.2, 1.7), 2)
                    vibration_g = round(random.uniform(2.2, 2.9), 2) 

        # EXECUTE INFERENCE MATRIX
        ai_verdict = ai_predict_risk(
            pressure, flow_rate, temperature, valve_raw, pump_state, 
            pump_speed, compressor_state, energy_consumption, acoustic_khz, vibration_g
        )

        if SYSTEM_MODE == "AUTO":
            if ai_verdict == "BLOCKAGE_CRITICAL":
                SYSTEM_MODE = "BLOCKAGE_MITIGATION"
                SUB_TICK = 0
                print(" [AUTOMATION ENGINE]: Blockage detected. Starting automated 4-stage pigging sequence...")
            elif ai_verdict == "FATIGUE_CRITICAL":
                SYSTEM_MODE = "LEAK_MITIGATION"
                SUB_TICK = 0
                print(" [AUTOMATION ENGINE]: Leak detected via AI Engine. Starting automated patch sequence...")
        elif SYSTEM_MODE == "FORCE_LEAK":
            SYSTEM_MODE = "LEAK_MITIGATION"
            SUB_TICK = 0
            print(" [COMMAND INTERLOCK]: Manual Leak Forced by Operator. Slamming system down instantly!")

        telemetry_payload = {
            "pipeline_id": PIPELINE_ID, "timestamp": time.time(), "status": ai_verdict,
            "system_mode": SYSTEM_MODE, "valve_status": VALVE_STATUS, "mitigation_step": MITIGATION_STEP,
            "metrics": {
                "pressure_psi": pressure, "temperature_f": temperature, "flow_rate_bph": flow_rate,
                "pump_speed_rpm": pump_speed, "energy_kw": energy_consumption
            }
        }
        redis_client.set(f"telemetry:latest:{PIPELINE_ID}", json.dumps(telemetry_payload))
        await asyncio.sleep(1)

async def websocket_handler(websocket):
    async def send_updates():
        try:
            while True:
                latest_data_raw = redis_client.get(f"telemetry:latest:{PIPELINE_ID}")
                if latest_data_raw: await websocket.send(latest_data_raw)
                await asyncio.sleep(1)
        except websockets.exceptions.ConnectionClosed: pass

    async def receive_commands():
        global SYSTEM_MODE, VALVE_STATUS
        try:
            async for message in websocket:
                command_data = json.loads(message)
                if "set_mode" in command_data: SYSTEM_MODE = command_data["set_mode"]
                if "set_valve" in command_data: VALVE_STATUS = command_data["set_valve"]
        except websockets.exceptions.ConnectionClosed: pass

    await asyncio.gather(send_updates(), receive_commands())

async def main():
    asyncio.create_task(pipeline_sensor_simulator())
    print(" AIQ Server running on ws://localhost:8765")
    async_server = await websockets.serve(websocket_handler, "localhost", 8765)
    await async_server.wait_closed()

if __name__ == "__main__":
    try: asyncio.run(main())
    except KeyboardInterrupt: print("\n Server shut down.")
