# coldplayt

```
Raspberry Pi/
├── main.py              # Live data collection
├── collect.py           # Analog reading logic
├── compute.py           # Thermo/fluids computations
├── plot_realtime.py     # Real-time temperature plotting
├── analyze.py           # Post-processing of results
├── config.yaml          # Sensor mapping and calibration
├── README.md            # This file
```

## 1. Basic Temperature Logging

Goal: Log and view real-time temperatures
Steps:

- Set T1, T2, T3, etc. in `config.yaml`
- Run `main.py` to start logging
- Run `plot_realtime.py` to view live temperature curves

## 2. Full Thermodynamic Monitoring

Goal: Compute heat transfer, efficiency
Requirements: Thermistors + heater power sensor
Steps:

- Ensure heater power is mapped in `config.yaml`
- Run `main.py` to collect data
- Run `analyze.py` to compute heat rate and efficiency

## 3. Pressure and Pump Analysis

Goal: Measure fluid flow resistance, compute pump power
Requirements: Inlet/outlet pressure sensors
Steps:

- Configure P_in, P_out in `config.yaml`
- Run `main.py`
- Use `analyze.py` — it will auto-compute pump power if available

## 4. Offline Analysis of CSV

Goal: Reanalyze or replot a past run
Steps:

- Place a previous CSV in the working directory
- Modify `analyze.py` to load that file (or rename it to `latest.csv`)
- Run analysis

---

### Features

- Live data logging from MCP3008 ADC.
- Optional support for heater and pump power sensors.
- Saves data as timestamped CSV.
- Real-time plotting.
- Post-run analysis and thermodynamic calculations.

---

#### 1. Basic Temperature Logging

```bash
python main.py
```

- Logs data to `data_<timestamp>.csv`.
- Real-time plot: `python plot_realtime.py`

#### 2. Analyze Data

```bash
python analyze.py
```

- Computes temperature, heat transfer, and optionally efficiency/pump power.
- Outputs line plots using `matplotlib` and `seaborn`.

### Optional Sensor Logic

- Heater power and pump power sensors are **optional**.
- If not included, the system will continue logging and analyzing the available data.
- Post-analysis functions gracefully skip calculations with missing inputs.

### Note

- All analog sensors must be connected to MCP3008 (or similar ADC).
- If a sensor is not connected, leave its channel out of `config.yaml`.
- CSV files are timestamped for easy archiving.

### Sample Data

Use the provided sample CSV file `sample_data.csv` to test plotting and analysis scripts.

### Requirements

- Raspberry Pi with MCP3008 ADC
- Python 3.7+
- Libraries: `spidev`, `matplotlib`, `pandas`, `numpy`, `seaborn`, `pyyaml`

Install required packages:

```bash
pip install matplotlib pandas numpy seaborn pyyaml
```
