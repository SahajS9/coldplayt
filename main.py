import time
import csv
from collect import read_all
from datetime import datetime

filename = f"data_{datetime.now().isoformat()}.csv"

header = [
    "timestamp", "T1", "T2", "T3", "fluid_in", "fluid_out", "P_in", "P_out",
    "heater_power",  # Optional: Will be filled with None if not connected
    "pump_power"      # Optional: Will be filled with None if not connected
]

with open(filename, "w", newline='') as f:
    writer = csv.writer(f)
    writer.writerow(header)

    try:
        while True:
            readings = read_all()
            row = [datetime.now().isoformat()]
            for key in header[1:]:
                row.append(readings.get(key, None))  # Optional sensors filled with None
            writer.writerow(row)
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopped logging.")