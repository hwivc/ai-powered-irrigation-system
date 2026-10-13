# AI- Powered Smart Irrigation System Using Environmental Sensor Data

An AI + IoT prototype that predicts irrigation need from three sensor readings and turns that prediction into a
**proposed** pump decision through a separate, configurable control layer.
Internship project (PlastiBytes, Cameroon, 2026). **This is a prototype, not a field-validated irrigation product.**

---

## 1. What the system does

```
Soil moisture + Temperature + Humidity  (Arduino sensors -> CSV)
        |
        v
Validation  ->  AI model (Decision Tree)  ->  Low / Medium / High
        |
        v
Irrigation control layer  (area -> depth -> volume -> flow rate -> runtime, safety rules)
        |
        v
Proposed pump ON/OFF + runtime  ->  stop conditions  ->  Pump OFF
```

| Layer | Question it answers | Method |
|---|---|---|
| **AI inference** | *Does this area need irrigation?* | Class-balanced Decision Tree (fixed, not changed by farm settings) |
| **Control layer** | *How much water, for how long, and when to stop?* | Equations + safety rules (configurable, no machine learning) |

The AI model does **not** calculate water volume or runtime. The control layer does.

---

## 2. Files

| File | Purpose |
|---|---|
| `smart_irrigation_model.ipynb` | The complete project notebook (Steps 1-38, appendix with the quick test function) |
| `model_artifacts/irrigation_model.joblib` | Saved model (scikit-learn Pipeline: pass-through scaler + Decision Tree) |
| `model_artifacts/model_metadata.json` | Feature order, classes, ranges, policy, metrics, library versions |
| 
| `README.md` | This file |

**Data files the notebook reads (not included here - put them next to the notebook):**
- `irrigation_prediction.csv` - training dataset (10,000 rows x 20 columns).
- `real_sensor_data.csv` - your Arduino log with columns `Timestamp, Soil_Moisture, Temperature_C, Humidity` (soil moisture in %).

---

## 3. Quick start

**Requirements** (versions used to create the saved model): Python 3.12, scikit-learn 1.8.0, pandas 3.0.2,
numpy 2.4.4, joblib 1.5.3, plus matplotlib and seaborn for the plots, and Jupyter.

```bash
pip install scikit-learn pandas numpy joblib matplotlib seaborn jupyter
jupyter notebook smart_irrigation_model.ipynb      # Run > Run All Cells
```

- The notebook takes a few minutes to run (model tuning).
- Keep the `model_artifacts/` folder next to the notebook. Part B loads the saved model from it.
- `FREEZE_SAVED_MODEL = True` (Step 20) means re-running the notebook **never overwrites** the saved model or metadata.
- **Stored outputs for the real data** (Steps 23 and 31) come from a **30-row excerpt**. Re-run with your complete
  `real_sensor_data.csv` to refresh them (an earlier run of the full log had 135 readings).

---

## 4. Test the model and the control unit

At the end of the notebook, one function tests the whole chain:

```python
test_irrigation(soil_moisture, temperature, humidity)                       # basic test
test_irrigation(12, 33, 50)                                                 # dry and hot  -> AI High, pump ON
test_irrigation(12, 33, 50, simulate=True)                                  # also simulate the running pump
test_irrigation(12, 33, 50, flow_sensor_available=True)                     # flow-sensor branch
test_irrigation(12, 33, 50, force_off=True)                                 # manual FORCE_OFF -> pump OFF
test_irrigation(30, 32, 55, zone=my_zone)                                   # your own zone settings
```

It prints the AI class, the pump decision and reason, the required water and runtime, the stop conditions and any warnings.

Automated tests already in the notebook: **20 final consistency checks** (Step 37) and **24 flow-branch / FORCE_OFF tests**
(Step 29.2). All pass.

---

## 5. Configure a farm zone (no retraining needed)

```python
my_zone = make_config(**{**asdict(EXAMPLE_ZONE), "zone_area_m2": 80.0, "flow_rate_lpm": 40.0})
```

`make_config` rejects invalid or unsafe values with a clear error. Main parameters:

