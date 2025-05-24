import serial
import time
import csv
import os
from datetime import datetime
import matplotlib.pyplot as plt
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Settings
SERIAL_PORT = '/dev/ttyACM0'
BAUD_RATE = 115200
TANK_DIAMETER_INCHES = 96  # Change this to match your tank
DATA_DIR = "tank_data"
os.makedirs(DATA_DIR, exist_ok=True)

def gallons_from_depth(depth_inches, diameter_inches):
    radius_ft = (diameter_inches / 12) / 2
    depth_ft = depth_inches / 12
    gallons = 3.1416 * (radius_ft**2) * depth_ft * 7.48052
    return round(gallons, 2)

def log_data(node_name, depth_inches):
    now = datetime.now()
    filename = os.path.join(DATA_DIR, f"{node_name}_log.csv")
    gallons = gallons_from_depth(depth_inches, TANK_DIAMETER_INCHES)
    with open(filename, "a", newline='') as f:
        writer = csv.writer(f)
        writer.writerow([now.isoformat(), depth_inches, gallons])
    return gallons

def read_serial():
    try:
        with serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=5) as ser:
            line = ser.readline().decode('utf-8').strip()
            print("Received:", line)
            if "DRY CREEK" in line:
                parts = line.split()
                for i, p in enumerate(parts):
                    if p == "CREEK":
                        try:
                            depth = float(parts[i+1])
                            return "DRY_CREEK", depth
                        except:
                            pass
    except Exception as e:
        print("Serial read error:", e)
    return None, None

def update_plot():
    node, depth = read_serial()
    if node and depth is not None:
        gallons = log_data(node, depth)
        timestamps, depths = [], []
        try:
            with open(os.path.join(DATA_DIR, f"{node}_log.csv")) as f:
                reader = csv.reader(f)
                for row in reader:
                    timestamps.append(datetime.fromisoformat(row[0]))
                    depths.append(float(row[1]))
        except:
            return

        ax.clear()
        ax.plot(timestamps[-144:], depths[-144:], label="Depth (inches)")
        ax.set_title(f"Water Level for {node.replace('_', ' ')}")
        ax.set_ylabel("Depth (inches)")
        ax.set_xlabel("Time")
        ax.legend()
        canvas.draw()

    root.after(60000, update_plot)  # Update every 60 seconds

# GUI
root = tk.Tk()
root.title("Tank Dashboard")

fig, ax = plt.subplots(figsize=(8, 4))
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack()

update_plot()
root.mainloop()
