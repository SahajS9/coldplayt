import time
import csv
from collect import read_all
from datetime import datetime

# Names log file as 'data_YYYY-MM-DD_HH.MM.SS.csv' (Windows does not allow : in file names)
filename = f"data_{datetime.now().isoformat(timespec='seconds').replace(':', '.').replace('T','_')}.csv" 

header = [
    "timestamp", "T1", "T2", "T3", "fluid_in", "fluid_out", "P_in", "P_out",
    "heater_power", "pump_power"
]

with open(filename, "w", newline='') as f:
    writer = csv.writer(f)
    writer.writerow(header)
    f.flush()  # Ensure header is written immediately
    print(f"Now collecting data in {filename}")
    print(f"Run 'python plot_realtime.py' to view live metrics")
    try:
        while True:
            readings = read_all()
            row = [datetime.now().isoformat(timespec='milliseconds')] # HH:MM:SS.sss
            for key in header[1:]:
                row.append(readings.get(key, None))  # Optional sensors filled with 'None'
            writer.writerow(row)
            f.flush()  # Ensure row is written immediately
            time.sleep(0.1) # Sleep for 100ms before looping
    except KeyboardInterrupt:
        print("Stopped logging.")
