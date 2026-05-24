import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from xgboost import XGBClassifier
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(BASE_DIR, "pipeline_telemetry_400k_realistic.csv")
model_path = os.path.join(BASE_DIR, "pipeline_risk_model.json")

if not os.path.exists(csv_path):
    print(f" Generating 400,000 row high-density telemetry matrix featuring advanced acoustics/vibrations...")
    np.random.seed(42)
    rows = 400000
    
    # 1. Establish realistic baseline matrices
    pressure = np.random.uniform(73.0, 78.0, rows)
    flow_rate = np.random.uniform(4.3, 4.7, rows)
    temperature = np.random.uniform(31.5, 34.5, rows)
    valve_raw = np.ones(rows, dtype=int)
    pump_state = np.ones(rows, dtype=int)
    pump_speed = np.random.uniform(1320.0, 1390.0, rows)
    compressor_state = np.random.choice([0, 1], rows)
    energy = np.random.uniform(33.0, 45.0, rows)
    acoustic = np.random.uniform(10.0, 20.0, rows)
    vibration = np.random.uniform(0.1, 0.4, rows)
    target = np.zeros(rows, dtype=int)
    
    # 2. Inject Explicit Blockage Anomalies (10% of data)
    blockage_indices = np.random.choice(rows, size=int(rows * 0.10), replace=False)
    pressure[blockage_indices] = np.random.uniform(94.5, 98.9, size=len(blockage_indices))
    flow_rate[blockage_indices] = np.random.uniform(1.2, 1.7, size=len(blockage_indices))
    vibration[blockage_indices] = np.random.uniform(2.2, 2.9, size=len(blockage_indices))
    target[blockage_indices] = 1
    
    # 3. Inject Explicit Structural Leak Anomalies (10% of remaining data)
    remaining_indices = np.setdiff1d(np.arange(rows), blockage_indices)
    leak_indices = np.random.choice(remaining_indices, size=int(rows * 0.10), replace=False)
    pressure[leak_indices] = np.random.uniform(74.0, 76.5, size=len(leak_indices))
    flow_rate[leak_indices] = np.random.uniform(1.1, 1.4, size=len(leak_indices))
    acoustic[leak_indices] = np.random.uniform(45.0, 55.0, size=len(leak_indices))
    target[leak_indices] = 1

    data = {
        "pressure_psi": pressure, "flow_rate_bph": flow_rate, "temperature_f": temperature,
        "valve_raw": valve_raw, "pump_state": pump_state, "pump_speed_rpm": pump_speed,
        "compressor_state": compressor_state, "energy_kw": energy,
        "acoustic_khz": acoustic, "vibration_g": vibration,
        "alarm_triggered": np.where(pressure > 95.0, 1, 0), "target": target
    }
    
    df_gen = pd.DataFrame(data)
    df_gen["timestamp"] = np.arange(rows)
    df_gen.to_csv(csv_path, index=False)

print("Loading dataset...")
df = pd.read_csv(csv_path)

X = df.drop(columns=['timestamp', 'target'])
y = df['target']

X_temp, X_test, y_temp, y_test = train_test_split(X, y, test_size=0.05, random_state=42, stratify=y)
X_train, X_dev, y_train, y_dev = train_test_split(X_temp, y_temp, test_size=0.05263, random_state=42, stratify=y_temp)

num_negative = np.sum(y_train == 0)
num_positive = np.sum(y_train == 1)
optimized_scale = np.sqrt(num_negative / num_positive) * 0.85

model = XGBClassifier(
    n_estimators=250, max_depth=10, learning_rate=0.08,
    scale_pos_weight=optimized_scale, subsample=0.9, colsample_bytree=0.9,
    random_state=42, eval_metric='logloss', n_jobs=-1
)

print("\nTraining the high-accuracy AI model...")
model.fit(X_train, y_train)

y_pred_test = model.predict(X_test)
acc_test = accuracy_score(y_test, y_pred_test) * 100
print(f" Final Test Dataset Accuracy: {acc_test:.2f}%")
print(classification_report(y_test, y_pred_test))

model.save_model(model_path)
print("Model saved successfully as 'pipeline_risk_model.json'")
