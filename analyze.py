import sys
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import yaml
from datetime import datetime
from plot_realtime import get_latest_csv
from compute import calibrate_df

# -----------------------------------------------------------------------------
# Loads CSV file specified in CLI or defaults to latest.csv
# -----------------------------------------------------------------------------
if len(sys.argv) > 1:
    csv_file = sys.argv[1]
else:
    csv_file = get_latest_csv()

print(f"Analyzing file: {csv_file}")

try:
    df = pd.read_csv(csv_file)
    print("Before calibration:\n", df[['pump_power', 'T1', 'T2', 'T3', 'P_in', 'P_out']].head())

except FileNotFoundError:
    print(f"Error: File '{csv_file}' not found.")
    sys.exit(1)

# -----------------------------------------------------------------------------
# Load calibration from config.yaml
# -----------------------------------------------------------------------------
with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

# -----------------------------------------------------------------------------
# Seconds processing, no longer needed since logging is now in seconds from T-0
# -----------------------------------------------------------------------------
# df['seconds'] = pd.to_datetime(df['seconds'])
# df['time_only'] = df['seconds'].dt.strftime('%H:%M:%S')
# analysis_date = df['seconds'].dt.date.iloc[0]

# -----------------------------------------------------------------------------
# Apply sensor calibrations and compute metrics
# -----------------------------------------------------------------------------
df = calibrate_df(df, config)
print("After calibration:\n", df[['P_in_psi', 'P_out_psi', 'T1_F', 'T2_F', 'T3_F']].head()) # Debug

# -----------------------------------------------------------------------------
# Calculate delta_T
# -----------------------------------------------------------------------------
if 'fluid_in_F' in df.columns and 'fluid_out_F' in df.columns:
    df['delta_T'] = df['fluid_in_F'] - df['fluid_out_F']

# -----------------------------------------------------------------------------
# Data processing
# -----------------------------------------------------------------------------
# Export processed data
computed_csv = f"computed_{csv_file}"
df.to_csv(computed_csv, index=False)
print(f"Saved computed data to {computed_csv}")

# Output summary into console
print("\n=== Statistics ===")
for col in ['Q_dot', 'heater_power', 'pump_power', 'efficiency']:
    if col in df.columns and df[col].notna().any():
        print(f"{col}: avg = {df[col].mean():.2f}, max = {df[col].max():.2f}")

# -----------------------------------------------------------------------------
# Plot setup
# -----------------------------------------------------------------------------
sns.set(style="whitegrid")
fig, axs = plt.subplots(2, 2, figsize=(14, 10))

# Plot 1: Temperature vs Time
for col in ['T1_F', 'T2_F', 'T3_F', 'fluid_in_F', 'fluid_out_F']:
    if col in df.columns:
        axs[0,0].plot(df['seconds'], df[col], label=col)
axs[0,0].set_title("Temperature vs Time")
axs[0,0].set_ylabel("Temperature (F)")
axs[0,0].legend()

# Plot 2: Pressure vs Time
for col in ['P_in_psi', 'P_out_psi', 'delta_p']:
    if col in df.columns:
        axs[0,1].plot(df['seconds'], df[col], label=col)
axs[0,1].set_title("Pressure vs Time")
axs[0,1].set_ylabel("Pressure (Pa)")
axs[0,1].legend()

# Plot 3: Heat power vs pump power ( + efficiency)
if 'Q_dot' in df.columns and 'pump_power' in df.columns:
    sc = axs[1,0].scatter(df['pump_power'], df['Q_dot'], c=df['efficiency'], cmap='viridis', label='Efficiency')
    axs[1,0].set_title("Heat Transfer Rate and Efficiency")
    axs[1,0].set_xlabel("Pump Power (W)")
    axs[1,0].set_ylabel("Heat Transfer Rate (W)")
    fig.colorbar(sc, ax=axs[1,0], label="Efficiency")

# Plot 4: Efficiency over time
if 'efficiency' in df.columns:
    axs[1,1].plot(df['seconds'], df['efficiency'])
    axs[1,1].set_title("System Efficiency Over Time")
    axs[1,1].set_ylabel("Efficiency")

for ax in axs.flat:
    ax.set_xlabel("Time")
    ax.tick_params(axis='x', rotation=30)

# Show plots
plt.tight_layout()
plot_file = f"analysis_grid_{csv_file.replace('.csv','')}.png"
plt.savefig(plot_file, dpi=300)
print(f"Saved analysis figure to {plot_file}")
# plt.show()
