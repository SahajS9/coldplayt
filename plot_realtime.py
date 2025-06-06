import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import glob
import os
import yaml
from matplotlib.animation import FuncAnimation
import matplotlib.gridspec as gridspec
from compute import calibrate_df

# Load config
with open("config.yaml") as f:
    config = yaml.safe_load(f)

def get_latest_csv():
    files = glob.glob("data_*.csv")
    return max(files, key=os.path.getmtime) if files else None

# Grid layout for 4 plots
fig = plt.figure(constrained_layout=True, figsize=(12, 8))
gs = gridspec.GridSpec(2, 2, figure=fig)

ax_temp = fig.add_subplot(gs[0, 0])
ax_pressure = fig.add_subplot(gs[0, 1])
ax_power = fig.add_subplot(gs[1, 0])
ax_efficiency = fig.add_subplot(gs[1, 1])

# -----------------------------------------------------------------------------
# Set up plots (animation for realtime view)
# -----------------------------------------------------------------------------
def animate(i):
    latest_csv = get_latest_csv()
    if not latest_csv:
        return

    try:
        df = pd.read_csv(latest_csv).tail(100)

        # Apply calibrations and metrics
        df = calibrate_df(df, config)

        # Temperature plot
        ax_temp.clear()
        for label in ['fluid_in_F', 'fluid_out_F', 'T1_F', 'T2_F', 'T3_F']:
            if label in df:
                ax_temp.plot(df['seconds'], df[label], label=label)
        ax_temp.set_title("Temperatures (Fluid + T1–T3)")
        ax_temp.legend()
        ax_temp.set_ylabel("°F")

        # Pressure plot
        ax_pressure.clear()
        for label in ['P_in', 'P_out']:
            if label in df:
                ax_pressure.plot(df['seconds'], df[label], label=label)
        ax_pressure.set_title("Pressures")
        ax_pressure.legend()
        ax_pressure.set_ylabel("psi")

        # Power plot
        ax_power.clear()
        if 'pump_power' in df and 'heater_power' in df:
            ax_power.scatter(df['pump_power'], df['heater_power'], alpha=0.6)
        ax_power.set_xlabel("Pump Power")
        ax_power.set_ylabel("Heater Power")
        ax_power.set_title("Heater vs Pump Power")

        # Efficiency plot
        ax_efficiency.clear()
        if 'efficiency' in df:
            ax_efficiency.plot(df['seconds'], df['efficiency'], label="Efficiency")
        ax_efficiency.set_ylim(0, 1)
        ax_efficiency.set_ylabel("η (Thermal)")
        ax_efficiency.set_title("System Efficiency")
        ax_efficiency.legend()

        for ax in [ax_temp, ax_pressure, ax_efficiency]:
            ax.tick_params(axis='x', rotation=45)

    except Exception as e:
        print(f"Plot error: {e}")

# Execution
print(f"Showing realtime plot using {get_latest_csv()}")
ani = FuncAnimation(fig, animate, interval=100, save_count=100)
plt.show()
