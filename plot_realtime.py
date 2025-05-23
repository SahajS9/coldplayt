import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import glob
import os
from matplotlib.animation import FuncAnimation
import matplotlib.gridspec as gridspec

def get_latest_csv():
    files = glob.glob("data_*.csv")
    return max(files, key=os.path.getmtime) if files else None

fig = plt.figure(constrained_layout=True, figsize=(12, 8))
gs = gridspec.GridSpec(2, 2, figure=fig)

ax_temp = fig.add_subplot(gs[0, 0])
ax_pressure = fig.add_subplot(gs[0, 1])
ax_power = fig.add_subplot(gs[1, 0])
ax_efficiency = fig.add_subplot(gs[1, 1])

def compute_efficiency(row):
    heater = row.get("heater_power")
    pump = row.get("pump_power")
    fluid_in = row.get("fluid_in")
    fluid_out = row.get("fluid_out")
    m_dot = 0.01  # adjust as needed
    cp = 4180  # water
    if pd.isna(heater) or pd.isna(fluid_in) or pd.isna(fluid_out):
        return np.nan
    q_dot = m_dot * cp * (fluid_in - fluid_out)
    return q_dot / heater if heater else np.nan

def animate(i):
    latest_csv = get_latest_csv()
    if not latest_csv:
        return

    try:
        df = pd.read_csv(latest_csv).tail(100)
        df['timestamp'] = pd.to_datetime(df['timestamp'])

        # Efficiency
        df['efficiency'] = df.apply(compute_efficiency, axis=1)

        ax_temp.clear()
        if 'fluid_in' in df: ax_temp.plot(df['timestamp'], df['fluid_in'], label="Fluid In")
        if 'fluid_out' in df: ax_temp.plot(df['timestamp'], df['fluid_out'], label="Fluid Out")
        if 'T1' in df: ax_temp.plot(df['timestamp'], df['T1'], label="T1")
        if 'T2' in df: ax_temp.plot(df['timestamp'], df['T2'], label="T2")
        if 'T3' in df: ax_temp.plot(df['timestamp'], df['T3'], label="T3")
        ax_temp.set_title("Temperatures (Fluid + T1–T3)")
        ax_temp.legend()
        ax_temp.set_ylabel("°C")

        ax_pressure.clear()
        ax_pressure.plot(df['timestamp'], df['P_in'], label="P_in")
        ax_pressure.plot(df['timestamp'], df['P_out'], la   bel="P_out")
        ax_pressure.set_title("Pressures")
        ax_pressure.legend()
        ax_pressure.set_ylabel("ADC or Pa")

        ax_power.clear()
        ax_power.scatter(df['pump_power'], df['heater_power'], alpha=0.6)
        ax_power.set_xlabel("Pump Power")
        ax_power.set_ylabel("Heater Power")
        ax_power.set_title("Heater vs Pump Power")

        ax_efficiency.clear()
        ax_efficiency.plot(df['timestamp'], df['efficiency'], label="Efficiency")
        ax_efficiency.set_ylim(0, 1)
        ax_efficiency.set_ylabel("η (Thermal)")
        ax_efficiency.set_title("System Efficiency")
        ax_efficiency.legend()

        for ax in [ax_temp, ax_pressure, ax_efficiency]:
            ax.tick_params(axis='x', rotation=45)

    except Exception as e:
        print(f"Plot error: {e}")

ani = FuncAnimation(fig, animate, interval=1000)
plt.show()
