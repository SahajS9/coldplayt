import pandas as pd
from compute import steinhart, heat_transfer_rate, pump_power
import matplotlib.pyplot as plt
import seaborn as sns

# Load your data
filename = "latest.csv"
df = pd.read_csv(filename)

# Convert voltages to temperatures
for col in ['fluid_in', 'fluid_out']:
    df[f'{col}_C'] = df[col].apply(lambda v: steinhart(v))

# Calculate heat transfer rate
m_dot = 0.01  # kg/s
cp = 4186     # J/kg·K

df['Q_dot'] = heat_transfer_rate(m_dot, cp, df['fluid_in_C'], df['fluid_out_C'])

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
    df['pump_power_calc'] = pump_power(flow_rate, df['delta_p'])
    print("Pump power estimated from pressure differential.")

# Plot heat transfer rate
sns.lineplot(data=df, x='timestamp', y='Q_dot')
plt.title("Heat Transfer Over Time")
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()
