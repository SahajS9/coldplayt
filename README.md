# coldplayt

Raspberry Pi/ # Monitoring suite for testing in the lab using the rPi 4
├── main.py # Entry point for live collection and plotting
├── config.yaml # Sensor channel mappings, calibration constants
├── collect.py # Functions for analog data acquisition
├── compute.py # Thermodynamic/fluids computations
├── plot_realtime.py # Live visualization module
├── analyze.py # Post-run analysis and plots
└── utils.py # Helper functions (e.g., timestamping, logging)

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

## Notes

- All analog sensors must be connected to MCP3008 (or similar ADC).
- If a sensor is not connected, leave its channel out of `config.yaml`.
- CSV files are timestamped for easy archiving.
