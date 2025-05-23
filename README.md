# coldplayt

Thermal-fluid data acquisition and analysis system using a Raspberry Pi and MCP3008 ADC.
Used for finding the efficiency of a two-phase cold plate design for high-power chip cooling.

```
coldplayt/
├── main.py              # Live data collection loop
├── collect.py           # Sensor reading logic (ADC + calibration)
├── compute.py           # Thermo/fluids computations (temp conversion, power)
├── plot_realtime.py     # Live plotting of temperature sensors
├── analyze.py           # Offline CSV post-processing and plotting
├── config.yaml          # Calibration values and sensor-channel mapping
├── README.md            # This file
```

---

## To-do:

- Add or measure accurate flow rate for better pump power calculations
- Plot pump power vs heat flux
- Plot system efficiency over time
- Analyze pressure drops across different heat exchanger geometries
- Plot deltas: `power in vs out`, `pressure in vs out`, etc.
- Calibrate thermistors using either:
  - Steinhart-Hart coefficients in `config.yaml`
  - Reference thermocouple readings (if attached)

---

## 1. Basic Temperature Logging

**Goal:** Log and monitor temperature in real time.

### Setup

- Define thermistor channels under `sensors.thermistors` in `config.yaml`.

### Run

```bash
python main.py              # Starts logging sensor data to CSV
python plot_realtime.py     # Shows live graph of temperatures
```

- Data is saved to `data_<timestamp>.csv`.

---

## 2. Full Thermodynamic Monitoring

**Goal:** Compute heat transfer rate and system efficiency.

### Requirements

- Thermistors (input/output fluid temps)
- Heater power sensor

### Steps

- Map thermistors and `heater_power` ADC channels in `config.yaml`.
- `main.py` will log raw ADC values.
- `collect.py` is used by `main.py` to read sensor values and convert them.
- `compute.py` provides all thermodynamic calculations like temperature, heat transfer, and pump power.

### Analyze

```bash
python analyze.py                # Analyzes the latest CSV
python analyze.py myfile.csv     # Analyzes specified file
```

- Outputs:
  - Computed temperatures
  - Heat transfer rate (`Q_dot`)
  - Efficiency (if heater power available)
  - Optional pump power (if pressure sensors configured)

---

## 3. Pressure and Pump Analysis

**Goal:** Estimate flow resistance and pump power.

### Requirements

- `P_in` and `P_out` sensors defined in `config.yaml`.

### Steps

- Run `main.py` to collect data.
- `analyze.py` will automatically compute `delta_p` and estimate pump power using flow rate (defined in script).
- `compute.py` handles the physical equation: `Pump Power = ΔP × Flow Rate`.

---

## 4. Offline Analysis of CSV

**Goal:** Re-analyze or re-plot previous runs.

### Steps

- Copy your `.csv` into the working directory.
- Either:
  - Rename it to `latest.csv`, or
  - Run `analyze.py your_file.csv`

---

## Role of Scripts

| Script             | Description                                                                                                                     |
| ------------------ | ------------------------------------------------------------------------------------------------------------------------------- |
| `main.py`          | Entry point for live data collection. Repeatedly calls `collect.py`.                                                            |
| `collect.py`       | Reads analog values from MCP3008 and uses `compute.py` to convert to physical values (e.g., °C).                                |
| `compute.py`       | Contains all physical/thermodynamic computation functions, such as temperature conversion, heat transfer rate, pump power, etc. |
| `analyze.py`       | Offline analysis of logged CSV data. Uses functions from `compute.py`.                                                          |
| `plot_realtime.py` | Displays live plot of temperatures. Optional during data collection.                                                            |

---

## Features

- MCP3008 ADC integration for analog sensors
- Thermistor temperature conversion via Steinhart-Hart equation
- Heat transfer and efficiency calculations
- Optional heater and pump power analysis
- Plots: temperature vs time, heat transfer, pump power
- Automatically skips unavailable data (e.g., no heater or pressure sensors)

---

## Notes

- Sensors not connected? Simply omit their entries in `config.yaml`.
- All analog sensors must be wired to the MCP3008 or similar ADC.
- Real-time plotting and post-analysis are optional but helpful for validation.
- All CSVs are timestamped for easy record-keeping.

---

## Sample Data

You can test the analysis and plotting pipeline using the provided `sample_data.csv`.

---

## Requirements

- Raspberry Pi (or any Linux SBC)
- MCP3008 ADC (or equivalent SPI-compatible ADC)
- Python 3.7+

### Install Python libraries:

```bash
    pip install matplotlib pandas numpy seaborn pyyaml spidev
```
