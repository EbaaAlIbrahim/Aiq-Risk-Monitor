# AIQ Pipeline Risk Monitor & Predictive Flare Controller (v1.0)
### **An Enterprise Industrial IoT (IIoT) Decision Support System**

##  Project Overview
AIQ Risk Monitor is an advanced, real-time industrial software framework engineered to monitor refinery pipeline telemetry, classify asset degradation footprints, and mitigate fluid anomalies. Inspired by high-performance automation software created by **AIQ** (the joint venture between ADNOC and G42), this application transitions asset safety away from traditional, rigid legacy threshold alarms toward an intelligent, multi-variable AI decision-making network.

Operating in a **Continuous Prediction Mode**, the system continuously streams sensor data without halting plant functionality. It cross-analyzes complex fluid mechanics to provide automated, step-by-step mitigation routines for mechanical faults, simulating physical responses like flare stack venting, scraper pigging, segment isolation, and high-pressure nitrogen line purging.

---

## System Architecture & Tech Stack

```text
  [11-Dimensional Sensors] ──► [Python Backend] ──► [XGBoost ML Classifier]
             ▲                                               │
             │ (WebSocket Command Room Overrides)            ▼ (In-Memory JSON Payload)
     [Angular Frontend] ◄───────────────────────────── [Redis RAM Cache]
```

*   **Machine Learning Layer:** XGBoost Classifier (Gradient Boosted Tree Ensemble Framework) optimized for rule-based boundary matching.
*   **Asynchronous Backend Engine:** Python 3.10+ powered by `asyncio` for non-blocking time-series hardware synthesis and `websockets` for bidirectional data streaming.
*   **Data Caching Layer:** In-memory RAM caching via Redis (`fakeredis` library implementation) guaranteeing sub-millisecond telemetry availability.
*   **Engineering Dashboard Frontend:** Angular (Standalone modular components, RxJS state observable stream subscriptions, and native programmatic HTML SVG time-series graphics).

---

## Machine Learning Engine & Data Synthesis
The machine learning pipeline (`model_scada_ai.py`) utilizes synthetic data modeling to simulate **400,000 dense rows** of pipeline operational data. It holds a multi-tier structure split cleanly into **60% Training, 20% Validation (Test-Dev), and 20% Final Unseen Test** arrays to protect against data leakage.

The model is trained on an **11-dimensional feature matrix**:
1. `pressure_psi` | 2. `flow_rate_bph` | 3. `temperature_f` | 4. `valve_raw` | 5. `pump_state` | 6. `pump_speed_rpm` | 7. `compressor_state` | 8. `energy_kw` | 9. `acoustic_khz` | 10. `vibration_g` | 11. `alarm_triggered`.

### **Mathematical Modeling Foundation**
XGBoost constructs an ensemble of sequential decision trees by minimizing a regularized loss objective at each iteration step $t$:
$$\mathcal{L}^{(t)} = \sum_{i=1}^{n} l\left(y_i, \hat{y}_i^{(t-1)} + f_t(x_i)\right) + \gamma T + \frac{1}{2}\lambda \sum_{j=1}^{T} w_j^2$$
To classify metrics quickly, it calculates an approximation score using Taylor Expansion derivatives—Gradients ($g_i$) and Hessians ($h_i$)—to optimize node splits based on maximum structural Gain:
$$\text{Gain} = \frac{1}{2} \left[ \frac{\left(\sum_{i \in I_L} g_i\right)^2}{\sum_{i \in I_L} h_i + \lambda} + \frac{\left(\sum_{i \in I_R} g_i\right)^2}{\sum_{i \in I_R} h_i + \lambda} - \frac{\left(\sum_{i \in I} g_i\right)^2}{\sum_{i \in I} h_i + \lambda} \right] - \gamma$$
Through this structure, the model handles class imbalances and targets complex, interlocking industrial risks with **~91%+ Balanced Accuracy** and exceptionally high recall.

---

## Telemetry Diagnoses & Real-World Solutions

The full-stack application models, identifies, and automatically resolves two critical refinery threat scenarios:

### **1. Internal Pipeline Blockages (`BLOCKAGE_CRITICAL`)**
*   **The Physics Footprint:** Occurs when wax crystals or hydrates plug a line, causing pressures to spike (**95.5–98.9 PSI**), flow velocity to crash (**1.2–1.7 GPM**), and joint vibration stresses to surge (**2.2–2.9 g**).
*   **The Automated Response Sequence:** The app sets operational states to `BLOCKAGE_MITIGATION` and runs an internal automated timer loop:
    *   *Step 1:* Activates emergency bypass loops to reroute crude oil throughput.
    *   *Step 2:* Simulates opening pressure relief valves, venting excess trapped volume safely to the refinery **Flare Stack**.
    *   *Step 3:* Simulates injecting a mechanical scraper pig tool into the line to scrub internal scaling.
    *   *Step 4:* Fires thermal induction external heating jackets to melt the plug and safely reset back to `NORMAL`.

### **2. Structural Fatigue & Fluid Leaks (`FATIGUE_CRITICAL`)**
*   **The Physics Footprint:** Occurs due to wall thinning from internal sediment erosion or mechanical tearing, causing internal pressure to sag (**74.0–76.5 PSI**), downstream volume output to drop, and high-frequency acoustic sensor hamping to jump (**45.0–55.0 kHz**).
*   **The Automated Response Sequence:** The system launches `LEAK_MITIGATION` to protect the environment:
    *   *Step 1:* Instantly closes virtual Emergency Shutdown (ESD) valves on both ends, dropping fluid parameters to `0`.
    *   *Step 2:* Dispatches simulated vacuum extraction utility trucks to drain toxic pooling crude out of the pipe section.
    *   *Step 3:* Pumps high-pressure inert **Nitrogen Gas** through the line to displace flammable hydrocarbon fumes.
    *   *Step 4:* Simulates a hot-tap welding sleeve patch execution, safely opening valves to restore plant flow.

---

## Local Setup Installation

### **1. Clone and Configure the Backend Architecture**
Open a terminal inside your backend folder directory:
```bash
# Install required numerical data processing, socket networking, and machine learning modules
pip install xgboost scikit-learn pandas websockets fakeredis numpy

# Step A: Run the generator script to create the 400k matrix dataset and train the model weights
python model_scada_ai.py

# Step B: Launch the asynchronous live server and sensor hardware simulator
python app.py
```
*The server will successfully initialize and open an active streaming loop channel at `ws://localhost:8765`.*

### **2. Boot Up the Angular Dashboard**
Open a secondary terminal window and execute:
```bash
cd frontend
npm install
ng serve
```
*Open your browser and navigate to `http://localhost:4200` to interact with the system command room deck override dashboard panels live.*
