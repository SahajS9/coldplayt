import sys
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import yaml
from datetime import datetime

from compute import adc_to_temperature, calculate_heat_transfer, calculate_pump_power

# Choose CSV file: default to 'latest.csv' if no argument provided
if len(sys.argv) > 1:
    csv_file = sys.argv[1]
    print(f"Using provided CSV file: {csv_file}")
else:
    csv_file = "latest.csv"
    print(f"No file provided. Defaulting to: {csv_file}")

# Load the CSV
try:
    df = pd.read_csv(csv_file)
except FileNotFoundError:
    print(f"❌ File not found: {csv_file}")
    sys.exit(1)

# Load calibration from config.yaml
with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

calibration = {
    'R_fixed': config['calibration']['thermistor'].get('R_fixed', 51000.0),
    'R_nominal': config['calibration']['thermistor'].get('R_nominal', 100000.0),
    'T_nominal': config['calibration']['thermistor'].get('T_nominal', 25.0),
    'beta': config['calibration']['thermistor'].get('B', 3950.0),
    'adc_max': config['calibration'].get('adc_max', 1023)
}

# Convert timestamp column to datetime
df['timestamp'] = pd.to_datetime(df['timestamp'])
df['time_only'] = df['timestamp'].dt.strftime('%H:%M:%S')
analysis_date = df['timestamp'].dt.date.iloc[0]

# Convert voltages to temperature (assuming voltages scaled 0–1)
for col in ['fluid_in', 'fluid_out']:
    df[f'{col}_C'] = df[col].apply(lambda v: adc_to_temperature(v * calibration['adc_max'], calibration))

# Calculate heat transfer rate
m_dot = 0.01  # kg/s
cp = 4186     # J/kg·K (for water)

df['Q_dot'] = calculate_heat_transfer(m_dot, cp, df['fluid_in_C'], df['fluid_out_C'])

# Optional: calculate thermal efficiency if heater power is available
if 'heater_power' in df.columns and df['heater_power'].notna().all():
    df['efficiency'] = df['Q_dot'] / df['heater_power']
    print("Thermal efficiency calculated.")
else:
    print("Heater power data not available — skipping efficiency calculation.")

# Optional: calculate pump power if pressure data is present
if 'P_in' in df.columns and 'P_out' in df.columns:
    df['delta_p'] = df['P_in'] - df['P_out']
    flow_rate = 0.0001  # m^3/s — assumed constant, update if measured
    df['pump_power_calc'] = calculate_pump_power(flow_rate, df['delta_p'])
    print("Pump power estimated from pressure differential.")

# Plot temperatures
plt.figure(figsize=(12,6))
for col in ['T1', 'T2', 'T3']:
    if col in df.columns:
        plt.plot(df['time_only'], df[col], label=col)

plt.xlabel('Time (HH:MM:SS)')
plt.ylabel('Temperature (°C)')
plt.title(f'Temperature vs Time - Analysis Date: {analysis_date}')
plt.xticks(rotation=45)
plt.legend()
plt.tight_layout()
plt.savefig("analysis_output.png", dpi=300) # Optional: Saves figure as image when X-11 is not available
print("Saved figure as 'analysis_output.png.'")
plt.show()
