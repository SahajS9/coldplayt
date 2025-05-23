
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.animation import FuncAnimation

fig, ax = plt.subplots()
data = pd.DataFrame()

def animate(i):
    global data
    try:
        data = pd.read_csv("latest.csv")[-100:]  # Make sure to link to current CSV
        ax.clear()
        ax.plot(data['timestamp'], data['fluid_in'], label="Fluid In")
        ax.plot(data['timestamp'], data['fluid_out'], label="Fluid Out")
        ax.legend()
        ax.set_title("Real-Time Fluid Temperature")
        ax.set_xlabel("Time")
        ax.set_ylabel("Temp (C)")
    except Exception as e:
        print(f"Error updating plot: {e}")

ani = FuncAnimation(fig, animate, interval=1000)
plt.show()