| Parameter | Meaning | Unit |
|---|---|---|
| `zone_area_m2` | Irrigated area | m2 |
| `soil_moisture_threshold` / `target_soil_moisture` | Irrigate only below / stop at | sensor % |
| `depth_mode`, `fixed_water_depth_mm`, `root_zone_depth_mm` | How water depth is obtained | mm |
| `crop_coefficient`, `soil_adjustment_coefficient`, `application_efficiency` | Depth multipliers / efficiency | - |
| `flow_rate_lpm` | Calibrated flow rate (must be valid) | L/min |
| `min_runtime_min`, `max_runtime_min`, `min_interval_hours`, `max_events_per_day` | Runtime and frequency limits | min, h |

Operator options: `force_off` (manual emergency OFF, highest priority), `flow_sensor_available`, `ood_policy` (`"warn"` or `"block"`
for inputs outside the training range). Fixed guard-rails that cannot be edited through the configuration: **120 min per cycle, 25 mm per event**.

The values in `EXAMPLE_ZONE` and the scenarios are **illustrative placeholders** and must be calibrated for a real field.

---

## 6. Key equations (all units explicit)

```
deficit      = max(0, target - current)                  [% points]
net depth    = Kc x Ks x (deficit/100) x root depth       [mm]
gross depth  = net depth / efficiency, limited to 25 mm   [mm]
volume       = area x depth      (1 mm over 1 m2 = 1 L)   [L]
runtime      = volume / flow rate, limited by cutoffs     [min]
flow rate    = volume / (time/60)   (calibration or flow sensor)  [L/min]
```

**Two flow branches:** with a flow sensor the delivered volume is *measured*; without one the runtime is an *estimate* from the
calibrated flow rate. An invalid flow rate (None, NaN, zero, negative, non-numeric) means automatic irrigation does not start.

**Pump stops at the first of:** FORCE_OFF, maximum-runtime cutoff, flow fault (sensor branch), target soil moisture reached,
required volume delivered (sensor) or calculated runtime reached (no sensor).

---

## 7. The AI model

| Item | Value |
|---|---|
| Algorithm | Decision Tree, `class_weight="balanced"`, `max_depth=2`, `min_samples_leaf=5`, `random_state=42` |
| Inputs | `Soil_Moisture`, `Temperature_C`, `Humidity` (in this order) |
| Output | `Low`, `Medium`, `High` |
| Data | 10,000 observations; 8,000 train / 2,000 test (stratified) |
| Test performance | Accuracy 57.8%, macro precision 48.4%, macro recall 59.5%, macro F1 48.9% |
| High class | Recall 64.2%, precision 17.7% |
| Baseline | Always predicting "Low" gives 58.7% accuracy |

The model is an **initial prototype**. It uses soil moisture (about 25% threshold) and temperature (about 30 C); humidity is not used.

---

## 8. What is implemented and what is not

| Status | Components |
|---|---|
| **Implemented** | Arduino sensing (Arduino Uno, soil-moisture sensor, DHT11, as reported by the author); CSV data; model training, saving and loading; inference on real readings |
| **Implemented in software / simulated** | Control layer, equations, configuration and validation, planner rules, flow branches, FORCE_OFF, closed-loop stopping logic (simulated with an assumed soil response and an ideal flow meter) |
| **Proposed / not built** | Pump, relay, valve, flow sensor, water-level sensor, multi-zone nodes, LoRa/LoRaWAN, solar power, dashboard/app |
| **Not implemented** | Continuous real-time acquisition-inference-control loop; persistent irrigation-history store; physical stop switch |

---

## 9. Known limitations

- Accuracy (57.8%) is slightly below the always-Low baseline (58.7%); the model is not production-ready.
- The training dataset has no documented source or labelling method, and its statistics suggest generated data.
- Most real soil-moisture readings (about 0%) lie **outside the training range (8-65%)**, so predictions on them are extrapolations; the soil sensor needs calibration.
- The model cannot output High at temperatures below about 30 C (the log is about 25.7 C).
- The AI class acts only as a gate (Low vs Medium/High); it does not scale the water amount.
- Control constants are placeholders; the equations ignore drainage, rain, evaporation and evapotranspiration.
- No physical pump or flow sensor has been tested. Without a flow sensor, delivered volume is only an estimate.

## 10. Recommended next steps

1. Calibrate the soil-moisture sensor and document the raw-to-percent conversion.
2. Log labelled real data (sensor readings with expert or outcome-based irrigation decisions), then evaluate or retrain the model.
3. Calibrate the control constants and flow rate for one real plot.
4. Add a relay/pump with an independent hardware stop, then a flow sensor, and test physically.
5. Only after that: dashboard/app development.
