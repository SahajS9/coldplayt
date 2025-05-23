import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.animation import FuncAnimation
import glob
import os

fig, ax = plt.subplots()
data = pd.DataFrame()

def get_latest_csv():
    """Find the most recently modified CSV file."""
    csv_files = glob.glob("data_*.csv")
    if not csv_files:
        return None
    latest = max(csv_files, key=os.path.getmtime)
    return latest

def animate(i):
    global data
    latest_csv = get_latest_csv()
    if latest_csv is None:
        print("No CSV files found.")
        return
    try:
        data = pd.read_csv(latest_csv).tail(100)  # Limit to last 100 points
        ax.clear()
        ax.plot(data['timestamp'], data['fluid_in'], label="Fluid In")
        ax.plot(data['timestamp'], data['fluid_out'], label="Fluid Out")
        ax.legend()
        ax.set_title("Real-Time Fluid Temperature")
        ax.set_xlabel("Time")
        ax.set_ylabel("Temp (°C)")
        plt.xticks(rotation=45)
        plt.tight_layout()
    except Exception as e:
        print(f"Error updating plot: {e}")

ani = FuncAnimation(fig, animate, interval=1000)
plt.show()
