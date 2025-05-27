import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import glob
import os
import yaml
from matplotlib.animation import FuncAnimation
import matplotlib.gridspec as gridspec
from compute import adc_to_temperature

# Load calibration config once
with open("config.yaml") as f:
    config = yaml.safe_load(f)

therm_cal = config['calibration']['thermistor']
pressure_cal = config['calibration'].get('pressure', {})  # Placeholder
power_cal = config['calibration'].get('power', {})        # Placeholder

def get_latest_csv():
    files = glob.glob("data_*.csv")
    return max(files, key=os.path.getmtime) if files else None

def convert_adc_pressure(adc_val, label=None):
    # Placeholder: add real conversion logic per label if available
    return adc_val  # Replace with volts_to_psi or similar

def convert_adc_power(adc_val, label=None):
    # Placeholder: add real conversion logic if available
    return adc_val  # Replace with actual calibration

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
    m_dot = 0.01  # kg/s
    cp = 4180  # J/kg·K for water
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

        # Calibrate ADC thermistors to °C
        for t_col in ['T1', 'T2', 'T3']:
            if t_col in df:
                df[t_col] = df[t_col].apply(lambda x: adc_to_temperature(x, therm_cal) if pd.notna(x) else np.nan)

        # Calibrate fluid in/out (assume they are thermistors too)
        for f_col in ['fluid_in', 'fluid_out']:
            if f_col in df:
                df[f_col] = df[f_col].apply(lambda x: adc_to_temperature(x, therm_cal) if pd.notna(x) else np.nan)

        # Calibrate pressure (placeholder)
        for p_col in ['P_in', 'P_out']:
            if p_col in df:
                df[p_col] = df[p_col].apply(lambda x: convert_adc_pressure(x, p_col) if pd.notna(x) else np.nan)

        # Calibrate power (placeholder)
        for pwr_col in ['heater_power', 'pump_power']:
            if pwr_col in df:
                df[pwr_col] = df[pwr_col].apply(lambda x: convert_adc_power(x, pwr_col) if pd.notna(x) else np.nan)

        # Efficiency
        df['efficiency'] = df.apply(compute_efficiency, axis=1)

        # Temperature plot
        ax_temp.clear()
        for label in ['fluid_in', 'fluid_out', 'T1', 'T2', 'T3']:
            if label in df:
                ax_temp.plot(df['timestamp'], df[label], label=label)
        ax_temp.set_title("Temperatures (Fluid + T1–T3)")
        ax_temp.legend()
        ax_temp.set_ylabel("°C")

        # Pressure plot
        ax_pressure.clear()
        for label in ['P_in', 'P_out']:
            if label in df:
                ax_pressure.plot(df['timestamp'], df[label], label=label)
        ax_pressure.set_title("Pressures")
        ax_pressure.legend()
        ax_pressure.set_ylabel("Pa or Raw ADC")

        # Power plot
        ax_power.clear()
        if 'pump_power' in df and 'heater_power' in df:
            ax_power.scatter(df['pump_power'], df['heater_power'], alpha=0.6)
        ax_power.set_xlabel("Pump Power")
        ax_power.set_ylabel("Heater Power")
        ax_power.set_title("Heater vs Pump Power")

        # Efficiency plot
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

print(f"Showing realtime plot using {get_latest_csv()}")
ani = FuncAnimation(fig, animate, interval=100, save_count=100)
plt.show()
