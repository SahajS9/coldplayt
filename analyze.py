import sys
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import yaml
from datetime import datetime
from plot_realtime import get_latest_csv
from compute import (
    adc_to_temperature,
    calculate_heat_transfer,
    calculate_pump_power,
    calculate_efficiency
)

# -----------------------------------------------------------------------------
# Loads CSV file specified in CLI or defaults to latest.csv
# -----------------------------------------------------------------------------
if len(sys.argv) > 1: # Read argument if any
    csv_file = sys.argv[1]
else: # Default to latest.csv if no argument given
    dsv_file = get_latest_csv()
    
print(f"Analyzing file: {csv_file}")

try: # Load data
    df = pd.read_csv(csv_file)
except FileNotFoundError:
    print(f"Error: File '{csv_file}' not found.")
    sys.exit(1)

# -----------------------------------------------------------------------------
# Load calibration from config.yaml
# -----------------------------------------------------------------------------
with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

cal = config['calibration']['thermistor']
calibration = {
    'R_fixed': cal.get('R_fixed', 51000.0),
    'R_nominal': cal.get('R_nominal', 100000.0),
    'T_nominal': cal.get('T_nominal', 25.0),
    'beta': cal.get('B', 3950.0),
    'adc_max': config['calibration'].get('adc_max', 1023)
}
flow_rate = config['calibration'].get('flow_rate_m3s', 0.0001)

# -----------------------------------------------------------------------------
# Timestamp processing
# -----------------------------------------------------------------------------
df['timestamp'] = pd.to_datetime(df['timestamp'])
df['time_only'] = df['timestamp'].dt.strftime('%H:%M:%S')
analysis_date = df['timestamp'].dt.date.iloc[0]

# -----------------------------------------------------------------------------
# Convert raw ADC readings to temperature
# -----------------------------------------------------------------------------
for col in ['fluid_in', 'fluid_out']:
    if col in df.columns:
        df[f'{col}_C'] = df[col].apply(lambda v: adc_to_temperature(v * calibration['adc_max'], calibration))

# -----------------------------------------------------------------------------
# Calculate heat transfer
# -----------------------------------------------------------------------------
m_dot = 0.01  # Mass flow rate (kg/s), assumed constant
cp = 1090     # Specific heat of Flutec PP1 (J/kg·K)
df['Q_dot'] = calculate_heat_transfer(m_dot, cp, df.get('fluid_in_C'), df.get('fluid_out_C'))

# -----------------------------------------------------------------------------
# Calculate thermal efficiency
# -----------------------------------------------------------------------------
if 'heater_power' in df.columns and df['heater_power'].notna().all():
    df['efficiency'] = calculate_efficiency(df['heater_power'], df['Q_dot'])
else:
    df['efficiency'] = np.nan

# -----------------------------------------------------------------------------
# Calculate pressure differential and pump power
# -----------------------------------------------------------------------------
if 'P_in' in df.columns and 'P_out' in df.columns:
    df['delta_p'] = df['P_in'] - df['P_out']
    df['pump_power'] = calculate_pump_power(flow_rate, df['delta_p'])
else:
    df['delta_p'] = df['pump_power'] = np.nan

# -----------------------------------------------------------------------------
# Calculate delta_T
# -----------------------------------------------------------------------------
if 'fluid_in_C' in df.columns and 'fluid_out_C' in df.columns:
    df['delta_T'] = df['fluid_in_C'] - df['fluid_out_C']

# -----------------------------------------------------------------------------
# Data processing
# -----------------------------------------------------------------------------
# Export processed data
computed_csv = f"computed_{csv_file}"
df.to_csv(computed_csv, index=False)
print(f"Saved computed data to {computed_csv}")

# Output summary into console
print("\n=== Summary Statistics ===")
for col in ['Q_dot', 'heater_power', 'pump_power', 'efficiency']:
    if col in df.columns and df[col].notna().any():
        print(f"{col}: avg = {df[col].mean():.2f}, max = {df[col].max():.2f}")

# -----------------------------------------------------------------------------
# Plot setup
# -----------------------------------------------------------------------------
sns.set(style="whitegrid")
fig, axs = plt.subplots(2, 2, figsize=(14, 10))

# Plot 1: Temperature vs Time
for col in ['T1', 'T2', 'T3', 'fluid_in', 'fluid_out']:
    if col in df.columns:
        axs[0,0].plot(df['timestamp'], df[col], label=col)
axs[0,0].set_title("Temperature vs Time")
axs[0,0].set_ylabel("Temperature (C)")
axs[0,0].legend()

# Plot 2: Pressure vs Time
for col in ['P_in', 'P_out', 'delta_p']:
    if col in df.columns:
        axs[0,1].plot(df['timestamp'], df[col], label=col)
axs[0,1].set_title("Pressure vs Time")
axs[0,1].set_ylabel("Pressure (Pa)")
axs[0,1].legend()

# Plot 3: Heat power vs pump power ( + efficiency)
if 'Q_dot' in df.columns and 'pump_power' in df.columns:
    sc = axs[1,0].scatter(df['pump_power'], df['Q_dot'], c=df['efficiency'], cmap='viridis', label='Efficiency')
    axs[1,0].set_title("Heat Transfer vs Pump Power")
    axs[1,0].set_xlabel("Pump Power (W)")
    axs[1,0].set_ylabel("Heat Transfer Rate (W)")
    fig.colorbar(sc, ax=axs[1,0], label="Efficiency")

# Plot 4: Efficiency over time
if 'efficiency' in df.columns:
    axs[1,1].plot(df['timestamp'], df['efficiency'])
    axs[1,1].set_title("System Efficiency Over Time")
    axs[1,1].set_ylabel("Efficiency")

for ax in axs.flat:
    ax.set_xlabel("Time")
    ax.tick_params(axis='x', rotation=30)

# Show plots
plt.tight_layout()
plot_file = f"analysis_grid_{csv_file.replace('.csv','')}.png"
plt.savefig(plot_file, dpi=300)
print(f"Saved analysis figure to {plot_file}") # Save plot as image
plt.show()
